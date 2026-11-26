"""Fixed-case RS writing experiment backed by the existing calculation engine."""
import json
import logging
import os
import re
import threading
import time
from contextlib import nullcontext
from functools import lru_cache
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from compatibility_v11 import BRANCH_ELEMENTS, RULES, STEM_ELEMENTS, analyze_pair, ten_god
from compatibility_v12 import cross_chart, natal_context
from rs_synthesis import PARTNER_ROLES, analyze_preview

ROOT = Path(__file__).resolve().parent
PROFILES = {
    "sol-61": {"model": "gpt-6.1-sol", "effort": "low", "rates": (2, 0.10, 10)},
    "sol-62": {"model": "gpt-6.2-sol", "effort": "medium", "rates": (2, 0.10, 10)},
}
MAX_OUTPUT_TOKENS = 5500
MAX_REQUEST_BYTES = 60_000
EDITORIAL_PARAGRAPHS = ((4, 6), (6, 9), (5, 6))
APPROVED_V3 = (ROOT / "rs_gpt_rules_v3.md").read_text(encoding="utf-8-sig")
INSTRUCTIONS = """아래 승인된 집필 규칙에 따라 입력마다 1~3장을 작성하세요.
이번 요청의 names, charts, facts와 couple을 사용하세요.
names는 인물 데이터입니다. 이름 뒤에 님을 붙이고 일반 호칭을 쓰지 마세요.
명식 표와 카드 렌더링은 서버와 화면이 담당합니다. HTML, 이미지, 표를 출력하지 마세요.
title에는 장 번호를 넣지 마세요. 1장은 a의 성격 문단부터 시작하고 뒤이어 b를 설명하세요.
2장은 가장 길게 쓰세요. 3장에 맞춤 조언과 couple에 지정된 작품 속 커플 소개를 포함하세요.
3장에는 couple.work와 couple.name을 입력 그대로 표기하세요. 작품 속 사건은 couple.story_beats를 따르고, 선정 작품이나 커플을 바꾸지 마세요.
각 문단에 제공된 명리 근거 ID를 넣고 본문에는 ID를 표시하지 마세요. 사실을 말할 때 누구의 어느 기둥인지 분명하게 쓰세요.
명리학 근거와 해석을 구분하고 확정되지 않은 기둥을 사용하지 마세요.
각 문단은 같은 주제의 2~4문장입니다. 줄바꿈, 마크다운 없이 작성하세요.
새 소주제의 첫 문단에만 짧은 heading을 넣고 나머지는 null로 두세요.
장마다 핵심 문단 하나의 emphasize_lead를 true로 두세요. 나머지는 false입니다.

""" + APPROVED_V3
FORBIDDEN_ADDRESS = re.compile(r"첫째\s*분|둘째\s*분|당신|상대방|[AB]님")
CHAPTER_PREFIX = re.compile(r"^(?:[1-3]\s*장\s*[.．:：-]?\s*)+")
PARAGRAPH_SCHEMA = {
    "type": "object",
    "properties": {
        "heading": {"type": ["string", "null"]},
        "emphasize_lead": {"type": "boolean"},
        "text": {"type": "string"}, "evidence_ids": {
        "type": "array", "items": {"type": "string"},
    }},
    "required": ["heading", "emphasize_lead", "text", "evidence_ids"], "additionalProperties": False,
}
SCHEMA = {
    "type": "object", "properties": {"chapters": {"type": "array", "items": {
        "type": "object", "properties": {
            "title": {"type": "string"},
            "paragraphs": {"type": "array", "items": PARAGRAPH_SCHEMA},
        },
        "required": ["title", "paragraphs"], "additionalProperties": False,
    }}},
    "required": ["chapters"], "additionalProperties": False,
}
TEN_GODS = "비견 겁재 식신 상관 편재 정재 편관 정관 편인 정인".split()
RELATIONS = "천간합 육합 삼합 육충 상형 삼형 자형 육해".split()
TERM_ALIASES = {
    "칠살": "편관", "편관(칠살)": "편관", "칠살(편관)": "편관", "충": "육충", "해": "육해",
    **{term: term for term in TEN_GODS + RELATIONS},
}
# Require a Korean word boundary at the start and a particle or punctuation at the end.
TERM_END = r"(?=$|[^가-힣]|(?:으로|이라고|이라는|이에요|이다|입니다|이라|이며|이고|처럼|에서|합니다|한다|하며|하고|하는|된다|됩니다|[은는이가을를과와의에로도])(?=$|[^가-힣]))"
TECHNICAL_TERM = re.compile(
    r"(?<![가-힣])(?:편관\s*\(\s*칠살\s*\)|칠살\s*\(\s*편관\s*\)|"
    + "|".join(r"\s*".join(term) for term in TERM_ALIASES if "(" not in term and len(term) > 1)
    + ")" + TERM_END
)
EDITORIAL_TERMS = re.compile(r"배우자궁|지장간|일간|[시일월연년][지간주]|천간(?!합)|지지|십성|오행")
SENTENCE_END = re.compile(r"[.!?。！？;；\n]+")
SYMBOLIC_RELATION = re.compile(
    r"([甲乙丙丁戊己庚辛壬癸]{2})\s*(合)|"
    r"([子丑寅卯辰巳午未申酉戌亥]{2,3})\s*\)?\s*(삼합|삼형|육합|육충|육해|合|沖|冲|害)"
)
SYMBOLIC_KINDS = {"沖": "육충", "冲": "육충", "害": "육해"}
PILLAR_NAMES = {"연": "year", "년": "year", "월": "month", "일": "day", "시": "hour"}
STEM_NAMES = dict(zip(STEM_ELEMENTS, "갑 을 병 정 무 기 경 신 임 계".split()))
STEM_KOREAN_ELEMENTS = dict(zip(("wood", "fire", "earth", "metal", "water"), "목화토금수"))
BRANCH_NAMES = dict(zip("子丑寅卯辰巳午未申酉戌亥", "자 축 인 묘 진 사 오 미 신 유 술 해".split()))
CHART_SYMBOLS = {
    symbol: {"reading": reading, "element": elements[symbol],
             "element_name": STEM_KOREAN_ELEMENTS[elements[symbol]]}
    for names, elements in ((STEM_NAMES, STEM_ELEMENTS), (BRANCH_NAMES, BRANCH_ELEMENTS))
    for symbol, reading in names.items()
}
UNKNOWN_HOUR_NOTICE = re.compile(
    r"\s*(?:은|는|이|가)?\s*(?:미상(?:입니다|이에요)?|확인되지 (?:않았습니다|않았어요)|"
    r"(?:미상이므로|확인되지 않았으므로),?\s*(?:이 해석은|이 설명은)\s*"
    r"확인된 (?:연주\s*[·,]\s*월주\s*[·,]\s*일주|세 기둥)(?:를|을) 바탕으로 "
    r"(?:합니다|한 해석입니다))\s*"
)
LIVE_SLOT = threading.BoundedSemaphore(1)
LOG = logging.getLogger("rs_gpt")


class ExperimentError(Exception):
    def __init__(self, code, message, status=502):
        super().__init__(message)
        self.code, self.status = code, status


class GroundingError(ExperimentError):
    def __init__(self, category, rule, **details):
        super().__init__("grounding", "원고의 형식 또는 명리 근거 검사를 통과하지 못했습니다.")
        self.diagnostic = {"category": category, "rule": rule, **details}


@lru_cache(maxsize=1)
def fixed_case():
    genders = {"a": "male", "b": "female"}
    result = analyze_preview(
        dict(year=1992, month=3, day=18, hour=None),
        dict(year=1992, month=4, day=30, hour=None), genders,
    )
    return evidence_payload(result, genders), result["report"]


def birth_payload(a, b, genders):
    result = analyze_pair(a, b)
    evidence = {}
    result["contexts"] = {
        owner: natal_context(chart, owner, evidence)
        for owner, chart in result["charts"].items()
    }
    result["interactions"] = cross_chart(result, evidence)
    result["evidence"] = evidence
    payload = evidence_payload(result, genders)
    for chart in payload["charts"].values():
        chart["pillars"] = {key: None if key in chart["unresolved"] else value
                            for key, value in chart["pillars"].items()}
        if "month" in chart["unresolved"]:
            chart["month_command"] = None
    return payload


def evidence_payload(result, genders):
    scopes = {owner: ctx["unresolved_pillars"] for owner, ctx in result["contexts"].items()}
    facts = {}
    for ref, fact in result["evidence"].items():
        if any(s.get("pillar") in scopes.get(s.get("person"), ())
               for s in fact.get("sources", [fact])):
            continue
        facts[ref] = {k: v for k, v in fact.items() if k != "year_month_alternatives"}
    for relation in result.get("relations", ()):
        owner = relation["scope"]
        if owner == "pair" or relation["kind"] not in {"삼형", "삼합", "육충", "천간합"}:
            continue
        sources = relation["sources"]
        if any(pillar in scopes[person] for person, pillar, _ in sources):
            continue
        kind = relation["kind"]
        key = ".".join(f"{person}.{pillar}" for person, pillar, _ in sources)
        facts[f"{owner}.{kind}.{key}"] = {
            "kind": kind, "layer": RULES[kind][0],
            "sources": [{"person": person, "pillar": pillar, "symbol": symbol}
                        for person, pillar, symbol in sources],
        }
    charts = {}
    for owner, other in (("a", "b"), ("b", "a")):
        chart = result["charts"][owner]
        context = result["contexts"][owner]
        master = chart["day_master"]
        charts[owner] = {"pillars": chart["pillars"], "day_master": master,
                         "element": STEM_ELEMENTS[master], "unresolved": scopes[owner],
                         "month_command": context["month_command"]}
        for ref, fact in facts.items():
            if fact.get("person") == owner and fact.get("layer") == "stem":
                fact["ten_god"] = ten_god(master, fact["symbol"])
        for placement in context["placements"]:
            if placement["id"] in facts:
                facts[placement["id"]]["ten_god"] = placement["ten_god"]
        tradition = PARTNER_ROLES.get(genders.get(owner))
        cross = f"pair.{owner}.reads.{other}"
        if tradition:
            category, roles = tradition
            facts[f"{owner}.partner"] = {
                "category": category, "traditional_roles": sorted(roles),
                "cross_ten_god": facts[cross]["ten_god"],
                "cross_is_partner_star": facts[cross]["ten_god"] in roles,
                "source_ids": [cross],
            }
        palace = next(p for p in context["placements"]
                      if p["pillar"] == "day" and p["tier"] == "본기")
        other_master = result["charts"][other]["day_master"]
        facts[f"{owner}.palace"] = {
            "branch": chart["pillars"]["day"][1], "principal_stem": palace["stem"],
            "ten_god": palace["ten_god"], "matches_other_day_master": palace["stem"] == other_master,
            "source_ids": [palace["id"], f"{other}.day.stem"],
        }
        facts[f"{other}.reads.{owner}.palace"] = {
            "perspective": other, "person": owner, "pillar": "day",
            "branch": chart["pillars"]["day"][1], "principal_stem": palace["stem"],
            "ten_god": ten_god(other_master, palace["stem"]),
            "source_ids": [palace["id"], f"{other}.day.stem"],
        }
    facts["pair.palaces"] = {
        "source_ids": ["a.palace", "b.palace"],
        "direct_branch_relation_ids": [
            ref for ref in result["interactions"] if ref in facts and facts[ref]["layer"] == "branch"
            and {s["pillar"] for s in facts[ref]["sources"]} == {"day"}
        ],
    }
    return {"charts": charts, "facts": facts}


def check_claims(prose, refs, chapter_refs, facts, people, position):
    """Match recognizable claims against typed facts and their named locations."""
    person = "|".join(re.escape(label) for label in sorted(people, key=len, reverse=True))
    owner_pattern = rf"(?P<person>{person})(?:의|은|는|이|가)?\s*"
    anchor_pattern = re.compile(owner_pattern + r"(?:(?P<pillar>[연년월일시])\s*(?P<layer>[간지주])|배우자궁)")
    owners = re.compile(owner_pattern)
    cited = [facts[ref] for ref in chapter_refs]
    previous_anchors = []
    previous_people = set()

    def reject(rule, sentence, term):
        raise GroundingError("evidence", rule, excerpt=sentence.strip(), terms=[term],
                             evidence_ids=refs, **position)

    for sentence in filter(str.strip, SENTENCE_END.split(prose)):
        for notation in SYMBOLIC_RELATION.finditer(sentence):
            stems, _, branches, label = notation.groups()
            kind = "천간합" if stems else (
                "삼합" if label == "合" and len(branches) == 3 else
                "육합" if label == "合" else SYMBOLIC_KINDS.get(label, label)
            )
            if not any(facts[ref].get("kind") == kind
                       and sorted(s["symbol"] for s in facts[ref].get("sources", ()))
                       == sorted(stems or branches) for ref in refs):
                reject("symbolic_relation_mismatch", sentence, notation[0])
        matches = list(anchor_pattern.finditer(sentence))
        locations = [(people[m["person"]], PILLAR_NAMES[m["pillar"]], m["layer"])
                     if m["pillar"] else (people[m["person"]], "day", "지") for m in matches]
        mentioned = {people[m["person"]] for m in owners.finditer(sentence)}
        grounded_locations = []
        for index, (owner, pillar, layer) in enumerate(locations):
            tail = sentence[matches[index].end():matches[index + 1].start() if index + 1 < len(matches) else None]
            placements = [f for f in facts.values() if f.get("person") == owner and f.get("pillar") == pillar]
            stem = next((f["symbol"] for f in placements if f.get("layer") == "stem"), None)
            branch = next((f["branch"] for f in placements if f.get("layer") == "hidden"), None)
            if stem is None:
                coverage = facts.get(f"{owner}.coverage", {}).get("unresolved_pillars", ())
                if (pillar == "hour" and layer == "주" and pillar in coverage
                        and UNKNOWN_HOUR_NOTICE.fullmatch(tail)):
                    continue
                reject("unresolved_pillar_claim", sentence, matches[index][0])
            grounded_locations.append((matches[index], (owner, pillar, layer)))
            stem_forms = {stem, STEM_NAMES[stem],
                          STEM_NAMES[stem] + STEM_KOREAN_ELEMENTS[STEM_ELEMENTS[stem]]}
            branch_forms = {branch, BRANCH_NAMES.get(branch)}
            pillar_forms = {stem + branch, STEM_NAMES[stem] + BRANCH_NAMES[branch]} if branch else set()
            expected = {"간": stem_forms, "지": branch_forms,
                        "주": stem_forms | branch_forms | pillar_forms}[layer]
            principal = re.match(r"\s*(?:의\s*)?본기", tail) if layer == "지" else None
            if principal:
                main = next(f["symbol"] for f in placements if f.get("tier") == "본기")
                expected = {main, STEM_NAMES[main],
                            STEM_NAMES[main] + STEM_KOREAN_ELEMENTS[STEM_ELEMENTS[main]]}
                tail = tail[principal.end():]
            readings = "".join(STEM_NAMES.values()) + "".join(BRANCH_NAMES.values())
            value = re.match(
                rf"\s*(?:(?:은|는|이|가)\s*|[:：]\s*)?(?:[‘“\(])?"
                rf"([{''.join(STEM_NAMES)}{''.join(BRANCH_NAMES)}]{{1,2}}|"
                rf"[{readings}](?:[목화토금수{readings}])?{TERM_END})", tail
            )
            # A role such as 정인 can also match the two-syllable reading
            # pattern. Leave the role to the scoped ten-god check below.
            if value and not TECHNICAL_TERM.match(tail, value.start(1)):
                hanja = re.match(r"\s*\(([甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥]{1,2})\)", tail[value.end():])
                if value[1] not in expected or (hanja and hanja[1] not in expected):
                    reject("pillar_symbol_mismatch", sentence, value[0] + (hanja[0] if hanja else ""))

        locations = [location for _, location in grounded_locations]
        terms = list(TECHNICAL_TERM.finditer(sentence))
        if locations or previous_anchors:
            terms += list(re.finditer(r"(?<![가-힣])(?:충|해)" + TERM_END, sentence))
        for match in sorted(terms, key=lambda m: m.start()):
            term = TERM_ALIASES[re.sub(r"\s+", "", match[0])]
            if term == "상관" and re.match(r"(?:이\s*)?\s*(?:없|있|없이|계수|관계)", sentence[match.end():].strip()):
                continue
            if term in RELATIONS:
                anchors = locations or (previous_anchors if not mentioned else [])
                participants = mentioned or (previous_people if anchors else set())
                if ("pair.palaces" in refs
                        and set(anchors) == {("a", "day", "지"), ("b", "day", "지")}
                        and re.match(r"\s*(?:이|가|은|는)?\s*없", sentence[match.end():])):
                    if any(facts[ref]["kind"] == term
                           for ref in facts["pair.palaces"]["direct_branch_relation_ids"]):
                        reject("direct_palace_relation_present", sentence, match[0])
                    continue
                candidates = [fact for fact in cited if fact.get("kind") == term]
                matching = [
                    fact for fact in candidates if all(
                        any(source["person"] == owner and source["pillar"] == pillar
                            and (layer == "주" or fact.get("layer") == {"간": "stem", "지": "branch"}[layer])
                            for source in fact.get("sources", ()))
                        for owner, pillar, layer in anchors
                    ) and participants <=
                    {source["person"] for source in fact.get("sources", ())}
                ]
            else:
                nearest = next((loc for anchor, loc in reversed(grounded_locations)
                                if anchor.end() <= match.start()), None)
                prefix = sentence[:match.start()]
                perspectives = list(re.finditer(owner_pattern + r"(?:에게|기준(?:으로)?|입장에서)", prefix))
                perspective = perspectives[-1] if perspectives else None
                if perspective:
                    viewer = people[perspective["person"]]
                    other = "b" if viewer == "a" else "a"
                    # Scope the claim to the latest viewer phrase, not earlier
                    # perspectives in the same sentence.
                    segment = sentence[perspective.end():match.start()]
                    palace_ref = f"{viewer}.reads.{other}.palace"
                    palace_fact = facts.get(palace_ref, {})
                    principal = palace_fact.get("principal_stem")
                    principal_forms = ({principal, STEM_NAMES.get(principal, "")}
                                       if principal else set())
                    has_principal = any(symbol and symbol in segment for symbol in principal_forms)
                    # An explicit palace mention in this viewer's clause is
                    # strongest; a preceding clause may establish shared
                    # palace context for a two-way comparison.
                    palace_context = ("배우자궁" in segment or "본기" in segment)
                    shared_palace_context = (
                        "배우자궁" in prefix[:perspective.start()]
                        and any(people[m["person"]] == other
                                for m in owners.finditer(segment))
                    )
                    palace_claim = bool(
                        palace_ref in chapter_refs and has_principal
                        and nearest != (other, "day", "간")
                        and (palace_context or shared_palace_context)
                        and (not nearest or nearest[:2] == (other, "day")
                             or shared_palace_context)
                    )
                    ref = palace_ref if palace_claim else f"pair.{viewer}.reads.{other}"
                    matching = [facts[ref]] if ref in chapter_refs and facts[ref].get("ten_god") == term else []
                else:
                    if nearest is None and not mentioned and len(previous_anchors) == 1:
                        nearest = previous_anchors[0]
                    prior_people = list(owners.finditer(prefix))
                    scoped = ({nearest[0]} if nearest else {people[prior_people[-1]["person"]]}
                              if prior_people else mentioned or previous_people)
                    matching = [
                        fact for fact in cited
                        if (fact.get("ten_god") == term or fact.get("cross_ten_god") == term)
                        and not (fact.get("principal_stem") and fact.get("perspective"))
                        and (not scoped or fact.get("person", fact.get("perspective")) in scoped)
                        and (nearest is None or (
                            fact.get("pillar") == nearest[1] and
                            (nearest[2] == "주" or fact.get("layer") ==
                             {"간": "stem", "지": "hidden"}[nearest[2]])
                            and (nearest[2] != "지" or fact.get("tier") == "본기"
                                 or ("지장간" in sentence and "본기" not in sentence))
                        ))
                    ]
            if not matching:
                scoped_claim = locations or mentioned or previous_anchors
                reject("scoped_fact_mismatch" if scoped_claim else "uncited_technical_term",
                       sentence, match[0])
        previous_anchors = locations
        previous_people = mentioned or (previous_people if not locations else set())


def validate(manuscript, facts, names=None, couple=None):
    """Check output structure, citations, and selected explicit technical terms."""
    if not isinstance(manuscript, dict) or set(manuscript) != {"chapters"}:
        raise GroundingError("structure", "report_fields")
    chapters = manuscript["chapters"]
    if not isinstance(chapters, list) or len(chapters) != 3:
        raise GroundingError("structure", "chapter_count", expected=3)
    seen = set()
    lengths = []
    editorial_failure = None
    people = {"첫째": "a", "둘째": "b"}
    people.update({f"{name}님": owner for owner, name in (names or {}).items()
                   if list(names.values()).count(name) == 1})
    for index, chapter in enumerate(chapters, 1):
        position = {"chapter": index}
        if not isinstance(chapter, dict) or set(chapter) != {"title", "paragraphs"}:
            raise GroundingError("structure", "chapter_fields", **position)
        title, paragraphs = chapter["title"], chapter["paragraphs"]
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 100:
            raise GroundingError("structure", "title_length", minimum=1, maximum=100, **position)
        if names:
            chapter["title"] = CHAPTER_PREFIX.sub("", title.strip())
            if not chapter["title"] or FORBIDDEN_ADDRESS.search(chapter["title"]):
                raise GroundingError("expression", "title_address_or_empty", excerpt=title, **position)
        minimum, maximum = EDITORIAL_PARAGRAPHS[index - 1] if names else (2, 6)
        if not isinstance(paragraphs, list) or not minimum <= len(paragraphs) <= maximum:
            raise GroundingError("structure", "paragraph_count", minimum=minimum,
                                 maximum=maximum, **position)
        lengths.append(0)
        chapter_refs = list(dict.fromkeys(
            ref for paragraph in paragraphs if isinstance(paragraph, dict)
            and isinstance(paragraph.get("evidence_ids"), list)
            for ref in paragraph["evidence_ids"] if isinstance(ref, str) and ref in facts
        ))
        for number, paragraph in enumerate(paragraphs, 1):
            position = {"chapter": index, "paragraph": number}
            if (not isinstance(paragraph, dict)
                    or set(paragraph) - PARAGRAPH_SCHEMA["properties"].keys()
                    or not {"text", "evidence_ids"} <= paragraph.keys()):
                raise GroundingError("structure", "paragraph_fields", **position)
            heading = paragraph.get("heading")
            if ((heading is not None and (not isinstance(heading, str)
                    or not 1 <= len(heading.strip()) <= 70 or "\n" in heading
                    or FORBIDDEN_ADDRESS.search(heading)))
                    or not isinstance(paragraph.get("emphasize_lead", False), bool)):
                raise GroundingError("structure", "paragraph_presentation", **position)
            prose, refs = paragraph["text"], paragraph["evidence_ids"]
            if not isinstance(prose, str) or not 30 <= len(prose.strip()) <= 1800:
                raise GroundingError("structure", "paragraph_length", minimum=30, maximum=1800,
                                     excerpt=prose, **position)
            lengths[-1] += len(prose)
            normalized = " ".join(prose.split())
            if normalized in seen:
                raise GroundingError("expression", "duplicate_paragraph", excerpt=prose, **position)
            seen.add(normalized)
            if not isinstance(refs, list) or not 1 <= len(refs) <= 12 or any(
                not isinstance(ref, str) or ref not in facts for ref in refs
            ):
                raise GroundingError("evidence", "invalid_evidence_ids", evidence_ids=refs, **position)
            check_claims(prose, refs, chapter_refs, facts, people, position)
            if names:
                sentences = [sentence for sentence in SENTENCE_END.split(prose) if sentence.strip()]
                if not 2 <= len(sentences) <= 4 or "\n" in prose or "\r" in prose:
                    raise GroundingError("structure", "sentence_count", minimum=2,
                                         maximum=4, **position)
                for sentence in SENTENCE_END.split(prose):
                    if FORBIDDEN_ADDRESS.search(sentence):
                        raise GroundingError("expression", "forbidden_address", excerpt=sentence.strip(),
                                             evidence_ids=refs, **position)
                    terms = EDITORIAL_TERMS.findall(sentence) + TECHNICAL_TERM.findall(sentence)
                    if len(terms) > 2 and editorial_failure is None:
                        editorial_failure = GroundingError("expression", "technical_term_density", excerpt=sentence.strip(),
                                             terms=terms, maximum=2, evidence_ids=refs, **position)
    if names:
        chapter_one = " ".join(p["text"] for p in chapters[0]["paragraphs"])
        if lengths[1] <= max(lengths[0], lengths[2]):
            raise GroundingError("expression", "chapter_two_not_longest", chapter=2, lengths=lengths)
        missing = [f"{name}님" for name in names.values() if f"{name}님" not in chapter_one]
        if missing:
            raise GroundingError("expression", "chapter_one_missing_names", chapter=1, expected=missing)
        required = {"a.palace", "b.palace", "pair.palaces",
                    "a.reads.b.palace", "b.reads.a.palace", "pair.a.reads.b", "pair.b.reads.a"}
        covered = {ref for p in chapters[1]["paragraphs"] for ref in p["evidence_ids"]}
        missing = sorted((required & facts.keys()) - covered)
        if missing:
            raise GroundingError("evidence", "chapter_two_missing_evidence", chapter=2,
                                 evidence_ids=missing)
    if couple:
        stories = [p["text"] for p in chapters[2]["paragraphs"]
                   if couple["work"] in p["text"] and couple["name"] in p["text"]]
        if not stories:
            raise GroundingError("expression", "selected_couple_missing", chapter=3,
                                 expected=[couple["work"], couple["name"]])
        if names and (len(stories) != 1 or
                      not 2 <= sum(bool(s.strip()) for s in SENTENCE_END.split(stories[0])) <= 3):
            raise GroundingError("structure", "selected_couple_length", chapter=3)
    if editorial_failure is not None:
        raise editorial_failure
    return {"paragraphs": len(seen), "checks": "형식·근거 ID·일부 명리 주장 통과"}


def usage_metrics(data, profile):
    if not isinstance(data, dict):
        return None
    input_tokens, output_tokens = data.get("input_tokens"), data.get("output_tokens")
    details = data.get("input_tokens_details")
    cached = details.get("cached_tokens", 0) if isinstance(details, dict) else 0
    if any(type(n) is not int or n < 0 for n in (input_tokens, output_tokens, cached)):
        return None
    if cached > input_tokens:
        return None
    input_rate, cached_rate, output_rate = profile["rates"]
    usd = ((input_tokens - cached) * input_rate + cached * cached_rate
           + output_tokens * output_rate) / 1_000_000
    return {"input_tokens": input_tokens, "cached_input_tokens": cached,
            "output_tokens": output_tokens, "estimated_usd": round(usd, 8)}


def request_openai(payload, profile, key, budget=None):
    body = {
        "model": profile["model"], "reasoning": {"effort": profile["effort"]},
        "service_tier": "default", "store": False, "max_output_tokens": MAX_OUTPUT_TOKENS,
        "instructions": INSTRUCTIONS, "input": json.dumps(payload, ensure_ascii=False),
        "text": {"format": {"type": "json_schema", "name": "rs_report", "strict": True,
                            "schema": SCHEMA}},
    }
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    if len(raw) > MAX_REQUEST_BYTES:
        raise ExperimentError("input_limit", "계산 근거가 요청 한도를 초과했습니다.")
    # The UTF-8 cap covers the text, instructions and schema. Allow 64k input
    # tokens for those bytes and provider framing, and reserve cache-write rates.
    input_rate, _, output_rate = profile["rates"]
    reservation = int(64_000 * (input_rate + 2.5) + MAX_OUTPUT_TOKENS * output_rate)
    request = Request("https://api.openai.com/v1/responses", raw,
                      {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with budget(reservation) if budget else nullcontext(), urlopen(request, timeout=90) as response:
            return json.loads(response.read(1_048_577))
    except HTTPError as exc:
        if exc.code == 429:
            raise ExperimentError("rate_limit", "OpenAI 요청 한도나 프로젝트 예산을 확인해 주세요.", 429) from None
        if exc.code in (401, 403):
            raise ExperimentError("auth", "서버의 OpenAI 키와 모델 권한을 확인해 주세요.") from None
        if exc.code == 404:
            raise ExperimentError("model_unavailable", "이 프로젝트에서 모델을 사용할 수 없습니다.") from None
        raise ExperimentError("provider", f"OpenAI 요청에 실패했습니다. 응답 상태 {exc.code}.") from None
    except (TimeoutError, URLError, OSError):
        raise ExperimentError("network", "OpenAI 연결이 지연되거나 끊겼습니다.", 504) from None
    except ValueError:
        raise ExperimentError("invalid_response", "OpenAI의 응답을 읽을 수 없습니다.") from None


def extract_report(response):
    if response.get("status") != "completed":
        raise ExperimentError("incomplete", "원고 생성이 중단됐습니다. 모델 설정과 출력 한도를 확인해 주세요.")
    content = [part for item in response.get("output", []) if item.get("type") == "message"
               for part in item.get("content", [])]
    if any(part.get("type") == "refusal" for part in content):
        raise ExperimentError("refused", "모델이 원고 생성을 거절했습니다.")
    try:
        original = "".join(part["text"] for part in content if part.get("type") == "output_text")
        return json.loads(original), original
    except (ValueError, KeyError, TypeError):
        raise ExperimentError("invalid_response", "모델 원고의 형식을 읽을 수 없습니다.") from None


def run_report(profile_id, mode, live_enabled=False, budget=None, payload=None, on_grounding_failure=None):
    if not isinstance(profile_id, str) or profile_id not in PROFILES or mode not in ("mock", "live"):
        raise ExperimentError("input", "모델 설정과 실행 방식을 선택해 주세요.", 400)
    if payload is None:
        payload, _ = fixed_case()
    profile = PROFILES[profile_id]
    metrics = {"latency_ms": None, "usage": None}
    status = "ok"
    grounding_rule = None
    acquired = False
    try:
        if mode == "mock":
            reports = json.loads((ROOT / "rs_gpt_mock.json").read_text(encoding="utf-8"))
            manuscript = reports[profile_id]
        else:
            key = os.environ.get("OPENAI_API_KEY")
            if not live_enabled or not key:
                raise ExperimentError("disabled", "이 서버에서 실호출을 사용할 수 없습니다.", 503)
            acquired = LIVE_SLOT.acquire(blocking=False)
            if not acquired:
                raise ExperimentError("busy", "다른 원고를 작성 중입니다. 잠시 뒤 다시 시도해 주세요.", 429)
            started = time.perf_counter()
            try:
                response = request_openai(payload, profile, key, budget)
            finally:
                metrics["latency_ms"] = round((time.perf_counter() - started) * 1000)
            if not isinstance(response, dict):
                raise ExperimentError("invalid_response", "OpenAI의 응답을 읽을 수 없습니다.")
            metrics["usage"] = usage_metrics(response.get("usage"), profile)
            if isinstance(response.get("model"), str):
                metrics["response_model"] = response["model"]
            manuscript, original = extract_report(response)
        try:
            audit = validate(manuscript, payload["facts"], payload.get("names"), payload.get("couple"))
        except GroundingError as exc:
            grounding_rule = exc.diagnostic["rule"]
            if mode == "live" and on_grounding_failure is not None:
                on_grounding_failure({
                    "original": original, "failure": exc.diagnostic,
                    "reference": {key: payload[key] for key in ("charts", "facts", "couple")
                                  if key in payload},
                })
            raise
        return {**manuscript, "audit": audit, "mode": mode, "profile": profile_id,
                "model": profile["model"], "effort": profile["effort"], "metrics": metrics}
    except ExperimentError as exc:
        status = exc.code
        exc.metrics = metrics
        raise
    except Exception:
        status = "internal"
        raise
    finally:
        if acquired:
            LIVE_SLOT.release()
        LOG.info("%s", json.dumps({"event": "rs_report", "profile": profile_id,
                                   "mode": mode, "status": status, **metrics,
                                   **({"grounding_rule": grounding_rule} if grounding_rule else {})}))

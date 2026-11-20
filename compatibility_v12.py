"""Evidence-linked Korean reports. This module has no service entry points."""

import re
from collections import Counter

from compatibility_v11 import (
    BRANCH_ELEMENTS, GEN, PILLARS, STEM_ELEMENTS, SUPPORT, analyze_pair as analyze_v11,
    ten_god,
)

POSITION = dict(zip(PILLARS, ("연주", "월주", "일주", "시주")))
EDITORIAL_WEIGHT = dict(zip(PILLARS, (1, 3, 4, 2)))
PEOPLE = {"a": "첫째 사람", "b": "둘째 사람"}
ELEMENT = dict(zip(("wood", "fire", "earth", "metal", "water"), "목화토금수"))
SEASONS = dict(zip("寅卯辰巳午未申酉戌亥子丑", ("봄",) * 3 + ("여름",) * 3 + ("가을",) * 3 + ("겨울",) * 3))
# Explicit tiers. Storage branches do not all follow the v1.1 member order.
HIDDEN_ORDER = dict(zip("子丑寅卯辰巳午未申酉戌亥", (
    "癸", "己辛癸", "甲丙戊", "乙", "戊癸乙", "丙庚戊",
    "丁己", "己乙丁", "庚壬戊", "辛", "戊丁辛", "壬甲",
)))
TIERS = ("본기", "중기", "여기")
READINGS = dict(zip("甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥", "갑을병정무기경신임계자축인묘진사오미신유술해"))
PRACTICE = {
    "천간합": "상대가 한 말을 내 말로 짧게 되짚고, 내가 이해한 뜻이 맞는지 물어보세요.",
    "육합": "둘 다 편하다고 답한 방식이 있다면 이번에 한 번 그대로 해 보세요.",
    "삼합": "함께할 시간과 장소, 각자 할 일 가운데 먼저 정해야 할 것부터 골라 보세요.",
    "육충": "의견이 갈리면 오늘 꼭 결정해야 하는 것부터 하나만 골라 보세요.",
    "상형": "각자 당연하다고 여긴 기준을 하나씩 말해 보세요. 먼저 들은 사람이 그 기준을 짧게 되짚어 줘도 좋습니다.",
    "삼형": "한 번에 결정하기 어려우면 사람, 일정, 장소 중 어디부터 바꿀 수 있는지 살펴보세요.",
    "자형": "같은 말이 다시 나오면 잠깐 쉬었다가 앞에서 미처 답하지 못한 질문 하나만 꺼내 보세요.",
    "육해": "도움을 주기 전에 “내가 해 주면 편할까, 그냥 들어 주면 좋을까?”라고 물어보세요.",
}
GOD_QUESTIONS = {
    "비견": "어디까지는 각자 정하면 좋겠어?", "겁재": "이번에는 누가 먼저 정해 볼까?",
    "식신": "지금 내가 해 주면 기분 좋을 작은 일이 있어?", "상관": "말하기 어려워서 미뤄 둔 이야기가 있어?",
    "편재": "아직 떠올려 보지 않은 선택지도 있을까?", "정재": "이번에 서로 시간이나 돈을 얼마나 쓰면 편할까?",
    "편관": "지금 맡은 일 중에 같이 나누고 싶은 게 있어?", "정관": "이번에 서로 꼭 지키고 싶은 약속은 뭐야?",
    "편인": "생각을 더 정리할 시간이 필요해?", "정인": "지금은 어떤 도움을 받으면 마음이 놓일 것 같아?",
}
SCENES = {
    "day": ("둘이 쉬는 방식이 다를 때", "오늘은 같이 쉬고 싶어, 각자 쉬고 싶어?"),
    "month": ("바쁜 주에 일정을 맞출 때", "이번 주에 꼭 지키고 싶은 일정이 있어?"),
    "year": ("서로의 가까운 사람들을 만날 때", "이번 모임에서 내가 미리 알면 좋을 게 있어?"),
    "hour": ("앞으로의 계획을 꺼낼 때", "지금 정하고 싶은 것과 조금 더 두고 볼 것은 뭐야?"),
}
GOD_LENS = {
    "비견": "서로의 선택을 존중할 여지", "겁재": "누가 먼저 결정을 내릴지",
    "식신": "작은 행동으로 마음을 전하는 법", "상관": "걸리는 점을 말로 꺼내는 법",
    "편재": "새로운 선택지를 함께 살피는 일", "정재": "시간이나 돈을 꾸준히 나누어 쓰는 법",
    "편관": "급한 일을 맡을 때 생기는 부담", "정관": "서로 지키고 싶은 약속",
    "편인": "각자 생각을 정리할 시간", "정인": "어떤 도움을 받으면 마음이 놓이는지",
}
RELATION_LENS = {
    "천간합": "말을 꺼냈을 때 상대가 그 뜻을 이어받는 장면",
    "육합": "익숙한 일을 두 사람이 손발을 맞춰 처리하는 장면",
    "삼합": "여러 조건이 맞을 때 함께 일이 풀리는 장면",
    "육충": "서로 당연하게 여긴 방식이 정면으로 엇갈리는 순간",
    "상형": "같은 일을 두고 서로의 기준을 자꾸 확인하게 되는 순간",
    "삼형": "한 가지 사정만 바꿔도 해결되기 어려워 보이는 순간",
    "자형": "비슷한 반응을 주고받다가 같은 이야기가 되풀이되는 순간",
    "육해": "한쪽의 배려가 상대에게는 다르게 전해지는 순간",
}
TRANSLATION_MARKERS = ("측면에 있어서", "상호 간에 있어", "관점에 입각하여", "그것은 의미합니다", "가지는 경향성을 보입니다")


def natal_context(chart, owner, evidence):
    """Record the observed placements and references for one chart."""
    placements = []
    visible = {}
    for position, detail in chart["details"].items():
        stem = detail["stem"]
        ref = f"{owner}.{position}.stem"
        evidence[ref] = {"person": owner, "pillar": position, "layer": "stem", "symbol": stem}
        visible.setdefault(stem, []).append(ref)
        branch = detail["branch"]
        for tier, hidden in zip(TIERS, HIDDEN_ORDER[branch]):
            ref = f"{owner}.{position}.hidden.{hidden}"
            evidence[ref] = {
                "person": owner, "pillar": position, "layer": "hidden", "symbol": hidden,
                "branch": branch, "tier": tier,
            }
            placements.append({
                "id": ref, "pillar": position, "tier": tier, "stem": hidden,
                "ten_god": ten_god(chart["day_master"], hidden),
            })
    # A hidden stem can surface in a later pillar as well as in its own pillar.
    for placement in placements:
        placement["exposed_at"] = list(visible.get(placement["stem"], ()))

    roots = {}
    for stem in visible:
        exact = [p["id"] for p in placements if p["stem"] == stem]
        same_element = [
            p["id"] for p in placements
            if p["stem"] != stem and STEM_ELEMENTS[p["stem"]] == STEM_ELEMENTS[stem]
        ]
        roots[stem] = {"exact": exact, "same_element_other_polarity": same_element}

    season = None
    if month := chart["details"].get("month"):
        branch = month["branch"]
        element = BRANCH_ELEMENTS[branch]
        day_element = STEM_ELEMENTS[chart["day_master"]]
        season = {
            "branch": branch, "season": SEASONS[branch], "branch_element": element,
            "day_master_element": day_element,
            "same_element": element == day_element, "generates_day_master": GEN[element] == day_element,
            "principal_id": f"{owner}.month.hidden.{HIDDEN_ORDER[branch][0]}",
        }
    unresolved = [p for p in PILLARS if chart["pillars"][p] is None]
    evidence[f"{owner}.coverage"] = {
        "person": owner, "kind": "확정 범위", "unresolved_pillars": unresolved,
        "year_month_alternatives": chart["year_month_alternatives"],
        "examined_hidden_ids": [p["id"] for p in placements],
    }
    return {"month_command": season, "placements": placements, "roots": roots,
            "unresolved_pillars": unresolved}


def cross_chart(base, evidence):
    interactions = []
    for relation in base["relations"]:
        if relation["scope"] != "pair":
            continue
        kind = relation["kind"]
        layer = "stem" if kind == "천간합" else "branch"
        sources = []
        for owner, position, symbol in relation["sources"]:
            stem = symbol if layer == "stem" else HIDDEN_ORDER[symbol][0]
            other = "b" if owner == "a" else "a"
            sources.append({
                "person": owner, "pillar": position, "symbol": symbol, "read_stem": stem,
                "owner_ten_god": ten_god(base["charts"][owner]["day_master"], stem),
                "other_ten_god": ten_god(base["charts"][other]["day_master"], stem),
                "source_id": f"{owner}.{position}.stem" if layer == "stem"
                else f"{owner}.{position}.hidden.{stem}",
            })
        key = ".".join(f"{s['person']}.{s['pillar']}" for s in sources)
        ref = f"pair.{kind}.{key}"
        evidence[ref] = {"kind": kind, "layer": layer, "sources": sources}
        interactions.append(ref)

    for viewer, other in (("a", "b"), ("b", "a")):
        ref = f"pair.{viewer}.reads.{other}"
        evidence[ref] = {
            "kind": "일간 교차 십성", "perspective": viewer,
            "ten_god": ten_god(base["charts"][viewer]["day_master"], base["charts"][other]["day_master"]),
            "source_ids": [f"{viewer}.day.stem", f"{other}.day.stem"],
        }
    return interactions


def interpretation_plan(contexts, interactions, evidence):
    ranked = sorted(interactions, key=lambda ref: (
        -sum(EDITORIAL_WEIGHT[s["pillar"]] for s in evidence[ref]["sources"]) / len(evidence[ref]["sources"]),
        -len(evidence[ref]["sources"]), ref,
    ))
    lead = ranked[0] if ranked else None
    counterpoint = next((
        ref for ref in sorted(ranked[1:], key=lambda ref: not bool(
            {s["source_id"] for s in evidence[ref]["sources"]}
            & {s["source_id"] for s in evidence[lead]["sources"]}
        ))
        if (evidence[ref]["kind"] in SUPPORT) != (evidence[lead]["kind"] in SUPPORT)
    ), None)
    day_reads = ["pair.a.reads.b", "pair.b.reads.a"]
    positions = {s["pillar"] for s in evidence[lead]["sources"]} if lead else set()
    scene = max(positions - {"day"}, key=EDITORIAL_WEIGHT.get, default="day")
    return {
        "individual": {
            owner: {"month_id": c["month_command"]["principal_id"] if c["month_command"] else None,
                    "root_ids": sorted(c["roots"][evidence[f"{owner}.day.stem"]["symbol"]]["exact"],
                                       key=lambda ref: (TIERS.index(evidence[ref]["tier"]),
                                                        -EDITORIAL_WEIGHT[evidence[ref]["pillar"]])),
                    "focus_id": next((
                        p["id"] for p in sorted(c["placements"], key=lambda p: (
                            p["pillar"] != "month", not p["exposed_at"],
                            TIERS.index(p["tier"]), -EDITORIAL_WEIGHT[p["pillar"]],
                        )) if p["pillar"] == "month" or p["pillar"] == "day"
                    ), None),
                    "coverage_id": f"{owner}.coverage",
                    "unresolved_pillars": c["unresolved_pillars"]}
            for owner, c in contexts.items()
        },
        "relationship": {"lead_id": lead, "counterpoint_id": counterpoint, "direction_ids": day_reads},
        "practice": {
            "scene": scene,
            "evidence_ids": [lead, day_reads[0]] if lead else day_reads,
        },
    }


def _paragraph(text, ids):
    return {"text": text, "evidence_ids": list(dict.fromkeys(ids))}


def _read(symbol):
    return f"{READINGS[symbol]}({symbol})"


def _individual(owner, context, plan, evidence):
    day_id = f"{owner}.day.stem"
    ids = [day_id, plan["coverage_id"]]
    label = PEOPLE[owner]
    month = context["month_command"]
    if month:
        principal = evidence[plan["month_id"]]
        element = ELEMENT[month["branch_element"]]
        text = (f"{label}의 월지는 {month['season']}에 속하는 {_read(month['branch'])}이며, "
                f"본기 {_read(principal['symbol'])}의 오행은 {element}입니다.")
        if month["same_element"]:
            text += f" {label}의 일간도 월지 본기와 같은 {element}에 속합니다."
        elif month["generates_day_master"]:
            text += f" {label}의 일간은 월지 본기에서 생을 받는 오행에 속합니다."
        ids.append(plan["month_id"])
    else:
        text = f"{label}의 월주는 출생 시각에 따라 달라집니다. 절입 전후의 월주 후보를 함께 기록했습니다."
    if plan["root_ids"]:
        root_id = plan["root_ids"][0]
        root = evidence[root_id]
        text += (f" {label}의 일간과 같은 {_read(root['symbol'])} 글자는 "
                 f"{POSITION[root['pillar']]} 지지 {_read(root['branch'])}에도 {root['tier']}로 들어 있습니다.")
        ids.append(root_id)
    else:
        stem = evidence[day_id]["symbol"]
        text += f" {label}의 확정된 지지에서는 일간과 같은 {_read(stem)} 글자를 찾을 수 없습니다."
    if month:
        placement = next(p for p in context["placements"] if p["id"] == plan["month_id"])
        alternate = next((p for p in context["placements"]
                          if p["pillar"] == "month" and p["id"] != plan["month_id"] and p["exposed_at"]), None)
        surfaced = placement if placement["exposed_at"] else alternate
        if surfaced:
            ref = surfaced["exposed_at"][0]
            text += f" {label}의 월지에 들어 있는 {_read(surfaced['stem'])} 글자는 {POSITION[evidence[ref]['pillar']]} 천간에도 드러납니다."
            ids.extend((surfaced["id"], ref))

    if focus_id := plan["focus_id"]:
        focus = next(p for p in context["placements"] if p["id"] == focus_id)
        text += (f" {label}의 {POSITION[focus['pillar']]}에 든 {_read(focus['stem'])} 글자를 "
                 f"일간에서 보면 {focus['ten_god']}이므로 "
                 f"‘{GOD_LENS[focus['ten_god']]}’라는 주제로 읽어 볼 수 있습니다.")
        ids.append(focus_id)
    return _paragraph(text, ids)


def _interaction_text(fact):
    places = "·".join(f"{PEOPLE[s['person']]} {POSITION[s['pillar']]} {_read(s['symbol'])}" for s in fact["sources"])
    kind = fact["kind"]
    return f"{places}에서 {kind} 조합이 나타납니다. 떠올려 볼 장면은 ‘{RELATION_LENS[kind]}’입니다."


def render_report(contexts, plan, evidence):
    individual = [_individual(owner, context, plan["individual"][owner], evidence)
                  for owner, context in contexts.items()]
    missing = [owner for owner, context in contexts.items() if "hour" in context["unresolved_pillars"]]
    if missing:
        names = "·".join(PEOPLE[owner] for owner in missing)
        individual.append(_paragraph(
            f"{names}의 출생 시각을 몰라 해당 시주는 해석에서 뺐습니다.",
            [f"{owner}.coverage" for owner in missing],
        ))
    relationship = plan["relationship"]
    first, second = relationship["direction_ids"]
    god_a, god_b = (evidence[ref]["ten_god"] for ref in (first, second))
    meeting = []
    if lead := relationship["lead_id"]:
        meeting.append(_paragraph(_interaction_text(evidence[lead]), [lead]))
    if counterpoint := relationship["counterpoint_id"]:
        fact = evidence[counterpoint]
        places = "·".join(f"{PEOPLE[s['person']]} {POSITION[s['pillar']]} {_read(s['symbol'])}" for s in fact["sources"])
        meeting.append(_paragraph(
            f"{places}에는 {fact['kind']}도 있습니다. 여기서 살필 대목은 ‘{RELATION_LENS[fact['kind']]}’입니다.",
            [counterpoint],
        ))
    if god_a == god_b:
        lens = f"일간끼리 읽으면 두 사람 모두 {god_a}입니다. 함께 나눠 볼 이야기는 ‘{GOD_LENS[god_a]}’입니다."
    else:
        lens = (f"첫째 사람에게 둘째의 일간은 {god_a}, 둘째 사람에게 첫째의 일간은 {god_b}입니다. "
                f"대화에서 첫째가 살펴볼 주제는 ‘{GOD_LENS[god_a]}’, 둘째가 살펴볼 주제는 ‘{GOD_LENS[god_b]}’입니다.")
    meeting.append(_paragraph(lens, [first, second]))
    scene, question = SCENES[plan["practice"]["scene"]]
    practice = (f"{scene}, “{question}” 하고 물어보세요. "
                f"이어서 “{GOD_QUESTIONS[god_a]}”라고 물어도 좋습니다.")
    if lead:
        practice += " " + PRACTICE[evidence[lead]["kind"]]
    return [
        {"title": "각자의 명식에서 읽히는 것", "paragraphs": individual},
        {"title": "두 사람의 명식이 만나는 자리", "paragraphs": meeting},
        {"title": "일상에서 나눠 볼 이야기",
         "paragraphs": [_paragraph(practice, plan["practice"]["evidence_ids"])]},
    ]


def review_report(chapters, evidence):
    paragraphs = [p for c in chapters for p in c["paragraphs"]]
    body = " ".join(p["text"] for p in paragraphs)
    sentences = re.split(r"(?<=[.!?])\s+", body)
    repeated = sorted(s for s, count in Counter(sentences).items() if s and count > 1)
    unresolved = sorted({ref for p in paragraphs for ref in p["evidence_ids"] if ref not in evidence})
    unlinked = sum(not p["evidence_ids"] for p in paragraphs)
    markers = [phrase for phrase in TRANSLATION_MARKERS if phrase in body]
    return {"paragraph_count": len(paragraphs), "unlinked_paragraphs": unlinked,
            "unresolved_ids": unresolved, "repeated_sentences": repeated, "translation_markers": markers}


def analyze_pair(a, b):
    """Return JSON-ready chart facts, interpretation plan, report, and editorial checks."""
    base = analyze_v11(a, b)
    evidence = {}
    contexts = {owner: natal_context(chart, owner, evidence) for owner, chart in base["charts"].items()}
    interactions = cross_chart(base, evidence)
    plan = interpretation_plan(contexts, interactions, evidence)
    report = render_report(contexts, plan, evidence)
    return {"version": "1.2", "charts": base["charts"], "contexts": contexts,
            "interactions": interactions, "evidence": evidence, "plan": plan, "report": report,
            "review": review_report(report, evidence),
            "limitation": "전통 명리의 상징을 바탕으로 구성한 대화 제안입니다. 실제 성격이나 관계의 미래를 예측할 수 없습니다."}


def report_markdown(result):
    chapters = []
    for number, chapter in enumerate(result["report"], 1):
        body = "\n\n".join(p["text"] for p in chapter["paragraphs"])
        chapters.append(f"## {number}장. {chapter['title']}\n\n{body}")
    return "\n\n".join([*chapters, result["limitation"]]) + "\n"

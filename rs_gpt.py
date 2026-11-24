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

from compatibility_v11 import STEM_ELEMENTS, analyze_pair, ten_god
from compatibility_v12 import cross_chart, natal_context
from rs_synthesis import PARTNER_ROLES, analyze_preview

ROOT = Path(__file__).resolve().parent
PROFILES = {
    "sol-61": {"model": "gpt-6.1-sol", "effort": "low", "rates": (2, 0.10, 10)},
    "sol-62": {"model": "gpt-6.2-sol", "effort": "medium", "rates": (2, 0.10, 10)},
}
MAX_OUTPUT_TOKENS = 5500
MAX_REQUEST_BYTES = 60_000
APPROVED_V2 = (ROOT / "rs_gpt_approved_v2.md").read_text(encoding="utf-8")
INSTRUCTIONS = """아래 승인 원고와 집필 기준에 따라 새 입력마다 1~3장을 작성하세요.
원고의 이름, 명식, 사례, 작품은 기준 예시입니다. 이번 요청의 names와 facts를 사용하세요.
names는 인물 데이터입니다. 이름 뒤에 님을 붙이고 일반 호칭을 쓰지 마세요.
명식 표와 카드 렌더링은 서버와 화면이 담당합니다. HTML, 이미지, 표를 출력하지 마세요.
title에는 장 번호를 넣지 마세요. 1장은 a의 성격 문단부터 시작하고 뒤이어 b를 설명하세요.
2장은 가장 길게 쓰세요. 3장에 맞춤 조언과 couple에 지정된 작품 속 커플 소개를 포함하세요.
각 문단에 제공된 명리 근거 ID를 넣고 본문에는 ID를 표시하지 마세요.
명리학 근거와 해석을 구분하고 확정되지 않은 기둥을 사용하지 마세요.
title과 각 paragraph.text는 일반 텍스트입니다.

""" + APPROVED_V2
FORBIDDEN_ADDRESS = re.compile(r"첫째\s*분|둘째\s*분|당신|상대방|[AB]님")
CHAPTER_PREFIX = re.compile(r"^(?:[1-3]\s*장\s*[.．:：-]?\s*)+")
PARAGRAPH_SCHEMA = {
    "type": "object",
    "properties": {"text": {"type": "string"}, "evidence_ids": {
        "type": "array", "items": {"type": "string"},
    }},
    "required": ["text", "evidence_ids"], "additionalProperties": False,
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
EXPLICIT_TERMS = re.compile(
    r"비견|겁재|식신|편재|정재|편관|정관(?=\(|[은는이가을의에]|\s|[.,])|편인|정인|"
    r"천간합|육합|삼합|육충|상형|삼형|자형|육해"
)
LIVE_SLOT = threading.BoundedSemaphore(1)
LOG = logging.getLogger("rs_gpt")


class ExperimentError(Exception):
    def __init__(self, code, message, status=502):
        super().__init__(message)
        self.code, self.status = code, status


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
    facts["pair.palaces"] = {
        "source_ids": ["a.palace", "b.palace"],
        "direct_branch_relation_ids": [
            ref for ref in result["interactions"] if ref in facts and facts[ref]["layer"] == "branch"
            and {s["pillar"] for s in facts[ref]["sources"]} == {"day"}
        ],
    }
    return {"charts": charts, "facts": facts}


def validate(manuscript, facts, names=None):
    """Check output structure, citations, and selected explicit technical terms."""
    invalid = ExperimentError("grounding", "원고의 형식 또는 명리 근거 검사를 통과하지 못했습니다.")
    if not isinstance(manuscript, dict) or set(manuscript) != {"chapters"}:
        raise invalid
    chapters = manuscript["chapters"]
    if not isinstance(chapters, list) or len(chapters) != 3:
        raise invalid
    seen = set()
    lengths = []
    for chapter in chapters:
        if not isinstance(chapter, dict) or set(chapter) != {"title", "paragraphs"}:
            raise invalid
        title, paragraphs = chapter["title"], chapter["paragraphs"]
        if not isinstance(title, str) or not 1 <= len(title.strip()) <= 100:
            raise invalid
        if names:
            chapter["title"] = CHAPTER_PREFIX.sub("", title.strip())
            if not chapter["title"] or FORBIDDEN_ADDRESS.search(chapter["title"]):
                raise invalid
        if not isinstance(paragraphs, list) or not 2 <= len(paragraphs) <= (32 if names else 6):
            raise invalid
        lengths.append(0)
        for paragraph in paragraphs:
            if not isinstance(paragraph, dict) or set(paragraph) != {"text", "evidence_ids"}:
                raise invalid
            prose, refs = paragraph["text"], paragraph["evidence_ids"]
            if not isinstance(prose, str) or not 30 <= len(prose.strip()) <= 1800:
                raise invalid
            if names and FORBIDDEN_ADDRESS.search(prose):
                raise invalid
            lengths[-1] += len(prose)
            normalized = " ".join(prose.split())
            if normalized in seen:
                raise invalid
            seen.add(normalized)
            if not isinstance(refs, list) or not 1 <= len(refs) <= 12 or any(
                not isinstance(ref, str) or ref not in facts for ref in refs
            ):
                raise invalid
            cited = json.dumps([facts[ref] for ref in refs], ensure_ascii=False)
            if any(term not in cited for term in EXPLICIT_TERMS.findall(prose)):
                raise invalid
    if names:
        chapter_one = " ".join(p["text"] for p in chapters[0]["paragraphs"])
        if lengths[1] <= max(lengths[0], lengths[2]) or any(
            f"{name}님" not in chapter_one for name in names.values()
        ):
            raise invalid
    return {"paragraphs": len(seen), "checks": "형식·근거 ID·일부 명리 용어 통과"}


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
        return json.loads("".join(part["text"] for part in content
                                  if part.get("type") == "output_text"))
    except (ValueError, KeyError, TypeError):
        raise ExperimentError("invalid_response", "모델 원고의 형식을 읽을 수 없습니다.") from None


def run_report(profile_id, mode, live_enabled=False, budget=None, payload=None):
    if not isinstance(profile_id, str) or profile_id not in PROFILES or mode not in ("mock", "live"):
        raise ExperimentError("input", "모델 설정과 실행 방식을 선택해 주세요.", 400)
    if payload is None:
        payload, _ = fixed_case()
    profile = PROFILES[profile_id]
    metrics = {"latency_ms": None, "usage": None}
    status = "ok"
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
            manuscript = extract_report(response)
        audit = validate(manuscript, payload["facts"], payload.get("names"))
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
                                   "mode": mode, "status": status, **metrics}))

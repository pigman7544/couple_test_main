"""Offline editorial candidate for the twenty fixed review inputs."""

import json
from pathlib import Path

from compatibility_editorial import build_brief
from compatibility_editorial_prose import NAMES, POSITIONS, references
from compatibility_v11 import ten_god
from compatibility_v12 import _paragraph, analyze_pair as analyze_facts, review_report

DIRECTORY = Path(__file__).parent / "docs" / "compatibility-editorial"
FIXED_PAIRS = DIRECTORY / "pairs.json"
SCENARIOS = DIRECTORY / "round2-scenarios.json"

RELATION = {
    "same_sources": "같은 글자에서 접점과 마찰을 함께 읽습니다.",
    "same_slots": "같은 기둥에서 천간의 합과 지지의 긴장이 층을 달리합니다.",
    "partial": "두 작용에 함께 들어가는 자리는 {shared}입니다.",
    "separate": "접점과 마찰의 자리는 서로 떨어져 있습니다.",
}


def sources(card):
    return "·".join(
        f"{NAMES[s['person']]} {POSITIONS[s['pillar']]} {s['symbol']}"
        for s in card["sources"]
    )


def individual(finding, evidence, month_id):
    owner = finding["owner"]
    day_id = f"{owner}.day.stem"
    lead = evidence[finding["lead"]]
    refs = [day_id, finding["lead"]]
    location = POSITIONS[lead["pillar"]]
    text = (f"{NAMES[owner]}의 일간 {evidence[day_id]['symbol']}에서 보면 "
            f"{location} 지지 속 {lead['symbol']} 글자는 {finding['role']}입니다.")
    if finding["exposed"]:
        visible = "·".join(POSITIONS[evidence[ref]["pillar"]] for ref in finding["exposed"])
        text += f" {lead['symbol']} 글자는 {visible} 천간에도 드러납니다."
        refs.extend(finding["exposed"])
    if finding["repeated"]:
        repeated = "·".join(POSITIONS[evidence[ref]["pillar"]] for ref in finding["repeated"])
        text += f" 같은 글자는 {repeated} 지지에서도 확인됩니다."
        refs.extend(finding["repeated"])
    if month_id:
        month = evidence[month_id]
        if month_id == finding["lead"]:
            text = text.replace("지지 속", "지지의 본기인", 1)
        else:
            text += f" 월지의 본기인 {month['symbol']} 글자는 {ten_god(evidence[day_id]['symbol'], month['symbol'])}입니다."
        refs.append(month_id)
    if (alt := finding["alternative"]) and alt != month_id:
        card = evidence[alt]
        text += (f" {POSITIONS[card['pillar']]} 지지에 든 {card['symbol']} 글자에서는 "
                 f"{finding['alternative_role']}의 단서도 읽습니다.")
        refs.append(alt)
    if finding["missing"]:
        missing = "·".join(POSITIONS[p] for p in finding["missing"])
        text += f" {missing} 정보가 미확정이라 확인된 위치까지만 읽었습니다."
        refs.append(f"{owner}.coverage")
    return _paragraph(text, refs)


def relationship(brief, evidence):
    support, tension = brief["support"], brief["tension"]
    a, b = brief["directions"]
    day_ids = ["a.day.stem", "b.day.stem"]
    a_day, b_day = (evidence[ref]["symbol"] for ref in day_ids)
    cross = (f"두 일간을 교차해서 읽으면 첫째({a_day})가 읽는 둘째({b_day})는 {a['role']}, "
             f"둘째가 읽는 첫째는 {b['role']}입니다.")
    refs = [*day_ids, a["id"], b["id"]]
    clauses = [cross]
    if support:
        clauses.append(f"{sources(support)}에는 {support['kind']} 관계가 있습니다.")
        refs.extend(references(support))
    if tension:
        clauses.append(f"{sources(tension)}에서는 {tension['kind']} 관계도 읽습니다.")
        refs.extend(references(tension))
    if support and tension:
        shared = "·".join(
            f"{NAMES[owner]} {POSITIONS[slot]}" for owner, slot in brief["shared_slots"]
        )
        clauses.append(RELATION[brief["scope"]].format(shared=shared))
    contrast = brief["contrast"]
    if contrast:
        source = contrast["source"]
        first, second = contrast["roles"]
        location = f"{NAMES[source['person']]} {POSITIONS[source['pillar']]}"
        layer = "천간" if (tension or support)["layer"] == "stem" else "지지 본기"
        clauses.append(f"{location} {layer} {source['read_stem']} 글자는 "
                       f"첫째에게 {first}, 둘째에게 {second}입니다.")
        refs.append(source["source_id"])
    return _paragraph(" ".join(clauses), refs)


def generate_packet():
    pairs = json.loads(FIXED_PAIRS.read_text(encoding="utf-8"))
    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    for pair, scenario in zip(pairs, scenarios, strict=True):
        base = analyze_facts(*pair["births"])
        brief = build_brief(base)
        if json.loads(json.dumps(brief)) != pair["after"]["plan"]:
            raise ValueError(f"Editorial evidence changed for pair {pair['pair']}")
        evidence = base["evidence"]
        natal = []
        for finding in brief["natal"]:
            command = base["contexts"][finding["owner"]]["month_command"]
            natal.append(individual(finding, evidence, command["principal_id"] if command else None))
        dynamics = relationship(brief["relationship"], evidence)
        all_refs = [ref for p in [*natal, dynamics] for ref in p["evidence_ids"]]
        report = [
            {"title": "각자가 중요하게 여길 수 있는 조건",
             "paragraphs": [*natal, _paragraph(scenario["hypothesis"], all_refs)]},
            {"title": scenario["title"],
             "paragraphs": [dynamics, _paragraph(scenario["scene"], all_refs)]},
            {"title": "다음번에 바꿔 볼 조건",
             "paragraphs": [_paragraph(scenario["trial"], all_refs)]},
        ]
        yield pair, {**base, "version": "1.6-editorial-review", "plan": brief,
                     "report": report, "review": review_report(report, evidence)}


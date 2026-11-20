"""Run a reproducible, paired editorial comparison against v1.1's evidence plan."""

import argparse
import json
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from compatibility_v11 import analyze_pair as analyze_v11
from compatibility_v12 import analyze_pair, report_markdown


def random_pairs(seed=20261121):
    rng = random.Random(seed)
    start = date(1900, 1, 1)
    span = (date(2050, 1, 1) - start).days
    for _ in range(20):
        births = []
        for _ in range(2):
            day = start + timedelta(days=rng.randrange(span))
            hour = None if rng.randrange(4) == 0 else rng.randrange(24)
            births.append(dict(year=day.year, month=day.month, day=day.day, hour=hour,
                               minute=0 if hour is None else rng.randrange(60)))
        yield births


def evaluate():
    rows = []
    for number, births in enumerate(random_pairs(), 1):
        previous = analyze_v11(*births)
        result = analyze_pair(*births)
        plan, evidence, review = (result[key] for key in ("plan", "evidence", "review"))
        relationship = plan["relationship"]
        interaction = evidence.get(relationship["lead_id"])
        counterpoint = evidence.get(relationship["counterpoint_id"])
        v11_topics = [card for card in previous["selection"]["pair"]]
        v12_lens = {
            "lead_kind": interaction["kind"] if interaction else None,
            "lead_positions": sorted(s["pillar"] for s in interaction["sources"]) if interaction else [],
            "counter_kind": counterpoint["kind"] if counterpoint else None,
            "directions": [evidence[ref]["ten_god"] for ref in relationship["direction_ids"]],
            "scene": plan["practice"]["scene"],
        }
        rows.append({
            "pair": number, "births": births, "v11_topics": v11_topics,
            "v12_lens": v12_lens, "same_pillars": previous["charts"] == result["charts"],
            "practice": result["report"][2]["paragraphs"][0]["text"], "review": review,
        })
    practice_counts = Counter(row["practice"] for row in rows)
    summary = {
        "pair_count": len(rows),
        "same_charts": sum(row["same_pillars"] for row in rows),
        "unknown_birth_times": sum(birth["hour"] is None for row in rows for birth in row["births"]),
        "v11_distinct_pair_topic_sequences": len({tuple(row["v11_topics"]) for row in rows}),
        "v12_distinct_position_and_interpretation_sequences": len({
            json.dumps(row["v12_lens"], sort_keys=True) for row in rows
        }),
        "v12_distinct_practice_paragraphs": len(practice_counts),
        "v12_most_repeated_practice_count": max(practice_counts.values()),
        "v12_reports_with_counterpoint": sum(row["v12_lens"]["counter_kind"] is not None for row in rows),
        "unlinked_paragraphs": sum(row["review"]["unlinked_paragraphs"] for row in rows),
        "unresolved_references": sum(len(row["review"]["unresolved_ids"]) for row in rows),
        "within_report_repeated_sentences": sum(len(row["review"]["repeated_sentences"]) for row in rows),
        "translation_marker_hits": sum(len(row["review"]["translation_markers"]) for row in rows),
    }
    return {"seed": 20261121, "summary": summary, "pairs": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, help="Write all 20 rendered reports to this Markdown file")
    args = parser.parse_args()
    if args.samples:
        reports = (f"# 비교 표본 {number:02}\n\n" + report_markdown(analyze_pair(*births))
                   for number, births in enumerate(random_pairs(), 1))
        args.samples.write_text("\n".join(reports), encoding="utf-8")
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))

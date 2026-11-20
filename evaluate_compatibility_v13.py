"""Build version-masked review packets and structural metrics for 24 synthetic pairs."""

import argparse
import json
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import compatibility_v12 as v12
import compatibility_v13 as v13


def fixtures():
    rng = random.Random(13020261120)
    start = date(1970, 1, 1)
    for index in range(24):
        births = []
        for side in range(2):
            day = start + timedelta(days=rng.randrange(14610))
            hour = None if (index + side) % 4 == 0 else rng.randrange(24)
            births.append(dict(year=day.year, month=day.month, day=day.day, hour=hour))
        yield births


def evaluate(output):
    rng = random.Random(20261120)
    packet, key, samples = [], {}, []
    metrics = {"1.2": Counter(), "1.3": Counter()}
    unique = {"1.2": set(), "1.3": set()}
    for number, births in enumerate(fixtures(), 1):
        left, right = v12.analyze_pair(*births), v13.analyze_pair(*births)
        assert left["charts"] == right["charts"]
        ordered = [left, right]
        rng.shuffle(ordered)
        key[number] = [result["version"] for result in ordered]
        # Shared chart data are included to let a reader judge interpretation fidelity.
        pillars = json.dumps({owner: chart["pillars"] for owner, chart in left["charts"].items()},
                             ensure_ascii=False)
        packet.append(f"# 표본 {number:02}\n\n명식 `{pillars}`\n")
        for label, result in zip(("A", "B"), ordered):
            packet.append(f"### 원고 {label}\n" + v12.report_markdown(result))
            version = result["version"]
            paragraphs = [p for chapter in result["report"] for p in chapter["paragraphs"]]
            review = result["review"]
            metrics[version].update({
                "reports": 1, "paragraphs": len(paragraphs),
                "characters": sum(len(p["text"]) for p in paragraphs),
                "unlinked_paragraphs": review["unlinked_paragraphs"],
                "unresolved_references": len(review["unresolved_ids"]),
                "repeated_sentences": len(review["repeated_sentences"]),
                "reports_with_cross_counterpoint": int(bool(
                    result["plan"]["relationship"].get("counter_id" if version == "1.3" else "counterpoint_id")
                )),
            })
            unique[version].add(paragraphs[-1]["text"])
        if number in (1, 2, 3):
            samples.append(f"# 합성 표본 {number:02}\n\n명식 `{pillars}`\n\n"
                           + v13.report_markdown(right)
                           + "\n### 해석 가정\n\n" + "\n".join("- " + line for line in right["assumptions"]))
    for version, strings in unique.items():
        metrics[version]["distinct_final_paragraphs"] = len(strings)
    output.mkdir(parents=True, exist_ok=True)
    for name, data in (("blind-review.md", "\n\n".join(packet)), ("samples.md", "\n\n".join(samples)),
                       ("key.json", json.dumps(key, indent=2)),
                       ("metrics.json", json.dumps(metrics, indent=2))):
        (output / name).write_text(data + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    evaluate(parser.parse_args().output)

"""Compare v1.3 and v1.4 with the original 24 synthetic birth pairs."""

import argparse
import json
from collections import Counter
from pathlib import Path

import compatibility_v13 as v13
import compatibility_v14 as v14
from compatibility_v12 import report_markdown
from evaluate_compatibility_v13 import fixtures


def evaluate(output):
    totals = {version: Counter() for version in ("1.3", "1.4")}
    endings = {version: set() for version in totals}
    scopes = Counter()
    samples = []
    rows = []
    for number, births in enumerate(fixtures(), 1):
        before, after = v13.analyze_pair(*births), v14.analyze_pair(*births)
        for field in ("charts", "contexts", "interactions", "evidence", "assumptions"):
            if before[field] != after[field]:
                raise ValueError(f"Pair {number}: {field} changed")
        scope = after["plan"]["relationship"]["scope"]
        scopes[scope] += 1
        metrics = {}
        for result in (before, after):
            version = result["version"]
            paragraphs = [p["text"] for chapter in result["report"] for p in chapter["paragraphs"]]
            review = result["review"]
            row = {
                "reports": 1,
                "characters": sum(map(len, paragraphs)),
                "repeated_sentences": len(review["repeated_sentences"]),
                "unlinked_paragraphs": review["unlinked_paragraphs"],
                "unresolved_ids": len(review["unresolved_ids"]),
                "mentions_dinner_appointment": int(any("저녁 약속" in p for p in paragraphs)),
                "reports_with_counterpoint": int(bool(result["plan"]["relationship"]["counter_id"])),
            }
            totals[version].update(row)
            endings[version].add(paragraphs[-1])
            metrics[version] = row
        rows.append({"pair": number, "births": births, "scope": scope, "metrics": metrics})
        if number <= 5:
            pillars = {person: chart["pillars"] for person, chart in before["charts"].items()}
            samples.append(f"# 표본 {number:02}\n\n명식 `{json.dumps(pillars, ensure_ascii=False)}`")
            for result in (before, after):
                samples.append(f"### v{result['version']}\n\n" + report_markdown(result).rstrip())

    for version, texts in endings.items():
        totals[version]["distinct_final_paragraphs"] = len(texts)
    output.mkdir(parents=True, exist_ok=True)
    (output / "COMPATIBILITY_V14_COMPARISON.json").write_text(
        json.dumps({"totals": totals, "scopes": scopes, "pairs": rows},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (output / "COMPATIBILITY_V14_SAMPLES.md").write_text(
        "\n\n".join(samples) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    evaluate(parser.parse_args().output)

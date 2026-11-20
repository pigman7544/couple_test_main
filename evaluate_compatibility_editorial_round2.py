"""Regenerate reviewed manuscripts, paired sentence inventories and evidence."""

import json
import re
from collections import Counter
from pathlib import Path

from compatibility_editorial_round2 import DIRECTORY, generate_packet
from evaluate_compatibility_editorial import write_json, write_manuscripts

OUTPUT = DIRECTORY / "round2"
VERSIONS = ("before", "after", "round2")
THRESHOLD = 0.60


def normalized(text):
    return "".join(re.findall(r"[\w]", text.casefold()))


def trigrams(text):
    clean = normalized(text)
    return {clean[i:i + 3] for i in range(len(clean) - 2)}


def similarity(left, right):
    union = left | right
    return len(left & right) / len(union) if union else 0


def location(row):
    return tuple(int(value) for value in row["id"].split("."))


def measure(rows, details=True):
    counts = Counter(normalized(row["text"]) for row in rows)
    features = [(location(row)[0], trigrams(row["text"])) for row in rows]
    similar = sum(
        any(pair != other_pair and grams != other and similarity(grams, other) >= THRESHOLD
            for other_pair, other in features[:i])
        for i, (pair, grams) in enumerate(features)
    )
    return {
        "sentences": len(rows),
        "repeated_occurrences_after_first": len(rows) - len({row["text"] for row in rows}),
        "normalized_repeated": len(rows) - len(counts),
        "near_repeated_from_earlier_pair": similar,
        **({"top_exact": Counter(row["text"] for row in rows).most_common(5)} if details else {}),
        "markers": Counter(marker for row in rows for marker in row["markers"]),
    }


def compare(rows, other):
    candidates = [(row, trigrams(row["text"])) for row in other]
    for row in rows:
        grams = trigrams(row["text"])
        same_chapter = [(similarity(grams, feature), item["id"])
                        for item, feature in candidates if location(row)[:2] == location(item)[:2]]
        score, ref = max(same_chapter, default=(0, None))
        yield [row["id"], ref if score else None, round(score, 3)]


def main(output=OUTPUT):
    output.mkdir(parents=True, exist_ok=True)
    packet = list(generate_packet())
    audit = {
        label: json.loads((DIRECTORY / f"{label}-sentences.json").read_text(encoding="utf-8"))
        for label in VERSIONS[:2]
    }
    audit["round2"] = write_manuscripts("round2", [result for _, result in packet], output)
    metrics = {label: measure(rows) for label, rows in audit.items()}
    metrics["near_threshold"] = THRESHOLD
    metrics["pairs"] = []
    traces = []
    for pair, result in packet:
        number = pair["pair"]
        trace = [[p["evidence_ids"] for p in c["paragraphs"]] for c in result["report"]]
        linked = {ref for chapter in trace for paragraph in chapter for ref in paragraph}
        traces.append({
            "pair": number, "births": pair["births"], "pillars": pair["pillars"],
            "paragraph_ids": trace,
            "new_evidence": {ref: result["evidence"][ref] for ref in sorted(linked)
                             if ref not in pair["evidence"]},
            "other_cross_interactions": [ref for ref in result["interactions"] if ref not in linked],
        })
        metrics["pairs"].append({
            "pair": number,
            "characters": [
                pair["before"]["characters"], pair["after"]["characters"],
                sum(len(p["text"]) for c in result["report"] for p in c["paragraphs"]),
            ],
            "versions": {label: measure([row for row in rows if location(row)[0] == number], details=False)
                         for label, rows in audit.items()},
        })
    write_json(output / "metrics.json", metrics)
    write_json(output / "trace.json", traces)
    comparisons = {
        f"{left}_to_{right}": list(compare(audit[left], audit[right]))
        for left, right in (("before", "round2"), ("after", "round2"),
                            ("round2", "before"), ("round2", "after"))
    }
    # Store compact alignments in JSON Lines to keep reviews readable and uploads small.
    with (output / "sentence-comparison.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        for label, rows in comparisons.items():
            for row in rows:
                stream.write(json.dumps([label, *row]) + "\n")


if __name__ == "__main__":
    main()


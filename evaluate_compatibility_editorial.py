"""Generate matched Korean report manuscripts and evidence for editorial review."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from compatibility_v12 import report_markdown
from compatibility_v14 import analyze_pair as baseline
from evaluate_compatibility_v13 import fixtures


OUTPUT = Path("docs/compatibility-editorial")
PATTERNS = {
    "linkage_proxy": r"한 가지 단서를 줍니다|접점을 찾을 수 있는 대목|작용이 함께 잡힙니다",
    "grammar": r"을을|를를|알아보기을|들리는지 묻게|쪽 글자인.*에서는 .*묻게 됩니다|대목을을",
    "clarity": r"작용이 함께 잡힙니다|에도 걸쳐 있습니다|같은 자리의 아래쪽 글자",
    "abstraction": r"읽은 주제|눈에 들어오는 주제|읽는 주제|다른 주제가|같은 주제가",
    "generic": r"떠오르는 일이 있다면 당시 상대에게 바랐던|최근 뜻이 맞았던 일 하나|‘그래서 좋아’와 ‘그래도 망설여져’",
}


def sentences(body):
    # Keep sentence punctuation inside direct speech with its enclosing sentence.
    return re.split(r"(?<=[.!?])\s+(?=(?:[^”]*“[^”]*”)*[^”]*$)", body)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")


def packet(analyze):
    return [analyze(*births) for births in list(fixtures())[:20]]


def write_manuscripts(label, results, output):
    bodies, audit = [], []
    for index, (births, result) in enumerate(zip(fixtures(), results), 1):
        bodies.append(f"# 표본 {index:02}\n\n" + "\n".join(
            "#" + line if line.startswith("## ") else line
            for line in report_markdown(result).rstrip().splitlines()
        ))
        for ch, chapter in enumerate(result["report"], 1):
            for p, paragraph in enumerate(chapter["paragraphs"], 1):
                for s, sentence in enumerate(sentences(paragraph["text"]), 1):
                    audit.append({
                        "id": f"{index:02}.{ch}.{p}.{s}", "text": sentence,
                        "markers": [key for key, pattern in PATTERNS.items()
                                    if re.search(pattern, sentence)],
                    })
    counts = Counter(row["text"] for row in audit)
    for row in audit:
        row["occurrences"] = counts[row["text"]]
    (output / f"{label}.md").write_text("\n\n".join(bodies) + "\n",
                                       encoding="utf-8", newline="\n")
    write_json(output / f"{label}-sentences.json", audit)
    return audit


def main(output, baseline_only):
    output.mkdir(parents=True, exist_ok=True)
    before = packet(baseline)
    before_audit = write_manuscripts("before", before, output)
    if baseline_only:
        results = [("before", before)]
    else:
        from compatibility_editorial import analyze_pair
        after = packet(analyze_pair)
        results = [("before", before), ("after", after)]
        after_audit = write_manuscripts("after", after, output)

    pairs = []
    for index, births in enumerate(list(fixtures())[:20]):
        facts = before[index]
        review = {}
        for label, versions in results:
            result = versions[index]
            for key in ("charts", "contexts", "interactions", "evidence"):
                assert result[key] == facts[key], (index, key)
            review[label] = {
                "plan": (result["plan"] if label == "after" else {
                    "relationship": {k: v for k, v in result["plan"]["relationship"].items()
                                     if k != "candidates"},
                    "natal": {k: v["lead"]["id"] for k, v in result["plan"]["natal"].items()},
                }),
                "paragraph_ids": [[p["evidence_ids"] for p in c["paragraphs"]]
                                  for c in result["report"]],
                "characters": sum(len(p["text"]) for c in result["report"]
                                  for p in c["paragraphs"]),
            }
        linked = {ref for v in review.values() for chapter in v["paragraph_ids"]
                  for paragraph in chapter for ref in paragraph}
        pairs.append({
            "pair": index + 1, "births": births,
            "pillars": {owner: c["pillars"] for owner, c in facts["charts"].items()},
            "interaction_kinds": sorted({facts["evidence"][ref]["kind"]
                                         for ref in facts["interactions"]}),
            "evidence": {ref: facts["evidence"][ref] for ref in sorted(linked)},
            **review,
        })
    write_json(output / "pairs.json", pairs)
    audits = {"before": before_audit}
    if not baseline_only:
        audits["after"] = after_audit
    metrics = {}
    for label, rows in audits.items():
        counts = Counter(row["text"] for row in rows)
        metrics[label] = {
            "sentences": len(rows),
            "questions": sum(row["text"].endswith("?") for row in rows),
            "distinct_sentences": len(counts),
            "repeated_occurrences_after_first": len(rows) - len(counts),
            "most_repeated": counts.most_common(8),
            "marker_counts": Counter(marker for row in rows for marker in row["markers"]),
            "character_counts": [pair[label]["characters"] for pair in pairs],
            "unique_last_paragraphs": len({
                r["report"][-1]["paragraphs"][-1]["text"] for r in dict(results)[label]
            }),
        }
    reference = Path(__file__).with_name("docs") / "COMPATIBILITY_TARGET_MANUSCRIPTS.md"
    target = re.split(r"(?m)^## 표본 \d+ .*?\n", reference.read_text(encoding="utf-8"))[1:]
    metrics["target"] = {
        "character_counts": [
            sum(len(line) for line in text.splitlines() if line.strip() and not line.startswith("#"))
            for text in target
        ],
    }
    write_json(output / "metrics.json", metrics)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--baseline-only", action="store_true")
    options = parser.parse_args()
    main(options.output, options.baseline_only)

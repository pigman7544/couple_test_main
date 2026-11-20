"""Reproduce round three manuscripts and evidence-link audits."""

import argparse
import json
import random
import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from statistics import mean

from compatibility_editorial_round3 import SCENES, analyze_pair
from compatibility_v12 import report_markdown
from evaluate_compatibility_editorial import PATTERNS, sentences, write_json
from evaluate_compatibility_editorial_round2 import measure
from evaluate_compatibility_v13 import fixtures

OUTPUT = Path(__file__).resolve().parent / "docs" / "compatibility-editorial" / "round3"


def holdouts():
    config = json.loads((OUTPUT / "holdout.json").read_text(encoding="utf-8"))
    start, end = map(date.fromisoformat, (config["start"], config["end"]))
    rng = random.Random(config["seed"])
    for index in range(config["count"]):
        pair = []
        for side in range(2):
            day = start + timedelta(days=rng.randrange((end - start).days + 1))
            if index % 6 == 0 and side == 0:
                day = date.fromisoformat(config["anchors"][index // 6])
            hour = rng.randrange(24)
            if index % 4 == 0 or (index % 2 and side == index // 2 % 2):
                hour = None
            pair.append(dict(year=day.year, month=day.month, day=day.day, hour=hour))
        yield pair


def score_packet(pairs, slug, output):
    manuscripts, rows, audit = [], [], []
    for index, pair in enumerate(pairs, 1):
        result = analyze_pair(*pair)
        manuscripts.append(f"# {slug} {index:02}\n\n{report_markdown(result)}")
        plan = result["plan"]
        relation = plan["relationship"]
        links = []
        characters = 0
        for chapter, section in enumerate(result["report"], 1):
            for paragraph, entry in enumerate(section["paragraphs"], 1):
                location = f"{index:02}.{chapter}.{paragraph}"
                characters += len(entry["text"])
                links.append({"paragraph": location, "ids": entry["evidence_ids"]})
                for sentence, line in enumerate(sentences(entry["text"]), 1):
                    rows.append({
                        "id": f"{location}.{sentence}", "text": line,
                        "markers": [key for key, pattern in PATTERNS.items() if re.search(pattern, line)],
                    })
        audit.append({
            "pair": index, "characters": characters, "scene": SCENES[plan["scene"]][0],
            "scene_scores": plan["scene_scores"], "mechanism": plan["mechanism"],
            "roles": plan["reading_roles"], "scope": relation["scope"],
            "support": relation["support"]["id"] if relation["support"] else None,
            "tension": relation["tension"]["id"] if relation["tension"] else None,
            "time_unknown": sum(birth["hour"] is None for birth in pair),
            "unresolved_pillars": [row["missing"] for row in plan["natal"]],
            "unresolved_ids": result["review"]["unresolved_ids"],
            "unlinked_paragraphs": result["review"]["unlinked_paragraphs"],
            "paragraph_links": links,
        })
    (output / f"{slug}.md").write_text("\n".join(manuscripts), encoding="utf-8", newline="\n")
    write_json(output / f"{slug}-audit.json", audit)
    return {
        **measure(rows),
        "pairs": len(audit),
        "characters_mean": round(mean(x["characters"] for x in audit), 1),
        "characters_range": [min(x["characters"] for x in audit), max(x["characters"] for x in audit)],
        "scene_counts": Counter(x["scene"] for x in audit),
        "scene_mechanism_counts": Counter(f"{x['scene']} / {x['mechanism']}" for x in audit),
        "scope_counts": Counter(x["scope"] for x in audit),
        "time_unknown_counts": Counter(x["time_unknown"] for x in audit),
        "unlinked_paragraphs": sum(x["unlinked_paragraphs"] for x in audit),
        "unresolved_ids": sum(len(x["unresolved_ids"]) for x in audit),
    }


def main(output):
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "metrics.json", {
        "matched": score_packet(list(fixtures())[:20], "matched", output),
        "holdout": score_packet(list(holdouts()), "holdout", output),
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    main(parser.parse_args().output)

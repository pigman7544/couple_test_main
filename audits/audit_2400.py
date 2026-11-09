"""Reproducible 2,400-pair archetype distribution and determinism audit.

Run: python -m audits.audit_2400
This audits symbolic prototype behavior, not real-world compatibility accuracy.
"""
import json
import random
from collections import Counter
from datetime import date, timedelta

from engine import person
from relationship_v08 import relation
from matcher import winner, DB

SEED = 20261109
N = 2400


def sample_person(rng):
    day = date(1970, 1, 1) + timedelta(days=rng.randrange(18000))
    hour = rng.randrange(24) if rng.randrange(5) else None
    return person(day.year, day.month, day.day, hour)


def result(a, b):
    rel = relation(a, b)
    return {"vector": rel["vector"], "winner": winner(rel["vector"])["id"]}


def main():
    rng = random.Random(SEED)
    counts = Counter()
    failures = []
    for i in range(N):
        a, b = sample_person(rng), sample_person(rng)
        first = result(a, b)
        second = result(a, b)
        if first != second:
            failures.append({"index": i, "reason": "repeat mismatch"})
        swapped = result(b, a)
        if first != swapped:
            failures.append({"index": i, "reason": "swap mismatch"})
        counts[first["winner"]] += 1

    ids = sorted(c["id"] for c in DB)
    summary = {
        "seed": SEED,
        "pairs": N,
        "counts": {key: counts[key] for key in ids},
        "percentages": {key: round(100 * counts[key] / N, 2) for key in ids},
        "missing_types": [key for key in ids if not counts[key]],
        "repeat_and_swap_failures": failures[:20],
        "failure_count": len(failures),
        "scope": "saju -> six axes -> matcher; full rendered report text not covered",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit("Determinism or swap-invariance audit failed")


if __name__ == "__main__":
    main()

"""Reproducible complete-output and matching swap audit. No matcher edits."""
import json
import random
from pathlib import Path
from audit_quality import payload, audit
from server import compute


def run():
    rng = random.Random(20261109)
    repeated = swapped = 0
    for _ in range(2400):
        p = payload(rng)
        first = compute(p, unlock=True)
        repeated += first == compute(p, unlock=True)
        reverse = compute({'a': p['b'], 'b': p['a']}, unlock=True)
        swapped += first['couple'] == reverse['couple']
    result = audit(2400, 30)
    result.update(full_output_repeat_matches=repeated, swapped_match_matches=swapped)
    Path('docs/qa-personalization.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    assert repeated == swapped == 2400
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    run()

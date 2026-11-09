"""Audit 12 report archetypes: baseline length, distribution, deterministic outputs.

Run: python audit_quality.py --samples 2400 --repeat 10
This is a diagnostic, not a claim of clinical or statistical validity.
"""
import argparse
import collections
import hashlib
import json
import random
import statistics

from server import compute
from matcher import DB
from engine import person
from relationship_v08 import relation
from story_report import make_report

REPORT_KEYS = ('roles', 'story', 'saju_a', 'crisis', 'tip')
BASELINE_ID = 'c06'


def payload(rng):
    def one():
        return {
            'date': '%04d-%02d-%02d' % (rng.randint(1970, 2004), rng.randint(1, 12), rng.randint(1, 28)),
            'calendar': 'solar',
            'time': '%02d:00' % rng.randrange(24),
            'gender': rng.choice(['male', 'female']),
        }
    return {'a': one(), 'b': one()}


def audit(samples=2400, repeat=10, seed=20261109):
    rng = random.Random(seed)
    counts = collections.Counter()
    lengths = collections.defaultdict(list)
    sample_inputs = {}
    for _ in range(samples):
        p = payload(rng)
        result = compute(p, unlock=True)
        cid = result['couple']['id']
        counts[cid] += 1
        sample_inputs.setdefault(cid, p)
        report = result['full_report']
        lengths[cid].append(sum(len(str(report.get(k, ''))) for k in REPORT_KEYS))
        assert len(report['chapters']) == 5, cid
        assert all(report.get(k) for k in REPORT_KEYS), cid

    # Compare every archetype on the exact same two birth charts, including
    # those never selected by the matcher in this sample.
    a, b = person(1992, 3, 18, 16), person(1992, 4, 30, 1)
    rel = relation(a, b)
    forced = {}
    for c in DB:
        report = make_report(a, b, rel, c, {})
        forced[c['id']] = sum(len(str(report.get(k, ''))) for k in REPORT_KEYS)
        assert len(report['chapters']) == 5, c['id']
        assert all(report.get(k) for k in REPORT_KEYS), c['id']
    forced_baseline = forced[BASELINE_ID]
    baseline = statistics.median(lengths[BASELINE_ID]) if lengths[BASELINE_ID] else None
    quality = {}
    for c in DB:
        cid = c['id']
        vals = lengths[cid]
        quality[cid] = {
            'name': c['name'],
            'count': counts[cid],
            'median_chars': statistics.median(vals) if vals else None,
            'min_chars': min(vals) if vals else None,
            'ratio_to_c06': round(statistics.median(vals) / baseline, 3) if vals and baseline else None,
            'forced_chars': forced[cid],
            'forced_ratio_to_c06': round(forced[cid] / forced_baseline, 3),
        }

    # Compare complete API output; repeated calls must match byte-for-byte
    # after canonical JSON serialization.
    fixed = payload(random.Random(seed + 1))
    def digest(p):
        output = compute(p, unlock=True)
        return hashlib.sha256(json.dumps(output, ensure_ascii=False, sort_keys=True).encode('utf8')).hexdigest()
    first = digest(fixed)
    deterministic = all(digest(fixed) == first for _ in range(repeat))
    for cid, p in sample_inputs.items():
        assert digest(p) == digest(p), 'nondeterministic output for ' + cid

    # Diagnostic gates: every archetype must appear; concentration is flagged
    # rather than forcing an artificial uniform distribution.
    expected_ids = {c['id'] for c in DB}
    observed_ids = set(counts)
    unmatched = sorted(expected_ids - observed_ids)
    max_share = max(counts.values()) / samples
    distribution_flags = []
    if unmatched:
        distribution_flags.append('unmatched archetypes: ' + ', '.join(unmatched))
    if max_share > 0.35:
        distribution_flags.append('largest archetype exceeds 35% of samples')
    distribution_ok = not distribution_flags

    return {
        'distribution_ok': distribution_ok,
        'distribution_flags': distribution_flags,
        'seed': seed,
        'samples': samples,
        'repeat': repeat,
        'deterministic': deterministic,
        'matched_types': sum(v > 0 for v in counts.values()),
        'unmatched_types': unmatched,
        'max_share': round(max_share, 4),
        'counts': dict(sorted(counts.items())),
        'quality': quality,
        'note': 'Equal frequency is not required; editorial quality must also be reviewed manually.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', type=int, default=2400)
    parser.add_argument('--repeat', type=int, default=10)
    parser.add_argument('--seed', type=int, default=20261109)
    args = parser.parse_args()
    result = audit(args.samples, args.repeat, args.seed)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['distribution_ok'] or not result['deterministic']:
        raise SystemExit(1)

"""Reproducible synthetic display audit, independent of operating matcher policy."""
import collections
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from experiments.matching.simulate import sample, digest
from matcher import KEYS, rank, DB
from story_report import make_report
from report_display import ten_point_score
from relationship_v08 import relation


def summary(values, transform):
    buckets = collections.defaultdict(collections.Counter)
    for value in values:
        buckets[transform(value)][value] += 1
    total_pairs = len(values) * (len(values) - 1) // 2
    tied = sum(sum(c.values()) * (sum(c.values()) - 1) // 2 for c in buckets.values())
    original_ties = sum(n * (n - 1) // 2 for n in collections.Counter(values).values())
    return {
        'histogram': {str(k): sum(buckets.get(k, {}).values()) for k in range(1, 11)},
        'mean': statistics.mean([transform(v) for v in values]),
        'modal_share': max(sum(c.values()) for c in buckets.values()) / len(values),
        'distinct_raw_values': len(set(values)),
        'introduced_tie_pairs': tied - original_ties,
        'introduced_tie_pair_rate': (tied - original_ties) / total_pairs,
        'raw_tie_pair_rate': original_ties / total_pairs,
        'all_display_tie_pair_rate': tied / total_pairs,
        'buckets': {str(k): {'min_raw': min(c), 'max_raw': max(c), 'distinct_raw_values': len(c)}
                    for k, c in sorted(buckets.items())},
    }


def main():
    rows = sample(20261109, 2400)
    assert digest([r[0] for r in rows]) == digest([r[0] for r in sample(20261109, 2400)])
    result = {'seed': 20261109, 'samples': len(rows), 'input_sha256': digest([r[0] for r in rows]),
              'population': 'Synthetic solar dates 1970–2004, days 1–28; not users or normative data.', 'axes': {}}
    candidates = {'linear_10': lambda x: max(1, min(10, int(x / 10 + .5))),
                  'previous_7': lambda x: max(1, min(10, int(5 + (x - 50) / 7 + .5))),
                  'selected_5': ten_point_score,
                  'wider_4': lambda x: max(1, min(10, int(5 + (x - 50) / 4 + .5)))}
    for key in KEYS:
        values = [r[3][key] for r in rows]
        result['axes'][key] = {
            'raw': {'min': min(values), 'max': max(values), 'mean': statistics.mean(values),
                    'sd': statistics.pstdev(values), 'histogram': dict(sorted(collections.Counter(map(str, values)).items()))},
            'candidates': {name: summary(values, fn) for name, fn in candidates.items()},
            'synthetic_gender_groups': {gender: summary([r[3][key] for r in rows if r[0]['a']['gender'] == gender], ten_point_score)
                                        for gender in ('male', 'female')},
        }
    winners = []
    report_hashes = []
    for payload, a, b, vector in rows:
        rel = relation(a, b)
        selected = rank(vector)[0][2]
        before = digest(rel)
        report = make_report(a, b, rel, selected, {})
        assert report == make_report(a, b, rel, selected, {})
        assert before == digest(rel)
        assert len(report['chapters']) == 5
        for chapter, axes in (('saju_a', ('attraction', 'security', 'growth')),
                              ('crisis', ('conflict', 'expression', 'autonomy'))):
            assert re.findall(r'(\d+)/10', report[chapter]) == [str(ten_point_score(vector[k])) for k in axes]
            assert not re.search(r'\d+(?:\.\d+)?/100', report[chapter])
        assert selected['id'] == rank(vector)[0][1]
        winners.append(selected['id'])
        report_hashes.append(digest(report))
    result['matching_counts'] = dict(collections.Counter(winners))
    result['winner_sha256'] = digest(winners)
    result['report_sha256'] = digest(report_hashes)
    result['deterministic_reports'] = 2400
    result['unmutated_relations_and_matching'] = 2400
    result['decision'] = 'Select uniform five-point step anchored at raw 45 -> 3 and 65 -> 7. Fewer introduced ties on all six axes and less than 3% ceiling share; no quantile remapping from synthetic data.'
    Path('docs/qa-display-2400.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({k: {name: {'mode': round(v['modal_share'], 4), 'introduced_ties': round(v['introduced_tie_pair_rate'], 4),
                               'at_10': v['histogram']['10']} for name, v in x['candidates'].items()}
                      for k, x in result['axes'].items()}, indent=2))


if __name__ == '__main__':
    main()

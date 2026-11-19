"""Generate date-based and forced-type editorial QA samples from a checkout.

Run: python tests/audit_a1.py --source . --output a1-after.json
Run again against the preceding checkout for a comparable baseline.
"""

import argparse
from collections import Counter, defaultdict
from datetime import date, timedelta
from hashlib import sha256
import json
from pathlib import Path
import random
import re
from statistics import median
import sys
from unittest.mock import patch


def plain(text):
    return text.replace('**', '').strip()


def character_count(text):
    return len(re.sub(r'\s+', ' ', plain(text)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    sys.path.insert(0, str(source))
    import server
    from matcher import DB

    hashes = {
        name: sha256((source / name).read_bytes()).hexdigest()
        for name in ('engine.py', 'relationship_v08.py', 'matcher.py', 'couples.json')
    }
    assets = {}
    for cid, variants in server.COUPLE_ART.items():
        for kind, path in variants.items():
            file = source / path.lstrip('/')
            data = file.read_bytes() if file.is_file() else b''
            if len(data) >= 24 and data[:8] == b'\x89PNG\r\n\x1a\n':
                assets[f'{cid}/{kind}'] = {
                    'path': path, 'size': len(data), 'sha256': sha256(data).hexdigest(),
                    'dimensions': [int.from_bytes(data[i:i + 4], 'big') for i in (16, 20)],
                }
            else:
                assets[f'{cid}/{kind}'] = None

    natural, forced = [], []
    keys = defaultdict(set)
    repeated = Counter()

    def sample(payload):
        preview = server.compute(payload)
        unlocked = server.compute(payload, unlock=True)
        assert preview['couple'] == unlocked['couple']
        assert preview['art'] == unlocked['art']
        assert 'full_report' not in preview and unlocked['test_mode']
        assert unlocked['has_art'], unlocked['couple']
        report = unlocked['full_report']
        cid = unlocked['couple']['id']
        chapters = {row['key']: plain(report[row['key']]) for row in report['chapters']}
        plot = report.get('plot', {}).get('body', '')
        sections = {key: character_count(body) for key, body in chapters.items()}
        for key, body in chapters.items():
            keys[cid, key].add(body)
        paragraphs = [p for body in chapters.values() for p in body.split('\n\n') if len(p) >= 30]
        repeated[cid] += len(paragraphs) - len(set(paragraphs))
        return dict(
            input=payload, id=cid, pillars=[report['pillars_a'], report['pillars_b']],
            preview=preview['preview'], art=unlocked['art'], chapters=chapters,
            plot=plain(plot), sections=sections, total=sum(sections.values()) + character_count(plot),
        )

    focus = {'a': {'date': '1982-09-13'}, 'b': {'date': '1981-06-02', 'time': '03:00'}}
    natural.append(sample(focus))
    rng = random.Random(661119)
    for n in range(240):
        payload = {}
        for i, key in enumerate(('a', 'b')):
            birthday = date(1971, 1, 1) + timedelta(days=rng.randrange(19_500))
            calendar = 'lunar' if (n + i) % 11 == 0 else 'solar'
            if calendar == 'lunar':
                birthday = birthday.replace(day=min(birthday.day, 28))
            entry = {'date': birthday.isoformat(), 'calendar': calendar}
            if (n + i) % 4:
                entry['time'] = f'{rng.randrange(24):02d}:{rng.choice((0, 15, 30, 45)):02d}'
            payload[key] = entry
        natural.append(sample(payload))
    rank = server.rank
    for couple in DB:
        cid = couple['id']
        with patch.object(server, 'rank', lambda vector: sorted(rank(vector), key=lambda row: row[2]['id'] != cid)):
            forced.append(sample(focus))

    stats = {}
    for cid in (couple['id'] for couple in DB):
        rows = [row for row in natural if row['id'] == cid]
        totals = [row['total'] for row in rows]
        stats[cid] = dict(
            natural=len(rows), min=min(totals, default=None), median=median(totals) if totals else None,
            max=max(totals, default=None), distinct_chapters={
                key: len(bodies) for (couple_id, key), bodies in keys.items() if couple_id == cid
            }, repeated_paragraphs=repeated[cid],
        )
    coverage = {row['id'] for row in natural}
    first_natural = [next(row for row in natural if row['id'] == cid) for cid in sorted(coverage)]
    result = dict(
        hashes=hashes, assets=assets, stats=stats,
        assignments=[{k: row[k] for k in ('input', 'id', 'pillars', 'art')} for row in natural],
        natural=first_natural, forced=forced,
    )
    if args.baseline:
        baseline = json.loads(args.baseline.read_text(encoding='utf-8'))
        for key in ('hashes', 'assignments', 'assets'):
            assert result[key] == baseline[key], f'Changed baseline {key}'
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(natural)} natural, {len(coverage)} types; {len(forced)} controlled; '
          f'{sum(asset is None for asset in assets.values())} missing cards')


if __name__ == '__main__':
    main()

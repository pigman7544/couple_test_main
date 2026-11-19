import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import server


ROOT = Path(__file__).resolve().parent
BASELINE = json.loads((ROOT / 'tests/fixtures/latest_matching.json').read_text(encoding='utf8'))


class LatestMatchingTests(unittest.TestCase):
    def test_matching_sources_match_pinned_development_commit(self):
        for name, expected in BASELINE['sources'].items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)

    def test_preview_and_unlock_use_full_chart_rank(self):
        original_rank = server.rank
        for row in BASELINE['cases']:
            for unlock in (False, True):
                with self.subTest(payload=row['payload'], unlock=unlock):
                    with patch.object(server, 'rank', wraps=original_rank) as rank:
                        result = server.compute(dict(row['payload'], edition='manuscript'), unlock)
                    rank.assert_called_once_with(row['vector'])
                    self.assertEqual([c[1] for c in original_rank(row['vector'])], row['rank'])
                    self.assertEqual(result['couple']['id'], row['couple'])
                    self.assertTrue(result['has_art'])
                    self.assertEqual('full_report' in result, unlock)
                    if not unlock:
                        self.assertTrue(result['preview']['story_excerpt'])
                        self.assertLessEqual(len(result['preview']['story_excerpt']), 96)

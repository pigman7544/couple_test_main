"""Regression tests for reader-facing typography and 10-point score display."""
import re
import unittest
from engine import person
from matcher import DB
from relationship_v08 import relation
from story_report import make_report


class ReportDisplayTests(unittest.TestCase):
    def test_all_archetypes_keep_headings_and_integer_ten_point_scores(self):
        a, b = person(1992, 3, 18, 16), person(1992, 4, 30, 1)
        rel = relation(a, b)
        for couple in DB:
            report = make_report(a, b, rel, couple, {})
            self.assertEqual(report, make_report(a, b, rel, couple, {}))
            for key in ('roles', 'story', 'saju_a', 'crisis', 'tip'):
                body = report[key]
                self.assertNotRegex(body, r'\\d+(?:\\.\\d+)?/100')
                for line in body.splitlines():
                    if not line.lstrip().startswith('◆ '):
                        self.assertNotIn('**', line, (couple['id'], key, line))
            for key in ('saju_a', 'crisis'):
                scores = [int(n) for n in re.findall(r'(?<!\\d)(\\d+)/10(?!\\d)', report[key])]
                self.assertGreaterEqual(len(scores), 3, (couple['id'], key))
                self.assertTrue(all(1 <= n <= 10 for n in scores))
            self.assertTrue(any(line.lstrip().startswith('◆ **')
                                for line in report['saju_a'].splitlines()))

if __name__ == '__main__':
    unittest.main()

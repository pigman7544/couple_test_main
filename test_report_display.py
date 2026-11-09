"""Regression tests for reader-facing typography and 10-point score display."""
import re
import unittest
import copy
from unittest.mock import patch
from report_display import ten_point_score, reduce_body_bold
from engine import person
from matcher import DB
from relationship_v08 import relation
from story_report import make_report


class ReportDisplayTests(unittest.TestCase):
    def test_boundaries_and_monotonicity(self):
        self.assertEqual([ten_point_score(x) for x in (0, 34.99, 35, 42.49, 42.5, 45, 50, 52.49, 52.5, 77.49, 77.5, 100)],
                         [1, 1, 1, 2, 3, 3, 4, 4, 5, 9, 10, 10])
        values = [ten_point_score(n / 100) for n in range(10001)]
        self.assertEqual(values, sorted(values))
        self.assertEqual(set(values), set(range(1, 11)))

    def test_heading_and_multiline_prose_preservation(self):
        self.assertEqual(reduce_body_bold('◆ **제목**\n**첫 문단\n둘째 문단**\n## **제목**'),
                         '◆ **제목**\n첫 문단\n둘째 문단\n## **제목**')

    def test_every_axis_and_raw_band_for_every_type(self):
        from c06_report import band
        a, b = person(1992, 3, 18, 16), person(1992, 4, 30, 1)
        axes = ('attraction', 'security', 'growth', 'conflict', 'expression', 'autonomy')
        for couple in DB:
            for value in (0, 44.99, 45, 53.49, 53.5, 64.99, 65, 100):
                rel = relation(a, b)
                rel['vector'] = dict(zip(axes, [value] * 6))
                original = copy.deepcopy(rel)
                report = make_report(a, b, rel, couple, {})
                self.assertEqual(rel, original)
                self.assertEqual(report['sections'], ['roles', 'story', 'saju_a', 'crisis', 'tip'])
                self.assertEqual([c['key'] for c in report['chapters']], report['sections'])
                for chapter in ('saju_a', 'crisis'):
                    scores = re.findall(r'(?<!\d)(\d+)/10(?!\d)', report[chapter])
                    self.assertEqual(scores, [str(ten_point_score(value))] * 3, (couple['id'], value, chapter))
                # Compare against the prose selected directly by the original raw bands.
                if couple['id'] in ('c01', 'c06'):
                    if couple['id'] == 'c01':
                        from c01_report import AXES
                    else:
                        from c06_report import AXES
                    for axis in axes:
                        self.assertIn(AXES[axis][1][band(value)][0], (report['saju_a'] + report['crisis']).replace('**', ''))
                else:
                    from other_reports import AXIS_TEXT
                    for axis in axes:
                        self.assertIn(AXIS_TEXT[axis][band(value)], (report['saju_a'] + report['crisis']).replace('**', ''))

    def test_original_story_and_headings_preserved(self):
        from report_display import reduce_body_bold
        a, b = person(1992, 3, 18), person(1992, 4, 30)
        rel = relation(a, b)
        for couple in DB:
            with patch('report_emphasis.emphasize', side_effect=lambda s, *args: s):
                before = make_report(a, b, rel, couple, {})
            after = make_report(a, b, rel, couple, {})
            for key in ('roles', 'story', 'saju_a', 'crisis', 'scene', 'tip', 'ending'):
                self.assertEqual(before[key].replace('**', ''), after[key].replace('**', ''))
                self.assertEqual([s for s in before[key].splitlines() if s.lstrip().startswith('◆ ')],
                                 [s for s in after[key].splitlines() if s.lstrip().startswith('◆ ')])

    def test_six_different_values_keep_axis_order(self):
        a, b = person(1992, 3, 18), person(1992, 4, 30)
        rel = relation(a, b)
        rel['vector'] = dict(zip(('attraction', 'security', 'growth', 'conflict', 'expression', 'autonomy'),
                                 (30, 45, 55, 65, 75, 100)))
        for couple in DB:
            report = make_report(a, b, rel, couple, {})
            for chapter, expected in (('saju_a', ['1', '3', '5']), ('crisis', ['7', '9', '10'])):
                self.assertEqual(re.findall(r'(\d+)/10', report[chapter]), expected, couple['id'])

    def test_missing_gender_time_and_gender_independent_reports(self):
        from server import compute
        for time in (None, '', '16:00'):
            payload = {'a': {'date': '1992-03-18'}, 'b': {'date': '1992-04-30'}}
            if time is not None:
                for p in payload.values():
                    p['time'] = time
            for couple in DB:
                # Controlled type selection exercises all report routes, not matcher coverage.
                other = next(c for c in DB if c['id'] != couple['id'])
                with patch('server.rank', return_value=[(0, couple['id'], couple), (1, other['id'], other)]):
                    base = compute(payload, unlock=True)
                    self.assertEqual(base, compute(payload, unlock=True))
                    for genders in (('female', 'male'), ('male', 'female'), ('other', 'other')):
                        data = copy.deepcopy(payload)
                        for key, gender in zip(('a', 'b'), genders):
                            data[key]['gender'] = gender
                        changed = compute(data, unlock=True)
                        for key in base['full_report']['sections']:
                            self.assertEqual(base['full_report'][key], changed['full_report'][key])
                        self.assertEqual(base['couple'], changed['couple'])

    def test_all_archetypes_keep_headings_and_integer_ten_point_scores(self):
        a, b = person(1992, 3, 18, 16), person(1992, 4, 30, 1)
        rel = relation(a, b)
        for couple in DB:
            report = make_report(a, b, rel, couple, {})
            self.assertEqual(report, make_report(a, b, rel, couple, {}))
            for key in ('roles', 'story', 'saju_a', 'crisis', 'tip'):
                body = report[key]
                self.assertNotRegex(body, r'\d+(?:\.\d+)?/100')
                for line in body.splitlines():
                    if not line.lstrip().startswith('◆ '):
                        self.assertEqual(line.count('**') % 2, 0, (couple['id'], key, line))
            for key in ('saju_a', 'crisis'):
                scores = [int(n) for n in re.findall(r'(?<!\d)(\d+)/10(?!\d)', report[key])]
                self.assertGreaterEqual(len(scores), 3, (couple['id'], key))
                self.assertTrue(all(1 <= n <= 10 for n in scores))
            self.assertTrue(any(line.lstrip().startswith('◆ **')
                                for line in report['saju_a'].splitlines()))

if __name__ == '__main__':
    unittest.main()

import copy
import unittest
from unittest.mock import patch
from engine import person
from matcher import DB
from relationship_v08 import relation
from story_report import make_report
from server import compute


class PersonalizedReading(unittest.TestCase):
    def test_birth_charts_change_scenes_even_with_identical_scores(self):
        a, b = person(1992, 3, 18, 16), person(1992, 4, 30, 1)
        c, d = person(1988, 6, 12), person(1995, 12, 1)
        rel = relation(a, b)
        original = copy.deepcopy((a, b, rel))
        for couple in DB:
            first = make_report(a, b, rel, couple, {})
            second = make_report(c, d, rel, couple, {})
            self.assertEqual(first['story'], second['story'])
            for key in ('saju_a', 'tip'):
                self.assertNotEqual(first[key], second[key], (couple['id'], key))
            self.assertIn('가상 장면', first['crisis'])
            self.assertEqual(first, make_report(a, b, rel, couple, {}))
        self.assertEqual((a, b, rel), original)

    def test_swapping_labels_preserves_new_chart_specific_advice(self):
        from personalized_reading import enrich
        a, b = person(1992, 3, 18, 16), person(1992, 4, 30, 1)
        def swap(text):
            return text.replace('당신', '@A@').replace('상대방', '당신').replace('@A@', '상대방')
        for couple in DB:
            one = enrich(dict(saju_a='', crisis='', tip=''), a, b, relation(a, b), couple)
            two = enrich(dict(saju_a='', crisis='', tip=''), b, a, relation(b, a), couple)
            for key in ('saju_a', 'tip'):
                # Paragraph order follows input order; each person's content follows their chart.
                self.assertEqual(sorted(swap(one[key]).split('\n\n')), sorted(two[key].split('\n\n')))
            self.assertEqual(one['crisis'], two['crisis'])

    def test_preview_unchanged_by_personalization(self):
        p = {'a': {'date': '1992-03-18'}, 'b': {'date': '1992-04-30'}}
        for couple in DB:
            rival = next(c for c in DB if c['id'] != couple['id'])
            with patch('server.rank', return_value=[(0, couple['id'], couple), (1, rival['id'], rival)]):
                current = compute(p)
                with patch('personalized_reading.enrich', side_effect=lambda result, *args: result):
                    self.assertEqual(current, compute(p))

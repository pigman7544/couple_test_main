"""Regression checks for the personalized Chunhyang report."""
import unittest
from c01_report import AXES, TITLES, TALE, enrich

class ChunhyangReportTests(unittest.TestCase):
    def test_chapter_structure(self):
        self.assertEqual(len(TITLES), 5)
        self.assertIn('춘향', TITLES[0])
        self.assertIn('변학도', TALE)
        self.assertIn('암행어사', TALE)

    def test_independent_variants(self):
        for key in ('attraction','security','growth','conflict','expression','autonomy'):
            self.assertEqual(len(AXES[key][1]), 3)
            for prose, advice in AXES[key][1]:
                self.assertTrue(prose.strip())
                self.assertTrue(advice.strip())
                self.assertNotIn('백소정', prose)
                self.assertNotIn('허선', prose)

    def test_route_isolated(self):
        from engine import person
        from matcher import DB
        from relationship_v08 import relation
        from story_report import make_report
        a, b = person(1992, 3, 18), person(1992, 4, 30)
        reports = {c['id']: make_report(a, b, relation(a, b), c, {}) for c in DB}
        self.assertIn('변학도', reports['c01']['roles'])
        self.assertNotIn('◆ ', reports['c01']['saju_a'])
        self.assertNotRegex(reports['c01']['roles'], '동점|편집상|누가 더 사랑|세심한 품격')
        for cid, report in reports.items():
            if cid != 'c01':
                self.assertNotIn('변학도', report['roles'])

if __name__ == '__main__':
    unittest.main()

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
        from pathlib import Path
        code = (Path(__file__).parent/'story_report.py').read_text(encoding='utf-8')
        self.assertIn("if couple['id'] == 'c01':", code)
        self.assertIn("if couple['id'] != 'c06':", code)

if __name__ == '__main__':
    unittest.main()

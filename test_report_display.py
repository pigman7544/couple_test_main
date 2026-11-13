"""Regression tests for reader-facing typography and score-free reports."""
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
    def test_heading_and_multiline_prose_preservation(self):
        self.assertEqual(reduce_body_bold('◆ **제목**\n**첫 문단\n둘째 문단**\n## **제목**'),
                         '◆ **제목**\n첫 문단\n둘째 문단\n## **제목**')

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

    def test_all_types_all_bands_have_no_reader_scores_or_grades(self):
        from server import compute
        a,b=person(1992,3,18,16),person(1992,4,30,1)
        forbidden=r'\d+(?:\.\d+)?\s*/\s*(?:10|100)(?!\d)|\d+\s*점|궁합\s*(?:점수|등급)|[A-FS][+−-]?등급'
        for couple in DB:
            for value in (0,44.99,45,55,64.99,65,100):
                rel=relation(a,b);rel['vector']=dict.fromkeys(rel['vector'],value)
                original=copy.deepcopy(rel)
                report=make_report(a,b,rel,couple,{})
                self.assertEqual(rel,original)
                for key in ('tagline','teaser','roles','story','saju_a','saju_b','chemistry','crisis','scene','tip','ending','questions'):
                    self.assertNotRegex(str(report.get(key,'')),forbidden,(couple['id'],value,key))
                self.assertEqual(len(report['chapters']),3 if couple['id']=='c11' else 5)
            other=next(c for c in DB if c['id']!=couple['id'])
            with patch('server.rank',return_value=[(0,couple['id'],couple),(1,other['id'],other)]):
                payload={'a':{'date':'1992-03-18'},'b':{'date':'1992-04-30'}}
                self.assertNotRegex(str(compute(payload)),forbidden)

    def test_no_score_formatter_imports_in_report_generators(self):
        from pathlib import Path
        for name in ('c01_report.py','c06_report.py','other_reports.py'):
            self.assertNotIn('ten_point_score',Path(name).read_text(encoding='utf8'))

if __name__=='__main__':unittest.main()

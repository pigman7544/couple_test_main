"""Smoke and editorial regression tests for every supported narrative archetype.
Run: python -m unittest test_all_couples.py
"""
import unittest
from engine import person
from relationship_v08 import relation
from matcher import DB
from narrative import describe
from story_report import make_report
from literary_edition import EDITION

class EditorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=person(1992,3,18,hour=16,minute=0)
        cls.b=person(1992,4,30,hour=1,minute=0)
        cls.rel=relation(cls.a,cls.b)
    def test_all_twelve_have_five_chapters(self):
        for couple in DB:
            with self.subTest(couple=couple['id']):
                story=describe(self.rel['vector'],couple['id'])
                report=make_report(self.a,self.b,self.rel,couple,story)
                self.assertEqual(len(report['chapters']),5)
                self.assertEqual([c['key'] for c in report['chapters']],['roles','story','saju_a','crisis','tip'])
                for key in ('roles','story','saju_a','crisis','tip','ending'):
                    self.assertGreater(len(report[key].strip()),40 if key!='ending' else 12)
                self.assertTrue(report.get('questions'))
                self.assertEqual(len({q.strip() for q in report['questions']}),len(report['questions']))
    def test_ten_other_archetypes_are_distinct(self):
        self.assertEqual(len(EDITION),10)
        titles=[v[0] for v in EDITION.values()]
        self.assertEqual(len(set(titles)),10)
        for couple in DB:
            if couple['id'] not in EDITION:continue
            with self.subTest(couple=couple['id']):
                report=make_report(self.a,self.b,self.rel,couple,describe(self.rel['vector'],couple['id']))
                self.assertIn(EDITION[couple['id']][0],report['roles'])
                self.assertIn(EDITION[couple['id']][1].replace('**',''),report['story'].replace('**',''))
                self.assertNotIn('백소정',report['roles']+report['story']+report['crisis']+report['tip'])
    def test_input_swap_preserves_archetype_and_story(self):
        for couple in DB:
            with self.subTest(couple=couple['id']):
                story=describe(self.rel['vector'],couple['id'])
                ab=make_report(self.a,self.b,self.rel,couple,story)
                ba=make_report(self.b,self.a,self.rel,couple,story)
                if couple['id']=='c06':
                    from c06_report import TALE
                    self.assertTrue(ab['story'].replace('**','').startswith(TALE.replace('**','')))
                    self.assertTrue(ba['story'].replace('**','').startswith(TALE.replace('**','')))
                else:
                    self.assertEqual(ab['story'],ba['story'])
                self.assertEqual([c['title'] for c in ab['chapters']],[c['title'] for c in ba['chapters']])
    def test_no_unverified_deterministic_claims(self):
        for couple in DB:
            if couple['id'] not in EDITION:continue
            with self.subTest(couple=couple['id']):
                report=make_report(self.a,self.b,self.rel,couple,describe(self.rel['vector'],couple['id']))
                for key in ('roles','saju_a'):
                    self.assertNotIn('당신은 반드시',report[key])
                    self.assertNotIn('운명적으로',report[key])

if __name__=='__main__':unittest.main()

"""Quality checks for ten distinct five-chapter archetype reports."""
import copy
import unittest
from engine import person
from matcher import DB
from relationship_v08 import relation
from story_report import make_report
from other_reports import LENSES, AXES
from individual_scenes import SCENES

class EditorialQuality(unittest.TestCase):
    def setUp(self):
        self.a=person(1992,3,18,16)
        self.b=person(1992,4,30,1)
        self.rel=relation(self.a,self.b)

    def test_all_ten_have_unique_original_scenes(self):
        self.assertEqual(set(LENSES),set(SCENES))
        self.assertEqual(len(set(v[0] for v in SCENES.values())),10)
        for c in DB:
            if c['id'] not in SCENES: continue
            r=make_report(self.a,self.b,self.rel,c,{})
            self.assertEqual(len(r['chapters']),5,c['id'])
            self.assertEqual(r['sections'],['roles','story','saju_a','crisis','tip'])
            for text in SCENES[c['id']]:
                self.assertIn(text,r['story']+r['crisis']+r['tip'],c['id'])
            self.assertEqual(r['saju_a'].count(LENSES[c['id']][4]),0,c['id'])
            self.assertIn(self.a['day_pillar'][0],r['roles'])
            self.assertIn(self.b['day_pillar'][0],r['roles'])
            self.assertNotIn('백소정',r['story']+r['tip'])
            if c.get('relationship_kind')=='friendship':
                self.assertIn('우정',r['tip'])
                self.assertNotIn('연인',r['story']+r['tip'])

    def test_six_axes_change_independently(self):
        for c in DB:
            if c['id'] not in SCENES: continue
            for axis in AXES:
                reports=[]
                for value in (30,55,80):
                    rel=copy.deepcopy(self.rel)
                    rel['vector'][axis]=value
                    before=copy.deepcopy(rel)
                    r=make_report(self.a,self.b,rel,c,{})
                    self.assertEqual(rel,before)
                    reports.append(r)
                chapter='saju_a' if axis in ('attraction','security','growth') else 'crisis'
                self.assertEqual(len(set(r[chapter] for r in reports)),3,(c['id'],axis))
                self.assertEqual(len(set(r['tip'] for r in reports)),3,(c['id'],axis))

    def test_gender_and_missing_birth_time(self):
        a=person(1988,6,12)
        b=person(1995,12,1)
        for c in DB:
            if c['id'] not in SCENES: continue
            r=make_report(a,b,relation(a,b),c,{})
            self.assertIn('시주는 계산에서 제외',r['roles'])
            gendered=make_report(dict(a,gender='male'),dict(b,gender='female'),relation(a,b),c,{})
            self.assertEqual(r['roles'],gendered['roles'])
            self.assertNotEqual(r['roles'],make_report(self.a,self.b,self.rel,c,{})['roles'])

if __name__=='__main__':
    unittest.main()

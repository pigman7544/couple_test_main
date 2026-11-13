import unittest
from engine import person
from matcher import DB
from relationship_v08 import relation
from story_report import make_report
from editorial_readings import READINGS


class EditorialReadings(unittest.TestCase):
    def test_all_twelve_have_comparable_length_and_distinct_readings(self):
        self.assertEqual(len(READINGS), 10)
        self.assertEqual(len(set(READINGS.values())), 10)
        for dates in (((1992,3,18,16),(1992,4,30,1)), ((1988,6,12),(1995,12,1)), ((2000,1,1,0),(2001,12,28,23))):
            a, b = (person(*d) for d in dates)
            reports = {c['id']: make_report(a,b,relation(a,b),c,{}) for c in DB}
            baseline = sum(len(reports['c06'][k]) for k in reports['c06']['sections'])
            for cid, r in reports.items():
                self.assertEqual(len(r['chapters']), 3 if cid=='c11' else 5)
                size = sum(len(r[k]) for k in r['sections'])
                self.assertGreaterEqual(size / baseline, .90, (cid, size, baseline))
                self.assertLess(size / baseline, 1.20, cid)
                if cid in READINGS and cid != 'c11':
                    self.assertIn(READINGS[cid].replace('**',''), r['story'].replace('**',''))
                    self.assertIn('문학적 해설', r['story'])


if __name__ == '__main__':
    unittest.main()

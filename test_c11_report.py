"""Production-matched A/B, full-chart evidence, source boundaries and roles."""
import copy
import json
import re
import unittest
from pathlib import Path
from engine import person
from matcher import DB
from relationship_v08 import relation
from server import compute
from story_report import make_report
from c06_chart import extract
from c11_report import TALE

class C11ReportTests(unittest.TestCase):
    def test_pillar_provenance_and_story_for_new_readers(self):
        from c06_narrative import basis, GOD_MEANING
        from c06_chart import GROUP
        for case in json.loads(Path('tests/fixtures/c11_comparison.json').read_text(encoding='utf8')):
            r=compute(case['payload'],True)['full_report']
            for who in ('a','b'):
                x=r['chart_evidence'][who]
                text=basis('당신',x)
                for word in ('일간','월주','연주','시주',x['season']):
                    self.assertIn(word,text)
                self.assertIn(GOD_MEANING[GROUP[x['visible_gods']['year_pillar']]],text)
                self.assertIn(GOD_MEANING[GROUP[x['anchors']['hour']]],text)
                # Independent recalculation verifies every visible/hidden
                # contribution, including the year; weights are editorial.
                expected={k:0 for k in ('self','voice','care','promise','reflect')}
                for pos,god in x['anchors'].items(): expected[GROUP[god]]+=3 if pos=='month' else 2
                for god in x['visible_gods'].values(): expected[GROUP[god]]+=1
                for values in x['hidden'].values():
                    for value in values: expected[GROUP[value['god']]]+=.25
                self.assertEqual({k:v for k,v in expected.items() if v},x['editorial_weights'])
        self.assertEqual(len(TALE.split('\n\n')),5)
        self.assertEqual(TALE.count('◆ '),2)
        for fact in ('군인 위컴','제인','빙리','편지','여동생','가디너','리디아','결혼을 약속'):
            self.assertIn(fact,TALE)
        x=extract(person(1996,12,13))
        self.assertNotIn('시주',basis('당신',x))

    def test_real_samples_differ_and_preserve_source(self):
        reports=[]
        for case in json.loads(Path('tests/fixtures/c11_comparison.json').read_text(encoding='utf8')):
            response=compute(case['payload'],True)
            self.assertEqual(response['couple']['id'],'c11')
            self.assertEqual(response,compute(case['payload'],True))
            r=response['full_report'];reports.append(r)
            self.assertEqual(len(r['chapters']),5)
            heads=re.findall(r'^◆ \*\*(.*?)\*\*',r['roles'],re.M)
            self.assertEqual(len(heads),2)
            self.assertEqual({h.split('를 닮은')[0] for h in heads},{'엘리자베스','다아시'})
            self.assertTrue(r['story'].replace('**','').startswith(TALE.replace('**','')))
            self.assertIn('가상 장면',r['crisis'])
            for key in r['sections']:
                self.assertNotRegex(r[key],r'\d+(?:\.\d+)?/(?:10|100)|\d+점|지장간|월령|십성|상극')
                for para in r[key].split('\n\n'):
                    lines=para.split('\n')
                    if lines[0].startswith('◆ '): lines.pop(0)
                    self.assertLessEqual(len(re.findall(r'\*\*(.+?)\*\*','\n'.join(lines))),2)
            self.assertFalse(r['chart_evidence']['a']['missing_hour'])
        self.assertEqual(reports[0]['story'],reports[1]['story'])
        for key in ('roles','saju_a','crisis','tip'):
            self.assertNotEqual(reports[0][key],reports[1][key])
        self.assertEqual(reports[0]['chart_evidence']['a']['theme'],'care')
        self.assertEqual(reports[1]['chart_evidence']['a']['theme'],'reflect')
        self.assertIn('예약',reports[0]['crisis']);self.assertIn('예약',reports[0]['tip'])
        self.assertIn('저녁 8시',reports[1]['tip'])
        self.assertIn('**예약 전에**',reports[0]['tip'])
        self.assertIn('**오늘 저녁 8시에**',reports[1]['tip'])

    def test_same_day_and_scores_other_pillars_change_reading(self):
        a,b=person(1999,1,22,1),person(1998,11,9,21)
        rel=relation(a,b);couple=next(c for c in DB if c['id']=='c11')
        original=copy.deepcopy((a,b,rel))
        r=make_report(a,b,rel,couple,{})
        # Synthetic chart sensitivity probe, never submitted as a real date.
        changed=dict(a,month_pillar='甲寅',hour_pillar='丙寅')
        s=make_report(changed,b,rel,couple,{})
        self.assertEqual(a['day_pillar'],changed['day_pillar'])
        for key in ('roles','saju_a','crisis','tip'):
            self.assertNotEqual(r[key],s[key],key)
        self.assertEqual((a,b,rel),original)
        self.assertEqual(r['chart_evidence']['a'],extract(a))

    def test_missing_time_gender_and_swap(self):
        a,b=person(1996,12,13),person(1986,10,21)
        c=next(c for c in DB if c['id']=='c11');rel=relation(a,b)
        r=make_report(a,b,rel,c,{})
        self.assertTrue(r['chart_evidence']['a']['missing_hour'])
        self.assertNotIn('hour',r['chart_evidence']['a']['anchors'])
        self.assertIn('시주는 계산에서 제외',r['roles'])
        self.assertEqual(r,make_report(dict(a,gender='male'),dict(b,gender='female'),rel,c,{}))
        swapped=make_report(b,a,relation(b,a),c,{})
        self.assertEqual(r['story'],swapped['story'])
        self.assertEqual(r['chart_evidence']['a'],swapped['chart_evidence']['b'])

if __name__=='__main__': unittest.main()

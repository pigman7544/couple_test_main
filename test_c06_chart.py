import copy
import json
from pathlib import Path
import subprocess
import unittest
from c06_chart import extract,cross,HIDDEN,THEMES
from c06_report import TALE
from engine import person
from server import compute
from story_report import ten_god,make_report
from matcher import DB
from relationship_v08 import relation

class FullChartTests(unittest.TestCase):
    def test_roles_connect_actual_assignment_to_tale_and_chart(self):
        from story_report import role_assignment
        c = next(c for c in DB if c['id']=='c06')
        for a,b in ((person(1985,1,11,16),person(1992,4,30,1)),
                    (person(1992,4,30,1),person(1985,6,10,16))):
            r=make_report(a,b,relation(a,b),c,{})
            text=r['roles'].replace('**','')
            lead=role_assignment(a,b)[0]
            label='당신' if lead=='첫 번째 사람' else '상대방'
            self.assertIn(label+'은 백소정을 닮았어요',text)
            headings=[line for line in text.splitlines() if line.startswith('◆ ')]
            expected=['백소정을 닮은 당신','허선을 닮은 상대방'] if label=='당신' else ['허선을 닮은 당신','백소정을 닮은 상대방']
            self.assertEqual(headings,['◆ '+h for h in expected])
            for phrase in ('우산을 빌려주면서','영초를 구하러','명확한 약속과 일관성',
                           '문학적 해석','서로를 이해하는 속도'):
                self.assertIn(phrase,text)
            for phrase in ('경금','단단한 쇠','병화','태양'):
                self.assertIn('**'+phrase+'**',r['roles'])

    def test_day_master_leads_and_season_modifies_same_core(self):
        from c06_narrative import basis
        from story_report import count_elements
        a,b=[person(1985,m,d,16) for m,d in ((1,11),(6,10))]
        self.assertEqual(count_elements(a),count_elements(b))
        self.assertEqual(a['day_pillar'][0],b['day_pillar'][0])
        texts=[basis('당신',extract(p)) for p in (a,b)]
        for text in texts:
            self.assertTrue(text.startswith('당신의 일간은 **경금(庚)**'))
            self.assertLess(text.index('일간'),text.index('태어난'))
            self.assertIn('명확한 약속과 일관성',text)
            self.assertNotRegex(text,r'월령|정인|정관|편인|통근|지장간|십성|읽어 볼게요|살펴요')
        self.assertIn('겨울',texts[0]);self.assertIn('신중함',texts[0])
        self.assertIn('여름',texts[1]);self.assertIn('약속',texts[1])
        self.assertNotEqual(texts[0],texts[1])

    def test_conventional_tables_and_season_roots(self):
        p=person(1985,1,11,16)
        x=extract(p)
        self.assertEqual(x['season'],'겨울')
        self.assertEqual(HIDDEN['丑'],'己癸辛')
        self.assertEqual(ten_god('甲','己'),'정재')
        self.assertEqual(ten_god('甲','癸'),'정인')
        self.assertEqual(p['day_pillar'],'庚戌')
        self.assertEqual(x['roots'],['month_pillar','day_pillar','hour_pillar'])

    def test_real_same_count_same_day_stem_but_all_chapters_differ(self):
        cases=json.loads(Path('tests/fixtures/c06_comparison.json').read_text(encoding='utf8'))
        reports=[compute(c['payload'],True) for c in cases]
        a,b=[r['full_report'] for r in reports]
        self.assertTrue(all(r['couple']['id']=='c06' for r in reports))
        self.assertEqual(cases[0]['counts_a'],cases[1]['counts_a'])
        self.assertEqual(cases[0]['counts_b'],cases[1]['counts_b'])
        self.assertEqual(a['chart_evidence']['a']['pillars']['day_pillar'][0],b['chart_evidence']['a']['pillars']['day_pillar'][0])
        for key in a['sections']+['questions','ending']:
            self.assertNotEqual(a[key],b[key],key)
        for c,r in zip(cases,reports):
            self.assertEqual(r,compute(c['payload'],True))
            self.assertTrue(r['full_report']['story'].replace('**','').startswith(TALE.replace('**','')))
            self.assertEqual(r,c['response'])

    def test_hour_unknown_does_not_get_invented(self):
        p=person(1992,3,18)
        x=extract(p)
        self.assertTrue(x['missing_hour'])
        self.assertNotIn('hour',x['anchors'])
        self.assertNotIn('hour_pillar',x['hidden'])
        self.assertFalse(any(r['a']=='hour_pillar' for r in cross(p,person(1992,4,30,1))))

    def test_hour_alone_changes_reading_without_mutating_inputs(self):
        a,b=person(1992,3,18,1),person(1992,4,30,1)
        later=person(1992,3,18,16)
        self.assertEqual(a['day_pillar'],later['day_pillar'])
        original=copy.deepcopy((a,b))
        self.assertNotEqual(extract(a),extract(later))
        c=next(c for c in DB if c['id']=='c06')
        r=make_report(a,b,relation(a,b),c,{})
        s=make_report(later,b,relation(later,b),c,{})
        for k in ('roles','crisis','tip'): self.assertNotEqual(r[k],s[k])
        self.assertEqual((a,b),original)

    def test_cross_positions_and_no_transformation(self):
        a={'year_pillar':'甲子','month_pillar':'丙寅','day_pillar':'甲午','hour_pillar':None}
        b={'year_pillar':'己丑','month_pillar':'丁卯','day_pillar':'辛酉','hour_pillar':'庚申'}
        links=cross(a,b)
        self.assertIn(dict(a='year_pillar',b='year_pillar',chars='甲己',kind='천간합'),links)
        self.assertIn(dict(a='month_pillar',b='hour_pillar',chars='寅申',kind='육충'),links)

    def test_calculator_matcher_and_c01_unchanged_from_start(self):
        for path in ('engine.py','relationship_v08.py','matcher.py','couples.json','archetypes.json'):
            before=subprocess.check_output(['git','show','388179f:'+path])
            self.assertEqual(Path(path).read_bytes().replace(b'\r\n',b'\n'),before)
        namespace={}
        exec(compile(subprocess.check_output(['git','show','388179f:story_report.py']).decode('utf8'),'baseline_story_report.py','exec'),namespace)
        a,b=person(1992,3,18,16),person(1992,4,30,1)
        rel=relation(a,b)
        for couple in DB:
            if couple['id']!='c01':continue  # Other types now intentionally repaired; c06 has dedicated fixtures.
            self.assertEqual(make_report(a,b,rel,couple,{}),namespace['make_report'](a,b,rel,couple,{}),couple['id'])

    def test_original_water_fire_sample_no_longer_overwrites_full_chart(self):
        p={'a':{'date':'1992-03-18','time':'16:00'},'b':{'date':'1992-04-30','time':'01:00'}}
        r=compute(p,True)
        self.assertEqual(r['couple']['id'],'c06')
        self.assertIn('chart_evidence',r['full_report'])
        self.assertIn('hidden',r['full_report']['chart_evidence']['a'])
        self.assertNotIn('지장간',r['full_report']['roles'])

    def test_reader_copy_has_no_methodology_but_keeps_story_boundaries(self):
        cases=json.loads(Path('tests/fixtures/c06_comparison.json').read_text(encoding='utf8'))
        for c in cases:
            r=compute(c['payload'],True)['full_report']
            text=' '.join(r[k] for k in r['sections'])
            self.assertNotRegex(text,r'월령|정인|정관|편인|통근|지장간|십성|시주|일지[의를에]|명식|읽어 볼게요|확인해 주세요|다음 장에서는')
            self.assertIn('문학적 해설',r['story'])
            self.assertIn('가상 장면',r['crisis'])
            self.assertIn('같은 장면을 다시',r['tip'])

if __name__=='__main__': unittest.main()

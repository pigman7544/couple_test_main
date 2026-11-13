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
    def test_keyword_edit_changes_only_c11_roles(self):
        import subprocess,types,c11_report
        from unittest.mock import patch
        baseline=types.ModuleType('before_keyword_echo')
        exec(subprocess.check_output(['git','show','0140306:c11_report.py']).decode('utf8'),baseline.__dict__)
        for case in json.loads(Path('tests/fixtures/c11_comparison.json').read_text(encoding='utf8')):
            current=compute(case['payload'],True)
            preview=compute(case['payload'])
            with patch.object(c11_report,'enrich',baseline.enrich):
                old=compute(case['payload'],True)
                self.assertEqual(preview,compute(case['payload']))
            self.assertEqual({k:v for k,v in current['full_report'].items() if k!='roles'},
                             {k:v for k,v in old['full_report'].items() if k!='roles'})
            self.assertEqual({k:v for k,v in current.items() if k!='full_report'},
                             {k:v for k,v in old.items() if k!='full_report'})

    def test_plain_language_and_personalized_keyword_placement(self):
        keyword_sets=[]
        for case in json.loads(Path('tests/fixtures/c11_comparison.json').read_text(encoding='utf8')):
            r=compute(case['payload'],True)['full_report']
            body='\n'.join(r[k] for k in r['sections'])
            self.assertNotRegex(body,r'겹쳐|닿아|맞닿|교차해|의 결(?:[ ,.!]|$)|비춰 보|비춰 볼|해석 방법')
            parts=re.split(r'^◆ \*\*.+?를 닮은 (?:당신|상대방)\*\*\n',r['roles'],flags=re.M)[1:]
            keys=[]
            for part in parts:
                line=part.split('\n')[0]
                words=re.findall(r'\*\*(.+?)\*\*',line)
                self.assertEqual(len(words),2)
                self.assertTrue(all(len(w)<=18 for w in words))
                self.assertRegex(part,'닮|비슷')
                self.assertIn('일간',part)
                self.assertIn('월주',part)
                explanation=part.split('\n\n',1)[1]
                paragraphs=explanation.split('\n\n')
                for index,word in enumerate(words):
                    self.assertEqual(explanation.count(word),1)
                    self.assertEqual(explanation.count('**'+word+'**'),1)
                    self.assertIn('**'+word+'**',paragraphs[1 if index==0 else 4])
                keys.append(words)
            keyword_sets.append(keys)
        self.assertNotEqual(keyword_sets[0][0],keyword_sets[1][0])
        self.assertNotEqual(keyword_sets[0][1],keyword_sets[1][1])

    def test_edit_preserves_preview_plot_evidence_and_other_types(self):
        import subprocess,types,c11_report
        from unittest.mock import patch
        baseline=types.ModuleType('before_edit')
        exec(subprocess.check_output(['git','show','a376cc6:c11_report.py']).decode('utf8'),baseline.__dict__)
        for case in json.loads(Path('tests/fixtures/c11_comparison.json').read_text(encoding='utf8')):
            current=compute(case['payload'],True)
            preview=compute(case['payload'])
            with patch.object(c11_report,'enrich',baseline.enrich):
                old=compute(case['payload'],True)
                self.assertEqual(preview,compute(case['payload']))
            for key in ('chart_evidence','plot','sections','chapters','questions','ending'):
                self.assertEqual(current['full_report'][key],old['full_report'][key])
            self.assertEqual({k:v for k,v in current.items() if k!='full_report'},
                             {k:v for k,v in old.items() if k!='full_report'})
        a,b=person(1999,1,22,1),person(1998,11,9,21)
        for couple in DB:
            if couple['id']=='c11': continue
            current=make_report(a,b,relation(a,b),couple,{})
            with patch.object(c11_report,'enrich',baseline.enrich):
                self.assertEqual(current,make_report(a,b,relation(a,b),couple,{}))

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
            self.assertEqual(len(r['chapters']),3)
            heads=re.findall(r'^◆ \*\*(.*?)\*\*',r['roles'],re.M)
            self.assertEqual(len(heads),2)
            self.assertEqual({h.split('를 닮은')[0] for h in heads},{'엘리자베스','다아시'})
            self.assertTrue(r['plot']['body'].replace('**','') == TALE.replace('**',''))
            self.assertEqual(r['story'],''); self.assertEqual(r['crisis'],'')
            self.assertIn('가상 장면',r['saju_a'])
            self.assertEqual(r['sections'],['roles','saju_a','tip'])
            for key in r['sections']:
                self.assertNotRegex(r[key],r'\d+(?:\.\d+)?/(?:10|100)|\d+점|지장간|월령|십성')
                for para in r[key].split('\n\n'):
                    lines=para.split('\n')
                    if lines[0].startswith('◆ '): lines.pop(0)
                    self.assertLessEqual(len(re.findall(r'\*\*(.+?)\*\*','\n'.join(lines))),2)
            self.assertFalse(r['chart_evidence']['a']['missing_hour'])
        self.assertEqual(reports[0]['story'],reports[1]['story'])
        for key in ('roles','saju_a','tip'):
            self.assertNotEqual(reports[0][key],reports[1][key])
        self.assertEqual(reports[0]['chart_evidence']['a']['theme'],'care')
        self.assertEqual(reports[1]['chart_evidence']['a']['theme'],'reflect')
        self.assertIn('예약',reports[0]['saju_a']);self.assertIn('예약',reports[0]['tip'])
        self.assertIn('저녁 8시',reports[1]['tip'])
        self.assertIn('**예약 전에**',reports[0]['tip'])
        self.assertIn('**오늘 저녁 8시에**',reports[1]['tip'])

    def test_three_chapters_preserve_preview_and_all_other_reports(self):
        import subprocess, types
        import c11_report
        from unittest.mock import patch
        baseline=types.ModuleType('old_c11')
        exec(subprocess.check_output(['git','show','9a6b2b0:c11_report.py']).decode('utf8'),baseline.__dict__)
        for case in json.loads(Path('tests/fixtures/c11_comparison.json').read_text(encoding='utf8')):
            current=compute(case['payload'])
            with patch.object(c11_report,'enrich',baseline.enrich):
                self.assertEqual(current,compute(case['payload']))
            report=compute(case['payload'],True)['full_report']
            self.assertEqual([c['key'] for c in report['chapters']],['roles','saju_a','tip'])
            self.assertEqual(report['plot']['body'],TALE)
            for who in ('a','b'):
                x=report['chart_evidence'][who]
                self.assertIn(x['pillars']['month_pillar'],report['roles'])
            self.assertIn('오행에서는',report['saju_a'])
            for kind in {x['kind'] for x in report['chart_evidence']['cross']}:
                self.assertIn(kind,report['saju_a'])
        a,b=person(1999,1,22,1),person(1998,11,9,21)
        # Compare actual original generator output, not reconstructed assertions.
        for couple in DB:
            if couple['id']=='c11': continue
            current=make_report(a,b,relation(a,b),couple,{})
            with patch.object(c11_report,'enrich',baseline.enrich):
                self.assertEqual(current,make_report(a,b,relation(a,b),couple,{}))
            self.assertEqual(len(current['chapters']),5)
            self.assertNotIn('plot',current)

    def test_same_day_and_scores_other_pillars_change_reading(self):
        a,b=person(1999,1,22,1),person(1998,11,9,21)
        rel=relation(a,b);couple=next(c for c in DB if c['id']=='c11')
        original=copy.deepcopy((a,b,rel))
        r=make_report(a,b,rel,couple,{})
        # Synthetic chart sensitivity probe, never submitted as a real date.
        changed=dict(a,month_pillar='甲寅',hour_pillar='丙寅')
        s=make_report(changed,b,rel,couple,{})
        self.assertEqual(a['day_pillar'],changed['day_pillar'])
        for key in ('roles','saju_a','tip'):
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

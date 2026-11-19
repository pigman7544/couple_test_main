"""Evidence provenance, interaction sensitivity and isolation from other reports."""
import copy
import json
import subprocess
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import person
from matcher import DB
from relationship_v08 import relation
from story_report import make_report, count_elements
from c11_integrated import extract, character_keywords


class IntegratedChartTests(unittest.TestCase):
    def test_real_structure_and_independent_flow_edges(self):
        from server import compute
        expected=[('shared_care','measured_voice'),('considered_response','supported_choice')]
        element={s:e for ss,e in [('甲乙','wood'),('丙丁','fire'),('戊己','earth'),('庚辛','metal'),('壬癸','water')] for s in ss}
        generate=dict(zip(('wood','fire','earth','metal','water'),('fire','earth','metal','water','wood')))
        control=dict(zip(('wood','earth','water','fire','metal'),('earth','water','fire','metal','wood')))
        for case,rules in zip(json.loads(Path('tests/fixtures/c11_comparison.json').read_text()),expected):
            r=compute(case['payload'],True)['full_report']
            for who,rule in zip(('a','b'),rules):
                x=r['chart_evidence'][who];s=x['synthesis']
                self.assertEqual(s['rule'],rule)
                nodes={n['id']:n for n in s['nodes']}
                expected_edges=set()
                for ai,a in nodes.items():
                    for bi,b in nodes.items():
                        if ai==bi: continue
                        ea,eb=element[a['stem']],element[b['stem']]
                        kind='동류' if ea==eb else '생' if generate[ea]==eb else '극' if control[ea]==eb else None
                        if kind: expected_edges.add((ai,bi,kind))
                self.assertEqual(expected_edges,{(e['source'],e['target'],e['kind']) for e in s['edges']})
                for n in nodes.values():
                    p=x['pillars'][n['position']]
                    if n['layer']=='visible': self.assertEqual(n['stem'],p[0])
                    else: self.assertIn(n['stem'],[h['stem'] for h in x['hidden'][n['position']]])
                for path in s['support_paths']:
                    self.assertIn((path[0],path[1],'생'),expected_edges)
                    self.assertIn((path[1],path[2],'생'),expected_edges)
                self.assertEqual(x['pillars']['day_pillar'][0],nodes['day_pillar:visible']['stem'])
        b=extract(person(1996,12,13,21))
        ids={n['id']:n for n in b['synthesis']['nodes']}
        self.assertTrue(any([ids[i]['stem'] for i in p]==['庚','癸','甲'] for p in b['synthesis']['support_paths']))

    def test_same_day_and_element_counts_different_month_structure(self):
        a,b=person(1999,1,22,1),person(1998,11,9,21)
        original=copy.deepcopy(a)
        # Synthetic permutation, not a birth-date fixture: same eight characters.
        changed=dict(a,year_pillar=a['month_pillar'],month_pillar=a['year_pillar'])
        self.assertEqual(count_elements(a),count_elements(changed))
        self.assertEqual(a['day_pillar'],changed['day_pillar'])
        aa,cc=extract(a),extract(changed)
        self.assertNotEqual(aa['synthesis']['rule'],cc['synthesis']['rule'])
        self.assertNotEqual(character_keywords(aa),character_keywords(cc))
        c=next(c for c in DB if c['id']=='c11');rel=relation(a,b)
        r,t=make_report(a,b,rel,c,{}),make_report(changed,b,rel,c,{})
        for key in ('roles','saju_a','tip'): self.assertNotEqual(r[key],t[key])
        self.assertEqual(a,original)

    def test_all_other_types_exactly_preserved_for_both_real_samples(self):
        import c11_report
        old=types.ModuleType('before_integration')
        exec(subprocess.check_output(['git','show','00f833f:c11_report.py']).decode('utf8'),old.__dict__)
        for a,b in [(person(1999,1,22,1),person(1998,11,9,21)),
                    (person(1996,12,13,21),person(1986,10,21,9))]:
            for c in DB:
                if c['id']=='c11': continue
                current=make_report(a,b,relation(a,b),c,{})
                with patch.object(c11_report,'enrich',old.enrich):
                    self.assertEqual(current,make_report(a,b,relation(a,b),c,{}))

    def test_missing_hour_has_no_invented_nodes_and_deterministic_rules(self):
        a=person(1996,12,13)
        x=extract(a)
        self.assertTrue(x['missing_hour'])
        self.assertFalse(any(n['position']=='hour_pillar' for n in x['synthesis']['nodes']))
        self.assertEqual(x,extract(a))
        self.assertEqual(x,extract(dict(a,gender='female')))

    def test_internal_clash_changes_conclusion_with_same_day_month_and_counts(self):
        a=person(1998,11,9,21)
        changed=dict(a,year_pillar='戊卯')  # synthetic same-element branch substitution
        self.assertEqual(count_elements(a),count_elements(changed))
        self.assertEqual(a['day_pillar'],changed['day_pillar'])
        self.assertEqual(a['month_pillar'],changed['month_pillar'])
        before,after=extract(a),extract(changed)
        self.assertTrue(any(l['kind']=='육충' for l in before['internal']))
        self.assertFalse(any(l['kind']=='육충' for l in after['internal']))
        self.assertEqual(before['synthesis']['rule'],'measured_voice')
        self.assertEqual(after['synthesis']['rule'],'voice')
        self.assertNotEqual(character_keywords(before),character_keywords(after))


if __name__=='__main__': unittest.main()

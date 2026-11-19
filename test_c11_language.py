"""Editorial contract and exact preservation of the integrated chart model."""
import json
import re
import subprocess
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import c11_report
from server import compute


class C11LanguageTests(unittest.TestCase):
    def test_traits_and_concrete_source_connections(self):
        expected=[['책임감','독립심','솔직함','조심성'],
                  ['신중함','자기성찰','주관이 뚜렷함','고집스러움']]
        cases=json.loads(Path('tests/fixtures/c11_comparison.json').read_text(encoding='utf8'))
        for case,words in zip(cases,expected):
            r=compute(case['payload'],True)['full_report']
            parts=re.split(r'^◆ \*\*.+?를 닮은 (?:당신|상대방)\*\*\n',r['roles'],flags=re.M)[1:]
            actual=[]
            for part in parts:
                keys=re.findall(r'\*\*(.+?)\*\*',part.split('\n')[0]);actual+=keys
                for key in keys:
                    self.assertEqual(part.count('**'+key+'**'),2)
            self.assertEqual(actual,words)
            body='\n'.join(r[k] for k in r['sections'])
            self.assertNotRegex(body,'함께 꾸리는 배려|관계의 여백|선택의 자리|마음의 속도|다시 묻는 대화|도움을 청하는 여유')
        self.assertIn('위컴의 말을 쉽게 믿고',r['roles'])
        self.assertIn('제인에 대한 자기 판단이 잘못',r['roles'])

    def test_a312031_evidence_preview_and_response_contract_preserved(self):
        old_integrated=types.ModuleType('old_integrated')
        exec(subprocess.check_output(['git','show','a312031:c11_integrated.py']).decode('utf8'),old_integrated.__dict__)
        old_report=types.ModuleType('old_report')
        exec(subprocess.check_output(['git','show','a312031:c11_report.py']).decode('utf8'),old_report.__dict__)
        old_report.enrich.__globals__.update({k:getattr(old_integrated,k) for k in ('extract','character_keywords','person_text','pair_context')})
        for case in json.loads(Path('tests/fixtures/c11_comparison.json').read_text(encoding='utf8')):
            current=compute(case['payload'],True);preview=compute(case['payload'])
            with patch.object(c11_report,'enrich',old_report.enrich):
                old=compute(case['payload'],True)
                self.assertEqual(preview,compute(case['payload']))
            self.assertEqual({k:v for k,v in current.items() if k!='full_report'},
                             {k:v for k,v in old.items() if k!='full_report'})
            for key in ('chart_evidence','plot','sections','questions','ending'):
                self.assertEqual(current['full_report'][key],old['full_report'][key])
            self.assertEqual([c['key'] for c in current['full_report']['chapters']],
                             [c['key'] for c in old['full_report']['chapters']])

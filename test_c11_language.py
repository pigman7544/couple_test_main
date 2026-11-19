"""Editorial contract and exact preservation of the integrated chart model."""
import json
import re
import unittest
from pathlib import Path
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

    def test_actual_chart_evidence_is_available_without_month_copy(self):
        cases = json.loads(Path('tests/fixtures/c11_comparison.json').read_text(encoding='utf8'))
        for case in cases:
            r = compute(case['payload'], True)['full_report']
            for label in ('a', 'b'):
                pillars = r['chart_evidence'][label]['pillars']
                self.assertIn(pillars['month_pillar'], r['pillars_' + label])
                self.assertNotIn(pillars['month_pillar'], r['roles'])

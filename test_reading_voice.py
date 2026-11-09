"""Editorial regressions: all symbols/branches and preservation against PR16."""
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import types
import unittest
from engine import person
from matcher import DB
from relationship_v08 import relation, STEMS
from story_report import make_report, relationship_style, count_elements
from reading_voice import profile, connection

class EssayVoice(unittest.TestCase):
    def test_all_stems_and_connections_are_readable(self):
        base = person(1992, 3, 18, 16)
        for stem in STEMS:
            a = dict(base, day_pillar=stem + base['day_pillar'][1])
            prose = profile('당신', relationship_style(a), count_elements(a))
            self.assertIn('일간은', prose)
            self.assertIn('떠올려 보세요', prose)
            self.assertNotRegex(prose, '십성|천간|지지|월령|지장간')
            for other in STEMS:
                b = dict(base, day_pillar=other + base['day_pillar'][1])
                text = connection(a, b)
                self.assertRegex(text, '연락|약속|데이트')
                self.assertNotIn('생하는', text)

    def test_all_twelve_preserve_source_and_score_prose(self):
        a,b=person(1992,3,18,16),person(1992,4,30,1)
        rel=relation(a,b)
        original=copy.deepcopy((a,b,rel))
        current={c['id']:make_report(a,b,rel,c,{}) for c in DB}
        names=('c01_report','c06_report','other_reports','personalized_reading')
        saved={name:sys.modules[name] for name in names}
        try:
            for name in names:
                module=types.ModuleType(name)
                code=subprocess.check_output(['git','show',f'bfc0922:{name}.py']).decode('utf8')
                exec(compile(code,name+'.py','exec'),module.__dict__)
                sys.modules[name]=module
            before={c['id']:make_report(a,b,rel,c,{}) for c in DB}
        finally:
            sys.modules.update(saved)
        examples=[]
        for cid,r in current.items():
            old=before[cid]
            for key in ('story','chapters','sections','teaser','tagline','questions','ending','tip'):
                self.assertEqual(str(old[key]).replace('**',''),str(r[key]).replace('**',''),(cid,key))
            self.assertEqual(old['crisis'].replace('**',''),r['crisis'].replace('**',''),cid)
            for key in ('saju_a','crisis'):
                def axes(text):
                    return [block.replace('**','') for block in text.split('\n\n') if re.match(r'◆ .*\d+/10', block)]
                self.assertEqual(axes(old[key]), axes(r[key]), (cid, key))
                self.assertEqual(re.findall(r'\d+/10',old[key]),re.findall(r'\d+/10',r[key]))
            self.assertNotRegex(r['roles'], '십성|천간|지지|월령|지장간')
            self.assertEqual(r['roles'].count('오행은 나무·불·흙·쇠·물'),1)
            self.assertEqual(r,make_report(a,b,rel,next(c for c in DB if c['id']==cid),{}))
            examples.append(dict(id=cid,before=old['roles'],after=r['roles'],chapter3=r['saju_a'],chapter4=r['crisis']))
        self.assertEqual((a,b,rel),original)
        Path('docs/qa-emphasis-examples.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__': unittest.main()

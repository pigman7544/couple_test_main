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

    def test_all_twelve_preserve_source_and_hide_scores(self):
        a,b=person(1992,3,18,16),person(1992,4,30,1)
        rel=relation(a,b)
        original=copy.deepcopy((a,b,rel))
        for couple in DB:
            r=make_report(a,b,rel,couple,{})
            self.assertEqual(r,make_report(a,b,rel,couple,{}))
            for key in r['sections']:
                self.assertNotRegex(r[key],r'\d+(?:\.\d+)?/(?:10|100)|\d+점')
            self.assertNotRegex(r['roles'],'십성|천간|지지|월령|지장간')
            if couple['id']=='c06':
                from c06_report import TALE
                self.assertTrue(r['story'].replace('**','').startswith(TALE.replace('**','')))
            elif couple['id']=='c11':
                from c11_report import TALE
                self.assertTrue(r['story'].replace('**','').startswith(TALE.replace('**','')))
            elif couple['id']!='c01':
                from individual_scenes import SCENES
                self.assertIn(SCENES[couple['id']][0].replace('**',''),r['story'].replace('**',''))
        self.assertEqual((a,b,rel),original)

if __name__=='__main__': unittest.main()

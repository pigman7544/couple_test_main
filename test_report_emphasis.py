"""Preserve prose and protect the editorial scan path across all score bands."""
import re
import unittest
from unittest.mock import patch
from engine import person
from matcher import DB
from relationship_v08 import relation
from story_report import make_report
from report_emphasis import emphasize


class EmphasisTests(unittest.TestCase):
    def test_literal_selection_and_quiet_paragraphs(self):
        value = '◆ **제목**\n짧은 설명이에요.\n\n먼저 설득하지 마세요. 서로 다른 기대를 확인해요.'
        self.assertEqual(emphasize(value, 'c06', 'crisis'),
                         '◆ **제목**\n짧은 설명이에요.\n\n먼저 설득하지 마세요. **서로 다른 기대**를 확인해요.')

    def test_all_types_bands_preserve_prose_headings_and_inputs(self):
        a, b = person(1992, 3, 18, 16), person(1992, 4, 30, 1)
        for couple in DB:
            for score in (30, 55, 75):
                rel = relation(a, b)
                rel['vector'] = dict.fromkeys(rel['vector'], score)
                with patch('report_emphasis.emphasize', side_effect=lambda s, *args: s):
                    before = make_report(a, b, rel, couple, {})
                after = make_report(a, b, rel, couple, {})
                self.assertEqual(after, make_report(a, b, rel, couple, {}))
                for key in before:
                    if isinstance(before[key], str):
                        self.assertEqual(before[key].replace('**', ''), after[key].replace('**', ''), (couple['id'], key))
                    else:
                        self.assertEqual(before[key], after[key])
                for key in after['sections']:
                    spans = []
                    for block in after[key].split('\n\n'):
                        lines = block.split('\n')
                        if lines[0].startswith('◆ '):
                            lines.pop(0)
                        body = '\n'.join(lines)
                        found = re.findall(r'\*\*(.+?)\*\*', body)
                        self.assertLessEqual(len(found), 1)
                        for phrase in found:
                            self.assertLessEqual(len(phrase), 32)
                            self.assertLess(len(phrase), len(body.replace('**', '')))
                            self.assertNotRegex(phrase, r'甲|乙|丙|丁|戊|己|庚|辛|壬|癸|일간|오행')
                        spans += found
                    self.assertTrue(spans, (couple['id'], score, key))


if __name__ == '__main__':
    unittest.main()

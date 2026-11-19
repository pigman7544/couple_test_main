"""Coverage of real-chart report composition and the editorial omission rule."""

from datetime import date, timedelta
import unittest

from engine import person
from matcher import DB
from relationship_v08 import relation
from report_evidence import CHARACTERS, ordered_people, select
from server import compute
from story_report import STEMS, make_report, role_assignment


class ReportEvidenceTests(unittest.TestCase):
    def test_c01_unsupported_chunhyang_and_supported_mongryong(self):
        payload = {'a': {'date': '1982-09-13'}, 'b': {'date': '1981-06-02', 'time': '03:00'}}
        preview, unlocked = compute(payload), compute(payload, unlock=True)
        self.assertEqual(preview['couple'], unlocked['couple'])
        self.assertEqual(unlocked['couple']['id'], 'c01')
        text = unlocked['full_report']['roles'].replace('**', '')
        chunhyang, mongryong = text.split('◆ 상대방에게 비춰 보는 이몽룡')
        self.assertIn('수청 요구를 거절해', chunhyang)
        self.assertNotIn('기토', chunhyang)
        self.assertIn('신금(辛)', mongryong)
        self.assertIn('약속을 행동으로 지키는 면', mongryong)
        for phrase in ('태어난 달의 글자를', '세부 조건', '주말 계획', '손에 잡히는 도움'):
            self.assertNotIn(phrase, text)

    def test_every_character_and_ordered_day_stem_pair(self):
        # Ten consecutive solar dates cover all day stems. Using real charts also
        # exercises the same role assignments and evidence extractors as the app.
        dates = [date(1995, 4, 7) + timedelta(days=i) for i in range(10)]
        charts = [person(d.year, d.month, d.day, hour=14 if i % 2 else None)
                  for i, d in enumerate(dates)]
        self.assertEqual({p['day_pillar'][0] for p in charts}, set(STEMS))
        self.assertEqual(set(CHARACTERS), {c['id'] for c in DB})
        for actions_by_character in CHARACTERS.values():
            for actions in actions_by_character:
                approved_stems = set()
                for action in actions:
                    self.assertTrue(action.source and action.event and action.meaning)
                    for reading in action.readings:
                        self.assertTrue(reading.trait and reading.reflection)
                        self.assertLessEqual(len(reading.trait), 32)
                        for stem in reading.stems:
                            self.assertIn(stem, STEMS)
                            self.assertNotIn(stem, approved_stems)
                            approved_stems.add(stem)

        for a in charts:
            for b in charts:
                rel = relation(a, b)
                for couple in DB:
                    cid = couple['id']
                    with self.subTest(cid=cid, a=a['day_pillar'], b=b['day_pillar']):
                        report = make_report(a, b, rel, couple, {})
                        self.assertEqual(report['sections'], [c['key'] for c in report['chapters']])
                        self.assertEqual(len(report['sections']), 3 if cid == 'c11' else 5)
                        self.assertNotIn('◆ ', report['saju_a'])
                        if cid == 'c11':
                            self.assertTrue(report['plot']['body'])
                            self.assertNotIn('◆ ', report['tip'])
                        for key in report['sections']:
                            self.assertTrue(report[key].strip())
                            self.assertNotIn('태어난 달의 글자를', report[key])
                        people = ordered_people(a, b)
                        if cid == 'c06':
                            lead, _, pa, pb = role_assignment(a, b)
                            labels = ('당신', '상대방') if lead == '첫 번째 사람' else ('상대방', '당신')
                            people = tuple((label, p['day_pillar'][0]) for label, p in zip(labels, (pa, pb)))
                        portraits = report['roles'].replace('**', '').split('◆ ')[1:]
                        self.assertEqual(len(portraits), 2)
                        for portrait, (label, stem), actions in zip(portraits, people, CHARACTERS[cid], strict=True):
                            action, reading = select(actions, stem)
                            self.assertTrue(portrait.startswith(label + '에게 비춰 보는'))
                            self.assertIn(action.event, portrait)
                            if reading:
                                self.assertIn(f'({stem})', portrait)
                                self.assertIn(reading.trait, portrait)
                                self.assertIn(reading.reflection, portrait)
                            else:
                                self.assertNotIn('일간', portrait)
                                self.assertEqual(portrait.strip().split('\n', 1)[1], f'{action.event} {action.meaning}')

    def test_alternate_action_is_used_before_fallback(self):
        penelope = CHARACTERS['c13'][1]
        action, reading = select(penelope, '壬')
        self.assertEqual(action, penelope[1])
        self.assertIn('수의', action.source)
        self.assertIsNotNone(reading)
        self.assertEqual(select(penelope, '丙'), (penelope[0], None))

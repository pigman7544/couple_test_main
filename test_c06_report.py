import copy
import hashlib
import json
from pathlib import Path
import unittest

from c06_report import AXES, TITLES, band
from engine import person
from matcher import DB
from narrative import describe
from relationship_v08 import relation
from server import compute
from story_report import make_report, role_assignment

ROOT = Path(__file__).parent


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class C06Report(unittest.TestCase):
    def setUp(self):
        self.a, self.b = person(1992, 3, 18, 16), person(1992, 4, 30, 1)
        self.rel = relation(self.a, self.b)
        self.couple = next(c for c in DB if c['id'] == 'c06')

    def report(self, a=None, b=None, rel=None):
        return make_report(a or self.a, b or self.b, rel or self.rel, self.couple, {})

    def test_five_chapters_plot_and_both_profiles(self):
        r = self.report()
        self.assertEqual(r['sections'], ['roles', 'story', 'saju_a', 'crisis', 'tip'])
        self.assertEqual([c['title'] for c in r['chapters']], TITLES)
        for word in ('서호', '우산', '부부', '약방', '웅황주', '법해', '뇌봉탑', '판본'):
            self.assertIn(word, r['story'])
        for p in (self.a, self.b):
            self.assertIn(p['day_pillar'][0], r['roles'])
            self.assertIn(p['month_pillar'][0], r['roles'])
        self.assertEqual(r['roles'].count('을 일간과 비교한 십성은'), 2)
        self.assertEqual(r['roles'].count('목(木)'), 2)

    def test_each_axis_changes_its_chapter_and_advice_independently(self):
        for key in AXES:
            chapter = 'saju_a' if key in ('attraction', 'security', 'growth') else 'crisis'
            reports = []
            for value in (30, 55, 80):
                rel = copy.deepcopy(self.rel)
                rel['vector'][key] = value
                original = copy.deepcopy(rel)
                r = self.report(rel=rel)
                self.assertEqual(rel, original)
                self.assertIn(f'{value}/100', r[chapter])
                reports.append(r)
            self.assertEqual(len({r[chapter] for r in reports}), 3, key)
            self.assertEqual(len({r['tip'] for r in reports}), 3, key)
            for fixed in ('roles', 'story', 'crisis' if chapter == 'saju_a' else 'saju_a'):
                self.assertEqual(len({r[fixed] for r in reports}), 1, fixed)
        self.assertEqual([band(x) for x in (0, 44.99, 45, 64.99, 65, 100)], [0, 0, 1, 1, 2, 2])

    def test_real_personalization_and_missing_time(self):
        base = self.report()
        a, b = person(1988, 6, 12), person(1995, 12, 1)
        r = self.report(a, b, relation(a, b))
        for key in ('roles', 'saju_a', 'crisis', 'tip'):
            self.assertNotEqual(base[key], r[key], key)
        self.assertIn('시주를 빼고', r['roles'])
        self.assertEqual(base['story'], r['story'])

    def test_roles_swap_and_gender_do_not_change_assignment(self):
        # Unequal drive: physical person retains role after swapping inputs.
        a = dict(self.a, day_pillar='丙子', month_pillar='甲子')
        b = dict(self.b, day_pillar='庚子', month_pillar='庚子')
        self.assertIs(role_assignment(a, b)[2], a)
        self.assertIs(role_assignment(b, a)[2], a)
        self.assertIn('당신에게 백소정', self.report(a, b)['roles'])
        self.assertIn('상대방에게 백소정', self.report(b, a)['roles'])
        self.assertEqual(self.report(a, b)['roles'], self.report(dict(a, gender='male'), dict(b, gender='female'))['roles'])
        self.assertIs(role_assignment(a, a.copy())[2], a)
        self.assertIn('입력 순서', self.report(a, a.copy())['roles'])

    def test_preview_exact_historical_hashes_and_unlock(self):
        fixtures = json.loads((ROOT / 'tests/fixtures/baek_heo_responses.json').read_text(encoding='utf8'))
        for fixture in fixtures:
            r = compute(fixture['payload'], unlock=fixture['unlock'])
            if not fixture['unlock']:
                self.assertEqual(digest(r), fixture['sha256'])
            else:
                self.assertEqual(len(r['full_report']['chapters']), 5)
                self.assertTrue(r['test_mode'])
                self.assertTrue(r['has_art'])

    def test_other_eleven_reports_exact_baseline(self):
        expected = json.loads((ROOT / 'tests/fixtures/other_reports.json').read_text(encoding='utf8'))
        for c in DB:
            if c['id'] == 'c06':
                continue
            r = make_report(self.a, self.b, self.rel, c, describe(self.rel['vector'], c['id']))
            self.assertEqual(digest(r), expected[c['id']], c['id'])
            self.assertNotIn('chapters', r)

    def test_assets_preview_markup_and_calculation_files_unchanged(self):
        protected = json.loads((ROOT / 'tests/fixtures/c06_protected.json').read_text(encoding='utf8'))
        html = (ROOT / 'index.html').read_text(encoding='utf8')
        for path, expected in protected.items():
            raw = (html[html.index('<section class="hide" id="result">'):html.index('<div class="hide" id="premiumReport">')].encode()
                   if path == 'preview_html' else (ROOT / path).read_bytes())
            if path == 'server.py':
                # Only the new, allowlisted font-serving branch may differ.
                source = raw.decode('utf8').replace('\r\n', '\n')
                start = source.index('        elif path in (\n')
                end = source.index('        else:self.send_error(404);return', start)
                raw = (source[:start] + source[end:]).replace('\n', '\r\n').encode('utf8')
            self.assertEqual(hashlib.sha256(raw).hexdigest(), expected, path)


if __name__ == '__main__':
    unittest.main()

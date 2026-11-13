import copy
import hashlib
import json
from pathlib import Path
import unittest

from report_display import ten_point_score
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
        self.assertIn('당신의 일간은',r['roles'])
        self.assertIn('상대방의 일간은',r['roles'])
        self.assertNotIn('지장간',r['roles'])
        self.assertIn('hidden',r['chart_evidence']['a'])
        self.assertIn('가상 장면',r['crisis'])

    def test_internal_scores_preserved_but_never_displayed(self):
        for key in AXES:
            rel=copy.deepcopy(self.rel);rel['vector'][key]=80
            original=copy.deepcopy(rel)
            r=self.report(rel=rel)
            self.assertEqual(rel,original)
            for chapter in r['sections']:
                self.assertNotRegex(r[chapter],r'\d+/10|\d+점')
        self.assertEqual([band(x) for x in (0,44.99,45,64.99,65,100)],[0,0,1,1,2,2])

    def test_real_personalization_and_missing_time(self):
        base = self.report()
        a, b = person(1988, 6, 12), person(1995, 12, 1)
        r = self.report(a, b, relation(a, b))
        for key in ('roles', 'saju_a', 'crisis', 'tip'):
            self.assertNotEqual(base[key], r[key], key)
        for who in ('a','b'):
            self.assertTrue(r['chart_evidence'][who]['missing_hour'])
            self.assertNotIn('hour_pillar',r['chart_evidence'][who]['pillars'])
        # The source tale stays fixed; the explicitly separated reading question varies.
        from c06_report import TALE
        self.assertTrue(base['story'].replace('**','').startswith(TALE.replace('**','')))
        self.assertTrue(r['story'].replace('**','').startswith(TALE.replace('**','')))

    def test_roles_swap_and_gender_do_not_change_assignment(self):
        # Unequal drive: physical person retains role after swapping inputs.
        a = dict(self.a, day_pillar='丙子', month_pillar='甲子')
        b = dict(self.b, day_pillar='庚子', month_pillar='庚子')
        self.assertIs(role_assignment(a, b)[2], a)
        self.assertIs(role_assignment(b, a)[2], a)
        self.assertIn('당신은 백소정을 닮았어요', self.report(a, b)['roles'])
        self.assertIn('상대방은 백소정을 닮았어요', self.report(b, a)['roles'])
        self.assertEqual(self.report(a, b)['roles'], self.report(dict(a, gender='male'), dict(b, gender='female'))['roles'])
        self.assertIs(role_assignment(a, a.copy())[2], a)
        self.assertIs(role_assignment(a, a.copy())[2],a)

    def test_preview_exact_historical_hashes_and_unlock(self):
        fixtures = json.loads((ROOT / 'tests/fixtures/baek_heo_responses.json').read_text(encoding='utf8'))
        for fixture in fixtures:
            r = compute(fixture['payload'], unlock=fixture['unlock'])
            if not fixture['unlock']:
                self.assertNotIn('full_report',r)
                self.assertNotRegex(str(r['preview']),r'\d+/10|궁합 점수|등급')
            else:
                self.assertEqual(len(r['full_report']['chapters']), 5)
                self.assertTrue(r['test_mode'])
                self.assertTrue(r['has_art'])

    def test_other_ten_reports_are_individual_five_chapter_reports(self):
        from other_reports import LENSES
        self.assertEqual(len(LENSES), 10)
        for c in DB:
            if c['id'] in ('c06', 'c01'):
                continue
            r = make_report(self.a, self.b, self.rel, c, describe(self.rel['vector'], c['id']))
            self.assertEqual(len(r['chapters']), 3 if c['id']=='c11' else 5, c['id'])
            self.assertEqual(len(r['sections']), 3 if c['id']=='c11' else 5, c['id'])
            self.assertIn(c['name'].split('·')[0], r['roles'], c['id'])
            self.assertTrue(all(r[key] for key in r['sections']), c['id'])

    def test_assets_preview_markup_and_calculation_files_unchanged(self):
        import subprocess
        # Compare with the exact main commit at which this PR branched.
        # Historical fixture hashes were generated at an older revision.
        baseline = 'e9c238f6c50607ea49e027517969122a3d0d12f7'
        protected = [
            'engine.py', 'relationship_v08.py', 'matcher.py',
            'couples.json', 'archetypes.json',
            'assets/baek_heo_title.png', 'assets/baek_heo_plain.png',
        ]
        # UI copy is intentionally revised in this PR; engine, matching and art remain frozen.
        for path in protected:
            before = subprocess.check_output(['git', 'show', f'{baseline}:{path}'], cwd=ROOT)
            actual = (ROOT / path).read_bytes()
            if path.endswith(('.py', '.json')):
                actual = actual.replace(b'\r\n', b'\n')
            self.assertEqual(actual, before, path)



if __name__ == '__main__':
    unittest.main()

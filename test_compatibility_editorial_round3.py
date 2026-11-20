import unittest

from compatibility_editorial_round3 import SCENES, analyze_pair
from compatibility_v12 import analyze_pair as analyze_facts
from evaluate_compatibility_editorial_round3 import holdouts
from evaluate_compatibility_v13 import fixtures


class RoundThreeTests(unittest.TestCase):
    def test_frozen_synthetic_coverage(self):
        matched = list(fixtures())[:20]
        held = list(holdouts())
        self.assertEqual(held, list(holdouts()))
        self.assertEqual(len(held), 24)
        self.assertTrue(all(pair not in matched and pair[::-1] not in matched for pair in held))
        self.assertEqual({sum(x["hour"] is None for x in pair) for pair in held}, {0, 1, 2})

    def test_matched_and_unseen_inputs(self):
        scenes = set()
        for pair in [*list(fixtures())[:20], *holdouts()]:
            with self.subTest(pair=pair):
                expected = analyze_facts(*pair)
                draft = analyze_pair(*pair)
                self.assertEqual(analyze_pair(*pair), draft)
                for key in ("charts", "contexts", "interactions", "evidence"):
                    self.assertEqual(draft[key], expected[key])
                self.assertEqual(len(draft["report"]), 3)
                self.assertEqual(draft["review"]["unresolved_ids"], [])
                self.assertEqual(draft["review"]["unlinked_paragraphs"], 0)
                plan = draft["plan"]
                scene = SCENES[plan["scene"]]
                scenes.add(scene[0])
                self.assertIn(scene[3], draft["report"][1]["paragraphs"][-1]["text"])
                self.assertIn(scene[3], draft["report"][2]["paragraphs"][0]["text"])
                self.assertIn(scene[5], draft["report"][2]["paragraphs"][1]["text"])
                for owner, birth in zip(("a", "b"), pair):
                    if birth["hour"] is None:
                        self.assertIn("hour", draft["contexts"][owner]["unresolved_pillars"])
                relation = plan["relationship"]
                for key in ("support", "tension"):
                    if relation[key]:
                        ref = relation[key]["id"]
                        self.assertTrue(any(ref in p["evidence_ids"]
                                            for p in draft["report"][1]["paragraphs"]))
        self.assertEqual(len(scenes), len(SCENES))

    def test_reverse_order_preserves_role_viewpoint(self):
        pair = next(holdouts())
        for draft in (analyze_pair(*pair), analyze_pair(*pair[::-1])):
            role = draft["plan"]["relationship"]["contrast"]["source"]
            expected = [role["owner_ten_god"], role["other_ten_god"]]
            if role["person"] == "b":
                expected.reverse()
            self.assertEqual(draft["plan"]["reading_roles"], expected)

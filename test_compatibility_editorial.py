import unittest

import compatibility_editorial as editorial
import compatibility_v14 as baseline
from evaluate_compatibility_editorial import PATTERNS, sentences
from evaluate_compatibility_v13 import fixtures
from server import compute_compatibility


class EditorialCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.births = list(fixtures())[:20]
        cls.before = [baseline.analyze_pair(*pair) for pair in cls.births]
        cls.after = [editorial.analyze_pair(*pair) for pair in cls.births]

    def test_determinism_and_unchanged_facts(self):
        for pair, before, after in zip(self.births, self.before, self.after):
            with self.subTest(pair=pair):
                self.assertEqual(after, editorial.analyze_pair(*pair))
                for key in ("charts", "contexts", "interactions", "evidence", "limitation"):
                    self.assertEqual(before[key], after[key], key)
                self.assertEqual(len(after["report"]), 3)
                self.assertEqual(after["review"]["unlinked_paragraphs"], 0)
                self.assertEqual(after["review"]["unresolved_ids"], [])

    def test_letter_roles_follow_viewer_and_appear_with_source(self):
        for result in self.after:
            plan = result["plan"]["relationship"]
            contrast = plan["contrast"]
            with self.subTest(plan=plan):
                source = contrast["source"]
                actual = {source["person"]: source["owner_ten_god"]}
                other = "b" if source["person"] == "a" else "a"
                actual[other] = source["other_ten_god"]
                self.assertEqual(contrast["roles"], [actual["a"], actual["b"]])
                paragraph = result["report"][1]["paragraphs"][1]
                self.assertIn(source["source_id"], paragraph["evidence_ids"])
                self.assertIn(f"첫째에게 {actual['a']}, 둘째에게 {actual['b']}", paragraph["text"])

    def test_reference_cases_cover_five_evidence_arrangements(self):
        self.assertEqual(
            [r["plan"]["relationship"]["scope"] for r in self.after[:5]],
            ["unpaired", "same_sources", "separate", "same_slots", "partial"],
        )
        sample = self.after[2]["plan"]["relationship"]["contrast"]
        self.assertEqual(sample["roles"], ["편관", "정재"])
        self.assertEqual(len(sample["same_letter"]), 2)
        self.assertEqual(self.after[0]["plan"]["natal"][0]["missing"], ["month", "hour"])

    def test_old_editorial_patterns_are_reproducible_and_absent_in_candidate(self):
        import re

        for label, pattern in PATTERNS.items():
            with self.subTest(marker=label):
                def matches(results):
                    return sum(bool(re.search(pattern, sentence))
                               for result in results for c in result["report"]
                               for p in c["paragraphs"] for sentence in sentences(p["text"]))
                self.assertGreater(matches(self.before), 0)
                self.assertEqual(matches(self.after), 0)

    def test_public_preview_and_unlock_still_use_v14(self):
        def api_birth(birth):
            time = "" if birth["hour"] is None else f"{birth['hour']:02}:00"
            return {"date": f"{birth['year']:04}-{birth['month']:02}-{birth['day']:02}",
                    "time": time}

        for births, before in zip(self.births, self.before):
            payload = dict(zip(("a", "b"), map(api_birth, births)))
            full = compute_compatibility(payload, unlock=True)
            preview = compute_compatibility(payload)
            self.assertEqual(full, {"version": "1.4", "chapters": before["report"]})
            self.assertEqual(preview["excerpt"], full["chapters"][1]["paragraphs"][0]["text"])


if __name__ == "__main__":
    unittest.main()

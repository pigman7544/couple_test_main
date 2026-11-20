import json
import unittest

from compatibility_v11 import HIDDEN, analyze_pair as analyze_v11
from compatibility_v12 import (
    BRANCH_ELEMENTS, HIDDEN_ORDER, STEM_ELEMENTS, analyze_pair, report_markdown, review_report,
)
from evaluate_compatibility_v12 import evaluate

A = dict(year=2024, month=2, day=4, hour=18)
B = dict(year=2024, month=2, day=10, hour=12)


class ContextTests(unittest.TestCase):
    def test_hidden_members_and_principal_element(self):
        self.assertEqual(HIDDEN_ORDER, dict(zip("子丑寅卯辰巳午未申酉戌亥",
            "癸 己辛癸 甲丙戊 乙 戊癸乙 丙庚戊 丁己 己乙丁 庚壬戊 辛 戊丁辛 壬甲".split())))
        for branch, hidden in HIDDEN_ORDER.items():
            self.assertCountEqual(hidden, HIDDEN[branch])
            self.assertEqual(STEM_ELEMENTS[hidden[0]], BRANCH_ELEMENTS[branch])

    def test_month_roots_tiers_and_exposure(self):
        result = analyze_pair(A, B)
        context = result["contexts"]["a"]
        self.assertEqual(context["month_command"]["principal_id"], "a.month.hidden.甲")
        self.assertEqual(context["month_command"]["season"], "봄")
        self.assertFalse(context["month_command"]["same_element"])
        self.assertIn("a.day.hidden.戊", context["roots"]["戊"]["exact"])
        self.assertIn("a.month.hidden.戊", context["roots"]["戊"]["exact"])
        day = {p["stem"]: p for p in context["placements"] if p["pillar"] == "day"}
        self.assertEqual((day["戊"]["tier"], day["丁"]["tier"], day["辛"]["tier"]), ("본기", "중기", "여기"))
        principal = next(p for p in context["placements"] if p["id"] == "a.month.hidden.甲")
        self.assertIn("a.year.stem", principal["exposed_at"])

    def test_unknown_time_never_becomes_a_source(self):
        unknown = dict(year=2024, month=2, day=4)
        result = analyze_pair(unknown, unknown)
        for owner, context in result["contexts"].items():
            self.assertIsNone(context["month_command"])
            self.assertEqual(context["unresolved_pillars"], ["year", "month", "hour"])
            self.assertEqual({p["pillar"] for p in context["placements"]}, {"day"})
            self.assertEqual(len(result["evidence"][f"{owner}.coverage"]["year_month_alternatives"]), 2)
        self.assertEqual(result["charts"], analyze_v11(unknown, unknown)["charts"])
        self.assertIn("월주 후보", report_markdown(result))

    def test_lunar_conversion_and_invalid_input(self):
        input_lunar = dict(year=2023, month=2, day=1, calendar="lunar", leap=True)
        self.assertEqual(analyze_pair(input_lunar, B), analyze_pair(dict(year=2023, month=3, day=22), B))
        with self.assertRaises(ValueError):
            analyze_pair(A | {"hour": 24}, B)


class ReportTests(unittest.TestCase):
    def test_cross_directions_and_original_locations(self):
        result = analyze_pair(A, B)
        evidence = result["evidence"]
        self.assertEqual(evidence["pair.a.reads.b"]["ten_god"], "편관")
        self.assertEqual(evidence["pair.b.reads.a"]["ten_god"], "편재")
        swapped = analyze_pair(B, A)
        self.assertEqual(swapped["evidence"]["pair.a.reads.b"]["ten_god"], "편재")
        self.assertEqual(swapped["evidence"]["pair.b.reads.a"]["ten_god"], "편관")
        for ref in result["interactions"]:
            sources = evidence[ref]["sources"]
            self.assertEqual({s["person"] for s in sources}, {"a", "b"})
            for source in sources:
                root = evidence[source["source_id"]]
                self.assertEqual(root["symbol"], source["read_stem"])
                self.assertIn(source["symbol"], result["charts"][source["person"]]["pillars"][source["pillar"]])

    def test_three_chapters_and_editorial_review(self):
        result = analyze_pair(A, B)
        self.assertEqual(result, analyze_pair(A, B))
        self.assertEqual(len(result["report"]), 3)
        self.assertTrue(json.dumps(result, ensure_ascii=False, allow_nan=False))
        lint = review_report([{"paragraphs": [{
            "text": "그것은 의미합니다. 그것은 의미합니다.", "evidence_ids": ["missing"],
        }, {"text": "새 문장입니다.", "evidence_ids": []}]}], {})
        self.assertEqual(lint["unresolved_ids"], ["missing"])
        self.assertEqual(lint["unlinked_paragraphs"], 1)
        self.assertEqual(lint["translation_markers"], ["그것은 의미합니다"])
        self.assertEqual(lint["repeated_sentences"], ["그것은 의미합니다."])

    def test_paired_random_comparison(self):
        summary = evaluate()["summary"]
        self.assertEqual(summary["pair_count"], 20)
        self.assertEqual(summary["same_charts"], 20)
        self.assertGreater(summary["unknown_birth_times"], 0)
        self.assertGreater(summary["v12_reports_with_counterpoint"], 0)
        for metric in ("unlinked_paragraphs", "unresolved_references",
                       "within_report_repeated_sentences", "translation_marker_hits"):
            self.assertEqual(summary[metric], 0, metric)


if __name__ == "__main__":
    unittest.main()

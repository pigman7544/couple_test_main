"""Regression tests for v1.3 reasoning and uncertain chart coverage."""

import unittest

import compatibility_v12 as v12
import compatibility_v13 as v13
from evaluate_compatibility_v13 import fixtures


class CompatibilityV13(unittest.TestCase):
    def test_same_calculation_and_traceable_report(self):
        for births in fixtures():
            with self.subTest(births=births):
                prior = v12.analyze_pair(*births)
                result = v13.analyze_pair(*births)
                self.assertEqual(prior["charts"], result["charts"])
                self.assertEqual(prior["interactions"], result["interactions"])
                self.assertEqual(prior["evidence"], result["evidence"])
                self.assertEqual(3, len(result["report"]))
                self.assertFalse(result["review"]["unlinked_paragraphs"])
                self.assertFalse(result["review"]["unresolved_ids"])

    def test_known_directions_and_source_pillars(self):
        result = v13.analyze_pair(*next(fixtures()))
        evidence = result["evidence"]
        a = result["plan"]["natal"]["a"]
        self.assertIsNone(a["month_id"])
        self.assertEqual(a["lead"]["id"], "a.day.hidden.丙")
        self.assertEqual(a["roots"]["same_element_other_polarity"], ["a.day.hidden.丙"])
        self.assertEqual(evidence["pair.a.reads.b"]["ten_god"], "겁재")
        self.assertEqual(evidence["pair.b.reads.a"]["ten_god"], "겁재")
        self.assertEqual(result["plan"]["relationship"]["lead_id"], "pair.육충.a.day.b.hour")

    def test_counterpoint_prefers_a_shared_pillar(self):
        for births in fixtures():
            result = v13.analyze_pair(*births)
            plan = result["plan"]["relationship"]
            if plan["counter_id"]:
                opposing = [row for row in plan["candidates"] if "shared_slots" in row]
                expected = max(opposing, key=lambda row: (row["shared_slots"], row["weight"]))
                self.assertEqual(expected["id"], plan["counter_id"])

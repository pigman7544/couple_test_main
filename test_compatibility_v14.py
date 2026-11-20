import json
import unittest

import compatibility_v13 as v13
import compatibility_v14 as v14
from compatibility_v12 import report_markdown
from evaluate_compatibility_v13 import fixtures


class CompatibilityV14(unittest.TestCase):
    def test_original_24_pairs_keep_facts_and_evidence_links(self):
        for number, births in enumerate(fixtures(), 1):
            with self.subTest(pair=number):
                prior, result = v13.analyze_pair(*births), v14.analyze_pair(*births)
                for field in ("charts", "contexts", "interactions", "evidence", "assumptions"):
                    self.assertEqual(prior[field], result[field])
                for ref in result["interactions"]:
                    for source in result["evidence"][ref]["sources"]:
                        chart = result["charts"][source["person"]]
                        self.assertIsNotNone(chart["pillars"][source["pillar"]])
                        self.assertIn(source["source_id"], result["evidence"])
                self.assertEqual(3, len(result["report"]))
                self.assertFalse(result["review"]["unresolved_ids"])
                self.assertFalse(result["review"]["unlinked_paragraphs"])
                self.assertNotIn("저녁 약속", report_markdown(result))
                json.dumps(result)

    def test_first_five_report_arcs_reflect_distinct_evidence_patterns(self):
        results = [v14.analyze_pair(*births) for births in list(fixtures())[:5]]
        self.assertEqual(["unpaired", "same_sources", "separate", "same_slots", "partial"],
                         [r["plan"]["relationship"]["scope"] for r in results])
        self.assertIn("월주·시주", report_markdown(results[0]))
        self.assertIn("시주는 확정", report_markdown(results[3]))
        self.assertEqual(5, len({r["report"][2]["paragraphs"][0]["text"] for r in results}))

    def test_no_cross_relation_uses_only_directions_and_coverage(self):
        base = v13.analyze_pair(*next(fixtures()))
        base["interactions"] = []
        plan = v14.infer(base)
        paragraph = v14.render(plan, base["evidence"])[1]["paragraphs"][0]
        self.assertEqual({"pair.a.reads.b", "pair.b.reads.a", "a.coverage", "b.coverage"},
                         set(paragraph["evidence_ids"]))

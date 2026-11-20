import json
import unittest

from compatibility_editorial_round2 import DIRECTORY, generate_packet
from compatibility_v14 import analyze_pair as baseline
from evaluate_compatibility_editorial_round2 import compare, measure


class RoundTwoReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = list(generate_packet())

    def test_fixed_pairs_charts_and_trace(self):
        self.assertEqual([pair["pair"] for pair, _ in self.packet], list(range(1, 21)))
        for pair, result in self.packet:
            with self.subTest(pair=pair["pair"]):
                old = baseline(*pair["births"])
                for key in ("charts", "contexts", "interactions", "evidence"):
                    self.assertEqual(old[key], result[key])
                self.assertEqual(len(result["report"]), 3)
                self.assertEqual(result["review"]["unlinked_paragraphs"], 0)
                self.assertEqual(result["review"]["unresolved_ids"], [])
                for owner, chapter in zip(("a", "b"), result["report"][0]["paragraphs"]):
                    self.assertIn(f"{owner}.day.stem", chapter["evidence_ids"])
                    month = result["contexts"][owner]["month_command"]
                    if month:
                        self.assertIn(month["principal_id"], chapter["evidence_ids"])

    def test_artifacts_cover_every_sentence_and_reduce_exact_reuse(self):
        directory = DIRECTORY / "round2"
        rows = json.loads((directory / "round2-sentences.json").read_text(encoding="utf-8"))
        previous = json.loads((DIRECTORY / "after-sentences.json").read_text(encoding="utf-8"))
        self.assertEqual({int(row["id"][:2]) for row in rows}, set(range(1, 21)))
        self.assertLess(measure(rows)["repeated_occurrences_after_first"],
                        measure(previous)["repeated_occurrences_after_first"])
        self.assertEqual(len(list(compare(rows, previous))), len(rows))
        expected = [p["text"] for _, result in self.packet for c in result["report"]
                    for p in c["paragraphs"]]
        manuscript = (directory / "round2.md").read_text(encoding="utf-8")
        self.assertTrue(all(paragraph in manuscript for paragraph in expected))


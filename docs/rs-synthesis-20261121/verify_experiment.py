"""Recheck the experiment packets, prose references and fixed holdout."""
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / "rs-ab-20261121"
sys.path[:0] = [str(PRIOR), str(HERE.parents[1])]

from reproduce import analyze_pair, fixtures, god, verify


class ExperimentChecks(unittest.TestCase):
    def test_source_values_and_references(self):
        decisions = json.loads((HERE / "decisions.json").read_text(encoding="utf-8"))
        for sample, decision in decisions.items():
            with self.subTest(sample=sample):
                original = json.loads((PRIOR / f"{sample}-evidence.json").read_text(encoding="utf-8"))
                result = analyze_pair(*original["births"])
                verify(result)
                self.assertEqual(original["charts"], result["charts"])
                for key, expected in original["evidence"].items():
                    actual = dict(result["evidence"][key])
                    if "symbol" in actual:
                        day = result["charts"][actual["person"]]["day_master"]
                        actual["ten_god_from_own_day"] = god(day, actual["symbol"])
                    self.assertEqual(expected, actual, key)
                for field in ("core", "support", "counter", "limits", "unused"):
                    self.assertLessEqual(set(decision[field]), original["evidence"].keys())
                for label, field, folder in (
                    ("C", "paragraphs", HERE), ("B", "prior_B_paragraphs", PRIOR)
                ):
                    report = (folder / f"{sample}-{label}.md").read_text(encoding="utf-8")
                    prose = [p for p in report.strip().split("\n\n") if not p.startswith("## ")]
                    self.assertEqual(len(prose) - 1, len(decision[field]))
                    for ids in decision[field]:
                        self.assertTrue(ids)
                        self.assertLessEqual(set(ids), original["evidence"].keys())

    def test_fixed_holdout(self):
        births = list(fixtures())[2]
        self.assertEqual(births, [
            dict(year=1975, month=1, day=16, hour=7),
            dict(year=1979, month=4, day=8, hour=3),
        ])
        result = analyze_pair(*births)
        verify(result)
        evidence = result["evidence"]
        self.assertEqual(
            [list(chart["pillars"].values()) for chart in result["charts"].values()],
            [list("甲寅 丁丑 壬戌 甲辰".split()), list("己未 戊辰 乙巳 戊寅".split())],
        )
        self.assertEqual(evidence["pair.a.reads.b"]["ten_god"], "상관")
        self.assertEqual(evidence["pair.b.reads.a"]["ten_god"], "정인")
        for key in (
            "pair.육충.a.day.b.month", "pair.상형.a.year.b.day",
            "pair.육해.a.year.b.day", "pair.상형.a.day.b.year",
            "pair.삼형.a.month.a.day.b.year", "a.day.hidden.戊",
            "b.day.hidden.丙", "a.month.hidden.己", "b.month.hidden.戊",
            "a.month.stem", "b.month.stem",
        ):
            self.assertIn(key, evidence)
        self.assertFalse(any(k.endswith(".day.b.day") for k in evidence))
        for side in ("a", "b"):
            self.assertEqual(evidence[f"{side}.coverage"]["unresolved_pillars"], [])

    def test_full_comparison_and_repeated_sentences(self):
        from html import escape

        comparison = (HERE / "comparison.md").read_text(encoding="utf-8")
        for version, folder in (("B", PRIOR), ("C", HERE)):
            by_sample = []
            total = 0
            for sample in ("01", "02", "04"):
                article = (folder / f"{sample}-{version}.md").read_text(encoding="utf-8")
                blocks = article.strip().split("\n\n")
                for block in blocks:
                    if block.startswith("## "):
                        self.assertIn(f"<h4>{escape(block[3:], quote=False)}</h4>", comparison)
                    else:
                        self.assertIn(f"<p>{escape(block, quote=False)}</p>", comparison)
                paragraphs = [p for p in blocks[:-1] if not p.startswith("## ")]
                sentences = re.split(r"(?<=[.!?])\s+", " ".join(paragraphs))
                total += len(sentences)
                by_sample.append(set(sentences))
            counts = Counter(sentence for sample in by_sample for sentence in sample)
            repeated = sum(count > 1 for count in counts.values())
            print(f"{version}: {total} body sentences, {repeated} distinct cross-sample repeats")
            self.assertEqual(repeated, 0)


if __name__ == "__main__":
    unittest.main()

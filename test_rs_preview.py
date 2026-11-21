import re
import unittest

from rs_synthesis import analyze_preview
from server import compute_compatibility


CASES = (
    ("shared-time", ("1992-10-08", None), ("1981-03-09", "22:00"),
     ("壬申", None, "丁巳", None), ("辛酉", "辛卯", "丙戌", "己亥")),
    ("ongoing-help", ("1974-06-24", "15:00"), ("1983-06-22", "12:00"),
     ("甲寅", "庚午", "丙申", "丙申"), ("癸亥", "戊午", "辛巳", "甲午")),
    ("terms-of-agreement", ("2007-10-17", "09:00"), ("1973-08-31", None),
     ("丁亥", "庚戌", "甲申", "己巳"), ("癸丑", "庚申", "己亥", None)),
    ("routine-and-exception", ("1975-01-16", "07:00"), ("1979-04-08", "03:00"),
     ("甲寅", "丁丑", "壬戌", "甲辰"), ("己未", "戊辰", "乙巳", "戊寅")),
)


def payload(a, b):
    return {owner: {"date": date, "time": time} for owner, (date, time) in zip(("a", "b"), (a, b))}


class RsPreviewTests(unittest.TestCase):
    def test_reports_and_coverage(self):
        seen = set()
        for focus, a, b, chart_a, chart_b in CASES:
            with self.subTest(focus=focus):
                data = payload(a, b)
                free = compute_compatibility(data)
                self.assertNotIn("full_report", free)
                full = compute_compatibility(data, unlock=True)
                self.assertTrue(full["test_mode"])
                self.assertEqual(free["art"], full["art"])
                report = full["full_report"]["compatibility"]
                self.assertEqual(report["synthesis"]["focus"], focus)
                self.assertEqual(len(report["chapters"]), 3)
                self.assertEqual(free["preview"]["title"], report["chapters"][1]["title"])
                for owner, expected in (("a", chart_a), ("b", chart_b)):
                    pillars = report["charts"][owner]["pillars"]
                    self.assertEqual(tuple(pillars.values()), expected)
                    self.assertEqual(report["coverage"][owner], [pos for pos, val in pillars.items() if val is None])
                for chapter in report["chapters"][1:]:
                    for entry in chapter["paragraphs"]:
                        self.assertTrue(entry["evidence_ids"])
                        self.assertLessEqual(set(entry["evidence_ids"]), report["evidence"].keys())
                        sentences = {s for s in re.split(r"(?<=[.?])\s+", entry["text"]) if s}
                        self.assertFalse(seen & sentences)
                        seen.update(sentences)

    def test_ambiguous_month_is_not_cited(self):
        a, b = CASES[0][1:3]
        report = compute_compatibility(payload(a, b), unlock=True)["full_report"]["compatibility"]
        self.assertEqual(report["coverage"]["a"], ["month", "hour"])
        self.assertEqual([row["month"] for row in report["charts"]["a"]["year_month_alternatives"]],
                         ["己酉", "庚戌"])
        self.assertFalse(any(key.startswith(("a.month.", "a.hour.")) for key in report["evidence"]))

    def test_other_births_and_invalid_input(self):
        report = analyze_preview(dict(year=1992, month=3, day=18, hour=16),
                                 dict(year=1992, month=4, day=30, hour=1))
        self.assertEqual(report["synthesis"]["focus"], "editorial")
        for date, time in (("2024-02-30", None), ("1992-03-18", "24:00"), ("1992-03-18", "08:99")):
            with self.subTest(date=date, time=time):
                with self.assertRaises(ValueError):
                    compute_compatibility(payload((date, time), CASES[0][2]))

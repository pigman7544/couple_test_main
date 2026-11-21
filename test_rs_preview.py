import unittest
from datetime import date, timedelta

from rs_synthesis import analyze_preview
from server import compute_compatibility


def payload(a, b):
    return {owner: {"date": day, "time": time, "gender": gender, "calendar": "solar"}
            for owner, (day, time), gender in zip(("a", "b"), (a, b), ("male", "female"))}


class RsPreviewTests(unittest.TestCase):
    def test_review_couple(self):
        data = payload(("1992-03-18", None), ("1992-04-30", None))
        free = compute_compatibility(data)
        self.assertNotIn("full_report", free)
        full = compute_compatibility(data, unlock=True)
        self.assertTrue(full["test_mode"])
        self.assertEqual(free["art"], full["art"])
        self.assertEqual(full["couple"]["id"], "c06")
        report = full["full_report"]["compatibility"]
        self.assertEqual(report["coverage"], {"a": ["hour"], "b": ["hour"]})
        self.assertEqual(report["charts"]["a"]["pillars"],
                         {"year": "壬申", "month": "癸卯", "day": "癸巳", "hour": None})
        self.assertEqual(report["charts"]["b"]["pillars"],
                         {"year": "壬申", "month": "甲辰", "day": "丙子", "hour": None})
        self.assertEqual(free["preview"]["title"], report["chapters"][1]["title"])
        text = str(report)
        for word in ("정재", "정관", "배우자궁", "월지", "지장간", "육해"):
            self.assertIn(word, text)
        for token in ("evidence_ids", "pair.a.reads.b", "literature", "다아시", "빌린 물건"):
            self.assertNotIn(token, text)

    def test_holdouts_generate_grounded_reports(self):
        signatures = set()
        for i in range(32):
            a = date(1964, 1, 1) + timedelta(days=i * 277)
            b = date(1997, 8, 21) - timedelta(days=i * 311)
            report = analyze_preview(
                dict(year=a.year, month=a.month, day=a.day, hour=None if i % 2 else 5),
                dict(year=b.year, month=b.month, day=b.day, hour=None if i % 3 else 17),
                {"a": "male", "b": "female" if i % 2 else "other"},
            )
            self.assertEqual(len(report["report"]), 3)
            self.assertEqual(len(report["report"][0]["paragraphs"]), 6)
            self.assertGreaterEqual(len(report["report"][1]["paragraphs"]), 4)
            self.assertEqual(len(report["report"][2]["paragraphs"]), 3)
            self.assertEqual(report["review"]["unresolved_ids"], [])
            self.assertEqual(report["review"]["unlinked_paragraphs"], 0)
            signatures.add(tuple(p["text"] for p in report["report"][1]["paragraphs"]))
        self.assertEqual(len(signatures), 32)

    def test_ambiguous_month_is_not_cited(self):
        report = analyze_preview(dict(year=1992, month=10, day=8),
                                 dict(year=1981, month=3, day=9, hour=22))
        self.assertEqual(report["contexts"]["a"]["unresolved_pillars"], ["month", "hour"])
        refs = [ref for chapter in report["report"]
                for entry in chapter["paragraphs"] for ref in entry["evidence_ids"]]
        self.assertFalse(any(ref.startswith(("a.month.", "a.hour.")) for ref in refs))

    def test_invalid_input(self):
        for day, time in (("2024-02-30", None), ("1992-03-18", "24:00"), ("1992-03-18", "08:99")):
            with self.subTest(day=day, time=time), self.assertRaises(ValueError):
                compute_compatibility(payload((day, time), ("1992-04-30", None)))

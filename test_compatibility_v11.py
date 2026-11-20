import json
import random
import unittest
from datetime import date, datetime, timedelta

from compatibility_v11 import analyze_pair, birth_chart, ten_god


class CalendarTests(unittest.TestCase):
    def test_twelve_month_boundaries_from_kasi_2024(self):
        # KASI 2024 calendar data, local rounded times. Bracket each by two minutes.
        terms = (
            (1, 6, 5, 49, "甲子", "乙丑"),
            (2, 4, 17, 27, "乙丑", "丙寅"),
            (3, 5, 11, 23, "丙寅", "丁卯"),
            (4, 4, 16, 2, "丁卯", "戊辰"),
            (5, 5, 9, 10, "戊辰", "己巳"),
            (6, 5, 13, 10, "己巳", "庚午"),
            (7, 6, 23, 20, "庚午", "辛未"),
            (8, 7, 9, 9, "辛未", "壬申"),
            (9, 7, 12, 11, "壬申", "癸酉"),
            (10, 8, 4, 0, "癸酉", "甲戌"),
            (11, 7, 7, 20, "甲戌", "乙亥"),
            (12, 7, 0, 17, "乙亥", "丙子"),
        )
        for month, day, hour, minute, old, new in terms:
            with self.subTest(month=month):
                term = datetime(2024, month, day, hour, minute)
                for delta, expected in ((-2, old), (2, new)):
                    instant = term + timedelta(minutes=delta)
                    chart = birth_chart(2024, month, day, instant.hour, instant.minute)
                    self.assertEqual(chart["pillars"]["month"], expected)
                    previous_year = month == 1 or (month == 2 and delta < 0)
                    self.assertEqual(chart["pillars"]["year"], "癸卯" if previous_year else "甲辰")

    def test_unknown_time_at_ipchun_preserves_joint_alternatives(self):
        chart = birth_chart(2024, 2, 4)
        self.assertEqual(chart["pillars"], {"year": None, "month": None, "day": "戊戌", "hour": None})
        self.assertEqual(chart["year_month_alternatives"], [
            {"year": "癸卯", "month": "乙丑"}, {"year": "甲辰", "month": "丙寅"},
        ])
        self.assertEqual(set(chart["details"]), {"day"})
        self.assertEqual(birth_chart(2024, 3, 5)["pillars"]["year"], "甲辰")
        self.assertEqual(birth_chart(2024, 2, 5)["year_month_alternatives"], [])

    def test_lunar_and_leap_month(self):
        self.assertEqual(birth_chart(2024, 1, 1, 12, calendar="lunar"), birth_chart(2024, 2, 10, 12))
        self.assertEqual(birth_chart(2024, 2, 10)["pillars"]["day"], "甲辰")
        self.assertEqual(
            birth_chart(2023, 2, 1, calendar="lunar", leap=True), birth_chart(2023, 3, 22),
        )
        with self.assertRaises(ValueError):
            birth_chart(2024, 1, 1, calendar="lunar", leap=True)

    def test_civil_midnight_and_hour_boundaries(self):
        for day, hour, minute, expected_day, expected_hour in (
            (4, 22, 59, "戊戌", "癸亥"), (4, 23, 0, "戊戌", "壬子"),
            (5, 0, 0, "己亥", "甲子"), (5, 1, 0, "己亥", "乙丑"),
        ):
            with self.subTest(day=day, hour=hour):
                pillars = birth_chart(2024, 2, day, hour, minute)["pillars"]
                self.assertEqual((pillars["day"], pillars["hour"]), (expected_day, expected_hour))

    def test_invalid_input(self):
        for fields in (
            {"day": 30}, {"year": 2051}, {"hour": 24}, {"hour": True}, {"hour": 12, "minute": 60},
            {"calendar": "other"}, {"leap": True}, {"minute": 1},
        ):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                birth_chart(**({"year": 2024, "month": 2, "day": 1} | fields))


class AnalysisTests(unittest.TestCase):
    def test_ten_gods_and_hidden_stems(self):
        expected = "비견 겁재 식신 상관 편재 정재 편관 정관 편인 정인".split()
        stems = "甲乙丙丁戊己庚辛壬癸"
        self.assertEqual([ten_god("甲", stem) for stem in stems], expected)
        self.assertEqual([ten_god("乙", stem) for stem in stems], [
            "겁재", "비견", "상관", "식신", "정재", "편재", "정관", "편관", "정인", "편인",
        ])
        for day_stem in stems:
            self.assertEqual({ten_god(day_stem, stem) for stem in stems}, set(expected))
        chart = birth_chart(2024, 2, 4, 18)
        self.assertEqual(chart["details"]["day"]["hidden_stems"], [
            {"stem": "戊", "element": "earth", "ten_god": "비견"},
            {"stem": "辛", "element": "metal", "ten_god": "상관"},
            {"stem": "丁", "element": "fire", "ten_god": "정인"},
        ])

    def test_seeded_100_pairs(self):
        rng = random.Random(20261120)
        origin = date(1900, 1, 1)
        span = (date(2050, 1, 1) - origin).days
        anchor = date(2024, 2, 10)  # KASI 甲辰 day.
        stems, branches = "甲乙丙丁戊己庚辛壬癸", "子丑寅卯辰巳午未申酉戌亥"
        kinds = set()
        coexisting = 0
        for index in range(100):
            births = []
            for _ in range(2):
                birthday = origin + timedelta(days=rng.randrange(span))
                hour = None if rng.randrange(4) == 0 else rng.randrange(24)
                births.append(dict(year=birthday.year, month=birthday.month, day=birthday.day,
                                   hour=hour, minute=0 if hour is None else rng.randrange(60)))
            with self.subTest(pair=index):
                result = analyze_pair(*births)
                self.assertEqual(result, analyze_pair(*births))
                self.assertTrue(json.dumps(result, allow_nan=False))
                for owner, birth in zip(("a", "b"), births):
                    chart = result["charts"][owner]
                    birthday = date(birth["year"], birth["month"], birth["day"])
                    offset = (birthday - anchor).days
                    self.assertEqual(chart["pillars"]["day"], stems[offset % 10] + branches[(4 + offset) % 12])
                    self.assertEqual(chart["pillars"]["hour"] is None, birth["hour"] is None)
                    self.assertEqual(sum(chart["known_pillar_element_counts"].values()), 2 * len(chart["details"]))
                cards = result["evidence_cards"]
                self.assertEqual(len(cards), len({card["id"] for card in cards}))
                self.assertEqual(cards, sorted(cards, key=lambda card: (-card["importance"], card["id"])))
                lookup = {card["id"]: card for card in cards}
                plan = result["selection"]
                for owner, limit in (("a", 2), ("b", 2), ("pair", 3)):
                    self.assertLessEqual(len(plan[owner]), limit)
                    self.assertTrue(all(lookup[card]["scope"] == owner for card in plan[owner]))
                for card in cards:
                    self.assertTrue(0 < card["importance"] <= 100)
                    fingerprints = {json.dumps(fact, sort_keys=True) for fact in card["facts"]}
                    self.assertEqual(len(fingerprints), len(card["facts"]))
                for relation in result["relations"]:
                    kinds.add(relation["kind"])
                    for owner, position, symbol in relation["sources"]:
                        self.assertIn(symbol, result["charts"][owner]["pillars"][position])
                swapped = analyze_pair(*reversed(births))
                self.assertEqual(swapped["selection"]["pair"], plan["pair"])
                if {"pair:조율과 협력", "pair:차이와 마찰"} <= lookup.keys():
                    coexisting += 1
                    self.assertEqual(set(plan["coexisting_evidence"]), {
                        "pair:조율과 협력", "pair:차이와 마찰",
                    })
        self.assertEqual(kinds, {"천간합", "육합", "삼합", "육충", "상형", "삼형", "자형", "육해"})
        self.assertGreater(coexisting, 0)


if __name__ == "__main__":
    unittest.main()

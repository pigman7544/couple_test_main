"""Traditional chart evidence for the Yeonyeon v1.1 interpretation engine."""

from collections import Counter, defaultdict
from datetime import date
from itertools import combinations

from korean_lunar_calendar import KoreanLunarCalendar

from engine import BRANCHES, CTRL, ELEMENT, GEN, STEMS, person

PILLARS = ("year", "month", "day", "hour")
HIDDEN = dict(zip(BRANCHES, (
    "癸", "己癸辛", "甲丙戊", "乙", "戊乙癸", "丙戊庚",
    "丁己", "己丁乙", "庚壬戊", "辛", "戊辛丁", "壬甲",
)))
BRANCH_ELEMENTS = dict(zip(BRANCHES, (
    "water", "earth", "wood", "wood", "earth", "fire",
    "fire", "earth", "metal", "metal", "earth", "water",
)))
STEM_ELEMENTS = dict(zip(STEMS, ELEMENT))

# Exact groups. Three-member rules require all members and retain their positions.
RULES = {
    "천간합": ("stem", "甲己 乙庚 丙辛 丁壬 戊癸"),
    "육합": ("branch", "子丑 寅亥 卯戌 辰酉 巳申 午未"),
    "삼합": ("branch", "申子辰 亥卯未 寅午戌 巳酉丑"),
    "육충": ("branch", "子午 丑未 寅申 卯酉 辰戌 巳亥"),
    "상형": ("branch", "子卯 寅巳 巳申 申寅 丑戌 戌未 未丑"),
    "삼형": ("branch", "寅巳申 丑戌未"),
    "자형": ("branch", "辰辰 午午 酉酉 亥亥"),
    "육해": ("branch", "子未 丑午 寅巳 卯辰 申亥 酉戌"),
}
SUPPORT = {"천간합", "육합", "삼합"}
POSITION_WEIGHT = {"day": 30, "month": 18, "hour": 10, "year": 8}
LIMITATION = "전통 명리의 상징적 해석이며 실제 성격이나 관계를 예측할 수 없습니다."
GOD_THEMES = {
    "비견": "자율성", "겁재": "자율성", "식신": "표현", "상관": "표현",
    "편재": "자원과 선택", "정재": "자원과 선택",
    "편관": "기대와 책임", "정관": "기대와 책임",
    "편인": "돌봄과 배움", "정인": "돌봄과 배움",
}
INTERPRETATIONS = {
    "조율과 협력": ("결속과 협력", "협력 방식을 함께 찾을 수 있음",
                "합의 과정에서 개인의 선호가 묻힐 수 있음", "공동 일정과 역할을 나눠 정하기"),
    "차이와 마찰": ("차이와 긴장", "서로 다른 방식이 필요한 상황을 알아차릴 수 있음",
                "기대와 반응의 속도가 다를 수 있음", "의견이 엇갈릴 때 각자의 기대를 먼저 확인하기"),
    "자율성": ("동료성과 독립성", "서로의 판단을 존중할 수 있음",
             "주도권을 두고 의견이 엇갈릴 수 있음", "혼자 정할 일과 함께 정할 일을 구분하기"),
    "표현": ("표현과 산출", "생각을 구체적인 말이나 행동으로 나눌 수 있음",
           "직접적인 표현이 부담스러울 수 있음", "말과 행동 중 어떤 표현이 편한지 묻기"),
    "자원과 선택": ("자원의 활용과 관리", "생활 자원을 의논하는 데 관심을 둘 수 있음",
               "지출이나 시간의 우선순위가 다를 수 있음", "시간과 지출의 우선순위를 함께 정하기"),
    "기대와 책임": ("규범과 책임", "서로 기대하는 역할을 분명히 할 수 있음",
               "역할 기대가 어긋나면 부담이 될 수 있음", "각자 맡을 수 있는 일을 확인하기"),
    "돌봄과 배움": ("수용과 지원", "필요한 도움을 나눌 수 있음",
               "원하는 지원 방식이 다를 수 있음", "도움이 필요한 때와 방식을 묻기"),
}


def ten_god(day_stem, target_stem):
    """Return the target stem's 십성 from the given day master's perspective."""
    source, target = STEM_ELEMENTS[day_stem], STEM_ELEMENTS[target_stem]
    opposite = (STEMS.index(day_stem) - STEMS.index(target_stem)) % 2
    if source == target:
        return ("비견", "겁재")[opposite]
    if GEN[source] == target:
        return ("식신", "상관")[opposite]
    if CTRL[source] == target:
        return ("편재", "정재")[opposite]
    if CTRL[target] == source:
        return ("편관", "정관")[opposite]
    return ("편인", "정인")[opposite]


def birth_chart(year, month, day, hour=None, minute=0, calendar="solar", leap=False):
    """Calculate stable pillars and retain joint year/month alternatives when needed."""
    if any(type(value) is not int for value in (year, month, day, minute)):
        raise ValueError("Date and minute must be integers")
    if not 0 <= minute <= 59 or (hour is None and minute):
        raise ValueError("Invalid birth minute")
    if hour is not None and (type(hour) is not int or not 0 <= hour <= 23):
        raise ValueError("Invalid birth hour")
    if type(leap) is not bool or calendar not in ("solar", "lunar"):
        raise ValueError("Invalid calendar or leap-month flag")
    if calendar == "solar":
        date(year, month, day)
        if leap:
            raise ValueError("Leap month requires a lunar date")
    else:
        lunar = KoreanLunarCalendar()
        if not lunar.setLunarDate(year, month, day, leap) or lunar.isIntercalation != leap:
            raise ValueError("Invalid or unsupported lunar date")

    first = person(year, month, day, hour if hour is not None else 0, minute, calendar, leap)
    last = first if hour is not None else person(year, month, day, 23, 59, calendar, leap)
    pillars = {
        name: first[name + "_pillar"] if first[name + "_pillar"] == last[name + "_pillar"] else None
        for name in PILLARS
    }
    alternatives = []
    if pillars["year"] is None or pillars["month"] is None:
        alternatives = [
            {"year": result["year_pillar"], "month": result["month_pillar"]}
            for result in (first, last)
        ]
    if hour is None:
        pillars["hour"] = None
    day_master = pillars["day"][0]
    details = {}
    elements = Counter(dict.fromkeys(GEN, 0))
    for position, pillar in pillars.items():
        if pillar is None:
            continue
        stem, branch = pillar
        elements.update((STEM_ELEMENTS[stem], BRANCH_ELEMENTS[branch]))
        details[position] = {
            "stem": stem, "branch": branch,
            "stem_ten_god": None if position == "day" else ten_god(day_master, stem),
            "hidden_stems": [
                {"stem": hidden, "element": STEM_ELEMENTS[hidden], "ten_god": ten_god(day_master, hidden)}
                for hidden in HIDDEN[branch]
            ],
        }
    return {
        "solar_date": first["solar_date"], "pillars": pillars, "day_master": day_master,
        "birth_time_known": hour is not None, "year_month_alternatives": alternatives,
        "details": details, "known_pillar_element_counts": dict(elements),
    }


def _relations(charts):
    relations = []
    for kind, (field, groups) in RULES.items():
        positions = [
            (owner, position, detail[field])
            for owner, chart in charts.items()
            for position, detail in chart["details"].items()
        ]
        for group in groups.split():
            for sources in combinations(positions, len(group)):
                if sorted(source[2] for source in sources) == sorted(group):
                    owners = {source[0] for source in sources}
                    scope = sources[0][0] if len(owners) == 1 else "pair"
                    relations.append({"kind": kind, "scope": scope, "sources": sources})
    return relations


def _fact(kind, sources, base):
    return {
        "kind": kind,
        "sources": [
            {"person": owner, "pillar": position, "symbol": symbol}
            for owner, position, symbol in sources
        ],
        "weight": min(100, base + sum(POSITION_WEIGHT[position] for _, position, _ in sources)),
    }


def _evidence(charts, relations):
    grouped = defaultdict(list)
    for owner, chart in charts.items():
        for position, detail in chart["details"].items():
            god = detail["stem_ten_god"]
            if god:
                grouped[owner, GOD_THEMES[god]].append(_fact(
                    god, [(owner, position, detail["stem"])], 25,
                ))
            for hidden in detail["hidden_stems"]:
                god = hidden["ten_god"]
                grouped[owner, GOD_THEMES[god]].append(_fact(
                    god, [(owner, position, hidden["stem"])], 15,
                ) | {"layer": "hidden_stem", "branch": detail["branch"]})

    day_a, day_b = (chart["day_master"] for chart in charts.values())
    if day_a == day_b:
        grouped["pair", "자율성"].append(_fact(
            "동일 일간", [("a", "day", day_a), ("b", "day", day_b)], 25,
        ))
    else:
        for source, target, stem, other in (("a", "b", day_a, day_b), ("b", "a", day_b, day_a)):
            god = ten_god(stem, other)
            grouped["pair", GOD_THEMES[god]].append(_fact(
                god, [(source, "day", stem), (target, "day", other)], 16,
            ) | {"perspective": source})

    for relation in relations:
        kind = relation["kind"]
        theme = "조율과 협력" if kind in SUPPORT else "차이와 마찰"
        grouped[relation["scope"], theme].append(_fact(
            kind, relation["sources"], 20 if relation["scope"] == "pair" else 10,
        ))

    cards = []
    for (scope, theme), facts in grouped.items():
        facts.sort(key=lambda fact: (-fact["weight"], fact["kind"]))
        # Repeated positional evidence can raise emphasis by at most eight points.
        importance = min(100, facts[0]["weight"] + 2 * min(len(facts) - 1, 4))
        meaning, strength, tension, application = INTERPRETATIONS[theme]
        cards.append({
            "id": f"{scope}:{theme}", "scope": scope, "theme": theme, "facts": facts,
            "traditional_meaning": meaning, "possible_strength": strength,
            "possible_tension": tension, "daily_application": application,
            "limitation": LIMITATION, "importance": importance,
        })
    return sorted(cards, key=lambda card: (-card["importance"], card["id"]))


def analyze_pair(a, b):
    """Accept two birth_chart keyword dictionaries and return JSON-ready evidence."""
    charts = {"a": birth_chart(**a), "b": birth_chart(**b)}
    relations = _relations(charts)
    cards = _evidence(charts, relations)
    interaction_ids = {"pair:조율과 협력", "pair:차이와 마찰"}
    pair_cards = [card for card in cards if card["scope"] == "pair"]
    # Keep both types of interaction when present, even if another theme ranks higher.
    selected_pair = [card for card in pair_cards if card["id"] in interaction_ids]
    selected_pair += [card for card in pair_cards if card["id"] not in interaction_ids][
        :3 - len(selected_pair)
    ]
    selected_ids = {card["id"] for card in selected_pair}
    plan = {
        owner: [card["id"] for card in cards if card["scope"] == owner][:2]
        for owner in charts
    }
    plan["pair"] = [card["id"] for card in pair_cards if card["id"] in selected_ids]
    plan["primary_theme"] = pair_cards[0]["theme"]
    plan["coexisting_evidence"] = [
        card["id"] for card in pair_cards if card["id"] in interaction_ids
    ] if interaction_ids <= selected_ids else []
    return {
        "version": "1.1", "charts": charts, "relations": relations,
        "evidence_cards": cards, "selection": plan,
    }

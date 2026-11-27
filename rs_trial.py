"""Presentation of the three-chapter, provider-free RS reader."""

from rs_gpt import CHART_SYMBOLS
from rs_local_report import ROLE_ACTIONS, STORY_PASSAGES


ELEMENT_ITEMS = {
    "wood": ("목", "초록", "작은 화분"),
    "fire": ("화", "빨강", "따뜻한 조명의 스탠드"),
    "earth": ("토", "황토색", "도자기 받침"),
    "metal": ("금", "흰색", "금속 트레이"),
    "water": ("수", "남색", "유리잔"),
}


def format_trial(report):
    first, second, third = report["chapters"]
    a, b = (report["names"][key] for key in ("a", "b"))
    charts = report["charts"]
    facts = report["facts"]
    role_a = facts["pair.a.reads.b"]["ten_god"]
    role_b = facts["pair.b.reads.a"]["ten_god"]
    couple = report["couple"]
    story, = (
        p for p in third["paragraphs"]
        if all(couple[key] in p["text"] for key in ("work", "name"))
    )
    story_text = story["text"]
    if report["mode"] == "local":
        event, advice = STORY_PASSAGES[couple["id"]]
        story_text = (
            f"『{couple['work']}』의 {couple['name']} 이야기에는 이런 대목이 있어요. {event}. "
            f"2장의 교차 십성에서 {a}님은 {ROLE_ACTIONS[role_a]}에, {b}님은 {ROLE_ACTIONS[role_b]}에 "
            f"주목할 수 있으니, {advice}."
        )
    example = {**story, "heading": "작품 속 닮은 커플", "text": story_text,
               "emphasize_lead": False, "couple": True}

    # Count the confirmed chart symbols only. This is a reading aid, not a
    # determination of favorable elements or a change to the matching logic.
    visible = [
        CHART_SYMBOLS[symbol]["element"]
        for chart in charts.values()
        for pillar in chart["pillars"].values() if pillar
        for symbol in pillar
    ]
    element = min(ELEMENT_ITEMS, key=visible.count)
    element_name, color, item = ELEMENT_ITEMS[element]
    seasons = [
        command["season"] if (command := charts[key]["month_command"]) else "미확정"
        for key in ("a", "b")
    ]
    advice_paragraphs = [p for p in third["paragraphs"] if p is not story]
    sections = [
        {"title": "두 개의 열쇠", "paragraphs": advice_paragraphs[:2]},
        {"title": "조화 오행", "paragraphs": [{"text": (
            f"두 명식의 확정된 천간과 지지에서 {element_name}에 해당하는 글자는 {visible.count(element)}개예요. "
            f"확정 글자 수가 가장 적은 오행 중 하나를 골라, 함께 바꾸고 싶은 일상 습관을 이야기해 보세요."
        )}]},
        {"title": "색과 물건", "paragraphs": [{"text": (
            f"{element_name}에 연결한 색은 {color}이에요. 이 색이나 {item}을 두 사람이 함께 정한 습관을 기억하는 표식으로 써 보세요."
        )}]},
        {"title": "우리의 계절", "paragraphs": [
            {"text": f"월지가 가리키는 계절은 {a}님 {seasons[0]}, {b}님 {seasons[1]}이에요."},
            *advice_paragraphs[2:],
        ]},
    ]
    return {"chapters": [
        first,
        {**second, "paragraphs": [*second["paragraphs"], example]},
        {"title": "두 사람을 위한 조언", "sections": sections},
    ]}

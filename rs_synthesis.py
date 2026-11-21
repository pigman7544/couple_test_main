"""Evidence-led preview writing. The editorial scenes are authored offline."""

from compatibility_editorial_round3 import analyze_pair as analyze_baseline
from compatibility_editorial_round3 import READINGS
from compatibility_v12 import review_report


DIRECTIONS = ("pair.a.reads.b", "pair.b.reads.a")

# Match the calculated structure, including direction and layer, never a demo date.
# Each entry contains the central interaction, a qualifying fact, and an edited scene.
READINGS_BY_STRUCTURE = (
    {
        "key": "shared-time",
        "days": ("丁巳", "丙戌"),
        "lead": "pair.육충.a.day.b.hour",
        "counter": ("a.day.hidden.庚", "b.day.hidden.辛"),
        "title": "비워 둔 시간이 약속이 되는 순간",
        "thesis": "각자 계획을 정할 자유가 있어도, 둘이 쓰기로 한 시간의 경계는 따로 생겨요.",
        "scene": "일요일 아침, 한 사람이 수영장을 예약해요. 다른 사람은 토요일 밤에 같이 아침을 먹자고 한 말을 떠올려요. 수영을 다녀와도 늦은 아침은 가능하지만, 기다리던 사람에게는 나란히 집을 나서는 아침 자체가 약속이었을 수 있어요.",
        "limit": "두 사람의 명식에서는 각자의 선택권과 맡은 약속을 지키려는 마음을 함께 읽을 수 있어요. 시각이 확인된 쪽의 시지와 상대의 일지가 만나는 자리에서 살핀 장면이에요.",
        "next": "일요일 오전을 누구의 시간으로 둘까?",
        "trial": "주말 일정을 얘기할 때 아직 정하지 않은 칸 하나만 골라 보세요. ‘아침은 같이 먹고 열 시부터는 각자 어때?’처럼 함께 쓰는 시간의 끝을 먼저 잡아 보면, 빈칸에 서로 다른 약속을 적어 뒀는지 알아차리기 쉬워요.",
    },
    {
        "key": "ongoing-help",
        "days": ("丙申", "辛巳"),
        "lead": "pair.상형.a.day.b.day",
        "counter": ("pair.육합.a.day.b.day",),
        "title": "한 번 손을 보탠 뒤에 생기는 일",
        "thesis": "손발을 잘 맞춘 일이 반복될 때, 도와준 사람과 그 일을 맡은 사람의 경계가 달라질 수 있어요.",
        "scene": "공동으로 쓰는 가계부가 밀린 날, 한 사람은 영수증을 모으고 다른 사람은 내역을 정리해요. 그날은 금방 끝나요. 다음 달에도 영수증이 한쪽 책상에 쌓이면, 건넨 사람은 지난번처럼 나눠 하자는 뜻일 수 있고 받은 사람은 정산이 자기 일이 된 듯 느낄 수 있어요.",
        "limit": "같은 두 일지에서 손발이 맞는 단서와 반복할 때 기준이 걸리는 단서를 함께 읽었어요. 그날의 협력이 좋았다는 사실은 다음 달 몫을 정할 때도 남아요.",
        "next": "다음 달 몫까지 정해 볼까요?",
        "trial": "정산을 마친 날 ‘오늘은 네가 입력했는데, 다음 달에는 내가 할까?’라고 물어보세요. 번갈아 맡기로 했다면 자료를 건네는 날짜도 같이 정해 보세요. 둘 다 다음 차례를 같은 사람으로 떠올리는지 확인할 수 있어요.",
    },
    {
        "key": "terms-of-agreement",
        "days": ("甲申", "己亥"),
        "lead": "pair.육해.a.day.b.day",
        "counter": ("pair.천간합.a.day.b.day",),
        "title": "같은 곳에 가기로 하고 다른 주말을 그릴 때",
        "thesis": "함께하고 싶은 일에는 뜻이 모여도, 그 일을 위해 내어 줄 시간까지 같은 크기일 필요는 없어요.",
        "scene": "둘이 기차로 바다를 보러 가기로 해요. 한 사람은 저녁까지 걷고 마지막 기차로 돌아오는 하루를 떠올려요. 다른 사람은 점심만 먹고 돌아와 다음 날을 준비할 생각이에요. 표를 고르는 순간이 오고서야 둘이 상상한 주말의 길이가 드러나요.",
        "limit": "두 일주의 위쪽에서 뜻이 모이는 단서를, 아래쪽에서 세부가 엇갈릴 여지를 읽었어요. 함께 바다를 보고 싶은 마음은 기차 시간을 다시 고를 때도 유효해요.",
        "next": "표를 고르기 전에 돌아올 시간을 말해요",
        "trial": "예약하기 전에 서로 꼭 하고 싶은 일 하나와 집에 돌아오고 싶은 시각을 말해 보세요. ‘바닷가에서 점심은 먹고 싶어. 저녁 여섯 시에는 집에 있고 싶어.’ 두 답을 나란히 놓으면 어떤 기차가 둘의 주말에 들어갈지 보이기 시작해요.",
    },
    {
        "key": "routine-and-exception",
        "days": ("壬戌", "乙巳"),
        "lead": "pair.육충.a.day.b.month",
        "counter": ("pair.상형.a.year.b.day", "pair.육해.a.year.b.day"),
        "title": "한 번 바뀐 저녁을 다음 주에도 바꿀 수 있을까",
        "thesis": "가까운 사이에서 받아들일 수 있는 예외와 계속 쓰고 싶은 생활 리듬은 따로 정할 수 있어요.",
        "scene": "평소 금요일에 함께 장을 보던 두 사람이 이번 주만 목요일에 가요. 주말이 한결 여유로워서 한 사람은 다음 주에도 목요일이 좋겠다고 생각해요. 다른 사람에게 목요일은 그 주에만 비울 수 있었던 저녁일 수 있어요.",
        "limit": "첫째의 일지와 둘째의 월지를 중심으로 읽었어요. 둘째의 일지에도 다른 교차 작용이 있으므로, 일정을 바꾸거나 지키고 싶어 하는 역할을 한쪽에 붙일 근거는 없어요.",
        "next": "이번 주의 예외에 끝나는 날짜를 붙여요",
        "trial": "장을 본 날 ‘이번 주만 목요일로 한 거였어, 아니면 다음 주도 해볼까?’라고 물어보세요. 새 요일을 시험해 보기로 했다면 두 번만 해본 뒤 무엇이 편해졌는지 이야기할 날을 정해도 좋아요.",
    },
)


def synthesize(result):
    evidence = result["evidence"]
    days = tuple(result["charts"][owner]["pillars"]["day"] for owner in ("a", "b"))
    scope = {owner: context["unresolved_pillars"] for owner, context in result["contexts"].items()}
    natal = {}
    for owner, context in result["contexts"].items():
        palace = next(row for row in context["placements"] if row["pillar"] == "day" and row["tier"] == "본기")
        month = context["month_command"]
        natal[owner] = {
            "palace": palace["id"],
            "month": month["principal_id"] if month else None,
            "direction": f"pair.{owner}.reads.{'b' if owner == 'a' else 'a'}",
        }
    for reading in READINGS_BY_STRUCTURE:
        refs = (reading["lead"], *reading["counter"])
        if days == reading["days"] and all(ref in evidence for ref in refs):
            return reading, {"focus": reading["key"], "core": [reading["lead"]],
                             "counter": list(reading["counter"]), "scope": scope, "natal": natal}
    baseline = result["plan"]["relationship"]
    return None, {"focus": "editorial", "core": [baseline["tension"]["id"]] if baseline["tension"] else [],
                  "counter": [baseline["support"]["id"]] if baseline["support"] else [],
                  "scope": scope, "natal": natal}


def paragraph(text, ids):
    return {"text": text, "evidence_ids": list(dict.fromkeys(ids))}


def write_report(result, reading, synthesis):
    natal = []
    for position, finding in enumerate(result["plan"]["natal"]):
        owner = finding["owner"]
        interest, _, _ = READINGS[finding["role"]]
        name = ("첫째", "둘째")[position]
        lead = result["evidence"][finding["lead"]]
        place = {"year": "연지", "month": "월지", "day": "일지", "hour": "시지"}[lead["pillar"]]
        text = (f"{name}에게서 먼저 살핀 건 {interest}이에요. "
                f"{place}에 든 {lead['symbol']}을 이 명식의 일간에서 읽으면 {finding['role']}에 해당해요.")
        natal.append(paragraph(text, (f"{owner}.day.stem", finding["lead"], f"{owner}.coverage")))
    chapters = [{"title": "각자의 명식, 각자의 관심", "paragraphs": natal}]
    if not reading:
        relationship, practice = result["report"][1:]
        anchor = relationship["paragraphs"][2 if synthesis["core"] else 1]
        return chapters + [
            {**relationship, "paragraphs": [relationship["paragraphs"][-1], anchor]},
            {**practice, "paragraphs": [practice["paragraphs"][1]]},
        ]
    refs = (*synthesis["core"], *synthesis["counter"], *DIRECTIONS)
    chapters.extend([
        {"title": reading["title"], "paragraphs": [
            paragraph(reading["thesis"], refs),
            paragraph(reading["scene"], refs),
            paragraph(reading["limit"], (*refs, "a.coverage", "b.coverage")),
        ]},
        {"title": reading["next"], "paragraphs": [paragraph(reading["trial"], refs)]},
    ])
    return chapters


def analyze_preview(a, b):
    result = analyze_baseline(a, b)
    reading, synthesis = synthesize(result)
    report = write_report(result, reading, synthesis)
    audit = review_report(report, result["evidence"])
    if any(audit[field] for field in ("unlinked_paragraphs", "unresolved_ids", "repeated_sentences")):
        raise RuntimeError("RS preview prose failed evidence review")
    for chapter in report:
        for entry in chapter["paragraphs"]:
            for ref in entry["evidence_ids"]:
                fact = result["evidence"][ref]
                positions = fact.get("sources", [fact])
                if any(source.get("pillar") in synthesis["scope"].get(source.get("person"), ())
                       for source in positions):
                    raise RuntimeError(f"Unresolved RS preview evidence: {ref}")
    result.update(version="RS-preview-1", report=report, review=audit, synthesis=synthesis,
                  preview_text=reading["thesis"] if reading else report[1]["paragraphs"][-1]["text"].split(". ", 1)[0] + ".")
    return result

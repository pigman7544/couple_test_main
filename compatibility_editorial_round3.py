"""Offline, birth-driven compatibility report candidate for editorial review."""

from compatibility_editorial import build_brief
from compatibility_editorial_prose import NAMES, POSITIONS, references
from compatibility_v11 import ten_god
from compatibility_v12 import _paragraph, _read, analyze_pair as analyze_facts, review_report


# One need, its useful contribution, and the condition it might overlook.
READINGS = {
    "비견": ("각자 맡은 몫의 방법을 스스로 고르는 것", "일을 나눠도 서로를 계속 기다릴 필요가 줄어듭니다", "한쪽의 선택이 다른 쪽 일정까지 바꾸는지"),
    "겁재": ("내 몫이 걸린 결정에 의견을 보태는 것", "한 사람의 제안에 다른 경험이 들어갈 수 있습니다", "물어보는 시점에 실제로 바꿀 여지가 남았는지"),
    "식신": ("눈앞의 수고를 조금 덜어 주는 것", "설명이 길어지기 전에 함께 움직일 수 있습니다", "상대가 정말 덜고 싶었던 수고가 무엇인지"),
    "상관": ("진행을 막을 조건을 미리 손보는 것", "일을 시작하기 전에 막힐 곳을 발견할 수 있습니다", "수정 제안이 처음 계획을 접자는 말처럼 들렸는지"),
    "편재": ("조건이 바뀔 때 쓸 대안을 열어 두는 것", "첫 계획이 틀어져도 함께할 길이 남습니다", "후보를 늘린 만큼 상대가 비교할 일도 늘었는지"),
    "정재": ("다음에도 지킬 수 있는 만큼만 맡는 것", "한 번으로 끝나지 않을 약속을 만들 수 있습니다", "지금 가능한 작은 시도까지 보류하게 되는지"),
    "편관": ("일이 틀어졌을 때의 부담을 먼저 따져 보는 것", "나중에 급히 수습할 일을 줄일 수 있습니다", "실제보다 이른 시점부터 둘 다 경계하고 있지는 않은지"),
    "정관": ("서로 같은 조건을 약속했는지 확인하는 것", "상대가 어디까지 맡아 줄지 짐작할 필요가 줄어듭니다", "기준을 바꿀 필요가 생겼을 때도 말할 수 있는지"),
    "편인": ("제안을 자기 속도로 생각해 본 뒤 답하는 것", "당장 맞장구치는 대신 숙고한 답을 낼 수 있습니다", "답을 기다리는 쪽에게 언제 다시 이야기할지 알려졌는지"),
    "정인": ("상대가 제안한 이유부터 듣는 것", "표현이 조금 서툴러도 부탁의 뜻을 알아들을 수 있습니다", "이유를 이해했다는 말이 동의로 받아들여지지는 않았는지"),
}

# Domains are examples, selected by the needs they make observable.
# Each domain supplies a single turning point and a detail that can be changed.
SCENES = (
    ("일정을 옮기기로 한 날", {"편인", "정인", "정관", "상관"},
     "둘이 저녁에 만나기로 했는데 한쪽의 일이 늦게 끝나는 날",
     "만남을 한 시간 미루자", "한 사람이 식당에 변경 연락을 하려 할 때",
     "연락 전에 각자 가능한 마지막 시각을 말해 보기", "원래 약속을 지키는 데 드는 이동 부담"),
    ("장바구니를 함께 채울 때", {"편재", "정재", "비견", "겁재"},
     "둘이 주말 식사 재료를 고르다가 사려던 물건이 품절된 날",
     "다른 걸로 바꾸자", "한 사람이 대체품을 장바구니에 담고 결제하려 할 때",
     "담기 전에 바꿔도 되는 품목과 한도를 한 번 확인하기", "대체품의 가격과 손질 시간"),
    ("손을 보탤 곳을 고를 때", {"식신", "정인", "비견", "편관"},
     "둘이 손님을 맞기 전에 거실을 정리하는 날",
     "정리를 나눠 하자", "한 사람이 상대가 꺼내 둔 물건까지 수납하려 할 때",
     "물건을 옮기기 전에 어디까지 손대도 되는지 묻기", "남은 일의 양과 실제로 쓸 수 있는 시간"),
    ("둘의 이름으로 답할 때", {"정관", "겁재", "편인", "정인"},
     "지인이 두 사람을 주말 모임에 초대한 날",
     "가능하다고 알려 주자", "한 사람이 도착 시각까지 적어 전송하려 할 때",
     "보내기 전에 각자 그대로 두고 싶은 표현을 한 줄씩 말하기", "참석 자체에 대한 두 사람의 의사"),
    ("한 번 해 본 일을 이어갈 때", {"식신", "상관", "정재", "편재"},
     "둘이 주말에 한 번 자전거를 타 보고 다음 코스를 고르는 날",
     "다음 주에도 같이 타자", "한 사람이 모임 신청 화면을 열고 정기 일정을 고르려 할 때",
     "다음 한 번만 정하고 정기 신청에는 둘이 따로 답하기", "이동 경로와 매주 비워야 하는 시간"),
    ("예약을 마치기 직전", {"편관", "정관", "편재", "정재"},
     "둘이 나들이를 앞두고 취소 가능한 숙소 두 곳을 비교하는 날",
     "오늘 중에 예약하자", "한 사람이 더 싼 객실의 결제 화면을 열었을 때",
     "결제 전에 각자 받아들일 수 있는 취소 조건을 말하기", "두 객실의 실제 비용 차이"),
    ("글을 함께 다듬는 저녁", {"상관", "편인", "비견", "겁재"},
     "둘이 함께 쓴 소개글의 초안을 다시 펼쳐 본 저녁",
     "한 번 더 읽고 올리자", "한 사람이 제목까지 고친 파일을 게시 화면에 붙여 넣을 때",
     "손봐도 되는 문장에 각자 표시한 뒤 겹치는 곳부터 고치기", "글을 올리기로 한 시각까지 남은 시간"),
    ("빌린 물건을 돌려줄 때", {"식신", "편관", "정관", "비견"},
     "둘이 빌려 온 공구로 수리를 끝낸 날",
     "사용한 공구를 돌려주자", "한 사람이 아직 필요한 부품까지 상자에 넣어 현관에 둘 때",
     "상자를 닫기 전에 남겨 둘 물건과 반납할 사람을 함께 확인하기", "빌린 곳의 반납 가능 시각"),
)

# The detail is the choice at the turning point, shared across both voices.
DETAILS = ("예약 시각", "대체품", "물건을 둘 자리", "도착 시각", "다음 일정",
           "예약할 객실", "제목", "상자에 넣을 물건")
QUESTIONS = {
    "비견": "내가 맡은 쪽은 내가 골라도 될까?",
    "겁재": "{detail}도 같이 정하는 줄 알았어. 지금 내 의견을 말해도 돼?",
    "식신": "내가 여기까지 해 두면 좀 편해질까?",
    "상관": "{detail}부터 다시 보자. 이대로 정하면 나중에 다시 손봐야 할 것 같아.",
    "편재": "{detail}에 다른 선택지도 남겨 두면 어때?",
    "정재": "이번에 정한 대로 다음에도 할 수 있을까?",
    "편관": "{detail}에 문제가 생기면 누가 다시 챙기게 돼?",
    "정관": "우리 둘 다 {detail}까지 정한 걸로 이해했어?",
    "편인": "{detail}까지 지금 답해야 해? 조금 생각하고 싶어.",
    "정인": "{detail}에 대해 이렇게 생각한 이유부터 듣고 싶어.",
}

SUPPORT = {
    "천간합": "한 사람이 꺼낸 제안을 상대가 이어받는 데서 접점을 찾아볼 수 있습니다",
    "육합": "둘 다 받아들이기 쉬운 부분에서 함께 시작할 여지가 있는지 살펴봅니다",
    "삼합": "각자가 가진 조건이 맞물릴 때 혼자서는 어려웠을 일을 시작할 수 있다는 해석입니다",
}

TENSION = {
    "육충": ("둘이 이미 정해졌다고 여긴 조건이 서로 충돌하는지", "이미 정했다고 여긴 조건이 그때도 달랐는지"),
    "상형": ("처음 동의한 범위를 한쪽이 더 넓게 받아들였는지", "두 사람이 동의한 범위를 같은 말로 설명할 수 있었는지"),
    "삼형": ("한 가지를 조정한 뒤 다른 부담이 연달아 생기는지", "첫 조건을 바꾼 뒤 새로 걸리는 조건이 있었는지"),
    "자형": ("새 정보 없이도 같은 확인으로 돌아오는지", "앞서 들은 답을 다시 묻고 싶었던 순간이 줄었는지"),
    "육해": ("수고를 덜어 주려던 일이 상대의 선택을 좁혔는지", "도움받았다고 느낀 부분과 맡기 싫었던 부분이 각각 무엇이었는지"),
    "none": ("함께하자는 말에 각자 어떤 조건을 붙였는지", "처음 제안을 들었을 때보다 합의할 범위가 또렷해졌는지"),
}

SCOPE = {
    "same_sources": "접점과 긴장이 같은 글자에 걸려 있어서, 함께하기 쉬웠던 바로 그 대목에서 다시 물어볼 일이 생기는지 봅니다.",
    "same_slots": "같은 기둥에서 위의 천간은 합을, 아래 지지는 긴장을 이루므로 제안을 받아들이는 때와 실행 조건을 정할 때의 반응을 따로 살펴봅니다.",
    "partial": "두 조합이 일부 자리만 공유합니다. 함께하려는 이유를 유지하면서 걸리는 조건 하나만 조정할 여지가 있는지 살펴봅니다.",
    "separate": "두 조합이 서로 다른 자리에서 성립합니다. 공동의 목적에 공감하는 일과 실행 방법을 합의하는 일을 따로 살펴봅니다.",
}


def form_hypothesis(base):
    brief = build_brief(base)
    relation = brief["relationship"]
    directions = [d["role"] for d in relation["directions"]]
    focus = relation["contrast"]
    roles = focus["roles"] if focus else directions
    natal = [row["role"] for row in brief["natal"]]
    alternative = [row["alternative_role"] for row in brief["natal"]]
    # Ordered ties keep selection reproducible. Dates and sample labels never
    # enter selection. Pillar position is not treated as a real-life domain.
    ranks = [
        4 * sum(role in scene[1] for role in roles)
        + 2 * sum(role in scene[1] for role in directions)
        + sum(role in scene[1] for role in natal)
        + sum(role in scene[1] for role in alternative)
        for scene in SCENES
    ]
    scene = max(range(len(SCENES)), key=ranks.__getitem__)
    return {**brief, "reading_roles": roles, "scene": scene, "scene_scores": ranks,
            "mechanism": relation["tension"]["kind"] if relation["tension"] else "none"}


def natal_paragraph(finding, context, evidence):
    owner = finding["owner"]
    day_id = f"{owner}.day.stem"
    lead_id = finding["lead"]
    lead = evidence[lead_id]
    day = _read(evidence[day_id]["symbol"])
    symbol = _read(lead["symbol"])
    slot = POSITIONS[lead["pillar"]]
    refs = [day_id, lead_id, f"{owner}.coverage"]
    month = context["month_command"]
    month_id = month["principal_id"] if month else None
    location = f"{slot} 지지의 본기" if lead_id == month_id else f"{slot} 지지에 든"
    interest, contribution, _ = READINGS[finding["role"]]
    text = (f"{NAMES[owner]}는 평소 {interest}을 중요하게 여길 수 있습니다. {contribution}. "
            f"명식에서는 {day} 일간과 {location} {symbol} 사이의 {finding['role']} 관계에서 이 성향을 읽습니다.")
    if finding["exposed"]:
        exposed = "·".join(dict.fromkeys(POSITIONS[evidence[ref]["pillar"]] for ref in finding["exposed"]))
        text += f" {symbol} 글자는 {exposed} 천간에도 보여 이 단서를 먼저 살폈습니다."
        refs.extend(finding["exposed"])
    if month_id and month_id != lead_id:
        card = evidence[month_id]
        month_role = ten_god(evidence[day_id]['symbol'], card['symbol'])
        text += (f" 태어난 달을 읽는 기준인 월령의 중심 글자는 {_read(card['symbol'])}입니다. "
                 f"이 글자의 {month_role} 관계에서는 {READINGS[month_role][0]}에도 마음이 쓰일 수 있다고 봅니다.")
        refs.append(month_id)
    if alternative := finding["alternative"]:
        card = evidence[alternative]
        if alternative != month_id:
            text += f" {POSITIONS[card['pillar']]} 지지의 {_read(card['symbol'])} 글자는 {finding['alternative_role']}입니다."
            text += f" 그 단서를 따라가면 {READINGS[finding['alternative_role']][0]}도 중요해질 수 있습니다."
        refs.append(alternative)
    if finding["missing"]:
        missing = "와 ".join(POSITIONS[p] for p in finding["missing"])
        text += f" 확인되지 않은 {missing}는 해석에서 보류했습니다."
    return _paragraph(text, refs)


def interaction_text(card):
    locations = ", ".join(
        f"{NAMES[s['person']]} {POSITIONS[s['pillar']]}의 {_read(s['symbol'])}"
        for s in card["sources"]
    )
    return f"{locations} 사이에 {card['kind']} 관계가 성립합니다."


def render(plan, base):
    relation = plan["relationship"]
    title, _, setting, proposal, turning, change, competing = SCENES[plan["scene"]]
    a, b = (READINGS[role] for role in plan["reading_roles"])
    support, tension = relation["support"], relation["tension"]
    mechanism, measure = TENSION[plan["mechanism"]]
    natal = [natal_paragraph(row, base["contexts"][row["owner"]], base["evidence"])
             for row in plan["natal"]]
    directions = relation["directions"]
    first, second = (READINGS[direction["role"]][0] for direction in directions)
    direction_refs = [direction["id"] for direction in directions]
    agreement = (f"서로의 일간을 읽으면 첫째에게는 {directions[0]['role']}, 둘째에게는 "
                 f"{directions[1]['role']}입니다. 첫째가 {first}에, 둘째가 {second}에 "
                 "마음을 쓴다면, 같은 제안에도 동의하는 이유는 다를 수 있습니다.")
    if first == second:
        agreement = (f"서로의 일간을 읽으면 두 사람 모두 상대에게서 {directions[0]['role']}의 "
                     f"상징을 봅니다. {first}에 서로 마음이 쓰인다면, 그 관심부터 맞닿을 수 있습니다.")
    if support:
        agreement += f" {interaction_text(support)} {SUPPORT[support['kind']]}."
        direction_refs.extend(references(support))
    else:
        agreement += " 여기서 접점을 찾는 단서는 서로의 일간을 읽은 두 관점입니다."

    individual_roles = [finding["role"] for finding in plan["natal"]]
    individual_needs = [READINGS[role][0] for role in individual_roles]
    handoff = (f"1장에서 읽은 첫째의 관심은 {individual_needs[0]}, 둘째의 관심은 {individual_needs[1]}이었습니다. "
               "둘이 함께 정할 때는 그 관심을 어느 단계에서 먼저 드러내는지가 중요해집니다.")
    natal_refs = [finding["lead"] for finding in plan["natal"]]

    focus_refs = []
    turn = ""
    if tension:
        turn += f"{interaction_text(tension)} 이 긴장을 장면에 옮겨 {mechanism} 살펴봅니다. "
        focus_refs.extend(references(tension))
    if support and tension:
        turn += f"{SCOPE[relation['scope']]} "
        focus_refs.extend(references(support))
    if contrast := relation["contrast"]:
        source = contrast["source"]
        layer = "천간" if (tension or support)["layer"] == "stem" else "지지 본기"
        first_role, second_role = plan["reading_roles"]
        turn += (f"{NAMES[source['person']]} {POSITIONS[source['pillar']]}의 {layer}인 "
                 f"{_read(source['read_stem'])} 글자는 첫째에게 {first_role}, 둘째에게 {second_role}입니다.")
        focus_refs.append(source["source_id"])
    else:
        turn = "이 장면에서 어디까지 뜻이 맞는지는 두 사람의 답을 들어 봐야 알 수 있습니다."

    scene = (f"{setting}이라고 해 보죠. “{proposal}”라는 말에 둘 다 고개를 끄덕입니다. "
             f"그런데 {turning}, 어디까지 동의했는지가 달라질 수 있습니다. "
             f"첫째 쪽에서 챙기고 싶은 것은 {a[0]}일 수 있습니다. {a[1]}. "
             f"둘째 쪽에선 {b[0]}에 마음이 쓰일 수 있습니다. {b[1]}.")
    detail = DETAILS[plan["scene"]]
    first_line, second_line = (QUESTIONS[role].format(detail=detail) for role in plan["reading_roles"])
    if a != b:
        scene += (f" 첫째가 “{first_line}”라고 묻고 둘째가 “{second_line}”라고 답한다면, "
                  f"둘 다 처음 제안에는 동의했어도 {detail}에 기대한 답은 달랐던 셈입니다.")
    else:
        scene = (f"{setting}이라고 해 보죠. “{proposal}”라는 말에는 둘 다 고개를 끄덕입니다. "
                 f"두 사람 모두 {a[0]}에 마음이 쓰인다고 해 보죠. {a[1]}. "
                 f"다만 {turning}, 두 사람이 “{first_line}”라는 말에 같은 답을 할지는 따로 물어볼 만합니다.")

    practice = (f"비슷한 일이 있었다면 “{proposal}”라고 했을 때 각자가 어디까지 맡거나 정하기로 "
                f"했다고 생각했는지 먼저 말해 보세요. 첫째는 {a[2]}, 둘째는 {b[2]}도 짚어볼 수 있습니다.")
    trial = (f"다음에 이 장면과 비슷한 일이 있다면 “{change}”부터 시작해 보세요. "
             f"결정이 끝난 뒤에는 {measure} 각자 답해 봅니다. "
             f"둘의 답이 여전히 멀다면 {competing}처럼 대화 방식 외에 실제로 달라져야 할 조건이 있는지 살펴보세요.")
    scene_refs = focus_refs or direction_refs
    return [
        {"title": "두 사람의 사주와 기질", "paragraphs": natal},
        {"title": title, "paragraphs": [
            _paragraph(handoff, natal_refs),
            _paragraph(agreement, direction_refs),
            _paragraph(turn, scene_refs),
            _paragraph(scene, [*direction_refs, *scene_refs]),
        ]},
        {"title": "다음에 같은 대목을 만난다면", "paragraphs": [
            _paragraph(practice, scene_refs), _paragraph(trial, scene_refs),
            _paragraph(f"서로에게 이렇게 물어보세요. “{proposal}”라고 말했을 때 "
                       f"{detail}까지 함께 정한 줄 알았어? 바꿀 수 있는 마지막 순간은 언제였어?", scene_refs),
        ]},
    ]


def literary_comparison(plan):
    # Match a specific misunderstanding and contrasting viewpoints from Chapter 2.
    if plan["mechanism"] not in {"육해", "상형"} or len(set(plan["reading_roles"])) != 2:
        return None
    return {
        "work": "오만과 편견",
        "pair": "엘리자베스와 다아시",
        "text": (
            "다아시는 첫 청혼에서 자신의 마음이 얼마나 강한지 전하려 하지만, 엘리자베스에게는 "
            "그가 자기 가족을 낮춰 보는 말이 먼저 들립니다. 한 사람이 전하려는 뜻과 상대가 실제로 "
            "받아들이는 뜻 사이에 간격이 생긴다는 점이 이 장의 해석과 닮았습니다. 소설에서는 계급에 "
            "대한 판단과 쌓여 온 불신이 그 간격을 키웁니다. 여기서 살핀 두 사람의 장면은 일상적인 "
            "결정에 관한 것이어서, 서로 어떤 범위까지 동의했다고 생각했는지를 그 자리에서 물어볼 수 있습니다."
        ),
    }


def analyze_pair(a, b):
    """Accept the same normalized birth dictionaries as the existing engine."""
    base = analyze_facts(a, b)
    plan = form_hypothesis(base)
    report = render(plan, base)
    audit = review_report(report, base["evidence"])
    if audit["unresolved_ids"] or audit["unlinked_paragraphs"]:
        raise ValueError("Round three draft contains invalid evidence links")
    for owner, context in base["contexts"].items():
        missing = set(context["unresolved_pillars"])
        prefix = f"{owner}."
        for chapter in report:
            for paragraph in chapter["paragraphs"]:
                for ref in paragraph["evidence_ids"]:
                    card = base["evidence"][ref]
                    if ref.startswith(prefix) and card.get("pillar") in missing:
                        raise ValueError(f"Unresolved pillar cited: {ref}")
                    if any(s["person"] == owner and s["pillar"] in missing
                           for s in card.get("sources", [])):
                        raise ValueError(f"Unresolved interaction source: {ref}")
    return {**base, "version": "1.7-editorial-review", "plan": plan,
            "report": report, "review": audit, "literature": literary_comparison(plan)}

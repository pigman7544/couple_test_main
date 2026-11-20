"""Turn the editorial brief into Korean chapters with localized citations."""

from compatibility_v12 import _paragraph, _read

NAMES = {"a": "첫째", "b": "둘째"}
POSITIONS = {"year": "연주", "month": "월주", "day": "일주", "hour": "시주"}

# Each role supplies a relational meaning, a plausible line of speech and a
# checkable detail. These describe possibilities, never inferred past events.
ROLES = {
    "비견": ("각자 판단할 몫을 남겨 두고 싶을 수 있습니다",
           "내가 맡은 부분은 내 방법으로 해 볼게", "각자가 정할 수 있는 범위"),
    "겁재": ("좋은 제안에도 내 의견을 넣을 자리가 있기를 바랄 수 있습니다",
           "내 생각도 듣고 나서 같이 정하면 좋겠어", "아직 같이 정해야 할 부분"),
    "식신": ("말을 더 보태기보다 작은 수고를 덜어 주고 싶을 수 있습니다",
           "지금 내가 할 수 있는 것부터 하나 해 둘게", "지금 당장 덜 수 있는 수고"),
    "상관": ("불편한 조건을 고쳐야 제안도 살릴 수 있다고 느낄 수 있습니다",
           "그대로 하면 여기서 막힐 것 같아", "고치면 계속할 수 있는 조건"),
    "편재": ("처음 제안에 얽매이지 않고 가능한 길을 더 열어 두고 싶을 수 있습니다",
           "이쪽도 가능하니까 일단 두 가지를 놓고 보자", "열어 둘 대안"),
    "정재": ("작더라도 꾸준히 지킬 수 있는 몫을 정할 때 마음이 놓일 수 있습니다",
           "다음번에도 할 수 있는 양만 맡을게", "다음에도 감당할 수 있는 분량"),
    "편관": ("결정이 급해질수록 문제가 생겼을 때의 부담부터 따져 볼 수 있습니다",
           "어긋나면 누가 수습하게 되는지부터 알고 싶어", "부담이 커질 때 멈출 기준"),
    "정관": ("서로 기대하는 바가 분명해야 약속을 믿고 움직일 수 있습니다",
           "둘 다 같은 조건으로 이해했는지 확인하고 싶어", "서로 지키기로 한 기준"),
    "편인": ("답하기에 앞서 들은 말을 자기 속도로 정리하고 싶을 수 있습니다",
           "지금 답하기보다 조금 생각하고 말할게", "생각한 뒤 답을 주고받을 시점"),
    "정인": ("결론을 듣는 것보다 상대가 왜 그런 말을 꺼냈는지 아는 편이 도움이 될 수 있습니다",
           "그 이야기를 왜 지금 꺼냈는지 먼저 듣고 싶어", "결정 전에 들을 사정"),
}

# The action tests the mechanism attributed to the interaction and uses a
# detail selected by the two viewpoints, rather than a fixed event per scope.
TENSIONS = {
    "육충": (
        "두 전제가 동시에 성립하기 어려울 때 엇갈림이 드러날 수 있습니다.",
        "각자 이미 정해졌다고 여긴 부분을 한 줄씩 적어 대조해 보세요.",
        "둘 중 하나를 바로 고르기보다 어느 전제가 바뀌면 두 쪽이 함께 움직일 수 있는지 확인해 봅니다.",
    ),
    "상형": (
        "동의한 뒤에도 해도 되는 범위를 다시 확인하고 싶어질 수 있습니다.",
        "상대가 기억하는 합의를 듣기 전에, 동의했던 범위를 각자 적어 보세요.",
        "다음에는 먼저 해 볼 분량을 정하고, 그다음 단계는 다시 동의를 얻어 시작해 봅니다.",
    ),
    "삼형": (
        "한쪽의 조건을 맞춰도 나머지 조건 때문에 같은 논의가 되돌아올 수 있습니다.",
        "어느 조건을 바꿨을 때 다른 부담이 생겼는지 순서대로 짚어 보세요.",
        "조건을 한꺼번에 바꾸지 말고 가장 먼저 걸린 항목 하나를 잠시 빼 본 뒤 나머지 부담을 확인합니다.",
    ),
    "자형": (
        "이미 확인한 것을 되짚는 동안 결정이 늦어질 수 있습니다.",
        "처음 답을 들었을 때와 다시 묻게 됐을 때 사이에 새로 생긴 정보를 찾아보세요.",
        "새 정보가 없었다면 다음에는 언제 다시 확인할지만 정해 두고 시간을 줘 봅니다.",
    ),
    "육해": (
        "배려로 건넨 말이 상대가 할 수 있는 선택을 줄이는 말처럼 들릴 수 있습니다.",
        "건넨 사람이 덜어 주려던 부담과 들은 사람이 실제로 떠안은 부담을 각각 말해 보세요.",
        "다음에는 한 사람이 대신 결정하기 전에 상대가 고치거나 거절할 수 있는 지점을 남겨 봅니다.",
    ),
}
SCENES = {
    "비견": "둘이 각자 시간을 보내다가 다시 합류할 때",
    "겁재": "한 사람이 정리한 계획을 둘이 검토할 때",
    "식신": "지친 사람의 집안일을 대신하겠다고 할 때",
    "상관": "자주 만나던 요일을 한 사람이 바꾸자고 할 때",
    "편재": "함께할 활동을 골라 이번 주에 시험해 볼 때",
    "정재": "매주 돌아오는 일을 둘이 나눠 맡을 때",
    "편관": "예약을 취소할 경우의 비용을 함께 따질 때",
    "정관": "함께 갈 모임에 둘의 이름으로 답장을 보낼 때",
    "편인": "바로 대답하기 어려운 제안을 두고 이야기를 멈췄을 때",
    "정인": "짧은 답에 담긴 이유를 듣고 원래 하려던 말을 바꿀 때",
}

TITLES = {
    "육충": "같은 말에 서로 다른 전제가 담길 때",
    "상형": "함께하기로 한 뒤 다시 묻게 되는 것",
    "삼형": "하나를 바꾸면 다른 조건도 움직일 때",
    "자형": "이미 들은 답을 다시 확인하는 순간",
    "육해": "도움이 상대의 선택을 줄일 때",
}
SUPPORTS = {
    "천간합": "한 사람이 꺼낸 말을 다른 사람이 자기 말로 이어받을 여지가 보입니다.",
    "육합": "서로에게 가장 쉽게 맞출 수 있는 부분부터 시작할 여지가 보입니다.",
    "삼합": "두 사람의 여러 조건이 맞물릴 때 한 방향으로 나아갈 여지가 보입니다.",
}
SCOPE = {
    "same_sources": "합이 성립한 바로 그 글자에 긴장도 함께 있습니다. 시작할 때 서로 좋았던 점이 진행 중에는 어디까지 동의했는지 확인할 이유가 될 수 있습니다.",
    "same_slots": "같은 기둥이라도 겉의 천간에서 합이, 아래의 지지에서 긴장이 성립합니다. 겉으로 뜻이 맞은 뒤에도 그 합의를 자기 말로 설명할 수 있는지는 따로 볼 만합니다.",
    "partial": "처음 함께하려던 마음은 그대로인데 결정할 항목 하나에서만 대화가 길어질 수 있습니다.",
    "separate": "합과 긴장은 서로 다른 자리에 있습니다. 같은 일을 두고도 목적에 뜻이 맞는지와 계속할 조건이 맞는지를 따로 살펴볼 만합니다.",
}


def individual(finding, evidence):
    owner = finding["owner"]
    ref = finding["lead"]
    card = evidence[ref]
    letter = _read(card["symbol"])
    slot = POSITIONS[card["pillar"]]
    role = finding["role"]
    refs = [ref, f"{owner}.day.stem", *finding["exposed"]]
    if finding["placement"] == "visible":
        visible = "·".join(POSITIONS[evidence[i]["pillar"]] for i in finding["exposed"])
        opening = f"{slot} 지지에 든 {letter} 글자가 {visible} 천간에도 보입니다."
    elif finding["placement"] == "month":
        opening = f"태어난 달의 지지에서 중심이 되는 {letter} 글자부터 읽었습니다."
    else:
        opening = f"{slot} 지지에 든 {letter} 글자에 무게를 두었습니다."
    if finding["repeated"]:
        repeated = "·".join(POSITIONS[evidence[i]["pillar"]] for i in finding["repeated"])
        opening += f" 같은 글자가 {repeated} 지지에도 있습니다."
        refs.extend(finding["repeated"])
    text = (f"{NAMES[owner]} 쪽을 보면, {opening} "
            f"이 글자는 일간을 기준으로 {role}에 해당합니다. {ROLES[role][0]}.")
    if alt := finding["alternative"]:
        refs.append(alt)
        alt_card = evidence[alt]
        alt_role = finding["alternative_role"]
        alt_slot = POSITIONS[alt_card["pillar"]]
        text += (f" {alt_slot} 지지의 {_read(alt_card['symbol'])} 글자는 {alt_role}입니다. "
                 f"이 단서를 함께 보면 {ROLES[alt_role][0]}.")
    if finding["missing"]:
        missing = "·".join(POSITIONS[p] for p in finding["missing"])
        text += f" {missing} 정보가 확정되면 이 해석의 근거도 달라질 수 있습니다."
        refs.append(f"{owner}.coverage")
    return _paragraph(text, refs)


def describe_interaction(card):
    sources = ", ".join(
        f"{NAMES[s['person']]} {POSITIONS[s['pillar']]}의 {_read(s['symbol'])}"
        for s in card["sources"]
    )
    return f"{sources} 사이에는 {card['kind']} 작용이 있습니다."


def references(card):
    return [card["id"], *(s["source_id"] for s in card["sources"])]


def direction_reading(roles):
    first, second = (ROLES[role][2] for role in roles)
    if first == second:
        return f"서로에게서 ‘{first}’에 마음을 쓰는 면을 알아볼 수 있다는 해석입니다."
    return (f"상대를 볼 때 첫째는 ‘{first}’, 둘째는 ‘{second}’에 "
            "먼저 눈이 갈 수 있다는 해석입니다.")


def dialogue(roles, scene_role):
    scene = SCENES[scene_role]
    first, second = (ROLES[role][1] for role in roles)
    if first == second:
        return f"가령 {scene}, 두 사람 모두 “{first}”라고 말하고 싶을 수 있습니다."
    return (f"가령 {scene}, 첫째는 “{first}”라고, "
            f"둘째는 “{second}”라고 말할 수 있습니다.")


def render(brief, evidence):
    relationship = brief["relationship"]
    dirs = relationship["directions"]
    direction_roles = [d["role"] for d in dirs]
    direction_refs = [d["id"] for d in dirs]
    a, b = direction_roles
    if a == b:
        opening = f"일간을 서로의 기준에서 읽으면 두 사람 모두 상대에게서 {a}의 상징을 읽습니다."
    else:
        opening = f"첫째 일간에서 둘째 일간은 {a}, 둘째 일간에서 첫째 일간은 {b}에 해당합니다."
    support, tension = relationship["support"], relationship["tension"]
    opening += " " + direction_reading(direction_roles)
    if support:
        opening += f" {describe_interaction(support)} {SUPPORTS[support['kind']]}"
    body = [_paragraph(opening, direction_refs + (references(support) if support else []))]

    contrast = relationship["contrast"]
    roles = contrast["roles"] if contrast else direction_roles
    focus_refs = list(direction_refs)
    if contrast:
        source = contrast["source"]
        letter = _read(source["read_stem"])
        location = f"{NAMES[source['person']]} {POSITIONS[source['pillar']]}"
        layer = "천간" if (tension or support)["layer"] == "stem" else "지지의 본기"
        facts = f"{location} {layer}인 {letter} 글자는 첫째에게 {roles[0]}, 둘째에게 {roles[1]}입니다."
        if len(contrast["same_letter"]) > 1:
            facts += f" 이 작용에 참여한 여러 자리에서 {letter} 글자가 확인됩니다."
        focus_refs = references(tension or support)
        focus_refs.extend(["a.day.stem", "b.day.stem"])
        if support and tension:
            focus_refs.extend(references(support))
        if tension:
            scope = SCOPE.get(relationship["scope"], "")
            if relationship["scope"] == "partial":
                slots = ", ".join(f"{NAMES[owner]}의 {POSITIONS[slot]}"
                                  for owner, slot in relationship["shared_slots"])
                scope = f"두 작용 모두 {slots}에 닿습니다. " + scope
            facts = f"{describe_interaction(tension)} {scope} {facts}"
            facts += " " + TENSIONS[tension["kind"]][0]
        facts = dialogue(roles, source["owner_ten_god"]) + " " + facts
        body.append(_paragraph(" ".join(facts.split()), focus_refs))
    else:
        body.append(_paragraph(
            "확정된 자리에서 이 글의 합·충·형·해 단서는 확인되지 않았습니다. "
            "앞의 두 말이 실제로 오간 적이 있는지는 두 사람의 경험에 비춰 보세요.",
            ["a.coverage", "b.coverage"],
        ))

    first, second = (ROLES[role][2] for role in roles)
    if first == second:
        check = f"‘{first}’에 대해 각자가 이해한 바를 비교해 보세요."
    else:
        check = f"이때 첫째는 ‘{first}’에, 둘째는 ‘{second}’에 마음이 쓰였는지 각자 얘기해 보세요."
    if tension:
        _, observe, try_next = TENSIONS[tension["kind"]]
    elif support:
        observe = "뜻이 맞았던 일이 있다면 처음으로 같이 결정할 수 있었던 대목을 찾아보세요."
        try_next = "그때 도움이 된 조건 하나만 다음 공동 결정에도 넣어 봅니다."
    else:
        observe = "같은 제안을 듣고 서로 다른 답을 했던 때가 있었다면 답한 이유를 각자 한 문장으로 말해 보세요."
        try_next = "서로 짐작한 이유와 실제로 들은 이유가 달랐다면 다음번에는 결정 전에 이유부터 들어 봅니다."
    if tension and support:
        renewal = (
            f"한 번 해 본 뒤에는 양쪽에 무엇이 달라졌는지 확인합니다. 첫째가 말한 ‘{first}’에만 변화가 있었는지, 둘째가 말한 ‘{second}’에도 변화가 있었는지 비교해 보세요."
            if relationship["shared_slots"] else
            "조건을 바꿔도 함께할 이유가 남는지까지 확인해 보세요."
        )
    else:
        renewal = "비슷한 경험이 없다면 이 장면은 건너뛰어도 됩니다."
    reflection = [
        _paragraph(f"{observe} {check}", focus_refs),
        _paragraph(f"{try_next} {renewal}",
                   focus_refs),
    ]
    return [
        {"title": "두 사람이 약속을 받아들이는 방식",
         "paragraphs": [individual(row, evidence) for row in brief["natal"]]},
        {"title": TITLES[tension["kind"]] if tension else "함께 뜻을 정하는 순간", "paragraphs": body},
        {"title": "다음에 함께 정할 때", "paragraphs": reflection},
    ]

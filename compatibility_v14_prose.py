"""Reader-facing Korean prose for the v1.4 interpretation plan."""

from compatibility_v12 import READINGS, _paragraph

NAMES = {"a": "첫째", "b": "둘째"}
POSITIONS = {"year": "연주", "month": "월주", "day": "일주", "hour": "시주"}
PERIODS = {"year": "태어난 해", "month": "태어난 달", "day": "태어난 날", "hour": "태어난 시각"}
TOPICS = {
    "agency": "각자의 몫과 자율성",
    "expression": "생각을 밖으로 표현하는 방식",
    "commitment": "서로에게 실제로 내어 줄 수 있는 것",
    "standard": "관계에 두는 기준과 책임",
    "reception": "상대의 말을 받아들이고 이해하는 과정",
}

TENSION_READINGS = {
    "육충": "두 사람이 같은 문제를 두고 서로 다른 전제에서 출발하는지",
    "육해": "같은 말이나 제안이 건넨 뜻과 다르게 받아들여지는지",
    "상형": "처음에 뜻이 맞아도 세부 기준에서 이견이 생기는지",
    "삼형": "한 가지를 바꿨을 때 다른 문제까지 함께 움직이는지",
    "자형": "이미 합의한 문제도 같은 이유로 다시 꺼내게 되는지",
}
SUPPORT_READINGS = {
    "천간합": "서로의 말을 이어받기 쉬운 대목",
    "육합": "둘 사이에 바로 접점을 찾을 수 있는 대목",
    "삼합": "각자가 보탠 요소가 맞물려 함께할 방향이 생기는 대목",
}
TENSION_QUESTIONS = {
    "육충": "처음부터 당연하다고 여긴 조건은 무엇이었나요?",
    "육해": "내 뜻과 상대가 받아들인 뜻은 어디서 달라졌나요?",
    "상형": "같이 하기로 했을 때 어디까지 정했다고 생각했나요?",
    "삼형": "어떤 조건을 바꾸면 다른 부분까지 다시 의논해야 할까요?",
    "자형": "이야기가 같은 곳으로 돌아올 때 아직 답을 듣지 못한 질문은 무엇인가요?",
}


def letter(symbol):
    return f"{READINGS[symbol]}({symbol})"


def source_summary(card):
    return " · ".join(
        f"{NAMES[s['person']]}의 {POSITIONS[s['pillar']]} {letter(s['symbol'])}"
        for s in card["sources"]
    )


def natal_prose(owner, finding, evidence):
    label = NAMES[owner]
    lead, alternative = finding["lead"], finding["alternative"]
    ref = lead["id"]
    refs = [ref, f"{owner}.day.stem", finding["coverage_id"]]
    topic = TOPICS[finding["lead_lens"]]
    position = POSITIONS[lead["pillar"]]
    stem = letter(lead["stem"])
    if lead["visible_role_ids"]:
        visible = "·".join(POSITIONS[evidence[i]["pillar"]] for i in lead["visible_role_ids"])
        opening = f"{label}의 명식에서 먼저 눈에 들어오는 주제는 ‘{topic}’입니다."
        detail = f"‘{PERIODS[lead['pillar']]}’에 해당하는 자리 안의 {stem} 글자가 {visible}의 겉글자에도 보입니다."
        refs.extend(lead["visible_role_ids"])
    elif ref == finding["month_id"]:
        opening = f"{label}의 명식은 태어난 달의 중심 글자에서 실마리를 줍니다."
        detail = f"그 글자 {stem}에서 읽은 주제는 ‘{topic}’입니다."
    else:
        opening = f"{label}의 경우 {position}에 숨어 있는 {stem} 글자에 먼저 주목했습니다."
        detail = f"여기서 읽는 주제는 ‘{topic}’입니다."

    if alternative:
        refs.append(alternative["id"])
        alternative_stem = letter(alternative["stem"])
        other = TOPICS[finding["alternative_lens"]]
        if topic == other:
            detail += f" {POSITIONS[alternative['pillar']]}의 {alternative_stem}에서도 같은 주제가 읽힙니다."
        else:
            detail += f" 한편 {POSITIONS[alternative['pillar']]}의 {alternative_stem}에서는 ‘{other}’도 읽을 수 있습니다."

    missing = finding["unresolved_pillars"]
    if missing:
        labels = "·".join(POSITIONS[p] for p in missing)
        detail += f" {labels}는 확정할 수 없어 여기서는 확인된 글자만 읽었습니다."
    return _paragraph(f"{opening} {detail}", refs)


def pair_prose(plan, evidence):
    refs = [*plan["direction_ids"]]
    a, b = (TOPICS[lens] for lens in plan["direction_lenses"])
    if a == b:
        perspective = f"두 사람의 중심 글자를 서로에게 비춰 보면 같은 주제가 보입니다. ‘{a}’입니다."
    else:
        perspective = (f"상대를 각자의 관점에서 읽을 때는 다른 주제가 보입니다. "
                       f"첫째에게는 ‘{a}’, 둘째에게는 ‘{b}’입니다.")

    support_id, tension_id = plan["support_id"], plan["tension_id"]
    for ref in (support_id, tension_id):
        if ref:
            refs.append(ref)
            refs.extend(s["source_id"] for s in evidence[ref]["sources"])
    support = evidence.get(support_id)
    tension = evidence.get(tension_id)
    shared = plan["scope"]
    if support and tension:
        support_topic = SUPPORT_READINGS[support["kind"]]
        tension_topic = TENSION_READINGS[tension["kind"]]
        if shared == "same_sources":
            symbols = "·".join(letter(s["symbol"]) for s in support["sources"])
            title = "통하는 지점에서 다시 걸릴 때"
            reading = (f"두 사람을 잇는 {symbols}에는 두 작용이 함께 잡힙니다. {support['kind']}과 {tension['kind']}입니다. "
                       f"{support_topic}에서 {tension_topic}도 살펴볼 만합니다.")
            question = ("쉽게 뜻이 맞았는데 막상 해 보니 서로 다르게 생각한 일이 있었나요? "
                        "상대의 설명을 듣기 전에 그때의 합의를 각자 한 문장으로 적어 보세요.")
        elif shared == "same_slots":
            title = "뜻이 맞은 뒤에 남는 차이"
            reading = (f"{source_summary(support)}에서 합을 읽을 수 있습니다. "
                       f"{support_topic}입니다. 같은 자리의 아래쪽 글자인 {source_summary(tension)}에서는 "
                       f"{tension_topic} 묻게 됩니다.")
            question = ("둘 다 좋다고 답했던 일이 있다면 무엇이 좋았는지, 이후 마음에 남은 점은 무엇이었는지 따로 이야기해 보세요.")
        elif shared == "partial":
            owner, position = plan["shared_slots"][0]
            title = "함께할 이유에 조건이 붙을 때"
            symbols = "·".join(letter(s["symbol"]) for s in support["sources"])
            reading = (f"{symbols}에 걸친 합에 {NAMES[owner]}의 {POSITIONS[position]}가 들어갑니다. "
                       f"그 자리는 마찰의 단서인 {tension['kind']}에도 걸쳐 있습니다. "
                       f"먼저 {support_topic}을 떠올려 보세요. 그 안에서 {tension_topic}도 따로 살펴볼 만합니다.")
            question = ("둘 다 해 보고 싶은 일이 있다면 ‘그래서 좋아’와 ‘그래도 망설여져’를 한 가지씩 말해 보세요. "
                        "좋은 이유를 놓치지 않으면서 망설임을 덜어 줄 조건을 함께 찾아보세요.")
        else:
            title = "잘 맞는 문제와 다시 볼 문제"
            reading = (f"{source_summary(support)}에서는 {support_topic}을 읽습니다. "
                       f"마찰의 단서는 별개의 자리인 {source_summary(tension)}에 있습니다. "
                       f"어떤 일에서는 뜻이 잘 맞더라도 다른 일에서는 {tension_topic} 따로 살펴볼 만합니다.")
            question = ("최근 뜻이 맞았던 일 하나와 말이 평행선을 달렸던 일 하나를 따로 떠올려 보세요. "
                        "잘 풀린 일에서 무엇을 공유하고 시작했는지, 어려웠던 일에도 그 전제가 있었는지 이야기해 보세요.")
    elif tension:
        title = "어디서 대화가 어긋나는가"
        reading = (f"{source_summary(tension)} 사이의 관계가 한 가지 단서를 줍니다. "
                   f"{TENSION_READINGS[tension['kind']]} 살펴볼 만합니다.")
        question = ("같은 문제를 두고 엇갈린 적이 있다면, 당시 서로 무엇을 이미 이해했다고 여겼는지 "
                    "각자의 말로 설명해 보세요.")
    elif support:
        title = "접점이 생기는 순간"
        reading = f"확인된 합은 {SUPPORT_READINGS[support['kind']]}을 돌아보게 합니다."
        question = ("둘이 수월하게 진행했던 일이 있다면, 상대의 어떤 말이나 선택 덕에 다음으로 넘어갈 수 있었는지 "
                    "하나씩 짚어 보세요.")
    else:
        title = "같은 말을 듣는 두 관점"
        reading = "확인된 자리의 교차 작용만으로 특정한 관계 흐름을 짚기 어려워, 두 관점의 주제에서 출발했습니다."
        question = ("두 사람에게 각자 중요했던 한마디를 골라 보세요. 왜 그 말이 남았는지, "
                    "상대에게도 같은 뜻이었는지 차례로 물어보세요.")

    if tension:
        question += f" {TENSION_QUESTIONS[tension['kind']]}"
    if not (support and tension):
        refs.extend(f"{owner}.coverage" for owner in NAMES)
    return title, _paragraph(f"{reading} {perspective}", refs), _paragraph(question, refs)


def render(plan, evidence):
    title, relationship, reflection = pair_prose(plan["relationship"], evidence)
    individuals = [natal_prose(owner, finding, evidence) for owner, finding in plan["natal"].items()]
    a, b = (plan["natal"][owner]["lead"] for owner in NAMES)
    refs = [a["id"], b["id"], "a.day.stem", "b.day.stem"]
    if a["stem"] == b["stem"] and a["ten_god"] != b["ten_god"]:
        first, second = (TOPICS[plan["natal"][owner]["lead_lens"]] for owner in NAMES)
        if first != second:
            individuals.append(_paragraph(
                f"두 명식에서 눈에 띄는 글자는 둘 다 {letter(a['stem'])}입니다. "
                f"태어난 날의 중심 글자를 기준으로 읽으면 첫째 쪽의 주제는 ‘{first}’, 둘째 쪽은 ‘{second}’입니다.",
                refs))
    elif plan["natal"]["a"]["lead_lens"] == plan["natal"]["b"]["lead_lens"]:
        topic = TOPICS[plan["natal"]["a"]["lead_lens"]]
        individuals.append(_paragraph(
            f"첫째의 {letter(a['stem'])}에서 읽은 주제는 둘째의 {letter(b['stem'])}에도 보입니다. "
            f"두 명식에서 함께 눈여겨볼 주제는 ‘{topic}’입니다. "
            "두 사람에게 그 주제가 실제로 같은 뜻인지는 대화에서 확인해 볼 문제입니다.", refs))
    return [
        {"title": "각자의 명식에서 먼저 보이는 것", "paragraphs": individuals},
        {"title": title, "paragraphs": [relationship]},
        {"title": "둘이 나눠 볼 이야기", "paragraphs": [reflection]},
    ]

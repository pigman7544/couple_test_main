"""Compose a complete RS manuscript from confirmed facts, without a provider."""

from compatibility_v12 import GOD_QUESTIONS, RELATION_LENS
from rs_gpt import STEM_NAMES, validate
from rs_synthesis import ELEMENT_STYLE, ROLE_MEANING, with_particle


# Each lens gives a concrete expression, the point where it can become a
# burden, and a small experiment a couple can try in that situation.
ROLE_SCENES = {
    "비견": ("휴일에 각자 하고 싶은 일을 먼저 꺼내는 모습",
           "의견을 맞추는 일이 내 선택을 포기하는 것처럼 느껴질 수 있어요",
           "함께할 시간 한 구간만 정하고 나머지는 각자 고른 일정에 써 보세요"),
    "겁재": ("함께 맡은 일에서 누가 첫 결정을 내릴지 살피는 모습",
           "둘이 동시에 앞장서면 도움을 받는 대신 자리를 빼앗긴 느낌이 들 수 있어요",
           "예약과 현장 진행을 나눠 각자 한 가지 결정권을 맡아 보세요"),
    "식신": ("피곤한 날 식사를 준비해 두거나 귀갓길을 챙기는 모습",
           "정성 들인 행동이 익숙해지면 수고를 알아차리기 어려울 수 있어요",
           "고마웠던 행동 하나를 구체적으로 짚고 다음에는 무엇을 해 줄지 물어보세요"),
    "상관": ("여행 계획에서 마음에 걸리는 부분을 먼저 말하는 모습",
           "내용에 바로 답하다 보면 기분이 어땠는지 듣는 순서를 놓칠 수 있어요",
           "고치고 싶은 점 하나와 그대로 두고 싶은 점 하나를 함께 말해 보세요"),
    "편재": ("예정한 가게가 문을 닫았을 때 근처의 다른 선택지를 찾아보는 모습",
           "한쪽에겐 신선한 제안인 변경이 다른 쪽에는 준비를 다시 해야 하는 일일 수 있어요",
           "새 제안을 꺼낼 때 그대로 갈 수 있는 선택지도 함께 남겨 보세요"),
    "정재": ("함께 쓰는 물건을 떨어지기 전에 보충하거나 약속한 비용을 챙기는 모습",
           "늘 챙기는 사람이 정해지면 배려가 맡겨진 일처럼 느껴질 수 있어요",
           "공동 비용이나 소모품 중 하나를 골라 다음 점검일과 담당을 정해 보세요"),
    "편관": ("갑자기 취소된 일정에 대안을 정하고 수습을 시작하는 모습",
           "빨리 해결하려는 판단이 상대에게는 의견을 낼 틈이 없다는 뜻으로 들릴 수 있어요",
           "급한 결정을 하나만 잠정적으로 내리고 확인할 시간을 따로 잡아 보세요"),
    "정관": ("만나기 어려워진 날 미리 연락하고 바뀐 약속을 다시 확인하는 모습",
           "서로 사정이 달라져도 처음 합의한 방식만 지키려 하면 부담이 쌓일 수 있어요",
           "늦을 때 연락하는 시점과 다음 약속을 잡을 사람을 함께 정해 보세요"),
    "편인": ("서운한 말을 듣고 곧바로 답하기보다 무슨 뜻이었는지 돌아보는 모습",
           "생각을 정리하는 침묵이 길어지면 상대는 대화가 끝난 줄 알 수 있어요",
           "지금 답하기 어려운 이유를 한 문장으로 말하고 돌아올 시간을 알려 주세요"),
    "정인": ("힘든 일이 있을 때 설명을 재촉하지 않고 곁에서 들어 주는 모습",
           "편안하게 이야기를 들어 주는 데 마음을 쓰다가 무엇을 바꿀지 의논할 기회를 놓칠 수 있어요",
           "먼저 들어 준 뒤 오늘 필요한 게 위로인지 도움인지 한 번만 확인해 보세요"),
}
SEATS = {
    "year": ("연간", "연지"),
    "month": ("월간", "월지"),
    "day": ("일간", "일지"),
    "hour": ("시간", "시지"),
}
STORY_DIMENSION = {
    "비견": "autonomy", "겁재": "conflict", "식신": "expression", "상관": "expression",
    "편재": "attraction", "정재": "security", "편관": "conflict", "정관": "security",
    "편인": "autonomy", "정인": "growth",
}


def paragraph(refs, *sentences, heading=None, lead=False):
    return {"heading": heading, "emphasize_lead": lead,
            "text": " ".join(sentences), "evidence_ids": list(dict.fromkeys(refs))}


def as_role(role):
    return with_particle(role, "으로", "로")


def natal(owner, charts, facts, name):
    chart = charts[owner]
    master = chart["day_master"]
    month = chart["month_command"]
    paragraphs = [paragraph(
        [f"{owner}.day.stem"],
        f"{name}님의 일간은 {with_particle(f'{STEM_NAMES[master]}({master})', '이에요', '예요')}.",
        f"이 글자는 사주에서 {ELEMENT_STYLE[chart['element']]}을 상징해요.",
        "여기에 태어난 달과 가까운 관계에서 드러날 수 있는 태도를 보태면, 같은 글자를 가진 사람도 서로 다른 방식으로 읽을 수 있어요.",
        heading=f"{name}님의 기본 성향", lead=owner == "a",
    )]
    stem = next((f"{owner}.{seat}.stem" for seat in ("month", "year", "hour")
                 if f"{owner}.{seat}.stem" in facts), None)
    if stem:
        fact = facts[stem]
        role = fact["ten_god"]
        seat = SEATS[fact["pillar"]][0]
        paragraphs.append(paragraph(
            [stem], f"{name}님의 {seat}은 {as_role(role)} 읽어요.",
            f"전통적으로 {ROLE_MEANING[role]}에 주목하는 풀이예요.",
            f"두 사람이 생활을 맞춰 간다면 {ROLE_SCENES[role][0]}에서 그 태도가 보일 수 있어요.",
        ))
    ref = month["principal_id"] if month else facts[f"{owner}.palace"]["source_ids"][0]
    role = facts[ref]["ten_god"]
    seat = "월지" if month else "일지"
    coverage = []
    if "hour" in chart["unresolved"]:
        coverage.append(f"{name}님의 시주는 확인되지 않았습니다.")
    if not month:
        coverage.append("절기 경계에 걸쳐 있어 태어난 달의 글자는 풀이에서 보류했어요.")
    paragraphs.append(paragraph(
        [ref, *([f"{owner}.coverage"] if coverage else [])],
        f"{name}님의 {seat} 본기는 {as_role(role)} 해석해요.",
        f"이 자리는 {ROLE_MEANING[role]}과 연결해 읽을 수 있어요." if not month else
        f"이 자리를 생활에 비춰 보면, {ROLE_SCENES[role][1]}.",
        *coverage,
    ))
    return paragraphs


def direction(viewer, other, names, facts, palace=False):
    reader, target = names[viewer], names[other]
    ref = f"{viewer}.reads.{other}.palace" if palace else f"pair.{viewer}.reads.{other}"
    fact = facts[ref]
    role = fact["ten_god"]
    if palace:
        stem = fact["principal_stem"]
        own = facts[f"{other}.palace"]["ten_god"]
        lead = f"{reader}님에게 {target}님의 일지 본기 {STEM_NAMES[stem]}({stem})는 {as_role(role)} 읽혀요."
        explanation = f"{target}님의 일지는 본인에게 {as_role(own)} 읽혀요."
        closing = f"함께 보내는 시간에는 {ROLE_MEANING[role]}이 관계를 이해하는 한 가지 단서가 될 수 있어요."
        return paragraph([ref, f"{other}.palace", *fact["source_ids"]], lead, explanation, closing)
    partner = facts.get(f"{viewer}.partner")
    refs = [ref]
    if partner:
        refs.append(f"{viewer}.partner")
    note = ("이 관계는 전통 풀이에서 쓰는 배우자성 범주에도 들어가요."
            if partner and partner["cross_is_partner_star"] else
            "두 사람이 서로를 볼 때 어떤 행동이 눈에 들어오는지 살펴볼 수 있는 대목이에요.")
    return paragraph(
        refs,
        f"{reader}님에게 {target}님의 일간은 {as_role(role)} 읽혀요.",
        f"처음 가까워지는 과정에서 {ROLE_SCENES[role][0]}이 인상에 남을 수 있어요.",
        note,
        f"이때 두 사람이 같은 뜻으로 받아들였는지는 직접 말을 나눠 보면서 알 수 있어요.",
        heading="서로에게 먼저 보이는 모습" if viewer == "a" else None, lead=viewer == "a",
    )


def relation_paragraph(ref, facts, names, heading):
    fact = facts[ref]
    kind = fact["kind"]
    layer = 0 if fact["layer"] == "stem" else 1
    places = [f"{names[s['person']]}님의 {SEATS[s['pillar']][layer]} {s['symbol']}" for s in fact["sources"]]
    scope = "두 명식을 포개어 보면" if ref.startswith("pair.") else "한 사람의 명식 안에"
    third = [f"여기에 {places[2]}도 함께 놓여 있어요."] if len(places) == 3 else []
    return paragraph(
        [ref], f"{scope} {', '.join(places[:2])}에 주목해요.",
        *third,
        f"전통 명리에서는 이 조합을 {as_role(kind)} 부릅니다.",
        f"둘이 함께할 때는 {RELATION_LENS[kind]}을 돌아보는 단서로 써 볼 수 있어요.",
        heading=heading,
    )


def compose_report(payload, couple):
    charts, facts = payload["charts"], payload["facts"]
    # Validate internal labels before inserting user-supplied names into prose.
    names = {"a": "ⓐ", "b": "ⓑ"}
    a, b = names.values()
    first = [p for owner in names for p in natal(owner, charts, facts, names[owner])]
    pair = [direction("a", "b", names, facts), direction("b", "a", names, facts),
            direction("b", "a", names, facts, palace=True),
            direction("a", "b", names, facts, palace=True)]
    pair[2]["heading"] = "가까워졌을 때 보이는 관계의 결"
    direct = facts["pair.palaces"]["direct_branch_relation_ids"]
    if direct:
        for index, ref in enumerate(direct):
            p = relation_paragraph(ref, facts, names, "두 사람이 가까이 지내는 방식" if not index else None)
            p["evidence_ids"].insert(0, "pair.palaces")
            pair.append(p)
    else:
        equal = facts["a.palace"]["branch"] == facts["b.palace"]["branch"]
        pair.append(paragraph(
            ["pair.palaces", "a.palace", "b.palace"],
            f"{a}님의 일지와 {b}님의 일지에는 직접 성립하는 조합이 없어요.",
            ("두 자리에 같은 글자가 놓여 있어 익숙함을 느끼는 지점이 있는지 살펴볼 수 있어요."
             if equal else "각자가 편하게 여기는 것을 따로 물어볼 때 두 자리의 차이를 생활에서 확인할 수 있어요."),
            "같은 공간에서 저녁을 보낼 때 무엇을 같이 하고 싶은지, 무엇은 각자 하고 싶은지 따로 말해 보면 관계에 필요한 거리가 구체적으로 드러나요.",
            heading="두 사람이 가까이 지내는 방식",
        ))
    relations = [ref for ref, fact in facts.items() if "sources" in fact]
    for prefix, title in (("pair.", "다른 자리에서 생기는 접점"), ("a.", f"{a}님에게 익숙할 수 있는 방식"),
                          ("b.", f"{b}님에게 익숙할 수 있는 방식")):
        candidates = [ref for ref in relations if ref.startswith(prefix) and ref not in direct]
        if candidates and len(pair) < 8:
            chosen = min(candidates, key=lambda ref: (
                sum(facts[ref]["kind"] in p["text"] for p in pair),
                -sum(s["pillar"] == "day" for s in facts[ref]["sources"]),
            ))
            pair.append(relation_paragraph(chosen, facts, names, title))
    ab, ba = "pair.a.reads.b", "pair.b.reads.a"
    r1, r2 = facts[ab]["ten_god"], facts[ba]["ten_god"]
    palace_a, palace_b = facts["a.palace"], facts["b.palace"]
    pa, pb = palace_a["ten_god"], palace_b["ten_god"]
    matching = [names[owner] + "님" for owner, palace in (("a", palace_a), ("b", palace_b))
                if palace["matches_other_day_master"]]
    if len(matching) == 2:
        summary = "각자의 배우자궁을 대표하는 글자가 서로를 나타내는 글자와 같아요."
    elif matching:
        summary = f"{matching[0]}의 배우자궁에는 상대를 나타내는 글자가 중심에 있어요."
    else:
        summary = "처음 인상과 가까이 지낼 때에 느끼는 편안함은 서로 다를 수 있어요."
    pair.append(paragraph(
        [ab, ba, "a.palace", "b.palace"],
        f"{a}님이 {b}님에게서 알아보기 쉬운 단서는 {ROLE_MEANING[r1]}에 있어요.",
        (f"반대로 {b}님에게는 {ROLE_MEANING[r2]}이 먼저 눈에 들어올 수 있어요." if r1 != r2
         else "두 사람 모두 그 태도에 공감할 여지가 있지만, 기대하는 정도까지 같은지는 대화를 나눠 봐야 해요."),
        summary,
        "한 주를 돌아보며 기억에 남은 배려를 하나씩 말하면 각자가 중요하게 여기는 행동을 비교할 수 있어요.",
        heading="두 사람의 궁합을 돌아보면",
    ))
    beat = next((beat for beat in couple["story_beats"] if STORY_DIMENSION[r1] in beat["dimensions"]),
                couple["story_beats"][0])
    third = [
        paragraph([ab], f"{a}님이 {b}님과 결정을 맞출 때는 {ROLE_MEANING[r1]}을 먼저 살펴보세요.",
                  f"{ROLE_SCENES[r1][2]}.", heading="마음과 행동을 맞춰 보는 연습", lead=True),
        paragraph([ba], f"{b}님은 {ROLE_MEANING[r2]}에 관한 자기 기준을 알려 주세요.",
                  f"“{GOD_QUESTIONS[r2]}”라고 먼저 물으면 각자 기대한 것을 비교해 볼 수 있어요.",
                  "한쪽이 질문을 던졌다면 그날의 결론을 내기 전에 다른 쪽도 자기 질문을 하나 보태 보세요."),
        paragraph(["a.palace", "b.palace"],
                  f"부딪힌 직후에는 {a}님이 중요하게 여길 수 있는 {ROLE_MEANING[pa]}과 "
                  f"{b}님의 {ROLE_MEANING[pb]}이 대화에 어떻게 드러났는지 돌아보세요."
                  if pa != pb else f"두 사람이 {ROLE_MEANING[pa]}에 마음이 가더라도 다툰 직후에는 각자 원하는 반응을 짚어 보는 편이 좋아요.",
                  "잠시 멈출 때는 다음에 말을 나눌 시각도 정해 두세요.",
                  "돌아온 뒤에는 각자 바라는 변화 한 가지를 말하고, 바로 답하기 전에 들은 뜻을 되짚어 보세요."),
        paragraph([ab], f"『{couple['work']}』의 {couple['name']} 이야기에는 ‘{beat['summary'].rstrip('.。')}’라는 장면이 나와요.",
                  f"그 장면에서 인물들이 무엇을 선택하는지 살펴보고, 두 사람의 일상에서는 {ROLE_MEANING[r1]}을 어떤 행동으로 전할지 이야기해 보세요.",
                  heading="작품 속 두 사람을 만나다"),
        paragraph(["b.palace", "a.palace"],
                  f"약속을 오래 지키려면 {ROLE_MEANING[pb]}이 두 사람의 일정 안에서 어떤 모습이어야 할지 정해 보세요.",
                  "앞으로 한 주 동안 각자 맡을 일 하나만 정한 뒤, 주말에 시간과 수고가 어느 쪽에 몰렸는지 확인해 보세요.",
                  "사정이 달라졌다면 다음 주에 바꿔 볼 역할 하나를 그 자리에서 정해도 좋아요.", heading="다음 주에 다시 꺼내 볼 이야기"),
    ]
    manuscript = {"chapters": [
        {"title": "서로 다른 두 사람의 사주팔자", "paragraphs": first},
        {"title": "두 사람의 궁합", "paragraphs": pair},
        {"title": "두 사람을 위한 조언과 닮은 커플", "paragraphs": third},
    ]}
    audit = validate(manuscript, facts, names, couple)
    display = {owner: f"{payload['names'][owner]}님" for owner in names}
    if display["a"] == display["b"]:
        display["a"] += "(가)"
        display["b"] += "(나)"
    for chapter in manuscript["chapters"]:
        for p in chapter["paragraphs"]:
            for field in ("heading", "text"):
                if p[field]:
                    for owner in names:
                        p[field] = p[field].replace(f"{names[owner]}님", display[owner])
    return {**manuscript, "audit": audit, "mode": "local"}

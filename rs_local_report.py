"""Compose a complete RS manuscript from confirmed facts, without a provider."""

from compatibility_v12 import GOD_QUESTIONS
from rs_gpt import CHART_SYMBOLS, STEM_NAMES, validate
from rs_synthesis import with_particle


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
# Short actions make the two readings of a single palace comparable.
ROLE_ACTIONS = {
    "비견": "각자 판단할 여지를 남기는 일",
    "겁재": "누가 결정할지 먼저 정하는 일",
    "식신": "필요한 것을 살펴 손을 보태는 일",
    "상관": "걸리는 점을 말로 꺼내는 일",
    "편재": "그 자리에서 다른 선택지를 찾는 일",
    "정재": "맡은 몫을 꾸준히 챙기는 일",
    "편관": "급한 일을 먼저 맡아 수습하는 일",
    "정관": "합의한 기준과 약속을 지키는 일",
    "편인": "자기 생각부터 차분히 정리하는 일",
    "정인": "상대가 말할 때까지 곁에서 기다리는 일",
}

# Each entry follows one recorded story beat and asks about a choice in it.
STORY_PASSAGES = {
    "c01": ("춘향과 몽룡은 처음 만나 정을 맺어요", "첫 만남을 떠올리며 상대의 어떤 행동이 기억에 남았는지 하나씩 말해 보세요"),
    "c02": ("칠석에 견우와 직녀가 오작교에서 만났다는 이야기가 전해져요", "함께 보낼 시간이 짧은 주에는 그 시간에 가장 하고 싶은 일을 하나씩 골라 보세요"),
    "c03": ("평강은 온달이 무예와 생활의 기반을 갖추도록 도와요", "상대가 배우고 싶은 일이 있다면 함께 연습할지 필요한 준비만 도울지 물어보세요"),
    "c06": ("백소정의 정체가 드러나며 허선과의 관계가 흔들려요", "예상 밖의 이야기를 들었을 때 그 자리에서 묻고 싶은 것과 시간을 두고 확인할 것을 나눠 보세요"),
    "c10": ("로미오와 줄리엣은 무도회에서 처음 만나요", "처음 상대에게 말을 걸고 싶었던 순간에 어떤 표정이나 말이 기억나는지 이야기해 보세요"),
    "c11": ("청혼과 편지, 위컴 사건을 거치면서 엘리자베스와 다아시는 서로에 대한 판단을 바꿔요", "처음엔 뜻을 몰랐지만 나중에 이해하게 된 행동이 있었는지 떠올려 보세요"),
    "c13": ("귀향한 오디세우스와 페넬로페는 서로를 확인해요", "오래 떨어져 지내다 만나면 그동안 바뀐 일상 중 무엇부터 듣고 싶은지 물어보세요"),
    "c18": ("개츠비는 부를 쌓아 데이지와 다시 만나려 해요", "오랜만에 만나는 사람을 위해 뭔가 준비하기 전에 지금 그 사람이 원하는 만남을 물어보세요"),
    "f01": ("홈즈가 사건을 풀어 가는 동안 왓슨은 동행하며 기록을 남겨요", "함께 맡은 일이 끝나면 각자가 보았던 중요한 순간을 하나씩 기록해 비교해 보세요"),
    "f02": ("산초는 돈키호테의 판단을 자신이 보는 현실에 비추어 받아들여요", "둘이 새로운 일을 계획한다면 해 보고 싶은 일과 쓸 수 있는 시간을 각각 적어 보세요"),
    "f03": ("포숙아가 관중의 능력을 인정해 추천했다는 고사가 전해져요", "상대를 다른 사람에게 소개한다면 어떤 구체적인 행동을 들어 그 사람을 설명하고 싶은지 생각해 보세요"),
    "f04": ("처음에는 맞서 싸운 길가메시와 엔키두가 이후 친구가 되어 함께 모험해요", "처음엔 의견이 달랐지만 함께해 볼 만하다고 느낀 일이 있었는지 이야기해 보세요"),
}
LONG_TERM_TESTS = {
    "비견": "함께해야 하는 일과 혼자 맡아도 되는 일에 표시해 보세요",
    "겁재": "둘 다 맡으려는 일이 있다면 이번 주에 결정할 사람을 정해 보세요",
    "식신": "평소 말없이 해 오던 일 하나를 꺼내 앞으로도 같은 사람이 맡을지 의논해 보세요",
    "상관": "일주일 동안 바꿔 보고 싶은 집안일 순서를 한 가지만 골라 보세요",
    "편재": "늘 하던 방식이 막힐 때의 대안을 하나만 정해 두세요",
    "정재": "정기적으로 들어가는 비용 중 다음 주에 함께 확인할 항목을 정해 보세요",
    "편관": "급한 일이 겹치면 누구에게 먼저 연락할지 정해 두세요",
    "정관": "서로에게 알리지 않고 바꿀 수 있는 일정과 미리 확인할 일정을 나눠 보세요",
    "편인": "지금 결정하기 어려운 일은 다음에 확인할 날짜와 함께 적어 두세요",
    "정인": "부탁할 일이 있다면 이번 주 어느 날에 시간을 낼 수 있는지 물어보세요",
}

RELATION_SCENES = {
    "천간합": "함께 살 곳을 고르는 중이라면 각자가 중요하게 여기는 조건을 말하고, 먼저 겹치는 조건부터 표시해 볼 수 있어요",
    "육합": "손님을 초대하는 날이라면 한 사람이 준비를 시작하고 다른 사람이 빈자리를 메우는 식으로 호흡이 맞는지 살펴보세요",
    "삼합": "이사를 준비한다면 각자 맡은 일의 마감 시점을 한곳에 적어 보고, 따로 진행하던 일이 어느 순간 맞물리는지 살펴보세요",
    "육충": "한 사람은 아침에 움직이고 다른 사람은 늦게까지 일한다면, 바꾸기 어려운 시간과 맞출 수 있는 시간을 따로 정해 보세요",
    "상형": "같이 요리할 때 손질과 정리의 순서를 두고 말이 반복된다면, 각자 왜 그 순서를 선호하는지 먼저 말해 보세요",
    "삼형": "두 집안의 모임 일정이 겹치면 한꺼번에 해결하려 하기보다 누구에게 언제까지 답해야 하는지부터 정리해 보세요",
    "자형": "서로 먼저 연락하기를 기다리다 약속이 미뤄진다면, 다음 한 번은 누가 언제 연락할지 정해 두고 기다림이 달라지는지 보세요",
    "육해": "옷이나 물건을 대신 골라 주고 싶을 때는 추천이 반가운지, 직접 비교하고 싶은지 물어서 배려가 어떻게 전달되는지 살펴보세요",
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
    stem = next((f"{owner}.{seat}.stem" for seat in ("month", "year", "hour")
                 if f"{owner}.{seat}.stem" in facts), None)
    first = paragraph(
        [f"{owner}.day.stem"],
        f"{name}님의 일간은 {with_particle(f'{STEM_NAMES[master]}({master})', '이에요', '예요')}.",
        f"이 글자의 오행은 {CHART_SYMBOLS[master]['element_name']}에 해당해요.",
        heading=f"{name}님의 기본 성향", lead=owner == "a",
    )
    coverage = []
    if not month:
        subject = "해와 달의 기둥" if "year" in chart["unresolved"] else "달의 기둥"
        coverage.append(f"절기 경계에 걸린 {subject}은 풀이에서 보류했어요.")
    if "hour" in chart["unresolved"]:
        coverage.append(f"{name}님의 시주는 확인되지 않았습니다.")
    coverage_refs = [f"{owner}.coverage"] if coverage else []
    if not month:
        if stem:
            role = facts[stem]["ten_god"]
            seat = SEATS[facts[stem]["pillar"]][0]
            first["evidence_ids"].append(stem)
            first["text"] += f" {name}님의 {seat}은 {as_role(role)} 읽어요."
            first["text"] += f" 생활에서는 {ROLE_SCENES[role][0]}에서 그 태도가 드러날 수 있어요."
        return [first, paragraph([*coverage_refs, f"{owner}.day.stem"], *coverage,
                                 "가까운 관계에 관한 풀이는 확인된 날의 글자에서 이어갈게요.")]

    ref = month["principal_id"]
    role = facts[ref]["ten_god"]
    reading = f"{name}님의 월지 본기는 {as_role(role)} 해석해요."
    stem_role = facts[stem]["ten_god"]
    seat = SEATS[facts[stem]["pillar"]][0]
    stem_reading = f"{name}님의 {seat}은 {as_role(stem_role)} 읽어요."
    if stem_role == role:
        first["evidence_ids"].extend([stem])
        first["text"] += f" {stem_reading} {ROLE_SCENES[stem_role][0]}에서 그 태도가 보일 수 있어요."
        bridge = "앞의 자리에서도 살핀 태도가 이 자리에 한 번 더 나타나요."
    else:
        first["evidence_ids"].append(stem)
        first["text"] += f" {stem_reading} 생활에서는 {ROLE_SCENES[stem_role][0]}에서 그 태도가 드러날 수 있어요."
        bridge = f"앞서 본 태도에 더해 {ROLE_ACTIONS[role]}에도 마음이 갈 수 있어요."
    paragraphs = [first, paragraph([ref, stem, *coverage_refs], reading, bridge,
                                    f"{ROLE_SCENES[role][1]}.", *coverage)]
    if stem_role == role:
        extra = next((f"{owner}.{seat}.stem" for seat in ("year", "hour")
                      if f"{owner}.{seat}.stem" in facts and facts[f"{owner}.{seat}.stem"]["ten_god"] != role), None)
        if extra:
            extra_role = facts[extra]["ten_god"]
            extra_seat = SEATS[facts[extra]["pillar"]][0]
            paragraphs.append(paragraph(
                [extra, ref], f"{name}님의 {extra_seat}은 {as_role(extra_role)} 읽어요.",
                f"{ROLE_SCENES[extra_role][0]}도 떠올릴 수 있어요.",
                f"{ROLE_ACTIONS[role]}도, {ROLE_ACTIONS[extra_role]}도 중요하게 여기는 상황이라면, 무엇을 먼저 챙길지 상대와 상의해 보세요.",
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
        comparison = (
            f"예를 들어 함께 낯선 일을 맡았을 때 두 사람 모두 {ROLE_ACTIONS[role]}에 마음이 갈 수 있어요."
            if role == own else
            f"{target}님이 {ROLE_ACTIONS[own]}에 마음을 쓴다면, {reader}님은 그중에서도 {ROLE_ACTIONS[role]}에 의미를 둘 수 있어요."
        )
        return paragraph(
            [ref, f"{other}.palace", *fact["source_ids"]],
            f"{reader}님에게 {target}님의 일지 본기 {with_particle(f'{STEM_NAMES[stem]}({stem})', '은', '는')} {as_role(role)} 읽혀요.",
            f"{target}님의 일지는 본인에게 {as_role(own)} 읽혀요.",
            comparison,
        )
    partner = facts.get(f"{viewer}.partner")
    refs = [ref]
    note = []
    if partner and partner["cross_is_partner_star"]:
        refs.append(f"{viewer}.partner")
        note = [
            f"이 십성은 전통 풀이에서 {reader}님의 배우자성으로 보는 {partner['category']}에 들어가요.",
            "상대의 날을 대표하는 글자를 기준으로 본 분류예요.",
        ]
    return paragraph(
        refs,
        f"{reader}님에게 {target}님의 일간은 {as_role(role)} 읽혀요.",
        f"상대에게서 {ROLE_SCENES[role][0]}이 눈에 들어올 수 있어요.",
        *note, heading="서로에게 먼저 보이는 모습" if viewer == "a" else None,
        lead=viewer == "a",
    )


def relation_paragraph(ref, facts, names, heading, overlapping=()):
    fact = facts[ref]
    kind = fact["kind"]
    layer = 0 if fact["layer"] == "stem" else 1
    places = [f"{names[s['person']]}님의 {SEATS[s['pillar']][layer]} {s['symbol']}" for s in fact["sources"]]
    scope = "두 명식을 포개면" if ref.startswith("pair.") else "한 사람의 명식 안에서는"
    lead = [f"{scope} {', '.join(places[:2])} 두 자리가 맞물려요."]
    if len(places) == 3:
        lead.append(f"여기에 {places[2]} 자리도 들어가요.")
    lead.append(f"전통 명리에서는 이 조합을 {as_role(kind)} 읽어요.")
    if overlapping:
        other = facts[overlapping[0]]["kind"]
        lead.append(f"같은 두 자리에는 {other}도 겹쳐 있어, 조정이 필요한 지점을 함께 살펴볼 수 있어요.")
    return paragraph([ref, *overlapping], *lead, f"{RELATION_SCENES[kind]}.",
                     heading=heading)


def compose_report(payload, couple):
    charts, facts = payload["charts"], payload["facts"]
    # Validate internal labels before inserting user-supplied names into prose.
    names = {"a": "ⓐ", "b": "ⓑ"}
    a, b = names.values()
    first = [p for owner in names for p in natal(owner, charts, facts, names[owner])]
    pair = [direction("a", "b", names, facts), direction("b", "a", names, facts)]
    palace_a, palace_b = facts["a.palace"], facts["b.palace"]
    direct = facts["pair.palaces"]["direct_branch_relation_ids"]
    positions = [
        f"{name}님의 일지에는 {palace['branch']} 자가 있어요."
        for name, palace in ((a, palace_a), (b, palace_b))
    ]
    if not direct:
        positions.append("두 자리만 놓고 보면 직접 맺는 조합이 없어요.")
    pair.append(paragraph(
        ["pair.palaces", "a.palace", "b.palace"],
        "가까운 관계에서 무엇을 편하게 느끼는지 살필 때는 배우자궁을 봐요.",
        *positions, heading="가까워졌을 때 살피는 자리",
    ))
    pair.extend(direction(viewer, other, names, facts, palace=True)
                for viewer, other in (("b", "a"), ("a", "b")))
    if direct:
        primary = next((ref for ref in direct if facts[ref]["kind"] == "육충"), direct[0])
        pair.append(relation_paragraph(primary, facts, names, "두 일지가 직접 만나는 자리",
                                       [ref for ref in direct if ref != primary]))
        pair[-1]["evidence_ids"].insert(0, "pair.palaces")

    other_relations = [ref for ref, fact in facts.items() if "sources" in fact and ref not in direct]
    # An exact same-kind reading of the same arrangement adds little to this chapter.
    used_kinds = {facts[ref]["kind"] for ref in direct}
    for prefix, title in (("pair.", "다른 자리에서 생기는 접점"),
                          ("pair.", "두 명식을 함께 볼 때"),
                          ("a.", f"{a}님의 명식 안에서"), ("b.", f"{b}님의 명식 안에서")):
        candidates = [ref for ref in other_relations
                      if ref.startswith(prefix) and facts[ref]["kind"] not in used_kinds
                      and (title != "두 명식을 함께 볼 때"
                           or any(s["pillar"] == "day" for s in facts[ref]["sources"]))]
        if candidates:
            chosen = max(candidates, key=lambda ref: (
                any(s["pillar"] == "day" for s in facts[ref]["sources"]),
                len(facts[ref]["sources"]),
            ))
            pair.append(relation_paragraph(chosen, facts, names, title))
            used_kinds.add(facts[chosen]["kind"])
        if len(pair) >= 8:
            break

    ab, ba = "pair.a.reads.b", "pair.b.reads.a"
    r1, r2 = facts[ab]["ten_god"], facts[ba]["ten_god"]
    pa, pb = palace_a["ten_god"], palace_b["ten_god"]
    matching = [names[owner] + "님" for owner, palace in (("a", palace_a), ("b", palace_b))
                if palace["matches_other_day_master"]]
    if len(matching) == 2:
        link = ["두 배우자궁의 중심 글자가 서로의 일간과 같아요."]
    elif matching:
        link = [f"{matching[0]}의 배우자궁 중심 글자가 상대의 일간과 같아요."]
    else:
        link = []
    contrast = (
        f"함께 준비하는 일이 있다면 {a}님에게는 {ROLE_ACTIONS[r1]}에, {b}님에게는 {ROLE_ACTIONS[r2]}에 상대의 배려가 담겨 보일 수 있어요."
        if r1 != r2 else
        f"두 사람 모두 {ROLE_ACTIONS[r1]}에서 상대의 마음을 읽기 쉬울 수 있어요."
    )
    pair.append(paragraph(
        [ab, ba, "a.palace", "b.palace"], *link, contrast,
        (f"그 일을 마친 뒤 {a}님은 {ROLE_ACTIONS[pa]}에서, {b}님은 {ROLE_ACTIONS[pb]}에서 편안함을 느꼈는지도 함께 살펴보세요."
         if pa != pb else f"조금 더 가까워진 사이에서는 두 사람 모두 {ROLE_ACTIONS[pa]}을 편하게 여기는지 물어볼 만해요."),
        "상대가 해 준 일과 내가 바라던 일을 나누어 말하면 서로의 대답을 비교하기 쉬워요.",
        heading="처음 눈에 띈 배려와 가까워진 뒤의 기대",
    ))

    event, story_advice = STORY_PASSAGES[couple["id"]]
    third = [
        paragraph([ab], f"{a}님이 {b}님에게 바라는 게 있다면 한 가지 상황을 골라 말해 보세요.",
                  f"{ROLE_SCENES[r1][2]}.", heading="다음에 해 볼 대화", lead=True),
        paragraph([ba], f"{b}님은 상대가 무엇을 바라는지 먼저 들어 보세요.",
                  f"“{GOD_QUESTIONS[r2]}”처럼 묻고, 들은 답에서 이번에 맞춰 볼 행동 하나를 정해도 좋아요."),
        paragraph(["a.palace", "b.palace"],
                  (f"같은 일을 두고 {a}님은 {ROLE_ACTIONS[pa]}에, {b}님은 {ROLE_ACTIONS[pb]}에 먼저 신경 쓸 수 있어요."
                   if pa != pb else f"둘 다 {ROLE_ACTIONS[pa]}을 중요하게 여기더라도 원하는 때는 다를 수 있어요."),
                  "대화가 어려워지면 이어서 이야기할 시각부터 정하고, 다시 만났을 때 각자 가장 먼저 확인하고 싶은 일 하나를 말해 보세요."),
        paragraph(["a.palace", "b.palace"],
                  f"{LONG_TERM_TESTS[pb]}.",
                  "한 주 뒤 실제로 들인 시간을 비교하고, 나누고 싶은 일 하나를 골라 다시 맡아 보세요.",
                  heading="한 주 뒤 확인할 일"),
        paragraph([ab, ba], f"『{couple['work']}』 속 {couple['name']} 이야기에는 이런 대목이 있어요. {event}.",
                  f"{story_advice}.", heading="작품 속 두 사람을 만나다"),
    ]
    manuscript = {"chapters": [
        {"title": "두 사람의 사주팔자", "paragraphs": first},
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

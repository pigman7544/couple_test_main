"""Compose the preview from confirmed natal and cross-chart evidence."""

from c06_narrative import particle
from compatibility_v11 import BRANCH_ELEMENTS, STEM_ELEMENTS, SUPPORT, ten_god
from compatibility_v12 import (
    EDITORIAL_WEIGHT, ELEMENT, GOD_LENS, GOD_QUESTIONS, READINGS,
    analyze_pair, review_report,
)


NAMES = {"a": "첫째", "b": "둘째"}
ELEMENT_WORD = {"wood": "나무", "fire": "불", "earth": "흙", "metal": "쇠", "water": "물"}


def stem_with_element(stem):
    element = STEM_ELEMENTS[stem]
    return f"{READINGS[stem]}{ELEMENT[element]}({stem}, {ELEMENT_WORD[element]} 기운)"
ELEMENT_STYLE = {
    "wood": "아직 모양이 잡히지 않은 일에 방향을 내고 키우는 힘",
    "fire": "마음속에 있던 뜻을 드러내고 눈앞의 반응에 응하는 힘",
    "earth": "흩어진 사정을 받아들여 계속 이어 갈 틀을 만드는 힘",
    "metal": "지킬 기준을 세우고 남길 것과 덜어 낼 것을 가르는 힘",
    "water": "상황의 흐름을 살피고 그에 맞는 길을 찾는 힘",
}
ROLE_MEANING = {
    "비견": "가까운 사이에서도 각자의 판단을 존중하는 태도",
    "겁재": "한정된 몫을 두고 서로 주도권을 의식하는 마음",
    "식신": "마음을 꾸준한 돌봄이나 손에 잡히는 결과로 표현하는 힘",
    "상관": "익숙한 방식에서 걸리는 점을 찾아 자기 말로 드러내는 힘",
    "편재": "새로운 가능성을 알아보고 여러 자원을 유연하게 쓰는 감각",
    "정재": "맡은 몫을 헤아리고 오래 감당할 수 있게 가꾸는 태도",
    "편관": "어려운 상황에서 결단하고 책임을 떠맡는 힘",
    "정관": "서로의 역할을 분명히 하고 한 번 맺은 약속을 지키는 태도",
    "편인": "받아들인 것을 자기 방식으로 곱씹고 해석하는 힘",
    "정인": "이해와 보살핌을 받으며 마음을 놓고 힘을 얻는 경험",
}
ELEMENT_SCENE = {
    "wood": "둘이 처음 해 보는 일이 생기면, 함께 첫발을 떼는 데서 호흡을 맞춰 볼 수 있습니다.",
    "fire": "반가운 일이나 서운한 일이 생겼을 때 그 마음을 말로 건네면 상대도 반응할 여지가 생깁니다.",
    "earth": "둘의 사정이 제각각일 때 시간을 맞추거나 일을 나누며 함께할 방법을 찾아볼 수 있습니다.",
    "metal": "할 일이 겹쳤을 때 무엇부터 지킬지 정해 두면 서로 어디에 힘을 쓸지 분명해집니다.",
    "water": "둘이 세운 계획이 틀어졌을 때 상대의 사정을 듣고 다른 방법을 찾는 쪽으로 이 힘을 써 볼 수 있습니다.",
}
RELATIONS = {
    "천간합": "두 사람은 원하는 바를 직접 말할 때 접점을 찾기 쉽습니다.",
    "육합": "각자 편한 방식이 상대의 수고를 덜어 주는 쪽으로 맞물릴 수 있습니다.",
    "삼합": "두 사람이 흩어진 일을 하나의 목표로 모으기 쉬운 접점이 있습니다.",
    "육충": "함께 지내며 각자 당연하게 여겼던 생활 방식을 바꿔야 할 수 있습니다.",
    "상형": "둘 다 성의를 들여도 일하는 순서나 기준을 두고 같은 얘기를 몇 번씩 할 수 있습니다.",
    "삼형": "각자 맡은 일을 잘해도 다른 쪽 일정까지 얽히면 함께 풀어야 할 일이 생깁니다.",
    "자형": "한 사람이 물러서면 다른 사람도 말을 아끼듯, 비슷하게 반응할 때 문제가 길어질 수 있습니다.",
    "육해": "도와주려는 말이 상대에게는 재촉처럼 들리는 등 뜻이 어긋날 수 있습니다.",
}
SEAT = {"year": "오래 익힌 관계의 틀", "month": "평소 일을 꾸려 가는 방식",
        "day": "가까운 사이에 바라는 것", "hour": "앞날에 품은 뜻"}
TRINE_ELEMENT = {
    frozenset("申子辰"): "수", frozenset("亥卯未"): "목",
    frozenset("寅午戌"): "화", frozenset("巳酉丑"): "금",
}
STEM_SEAT = {"year": "해의 앞 글자", "month": "달의 앞 글자",
             "day": "날의 앞 글자", "hour": "시각의 앞 글자"}
BRANCH_SEAT = {"year": "연지", "month": "월지", "day": "일지", "hour": "시지"}
PARTNER_ROLES = {
    "male": ("재성", {"정재", "편재"}),
    "female": ("관성", {"정관", "편관"}),
}


def symbol(value):
    return f"{READINGS[value]}({value})"


def with_particle(word, consonant, vowel):
    reading = word.rsplit("(", 1)[0].rstrip() if word.endswith(")") else word
    return word + particle(reading, consonant, vowel)


def paragraph(text, refs, owner=None, heading=None):
    entry = {"text": text, "evidence_ids": list(dict.fromkeys(refs))}
    if owner:
        entry["owner"] = owner
    if heading:
        entry["heading"] = heading
    return entry


def principal(context, position):
    return next((row for row in context["placements"]
                 if row["pillar"] == position and row["tier"] == "본기"), None)


def hidden_text(placements):
    return ", ".join(f"{READINGS[p['stem']]}({p['ten_god']})" for p in placements)


def partner_placements(result, owner, target, roles):
    stem = result["charts"][owner]["day_master"]
    visible = [
        (f"{STEM_SEAT[position]} {symbol(detail['stem'])}", f"{target}.{position}.stem", god)
        for position, detail in result["charts"][target]["details"].items()
        if (god := ten_god(stem, detail["stem"])) in roles
    ]
    hidden = [
        (f"{BRANCH_SEAT[p['pillar']]}에 든 {symbol(p['stem'])}", p["id"], god)
        for p in result["contexts"][target]["placements"]
        if (god := ten_god(stem, p["stem"])) in roles
    ]
    return visible + hidden


def natal(result, owner, gender):
    context = result["contexts"][owner]
    chart = result["charts"][owner]
    stem = chart["day_master"]
    element = STEM_ELEMENTS[stem]
    day_id = f"{owner}.day.stem"
    palace = principal(context, "day")
    month = principal(context, "month")
    basics = [f"{owner}.{position}.stem" for position in chart["details"]]
    branches = [p for p in context["placements"] if p["tier"] == "본기"]
    main_elements = [STEM_ELEMENTS[d["stem"]] for d in chart["details"].values()]
    main_elements.extend(BRANCH_ELEMENTS[d["branch"]] for d in chart["details"].values())
    count = main_elements.count(element)
    opening = paragraph(
        f"{NAMES[owner]}의 관계에서 눈여겨볼 점은 {ELEMENT_STYLE[element]}입니다. "
        f"태어난 날의 첫 글자인 일간은 {stem_with_element(stem)}이고, 확인된 글자 중 같은 기운을 대표하는 자리는 {count}곳입니다. "
        f"{ELEMENT_SCENE[element]}",
        [*basics, *(p["id"] for p in branches)], owner, "태어난 날의 글자",
    )

    if month:
        season = context["month_command"]
        role = month["ten_god"]
        hidden = [p for p in context["placements"] if p["pillar"] == "month"]
        layers = ""
        if hidden[1:]:
            layers = (" 월지 안에 함께 든 글자를 지장간이라 하며, 여기에는 "
                      f"{hidden_text(hidden[1:])}도 있습니다.")
        if month["exposed_at"]:
            layers += " 달의 중심 기운은 명식의 앞 글자에도 한 번 더 나타납니다."
        month_entry = paragraph(
            f"{NAMES[owner]}의 평소 생활에서는 {with_particle(ROLE_MEANING[role], '을', '를')} 눈여겨볼 만합니다. "
            f"태어난 달의 뒤 글자인 월지는 {season['season']}의 {symbol(season['branch'])}이고, "
            f"그 속의 중심 글자 {with_particle(symbol(month['stem']), '은', '는')} 일간을 기준으로 {role}에 해당합니다."
            f"{layers} 가까운 사람이 이 모습을 알아보려면, 바쁜 날 무엇을 먼저 챙기는지 살펴볼 수 있습니다.",
            [day_id, *(p["id"] for p in hidden), *month["exposed_at"]],
            owner, "태어난 계절과 평소의 모습",
        )
    else:
        month_entry = paragraph(
            "평소 생활에 관한 계절 풀이는 태어난 시각을 확인한 뒤 이어갈 수 있습니다. "
            "태어난 날이 절기가 바뀌는 때와 겹쳐 월주에 두 후보가 있습니다. "
            "가까운 사람에게 무엇을 기대하는지는 확인된 일지에서 살펴볼 수 있습니다.",
            [day_id, f"{owner}.coverage"], owner, "절기가 바뀌는 날",
        )

    hidden = [p for p in context["placements"] if p["pillar"] == "day"]
    role = palace["ten_god"]
    branch = symbol(chart["pillars"]["day"][1])
    text = (
        f"{NAMES[owner]}는 가까운 사이에서 {with_particle(ROLE_MEANING[role], '을', '를')} 소중하게 여길 수 있습니다. "
        f"태어난 날의 뒤 글자이자 가까운 관계를 살피는 배우자궁은 {branch}이며, "
        f"그 중심 글자 {with_particle(symbol(palace['stem']), '은', '는')} 자신의 일간을 기준으로 {role}에 해당합니다."
    )
    if hidden[1:]:
        other_role = hidden[1]["ten_god"]
        text += (f" 이 자리의 {hidden_text(hidden[1:])}에서는 "
                 f"{with_particle(ROLE_MEANING[other_role], '을', '를')} 함께 살핍니다.")
    tradition = PARTNER_ROLES.get(gender) if isinstance(gender, str) else None
    markers = []
    if tradition:
        category, roles = tradition
        markers = partner_placements(result, owner, owner, roles)
        if role in roles:
            text += (f" 이 {with_particle(role, '은', '는')} 전통적으로 배우자를 상징하는 "
                     f"{category}, 곧 이 명식의 배우자성에도 해당합니다.")
        elif markers:
            text += (f" 이 명식에서 배우자를 상징하는 {with_particle(category, '은', '는')} "
                     f"{markers[0][0]}에서 {markers[0][2]}에 해당합니다.")
        else:
            text += f" 확인된 글자에는 전통적으로 배우자성을 뜻하는 {with_particle(category, '이', '가')} 드러나지 않습니다."
    palace_entry = paragraph(
        text + f" “{GOD_QUESTIONS[role]}” 하고 물어보면 가까운 사람에게 바라는 점을 구체적으로 이야기할 수 있습니다.",
        [day_id, f"{owner}.coverage", *(p["id"] for p in hidden),
               *(ref for _, ref, _ in markers)],
        owner, "가까운 관계에 바라는 것",
    )
    return [opening, month_entry, palace_entry]


def direction(result, owner, gender):
    other = "b" if owner == "a" else "a"
    ref = f"pair.{owner}.reads.{other}"
    role = result["evidence"][ref]["ten_god"]
    own_stem = result["charts"][owner]["day_master"]
    other_stem = result["charts"][other]["day_master"]
    palace = principal(result["contexts"][other], "day")
    palace_role = ten_god(own_stem, palace["stem"])
    tradition = PARTNER_ROLES.get(gender) if isinstance(gender, str) else None
    text = (f"{NAMES[owner]}는 {NAMES[other]}와 함께 지내며 {with_particle(ROLE_MEANING[role], '을', '를')} 눈여겨볼 수 있습니다. "
            f"{NAMES[owner]}의 {symbol(own_stem)}에서 바라보면 "
            f"{NAMES[other]}의 일간 {with_particle(symbol(other_stem), '은', '는')} {role}에 해당합니다.")
    refs = [ref, palace["id"]]
    if tradition:
        category, roles = tradition
        found = partner_placements(result, owner, other, roles)
        if role in roles:
            text += f" {with_particle(role, '은', '는')} 이 명식의 배우자성인 {category}에 속합니다."
        elif found:
            place, _, partner_role = found[0]
            text += (f" 배우자성을 나타내는 {with_particle(category, '은', '는')} "
                     f"상대의 {place}에서 {partner_role}에 해당합니다.")
        else:
            text += f" 상대의 확인된 글자에서는 이 방향의 배우자성인 {with_particle(category, '이', '가')} 드러나지 않습니다."
        refs += [f"{other}.coverage", *(source for _, source, _ in found)]
    if palace_role == "비견":
        text += (f" 상대의 배우자궁에도 {NAMES[owner]}의 일간과 같은 {with_particle(symbol(palace['stem']), '이', '가')} 있습니다. "
                 "상대가 익숙하게 해 온 일을 따라가다 보면 자기와 닮은 점을 발견할 수 있습니다.")
    else:
        text += (f" 상대의 배우자궁 속 {with_particle(symbol(palace['stem']), '은', '는')} 같은 방향에서 보면 {palace_role}입니다. "
                 f"둘만의 생활이 생긴 뒤에는 {ROLE_MEANING[palace_role]}도 중요해질 수 있습니다.")
    return paragraph(text, refs, heading=f"{NAMES[owner]}의 눈으로 본 {NAMES[other]}")


def interaction_places(fact):
    seats = STEM_SEAT if fact["layer"] == "stem" else BRANCH_SEAT
    places = [
        f"{NAMES[source['person']]}의 {seats[source['pillar']]} {symbol(source['symbol'])}"
        for source in fact["sources"]
    ]
    if len(places) == 2:
        return f"{places[0]}{particle(READINGS[fact['sources'][0]['symbol']], '과', '와')} {places[1]}"
    return ", ".join(places[:-1]) + f" 그리고 {places[-1]}"


def interaction_sentence(fact):
    places = interaction_places(fact)
    positions = {source["pillar"] for source in fact["sources"]}
    kind = fact["kind"]
    if len(positions) == 1:
        seat = SEAT[next(iter(positions))]
        scope = f"두 사람 모두 {with_particle(seat, '을', '를')} 이야기할 때 이 점을 떠올려 볼 만합니다."
    elif kind == "삼합" and positions == {"year", "month", "day"}:
        scope = "자라며 배운 방식이 지금 둘의 살림이나 가족 약속을 꾸리는 데 도움이 될 수 있습니다."
    elif "day" in positions:
        other = next(position for position in SEAT if position in positions and position != "day")
        scope = f"한 사람의 {with_particle(SEAT[other], '이', '가')} 상대에게는 둘 사이의 약속으로 받아들여질 수 있습니다."
    else:
        scope = "예전부터 각자 해 오던 방식이 무엇인지 말해 보면 함께할 때의 차이가 분명해집니다."
    if kind == "삼합":
        element = TRINE_ELEMENT[frozenset(source["symbol"] for source in fact["sources"])]
        evidence_text = f"{places}의 세 글자가 모여 {element}의 흐름을 이루는 삼합입니다."
    else:
        evidence_text = f"{places} 사이에 {with_particle(kind, '이', '가')} 있습니다."
    return f"{RELATIONS[kind]} {evidence_text} {scope}"


def analyze_preview(a, b, genders=None):
    result = analyze_pair(a, b)
    genders = genders or {}
    evidence = result["evidence"]
    contexts = result["contexts"]
    directions = [direction(result, owner, genders.get(owner)) for owner in NAMES]
    ranked = sorted(result["interactions"], key=lambda ref: (
        -sum(EDITORIAL_WEIGHT[s["pillar"]] for s in evidence[ref]["sources"]) / len(evidence[ref]["sources"]),
        -len(evidence[ref]["sources"]), ref,
    ))
    groups = {}
    for ref in ranked:
        fact = evidence[ref]
        positions = {s["pillar"] for s in fact["sources"]}
        layer = "palace" if positions == {"day"} and fact["layer"] == "branch" else (
            "month" if "month" in positions else "chart")
        groups.setdefault(layer, []).append(ref)

    relationship = directions[:]
    links = [entry["evidence_ids"][0] for entry in directions]
    roles = [evidence[ref]["ten_god"] for ref in links]
    palaces = [principal(context, "day") for context in contexts.values()]
    palace_refs = [p["id"] for p in palaces]
    palace_roles = [p["ten_god"] for p in palaces]
    mutual = all(
        isinstance(genders.get(owner), str)
        and roles[index] in PARTNER_ROLES.get(genders[owner], (None, ()))[1]
        for index, owner in enumerate(NAMES)
    )

    stems = [result["charts"][owner]["day_master"] for owner in NAMES]
    if mutual:
        categories = [PARTNER_ROLES[genders[owner]][0] for owner in NAMES]
        relationship.insert(0, paragraph(
            "두 사람은 각자가 배우자에게 바라는 모습을 상대에게서 발견하기 쉬운 궁합입니다. "
            f"첫째의 배우자성은 {categories[0]}이며 둘째의 일간 {with_particle(stem_with_element(stems[1]), '이', '가')} 그중 {roles[0]}에 해당합니다. "
            f"둘째의 배우자성은 {categories[1]}이며 첫째의 일간 {with_particle(stem_with_element(stems[0]), '이', '가')} {roles[1]}에 해당합니다. "
            "서로에게 어떤 점이 든든한지 말해 보면, 각자가 관계에서 소중하게 여기는 것도 자연스레 드러납니다.",
            links, heading="서로에게서 알아보는 배우자의 모습",
        ))
    if [p["stem"] for p in palaces] == stems[::-1]:
        branches = [symbol(result["charts"][owner]["pillars"]["day"][1]) for owner in NAMES]
        relationship.insert(int(mutual), paragraph(
            "두 사람이 가까워질수록 상대의 방식이 낯설지 않게 다가올 수 있습니다. "
            f"첫째의 배우자궁 {branches[0]}의 중심 글자는 둘째의 일간 {symbol(stems[1])}이고, "
            f"둘째의 배우자궁 {branches[1]}의 중심 글자는 첫째의 일간 {symbol(stems[0])}입니다. "
            "둘이 함께 일정을 챙기거나 집안일을 나눌 때, 상대가 무엇을 중요하게 여기는지 알아차리기 쉬운 접점입니다.",
            [*palace_refs, *links], heading="서로의 가까운 자리에 든 사람",
        ))
    months = [principal(contexts[owner], "month") for owner in NAMES]
    if all(month and month["ten_god"] == "식신" for month in months):
        relationship.append(paragraph(
            "마음을 행동으로 전하는 방식에서 두 사람이 서로를 이해하기 쉬운 면도 있습니다. "
            "두 명식 모두 태어난 달의 중심 글자가 일간을 기준으로 식신에 해당합니다. "
            "바쁜 날 음식을 챙겨 주거나 밀린 일을 거드는 작은 행동을 서로의 배려로 알아차릴 수 있습니다.",
            [*(month["id"] for month in months), "a.day.stem", "b.day.stem"],
            heading="마음을 행동으로 전하는 두 사람",
        ))

    palace_interactions = groups.get("palace", [])
    if not palace_interactions:
        a_branch, b_branch = [symbol(chart["pillars"]["day"][1]) for chart in result["charts"].values()]
        relationship.append(paragraph(
            "둘이 얼마나 쉽게 맞춰 가는지는 각자 살아온 방식까지 함께 살펴야 드러납니다. "
            f"두 배우자궁인 첫째의 {with_particle(a_branch, '과', '와')} 둘째의 {b_branch} 사이에는 직접 성립하는 합·충·형·해가 없습니다. "
            "함께 지낼 때 어떤 점이 편하고 어떤 점에 손이 가는지는 평소 집안일이나 약속을 다뤄 온 방식에서 실마리를 찾을 수 있습니다.",
            [*palace_refs, *links], heading="두 배우자궁을 나란히 놓으면",
        ))

    shown = set()
    for layer, heading in (
        ("palace", "두 배우자궁을 나란히 놓으면"),
        ("month", "태어난 달의 글자가 관계에 닿을 때"),
        ("chart", "다른 기둥에서 이어지는 관계"),
    ):
        selected = {}
        for ref in groups.get(layer, []):
            selected.setdefault(evidence[ref]["kind"], ref)
        for ref in selected.values():
            if ref in shown:
                continue
            fact = evidence[ref]
            seats = frozenset(s["source_id"] for s in fact["sources"])
            overlaps = [candidate for candidate in groups[layer] if candidate != ref
                        and (evidence[candidate]["kind"] in SUPPORT) != (fact["kind"] in SUPPORT)
                        and seats == frozenset(s["source_id"] for s in evidence[candidate]["sources"])]
            if overlaps:
                counterpart = overlaps[0]
                shared, strained = (ref, counterpart) if fact["kind"] in SUPPORT else (counterpart, ref)
                same_text = (
                    "뜻을 모으기는 쉬워도 구체적인 방법까지 같지는 않을 수 있습니다. "
                    f"{interaction_places(fact)}에는 {with_particle(evidence[shared]['kind'], '과', '와')} "
                    f"{with_particle(evidence[strained]['kind'], '이', '가')} 겹칩니다. "
                    "예를 들어 가족을 챙기자는 데 뜻이 맞아도, 얼마나 자주 찾아뵐지는 따로 상의할 일입니다."
                )
                if layer != "palace" and any(source["pillar"] == "day" for source in fact["sources"]):
                    same_text += (" 한 사람은 원래 해 오던 일이라고 생각해도, 다른 사람에게는 둘이 새로 정할 약속일 수 있습니다.")
                relationship.append(paragraph(same_text, [shared, strained],
                                              heading="한 자리에서 맞물리고 걸리는 두 힘"))
                shown.update((ref, counterpart))
            else:
                relationship.append(paragraph(interaction_sentence(fact), [ref], heading=heading))
                heading = None
                shown.add(ref)

    month_reads = []
    month_refs = []
    for owner, other in (("a", "b"), ("b", "a")):
        month = principal(contexts[other], "month")
        if month:
            god = ten_god(result["charts"][owner]["day_master"], month["stem"])
            month_reads.append(
                f"{NAMES[owner]}에게 {NAMES[other]}의 월지에 든 {with_particle(symbol(month['stem']), '은', '는')} "
                f"{god}에 해당하고, 이 자리에서는 {with_particle(ROLE_MEANING[god], '을', '를')} 살핍니다."
            )
            month_refs.extend((f"{owner}.day.stem", month["id"]))
    if month_reads:
        relationship.append(paragraph(
            "함께 지내 보면 상대에게 처음에는 몰랐던 면이 보일 수 있습니다. "
            + " ".join(month_reads)
            + " 각자 일이 몰린 날 어떻게 하루를 꾸리는지 이야기해 보면, 상대가 무엇을 먼저 챙기는지 알 수 있습니다.",
            month_refs, heading="함께 지내며 발견하는 면",
        ))

    support = next((ref for ref in ranked if evidence[ref]["kind"] in SUPPORT), None)
    tension = next((ref for ref in ranked if evidence[ref]["kind"] not in SUPPORT), None)
    refs = [ref for ref in (support, tension) if ref]
    if support and tension:
        summary = (
            "함께하고 싶은 일이 생기면 뜻을 모은 다음, 각자가 어디까지 맡을지도 확인해 볼 만합니다. "
            f"앞에서 살핀 {with_particle(evidence[support]['kind'], '과', '와')} "
            f"{with_particle(evidence[tension]['kind'], '이', '가')} 뜻을 모으는 부분과 손을 맞춰야 할 부분을 각각 보여 줍니다. "
            "같은 계획을 두고도 한 사람은 벌써 날짜를 정했다고 생각하고 다른 사람은 가능성을 검토 중일 수 있습니다."
        )
    elif support:
        summary = (
            "둘이 힘을 모을 때는 서로에게 어떤 도움이 반가웠는지 살펴볼 만합니다. "
            f"앞에서 본 {with_particle(evidence[support]['kind'], '이', '가')} 두 사람이 뜻을 이어 갈 실마리입니다. "
            "최근 같이 해낸 일 하나를 떠올리고 상대가 해 줘서 고마웠던 일을 말해 보세요."
        )
    elif tension:
        summary = (
            "의견이 자주 어긋나는 일이라면 각자 무엇을 지키려 했는지부터 들어볼 만합니다. "
            f"앞에서 본 {with_particle(evidence[tension]['kind'], '은', '는')} 익숙한 반응이 반복될 때 생기는 차이를 보여 줍니다. "
            "일정 하나를 두고도 한 사람은 시간을 아끼고 싶고 다른 사람은 여유를 남기고 싶을 수 있습니다."
        )
    else:
        summary = (
            "두 사람이 무엇을 반갑게 여기는지 각자의 입장에서 살펴볼 만합니다. "
            f"확인된 기둥에서 합·충·형·해가 두드러지지 않아 서로의 일간에서 본 {with_particle(roles[0], '과', '와')} {roles[1]}에 무게를 둡니다. "
            "상대가 최근 했던 말과 행동 중에 마음이 놓였던 순간을 서로 들려주어도 좋습니다."
        )
    relationship.append(paragraph(summary, [*refs, *links], heading="이 궁합에서 함께 읽을 것"))

    practice = [
        paragraph(
            "함께 결정을 내릴 때 서로 무엇을 중요하게 여기는지 먼저 물어보면 대화가 한결 쉬워집니다. "
            f"2장에서 살핀 첫째 쪽의 {with_particle(roles[0], '과', '와')} 둘째 쪽의 {with_particle(roles[1], '이', '가')} "
            "각자 어떤 질문부터 꺼내 볼지 실마리를 줍니다. "
            f"“{GOD_QUESTIONS[roles[0]]}”와 “{GOD_QUESTIONS[roles[1]]}”처럼, "
            "먼저 이렇게 물으면 같은 대답 안에 담긴 서로 다른 기대도 들을 수 있습니다.",
            links, heading="같은 결정에 담긴 두 사람의 뜻",
        ),
        paragraph(
            ("의견이 자주 어긋난다면 각자 어디까지 결정됐다고 생각하는지부터 맞춰 보세요. "
             f"앞에서 본 {with_particle(evidence[tension]['kind'], '은', '는')} 같은 일을 두고도 기준이 다를 수 있음을 보여 줍니다. "
             "날짜까지 정한 건지, 아직 갈 수 있는 날을 알아보는 중인지 한 문장으로 확인하면 됩니다. "
             if tension else
             "이미 둘이 뜻을 모았던 결정을 떠올려 보세요. 그때 어떤 말이 서로의 마음을 놓이게 했는지 이야기해 보세요. ")
            + ("부담이 적은 결정부터 이 방식으로 맞춰 볼 수 있습니다."
               if support else "다음 결정에서는 서로의 말에 어떤 뜻을 담았는지 한 번 더 확인해 보세요."),
            [*refs, *links], heading="함께 정했다는 감각",
        ),
        paragraph(
            "지금 함께 지킬 수 있는 작은 약속을 하나 골라 보세요. "
            f"두 배우자궁의 중심에서 살핀 {with_particle(palace_roles[0], '과', '와')} {palace_roles[1]}은 "
            "둘이 가까운 사이에 바라는 점을 돌아볼 단서입니다. "
            f"“{GOD_QUESTIONS[palace_roles[0]]}” “{GOD_QUESTIONS[palace_roles[1]]}” "
            "서로 답을 들어 보고 이번 주에 해 볼 수 있는 일로 좁혀도 충분합니다.",
            palace_refs, heading="지금의 두 사람에게 필요한 약속",
        ),
    ]
    report = [
        {"title": "각자의 명식과 관계의 바탕", "paragraphs": [
            entry for owner in NAMES for entry in natal(result, owner, genders.get(owner))
        ]},
        {"title": "두 명식이 만나는 자리", "paragraphs": relationship},
        {"title": "두 사람의 관계를 이어 가는 법", "paragraphs": practice},
    ]
    audit = review_report(report, evidence)
    if audit["unlinked_paragraphs"] or audit["unresolved_ids"]:
        raise RuntimeError("RS preview prose failed evidence review")
    scope = {owner: context["unresolved_pillars"] for owner, context in contexts.items()}
    for chapter in report:
        for entry in chapter["paragraphs"]:
            for ref in entry["evidence_ids"]:
                fact = evidence[ref]
                if any(source.get("pillar") in scope.get(source.get("person"), ())
                       for source in fact.get("sources", [fact])):
                    raise RuntimeError(f"Unresolved RS preview evidence: {ref}")
    preview = (f"두 명식에서 눈여겨볼 주제는 첫째의 관점에서 ‘{GOD_LENS[roles[0]]}’, "
               f"둘째의 관점에서 ‘{GOD_LENS[roles[1]]}’예요. 전체 리포트에서 각자의 명식과 두 사람의 접점을 이어서 읽을 수 있어요.")
    result.update(version="RS-preview-2", report=report, review=audit, preview_text=preview)
    return result

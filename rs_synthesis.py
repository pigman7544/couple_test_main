"""Compose the preview from confirmed natal and cross-chart evidence."""

from c06_narrative import particle
from compatibility_v11 import BRANCH_ELEMENTS, STEM_ELEMENTS, SUPPORT, ten_god
from compatibility_v12 import (
    EDITORIAL_WEIGHT, ELEMENT, GOD_LENS, GOD_QUESTIONS, READINGS,
    analyze_pair, review_report,
)
from engine import STEMS


NAMES = {"a": "첫째", "b": "둘째"}
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
RELATIONS = {
    "천간합": "겉으로 드러난 뜻이 서로 닿기 쉬운 자리예요.",
    "육합": "서로 다른 두 자리가 자연스럽게 맞물리는 관계를 뜻해요.",
    "삼합": "흩어진 세 자리가 오행의 한 흐름으로 모이는 관계예요.",
    "육충": "서로 마주한 두 글자가 만나 익숙한 방향에 변화를 일으키는 관계예요.",
    "상형": "서로의 기준이 걸리면서 같은 문제를 거듭 조율하기 쉬운 관계예요.",
    "삼형": "세 자리의 기대가 얽혀 어느 한쪽의 방식만 바꾸어도 풀기 어려운 관계예요.",
    "자형": "같은 글자의 반응이 되풀이되며 긴장이 깊어질 수 있는 관계예요.",
    "육해": "한쪽의 뜻과 다른 쪽이 받아들이는 뜻 사이에 틈이 생길 수 있는 관계예요.",
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
    polarity = "음" if STEMS.index(stem) % 2 else "양"
    day_id = f"{owner}.day.stem"
    palace = principal(context, "day")
    month = principal(context, "month")
    basics = [f"{owner}.{position}.stem" for position in chart["details"]]
    branches = [p for p in context["placements"] if p["tier"] == "본기"]
    main_elements = [STEM_ELEMENTS[d["stem"]] for d in chart["details"].values()]
    main_elements.extend(BRANCH_ELEMENTS[d["branch"]] for d in chart["details"].values())
    count = main_elements.count(element)
    orientation = (
        f"확정된 글자 가운데 {ELEMENT[element]}의 성질을 대표하는 자리가 {count}곳이에요. "
        "같은 성질이 명식 어디에 놓였는지는 달과 날의 글자를 차례로 보면 드러나요."
        if count > 1 else
        f"겉으로 드러난 {ELEMENT[element]}의 자리는 일간 하나예요. "
        "그 성질이 어디서 힘을 얻고 어디에 쓰이는지는 주변 글자를 함께 읽어야 알 수 있어요."
    )
    lead = (
        f"태어난 날의 앞 글자, 곧 일간부터 볼게요. 첫째는 {symbol(stem)} 일간이에요."
        if owner == "a" else
        f"{NAMES[owner]}의 명식은 태어난 날의 앞 글자인 {symbol(stem)}에서 읽기 시작해요."
    )
    opening = paragraph(
        f"{lead} {polarity}의 {ELEMENT[element]}에 속하는 이 글자는 전통 명리에서 "
        f"{ELEMENT_STYLE[element]}으로 풀이해요. {orientation}",
        [*basics, *(p["id"] for p in branches)], owner, "태어난 날의 글자",
    )

    if month:
        season = context["month_command"]
        role = month["ten_god"]
        support = (
            "계절을 나타내는 글자에도 일간과 같은 성질이 실려 있어요."
            if season["same_element"] else
            "계절의 오행은 일간에 힘을 보태는 쪽으로 읽혀요."
            if season["generates_day_master"] else
            f"일간의 {ELEMENT[element]} 기운은 이 달의 {ELEMENT[season['branch_element']]} 기운 속에서 읽어요."
        )
        hidden = [p for p in context["placements"] if p["pillar"] == "month"]
        layers = ""
        if hidden[1:]:
            layers = (" 이 글자에 깃든 다른 기운, 즉 지장간도 함께 보면 "
                      f"{hidden_text(hidden[1:])}도 보여요. "
                      f"그중 {hidden[1]['ten_god']}에는 {ROLE_MEANING[hidden[1]['ten_god']]}도 담겨 있어요.")
        if month["exposed_at"]:
            layers += " 달의 중심 기운은 명식의 앞 글자에도 한 번 더 나타나요."
        month_entry = paragraph(
            f"태어난 달의 뒤 글자인 월지는 {season['season']}의 {symbol(season['branch'])}예요. {support} "
            f"그 속에 든 {symbol(month['stem'])}에서 일간을 기준으로 {role}의 뜻을 읽어요. "
            f"평소 생활이나 일을 꾸려 가는 방식에서는 {with_particle(ROLE_MEANING[role], '을', '를')} 눈여겨볼 만해요."
            f"{layers}", [day_id, *(p["id"] for p in hidden), *month["exposed_at"]],
            owner, "태어난 계절과 평소의 모습",
        )
    else:
        month_entry = paragraph(
            "태어난 날이 절기가 바뀌는 때와 겹쳐 월주에 두 후보가 있어요. "
            "계절에 따른 풀이는 시각을 알 때까지 보류하고, 확인된 날의 글자로 가까운 관계를 살펴볼게요.",
            [day_id, f"{owner}.coverage"], owner, "절기가 바뀌는 날",
        )

    hidden = [p for p in context["placements"] if p["pillar"] == "day"]
    role = palace["ten_god"]
    branch = symbol(chart["pillars"]["day"][1])
    text = (
        f"태어난 날의 뒤 글자인 일지는 가까운 관계를 살피는 자리라 배우자궁이라고 불러요. "
        f"{branch}에 든 {symbol(palace['stem'])}에서 읽는 십성, 곧 일간과 맺는 관계의 이름은 {with_particle(role, '이에요', '예요')}. "
        f"가까이 지내는 사이에서 {with_particle(ROLE_MEANING[role], '을', '를')} 소중하게 여길 수 있다는 뜻이에요."
    )
    if hidden[1:]:
        other_role = hidden[1]["ten_god"]
        text += (f" 이 자리에는 {hidden_text(hidden[1:])}도 들어 있어요. "
                 f"{ROLE_MEANING[other_role]}도 친밀함을 이루는 한 부분이 될 수 있어요.")
    tradition = PARTNER_ROLES.get(gender) if isinstance(gender, str) else None
    markers = []
    if tradition:
        category, roles = tradition
        markers = partner_placements(result, owner, owner, roles)
        if role in roles:
            text += (f" 전통 명리에서 배우자를 상징하는 글자를 배우자성이라 해요. "
                     f"이 명식에서는 {with_particle(category, '을', '를')} 배우자성으로 보는데, 배우자궁의 중심에 바로 그 {with_particle(role, '이', '가')} 자리해요.")
        elif markers:
            text += (f" 이 명식에서 배우자를 상징하는 {with_particle(category, '은', '는')} "
                     f"{markers[0][0]}에서 {markers[0][2]}에 해당해요. 배우자궁은 가까운 사이에 무엇을 바라는지, "
                     "배우자성은 어떤 관계의 성질을 반기는지 살피는 데 쓰여요.")
        else:
            text += f" 확인된 글자에는 전통적으로 배우자성을 뜻하는 {with_particle(category, '이', '가')} 드러나지 않아요."
    palace_entry = paragraph(
        text, [day_id, f"{owner}.coverage", *(p["id"] for p in hidden),
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
    text = (f"{NAMES[owner]}의 {symbol(own_stem)}에서 바라보면 "
            f"{NAMES[other]}의 일간 {with_particle(symbol(other_stem), '은', '는')} {role}에 해당해요. "
            f"이 글자에서 읽는 관계의 성질은 {with_particle(ROLE_MEANING[role], '이에요', '예요')}.")
    refs = [ref, palace["id"]]
    if tradition:
        category, roles = tradition
        found = partner_placements(result, owner, other, roles)
        if role in roles:
            text += f" {with_particle(role, '은', '는')} 이 명식의 배우자성인 {category}에 속해요."
        elif found:
            place, _, partner_role = found[0]
            text += (f" 배우자성을 나타내는 {with_particle(category, '은', '는')} 상대의 {place}에서 {partner_role}에 해당해요. "
                     "상대의 첫인상에 가까운 일간과 함께, 그 글자가 놓인 자리도 살펴야 해요.")
        else:
            text += f" 상대의 확인된 글자에서는 이 방향의 배우자성인 {with_particle(category, '이', '가')} 드러나지 않아요."
        refs += [f"{other}.coverage", *(source for _, source, _ in found)]
    if palace_role == "비견":
        text += (f" 한편 상대의 배우자궁에 든 {with_particle(symbol(palace['stem']), '은', '는')} {NAMES[owner]}의 일간과 같은 글자예요. "
                 "전통 명리에서 비견이라고 부르는 관계로, 서로 가까이 지낼 때 상대에게서 익숙한 면을 발견할 수 있다는 풀이예요.")
    else:
        text += (f" 상대의 배우자궁 속 {with_particle(symbol(palace['stem']), '은', '는')} 같은 방향에서 보면 {with_particle(palace_role, '이에요', '예요')}. "
                 f"가까이 지내는 과정에서는 {ROLE_MEANING[palace_role]}도 눈여겨볼 만해요.")
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


def interaction_meaning(fact):
    if fact["kind"] == "삼합":
        element = TRINE_ELEMENT[frozenset(source["symbol"] for source in fact["sources"])]
        return f"세 글자가 만나 {element}의 흐름을 이루는 자리예요."
    return RELATIONS[fact["kind"]]


def interaction_sentence(fact):
    places = interaction_places(fact)
    positions = {source["pillar"] for source in fact["sources"]}
    kind = fact["kind"]
    if len(positions) == 1:
        seat = SEAT[next(iter(positions))]
        scope = f"두 사람 모두에게 {with_particle(seat, '과', '와')} 관련된 자리예요."
    elif kind == "삼합" and positions == {"year", "month", "day"}:
        scope = ("오래 익힌 관계의 틀이 상대의 생활 방식과 배우자궁에 이어져요. "
                 "가까운 사이에서 뜻을 모으는 데 두 사람 각자의 배경도 한몫할 수 있다는 풀이예요.")
    elif "day" in positions:
        other = next(position for position in SEAT if position in positions and position != "day")
        scope = f"{with_particle(SEAT[other], '이', '가')} 상대의 배우자궁에 닿는 구조예요."
    else:
        scope = "이 작용은 두 사람이 각자 익혀 온 방식이 만나는 자리에서 살펴볼 수 있어요."
    return (f"{places} 사이에서는 {kind}을 살펴요. " if kind != "육해" else
            f"{places} 사이에는 육해가 성립해요. ") + f"{interaction_meaning(fact)} {scope}"


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

    if mutual and roles == ["정재", "정관"]:
        relationship.append(paragraph(
            "두 사람은 상대를 대표하는 글자에서 각자의 배우자성을 마주해요. "
            "첫째 쪽의 정재가 함께 감당할 수 있는 몫에 마음을 둔다면, 둘째 쪽의 정관은 그 몫을 나누는 약속이 "
            "서로에게 같은 뜻인지 살펴요. 서로에게 기대하는 것이 서로를 향해 있는 구조예요. 다만 "
            "첫째에게 충분히 책임을 다한 일도 둘째에게는 아직 뜻을 확인할 일로 남을 수 있어요.",
            links, heading="서로에게서 알아보는 배우자의 모습",
        ))

    palace_interactions = groups.get("palace", [])
    if not palace_interactions:
        a_branch, b_branch = [symbol(chart["pillars"]["day"][1]) for chart in result["charts"].values()]
        opening = (
            "서로의 일간에서 배우자성을 읽었다면, 이제 가까운 관계의 자리를 나란히 놓을 차례예요. "
            if mutual else "상대를 대표하는 일간을 살폈으니 이제 두 배우자궁을 나란히 놓아 볼게요. "
        )
        relationship.append(paragraph(
            opening + f"첫째의 {with_particle(a_branch, '과', '와')} 둘째의 {b_branch} 사이에는 직접 성립하는 합·충·형·해가 없어요. "
            "두 사람이 가까워졌을 때의 모습은 각 배우자궁에 담긴 기대와, 그 자리에 상대의 다른 글자가 어떻게 닿는지를 함께 봐야 드러나요.",
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
                    f"{interaction_places(fact)}에는 {evidence[shared]['kind']}과 {evidence[strained]['kind']}이 겹쳐요. "
                    "함께 움직이게 하는 힘과 서로의 기준을 자꾸 되묻게 하는 힘이 한곳에서 나와요. "
                    "쉽게 뜻이 통하는 사이일수록, 둘이 같은 방식에 동의했다고 여기기 쉬운 자리이기도 해요."
                )
                if layer != "palace" and any(source["pillar"] == "day" for source in fact["sources"]):
                    same_text += (" 한 사람에게는 오래 써 온 방식이 다른 사람에게는 둘만의 관계에 관한 약속처럼 "
                                  "들릴 수 있다는 점에서, 이 겹침이 특히 중요해요."
                                  if any(source["pillar"] == "year" for source in fact["sources"]) else
                                  " 한 사람의 배우자궁이 걸린 만큼, 방식의 차이가 친밀함에 대한 기대까지 건드릴 수 있어요.")
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
                f"{god}에 해당해요. 상대가 평소 살아가는 방식에서 "
                f"{with_particle(ROLE_MEANING[god], '을', '를')} 발견할 수 있는 자리예요."
            )
            month_refs.extend((f"{owner}.day.stem", month["id"]))
    if month_reads:
        relationship.append(paragraph(
            " ".join(month_reads) + " 일간에서 서로를 알아보는 이유와, 함께 지내며 상대에게서 새로 발견하는 면이 "
            "어떻게 이어지는지 이 두 방향에서 살펴볼 수 있어요.",
            month_refs, heading="함께 지내며 발견하는 면",
        ))

    support = next((ref for ref in ranked if evidence[ref]["kind"] in SUPPORT), None)
    tension = next((ref for ref in ranked if evidence[ref]["kind"] not in SUPPORT), None)
    refs = [ref for ref in (support, tension) if ref]
    if support and tension:
        summary = (
            f"앞에서 본 {with_particle(evidence[support]['kind'], '과', '와')} "
            f"{with_particle(evidence[tension]['kind'], '을', '를')} 함께 놓고 보면, "
            "한 관계 안에서도 마음이 통하는 자리와 기준을 조율해야 하는 자리가 함께 보여요. "
            "서로 뜻을 모은 순간을 떠올릴 때, 그 뜻에 두 사람이 같은 기대를 담았는지도 돌아볼 만해요."
        )
    elif support:
        summary = (
            f"확인된 {with_particle(evidence[support]['kind'], '은', '는')} 서로 뜻을 이어 갈 자리를 보여 줘요. "
            f"그 자리에서 첫째가 눈여겨볼 것은 {ROLE_MEANING[roles[0]]}, "
            f"둘째가 살펴볼 것은 {with_particle(ROLE_MEANING[roles[1]], '이에요', '예요')}. "
            "같은 방향을 바라볼 때 서로 무엇을 반가워하는지도 헤아려 보세요."
        )
    elif tension:
        summary = (
            f"확인된 {with_particle(evidence[tension]['kind'], '은', '는')} 익숙한 반응을 그대로 주고받을 때 기준이 어긋날 수 있음을 보여 줘요. "
            f"그때 첫째가 지키고 싶은 것은 {ROLE_MEANING[roles[0]]}, "
            f"둘째에게 의미가 있는 것은 {ROLE_MEANING[roles[1]]}에 닿아 있을 수 있어요. "
            "엇갈린 의견 뒤에 무엇을 지키려는 마음이 있었는지 살필 자리예요."
        )
    else:
        summary = (
            f"확인된 기둥에서 합·충·형·해를 찾기 어려울 때는 서로가 상대에게서 읽는 뜻에 무게를 둬요. "
            f"첫째는 {ROLE_MEANING[roles[0]]}에, 둘째는 {ROLE_MEANING[roles[1]]}에 마음이 갈 수 있어요."
        )
    relationship.append(paragraph(summary, [*refs, *links], heading="이 궁합에서 함께 읽을 것"))

    practice = [
        paragraph(
            f"첫째가 둘째에게서 읽은 {with_particle(roles[0], '과', '와')} 둘째가 첫째에게서 읽은 {with_particle(roles[1], '은', '는')} "
            "서로에게 어떤 점을 바라는지 대화를 시작할 실마리가 돼요. "
            "함께 내리는 결정에서 서로의 뜻을 한 문장씩 들어 보세요. "
            f"“{GOD_QUESTIONS[roles[0]]}”와 “{GOD_QUESTIONS[roles[1]]}”처럼, "
            "각자가 중요하게 여기는 점부터 물으면 같은 대답 속에 담긴 서로 다른 기대도 들을 수 있어요.",
            links, heading="같은 결정에 담긴 두 사람의 뜻",
        ),
        paragraph(
            (f"두 명식의 {evidence[tension]['kind']}에서 살핀 엇갈림이 반복된다면, "
             "누가 결론을 내리기 전에 각자 어디까지 결정됐다고 생각했는지 맞춰 보세요. "
             "서로의 동의가 필요한 범위를 먼저 정하면 무엇을 더 이야기할지 분명해져요. "
             if tension else
             "이미 둘이 뜻을 모았던 결정을 떠올려 보세요. 그때 어떤 말이 서로의 마음을 놓이게 했는지 이야기해 보세요. ")
            + ("함께 뜻을 모으기 쉬운 자리에서부터 이 합의를 실천해 보면, 둘이 함께 감당할 수 있는 범위가 조금씩 선명해질 거예요."
               if support else "다음 결정에서는 서로의 말에 어떤 뜻을 담았는지 한 번 더 확인해 보세요."),
            [*refs, *links], heading="함께 정했다는 감각",
        ),
        paragraph(
            "둘만의 관계에 무엇이 필요한지는 당사자의 말에서 가장 잘 드러나요. "
            f"첫째의 배우자궁에 담긴 {ROLE_MEANING[palace_roles[0]]}, "
            f"둘째의 배우자궁에 담긴 {ROLE_MEANING[palace_roles[1]]} 가운데 "
            "지금 우리에게 더 필요한 것이 무엇인지 물어보세요. 서로의 답을 듣고 두 사람이 함께 지킬 약속을 하나만 골라도 충분해요.",
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

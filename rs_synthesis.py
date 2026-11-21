"""Compose the preview from confirmed natal and cross-chart evidence."""

from collections import Counter

from compatibility_editorial_round3 import READINGS as ROLE_READINGS
from compatibility_v11 import BRANCH_ELEMENTS, STEM_ELEMENTS, SUPPORT, ten_god
from compatibility_v12 import (
    EDITORIAL_WEIGHT, ELEMENT, GOD_LENS, POSITION, READINGS,
    analyze_pair, review_report,
)
from engine import STEMS


NAMES = {"a": "첫째", "b": "둘째"}
ELEMENT_STYLE = {
    "wood": "새 방향을 세우고 키우는 힘",
    "fire": "뜻을 드러내고 반응을 주고받는 힘",
    "earth": "여러 조건을 받아들여 자리를 잡는 힘",
    "metal": "기준을 세우고 경계를 가르는 힘",
    "water": "상황을 살피고 흐름에 맞춰 움직이는 힘",
}
RELATIONS = {
    "천간합": "겉으로 드러난 의도에서 접점을 찾기 쉬운 단서",
    "육합": "두 자리가 익숙한 방식으로 손발을 맞추는 단서",
    "삼합": "세 자리가 함께 움직일 때 공통 방향이 생기는 단서",
    "육충": "각자 당연하게 여긴 리듬이 맞부딪히는 단서",
    "상형": "처리 순서나 기준을 몇 번이고 확인하게 되는 단서",
    "삼형": "여러 기대가 얽혀 한 조건만 바꿔서는 풀리기 어려운 단서",
    "자형": "비슷한 반응이 거듭되면서 긴장이 높아질 수 있는 단서",
    "육해": "의도와 받아들이는 뜻이 조용히 어긋날 수 있는 단서",
}
PARTNER_ROLES = {
    "male": ("재성", {"정재", "편재"}),
    "female": ("관성", {"정관", "편관"}),
}


def symbol(value):
    return f"{READINGS[value]}({value})"


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


def distribution(owner, chart):
    counts = Counter()
    for detail in chart["details"].values():
        counts[STEM_ELEMENTS[detail["stem"]]] += 1
        counts[BRANCH_ELEMENTS[detail["branch"]]] += 1
    summary = " · ".join(f"{label} {counts[key]}" for key, label in ELEMENT.items())
    return f"{NAMES[owner]}의 확정 기둥을 천간과 지지의 대표 오행으로 세면 {summary}이에요."


def natal(result, owner, gender):
    context = result["contexts"][owner]
    chart = result["charts"][owner]
    name = NAMES[owner]
    stem = chart["day_master"]
    element = STEM_ELEMENTS[stem]
    polarity = "음" if STEMS.index(stem) % 2 else "양"
    day_id = f"{owner}.day.stem"
    palace = principal(context, "day")
    month = principal(context, "month")
    confirmed = [f"{owner}.{position}.stem" for position in chart["details"]]
    counts = distribution(owner, chart)
    opening = paragraph(
        f"{name}의 일간은 {symbol(stem)}, {polarity}에 속하는 {ELEMENT[element]} 오행이에요. "
        f"일간은 다른 글자가 나에게 어떤 작용을 하는지 읽는 기준이에요. "
        f"전통 명리는 이 오행을 ‘{ELEMENT_STYLE[element]}’이라는 상징으로 읽어요. "
        f"{counts} 계절과 지장간에 따라 같은 오행도 작용의 무게가 달라져요.",
        [*confirmed, *(p["id"] for p in context["placements"] if p["tier"] == "본기")],
        owner, "일간과 오행",
    )
    if month:
        season = context["month_command"]
        branch = symbol(season["branch"])
        role = month["ten_god"]
        link = ("일간과 같은 오행의 계절 바탕이 있어요." if season["same_element"]
                else "월지의 오행이 일간의 오행을 북돋우는 흐름이에요." if season["generates_day_master"]
                else f"일간의 {ELEMENT[element]} 기질은 이 계절의 {ELEMENT[season['branch_element']]} 환경 속에서 드러나요.")
        hidden = [p for p in context["placements"] if p["pillar"] == "month"]
        secondary = [f"{symbol(p['stem'])}({p['ten_god']})" for p in hidden[1:]]
        extra = f" 그 안에는 {'·'.join(secondary)}도 함께 있어요." if secondary else ""
        exposed = (" 이 본기가 천간에도 보여 안팎에서 반복돼요." if month["exposed_at"]
                   else " 이 본기는 지지 안에서 계절의 바탕을 이뤄요.")
        month_entry = paragraph(
            f"{name}의 월지는 {season['season']}의 {branch}예요. {link} "
            f"월지 안의 중심 글자 {symbol(month['stem'])}에 해당하는 십성은 ‘{role}’로 분류해요. "
            f"일이나 생활의 틀에서는 ‘{ROLE_READINGS[role][0]}’을 중요하게 보는 자리로 읽어요."
            f"{exposed}{extra}", [day_id, *(p["id"] for p in hidden), *month["exposed_at"]],
            owner, "월지와 생활의 리듬",
        )
    else:
        month_entry = paragraph(
            f"{name}의 월주는 절기 경계에서 후보가 갈려요. 계절을 하나로 정해 기질의 강약을 판단하기 어려워서, "
            "가까운 관계에 관한 해석은 확정된 일주에서 시작해요.",
            [day_id, f"{owner}.coverage"], owner, "월주가 열려 있는 경우",
        )
    role = palace["ten_god"]
    palace_branch = symbol(chart["pillars"]["day"][1])
    hidden = [p for p in context["placements"] if p["pillar"] == "day"]
    secondary = "·".join(f"{symbol(p['stem'])}({p['ten_god']})" for p in hidden[1:])
    qualification = (f" 여기에는 {secondary}도 들어 있어 가까운 사이에 기대하는 바를 한 가지로 줄이기 어려워요."
                     if secondary else "")
    tradition = PARTNER_ROLES.get(gender) if isinstance(gender, str) else None
    roles = tradition[1] if tradition else set()
    markers = [p for p in context["placements"] if p["ten_god"] in roles]
    visible = [(position, detail["stem"], ten_god(stem, detail["stem"]))
               for position, detail in chart["details"].items()
               if ten_god(stem, detail["stem"]) in roles]
    if tradition:
        places = [f"{POSITION[position]} 천간 {symbol(value)}({god})" for position, value, god in visible]
        places += [f"{POSITION[p['pillar']]} 지장간 {symbol(p['stem'])}({p['ten_god']})" for p in markers]
        presence = (f" {', '.join(places)}에서 그 단서를 읽어요." if places
                    else " 확정된 천간과 지장간에서는 이에 해당하는 글자가 드러나지 않아요.")
        partner = f" 전통 방식에서 {name}의 배우자성은 {tradition[0]}으로 살펴요.{presence}"
    else:
        partner = ""
    palace_entry = paragraph(
        f"가까운 관계의 자리를 뜻하는 {name}의 일지, 곧 배우자궁은 {palace_branch}예요. "
        f"그 중심 글자인 {symbol(palace['stem'])}에서 십성 ‘{role}’의 의미를 읽어요. 가까운 사람과 지낼 때 "
        f"‘{ROLE_READINGS[role][0]}’에 마음이 갈 수 있어요.{qualification}{partner}",
        [day_id, f"{owner}.coverage", *(p["id"] for p in [*hidden, *markers]),
         *(f"{owner}.{position}.stem" for position, _, _ in visible)],
        owner, "일지와 가까운 관계에서의 기대",
    )
    return [opening, month_entry, palace_entry]


def direction(result, owner, gender):
    evidence = result["evidence"]
    other = "b" if owner == "a" else "a"
    ref = f"pair.{owner}.reads.{other}"
    role = evidence[ref]["ten_god"]
    chart = result["charts"][other]
    palace = principal(result["contexts"][other], "day")
    palace_role = ten_god(result["charts"][owner]["day_master"], palace["stem"])
    tradition = PARTNER_ROLES.get(gender) if isinstance(gender, str) else None
    roles = tradition[1] if tradition else set()
    found = [
        (f"{POSITION[position]} 천간 {symbol(detail['stem'])}", f"{other}.{position}.stem", god)
        for position, detail in chart["details"].items()
        if (god := ten_god(result["charts"][owner]["day_master"], detail["stem"])) in roles
    ]
    found += [
        (f"{POSITION[p['pillar']]} 지장간 {symbol(p['stem'])}", p["id"], god)
        for p in result["contexts"][other]["placements"]
        if (god := ten_god(result["charts"][owner]["day_master"], p["stem"])) in roles
    ]
    text = (f"{NAMES[owner]}의 일간에서 {NAMES[other]}의 일간인 {symbol(chart['day_master'])}에 어떤 십성이 대응하는지 보면 ‘{role}’에 해당해요. "
            f"두 사람이 직접 주고받는 관계에서는 {GOD_LENS[role]}이 화두가 될 수 있어요. "
            f"상대의 일지에 든 중심 글자 {symbol(palace['stem'])}에서 ‘{palace_role}’의 의미가 읽혀, "
            f"가까이 지낼 때는 {GOD_LENS[palace_role]}도 함께 중요해질 수 있어요.")
    refs = [ref, palace["id"]]
    if tradition:
        matches = ", ".join(f"{place}({god})" for place, _, god in found)
        if role in roles:
            text += f" 상대의 일간부터 {NAMES[owner]}의 배우자성인 {tradition[0]}에 해당해요."
        elif found:
            text += f" {NAMES[owner]}의 배우자성인 {tradition[0]}은 상대의 확정 명식 중 {matches}에서 읽혀요."
        else:
            text += f" 상대의 확정 기둥에서는 {NAMES[owner]}의 배우자성인 {tradition[0]}을 직접 읽을 자리가 확인되지 않아요."
        refs += [f"{other}.coverage", *(source for _, source, _ in found)]
    return paragraph(text, refs, heading=f"{NAMES[owner]}의 눈으로 본 {NAMES[other]}")


def interaction_name(fact):
    places = []
    for source in fact["sources"]:
        position = source["pillar"]
        seat = (POSITION[position] if fact["layer"] == "stem"
                else {"year": "연지", "month": "월지", "day": "일지", "hour": "시지"}[position])
        places.append(f"{NAMES[source['person']]} {seat} {symbol(source['symbol'])}")
    return " · ".join(places) + f"의 {fact['kind']}"


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
    for layer, heading, focus in (
        ("palace", "두 배우자궁이 만나는 자리", "가까운 사이의 기본 리듬"),
        ("month", "월지에서 만나는 생활 조건", "일상에서 각자 익숙하게 써 온 방식"),
        ("chart", "나머지 확정 기둥의 작용", "두 사람 사이에 겹쳐 작용할 수 있는 조건"),
    ):
        refs = groups.get(layer, [])
        if layer == "palace" and not refs:
            palace_refs = [principal(context, "day")["id"] for context in contexts.values()]
            branches = [symbol(chart["pillars"]["day"][1]) for chart in result["charts"].values()]
            relationship.append(paragraph(
                f"첫째의 배우자궁에 든 글자는 {branches[0]}, 둘째의 배우자궁에 든 글자는 {branches[1]}예요. 이 두 일지만 직접 놓았을 때 "
                "계산 기준에 해당하는 지지 합·충·형·해는 없어요. 두 사람이 가까워지는 방식은 "
                "각 일지 안의 십성과 다른 기둥이 이어 주는 자리까지 살펴야 윤곽이 보여요.",
                palace_refs, heading=heading))
        elif refs:
            selected = {}
            for ref in refs:
                selected.setdefault(evidence[ref]["kind"], ref)
            parts = [f"{interaction_name(evidence[ref])}에서는 {RELATIONS[kind]}를 살펴요."
                     for kind, ref in selected.items()]
            relationship.append(paragraph(f"이 자리에서 살피는 주제는 {focus}이에요. " + " ".join(parts),
                                          selected.values(), heading=heading))

    month_reads = []
    month_refs = []
    for owner, other in (("a", "b"), ("b", "a")):
        month = principal(contexts[other], "month")
        if month:
            god = ten_god(result["charts"][owner]["day_master"], month["stem"])
            month_reads.append(
                f"{NAMES[owner]}의 일간에서 본 {NAMES[other]} 월지의 중심 글자 {symbol(month['stem'])}에서 "
                f"‘{god}’을 읽어요. 상대의 평소 생활 방식을 이해하는 데 ‘{GOD_LENS[god]}’라는 주제가 따라와요."
            )
            month_refs.extend((f"{owner}.day.stem", month["id"]))
    if month_reads:
        relationship.append(paragraph(
            " ".join(month_reads) + " 일간끼리 읽은 관계와 함께 놓으면 서로에게 기대하는 역할이 "
            "평소 생활에서 어떤 조건을 만나는지 살펴볼 수 있어요.",
            month_refs, heading="상대의 월지와 지장간을 읽으면",
        ))

    support = next((ref for ref in ranked if evidence[ref]["kind"] in SUPPORT), None)
    tension = next((ref for ref in ranked if evidence[ref]["kind"] not in SUPPORT), None)
    shared_support = {}
    for ref in sorted(ranked, key=lambda ref: evidence[ref]["kind"] not in SUPPORT):
        fact = evidence[ref]
        if fact["kind"] in SUPPORT:
            shared_support.setdefault(tuple(s["source_id"] for s in fact["sources"]), ref)
        else:
            same_seats = tuple(s["source_id"] for s in fact["sources"])
            if same_seats in shared_support:
                shared = shared_support[same_seats]
                relationship.append(paragraph(
                    f"{interaction_name(evidence[shared])}과 {fact['kind']}이 같은 자리에 겹쳐요. "
                    "처음 손발을 맞추기는 쉬워도, 한 번 통했던 기준을 다음에도 그대로 쓰기로 했는지는 별개예요. "
                    "특히 한쪽의 일지가 걸린 경우에는 다른 자리에서 자연스럽던 방식도 가까운 사이에서 조정이 필요할 수 있어요."
                    if any(s["pillar"] == "day" for s in fact["sources"]) else
                    f"{interaction_name(evidence[shared])}과 {fact['kind']}이 같은 자리에 겹쳐요. "
                    "함께 움직일 방향이 정해진 뒤에도 맡는 범위와 결정 순서는 다시 맞춰 볼 만해요.",
                    [shared, ref], heading="같은 자리에 겹치는 협력과 긴장",
                ))
                break
    refs = [ref for ref in (support, tension) if ref]
    roles = [evidence["pair.a.reads.b"]["ten_god"], evidence["pair.b.reads.a"]["ten_god"]]
    links = [entry["evidence_ids"][0] for entry in directions]
    focus = "첫째에게는 " + GOD_LENS[roles[0]] + ", 둘째에게는 " + GOD_LENS[roles[1]]
    if support and tension:
        summary = (f"{interaction_name(evidence[support])}이 두 사람의 협력 가능성을 보여 주고, "
                   f"{interaction_name(evidence[tension])}은 그 협력 안에서도 맞춰 갈 조건을 짚어 줘요. "
                   "뜻을 모으기 쉬운 일에서도 둘이 기대하는 방법이나 부담이 같은지는 따로 살펴볼 만해요.")
    elif support:
        summary = (f"확정 명식에서 {interaction_name(evidence[support])}이 접점을 만들어요. "
                   f"그 접점을 오래 쓰려면 각자 무엇을 중요하게 여기는지도 살펴보세요. {focus}에 주목할 수 있어요.")
    elif tension:
        summary = (f"{interaction_name(evidence[tension])}은 조율이 필요한 자리를 보여 줘요. "
                   f"그 자리에서 대화의 실마리를 찾는다면 {focus}에 관해 묻는 데서 시작해 보세요.")
    else:
        summary = f"두 사람을 잇는 확정된 합충형해보다 각자의 관점에서 읽은 십성이 해석의 출발점이에요. 함께 다뤄 볼 주제는 {focus}이에요."
    relationship.append(paragraph(summary, [*refs, *links], heading="강점과 긴장을 함께 읽으면"))

    practice = [
        paragraph(
            f"관계에서 중요해질 수 있는 조건을 한 문장씩 적으면 첫째는 ‘{ROLE_READINGS[roles[0]][0]}’, 둘째는 ‘{ROLE_READINGS[roles[1]][0]}’이에요. "
            "함께 정할 일이 생기면 어떤 결론을 원하는지와 어떤 방식으로 결정하고 싶은지를 한 번씩 말해 보세요. "
            "결론은 같은데 절차에서 의견이 갈리는지, 각자가 기대하는 결과부터 다른지 가늠할 수 있어요.",
            links, heading="각자가 중요하게 여기는 조건을 말해요",
        ),
        paragraph(
            (f"의견이 엇갈릴 때는 {interaction_name(evidence[tension])}에서 살핀 조율의 지점을 떠올려 보세요. "
             "서로 바꾸기 어려운 조건을 하나만 남기고, 둘 다 감당할 수 있는 범위를 찾아 보세요. "
             if tension else
             "평소 합의하기 쉬운 일 하나를 골라 누가 무엇을 맡았을 때 편했는지 되짚어 보세요. ")
            + (f"{interaction_name(evidence[support])}에서 읽은 접점이 실제로 어떤 도움을 주는지 확인할 기회예요. "
               if support else "상대의 제안을 자기 쪽 부담으로만 받아들이고 있었는지도 살필 수 있어요. ")
            + "한 번 시도한 뒤 누구에게 수고가 더 갔는지 확인하고, 다음번에 조정할 항목 하나를 정해 보세요.",
            [*refs, *links], heading="한 가지 조건을 바꾸고 다시 살펴요",
        ),
        paragraph(
            "가까운 관계에서는 도움을 건네는 방식과 도움으로 받아들이는 방식이 다를 수 있어요. "
            f"첫째의 배우자궁에서 읽은 ‘{GOD_LENS[principal(contexts['a'], 'day')['ten_god']]}’, "
            f"둘째의 배우자궁에서 읽은 ‘{GOD_LENS[principal(contexts['b'], 'day')['ten_god']]}’ 중 "
            "요즘 특히 중요해진 것이 있는지 먼저 물어보세요. 실제로 들은 답을 바탕으로 둘만의 기준을 조금씩 정해 가면 좋아요.",
            [principal(context, "day")["id"] for context in contexts.values()],
            heading="가까운 사이의 기준은 다시 물을 수 있어요",
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

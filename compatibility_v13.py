"""Offline, traceable hypothesis and report engine for Yeonyeon v1.3."""

from compatibility_v11 import SUPPORT, ten_god
from compatibility_v12 import (
    EDITORIAL_WEIGHT, PEOPLE, POSITION, TIERS, _paragraph, _read,
    analyze_pair as analyze_v12, report_markdown, review_report,
)

ASSUMPTIONS = (
    "자평식 월지 본기와 v1.2 지장간 배열을 사용합니다. 절입 후 일수에 따른 사령은 적용하지 않습니다.",
    "동일 천간을 투간과 통근의 우선 근거로, 반대 음양의 동오행을 보조 근거로 읽습니다.",
    "합충형해는 v1.1의 성립 규칙을 따릅니다. 합화·격국·용신 및 관계의 길흉은 판정하지 않습니다.",
    "일주와 월주에 비중을 둔 순위는 원고 편집 기준입니다.",
)

# Observable choices for illustrating a hypothesized interaction, keyed by viewpoint.
ACTIONS = {
    "비견": "각자 편한 시간을 먼저 고르기",
    "겁재": "이번에 누가 만남을 준비할지 정하기",
    "식신": "바로 해 볼 수 있는 작은 배려를 건네기",
    "상관": "기존 약속에서 불편했던 대목을 꺼내기",
    "편재": "시간과 장소의 대안을 더 찾아보기",
    "정재": "반복해도 부담 없는 시간과 비용을 정하기",
    "편관": "급히 결정할 일의 담당을 정하기",
    "정관": "둘이 지킬 약속을 먼저 확인하기",
    "편인": "제안을 받아들일 시간을 확보하기",
    "정인": "어떤 도움이 필요한지 먼저 확인하기",
}
SITUATIONS = {
    "day": "둘만의 저녁 약속을 바꾸는 상황",
    "month": "일정이 빽빽한 주에 만날 시간을 잡는 상황",
    "year": "지인들과의 모임에 함께 가기로 한 상황",
    "hour": "다음 달의 공동 계획을 의논하는 상황",
}
EFFECT = {
    "천간합": "한 사람이 꺼낸 제안을 다른 사람이 이어받기",
    "육합": "일단 맞는 부분부터 함께 정해 두기",
    "삼합": "시간과 역할이 함께 맞을 때 계획을 진행하기",
    "육충": "같은 시간이나 역할에 서로 다른 조건을 걸기",
    "상형": "합의한 뒤에도 그 기준을 다시 확인하기",
    "삼형": "여러 조건이 얽혀 한 가지 변경으로는 결론이 나지 않기",
    "자형": "같은 확인이 되풀이되어 결정을 미루기",
    "육해": "한 사람이 덜어 주려던 일이 상대에게 새 부담이 되기",
}


def natal_hypothesis(owner, context, evidence):
    month = context["month_command"]
    month_id = month["principal_id"] if month else None
    day = evidence[f"{owner}.day.stem"]["symbol"]
    roots = context["roots"][day]
    exact = set(roots["exact"])
    related = set(roots["same_element_other_polarity"])
    ranked = []
    for placement in context["placements"]:
        # The day stem alone does not make a hidden role outwardly visible.
        exposure = [ref for ref in placement["exposed_at"] if ref != f"{owner}.day.stem"]
        score = (4 - TIERS.index(placement["tier"])) + EDITORIAL_WEIGHT[placement["pillar"]]
        score += 3 * bool(exposure) + 3 * (placement["id"] == month_id)
        score += 2 * (placement["id"] in exact) + (placement["id"] in related)
        ranked.append({**placement, "visible_role_ids": exposure, "weight": score})
    ranked.sort(key=lambda item: (-item["weight"], item["id"]))
    lead = ranked[0]
    rival = next((item for item in ranked if item["ten_god"] != lead["ten_god"]), None)
    return {
        "month_id": month_id, "lead": lead, "alternative": rival, "ranked_roles": ranked,
        "roots": roots, "coverage_id": f"{owner}.coverage",
    }


def relationship_hypothesis(evidence, interactions, natal):
    candidates = []
    for ref in interactions:
        card = evidence[ref]
        sources = card["sources"]
        overlap = sum(s["source_id"] == natal[s["person"]]["lead"]["id"] or
                      s["source_id"] in natal[s["person"]]["lead"]["visible_role_ids"]
                      for s in sources)
        reciprocal = sum(
            s["other_ten_god"] == evidence[f"pair.{'b' if s['person'] == 'a' else 'a'}.reads.{s['person']}"]["ten_god"]
            for s in sources
        )
        position = sum(EDITORIAL_WEIGHT[s["pillar"]] for s in sources) / len(sources)
        candidates.append({"id": ref, "position": position, "natal_overlap": overlap,
                           "direction_overlap": reciprocal,
                           "weight": 2 * position + 2 * overlap + reciprocal})
    candidates.sort(key=lambda row: (-row["weight"], row["id"]))
    lead = candidates[0]["id"] if candidates else None
    counter = None
    if lead:
        source_slots = {(s["person"], s["pillar"]) for s in evidence[lead]["sources"]}
        opposites = [row for row in candidates
                     if (evidence[row["id"]]["kind"] in SUPPORT) != (evidence[lead]["kind"] in SUPPORT)]
        for row in opposites:
            row["shared_slots"] = len(source_slots & {
                (s["person"], s["pillar"]) for s in evidence[row["id"]]["sources"]
            })
        if opposites:
            counter = max(opposites, key=lambda row: (row["shared_slots"], row["weight"]))["id"]
    return {"lead_id": lead, "counter_id": counter, "candidates": candidates,
            "direction_ids": ["pair.a.reads.b", "pair.b.reads.a"]}


def placement_text(item, evidence):
    fact = evidence[item["id"]]
    return f"{POSITION[item['pillar']]} {_read(fact['branch'])}의 {item['tier']} {_read(item['stem'])}"


def natal_paragraph(owner, hypothesis, evidence):
    day_id = f"{owner}.day.stem"
    lead, rival = hypothesis["lead"], hypothesis["alternative"]
    lead_action = ACTIONS[lead["ten_god"]]
    refs = [day_id, lead["id"], hypothesis["coverage_id"], *lead["visible_role_ids"]]
    month = hypothesis["month_id"]
    if month:
        month_branch = _read(evidence[month]["branch"])
        opening = f"{PEOPLE[owner]}의 원국은 월지 {month_branch}에서 출발해 읽었습니다."
        refs.append(month)
    else:
        opening = f"{PEOPLE[owner]}은 절입 전후 월주가 달라질 수 있어 확인된 자리부터 읽었습니다."
    exposure = lead["visible_role_ids"]
    if exposure:
        positions = "·".join(POSITION[evidence[ref]["pillar"]] for ref in exposure)
        visibility = f"{positions} 천간에도 같은 글자가 드러납니다."
    else:
        visibility = "일간을 제외한 확인 범위에서는 이 글자의 투간은 확인되지 않습니다."
    roots = hypothesis["roots"]["exact"]
    other_roots = hypothesis["roots"]["same_element_other_polarity"]
    if roots or other_roots:
        ref = (roots or other_roots)[0]
        refs.append(ref)
        label = "같은 천간의 뿌리" if roots else "음양이 다른 동오행의 뿌리 후보"
        footing = f"일간에는 {POSITION[evidence[ref]['pillar']]} {_read(evidence[ref]['branch'])}에 {label}도 있습니다."
    else:
        footing = "확인된 지장간 범위에서 일간과 같은 오행은 발견되지 않았습니다."
    text = (
        f"{opening} {placement_text(lead, evidence)}에 나타나는 십성은 {lead['ten_god']}입니다. "
        f"{visibility} {footing} 관계에서는 ‘{lead_action}’라는 선택이 중요해지는 때가 있는지 살펴볼 만합니다."
    )
    if rival:
        refs.extend([rival["id"], *rival["visible_role_ids"]])
        text += (f" {placement_text(rival, evidence)}에서 읽는 {rival['ten_god']}까지 고려하면 "
                 f"상황에 따라 ‘{ACTIONS[rival['ten_god']]}’부터 필요할 수도 있습니다.")
    return _paragraph(text, refs)


def relation_text(card):
    labels = " · ".join(f"{PEOPLE[s['person']]}의 {POSITION[s['pillar']]} {_read(s['symbol'])}"
                       for s in card["sources"])
    return f"{labels} 사이에 나타나는 관계는 {card['kind']}입니다"


def render(natal, relationship, evidence):
    directions = relationship["direction_ids"]
    a, b = (evidence[ref]["ten_god"] for ref in directions)
    lead, counter = relationship["lead_id"], relationship["counter_id"]
    interaction = evidence[lead] if lead else None
    position = max((s["pillar"] for s in interaction["sources"]), key=EDITORIAL_WEIGHT.get) if lead else "day"
    scene = SITUATIONS[position]
    if a == b:
        dynamic = (f"두 사람 모두 ‘{ACTIONS[a]}’부터 하려는 경우를 생각해 보세요. "
                   "같은 대목에 관심이 모여도 먼저 움직일 사람이 정해져 있는지는 따로 살필 문제입니다.")
    else:
        dynamic = (f"첫째가 ‘{ACTIONS[a]}’부터 하려는 동안 둘째는 "
                   f"‘{ACTIONS[b]}’에 뜻을 두는 상황을 떠올려 볼 수 있습니다.")
    reads = _paragraph(
        f"{scene}을 예로 들어 보겠습니다. 첫째가 둘째의 일간에서 읽는 십성은 {a}, "
        f"둘째가 첫째에게서 읽는 십성은 {b}입니다. {dynamic}", directions,
    )
    if lead:
        text = f"{relation_text(interaction)}. 이 장면에서 눈여겨볼 흐름은 ‘{EFFECT[interaction['kind']]}’입니다."
    else:
        text = "확인된 자리에서 교차 합충형해가 검출되지 않아 두 방향의 십성을 중심으로 이 장면을 읽었습니다."
    if lead:
        source = max(interaction["sources"], key=lambda item: EDITORIAL_WEIGHT[item["pillar"]])
        own, other = source["owner_ten_god"], source["other_ten_god"]
        if own != other:
            person = PEOPLE[source["person"]]
            text += (f" 특히 {person} 쪽의 {_read(source['read_stem'])}은 본인에게 {own}, 상대에게는 "
                     f"{other}에 해당합니다. 한쪽이 ‘{ACTIONS[own]}’에 뜻을 두더라도, "
                     f"다른 쪽의 관심은 ‘{ACTIONS[other]}’에 가 있을 수 있다는 해석입니다.")
    if counter:
        alternative = evidence[counter]
        shared = next(row["shared_slots"] for row in relationship["candidates"] if row["id"] == counter)
        connection = ("앞서 본 자리 중 일부가 이 관계에도 들어 있습니다."
                      if shared else "이 관계는 앞에서 본 것과 다른 자리에서 생깁니다.")
        text += (f" 한편 {relation_text(alternative)}. {connection} "
                 f"‘{EFFECT[alternative['kind']]}’가 더 두드러진다면 어떤 조건에서 흐름이 달라졌는지 살펴보세요.")
    refs = [*directions, *(ref for ref in (lead, counter) if ref)]
    scene_read = _paragraph(text, refs)
    if lead and interaction["kind"] in SUPPORT:
        experiment = "먼저 서로 바로 동의할 수 있는 한 가지를 정하고, 합의 뒤에 새로 생긴 부담이 있는지 돌아보세요."
    elif lead:
        experiment = "각자 바꿀 수 있는 조건 하나와 지켜야 할 조건 하나를 말한 뒤, 바꿀 수 있는 것부터 조정해 보세요."
    else:
        experiment = "어느 제안이 먼저였는지 떠올리고, 그때 상대가 어떤 조건을 확인하려 했는지 물어보세요."
    practice = _paragraph(
        f"지난 약속을 하나 골라 첫째가 관심을 둔 일이 ‘{ACTIONS[a]}’였는지, "
        f"둘째에게는 ‘{ACTIONS[b]}’가 중요했는지 돌아보세요. {experiment} "
        + (f"‘{EFFECT[evidence[counter]['kind']]}’가 더 익숙한 장면이었다면 그때의 조건부터 꺼내 보세요."
           if counter else "둘 다 다른 일을 먼저 떠올렸다면, 그 일을 다음 대화의 출발점으로 삼아도 좋겠습니다."),
        refs)
    return [
        {"title": "각자 무엇을 먼저 살피는가", "paragraphs": [
            natal_paragraph(owner, item, evidence) for owner, item in natal.items()
        ]},
        {"title": "같은 약속을 두고", "paragraphs": [reads, scene_read]},
        {"title": "다음 약속에서 확인할 것", "paragraphs": [practice]},
    ]


def analyze_pair(a, b):
    """Analyze two existing v1.2 birth dictionaries without changing service routes."""
    base = analyze_v12(a, b)
    evidence = base["evidence"]
    natal = {owner: natal_hypothesis(owner, context, evidence)
             for owner, context in base["contexts"].items()}
    relationship = relationship_hypothesis(evidence, base["interactions"], natal)
    report = render(natal, relationship, evidence)
    return {**base, "version": "1.3", "assumptions": ASSUMPTIONS,
            "plan": {"natal": natal, "relationship": relationship}, "report": report,
            "review": review_report(report, evidence)}

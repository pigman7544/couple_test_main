"""Compose five chapters for the reports that share the same role assignment."""

from c06_report import band
from reading_voice import GOD_SCENES
from relationship_scenes import (
    FOLLOW_THROUGH, ROLE_DETAILS, SCENES, SCENE_BANDS, SCENE_TURNS, SECOND_LOOK, STEM_RELATION,
)


STORIES = {
    'c02': (
        '견우와 직녀는 하늘에 사는 두 사람으로 전해져요. 견우는 소를 돌보고, 직녀는 베를 짜요. 둘이 부부가 된 뒤 하던 일을 소홀히 하자 하늘의 명으로 떨어져 살게 됐다는 이야기가 널리 알려져 있어요. 둘을 갈라놓은 이유가 다르게 전해지는 곳도 있어요.',
        '은하수 양쪽에 살게 된 두 사람은 평소에 강을 건너지 못해요. 음력 칠월 칠석이 되면 까치와 까마귀가 다리를 놓고, 둘은 그 오작교에서 다시 만나요. 어느 날 만날 수 있는지 정해져 있어도, 날을 앞당기거나 함께 보낼 시간을 늘릴 수는 없어요.',
        '칠석에 오는 비를 두 사람이 만나 흘린 눈물이나 헤어지며 흘린 눈물로 풀이하는 이야기도 있어요. 설화에 둘이 평소에 어떻게 지냈는지는 자세히 나오지 않아요. 분명한 건 두 사람이 다시 만나려면 자기 마음과 별개로 주변의 도움과 가능한 날이 필요했다는 점이에요.',
    ),
    'c10': (
        '베로나에서 몬터규 집안과 캐퓰릿 집안은 오랫동안 다퉈요. 몬터규의 아들 로미오와 캐퓰릿의 딸 줄리엣은 무도회에서 만나 마음이 가요. 상대가 어느 집안 사람인지 알게 된 뒤에도, 그날 밤 정원에서 다시 만나 서로의 마음을 확인해요.',
        '로미오는 달을 두고 사랑을 맹세하려 하고, 줄리엣은 모양이 변하는 달에 맹세하지 말라고 해요. 줄리엣은 혼인할 뜻이 확실하다면 다음 날 소식을 보내 달라고 해요. 두 사람은 로렌스 수사의 도움으로 결혼하지만 가족에게는 알리지 못해요.',
        '집안 사이의 다툼으로 티볼트가 죽고 로미오는 베로나에서 추방돼요. 줄리엣은 다른 사람과 결혼할 처지가 되자 수사의 도움을 받아 죽은 것처럼 보이는 약을 마셔요. 계획을 알려 주려던 편지는 로미오에게 닿지 않아요. 로미오는 줄리엣이 죽었다는 소식만 듣고 돌아오고, 둘은 끝내 다시 이야기하지 못해요.',
    ),
    'c13': (
        '오디세우스는 트로이 전쟁이 끝난 뒤에도 오랫동안 이타카로 돌아오지 못해요. 집에는 아내 페넬로페와 아들 텔레마코스가 있어요. 남편이 돌아오지 않을 거라 여긴 구혼자들은 페넬로페에게 새 남편을 고르라고 압박해요.',
        '페넬로페는 시아버지의 수의를 다 짜고 나서 결정하겠다고 말해요. 낮에 짠 천을 밤에 다시 풀어 시간을 벌지만, 그 사실을 들키고 말아요. 오디세우스는 뒤늦게 거지 차림으로 집에 돌아오고, 아들과 함께 구혼자들을 물리쳐요.',
        '페넬로페는 돌아온 사람의 말을 듣고 부부의 침대를 밖으로 옮기라고 해요. 침대를 옮길 수 없다는 답과 함께, 오디세우스는 그 침대를 뿌리 내린 올리브나무에 붙여 만든 일을 설명해요. 그 말을 듣고서야 페넬로페는 눈앞의 사람이 남편임을 확인해요.',
    ),
    'c18': (
        '닉 캐러웨이는 새로 이사 온 곳에서 개츠비의 이웃이 돼요. 개츠비가 화려한 파티를 열던 집 건너편에는 데이지가 남편 톰과 살고 있어요. 개츠비와 데이지는 예전에 사랑했지만, 다시 만나기 전까지 각자 다른 시간을 보냈어요.',
        '개츠비는 닉에게 차를 마실 자리를 마련해 달라고 해요. 다시 만난 뒤에도 개츠비는 지나간 몇 년을 되돌릴 수 있다고 기대해요. 호텔에서 톰과 맞서자 데이지에게 톰을 한 번도 사랑한 적 없다고 말해 달라고 해요. 데이지는 두 사람의 과거를 그 말로 정리할 수 없다고 답해요.',
        '돌아오는 길에 데이지가 운전하던 차가 머틀을 치어요. 개츠비는 데이지를 보호하려 하지만, 머틀의 남편은 개츠비를 찾아가 그를 죽여요. 데이지와 톰은 떠나고, 닉은 개츠비의 장례를 준비해요. 개츠비가 준비한 재회와 데이지가 실제로 고른 삶은 끝까지 달랐어요.',
    ),
    'f01': (
        '의사인 왓슨은 홈즈와 베이커가 221B에 함께 살면서 그의 일을 가까이에서 보게 돼요. 홈즈는 사건을 의뢰받으면 처음 들은 설명만으로 결론짓지 않아요. 장소와 물건을 살피거나 사람들의 말을 대조해 앞뒤가 맞는지 확인해요.',
        '왓슨도 함께 현장을 찾아가고 자신이 보고 들은 일을 기록해요. 독자는 그 기록을 따라가며 홈즈의 결론을 듣기 전에 어떤 단서가 나왔는지 알 수 있어요. 두 사람이 같은 일을 맡는 경우보다 서로 다른 일을 하는 모습이 자주 나와요.',
        '홈즈가 놓치기 쉬운 단서를 찾아내는 데 능하다면, 왓슨은 그 과정에 함께 있으며 일이 어떻게 진행됐는지 독자에게 설명해요. 사건의 답을 찾는 것과 다른 사람이 답에 이른 과정을 이해하게 하는 일에는 각각 수고가 들어요.',
    ),
    'f02': (
        '돈키호테는 기사 이야기를 즐겨 읽고 자신도 세상을 돌아다니며 어려운 일을 해결하겠다고 해요. 이웃인 산초 판사는 함께 길을 떠나요. 두 사람이 같은 장소에 도착하고도 눈앞에 있는 것을 다르게 설명하는 일이 생겨요.',
        '돈키호테는 평원에 서 있는 풍차를 거인으로 보아요. 산초는 팔처럼 보이는 것이 바람에 도는 풍차의 날개라고 알려 줘요. 돈키호테는 말을 몰고 달려들었다가 풍차 날개에 부딪혀 쓰러져요.',
        '돈키호테는 나중에 마법사가 거인을 풍차로 바꿨다고 설명해요. 산초가 본 사실을 듣고도 처음 판단을 되돌리지는 않아요. 그런데도 두 사람은 여행을 계속해요. 풍차 장면을 보면 같은 목표로 출발하는 일과 눈앞의 일을 함께 판단하는 일이 서로 다르다는 걸 알 수 있어요.',
    ),
    'f03': (
        '관중과 포숙아의 우정은 고사로 전해져요. 관중은 함께 장사할 때 자신이 이익을 더 가져간 적에도 포숙아는 가난한 형편을 알아줬다고 말해요. 전쟁에서 물러났을 때도 그에게 돌볼 어머니가 있다는 사정을 헤아렸다고 해요.',
        '뒤에 두 사람은 제나라 왕위를 두고 맞선 사람들을 각기 섬겨요. 포숙아가 섬기던 공자 소백이 환공이 되고, 관중은 처벌받을 처지에 놓여요. 포숙아는 환공에게 관중이 나라를 맡을 만한 인재라고 추천해요.',
        '환공은 관중을 등용하고, 관중은 뒤에 자신을 알아준 사람으로 포숙아를 기억해요. 포숙아가 관중의 사정을 헤아린 일과, 중요한 자리에 그의 능력이 필요하다고 판단한 일은 서로 다른 선택이었어요.',
    ),
    'f04': (
        '길가메시가 다스리는 우루크에서 사람들은 왕의 행동에 시달려요. 엔키두는 그런 길가메시에게 맞서고 두 사람은 힘을 겨뤄요. 처음 만났을 때 길가메시에게 엔키두는 자기 뜻대로 움직이지 않는 사람이었어요.',
        '훗날 두 사람은 함께 삼나무 숲으로 가서 훔바바와 맞서요. 처음에는 서로에게 힘을 쓰던 두 사람이 이번에는 같은 일에 힘을 합쳐요. 엔키두는 길가메시와 함께 움직이는 동안에도 자기 의견을 내요.',
        '엔키두가 죽자 길가메시는 친구를 잃은 슬픔을 겪고 자신도 죽을 수 있다는 사실을 두려워해요. 영원히 살 방법을 찾아 떠날 정도로 큰 변화였어요. 처음에는 맞서던 한 사람이 나중에는 길가메시가 자기 삶을 다시 생각하게 하는 친구가 됐어요.',
    ),
}

TITLES = {
    'c01': ('춘향이 지킨 선택과 이몽룡이 지킨 약속', '두 사람은 어떻게 다시 만났을까요?', '한 사람의 일정이 달라질 때', '기다리는 사람에게 필요한 말', '다음 약속을 함께 잡는 법'),
    'c02': ('견우와 직녀는 어떻게 다시 만났을까요?', '칠석에만 만날 수 있었던 두 사람', '만나지 못하는 날에도 관심을 전하는 법', '원하는 연락 횟수가 다를 때', '가능한 연락 시간을 먼저 말해요'),
    'c10': ('고백을 한 로미오와 다음 날을 물은 줄리엣', '마음이 같아도 소식을 전할 길은 필요했어요', '마음을 말하는 일과 계획을 세우는 일', '빨리 정할수록 놓치기 쉬운 조건', '함께하고 싶은 마음과 가능한 일을 말해요'),
    'c13': ('서로를 알아본 오디세우스와 페넬로페', '페넬로페가 침대를 옮기라고 한 이유', '오랜만에 만나도 달라진 일은 물어봐요', '같은 추억을 다른 뜻으로 떠올릴 때', '지금 가능한 약속을 정해요'),
    'c18': ('재회를 준비한 개츠비와 다른 시간을 살아온 데이지', '개츠비가 되돌리고 싶었던 시간', '좋았던 기억과 달라진 취향', '상대에게 예전 모습만 기대할 때', '추억은 함께 나누고 다음 계획은 다시 정해요'),
    'f01': ('홈즈와 왓슨이 각각 잘한 일', '같은 사건에서 서로 다른 일을 맡은 두 사람', '함께 맡은 일이 막히면', '한 사람의 수고만 기억될 때', '누가 무엇을 했는지 구체적으로 말해요'),
    'f02': ('돈키호테와 산초는 왜 같은 풍차를 다르게 봤을까요?', '같은 길에서 서로 다른 판단을 한 두 사람', '가 보고 싶은 곳과 실제 갈 수 있는 곳', '걱정을 반대로 받아들일 때', '기대되는 점과 지킬 조건을 함께 정해요'),
    'f03': ('포숙아가 관중에게 해 준 일', '관중이 포숙아를 기억한 이유', '친구의 실수를 함께 수습할 때', '도움이 한쪽의 부담이 될 때', '할 수 있는 도움과 맡을 일을 말해요'),
    'f04': ('길가메시와 엔키두가 힘을 합치기까지', '처음 맞서고 나중에 함께 싸운 두 사람', '계획을 시작하는 힘과 살펴보는 힘', '의견이 갈릴 때 수고까지 놓치지 않으려면', '둘 다 받아들일 수 있는 시험 계획을 정해요'),
}


def day_opening(a, b):
    from story_report import STEM_NAME, relationship_style, elem
    from relationship_v08 import GEN
    left, right = (relationship_style(p)['stem'] for p in (a, b))
    ea, eb = elem(a), elem(b)
    if left == right:
        same = STEM_NAME[left]
        return (f'두 사람 모두 {same} 일간을 가졌어요. '
                f'공통으로 읽을 수 있는 점은 **{STEM_RELATION[left][0]}**이에요. '
                '비슷한 점이 있어도 어느 때 그 모습을 보이는지는 두 사람의 사정에 따라 달라져요.')
    opening = (f'당신의 일간은 {STEM_NAME[left]}, 상대방의 일간은 {STEM_NAME[right]}이에요. '
               f'당신에게서 {STEM_RELATION[left][0]}을, 상대방에게서 {STEM_RELATION[right][0]}을 읽을 수 있어요. ')
    if ea == eb:
        return opening + '같은 오행 안에서도 두 사람이 중요하게 여기는 조건에는 차이가 있을 수 있어요.'
    if GEN[ea] == eb or GEN[eb] == ea:
        giver = '당신이' if GEN[ea] == eb else '상대방이'
        return (opening + '오행에서 한 성질이 다른 성질을 돕는 관계를 상생이라고 해요. '
                f'{giver} 먼저 제안하고 다른 쪽이 자기 형편에 맞게 바꿔 실행하면, 제안도 실행도 둘 사이에 어떤 도움이 됐는지 알 수 있어요.')
    return opening + '오행에서 한 성질이 다른 성질을 조절하는 관계를 상극이라고 해요. 서로 다른 의견을 들으면 한 사람이 혼자 정할 때 빠뜨린 조건을 확인할 수 있어요.'


def profile(label, name, chart_style, scene, detail):
    from story_report import STEM_NAME
    event, trait, supported, example = scene
    stem = chart_style['stem']
    reading, independent_example = STEM_RELATION[stem]
    opening = f'{event} {trait}'
    chart = f'{label}의 일간은 **{STEM_NAME[stem]}**({stem})이에요. 여기서 {reading}을 읽어요.'
    if stem in supported:
        comparison = f'이 모습이 {name}의 선택과 닮았어요. {example}'
    else:
        comparison = f'이 성향을 일상에 비춰 보면, {independent_example[0].lower() + independent_example[1:]}'
    month = '태어난 달의 글자를 함께 보면 가까운 사이에서 보일 수 있는 또 다른 행동이 있어요. '
    month += GOD_SCENES[chart_style['god']] + '.'
    title = f'{label}에게 비춰 보는 {name}'
    return f'◆ **{title}**\n{opening}\n\n{chart} {comparison}\n\n{month}\n\n{detail}'


def enrich(result, a, b, rel, couple):
    from story_report import relationship_style, count_elements
    from c01_report import TALE
    from literary_edition import EDITION
    from other_reports import LENSES, ADVICE
    from personalized_reading import CONFLICT, EXPRESSION, AUTONOMY, PACE
    from story_report import elem

    cid = couple['id']
    first, second = couple['name'].split('·', 1)
    sa, sb = relationship_style(a), relationship_style(b)

    def strength(person, style):
        counts = count_elements(person)
        return counts['earth'] + counts['metal'] + (style['god'] in ('정관', '정재', '비견'))

    if strength(a, sa) >= strength(b, sb):
        labels, styles = ('당신', '상대방'), (sa, sb)
    else:
        labels, styles = ('상대방', '당신'), (sb, sa)

    left, right, moment, conflict, repair = SCENES[cid]
    detail, consequence, follow_up = FOLLOW_THROUGH[cid]
    read_again, try_again = SECOND_LOOK[cid]
    result['roles'] = '\n\n'.join(
        profile(label, name, style, scene, example)
        for label, name, style, scene, example in
        zip(labels, (first, second), styles, (left, right), ROLE_DETAILS[cid])
    )
    result['story'] = TALE if cid == 'c01' else '\n\n'.join(STORIES[cid])
    v = rel['vector']
    # Sentence-level readings keep the existing score bands without imposing a
    # fixed chapter outline. The example remains grounded in this work.
    focus = {'c01':'security', 'c02':'security', 'c10':'attraction', 'c13':'security',
             'c18':'attraction', 'f01':'growth', 'f02':'growth', 'f03':'security', 'f04':'growth'}[cid]
    result['saju_a'] = '\n\n'.join((
        day_opening(a, b), moment, detail, SCENE_BANDS[cid][band(v[focus])], SCENE_TURNS[cid],
    ))
    result['crisis'] = '\n\n'.join((conflict, consequence, read_again, CONFLICT[band(v['conflict'])], EXPRESSION[band(v['expression'])]))
    topics = [PACE[elem(p)][1] for p in (a, b)]
    prompts = (f'두 분 모두 ‘{topics[0]}’에 관해 한 가지씩 말해 보세요. '
               if topics[0] == topics[1] else
               f'당신은 ‘{topics[0]}’에 관해, 상대방은 ‘{topics[1]}’에 관해 한 가지씩 말해 보세요. ')
    prompts += '서로의 답을 듣고 앞에서 정한 약속을 바꿔야 할 게 있는지도 함께 확인해 보세요.'
    result['tip'] = '\n\n'.join((repair, follow_up, try_again, prompts,
        ' '.join(ADVICE[key][band(v[key])] for key in ('attraction', 'security', 'growth') if key != focus),
        AUTONOMY[band(v['autonomy'])]))
    if cid == 'c01':
        result['tagline'] = '떨어져 있어도 이어 가는 약속'
        result['teaser'] = '춘향은 자신이 한 선택을 지켰고, 이몽룡은 남원으로 돌아왔어요. 두 분은 약속을 바꿔야 할 때 어떻게 다시 정하나요?'
        question = '바쁜 날에도 서로 지킬 수 있는 약속은 무엇인가요?'
    else:
        result['tagline'] = LENSES[cid][0]
        result['teaser'] = left[0] + ' ' + right[0]
        question = EDITION[cid][-1]
    result['questions'] = [question]
    result['ending'] = question
    fields = ['roles', 'story', 'saju_a', 'crisis', 'tip']
    result['sections'] = fields
    result['chapters'] = [dict(key=key, title=title) for key, title in zip(fields, TITLES[cid])]
    return result

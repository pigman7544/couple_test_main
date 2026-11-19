"""Five-chapter literary edition for non-Baek, non-Chunhyang matches.

Literary events come from the existing curated SCENES, not from the chart.
The birth-chart symbolism is an interpretive analogy, never a prediction.
"""
from individual_scenes import SCENES
from character_connections import CONNECTIONS
from story_report import relationship_style, STEM_NAME, elem, GEN, CTRL

# Each archetype has its own moral tension, everyday conflict, and actionable ending.
EDITION = {
'c02': ('견우와 직녀', '서로 떨어져 있는 날에도 사랑은 어떻게 이어질까요?',
 '견우와 직녀는 만나는 하루만으로 사랑을 설명할 수 없는 사람들이에요. 기다리는 동안에도 각자 살아 내야 할 하루가 있었으니까요.',
 '한쪽은 기다림을 믿음의 표시로 여기지만, 다른 한쪽은 오늘의 안부가 없으면 외로워질 수 있어요. 둘 다 사랑하지만 시간을 견디는 방식은 다를 수 있죠.',
 '연락이 뜸한 날, “바빠서 그랬어”라는 설명이 “나는 네 하루가 궁금했어”라는 마음을 놓칠 수 있어요.',
 '만날 날짜뿐 아니라 떨어져 있는 날의 연락 방식을 함께 정해요. 답장이 늦을 때는 마음을 추측하기보다 가능한 시간을 물어봐요.',
 '서로 떨어져 있을 때 가장 듣고 싶은 한마디는 무엇일까요?'),
'c03': ('온달과 평강공주', '온달과 평강은 함께 살아갈 준비를 어떻게 했을까요?',
 '평강은 남들이 바보라고 놀리던 온달을 직접 찾아가 함께 살림을 꾸렸어요. 평강이 말을 고르는 법을 알려 주자 온달은 직접 말을 구해 돌보고 무예를 익혔어요.',
 '상대가 수업을 알아봐 달라고 했어도 등록까지 원한다는 뜻인지는 물어봐야 해요. 수업 시간과 비용을 보고 나면 처음 마음과 달라질 수 있어요.',
 '한 사람이 새 자격증에 관심이 있다고 해요. 다른 사람은 도움이 되고 싶어서 수업 세 곳을 알아보고 이번 주 안에 등록하자고 권해요. 자료를 받은 사람은 고맙지만 야근이 끝나는 다음 달에야 공부할 시간을 낼 수 있어요. 자료를 보낸 사람은 답을 못 들으면 자기가 한 수고가 필요 없었다고 느낄 수 있어요.',
 '“수업 정보는 도움이 됐어. 신청은 야근이 끝나고 정하고 싶어”라고 말해 보세요. 자료를 찾은 사람은 “그럼 다음 달 첫 주에 같이 볼까?”라고 물을 수 있어요.',
 '내가 지금 받고 싶은 도움은 무엇이고, 직접 정하고 싶은 일은 무엇인가요?'),
'c10': ('로미오와 줄리엣', '뜨거운 마음을 지키면서도 선택할 여유를 남길 수 있을까요?',
 '두 사람은 빠르게 사랑에 빠졌지만, 가문의 다툼과 비밀은 서로 확인할 수 있는 길을 좁혔어요. 비극을 만든 것은 사랑의 부족함만이 아니었죠.',
 '서로에게만 집중하는 마음은 아름답지만, 위기에서 도움을 구할 통로까지 닫아서는 안 돼요. 절박함은 때로 선택지를 실제보다 적게 보이게 하니까요.',
 '주변의 반대가 생긴 날, 한 사람은 당장 결론을 내리고 싶고 다른 사람은 상황을 더 알아보고 싶을 수 있어요.',
 '감정이 가장 격한 날에는 돌이키기 어려운 결정을 미뤄요. 반대의 이유가 편견인지 실제 걱정인지 나누어 듣고, 믿을 만한 도움을 남겨 둬요.',
 '우리가 급해질 때 서로에게 만들어 줄 수 있는 여유는 무엇일까요?'),
'c11': ('엘리자베스와 다아시', '처음의 판단을 고쳐 쓸 용기도 사랑일까요?',
 '엘리자베스와 다아시는 서로를 오해했어요. 편지와 실제 행동을 통해 첫인상을 다시 살핀 뒤에야 상대의 다른 모습을 볼 수 있었죠.',
 '상대를 이해하는 일은 잘못된 행동을 없던 일로 만드는 게 아니에요. 사실과 추측을 나누고, 달라진 행동을 확인하는 과정이에요.',
 '짧은 메시지 하나를 보고 “또 무시했네”라고 생각하는 순간, 상대는 전혀 다른 의도로 보냈을 수도 있어요.',
 '“네가 그런 뜻으로 말한 줄 알았어”라고 추측을 먼저 인정해요. 사과는 말로 하고 변화는 행동으로 확인해요.',
 '처음에는 오해했지만 지금은 다르게 보이는 모습이 있나요?'),
'c13': ('오디세우스와 페넬로페', '오래 기다린 뒤에도 서로를 다시 알아볼 수 있을까요?',
 '오디세우스는 먼 길을 돌아왔고 페넬로페는 자기 자리에서 삶을 지켰어요. 재회의 순간에도 페넬로페는 두 사람만 아는 비밀로 그를 확인했죠.',
 '기다렸다는 사실만으로 서로의 변화를 모두 아는 것은 아니에요. 신뢰에는 다시 질문할 권리도 포함돼요.',
 '오랜만에 만난 날 “예전엔 이걸 좋아했잖아”라는 말이 “나는 그동안 조금 달라졌어”라는 대답을 만나기도 해요.',
 '함께 있지 못했던 시간의 이야기를 번갈아 들어요. 예전의 약속이 지금도 편안한지 다시 확인해요.',
 '서로 만나지 못했던 시간에 내가 새롭게 알게 된 것은 무엇일까요?'),
'c18': ('개츠비와 데이지', '기억 속 사랑이 아니라 지금의 서로를 볼 수 있을까요?',
 '개츠비는 과거의 시간을 되찾으려 했어요. 그러나 데이지는 이미 다른 삶을 살아가는 사람이었죠. 간절한 기억이 현재의 동의를 대신할 수는 없어요.',
 '그리움이 클수록 상대를 실제 사람보다 오래된 이미지로 바라보기 쉬워요. 사랑은 추억을 간직하면서도 달라진 마음을 들을 수 있어야 해요.',
 '예전에 즐겨 가던 장소에서 “넌 여기 좋아하잖아”라고 말했을 때 상대가 “지금은 달라”라고 대답할 수도 있어요.',
 '“지금도 좋아해?”라는 질문을 추억 뒤에 붙여요. 상대의 현재 선택을 과거의 약속으로 압박하지 않아요.',
 '내가 사랑하는 너의 모습 중 지금 새롭게 알게 된 것은 무엇일까요?'),
'f01': ('셜록 홈즈와 존 왓슨', '다른 재능을 가진 두 사람이 어떻게 한 팀이 될까요?',
 '홈즈의 추리만큼 왓슨의 관찰과 동행도 중요했어요. 이들은 원작에서 연인이 아닌 동료이지만, 서로 다른 기여가 관계를 지탱한다는 점을 비춰 볼 수 있어요.',
 '눈에 띄는 해결 능력만 인정하면 조용히 곁을 지킨 노력은 보이지 않게 돼요. 관계는 누가 더 뛰어난가를 겨루는 일이 아니에요.',
 '함께 해결한 문제를 두고 한 사람만 칭찬받을 때, 다른 사람의 준비와 돌봄은 쉽게 잊힐 수 있어요.',
 '이번 주 상대가 해 준 보이지 않는 일을 하나 구체적으로 고마워해요. 역할을 고정하지 말고 번갈아 맡아 봐요.',
 '내가 당연하게 여겼던 너의 기여는 무엇일까요?'),
'f02': ('돈키호테와 산초 판사', '꿈과 현실을 함께 바라보면 어떤 길이 열릴까요?',
 '돈키호테는 풍차를 거인으로 보았고 산초는 풍차라고 말했어요. 두 사람은 다르게 보면서도 같은 길을 걸었고 서로의 시선에 영향을 받았죠.',
 '상상력을 비웃으면 꿈이 작아지고 현실 점검을 무시하면 위험이 커져요. 사랑에는 가능성을 보는 눈과 발밑을 살피는 눈이 모두 필요해요.',
 '여행 계획을 세울 때 한 사람은 즉흥적인 모험을 원하고 다른 사람은 예산과 시간을 확인하고 싶을 수 있어요.',
 '아이디어를 바로 거절하기 전에 기대되는 점 하나를 말해요. 그다음 안전과 비용을 함께 확인해요.',
 '우리가 함께 해 보고 싶은 모험과 꼭 지키고 싶은 현실 조건은 무엇일까요?'),
'f03': ('관중과 포숙아', '사정을 이해하는 마음은 어디까지 상대를 도울까요?',
 '포숙아는 관중의 행동만 보고 단정하지 않고 그 뒤의 사정을 보려 했어요. 관중의 재능을 인정해 추천하기도 했죠. 두 사람은 연인이 아닌 역사적 우정의 비유예요.',
 '이해는 무조건 눈감아 주는 일이 아니에요. 상대를 믿는다는 것은 능력을 인정하면서 책임도 함께 바라보는 일이죠.',
 '상대가 실수했을 때 한 사람은 이유부터 묻고 다른 사람은 해결할 책임부터 정하고 싶을 수 있어요.',
 '사정을 먼저 듣되 무엇을 바로잡을지도 함께 정해요. 상대를 대신해 모든 문제를 해결하려 하지 않아요.',
 '내가 오해받았던 순간, 네가 알아주었으면 했던 사정은 무엇일까요?'),
'f04': ('길가메시와 엔키두', '서로 맞서던 두 사람이 어떻게 서로를 바꿀까요?',
 '길가메시와 엔키두는 처음에는 힘을 겨뤘지만 깊은 친구가 됐어요. 함께한 모험과 상실은 삶을 바라보는 시선을 바꾸었죠. 원작은 연애담이 아닌 우정의 서사예요.',
 '강한 개성끼리 만나면 충돌할 수 있어요. 하지만 서로를 이겨야 할 상대로만 보지 않으면 차이가 배움의 계기가 될 수 있어요.',
 '같은 목표를 놓고 둘 다 자기 방식이 옳다고 주장할 때, 경쟁이 협력의 자리를 빼앗을 수 있어요.',
 '승패를 가르기 전에 상대에게서 배운 점을 말해요. 중요한 결정은 각자의 이유를 듣고 함께 정해요.',
 '우리가 처음 부딪혔지만 지금은 고맙게 생각하는 차이는 무엇일까요?'),
}

# Actions used to explain the two literary roles in the opening chapter.
ROLE_ACTIONS = {
    'c02': ('견우는 은하수 너머의 직녀를 만나기 위해 칠석을 기다려요.',
            '직녀는 칠석에 까치와 까마귀가 놓은 오작교에서 견우를 만나요.'),
    'c03': ('온달은 무예를 익혀 전쟁에 나가 공을 세워요.',
            '평강공주는 아버지의 반대에도 온달을 찾아가 살림과 배움을 도와요.'),
    'c10': ('로미오는 정원에 들어가 줄리엣에게 사랑을 고백해요.',
            '줄리엣은 로미오에게 결혼할 뜻이 확실하다면 다음 날 소식을 보내 달라고 해요.'),
    'c11': ('엘리자베스는 다아시의 편지를 다시 읽으며 위컴에 대한 판단을 돌아봐요.',
            '다아시는 첫 청혼을 거절당한 뒤 엘리자베스에게 편지로 자기 행동을 설명해요.'),
    'c13': ('오디세우스는 이타카에 돌아온 뒤 부부의 침대를 어떻게 만들었는지 설명해요.',
            '페넬로페는 두 사람만 아는 침대 이야기를 꺼내 돌아온 사람이 남편인지 확인해요.'),
    'c18': ('개츠비는 데이지를 다시 만나려고 닉에게 차 자리를 마련해 달라고 부탁해요.',
            '데이지는 호텔에서 톰을 한 번도 사랑하지 않았다고 말해 달라는 개츠비의 요구를 따르지 못해요.'),
    'f01': ('홈즈는 사건에서 남들이 지나친 단서를 살펴요.',
            '왓슨은 홈즈와 함께 사건 현장을 찾아가 자신이 본 일을 기록해요.'),
    'f02': ('돈키호테는 풍차를 거인으로 보고 달려들어요.',
            '산초는 눈앞에 있는 것이 거인이 아니라 풍차라고 알려 줘요.'),
    'f03': ('관중은 제나라 환공을 섬기게 된 뒤 포숙아가 자신의 가난한 형편을 알아주었다고 말해요.',
            '포숙아는 자기보다 관중이 그 자리에 어울린다고 판단해 관중을 추천해요.'),
    'f04': ('길가메시는 처음 만난 엔키두와 힘을 겨뤄요. 이후 그와 함께 훔바바에게 맞서요.',
            '엔키두는 처음에는 길가메시에게 맞서지만, 나중에는 길가메시와 함께 위험한 여정에 나서요.'),
}

def enrich(result,a,b,rel,couple):
    cid=couple['id']
    if cid not in EDITION:
        return result
    characters, central, portrait, tension, everyday, action, question = EDITION[cid]
    first, second=couple['name'].split('·',1)
    sa,sb=relationship_style(a),relationship_style(b)
    # Archetypal role allocation uses the same order as the existing report;
    # avoid gender claims or invented psychometric certainty.
    from story_report import count_elements
    def strength(p,s):
        c=count_elements(p)
        return c['earth']+c['metal']+(1 if s['god'] in ('정관','정재','비견') else 0)
    a_first=strength(a,sa)>=strength(b,sb)
    left,right=('당신','상대방') if a_first else ('상대방','당신')
    sl,sr=(sa,sb) if a_first else (sb,sa)
    origin,source_tension,source_action=SCENES[cid]
    left_action, right_action = ROLE_ACTIONS[cid]
    left_link, right_link = CONNECTIONS.get(cid, (
        '엘리자베스는 편지에서 알게 된 사실을 펨벌리에서 직접 본 행동과 대조해요.',
        '다아시는 편지에서 할 말을 정리하고 이후에는 달라진 태도를 행동으로 보여 줘요.',
    ))
    result['roles']=(f'**두 분은 {characters}의 이야기를 닮았어요.**\n\n'
        f'{portrait}\n\n'
        f'◆ **{left}과 닮은 인물 · {first}**\n{left_action} '
        f'{left}의 일간은 **{STEM_NAME[sl["stem"]]}({sl["stem"]})**이에요. '
        '일간은 태어난 날을 이루는 두 글자 중 앞 글자예요. '
        f'{STEM_NAME[sl["stem"]]}의 관계 성향을 읽을 때는 ‘{sl["desc"][2]}’에 주목해요. '
        f'{left_link}\n\n'
        f'◆ **{right}과 닮은 인물 · {second}**\n{right_action} '
        f'{right}의 일간은 **{STEM_NAME[sr["stem"]]}({sr["stem"]})**이에요. '
        f'{STEM_NAME[sr["stem"]]}의 관계 성향을 읽을 때는 ‘{sr["desc"][2]}’에 주목해요. '
        f'{right_link}')
    result['story']=(f'**{central}**\n\n'
        f'◆ **이야기 속 두 사람**\n{origin}\n\n'
        f'◆ **두 사람이 놓친 것**\n{tension}')
    ea,eb=elem(a),elem(b)
    if ea==eb: dynamic='두 사람의 일간은 같은 오행이에요. 비슷한 언어로 이해하기 쉬울 수 있지만, 같은 고집이 부딪힐 수도 있어요.'
    elif GEN[ea]==eb or GEN[eb]==ea: dynamic='두 일간은 상생의 관계예요. 서로를 북돋는 이미지지만, 도움을 주는 역할이 한쪽에만 쏠리지 않는지 살펴봐요.'
    else: dynamic='두 일간은 상극의 관계예요. 한 사람이 먼저 방향을 정하면 다른 사람은 그 결정이 지켜야 할 조건을 짚어 줄 수 있어요.'
    result['saju_a']=(f'**우리는 왜 서로에게 끌렸을까요?**\n\n'
        f'당신은 **{sa["stem"]}({STEM_NAME[sa["stem"]]})**, 상대방은 **{sb["stem"]}({STEM_NAME[sb["stem"]]})**의 일간을 가졌어요. '
        f'당신에게는 {sa["desc"][2]}, 상대방에게는 {sb["desc"][2]}이라는 관계의 이미지가 있어요.\n\n'
        f'◆ **서로 다른 두 사람의 기준**\n{dynamic}')
    result['crisis']=(f'◆ **서로 좋아해도 의견이 다를 때**\n\n'
        f'◆ **작품에서 갈등이 생긴 이유**\n{source_tension}\n\n'
        f'◆ **우리의 평범한 하루라면**\n{everyday}\n\n'
        f'**{tension}**')
    result['tip']=(f'◆ **비슷한 상황에서 해 볼 일**\n\n'
        f'◆ **첫 번째 선택 — 대화를 시작하기**\n{source_action}\n\n'
        f'◆ **두 번째 선택 — 작은 실천으로 옮기기**\n{action}\n\n'
        f'◆ **세 번째 선택 — 함께 정하기**\n'
        '각자 바라는 것을 한 문장씩 말하고, 이번 주 실천할 작은 약속 하나를 함께 골라 보세요. '
        '다음에는 지켰는지 채점하기보다 어떤 순간이 편안했는지 나눠요.\n\n'
        '서로의 답을 미리 정하지 않고, 직접 듣는 것에서 시작해요.')
    result['ending']='이번 주에 같이 해 볼 일 하나를 정하고, 해 본 뒤 서로 어땠는지 이야기해 보세요.'
    result['questions']=[question]
    result['chapters']=[
        {'key':'roles','title':f'우리는 왜 {characters}일까?'},
        {'key':'story','title':f'{characters}은 어떤 이야기를 남겼을까?'},
        {'key':'saju_a','title':'우리는 왜 서로에게 끌렸을까?'},
        {'key':'crisis','title':'그런데 왜 사랑하면서도 어긋날까?'},
        {'key':'tip','title':'우리는 다른 결말을 만들 수 있을까?'},
    ]
    # The final edition used to erase all score-band and chart-specific prose.
    # Restore those reader-facing distinctions after composing the source story.
    from other_reports import AXIS_TEXT, ADVICE, LABELS
    from editorial_readings import READINGS
    result['story'] += '\n\n' + READINGS[cid]
    from c06_report import band
    for key, axes in (('saju_a', ('attraction','security','growth')),
                      ('crisis', ('conflict','expression','autonomy'))):
        result[key] += '\n\n' + '\n\n'.join(
            f'◆ **{LABELS[axis]}**\n{AXIS_TEXT[axis][band(rel["vector"][axis])]}' for axis in axes)
    result['tip'] += '\n\n' + '\n\n'.join(ADVICE[axis][band(rel['vector'][axis])]
        for axis in ('attraction','security','growth','conflict','expression','autonomy'))
    from personalized_reading import enrich as personalize
    result = personalize(result, a, b, rel, couple)
    if cid == 'c03':
        from ondal_reading import revise
        revise(result, left, right, sl, sr, rel['vector'])
    if couple.get('relationship_kind') == 'friendship':
        result['roles'] = result['roles'].replace('사랑의 크기', '친밀함의 크기')
        result['crisis'] = result['crisis'].replace('사랑하면서도', '가까운데도')
        for chapter in result['chapters']:
            chapter['title'] = chapter['title'].replace('사랑하면서도', '가까운데도')
        for key in ('story','saju_a','crisis','tip'):
            result[key] = result[key].replace('사랑에는', '동행에는').replace('데이트', '만남').replace('애정 표현', '마음을 전하는 방법')
    result['sections']=['roles','story','saju_a','crisis','tip']
    return result

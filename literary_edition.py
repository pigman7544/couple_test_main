"""Five-chapter literary edition for non-Baek, non-Chunhyang matches.

Literary events come from the existing curated SCENES, not from the chart.
The birth-chart symbolism is an interpretive analogy, never a prediction.
"""
from individual_scenes import SCENES
from story_report import relationship_style, STEM_NAME, elem, GEN, CTRL

# Each archetype has its own moral tension, everyday conflict, and actionable ending.
EDITION = {
'c02': ('견우와 직녀', '서로 떨어져 있는 날에도 사랑은 어떻게 이어질까요?',
 '견우와 직녀는 만나는 하루만으로 사랑을 설명할 수 없는 사람들이에요. 기다리는 동안에도 각자 살아 내야 할 하루가 있었으니까요.',
 '한쪽은 기다림을 믿음의 표시로 여기지만, 다른 한쪽은 오늘의 안부가 없으면 외로워질 수 있어요. 둘 다 사랑하지만 시간을 견디는 방식은 다를 수 있죠.',
 '연락이 뜸한 날, “바빠서 그랬어”라는 설명이 “나는 네 하루가 궁금했어”라는 마음을 놓칠 수 있어요.',
 '만날 날짜뿐 아니라 떨어져 있는 날의 연락 방식을 함께 정해요. 답장이 늦을 때는 마음을 추측하기보다 가능한 시간을 물어봐요.',
 '서로 떨어져 있을 때 가장 듣고 싶은 한마디는 무엇일까요?'),
'c03': ('온달과 평강공주', '사랑하는 사람의 가능성을 믿는다는 건 무엇일까요?',
 '평강은 남들이 붙인 이름 너머의 온달을 보았어요. 그러나 온달 역시 자기 힘으로 배우고 선택했죠. 두 사람 모두 이야기의 주인공이에요.',
 '응원은 상대를 내 계획에 맞춰 고치는 일이 아니에요. 상대가 원하는 성장과 내가 기대하는 성공이 다를 수도 있으니까요.',
 '새로운 도전을 이야기하는 자리에서 “그렇게 해야 잘될 거야”라는 조언이 “내 선택을 믿어 줘”라는 바람과 부딪힐 수 있어요.',
 '도움이 필요한지 먼저 물어보고, 결과와 상관없이 지금 고마운 점을 말해요. 상대의 목표는 상대가 정하도록 남겨 둬요.',
 '내가 바라는 변화와 네가 바라는 변화는 어디에서 다를까요?'),
'c10': ('로미오와 줄리엣', '뜨거운 마음을 지키면서도 선택할 여유를 남길 수 있을까요?',
 '두 사람은 빠르게 사랑에 빠졌지만, 가문의 다툼과 비밀은 서로 확인할 수 있는 길을 좁혔어요. 비극을 만든 것은 사랑의 부족함만이 아니었죠.',
 '서로에게만 집중하는 마음은 아름답지만, 위기에서 도움을 구할 통로까지 닫아서는 안 돼요. 절박함은 때로 선택지를 실제보다 적게 보이게 하니까요.',
 '주변의 반대가 생긴 날, 한 사람은 당장 결론을 내리고 싶고 다른 사람은 상황을 더 알아보고 싶을 수 있어요.',
 '감정이 가장 격한 날에는 돌이키기 어려운 결정을 미뤄요. 반대의 이유가 편견인지 실제 걱정인지 나누어 듣고, 믿을 만한 도움을 남겨 둬요.',
 '우리가 급해질 때 서로에게 만들어 줄 수 있는 여유는 무엇일까요?'),
'c11': ('엘리자베스와 다아시', '처음의 판단을 고쳐 쓸 용기도 사랑일까요?',
 '엘리자베스와 다아시는 서로를 잘못 읽었어요. 편지와 실제 행동을 통해 첫인상을 다시 살핀 뒤에야 상대의 다른 모습을 볼 수 있었죠.',
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
    result['roles']=(f'**당신들은 {characters}의 이야기를 닮았어요.**\n\n'
        f'{portrait}\n\n'
        f'◆ **{left}에게서 읽는 {first}의 모습**\n'
        f'{left}의 일간은 **{sl["stem"]}({STEM_NAME[sl["stem"]]})**이에요. '
        f'{sl["desc"][0]}이라는 자연의 비유를 통해 {sl["desc"][2]}을 중요하게 여기는 모습을 상상해 볼 수 있어요. '
        f'{first}의 선택을 그대로 반복한다는 뜻은 아니에요.\n\n'
        f'◆ **{right}에게서 읽는 {second}의 모습**\n'
        f'{right}의 일간은 **{sr["stem"]}({STEM_NAME[sr["stem"]]})**이에요. '
        f'{sr["desc"][0]}이라는 상징에서는 {sr["desc"][2]}을 떠올릴 수 있어요. '
        f'두 사람이 다른 방식으로 관계를 지탱한다는 점에 주목해 봐요.\n\n'
        f'**두 역할은 사랑의 크기나 성별이 아닌, 서로 다른 선택을 살피기 위한 문학적 비유예요.**')
    result['story']=(f'**{central}**\n\n'
        f'◆ **이야기 속 두 사람**\n{origin}\n\n'
        f'◆ **이 이야기를 오늘 읽는 이유**\n{tension}\n\n'
        '※ 원전의 사건과 오늘의 관계에 적용한 해석은 구별해 읽어 주세요. 전승과 판본에 따라 세부가 다를 수 있어요.')
    ea,eb=elem(a),elem(b)
    if ea==eb: dynamic='두 사람의 일간은 같은 오행이에요. 비슷한 언어로 이해하기 쉬울 수 있지만, 같은 고집이 부딪힐 수도 있어요.'
    elif GEN[ea]==eb or GEN[eb]==ea: dynamic='두 일간은 상생의 관계예요. 서로를 북돋는 이미지지만, 도움을 주는 역할이 한쪽에만 쏠리지 않는지 살펴봐요.'
    else: dynamic='두 일간은 상극의 관계예요. 이를 불행의 예언으로 보지 않고, 서로 다른 기준이 만나는 장면으로 읽을 수 있어요.'
    result['saju_a']=(f'**우리는 왜 서로에게 끌렸을까요?**\n\n'
        f'당신은 **{sa["stem"]}({STEM_NAME[sa["stem"]]})**, 상대방은 **{sb["stem"]}({STEM_NAME[sb["stem"]]})**의 일간을 가졌어요. '
        f'당신에게는 {sa["desc"][2]}, 상대방에게는 {sb["desc"][2]}이라는 관계의 이미지가 있어요.\n\n'
        f'◆ **서로 다른 두 자연의 이미지**\n{dynamic}\n\n'
        '◆ **상징을 현실과 구별하기**\n오행의 관계가 실제 두 사람의 감정이나 행동을 결정하지는 않아요. 다름을 확인할 때는 서로의 경험과 말에 귀 기울여 주세요.\n\n'
        '사주는 사람의 실제 성격이나 미래를 판정하지 않아요. 이 비유가 자신의 경험과 맞지 않는다면 실제로 나눈 이야기를 더 중요하게 생각해 주세요.')
    result['crisis']=(f'**그런데 왜 사랑하면서도 어긋날까요?**\n\n'
        f'◆ **작품이 보여 준 균열**\n{source_tension}\n\n'
        f'◆ **우리의 평범한 하루라면**\n{everyday}\n\n'
        f'**{tension}**\n\n'
        '이 장면은 실제 두 분이 겪은 사건이 아니라, 서로의 마음을 이야기하기 위한 가상 상황이에요.')
    result['tip']=(f'**우리는 다른 결말을 만들 수 있을까요?**\n\n'
        f'◆ **첫 번째 선택 — 대화를 시작하기**\n{source_action}\n\n'
        f'◆ **두 번째 선택 — 작은 실천으로 옮기기**\n{action}\n\n'
        f'◆ **세 번째 선택 — 함께 정하기**\n'
        '각자 바라는 것을 한 문장씩 말하고, 이번 주 실천할 작은 약속 하나를 함께 골라 보세요. '
        '다음에는 지켰는지 채점하기보다 어떤 순간이 편안했는지 나눠요.\n\n'
        '서로의 답을 미리 정하지 않고, 직접 듣는 것에서 시작해요.')
    result['ending']='책 속 인물의 이야기는 여기까지지만, 우리 둘의 다음 장면은 오늘의 대화에서 시작돼요.'
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
    if not a.get('hour_pillar') or not b.get('hour_pillar'):
        result['roles'] += '\n\n출생시간을 모르는 사람의 시주는 계산에서 제외했어요.'
    if couple.get('relationship_kind') == 'friendship':
        result['roles'] = result['roles'].replace('사랑의 크기', '친밀함의 크기')
        result['crisis'] = result['crisis'].replace('사랑하면서도', '가까운데도')
        for chapter in result['chapters']:
            chapter['title'] = chapter['title'].replace('사랑하면서도', '가까운데도')
        for key in ('story','saju_a','crisis','tip'):
            result[key] = result[key].replace('사랑에는', '동행에는').replace('데이트', '만남').replace('애정 표현', '마음을 전하는 방법')
    result['sections']=['roles','story','saju_a','crisis','tip']
    return result

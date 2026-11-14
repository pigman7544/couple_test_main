"""Five-chapter editorial reports for the ten remaining archetypes.

No change to matching or saju calculations. Existing couple metadata supplies
individual story beats; the thematic lens is specific to each work.
"""
from c06_report import band
from individual_scenes import SCENES
from editorial_readings import READINGS
from story_report import relationship_style, count_elements, STEM_NAME, GOD_TEXT, KO

LENSES = {
 'c02': ('기다림과 재회의 약속', '만날 수 없는 시간에도 관계를 이어 가는 방법', '견우와 직녀', '만남이 드물다고 마음까지 멀어진 것은 아니에요. 하지만 그리움을 표현하지 않으면 서로 다른 이야기를 상상할 수도 있어요.', '재회가 특별한 만큼 평소의 안부도 중요해요.', '거리와 사정 때문에 함께하지 못하는 시간을 사랑의 부족함으로 해석하지 마세요.'),
 'c03': ('서로의 가능성을 알아보는 사랑', '평가받던 사람이 자기 길을 찾는 순간', '온달과 평강공주', '서로의 잠재력을 알아보는 관계예요. 다만 응원과 상대를 내 뜻대로 바꾸려는 일은 구분해야 해요.', '가능성을 믿되 성취를 사랑의 조건으로 삼지 마세요.', '평강의 선택을 일방적인 희생으로, 온달의 성장을 한 사람의 공으로만 설명하지 마세요.'),
 'c10': ('열정과 주변 세계의 충돌', '서로를 향한 마음과 위험한 선택의 경계', '로미오와 줄리엣', '빠른 끌림이 큰 용기를 줄 수 있어요. 하지만 절박한 감정이 안전한 판단을 대신하지는 못해요.', '서로를 지키는 선택은 둘의 세계를 좁히지 않는 선택이에요.', '원작의 비극을 운명적인 사랑의 모범이나 현실의 행동 지침으로 미화하지 마세요.'),
 'c11': ('오해를 넘어 다시 읽는 사랑', '첫인상을 고쳐 쓸 수 있는 용기', '엘리자베스와 다아시', '서로를 빠르게 판단할수록 놓치는 모습이 생겨요. 상대를 새롭게 이해할 여지가 관계를 바꿔요.', '잘못 알았던 부분을 인정하는 일도 애정 표현이에요.', '편견과 계급 차이를 단순한 말다툼으로 축소하지 마세요.'),
 'c13': ('긴 기다림과 전략적 신뢰', '각자의 자리에서 지킨 삶과 재회', '오디세우스와 페넬로페', '믿음은 아무것도 묻지 않는 일이 아니에요. 긴 시간 뒤 다시 만났을 때 서로를 확인할 권리도 포함해요.', '함께 있지 못한 시간에도 각자의 삶을 존중해요.', '페넬로페를 수동적인 기다림의 상징으로만 읽지 마세요.'),
 'c18': ('이상화와 현실의 간극', '기억 속 사랑과 지금의 상대를 구분하기', '개츠비와 데이지', '강렬한 그리움은 때로 현재의 상대보다 과거의 이미지를 더 크게 만들어요.', '사랑했던 기억보다 지금 서로가 원하는 삶을 확인해요.', '파멸과 집착을 깊은 사랑의 증거로 포장하지 마세요.'),
 'f01': ('추론과 공감의 상호보완', '다른 재능이 만나 하나의 팀이 되는 방식', '셜록 홈즈와 존 왓슨', '한 사람의 날카로운 판단과 다른 사람의 꾸준한 동행이 서로를 빛나게 할 수 있어요.', '상대의 기여가 눈에 잘 띄지 않아도 말로 인정해요.', '왓슨을 단순한 조수로만 취급하지 마세요.'),
 'f02': ('이상과 현실의 동행', '다르게 보는 두 사람이 함께 길을 가는 법', '돈키호테와 산초 판사', '한 사람은 가능성을 크게 그리고 다른 사람은 발밑의 길을 살펴요. 두 시선이 만나면 모험이 달라져요.', '꿈을 비웃지 않고 위험은 함께 점검해요.', '위험한 판단을 낭만적인 도전으로 정당화하지 마세요.'),
 'f03': ('진가를 알아보는 오래된 신뢰', '결과보다 사람의 사정을 먼저 알아보는 관계', '관중과 포숙아', '서로의 사정을 이해하려는 마음은 신뢰를 깊게 해요. 하지만 무조건 감싸는 일과 이해는 달라요.', '상대의 능력을 인정하되 대신 결정하지 마세요.', '전승된 고사를 확인된 모든 역사적 사실로 단정하지 마세요.'),
 'f04': ('경쟁을 넘어 서로를 변화시키는 사랑', '맞서는 힘이 서로를 바꾸는 계기', '길가메시와 엔키두', '처음에는 부딪히던 두 사람이 서로의 삶을 넓혀 줄 수도 있어요. 다름을 이겨야 할 대상으로만 보지 마세요.', '서로에게 배운 점을 살아 있는 동안 표현해요.', '상실과 죽음을 관계의 성숙을 위한 필수 조건처럼 말하지 마세요.'),
}
AXES = ('attraction','security','growth','conflict','expression','autonomy')
LABELS = {'attraction':'끌림과 호기심','security':'신뢰와 안정','growth':'함께하는 성장','conflict':'차이를 다루는 방식','expression':'마음의 표현','autonomy':'각자의 선택'}
# Independent low/mid/high branches for every axis, shared calculation and
# archetype-specific story lens. No random or external generation.
AXIS_TEXT = {
 'attraction': ('천천히 마음이 열리는 흐름이에요. 상대의 의외의 모습을 알아갈 시간을 남겨 두세요.',
                '호기심과 익숙함이 함께 자라는 흐름이에요. 처음과 달라진 매력을 발견해 보세요.',
                '강한 끌림이 느껴지는 상징이에요. 다만 설렘이 곧 서로를 다 안다는 뜻은 아니에요.'),
 'security': ('확신을 서두르기보다 작은 약속부터 쌓아 가는 편이 좋아요.',
              '신뢰를 만들 여지가 있어요. 서로가 안심하는 행동이 무엇인지 물어보세요.',
              '안정감의 상징이 두드러져요. 익숙함 때문에 고마움을 생략하지는 마세요.'),
 'growth': ('상대의 변화를 요구하기보다 지금의 선택을 응원하는 것부터 시작해요.',
            '서로 다른 목표가 배움의 계기가 될 수 있어요. 성취의 속도를 비교하지 마세요.',
            '서로에게 새로운 시야를 열어 줄 수 있어요. 격려가 압박이 되지 않게 조심해요.'),
 'conflict': ('큰 다툼이 없더라도 작은 서운함은 쌓일 수 있어요. 가볍게 확인해 보세요.',
             '의견 차이를 조율할 여지가 있어요. 각자가 지키려는 기준을 먼저 들어 보세요.',
             '부딪힘이 두드러지는 상징이에요. 이기려는 말보다 이해하려는 질문이 필요해요.'),
 'expression': ('마음을 짐작에 맡기지 말고 짧게라도 직접 전해 보세요.',
                '표현의 방식이 서로 다를 수 있어요. 듣고 싶은 말을 알려 주세요.',
                '감정을 나눌 통로가 열려 있어요. 상대가 대답할 공간도 남겨 두세요.'),
 'autonomy': ('함께하는 시간이 소중해도 혼자 쉴 권리를 확인해 주세요.',
              '함께할 일과 각자 결정할 일을 나눠 보는 게 좋아요.',
              '독립적인 선택을 존중할 여지가 커요. 중요한 순간에는 다시 연결되는 약속도 필요해요.'),
}
ADVICE = {
 'attraction': ('함께 새롭게 해 볼 일을 하나 정해 보세요.', '서로에게 새롭게 발견한 장점을 하나씩 말해 보세요.', '끌리는 이유와 아직 잘 모르는 점을 하나씩 나눠 보세요.'),
 'security': ('이번 주 꼭 지킬 수 있는 작은 약속을 정해 보세요.', '상대가 안심했던 행동을 구체적으로 물어보세요.', '당연하게 여겼던 배려 하나를 고맙다고 말해 보세요.'),
 'growth': ('상대가 요즘 배우고 싶은 것을 물어보세요.', '서로의 목표를 평가하지 말고 필요한 도움을 물어보세요.', '상대의 도전을 응원하되 결정은 상대에게 맡겨 보세요.'),
 'conflict': ('사소한 불편을 쌓아 두지 말고 한 가지씩 이야기해 보세요.', '다른 의견이 나왔을 때 각자의 우선순위를 먼저 확인해 보세요.', '설득하기 전에 서로의 말을 한 문장으로 다시 말해 보세요.'),
 'expression': ('고마운 일을 하나 구체적으로 말해 보세요.', '서로 듣고 싶은 표현을 하나씩 알려 주세요.', '상대의 말을 끊지 않고 끝까지 들어 보세요.'),
 'autonomy': ('각자 쉬는 시간을 정하고 다시 만날 시간도 약속해 보세요.', '함께 정할 일과 혼자 결정할 일을 구분해 보세요.', '상대의 선택을 대신하지 않고 먼저 물어보세요.'),
}

def enrich(result, a, b, rel, couple):
    cid=couple['id']
    if cid not in LENSES:
        return result
    theme, question, characters, hook, takeaway, caution = LENSES[cid]
    # Friendship stories are analogies for patterns within romantic couples.
    bond = '사랑'
    first, second = couple['name'].split('·', 1)
    x,y=relationship_style(a),relationship_style(b)
    counts_a,counts_b=count_elements(a),count_elements(b)
    def strength(p,style,counts):
        return counts['earth']+counts['metal']+(1 if style['god'] in ('정관','정재','비견') else 0)
    a_first=strength(a,x,counts_a)>=strength(b,y,counts_b)
    p,q=('당신','상대방') if a_first else ('상대방','당신')
    sx,sy=(x,y) if a_first else (y,x)
    cp,cq=(counts_a,counts_b) if a_first else (counts_b,counts_a)
    def profile(label,name,style,counts):
        from reading_voice import profile as reader_profile
        return f'◆ **{label}에게 비춰 보는 {name}의 시선**\n' + reader_profile(label, style, counts, name == first)
    if cid.startswith('f'):
        hook = '이 원작은 우정의 이야기지만, 여기서는 연인 사이에 나타나는 협력·신뢰·차이의 양상을 비춰 보는 거울로 사용해요. ' + hook
        question = '연인 사이에서 ' + question
        takeaway = '원작의 두 사람은 친구였어요. 그 관계의 특징을 연인 사이의 사랑에 비춰 보면, ' + takeaway
    result['tagline']=theme
    result['teaser']=hook
    result['roles']=(f'**왜 우리는 {characters}의 이야기와 닮았을까요?**\n'
                     f'{bond}의 핵심을 {question}이라는 질문으로 읽어 볼게요. '
                     f'두 사람을 성별이 아닌 나를 상징하는 글자와 태어난 달의 글자, 자연의 이미지로 배역에 비춰 봤어요. '
                     f'{p}은 {first}, {q}은 {second}의 시선에서 읽어요.\n\n'
                     +profile(p,first,sx,cp)+'\n\n'+profile(q,second,sy,cq)
                     +'\n\n이 역할은 상징적인 비교예요. 누가 더 많이 사랑하거나 더 훌륭한지를 가리는 기준이 아니에요. '
                     +'자연 이미지의 개수만으로 기운의 강약을 정하지 않으며, 동점은 입력 순서로 정했어요. '
                     +('출생시각을 모르면 시주는 계산에서 제외했어요. 시주는 태어난 시간을 나타내는 글자예요.' if not a.get('hour_pillar') or not b.get('hour_pillar') else ''))
    beats=couple.get('story_beats',[])
    headings=('이야기의 시작','서로 다른 선택','끝내 남은 장면')
    blocks=[]
    for i,beat in enumerate(beats):
        blocks.append(f'◆ **{headings[i] if i<3 else "이어지는 이야기"}**\n{beat["summary"]} '
                      + (('이 장면에서 눈여겨볼 것은 단순한 사건보다 두 사람이 서로에게 어떤 선택을 요구받았는지예요.' if i==0 else
                          '그 선택은 관계를 더 단단하게 만들 수도, 서로의 차이를 선명하게 드러낼 수도 있어요.' if i==1 else
                          '이 결말을 지금 두 사람의 미래에 그대로 대입할 필요는 없어요.')))
    original_scene, tension, action = SCENES[cid]
    result['story']='\n\n'.join(blocks)+f'\n\n◆ **작품 속에서 더 읽어 볼 장면**\n{original_scene}\n\n**{question}**\n{takeaway} {caution} 작품과 고사의 세부는 판본과 전승에 따라 다를 수 있어요.'
    result['story'] += '\n\n' + READINGS[cid]
    v=rel['vector']
    def axis(key):
        score=v[key];i=band(score)
        return f'◆ **{LABELS[key]}**\n{AXIS_TEXT[key][i]}'
    result['saju_a']=(f'두 사람의 관계를 {theme}이라는 관점에서 읽어 볼게요. '
                      f'당신에게는 {x["desc"][2]}, 상대방에게는 {y["desc"][2]}이 중요하다는 상징으로 해석할 수 있어요.\n\n'
                      +'\n\n'.join(axis(k) for k in ('attraction','security','growth'))
                      +'\n\n사주의 상징을 빌린 이야기이며, 실제 감정이나 미래를 확정하지 않아요.')
    result['crisis']=(f'**{question}**\n{hook}\n\n{tension}\n\n'
                      +'\n\n'.join(axis(k) for k in ('conflict','expression','autonomy'))
                      +f'\n\n{caution} 서사 속 갈등을 현실의 위험한 행동과 동일시하지 않아요.')
    result['tip']=(f'**이번 주, {bond}을 지키는 작은 실천**\n{takeaway}\n\n◆ **{characters}에게서 배운 한 가지**\n{action}\n\n'
                   +'\n\n'.join(f'◆ **{LABELS[k]}**\n{ADVICE[k][band(v[k])]}' for k in ('security','expression','autonomy','conflict','growth','attraction')))
    result['ending']=f'{bond}의 결말은 이야기처럼 정해져 있지 않아요. 오늘 두 사람이 함께 선택해요.'
    result['questions']=[question, '상대에게 아직 물어보지 못한 마음은 무엇인가요?', action]
    result['sections']=['roles','story','saju_a','crisis','tip']
    result['chapters']=[{'key':k,'title':t} for k,t in zip(result['sections'],[
        f'우리는 왜 {characters}일까요?',
        f'{characters}의 이야기는 무엇을 남겼을까요?',
        f'우리 관계의 {theme}은 어떤 모습일까요?',
        '서로 다른 마음은 어디에서 부딪힐까요?',
        '우리는 어떤 선택을 함께할까요?',
    ])]
    return result

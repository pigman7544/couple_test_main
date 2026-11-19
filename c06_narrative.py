"""White Snake live report and historical comparison helpers."""
from c06_chart import GROUP

GOD_MEANING = {
 'reflect':'마음을 안에서 살피고 충분히 이해하려는 모습',
 'care':'필요한 것을 챙기고 마음을 생활 속 행동으로 옮기는 모습',
 'voice':'느낌과 생각을 말과 행동으로 나누려는 모습',
 'promise':'지킬 수 있는 약속과 분명한 기준을 찾는 모습',
 'self':'자기 뜻을 지키면서 나란히 서려는 모습',
}
def block(title,text):
    return f'◆ **{title}**\n{text}'

def particle(word,consonant,vowel):
    return consonant if (ord(word[-1])-0xAC00)%28 else vowel

def basis(label,x):
    """Previous editorial reading, retained for historical comparison tests."""
    from story_report import STEM_NAME, STEM_DESC
    stem=x['pillars']['day_pillar'][0]; desc=STEM_DESC[stem]
    month=GROUP[x['anchors']['month']]; day=GROUP[x['anchors']['day']]
    s=(f"{label}의 일간은 **{STEM_NAME[stem]}({stem})**이에요. 사주에서 자신을 상징하는 글자로, {desc[0]}에 비유할 수 있어요."
       f"\n\n가까운 사이에서는 {desc[2]}{particle(desc[2],'을','를')} 중요하게 여길 수 있어요. {desc[3]}{particle(desc[3],'이','가')} 있으면 마음이 놓일 수 있어요. ")
    seasonal={'reflect':'마음을 서둘러 꺼내기보다 충분히 이해한 뒤 말하고 싶은 신중한 면도 볼 수 있어요. 대답이 늦어지는 날에도 속에서는 할 말을 오래 고르고 있을 수 있죠.',
              'care':'마음이 쓰이면 필요한 것을 챙기는 손길이 먼저 나갈 수 있어요. 바쁜 날 먹을 것을 챙기거나 만날 시간을 비워 두는 식으로요.',
              'voice':'좋았던 일도 속상했던 일도 함께 나누고 싶은 마음도 생길 수 있어요. 하루 끝에 주고받는 짧은 이야기가 유난히 반가울 수 있죠.',
              'promise':'약속을 가볍게 넘기고 싶지 않은 마음도 생길 수 있어요. 언제 만날지, 어디까지 함께할 수 있을지 분명해질수록 편안해질 수 있죠.',
              'self':'좋아하는 사람 곁에서도 자기 뜻을 지키고 싶은 마음도 생길 수 있어요. 서로 다른 취향을 말할 수 있을 때 함께 있는 시간도 편안해질 수 있죠.'}
    s+=f"월주(태어난 달의 글자)에서 관계의 또 다른 특징을 살펴볼 수 있어요. "+seasonal[month]
    if day!=month:
        s+=' 일주의 아래 글자도 함께 살펴봤어요. '+{'reflect':'가까워질수록 혼자 생각을 정리할 시간도 소중해질 수 있어요.',
                 'care':'가까운 사람에게는 말보다 작은 수고로 마음을 전하고 싶어질 수 있어요.',
                 'voice':'마음이 놓이는 사람 앞에서는 사소한 감정도 말로 나누고 싶어질 수 있어요.',
                 'promise':'친밀한 사이일수록 작은 약속을 지키는 일이 오래 마음에 남을 수 있어요.',
                 'self':'함께할 일을 정할 때 자신의 의견도 존중받고 싶을 수 있어요.'}[day]
    if x['theme']!=month:
        s+=' '+{'care':'그 마음은 만나기 전 동선과 식사를 미리 챙기는 정성으로도 이어질 수 있어요.',
                 'reflect':'그래도 중요한 대답 앞에서는 잠시 멈춰 자신의 마음부터 헤아리고 싶을 수 있어요.',
                 'voice':'쌓아 둔 마음은 일상의 작은 이야기를 주고받으며 조금씩 드러날 수 있어요.',
                 'promise':'그 마음이 오래 이어지려면 서로 지킬 수 있는 약속이 필요하겠죠.',
                 'self':'그 안에서도 직접 고르고 결정하고 싶은 마음은 남아 있어요.'}[x['theme']]
    # Describe only computed stem relationships. Do not infer childhood, family
    # history, future events, or qi strength from a pillar's position.
    year=GROUP[x['visible_gods']['year_pillar']]
    s+='\n\n태어난 해인 연주의 겉글자를 일간과 함께 읽으면 '+GOD_MEANING[year]+'도 보여요.'
    if not x['missing_hour']:
        hour=GROUP[x['anchors']['hour']]
        if hour==year:
            s+=' 태어난 시간의 시주에서도 같은 상징이 이어져요.'
        else:
            s+=' 태어난 시간의 시주에는 '+GOD_MEANING[hour]+'도 있어요.'
    return s

def compose(result, a, b):
    from c06_report import TALE, TITLES
    from report_evidence import profiles
    from story_report import role_assignment

    lead, _, pa, pb = role_assignment(a, b)
    labels = ('당신', '상대방') if lead == '첫 번째 사람' else ('상대방', '당신')
    people = tuple((label, person['day_pillar'][0]) for label, person in zip(labels, (pa, pb)))
    result['roles'] = profiles('c06', ('백소정', '허선'), people)
    result['tagline'] = '서로를 이해하며 함께 살아가는 사랑'
    result['teaser'] = '허선은 백소정에게 우산을 빌려주고, 두 사람은 함께 약방을 꾸려요. 서로를 돕던 사이에 뒤늦게 알게 된 사실이 두 사람을 흔들어요.'
    result['story'] = TALE
    result['saju_a'] = (
        '허선이 우산을 건넬 때는 백소정에게 무엇이 필요한지 눈앞에 보였어요. 약방을 함께 꾸릴 때는 두 사람의 생활에 무엇이 필요한지 계속 이야기해야 했어요. '
        '처음에는 뜻이 잘 맞는다고 느껴도 함께하는 일이 많아지면, 어느 쪽이 먼저 결정해도 되는지 서로 다르게 생각할 수 있어요.\n\n'
        '우산을 빌려준 일 뒤에는 물건을 돌려주며 다시 만날 기회가 있었어요. 약방을 함께 꾸리는 일은 서로의 하루에 계속 시간을 내는 선택으로 이어져요. '
        '처음에 고마웠던 행동을 자주 해 주고 싶다면, 그때 상대가 반가워한 게 어떤 부분이었는지 물어볼 수 있어요. 준비해 준 일 자체가 반가웠을 수도 있고, 필요한 순간에 먼저 물어봐 준 게 더 고마웠을 수도 있어요.\n\n'
        '두 사람 가운데 한 사람이 일찍 퇴근하는 날 저녁을 준비한다고 생각해 봐요. 예전에는 상대가 반갑게 먹었지만, 오늘은 늦게 돌아와 잠시 쉬고 싶을 수도 있어요. '
        '고마운 마음을 전하면서 언제 함께 먹을 수 있는지 말하면, 준비한 사람도 자기 저녁 시간을 정할 수 있어요.\n\n'
        '백소정과 허선이 약방을 꾸린다는 것은 큰 결정을 한 번 함께 내리는 일이면서, 손님을 맞고 가게 일을 나누는 작은 결정의 시작이었어요. '
        '두 분에게도 각자 해도 편한 일과 함께 정해야 편한 일이 있을 거예요. 상대도 시간을 내야 하는 일이라면 미리 물어봐 주세요.'
    )
    result['crisis'] = (
        '허선은 백소정에 관해 미처 알지 못한 사실을 접하고 크게 흔들려요. 지금까지 함께 살아온 경험도 있고 당장 이해하기 어려운 일도 생겼어요. '
        '가까운 사람이 낯선 이야기를 꺼낸다면, 그 자리에서 대답을 다 정리하기 어려울 수 있어요.\n\n'
        '단오 이야기를 전하는 판본에서는 백소정이 직접 설명할 기회를 얻기 전에 허선이 그 모습을 보게 돼요. '
        '그때 허선이 알게 된 일과 백소정에게 설명할 기회가 있었는지는 따로 생각할 수 있어요. 오늘의 관계에서 중요한 일을 뒤늦게 알았다면, '
        '그 일 자체가 받기 어려운 이야기였는지, 의논할 기회 없이 알게 된 게 더 서운했는지 상대에게 말해 봐요. 어느 쪽인지에 따라 다음에 함께 다룰 내용이 달라져요.\n\n'
        '이야기를 꺼낸 쪽은 대답이 늦어지면 상대가 더 듣고 싶어 하는지부터 궁금해요. 듣는 쪽은 생각을 정리할 시간이 필요한데 계속 대답을 재촉받으면 자기 말을 고르기 어려워져요. '
        '서로 다음 대화가 언제 이어질지 정해 두면 한 사람은 하고 싶은 말을 정리하고 다른 사람은 얼마나 기다릴지 알 수 있어요.\n\n'
        '다시 이야기할 때는 내가 직접 들은 말부터 확인해요. “아까 그 얘기는 오늘 처음 알게 됐어. 내가 이해한 게 맞는지 한번 들어 줄래?”라고 물으면 '
        '시간을 내어 생각한 뒤에도 서로 다른 뜻으로 이해한 부분을 바로잡을 수 있어요.'
    )
    result['tip'] = (
        '도움을 건네고 싶을 때는 먼저 내가 맡을 수 있는 일을 제안해요. “저녁을 준비할 수 있어. 같이 먹을 수 있는 시간은 언제야?”라고 물으면 '
        '준비할 사람과 준비를 받는 사람이 각각 자기 사정을 말할 자리가 생겨요.\n\n'
        '중요한 이야기를 듣다가 시간을 더 쓰고 싶다면 무엇을 다시 이야기할지와 가능한 시간을 같이 정해 보세요. '
        '“지금 바로 답하기 어려워. 내일 저녁에 네가 어느 때부터 이 일을 걱정했는지 더 듣고 싶어”처럼 다음 대화에서 알고 싶은 것을 알려 줄 수 있어요.\n\n'
        '다시 만났을 때는 앞에서 들은 말을 한 번 짚고 아직 남은 질문 하나를 꺼내 보세요. 상황이 달라져 정한 시간에 이야기하기 어렵다면 먼저 알려 주세요. '
        '다음에 연락할 시점을 서로 다시 고르면 기다리는 동안 각자의 일을 계속할 수 있어요.\n\n'
        '다음 주에 도움이 필요한 일이 생기면 서로 맡아도 되는 범위를 먼저 정해요. 평소 하던 일은 그대로 해도 좋고, 상대에게 시간이나 비용이 드는 일은 결정하기 전에 물어요. '
        '합의한 방식이 편했는지는 일을 마친 뒤 확인해요. “일정을 먼저 물어봐 줘서 준비하기 편했어”처럼 달라진 말을 짚어 주면 다음에도 같이 쓸 방법을 찾기 쉬워요.'
    )
    result['questions'] = ['상대가 준비한 일에서 무엇이 고마웠나요?', '생각할 시간이 더 필요할 때 언제 다시 이야기하면 좋을까요?']
    result['ending'] = '상대의 이야기를 더 듣고 싶은 부분을 한 가지 말해 보세요.'
    result['sections'] = ['roles', 'story', 'saju_a', 'crisis', 'tip']
    result['chapters'] = [dict(key=key, title=title) for key, title in zip(result['sections'], TITLES)]
    result.update(scene='', saju_b='', chemistry='')
    return result

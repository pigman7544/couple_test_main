"""Reader-facing chart imagery. No calculation or role selection lives here."""
IMAGES = {
    'wood': ('나무', '새로운 가지가 뻗을 자리를 찾는 모습', '다음 데이트에서 처음 가 보는 곳을 제안해 볼 수 있어요'),
    'fire': ('불', '곁에 온기를 나누는 모습', '만나서 반가웠다는 말을 먼저 건네 볼 수 있어요'),
    'earth': ('흙', '매일 돌아올 자리를 가꾸는 모습', '바쁜 날에도 지킬 수 있는 연락 시간을 정해 볼 수 있어요'),
    'metal': ('쇠', '흐트러진 것을 차분히 정리하는 모습', '약속이 바뀌면 무엇부터 다시 정할지 이야기해 볼 수 있어요'),
    'water': ('물', '서두르지 않고 길을 찾아 흐르는 모습', '대답하기 어려운 날에는 생각할 시간부터 부탁해 볼 수 있어요'),
}
GOD_SCENES = {
    '비견': '함께 계획을 짤 때 각자의 의견을 동등하게 놓고 싶을 수 있어요',
    '겁재': '좋아하는 사람과 함께하면서도 내가 고른 일정을 남겨 두고 싶을 수 있어요',
    '식신': '좋아하는 간식을 챙기듯 작은 행동을 꾸준히 이어 가는 모습도 떠올라요',
    '상관': '늘 가던 곳 대신 새로운 데이트를 제안하며 마음을 전할 수도 있어요',
    '편재': '함께 해 보고 싶은 일을 찾는 즐거움이 마음을 표현하는 계기가 될 수 있어요',
    '정재': '만날 시간을 미리 비워 두는 실천으로 마음을 전할 수도 있어요',
    '편관': '계획이 어긋났을 때 해결책을 먼저 찾고 싶을 수도 있어요',
    '정관': '작은 약속도 서로 확인하며 지키는 데 마음이 놓일 수 있어요',
    '편인': '바로 답하기보다 혼자 생각한 뒤 내 말로 설명하는 시간이 편할 수 있어요',
    '정인': '지친 날 조언보다 곁에서 이야기를 들어 주는 배려가 반가울 수 있어요',
}

def profile(label, style, counts, explain=True):
    from story_report import STEM_NAME
    stem = style['stem']
    desc = style['desc']
    dominant = [k for k, value in counts.items() if value == max(counts.values())]
    images = ' · '.join(IMAGES[k][0] for k in dominant)
    scenes = ' '.join(IMAGES[k][2] + '.' for k in dominant)
    element_hanja = dict(wood='木', fire='火', earth='土', metal='金', water='水')
    from relationship_v08 import STEM_ELEM, STEMS
    symbol = stem + element_hanja[STEM_ELEM[STEMS.index(stem)]]
    intro = '오행은 나무·불·흙·쇠·물, 다섯 자연의 이미지로 사주를 읽는 방식이에요. ' if explain else '이쪽의 글자도 같은 다섯 자연 이미지로 살펴볼게요. '
    return (
        f'{label}을 상징하는 사주 글자, 일간은 {STEM_NAME[stem]}({symbol})이에요. '
        f'{desc[0]}을 떠올려 보세요. 가까운 사이에서는 {desc[2]}을 바라는 모습에 비춰 볼 수 있어요. '
        f'이를테면 “{desc[3]}” 같은 배려를 받는 날, 함께하는 시간이 한결 편안할 수 있겠죠.\n\n'
        f'태어난 달의 글자를 함께 읽으면 또 다른 표현 방식도 떠올라요. {GOD_SCENES[style["god"]]}. '
        '앞의 비유와 꼭 같은 모습일 필요는 없어요. 먼저 챙겨 주고 싶은 날에도, 내 마음을 들어 주길 바라는 날이 있으니까요.\n\n'
        + intro +
        f'입력한 글자에서 자주 보이는 이미지는 {images}이에요. {scenes} '
        '이는 두 사람이 대화를 시작할 실마리예요. 실제로 어떤 배려가 좋은지는 서로의 답을 들어 보세요.'
    )

def connection(a, b):
    from story_report import elem
    from relationship_v08 import GEN
    ea, eb = elem(a), elem(b)
    if ea == eb:
        return ('두 사람을 같은 자연의 이미지에 비춰 읽을 수 있어요. 익숙한 표현이 반가울 수 있지만, '
                '같은 방식으로 마음을 전한다고 가정하지는 말아요. 약속을 잡을 때도 각자 편한 시간을 먼저 물어보세요.')
    if GEN[ea] == eb or GEN[eb] == ea:
        source, target = (ea, eb) if GEN[ea] == eb else (eb, ea)
        analogy = {('water','wood'):'비가 나무를 적시듯', ('wood','fire'):'나무가 불을 이어 주듯',
                   ('fire','earth'):'불이 지나간 자리에 재가 흙으로 남듯', ('earth','metal'):'흙이 광물을 품듯',
                   ('metal','water'):'차가운 금속 표면에 물방울이 맺히듯'}[(source,target)]
        return (f'전통 사주에서는 서로를 북돋는 흐름을 상생이라고 불러요. {analogy} 한쪽의 힘이 다른 쪽에 닿는 비유예요. '
                '연락이 뜸한 날 먼저 안부를 묻거나, 망설이는 계획에 응원을 건네는 장면을 떠올려 볼 수 있어요. '
                '다만 챙기는 사람이 늘 같아야 한다는 뜻은 아니에요. 오늘은 누구에게 어떤 도움이 필요한지 물어보세요.')
    return ('전통 사주에서 상극은 서로 다른 힘이 맞닿아 조절되는 흐름을 말해요. 가지를 다듬을 때 남길 부분을 살피듯, '
            '차이를 어떻게 다룰지가 중요하다는 비유로 읽어 볼게요. 데이트 장소를 빨리 정하고 싶은 마음과 '
            '조금 더 찾아보고 싶은 마음이 만난다면, 언제까지 고를지부터 함께 정해 볼 수 있어요. 관계가 나쁘다는 판정은 아니에요.')

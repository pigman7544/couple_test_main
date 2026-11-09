"""Chart-derived modern scenes, kept separate from the unchanged source tale."""
from c06_report import band

# Everyday settings and questions are editorial analogies, never source events.
SETTINGS = {
    'c01': ('기다리던 약속이 미뤄진 저녁', '기다림을 혼자 감당하지 않으려면'),
    'c02': ('서로 다른 일정 사이로 전화를 잡는 밤', '만나지 못하는 날에도 연결되려면'),
    'c03': ('새로운 공부를 시작할지 이야기하는 주말', '응원이 평가가 되지 않으려면'),
    'c06': ('말하기 어려운 고민을 꺼내려는 저녁', '낯선 마음을 의심보다 질문으로 만나려면'),
    'c10': ('둘의 계획에 주변의 반대가 생긴 날', '급한 마음 속에서도 선택할 여유를 지키려면'),
    'c11': ('짧은 메시지를 서로 다르게 읽은 저녁', '첫 판단을 다시 살펴보려면'),
    'c13': ('오랜만에 서로의 일상을 나누는 밤', '익숙한 사람의 달라진 모습을 만나려면'),
    'c18': ('예전에 좋아하던 장소를 다시 찾은 날', '기억보다 지금의 바람을 들으려면'),
    'f01': ('함께 맡은 일의 해결책을 고르는 오후', '판단과 공감이 함께 일하려면'),
    'f02': ('새로운 여행 계획을 펼쳐 놓은 주말', '기대와 현실을 같은 지도에 놓으려면'),
    'f03': ('상대의 실수를 어떻게 도울지 고민하는 날', '이해하면서도 책임을 나누려면'),
    'f04': ('같은 목표를 두고 의견이 맞선 오후', '경쟁 속에서도 서로의 자리를 지키려면'),
}
PACE = {
    'wood': ('새로운 방법을 제안하는', '다음에 시도할 작은 변화'),
    'fire': ('마음을 바로 말로 건네는', '오늘 반가웠던 순간'),
    'earth': ('먼저 생활의 빈틈을 챙기는', '이번 주 지킬 수 있는 약속'),
    'metal': ('무엇을 정할지 분명히 하는', '서로 동의한 결정의 범위'),
    'water': ('여러 가능성을 두고 생각하는', '아직 답을 정하지 못한 마음'),
}
CONFLICT = (
    '둘 다 괜찮다고 넘어가면 대화는 빨리 끝나요. 하지만 편안한 침묵인지, 말할 자리를 놓친 것인지 한 번 더 물을 수 있어요.',
    '한 사람은 지금 결정하고 싶고 다른 사람은 이유를 더 듣고 싶을 수 있어요. 대화가 멈춘 지점을 찾으면 마음 전체를 다툴 필요가 줄어요.',
    '좋은 뜻을 설명할수록 반박이 돌아오는 장면을 상상해 보세요. 그때는 의도를 증명하기보다 오늘 정할 일을 작게 나누는 편이 도움이 될 수 있어요.',
)
EXPRESSION = (
    '“알아서 알겠지” 하고 남겨 둔 마음을 한 문장만 꺼내 보세요. 길게 설명하지 않아도 “지금은 답보다 들어 주는 시간이 필요해”라고 시작할 수 있어요.',
    '“내가 들은 건 이런 뜻인데 맞아?”라고 확인해 보세요. 같은 단어를 쓰고도 서로 다른 기대를 품었는지 알아볼 자리가 생겨요.',
    '말이 잘 이어지는 날에도 각자 마지막 한 문장을 남겨 두세요. 먼저 말한 사람이 답을 채우지 않고 기다릴 때 뒤늦게 떠오른 마음도 나올 수 있어요.',
)
AUTONOMY = (
    '함께할 계획을 정한 뒤 각자 쉬고 싶은 시간도 적어 보세요. 가까이 있고 싶은 마음과 혼자 쉬고 싶은 마음이 한날에 함께 있을 수 있어요.',
    '공동 일정 한 가지와 각자 정할 일정 한 가지를 나눠 보세요. 어디까지 상의할지 먼저 알면 허락을 구하는 대화가 합의하는 대화로 바뀔 수 있어요.',
    '각자의 계획을 먼저 말하고 두 일정이 겹치는 자리에 만남을 놓아 보세요. 자유를 보장하는 일과 다시 연결될 시간을 정하는 일은 함께 할 수 있어요.',
)


def enrich(result, a, b, rel, couple):
    from story_report import relationship_style, count_elements, elem, STEM_NAME
    styles = [relationship_style(p) for p in (a, b)]
    counts = [count_elements(p) for p in (a, b)]
    setting, question = SETTINGS[couple['id']]
    voices = []
    tasks = []
    for label, style, count, chart in zip(('당신', '상대방'), styles, counts, (a, b)):
        element = elem(chart)
        image, prompt = PACE[element]
        dominant = [k for k, value in count.items() if value == max(count.values())]
        # Include all tied dominant elements rather than silently privileging one.
        supports = ' · '.join(PACE[k][1] for k in dominant)
        voices.append(f'{label}의 일간 {STEM_NAME[style["stem"]]}: {image} 모습으로 비춰 볼게요. '
                      f'그 마음이 닿으려면 {style["desc"][3]}이 필요할 수 있어요. '
                      f'겉글자에서 많이 나타난 오행은 {supports}에도 시선을 두게 해요.')
        tasks.append(f'{label}에게: “{prompt}에 관해 내가 바라는 것은…”을 완성해 보세요. '
                     f'상대가 답하면 바로 고치거나 설명하지 말고, 들은 바람 하나를 되짚어 주세요.')
    v = rel['vector']
    result['saju_a'] += '\n\n◆ **두 사람의 상징이 일상에서 만난다면**\n\n' + '\n\n'.join(voices)
    result['crisis'] += (f'\n\n◆ **현실에 비춰 보는 가상 장면 — {setting}**\n'
                         '아래는 원전의 사건이나 두 분이 실제로 겪은 일이 아닌, 출생정보의 상징과 관계 점수로 고른 대화 예시예요. '
                         + CONFLICT[band(v['conflict'])] + '\n\n' + EXPRESSION[band(v['expression'])]
                         + '\n\n' + AUTONOMY[band(v['autonomy'])])
    result['tip'] += (f'\n\n◆ **{question}**\n\n' + '\n\n'.join(tasks)
                      + '\n\n각자의 답에서 이번 주 실제로 할 수 있는 행동을 하나씩 고르세요. '
                      '언제 할지 정한 뒤, 다음 대화에서는 지켰는지를 채점하기보다 어떤 점이 편했고 어려웠는지 나눠 보세요. '
                      '상징이 자신의 경험과 맞지 않는다면, 서로 말해 준 실제 바람을 우선해 약속을 고쳐도 좋아요.')
    return result

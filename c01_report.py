"""Five-chapter Chunhyang report. Editorial saju symbolism, not psychological prediction."""
from c06_report import AXES, band

TITLES = [
    '우리는 왜 춘향과 몽룡일까?',
    '춘향과 몽룡은 어떤 사랑을 했을까?',
    '우리는 왜 서로에게 끌렸을까?',
    '믿고 있는데도 왜 외로울까?',
    '우리의 약속을 어떻게 지킬까?',
]

TALE = """◆ 광한루에서 시작된 선택
남원 부사의 아들 이몽룡은 광한루 근처에서 그네를 타던 춘향을 보고 마음을 빼앗겨요. 두 사람은 서로에게 끌리고 사랑을 약속하죠. 하지만 춘향은 기생 월매의 딸이고 몽룡은 양반가의 자제예요. 신분의 벽이 높은 시대에 그 약속은 설렘만으로 지킬 수 있는 일이 아니었어요.

◆ 함께할 수 없게 된 시간
몽룡은 아버지를 따라 한양으로 떠나게 돼요. 돌아오겠다는 약속을 남기지만 춘향에게는 언제 끝날지 모르는 기다림이 시작되죠. 한 사람은 떠나서 자신의 길을 가고, 다른 사람은 남아서 자기 삶을 지켜야 했어요. 둘의 시간이 다르게 흐르기 시작한 거예요.

◆ 기다림보다 더 어려운 선택
새로 부임한 사또 변학도는 춘향에게 수청을 강요해요. 춘향은 이를 거부하고 옥에 갇혀 고초를 겪죠. 여기서 춘향을 단지 몽룡만 기다린 사람으로 보면 중요한 부분을 놓쳐요. 누구를 사랑하고 어떤 요구를 거절할지는 자신이 결정한다는 뜻을 지킨 인물이기도 하니까요. **춘향의 굳센 마음은 순종이 아니라 선택의 주체성에서 나와요.**

◆ 돌아온 사람이 증명한 약속
몽룡은 과거에 급제한 뒤 암행어사가 되어 남원으로 돌아와요. 초라한 행색으로 춘향 앞에 나타나는 장면과 암행어사 출두는 널리 알려진 이야기의 절정이에요. 그는 변학도의 횡포를 바로잡고 춘향과 재회하죠. 약속이 단지 아름다운 말이 아니라 행동으로 이어지는 순간이에요.

《춘향전》에는 여러 이본이 있고 사건의 표현과 세부는 달라질 수 있어요. 무엇보다 춘향이 당한 강압과 부당한 처벌을 연인 사이의 소통 문제로 축소해서는 안 돼요. 이 이야기가 오늘의 두 사람에게 남기는 질문은 하나예요. **서로 보이지 않는 시간에도 상대의 선택을 존중하며, 약속을 오늘의 행동으로 만들 수 있을까요?**"""

def enrich(result, a, b, rel):
    from story_report import relationship_style, count_elements, STEM_NAME, GOD_TEXT, KO, ELEM_DESC
    # Assign symbolic roles without gender. The comparison is stable for a given pair.
    def resolve(p):
        x = relationship_style(p)
        counts = count_elements(p)
        return x, counts
    xa, ca = resolve(a)
    xb, cb = resolve(b)
    # Stronger earth/metal emphasis represents steadfast boundaries; tie breaks by input order.
    def steadfast(p, x, counts):
        return counts['earth'] + counts['metal'] + (1 if x['god'] in ('정관', '정재', '비견') else 0)
    a_chun = steadfast(a, xa, ca) >= steadfast(b, xb, cb)
    chun, mong = ('당신', '상대방') if a_chun else ('상대방', '당신')
    pc, pm = (a, b) if a_chun else (b, a)
    xc, cc = (xa, ca) if a_chun else (xb, cb)
    xm, cm = (xb, cb) if a_chun else (xa, ca)
    def profile(label, character, p, x, counts):
        elements = ' · '.join(f'{KO[k]} {v}개' for k,v in counts.items())
        dominant = [k for k in KO if counts[k] == max(counts.values())]
        return (f'◆ **{label}에게 비춰 보는 {character}의 마음**\n'
                f'{label}의 일간은 {STEM_NAME[x["stem"]]}({x["stem"]})이에요. '
                f'{x["desc"][0]}이라는 상징에서 {x["desc"][1]}을 떠올려 볼 수 있어요. '
                f'가까운 사이에서는 {x["desc"][2]}을 중요하게 읽어요. '
                f'월간 {p["month_pillar"][0]}과 일간의 관계를 나타내는 십성은 {x["god"]}이고, '
                f'이는 {GOD_TEXT[x["god"]]}의 이미지와 이어져요. '
                f'겉으로 드러난 오행은 {elements}예요. '
                f'가장 자주 보이는 {", ".join(KO[k] for k in dominant)}은(는) '
                f'{ELEM_DESC[dominant[0]].replace("이미지야.", "이미지예요.").replace("있어.", "있어요.")}')
    result['tagline'] = '서로 떨어져 있어도, 마음속 약속을 지키는 사랑'
    result['teaser'] = '서로에 대한 믿음이 관계를 지탱하는 커플이에요. 하지만 그 믿음이 때로는 말하지 못한 외로움과 기다림을 감추기도 해요.'
    result['roles'] = (
        '춘향은 자신의 선택을 지켰고, 몽룡은 돌아와 약속을 행동으로 보여 주었어요. '
        f'사주 상징을 문학적 배역에 비추면 {chun}은 춘향 쪽, {mong}은 몽룡 쪽으로 읽어 볼 수 있어요. '
        '성별이나 누가 더 사랑하는지를 판단하는 배역은 아니에요.\n\n'
        + profile(chun, '춘향', pc, xc, cc) + '\n\n'
        + profile(mong, '몽룡', pm, xm, cm) + '\n\n'
        '이 역할은 일간·월간 십성과 겉으로 드러난 오행의 편집상 비교예요. '
        '오행 개수는 월령·지장간까지 고려한 강약 판정이 아니며, 동점이면 입력 순서로 정해요. '
        + ('출생시각을 모르면 시주를 제외했어요. ' if not a.get('hour_pillar') or not b.get('hour_pillar') else '')
        + '실제 성격이나 미래를 예측하는 진단이 아니에요.'
    )
    result['story'] = TALE
    vector = rel['vector']
    def axis(key, intro):
        label, variants = AXES[key]
        return f'◆ **{label} {vector[key]:g}/100**\n{intro} {variants[band(vector[key])][0]}'
    result['saju_a'] = (
        '춘향과 몽룡에게 끌림은 출발점이었지만, 오래 남은 것은 서로를 믿고 성장하려는 선택이었어요. '
        '당신들의 관계를 기존 사주 상징 점수로 세 방향에서 읽어 볼게요.\n\n'
        + '\n\n'.join((
            axis('attraction','광한루의 만남처럼 서로에게 다가가게 되는 순간을 생각해 봐요.'),
            axis('security','약속이 일상의 신뢰로 이어지는 방식을 살펴봐요.'),
            axis('growth','몽룡이 자신의 길을 걸었던 시간처럼 각자의 성장을 존중할 수 있을까요?')
        ))
        + '\n\n이 점수는 기존 규칙에서 만든 편집용 상징 점수이며, 사랑의 크기나 재회 가능성을 뜻하지 않아요.'
    )
    # Interpret the three axes independently, rather than assuming distance or abandonment.
    result['crisis'] = (
        '춘향이 겪은 권력의 폭력은 연인 사이의 다툼과 같지 않아요. '
        '여기서는 두 사람의 관계에서 서로 다른 시간과 기대가 만들어 내는 일상적 오해만 살펴봐요. '
        '실제 장거리 연애나 일방적인 기다림을 겪고 있다고 단정하지 않아요.\n\n'
        + '\n\n'.join((
            axis('conflict','서로의 계획이 달라질 때 무엇을 먼저 확인할지 살펴봐요.'),
            axis('expression','믿는 마음이 말과 행동으로 얼마나 전달되는지 생각해 봐요.'),
            axis('autonomy','각자의 길을 지키면서도 함께할 시간을 만드는 방식을 살펴봐요.')
        ))
        + '\n\n세 점수는 두 사람의 관계를 비유한 것이지 어느 한 사람의 결함을 가리키지 않아요.'
    )
    labels = {'attraction':'끌림','security':'안정감','growth':'성장','conflict':'갈등','expression':'표현','autonomy':'자율성'}
    result['tip'] = (
        '춘향의 신념도, 몽룡의 약속도 오늘의 행동으로 이어질 때 의미가 있어요. '
        '서로를 기다리게 만드는 대신 서로의 시간을 함께 설계해 보세요.\n\n'
        + '\n\n'.join(
            f'◆ **{labels[key]}을 위한 이번 주의 선택**\n{AXES[key][1][band(vector[key])][1]}'
            for key in ('security','expression','autonomy','conflict','growth','attraction')
        )
    )
    result['ending'] = '사랑은 언젠가 돌아오겠다는 약속만이 아니라, 오늘도 서로를 향해 조금씩 걸어가는 일이에요.'
    result['questions'] = [
        f'{chun}에게: 지금 지키고 싶은 선택을 상대에게 어떻게 알려 주고 싶나요?',
        f'{mong}에게: 미래의 약속을 오늘의 작은 행동으로 바꾼다면 무엇을 할 수 있나요?',
        '이번 주 서로가 기다리지 않아도 되는 약속 하나를 정해 볼까요?',
    ]
    result['sections'] = ['roles','story','saju_a','crisis','tip']
    result['chapters'] = [{'key':k,'title':title} for k,title in zip(result['sections'],TITLES)]
    return result

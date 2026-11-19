"""c06 editorial evidence only. Never changes calendar, rank, scores or roles.

Policy: fixed conventional hidden stems (main qi first); roots mean same
element anywhere in hidden stems, not a strength verdict. Month main qi is
a seasonal cue, not a quantified strength model. Combinations never imply
transformation. No luck cycles, useful gods or inferred missing birth time.
"""
from itertools import combinations
from collections import Counter
from relationship_v08 import STEMS, STEM_ELEM, COMB, CLASH

PILLARS = ('year_pillar', 'month_pillar', 'day_pillar', 'hour_pillar')
LABELS = dict(zip(PILLARS, ('년주', '월주', '일주', '시주')))
HIDDEN = dict(zip('子丑寅卯辰巳午未申酉戌亥',
                  ('癸', '己癸辛', '甲丙戊', '乙', '戊乙癸', '丙戊庚',
                   '丁己', '己丁乙', '庚壬戊', '辛', '戊辛丁', '壬甲')))
STEM_COMB = {frozenset(x) for x in ('甲己','乙庚','丙辛','丁壬','戊癸')}
SEASONS = {b: s for bs, s in [('寅卯辰','봄'),('巳午未','여름'),('申酉戌','가을'),('亥子丑','겨울')] for b in bs}
GROUP = {'비견':'self','겁재':'self','식신':'voice','상관':'voice',
         '편재':'care','정재':'care','편관':'promise','정관':'promise',
         '편인':'reflect','정인':'reflect'}
# Each selected theme has its own attraction, tension, scene, repair, question.
THEMES = {
 'self': ('각자의 선택', '서로 자기 의견을 낼 수 있다는 점이 반가울 수 있어요.',
          '함께하자는 제안이 내 일정까지 대신 정하는 말로 들릴 수 있어요.',
          '주말 여행을 제안하자 “좋아. 그런데 토요일 오전은 내 시간으로 남겨 두고 싶어”라는 답이 돌아와요.',
          '각자 꼭 지킬 시간 하나를 먼저 적고, 겹치는 시간에만 함께할 약속을 잡아 보세요.',
          '함께하고 싶어도 내가 직접 정하고 싶은 일은 무엇인가요?'),
 'voice': ('표현의 온도', '작은 경험을 말과 행동으로 나누며 가까워지는 모습을 떠올릴 수 있어요.',
           '즐거운 제안이 이어질수록 조용히 듣고 싶은 사람의 자리가 좁아질 수 있어요.',
           '힘든 하루를 말했는데 “주말에 놀러 가자”는 답을 받아요. 기분을 바꿔 주려는 마음과 들어 주길 바라는 마음이 엇갈려요.',
           '고민을 꺼낼 때 “오늘은 10분만 들어 줘”라고 말하고, 듣는 사람은 제안 전에 들은 마음을 한 번 되짚어 주세요.',
           '내가 바란 것은 새로운 제안이었나요, 내 말을 들어 주는 시간이었나요?'),
 'care': ('돌봄의 방식', '만날 시간을 비우고 필요한 것을 챙기는 실천에서 애정을 발견할 수 있어요.',
          '정성 들여 준비했어도 상대에게 필요한 배려와 다르면 서운함이 남을 수 있어요.',
          '한 사람이 저녁 식사와 이동편을 모두 예약해요. 다른 사람은 “고맙지만 오늘은 집에서 쉬고 싶었어”라고 말해요.',
          '예약하기 전에 외출과 집에서 쉬기 중 무엇이 편한지 묻고, 취소가 필요한 준비는 함께 나누어 정리해 보세요.',
          '상대를 위해 준비하기 전에 먼저 물어보고 싶은 배려는 무엇인가요?'),
 'promise': ('약속의 무게', '모호했던 마음도 다음에 만날 날이나 짧은 연락 약속이 생기면 조금 더 편하게 나눌 수 있겠죠.',
             '확실히 하려는 질문이 상대에게는 지금 답을 내놓으라는 요구로 들릴 수 있어요.',
             '다음 달 여행 예약을 앞두고 “오늘 정하자”와 “근무표가 나올 때까지 기다려 줘”가 마주해요.',
             '예약 마감과 근무표가 나오는 날짜를 따로 적고, 확정 전에는 취소 가능한 선택지만 함께 살펴보세요.',
             '지금 확정할 수 있는 약속과 아직 기다려야 하는 사정은 각각 무엇인가요?'),
 'reflect': ('마음을 여는 속도', '답을 재촉하지 않고 생각할 자리를 남겨 주는 배려에서 가까워질 수 있어요.',
             '생각을 정리하는 침묵이 기다리는 쪽에는 마음을 닫는 행동으로 보일 수 있어요.',
             '고민을 물었는데 “조금 생각하고 싶어”라는 답이 와요. 기다리는 사람은 자꾸 메시지를 보내고 싶어져요.',
             '생각할 시간이 필요하면 오늘 밤 9시처럼 다시 이야기할 때를 정하고, 그때는 결론이 없어도 현재 마음 한 문장을 전해 보세요.',
             '생각할 시간을 달라고 말할 때 언제 다시 이야기할 수 있나요?'),
}

def element(stem):
    return STEM_ELEM[STEMS.index(stem)]

def extract(p):
    from story_report import ten_god
    day = p['day_pillar'][0]
    pillars = {k:p[k] for k in PILLARS if p.get(k)}
    hidden = {k:[{'stem':s,'god':ten_god(day,s)} for s in HIDDEN[v[1]]] for k,v in pillars.items()}
    visible = {k:ten_god(day,v[0]) for k,v in pillars.items() if k != 'day_pillar'}
    roots = [k for k,v in hidden.items() if any(element(x['stem']) == element(day) for x in v)]
    # Three anchored positions: seasonal main qi, intimate day branch, private hour.
    anchors = [('month',hidden['month_pillar'][0]['god']),('day',hidden['day_pillar'][0]['god'])]
    if 'hour_pillar' in pillars: anchors.append(('hour',visible['hour_pillar']))
    weights = Counter()
    for position,god in anchors: weights[GROUP[god]] += 3 if position == 'month' else 2
    # Every non-day visible stem and every hidden stem participates; hidden count
    # is an editorial tie-breaker, never qi strength or a compatibility score.
    for god in visible.values(): weights[GROUP[god]] += 1
    for values in hidden.values():
        for x in values: weights[GROUP[x['god']]] += 0.25
    theme = max(THEMES, key=lambda k:weights[k])
    internal = []
    for (ka,va),(kb,vb) in combinations(pillars.items(),2):
        pair=frozenset((va[1],vb[1]))
        if pair in COMB or pair in CLASH:
            internal.append({'positions':[ka,kb],'branches':va[1]+vb[1], 'kind':'육충' if pair in CLASH else '육합'})
    return dict(pillars=pillars,season=SEASONS[p['month_pillar'][1]],hidden=hidden,
                visible_gods=visible,roots=roots,anchors=dict(anchors),theme=theme,
                editorial_weights=dict(weights),internal=internal,missing_hour='hour_pillar' not in pillars)

def cross(a,b):
    found=[]
    for ka in PILLARS:
        for kb in PILLARS:
            if not a.get(ka) or not b.get(kb): continue
            va,vb=a[ka],b[kb]
            pair=frozenset((va[1],vb[1]))
            if pair in COMB or pair in CLASH:
                found.append(dict(a=ka,b=kb,chars=va[1]+vb[1],kind='육충' if pair in CLASH else '육합'))
            if frozenset((va[0],vb[0])) in STEM_COMB:
                found.append(dict(a=ka,b=kb,chars=va[0]+vb[0],kind='천간합'))
    return found

def evidence_text(label,x):
    month=x['pillars']['month_pillar']; day=x['pillars']['day_pillar']
    root=('일간과 같은 오행의 뿌리(통근)를 찾은 자리는 '+ '·'.join(LABELS[k] for k in x['roots'])+'예요.' if x['roots'] else '입력된 가지의 속글자에서는 일간과 같은 오행의 뿌리(통근)를 찾지 못했어요.')
    hour=(f"시주 {x['pillars']['hour_pillar']}의 겉글자는 {x['visible_gods']['hour_pillar']}의 상징으로 읽었어요." if not x['missing_hour'] else '출생시간 미입력으로 시주는 제외했어요.')
    return (f"{label}의 입력 기둥은 "+' · '.join(f'{LABELS[k]} {v}' for k,v in x['pillars'].items())+'. '
            f"월령 {month[1]}({x['season']})의 중심 상징은 {x['anchors']['month']}, "
            f"일지 {day[1]}의 중심 상징은 {x['anchors']['day']}의 이미지로 읽었어요. {hour} "
            f"지장간은 가지 안에 담긴 글자라는 뜻이에요. "
            + ' / '.join(f"{LABELS[k]} {x['pillars'][k][1]}: {''.join(v['stem'] for v in values)}" for k,values in x['hidden'].items())
            + f'. {root} 뿌리의 수로 강약을 판정하지 않아요.')

def enrich(result,a,b):
    from c06_narrative import compose
    aa,bb=extract(a),extract(b)
    result['chart_evidence'] = dict(version='c06-chart-v2',a=aa,b=bb,cross=cross(a,b),
        policy='기존 전체 명식 편집 규칙 유지. 합화·신강약·용신·대운 판단 없음. 배역·내부 점수·매칭 보존.')
    return compose(result,a,b,aa,bb,result['chart_evidence']['cross'])

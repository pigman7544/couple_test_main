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
 'promise': ('약속의 무게', '모호한 마음을 작은 약속으로 확인할 때 편안함을 느끼는 장면에 비춰 볼 수 있어요.',
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
    aa,bb=extract(a),extract(b); links=cross(a,b)
    ta,tb=THEMES[aa['theme']],THEMES[bb['theme']]
    result['chart_evidence'] = dict(version='c06-chart-v1',a=aa,b=bb,cross=links,
        policy='계절·십성·지장간·통근·육합·육충·천간합의 고정 편집 규칙. 합화·신강약·용신·대운 판단 없음. 기존 배역·점수·매칭 보존.')
    # Keep the existing role assignment explanation; remove day-only profiles
    # so the full-chart reading is the main argument, not an appendix to it.
    role_intro=result['roles'].split('\n\n')[0]
    result['roles'] = (role_intro+'\n\n◆ **기둥 전체에서 고른 관계의 실마리**\n'
        f'당신에게서는 **{ta[0]}**, 상대방에게서는 **{tb[0]}**에 주목했어요. '
        '태어난 계절과 가까운 관계를 비추는 자리, 입력한 경우 태어난 시간의 표현을 먼저 보고 나머지 글자를 함께 살폈어요. '
        '앞의 배역은 기존 기준을 유지하지만, 아래 현실 장면은 이 추가 근거로 달라져요.\n\n'
        + evidence_text('당신',aa)+'\n\n'+evidence_text('상대방',bb)
        +'\n\n태어난 달의 글자를 함께 읽으면 일간 하나로는 보이지 않는 차이를 살필 수 있어요. '
        '오행은 나무·불·흙·쇠·물, 다섯 자연의 이미지예요. '
        '이 근거로 실제 성격이나 관계의 미래를 확정하지 않아요. '
        '배역 기준의 차이가 같으면 입력 순서로 정하며 역할을 바꾸어 읽어도 좋아요. '
        + ('출생시간을 모르는 사람은 시주를 빼고 읽었어요.' if aa['missing_hour'] or bb['missing_hour'] else ''))
    result['story'] += ('\n\n◆ **이야기 뒤에 두 분에게 묻는 질문**\n'
        '위의 전승과 아래 상징적 질문은 구분해 읽어 주세요. 백소정이 삶을 지키려 한 선택과 허선이 낯선 모습을 마주한 일을 거울로 삼아 봐요. '
        f'당신에게는 “{ta[5]}”, 상대방에게는 “{tb[5]}”를 건네요.')
    result['saju_a'] += ('\n\n◆ **같은 배역, 서로 다른 끌림**\n'
        f'당신 쪽은 ‘{ta[0]}’의 관점으로 일상을 살펴봐요. {ta[1]} 상대방 쪽은 ‘{tb[0]}’의 관점으로 읽어요. {tb[1]} '
        '이 두 배려가 서로에게 반가운지는 직접 물어봐야 해요. 사주의 상징은 실제 마음의 증거가 아니니까요.')
    for label,x in [('당신',aa),('상대방',bb)]:
        if GROUP[x['anchors']['day']]==x['theme']:continue
        day_theme=THEMES[GROUP[x['anchors']['day']]]
        result['saju_a'] += f'\n\n{label}의 일지에 담긴 중심 글자는 가까운 관계의 비유로 보았어요. {day_theme[1]}'
    link_text=' / '.join(f"당신 {LABELS[x['a']]}·상대방 {LABELS[x['b']]} {x['chars']} {x['kind']}" for x in links)
    clash=any(x['kind']=='육충' for x in links)
    link_read=('서로 다른 생활 리듬을 조정하는 질문을 더해요. 충이 다툼이나 이별을 뜻하지는 않아요.' if clash else
               '맞추기 쉬워 보이는 부분에서도 동의를 생략하지 않는 질문을 더해요. 합이 좋은 관계를 보장하지는 않아요.' if links else
               '검사한 두 명식 사이에는 육합·육충·천간합이 없어요. 관계의 의미가 없다는 뜻은 아니에요.')
    internal=' / '.join(f"{label} {LABELS[v['positions'][0]]}·{LABELS[v['positions'][1]]} {v['branches']} {v['kind']}" for label,x in [('당신',aa),('상대방',bb)] for v in x['internal'])
    result['crisis'] += ('\n\n◆ **현실에 비춰 보는 가상 장면 — 두 가지 바람**\n'
        '다음은 실제 경험이나 원전 사건이 아닌 편집 예시예요.\n\n'
        f'당신의 시선: {ta[3]} {ta[2]}\n\n상대방의 시선: {tb[3]} {tb[2]}\n\n'
        f'두 사람 사이에서 확인한 글자 관계: {link_text or "해당 없음"}. {link_read} '
        f'각 명식 안의 합충: {internal or "검사한 육합·육충 없음"}. '
        '합을 다른 오행으로 변했다고 가정하거나 충을 실제 사건으로 바꾸지 않았어요.')
    for label,x in [('당신',aa),('상대방',bb)]:
        if not x['missing_hour'] and GROUP[x['anchors']['hour']]!=x['theme']:
            h=THEMES[GROUP[x['anchors']['hour']]]
            result['crisis'] += (f'\n\n{label}의 시주를 혼자 하루를 정리하는 시간에 비춰 본다면: {h[2]} '
                                '시주가 반드시 사적인 성격을 결정한다는 뜻은 아니에요.')
        root_read=('익숙한 방식을 지키는 바람과 새로운 제안을 함께 놓아 보는 장면' if x['roots'] else
                   '주변 상황에 맞추기 전에 자기 바람을 먼저 말해 보는 장면')
        result['crisis'] += f'\n\n{label}의 뿌리 유무는 {root_read}을 고르는 보조 비유로만 사용했어요.'
    bridge=('이번 주 일정이 어긋난 날을 가정해, 바꿀 수 없는 일정과 조정 가능한 일정을 하나씩 적어 보세요.' if clash else
            '서로 편하다고 짐작한 약속 하나를 골라, 지금도 같은 방식이 좋은지 다시 확인해 보세요.' if links else
            '두 사람의 배려 중 이번 주 받고 싶은 것을 하나씩 골라 말해 보세요.')
    result['tip'] += ('\n\n◆ **앞의 장면을 바꾸는 두 사람의 선택**\n'
        f'당신에게: {ta[4]}\n\n상대방에게: {tb[4]}\n\n함께: {bridge} '
        '일주일 뒤 그 약속이 편했는지 확인하고, 맞지 않았다면 실제 바람에 맞춰 바꾸세요.')
    for label,x in [('당신',aa),('상대방',bb)]:
        if GROUP[x['anchors'].get('hour',x['anchors']['day'])]==x['theme']:continue
        h=THEMES[GROUP[x['anchors'].get('hour',x['anchors']['day'])]]
        result['tip'] += f'\n\n{label}의 하루 끝에 더해 볼 선택: {h[4]}'
    result['questions']=[f'당신에게: {ta[5]}',f'상대방에게: {tb[5]}',bridge]
    result['ending']=f'두 주제를 대화에 놓아 주세요: **{ta[0]}**, **{tb[0]}**. 두 분의 실제 답이 사주의 비유보다 먼저예요.'
    return result

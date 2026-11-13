"""c11 editorial synthesis, separate from calendar, matching and c06 policy.

Relations are conventional symbols, never measured personality or qi strength.
Nodes retain position and hidden/visible provenance. No transformation verdicts.
"""
from itertools import combinations
from c06_chart import extract as base_extract, element, GROUP, STEM_COMB, LABELS
from relationship_v08 import GEN, CTRL
from story_report import ten_god, STEM_NAME, STEM_DESC
from c06_narrative import particle


def flow(a, b):
    a, b = element(a), element(b)
    if a == b:
        return '동류'
    if GEN[a] == b:
        return '생'
    if CTRL[a] == b:
        return '극'
    return None


def extract(p):
    x = base_extract(p)
    day = p['day_pillar'][0]
    nodes = []
    for pos, pillar in x['pillars'].items():
        nodes.append(dict(id=pos+':visible', position=pos, layer='visible',
                          stem=pillar[0], god=ten_god(day, pillar[0])))
        for i, hidden in enumerate(x['hidden'][pos]):
            nodes.append(dict(id=f'{pos}:hidden:{i}', position=pos,
                              layer='hidden', **hidden))
    edges = [dict(source=a['id'], target=b['id'], kind=kind)
             for a in nodes for b in nodes if a['id'] != b['id']
             for kind in [flow(a['stem'], b['stem'])] if kind]
    stem_combinations = [dict(positions=[a,b], chars=va[0]+vb[0], kind='천간합')
                         for (a,va),(b,vb) in combinations(x['pillars'].items(),2)
                         if frozenset((va[0],vb[0])) in STEM_COMB]
    month = x['hidden']['month_pillar'][0]
    groups = {GROUP[n['god']] for n in nodes if n['id'] != 'day_pillar:visible'}
    m = GROUP[month['god']]
    rooted = bool(x['roots'])
    clash = any(l['kind'] == '육충' for l in x['internal'])
    # Conjunctions, not added personality scores. Month main qi is the anchor;
    # all other positions supply support, pressure, expression or mediation.
    if m == 'care' and rooted and 'self' in groups:
        mode = 'shared_care'
    elif m == 'reflect' and 'promise' in groups and rooted:
        mode = 'considered_response'
    elif m == 'self' and rooted and 'reflect' in groups:
        mode = 'supported_choice'
    elif m == 'voice' and rooted and 'promise' in groups and clash:
        mode = 'measured_voice'
    else:
        mode = m
    # Internal tension changes the conclusion even when visible counts match.
    variant = 'tension' if clash else ('rooted' if rooted else 'unrooted')
    if mode not in PROFILES:
        mode = m
    paths = []
    for a in nodes:
        if a['id'] == 'day_pillar:visible':
            continue
        for b in nodes:
            if b['id'] in (a['id'], 'day_pillar:visible'):
                continue
            if flow(a['stem'],b['stem']) == '생' and flow(b['stem'],day) == '생':
                paths.append([a['id'],b['id'],'day_pillar:visible'])
    x['synthesis'] = dict(rule=mode, variant=variant, month_group=m,
        nodes=nodes, edges=edges, stem_combinations=stem_combinations,
        support_paths=paths, roots=x['roots'], groups=sorted(groups),
        policy='월지 중심과 일간의 관계를 통근·생극 경로·내부 합충으로 조정하는 편집 규칙. 강약·합화 판정 아님.')
    x['theme'] = {'shared_care':'care','considered_response':'reflect',
                  'supported_choice':'self','measured_voice':'voice'}.get(mode,m)
    return x


# First sentence and second sentence form a single response to the same structure.
PROFILES = {
 'shared_care': ('함께 꾸리는 배려','선택을 묻는 준비',
   '필요한 일을 직접 챙기는 마음과 나도 상대도 자기 뜻을 갖는다는 마음을 함께 읽을 수 있어요.',
   '그래서 준비를 많이 하는 것만큼, 그 준비가 상대에게도 필요한지 묻는 일이 중요해져요.'),
 'considered_response': ('확인하며 여는 마음','대답을 남기는 신중함',
   '사정을 이해하려는 마음과 빨리 판단해야 한다는 부담이 함께 있는 모습으로 읽을 수 있어요.',
   '생각을 마칠 때까지 조용히 기다리기보다, 내 뜻과 다시 답할 때를 먼저 알려 주는 쪽으로 풀어 볼 수 있죠.'),
 'supported_choice': ('스스로 고르는 믿음','다시 살피는 확신',
   '도움을 받아도 자신의 선택은 직접 하고 싶은 마음으로 읽을 수 있어요.',
   '그 믿음이 가까운 사람의 선택까지 대신 정하는 확신이 되지 않도록, 상대가 고를 시간도 남길 수 있겠죠.'),
 'measured_voice': ('조심스러운 솔직함','다시 묻는 대화',
   '표현하고 싶은 마음에 스스로 말을 조절하려는 마음이 함께 있는 모습으로 읽을 수 있어요.',
   '가까워지려는 움직임과 자기 자리를 지키려는 긴장이 함께 있으니, 말한 뒤 상대가 어떻게 들었는지 다시 묻는 일이 도움이 될 수 있죠.'),
 'care': ('생활을 살피는 마음','함께 고르는 배려','생활에 필요한 것을 마련하는 마음으로 읽을 수 있어요.','준비를 시작하기 전에 원하는 것을 서로 확인해 볼 수 있죠.'),
 'reflect': ('이해를 구하는 마음','생각을 나누는 여유','바로 답하기보다 뜻을 충분히 이해하려는 마음으로 읽을 수 있어요.','생각하는 중에도 현재 마음을 조금씩 알려 줄 수 있겠죠.'),
 'self': ('자기 뜻을 지키는 마음','서로 남기는 선택','가까워져도 자신의 뜻을 갖고 싶은 마음으로 읽을 수 있어요.','다른 의견이 나오더라도 함께할 방법을 다시 고를 수 있겠죠.'),
 'voice': ('경험을 나누는 마음','대답을 듣는 표현','속에 둔 생각을 말과 행동으로 나누려는 마음으로 읽을 수 있어요.','말하는 즐거움과 상대의 대답을 듣는 시간을 함께 남겨 볼 수 있죠.'),
 'promise': ('약속을 살피는 마음','함께 정하는 책임','관계를 구체적인 약속으로 확인하고 싶은 마음으로 읽을 수 있어요.','확정할 수 있는 일과 기다려야 하는 일을 함께 나누어 볼 수 있죠.'),
}


def character_keywords(x):
    s=x['synthesis']; keys=PROFILES[s['rule']][:2]
    if s['rule'] in ('shared_care','considered_response','supported_choice','measured_voice'):
        # A conjunction may coexist with a newly introduced clash in a probe.
        if s['variant']=='tension' and s['rule']!='measured_voice':
            return keys[0], '차이를 확인하는 대화'
        return keys
    return keys[0], {'tension':'차이를 확인하는 대화','rooted':keys[1],
                      'unrooted':'도움을 청하는 여유'}[s['variant']]


def combined_basis(label,x):
    day=x['pillars']['day_pillar'][0]; month=x['pillars']['month_pillar']
    center=x['hidden']['month_pillar'][0]['stem']; s=x['synthesis']
    relation={('생',True):'일간을 돕고',('생',False):'일간이 밖으로 표현하는 길이 되고',
              ('극',True):'일간을 제어하고',('극',False):'일간이 다루는 대상이 되고'}
    incoming=flow(center,day); outgoing=flow(day,center)
    action='일간과 같은 오행이고' if incoming=='동류' else relation.get((incoming,True),relation.get((outgoing,False),'일간과 다른 역할을 하고'))
    root=(' · '.join(LABELS[k].replace('년주','연주')+' '+x['pillars'][k][1] for k in x['roots'])
          +' 안에는 일간과 같은 오행의 뿌리가 있어요.' if x['roots'] else
          '입력된 가지 안에서는 일간과 같은 오행의 뿌리가 확인되지 않아요. 이것만으로 마음이 약하다고 판단하지는 않아요.')
    # Reader language describes functions, evidence keeps exact ten gods.
    functions={'self':'자기 뜻을 지키는 역할','voice':'밖으로 표현하는 역할',
               'care':'생활의 일을 챙기는 역할','promise':'기준을 세우고 조절하는 역할',
               'reflect':'받아들이고 이해를 돕는 역할'}
    focus={'shared_care':'self','considered_response':'promise',
           'supported_choice':'reflect','measured_voice':'promise'}.get(s['rule'],'self')
    relevant=[n for n in s['nodes'] if n['id']!='day_pillar:visible' and GROUP[n['god']]==focus]
    # Prefer a visible concrete counterpoint over a catalogue of all roles.
    relevant.sort(key=lambda n:n['layer']!='visible')
    counterpoint=(f"함께 있는 {STEM_NAME[relevant[0]['stem']]}도 {functions[focus]}을 해요. "
                  if relevant else '')
    center_name=STEM_NAME[center]
    first=(f"{label}의 일간 {STEM_NAME[day]}({day}){particle(STEM_NAME[day],'은','는')} {STEM_DESC[day][0]}에 비유돼요. "
           +f"{x['season']}의 월주 {month} 속 {center_name}{particle(center_name,'은','는')} {action}, {root} "
           +counterpoint+PROFILES[s['rule']][2])
    # Explicit interacting flow, not four positional personality descriptions.
    if s['support_paths'] and s['rule']=='considered_response':
        path=s['support_paths'][0]; ns={n['id']:n for n in s['nodes']}
        names={'wood':'나무','fire':'불','earth':'흙','metal':'금','water':'물'}
        a,b,c=[names[element(ns[n]['stem'])] for n in path]
        second=f'{a}에서 {b}, 다시 일간의 {c}로 도움을 잇는 흐름도 있어요. 부담을 느끼는 자리에서도 사정을 이해할 실마리를 찾는 모습이 떠올라요. '
    elif s['rule']=='shared_care':
        second='일간이 생활의 일을 다루는 관계에 뿌리와 같은 오행의 도움이 함께 있어요. 일을 챙기는 힘을 혼자 결정하는 데만 쓰기보다, 서로의 바람을 모아 준비하는 모습이 떠올라요. '
    elif s['rule']=='supported_choice':
        second='일간과 같은 오행이 바탕에 있고 일간을 돕는 글자도 함께 있어요. 익숙한 기준을 지킬 수 있다는 마음을, 상대가 다른 답을 해도 기다려 줄 여유로 풀어 볼 수 있어요. '
    else:
        second='같은 명식 안에서도 표현하려는 역할과 조절하거나 받아들이는 역할을 함께 보아야 해요. 어느 한 글자만으로 말이 많거나 적다고 정하지 않아요. '
    if x['internal']:
        kinds='·'.join(dict.fromkeys(l['kind'] for l in x['internal']))
        pairs=' · '.join(dict.fromkeys(l['branches'] for l in x['internal']))
        second+=f'{pairs}의 {kinds}도 있어, 가까워지려는 마음과 차이를 조절하는 일을 함께 떠올려요. '
    if s['stem_combinations']:
        second+='서로 짝을 이루는 겉글자도 있지만, 표현하고 조절하는 본래 역할을 없애는 것으로 읽지는 않아요. '
    second+=PROFILES[s['rule']][3]
    return first,second


def person_text(label,x,role):
    first,second=character_keywords(x); basis,adjustment=combined_basis(label,x)
    if role=='엘리자베스':
        events=('엘리자베스는 다아시의 첫 청혼에서 가족을 낮춰 말하는 태도에 반대해요. 이후 편지를 여러 번 읽으며 위컴에 대한 자기 판단도 돌아보죠.',
                '펨벌리에서의 예의와 가족을 도운 행동을 알게 된 뒤에도, 도움에 보답하려고 바로 관계를 선택하지는 않아요. 달라진 자기 마음을 확인하고 다시 마음을 전해요.')
    else:
        events=('다아시는 첫 청혼을 거절당한 뒤 편지로 사정을 설명해요. 나중에 펨벌리에서 엘리자베스와 가디너 부부를 정중하게 대하며 태도도 고쳐요.',
                '그는 리디아와 위컴의 결혼을 도우면서 자기 수고를 앞세우지 않아요. 다시 고백할 때도 엘리자베스의 마음이 여전하다면 더는 말하지 않겠다고 해요.')
    if x['theme']=='care' and role=='엘리자베스':
        events=('엘리자베스는 아픈 언니 제인을 돌보려고 진흙길을 걸어 네더필드로 가요. 가까운 사람에게 필요한 일을 직접 하려는 선택이죠.',
                '하지만 다아시의 청혼은 재산이나 집안의 기대만으로 받아들이지 않아요. 가족을 위한 마음과 자신이 관계를 고를 권리를 함께 지킨 사람이에요.')
    elif x['theme']=='voice' and role=='다아시':
        events=('다아시는 첫 청혼에서 마음을 고백하면서도 그녀의 가족을 낮춰 말해 상처를 줘요. 솔직히 말하는 것만으로 상대를 존중하는 대화가 완성되지는 않았죠.',
                '다시 고백할 때는 엘리자베스의 마음이 여전하다면 더는 말하지 않겠다고 해요. 자신의 말을 전하는 데서 상대의 대답을 듣는 쪽으로 달라진 거예요.')
    similarities={'care':'가까운 사람을 위해 움직이면서도 각자의 선택을 남기고 싶다는 점',
                  'reflect':'처음의 판단에 머무르지 않고 사정을 이해한 뒤 마음을 전하려는 점',
                  'self':'자기 뜻을 지키면서 새로 확인한 사실도 받아들이려는 점',
                  'voice':'마음을 표현하되 상대에게 어떻게 들렸는지도 살피려는 점',
                  'promise':'말과 행동이 함께 바뀌는 관계를 바란다는 점'}
    return (' · '.join('**'+k+'**' for k in (first,second))+'\n\n'+basis
            +'\n\n'+events[0]+f" {label}의 **{first}**도 {similarities[x['theme']]}에서 이런 모습과 닮았어요."
            +'\n\n'+adjustment+'\n\n'+events[1]
            +f' {label}의 **{second}**도 마음을 갖는 것에서 그치지 않고 상대의 대답을 존중하는 선택으로 이어질 때 이런 모습과 비슷해질 수 있어요. 좋아하는 마음이 있어도 원하는 답을 미리 정하지 않는 일은 실제 대화에서 골라 볼 수 있는 선택이에요.')


def pair_context(a,b,links):
    ka,kb=character_keywords(a)[0],character_keywords(b)[0]
    text=f'당신의 {ka}{particle(ka,"과","와")} 상대방의 {kb}{particle(kb,"이","가")} 만나요. '
    wishes={'care':'준비한 마음을 알아주길','reflect':'충분히 이해하고 답할 시간을 주길',
            'self':'자기 선택을 존중해 주길','voice':'표현을 듣고 뜻을 다시 확인해 주길',
            'promise':'약속을 구체적으로 정해 주길'}
    text+=f"당신은 {wishes[a['theme']]} 바라는 쪽이라면, 상대방은 {wishes[b['theme']]} 바라는 쪽으로 읽어 볼 수 있어요. "
    text+=' 서로에게 없는 답을 보태 줄 때 반갑지만, 같은 호의에도 원하는 반응은 다를 수 있어요.'
    if any(x['kind']=='육충' for x in links):
        text+=' 두 명식 사이에는 육충도 있어요. 각자 지키고 싶은 것을 확인하는 대화로 풀어 볼 수 있지만, 다툼이 정해져 있다는 뜻은 아니에요.'
    if any(x['kind'] in ('육합','천간합') for x in links):
        text+=' 육합이나 천간합은 함께할 이유를 찾는 상징으로 읽을 수 있어요. 가까워지고 싶은 마음이 서로의 선택을 대신해 주지는 않아요.'
    return text

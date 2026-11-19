"""Pinned editorial mapping and draft manuscripts for the local prototype."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEMS = str.maketrans('甲乙丙丁戊己庚辛壬癸', '갑을병정무기경신임계')
CHAPTERS = ('roles', 'crisis', 'tip')
ROMEO_COPY = {
    '병병': '좋았던 마음은 바로 전하고 싶어요. 함께할 일정은 하나씩 정해도 좋아요.',
    '병계': '좋아하는 마음은 같아도 약속을 받아들이는 방식은 달라요. 지킬 수 있는 약속부터 같이 정해 봐요.',
}


def pair_key(stems):
    return ''.join(sorted(stems))


def load_manuscripts():
    sources = json.loads((ROOT / 'review_manuscripts.json').read_text(encoding='utf8'))
    manuscripts = {}
    for source in sources:
        key = Path(source['path']).stem
        front, *sections = re.split(r'^## Chapter [123] — (.+)\n', source['content'], flags=re.M)
        title = front.splitlines()[0].split(' — ', 1)[1]
        work = front.splitlines()[2].split(' · ')[1]
        note = next(line[2:] for line in front.splitlines() if line.startswith('> '))
        chapters = list(zip(sections[::2], sections[1::2], strict=True))
        if len(chapters) != 3:
            raise ValueError(f'{key}: expected three chapters')
        manuscripts[pair_key(key)] = (key, work, title, note, chapters)
    return manuscripts


MANUSCRIPTS = load_manuscripts()
MAPPING = {
    pair_key(key): couple for key, couple in
    json.loads((ROOT / 'review_mapping.json').read_text(encoding='utf8')).items()
}


def review_match(a, b, unlock):
    first, second = (p['day_pillar'][0].translate(STEMS) for p in (a, b))
    pair = pair_key(first + second)
    couple_id = MAPPING.get(pair)
    if not couple_id or pair not in MANUSCRIPTS:
        return None
    key, work, title, note, chapters = MANUSCRIPTS[pair]
    tagline = ROMEO_COPY.get(key, title)
    couple = {'id': 'review-' + couple_id, 'name': work, 'work': work}
    result = {'couple': couple, 'has_art': False}
    if not unlock:
        heading, body = chapters[1]
        result['preview'] = {
            'tagline': tagline, 'teaser': '',
            'blur_title': heading, 'story_excerpt': body.strip().split('\n\n')[0][:105] + '…',
        }
        return result

    if key == '병계':
        note = ('본문의 ‘당신’은 병화 쪽, ‘상대방’은 계수 쪽을 뜻해요. '
                '인물 성향은 원작을 읽는 한 가지 해석이며 통화 장면은 가상이에요.')
    if key[0] != key[1] and '‘당신’' in note:
        reader = '첫 번째로 입력한 분' if first == key[0] else '두 번째로 입력한 분'
        note = f'이 글에서 ‘당신’은 {reader}이에요.\n\n{note}'
    report = {'chapters': [], 'tagline': tagline, 'has_questions': False}
    for field, (heading, body) in zip(CHAPTERS, chapters, strict=True):
        if key == '병계':
            body = body.replace('달에 걸고 맹세하려 해요.', '달을 증인 삼아 맹세하려 해요.')
        if key == '병병':
            body = body.replace('평소 두 분 다 즐거웠던 일은 잘 표현하고, 또 하고 싶은 일이 있으면 먼저 제안하는 편이에요.',
                                '두 분 모두 즐거웠던 일을 바로 말하고 다음에 하고 싶은 일을 먼저 제안하는 상황을 떠올려 보세요.')
        report['chapters'].append({'key': field, 'title': heading})
        report[field] = re.sub(r'^### ', '◆ ', body.strip(), flags=re.M)
    report['roles'] = note + '\n\n' + report['roles']
    result.update(full_report=report, test_mode=True)
    return result

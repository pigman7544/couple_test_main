"""Export current actual-compute responses and readable QA artifacts."""
import json
from pathlib import Path
from server import compute
from engine import person
from matcher import DB
from relationship_v08 import relation
from story_report import make_report

cases=json.loads(Path('tests/fixtures/c11_comparison.json').read_text(encoding='utf8'))
for c in cases:
    c['response']=compute(c['payload'],True)
    r=c['response']['full_report']
    text='\n\n'.join('# '+chapter['title']+'\n\n'+r[chapter['key']] for chapter in r['chapters'])
    Path('docs/review-c11-'+c['id']+'.md').write_text(text+'\n',encoding='utf8')
Path('tests/c11-browser-responses.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf8')
a,b=person(1992,3,18,16),person(1992,4,30,1)
reports={c['id']:make_report(a,b,relation(a,b),c,{}) for c in DB}
sizes={cid:sum(len(r[k]) for k in r['sections']) for cid,r in reports.items()}
Path('docs/qa-resume-lengths.json').write_text(json.dumps(sizes,indent=2),encoding='utf8')
print(json.dumps(dict(samples=[dict(id=c['id'],match=c['response']['couple']['id'],themes=[c['response']['full_report']['chart_evidence'][x]['theme'] for x in ('a','b')]) for c in cases],lengths=sizes)))

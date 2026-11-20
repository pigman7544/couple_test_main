"""Find real calendar inputs, never force c06 or manufacture pillars."""
import json
from datetime import date,timedelta
from pathlib import Path
from engine import person
from matcher import rank
from relationship_v08 import relation
from story_report import count_elements
from server import compute
from c06_chart import extract

def build():
    b=person(1992,4,30,1)
    seen={}
    start=date(1985,1,1)
    for n in range(365*18):
        d=start+timedelta(days=n)
        a=person(d.year,d.month,d.day,16)
        rel=relation(a,b)
        if rank(rel['vector'])[0][2]['id']!='c06': continue
        key=(a['day_pillar'][0],tuple(count_elements(a).values()))
        theme=extract(a)['theme']
        if key in seen and seen[key][1]!=theme:
            old=seen[key][0]
            cases=[]
            for i,p in enumerate((old,a)):
                payload={'a':{'date':p['solar_date'],'time':'16:00','calendar':'solar'},'b':{'date':'1992-04-30','time':'01:00','calendar':'solar'}}
                response=compute(payload,unlock=True)
                assert response['couple']['id']=='c06'
                cases.append(dict(id='AB'[i],payload=payload,counts_a=count_elements(p),counts_b=count_elements(b),response=response))
            Path('tests/fixtures/c06_comparison.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf8')
            print(json.dumps([{k:v for k,v in x.items() if k!='response'} for x in cases],ensure_ascii=True))
            return cases
        seen[key]=(a,theme)
    raise AssertionError('no matched same-count pair found')

if __name__=='__main__':build()

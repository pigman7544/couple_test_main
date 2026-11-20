import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import person
from matcher import DB
from relationship_v08 import relation
from story_report import make_report
a,b=person(1992,3,18,16),person(1992,4,30,1)
out=[]
for c in DB:
    r=make_report(a,b,relation(a,b),c,{})
    out.append(dict(couple=dict(id=c['id'],name=c['name']),full_report=r,has_art=c['id']=='c06',test_mode=True))
Path('tests/browser-reports.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')

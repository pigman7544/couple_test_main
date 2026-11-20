import sys, json, random, math, statistics, hashlib, collections
from pathlib import Path
from bisect import bisect_left, bisect_right
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from audit_quality import payload
from engine import person
from relationship_v08 import relation
from matcher import KEYS, DB, STORY, REFERENCE, rank, transformed

ROOT=Path(__file__).resolve().parent
def digest(x):
    return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def build(p):
    return person(*map(int,p['date'].split('-')),hour=int(p['time'].split(':')[0]) if p.get('time') else None)
def sample(seed,n):
    rng=random.Random(seed);out=[]
    for _ in range(n):
        p=payload(rng);a,b=build(p['a']),build(p['b']);v=relation(a,b)['vector']
        out.append((p,a,b,v))
    return out
def fit(rows):
    return {k:sorted(r[3][k] for r in rows) for k in KEYS}
def percentile(v,ref):
    return [100*(bisect_left(ref[k],v[k])+bisect_right(ref[k],v[k]))/(2*len(ref[k])) for k in KEYS]
def ranking(v,ref,method):
    if method=='baseline':return [r[1] for r in rank(v)]
    x=percentile(v,ref)
    def score(c):
        s=STORY[c['id']]
        if method=='percentile_distance':return sum((a-b)**2 for a,b in zip(x,s))
        # Centered cosine removes a story's radius advantage, keeps authored axis direction.
        u=[a-50 for a in x];w=[b-50 for b in s]
        return -sum(a*b for a,b in zip(u,w))/max(1e-12,math.sqrt(sum(a*a for a in u)*sum(b*b for b in w)))
    return [c['id'] for c in sorted(DB,key=lambda c:(score(c),c['id']))]
def counts(rows,ref,m):return {c['id']:sum(ranking(r[3],ref,m)[0]==c['id'] for r in rows) for c in DB}
if __name__=='__main__':
    rows=sample(20261109,2400);training=sample(20261001,12000);ref=fit(training)
    methods=['baseline','percentile_distance','percentile_cosine']
    result={'seed':20261109,'calibration_seed':20261001,'calibration_samples':12000,'input_sha256':digest([r[0] for r in rows]),'counts':{m:counts(rows,ref,m) for m in methods},'axes':{}}
    for k in KEYS:
        vals=[r[3][k] for r in rows];result['axes'][k]={'min':min(vals),'max':max(vals),'mean':statistics.mean(vals),'sd':statistics.pstdev(vals),'reference':REFERENCE[k],'clipped':sum(transformed(r[3])[k] in (0,100) for r in rows)}
    (ROOT/'inputs-2400.json').write_text(json.dumps([r[0] for r in rows],ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'calibration.json').write_text(json.dumps(ref),encoding='utf8')
    (ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=True,indent=2))

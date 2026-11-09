"""Additional offline ablations; never mutates matcher or production data."""
import sys,json,math,statistics,collections,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path[:0]=[str(R.parents[1]),str(R)]
from simulate import *
from story_report import make_report
from narrative import describe

protected = ['matcher.py','engine.py','relationship_v08.py','couples.json','archetypes.json']
before = {p:hashlib.sha256((R.parents[1]/p).read_bytes()).hexdigest() for p in protected}

train=sample(20261001,12000)
ref=fit(train)
means=[statistics.mean(r[3][k] for r in train) for k in KEYS]
sds=[statistics.pstdev(r[3][k] for r in train) for k in KEYS]
ids=list(STORY)
def oldx(v): return [transformed(v)[k] for k in KEYS]
def z(v): return [max(0,min(100,50+18*(v[k]-means[i])/sds[i])) for i,k in enumerate(KEYS)]
def d(a,b):return sum((x-y)**2 for x,y in zip(a,b))
# Project each authored prototype onto an actual training observation, without quotas.
projected={cid:oldx(min(train,key=lambda r:d(oldx(r[3]),STORY[cid]))[3]) for cid in ids}
methods=['baseline','percentile_distance','percentile_cosine','empirical_z','projected_story','empirical_z_projected']
zprojected={cid:z(min(train,key=lambda r:d(z(r[3]),STORY[cid]))[3]) for cid in ids}
def order(v,m):
    if m in methods[:3]:return ranking(v,ref,m)
    x=z(v) if m.startswith('empirical_z') else oldx(v)
    centers=zprojected if m=='empirical_z_projected' else projected if m=='projected_story' else STORY
    return sorted(ids,key=lambda cid:(d(x,centers[cid]),cid))
out={'calibration_seed':20261001,'calibration_n':12000,'means':means,'sds':sds,'projected_story':projected,'z_projected_story':zprojected,'seeds':{},'quality_definition':'Structural completeness, deterministic reports, original-coordinate distance regret and protected fixture IDs; no labeled semantic accuracy available.'}
fixtures=json.loads((R.parents[1]/'tests/fixtures/baek_heo_responses.json').read_text(encoding='utf8'))
for seed in [20261109,20261110,20261111,20261112]:
    rows=sample(seed,2400);result={}
    for m in methods:
        counts=collections.Counter();unchanged=repeat=swap=report_repeat=missing=0;regret=[];hashes=[]
        for p,a,b,v in rows:
            o=order(v,m);cid=o[0];counts[cid]+=1;unchanged+=cid==order(v,'baseline')[0]
            repeat+=o==order(v,m);swap+=o==order(relation(b,a)['vector'],m)
            regret.append((d(oldx(v),STORY[cid])-min(d(oldx(v),s) for s in STORY.values()))/625)
            if seed==20261109:
                c=next(c for c in DB if c['id']==cid)
                def report():return make_report(a,b,relation(a,b),c,describe(v,cid,o[1]))
                r=report();report_repeat+=digest(r)==digest(report());hashes.append(digest(r))
                missing+=len(r.get('chapters',[]))!=5 or not all(r.get(k) for k in ('roles','story','saju_a','crisis','tip'))
        result[m]={'counts':{cid:counts[cid] for cid in ids},'max_share':max(counts.values())/2400,'coverage':len(counts),'unchanged':unchanged,'rank_repeat':repeat,'swap_rank':swap,'mean_original_distance_regret':statistics.mean(regret)}
        if seed==20261109:
            result[m].update(report_repeat=report_repeat,structural_failures=missing,report_digest=digest(hashes),protected_ids=[order(relation(build(f['payload']['a']),build(f['payload']['b']))['vector'],m)[0] for f in fixtures])
    out['seeds'][seed]=result
for result in out['seeds'].values():
    for metrics in result.values():
        assert sum(metrics['counts'].values()) == 2400
        assert metrics['rank_repeat'] == metrics['swap_rank'] == 2400
        if 'report_repeat' in metrics:
            assert metrics['report_repeat'] == 2400 and metrics['structural_failures'] == 0
after = {p:hashlib.sha256((R.parents[1]/p).read_bytes()).hexdigest() for p in protected}
assert before == after
out['protected_sha256'] = after
(R/'extended-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out['seeds'][20261109],indent=2))

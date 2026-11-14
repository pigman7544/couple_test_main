"""Compare editorial scope to the exact starting commit and export review copies."""
import json, re, subprocess
from pathlib import Path

before=json.loads(subprocess.check_output(['git','show','c6d7462:tests/fixtures/c06_comparison.json']).decode('utf8'))
after=json.loads(Path('tests/fixtures/c06_comparison.json').read_text(encoding='utf8'))
rows=[]
for old,new in zip(before,after):
    a,b=old['response'],new['response']
    assert {k:v for k,v in a.items() if k!='full_report'}=={k:v for k,v in b.items() if k!='full_report'}
    assert a['full_report']['chart_evidence']==b['full_report']['chart_evidence']
    r=b['full_report']
    text='\n\n'.join(r[k] for k in r['sections'])
    assert not re.search(r'월령|정인|정관|편인|지장간|통근|십성|시주|일지[의를에]|명식|읽어 볼게요|확인해 주세요',text)
    assert not re.search(r'\d+/10|\d+점|궁합 점수|궁합 등급',text)
    copy=f"# c06 {new['id']} — 관계 중심 편집 검수본\n\n"
    for chapter in r['chapters']:
        copy+=f"## {chapter['title']}\n\n{r[chapter['key']]}\n\n"
    copy+='## 오늘 나눌 질문\n\n'+'\n\n'.join(r['questions'])+'\n\n'+r['ending']+'\n'
    Path(f"docs/review-c06-{new['id']}.md").write_text(copy,encoding='utf8')
    rows.append(dict(sample=new['id'],envelopeUnchanged=True,evidenceUnchanged=True,
                     beforeCharacters=sum(len(a['full_report'][k]) for k in r['sections']),afterCharacters=len(text),
                     technicalListsAbsent=True,scoresAbsent=True))
base=Path('tests/plain-language-baseline-log.txt').read_text(encoding='utf8')
now=Path('tests/plain-language-full-log.txt').read_text(encoding='utf8')
failures=lambda s:re.findall(r'^FAIL: (.+)$',s,re.M)
assert failures(base)==failures(now),(failures(base),failures(now))
Path('docs/qa-plain-language-scope.json').write_text(json.dumps(dict(samples=rows,unchangedFailures=failures(now)),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(rows,ensure_ascii=False))

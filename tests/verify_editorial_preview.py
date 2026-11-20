"""Preview-only release verification against the exact local synthetic reports."""
import json,re,urllib.request
from pathlib import Path
BASE='https://yeonyeon-preview-pr17.onrender.com'

def request(path,payload=None):
    raw=None if payload is None else json.dumps(payload).encode('utf8')
    req=urllib.request.Request(BASE+path,data=raw,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=55) as response:
        assert response.status==200
        return response.read()

if __name__=='__main__':
    cases=json.loads(Path('tests/fixtures/c06_comparison.json').read_text(encoding='utf8'))
    assert request('/health')==b'OK'
    rows=[]
    for case in cases:
        remote=json.loads(request('/api/c06-sample/'+case['id']))
        expected=case['response']
        assert remote['sample_payload']==case['payload']
        del remote['sample_payload']
        assert remote==expected,case['id']
        preview=json.loads(request('/api/match',case['payload']))
        assert 'full_report' not in preview
        assert not re.search(r'\d+(?:\.\d+)?\s*/\s*(?:10|100)(?!\d)|\d+\s*점|궁합\s*(?:점수|등급)',str(preview))
        unlocked=json.loads(request('/api/test-unlock',case['payload']))
        assert unlocked==expected
        rows.append({'sample':case['id'],'sample_matches_fixture':True,'preview_score_free':True,'unlock_matches_sample':True,'chapters':len(unlocked['full_report']['chapters'])})
    Path('docs/qa-editorial-api.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(rows))

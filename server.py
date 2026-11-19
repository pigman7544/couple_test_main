"""Small demo web server. Uses existing Python engine; serves real local image assets."""
import json, os, re, traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from engine import person
from relationship_v08 import relation
from matcher import DB, rank
from narrative import describe
from story_report import make_report

ROOT=Path(__file__).resolve().parent
MAX_BODY=8192
COUPLE_ART = {
    couple['id']: {
        variant: f"/assets/{'baek_heo' if couple['id'] == 'c06' else couple['id']}_{variant}.png"
        for variant in ('title', 'plain')
    }
    for couple in DB
}
ART_PATHS = {path for art in COUPLE_ART.values() for path in art.values()}

def compute(payload, unlock=False):
    if not isinstance(payload,dict):
        raise ValueError('두 사람의 정보를 입력해 주세요.')
    def build(x):
        if not isinstance(x,dict) or not isinstance(x.get('date'),str):
            raise ValueError('생년월일을 입력해 주세요.')
        date=x['date'].split('-')
        if len(date)!=3:raise ValueError('생년월일을 입력해 주세요.')
        t=x.get('time') or None
        if t is not None and not isinstance(t,str):
            raise ValueError('태어난 시간을 확인해 주세요.')
        hh,mm=map(int,t.split(':')) if t else (None,0)
        return person(*map(int,date),hour=hh,minute=mm,calendar=x.get('calendar','solar'),leap=bool(x.get('leap',False)))
    a,b=build(payload['a']),build(payload['b'])
    rel=relation(a,b)
    ranked=rank(rel['vector']);couple=ranked[0][2]
    story=describe(rel['vector'],couple['id'],ranked[1][2]['id'])
    full=make_report(a,b,rel,couple,story)
    full['gender_a']=payload['a'].get('gender','other')
    full['gender_b']=payload['b'].get('gender','other')
    art = COUPLE_ART.get(couple['id'])
    if art and not all((ROOT / path.lstrip('/')).is_file() for path in art.values()):
        art = None
    if unlock:
        return {'full_report':full,'couple':{'id':couple['id'],'name':couple['name'],'work':couple['work']},'has_art':art is not None,'art':art,'test_mode':True}
    excerpt = full.get('plot', {}).get('body') or full.get('crisis') or full.get('story', '')
    excerpt = re.sub(r'^◆ .*\n', '', excerpt.strip(), count=1).split('\n\n')[0].replace('**', '')
    if len(excerpt) > 95:
        excerpt = excerpt[:95].rsplit(' ', 1)[0] + '…'
    teaser = full.get('teaser', '')
    lines = re.split(r'(?<=[.!?])\s+', teaser)
    teaser = '\n'.join(lines) if 2 <= len(lines) <= 3 else teaser
    return {'preview':{'tagline':full['tagline'],'teaser':teaser,'story_excerpt':excerpt},'couple':{'id':couple['id'],'name':couple['name'],'work':couple['work']},'theme':full['tagline'],'version':'6.7-yeonyeon','has_art':art is not None,'art':art}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=urlparse(self.path).path
        if path in ('/api/c06-sample/A','/api/c06-sample/B','/api/c11-sample/A','/api/c11-sample/B'):
            cid=path.split('/')[2].split('-')[0]
            cases=json.loads((ROOT/f'tests/fixtures/{cid}_comparison.json').read_text(encoding='utf8'))
            sample=next(x for x in cases if x['id']==path.rsplit('/',1)[1])
            response=compute(sample['payload'],unlock=True)
            response['sample_payload']=sample['payload']
            raw=json.dumps(response,ensure_ascii=False).encode('utf8');mime='application/json; charset=utf-8'
        elif path=='/manuscripts':
            raw=(ROOT/'manuscript-shelf.html').read_bytes();mime='text/html; charset=utf-8'
        elif path in ('/report-glossary.js', '/report-glossary.css'):
            raw=(ROOT/path.lstrip('/')).read_bytes()
            mime=('text/javascript' if path.endswith('.js') else 'text/css')+'; charset=utf-8'
        elif path=='/health':raw=b'OK';mime='text/plain; charset=utf-8'
        elif path in ('/preview','/preview.html'):
            raw=(ROOT/'preview.html').read_bytes();mime='text/html; charset=utf-8'
        elif path in ('/','/index.html'):
            raw=(ROOT/'index.html').read_bytes();mime='text/html; charset=utf-8'
        elif path in ART_PATHS and (ROOT/path.lstrip('/')).is_file():
            raw=(ROOT/path.lstrip('/')).read_bytes();mime='image/png'
        else:self.send_error(404);return
        self.send_response(200)
        self.send_header('Content-Type',mime)
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-cache, must-revalidate')
        self.end_headers();self.wfile.write(raw)
    def do_POST(self):
        endpoint=urlparse(self.path).path
        if endpoint not in ('/api/match','/api/test-unlock'):self.send_error(404);return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if size<=0 or size>MAX_BODY:raise ValueError('입력 형식이 올바르지 않습니다.')
            result=compute(json.loads(self.rfile.read(size)),unlock=(endpoint=='/api/test-unlock'));status=200
        except (ValueError,TypeError,KeyError,IndexError,OverflowError):
            result={'error':'입력 정보를 확인해 주세요. 생년월일과 시간을 올바르게 입력해 주세요.'};status=400
        except Exception:
            self.log_error('Unhandled match error: %s',traceback.format_exc())
            result={'error':'계산 중 오류가 발생했습니다. 입력값을 확인해 주세요.'};status=500
        raw=json.dumps(result,ensure_ascii=False).encode('utf-8')
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw)

def serve(open_browser=False):
    port=int(os.environ.get('PORT','8765'))
    url=f'http://127.0.0.1:{port}'
    host = os.environ.get('BIND_HOST', '127.0.0.1')
    with ThreadingHTTPServer((host,port),Handler) as server:
        print(f'Open {url}',flush=True)
        if open_browser:
            import webbrowser
            webbrowser.open(url)
        server.serve_forever()


if __name__=='__main__':
    serve()

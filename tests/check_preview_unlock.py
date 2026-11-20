"""Low-volume preview-only probe using the existing synthetic demo inputs."""
import json
from pathlib import Path
import time
import urllib.request
import urllib.error

BASE = 'https://yeonyeon-preview-pr17.onrender.com'
payload = json.dumps({'a': {'date': '1992-03-18', 'time': '16:00'},
                      'b': {'date': '1992-04-30', 'time': '01:00'}}).encode()
rows = []
for i in range(10):
    started = time.monotonic()
    req = urllib.request.Request(BASE + '/api/test-unlock', data=payload,
                                 headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=55) as response:
            raw = response.read()
            data = json.loads(raw)
            report = data['full_report']
            rows.append(dict(attempt=i+1, status=response.status, seconds=round(time.monotonic()-started,3),
                             type=data['couple']['id'], chapters=len(report['chapters']),
                             body_emphasis='**' in report['roles'].split('\n\n')[0]))
    except urllib.error.HTTPError as exc:
        rows.append(dict(attempt=i+1, status=exc.code, body=exc.read(500).decode(errors='replace')))
    except Exception as exc:
        rows.append(dict(attempt=i+1, error=str(exc)))
    print(rows[-1], flush=True)
Path('docs/qa-emphasis-preview-unlock.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')

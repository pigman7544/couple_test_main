"""Find synthetic inputs through the unchanged production matcher."""
import random
import json
from engine import person
from matcher import rank
from relationship_v08 import relation
from c06_chart import extract

random.seed(11)
found, seen = [], set()
for i in range(12000):
    dates = [(random.randint(1984,2002),random.randint(1,12),random.randint(1,28),random.choice([1,9,16,21])) for _ in range(2)]
    a,b = [person(*d) for d in dates]
    if rank(relation(a,b)['vector'])[0][1] != 'c11':
        continue
    themes = (extract(a)['theme'],extract(b)['theme'])
    if themes in seen:
        continue
    seen.add(themes)
    found.append(dict(dates=dates,themes=themes,days=[a['day_pillar'],b['day_pillar']]))
    if len(found) == 8:
        break
print(json.dumps(found))

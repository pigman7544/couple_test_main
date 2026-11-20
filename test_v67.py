import unittest
from pathlib import Path
from PIL import Image
from server import compute
S={'a':{'date':'1992-03-18','time':'16:00','calendar':'solar','gender':'female'},'b':{'date':'1992-04-30','time':'01:00','calendar':'solar','gender':'male'}}
class TestYeonyeon(unittest.TestCase):
 def test_preview_no_report(self):
  d=compute(S);self.assertNotIn('full_report',d);self.assertIn('preview',d);self.assertIn('couple',d)
 def test_unlock(self):
  d=compute(S,unlock=True);self.assertIn('full_report',d);self.assertTrue(d['full_report']['roles']);self.assertTrue(d['full_report']['story'])
 def test_no_time(self):
  s={'a':dict(S['a'],time=''),'b':dict(S['b'],time='')};self.assertTrue(compute(s,unlock=True)['full_report']['story'])
 def test_ui(self):
  s=Path('index.html').read_text(encoding='utf8');self.assertIn('연연(緣硏)',s);self.assertIn('analysisLoading',s);self.assertIn('test-unlock',s)
 def test_images(self):
  for n in ('baek_heo_title.png','baek_heo_plain.png'):
   with Image.open(Path('assets')/n) as im:im.verify()
if __name__=='__main__':unittest.main()

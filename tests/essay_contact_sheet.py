from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
ids=['c01','c02','c03','c06','c10','c11','c13','c18','f01','f02','f03','f04']
for n in range(4):
 out=Image.new('RGB',(1560,1560),'#eee');d=ImageDraw.Draw(out)
 for row,cid in enumerate(ids[n*3:n*3+3]):
  for col,ch in enumerate([1,2,3,4]):
   im=Image.open(f'tests/qa-essay-{cid}-390-ch{ch}.png').convert('RGB')
   im=im.crop((0,0,min(im.width,390),min(im.height,490)))
   out.paste(im,(col*390,row*520+25));d.text((col*390+8,row*520+4),f'{cid} chapter {ch}',fill='black')
 out.save(f'tests/qa-essay-sheet-{n+1}.png')

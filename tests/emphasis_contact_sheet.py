from PIL import Image,ImageDraw
ids=['c01','c02','c03','c06','c10','c11','c13','c18','f01','f02','f03','f04']
for n in range(4):
 out=Image.new('RGB',(1950,1710),'#eee');d=ImageDraw.Draw(out)
 for row,cid in enumerate(ids[n*3:n*3+3]):
  for col,ch in enumerate(range(1,6)):
   im=Image.open(f'tests/qa-emphasis-{cid}-390-ch{ch}.png').convert('RGB')
   out.paste(im.crop((0,0,min(im.width,390),min(im.height,535))),(col*390,row*570+25))
   d.text((col*390+8,row*570+5),f'{cid} chapter {ch}',fill='black')
 out.save(f'tests/qa-emphasis-sheet-{n+1}.png')


from pathlib import Path
import sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from shapely.affinity import translate,scale
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'mingyeol-rounded'))
from model_shapes import textshape
p=Path(__file__).resolve().parent
# Keep original stroke weight; opening/closing rounds the corners without a positive offset.
g=textshape('민결',30.2,13.6,0,0,font=str(p/'blackhansans-BlackHanSans-Regular.ttf'))
r=.38
rounded=g.buffer(-r,quad_segs=16).buffer(r,quad_segs=16)
im=Image.new('RGB',(1400,670),'#fffaf8');d=ImageDraw.Draw(im)
ui='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
title=ImageFont.truetype(bold,42,index=1);label=ImageFont.truetype(ui,29,index=1);small=ImageFont.truetype(ui,23,index=1)
d.text((55,35),'5번 검은고딕 · 모서리 라운딩',font=title,fill='#3b3033')
d.text((57,100),'획을 굵히지 않고, 각진 모서리만 부드럽게 다듬었습니다.',font=small,fill='#806c73')
for i,(shape,name) in enumerate([(g,'원본'),(rounded,'모서리만 둥글게')]):
 x=45+i*685;y=165
 d.rounded_rectangle((x,y,x+665,y+450),radius=22,fill='white',outline='#eadde1',width=2)
 d.text((x+332,y+25),name,font=label,fill='#4e3b43',anchor='mt')
 a,b,c,e=shape.bounds;factor=17.5
 geom=translate(scale(shape,factor,-factor,origin=(0,0)),x+332,y+282+13.6*factor/2)
 mask=Image.new('L',im.size);md=ImageDraw.Draw(mask)
 for poly in ([geom] if geom.geom_type=='Polygon' else geom.geoms):
  md.polygon(list(poly.exterior.coords),fill=255)
  for hole in poly.interiors:md.polygon(list(hole.coords),fill=0)
 im.paste('#b65c7b',(0,0),mask)
im.save(p/'blackhan-rounded-comparison.png')

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
r=1.14
import math
from shapely.geometry import Polygon
from shapely.ops import unary_union
def round_ring(ring):
 pts=list(ring.coords)[:-1];result=[]
 for i,v in enumerate(pts):
  prev=pts[i-1];nxt=pts[(i+1)%len(pts)]
  l1=math.dist(prev,v);l2=math.dist(v,nxt)
  if min(l1,l2)<1e-8:continue
  u=((v[0]-prev[0])/l1,(v[1]-prev[1])/l1);w=((nxt[0]-v[0])/l2,(nxt[1]-v[1])/l2)
  turn=math.atan2(u[0]*w[1]-u[1]*w[0],u[0]*w[0]+u[1]*w[1])
  t=math.tan(abs(turn)/2)
  if t<1e-5:result.append(v);continue
  trim=min(r*t,.45*l1,.45*l2);radius=trim/t;sign=1 if turn>0 else -1
  a=(v[0]-u[0]*trim,v[1]-u[1]*trim)
  center=(a[0]-u[1]*radius*sign,a[1]+u[0]*radius*sign)
  angle=math.atan2(a[1]-center[1],a[0]-center[0])
  for j in range(13):
   q=angle+turn*j/12;result.append((center[0]+radius*math.cos(q),center[1]+radius*math.sin(q)))
 return result
simple=g.simplify(.075,preserve_topology=True)
rounded=unary_union([Polygon(round_ring(p.exterior),[round_ring(h) for h in p.interiors]).buffer(0) for p in simple.geoms])
im=Image.new('RGB',(1400,670),'#fffaf8');d=ImageDraw.Draw(im)
ui='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';bold='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
title=ImageFont.truetype(bold,42,index=1);label=ImageFont.truetype(ui,29,index=1);small=ImageFont.truetype(ui,23,index=1)
d.text((55,35),'5번 검은고딕 · 모서리 라운딩',font=title,fill='#3b3033')
d.text((57,100),'최대 약 20px 라운드 · 짧은 모서리는 획이 유지되도록 반경을 제한했습니다.',font=small,fill='#806c73')
for i,(shape,name) in enumerate([(g,'원본'),(rounded,'라운드 3배 · 약 20px')]):
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
im.save(p/'blackhan-rounded-3x-comparison.png')

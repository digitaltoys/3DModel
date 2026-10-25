import sys,json,math
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent))
from sc_client import Client
from shapely.geometry import Point,Polygon,box,LineString
from shapely.affinity import scale,rotate,translate
from shapely.ops import unary_union
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from pathlib import Path
out=Path(__file__).resolve().parent;out.mkdir(exist_ok=True)
def ellipse(x,y,rx,ry,angle=0):return rotate(scale(Point(0,0).buffer(1,quad_segs=20),rx,ry),angle,origin=(0,0)).__class__ if False else translate(rotate(scale(Point(0,0).buffer(1,quad_segs=20),rx,ry),angle,origin=(0,0)),x,y)
def rounded(x0,y0,x1,y1,r):return box(x0+r,y0+r,x1-r,y1-r).buffer(r,quad_segs=8)
def smooth(points,r=.7):return Polygon(points).buffer(r,quad_segs=6).buffer(-r*.35,quad_segs=6)
class Pen(BasePen):
 def __init__(self,gs):super().__init__(gs);self.rings=[];self.pts=[]
 def _moveTo(self,p):self.pts=[p]
 def _lineTo(self,p):self.pts.append(p)
 def _curveToOne(self,a,b,c):
  p=self.pts[-1]
  for t in [i/10 for i in range(1,11)]:self.pts.append(tuple((1-t)**3*p[j]+3*(1-t)**2*t*a[j]+3*(1-t)*t*t*b[j]+t**3*c[j] for j in (0,1)))
 def _qCurveToOne(self,a,b):
  p=self.pts[-1]
  for t in [i/8 for i in range(1,9)]:self.pts.append(tuple((1-t)**2*p[j]+2*(1-t)*t*a[j]+t*t*b[j] for j in (0,1)))
 def _closePath(self):
  if len(self.pts)>2:self.rings.append(self.pts)
 def _endPath(self):self._closePath()
def textshape(s,w,h,x,y,font='/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'):
 f=TTFont(font,fontNumber=1);gs=f.getGlyphSet();cmap=f.getBestCmap();shapes=[];advance=0
 for ch in s:
  n=cmap[ord(ch)];p=Pen(gs);gs[n].draw(p);g=Polygon()
  for ring in p.rings:g=g.symmetric_difference(Polygon(ring).buffer(0))
  shapes.append(translate(g,advance,0));advance+=f['hmtx'][n][0]
 g=unary_union(shapes);a,b,c,d=g.bounds;g=translate(g,-a,-b);g=scale(g,w/(c-a),h/(d-b),origin=(0,0));return translate(g,x-w/2,y).buffer(.06,quad_segs=3)
left=ellipse(-8,40,4.8,9.3,20);right=ellipse(8,39.8,4.8,8.3,-23)
head=ellipse(0,31,13.1,10.2)
tailL=smooth([(-10,7),(-20.5,10),(-21,7),(-17,3),(-20,-1),(-14,-1),(-7,2)])
tailR=scale(tailL,-1,1,origin=(0,0))
banner=rounded(-13,0,13,7,2)
nameplate=rounded(-17.3,7,17.3,25,3)
loop=ellipse(0,47.5,3.7,3.7);neck=rounded(-2.8,39,2.8,48,1)
base=unary_union([left,right,head,tailL,tailR,banner,nameplate,loop,neck]).buffer(.65,quad_segs=8)
# A 3.2 mm through hole with a reinforced 2.2 mm radial wall.
hole=ellipse(0,47.8,1.6,1.6);base=base.difference(hole)
# Fit exactly 45 mm wide; retain the proportions of the illustrated silhouette.
s=45/(base.bounds[2]-base.bounds[0])
def S(g):return scale(g,s,s,origin=(0,0)).simplify(.065,preserve_topology=True)
face=head.buffer(-.7).difference(box(-30,-10,30,26))
inners=unary_union([ellipse(-8.2,41.4,2.35,6.4,20),ellipse(8.2,41.3,2.35,5.7,-23)])
letters=textshape('민결',30,13.4,0,9).buffer(-.3,quad_segs=6).buffer(.3,quad_segs=6)
latin=textshape('MINGYEOL',21.3,3,0,2)
paws=unary_union([ellipse(-10,26,2.9,2.1),ellipse(10,26,2.9,2.1)])
bow=unary_union([smooth([(5.5,38),(4.7,42),(7,43.2),(9.5,40),(8,37.8)],.6),smooth([(9,39.5),(12.6,42),(14,40),(12.9,36.7),(10,37.3)],.6),ellipse(9.1,39.1,1.3,1.4)])
eyes=unary_union([ellipse(-4.7,32.1,.85,1.25),ellipse(4.7,32.1,.85,1.25)])
nose=smooth([(-.9,30.4),(.9,30.4),(0,29.5)],.15)
mouth=unary_union([LineString([(0,29.7),(0,29),(-.75,28.6),(-1.45,28.9)]).buffer(.25),LineString([(0,29),(.75,28.6),(1.45,28.9)]).buffer(.25)])
cheeks=unary_union([ellipse(-7,29.6,1.5,.85),ellipse(7,29.6,1.5,.85)])
c=Client();log=[]
def exe(cmd,p):
 r=c.execute(cmd,p);log.append({'command':cmd,'params':p,'result':r});return r
def feature(g,z,d,name,op='join'):
 g=S(g);polys=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
 print(name,'contours',len(polys),'points',sum(len(p.exterior.coords) for p in polys),flush=True)
 exe('sketch.create',{'plane':'XY','offset':z,'name':name+'Sketch'})
 for p in polys:
  for ring in [p.exterior,*p.interiors]:exe('sketch.line',{'points':[[round(x,5),round(y,5)] for x,y in list(ring.coords)[:-1]],'closed':True,'infer':False,'connect':False})
 exe('sketch.finish',{})
 picks=[{'point':list(p.representative_point().coords)[0]} for p in polys]
 exe('solid.extrude',{'distance':d,'operation':op,'profiles':picks,'name':name})
try:
 feature(base,0,2,'Base','new')
 feature(face,2,.4,'BunnyFace')
 feature(inners,2,.25,'InnerEars')
 feature(unary_union([tailL,tailR]),2,.25,'RibbonTails')
 feature(banner.buffer(-.25),2,.4,'Banner')
 feature(letters,2,1,'KoreanName')
 feature(latin,2.4,.6,'EnglishName')
 feature(paws,2.35,.65,'Paws')
 feature(bow.buffer(-.5,quad_segs=6).buffer(.5,quad_segs=6),2,.95,'EarBow')
 feature(cheeks,2.38,.22,'Cheeks')
 feature(unary_union([eyes,nose,mouth]),2.41,-.42,'FaceEngraving','cut')
 measure=c.tool('measure');(out/'measure.json').write_text(json.dumps(measure,ensure_ascii=False,indent=2))
 print('MEASURE',json.dumps(measure),flush=True)
 c.tool('save',{'path':str(out/'mingyeol-bunny-thin.solidcraft')})
 for ext in ['stl','step','3mf']:print('export',ext,c.tool('export',{'path':str(out/('mingyeol-bunny-thin.'+ext))}),flush=True)
 for view in ['top','iso']:
  r=c.tool('screenshot',{'view':view,'source':'model','grid':False,'axes':False,'width':1200,'height':1200,'path':str(out/('preview-'+view+'.png'))})
 print('DONE',flush=True)
finally:
 (out/'build-log.json').write_text(json.dumps(log,ensure_ascii=False));c.p.terminate()

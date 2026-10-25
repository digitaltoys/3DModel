from shapely.geometry import Point,Polygon,box
from shapely.affinity import scale,rotate,translate
from shapely.ops import unary_union
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
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

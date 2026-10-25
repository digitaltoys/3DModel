import math
from shapely.geometry import Polygon
from shapely.ops import unary_union
def round_ring(ring,r=1.14):
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

def round_font_shape(g,r=1.14):
 simple=g.simplify(.075,preserve_topology=True)
 return unary_union([Polygon(round_ring(p.exterior,r),[round_ring(h,r) for h in p.interiors]).buffer(0) for p in simple.geoms])

import sys,math,json
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt as edt, gaussian_filter
from shapely.geometry import Polygon,Point,box
from shapely.affinity import translate,scale,rotate
from shapely.ops import unary_union,transform
from PIL import Image,ImageDraw
from skimage.measure import marching_cubes
import trimesh
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from sc_client import Client
from model_shapes import ellipse,rounded,textshape
out=ROOT
def bez(start,segments):
 pts=[start];p=start
 for a,b,c in segments:
  for t in np.linspace(0,1,20)[1:]:pts.append(tuple((1-t)**3*p[j]+3*(1-t)**2*t*a[j]+3*(1-t)*t*t*b[j]+t**3*c[j] for j in (0,1)))
  p=c
 return Polygon(pts).buffer(0)
def arch(g):
 def f(x,y,z=None):
  x=np.asarray(x);y=np.asarray(y);theta=x/43
  return (43+y)*np.sin(theta),(43+y)*np.cos(theta)-43+1.4
 return transform(f,g.segmentize(.12))
from scipy.ndimage import label
from skimage.measure import find_contours
source=np.asarray(Image.open(ROOT/'reference-sketch.png').convert('L'))
def extract_glyphs(bounds,ids):
 x0,y0,x1,y1=bounds
 a=np.zeros_like(source,dtype=bool);a[y0:y1,x0:x1]=source[y0:y1,x0:x1]>145
 labels,_=label(a);regions=[]
 for id in ids:
  g=Polygon()
  for contour in find_contours((labels==id).astype(float),.5):
   g=g.symmetric_difference(Polygon([(float(x),float(y)) for y,x in contour]).buffer(0))
  regions.append(g)
 return unary_union(regions).buffer(1.15,quad_segs=6).simplify(.8,preserve_topology=True)
letters=extract_glyphs((484,510,1005,735),[21,23,24,29])
latin=extract_glyphs((567,733,923,815),[4,5,6,7,8,9,11,12])
left=bez((594,366),[
 ((531,331),(491,280),(507,222)),
 ((520,166),(564,133),(612,151)),
 ((666,168),(700,229),(716,303)),
 ((672,320),(627,342),(594,366))])
right=bez((771,303),[
 ((786,235),(807,171),(858,152)),
 ((919,129),(967,173),(974,230)),
 ((985,291),(948,334),(908,358)),
 ((855,336),(814,316),(771,303))])
head=bez((594,366),[
 ((635,324),(677,292),(716,303)),
 ((734,296),(752,295),(771,303)),
 ((827,300),(900,350),(924,405)),
 ((936,435),(938,460),(929,483)),
 ((899,515),(837,519),(791,508)),
 ((770,509),(753,511),(742,519)),
 ((719,508),(686,506),(655,514)),
 ((603,516),(554,507),(544,470)),
 ((535,433),(552,393),(594,366))])
face=head.buffer(-7)
inners=unary_union([
 bez((624,338),[ ((599,308),(573,274),(588,244)),((613,202),(655,242),(681,310)),((658,315),(640,326),(624,338))]),
 bez((813,306),[ ((798,284),(817,237),(846,239)),((873,240),(891,273),(888,297)),((860,297),(834,300),(813,306))])])
ear_rims=unary_union([left.buffer(-8),right.buffer(-8)]).difference(inners).difference(face)
tailL=bez((605,756),[
 ((551,728),(480,678),(434,700)),
 ((392,709),(390,759),(419,783)),
 ((433,795),(449,801),(461,800)),
 ((434,820),(417,862),(446,880)),
 ((474,905),(537,866),(598,838)),
 ((615,807),(616,779),(605,756))])
tailR=scale(tailL,-1,1,origin=(742,0))
footL=ellipse(642,839,80,40,-26);footR=scale(footL,-1,1,origin=(742,0));feet=unary_union([footL,footR])
bottom_knot=rounded(710,795,781,847,15)
banner=bez((560,750),[
 ((662,709),(826,709),(929,751)),
 ((948,758),(958,773),(950,794)),
 ((944,813),(943,828),(928,828)),
 ((819,786),(665,789),(567,827)),
 ((549,831),(543,809),(538,790)),
 ((532,771),(538,759),(560,750))])
heartL=bez((434,594),[
 ((418,570),(397,579),(397,605)),
 ((397,636),(430,658),(461,669)),
 ((477,630),(489,603),(468,585)),
 ((450,571),(437,581),(434,594))])
heartR=scale(heartL,-1,1,origin=(742,0));hearts=unary_union([heartL,heartR])
plate=rounded(462,497,1025,742,44)
wingL=bez((870,335),[
 ((843,351),(805,354),(791,337)),
 ((778,322),(794,294),(806,286)),
 ((806,254),(829,231),(849,240)),
 ((877,249),(884,286),(879,309)),
 ((885,319),(879,330),(870,335))])
wingR=bez((899,339),[
 ((923,318),(968,305),(989,320)),
 ((1010,340),(991,383),(967,407)),
 ((944,432),(920,393),(907,370)),
 ((897,360),(893,349),(899,339))])
knot=rotate(rounded(866,301,911,362,14),28,origin=(889,332))
pawL=bez((527,481),[
 ((526,455),(553,440),(577,446)),
 ((607,444),(627,462),(625,486)),
 ((624,500),(618,513),(607,513)),
 ((597,514),(592,511),(591,498)),
 ((593,519),(565,521),(560,498)),
 ((564,516),(539,520),(531,502)),
 ((527,496),(526,488),(527,481))])
pawR=scale(pawL,-1,1,origin=(744,0))
cheeks=unary_union([ellipse(630,465,22,24),ellipse(855,466,22,24)])
eyes=unary_union([ellipse(667,426,16.5,22),ellipse(822,426,16.5,22)])
nose=bez((733,436),[((738,432),(752,432),(757,438)),((760,444),(748,453),(744,456)),((738,451),(727,443),(733,436))])
from shapely.geometry import LineString
mouth=unary_union([LineString([(744,451),(744,462),(734,473),(724,473),(717,466)]).buffer(3.4),LineString([(744,462),(753,473),(764,473),(772,466)]).buffer(3.4)])
# Map the main silhouette to 40 mm in height; the top ring protrudes another 4 mm.
sx=45/724;sy=40/746
def P(g):return translate(scale(g,sx,-sy,origin=(0,0)),-742*sx,893*sy)
partnames=['left','right','head','face','inners','ear_rims','tailL','tailR','feet','bottom_knot','banner','hearts','plate','wingL','wingR','knot','pawL','pawR','cheeks','eyes','nose','mouth','letters','latin']
for name in partnames:globals()[name]=P(globals()[name])
loopcenter=(0,(893-146)*sy)
loop=ellipse(*loopcenter,4,4)
neck=rounded(-2.8,35.6,2.8,40.6,1)
base=unary_union([left,right,head,tailL,tailR,banner,plate,loop,neck,feet,hearts,wingL,wingR,knot,pawL,pawR,bottom_knot]).buffer(.48,quad_segs=10)
# Keep width exactly 45 mm, then drill a round 3 mm hole in calibrated mm units.
width=base.bounds[2]-base.bounds[0]
xf=45/width
for name in partnames:globals()[name]=scale(globals()[name],xf,1,origin=(0,0))
base=scale(base,xf,1,origin=(0,0))
hole=ellipse(0,loopcenter[1],1.5,1.5)
base=base.difference(hole)
def S(g):return g

# A distance-based roundover gives the relief a truly curved upper surface.
res=.065
b=S(base);xmin,ymin,xmax,ymax=b.bounds
xmin-=1;ymin-=1;xmax+=1;ymax+=1
nx=int(np.ceil((xmax-xmin)/res))+1;ny=int(np.ceil((ymax-ymin)/res))+1
shape=(ny,nx)
def mask(g):
 g=S(g);im=Image.new('1',(nx,ny));draw=ImageDraw.Draw(im)
 for p in ([g] if g.geom_type=='Polygon' else g.geoms):
  def pts(r):return [((x-xmin)/res,(y-ymin)/res) for x,y in r.coords]
  draw.polygon(pts(p.exterior),fill=1)
  for r in p.interiors:draw.polygon(pts(r),fill=0)
 return np.array(im,dtype=bool)
base=base.difference(hole)
assert base.buffer(-.4).covers(pawL) and base.buffer(-.4).covers(pawR), 'Paws must be fully supported by the base'
bm=mask(base);dist=edt(bm)*res
height=np.where(bm,1.8-.32+np.sqrt(np.maximum(0,.32**2-np.maximum(0,.32-dist)**2)),0)
def relief(g,z,r):
 global height
 m=mask(g)
 d=edt(m)*res
 h=z-r+np.sqrt(np.maximum(0,r*r-np.maximum(0,r-d)**2))
 height=np.where(m,np.maximum(height,h),height)
def pocket(g,floor,rounding=.35):
 global height
 m=mask(g);d=edt(m)*res;t=np.clip(d/rounding,0,1);t=t*t*(3-2*t)
 height=np.where(m,height*(1-t)+floor*t,height)
relief(unary_union([tailL,tailR]).buffer(-.15),2.16,.36)
relief(ear_rims,2.45,.38)
relief(inners,1.95,.18)
relief(face,2.32,.65)
relief(feet,2.25,.5)
relief(bottom_knot,2.7,.5)
relief(banner.buffer(-.12),2.43,.62)
relief(hearts,2.8,.58)
relief(letters,3,.68)
relief(latin,3,.42)
relief(unary_union([pawL,pawR]),2.97,.7)
relief(wingL,2.94,.75);relief(wingR,2.94,.75);relief(knot,3,.65)
relief(cheeks,2.5,.32)
pocket(unary_union([eyes,nose,mouth]),1.94,.18)
# Smooth the sampled surface, without closing the ring hole or changing the flat underside.
height=gaussian_filter(height,.55);height=np.where(bm,height,0)
zmin=-.195;zs=np.arange(zmin,3.2+res,res)
sd_xy=(edt(bm)-edt(~bm))*res
field=np.minimum(np.minimum(height[:,:,None]-zs[None,None,:],zs[None,None,:]),sd_xy[:,:,None]).astype('float32')
print('marching cubes',field.shape,flush=True)
v,f,_,_=marching_cubes(field,level=0,spacing=(res,res,res),allow_degenerate=False)
v=v[:,[1,0,2]];v[:,0]+=xmin;v[:,1]+=ymin;v[:,2]+=zmin
mesh=trimesh.Trimesh(v,f,process=True);mesh.fix_normals()
print('initial mesh',len(mesh.faces),'watertight',mesh.is_watertight,flush=True)
original_mesh=mesh
mesh=mesh.simplify_quadric_decimation(percent=.77);mesh.process(validate=True);mesh.fix_normals()
if not mesh.is_watertight:
 trimesh.repair.fill_holes(mesh)
 mesh.fix_normals()
if not mesh.is_watertight:
 mesh=original_mesh
 print('Retaining full resolution to preserve a watertight surface',flush=True)
# Normalize bed contact to precisely z=0.
mesh.vertices[:,2]-=mesh.bounds[0,2]
raw=out/'rounded-source.stl';mesh.export(raw)
validation={'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'connected_bodies':len(mesh.split()),'dimensions_mm':mesh.extents.tolist(),'triangles':len(mesh.faces),'volume_mm3':float(mesh.volume)}
print(validation,flush=True);assert validation['watertight'] and validation['connected_bodies']==1
(out/'print-validation.json').write_text(json.dumps(validation,indent=2))
c=Client()
try:
 print(c.execute('file.insert_mesh',{'path':str(raw),'name':'MingyeolSketchV2'}),flush=True)
 try:print(c.execute('appearance.assign',{'bodies':['rounded-source'],'color':'#f2a1b0'}),flush=True)
 except Exception as e:print('appearance',e)
 print(c.tool('save',{'path':str(out/'mingyeol-sketch-v2.solidcraft')}),flush=True)
 for ext in ['stl','3mf']:print(c.tool('export',{'path':str(out/('mingyeol-sketch-v2.'+ext))}),flush=True)
 for view in ['top','iso']:c.tool('screenshot',{'view':view,'grid':False,'axes':False,'width':1400,'height':1400,'path':str(out/('preview-'+view+'.png'))})
finally:c.p.terminate()
print('DONE',flush=True)

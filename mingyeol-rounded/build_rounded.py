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
from rounded_font import round_font_shape
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
left=ellipse(-7.9,39.1,4.9,9.1,19);right=ellipse(7.9,39.1,4.9,8.5,-21)
head=ellipse(0,30.6,12.9,10.1)
# Candy-ribbon tails with rounded lobes and an inward crease, as in the reference.
tailL=bez((-9,6),[
 ((-13,8),(-18,12),(-21,9)),
 ((-23,6),(-18,4),(-17,2.8)),
 ((-18,1.8),(-22,-1),(-18,-2)),
 ((-14,-3),(-10,-.2),(-7,2)),
 ((-6,3),(-7,5),(-9,6))])
tailR=scale(tailL,-1,1,origin=(0,0))
banner=arch(rounded(-13,-1.7,13,4.8,1.8))
# Two rounded feet sit behind the curved name ribbon, peeking below it.
footL=ellipse(-5.8,-1.05,4.65,3.05,22)
footR=scale(footL,-1,1,origin=(0,0))
feet=unary_union([footL,footR])
# Small paired hearts flank the Korean name without overlapping its strokes.
heart=bez((0,.85),[
 ((-.65,2.05),(-2.15,1.7),(-2.1,.45)),
 ((-2.05,-.45),(-.7,-1.45),(0,-2)),
 ((.7,-1.45),(2.05,-.45),(2.1,.45)),
 ((2.15,1.7),(.65,2.05),(0,.85))])
heartL=translate(rotate(heart,14,origin=(0,0)),-18.9,16.7)
heartR=scale(heartL,-1,1,origin=(0,0))
hearts=unary_union([heartL,heartR])
plate=rounded(-17,6,17,24,3.2)
loop=ellipse(0,47.5,3.8,3.8);neck=rounded(-2.9,39,2.9,48,1)
base=unary_union([left,right,head,tailL,tailR,banner,plate,loop,neck,feet,hearts]).buffer(.65,quad_segs=12)
hole=ellipse(0,47.8,1.6,1.6);base=base.difference(hole)
factor=45/(base.bounds[2]-base.bounds[0])
def S(g):return scale(g,factor,factor,origin=(0,0))
# Face and lettering are nested shallow reliefs; a rounded display font replaces the angular font.
original_letters=textshape('민결',30.2,13.6,0,8.1,font=str(ROOT/'fonts/BlackHanSans-Regular.ttf'))
letters=round_font_shape(original_letters,r=1.14)
latin=arch(textshape('MINGYEOL',21.7,3.05,0,.025,font=str(ROOT/'fonts/Jua-Regular.ttf')).buffer(.10,quad_segs=8))
face=head.buffer(-.65).intersection(box(-30,24.7,30,60))
inners=unary_union([ellipse(-8.1,40.5,2.7,6.3,19),ellipse(8.2,40.1,2.6,5.7,-21)])
# The ears are a backing silhouette plus a raised rim, not a pocket cut into the backing.
ear_rims=unary_union([left.buffer(-.35),right.buffer(-.35)]).difference(inners).difference(head.buffer(-.65))
# Two soft folded bow wings and a rounded central knot.
wingL=bez((8.4,38.7),[
 ((7.4,40.5),(6.5,43.7),(4.8,42.9)),
 ((3.7,42.4),(3.6,39.6),(4.0,38.1)),
 ((4.4,36.9),(6.5,37.5),(8.4,38.7))])
wingR=bez((9.2,38.7),[
 ((10.6,40.2),(12.5,42),(13.8,40.6)),
 ((15,39),(14.2,36.5),(12.9,36)),
 ((11.8,35.6),(10.1,37.6),(9.2,38.7))])
knot=ellipse(8.6,38.6,1.4,1.65,-20)
pawL=unary_union([ellipse(-10,25.6,2.8,2),ellipse(-11.6,24.6,.85,1.2),ellipse(-10,24.3,.85,1.25),ellipse(-8.5,24.6,.85,1.15)])
pawL=translate(pawL,1.6,-.35)
pawR=scale(pawL,-1,1,origin=(0,0))
cheeks=unary_union([ellipse(-7.1,29.1,1.5,.9),ellipse(7.1,29.1,1.5,.9)])
eyes=unary_union([ellipse(-4.6,31.4,.84,1.18),ellipse(4.6,31.4,.84,1.18)])
nose=ellipse(0,29.85,.85,.48)
from shapely.geometry import LineString
mouth=unary_union([LineString([(0,29.7),(0,29),(-.65,28.55),(-1.25,28.7),(-1.45,29)]).buffer(.24),LineString([(0,29),(.65,28.55),(1.25,28.7),(1.45,29)]).buffer(.24)])
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
base=unary_union([base,wingL.buffer(.55),wingR.buffer(.55),knot.buffer(.55),pawL.buffer(.55),pawR.buffer(.55)]).difference(hole)
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
relief(face,2.32,.65)
relief(feet,2.27,.62)
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
 print(c.execute('file.insert_mesh',{'path':str(raw),'name':'MingyeolRounded'}),flush=True)
 try:print(c.execute('appearance.assign',{'bodies':['rounded-source'],'color':'#f2a1b0'}),flush=True)
 except Exception as e:print('appearance',e)
 print(c.tool('save',{'path':str(out/'mingyeol-rounded.solidcraft')}),flush=True)
 for ext in ['stl','3mf']:print(c.tool('export',{'path':str(out/('mingyeol-rounded.'+ext))}),flush=True)
 for view in ['top','iso']:c.tool('screenshot',{'view':view,'grid':False,'axes':False,'width':1400,'height':1400,'path':str(out/('preview-'+view+'.png'))})
finally:c.p.terminate()
print('DONE',flush=True)

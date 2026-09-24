from pathlib import Path
import re,json
from PIL import Image,ImageDraw
o=Path('reports/EPC9186-inductance');base='EPC9186_B5453_Rev1_0_Gerbers.'
# Geometry-only preview: linear paths, polygons and approximate rectangular macro apertures.
def parse(ext):
 text=(o/(base+ext)).read_text(); aps={}
 for k,sh,args in re.findall(r'%ADD(\d+)([CR]),([^*]+)\*%',text):
  vals=[float(v)*25.4 for v in args.split('X')];aps[int(k)]=(sh,vals[0],vals[1] if len(vals)>1 else vals[0])
 for k,x,y,rot in re.findall(r'AMPARAMS\|DCode=(\d+)\|XSize=([\d.]+)mil\|YSize=([\d.]+)mil.*?Rotation=([\d.]+)',text):
  x=float(x)*.0254;y=float(y)*.0254
  if round(float(rot))%180==90:x,y=y,x
  aps[int(k)]=('R',x,y)
 text=re.sub(r'%.*?%','',text,flags=re.S)
 x=y=0.;d=2;ap=11;reg=None;shapes=[];fl=[]
 for cmd in text.split('*'):
  cmd=cmd.strip()
  if cmd.startswith('G04'):continue
  if 'G36' in cmd:reg=[];continue
  if 'G37' in cmd:
   if reg:shapes.append(('poly',reg))
   reg=None;continue
  sel=re.fullmatch(r'(?:G54)?D(\d+)',cmd)
  if sel and int(sel[1])>=10:ap=int(sel[1]);continue
  if not re.search('[XY]',cmd) and cmd not in ['D03','D3']:continue
  nx=re.search(r'X(-?\d+)',cmd);ny=re.search(r'Y(-?\d+)',cmd);dd=re.search(r'D0?([123])',cmd)
  xx=float(nx[1])*.000254 if nx else x;yy=float(ny[1])*.000254 if ny else y
  if dd:d=int(dd[1])
  if reg is not None:reg.append((xx,yy))
  elif d==1:shapes.append(('line',(x,y),(xx,yy),aps.get(ap,('C',.1,.1))[1]))
  elif d==3:shapes.append(('flash',(xx,yy),aps.get(ap,('C',.3,.3))));fl.append([ap,xx,yy,*aps.get(ap,('C',.3,.3))])
  x,y=xx,yy
 return shapes,fl
scale=10; bounds=(-85,-55,75,55)
def point(p):return ((p[0]-bounds[0])*scale,(bounds[3]-p[1])*scale)
for ext,overlay in [('GTL','GTO'),('GBL','GBO'),('G1',None)]:
 im=Image.new('RGB',(1600,1100),'#10232a');dr=ImageDraw.Draw(im)
 for layer,color in [(ext,'#bd8d48')]+([(overlay,'white')] if overlay else []):
  shapes,fl=parse(layer)
  if layer==ext:(o/(ext+'-flashes.json')).write_text(json.dumps(fl))
  for s in shapes:
   if s[0]=='line':dr.line([point(s[1]),point(s[2])],fill=color,width=max(1,round(s[3]*scale)))
   elif s[0]=='poly' and len(s[1])>=3:dr.polygon([point(p) for p in s[1]],fill=color)
   elif s[0]=='flash':
    x,y=point(s[1]);sh,w,h=s[2];box=(x-w*scale/2,y-h*scale/2,x+w*scale/2,y+h*scale/2)
    (dr.ellipse if sh=='C' else dr.rectangle)(box,fill=color)
 im.save(o/(ext+'-preview.png'))
print('Approximate previews created; not a connectivity or polarity-accurate Gerber reconstruction.')
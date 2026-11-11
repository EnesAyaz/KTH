from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
from PIL import ImageFont
import json,hashlib

ROOT=Path.cwd();P=ROOT/'reports/paper';A=P/'icpe/vector_alignment_2026-11-07';A.mkdir(parents=True,exist_ok=True)
SRC=P/'Submission-Final/ICPE_Digest_vector_figures_2026-11-07.docx';OUT=P/'Submission-Final/ICPE_Digest_vector_figures_aligned_2026-11-07.docx'
base=P/'icpe/make_compact_digest_figures.py';scope={'__file__':str(base)};exec(base.read_text(encoding='utf-8').split('dimensions={}')[0],scope);scope['A']=A;scope['dimensions']={}
BaseFig=scope['Fig'];bounds=[];font=ImageFont.truetype('C:/Windows/Fonts/times.ttf',1000)

def clip_line(points,rect):
 x0,y0,w,h=rect;x1=x0+w;y1=y0+h;chunks=[];chunk=[]
 for a,b in zip(points,points[1:]):
  dx=b[0]-a[0];dy=b[1]-a[1];lo=0.;hi=1.;valid=True
  for pp,qq in [(-dx,a[0]-x0),(dx,x1-a[0]),(-dy,a[1]-y0),(dy,y1-a[1])]:
   if abs(pp)<1e-15:
    if qq<0:valid=False;break
   else:
    rr=qq/pp
    if pp<0:lo=max(lo,rr)
    else:hi=min(hi,rr)
    if lo>hi:valid=False;break
  if valid:
   aa=(a[0]+lo*dx,a[1]+lo*dy);bb=(a[0]+hi*dx,a[1]+hi*dy)
   if chunk and max(abs(chunk[-1][k]-aa[k]) for k in [0,1])>1e-6:chunks.append(chunk);chunk=[]
   if not chunk:chunk=[aa]
   chunk.append(bb)
  elif chunk:chunks.append(chunk);chunk=[]
 if chunk:chunks.append(chunk)
 for chunk in chunks:assert all(x0-1e-6<=x<=x1+1e-6 and y0-1e-6<=y<=y1+1e-6 for x,y in chunk)
 return chunks

class AlignedFig(BaseFig):
 def __init__(self,w,h):super().__init__(w,h);self.frames=[]
 def axes(self,x,y,w,h,*args):
  idx=len(self.frames);self.frames.append((x,y,w,h))
  self.s.append(f'<defs><clipPath id="alignClip{idx}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs>')
  return super().axes(x,y,w,h,*args)
 def text(self,x,y,t,size=7.5,anchor='start',col='#111111',rotate=None,raw=False):
  if anchor=='end' and rotate is None:y+=1.0
  size=10
  if not raw:
   bb=[v/100 for v in font.getbbox(t,anchor='ls')];shift=0 if anchor=='start' else (bb[2]-bb[0])/2 if anchor=='middle' else bb[2]-bb[0]
   pts=[(xx-shift,yy) for xx in [bb[0],bb[2]] for yy in [bb[1],bb[3]]]
   if rotate==-90:pts=[(yy,-xx) for xx,yy in pts]
   pts=[(x+xx,y+yy) for xx,yy in pts]
   assert min(p[0] for p in pts)>=-.1 and max(p[0] for p in pts)<=self.w+.1,(t,pts)
   assert min(p[1] for p in pts)>=-.1 and max(p[1] for p in pts)<=self.h+.1,(t,pts)
   bounds.append({'text':t,'corners':pts})
  return super().text(x,y,t,size,anchor,col,rotate,raw)
 def line(self,points,col='#111111',dash=None,lw=.7):
  if len(points)>10 and self.frames:
   rect=self.frames[0 if sum(p[0] for p in points)/len(points)<180 else 1]
   for pts in clip_line(points,rect):super().line(pts,col,dash,lw)
  else:super().line(points,col,dash,lw)
 def dot(self,x,y,col='#111111',r=1.5,square=False):
  self.s.append('<g clip-path="url(#alignClip2)">');super().dot(x,y,col,r,square);self.s.append('</g>')

src=(P/'create_revision_fig08.py').read_text(encoding='utf-8')
src=src.replace("A=P/'icpe/revised_blue_2026-11-06'","A=P/'icpe/vector_alignment_2026-11-07'")
src=src.replace("Fig=ns['Fig'];","Fig=AlignedFig;")
src=src.replace('f.axes(29,27,133,67,(-5,45),(0,110)','f.axes(36,27,126,67,(0,45),(-4,110)')
src=src.replace('f.axes(199,27,133,67,(-5,45)','f.axes(202.5,27,126,67,(0,45)')
src=src.replace("f.text(95,10,'(a) Rated current: settings A–C'","f.text(99,10,'(a) Rated current'")
src=src.replace("f.text(265,10,'(b) Rated current: settings A–C'","f.text(265.5,10,'(b) Rated current'")
src=src.replace("'(c) Positive-current sweep'","'(c) Current sweep'")
src=src.replace('ta(-5,90)','ta(0,90)').replace('tb(-5,.8)','tb(0,.8)')
src=src.replace('(x,129),(x+12,129)','(x,126),(x+12,126)').replace('x+16,131','x+16,129')
src=src.replace("f.finish('fig08_routed_margin_map')","f.finish('fig08_aligned')")
exec(src,{'__file__':str(P/'create_revision_fig08.py'),'AlignedFig':AlignedFig})

with ZipFile(SRC) as z:files={n:z.read(n) for n in z.namelist()}
sourcehash=hashlib.sha256(SRC.read_bytes()).hexdigest();files['word/media/vector_quality_8.svg']=(A/'fig08_aligned.svg').read_bytes();files['word/media/image8.png']=(A/'fig08_aligned.png').read_bytes()
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
 for name,data in files.items():z.writestr(name,data)
with ZipFile(SRC) as z:assert z.read('word/document.xml')==files['word/document.xml']
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==sourcehash
(A/'verification.json').write_text(json.dumps({'source_sha256':sourcehash,'axes_rectangles':[(36,27,126,67),(202.5,27,126,67),(369,27,126,67)],'all_text_within_canvas':bounds,'curves_numerically_clipped':True,'data_source':'same raw switching data and results_complete_windows.json as previous figure','body_xml_unchanged':True},indent=2))
print(OUT)

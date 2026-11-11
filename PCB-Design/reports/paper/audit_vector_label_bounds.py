from zipfile import ZipFile
from lxml import etree as E
from PIL import ImageFont
from pathlib import Path
import json
P=Path('reports/paper');z=ZipFile(P/'Submission-Final/ICPE_Digest_vector_figures_aligned_2026-11-07.docx');ns={'s':'http://www.w3.org/2000/svg'};out={}
for i in range(1,9):
 r=E.fromstring(z.read(f'word/media/vector_quality_{i}.svg'));_,_,w,h=map(float,r.get('viewBox').split());bad=[]
 for e in r.findall('.//s:text',ns):
  if len(e):continue
  t=e.text or '';size=float(e.get('font-size','7.5'));font=ImageFont.truetype('C:/Windows/Fonts/times.ttf',round(size*100));bb=[v/100 for v in font.getbbox(t,anchor='ls')]
  anchor=e.get('text-anchor','start');shift=0 if anchor=='start' else (bb[2]-bb[0])/2 if anchor=='middle' else bb[2]-bb[0]
  pts=[(xx-shift,yy) for xx in [bb[0],bb[2]] for yy in [bb[1],bb[3]]]
  if e.get('transform','').startswith('rotate(-90'):pts=[(yy,-xx) for xx,yy in pts]
  x=float(e.get('x'));y=float(e.get('y'));pts=[(x+xx,y+yy) for xx,yy in pts]
  if min(q[0] for q in pts)<-.3 or max(q[0] for q in pts)>w+.3 or min(q[1] for q in pts)<-.3 or max(q[1] for q in pts)>h+.3:bad.append({'text':t,'bounds':[min(q[0] for q in pts),min(q[1] for q in pts),max(q[0] for q in pts),max(q[1] for q in pts)]})
 out[i]=bad
(P/'icpe/vector_alignment_2026-11-07/other_labels_audit.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))

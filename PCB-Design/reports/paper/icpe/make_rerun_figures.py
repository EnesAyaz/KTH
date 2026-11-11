from pathlib import Path
from html import escape
import json,math,subprocess,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from icpe_gate_results import read_raw,T2
from icpe_gate_loop_rerun import RUN
A=Path(__file__).parent/'gate_loop_rerun_2026-11-02'
D=json.loads((A/'results.json').read_text())
TEAL='#018789';WINE='#A41C59';INK='#111111';GREY='#898781';OCHRE='#C38714'
INKSCAPE=r'C:\Program Files\Inkscape\bin\inkscape.com'

class Figure:
 def __init__(self,height):
  self.height=height;self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="{height*160/454}mm" viewBox="0 0 454 {height}"><rect width="454" height="{height}" fill="white"/><g font-family="Times New Roman" font-size="9" fill="{INK}">']
 def text(self,x,y,t,size=9,anchor='start',color=INK,rotate=None):
  tr=f' transform="rotate({rotate} {x} {y})"' if rotate else ''
  self.parts.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}" fill="{color}"{tr}>{escape(t)}</text>')
 def line(self,pts,color=INK,dash=None,width=.9):
  dash=f' stroke-dasharray="{dash}"' if dash else ''
  self.parts.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}"{dash}/>')
 def dot(self,x,y,color,shape='circle'):
  if shape=='circle':self.parts.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="1.8" fill="{color}"/>')
  else:self.parts.append(f'<rect x="{x-1.7:.3f}" y="{y-1.7:.3f}" width="3.4" height="3.4" fill="white" stroke="{color}" stroke-width=".7"/>')
 def rect(self,x,y,w,h,color):self.parts.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{color}"/>')
 def axes(self,x,y,w,h,xlim,ylim,xticks,yticks,xlab,ylab):
  def t(a,b):return x+(a-xlim[0])/(xlim[1]-xlim[0])*w,y+h-(b-ylim[0])/(ylim[1]-ylim[0])*h
  for b in yticks:
   _,yy=t(xlim[0],b);self.line([(x,yy),(x+w,yy)],'#E2E0DA',width=.35);self.text(x-5,yy+3,str(b),8.5,'end')
  for a in xticks:
   xx,_=t(a,ylim[0]);self.line([(xx,y+h),(xx,y+h+3)],width=.5);self.text(xx,y+h+13,str(a),8.5,'middle')
  self.line([(x,y),(x,y+h),(x+w,y+h)],width=.6)
  self.text(x+w/2,y+h+27,xlab,9.5,'middle');self.text(x-31,y+h/2,ylab,9.5,'middle',rotate=-90)
  return t
 def finish(self,name):
  path=A/(name+'.svg');path.write_text(''.join(self.parts)+'</g></svg>',encoding='utf-8')
  for typ in ['pdf','png']:
   cmd=[INKSCAPE,str(path),'--export-type='+typ,'--export-filename='+str(A/(name+'.'+typ))]
   if typ=='png':cmd+=['--export-dpi=450']
   subprocess.run(cmd,check=True,capture_output=True)

styles=[(10,.5,TEAL,None),(10,1,TEAL,'4 2'),(20,.5,WINE,None),(20,1,WINE,'4 2')]
def legend(f,y):
 for j,(g,p,col,dash) in enumerate(styles):
  x=48+101*j;f.line([(x,y-3),(x+14,y-3)],col,dash);f.text(x+18,y,f'{g} / {p:g} nH',8.5)

f=Figure(244);legend(f,14)
maxv=max(max(r['vdsl_pk'],r['vdsh_pk']) for rows in D['single'].values() for r in rows)
vlim=math.ceil(maxv/50)*50
emax=math.ceil(max(r['eon']*1e6 for rows in D['single'].values() for r in rows)/20)*20
for j,field,ylim,yt,ylab in [(0,'stress',(60,vlim),list(range(60,int(vlim)+1,40)),'Peak drain–source voltage (V)'),(1,'eon',(0,emax),list(range(0,int(emax)+1,20)),'Turn-on energy (µJ)')]:
 t=f.axes(42+228*j,40,170,163,(0,170),ylim,[0,40,80,120,160],yt,'Device current (A)',ylab);f.text(42+228*j,33,'(a)' if j==0 else '(b)',10)
 if j==0:f.line([t(0,90),t(170,90)],GREY,'2 3',.7)
 for g,p,col,dash in styles:
  rows=D['single'][f'g{g}_p{p:g}'];pts=[t(r['iload'],max(r['vdsl_pk'],r['vdsh_pk']) if field=='stress' else r['eon']*1e6) for r in rows]
  f.line(pts,col,dash)
  for xy in pts:f.dot(*xy,col,'circle' if g==10 else 'square')
f.finish('single_cell_characterization')

f=Figure(244)
t=f.axes(42,39,170,164,(1.4,8.6),(0,65),[2,3,4,5,6,7,8],[0,20,40,60],'Parallel transistors per switch, n','Total phase-leg loss (W)');f.text(42,32,'(a) 10 nH gate; 0.5 nH power',9.5)
for r in D['parallel']['g10_p0.5']:
 base=0
 for key,col in [('cond',INK),('sw',TEAL),('dead',WINE),('gate',OCHRE)]:
  val=r[key];x,y=t(r['n']-.28,base+val);xx,yy=t(r['n']+.28,base);f.rect(x,y,xx-x,yy-y,col);base+=val
for j,(name,col) in enumerate([('Conduction',INK),('Switching',TEAL),('Dead time',WINE),('Gate drive',OCHRE)]):
 x=7+111*j;f.rect(x,5,6,5,col);f.text(x+10,11,name,8.5)
t=f.axes(270,39,170,164,(1.7,8.3),(70,240),[2,3,4,5,6,7,8],[80,90,120,160,200,240],'Parallel transistors per switch, n','Peak drain–source voltage (V)');f.text(270,32,'(b)',10);f.line([t(1.7,90),t(8.3,90)],GREY,'2 3',.7)
for g,p,col,dash in styles:
 pts=[t(r['n'],r['vpk']) for r in D['parallel'][f'g{g}_p{p:g}']];f.line(pts,col,dash)
 for xy in pts:f.dot(*xy,col,'circle' if g==10 else 'square')
# Compact direct legend occupies the empty area of the voltage panel.
for j,(g,p,col,dash) in enumerate(styles):
 x=307 if j<2 else 377;y=49+(j%2)*12;f.line([(x,y),(x+12,y)],col,dash);f.text(x+15,y+3,f'{g}/{p:g}',8)
f.finish('parallel_count_selection')

f=Figure(270)
cases=[('board_load_g20_on3_revised_drive',INK,None),('board_extracted_g0_on3.5',TEAL,'5 2'),('board_extracted_g0_on2.5',WINE,'5 2 1 2')]
t=f.axes(42,25,170,154,(-5,65),(-5,120),[0,20,40,60],[0,30,60,90,120],'Time from turn-on command (ns)','High-side drain–source voltage (V)');f.text(42,18,'(a)',10)
for name,col,dash in cases:
 z=read_raw(RUN/(name+'.raw'))[0];tt=z['time'];mask=(tt>=T2)&(tt<=T2+150e-9);worst=max(range(1,5),key=lambda k:np.max((z[f'v(dh{k})']-z[f'v(qh_s_{k})'])[mask]));v=z[f'v(dh{worst})']-z[f'v(qh_s_{worst})'];ix=np.flatnonzero((tt>=T2-5e-9)&(tt<=T2+65e-9))[::3];f.line([t((tt[i]-T2)*1e9,v[i]) for i in ix],col,dash)
f.line([t(-5,90),t(65,90)],GREY,'2 3',.7)
t=f.axes(270,25,170,154,(-5,65),(-4,2),[0,20,40,60],[-4,-2,0,2],'Time from turn-on command (ns)','Held-off gate–source voltage (V)');f.text(270,18,'(b)',10)
for name,col,dash in [('board_load_g20_on3',GREY,'2 2'),('board_load_g20_on3_revised_drive',INK,None),('board_extracted_g0_on3.5',TEAL,'5 2')]:
 z=read_raw(RUN/(name+'.raw'))[0];tt=z['time'];v=z['v(gh1)']-z['v(qh_s_1)'];ix=np.flatnonzero((tt>=T2-5e-9)&(tt<=T2+65e-9))[::3];f.line([t((tt[i]-T2)*1e9,v[i]) for i in ix],col,dash)
f.line([t(-5,.8),t(65,.8)],GREY,'2 3',.7)
for x,y,label,col,dash in [(8,226,'Operating: 20 nH, revised drive',INK,None),(8,240,'DPT: extracted, 3.5 Ω on',TEAL,'5 2'),(8,254,'DPT: extracted, 2.5 Ω on',WINE,'5 2 1 2'),(255,226,'Operating: 20 nH, 0 V off',GREY,'2 2'),(255,240,'Operating: 20 nH, −1 V off',INK,None),(255,254,'DPT: extracted, −1.9 V off',TEAL,'5 2')]:
 f.line([(x,y-3),(x+17,y-3)],col,dash);f.text(x+22,y,label,8.5)
f.finish('extracted_network_switching')
print(A)

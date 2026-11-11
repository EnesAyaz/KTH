"""Compact, readable vector versions of the nine retained digest figures."""
from pathlib import Path
from html import escape
import base64,csv,json,math,subprocess,sys
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'reports/paper';A=P/'icpe/latest_digest_figures';A.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'scripts'))
from icpe_gate_results import read_raw,T2
from icpe_gate_loop_rerun import RUN
D=json.loads((P/'icpe/gate_loop_rerun_2026-11-02/results.json').read_text())
INK='#111111';TEAL='#018789';WINE='#A41C59';OCHRE='#C38714';GREY='#898781';LIGHT='#E2E0DA'
INKSCAPE=r'C:\Program Files\Inkscape\bin\inkscape.com'

class Fig:
 def __init__(self,w,h):
  self.w=w;self.h=h
  self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w/72}in" height="{h/72}in" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="white"/><g font-family="Times New Roman" font-size="7.5" fill="{INK}">']
 def text(self,x,y,t,size=7.5,anchor='start',col=INK,rotate=None,raw=False):
  tr=f' transform="rotate({rotate} {x} {y})"' if rotate else ''
  self.s.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}" fill="{col}"{tr}>{t if raw else escape(t)}</text>')
 def line(self,pts,col=INK,dash=None,lw=.7):
  ds=f' stroke-dasharray="{dash}"' if dash else ''
  self.s.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+f'" fill="none" stroke="{col}" stroke-width="{lw}"{ds}/>')
 def rect(self,x,y,w,h,fill='white',stroke=None,lw=.7,dash=None):
  ds=f' stroke-dasharray="{dash}"' if dash else ''
  self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{lw}"{ds}/>')
 def dot(self,x,y,col=INK,r=1.5,square=False):
  if square:self.rect(x-r,y-r,2*r,2*r,'white',col,.7)
  else:self.s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>')
 def arrow(self,pts,col=INK,dash=None):
  self.line(pts,col,dash);a,b=pts[-2:];ang=math.atan2(b[1]-a[1],b[0]-a[0]);v=[b]+[(b[0]-4*math.cos(ang+d),b[1]-4*math.sin(ang+d)) for d in [-.4,.4]]
  self.s.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in v)+f'" fill="{col}"/>')
 def image(self,path,x,y,w,h):
  with Image.open(path) as im:iw,ih=im.size
  scale=min(w/iw,h/ih);ww=iw*scale;hh=ih*scale
  b64=base64.b64encode(Path(path).read_bytes()).decode()
  self.s.append(f'<image x="{x+(w-ww)/2}" y="{y+(h-hh)/2}" width="{ww}" height="{hh}" href="data:image/png;base64,{b64}"/>')
 def axes(self,x,y,w,h,xlim,ylim,xt,yt,xlabel,ylabel):
  def t(a,b):return x+(a-xlim[0])/(xlim[1]-xlim[0])*w,y+h-(b-ylim[0])/(ylim[1]-ylim[0])*h
  for b in yt:
   _,yy=t(xlim[0],b);self.line([(x,yy),(x+w,yy)],LIGHT,lw=.3);self.text(x-4,yy+2.5,str(b),7,'end')
  for a in xt:
   xx,_=t(a,ylim[0]);self.line([(xx,y+h),(xx,y+h+2)],lw=.5);self.text(xx,y+h+11,str(a),7,'middle')
  self.line([(x,y),(x,y+h),(x+w,y+h)],lw=.5)
  self.text(x+w/2,y+h+23,xlabel,7.5,'middle');self.text(x-24,y+h/2,ylabel,7.5,'middle',rotate=-90)
  return t
 def finish(self,name):
  path=A/(name+'.svg');path.write_text(''.join(self.s)+'</g></svg>',encoding='utf-8')
  for typ in ['pdf','png']:
   cmd=[INKSCAPE,str(path),'--export-type='+typ,'--export-filename='+str(A/(name+'.'+typ))]
   if typ=='png':cmd+=['--export-dpi=450']
   subprocess.run(cmd,check=True,capture_output=True)
  dimensions[name]={'width_pt':self.w,'height_pt':self.h,'minimum_main_font_pt':7}
  print(name,flush=True)

dimensions={}

# 1. The same stacked topology and expanded three-phase bridge, with GaN symbols.
f=Fig(454,138)
f.text(3,9,'(a)');f.text(171,11,'Common machine',7.5,'middle');f.rect(137,16,70,104,'#F5F8F7',GREY,.5,'3 2')
f.line([(17,26),(17,119)]);f.rect(12,63,10,18,'white',INK);f.line([(14,69),(20,69)]);f.line([(15,74),(19,74)]);f.text(1,59,'V<tspan baseline-shift="sub" font-size="5.5">dc</tspan>',raw=True)
f.line([(17,66),(17,72)])
f.line([(17,26),(43,26)]);f.line([(17,121),(43,121)]);f.line([(17,119),(17,121)])
f.line([(43,47),(43,63)]);f.line([(43,84),(43,100)])
for y,lab in [(26,'N'),(63,'2'),(100,'1')]:
 f.text(88,y-5,'Submodule '+lab,7.5,'middle')
 f.line([(43,y),(69,y)]);f.line([(43,y+21),(69,y+21)])
 f.line([(43,y),(43,y+8)]);f.line([(37,y+8),(49,y+8)]);f.line([(37,y+11),(49,y+11)]);f.line([(43,y+11),(43,y+21)])
 f.text(51,y+13,'C<tspan baseline-shift="sub" font-size="5.5">'+lab+'</tspan>',7,raw=True)
 f.rect(69,y,41,21,'#F0F5F7',INK);f.line([(69,y+21),(110,y)]);f.text(77,y+8,'=',8);f.text(98,y+18,'3~',8)
 for j in range(3):
  yy=y+4+j*6;f.line([(110,yy),(150,yy)])
  f.s.append(f'<path d="M150 {yy} '+''.join('a2 3 0 0 1 4 0 ' for _ in range(3))+'" fill="none" stroke="#111111" stroke-width=".7"/>')
  f.line([(162,yy),(189,yy)])
 f.line([(189,y+4),(189,y+16)]);f.text(194,y+12,'n<tspan baseline-shift="sub" font-size="5.5">'+lab+'</tspan>',7,raw=True)
f.arrow([(112,30),(134,30)]);f.text(121,24,'i<tspan baseline-shift="sub" font-size="5.5">ph</tspan>',raw=True)
f.text(127,57,'⋮',8,'middle');f.text(174,57,'⋮',8,'middle')
f.text(109,132,'V<tspan baseline-shift="sub" font-size="5.5">m</tspan> = V<tspan baseline-shift="sub" font-size="5.5">dc</tspan>/N',8,'middle',raw=True)
f.text(228,9,'(b)');f.text(349,11,'One three-phase submodule',7.5,'middle')
f.rect(273,20,36,94,'#EDF7F7',TEAL,.7,'3 2');f.line([(257,20),(430,20)]);f.line([(257,114),(430,114)])
f.line([(257,20),(257,58)]);f.line([(251,58),(263,58)]);f.line([(251,61),(263,61)]);f.line([(257,61),(257,114)]);f.text(236,66,'Cm',7)
def gan(x,y):
 f.s.append(f'<circle cx="{x}" cy="{y}" r="9" fill="white" stroke="#111111" stroke-width=".7"/>')
 f.line([(x-6,y-6),(x-6,y+6)]);f.line([(x-12,y),(x-6,y)])
 for a,b in [(-6,-2),(-1,1),(2,6)]:f.line([(x-3,y+a),(x-3,y+b)])
 f.line([(x+2,y-12),(x+2,y-6),(x-3,y-6)]);f.line([(x-3,y+6),(x+2,y+6),(x+2,y+12)])
 f.line([(x+5,y-6),(x+5,y+6)]);f.line([(x+2,y-6),(x+5,y-6)]);f.line([(x+2,y+6),(x+5,y+6)])
 f.s.append(f'<polygon points="{x+2},{y+2} {x+8},{y+2} {x+5},{y-3}" fill="#111111"/>');f.line([(x+2,y-3),(x+8,y-3)])
for j,x in enumerate([289,353,417]):
 for y in [43,91]:gan(x,y)
 f.line([(x+2,20),(x+2,31)]);f.line([(x+2,55),(x+2,79)]);f.line([(x+2,103),(x+2,114)])
 yy=65+j*7;f.dot(x+2,yy,r=1.2);f.line([(x+2,yy),(445,yy)]);f.text(447,yy+3,'abc'[j],7)
f.text(352,131,'Four parallel devices per switch',7.5,'middle');f.finish('fig01_topology')

# 2. The same surveyed points and constant-product contours, with a readable legend.
f=Fig(252,146)
def xy(c,r):return 34+207*math.log10(c/15)/math.log10(4000/15),117-105*math.log10(r/.4)/math.log10(900/.4)
for c in [20,100,500,2000]:
 x,y=xy(c,.4);f.line([(x,12),(x,117)],LIGHT,lw=.3);f.text(x,129,str(c),7,'middle')
for r in [1,10,100]:
 x,y=xy(15,r);f.line([(34,y),(241,y)],LIGHT,lw=.3);f.text(29,y+2,str(r),7,'end')
f.line([(34,12),(34,117),(241,117)],lw=.5)
for tau in [1,2,5,10]:
 pts=[xy(15*(4000/15)**(i/150),1000*tau/(15*(4000/15)**(i/150))) for i in range(151)];pts=[p for p in pts if 12<=p[1]<=117];f.line(pts,GREY,'3 2',.5)
 x,y=xy(21,1000*tau/21);f.text(x,y-2,f'{tau} ps',7,col=GREY)
cols={100:TEAL,200:WINE,350:OCHRE,650:INK}
def mark(x,y,v):
 if v==100:f.dot(x,y,cols[v],1.8)
 elif v==200:f.rect(x-1.8,y-1.8,3.6,3.6,cols[v])
 elif v==350:f.s.append(f'<polygon points="{x},{y-2.3} {x+2.1},{y+2} {x-2.1},{y+2}" fill="{cols[v]}"/>')
 else:f.s.append(f'<polygon points="{x},{y-2.3} {x+2.1},{y} {x},{y+2.3} {x-2.1},{y}" fill="{cols[v]}"/>')
with (P/'icpe/GaN_device_voltage_class_comparison_data.csv').open() as stream:
 for row in csv.DictReader(stream):
  v=int(row['Voltage_class_V']);x,y=xy(float(row['Coss_tr_pF']),float(row['Rds_typ_25C_mOhm']));mark(x,y,v)
  if row['Device']=='EPC2361':f.text(x+3,y+3,'EPC2361',7)
for j,v in enumerate([100,200,350,650]):mark(187,19+10*j,v);f.text(193,22+10*j,f'{v} V',7)
f.text(137,143,'Charge-equivalent capacitance (pF)',7.5,'middle');f.text(9,65,'On-resistance (mΩ)',7.5,'middle',rotate=-90);f.finish('fig02_devices')

# 3–4. All four actual rerun combinations; identical colour/line encoding.
styles=[(10,.5,TEAL,None),(10,1,TEAL,'3 2'),(20,.5,WINE,None),(20,1,WINE,'3 2')]
def inductance_legend(f,y):
 for j,(g,p,c,dash) in enumerate(styles):
  x=15+j*78;f.line([(x,y-2),(x+11,y-2)],c,dash);f.text(x+14,y,f'{g}/{p:g} nH',7)

f=Fig(320,134);inductance_legend(f,8)
for j,key,ylim,yt,ylab in [(0,'vpk',(60,200),[60,100,140,180],'Peak drain voltage (V)'),(1,'eon',(0,100),[0,50,100],'Turn-on energy (µJ)')]:
 t=f.axes(31+j*161,25,112,80,(0,170),ylim,[0,80,160],yt,'Device current (A)',ylab);f.text(31+j*161,19,'(a)' if j==0 else '(b)')
 if j==0:f.line([t(0,90),t(170,90)],GREY,'2 2',.6)
 for g,p,c,dash in styles:
  rows=D['single'][f'g{g}_p{p:g}'];pts=[t(r['iload'],max(r['vdsl_pk'],r['vdsh_pk']) if key=='vpk' else r['eon']*1e6) for r in rows];f.line(pts,c,dash)
  for xx,yy in pts:f.dot(xx,yy,c,1.3,g==20)
f.finish('fig03_single_cell')

f=Fig(320,141)
for j,(label,col) in enumerate([('Conduction',INK),('Switching',TEAL),('Dead time',WINE),('Gate',OCHRE)]):
 x=8+80*j;f.rect(x,2,5,4,col);f.text(x+8,7,label,7)
t=f.axes(31,27,112,80,(1.4,8.6),(0,60),list(range(2,9)),[0,20,40,60],'Parallel count, n','Phase-leg loss (W)');f.text(31,20,'(a) 10 nH / 0.5 nH',7)
for r in D['parallel']['g10_p0.5']:
 base=0
 for key,c in [('cond',INK),('sw',TEAL),('dead',WINE),('gate',OCHRE)]:
  val=r[key];x,y=t(r['n']-.28,base+val);xx,yy=t(r['n']+.28,base);f.rect(x,y,xx-x,yy-y,c);base+=val
t=f.axes(192,27,112,80,(1.7,8.3),(75,185),list(range(2,9)),[90,120,150,180],'Parallel count, n','Peak drain voltage (V)');f.text(192,20,'(b)',7);f.line([t(1.7,90),t(8.3,90)],GREY,'2 2',.6)
for g,p,c,dash in styles:
 pts=[t(r['n'],r['vpk']) for r in D['parallel'][f'g{g}_p{p:g}']];f.line(pts,c,dash)
 for xx,yy in pts:f.dot(xx,yy,c,1.3,g==20)
inductance_legend(f,140);f.finish('fig04_parallel_count')

# 5. Three panels in one row, retaining the sensitivity, paired drive and Kelvin concepts.
f=Fig(454,117);f.text(1,8,'(a) Sharing sensitivity');f.text(155,8,'(b) Two independently driven pairs');f.text(333,8,'(c) Kelvin return')
for y,label,v in [(23,'Power loop: ΔL = 0.3 nH',2),(47,'Gate loop: 2 / 8 nH',19),(71,'No Kelvin: ΔLs = 0.2 nH',29)]:
 f.text(2,y,label,7);f.rect(2,y+3,v*3,7,GREY if v==2 else WINE);f.text(6+v*3,y+10,f'{v}%',7)
f.text(2,102,'75 V / 120 A; energy imbalance',7,col=GREY)
def small_fet(x,y,left,label):
 k=1 if left else -1
 f.line([(x,y-7),(x,y-4),(x+k*4,y-4),(x+k*4,y+4),(x,y+4),(x,y+7)])
 f.line([(x+k*6,y-4),(x+k*6,y+4)]);f.line([(x+k*12,y),(x+k*6,y)])
 f.text(x-3 if left else x+3,y+2,label,7,'end' if left else 'start')
for idx,yy in enumerate([34,80]):
 f.rect(225,yy-16,35,32,'#F5F5F3',INK);f.text(242.5,yy-19,'Driver '+str(idx+1),7,'middle')
 f.text(242.5,yy-6,'HO',7,'middle',WINE);f.text(242.5,yy+10,'LO',7,'middle',TEAL)
 for side,x in [(True,181),(False,304)]:
  n=idx*2+(1 if side else 2)
  small_fet(x,yy-9,side,'QH'+str(n));small_fet(x,yy+9,side,'QL'+str(n))
  gx=x+(12 if side else -12)
  for gy,c in [(yy-9,WINE),(yy+9,TEAL)]:
   start=225 if side else 260;f.line([(start,gy),(gx,gy)],c);rr=(start+gx)/2;f.rect(rr-3,gy-1.7,6,3.4,'white',c,.6)
f.text(244,109,'Two gates per driver output',7,'middle')
for j,lab in enumerate(['G/K','D','S','D','S','D']):
 xx=335+j*17;f.rect(xx,20,13,27,'#F5F5F3',GREY,.5)
 if j==0:f.text(xx+6.5,30,'G',7,'middle',WINE);f.text(xx+6.5,42,'K',7,'middle',TEAL)
 else:f.text(xx+6.5,36,lab,7,'middle')
f.rect(334,71,33,24,'#F5F5F3',INK);f.text(350.5,81,'Driver',7,'middle');f.text(350.5,91,'output',7,'middle')
f.line([(367,78),(410,78)],WINE);f.text(385,74,'G',7,'middle',WINE)
f.line([(410,70),(410,85)]);f.line([(414,69),(414,86)]);f.line([(414,69),(422,69),(422,58),(440,58)])
f.line([(414,86),(422,86),(422,94)]);f.line([(422,86),(422,90),(367,90)],TEAL,'2 2');f.text(389,102,'K',7,'middle',TEAL)
f.s.append('<path d="M422 94 c5 0 5 4 0 4 c5 0 5 4 0 4 v5" fill="none" stroke="#111111" stroke-width=".7"/>')
f.text(431,102,'Ls',7);f.text(442,57,'D',7);f.text(453,110,'S power',7,'end');f.finish('fig05_gate_drive')

# 6. Same six stages; a shallow one-row layout saves height while keeping 7.5 pt labels.
f=Fig(454,78)
blocks=[['Initial sizing','75 V; four devices'],['KiCad','Place and route'],['Ansys Q3D','Power / gate R, L, M'],['LTspice','Switching assessment'],['Check targets','Update loss / Tj'],['Experimental DPT','Planned correlation']]
for i,lines in enumerate(blocks):
 x=2+76*i;f.rect(x,5,69,34,'white',INK)
 for j,t in enumerate(lines):f.text(x+34.5,19+j*11,t,7,'middle')
 if i<5:f.arrow([(x+69,22),(x+76,22)],GREY if i==4 else INK,'2 2' if i==4 else None)
f.arrow([(340,39),(340,54),(112,54),(112,39)],WINE);f.text(226,51,'Refine layout / gate drive',7,'middle',WINE)
f.arrow([(340,54),(340,70),(36,70),(36,39)],WINE,'3 2');f.text(189,77,'Revisit voltage or parallel count if required',7,'middle',WINE);f.finish('fig06_workflow')

# 7. Same two board renders and two extracted-loop plots, arranged in one readable row.
f=Fig(454,97)
for x,path,label in [(0,'r3d_load.png','(a) Operating board'),(114,'r3d_dpt_top.png','(b) DPT board')]:
 f.text(x+2,8,label,7.5);f.image(P/'figures/revb'/path,x+1,13,106,74)
f.text(230,8,'(c) Power loop (nH)',7.5)
# loop split per cell from Q3D (simulation/bb_q3d/loop_breakdown.py; DPT: board with the 15 SW vias per cell)
LBK=json.loads((ROOT/'simulation/bb_q3d/results/loop_breakdown.json').read_text())
for y,label,b in [(27,'Operating','load'),(46,'DPT','dpt')]:
 d=LBK[b];vals=[(d['copper'],INK),(d['esl_part'],TEAL)]+([(d['shunt_part'],WINE)] if d['shunt_part']>1e-4 else [])
 f.text(230,y+5,label,7);xx=265
 for val,col in vals:f.rect(xx,y,val*70,7,col);xx+=val*70
 f.text(xx+3,y+6,f"{d['total']:.2f}",7)
for yy,label,col in [(66,'Copper',INK),(78,'Capacitor ESL',TEAL),(90,'Shunt',WINE)]:f.rect(231,yy-5,5,5,col);f.text(239,yy,label,7)
f.text(345,8,'(d) Gate loop (nH)',7.5)
for y,label,val,c in [(24,'HS indiv.',12.5,WINE),(41,'HS pair',20.6,WINE),(58,'LS indiv.',7.6,TEAL),(75,'LS pair',12.3,TEAL)]:
 f.text(345,y+5,label,7);f.rect(379,y,val*2.2,7,c);f.text(382+val*2.2,y+6,str(val),7)
f.finish('fig07_boards')

# 8. All three original Q3D geometry views; the larger external net legend is authoritative.
f=Fig(454,100)
for x,name,label in [(0,'q3d_loop_load.png','(a) Operating power network'),(151,'q3d_loop_dpt.png','(b) DPT power network'),(302,'q3d_model_cells.png','(c) Cell-pair detail')]:
 f.text(x+3,8,label,7.5);f.image(P/'figures/revb'/name,x+1,12,148,72)
for x,label,c in [(5,'DC+', '#d92c27'),(65,'DC−','#2167b7'),(127,'Switch node','#ed9c20'),(225,'Shunt path','#329f50'),(323,'Device / capacitor terminals','#d5b85b')]:
 f.rect(x,90,5,5,c);f.text(x+9,96,label,7.5)
f.finish('fig08_q3d')

# 9. Same rerun traces, with short legends and full-size scientific lettering.
f=Fig(320,163)
cases=[('board_load_g20_on3_revised_drive',INK,None),('board_extracted_g0_on3.5',TEAL,'4 2'),('board_extracted_g0_on2.5',WINE,'4 2 1 2')]
t=f.axes(31,17,112,80,(-5,65),(-5,120),[0,30,60],[0,60,90,120],'Time from command (ns)','High-side drain voltage (V)');f.text(31,10,'(a)')
for name,c,dash in cases:
 z=read_raw(RUN/(name+'.raw'))[0];tt=z['time'];mask=(tt>=T2)&(tt<=T2+150e-9);k=max(range(1,5),key=lambda k:np.max((z[f'v(dh{k})']-z[f'v(qh_s_{k})'])[mask]));v=z[f'v(dh{k})']-z[f'v(qh_s_{k})'];ii=np.flatnonzero((tt>=T2-5e-9)&(tt<=T2+65e-9))[::3];f.line([t((tt[i]-T2)*1e9,v[i]) for i in ii],c,dash)
f.line([t(-5,90),t(65,90)],GREY,'2 2',.6)
t=f.axes(192,17,112,80,(-5,65),(-4,2),[0,30,60],[-4,-2,0,2],'Time from command (ns)','Held-off gate voltage (V)');f.text(192,10,'(b)')
for name,c,dash in [('board_load_g20_on3',GREY,'2 2'),('board_load_g20_on3_revised_drive',INK,None),('board_extracted_g0_on3.5',TEAL,'4 2')]:
 z=read_raw(RUN/(name+'.raw'))[0];tt=z['time'];v=z['v(gh1)']-z['v(qh_s_1)'];ii=np.flatnonzero((tt>=T2-5e-9)&(tt<=T2+65e-9))[::3];f.line([t((tt[i]-T2)*1e9,v[i]) for i in ii],c,dash)
f.line([t(-5,.8),t(65,.8)],GREY,'2 2',.6)
for x,y,lab,c,dash in [(4,133,'Operating: 20 nH, revised drive',INK,None),(4,146,'DPT: 3.5 Ω effective on',TEAL,'4 2'),(4,159,'DPT: 2.5 Ω effective on',WINE,'4 2 1 2'),(169,133,'Operating: 0 V off',GREY,'2 2'),(169,146,'Operating: −1 V off',INK,None),(169,159,'DPT: −1.9 V off',TEAL,'4 2')]:
 f.line([(x,y-2),(x+11,y-2)],c,dash);f.text(x+15,y,lab,7)
f.finish('fig09_switching')

(A/'dimensions.json').write_text(json.dumps(dimensions,indent=2))

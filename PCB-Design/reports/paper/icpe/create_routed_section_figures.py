from pathlib import Path
import subprocess,json,math,re
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
P=Path(r'C:\Github\KTH\PCB-Design\reports\paper');R=P.parents[1];A=P/'icpe';W=454
pop=Path(r'C:\Users\enesa\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe')
pdfmetrics.registerFont(TTFont('TimesLocal',r'C:\Windows\Fonts\times.ttf'))
INK='#111111';TEAL='#018789';WINE='#A41C59';OCHRE='#C38714';GREY='#898781'
def text(c,x,y,t,size=10,align='left',col=INK):
 c.setFillColor(col);c.setFont('TimesLocal',size);getattr(c,{'left':'drawString','center':'drawCentredString','right':'drawRightString'}[align])(x,y,t)
def line(c,pts,col=INK,dash=None,lw=1):
 c.setStrokeColor(col);c.setLineWidth(lw);c.setDash(dash or []);z=c.beginPath();z.moveTo(*pts[0]);[z.lineTo(*pt) for pt in pts[1:]];c.drawPath(z);c.setDash([])
def finish(c,name):
 c.save();subprocess.run([str(pop),'-singlefile','-r','400','-png',str(A/(name+'.pdf')),str(A/name)],check=True)
 subprocess.run([r'C:\Program Files\Inkscape\bin\inkscape.com',str(A/(name+'.pdf')),'--export-type=svg','--export-plain-svg','--export-filename='+str(A/(name+'.svg'))],check=True)
def box(c,x,y,w,h,ls):
 c.setFillColor('white');c.setStrokeColor(INK);c.setLineWidth(.8);c.rect(x,y,w,h,fill=1,stroke=1)
 for j,l in enumerate(ls):text(c,x+w/2,y+h/2+(len(ls)-1)*6-j*12-3,l,10,'center')
def arrow(c,pts,col=INK,dash=None):
 line(c,pts,col,dash,.8);a,b=pts[-2:];ang=math.atan2(b[1]-a[1],b[0]-a[0]);z=c.beginPath();z.moveTo(*b)
 for off in [-.5,.5]:z.lineTo(b[0]-5*math.cos(ang+off),b[1]-5*math.sin(ang+off))
 z.close();c.setFillColor(col);c.drawPath(z,fill=1,stroke=0)
# Fig 6
c=canvas.Canvas(str(A/'routed_design_workflow.pdf'),pagesize=(W,202))
for x,y,ls in [(8,136,['Initial sizing','75 V; four devices/switch']),(163,136,['KiCad','Placement and routing']),(318,136,['Ansys Q3D','Power / gate R, L and M']),(318,52,['LTspice','Overshoot, gate voltage','Sharing and energy']),(163,52,['Assess design targets','Update losses / temperature']),(8,52,['Experimental DPT','Planned correlation'])]:box(c,x,y,128,49,ls)
arrow(c,[(136,160),(163,160)]);arrow(c,[(291,160),(318,160)]);arrow(c,[(382,136),(382,101)]);arrow(c,[(318,76),(291,76)]);arrow(c,[(163,76),(136,76)],GREY,[3,2]);arrow(c,[(227,101),(227,136)],WINE)
text(c,234,119,'Refine layout / drive',9,col=WINE)
arrow(c,[(202,52),(202,30),(3,30),(3,120),(72,120),(72,136)],WINE,[3,2]);text(c,126,15,'Revisit voltage or parallel count if necessary',9,'center',WINE)
finish(c,'routed_design_workflow')
# Fig 7 board variants + quantitative extracted network
c=canvas.Canvas(str(A/'board_parasitic_comparison.pdf'),pagesize=(W,307))
for x,path,label in [(0,'r3d_load.png','(a) Operating board'),(231,'r3d_dpt_top.png','(b) DPT board')]:
 c.drawImage(str(P/'figures/revb'/path),x+5,170,width=212,height=113,preserveAspectRatio=True,anchor='c',mask='auto');text(c,x+110,290,label,10,'center')
text(c,7,152,'(c) Commutation-loop composition',10)
# horizontal bars with exact stacked composition
for y,label,vals in [(115,'Operating',[(.35,INK),(.06,TEAL)]),(82,'DPT',[(.47,INK),(.06,TEAL),(.12,WINE)])]:
 text(c,7,y+4,label,9);xx=62
 for val,col in vals:c.setFillColor(col);c.rect(xx,y,val*190,13,fill=1,stroke=0);xx+=val*190
 text(c,xx+5,y+3,f'{sum(v for v,_ in vals):.2f} nH',9)
for x,y,label,col in [(8,54,'Copper',INK),(79,54,'Capacitor ESL',TEAL),(8,36,'Shunt',WINE)]:
 c.setFillColor(col);c.rect(x,y,7,6,fill=1,stroke=0);text(c,x+11,y,label,9)
text(c,234,152,'(d) DPT gate-loop inductance',10)
for y,label,v,col in [(118,'HS, individual',12.5,WINE),(93,'HS, pair-driven',20.6,WINE),(68,'LS, individual',7.6,TEAL),(43,'LS, pair-driven',12.3,TEAL)]:
 text(c,234,y+4,label,9);c.setFillColor(col);c.rect(324,y,v*4,12,fill=1,stroke=0);text(c,329+v*4,y+3,str(v),9)
text(c,385,20,'Inductance (nH)',9,'center');finish(c,'board_parasitic_comparison')
# Raw reader and two switching panels. No unsaved/new simulation data.
def read_raw(path):
 data=path.read_bytes();mark='Binary:\n'.encode('utf-16-le');off=data.index(mark)+len(mark);hdr=data[:off].decode('utf-16-le')
 nv=int(re.search(r'No. Variables:\s*(\d+)',hdr).group(1));nn=int(re.search(r'No. Points:\s*(\d+)',hdr).group(1));names=re.findall(r'^\t\d+\t(\S+)\t',hdr,re.M)
 a=np.frombuffer(data,np.dtype([('t','<f8')]+[(str(i),'<f4') for i in range(1,nv)]),count=nn,offset=off)
 return {names[i].lower():np.abs(a['t']) if i==0 else a[str(i)] for i in range(nv)}
raw={k:read_raw(R/'simulation/bb_spice'/('REVB_Q3D_'+k+'.raw')) for k in ['load_rg3','load','dpt','dpt_rg2.5']};T2=12.167e-6

def axes(c,x,y,w,h,ylims,yt,ylab):
 def t(a,b):return x+(a+5)/70*w,y+(b-ylims[0])/(ylims[1]-ylims[0])*h
 for b in yt:
  yy=t(0,b)[1];line(c,[(x,yy),(x+w,yy)],'#E2E0DA',lw=.35);text(c,x-5,yy-3,str(b),9,'right')
 for a in [0,20,40,60]:
  xx=t(a,0)[0];line(c,[(xx,y),(xx,y-3)],lw=.6);text(c,xx,y-14,str(a),9,'center')
 line(c,[(x,y+h),(x,y),(x+w,y)],lw=.6);text(c,x+w/2,y-30,'Time from turn-on command (ns)',9,'center')
 c.saveState();c.translate(x-30,y+h/2);c.rotate(90);text(c,0,0,ylab,10,'center');c.restoreState();return t
c=canvas.Canvas(str(A/'extracted_network_switching.pdf'),pagesize=(W,280))
t=axes(c,43,111,172,143,(-5,115),[0,30,60,90],'High-side drain–source voltage (V)');text(c,43,265,'(a)',11)
for key,col,dash in [('load_rg3',INK,[]),('dpt',TEAL,[5,2]),('dpt_rg2.5',WINE,[5,2,1,2])]:
 z=raw[key];tt=z['time'];mask=(tt>T2)&(tt<T2+150e-9);j=1+int(np.argmax([np.max((z[f'v(dh{q})']-z[f'v(qh_s_{q})'])[mask]) for q in range(1,5)]));v=z[f'v(dh{j})']-z[f'v(qh_s_{j})'];ii=np.flatnonzero((tt>T2-5e-9)&(tt<T2+65e-9))[::3];line(c,[t((tt[i]-T2)*1e9,float(v[i])) for i in ii],col,dash,.9)
line(c,[t(-5,90),t(65,90)],GREY,[2,3],.7)
t=axes(c,273,111,172,143,(-4,2),[-4,-2,0,2],'Held-off gate–source voltage (V)');text(c,273,265,'(b)',11)
for key,col,dash in [('load',INK,[]),('dpt',TEAL,[5,2])]:
 z=raw[key];tt=z['time'];v=z['v(gh1)']-z['v(qh_s_1)'];ii=np.flatnonzero((tt>T2-5e-9)&(tt<T2+65e-9))[::3];line(c,[t((tt[i]-T2)*1e9,float(v[i])) for i in ii],col,dash,.9)
line(c,[t(-5,.8),t(65,.8)],GREY,[2,3],.7);text(c,*t(28,.95),'0.8 V threshold',9,col=GREY)
for x,y,label,col,dash in [(12,43,'(a) Operating: 3 Ω; preliminary gate model',INK,[]),(12,27,'DPT: 3.5 Ω; extracted gate network',TEAL,[5,2]),(12,11,'DPT: 2.5 Ω; extracted gate network',WINE,[5,2,1,2]),(260,43,'(b) Operating: 0 V turn-off bias',INK,[]),(260,27,'DPT: −1.9 V turn-off bias',TEAL,[5,2])]:
 line(c,[(x,y+3),(x+19,y+3)],col,dash,.9);text(c,x+24,y,label,8.5)
finish(c,'extracted_network_switching')

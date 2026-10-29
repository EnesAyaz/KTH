from pathlib import Path
import json,math,subprocess,xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
P=Path(r'C:\Github\KTH\PCB-Design\reports\paper');A=P/'icpe/digest_5page_assets';A.mkdir(exist_ok=True);W=454
pdfmetrics.registerFont(TTFont('DigestTimes',r'C:\Windows\Fonts\times.ttf'))
INK='#111111';TEAL='#018789';WINE='#A41C59';GREY='#898781'
pop=r'C:\Users\enesa\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe';inkscape=r'C:\Program Files\Inkscape\bin\inkscape.com'
def text(c,x,y,t,size=9,align='left',col=INK):
 c.setFillColor(col);c.setFont('DigestTimes',size);getattr(c,{'left':'drawString','center':'drawCentredString','right':'drawRightString'}[align])(x,y,t)
def line(c,pts,col=INK,dash=None,w=.9):
 c.setStrokeColor(col);c.setLineWidth(w);c.setDash(dash or []);z=c.beginPath();z.moveTo(*pts[0]);[z.lineTo(*q) for q in pts[1:]];c.drawPath(z);c.setDash([])
def finish(c,name):
 c.save();subprocess.run([pop,'-singlefile','-r','450','-png',str(A/(name+'.pdf')),str(A/name)],check=True);subprocess.run([inkscape,str(A/(name+'.pdf')),'--export-type=svg','--export-plain-svg','--export-filename='+str(A/(name+'.svg'))],check=True)
def axes(c,x,y,w,h,xlim,ylim,xt,yt,xlab,ylab):
 def t(a,b):return x+w*(a-xlim[0])/(xlim[1]-xlim[0]),y+h*(b-ylim[0])/(ylim[1]-ylim[0])
 for v in yt:
  yy=t(0,v)[1];line(c,[(x,yy),(x+w,yy)],'#E2E0DA',w=.35);text(c,x-4,yy-3,str(v),8,'right')
 for v in xt:
  xx=t(v,0)[0];text(c,xx,y-13,str(v),8,'center')
 line(c,[(x,y+h),(x,y),(x+w,y)],w=.6);text(c,x+w/2,y-28,xlab,9,'center');c.saveState();c.translate(x-27,y+h/2);c.rotate(90);text(c,0,0,ylab,9,'center');c.restoreState();return t
r=json.loads((P.parents[1]/'reports/slides/data/revb_flow_numbers.json').read_text())
c=canvas.Canvas(str(A/'digest_selection.pdf'),pagesize=(W,170))
t=axes(c,38,43,102,103,(.5,4.5),(0,1.2),[1,2,3,4],[0,.5,1],'Voltage class (V)','Relative D-FOM')
for i,(v,tau) in enumerate([(100,1.35),(200,4.14),(350,6.875),(650,4.90)],1):
 a,b=t(i-.25,0);X,Y=t(i+.25,math.sqrt(1.35/tau));c.setFillColor(TEAL if i==1 else GREY);c.rect(a,b,X-a,Y-b,fill=1,stroke=0);c.setFillColor('white');c.rect(t(i,0)[0]-9,26,18,13,fill=1,stroke=0);text(c,t(i,0)[0],30,str(v),8,'center')
text(c,38,157,'(a)',10)
nr=[v for v in r['npar']['0.5nH'] if v['n']>=2]
t=axes(c,192,43,102,103,(1.5,8.5),(0,45),[2,4,6,8],[0,20,40],'Devices per switch','Phase-leg loss (W)')
line(c,[t(v['n'],v['tot']) for v in nr],TEAL);line(c,[t(v['n'],v['cond']) for v in nr],INK,[4,2]);text(c,192,157,'(b)',10);text(c,226,134,'Total',8,col=TEAL);text(c,226,122,'Conduction',8)
t=axes(c,344,43,102,103,(2,8),(75,185),[2,4,6,8],[90,130,180],'Devices per switch','Peak drain voltage (V)')
for key,col,dash in [('0.5nH',TEAL,None),('1nH',WINE,[4,2])]:
 vals=[v for v in r['npar'][key] if v['n']>=2];line(c,[t(v['n'],v['vpk']) for v in vals],col,dash)
line(c,[t(2,90),t(8,90)],GREY,[2,2],.7);text(c,344,157,'(c)',10);text(c,382,134,'1 nH',8,col=WINE);text(c,382,122,'0.5 nH',8,col=TEAL)
finish(c,'digest_selection')
# Paired-drive circuit is reused as editable SVG; workflow drawn at the same label scale.
source=ET.parse(P/'icpe/paired_gate_drive_cell_layout_v2.svg').getroot()
source.set('x','0');source.set('y','8');source.set('width','238');source.set('height','186');source.set('viewBox','198 0 256 200');source.set('overflow','hidden')
for e in source.iter():
 if e.tag.endswith('text') and e.text=='(b)':e.text='(a)'
s=['<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="74mm" viewBox="0 0 454 210"><defs><marker id="ar" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="#111111"/></marker></defs><rect width="454" height="210" fill="white"/>',ET.tostring(source,encoding='unicode')]
def tx(x,y,t):s.append(f'<text x="{x}" y="{y}" font-family="Times New Roman" font-size="10" text-anchor="middle">{t}</text>')
tx(269,17,'(b)');tx(354,17,'Extraction-based refinement')
for y,a,b in [(30,'KiCad','Place and route'),(74,'Ansys Q3D','Power and gate networks'),(118,'LTspice','Stress, sharing and energy'),(162,'Check targets','Update losses / temperature')]:
 s.append(f'<rect x="275" y="{y}" width="160" height="33" fill="white" stroke="#111111" stroke-width="0.8"/>');tx(355,y+13,a);tx(355,y+26,b)
 if y<162:s.append(f'<path d="M355 {y+33} V{y+44}" fill="none" stroke="#111111" stroke-width="0.8" marker-end="url(#ar)"/>')
s.append('<path d="M275 178 H259 V47 H275" fill="none" stroke="#A41C59" stroke-width="0.9" marker-end="url(#ar)"/>');s.append('</svg>');(A/'digest_gate_workflow.svg').write_text('\n'.join(s),encoding='utf-8')
for ext in ['png','pdf']:
 cmd=[inkscape,str(A/'digest_gate_workflow.svg'),'--export-type='+ext,'--export-filename='+str(A/('digest_gate_workflow.'+ext))]
 if ext=='png':cmd+=['--export-width=2400']
 subprocess.run(cmd,check=True)
# Essential physical PCB and Q3D views together.
c=canvas.Canvas(str(A/'digest_hardware_q3d.pdf'),pagesize=(W,275))
for x,y,w,h,f,label in [(2,145,218,112,'r3d_load.png','(a) Operating board'),(234,145,218,112,'r3d_dpt_top.png','(b) DPT board'),(2,22,218,111,'q3d_loop_load.png','(c) Operating-board Q3D model'),(234,22,218,111,'q3d_loop_dpt.png','(d) DPT-board Q3D model')]:
 c.drawImage(str(P/'figures/revb'/f),x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto');text(c,x+4,y+h+4,label,9)
for x,label,col in [(12,'DC+','#d92c27'),(80,'DC−','#2167b7'),(148,'AC','#ed9c20'),(210,'Source-to-shunt','#329f50'),(335,'Terminals','#d5b85b')]:
 c.setFillColor(col);c.rect(x,6,6,6,fill=1,stroke=0);text(c,x+10,6,label,9)
finish(c,'digest_hardware_q3d')

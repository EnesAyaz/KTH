from pathlib import Path
import json,csv,subprocess
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
root=Path(r'C:\Github\KTH\PCB-Design');out=root/'reports/paper/icpe';d=json.loads((root/'reports/slides/data/revb_flow_numbers.json').read_text())
pdfmetrics.registerFont(TTFont('TimesPaper',r'C:\Windows\Fonts\times.ttf'))
pop=r'C:\Users\enesa\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe'
ink='#111111';teal='#018789';wine='#A41C59';ochre='#C38714';grey='#898781'
def txt(c,x,y,t,size=10,align='left',col=ink):
 c.setFillColor(col);c.setFont('TimesPaper',size);getattr(c,{'left':'drawString','center':'drawCentredString','right':'drawRightString'}[align])(x,y,t)
def seg(c,pts,col=ink,dash=None,w=1):
 c.setStrokeColor(col);c.setLineWidth(w);c.setDash(dash or []);p=c.beginPath();p.moveTo(*pts[0]);[p.lineTo(*pt) for pt in pts[1:]];c.drawPath(p);c.setDash([])
def axes(c,x,y,w,h,xlim,ylim,xt,yt,xlab,ylab):
 def t(a,b):return x+w*(a-xlim[0])/(xlim[1]-xlim[0]),y+h*(b-ylim[0])/(ylim[1]-ylim[0])
 for b in yt:
  yy=t(xlim[0],b)[1];seg(c,[(x,yy),(x+w,yy)],'#E2E0DA',w=.35);txt(c,x-6,yy-3,str(b),9,'right')
 for a in xt:
  xx=t(a,ylim[0])[0];seg(c,[(xx,y),(xx,y-3)],w=.6);txt(c,xx,y-15,str(a),9,'center')
 seg(c,[(x,y+h),(x,y),(x+w,y)],w=.65);txt(c,x+w/2,y-31,xlab,10,'center')
 c.saveState();c.translate(x-32,y+h/2);c.rotate(90);txt(c,0,0,ylab,10,'center');c.restoreState();return t

def points(c,pts,col):
 for x,y in pts:c.setFillColor(col);c.circle(x,y,2,stroke=0,fill=1)
def finish(c,name):
 c.save();subprocess.run([pop,'-singlefile','-r','450','-png',str(out/(name+'.pdf')),str(out/name)],check=True)
# Figure 3: same actual current samples for stress and energy.
name='single_cell_characterization';c=canvas.Canvas(str(out/(name+'.pdf')),pagesize=(454,223))
for j,field,ylim,yt,ylab in [(0,'vpk',(60,200),[60,90,120,160,200],'Peak drain–source voltage (V)'),(1,'eon',(0,85),[0,20,40,60,80],'Turn-on energy (µJ)')]:
 t=axes(c,43+228*j,46,172,141,(0,170),ylim,[0,40,80,120,160],yt,'Device current (A)',ylab)
 txt(c,43+228*j,204,'(a)' if j==0 else '(b)',11)
 if j==0:seg(c,[t(0,90),t(170,90)],grey,[2,3],.8);txt(c,*t(15,94),'90 V target',9,col=grey)
 for key,col,dash in [('0.5nH',teal,None),('1nH',wine,[5,3])]:
  vals=d['single'][key];pts=[t(i,v*(1e6 if field=='eon' else 1)) for i,v in zip(vals['I'],vals[field]) if i<170]
  seg(c,pts,col,dash);points(c,pts,col)
# common legend above plot
for x,key,col,dash in [(85,'0.5 nH',teal,None),(180,'1 nH',wine,[5,3])]:
 seg(c,[(x,216),(x+18,216)],col,dash);txt(c,x+23,212,key,9)
finish(c,name)
# Figure 4: parallel count loss and voltage.
name='parallel_count_selection';c=canvas.Canvas(str(out/(name+'.pdf')),pagesize=(454,235))
nr=[r for r in d['npar']['0.5nH'] if r['n']>=2]
t=axes(c,43,46,172,150,(1.4,8.6),(0,45),[2,3,4,5,6,7,8],[0,10,20,30,40],'Parallel transistors per switch, n','Total phase-leg loss (W)');txt(c,43,214,'(a)',11)
for r in nr:
 base=0
 for val,col in [(r['cond'],ink),(r['sw'],teal),(r['dead']+r['gate'],ochre)]:
  x,y=t(r['n']-.27,base);X,Y=t(r['n']+.27,base+val);c.setFillColor(col);c.rect(x,y,X-x,Y-y,fill=1,stroke=0);base+=val
 if r['n']==4:
  x,y=t(4,base);txt(c,x,y+5,'18.0 W',9,'center',teal)
for x,label,col in [(45,'Conduction',ink),(139,'Switching',teal),(235,'Dead time + gate',ochre)]:
 c.setFillColor(col);c.rect(x,226,7,5,fill=1,stroke=0);txt(c,x+11,224,label,9)
t=axes(c,271,46,172,150,(1.6,8.4),(70,190),[2,3,4,5,6,7,8],[80,90,120,150,180],'Parallel transistors per switch, n','Peak drain–source voltage (V)');txt(c,271,214,'(b)',11)
seg(c,[t(1.6,90),t(8.4,90)],grey,[2,3],.8)
for key,col,dash in [('0.5nH',teal,None),('1nH',wine,[5,3])]:
 rr=[r for r in d['npar'][key] if r['n']>=2];pts=[t(r['n'],r['vpk']) for r in rr];seg(c,pts,col,dash);points(c,pts,col)
for x,label,col,dash in [(303,'0.5 nH',teal,None),(375,'1 nH',wine,[5,3])]:
 seg(c,[(x,183),(x+15,183)],col,dash);txt(c,x+19,180,label,9)
seg(c,[t(4,70),t(4,105)],grey,[2,3],.7);txt(c,*t(4.2,106),'n = 4',9,col=teal)
finish(c,name)
with (out/'parallel_count_selection_data.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['n','Ipeak_per_device_A','Pleg_W','Tjunction_C','Vpeak_0.5nH_V','Vpeak_1nH_V'])
 other={r['n']:r for r in d['npar']['1nH']}
 for r in nr:w.writerow([r['n'],322/r['n'],r['tot'],r['tj'],r['vpk'],other[r['n']]['vpk']])

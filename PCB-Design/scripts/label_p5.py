"""Reflow silkscreen only on a specified P3 board; preserve all electrical geometry."""
from p5_data import *
import sys,re
import pcbnew as p
import wx
app=wx.App(False)
path=Path(sys.argv[1]) if len(sys.argv)>1 else OUT/(NAME+'.kicad_pcb')
content=path.read_text();out=[];skip=False;depth=0
for line in content.splitlines(True):
    if line.lstrip().startswith('(gr_text '):skip=True;depth=0
    if skip:
        stripped=re.sub(r'"(?:\\.|[^"\\])*"','""',line);depth+=stripped.count('(')-stripped.count(')')
        if depth==0:skip=False
    else:out.append(line)
path.write_text(''.join(out));b=p.LoadBoard(str(path));fps={f.GetReference():f for f in b.GetFootprints()}
def vec(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def box(o,margin=.18):
    q=o.GetBoundingBox();return(p.ToMM(q.GetX())-margin,p.ToMM(q.GetY())-margin,p.ToMM(q.GetRight())+margin,p.ToMM(q.GetBottom())+margin)
occupied=[]
for f in fps.values():
    occupied.extend(box(q,.3) for q in f.Pads())
    occupied.extend(box(g,.18) for g in f.GraphicalItems() if g.GetLayer()==p.F_SilkS)
for q in b.GetTracks():
    if isinstance(q,p.PCB_VIA):occupied.append(box(q,.2))
def label(s,x,y,angle=0,size=.8,fixed=False):
    t=p.PCB_TEXT(b);t.SetText(s);t.SetLayer(p.F_SilkS);t.SetTextSize(vec(size,size));t.SetTextThickness(p.FromMM(.12));t.SetTextAngle(p.EDA_ANGLE(angle,p.DEGREES_T))
    candidates=[(0,0)] if fixed else sorted([(a,c) for a in range(-24,25) for c in range(-24,25)],key=lambda q:q[0]*q[0]+q[1]*q[1])
    for a,c in candidates:
        t.SetPosition(vec(x+a*.5,y+c*.5));bb=box(t,.15)
        if bb[0]<5.6 or bb[2]>82.9 or bb[1]<5.6 or bb[3]>55.4:continue
        if any(bb[0]<q[2] and bb[2]>q[0] and bb[1]<q[3] and bb[3]>q[1] for q in occupied):continue
        b.Add(t);occupied.append(bb);return
    raise RuntimeError('No position '+s)
label('EPC2361 / TWO PER SWITCH / P5',59,8,size=1,fixed=True)
label('24 x 1uF 100V / ALL CAPS TOP',59,11,size=.9,fixed=True)
label('REVIEW PROTOTYPE',47,54,size=.9,fixed=True)
label('DC+',39,9,size=.9)
label('DC-',39,16,size=.9)
label('JDC1 DC+ ALL 24',22,12,size=.8);label('JDC2 DC- ALL 24',22,18,size=.8);label('JAC1 AC ALL 24',81.8,36,90,size=.8)
# Vertical capacitor references remain directly aligned with each component.
for r in bus_caps:
    c=parts[r];label(r,c['x'],20.8 if c['y']<35 else 49.5,90)
for r in ['JGH1','JGL1','JGH2','JGL2']:
    c=parts[r];label(r,c['x']-1.8,c['y']+.65,90)
    for pin,txt in [('1','G'),('2','S')]:
        q=next(q for q in fps[r].Pads() if q.GetNumber()==pin);a=q.GetPosition();label(txt,p.ToMM(a.x)+1.65,p.ToMM(a.y),size=.8)
for i,txt in enumerate(['12V','GND','HI','GND','LI','GND']):label(txt,15.3,30+i*2.54)
for r,c in parts.items():
    if r in bus_caps or r in ['JGH1','JGL1','JGH2','JGL2','JDC1','JDC2','JAC1']:continue
    x,y=c['x'],c['y'];label(r,x,y+(7 if r in ['JDC1','JDC2','JAC1'] else 1.8))
    if r.startswith('TP') and int(r[2:])<=5:label(c['value'],x,y-1.5)
p.SaveBoard(str(path),b)
p.WriteDRCReport(b,str(OUT/'silkscreen-drc.rpt'),p.EDA_UNITS_MILLIMETRES,True)
print('Silkscreen reflowed:',path)

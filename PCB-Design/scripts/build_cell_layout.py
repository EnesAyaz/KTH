"""EPC2361 single-cell PCB placement study; not a manufacturing release."""
from pathlib import Path
import math
import pcbnew as p
import wx
app = wx.App(False)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/epc2361-cell'
LIB = OUT / 'epc2361-cell.pretty'
OUT.mkdir(parents=True, exist_ok=True)
LIB.mkdir(exist_ok=True)

def rr_poly(x,y,w,h,r,layer):
    pts=[]
    for cx,cy,start in [(x+w/2-r,y+h/2-r,0),(x-w/2+r,y+h/2-r,90),(x-w/2+r,y-h/2+r,180),(x+w/2-r,y-h/2+r,270)]:
        for i in range(9):
            a=math.radians(start+i*90/8)
            pts.append(f'(xy {cx+r*math.cos(a):.6f} {cy+r*math.sin(a):.6f})')
    return f'(fp_poly (pts {" ".join(pts)}) (stroke (width 0) (type solid)) (fill solid) (layer "{layer}"))'

def pad(num,x,y,w,h,layers='"F.Cu" "F.Paste" "F.Mask"',r=.05):
    return f'(pad "{num}" smd roundrect (at {x} {y}) (size {w} {h}) (layers {layers}) (roundrect_rratio {r/min(w,h):.6f}))'

def footprint(name,body,desc=''):
    text=f'''(footprint "{name}" (version 20221018) (generator pcbnew)
    (layer "F.Cu") (descr "{desc}") (attr smd)
    (fp_text reference "REF**" (at 0 -3) (layer "F.SilkS") (effects (font (size .7 .7) (thickness .12))))
    (fp_text value "{name}" (at 0 3) (layer "F.Fab") (effects (font (size .7 .7) (thickness .1))))
    {body})'''
    (LIB/f'{name}.kicad_mod').write_text(text,encoding='utf-8')

# Datasheet rev2.4 p12 copper, p11 separate solder-mask and stencil drawings.
body=[]
for n,x,y,w,h,r in [(1,-2.352,-1.23,1.102,1.14,.11),(2,-2.352,.67,1.102,2.26,.11),(3,-1.275,0,.65,3.6,.065),(4,-.425,0,.65,3.6,.065),(5,.425,0,.65,3.6,.065),(6,1.275,0,.65,3.6,.065),(7,2.352,0,1.102,3.6,.11)]:
    body.append(pad(n,x,y,w,h,'"F.Cu"',r))
# Union of radiused mask rectangles. Separate mask graphics preserve SMD copper.
for x,y,w,h in [(-2.175,-1.2075,.4,.985),(-2.175,.65,.4,2.1),(2.175,0,.4,3.4)]+[(x,0,.3,3.4) for x in [-1.275,-.425,.425,1.275]]:
    body.append(rr_poly(x,y,w,h,.05,'F.Mask'))
for x,ys in [(-2.3375,[-.975,-.225,.325,.975]),(2.3375,[-.975,-.325,.325,.975])]:
    for y in ys: body.append(rr_poly(x,y,.725,.37,.05,'F.Mask'))
# Stencil opening centres are from p11; stencil specified100um, SAC305Type4.
for x,y,w,h,r in [(-2.09,-1.1825,.54,1.035,.10),(-2.09,.04,.535,.973,.06),(-2.09,1.2135,.535,.973,.06)]+[(x,y,.4,1.6,.1) for x in [-1.275,-.425,.425,1.275] for y in [-.9,.9]]+[(2.143,y,.435,1.6,.109) for y in [-.9,.9]]:
    body.append(rr_poly(x,y,w,h,r,'F.Paste'))
for x,ys in [(-2.665,[-1.182,-.265,.365,1.0]),(2.665,[-.975,-.325,.325,.975])]:
    for y in ys: body.append(rr_poly(x,y,.25,.45,.06,'F.Paste'))
body.append('(fp_rect (start -2.5 -1.5) (end 2.5 1.5) (stroke (width .1) (type solid)) (fill none) (layer "F.Fab"))')
body.append('(fp_rect (start -3.1 -2) (end 3.1 2) (stroke (width .05) (type solid)) (fill none) (layer "F.CrtYd"))')
body.append('(fp_circle (center -3.2 -1.2) (end -3.05 -1.2) (stroke (width .1) (type solid)) (fill none) (layer "F.SilkS"))')
footprint('EPC2361','\n'.join(body),'EPC2361 rev2.4 pp11-12; copper mask stencil transcribed; independent fabrication verification required')
footprint('Gate_Source_Pads',pad(1,0,-.95,1.4,1.0,'"F.Cu" "F.Mask"')+pad(2,0,.95,1.4,1.0,'"F.Cu" "F.Mask"'),'Unselected top contact interface; no connector current or insulation rating')
footprint('Power_Port_Pad',pad(1,0,0,3,3,'"F.Cu" "F.Mask"'),'Study power access pad; not a rated high-current terminal')
footprint('Probe_Pad',pad(1,0,0,.7,.7,'"F.Cu" "F.Mask"'),'Compact probe contact')

b=p.BOARD(); b.SetCopperLayerCount(4)
netnames=['DC+','DC-','AC','GH_DRV','GL_DRV','GH','GL']
nets={}
for name in netnames:
    n=p.NETINFO_ITEM(b,name);b.Add(n);nets[name]=n
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def add(lib,name,ref,value,x,y,mapping,angle=0):
    ref={'TP_GH':'TP1','TP_SH':'TP2','TP_GL':'TP3','TP_SL':'TP4','TP_DC+':'TP5','TP_DC-':'TP6','TP_AC':'TP7'}.get(ref,ref)
    f=p.FootprintLoad(str(LIB if lib=='epc2361-cell' else Path('C:/Program Files/KiCad/7.0/share/kicad/footprints')/(lib+'.pretty')),name)
    if not f:raise RuntimeError(name)
    f.SetReference(ref); f.SetValue(value);f.SetFPID(p.LIB_ID(lib,name));f.SetPosition(v(x,y));f.SetOrientationDegrees(angle)
    f.Reference().SetVisible(False);f.Value().SetVisible(False)
    for q in f.Pads():
        if q.GetNumber() in mapping:q.SetNet(nets[mapping[q.GetNumber()]])
    b.Add(f);return f
parts={}
for ref,y,g,d,s in [('QH1',16,'GH','DC+','AC'),('QL1',24,'GL','AC','DC-')]:
    parts[ref]=add('epc2361-cell','EPC2361',ref,'EPC2361',15,y,{'1':g,'2':s,'3':d,'4':s,'5':d,'6':s,'7':d})
for i,y in enumerate([11.5,16,24,28.5],1):parts[f'C{i}']=add('Capacitor_SMD','C_1210_3225Metric',f'C{i}','2.2uF 100V candidate',21.7,y,{'1':'DC+','2':'DC-'})
for ref,y,gn,sn in [('JGH1',15.72,'GH_DRV','AC'),('JGL1',23.72,'GL_DRV','DC-')]:parts[ref]=add('epc2361-cell','Gate_Source_Pads',ref,'TOP G/K-S INTERFACE',7,y,{'1':gn,'2':sn})
for ref,y,a,c in [('RG1',14.77,'GH_DRV','GH'),('RG2',22.77,'GL_DRV','GL')]:parts[ref]=add('Resistor_SMD','R_0402_1005Metric',ref,'0R provisional',10,y,{'1':a,'2':c})
for ref,y,g,s in [('RGS1',18.2,'GH','AC'),('RGS2',26.2,'GL','DC-')]:parts[ref]=add('Resistor_SMD','R_0402_1005Metric',ref,'DNP',7,y,{'1':g,'2':s},90)
for ref,x,y,net in [('JDC1',15,5,'DC+'),('JDC2',24,34,'DC-'),('JAC1',15,34,'AC')]:parts[ref]=add('epc2361-cell','Power_Port_Pad',ref,net+' study port',x,y,{'1':net})
for ref,x,y,net in [('TP_GH',10.5,12.8,'GH'),('TP_SH',9.2,18.3,'AC'),('TP_GL',10.5,20.8,'GL'),('TP_SL',9.2,26.3,'DC-'),('TP_DC+',20.2,7.8,'DC+'),('TP_DC-',23.2,7.8,'DC-'),('TP_AC',18.7,20,'AC')]:parts[ref]=add('epc2361-cell','Probe_Pad',ref,net,x,y,{'1':net})
def track(net,x1,y1,x2,y2,w=.25,layer=p.F_Cu):
    t=p.PCB_TRACK(b);t.SetStart(v(x1,y1));t.SetEnd(v(x2,y2));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNet(nets[net]);b.Add(t)
def via(net,x,y):
    q=p.PCB_VIA(b);q.SetPosition(v(x,y));q.SetWidth(p.FromMM(.6));q.SetDrill(p.FromMM(.3));q.SetLayerPair(p.F_Cu,p.B_Cu);q.SetNet(nets[net]);b.Add(q)
def shape(x1,y1,x2,y2,layer=p.Dwgs_User,w=.15):
    z=p.PCB_SHAPE();z.SetShape(p.SHAPE_T_SEGMENT);z.SetStart(v(x1,y1));z.SetEnd(v(x2,y2));z.SetLayer(layer);z.SetWidth(p.FromMM(w));b.Add(z)
def label(text,x,y,layer=p.F_SilkS,size=.7):
    if layer==p.F_SilkS: size=max(size,.8)
    t=p.PCB_TEXT(b);t.SetText(text);t.SetPosition(v(x,y));t.SetTextSize(v(size,size));t.SetTextThickness(p.FromMM(.12));t.SetLayer(layer);b.Add(t)
for a,c in [((0,0),(30,0)),((30,0),(30,40)),((30,40),(0,40)),((0,40),(0,0))]:shape(*a,*c,p.Edge_Cuts,.05)
# Top-side drain and source combs. No open via-in-pad in solder lands.
for y,d,s,dy,sy in [(16,'DC+','AC',13.2,20),(24,'AC','DC-',20,27)]:
    for x in [13.725,15.425,17.352]:track(d,x,y-1.5,x,dy,.5)
    track(d,13.725,dy,17.352,dy,1)
    for x,py in [(12.648,y+.67),(14.575,y),(16.275,y)]:track(s,x,py,x,sy,.5)
    track(s,12.648,sy,17.352 if s=='AC' else 16.275,sy,1)
track('DC+',17.352,13.2,20.2,13.2,.8)
track('DC+',20.2,7.8,20.2,28.5,.7)
for i in range(1,5):
    f=parts[f'C{i}'];pd={q.GetNumber():q for q in f.Pads()};a=pd['1'].GetPosition();c=pd['2'].GetPosition();ax,ay=p.ToMM(a.x),p.ToMM(a.y);cx,cy=p.ToMM(c.x),p.ToMM(c.y)
    track('DC+',ax,ay,20.2,ay,.7)
    track('DC-',cx,cy,24.4,cy,.8)
    for yy in [cy-.6,cy,cy+.6]:via('DC-',24.4,yy);track('DC-',24.4,cy,24.4,yy,.7)
for x in [12.648,14.575,16.275]:
    for dx in [-.3,.3]:via('DC-',x+dx,27.7);track('DC-',x,27,x+dx,27.7,.5)
# Short top gate and Kelvin traces; interfaces are study contact pads.
for y,g,gd,s,rg in [(16,'GH','GH_DRV','AC','RG1'),(24,'GL','GL_DRV','DC-','RG2')]:
    pp={q.GetNumber():q for q in parts[rg].Pads()};a=pp['1'].GetPosition();c=pp['2'].GetPosition()
    track(gd,7,y-1.23,p.ToMM(a.x),p.ToMM(a.y),.2)
    track(g,p.ToMM(c.x),p.ToMM(c.y),12.648,y-1.23,.2)
    track(s,7,y+.67,12.648,y+.67,.2)
# Proposed first-inner commutation return only. Distribution and mechanical stackup remain open.
z=p.ZONE(b);z.SetLayer(p.In1_Cu);z.SetNet(nets['DC-']);z.SetLocalClearance(p.FromMM(.3));z.SetPadConnection(p.ZONE_CONNECTION_FULL)
z.SetMinThickness(p.FromMM(.2));poly=z.Outline();poly.NewOutline()
for x,y in [(11,9),(25.5,9),(25.5,29.5),(11,29.5)]:poly.Append(p.FromMM(x),p.FromMM(y))
b.Add(z)
for a,c in [((11.4,13.8),(18.4,13.8)),((18.4,13.8),(18.4,26.2)),((18.4,26.2),(11.4,26.2)),((11.4,26.2),(11.4,13.8))]:shape(*a,*c)
label('COLD PLATE CONTACT CORRIDOR',15,31,p.Dwgs_User,.55)
label('EPC2361  ONE PAIR',15,1.8,size=.8)
label('PLACEMENT ONLY / NO FAB',15,38,size=.8)
for text,x,y in [('DC+',15,7.3),('AC',15,36.3),('DC-',24,36.3),('QH1',15,11.5),('QL1',15,29.5),('G / K-S',5.8,12),('G / K-S',5.8,20),('C1-C4',25.5,20)]:label(text,x,y,size=.65)
b.BuildListOfNets();b.BuildConnectivity()
p.SaveBoard(str(OUT/'epc2361-cell.kicad_pcb'),b)
print('Saved PCB:',OUT/'epc2361-cell.kicad_pcb')
print('Footprints:',len(list(b.GetFootprints())),'Tracks/vias:',len(list(b.GetTracks())))

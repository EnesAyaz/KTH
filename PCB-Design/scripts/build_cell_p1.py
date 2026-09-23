"""EPC optimal-loop study derived from P0; preserves the original open project."""
from pathlib import Path
import shutil
import json
import pcbnew as p
import wx
app=wx.App(False)
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'hardware/epc2361-cell'
OUT=ROOT/'hardware/epc2361-cell-p1'
OUT.mkdir(exist_ok=True)
for name in ['fp-lib-table','epc2361-cell.kicad_pro']:
    if not (OUT/name).exists(): shutil.copy2(SRC/name,OUT/name)
shutil.copytree(SRC/'epc2361-cell.pretty',OUT/'epc2361-cell.pretty',dirs_exist_ok=True)
b=p.BOARD();b.SetCopperLayerCount(4)
nets={}
for name in ['DC+','DC-','AC','GH_DRV','GL_DRV','GH','GL']:
    n=p.NETINFO_ITEM(b,name);b.Add(n);nets[name]=n
parts={}
manifest=json.loads((SRC/'schematic-manifest.json').read_text())['components']
for ref,c in manifest.items():
    if ref.startswith('C'):continue
    lib,name=c['footprint'].split(':')
    libpath=OUT/'epc2361-cell.pretty' if lib=='epc2361-cell' else Path('C:/Program Files/KiCad/7.0/share/kicad/footprints')/(lib+'.pretty')
    f=p.FootprintLoad(str(libpath),name);f.SetReference(ref);f.SetValue(c['value']);f.SetFPID(p.LIB_ID(lib,name))
    if ref.startswith('RGS'):f.SetOrientationDegrees(90)
    for q in f.Pads():q.SetNet(nets[c['pins'][q.GetNumber()]])
    f.Reference().SetVisible(False);f.Value().SetVisible(False)
    b.Add(f);parts[ref]=f
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def move(ref,x,y):parts[ref].SetPosition(v(x,y))
def padpos(ref,num):
    q=next(q for q in parts[ref].Pads() if q.GetNumber()==str(num));a=q.GetPosition()
    return p.ToMM(a.x),p.ToMM(a.y)
def track(net,x1,y1,x2,y2,w=.3,layer=p.F_Cu):
    if abs(x1-x2)+abs(y1-y2)<.00001:return
    t=p.PCB_TRACK(b);t.SetStart(v(x1,y1));t.SetEnd(v(x2,y2));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNet(nets[net]);b.Add(t)
def via(net,x,y):
    q=p.PCB_VIA(b);q.SetPosition(v(x,y));q.SetWidth(p.FromMM(.6));q.SetDrill(p.FromMM(.3));q.SetLayerPair(p.F_Cu,p.B_Cu);q.SetNet(nets[net]);b.Add(q)
def zone(net,layer,points):
    z=p.ZONE(b);z.SetLayer(layer);z.SetNet(nets[net]);z.SetLocalClearance(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(p.FromMM(.15))
    poly=z.Outline();poly.NewOutline()
    for x,y in points:poly.Append(p.FromMM(x),p.FromMM(y))
    b.Add(z)
def line(x1,y1,x2,y2,layer=p.Dwgs_User):
    z=p.PCB_SHAPE();z.SetShape(p.SHAPE_T_SEGMENT);z.SetStart(v(x1,y1));z.SetEnd(v(x2,y2));z.SetLayer(layer);z.SetWidth(p.FromMM(.05 if layer==p.Edge_Cuts else .12));b.Add(z)
def text(s,x,y,layer=p.F_SilkS,size=.8):
    t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(v(x,y));t.SetTextSize(v(size,size));t.SetTextThickness(p.FromMM(.12));t.SetLayer(layer);b.Add(t)
move('QH1',15,16);move('QL1',15,22)
for ref,x,y in [('JGH1',6.5,15.72),('JGL1',6.5,21.72),('RG1',10,14.77),('RG2',10,20.77),('RGS1',4,17.5),('RGS2',4,23.5),('JDC1',23,12),('JDC2',23,7),('JAC1',23,19),('TP1',10.6,13),('TP2',9,17.8),('TP3',10.6,19),('TP4',9,23.8),('TP5',22,14.5),('TP6',22,4.5),('TP7',20,19)]:move(ref,x,y)
xs=[9.75,11.85,13.95,16.05,18.15,20.25]
move('RG1',9.2,14.77);move('RG2',9.2,20.77)
for ref,y in [('RGS1',15.72),('RGS2',21.72)]:
    move(ref,11,y);parts[ref].SetOrientationDegrees(270)
for bank in range(2):
    for j,x in enumerate(xs):
        ref='C'+str(bank*6+j+1)
        f=p.FootprintLoad('C:/Program Files/KiCad/7.0/share/kicad/footprints/Capacitor_SMD.pretty','C_0805_2012Metric')
        f.SetReference(ref);f.SetValue('1u / 100V');f.SetFPID(p.LIB_ID('Capacitor_SMD','C_0805_2012Metric'));f.SetPosition(v(x,10));f.SetOrientationDegrees(90)
        b.Add(f)
        if bank:
            f.Flip(v(x,10),False)
            # Keep DC+ facing the FETs on both sides.
            if p.ToMM(next(q for q in f.Pads() if q.GetNumber()=='1').GetPosition().y)<10:f.SetOrientationDegrees(f.GetOrientationDegrees()+180)
        for q in f.Pads():q.SetNet(nets['DC+' if q.GetNumber()=='1' else 'DC-'])
        f.Reference().SetVisible(False);f.Value().SetVisible(False);parts[ref]=f
        layer=p.F_Cu if bank==0 else p.B_Cu
        for num,net,yy in [(1,'DC+',12.1),(2,'DC-',7.8)]:
            px,py=padpos(ref,num);track(net,px,py,px,yy,.85,layer)
            if bank==0:
                via(net,x,yy)
                if net=='DC-':via(net,x,yy-.7);track(net,x,yy,x,yy-.7,.6)
# Broad top DC+ feed and first-inner DC- return; capacitor vias stay above FET lands.
zone('DC+',p.F_Cu,[(9.1,11.7),(24,11.7),(24,13),(13.3,13),(13.3,13.6),(9.1,13.6)])
zone('DC-',p.In1_Cu,[(9,6.5),(24,6.5),(24,8.3),(21,8.3),(21,26.5),(11.7,26.5),(11.7,13.5),(9,13.5)])
for y,d,s,dy,sy in [(16,'DC+','AC',13.2,19),(22,'AC','DC-',19,25)]:
    for x in [13.725,15.425,17.352]:track(d,x,y-1.5,x,dy,.5)
    track(d,13.725,dy,17.352,dy,1)
    for x,py in [(12.648,y+.67),(14.575,y),(16.275,y)]:track(s,x,py,x,sy,.5)
    track(s,12.648,sy,17.352 if s=='AC' else 16.275,sy,1)
for x in [12.648,14.575,16.275]:
    for dx in [-.35,.35]:
        via('DC-',x+dx,25.8);track('DC-',x,25,x+dx,25.8,.55)
# AC leaves laterally; supply terminals are outside the local commutation loop.
track('AC',17.352,19,23,19,1.5)
track('DC-',23,7,21.8,7,1);via('DC-',21.8,7)
track('DC+',23,12,22,14.5,.6)
track('DC-',23,7,22,4.5,.6);via('DC-',22,4.5)
track('DC-',22,4.5,21.8,7,.6,p.In1_Cu)
for y,g,drv,s,rg,j,rs,tg,ts in [(16,'GH','GH_DRV','AC','RG1','JGH1','RGS1','TP1','TP2'),(22,'GL','GL_DRV','DC-','RG2','JGL1','RGS2','TP3','TP4')]:
    a=padpos(rg,1);c=padpos(rg,2)
    track(drv,*padpos(j,1),*a,.2)
    track(g,*c,12.648,y-1.23,.2)
    track(s,*padpos(j,2),12.648,y+.67,.2)
    track(g,*padpos(tg,1),*c,.2)
    track(s,*padpos(ts,1),9,y+.67,.2)
    # DNP resistor return connected locally, gate routed around the outside.
    r1=padpos(rs,1);r2=padpos(rs,2)
    track(s,*r2,11,y+.67,.2)
    track(g,*r1,11,y-1.23,.2)
for a,c in [((0,0),(27,0)),((27,0),(27,30)),((27,30),(0,30)),((0,30),(0,0))]:line(*a,*c,p.Edge_Cuts)
for a,c in [((11.4,14),(18.4,14)),((18.4,14),(18.4,24)),((18.4,24),(11.4,24)),((11.4,24),(11.4,14))]:line(*a,*c)
text('EPC2361 P1 / NO DRIVER IC',13.5,1.6)
text('C1-C6 TOP / C7-C12 BELOW',13.5,3)
text('STUDY - NOT FOR FAB',13.5,28.3)
text('DC-',24.3,5);text('DC+',24.3,14.8);text('AC',24.3,21.5)
text('G/KS',5.5,10.3);text('G/KS',5.5,19)
text('INSULATED COLD PLATE',15,27,p.Dwgs_User,.6)
text('OPTIONAL C7-C12 DNP',15,5,p.B_SilkS)
b.BuildConnectivity();p.SaveBoard(str(OUT/'epc2361-cell.kicad_pcb'),b)
boardpath=OUT/'epc2361-cell.kicad_pcb'
stack='''(stackup
 (layer "F.SilkS" (type "Top Silk Screen"))
 (layer "F.Paste" (type "Top Solder Paste"))
 (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
 (layer "F.Cu" (type "copper") (thickness 0.07))
 (layer "dielectric 1" (type "prepreg") (thickness 0.1) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In1.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 2" (type "core") (thickness 1.19) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In2.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 3" (type "prepreg") (thickness 0.1) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "B.Cu" (type "copper") (thickness 0.07))
 (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
 (layer "B.Paste" (type "Bottom Solder Paste"))
 (layer "B.SilkS" (type "Bottom Silk Screen"))
 (dielectric_constraints no))'''
boardpath.write_text(boardpath.read_text().replace('(setup','(setup\n'+stack,1))
print('P1 saved: 27 x 30 mm, 6 top + 6 optional bottom capacitors')

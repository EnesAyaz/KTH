from pathlib import Path
import os,json,xml.etree.ElementTree as ET
os.environ['KICAD7_FOOTPRINT_DIR']='C:/Program Files/KiCad/7.0/share/kicad/footprints'
import pcbnew as p
import wx
app=wx.App(False)
OUT=Path(__file__).resolve().parents[1]/'hardware/epc2361-sixparallel';NAME='epc2361-sixparallel'
b=p.LoadBoard(str(OUT/(NAME+'.kicad_pcb')))
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
nets={n.GetNetname():n for n in b.GetNetInfo().NetsByName().values()}
def tr(n,x1,y1,x2,y2,w,layer):
    t=p.PCB_TRACK(b);t.SetStart(v(x1,y1));t.SetEnd(v(x2,y2));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNet(nets[n]);b.Add(t)
def via(n,x,y):
    t=p.PCB_VIA(b);t.SetPosition(v(x,y));t.SetWidth(p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(nets[n]);b.Add(t)
for i in range(6):
    x=23+22*i
    # Distributed AC collector taps; this rail requires a bonded busbar for high current.
    tr('AC',x,19,x,32,2,p.B_Cu)
    for dx in [-.6,0,.6]:
        for dy in [-.6,0,.6]:via('AC',x+dx,19+dy);tr('AC',x,19,x+dx,19+dy,.6,p.F_Cu);tr('AC',x,19,x+dx,19+dy,.6,p.B_Cu)
    if i<5:
        tr('DC+',x,12,x+22,12,1.2,p.F_Cu)
        tr('DC-',x,7,x+22,7,2,p.In1_Cu)
tr('AC',23,32,133,32,4,p.B_Cu)
for a,c in [((0,0),(137,0)),((137,0),(137,36)),((137,36),(0,36)),((0,36),(0,0))]:
    z=p.PCB_SHAPE();z.SetShape(p.SHAPE_T_SEGMENT);z.SetStart(v(*a));z.SetEnd(v(*c));z.SetLayer(p.Edge_Cuts);z.SetWidth(p.FromMM(.05));b.Add(z)
for i in range(6):
    t=p.PCB_TEXT(b);t.SetText('CELL '+str(i+1));t.SetPosition(v(15+22*i,3));t.SetTextSize(v(1,1));t.SetTextThickness(p.FromMM(.15));t.SetLayer(p.F_SilkS);b.Add(t)
t=p.PCB_TEXT(b);t.SetText('SIX PARALLEL PAIRS - BUSBARS REQUIRED - ENGINEERING STUDY');t.SetPosition(v(68.5,34));t.SetTextSize(v(.9,.9));t.SetTextThickness(p.FromMM(.15));t.SetLayer(p.F_SilkS);b.Add(t)
m=json.loads((OUT/'schematic-manifest.json').read_text())['components']
expected={(r,pin):n for r,c in m.items() for pin,n in c['pins'].items()}
actual={}
for net in ET.parse(OUT/'netlist.xml').findall('./nets/net'):
    for node in net.findall('node'):actual[(node.attrib['ref'],node.attrib['pin'])]=net.attrib['name']
assert expected==actual,[(k,v,actual.get(k)) for k,v in expected.items() if actual.get(k)!=v]
assert set(m)=={f.GetReference() for f in b.GetFootprints()}
for f in b.GetFootprints():assert {q.GetNumber():q.GetNetname() for q in f.Pads()}==m[f.GetReference()]['pins'],f.GetReference()
b.BuildConnectivity();p.SaveBoard(str(OUT/(NAME+'.kicad_pcb')),b)
# Reload before zone filling to initialize native board state.
b=p.LoadBoard(str(OUT/(NAME+'.kicad_pcb')));fill=p.ZONE_FILLER(b);fill.Fill(b.Zones());p.SaveBoard(str(OUT/(NAME+'.kicad_pcb')),b)
p.WriteDRCReport(b,str(OUT/'drc.rpt'),p.EDA_UNITS_MILLIMETRES,True)
(OUT/'connectivity-check.txt').write_text(f'PASS: {len(m)} components, {len(expected)} pin assignments; schematic and PCB match.\nSee drc.rpt. Native schematic ERC not run.\n')
print('Connectivity audit passed:',len(m),'components,',len(expected),'pins')

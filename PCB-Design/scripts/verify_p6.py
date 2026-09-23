from p6_data import *
import pcbnew as p,wx,json,xml.etree.ElementTree as ET
app=wx.App(False)
b=p.LoadBoard(str(OUT/(NAME+'.kicad_pcb')))
fps={f.GetReference():f for f in b.GetFootprints()}
actual={}
for net in ET.parse(OUT/'netlist.xml').findall('./nets/net'):
    for node in net.findall('node'):actual[(node.attrib['ref'],node.attrib['pin'])]=net.attrib['name'].removeprefix('/')
expected={(r,k):n for r,c in parts.items() for k,n in c['pins'].items() if not n.startswith('NC')}
assert all(actual.get(k)==n for k,n in expected.items())
assert set(fps)==set(parts)|{'MH1','MH2','MH3','MH4','MECH1'}
for r,c in parts.items():assert {q.GetNumber():q.GetNetname() for q in fps[r].Pads() if q.GetNumber()}==c['pins'],r
for f in fps.values():
    for m in f.Models():assert Path(str(m.m_Filename).replace('${KIPRJMOD}',str(OUT))).exists()
p.WriteDRCReport(b,str(OUT/'final-drc.rpt'),p.EDA_UNITS_MILLIMETRES,True)
report={'connected_schematic_assignments':len(expected),'pcb_footprints':len(fps),'mechanical_only_footprints':5,'model_paths_exist':True,'native_erc':'not run; custom passive symbols limit its coverage','release':'HOLD: mechanical, sensor closure and supplier process confirmation pending'}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

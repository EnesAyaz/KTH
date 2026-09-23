"""Validate KiCad-exported connectivity and finalize the placement study."""
from pathlib import Path
import json
import os
os.environ['KICAD7_FOOTPRINT_DIR']='C:/Program Files/KiCad/7.0/share/kicad/footprints'
import xml.etree.ElementTree as ET
import pcbnew as p
import wx
app=wx.App(False)
root=Path(__file__).resolve().parents[1]/'hardware'/os.environ.get('CELL_REVISION','epc2361-cell')
m=json.loads((root/'schematic-manifest.json').read_text())['components']
xml=ET.parse(root/'cell-netlist.xml')
actual={}
for net in xml.findall('./nets/net'):
    for node in net.findall('node'):
        actual[(node.attrib['ref'],node.attrib['pin'])]=net.attrib['name'].removeprefix('/')
expected={(ref,pin):net for ref,c in m.items() for pin,net in c['pins'].items()}
assert actual==expected, {'missing_or_wrong':{str(k):(v,actual.get(k)) for k,v in expected.items() if actual.get(k)!=v},'extra':list(actual.keys()-expected.keys())}
b=p.LoadBoard(str(root/'epc2361-cell.kicad_pcb'))
assert {f.GetReference() for f in b.GetFootprints()}==set(m)
for f in b.GetFootprints():
    c=m[f.GetReference()]
    assert str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName())==c['footprint'], f.GetReference()
    assert {q.GetNumber():q.GetNetname().removeprefix('/') for q in f.Pads()}==c['pins'],f.GetReference()
    f.SetPath(p.KIID_PATH(c['path']))
    f.SetValue(c['value'])
filler=p.ZONE_FILLER(b)
filler.Fill(b.Zones())
p.SaveBoard(str(root/'epc2361-cell.kicad_pcb'),b)
p.WriteDRCReport(b,str(root/'cell-drc.rpt'),p.EDA_UNITS_MILLIMETRES,True)
report=f'PASS: {len(m)} components and {len(expected)} pin-to-net assignments agree between KiCad netlist, design manifest and PCB.\nZone fill completed. Schematic UUID paths attached to footprints.\nPlacement study: consult cell-drc.rpt for incomplete routing and warnings. Native schematic ERC has not been run.\n'
(root/'connectivity-check.txt').write_text(report)
print(report)

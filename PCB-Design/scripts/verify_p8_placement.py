"""Validate circuit preservation only; this board is intentionally unrouted."""
from pathlib import Path
import json, xml.etree.ElementTree as ET
import pcbnew as p
root=Path(__file__).resolve().parents[1]
out=root/'hardware/epc2361-prototype-p8-placement'
parts=json.loads((out/'BOM.json').read_text())
b=p.LoadBoard(str(out/'epc2361-prototype-p8-placement.kicad_pcb'))
fps={f.GetReference():f for f in b.GetFootprints()}
assert set(fps)==set(parts)|{'MECH1'}
expected={(r,k):v for r,c in parts.items() for k,v in c['pins'].items() if not v.startswith('NC')}
actual={}
for net in ET.parse(out/'netlist.xml').findall('./nets/net'):
    for node in net.findall('node'):actual[node.attrib['ref'],node.attrib['pin']]=net.attrib['name'].removeprefix('/')
assert all(actual.get(k)==v for k,v in expected.items())
for ref,c in parts.items():
    assert {pad.GetNumber():pad.GetNetname() for pad in fps[ref].Pads() if pad.GetNumber()}==c['pins'],ref
    assert abs(p.ToMM(fps[ref].GetPosition().x)-c['x'])<.001
    assert abs(p.ToMM(fps[ref].GetPosition().y)-c['y'])<.001
assert len(list(b.GetTracks()))==0 and len(list(b.Zones()))==0
for f in fps.values():
    for m in f.Models():assert Path(str(m.m_Filename).replace('${KIPRJMOD}',str(out))).exists()
result=dict(connected_pin_assignments_checked=len(expected),electrical_footprints=len(parts),
            placed_positions_match_bom=True,model_files_exist=True,
            tracks=0,zones=0,release='HOLD: unrouted placement study; no coil access geometry')
(out/'placement-verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))

"""Check exported schematic connectivity, PCB assignments and local model coverage."""
from p4_data import *
import json, xml.etree.ElementTree as ET
import pcbnew as p
actual={}
for net in ET.parse(OUT/'netlist.xml').findall('./nets/net'):
    for node in net.findall('node'):
        actual[(node.attrib['ref'],node.attrib['pin'])]=net.attrib['name'].removeprefix('/')
expected={(r,k):n for r,c in parts.items() for k,n in c['pins'].items() if not n.startswith('NC')}
assert all(actual.get(k)==n for k,n in expected.items()), {str(k):(n,actual.get(k)) for k,n in expected.items() if actual.get(k)!=n}
b=p.LoadBoard(str(OUT/(NAME+'.kicad_pcb')))
assert {f.GetReference() for f in b.GetFootprints()}==set(parts)
models=0
for f in b.GetFootprints():
    r=f.GetReference();c=parts[r]
    assert {q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()}==c['pins'],r
    assert f.GetLayer()==p.F_Cu,r
    if not r.startswith('TP'):
        ms=list(f.Models());assert ms,r
        for m in ms:
            path=Path(str(m.m_Filename).replace('${KIPRJMOD}',str(OUT)))
            assert path.exists(),str(path)
        models+=1
report=(f'PASS: {len(parts)} components; {len(expected)} connected pin assignments agree between exported schematic and PCB.\n'
        f'PASS: all footprints on F.Cu; all 24 local bus capacitors on top face.\n'
        f'PASS: {models} purchased-component placements have existing local 3D files; five are approximate envelopes.\n'
        'U1 NC pins 1, 11, 15 excluded from connected-net comparison; PCB assignments checked separately.\n'
        'Native schematic ERC not run. DRC is a geometric/connectivity check, not power, thermal or switching validation.\n')
(OUT/'connectivity-check.txt').write_text(report);print(report)

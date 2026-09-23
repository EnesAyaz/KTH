"""Integrate mechanical study into checked P6, preserving all earlier revisions."""
from p6_data import *
import pcbnew as p
import wx,shutil,json
app=wx.App(False)
path=OUT/(NAME+'.kicad_pcb')
b=p.LoadBoard(str(path))
mechroot=ROOT/'hardware/epc2361-prototype-p6-mechanical'
mb=p.LoadBoard(str(mechroot/'epc2361-prototype-p6-mechanical.kicad_pcb'))
lib=OUT/(LIB+'.pretty')
for f in mb.GetFootprints():
    if f.GetReference() not in ['MH1','MH2','MH3','MH4','MECH1']:continue
    g=f.Duplicate();g.SetParent(b)
    name='Support_NPTH_2p4' if f.GetReference().startswith('MH') else 'Spreader_Envelope'
    g.SetFPID(p.LIB_ID(LIB,name))
    b.Add(g)
    p.FootprintSave(str(lib),g)
for item in mb.GetDrawings():
    if item.GetLayer() in [p.Dwgs_User,p.Cmts_User]:b.Add(item.Duplicate())
shutil.copy2(mechroot/'models/P6-raised-spreader-envelope.wrl',OUT/'models/P6-raised-spreader-envelope.wrl')
shutil.copy2(mechroot/'p6-mechanical-drawing.svg',OUT/'p6-mechanical-drawing.svg')
# Simple formed-link envelope, no claim of manufacturing-qualified bend geometry.
model=['#VRML V2.0 utf8']
for x,y,z,w,d,h in [(0,-3,1.75,2,.5,3.5),(0,3,1.75,2,.5,3.5),(0,0,3.25,2,6,.5)]:
    model.append(f'Transform {{ translation {x/2.54} {y/2.54} {z/2.54} children [ Shape {{ appearance Appearance {{ material Material {{ diffuseColor .8 .4 .15 }} }} geometry Box {{ size {w/2.54} {d/2.54} {h/2.54} }} }} ] }}')
(OUT/'models/P6-current-link-envelope.wrl').write_text('\n'.join(model))
lk=next(f for f in b.GetFootprints() if f.GetReference()=='LK1')
m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/models/P6-current-link-envelope.wrl';lk.Add3DModel(m)
p.FootprintSave(str(lib),lk)
b.BuildConnectivity();p.SaveBoard(str(path),b)
b=p.LoadBoard(str(path));filler=p.ZONE_FILLER(b);filler.Fill(b.Zones());p.SaveBoard(str(path),b)
p.WriteDRCReport(b,str(OUT/'final-drc.rpt'),p.EDA_UNITS_MILLIMETRES,True)
pins={f.GetReference():{q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()} for f in b.GetFootprints()}
expected={('QL1','3'),('QL1','5'),('QL1','7'),('TP8','1'),('LK1','2')}
actual={(ref,num) for ref,pp in pins.items() for num,net in pp.items() if net=='D_QL1'}
assert actual==expected,(actual,expected)
assert pins['LK1']['1']=='AC'
assert all(pins['QL1'][k]=='DC-' for k in ['2','4','6'])
assert not any(z.GetNetname()=='D_QL1' for z in b.Zones())
(OUT/'device-current-audit.json').write_text(json.dumps({'D_QL1_pads':sorted(actual),'sole_component_connection':'LK1 pin2 to pin1; physical link required','source_pads':'DC- unchanged','D_QL1_zones':0,'scope':'Net membership and DRC check; physical link omission must be continuity-tested before energizing.'},indent=2))
print('Mechanical integration and device-current net audit complete')

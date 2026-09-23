"""Compact P8 placement study. Intentionally unrouted; never manufacture.
Preserve all historical boards. No invented coil drilling geometry.
"""
from p5_data import *
import pcbnew as p
import wx, shutil, json, re
app=wx.App(False)
src=OUT
out=ROOT/'hardware/epc2361-prototype-p8-placement'
name='epc2361-prototype-p8-placement'
out.mkdir(exist_ok=True)
for path in src.iterdir():
    if path.is_dir() and (path.name.endswith('.pretty') or path.name=='models'):
        shutil.copytree(path,out/path.name,dirs_exist_ok=True)
for fn in ['fp-lib-table']:
    shutil.copy2(src/fn,out/fn)
shutil.copy2(src/(NAME+'.kicad_pro'),out/(name+'.kicad_pro'))
lines=[];skip=False;depth=0
for line in (src/(NAME+'.kicad_pcb')).read_text().splitlines(True):
    if re.match(r'^(?:  |\t)\((segment|via|zone|gr_text|gr_line|gr_arc|gr_rect)\b',line):skip=True;depth=0
    if skip:
        s=re.sub(r'"(?:\\.|[^"\\])*"','""',line);depth+=s.count('(')-s.count(')')
        if depth==0:skip=False
    else:lines.append(line)
content=''.join(lines)
blocks=[];capturing=False;depth=0;block=[]
for line in content.splitlines(True):
    if re.match(r'^(?:  |\t)\(footprint ',line):capturing=True;depth=0;block=[]
    if capturing:
        block.append(line);s=re.sub(r'"(?:\\.|[^"\\])*"','""',line);depth+=s.count('(')-s.count(')')
        if depth==0:
            joined=''.join(block)
            if not re.search(r'\(fp_text reference "H[12]"',joined):blocks.append(joined)
            capturing=False
    else:blocks.append(line)
seed=out/'placement-seed.kicad_pcb';seed.write_text(''.join(blocks))
b=p.LoadBoard(str(seed))
assert len(list(b.GetTracks()))==0 and len(list(b.Zones()))==0
fps={f.GetReference():f for f in b.GetFootprints()}
assert 'H1' not in fps and 'H2' not in fps
for ref in ['H1','H2']:parts.pop(ref)
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def place(ref,x,y,angle=None):
    f=fps[ref];f.SetPosition(v(x,y));parts[ref].update(x=x,y=y)
    if angle is not None:f.SetOrientationDegrees(angle);parts[ref]['angle']=angle
    f.Reference().SetVisible(False);f.Value().SetVisible(False)
for i,x in [(1,36),(2,48)]:
    for kind,y in [('H',20),('L',26)]:
        place('Q'+kind+str(i),x,y,0)
        place('RG'+kind+str(i),x-4.3,y-1.23,0)
        # Pins outside the spreader, at the power-stage perimeter.
        place('JG'+kind+str(i),x-3,y-9 if kind=='H' else y+10,90)
for ref in bus_caps:
    c=parts[ref];place(ref,c['x']-(12 if c['x']<57 else 18),14 if c['y']<35 else 33,90)
for ref,x,y in [('U1',24,23),('C13',20,19),('C14',22,29),('C15',25,29),
                ('C16',24,26.5),('C17',26,18),('C18',24,19.3),('RB1',23,16),
                ('D1',26,14),('RH1',20,13),('RL1',23,13),('JCTRL1',20,5),
                ('TP1',54,11),('TP2',28,36),('TP3',56,35),('TP4',27,11),('TP5',24,33)]:
    place(ref,x,y)
place('JCTRL1',20,5,90)
for ref,x in [('JDC1',5),('JDC2',12),('JAC1',60)]:place(ref,x,7,0)
for q,dr,sr in vds_pairs:
    i=int(q[-1]);x=36 if i==1 else 48
    y=17 if q[1]=='H' else 30
    place(dr,x+1,y);place(sr,x+2.5,y)
def rect(x0,y0,x1,y1,layer):
    for a,c in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:
        s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(v(*a));s.SetEnd(v(*c));s.SetWidth(p.FromMM(.1));s.SetLayer(layer);b.Add(s)
def text(s,x,y,layer=p.F_SilkS,size=.8):
    t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(v(x,y));t.SetTextSize(v(size,size));t.SetTextThickness(p.FromMM(.12));t.SetLayer(layer);b.Add(t)
rect(1,1,65,43,p.Edge_Cuts)
# Narrow central plate leaves capacitor banks and measurement pads accessible.
rect(32.8,18,51.2,28.2,p.Dwgs_User)
text('CONTINUOUS SPREADER / POSITION STUDY',42,23,p.Dwgs_User,.65)
text('P8 PLACEMENT ONLY - DO NOT FABRICATE',33,41,size=.8)
for s,x,y in [('DC+',6,4),('DC-',13,4),('AC',61,4),('75V MAX',54,40),
              ('12V G HI G LI G',26,3),('QL1',36,28.8),('QL2',48,28.8),
              ('QH1',36,18.7),('QH2',48,18.7),('DRIVER',23,35)]:text(s,x,y)
for r,c in parts.items():
    if r.startswith('JG'):
        text(r+' G S',c['x']+1,c['y']+2)
    elif r.startswith('TP'):
        text(r,c['x'],c['y']+.9,size=.65)
    elif r.startswith(('C','R','D')) and not r.startswith('J'):
        text(r,c['x'],c['y']-1.8,size=.6)
# Low continuous plate envelope. No mounting/thermal qualification implied.
boxes=[(42,23.1,2.5,18.4,10.2,3,.65,.67,.7)]
for x in [36,48]:
    for y in [20,26]:boxes.append((x,y,.825,5,3,.35,.2,.7,.7))
vrml=['#VRML V2.0 utf8','# Review envelope; underside z=1mm; no tolerances or supports qualified']
for x,y,z,w,d,h,r,g,bl in boxes:
    vrml.append(f'Transform {{ translation {x/2.54} {-y/2.54} {z/2.54} children [ Shape {{ appearance Appearance {{ material Material {{ diffuseColor {r} {g} {bl} transparency .35 }} }} geometry Box {{ size {w/2.54} {d/2.54} {h/2.54} }} }} ] }}')
(out/'models/P8-continuous-spreader-study.wrl').write_text('\n'.join(vrml))
f=p.FOOTPRINT(b);f.SetReference('MECH1');f.SetValue('UNQUALIFIED spreader envelope');f.SetPosition(v(0,0));f.Reference().SetVisible(False);f.Value().SetVisible(False)
m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/models/P8-continuous-spreader-study.wrl';f.Add3DModel(m);b.Add(f)
b.BuildConnectivity();p.SaveBoard(str(out/(name+'.kicad_pcb')),b)
# Generate a matching schematic/BOM, with original circuit connectivity.
code=(ROOT/'scripts/build_p5_schematic.py').read_text().replace('from p5_data import *','')
code=code.replace("+['H1','H2']",'').replace('(rev "P5")','(rev "P8 placement")')
scope=dict(globals());scope.update(OUT=out,NAME=name)
exec(compile(code,'build_p8_schematic','exec'),scope)
audit={'status':'UNROUTED PLACEMENT STUDY - DO NOT FABRICATE',
       'outline_mm':[64,42], 'previous_outline_mm':[78.5,51],
       'area_reduction_percent':100*(1-64*42/(78.5*51)),
       'fet_pitch_mm':12,'spreader_envelope_mm':[18.4,10.2,3],
       'spreader_underside_above_pcb_mm':1.0,
       'tracks':len(list(b.GetTracks())), 'zones':len(list(b.Zones())),
       'coil_access':'not implemented; all-layer sensing topology unresolved',
       'holds':['Routing and electrical validation','Coil sensing topology and fit',
                'Spreader mounting and tolerance stack','Silkscreen cleanup','Thermal/current qualification']}
(out/'placement-status.json').write_text(json.dumps(audit,indent=2))
(out/'README.md').write_text('# P8 compact placement study\n\n**UNROUTED. DO NOT FABRICATE.**\n\n64 x 42 mm placement target; this is not a finished PCB. Original boards are preserved. Four EPC2361s, 12 mm branch pitch, driver left, DC inputs left, AC right. Continuous central spreader envelope leaves the tall capacitor banks outside its footprint. Gate headers and VDS pads are moved outside that footprint. No coil holes have been invented. Individual device sensing, mounting hardware, all routing and silkscreen verification remain unfinished. The schematic preserves P5 circuit connectivity and does not claim independent current-sensing branches.\n')
print(json.dumps(audit,indent=2))

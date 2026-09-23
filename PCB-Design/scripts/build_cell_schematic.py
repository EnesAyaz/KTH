"""Build the reviewable KiCad 7 single-pair schematic and project metadata.

This is a generator for a placement prototype, not a manufacturing release.
Connectivity is subsequently checked from KiCad's own exported XML netlist.
"""
from pathlib import Path
import json
import uuid
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware' / os.environ.get('CELL_REVISION','epc2361-cell')
NAME = 'epc2361-cell'
LIB = 'epc2361-cell'
NS = uuid.UUID('c07c3dab-55b6-4f34-85ec-8c019371fa50')

def uid(name):
    return str(uuid.uuid5(NS, name))

def q(text):
    return json.dumps(str(text))

def num(value):
    return f'{value:.4f}'.rstrip('0').rstrip('.')

def font(size=1.27, hidden=False):
    return f'(effects (font (size {size} {size}))' + (' hide' if hidden else '') + ')'

def prop(key, value, x=0, y=0, hidden=False, left=False):
    effects = f'(effects (font (size 1.27 1.27))' + (' (justify left)' if left else '') + (' hide' if hidden else '') + ')'
    return f'(property {q(key)} {q(value)} (at {num(x)} {num(y)} 0) {effects})'

def pin(number, name, x, y, angle, length=2.54, kind='passive'):
    return f'(pin {kind} line (at {x} {y} {angle}) (length {length}) (name {q(name)} {font(1.0)}) (number {q(number)} {font(1.0)}))'

def poly(points, width=0.254):
    coords = ' '.join(f'(xy {x} {y})' for x, y in points)
    return f'(polyline (pts {coords}) (stroke (width {width}) (type default)) (fill (type none)))'

def rect(x1,y1,x2,y2):
    return f'(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.254) (type default)) (fill (type background)))'

def definition(name, reference, graphics, pins, value=None, footprint=''):
    return '\n'.join([
        f'(symbol {q(name)} (pin_names (offset 0.635)) (in_bom yes) (on_board yes)',
        prop('Reference', reference, 0, 8.89), prop('Value', value or name, 0, -8.89),
        prop('Footprint', footprint, hidden=True), prop('Datasheet','',hidden=True),
        f'(symbol {q(name + "_0_1")} {graphics})',
        f'(symbol {q(name + "_1_1")} {pins})', ')'])

defs = {}
defs['EPC2361'] = definition('EPC2361','Q',rect(-5.08,5.08,5.08,-5.08),
    ' '.join([pin(1,'G',-7.62,0,0)] +
             [pin(n,'D',x,7.62,270) for n,x in [(3,-2.54),(5,0),(7,2.54)]] +
             [pin(n,'S',x,-7.62,90) for n,x in [(2,-2.54),(4,0),(6,2.54)]]),
    footprint=LIB+':EPC2361')
defs['R_H'] = definition('R_H','R',rect(-2.54,1.016,2.54,-1.016),
    pin(1,'~',-3.81,0,0,1.27)+pin(2,'~',3.81,0,180,1.27))
defs['R_V'] = definition('R_V','R',rect(-1.016,2.54,1.016,-2.54),
    pin(1,'~',0,3.81,270,1.27)+pin(2,'~',0,-3.81,90,1.27))
defs['C'] = definition('C','C',poly([(-2.032,0.762),(2.032,0.762)])+poly([(-2.032,-0.762),(2.032,-0.762)]),
    pin(1,'~',0,3.81,270,3.048)+pin(2,'~',0,-3.81,90,3.048))
defs['Gate_Source'] = definition('Gate_Source','J',rect(-2.54,1.27,2.54,-3.81),
    pin(1,'G',5.08,0,180)+pin(2,'KS',5.08,-2.54,180))
defs['Pad'] = definition('Pad','TP',
    '(circle (center 0 3.175) (radius 0.635) (stroke (width 0.254) (type default)) (fill (type none)))',
    pin(1,'~',0,0,90))

sheet_id=uid('sheet')
parts=[]
manifest={}
serial=0
def wire(x1,y1,x2,y2):
    global serial
    serial+=1
    parts.append(f'(wire (pts (xy {num(x1)} {num(y1)}) (xy {num(x2)} {num(y2)})) (stroke (width 0) (type default)) (uuid {uid("wire"+str(serial))}))')

def junction(x,y):
    global serial
    serial+=1
    parts.append(f'(junction (at {num(x)} {num(y)}) (diameter 0) (color 0 0 0 0) (uuid {uid("junction"+str(serial))}))')

def label(net,x,y):
    global serial
    serial+=1
    parts.append(f'(label {q(net)} (at {num(x)} {num(y)} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {uid("label"+str(serial))}))')

def text(value,x,y,size=1.27):
    global serial
    serial+=1
    parts.append(f'(text {q(value)} (at {num(x)} {num(y)} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {uid("text"+str(serial))}))')

def symbol(kind,ref,value,x,y,footprint,nets,dnp=False,show_value=True):
    ref={'TP_GH':'TP1','TP_SH':'TP2','TP_GL':'TP3','TP_SL':'TP4','TP_DC+':'TP5','TP_DC-':'TP6','TP_AC':'TP7'}.get(ref,ref)
    instance_id=uid(ref)
    if kind=='EPC2361':
        px,py=x+8.89,y-1.27
    elif kind=='C':
        px,py=x+3.81,y-1.27
    elif kind=='R_V':
        px,py=x+3.81,y-1.27
    elif kind=='Pad':
        px,py=x+2.54,y-5.08
    else:
        px,py=x-2.54,y-7.62
    item=[f'(symbol (lib_id {q(LIB+":"+kind)}) (at {num(x)} {num(y)} 0) (unit 1)',
        f'(in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid {instance_id})',
        prop('Reference',ref,px,py,left=True),prop('Value',value,px,py+2.54,not show_value,left=True),
        prop('Footprint',footprint,x,y,True),prop('Datasheet','',x,y,True)]
    for number in nets:
        item.append(f'(pin {q(number)} (uuid {uid(ref+"-pin-"+str(number))}))')
    item.append(f'(instances (project {q(NAME)} (path {q("/"+sheet_id)} (reference {q(ref)}) (unit 1))))')
    rendered='\n'.join(item)+')'
    if kind=='C' and os.environ.get('CELL_REVISION')=='epc2361-cell-p1':rendered=rendered.replace('(size 1.27 1.27)','(size 0.95 0.95)')
    parts.append(rendered)
    manifest[ref]={'uuid':instance_id,'path':'/'+sheet_id+'/'+instance_id,'footprint':footprint,'value':value,'dnp':dnp,'pins':{str(k):v for k,v in nets.items()}}

text('EPC2361 / ONE HALF-BRIDGE CELL',20,14,2.54)
text('75 V max bus | 50 kHz nominal, 100 kHz max | One of six eventual parallel cells',20,21,1.52)
text('TOP-SIDE DRIVER CONTACTS',20,33,1.52)
text('POWER PAIR',140,33,1.52)
text('LOCAL DC-LINK CERAMICS',193,33,1.52)

for index,(ref,y,gate,drv,source,drain) in enumerate([
    ('QH1',65,'GH','GH_DRV','AC','DC+'),('QL1',110,'GL','GL_DRV','DC-','AC')],1):
    symbol('EPC2361',ref,'EPC2361',150,y,LIB+':EPC2361',
           {1:gate,2:source,3:drain,4:source,5:drain,6:source,7:drain})
    upper=y-15
    lower=y+20
    for x in [147.46,150,152.54]:
        wire(x,y-7.62,x,upper)
        wire(x,y+7.62,x,lower)
    wire(147.46,upper,150,upper);wire(150,upper,152.54,upper)
    wire(147.46,lower,150,lower);wire(150,lower,152.54,lower)
    junction(150,upper);junction(150,lower)
    label(drain,152.54,upper);label(source,152.54,lower)
    jref='JGH1' if index==1 else 'JGL1'
    symbol('Gate_Source',jref,'G / KELVIN S',50,y,LIB+':Gate_Source_Pads',{1:drv,2:source})
    wire(55.08,y,91.19,y)
    label(drv,67,y)
    wire(55.08,y+2.54,67,y+2.54);label(source,67,y+2.54)
    symbol('R_H','RG'+str(index),'0R / TUNE',95,y,'Resistor_SMD:R_0402_1005Metric',{1:drv,2:gate})
    wire(98.81,y,120,y);wire(120,y,142.38,y);junction(120,y);label(gate,132,y)
    symbol('R_V','RGS'+str(index),'10k / DNP',120,y+11.43,'Resistor_SMD:R_0402_1005Metric',{1:gate,2:source},True)
    wire(120,y,120,y+7.62);wire(120,y+15.24,120,lower);label(source,120,lower)

# Main power continuity and three logical supply/load ports.
wire(150,85,150,90);wire(150,90,150,95);junction(150,90)
wire(150,90,175,90)
symbol('Pad','JAC1','AC PORT PAD',175,90,LIB+':Power_Port_Pad',{1:'AC'},show_value=False)
symbol('Pad','JDC1','DC+ PORT PAD',150,42,LIB+':Power_Port_Pad',{1:'DC+'},show_value=False)
wire(150,42,150,50)
symbol('Pad','JDC2','DC- PORT PAD',150,140,LIB+':Power_Port_Pad',{1:'DC-'},show_value=False)
wire(150,130,150,140)

# Capacitor banks; P1 has six top parts and six optional bottom parts.
if os.environ.get('CELL_REVISION')=='epc2361-cell-p1':
    for bank,cy in enumerate([49,75]):
        for j in range(6):
            x=191+j*16
            symbol('C','C'+str(bank*6+j+1),'1u / 100V',x,cy,'Capacitor_SMD:C_0805_2012Metric',{1:'DC+',2:'DC-'},bank==1)
            wire(x,cy-3.81,x,cy-7);label('DC+',x,cy-7)
            wire(x,cy+3.81,x,cy+7);label('DC-',x,cy+7)
    text('C1-C6 TOP: 6 uF nominal. C7-C12 BOTTOM: optional/DNP.\nTDK C2012X7S2A105K125AB. Retained C/ripple require validation.',190,88,.95)
else:
    pass
# Original revision bank retained below only for P0.
cap_x=[195,218,241,264]
for i,x in enumerate(cap_x if os.environ.get('CELL_REVISION')!='epc2361-cell-p1' else [],1):
    symbol('C','C'+str(i),'2.2u / 100V',x,60,'Capacitor_SMD:C_1210_3225Metric',{1:'DC+',2:'DC-'})
    wire(x,56.19,x,47);wire(x,63.81,x,73)
    if i>1:
        wire(cap_x[i-2],47,x,47);wire(cap_x[i-2],73,x,73)
    if 1<i<4:
        junction(x,47);junction(x,73)
if os.environ.get('CELL_REVISION')!='epc2361-cell-p1':
    label('DC+',195,47);label('DC-',195,73)
    text('C1-C4: placement candidates, 8.8 uF nominal total.\nRetained C at 75 V and RMS heating NOT yet verified.\nExternal bulk DC-link connection is required.',193,78,1.05)

text('DEVICE-REFERENCED PROBE PADS',193,99,1.52)
for ref,net,x,y in [('TP_GH','GH',197,116),('TP_SH','AC',225,116),('TP_GL','GL',253,116),
                    ('TP_SL','DC-',197,135),('TP_DC+','DC+',225,135),('TP_DC-','DC-',253,135),('TP_AC','AC',175,116)]:
    symbol('Pad',ref,net,x,y,LIB+':Probe_Pad',{1:net},show_value=False)
    wire(x,y,x,y+3.81);label(net,x,y+3.81)

text('PLACEMENT PROTOTYPE - NOT FOR MANUFACTURE OR FULL-CURRENT TEST',20,153,1.52)
text('1. One cell is one-sixth of the future 220 A RMS module: about 51.9 A peak with ideal sinusoidal sharing.',20,160,1.16)
text('2. QH1 / QL1 symbol exposes every package pad: 1 gate; 2,4,6 source; 3,5,7 drain. No separate Kelvin package pin.',20,165,1.16)
text('3. Gate return must take off at the source pad nearest the gate; copper geometry defines Kelvin performance.',20,170,1.16)
text('4. Cold plate contacts the source-connected FET tops through insulating TIM. Driver circuitry is external.',20,175,1.16)
text('5. Port pads and driver pads are interface placeholders, not selected/rated connectors. RG values require driver tuning.',20,180,1.16)
text('6. Verify VDS overshoot, capacitance bias/ripple, current sharing, coolant conditions and completed routing before release.',20,185,1.16)

OUT.mkdir(parents=True,exist_ok=True)
embedded=[value.replace('(symbol '+q(name), '(symbol '+q(LIB+':'+name),1) for name,value in defs.items()]
schematic='\n'.join(['(kicad_sch (version 20230121) (generator eeschema)',f'(uuid {sheet_id})','(paper "A4")',
    '(title_block (title "EPC2361 one-cell placement prototype") (date "2026-09-20") (rev "P0") (comment 1 "75 V max | 50-100 kHz | Not for manufacture"))',
    '(lib_symbols '+'\n'.join(embedded)+')','\n'.join(parts),'(sheet_instances (path "/" (page "1")))',')'])
if os.environ.get('CELL_REVISION')=='epc2361-cell-p1':schematic=schematic.replace('(rev "P0")','(rev "P1")').replace('2026-09-20','2026-09-21')
(OUT/(NAME+'.kicad_sch')).write_text(schematic,encoding='utf-8')
(OUT/(LIB+'.kicad_sym')).write_text('(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)\n'+'\n'.join(defs.values())+'\n)',encoding='utf-8')
(OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "epc2361-cell")(type "KiCad")(uri "${KIPRJMOD}/epc2361-cell.kicad_sym")(options "")(descr "Project-local EPC2361 cell symbols")))\n',encoding='utf-8')
project_path=OUT/(NAME+'.kicad_pro')
if not project_path.exists():
    template=Path('C:/Program Files/KiCad/7.0/share/kicad/template/kicad.kicad_pro')
    project=json.loads(template.read_text(encoding='utf-8'))
    project['meta']['filename']=project_path.name
    project_path.write_text(json.dumps(project,indent=2)+'\n',encoding='utf-8')
(OUT/'schematic-manifest.json').write_text(json.dumps({'sheet_uuid':sheet_id,'components':manifest},indent=2)+'\n',encoding='utf-8')
print(f'Wrote {len(manifest)} components to {OUT/(NAME+".kicad_sch")}')

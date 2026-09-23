"""Separate P6 mechanical study derived from P5. No copper/routing modifications."""
from pathlib import Path
import json, math, shutil
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'hardware/epc2361-prototype-p5'
OUT=ROOT/'hardware/epc2361-prototype-p6-mechanical'
OUT.mkdir(exist_ok=True)
(OUT/'models').mkdir(exist_ok=True)
b=p.LoadBoard(str(SRC/'epc2361-prototype-p5.kicad_pcb'))
def vec(x,y): return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def mm(v): return p.ToMM(v)
supports=[(40,8),(74,8),(40,53),(74,53)]
devices=[('QH1',48,32),('QL1',48,38),('QH2',66,32),('QL2',66,38)]
windows=[(39.2,29,42.8,40),(57.2,29,60.8,40),(50.8,29,54,40),(68.8,29,72,40),(38,33.25,76,36.75)]
def segdistance(x,y,x1,y1,x2,y2):
    dx=x2-x1;dy=y2-y1;t=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
    return math.hypot(x-x1-t*dx,y-y1-t*dy)
def rectdistance(x,y,l,t,r,bt): return math.hypot(max(l-x,0,x-r),max(t-y,0,y-bt))
audit=[]
for x,y in supports:
    nearby=[]
    for item in b.GetTracks():
        a=item.GetStart();c=item.GetEnd();d=segdistance(x,y,mm(a.x),mm(a.y),mm(c.x),mm(c.y))-mm(item.GetWidth())/2-1.2
        nearby.append((d,'track/via '+item.GetNetname()))
    for f in b.GetFootprints():
        for pad in f.Pads():
            box=pad.GetBoundingBox();d=rectdistance(x,y,mm(box.GetLeft()),mm(box.GetTop()),mm(box.GetRight()),mm(box.GetBottom()))-1.2
            nearby.append((d,f.GetReference()+'.'+pad.GetNumber()))
    nearby.sort()
    audit.append({'hole_center_mm':[x,y],'drill_mm':2.4,'nearest_existing_track_or_pad_edge_clearance_mm':round(nearby[0][0],3),'nearest_item':nearby[0][1],'nearest_five':[(round(a,3),c) for a,c in nearby[:5]],'zone_status':'Existing copper zones require refill/DRC around new NPTH; numeric scan excludes zones.'})
def line(x1,y1,x2,y2,layer=p.Dwgs_User):
    s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(vec(x1,y1));s.SetEnd(vec(x2,y2));s.SetLayer(layer);s.SetWidth(p.FromMM(.15));b.Add(s)
def rect(x1,y1,x2,y2,layer=p.Dwgs_User):
    for a,c in [((x1,y1),(x2,y1)),((x2,y1),(x2,y2)),((x2,y2),(x1,y2)),((x1,y2),(x1,y1))]:line(*a,*c,layer)
def text(s,x,y):
    t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(vec(x,y));t.SetTextSize(vec(.65,.65));t.SetTextThickness(p.FromMM(.1));t.SetLayer(p.Dwgs_User);b.Add(t)
for i,(x,y) in enumerate(supports,1):
    f=p.FOOTPRINT(b);f.SetReference('MH'+str(i));f.SetValue('M2 support STUDY');f.SetPosition(vec(x,y));f.Reference().SetVisible(False);f.Value().SetVisible(False)
    pad=p.PAD(f);pad.SetAttribute(p.PAD_ATTRIB_NPTH);pad.SetShape(p.PAD_SHAPE_CIRCLE);pad.SetSize(vec(2.4,2.4));pad.SetDrillSize(vec(2.4,2.4));pad.SetLayerSet(p.LSET.AllCuMask());pad.SetPosition(vec(x,y));f.Add(pad);b.Add(f)
    rect(x-2.5,y-2.5,x+2.5,y+2.5);text('MH'+str(i),x,y+3.5)
rect(38,6,76,33.25);rect(38,36.75,76,55)
for box in windows:rect(*box)
for ref,x,y in devices:
    rect(x-2,y-1,x+2,y+1)
    rect(x-2.75,y-1.75,x+2.75,y+1.75,p.Cmts_User)
text('P6 MECHANICAL STUDY / PLATE UNDERSIDE z=9 mm',57,12)
text('INSULATED BOSSES z=1.05 nominal / SHIM TO MEASURED STACK',57,15)
text('WINDOWS: GATE CONNECTORS + VDS PROBES',57,48)
# Retain original component models by copying into separate candidate project.
for f in (SRC/'models').iterdir():
    if f.is_file():shutil.copy2(f,OUT/'models'/f.name)
for name in ['fp-lib-table']:
    if (SRC/name).exists():shutil.copy2(SRC/name,OUT/name)
for f in SRC.glob('*.pretty'):
    shutil.copytree(f,OUT/f.name,dirs_exist_ok=True)
shutil.copy2(SRC/'epc2361-prototype-p5.kicad_pro',OUT/'epc2361-prototype-p6-mechanical.kicad_pro')
# VRML mechanical envelope: actual through windows, rectangular bolt keepout openings.
boxes=[]
cuts=windows+[(x-1.4,y-1.4,x+1.4,y+1.4) for x,y in supports]
xs=sorted(set([38,76]+[q for c in cuts for q in [c[0],c[2]]]))
ys=sorted(set([6,55]+[q for c in cuts for q in [c[1],c[3]]]))
for x1,x2 in zip(xs,xs[1:]):
    for y1,y2 in zip(ys,ys[1:]):
        cx=(x1+x2)/2;cy=(y1+y2)/2
        if not any(l<cx<r and t<cy<bt for l,t,r,bt in cuts):boxes.append((cx,cy,10.5,x2-x1,y2-y1,3,.55,.60,.66))
for ref,x,y in devices:
    boxes.append((x,y,5.025,4,2,7.95,.55,.60,.66))
    boxes.append((x,y,.875,5.5,3.5,.35,.25,.7,.75))
vrml=['#VRML V2.0 utf8']
for x,y,z,w,h,d,r,g,bl in boxes:
    vrml.append(f'Transform {{ translation {x/2.54:.6f} {-y/2.54:.6f} {z/2.54:.6f} children [ Shape {{ appearance Appearance {{ material Material {{ diffuseColor {r} {g} {bl} transparency 0.15 }} }} geometry Box {{ size {w/2.54:.6f} {h/2.54:.6f} {d/2.54:.6f} }} }} ] }}')
(OUT/'models/P6-raised-spreader-envelope.wrl').write_text('\n'.join(vrml))
f=p.FOOTPRINT(b);f.SetReference('MECH1');f.SetValue('UNQUALIFIED PLATE ENVELOPE');f.SetPosition(vec(0,0));f.Reference().SetVisible(False);f.Value().SetVisible(False)
m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/models/P6-raised-spreader-envelope.wrl';f.Models().push_back(m);b.Add(f)
b.BuildConnectivity();p.SaveBoard(str(OUT/'epc2361-prototype-p6-mechanical.kicad_pcb'),b)
(OUT/'mechanical-audit.json').write_text(json.dumps({'source':'P5 unchanged','supports':audit,'plate_mm':[38,6,76,55],'plate_underside_z_mm':9,'plate_top_z_mm':12,'boss_bottom_z_mm':1.05,'boss_foot_mm':[4,2],'TIM_nominal_uncompressed_mm':.5,'TIM_visual_compressed_mm':.35,'windows_mm':windows,'qualification':'Geometry study only. No thermal, electrical insulation, compression, strength or fluid qualification.'},indent=2))
# Engineering drawing with top plan and explicit stack section. No fluid channels implied.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="850" viewBox="0 0 120 85"><rect width="120" height="85" fill="white"/><g font-family="Arial" font-size="1.65" fill="#182536">','<text x="4" y="4" font-size="2.6">P6 raised spreader / cold-plate interface — mechanical candidate</text>','<text x="4" y="7">P5 copper preserved. Dimensions mm. Not a machining or fabrication release.</text>']
def sr(x,y,w,h,fill,stroke='#24384b',sw=.15):svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
sr(5,10,78.5,51,'#dce9df');sr(38,11,38,49,'#c1cbd4')
for l,t,r,bt in windows:sr(l,t+5,r-l,bt-t,'#ffffff')
for x,y in supports:svg.append(f'<circle cx="{x}" cy="{y+5}" r="1.2" fill="white" stroke="#24384b" stroke-width=".15"/>')
for ref,x,y in devices:
    sr(x-2.75,y+5-1.75,5.5,3.5,'#76c8ca');sr(x-2,y+5-1,4,2,'#65798a');svg.append(f'<text x="{x-2}" y="{y+9}">{ref}</text>')
svg+=['<text x="5" y="64">Plan: board 78.5 × 51; plate envelope 38 × 49; four Ø2.4 PCB support holes.</text>','<text x="5" y="67">White slots: connectors/probes and full-width3.5 coil gap; split rails require rigid external support.</text>']
# Enlarged section at right.
sr(89,52,26,2,'#477656');sr(97,50.6,10,1.4,'#272c32');sr(96.5,49.9,11,.7,'#76c8ca');sr(98,34,8,15.9,'#8396a6');sr(89,28,26,6,'#8396a6')
for txt,y in [('z=12 plate top',26),('z=9 underside',37),('z=1.05 boss foot',46),('TIM: 0.5 free, gap variable',58),('z=0 PCB top',61)]:svg.append(f'<text x="87" y="{y}" font-size="1.3">{txt}</text>')
svg+=['<text x="5" y="73">Stack: package 0.60–0.70 + assumed solder 0.02–0.08; boss datum 1.05 ± 0.05.</text>','<text x="5" y="76">Resulting TIM gap 0.22–0.48 (4–56% compression for nominal 0.5 TIM): measure and shim.</text>','<text x="5" y="79">Split spreaders: upright80mm CWTUM loop near x55,y35; fluid channels and rail stiffness unspecified.</text>','</g></svg>']
(OUT/'p6-mechanical-drawing.svg').write_text('\n'.join(svg),encoding='utf-8')
verified=p.LoadBoard(str(OUT/'epc2361-prototype-p6-mechanical.kicad_pcb'))
verified.BuildConnectivity()
filler=p.ZONE_FILLER(verified);filler.Fill(verified.Zones())
p.SaveBoard(str(OUT/'epc2361-prototype-p6-mechanical.kicad_pcb'),verified)
p.WriteDRCReport(verified,str(OUT/'mechanical-drc.rpt'),p.EDA_UNITS_MILLIMETRES,True)
print(json.dumps(audit,indent=2))
print(OUT)

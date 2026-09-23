"""Integrate two-current-channel mechanical envelopes; retain release hold."""
from p7_data import *
import pcbnew as p,wx,shutil,json,math
app=wx.App(False)
b=p.LoadBoard(str(OUT/(NAME+'.kicad_pcb')))
mb=p.LoadBoard(str(ROOT/'hardware/epc2361-prototype-p6-mechanical/epc2361-prototype-p6-mechanical.kicad_pcb'))
lib=OUT/(LIB+'.pretty')
for f in mb.GetFootprints():
    if not f.GetReference().startswith('MH'):continue
    g=f.Duplicate();g.SetParent(b);g.SetFPID(p.LIB_ID(LIB,'Support_NPTH_2p4'));b.Add(g);p.FootprintSave(str(lib),g)
def vec(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def rect(l,t,r,bt,layer=p.Dwgs_User):
    for a,c in [((l,t),(r,t)),((r,t),(r,bt)),((r,bt),(l,bt)),((l,bt),(l,t))]:
        g=p.PCB_SHAPE();g.SetShape(p.SHAPE_T_SEGMENT);g.SetStart(vec(*a));g.SetEnd(vec(*c));g.SetWidth(p.FromMM(.15));g.SetLayer(layer);b.Add(g)
def text(s,x,y):
    g=p.PCB_TEXT(b);g.SetText(s);g.SetPosition(vec(x,y));g.SetTextSize(vec(.8,.8));g.SetTextThickness(p.FromMM(.12));g.SetLayer(p.Dwgs_User);b.Add(g)
windows=[(39.2,29,42.8,40),(57.2,29,60.8,40),(50.8,29,54,40),(68.8,29,72,40),(38,32.9,76,37.1)]
supports=[(40,8),(74,8),(40,53),(74,53)]
cuts=windows+[(x-1.4,y-1.4,x+1.4,y+1.4) for x,y in supports]
xs=sorted(set([38,76]+[v for a in cuts for v in [a[0],a[2]]]))
ys=sorted(set([6,55]+[v for a in cuts for v in [a[1],a[3]]]))
boxes=[]
for x1,x2 in zip(xs,xs[1:]):
    for y1,y2 in zip(ys,ys[1:]):
        x,y=(x1+x2)/2,(y1+y2)/2
        if not any(l<x<r and t<y<bt for l,t,r,bt in cuts):boxes.append((x,y,10.5,x2-x1,y2-y1,3,.55,.60,.66))
for q in ['QH1','QL1','QH2','QL2']:
    x,y=parts[q]['x'],parts[q]['y'];boxes.append((x,y,5.025,4,1.6,7.95,.55,.60,.66))
    boxes.append((x,y,.875,5.5,3.5,.35,.25,.7,.75));rect(x-2,y-.8,x+2,y+.8)
vrml=['#VRML V2.0 utf8']
for x,y,z,w,d,h,r,g,bl in boxes:
    vrml.append(f'Transform {{ translation {x/2.54} {-y/2.54} {z/2.54} children [ Shape {{ appearance Appearance {{ material Material {{ diffuseColor {r} {g} {bl} transparency .2 }} }} geometry Box {{ size {w/2.54} {d/2.54} {h/2.54} }} }} ] }}')
(OUT/'models/P7-spreader-envelope.wrl').write_text('\n'.join(vrml))
# Both links have the same 5mm underside height. This raises the coil above
# the AC header housing; mating connectors and closure geometry remain unverified.
link=['#VRML V2.0 utf8']
for x,y,z,w,d,h in [(0,-3,2.75,2,.5,5.5),(0,3,2.75,2,.5,5.5),(0,0,5.25,2,6,.5)]:
    link.append(f'Transform {{ translation {x/2.54} {y/2.54} {z/2.54} children [ Shape {{ appearance Appearance {{ material Material {{ diffuseColor .8 .4 .15 }} }} geometry Box {{ size {w/2.54} {d/2.54} {h/2.54} }} }} ] }}')
(OUT/'models/P7-current-link-envelope.wrl').write_text('\n'.join(link))
for r in ['LK1','LK2']:
    f=next(f for f in b.GetFootprints() if f.GetReference()==r);f.Models().clear();m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/models/P7-current-link-envelope.wrl';f.Add3DModel(m);p.FootprintSave(str(lib),f)
# Circular coil winding envelopes only: no invented closing-head geometry.
coils=['#VRML V2.0 utf8'];R=80/(2*math.pi);tube=.8;cz=3+R+tube
for cx,cy,color in [(55,34,'.1 .55 .95'),(73,36,'.85 .15 .3')]:
    points=[];faces=[];N=96;M=12
    for i in range(N):
        a=2*math.pi*i/N
        for j in range(M):
            t=2*math.pi*j/M;r=R+tube*math.cos(t)
            points.append(f'{(cx+r*math.cos(a))/2.54} {-(cy+tube*math.sin(t))/2.54} {(cz+r*math.sin(a))/2.54}')
            faces.append(f'{i*M+j} {((i+1)%N)*M+j} {((i+1)%N)*M+(j+1)%M} {i*M+(j+1)%M} -1')
    coils.append('Shape { appearance Appearance { material Material { diffuseColor '+color+' transparency .35 } } geometry IndexedFaceSet { solid FALSE coord Coordinate { point [ '+', '.join(points)+' ] } coordIndex [ '+', '.join(faces)+' ] } }')
(OUT/'models/P7-two-coil-envelopes.wrl').write_text('\n'.join(coils))
f=p.FOOTPRINT(b);f.SetReference('MECH1');f.SetValue('P7 mechanical envelopes - review');f.SetPosition(vec(0,0));f.SetFPID(p.LIB_ID(LIB,'P7_Mechanical_Envelopes'));f.Reference().SetVisible(False);f.Value().SetVisible(False)
for fn in ['P7-spreader-envelope.wrl','P7-two-coil-envelopes.wrl']:
    m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/models/'+fn;f.Add3DModel(m)
b.Add(f);p.FootprintSave(str(lib),f)
rect(38,6,76,32.9);rect(38,37.1,76,55)
text('TWO LOW-SIDE CURRENTS: LK1=QL1 / LK2=QL2',54,58)
text('Coil planes y34/y36; matching links; geometry review only',54,60)
p.SaveBoard(str(OUT/(NAME+'.kicad_pcb')),b)
b=p.LoadBoard(str(OUT/(NAME+'.kicad_pcb')));fill=p.ZONE_FILLER(b);fill.Fill(b.Zones());p.SaveBoard(str(OUT/(NAME+'.kicad_pcb')),b)
pins={f.GetReference():{q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()} for f in b.GetFootprints()}
audit={}
for i,tp in [(1,'TP8'),(2,'TP12')]:
    q='QL'+str(i);lk='LK'+str(i);n='D_'+q
    expected={(q,'3'),(q,'5'),(q,'7'),(tp,'1'),(lk,'2')}
    actual={(r,k) for r,pp in pins.items() for k,v in pp.items() if v==n}
    assert actual==expected and pins[lk]['1']=='AC'
    assert all(pins[q][k]=='DC-' for k in ['2','4','6'])
    audit[q]=sorted(actual)
assert 'H1' not in pins and 'H2' not in pins
(OUT/'dual-current-audit.json').write_text(json.dumps({'channels':audit,'output_holes_removed':True,'coil_planes_y_mm':[34,36],'coil_outer_height_mm':[3,round(3+2*R+2*tube,3)],'nominal_winding_clearance_mm':.4,'closure_and_mating_fit':'unverified','link_underside_mm':5,'boss_contact_mm':[4,1.6]},indent=2))
print('P7 dual-current channels and mechanical envelopes integrated')

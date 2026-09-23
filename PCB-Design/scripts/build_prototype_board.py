from prototype_data import *
import json,shutil,re,copy,uuid
import pcbnew as p
import wx
app=wx.App(False)
SRC=ROOT/'hardware/epc2361-cell-p1';FPROOT=Path('C:/Program Files/KiCad/7.0/share/kicad/footprints');MROOT=Path('C:/Program Files/KiCad/7.0/share/kicad/3dmodels')
OUT.mkdir(exist_ok=True);(OUT/(LIB+'.pretty')).mkdir(exist_ok=True);(OUT/'models').mkdir(exist_ok=True)
for name in ['EPC2361','Probe_Pad']:shutil.copy2(SRC/'epc2361-cell.pretty'/(name+'.kicad_mod'),OUT/(LIB+'.pretty')/(name+'.kicad_mod'))
for name,model in [('EPC2361','EPC2361-envelope.wrl'),('LMG1210_RVR','LMG1210-envelope.wrl')]:
    fpfile=OUT/(LIB+'.pretty')/(name+'.kicad_mod');content=fpfile.read_text()
    if model not in content:
        end=content.rfind(')');content=content[:end]+f'(model "${{KIPRJMOD}}/models/{model}" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n'+content[end:];fpfile.write_text(content)
if not(OUT/(NAME+'.kicad_pro')).exists():shutil.copy2(SRC/'epc2361-cell.kicad_pro',OUT/(NAME+'.kicad_pro'))
for c in parts.values():
    lib,name=c['footprint'].split(':')
    if lib==LIB:continue
    folder=OUT/(lib+'.pretty');folder.mkdir(exist_ok=True)
    content=(FPROOT/(lib+'.pretty')/(name+'.kicad_mod')).read_text()
    def local_model(match):
        original=match.group(1) or match.group(2);rel=original.replace('\\','/').split('}',1)[-1].lstrip('/');source=MROOT/rel
        if source.exists():
            shutil.copy2(source,OUT/'models'/source.name)
            return '(model "${KIPRJMOD}/models/'+source.name+'"'
        return match.group(0)
    content=re.sub(r'\(model\s+(?:"([^"]+)"|([^\s()]+))',local_model,content)
    (folder/(name+'.kicad_mod')).write_text(content)
b=p.BOARD();b.SetCopperLayerCount(4)
nets={}
for n in sorted({n for c in parts.values() for n in c['pins'].values()}):
    ni=p.NETINFO_ITEM(b,n);b.Add(ni);nets[n]=ni
fps={};manifest=json.loads((OUT/'schematic-manifest.json').read_text())['components']
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def pos(ref,pin):
    q=next(q for q in fps[ref].Pads() if q.GetNumber()==str(pin));a=q.GetPosition();return p.ToMM(a.x),p.ToMM(a.y)
modelreport=[]
for ref,c in parts.items():
    lib,name=c['footprint'].split(':');path=OUT/(lib+'.pretty')
    f=p.FootprintLoad(str(path),name);assert f,ref
    f.SetReference(ref);f.SetValue(c['value']);f.SetFPID(p.LIB_ID(lib,name));f.SetPosition(v(c['x'],c['y']));f.SetOrientationDegrees(c['angle']);f.SetPath(p.KIID_PATH(manifest[ref]['path']))
    for q in f.Pads():
        if q.GetNumber():q.SetNet(nets[c['pins'][q.GetNumber()]])
    f.Reference().SetVisible(False);f.Value().SetVisible(False);b.Add(f);fps[ref]=f
    localmodels=[]
    for model in f.Models():
        rel=str(model.m_Filename).replace('\\','/').split('}',1)[-1].lstrip('/');source=MROOT/rel
        if source.exists():
            dest=OUT/'models'/source.name
            if not dest.exists():shutil.copy2(source,dest)
            model.m_Filename='${KIPRJMOD}/models/'+source.name
            modelreport.append((ref,source.name,'KiCad package model; mechanical fit must be checked'))
        localmodels.append(model)
        if ref not in ['QH1','QH2','QL1','QL2','U1'] and str(model.m_Filename).startswith('${KIPRJMOD}'):
            modelreport.append((ref,Path(str(model.m_Filename)).name,'Generic KiCad package model; verify mechanical fit'))
    f.Models().clear()
    for model in localmodels:f.Add3DModel(model)
def tr(n,x1,y1,x2,y2,w=.25,layer=p.F_Cu):
    if abs(x1-x2)+abs(y1-y2)<1e-6:return
    t=p.PCB_TRACK(b);t.SetStart(v(x1,y1));t.SetEnd(v(x2,y2));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNet(nets[n]);b.Add(t)
def via(n,x,y,d=.6,h=.3):
    q=p.PCB_VIA(b);q.SetPosition(v(x,y));q.SetWidth(p.FromMM(d));q.SetDrill(p.FromMM(h));q.SetLayerPair(p.F_Cu,p.B_Cu);q.SetNet(nets[n]);b.Add(q)
def zone(n,layer,points):
    z=p.ZONE(b);z.SetLayer(layer);z.SetNet(nets[n]);z.SetLocalClearance(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(p.FromMM(.15));poly=z.Outline();poly.NewOutline()
    for x,y in points:poly.Append(p.FromMM(x),p.FromMM(y))
    b.Add(z)
def text(s,x,y,layer=p.F_SilkS,size=.9):
    t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(v(x,y));t.SetTextSize(v(size,size));t.SetTextThickness(p.FromMM(.15));t.SetLayer(layer);b.Add(t)
def line(a,c,layer=p.Edge_Cuts):
    s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(v(*a));s.SetEnd(v(*c));s.SetLayer(layer);s.SetWidth(p.FromMM(.05));b.Add(s)
# Two copies of the checked local power loop, one rotated180deg. All parts F.Cu.
def xy(x,y,cell):return (49-x,54-y) if cell==1 else (41+x,16+y)
for cell in [1,2]:
    def track(n,x1,y1,x2,y2,w=.5):tr(n,*xy(x1,y1,cell),*xy(x2,y2,cell),w)
    for y,d,s,dy,sy in [(16,'DC+','AC',13.2,19),(22,'AC','DC-',19,25)]:
        for x in [13.725,15.425,17.352]:track(d,x,y-1.5,x,dy)
        track(d,13.725,dy,17.352,dy,1)
        for x,py in [(12.648,y+.67),(14.575,y),(16.275,y)]:track(s,x,py,x,sy)
        track(s,12.648,sy,17.352 if s=='AC' else 16.275,sy,1)
    for x in [12.648,14.575,16.275]:
        for dx in [-.35,.35]:
            vx,vy=xy(x+dx,25.8,cell);via('DC-',vx,vy);track('DC-',x,25,x+dx,25.8,.55)
    for x in [9.75,11.85,13.95,16.05,18.15,20.25]:
        for n,py,yy in [('DC+',10.95,12.1),('DC-',9.05,7.8)]:
            track(n,x,py,x,yy,.85);via(n,*xy(x,yy,cell))
            if n=='DC-':via(n,*xy(x,yy-.7,cell));track(n,x,yy,x,yy-.7,.6)
    zone('DC+',p.F_Cu,[xy(x,y,cell) for x,y in [(9.1,11.7),(21,11.7),(21,13),(13.3,13),(13.3,13.6),(9.1,13.6)]])
    track('AC',17.352,19,21,19,1.5)
    for dx in [-.6,0,.6]:
        for dy in [-.6,0,.6]:via('AC',*xy(21+dx,19+dy,cell));track('AC',21,19,21+dx,19+dy,.6)
# Common current collectors. They require electrothermal verification, not just net connectivity.
zone('DC-',p.In1_Cu,[(12,16),(82,16),(82,55),(12,55)])
zone('DC+',p.In2_Cu,[(24,8),(82,8),(82,55),(24,55)])
zone('AC',p.B_Cu,[(24,32),(31,32),(31,49),(59,49),(59,32),(82,32),(82,56),(24,56)])
for ref in ['JDC1','JDC2','JAC1']:
    c=parts[ref];n=c['pins']['1'];x,y=c['x'],c['y'];zone(n,p.F_Cu,[(x-6,y-6),(x+6,y-6),(x+6,y+6),(x-6,y+6)])
# Gate resistor to device: short local F.Cu links. Headers connect on the device side.
for rg,q,header,n in [('RGH1','QH1','JGH1','GH1'),('RGL1','QL1','JGL1','GL1'),('RGH2','QH2','JGH2','GH2'),('RGL2','QL2','JGL2','GL2')]:
    tr(n,*pos(rg,2),*pos(q,1),.2)
    gx,gy=pos(q,1);vx=gx+(.5 if q.endswith('1') else -.5);via(n,vx,gy);tr(n,gx,gy,vx,gy,.2)
    tr(n,vx,gy,*pos(header,1),.2,p.B_Cu)
    sx,sy=pos(q,2);hx,hy=pos(header,2);nsource=parts[q]['pins']['2'];tr(nsource,sx,sy,hx,hy,.25)
# Driver power-pin escapes; external net routing is finalized in a separate pass.
for pin,net,ex,ey in [(3,'DC-',41.8,35),(6,'VDD',43.75,37.6),(8,'LO',44.75,37.6),(10,'HO',46.25,37.6),(12,'HB',48.1,35.5),(13,'AC',47.4,35),(14,'AC',49.2,34.5),(17,'BST',44.75,32.3),(18,'HI',44.25,32.6),(19,'LI',43.75,33.1)]:
    tr(net,*pos('U1',pin),ex,ey,.15)
# Simple terminal test-point ties. No extra loops in the fast commutation path.
for ref in ['TP1','TP2','TP3','TP4','TP5']:
    x,y=pos(ref,1);n=parts[ref]['pins']['1'];via(n,x+.8,y);tr(n,x,y,x+.8,y,.25)
tr('DC+',63,28,61.25,28.1,.25)
for a,c in [((8,6),(84,6)),((84,6),(84,59)),((84,59),(8,59)),((8,59),(8,6))]:line(a,c)
for x in [34,56]:
    for a,c in [((x-3.5,30),(x+3.5,30)),((x+3.5,30),(x+3.5,40)),((x+3.5,40),(x-3.5,40)),((x-3.5,40),(x-3.5,30))]:line(a,c,p.Dwgs_User)
text('EPC2361 / 2 PARALLEL PER SWITCH / P2',44,8.5)
text('ALL CAPS ON TOP FACE',45,11)
text('DC+',75,8);text('DC-',75,23.7);text('AC',75,42)
text('12V / GND / HI / GND / LI / GND',15,43,p.Dwgs_User,.65)
text('ENGINEERING PROTOTYPE - NOT FOR FABRICATION',45,57.5)
text('INSULATED COLD PLATE CONTACTS',45,51,p.Dwgs_User,.8)
# Dimensioned envelope models explicitly distinguished from manufacturer models.
for name,w,d,h in [('EPC2361-envelope',5,3,.65),('LMG1210-envelope',4,3,.8)]:
    (OUT/'models'/(name+'.wrl')).write_text(f'#VRML V2.0 utf8\n# Approximate dimensioned envelope, NOT manufacturer CAD\nTransform {{ translation 0 0 {(h/2+.05)/2.54} children [ Shape {{ appearance Appearance {{ material Material {{ diffuseColor .15 .16 .18 }} }} geometry Box {{ size {w/2.54} {d/2.54} {h/2.54} }} }} ] }}\n')
for ref in ['QH1','QH2','QL1','QL2','U1']:
    name='LMG1210-envelope.wrl' if ref=='U1' else 'EPC2361-envelope.wrl';modelreport.append((ref,name,'Approximate envelope, not manufacturer CAD'))
b.BuildConnectivity();p.SaveBoard(str(OUT/(NAME+'.kicad_pcb')),b)
# Preserve checked P1 stackup description.
s=(SRC/'epc2361-cell.kicad_pcb').read_text();start=s.index('(stackup');depth=0;end=start
for j in range(start,len(s)):
    if s[j]=='(':depth+=1
    elif s[j]==')':
        depth-=1
        if depth==0:end=j+1;break
f=OUT/(NAME+'.kicad_pcb');f.write_text(f.read_text().replace('(setup','(setup\n'+s[start:end],1))
libs=sorted({c['footprint'].split(':')[0] for c in parts.values()})
(OUT/'fp-lib-table').write_text('(fp_lib_table\n'+''.join(f'(lib (name "{lib}")(type "KiCad")(uri "${{KIPRJMOD}}/{lib}.pretty")(options "")(descr ""))\n' for lib in libs)+')')
(OUT/'model-coverage.json').write_text(json.dumps(modelreport,indent=2))
print('Prototype board generated:',len(fps),'components')

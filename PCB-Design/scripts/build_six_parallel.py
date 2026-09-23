"""Replicate checked P1 cells with common power rails and independent gate nets."""
from pathlib import Path
import re,json,uuid,copy,shutil
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'hardware/epc2361-cell-p1';OUT=ROOT/'hardware/epc2361-sixparallel'
OUT.mkdir(exist_ok=True)
NAME='epc2361-sixparallel'
class Q(str):pass
def parse(s):
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s);stack=[];root=None
    for t in tokens:
        if t=='(':
            a=[]
            if stack:stack[-1].append(a)
            else:root=a
            stack.append(a)
        elif t==')':stack.pop()
        else:stack[-1].append(Q(json.loads(t)) if t.startswith('"') else t)
    return root
def dump(a):
    if isinstance(a,list):return '('+' '.join(dump(x) for x in a)+')'
    return json.dumps(str(a)) if isinstance(a,Q) else str(a)
def child(a,key):return next((v for v in a[1:] if isinstance(v,list) and v and v[0]==key),None)
def walk(a):
    if isinstance(a,list):
        yield a
        for x in a:yield from walk(x)
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'epc2361-six/'+s))
def net(name,i):return name if name in ['DC+','DC-','AC',''] else name+'_'+str(i)
def ref(name,i):
    match=re.fullmatch(r'([A-Z]+)(\d+)',name);prefix,n=match.group(1),int(match.group(2))
    stride={'QH':1,'QL':1,'C':12,'RG':2,'RGS':2,'JGH':1,'JGL':1,'JDC':2,'JAC':1,'TP':7}[prefix]
    return prefix+str(n+(i-1)*stride)
manifest=json.loads((SRC/'schematic-manifest.json').read_text())['components']
sheet= parse((SRC/'epc2361-cell.kicad_sch').read_text())
board=parse((SRC/'epc2361-cell.kicad_pcb').read_text())
rootid=uid('root');allparts={}
netnames=['','DC+','DC-','AC']+[net(n,i) for i in range(1,7) for n in ['GH','GL','GH_DRV','GL_DRV']]
netids={n:j for j,n in enumerate(netnames)}
oldnets={str(a[1]):str(a[2]) for a in board[1:] if isinstance(a,list) and a[0]=='net'}
newboard=[board[0]]+[copy.deepcopy(a) for a in board[1:] if isinstance(a,list) and a[0] in ['version','generator','general','paper','layers','setup']]
newboard += [['net',str(k),Q(n)] for n,k in netids.items()]
parentsheets=[]
for i in range(1,7):
    sid=uid('sheet'+str(i));path='/'+rootid+'/'+sid;dx=(i-1)*22
    cs=copy.deepcopy(sheet)
    for a in walk(cs):
        if a and a[0]=='uuid':a[1]=uid(str(i)+'/'+str(a[1]))
    cs[:]=[a for a in cs if not(isinstance(a,list) and a[0]=='sheet_instances')]
    for a in cs[1:]:
        if not isinstance(a,list):continue
        if a[0]=='symbol' and child(a,'lib_id'):
            r=next(p for p in a if isinstance(p,list) and p[:2]==['property','Reference']);old=str(r[2]);new=ref(old,i);r[2]=Q(new)
            ins=child(a,'instances');ins[:]=['instances',['project',Q(NAME),['path',Q(path),['reference',Q(new)],['unit','1']]]]
            c=copy.deepcopy(manifest[old]);c['uuid']=child(a,'uuid')[1];c['path']=path+'/'+c['uuid'];c['pins']={k:net(v,i) for k,v in c['pins'].items()};allparts[new]=c
        elif a[0]=='label':
            a[0]='global_label';a[1]=Q(net(str(a[1]),i));a.append(['shape','input'])
        elif a[0]=='text':
            a[1]=Q(str(a[1]).replace('ONE HALF-BRIDGE CELL','PARALLEL CELL '+str(i)))
    (OUT/f'cell-{i}.kicad_sch').write_text(dump(cs))
    x=25+((i-1)%3)*85;y=50+((i-1)//3)*65
    parentsheets.append(parse(f'''(sheet (at {x} {y}) (size 65 35) (stroke (width 0) (type default)) (fill (color 0 0 0 0)) (uuid {sid})
      (property "Sheetname" "Cell {i}" (at {x} {y-1} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
      (property "Sheetfile" "cell-{i}.kicad_sch" (at {x} {y+36} 0) (effects (font (size 1.27 1.27)) (justify left top)))
      (instances (project "{NAME}" (path "/{rootid}" (page "{i+1}")))))'''))
    for orig in board[1:]:
        if not isinstance(orig,list) or orig[0] not in ['footprint','segment','via','zone','gr_line']:continue
        if orig[0]=='gr_line' and child(orig,'layer')[1]!='Dwgs.User':continue
        a=copy.deepcopy(orig)
        for node in walk(a):
            if node and node[0]=='tstamp':node[1]=uid(str(i)+'/'+str(node[1]))
            if node and node[0]=='net':
                n=net(oldnets[str(node[1])],i);node[1]=str(netids[n])
                if len(node)>2:node[2]=Q(n)
            if node and node[0]=='net_name':node[1]=Q(net(str(node[1]),i))
            if node and node[0]=='model':node[1]=Q(str(node[1]).replace('KICAD6_3DMODEL_DIR','KICAD7_3DMODEL_DIR'))
        if a[0]=='footprint':
            pos=child(a,'at');pos[1]=str(float(pos[1])+dx)
            r=next(n for n in a if isinstance(n,list) and n[:2]==['fp_text','reference']);old=str(r[2]);r[2]=Q(ref(old,i))
            child(a,'path')[1]=Q(allparts[ref(old,i)]['path'])
            if old.startswith('Q'):a.append(parse('(model "${KIPRJMOD}/models/EPC2361-envelope.wrl" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))'))
        else:
            # All coordinates outside footprints are board coordinates.
            a[:]=[n for n in a if not(isinstance(n,list) and n[0]=='filled_polygon')]
            for n in walk(a):
                if n and n[0] in ['start','end','at','xy']:n[1]=str(float(n[1])+dx)
        newboard.append(a)
parent=parse(f'''(kicad_sch (version 20230121) (generator eeschema) (uuid {rootid}) (paper "A4")
 (title_block (title "Six parallel EPC2361 half-bridge cells") (rev "S1") (date "2026-09-21"))
 (lib_symbols)
 (text "SIX PARALLEL CELLS / 12 EPC2361" (at 25 20 0) (effects (font (size 2 2)) (justify left top)) (uuid {uid('title')}))
 (text "Common global DC+, DC- and AC. Each device retains an individual gate input and resistor." (at 25 29 0) (effects (font (size 1.27 1.27)) (justify left top)) (uuid {uid('note')}))
 (text "75 V max; 50-100 kHz. 220 A RMS is a target, not a validated rating. Study only." (at 25 173 0) (effects (font (size 1.27 1.27)) (justify left top)) (uuid {uid('warning')}))
 (sheet_instances (path "/" (page "1"))))''')
parent.extend(parentsheets);(OUT/(NAME+'.kicad_sch')).write_text(dump(parent))
(OUT/(NAME+'.kicad_pcb')).write_text(dump(newboard))
(OUT/'schematic-manifest.json').write_text(json.dumps({'sheet_uuid':rootid,'components':allparts},indent=2))
for f in ['sym-lib-table','fp-lib-table','epc2361-cell.kicad_sym']:shutil.copy2(SRC/f,OUT/f)
shutil.copytree(SRC/'epc2361-cell.pretty',OUT/'epc2361-cell.pretty',dirs_exist_ok=True)
if not(OUT/(NAME+'.kicad_pro')).exists():shutil.copy2(SRC/'epc2361-cell.kicad_pro',OUT/(NAME+'.kicad_pro'))
(OUT/'models').mkdir(exist_ok=True)
(OUT/'models/EPC2361-envelope.wrl').write_text('#VRML V2.0 utf8\n# Approximate 5 x 3 x 0.65 mm package envelope; not manufacturer CAD.\nTransform { translation 0 0 0.147638 children [ Shape { appearance Appearance { material Material { diffuseColor 0.12 0.13 0.15 } } geometry Box { size 1.968504 1.181102 0.255906 } } ] }\n')
print('Six-cell schematic and board geometry written')

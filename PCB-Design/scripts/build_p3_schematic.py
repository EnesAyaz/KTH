from p3_data import *
import uuid,json,collections
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'epc2361-prototype/'+s))
def q(s):return json.dumps(str(s))
sheet=uid('sheet');defs=[];items=[];manifest={}
def effects(size=1,hidden=False):return f'(effects (font (size {size} {size}))'+(' hide' if hidden else '')+')'
def prop(k,v,x,y,hidden=False):return f'(property {q(k)} {q(v)} (at {x} {y} 0) {effects(1,hidden)})'
def text(s,x,y,size=1.4):items.append(f'(text {q(s)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {uid(s+str(x)+str(y))}))')
def wire(x,y,ex,ey,key):items.append(f'(wire (pts (xy {x} {y}) (xy {ex} {ey})) (stroke (width 0) (type default)) (uuid {uid(key)}))')
def lab(n,x,y,key):items.append(f'(label {q(n)} (at {x} {y} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid {uid(key)}))')
def put(ref,x,y):
    c=parts[ref];pins=list(c['pins']);n=len(pins);rows=(n+1)//2;h=max(5,rows*2.54);w=7.62 if n>7 else 5.08
    ps=[];coords={}
    for j,pin in enumerate(pins):
        side=0 if j<rows else 1;r=j if side==0 else j-rows;py=(rows-1)*1.27-r*2.54;px=-w-2.54 if side==0 else w+2.54;angle=0 if side==0 else 180
        pn=c['pins'][pin];kind='passive'
        if ref=='U1' and pn.startswith('NC'):kind='no_connect'
        ps.append(f'(pin {kind} line (at {px} {py} {angle}) (length 2.54) (name {q(pn)} {effects(.85)}) (number {q(pin)} {effects(.85)}))')
        coords[pin]=(x+px,y-py,side)
    defs.append(f'(symbol {q(LIB+":"+ref)} (pin_names (offset .5)) (in_bom yes) (on_board yes) '+prop('Reference',ref,0,-h/2-2)+prop('Value',c['value'],0,h/2+2)+f'(symbol {q(ref+"_0_1")} (rectangle (start {-w} {h/2}) (end {w} {-h/2}) (stroke (width .2) (type default)) (fill (type background)))) (symbol {q(ref+"_1_1")} '+''.join(ps)+'))')
    symbolid=uid(ref);body=f'(symbol (lib_id {q(LIB+":"+ref)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if c["dnp"] else "no"}) (uuid {symbolid})'
    body+=prop('Reference',ref,x,y-h/2-3)+prop('Value',c['value'],x,y+h/2+3)+prop('Footprint',c['footprint'],x,y,True)
    body+=f'(instances (project {q(NAME)} (path {q("/"+sheet)} (reference {q(ref)}) (unit 1)))))';items.append(body)
    for pin,(px,py,side) in coords.items():
        net=c['pins'][pin]
        if ref=='U1' and net.startswith('NC'):
            items.append(f'(no_connect (at {px} {py}) (uuid {uid(ref+pin+"NC")}))');continue
        ex=px+(-5.08 if side==0 else 5.08);wire(px,py,ex,py,ref+pin+'wire');lab(net,ex,py,ref+pin+'label')
    manifest[ref]={**c,'uuid':symbolid,'path':'/'+sheet+'/'+symbolid}
text('EPC2361 / TWO PARALLEL DEVICES PER SWITCH',15,12,2.5)
text('75 V max | 36.7 A RMS / 51.9 A peak target | 50 kHz nominal, 100 kHz max | Engineering prototype',15,20,1.4)
for ref,x,y in [('QH1',45,52),('QH2',105,52),('QL1',45,92),('QL2',105,92)]:put(ref,x,y)
for j,ref in enumerate(bus_caps):put(ref,165+(j%8)*30,38+(j//8)*25)
text('24 BUS CAPS: SIX ABOVE AND SIX BELOW EACH PAIR. ALL ON TOP FACE.',150,99,1.1)
for j,ref in enumerate(['RGH1','RGH2','RGL1','RGL2']):put(ref,40+j*90,125)
for j,ref in enumerate(['JGH1','JGH2','JGL1','JGL2']):put(ref,40+j*90,150)
put('U1',62,208);put('JCTRL1',145,208)
for j,ref in enumerate(['C13','C14','C15','C16','C17','C18','RB1','D1','RH1','RL1']):put(ref,205+(j%5)*40,188+(j//5)*37)
for j,ref in enumerate(['JDC1','JDC2','JAC1','TP1','TP2','TP3','TP4','TP5']):put(ref,25+j*48,242)
text('IIM: external HI/LI MUST have nonoverlap. Bootstrap needs startup charging and periodic low-side intervals; no sustained100% high-side duty.',15,277,1.1)
text('G/KS headers: do not attach an external driver with onboard outputs connected. RG footprints remain independently tunable.',15,283,1.1)
OUT.mkdir(exist_ok=True)
(OUT/(NAME+'.kicad_sch')).write_text('\n'.join(['(kicad_sch (version 20230121) (generator eeschema)',f'(uuid {sheet})','(paper "A3")','(title_block (title "Four EPC2361 onboard-driver prototype") (rev "P3") (date "2026-09-21"))','(lib_symbols '+''.join(defs)+')',*items,'(sheet_instances (path "/" (page "1")))',')']))
(OUT/'schematic-manifest.json').write_text(json.dumps({'sheet_uuid':sheet,'components':manifest},indent=2))
groups=collections.defaultdict(list)
for r,c in parts.items():groups[(c['mpn'],c['value'],c['footprint'],c['dnp'],c['notes'])].append(r)
rows=['# Prototype BOM','', 'All quantities are for one four-FET board. Provisional engineering BOM; not purchasing release.','', '| References | Qty | MPN | Value | Footprint | Fit | Notes |','|---|---:|---|---|---|---|---|']
for (mpn,val,fp,dnp,notes),refs in groups.items():rows.append('| '+', '.join(refs)+f' | {len(refs)} | {mpn} | {val} | {fp} | '+('Optional/DNP' if dnp else 'Fit')+' | '+notes+' |')
(OUT/'BOM.md').write_text('\n'.join(rows)+'\n')
(OUT/'BOM.json').write_text(json.dumps(parts,indent=2))
print('Schematic/BOM:',len(parts),'components')

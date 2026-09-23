from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1];scripts=root/'scripts';src=root/'hardware/epc2361-prototype-p4';dst=root/'hardware/epc2361-prototype-p5'
dst.mkdir(exist_ok=True)
for name in ['epc2361-prototype.pretty','models']:shutil.copytree(src/name,dst/name,dirs_exist_ok=True)
(dst/'epc2361-prototype.pretty/Coil_Access_3.2.kicad_mod').write_text('(footprint "Coil_Access_3.2" (version 20221018) (generator pcbnew) (layer "F.Cu") (attr exclude_from_pos_files exclude_from_bom) (fp_text reference "REF**" (at 0 -2.5) (layer "F.SilkS") (effects (font (size .8 .8)(thickness .12)))) (fp_text value "Coil_Access_3.2" (at 0 2.5) (layer "F.Fab") (effects (font (size .8 .8)(thickness .12)))) (pad "" np_thru_hole circle (at 0 0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask")))')
mapping=[('build_p4_schematic.py','build_p5_schematic.py'),('build_p4_board.py','build_p5_board.py'),('route_p4.py','route_p5.py'),('route_p4_gates.py','route_p5_gates.py'),('check_p4.py','check_p5.py'),('label_p4.py','label_p5.py'),('audit_p4_gate_paths.py','audit_p5_gate_paths.py')]
for old,new in mapping:
    s=(scripts/old).read_text(encoding='utf-8-sig').replace('from p4_data import *','from p5_data import *').replace('/ P4','/ P5').replace('(rev "P4")','(rev "P5")').replace("'scripts/route_p4.py'","'scripts/route_p5.py'")
    if new=='build_p5_schematic.py':
        s=s.replace("for j,ref in enumerate(['JDC1','JDC2','JAC1','TP1','TP2','TP3','TP4','TP5']):put(ref,25+j*48,242)","for j,ref in enumerate(['JDC1','JDC2','JAC1']):put(ref,30+j*48,247)\nfor j,ref in enumerate(['TP'+str(i) for i in range(1,14)]+['H1','H2']):put(ref,180+(j%8)*29,243+(j//8)*20)")
    if new=='build_p5_board.py':
        s=s.replace("zone('DC-',p.In1_Cu,[(7,7),(88,7),(88,57),(7,57)])","zone('DC-',p.In1_Cu,[(7,7),(74,7),(74,55),(7,55)])")
        s=s.replace("zone('DC+',p.In2_Cu,[(7,7),(88,7),(88,57),(7,57)])","zone('DC+',p.In2_Cu,[(7,7),(74,7),(74,55),(41,55),(41,19),(7,19)])\nzone('VIN',p.In2_Cu,[(8,21),(32,21),(32,51),(8,51)])\nzone('VDD',p.In2_Cu,[(33,40.5),(40,40.5),(40,51),(33,51)])")
        s=s.replace("[(40,32),(45,32),(45,49),(69,49),(69,29),(87,29),(87,56),(40,56)]","[(40,32),(45,32),(45,49),(69,49),(69,30),(77,30),(77,21),(82.5,21),(82.5,50.8),(77,50.8),(77,40),(74,40),(74,50.8),(40,50.8)]")
        a=s.index('for a,c in [((5,5)')
        s=s[:a]+"for q,dr,sr in vds_pairs:\n    tr(parts[dr]['pins']['1'],*pos(q,7),*pos(dr,1),.2)\n    tr(parts[sr]['pins']['1'],*pos(q,6),*pos(sr,1),.2)\n"+s[a:]
    if new=='check_p5.py':s=s.replace("if not r.startswith('TP'):","if not r.startswith(('TP','H')):")
    if new=='label_p5.py':s=s.replace("if r.startswith('TP'):label(c['value'],x,y-1.5)","if r.startswith('TP') and int(r[2:])<=5:label(c['value'],x,y-1.5)")
    (scripts/new).write_text(s)
print('P5 generators prepared')

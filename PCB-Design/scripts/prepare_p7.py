from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1];scripts=root/'scripts'
src=root/'hardware/epc2361-prototype-p6';dst=root/'hardware/epc2361-prototype-p7'
dst.mkdir(exist_ok=True)
for d in src.iterdir():
    if d.is_dir() and (d.suffix=='.pretty' or d.name=='models'):shutil.copytree(d,dst/d.name,dirs_exist_ok=True)
for stem in ['build_p6_schematic','build_p6_board','route_p6','route_p6_gates','label_p6','audit_p6_gate_paths']:
    s=(scripts/(stem+'.py')).read_text(encoding='utf-8-sig').replace('from p6_data import *','from p7_data import *').replace('scripts/route_p6.py','scripts/route_p7.py').replace('/ P6','/ P7').replace('(rev "P6")','(rev "P7")')
    if stem=='build_p6_schematic':
        s=s.replace("+['H1','H2']",'')
        s=s.replace("put('LK1',375,273)","put('LK1',330,267)\nput('LK2',375,267)")
    if stem=='build_p6_board':
        s=s.replace("        if cell==1:\n            if y==16:sy=18.5\n            else:d='D_QL1';dy=19.55", "        if y==16:sy=18.5\n        else:d='D_QL'+str(cell);dy=19.55")
        s=s.replace(".5 if d=='D_QL1' else 1", ".5 if d.startswith('D_QL') else 1")
        a=s.index('    if cell==1:\n        tr(\'AC\',50.352')
        z=s.index('# Supplementary',a)
        s=s[:a]+'''    offset=18*(cell-1);dn='D_QL'+str(cell)
    tr('AC',50.352+offset,34.5,53.8+offset,34.5,.8)
    tr('AC',53.8+offset,34.5,55+offset,32,1)
    for dx in [-.6,0,.6]:
        for dy in [-.6,0,.6]:via('AC',55+offset+dx,32+dy)
    tr(dn,50.352+offset,35.55,53.2+offset,35.55,.5)
    tr(dn,53.2+offset,35.55,53.2+offset,38,.8)
    tr(dn,53.2+offset,38,55+offset,38,.8)
'''+s[z:]
    if stem=='route_p6':s=s.replace('[(55,32),(72,35)]','[(55,32),(73,32)]')
    if stem=='label_p6':
        s=s.replace("label('EPC2361 / TWO PER SWITCH / P7',59,8,size=1,fixed=True)","label('EPC2361 / TWO PER SWITCH / P7',59,8,size=.9)")
        s=s.replace('occupied=[]','occupied=[]\nfor x,y in [(40,8),(74,8),(40,53),(74,53)]:occupied.append((x-1.7,y-1.7,x+1.7,y+1.7))')
        s=s.replace("label('REVIEW PROTOTYPE',47,54", "label('REVIEW PROTOTYPE',54,54")
        s=s.replace("label('LK1 QL1 CURRENT',55,17,size=.8)","label('LK1 / QL1 CURRENT',51,16,size=.8)\nlabel('LK2 / QL2 CURRENT',69,18,size=.8)")
        s=s.replace("if r=='LK1':continue","if r.startswith('LK'):continue")
    (scripts/(stem.replace('p6','p7')+'.py')).write_text(s)
print('Dual-current P7 generators prepared')

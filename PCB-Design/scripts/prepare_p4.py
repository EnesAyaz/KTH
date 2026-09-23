"""Create revision-specific generators by mechanical reuse of P3 machinery."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1];scripts=root/'scripts'
dst=root/'hardware/epc2361-prototype-p4';src=root/'hardware/epc2361-prototype-p3'
dst.mkdir(exist_ok=True)
for name in ['epc2361-prototype.pretty','models']:
    shutil.copytree(src/name,dst/name,dirs_exist_ok=True)
for old,new in [('build_p3_schematic.py','build_p4_schematic.py'),('build_p3_board.py','build_p4_board.py'),('route_p3.py','route_p4.py'),('check_p3.py','check_p4.py'),('label_p3.py','label_p4.py')]:
    s=(scripts/old).read_text(encoding='utf-8-sig').replace('from p3_data import *','from p4_data import *').replace('/ P3','/ P4').replace('(rev "P3")','(rev "P4")').replace('2026-09-21','2026-09-22')
    if new=='build_p4_board.py':
        s=s.replace("c=parts[ref];n=c['pins']['1'];x,y=c['x'],c['y'];zone(n,p.F_Cu,[(x-6,y-6),(x+6,y-6),(x+6,y+6),(x-6,y+6)])", "c=parts[ref];n=c['pins']['1'];coords=[pos(ref,i) for i in range(1,25)];xs=[a[0] for a in coords];ys=[a[1] for a in coords];x0=min(xs)-1.25;x1=max(xs)+1.25;y0=min(ys)-1.25;y1=max(ys)+1.25;zone(n,p.F_Cu,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)])")
        a=s.index('for a,c in [((5,5)');z=s.index('# Dimensioned envelope',a)
        s=s[:a]+"for a,c in [((5,5),(83.5,5)),((83.5,5),(83.5,56)),((83.5,56),(5,56)),((5,56),(5,5))]:line(a,c)\n"+s[z:]
    if new=='route_p4.py':s=s.replace('W=830;H=530','W=765;H=490')
    if new=='label_p4.py':
        s=s.replace('89.4','82.9').replace('59.4','55.4').replace("label('REVIEW PROTOTYPE',47,58", "label('REVIEW PROTOTYPE',47,54")
        s=s.replace("label('DC+',14,22,size=1);label('DC-',32,24,size=1);label('AC',80,27,size=1)","label('JDC1 DC+ ALL 24',22,12,size=.8);label('JDC2 DC- ALL 24',22,18,size=.8);label('JAC1 AC ALL 24',81.8,36,90,size=.8)")
        s=s.replace("if r in bus_caps or r in ['JGH1','JGL1','JGH2','JGL2']:continue", "if r in bus_caps or r in ['JGH1','JGL1','JGH2','JGL2','JDC1','JDC2','JAC1']:continue")
    (scripts/new).write_text(s)
print('P4 generators prepared')
s=(scripts/'route_p3_gates.py').read_text().replace('from p3_data import *','from p4_data import *').replace("'scripts/route_p3.py'","'scripts/route_p4.py'")
(scripts/'route_p4_gates.py').write_text(s)

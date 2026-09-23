"""DPT review revision: physically separated driver supply and VDS taps."""
from p4_data import *
parts=copy.deepcopy(parts)
OUT=ROOT/'hardware/epc2361-prototype-p5'
NAME='epc2361-prototype-p5'
vds_pairs=[]
for i,q in enumerate(['QH1','QL1','QH2','QL2']):
    base=6+2*i;x=parts[q]['x']+4;y=parts[q]['y']
    for ref,net,yy,role in [('TP'+str(base),parts[q]['pins']['3'],y-1.5,'D'),('TP'+str(base+1),parts[q]['pins']['2'],y,'S')]:
        parts[ref]=dict(value=q+' '+role,mpn='PCB copper test pad',footprint=LIB+':Probe_Pad',pins={'1':net},x=x,y=yy,angle=0,dnp=False,notes='Local VDS spring-tip contact; 1.5 mm D/S spacing, verify actual probe accessory. High-side source is AC, not earth.')
    vds_pairs.append((q,'TP'+str(base),'TP'+str(base+1)))
parts['TP1'].update(x=72,y=29)
parts['TP3'].update(x=73,y=47)
for ref,x,y in [('H1',75,27),('H2',75,43)]:
    parts[ref]=dict(value='I_OUT coil access',mpn='PCB drilled feature',footprint=LIB+':Coil_Access_3.2',pins={},x=x,y=y,angle=0,dnp=False,notes='Provisional 3.2 mm NPTH Rogowski access, 16 mm centre spacing. Measures output current only. Coil closure, bend radius and insulation must be checked before drilling release.')

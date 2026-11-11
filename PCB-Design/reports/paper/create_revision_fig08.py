from pathlib import Path
import sys,json
import numpy as np
ROOT=Path.cwd();P=ROOT/'reports/paper';A=P/'icpe/revised_blue_2026-11-06'
src=(P/'icpe/make_compact_digest_figures.py').read_text(encoding='utf-8');ns={'__file__':str(P/'icpe/make_compact_digest_figures.py')};exec(src.split('dimensions={}')[0],ns);ns['A']=A;ns['dimensions']={}
Fig=ns['Fig'];TEAL=ns['TEAL'];WINE=ns['WINE'];OCHRE=ns['OCHRE'];GREY=ns['GREY'];INK=ns['INK']
sys.path.insert(0,str(ROOT/'scripts'));from icpe_gate_results import read_raw
R=ROOT/'simulation/bb_spice/icpe_digest_revision_2026-11-06/controlled_current';D=json.loads((R/'results_complete_windows.json').read_text())
f=Fig(500,132)
ta=f.axes(29,27,133,67,(-5,45),(0,110),[0,20,40],[0,50,90],'Time from turn-on (ns)','HS voltage (V)');f.text(95,10,'(a) Rated current: settings A–C',7.5,'middle');f.line([ta(-5,90),ta(45,90)],GREY,'2 2')
tb=f.axes(199,27,133,67,(-5,45),(-3,2),[0,20,40],[-2,0,1],'Time from turn-on (ns)','Held-off gate (V)');f.text(265,10,'(b) Rated current: settings A–C',7.5,'middle');f.line([tb(-5,.8),tb(45,.8)],GREY,'2 2')
for lab,r,bias,col in [('A',2,0,INK),('B',3,0,OCHRE),('C',3,-1,WINE)]:
 key=f'proto_g20_r{r}_off{bias}_i322.061_v75_t27_dt0.2';z=read_raw(R/(key+'.raw'))[0];v=D[key];k=max(v['branches'],key=lambda b:b['vhs_on'])['k'];kg=max(v['branches'],key=lambda b:b['gate_bump'])['k'];t=z['time'];m=(t>=1.695e-6)&(t<=1.745e-6);ix=np.flatnonzero(m)[::2]
 vv=z[f'v(dh{k})']-z[f'v(qh_s_{k})'];gg=z[f'v(gh{kg})']-z[f'v(qh_s_{kg})'];f.line([ta((t[i]-1.7e-6)*1e9,vv[i]) for i in ix],col,lw=.8);f.line([tb((t[i]-1.7e-6)*1e9,gg[i]) for i in ix],col,lw=.8)
 x=21+54*('ABC'.index(lab));f.line([(x,129),(x+12,129)],col);f.text(x+16,131,lab,7.5)
tc=f.axes(369,27,126,67,(0,330),(85,94),[0,160,320],[86,90,94],'Total current (A)','Peak voltage (V)');f.text(432,10,'(c) Positive-current sweep',7.5,'middle');f.line([tc(0,90),tc(330,90)],GREY,'2 2')
for g,c,lab in [(10,TEAL,'D: 10 nH'),(20,WINE,'C: 20 nH')]:
 pts=[(v['setup']['controlled_current_A'],v['vds_peak']) for v in D.values() if v['setup']['gate_loop_nH']==g and v['setup']['Rgon_ohm']==3 and v['setup']['Voff_V']==-1 and v['setup']['Tj_C']==27 and v['setup']['Vbus_V']==75 and abs(v['setup']['controlled_current_A']-315.946)>.1];pts.sort();f.line([tc(x,y) for x,y in pts],c)
 for x,y in pts:f.dot(*tc(x,y),c,1.5)
 x=335 if g==10 else 421;f.line([(x,129),(x+12,129)],c);f.text(x+16,131,lab,7.5)
f.finish('fig08_routed_margin_map')

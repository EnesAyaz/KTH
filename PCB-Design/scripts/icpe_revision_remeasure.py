from pathlib import Path
import sys,json,re,hashlib
import numpy as np
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'scripts'))
from icpe_gate_results import read_raw,window
from icpe_gate_loop_rerun import readlog
from icpe_gate_analysis import calculate,Rjh
A=ROOT/'reports/paper/icpe/revised_blue_2026-11-06';A.mkdir(exist_ok=True)
RUN=ROOT/'simulation/bb_spice/icpe_gate_loop_2026-11-02';T1=11.167e-6;T2=12.167e-6
allrows={};out={}
for g in [10,20]:
 for lp in [.5,1]:
  paths=[RUN/f'single_g{g}_p{lp:g}_on3_off1_biasminus1.cir']
  fine=RUN/f'single_g{g}_p{lp:g}_on3_off1_biasminus1_fine.cir'
  if fine.exists():paths.append(fine)
  rows={}
  for p in paths:
   currents=[float(x) for x in re.findall(r'^\.step ipk=([\d.eE+\-]+)',readlog(p.with_suffix('.log')),re.M)]
   runs=read_raw(p.with_suffix('.raw'));assert len(currents)==len(runs)
   for ip,z in zip(currents,runs):
    t=z['time'];vl=z['v(dl)']-z['v(sl)'];vh=z['v(dh)']-z['v(sw)'];il=z['i(vil)'];gh=z['v(gh)']-z['v(sw)'];ml=(t>=T1)&(t<T2);mh=(t>=T2)&(t<=T2+.5e-6)
    en={}
    for k,start,end in [('eon',T2,T2+150e-9),('eoff',T1,T2-1e-9)]:
     tt,yy=window(z,vl*il,start,end);en[k]=float(np.trapezoid(yy,tt))
    rows[ip]={'ipk':ip,'iload':float(np.interp(T1,t,il)),'vdsl_pk':float(vl[ml].max()),'vdsh_pk':float(vh[mh].max()),'vgsh_bump':float(gh[mh].max()),**en}
  key=f'g{g}_p{lp:g}';allrows[key]=sorted(rows.values(),key=lambda x:x['iload']);out[key]=[calculate(allrows[key],n) for n in range(2,9)]
(A/'single_and_sizing.json').write_text(json.dumps({'single':allrows,'parallel':out,'thermal_assumptions':{'junction_to_sink_K_per_W':Rjh,'shared_sink_to_ambient_K_per_W':.65,'ambient_C':40,'deadtime_ns':10,'gate_charge_nC':28,'gate_swing_V':6,'freewheel_capacitive_term_uJ':2.9,'switch_energy_model':'terminal Eon over150ns; terminal Eoff overcomplete1us offinterval'}},indent=2))
for k in ['g10_p0.5','g20_p0.5']:print(k,[{q:round(v[q],3) for q in ['n','tot','tj','vls','vhs']} for v in out[k] if v['n'] in [2,3,4]])
for key,val in allrows.items():print('LOW',key,val[0])
# Record the protected source files before authoring.
p=ROOT/'reports/paper/Submission-Final'
(A/'protected_sources.json').write_text(json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [p/'ICPE_Digest.pdf',p/'ICPE_Template.docx']},indent=2))

from pathlib import Path
import subprocess,sys,re,json,time
import numpy as np
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'scripts'))
from icpe_gate_results import read_raw,window
A=ROOT/'simulation/sharing/gate_10_20_2026-11-05';A.mkdir(exist_ok=True)
s=(ROOT/'simulation/sharing/paper_run/Sharing_paper.net').read_text(encoding='utf-8')
s=s.replace('.param LG1=2n LG2={if(CASE==2,8n,2n)}','.param LG1=10n LG2={if(CASE==2,20n,10n)}')
s=s.replace('.step param CASE list 0 1 2 3 4 5','.step param CASE list 0 1 2 3 4')
s=s.replace('.include ../../LMG1210-EPC2361/EPC2361.lib','.include "'+(ROOT/'simulation/LMG1210-EPC2361/EPC2361.lib').as_posix()+'"')
s=s.replace('.tran 0 {T2+TON2+0.5u} 0 0.1n','.tran 0 {T2+TON2+0.5u} {T1-200n} 0.1n')
s='\n'.join(l for l in s.splitlines() if not l.startswith('.meas') and not l.startswith('*'))
s='* Two parallel EPC2361; nominal gate loop 10 nH, mismatch 10/20 nH\n'+s
s=s.replace('.backanno','.save V(D1) V(S1) V(D2) V(S2) V(G1) V(G2) V(SW) V(DH) I(LD1) I(LD2) I(Lload)')
p=A/'sharing_10_20.cir';p.write_text(s)
lt=Path.home()/'AppData/Local/Programs/ADI/LTspice/LTspice.exe';start=time.time()
r=subprocess.run([str(lt),'-b','-Run',str(p)],capture_output=True,timeout=1200,cwd=A)
assert r.returncode==0,(r.returncode,r.stderr)
z=read_raw(p.with_suffix('.raw'));assert len(z)==5
T1=8.5e-6;T2=9.5e-6;rows=[]
for case,v in enumerate(z):
 t=v['time'];mask=(t>=T2)&(t<=T2+100e-9)
 peaks=[float(v['i(ld'+str(k)+')'][mask].max()) for k in [1,2]]
 row={'case':case,'gate_loops_nH':[10,20 if case==2 else 10],'peak_currents_A':peaks,'peak_current_imbalance_pct':100*abs(peaks[0]-peaks[1])/sum(peaks)}
 for k in [1,2]:
  power=(v[f'v(d{k})']-v[f'v(s{k})'])*v[f'i(ld{k})']
  for key,t0 in [('eon',T2),('eoff',T1)]:
   tt,pp=window(v,power,t0,t0+100e-9);row[f'{key}{k}_uJ']=float(np.trapezoid(pp,tt)*1e6)
 row['total_energy_imbalance_pct']=100*abs((row['eon1_uJ']+row['eoff1_uJ'])-(row['eon2_uJ']+row['eoff2_uJ']))/(row['eon1_uJ']+row['eoff1_uJ']+row['eon2_uJ']+row['eoff2_uJ'])
 rows.append(row)
(A/'results.json').write_text(json.dumps({'conditions':{'Vbus':75,'nominal_total_current_A':120,'Vgate':[0,5],'gate_resistors_ohm':[2,2],'max_step_ns':.1,'energy_window_ns':100},'cases':rows},indent=2))
print('Elapsed',round(time.time()-start,1),'s');print(json.dumps(rows,indent=2))

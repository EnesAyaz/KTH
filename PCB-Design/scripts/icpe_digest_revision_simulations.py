from pathlib import Path
import sys,re,json,subprocess,time
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'scripts'))
from icpe_gate_results import read_raw,window
from icpe_gate_loop_rerun import readlog
A=ROOT/'simulation/bb_spice/icpe_digest_revision_2026-11-06';A.mkdir(exist_ok=True)
LTS=Path.home()/'AppData/Local/Programs/ADI/LTspice/LTspice.exe'
T1=11.167e-6;T2=12.167e-6

def run_file(p):
 start=time.time();r=subprocess.run([str(LTS),'-b','-Run',str(p)],cwd=p.parent,capture_output=True,timeout=1800)
 assert r.returncode==0,(p,r.returncode,r.stderr)
 assert 'Total elapsed time' in readlog(p.with_suffix('.log'))
 print(p.stem,'finished',round(time.time()-start,1),'s',flush=True)
 return p

def sharing():
 old=ROOT/'simulation/sharing/gate_10_20_2026-11-05/sharing_10_20.cir';s=old.read_text()
 s=s.replace('LD2={if(CASE==1,0.45n,0.15n)}','LD2={if(CASE==1,0.25n,0.15n)}').replace('LG2={if(CASE==2,20n,10n)}','LG2={if(CASE==2,15n,10n)}').replace('LS2={if(CASE==4,0.25n,0.05n)}','LS2={if(CASE==4,0.10n,0.05n)}').replace('RG1=2 RG2=2','RG1=3 RG2=3')
 s=s.replace('nominal gate loop 10 nH, mismatch 10/20 nH','nominal gate loop 10 nH, mismatch 10/15 nH; RG=3 ohm')
 p=A/'sharing_final_conditions.cir';p.write_text(s);return p

def proto(g=20,ron=3,bias=-1,ip=328.2,vm=75,temp=27):
 name=f'prototype_g{g}_r{ron:g}_off{bias:g}_i{ip:g}_v{vm:g}_t{temp:g}'
 s=(ROOT/'simulation/bb_spice/icpe_gate_loop_2026-11-02/board_load_g20_on3_revised_drive.cir').read_text()
 s=re.sub(r'RGON=\S+',f'RGON={ron:g}',s);s=re.sub(r'IPK=\S+',f'IPK={ip:g}',s);s=re.sub(r'VBUS=\S+',f'VBUS={vm:g}',s)
 s=re.sub(r'LGO=\S+ LGK=\S+',f'LGO={g*.7:g}n LGK={g*.3:g}n',s)
 # All drive sources in this source have -1-V off commands.
 s=re.sub(r'^(VHO\w+\s+\S+\s+\S+) -1$',rf'\g<1> {bias:g}',s,flags=re.M)
 for namev in ['VLOA','VLOB']:
  lines=s.splitlines();s='\n'.join(l.replace(' -1 ',f' {bias:g} ').replace(' -1)',f' {bias:g})') if l.startswith(namev+' ') else l for l in lines)+'\n'
 s='\n'.join(l for l in s.splitlines() if not l.lower().startswith('.meas'))
 s=re.sub(r'^\.end\s*$',f'.temp {temp:g}\n.end',s,flags=re.M)
 p=A/(name+'.cir');p.write_text(s);return p

def summarize(p):
 runs=read_raw(p.with_suffix('.raw'))
 if p.stem.startswith('sharing'):
  out=[]
  for case,z in enumerate(runs):
   t=z['time'];m=(t>=9.5e-6)&(t<=9.6e-6);pk=[float(z[f'i(ld{k})'][m].max()) for k in [1,2]]
   out.append({'case':case,'peak_currents_A':pk,'imbalance_pct':100*abs(pk[0]-pk[1])/sum(pk)})
  val={'conditions':{'gate_resistors_ohm':3,'gate_loops_nominal_nH':[10,10],'gate_mismatch_nH':[10,15],'power_mismatch_nH':.1,'source_mismatch_nH':.05,'Vbus':75,'nominal_current_A':120},'cases':out}
 else:
  z=runs[0];t=z['time'];moff=(t>=T1)&(t<=T1+150e-9);mon=(t>=T2)&(t<=T2+150e-9);mall=t>=T1-100e-9
  branches=[]
  for k in range(1,5):
   vl=z[f'v(dl{k})']-z[f'v(ql_s_{k})'];vh=z[f'v(dh{k})']-z[f'v(qh_s_{k})'];gl=z[f'v(gl{k})']-z[f'v(ql_s_{k})'];gh=z[f'v(gh{k})']-z[f'v(qh_s_{k})'];il=z[f'i(vil{k})']
   b={'k':k,'vls_off':float(vl[moff].max()),'vhs_on':float(vh[mon].max()),'gate_bump':float(gh[mon].max()),'gate_min':float(min(gl[mall].min(),gh[mall].min())),'gate_max':float(max(gl[mall].max(),gh[mall].max())),'current_peak_on':float(il[mon].max()),'current_before_off':float(np.interp(T1-5e-9,t,il))}
   for tag,tc in [('eon',T2),('eoff',T1)]:
    tt,yy=window(z,vl*il,tc,tc+150e-9);b[tag+'_uJ']=float(np.trapezoid(yy,tt)*1e6)
   # 90-10% fall time uses the local low-side voltage, relative to bus parameter.
   vm=float(re.search(r'VBUS=([\d.]+)',p.read_text())[1]);ix=np.flatnonzero(mon);v=vl[ix];ts=t[ix]
   try:
    def crossing(th):
     j=np.flatnonzero(v<=th)[0]
     return ts[0] if j==0 else float(np.interp(th,[v[j],v[j-1]],[ts[j],ts[j-1]]))
    b['fall_90_10_ns']=(crossing(.1*vm)-crossing(.9*vm))*1e9
   except IndexError:b['fall_90_10_ns']=None
   branches.append(b)
  peaks=[b['current_peak_on'] for b in branches]
  val={'current_before_off_A':float(abs(np.interp(T1-5e-9,t,z['i(lload)']))),'current_before_on_A':float(abs(np.interp(T2-5e-9,t,z['i(lload)']))),'vds_peak':max(max(b['vls_off'],b['vhs_on']) for b in branches),'gate_bump':max(b['gate_bump'] for b in branches),'gate_min':min(b['gate_min'] for b in branches),'gate_max':max(b['gate_max'] for b in branches),'Eon_mean_uJ':sum(b['eon_uJ'] for b in branches)/4,'Eoff_mean_uJ':sum(b['eoff_uJ'] for b in branches)/4,'fall_mean_ns':sum(b['fall_90_10_ns'] or 0 for b in branches)/4,'peak_spread_pct':100*(max(peaks)-min(peaks))/(max(peaks)+min(peaks)),'branches':branches}
 p.with_suffix('.json').write_text(json.dumps(val,indent=2));return val

if __name__=='__main__':
 jobs=[sharing()]
 # Matched high-current gate-setting comparison and a positive-current range sweep.
 jobs += [proto(20,2,0),proto(20,3,0)]
 jobs += [proto(g,3,-1,ip) for g in [10,20] for ip in [1,40,80,160,240,328.2]]
 # Device-temperature and +5% bus sensitivities of the lower-inductance candidate.
 jobs += [proto(10,3,-1,328.2,75,125),proto(10,3,-1,328.2,78.75,27),proto(10,3,-1,328.2,78.75,125)]
 done={}
 with ThreadPoolExecutor(max_workers=2) as pool:
  pending={pool.submit(run_file,p):p for p in jobs if not p.with_suffix('.json').exists()}
  for fu in as_completed(pending):
   p=fu.result();v=summarize(p);done[p.stem]=v
   print('SUMMARY',p.stem, json.dumps(v if p.stem.startswith('sharing') else {k:v[k] for k in ['current_before_on_A','vds_peak','gate_bump','gate_min','Eon_mean_uJ','Eoff_mean_uJ','fall_mean_ns']}),flush=True)
 for p in jobs:
  if p.stem not in done:done[p.stem]=json.loads(p.with_suffix('.json').read_text())
 (A/'results.json').write_text(json.dumps(done,indent=2));print('ALL DONE',len(done),flush=True)

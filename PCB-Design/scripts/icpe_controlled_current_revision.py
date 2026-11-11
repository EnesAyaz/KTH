from pathlib import Path
import sys,re,json,time,subprocess
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'scripts'))
import icpe_digest_revision_simulations as old
old.T1=.7e-6;old.T2=1.7e-6
A=ROOT/'simulation/bb_spice/icpe_digest_revision_2026-11-06/controlled_current';A.mkdir(exist_ok=True)
BASE=(ROOT/'simulation/bb_spice/icpe_gate_loop_2026-11-02/board_load_g20_on3_revised_drive.cir').read_text()
LTS=old.LTS

def make(g=20,r=3,bias=-1,current=322.061,vm=75,temp=27,dt=.2):
 name=f'proto_g{g}_r{r:g}_off{bias:g}_i{current:g}_v{vm:g}_t{temp:g}_dt{dt:g}'
 s=BASE
 s=re.sub(r'RGON=\S+',f'RGON={r:g}',s);s=re.sub(r'IPK=\S+',f'IPK={current:g}',s);s=re.sub(r'VBUS=\S+',f'VBUS={vm:g}',s);s=re.sub(r'TON1=\S+','TON1=0.2u',s)
 s=re.sub(r'LGO=\S+ LGK=\S+',f'LGO={g*.7:g}n LGK={g*.3:g}n',s)
 s=re.sub(r'^(VHO\w+\s+\S+\s+\S+) -1$',rf'\g<1> {bias:g}',s,flags=re.M)
 s='\n'.join(l.replace(' -1 ',f' {bias:g} ').replace(' -1)',f' {bias:g})') if l.startswith(('VLOA ','VLOB ')) else l for l in s.splitlines())
 s=s.replace('Lload ACO BP {LLOAD} Rser=2m Cpar=20p','ILOAD BP ACO {IPK}\nCload ACO BP 20p')
 s=s.replace('I(Lload)','I(ILOAD)');s=re.sub(r'^\.meas.*$','',s,flags=re.M)
 s=s.replace('.tran 0 {TEND} {T1-200n} 0.1n',f'.tran 0 {{TEND}} {{T1-100n}} {dt:g}n')
 s=re.sub(r'^\.end\s*$',f'.temp {temp:g}\n.end',s,flags=re.M)
 # This is the same routed R/L network with controlled approximately inductive commutation current.
 p=A/(name+'.cir');p.write_text(s);return p

def measure(p):
 # The shared reader expects the original load-current variable name; alias it only in memory.
 raw=old.read_raw;z=raw(p.with_suffix('.raw'))[0];z['i(lload)']=z['i(iload)']
 orig=old.read_raw;old.read_raw=lambda path:[z]
 try:val=old.summarize(p)
 finally:old.read_raw=orig
 # Capture the complete off interval: low-current capacitance commutation may exceed 150 ns.
 for b in val['branches']:
  k=b['k'];vl=z[f'v(dl{k})']-z[f'v(ql_s_{k})'];vh=z[f'v(dh{k})']-z[f'v(qh_s_{k})'];t=z['time'];im=z[f'i(vil{k})']
  mo=(t>=old.T1)&(t<old.T2);mn=(t>=old.T2)&(t<=old.T2+.5e-6)
  b['vls_off']=float(vl[mo].max());b['vhs_on']=float(vh[mn].max())
  tt,pp=old.window(z,vl*im,old.T1,old.T2-1e-9);b['eoff_uJ']=float(old.np.trapezoid(pp,tt)*1e6)
 val['vds_peak']=max(max(b['vls_off'],b['vhs_on']) for b in val['branches'])
 val['Eoff_mean_uJ']=sum(b['eoff_uJ'] for b in val['branches'])/4
 val['setup']={'controlled_current_A':float(re.search(r'IPK=([\d.]+)',p.read_text())[1]),'gate_loop_nH':float(re.search(r'proto_g(\d+)',p.stem)[1]),'Rgon_ohm':float(re.search(r'_r([\d.]+)',p.stem)[1]),'Voff_V':float(re.search(r'_off(-?[\d.]+)',p.stem)[1]),'Vbus_V':float(re.search(r'_v([\d.]+)',p.stem)[1]),'Tj_C':float(re.search(r'_t([\d.]+)',p.stem)[1])}
 p.with_suffix('.json').write_text(json.dumps(val,indent=2));return val

def run(p):
 t=time.time();q=subprocess.run([str(LTS),'-b','-Run',str(p)],cwd=A,capture_output=True,timeout=1800)
 log=old.readlog(p.with_suffix('.log'));assert q.returncode==0 and 'Total elapsed time' in log and 'Unknown control card' not in log,(p,q.returncode,log[-1000:])
 # Return parsed data to the main thread; the common summarizer is not thread safe.
 print(p.stem,'finished',round(time.time()-t,1),'s',flush=True);return p

if __name__=='__main__':
 jobs=[make(20,3,-1,315.946,dt=.1)]
 jobs += [make(20,r,0) for r in [2,3]]
 jobs += [make(g,3,-1,i) for g in [10,20] for i in [1,40,80,160,240,322.061]]
 jobs += [make(10,3,-1,322.061,75,125),make(10,3,-1,322.061,78.75,27),make(10,3,-1,322.061,78.75,125)]
 done={}
 with ThreadPoolExecutor(max_workers=2) as pool:
  fs={pool.submit(run,p):p for p in jobs if not p.with_suffix('.json').exists()}
  for fu in as_completed(fs):
   p=fu.result();v=measure(p);done[p.stem]=v
   print('RESULT',p.stem, json.dumps({k:v[k] for k in ['vds_peak','gate_bump','gate_min','Eon_mean_uJ','Eoff_mean_uJ','fall_mean_ns','peak_spread_pct']}),flush=True)
 for p in jobs:
  if p.stem not in done:done[p.stem]=json.loads(p.with_suffix('.json').read_text())
 (A/'results.json').write_text(json.dumps(done,indent=2));print('ALL DONE',len(done),flush=True)

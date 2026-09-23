"""DUT-only discrete gate-resistance search; existing GUI is untouched."""
from pathlib import Path
import concurrent.futures,hashlib,json,csv,subprocess,time
import numpy as np
import dpt_gui as d
from datasheet_sweep import raw_read
ROOT=d.BASE/'dut_gate_search';ROOT.mkdir(exist_ok=True)
BASE=d.normalize_settings(json.loads((d.BASE/'DPT-75V-50A-candidate.json').read_text()))
BASE.update(Von='5',Voff='-4',AutoT1='0',Maxstep='500p')
CEILING=100.0
MODEL_HASH=hashlib.sha256((d.BASE/'EPCGaNLibrary.lib').read_bytes()).hexdigest()

def run(current,inductance,on,off,charge,step='500p',tag='search'):
 name=f'I{current}_L{inductance}_on{on:g}_off{off:g}_{step}_{tag}'
 folder=ROOT/'runs'/name;folder.mkdir(parents=True,exist_ok=True)
 values=dict(BASE,Itest=str(current),Icond=str(current),Lloop=f'{inductance}n',Rg_on=str(on),Rg_off=str(off),Tcharge=f'{charge:.12g}',Maxstep=step)
 path=folder/'result.json'
 if path.exists():
  old=json.loads(path.read_text())
  if old.get('values')==values and old.get('model_hash')==MODEL_HASH and old.get('status')=='ok':return old
 result=dict(name=name,target_A=current,L_nH=inductance,Ron=on,Roff=off,step=step,values=values,model_hash=MODEL_HASH,status='failed')
 started=time.monotonic()
 try:
  asc=d.export(values,folder/'DPT.asc');cir=asc.with_suffix('.cir')
  options='.options plotwinsize=0 method=gear reltol=1e-4 abstol=1e-9 vntol=1e-6 numdgt=7'
  for p in (asc,cir):p.write_text(p.read_text().replace('.options plotwinsize=0',options))
  proc=subprocess.run([d.find_ltspice(),'-b',str(cir)],cwd=folder,capture_output=True,timeout=300)
  if proc.returncode:raise RuntimeError(f'LTspice exit {proc.returncode}')
  w=raw_read(cir.with_suffix('.raw'));t=w['time'];v=w['V(drain)']-w['V(sl)'];p=d.validate(values);load=w['I(Lload)']
  result.update(status='ok',peak_V=float(v.max()),Ioff1_A=float(np.interp(p['A'],t,load)),Ion2_A=float(np.interp(p['B'],t,load)),Ioff2_A=float(np.interp(p['C'],t,load)),charge_s=charge)
  result['pass']=result['peak_V']<CEILING
  np.savez_compressed(folder/'waveforms.npz',time=t,vds=v,load=load,current=w['I(Vsense)'],vgs=w['V(gl)']-w['V(sl)'],A=p['A'],B=p['B'],C=p['C'])
 except Exception as exc:result.update(error=str(exc),**{'pass':False})
 result['elapsed_s']=round(time.monotonic()-started,2);path.write_text(json.dumps(result,indent=2));return result

def cell(current,inductance):
 # Calibrate first-turn-off current once, then keep pulse length fixed through the search.
 initial=current*20e-6/75
 cal=run(current,inductance,2,2,initial,tag='calibration')
 charge=initial*current/cal['Ioff1_A'] if cal['status']=='ok' and cal['Ioff1_A']>0 else initial
 tested=[];chosen=None;fine=None;finest=None
 # Integer lattice units are 0.5 ohm. Increasing sum gives an exhaustive lower-sum search.
 pairs=[(a*.5,(total-a)*.5) for total in range(2,49) for a in range(max(1,total-24),min(24,total-1)+1)]
 batch_size=6 if current==45 and inductance==5 else 1
 with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as batch_pool:
  for start in range(0,len(pairs),batch_size):
   batch=pairs[start:start+batch_size]
   nominal=list(batch_pool.map(lambda pair:run(current,inductance,pair[0],pair[1],charge),batch))
   tested.extend(nominal)
   for r in nominal:
    if r['pass']:
     f=run(current,inductance,r['Ron'],r['Roff'],charge,step='250p',tag='verification');tested.append(f)
     if f['pass']:
      ff=run(current,inductance,r['Ron'],r['Roff'],charge,step='125p',tag='additional_check');tested.append(ff)
      if ff['pass']:
       chosen=r;fine=f;finest=ff;break
   if chosen:break
   if batch_size>1:print('SCAN',current,inductance,'pairs',start+len(batch),'of',len(pairs),flush=True)
 if chosen:
  # Direct neighbours quantify sensitivity around the reported grid minimum.
  for ron,roff in [(chosen['Ron']+.5,chosen['Roff']),(chosen['Ron'],chosen['Roff']+.5)]:
   if max(ron,roff)<=12:tested.append(run(current,inductance,ron,roff,charge,tag='neighbour'))
 unresolved=sum(r['status']!='ok' for r in tested)
 result={'current_A':current,'L_nH':inductance,'charge_s':charge,'selected':chosen,'fine':fine,'finest':finest,'tested':tested,'unresolved_runs':unresolved}
 (ROOT/f'cell_I{current}_L{inductance}.json').write_text(json.dumps(result,indent=2))
 print('CELL',current,inductance,'selected',None if chosen is None else (chosen['Ron'],chosen['Roff'],finest['peak_V']), 'trials',len(tested),'unresolved',unresolved,flush=True)
 return result

if __name__=='__main__':
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  fs=[pool.submit(cell,i,l) for l in (1,3,5) for i in (15,30,45)]
  for f in concurrent.futures.as_completed(fs):
   results.append(f.result());(ROOT/'summary.json').write_text(json.dumps(results,indent=2))
 trials=[r for c in results for r in c['tested']]
 cols=['target_A','L_nH','Ron','Roff','step','status','pass','peak_V','Ioff1_A','Ion2_A','Ioff2_A','name','error']
 with (ROOT/'trials.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(trials)
 (ROOT/'provenance.json').write_text(json.dumps({'base':BASE,'ceiling_V':CEILING,'minimum_external_ohm':.5,'step_ohm':.5,'maximum_external_ohm':12,'objective':'minimum Ron+Roff, ties lower Ron; must pass at 500ps, 250ps and 125ps','model_sha256':MODEL_HASH,'gui_sha256':hashlib.sha256((d.BASE/'dpt_gui.py').read_bytes()).hexdigest(),'upper_Vds_in_constraint':False},indent=2))

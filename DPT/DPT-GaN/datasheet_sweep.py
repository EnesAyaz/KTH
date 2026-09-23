"""Reproducible DPT sweep. Does not modify the interactive GUI or EPC library."""
from pathlib import Path
import argparse, concurrent.futures, csv, hashlib, json, re, subprocess, time
import numpy as np
import dpt_gui as d
ROOT=d.BASE/'dpt_datasheet_75V'
BASE=d.normalize_settings(json.loads((d.BASE/'DPT-75V-50A-candidate.json').read_text()))
BASE.update(Von='5',Voff='-4',Rg_on='2',Rg_off='0.5',Lloop='1n',AutoT1='0',Maxstep='500p')

def raw_read(path):
 b=Path(path).read_bytes();mark='Binary:\n'.encode('utf-16-le');end=b.index(mark)
 h=b[:end].decode('utf-16-le');n=int(re.search(r'No. Variables:\s*(\d+)',h)[1]);count=int(re.search(r'No. Points:\s*(\d+)',h)[1])
 names=re.findall(r'^\s*\d+\s+(\S+)\s+\S+',h,re.M)
 payload=b[end+len(mark):]
 real_type='<f8' if len(payload)==count*n*8 else '<f4'
 dtype=np.dtype([('time','<f8'),('values',real_type,(n-1,))])
 data=np.frombuffer(b[end+len(mark):],dtype=dtype)
 if len(data)!=count:raise ValueError('Incomplete waveform')
 out={'time':data['time']}
 out.update({name:data['values'][:,i-1].astype(float) for i,name in enumerate(names) if i})
 return out

def run_case(spec,force=False):
 name,current,rgon,rgoff,inductance,step=spec
 folder=ROOT/'runs'/name;folder.mkdir(parents=True,exist_ok=True)
 result_path=folder/'result.json'
 values=dict(BASE,Itest=str(max(current,.001)),Icond=str(current),Rg_on=str(rgon),Rg_off=str(rgoff),Lloop=f'{inductance}n',Maxstep=step)
 values['Tcharge']=f'{max(current*20e-6/75,1e-6):.12g}'
 if current==0:values.update(Lload='1Meg',Tcharge='1u')
 if result_path.exists() and not force:
  cached=json.loads(result_path.read_text())
  if cached.get('status')=='ok' and cached.get('values')==values:return cached
 dest=d.export(values,folder/'DPT.asc');cir=dest.with_suffix('.cir')
 txt=cir.read_text().replace('.options plotwinsize=0','.options plotwinsize=0 method=gear reltol=1e-4 abstol=1e-9 vntol=1e-6 numdgt=7')
 # Save matched .asc solver settings too, for an executable reproduction.
 cir.write_text(txt);dest.write_text(dest.read_text().replace('.options plotwinsize=0','.options plotwinsize=0 method=gear reltol=1e-4 abstol=1e-9 vntol=1e-6 numdgt=7'))
 result=dict(name=name,target_A=current,rgon=rgon,rgoff=rgoff,L_nH=inductance,step=step,status='failed',values=values)
 started=time.monotonic()
 try:
  proc=subprocess.run([d.find_ltspice(),'-b',str(cir)],cwd=folder,capture_output=True,timeout=35)
  logbytes=cir.with_suffix('.log').read_bytes();log=logbytes.decode('utf-16-le' if b'\0' in logbytes[:100] else 'utf-8',errors='replace')
  if proc.returncode:raise RuntimeError(log[-1500:])
  m=d.parse_measurements(log)
  if 'eon2_window' not in m:raise RuntimeError('Missing switching measurements')
  w=raw_read(cir.with_suffix('.raw'));t=w['time'];p=d.validate(values)
  vds=w['V(drain)']-w['V(sl)'];vhs=w['V(rail)']-w['V(sh)'];vgs=w['V(gl)']-w['V(sl)'];vgh=w['V(gh)']-w['V(sh)'];power=vds*w['I(Vsense)']
  def energy(edge,post):
   start=edge-p['Wpre'];stop=edge+post
   tt=np.r_[start,t[(t>start)&(t<stop)],stop]
   return float(np.trapezoid(np.interp(tt,t,power),tt)*1e6)
  result.update(status='ok',measurements=m,Ioff_A=float(np.interp(p['A'],t,w['I(Lload)'])),Ion_A=float(np.interp(p['B'],t,w['I(Lload)'])),
   Eon_uJ=energy(p['B'],p['Wpost']),Eoff_uJ=energy(p['A'],p['Wpost']),
   Eon_200ns_uJ=energy(p['B'],200e-9),Eoff_200ns_uJ=energy(p['A'],200e-9),
   Vds_LS_peak=float(vds.max()),Vds_HS_peak=float(vhs.max()),Vgs_LS_min=float(vgs.min()),Vgs_LS_max=float(vgs.max()),Vgs_HS_min=float(vgh.min()),Vgs_HS_max=float(vgh.max()))
  result['flags']=[label for flag,label in [
   (max(vds.max(),vhs.max())>100,'Vds > 100 V'),(max(vds.max(),vhs.max())>120,'Vds > 120 V'),
   (min(vgs.min(),vgh.min())< -4.001,'Vgs < -4 V'),(max(vgs.max(),vgh.max())>6.001,'Vgs > 6 V'),
   (result['Eon_uJ']<0 or result['Eoff_uJ']<0,'negative signed energy')] if flag]
  np.savez_compressed(folder/'waveforms.npz',time=t,vds=vds,vhs=vhs,vgs=vgs,vgh=vgh,current=w['I(Vsense)'],load_current=w['I(Lload)'],power=power,cmd=w['V(cmd)'],A=p['A'],B=p['B'])
 except Exception as exc:result['error']=str(exc)
 result['elapsed_s']=round(time.monotonic()-started,2)
 result_path.write_text(json.dumps(result,indent=2));return result

def specs(full=False):
 combinations=[(2,.5,1),(2,.5,5),(5,2,1),(5,.5,1),(2,2.5,1)]
 if full:combinations=[(a,b,l) for a in (1,2,3,4,5) for b in (.5,1.1,2.5,5.2) for l in (1,2,3,4,5)]
 return [(f'on{a}_off{b}_L{l}_I{i}',i,a,b,l,'500p') for a,b,l in combinations for i in (0,10,20,30,40,50)]

def save_summary(results):
 ROOT.mkdir(exist_ok=True)
 (ROOT/'results.json').write_text(json.dumps(results,indent=2))
 columns=['name','status','target_A','Ion_A','Ioff_A','rgon','rgoff','L_nH','step','Eon_uJ','Eoff_uJ','Eon_200ns_uJ','Eoff_200ns_uJ','Vds_LS_peak','Vds_HS_peak','Vgs_LS_min','Vgs_LS_max','Vgs_HS_min','Vgs_HS_max','flags','error']
 with (ROOT/'results.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(results)
 (ROOT/'provenance.json').write_text(json.dumps({'base':BASE,'model_sha256':hashlib.sha256((d.BASE/'EPCGaNLibrary.lib').read_bytes()).hexdigest(),'gui_sha256':hashlib.sha256((d.BASE/'dpt_gui.py').read_bytes()).hexdigest(),'solver':'Gear, reltol=1e-4, abstol=1e-9, vntol=1e-6','energy':'signed integral from -20ns to +100ns relative to command edge; Eon pulse2, Eoff pulse1','no_load':'0 A nominal uses 1 MH to approximate an open load; actual simulated current retained'},indent=2))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--pilot',action='store_true');ap.add_argument('--full',action='store_true');ap.add_argument('--force',action='store_true');args=ap.parse_args()
 jobs=specs(args.full)
 if args.pilot:jobs=[jobs[0],jobs[1],jobs[5],('reference_250ps_50A',50,2,.5,1,'250p')]
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(run_case,s,args.force) for s in jobs]
  for f in concurrent.futures.as_completed(futures):
   r=f.result();results.append(r)
   print(len(results),'/',len(jobs),r['name'],r['status'],{k:round(r[k],4) for k in ['Ion_A','Eon_uJ','Eoff_uJ','Vds_HS_peak'] if k in r},flush=True)
   save_summary(results)

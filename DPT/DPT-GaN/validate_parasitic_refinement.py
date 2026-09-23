"""Bounded regression/validation: three simulations, no optimization sweep."""
from pathlib import Path
import importlib.util,json,hashlib,subprocess
import dpt_gui as d
import dpt_parasitics as par
from datasheet_sweep import raw_read
BASE=Path(__file__).resolve().parent;ROOT=BASE/'parasitic_refinement';ROOT.mkdir(exist_ok=True)

def main():
 original=json.loads((BASE/'DPT-75V-50A-candidate.json').read_text())
 spec=importlib.util.spec_from_file_location('legacy_gui',ROOT/'legacy/dpt_gui.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
 legacy=d.normalize_settings(original);assert legacy['Refined']=='0'
 assert d.circuit(legacy)[0]==old.circuit(old.normalize_settings(original))[0],'Legacy physical circuit changed'
 refined=dict(legacy,**par.NEW_DEFAULTS)
 p=d.validate(refined);assert abs(p['Lloop']*(p['LplusFrac']+p['LreturnFrac']+1-p['LplusFrac']-p['LreturnFrac'])-p['Lloop'])<1e-20
 for bad in [dict(refined,LplusFrac='.8',LreturnFrac='.3'),dict(refined,RgTraceLS='-1m'),dict(refined,Refined='2')]:
  try:d.validate(bad)
  except ValueError:pass
  else:raise AssertionError('Invalid parasitics accepted')
 parts,_,_=d.circuit(refined);nodes={r[1]:r[2] for r in parts}
 assert nodes['Lsl']==['sl','pgnd'] and nodes['Lsh']==['sh','hs_ref']
 assert nodes['Von']==['on','lret'] and nodes['Vhs']==['offhs','hret']
 assert nodes['LgateReturnHS']==['hret','hs_ref'] and nodes['LgateReturnLS']==['lret','pgnd']
 assert d.schematic(refined).count('SYMBOL ')==len(parts),'Schematic lost components'
 assert d.normalize_settings(refined)==refined
 gui=d.App();gui.withdraw();gui.update_idletasks()
 for key in par.NEW_DEFAULTS:assert key in gui.vars
 for key,value in legacy.items():gui.vars[key].set(value)
 gui.apply_parasitics();assert gui.values()['Refined']=='1' and gui.values()['Vin']==original['Vin']
 gui.update_idletasks();gui.destroy()
 print('Regression checks passed: legacy topology, settings, reference nodes, validation, schematic completeness and GUI controls.',flush=True)
 cases={'legacy':legacy,'refined':refined,'refined_local_cap':dict(refined,Cdecap='4.7u')}
 results=[]
 for label,values in cases.items():
  folder=ROOT/'validation'/label
  previous=(folder/'DPT.cir').read_text(encoding='utf-8') if (folder/'DPT.cir').exists() else None
  dest=d.export(values,folder/'DPT.asc')
  # A fixed documented solver is used only for this validation, not to hide ringing.
  for ext in ('.asc','.cir'):
   q=dest.with_suffix(ext);q.write_text(q.read_text().replace('.options plotwinsize=0','.options plotwinsize=0 method=gear reltol=1e-4 abstol=1e-9 vntol=1e-6 numdgt=7'))
  if previous!=dest.with_suffix('.cir').read_text(encoding='utf-8') or not dest.with_suffix('.raw').exists():
   subprocess.run([d.find_ltspice(),'-b',str(dest.with_suffix('.cir'))],cwd=folder,check=True,timeout=120,capture_output=True)
  log=dest.with_suffix('.log').read_bytes();txt=log.decode('utf-16-le' if b'\0' in log[:100] else 'utf-8',errors='replace');m=d.parse_measurements(txt)
  for key in ('vds_peak','vds_hs_peak','vgs_ls_peak','vgs_ls_min','vgs_hs_peak','vgs_hs_min','eon2_window','eoff1_window'):assert key in m,(label,key)
  w=raw_read(dest.with_suffix('.raw'));assert w['time'][-1]>=d.validate(values)['Stop']-1e-12
  if label!='legacy':
   for key in ('I(Llayout)','I(Lmid)','I(Lreturn)','I(LgateLS)','I(LgateHS)','V(pgnd)'):assert key.lower() in {k.lower() for k in w},(label,key)
  results.append(dict(case=label,measurements=m,settings=values,completed_time_s=float(w['time'][-1])))
  print(label,{k:round(m[k],3) for k in ('vds_peak','vds_hs_peak','vgs_ls_peak','vgs_ls_min','vgs_hs_peak','vgs_hs_min')},flush=True)
 # Verify that the generated symbol schematic also produces all circuit elements.
 asc=ROOT/'validation/refined/DPT.asc'
 subprocess.run([d.find_ltspice(),'-netlist',str(asc)],cwd=asc.parent,check=True,timeout=30,capture_output=True)
 net=asc.with_suffix('.net').read_bytes();txt=net.decode('utf-16-le' if b'\0' in net[:100] else 'utf-8',errors='replace')
 for kind,name,_,_,_ in parts:
  names={name.lower()}|({'x'+name.lower()} if kind=='EPCGaN' else set())
  assert any(line.split()[0].lower() in names for line in txt.splitlines() if line.strip()),name
 (ROOT/'validation/results.json').write_text(json.dumps({'physical_legacy_compatibility':True,'GUI_controls_checked':True,'schematic_netlisting_checked':True,'model_sha256':hashlib.sha256((BASE/'EPCGaNLibrary.lib').read_bytes()).hexdigest(),'cases':results},indent=2))
 print('PASS: three complete 75 V / 50 A-preset simulations. This is model validation, not voltage qualification.',flush=True)
if __name__=='__main__':main()

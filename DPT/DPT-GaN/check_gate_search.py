from pathlib import Path
import json,hashlib
import numpy as np
import dpt_gui as d
ROOT=d.BASE/'dut_gate_search'

def check():
 cells=json.loads((ROOT/'summary.json').read_text());assert len(cells)==9
 for c in cells:
  selected=c['selected']
  checks={(round(2*r['Ron']),round(2*r['Roff']),r['step']):r for r in c['tested'] if not r['name'].endswith('_neighbour')}
  if selected:
   assert all(c[k]['status']=='ok' and c[k]['peak_V']<100 for k in ('selected','fine','finest'))
   for k in ('selected','fine','finest'):
    r=c[k];w=np.load(ROOT/'runs'/r['name']/'waveforms.npz')
    assert w['time'][-1]>=d.validate(r['values'])['Stop']-1e-12,'Incomplete simulation'
    assert abs(float(w['vds'].max())-r['peak_V'])<1e-8
   total=round(2*(selected['Ron']+selected['Roff']));on_selected=round(2*selected['Ron'])
  else:
   total=48;on_selected=25
  for sm in range(2,total+1):
   for a in range(max(1,sm-24),min(24,sm-1)+1):
    if selected and sm==total and a>=on_selected:continue
    b=sm-a;r=checks[a,b,'500p']
    if selected:assert r['status']=='ok','Unresolved lower-ranked pair'
    if r['pass']:
     f=checks[a,b,'250p']
     if selected:assert f['status']=='ok'
     if f['pass']:
      ff=checks[a,b,'125p']
      if selected:assert ff['status']=='ok'
      assert not ff['pass']
  if not selected:assert len([r for key,r in checks.items() if key[2]=='500p'])==576
 prov=json.loads((ROOT/'provenance.json').read_text())
 assert prov['gui_sha256']==hashlib.sha256((d.BASE/'dpt_gui.py').read_bytes()).hexdigest()
 report={'verified_cells':sum(bool(c['selected']) for c in cells),'no_verified_pair_cells':sum(not c['selected'] for c in cells),'unresolved_runs':sum(c['unresolved_runs'] for c in cells),'predicate':'DUT peak <100 V at 500, 250 and 125 ps','lower_ranked_pairs_checked':True,'GUI_unchanged':True,'upper_device_constraint':False}
 (ROOT/'qa.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':check()

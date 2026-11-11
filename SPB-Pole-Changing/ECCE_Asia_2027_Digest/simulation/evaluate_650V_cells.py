"""Explicit 650-V cell-count voltage/winding screen under stated margins."""
from pathlib import Path
import ast,json,math,csv,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'simulation/vendor'))
import numpy as np
tree=ast.parse((ROOT/'simulation/run_design_selection.py').read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='candidate')
exec(compile(ast.Module(body=[node],type_ignores=[]),'winding_candidate','exec'))
cases=[]
for N,Q in [(2,36),(3,54),(4,36)]:
 stress=1320*1.1*1.1/N;w=candidate(Q,N,12,6,True);assert w['supported']
 cases.append({'device_rating_V':650,'N':N,'nominal_cell_V':1200/N,'stress_estimate_V':stress,'chosen_allowance_V':520,'below_continuous_rating':stress<=650,'meets_chosen_allowance':stress<=520,'Q':Q,'winding_factors':[w['kwH'],w['kwL']],'other_selected_order_residual':w['mode_leakage_max']})
assert [x['meets_chosen_allowance'] for x in cases]==[False,False,True]
assert [round(x['stress_estimate_V'],1) for x in cases]==[798.6,532.4,399.3]
out=ROOT/'simulation/results_selection'
(out/'650V_cell_count_screen.json').write_text(json.dumps({'source':'Infineon IGLT65R025D2 rev1.1, 2026-03-03','device_Rmax_mohm_25C':30,'assumptions':'1200V nominal,1320V maximum,1.10 imbalance,1.10 overshoot,0.80 rating utilization','cases':cases,'scope':'Chosen voltage and selected-order winding constraints only; not electrothermal validation','three_cell_note':'Below continuous rating but fails this chosen allowance; could be reconsidered with justified different margins or bus envelope'},indent=2))
w=candidate(36,4,12,6,True);rows=[]
for j,g in enumerate(w['groups']):
 for ph,leg in enumerate(g):
  for k,s in enumerate(leg):rows.append({'cell':j+1,'phase':'ABC'[ph],'series_index':k+1,'start_slot':s+1,'return_slot':(s+w['y'])%36+1,'connection_sign':1})
with (out/'winding_4cells_36slots_12_6poles.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=rows[0]);wr.writeheader();wr.writerows(rows)
assert len(rows)==36
for p in [3,6]:
 # Independent direct coil-side sum for the documented four-cell series groups.
 coeff=0j;other=6 if p==3 else 3;leak=[0j,0j]
 for row in rows:
  theta=2*np.pi*(row['start_slot']-1)/36;ret=2*np.pi*(row['return_slot']-1)/36;current=np.exp(1j*p*theta)
  coeff+=current*(np.exp(-1j*p*theta)-np.exp(-1j*p*ret))/72
  for k,n in enumerate([other,-other]):leak[k]+=current*(np.exp(-1j*n*theta)-np.exp(-1j*n*ret))/72
 assert abs(abs(coeff)-np.sqrt(3)/2)<1e-12
 assert max(abs(z) for z in leak)/abs(coeff)<1e-12
print(json.dumps(cases,indent=2))

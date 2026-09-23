"""Measured 10-90% terminal switching slopes from saved DPT waveforms."""
from pathlib import Path
import json,csv
import numpy as np
BASE=Path(__file__).resolve().parent;ROOT=BASE/'dut_gate_search'

def crossings(t,y,level,start,stop,direction):
 idx=np.flatnonzero((t[:-1]>=start)&(t[1:]<=stop)&(((y[:-1]<level)&(y[1:]>=level)) if direction>0 else ((y[:-1]>level)&(y[1:]<=level))))
 return t[idx]+(level-y[idx])*(t[idx+1]-t[idx])/(y[idx+1]-y[idx])

def interval(t,y,a,b,edge):
 sign=1 if b>a else -1
 starts=crossings(t,y,a,edge,edge+200e-9,sign)
 ends=crossings(t,y,b,edge,edge+200e-9,sign)
 for end in ends:
  before=starts[starts<end]
  if len(before):
   start=float(before[-1]);end=float(end)
   return dict(start_s=start,end_s=end,start_level=a,end_level=b,duration_ns=(end-start)*1e9,slope_per_ns=(b-a)/(end-start)*1e-9)
 raise ValueError('No complete directed transition in 200 ns window')

def extract():
 rows=[];records=[]
 for c in sorted(json.loads((ROOT/'summary.json').read_text()),key=lambda c:(c['L_nH'],c['current_A'])):
  if not c['selected']:continue
  r=c['finest'];w=np.load(ROOT/'runs'/r['name']/'waveforms.npz');t=w['time'];v=w['vds'];i=w['current']
  rec=dict(L_nH=c['L_nH'],target_A=c['current_A'],Ron=r['Ron'],Roff=r['Roff'],run=r['name'],events={})
  for event,key,on in [('on2','B',True),('off1','A',False),('off2','C',False)]:
   edge=float(w[key]);iref=float(np.interp(edge,t,w['load']));vref=float(r['values']['Vin'])
   vi=interval(t,v,(.9 if on else .1)*vref,(.1 if on else .9)*vref,edge)
   ii=interval(t,i,(.1 if on else .9)*iref,(.9 if on else .1)*iref,edge)
   rec['events'][event]=dict(edge_s=edge,Iref_A=iref,voltage=vi,current=ii)
   rows.append(dict(L_nH=c['L_nH'],target_A=c['current_A'],Ron_ohm=r['Ron'],Roff_ohm=r['Roff'],event=event,Iref_A=iref,dv_dt_V_per_ns=vi['slope_per_ns'],di_dt_A_per_ns=ii['slope_per_ns'],voltage_transition_ns=vi['duration_ns'],current_transition_ns=ii['duration_ns'],voltage_crossing_start_ns=(vi['start_s']-edge)*1e9,voltage_crossing_end_ns=(vi['end_s']-edge)*1e9,current_crossing_start_ns=(ii['start_s']-edge)*1e9,current_crossing_end_ns=(ii['end_s']-edge)*1e9,run=r['name']))
  records.append(rec)
 (ROOT/'switching_rates.json').write_text(json.dumps(records,indent=2))
 with (ROOT/'switching_rates.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 for r in records:print(r['L_nH'],r['target_A'],{e:(round(x['voltage']['slope_per_ns'],2),round(x['current']['slope_per_ns'],2)) for e,x in r['events'].items()})
 return records
if __name__=='__main__':extract()

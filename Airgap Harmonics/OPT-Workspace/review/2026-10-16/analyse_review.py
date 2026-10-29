from pathlib import Path
import numpy as np,json
P=Path(__file__).parent
def raw(path):
 b=path.read_bytes(); mark='Binary:\n'.encode('utf-16le'); idx=b.index(mark)+len(mark); h=b[:idx].decode('utf-16le'); n=int(h.split('No. Variables:')[1].splitlines()[0]); names=[x.split()[1] for x in h.split('Variables:\n')[1].split('Binary:')[0].splitlines() if x.strip()]; dt=np.dtype([('time','<f8'),('data','<f4',(n-1,))]); a=np.frombuffer(b[idx:],dtype=dt); return {names[0]:a['time'],**{name:a['data'][:,i] for i,name in enumerate(names[1:])}}
def cross(t,x,level):
 ids=np.where((t[:-1]>=.5)&((x[:-1]-level)*(x[1:]-level)<=0))[0]
 if not len(ids): return None
 k=ids[0]; return float((t[k]+(level-x[k])*(t[k+1]-t[k])/(x[k+1]-x[k])-.5)*1000)
res={}
for case in ['reversal','reversal_fine','reference','deexcitation','shaded_one','reversal_clamp37','reversal_clamp40']:
 d=raw(P/(case+'.raw')); print(case,list(d)); t=d['time']; i=d['I(Lf)']; v=d['V(a)']; m=t>=.5
 r={'initial_current_A':float(i[0]),'final_current_A':float(i[-1]),'initial_voltage_V':float(v[0]),'final_voltage_V':float(v[-1]),'peak_absolute_voltage_V':float(abs(v[m]).max()),'zero_crossing_ms':cross(t,i,0),'decay_to_5percent_ms':cross(t,i,.05*i[0]),'reversal_to_minus_95percent_initial_ms':cross(t,i,-.95*i[0])}
 if 'I(Dbp1)' in d:
  power=d['I(Dbp1)']*(-v)
  r.update(positive_group_one_branch_peak_W=float(power[m].max()),positive_group_six_branches_energy_J=float(6*np.trapezoid(power[m],t[m])),positive_group_one_branch_peak_current_A=float(d['I(Dbp1)'][m].max()))
 if case=='shaded_one': r['shaded_device_final_absorbed_W']=float(-v[-1]*d['I(Rsp1)'][-1])
 res[case]=r
(P/'results.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))

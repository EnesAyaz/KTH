"""Design selection from discrete GaN classes, coil budget and balanced cells.
Constructive screen only: no general impossibility claims for other windings.
"""
from pathlib import Path
import sys,math,json,csv
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(HERE/'vendor'))
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch
OUT=HERE/'results_selection';OUT.mkdir(exist_ok=True)
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'legend.fontsize':8,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':260})
Vnom,Vbusmax,kimb,kov,u=1200.,1320.,1.10,1.10,.80
classes=[{'rating_V':100,'part':'EPC2361','Rmax_mohm_25C':1.,'Rtyp_mohm_25C':.75,'source':'EPC2361.pdf','static_page':1}, {'rating_V':150,'part':'EPC2305','Rmax_mohm_25C':3.,'Rtyp_mohm_25C':2.2,'source':'EPC2305.pdf','static_page':2}, {'rating_V':200,'part':'EPC2304','Rmax_mohm_25C':5.,'Rtyp_mohm_25C':3.5,'source':'EPC2304.pdf','static_page':1}, {'rating_V':350,'part':'EPC2050','Rmax_mohm_25C':80.,'Rtyp_mohm_25C':55.,'source':'EPC2050.pdf','static_page':1}]
for d in classes:
 d.update(N_voltage_min=math.ceil(Vbusmax*kimb*kov/(u*d['rating_V'])))
 d['coil_min_double_layer']=3*d['N_voltage_min'];d['slot_min_single_layer']=6*d['N_voltage_min'];d['N_R_screen_mohm']=d['N_voltage_min']*d['Rmax_mohm_25C']
Qs=list(range(18,97,6));pairs=[(8,4),(12,6),(16,8),(24,12),(32,16),(12,4),(24,8),(10,4),(20,8)]

def candidate(Q,N,PH,PL,include_groups=False):
 pH,pL=PH//2,PL//2;g=math.gcd(pH,pL);a,b=pH//g,pL//g
 reason=None
 if a%3==0 or b%3==0:reason='Uniform triples fail: a reduced spatial order is zero sequence'
 elif Q%(3*N):reason='Noninteger equal coil count per phase branch'
 elif Q%(3*g):reason='Uniform phase-axis spacing does not land on the slot grid'
 if reason:return {'supported':False,'reason':reason}
 c=Q//(3*N);s=Q//(3*g)
 # g repeating identical sector triples per q, grouped in equal blocks.
 primitive=[(q,sector) for q in range(s) for sector in range(g)]
 if len(primitive)!=Q//3:raise AssertionError
 groups=[]
 for j in range(N):
  picked=primitive[j*c:(j+1)*c]
  groups.append([[sector*3*s+q+ph*s for q,sector in picked] for ph in range(3)])
 assert sorted(k for group in groups for leg in group for k in leg)==list(range(Q))
 th=2*np.pi*np.arange(Q)/Q
 gain={};leak={};kd={}
 currents={}
 for p in [pH,pL]:
  voltages=np.array([[np.sum(np.exp(1j*p*th[leg])) for leg in group] for group in groups])
  if np.max(abs(voltages.sum(axis=1)))>1e-8:raise AssertionError('unbalanced phase phasors')
  if np.max(np.ptp(abs(voltages),axis=1))>1e-8:raise AssertionError('phase amplitudes differ')
  gain[p]=abs(voltages[:,0])/c
  if min(gain[p])<1e-8:return {'supported':False,'reason':'Zero induced voltage in a selected order'}
  # Keep the demonstrated family exactly equal-loaded across cells for equal current.
  if np.ptp(gain[p])>1e-8:return {'supported':False,'reason':'Unequal cell modal gain; separate balancing/current optimization required'}
  ip=np.zeros(Q,dtype=complex)
  for j,group in enumerate(groups):
   for ph,leg in enumerate(group):ip[leg]=np.exp(1j*np.angle(voltages[j,ph]))
  currents[p]=ip
  target=abs(np.sum(ip*np.exp(-1j*p*th)))
  other=pL if p==pH else pH
  leak[p]=max(abs(np.sum(ip*np.exp(-1j*other*th))),abs(np.sum(ip*np.exp(1j*other*th))))/target
  kd[p]=float(gain[p].mean())
 # Per-cell balancing is not enough: reject inability to select only one target pole order.
 if max(leak.values())>1e-8:return {'supported':False,'reason':'One selected pole order cannot be suppressed independently','cross_mode_leakage':{str(k):float(v) for k,v in leak.items()}}
 ys=np.arange(1,Q//2+1);kwH=kd[pH]*abs(np.sin(np.pi*pH*ys/Q));kwL=kd[pL]*abs(np.sin(np.pi*pL*ys/Q));score=np.minimum(kwH,kwL)
 j=int(np.flatnonzero(score>=score.max()-1e-10)[0]);y=int(ys[j]);short=ys<=1.5*Q/PH
 jj=int(np.argmax(np.where(short,score,-1))) if short.any() else None
 rec={'supported':True,'Q':Q,'N':N,'PH':PH,'PL':PL,'pH':pH,'pL':pL,'ratio':PH/PL,'c':c,'gcd_orders':g,'a':a,'b':b,'phase_axis_step_slots':s,'y':y,'kwH':float(kwH[j]),'kwL':float(kwL[j]),'min_kw':float(score[j]),'kdH':kd[pH],'kdL':kd[pL],'pitch_in_high_pole_pitches':float(y/(Q/PH)),'short_y':int(ys[jj]) if jj is not None else None,'short_min_kw':float(score[jj]) if jj is not None else None,'mode_leakage_max':float(max(leak.values()))}
 if include_groups:rec['groups']=groups
 return rec

records=[];alltests=[]
for PH,PL in pairs:
 for Q in Qs:
  for N in range(1,33):
   r=candidate(Q,N,PH,PL)
   alltests.append({'PH':PH,'PL':PL,'Q':Q,'N':N,**{k:v for k,v in r.items() if k not in ['groups']}})
   if r['supported']:records.append(r)
# Smallest controlled example for requested 12/6 with practical 36 slots.
control=candidate(36,2,12,6,True);assert control['supported']
no_single=candidate(36,1,12,6);assert not no_single['supported']
selected=[]
for PH,PL in pairs:
 for d in classes:
  for cap in [60,72,96]:
   options=[r for r in records if r['PH']==PH and r['PL']==PL and r['N']>=d['N_voltage_min'] and r['Q']<=cap]
   # A transparent shortlist rule, not a motor-efficiency optimum: first N, then Q.
   best=min(options,key=lambda x:(x['N'],x['Q'],-x['min_kw'])) if options else None
   selected.append({'PH':PH,'PL':PL,'rating_V':d['rating_V'],'slot_cap':cap,'candidate':best})
# Explicit export for 200 V / 12 cells / 36 slots, now an outcome of the screen.
W=candidate(36,12,12,6,True);assert W['supported']
rows=[]
for j,group in enumerate(W['groups']):
 for ph,leg in enumerate(group):
  for ii,k in enumerate(leg):rows.append({'cell':j+1,'phase':'ABC'[ph],'series_index':ii+1,'start_slot':k+1,'return_slot':(k+W['y'])%36+1,'connection_sign':1,'angle_12pole_deg':round((6*360*k/36)%360,8),'angle_6pole_deg':round((3*360*k/36)%360,8)})
with (OUT/'winding_12cells_36slots_12_6poles.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=rows[0]);wr.writeheader();wr.writerows(rows)
# Also retain 2-cell control proof, independent of semiconductor voltage.
controlrows=[]
for j,group in enumerate(control['groups']):
 for ph,leg in enumerate(group):
  for ii,k in enumerate(leg):controlrows.append({'cell':j+1,'phase':'ABC'[ph],'series_index':ii+1,'start_slot':k+1,'return_slot':(k+control['y'])%36+1})
with (OUT/'winding_2cell_control_example_36slots_12_6poles.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=controlrows[0]);wr.writeheader();wr.writerows(controlrows)
# Figure 1: constraint flow, degrees of freedom and source-grounded slot range.
fig=plt.figure(figsize=(6.3,2.7));ax=fig.add_axes([0,0,1,1]);ax.axis('off');ax.set_xlim(0,10);ax.set_ylim(0,4)
boxes=[(.15,2.3,2.8,1.25,'Discrete device rating\n100 / 150 / 200 / 350 V'),(3.6,2.3,2.8,1.25,'Voltage margin\nminimum N'),(7,2.3,2.8,1.25,'Winding capacity\n3N branches ≤ C')]
for x,y,w,h,label in boxes:
 ax.add_patch(Rectangle((x,y),w,h,facecolor='#e7eef6',edgecolor='#315574'));ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=10)
for x1,x2 in [(3,3.55),(6.45,6.95)]:ax.annotate('',(x2,2.92),(x1,2.92),arrowprops={'arrowstyle':'->','color':'black'})
ax.add_patch(Rectangle((1.2,.35),7.6,1.15,facecolor='#f1f1f1',edgecolor='gray'));ax.text(5,.93,'Balanced A B C in every cell at BOTH pole counts\nThen check pitch, harmonics, rotor compatibility and losses',ha='center',va='center',fontsize=10)
ax.annotate('',(8.4,1.6),(8.4,2.25),arrowprops={'arrowstyle':'->'});ax.annotate('',(2.6,1.6),(2.6,2.25),arrowprops={'arrowstyle':'->'})
fig.savefig(FIG/'fig_selection_workflow.png',bbox_inches='tight');fig.savefig(FIG/'fig_selection_workflow.svg',bbox_inches='tight');plt.close(fig)
# Figure 2: exact shortlisted counts at Q<=60, and sensitivity allowing Q<=72.
fig,axes=plt.subplots(1,2,figsize=(6.3,2.65))
showpairs=[(8,4),(12,6),(10,4),(12,4)];ratings=[d['rating_V'] for d in classes]
for ax,cap in zip(axes,[60,72]):
 mat=np.zeros((4,4));labels={}
 for ri,(PH,PL) in enumerate(showpairs):
  for ci,v in enumerate(ratings):
   sel=next(s for s in selected if s['PH']==PH and s['PL']==PL and s['rating_V']==v and s['slot_cap']==cap)['candidate']
   mat[ri,ci]=sel['N'] if sel else 0;labels[(ri,ci)]=f"{sel['N']} / {sel['Q']}" if sel else '—'
 ax.imshow(mat,cmap='Blues',vmin=0,vmax=24,aspect='auto')
 for ri in range(4):
  for ci in range(4):ax.text(ci,ri,labels[(ri,ci)],ha='center',va='center',fontsize=8,color='white' if mat[ri,ci]>=19 else 'black')
 ax.set_xticks(range(4),ratings);ax.set_yticks(range(4),[f'{h}/{l}' for h,l in showpairs]);ax.set_xlabel('Device rating (V)');ax.set_title(f'Q ≤ {cap} slots',fontsize=10)
axes[0].set_ylabel('Total pole combination')
fig.suptitle('Entries are N / Q; dash means outside this winding screen',fontsize=10);fig.tight_layout();fig.savefig(FIG/'fig_device_slot_shortlist.png');fig.savefig(FIG/'fig_device_slot_shortlist.svg');plt.close(fig)
# Figure 3: coil-pitch cost, separated from module balance.
fig,ax=plt.subplots(figsize=(6.3,2.6));rho=np.linspace(0,3,1201)
# rho=y/(high-pole pitch); low-order electrical half-angle is pi*rho/(2r).
for r,label,col in [(2,'2:1','#164e7c'),(3,'3:1 pitch only','#888888'),(2.5,'5:2','#b15e1a')]:
 score=np.minimum(abs(np.sin(np.pi*rho/2)),abs(np.sin(np.pi*rho/(2*r))))
 ax.plot(rho,score,label=label,lw=1.8,color=col,ls='--' if r==3 else '-')
ax.axvline(1.5,color='#999999',ls=':',lw=1);ax.text(1.52,.12,'Short-span screen',fontsize=8,color='#666666');ax.set(xlabel='Coil span / high-pole pitch',ylabel='Minimum pitch factor',xlim=(0,3),ylim=(0,1.04));ax.legend(loc='upper left',framealpha=.9);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(FIG/'fig_ratio_pitch.png');fig.savefig(FIG/'fig_ratio_pitch.svg');plt.close(fig)
# The old 24-cell dq curves are terminal-equivalent scaled to the new 12-cell
# illustration; no new geometry optimization is implied by this change of basis.
old=json.loads((HERE/'results_three_phase/three_phase_codesign.json').read_text())
scaled={'N':12,'Q':36,'assumption':'terminal-equivalent scaling from the earlier illustrative model; not identified geometry','V_phase_peak_V':old['inputs']['V_phase_peak_limit_V']*2,'I_peak_A':old['inputs']['I_peak_A'],'phase_R_ohm':old['inputs']['phase_R_ohm']*2,'models':[{**m,'psi_Wb':m['psi_Wb']*2,'Ld_H':m['Ld_H']*2,'Lq_H':m['Lq_H']*2} for m in old['models']],'curves':old['curves'],'metrics':old['metrics']}
# Plot concise diagnostic: same curves, chosen after the winding/device screen.
fig,axes=plt.subplots(2,1,figsize=(6.3,3.0),sharex=True)
for name,col,ls in [('IPMSM 12 poles','#555555','--'),('HEPM selectable 12 or 6','#164e7c','-'),('IPMSM stronger FW','#2d7b48','-.')]:
 curve=scaled['curves'][name];rpm=[x['rpm'] for x in curve];axes[0].plot(rpm,[x['torque_Nm'] for x in curve],color=col,ls=ls,lw=1.6,label=name);axes[1].plot(rpm,[x['power_kW'] for x in curve],color=col,ls=ls,lw=1.6)
axes[0].set_ylabel('Torque (N m)');axes[1].set_ylabel('Power (kW)');axes[1].set_xlabel('Mechanical speed (rpm)');axes[0].legend(loc='upper right',framealpha=.95)
for ax in axes:ax.set_xlim(0,9000);ax.set_ylim(bottom=0);ax.grid(alpha=.2)
fig.tight_layout();fig.savefig(FIG/'fig_selected_diagnostic_envelope.png');fig.savefig(FIG/'fig_selected_diagnostic_envelope.svg');plt.close(fig)
meta={'scope':'Discrete device classes intersected with fixed slot budgets and three-wire balanced winding constraints','parameters':{'Vdc_nom_V':Vnom,'Vdc_max_V':Vbusmax,'imbalance':kimb,'overshoot':kov,'rating_utilization':u,'slot_set':Qs,'N_range':[1,32],'primary_slot_cap':60,'sensitivity_slot_cap':72,'winding_layer':'double layer Q coils; single-layer capacity bound separately'},'device_classes':classes,'records':records,'shortlists':selected,'two_cell_control_example':{k:v for k,v in control.items() if k!='groups'},'one_cell_rejection':no_single,'illustrative_selected_winding':{k:v for k,v in W.items() if k!='groups'},'illustrative_terminal_model':scaled,'limits':['Sufficient uniform-triple family with exact equal modal gain across cells','Rejection is not a universal impossibility theorem','3:1 not demonstrated in this family; different multi-coil layouts remain open','Pitch factors do not establish loss, torque or rotor feasibility','Device resistance screen is part-specific at 25 C, not a full thermal or switching loss calculation','No global optimal device or cell count is claimed']}
(OUT/'design_selection.json').write_text(json.dumps(meta,indent=2))
with (OUT/'feasible_windings.csv').open('w',newline='') as f:
 keys=sorted({k for r in records for k in r});wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows(records)
with (OUT/'voltage_class_screen.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=classes[0]);wr.writeheader();wr.writerows(classes)
print('Voltage minimums:',[(d['rating_V'],d['N_voltage_min']) for d in classes]);print('Two-cell example:',meta['two_cell_control_example']);print('One-cell rejection:',no_single)
for PH,PL in showpairs:
 print('POLES',PH,PL,[(d['rating_V'],next(s for s in selected if s['PH']==PH and s['PL']==PL and s['rating_V']==d['rating_V'] and s['slot_cap']==60)['candidate']) for d in classes])

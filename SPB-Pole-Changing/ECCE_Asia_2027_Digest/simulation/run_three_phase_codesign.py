"""Three-wire SPB winding construction and conditional synchronous envelopes.
All new work and outputs remain within the Digest folder. No research model imported.
"""
from pathlib import Path
import sys, json, csv, math
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(HERE/'vendor'))
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch,Arc
OUT=HERE/'results_three_phase';OUT.mkdir(exist_ok=True)
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':260,'legend.fontsize':8})
# Construction: phase offsets are 120/pL mechanical degrees. Thus pH/pL
# integer r must not be divisible by 3. No neutral lead is present.
Ns=[8,12,16,20,24];families=[(8,4),(12,6),(16,8),(20,10),(16,4),(12,4)]
Vnom=1200.;Vmaxbus=1320.;imbalance=1.1;overshoot=1.1;rating_util=.8
ratings=[80,100,150,200,250,300,400,650,1200,1700]
records=[]

def winding(N,PH,PL):
 assert PH%2==0 and PL%2==0
 pH,pL=PH//2,PL//2
 if pH%pL or (pH//pL)%3==0:return None
 g=math.gcd(N,pL);Q=3*N*pL//g;c=pL//g;s=Q//(3*pL)
 groups=[]
 for q in range(s):
  for rr in range(g):
   phases=[]
   for ph in range(3):
    phases.append([b*3*s+q+ph*s for b in range(rr*c,(rr+1)*c)])
   groups.append(phases)
 assert len(groups)==N
 assert sorted(k for gr in groups for leg in gr for k in leg)==list(range(Q))
 # Both modes must give balanced equal-amplitude three-wire phase phasors.
 for pp in [pH,pL]:
  for group in groups:
   vv=np.array([sum(np.exp(1j*pp*2*np.pi*np.array(leg)/Q)) for leg in group])
   assert abs(sum(vv))<1e-10
   assert np.max(abs(abs(vv)-c))<1e-10
 ys=np.arange(1,Q//2+1)
 kpH=abs(np.sin(np.pi*pH*ys/Q));kpL=abs(np.sin(np.pi*pL*ys/Q));score=np.minimum(kpH,kpL)
 # shortest pitch within 1e-12 of the discrete maximin optimum
 y=int(ys[np.argmax(score)])
 return {'N':N,'poles_high':PH,'poles_low':PL,'ratio':PH/PL,'Q':Q,'coils_per_leg':c,'phase_spacing_slots':s,'pitch_slots':y,'kp_high':float(kpH[y-1]),'kp_low':float(kpL[y-1]),'minimum_pitch_factor':float(score[y-1]),'groups':groups}

for PH,PL in families:
 for N in range(2,41):
  ww=winding(N,PH,PL)
  required=Vmaxbus/N*imbalance*overshoot/rating_util
  record={'N':N,'poles_high':PH,'poles_low':PL,'ratio':PH/PL,'Vcell_nom_V':Vnom/N,'Vcell_max_scenario_V':Vmaxbus/N*imbalance*overshoot,'rating_min_V':required,'illustrative_device_rating_V':next(v for v in ratings if v>=required),'construction_supported':ww is not None}
  if ww:record.update({k:v for k,v in ww.items() if k!='groups'})
  records.append(record)
W=winding(24,12,6)
rows=[]
for j,group in enumerate(W['groups']):
 for ph,leg in enumerate(group):
  for ii,k in enumerate(leg):
   rows.append({'cell':j+1,'phase':'ABC'[ph],'series_index':ii+1,'coil':k+1,'start_slot':k+1,'return_slot':(k+W['pitch_slots'])%W['Q']+1,'connection_polarity':1,'phase_angle_12pole_deg':round((6*360*k/W['Q'])%360,8),'phase_angle_6pole_deg':round((3*360*k/W['Q'])%360,8)})
with (OUT/'winding_12_6_N24_Q72.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
# Winding MMF direct harmonic check using coil pitch. Current phase compensates
# the complex coil-side phasor; evaluate signed spatial orders on all coil sides.
Q=W['Q'];theta=2*np.pi*np.arange(Q)/Q;delta=2*np.pi*W['pitch_slots']/Q
spectra={}
for pp in [6,3]:
 # At temporal phase 0, choose current that maximizes +pp travelling coefficient.
 phase=pp*theta+pp*delta/2
 current=np.cos(phase)
 # An ideal waveform in every phase is balanced because offsets are +/-120 deg.
 for group in W['groups']:
  assert abs(sum(current[leg[0]] for leg in group))<1e-10
 spectrum=[]
 for nu in range(1,25):
  # current sheet coefficient includes outgoing and returning sides.
  coeff=abs(np.sum(current*(np.exp(-1j*nu*theta)-np.exp(-1j*nu*(theta+delta)))))/Q
  spectrum.append(float(coeff))
 spectra[str(2*pp)]=spectrum
 assert abs(spectrum[pp-1]-abs(np.sin(pp*delta/2)))<1e-10
# Repeating 4-segment rotor pattern for 12/6 poles. PM segments keep sign;
# the other six segments are reversed by bipolar field excitation.
M=12;arc=.7;rotth=2*np.pi*np.arange(M)/M
patH=(-1.)**np.arange(M);patL=np.array([1,1,-1,-1]*3)
fixed=np.where(patH==patL)[0];reversed_=np.where(patH!=patL)[0]
def rotor_fundamental(pattern,p):
 return float(2*np.sin(p*np.pi*arc/M)/(np.pi*p)*abs(np.sum(pattern*np.exp(-1j*p*rotth))))
bH=rotor_fundamental(patH,6);bL=rotor_fundamental(patL,3)
flux_ratio=(bL/3)/(bH/6)*(W['kp_low']/W['kp_high'])
# This modal extension assumes enough stator back iron for the low-pole mode.
# Model includes only desired spatial order, not unused-harmonic EMFs.
N=24;Imax=math.sqrt(2)*266.08980965544276;Vpk=.95*1200/N/math.sqrt(3);R=.002
psiH=.026;LdH=45e-6;LqH=90e-6;Llow=4*(LdH+LqH)/2
models=[{'name':'IPMSM 12 poles','p':6,'psi_Wb':psiH,'Ld_H':LdH,'Lq_H':LqH,'field_loss_W':0},
{'name':'HEPM 12 poles','p':6,'psi_Wb':psiH,'Ld_H':LdH,'Lq_H':LqH,'field_loss_W':3000},
{'name':'HEPM 6 poles','p':3,'psi_Wb':psiH*flux_ratio,'Ld_H':Llow,'Lq_H':Llow,'field_loss_W':3000},
{'name':'IPMSM stronger FW','p':6,'psi_Wb':psiH,'Ld_H':psiH/(.9*Imax),'Lq_H':2*psiH/(.9*Imax),'field_loss_W':0}]
ng=np.linspace(0,9000,181)

def envelope(model,n_grid,number_id=4001):
 ids=np.linspace(-Imax,0,number_id);circle=np.sqrt(np.maximum(0,Imax**2-ids**2));p=model['p'];ld=model['Ld_H'];lq=model['Lq_H'];psi=model['psi_Wb'];K=3*N/2*p
 result=[]
 for nr in n_grid:
  wm=nr*2*np.pi/60;we=p*wm
  aa=(we*lq)**2+R**2;bb=2*R*we*(psi+(ld-lq)*ids);cc=(R*ids)**2+we**2*(psi+ld*ids)**2-Vpk**2
  disc=bb*bb-4*aa*cc;sq=np.sqrt(np.maximum(disc,0));upper=(-bb+sq)/(2*aa);lower=(-bb-sq)/(2*aa)
  iq=np.minimum(circle,upper);lo=np.maximum(lower,0)
  coefficient=K*(psi+(ld-lq)*ids);ok=(disc>=0)&(iq>=lo)&(iq>=0)&(coefficient>0)
  tq=np.where(ok,coefficient*iq,-np.inf)
  if not np.any(ok):
   result.append({'rpm':float(nr),'torque_Nm':0.,'power_kW':0.,'feasible_positive_torque':False,'id_A':None,'iq_A':None});continue
  # A 300 kW electromagnetic output ceiling, not a thermal continuous rating.
  cap=300000/wm if wm>0 else np.inf
  best=int(np.argmax(tq));val=min(float(tq[best]),cap)
  q=val/coefficient[best];dd=float(ids[best]);vd=R*dd-we*lq*q;vq=R*q+we*(psi+ld*dd)
  assert dd*dd+q*q<=Imax**2*(1+1e-10)
  assert vd*vd+vq*vq<=Vpk**2*(1+1e-9)
  result.append({'rpm':float(nr),'torque_Nm':val,'power_kW':val*wm/1000,'feasible_positive_torque':True,'id_A':dd,'iq_A':float(q),'voltage_peak_V':float(np.hypot(vd,vq)),'stator_copper_W':float(3*N/2*R*(dd*dd+q*q))})
 return result
curves={m['name']:envelope(m,ng) for m in models}
combined=[]
for a,b in zip(curves['HEPM 12 poles'],curves['HEPM 6 poles']):
 chosen=dict(a if a['torque_Nm']>=b['torque_Nm'] else b);chosen['active_poles']=12 if a['torque_Nm']>=b['torque_Nm'] else 6;combined.append(chosen)
curves['HEPM selectable 12 or 6']=combined
# Independent brute-force check against the analytic feasible iq interval.
checks=[]
for model in [models[0],models[2]]:
 for nr in [1000,3000,6000,9000]:
  ids,iqs=np.meshgrid(np.linspace(-Imax,0,401),np.linspace(0,Imax,401),indexing='ij');we=model['p']*nr*2*np.pi/60;wm=nr*2*np.pi/60
  vd=R*ids-we*model['Lq_H']*iqs;vq=R*iqs+we*(model['psi_Wb']+model['Ld_H']*ids)
  ok=(ids**2+iqs**2<=Imax**2)&(vd**2+vq**2<=Vpk**2)
  T=3*N/2*model['p']*(model['psi_Wb']+(model['Ld_H']-model['Lq_H'])*ids)*iqs
  brute=max(0,float(np.max(np.where(ok,T,-1))));brute=min(brute,300000/wm)
  exact=envelope(model,[nr])[0]['torque_Nm']
  assert brute<=exact+1e-3
  checks.append({'name':model['name'],'rpm':nr,'analytic_interval_T_Nm':exact,'brute_grid_T_Nm':brute,'relative_grid_gap':(exact-brute)/exact if exact else 0})
metrics={}
for name,curve in curves.items():
 metrics[name]={'peak_torque_Nm':max(x['torque_Nm'] for x in curve),'end_rpm_at_150kW':max([x['rpm'] for x in curve if x['power_kW']>=150]+[0]),'end_rpm_at_300kW':max([x['rpm'] for x in curve if x['power_kW']>=299.999]+[0]),'power_at_9000_kW':curve[-1]['power_kW'],'electrical_study_max_rpm':9000}
# Illustrative inductance sensitivity of the lower-pole mode, not a new machine.
sensitivity=[]
for factor in [2,4,6]:
 mm=dict(models[2],Ld_H=factor*(LdH+LqH)/2,Lq_H=factor*(LdH+LqH)/2)
 cc=envelope(mm,[4500,9000]);sensitivity.append({'low_mode_inductance_factor':factor,'Llow_H':mm['Ld_H'],'points':cc})
# FIGURE 1: no-neutral three-wire architecture and explicit coil grouping.
fig=plt.figure(figsize=(6.3,2.8));ax=fig.add_axes([.01,.05,.44,.9]);ax.set_xlim(0,10);ax.set_ylim(0,10);ax.axis('off');ax.text(.1,9.8,'(a) Three-wire SPB groups',fontsize=10);ax.plot([1,1],[.7,8.7],color='black',lw=.9,zorder=0)
for j,yy in enumerate([7,4,1]):
 for lo,hi in [(yy-.3,yy),(yy+1.4,yy+1.7)]:ax.plot([1,1],[lo,hi],color='black',lw=.9)
 ax.add_patch(Rectangle((.1,yy),1.9,1.4,facecolor='#e8eff7',edgecolor='black'));ax.text(1.05,yy+.7,['Cell 1','Cell 2','Cell N'][j],ha='center',va='center',fontsize=9)
 ax.add_patch(Rectangle((5,yy-.1),4.5,1.7,facecolor='#f5f5f5',edgecolor='black'));ax.text(7.25,yy+.75,'Winding group',ha='center',va='center',fontsize=9)
 for k,lab in enumerate('ABC'):
  y=yy+.25+.45*k;ax.plot([2,5],[y,y],color='black',lw=.8);ax.text(3.3,y+.04,lab,fontsize=8)
ax.text(.1,.0,'No neutral lead between cells or groups',fontsize=8)
ax=fig.add_axes([.51,.12,.46,.79]);ax.set_aspect('equal');ax.axis('off');ax.set_xlim(-1.55,1.55);ax.set_ylim(-1.45,1.55);ax.text(-1.5,1.48,'(b) N = 24, Q = 72, coil pitch y = 8',fontsize=10)
ang=2*np.pi*np.arange(72)/72
ax.scatter(np.cos(ang),np.sin(ang),s=8,color='#b0b0b0')
cols=['#164e7c','#b05d19','#2b7a47']
for phase,k in enumerate(W['groups'][0]):
 q=k[0];r=(q+8)%72
 for sl in [q,r]:ax.scatter(np.cos(ang[sl]),np.sin(ang[sl]),s=32,color=cols[phase],zorder=3)
 ax.plot([np.cos(ang[q]),np.cos(ang[r])],[np.sin(ang[q]),np.sin(ang[r])],color=cols[phase],lw=2)
 mid=ang[q]+(ang[r]-ang[q])/2
 ax.text(1.18*np.cos(mid),1.18*np.sin(mid),'ABC'[phase],color=cols[phase],ha='center',fontsize=10,fontweight='bold')
for q in [0,8,16,24]:ax.text(.84*np.cos(ang[q]),.84*np.sin(ang[q]),str(q+1),ha='center',va='center',fontsize=8)
ax.text(-1.5,-1.4,'Cell 1 coils: A 1→9, B 9→17, C 17→25\nSlot labels are 1-based; layers remain separate.',fontsize=8)
fig.savefig(FIG/'fig_three_wire_winding.png',bbox_inches='tight');fig.savefig(FIG/'fig_three_wire_winding.svg',bbox_inches='tight');plt.close(fig)
# FIGURE 2: slot compatibility and rotor polarity pattern.
fig=plt.figure(figsize=(6.3,3.0));ax=fig.add_axes([.18,.43,.72,.47]);PHs=[8,12,16,20];mat=np.array([[winding(n,ph,ph//2)['Q'] for n in Ns] for ph in PHs]);im=ax.imshow(mat,cmap='Blues',vmin=24,vmax=360,aspect='auto')
for r in range(4):
 for c in range(5):ax.text(c,r,str(mat[r,c]),ha='center',va='center',color='white' if mat[r,c]>200 else 'black')
ax.set_xticks(range(5),Ns);ax.set_yticks(range(4),[f'{ph}/{ph//2}' for ph in PHs]);ax.set_xlabel('Stacked cell count N');ax.set_ylabel('Total pole combination');ax.set_title('(a) Minimum Q for this balanced construction',fontsize=10)
ax=fig.add_axes([.18,.06,.72,.20]);ax.set_xlim(0,12);ax.set_ylim(-.1,2.4);ax.axis('off')
for r,pat,label in [(1,patH,'12 poles'),(0,patL,'6 poles')]:
 ax.text(-.1,r+.45,label,ha='right',va='center',fontsize=9)
 for k in range(12):
  ax.add_patch(Rectangle((k,r+.05),.96,.8,facecolor='#f1ded8' if k in fixed else '#dbe7f3',edgecolor='white'));ax.text(k+.48,r+.45,'N' if pat[k]>0 else 'S',ha='center',va='center',fontsize=9)
ax.text(0,2.12,'(b) Rotor polarity example     warm: fixed PM     cool: reversible field',fontsize=8)
fig.savefig(FIG/'fig_cell_pole_design.png',bbox_inches='tight');fig.savefig(FIG/'fig_cell_pole_design.svg',bbox_inches='tight');plt.close(fig)
# FIGURE 3: torque and power with controlled comparison and FW sensitivity.
fig,axes=plt.subplots(2,1,figsize=(6.3,3.8),sharex=True)
style={'IPMSM 12 poles':('#444444','--',1.5),'HEPM 6 poles':('#b05d19',':',1.7),'HEPM selectable 12 or 6':('#164e7c','-',2.),'IPMSM stronger FW':('#2c7a49','-.',1.2)}
for name,(col,ls,lw) in style.items():
 cc=curves[name];axes[0].plot(ng,[x['torque_Nm'] for x in cc],color=col,ls=ls,lw=lw,label=name);axes[1].plot(ng,[x['power_kW'] for x in cc],color=col,ls=ls,lw=lw)
axes[0].set_ylabel('Torque (N m)');axes[1].set_ylabel('Power (kW)');axes[1].set_xlabel('Mechanical speed (rpm)')
axes[0].legend(loc='upper right',framealpha=.95);axes[1].axhline(150,color='#aaaaaa',ls=':',lw=.8);axes[1].axhline(300,color='#aaaaaa',ls=':',lw=.8)
for ax in axes:ax.grid(alpha=.2);ax.set_xlim(0,9000);ax.set_ylim(bottom=0)
fig.tight_layout();fig.savefig(FIG/'fig_hybrid_ipmsm_envelope.png');fig.savefig(FIG/'fig_hybrid_ipmsm_envelope.svg');plt.close(fig)
meta={'scope':'Three-wire three-phase groups only; no neutral conductor','construction':'Uniform phase spacing 120/pL mechanical degrees; combine identical sector triples. Sufficient construction, not a general necessary condition.','inputs':{'Vdc_nom_V':Vnom,'Vdc_max_scenario_V':Vmaxbus,'imbalance_factor':imbalance,'overshoot_factor':overshoot,'device_rating_utilization':rating_util,'I_peak_A':Imax,'V_phase_peak_limit_V':Vpk,'phase_R_ohm':R,'power_ceiling_W':300000,'rpm_window':[0,9000],'mechanical_limit_validated':False,'number_id':4001,'per_mode_field_loss_W_assumed':3000},'winding_cases':records,'selected_winding':{k:v for k,v in W.items() if k!='groups'},'winding_harmonic_amplitudes':spectra,'rotor':{'segments':12,'pole_arc_ratio':arc,'high_pattern':patH.tolist(),'low_pattern':patL.tolist(),'fixed_PM_segments_1based':(fixed+1).tolist(),'reversed_field_segments_1based':(reversed_+1).tolist(),'B_high_fundamental_per_face':bH,'B_low_fundamental_per_face':bL,'low_high_flux_linkage_ratio':flux_ratio,'required_low_high_yoke_flux_ratio':flux_ratio},'models':models,'curves':curves,'metrics':metrics,'validation':{'balanced_three_wire_phasors':'passed','coil_coverage_unique':'passed','coil_side_fourier_vs_pitch':'passed','analytic_interval_vs_brute_grid':checks},'low_mode_inductance_sensitivity':sensitivity,'limits':['Linear desired-order dq model; uncalibrated conceptual parameters','No unused rotor-harmonic EMFs, saturation, iron loss, demagnetization, thermal or mechanical validation','No transition or cell-energy balancing simulation','Fixed high and low endpoint fluxes; no freely adjustable hybrid flux assumed','Matched 12-pole electrical baseline, not an optimized equal-volume IPMSM comparison','Field supply power is disclosed but excluded from electromagnetic output curves','Device-rating examples are assumptions, not selected commercial device specifications']}
(OUT/'three_phase_codesign.json').write_text(json.dumps(meta,indent=2))
with (OUT/'cell_pole_sweep.csv').open('w',newline='') as f:
 keys=sorted({k for r in records for k in r});wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows(records)
with (OUT/'torque_power_curves.csv').open('w',newline='') as f:
 wr=csv.writer(f);wr.writerow(['machine','rpm','torque_Nm','power_kW']);
 for name,cc in curves.items():
  for pt in cc:wr.writerow([name,pt['rpm'],pt['torque_Nm'],pt['power_kW']])
print(json.dumps({'selected_winding':meta['selected_winding'],'rotor':meta['rotor'],'metrics':metrics},indent=2))

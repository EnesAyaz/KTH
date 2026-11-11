"""Independent ideal phase-domain and capacitor-energy screen, not a motor model.
Run with the bundled Python. Optional local plotting packages are in vendor/.
Every output is confined to this Digest folder. No sibling scripts are imported.
"""
from pathlib import Path
import sys, json, hashlib, csv
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'vendor'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=HERE.parent
FIG=ROOT/'figures'; OUT=HERE/'results'
FIG.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':260,'axes.labelsize':10,'legend.fontsize':8})
N=16; V0=75.; RPM=2100.; fm=RPM/60
T=0.2; dt=1e-5; t=np.arange(round(T/dt))*dt
# Across m, keep total per-cell real power and summed phase-current-square fixed.
# Equal modal RMS amplitudes. Phase voltage total RMS = 16 V.
# m=3 total phase current RMS=200 A; m=5 scales by sqrt(3/5).
# Real power then differs with sqrt(m): instead fix real power AND current loss
# by scaling voltage and current by sqrt(3/m). All cases have 9.6 kW/cell.
Vbase=16.; Ibase=200.
cases=[('A',3,2,1),('B',5,3,1),('C',5,2,1),('E3',3,4,2),('E5',5,4,2)]
results=[]; traces={}
for name,m,a,b in cases:
    scale=np.sqrt(3/m); Vr=Vbase*scale; Ir=Ibase*scale
    alpha=2*np.pi*np.arange(N)/(m*N)
    theta=alpha[:,None]+2*np.pi*np.arange(m)[None,:]/m
    x=2*np.pi*(a*fm)*t[:,None,None]-a*theta[None,:,:]
    y=2*np.pi*(b*fm)*t[:,None,None]-b*theta[None,:,:]
    # Modal RMS = total RMS/sqrt(2), hence modal peak = total RMS.
    va=Vr*np.cos(x); vb=Vr*np.cos(y)
    ia=Ir*np.cos(x); ib=Ir*np.cos(y)
    v=va+vb; i=ia+ib
    P=np.sum(v*i,axis=2)
    own=np.sum(va*ia+vb*ib,axis=2)
    cross=np.sum(va*ib+vb*ia,axis=2)
    ripple=P-np.mean(P,axis=1,keepdims=True)
    pulse=float(np.max(np.abs(ripple)))
    # Integrate the prescribed nominal-recharge mismatch. This is an energy
    # buffer sizing screen, NOT exact closed-loop series-stack voltage dynamics.
    e=np.zeros(len(t)); e[1:]=-np.cumsum((ripple[:-1,0]+ripple[1:,0])*.5*dt)
    e-=.5*(e.max()+e.min())
    Cexact=max(2*e.max()/((1.1*V0)**2-V0**2),-2*e.min()/(V0**2-(.9*V0)**2))
    allowed=bool((a+b)%m==0 or (a-b)%m==0)
    freq=(a+b)*fm if (a+b)%m==0 else (abs(a-b)*fm if (a-b)%m==0 else None)
    expected=m*Vr*Ir if allowed else 0.
    assert np.max(np.abs(P-own-cross))<1e-7
    assert abs(pulse-expected)<1e-6
    assert np.max(np.abs(np.sum(v,axis=2)))<1e-10
    assert np.max(np.abs(np.sum(i,axis=2)))<1e-9
    assert np.ptp(P.sum(axis=1))<1e-6
    voltages={}
    for CmF in [5,10,20,30]:
        C=CmF/1000; v2=V0**2+2*e/C
        vv=np.sqrt(np.maximum(v2,0))
        voltages[str(CmF)]={'min_V':float(vv.min()) if v2.min()>0 else None,'max_V':float(vv.max()),'energy_positive':bool(v2.min()>0),'within_10_percent':bool(v2.min()>=(.9*V0)**2 and v2.max()<=(1.1*V0)**2)}
    rec={'case':name,'m':m,'poles':[2*a,2*b],'Q':m*N,'N':N,'Vrms_total_V':float(Vr),'Irms_total_A':float(Ir),'cell_mean_power_W':float(P.mean()),'sum_phase_Irms_squared_A2':float(m*Ir**2),'cross_power_peak_W':pulse,'cross_power_expected_W':float(expected),'frequency_Hz':freq,'buffer_energy_amplitude_J':float(max(abs(e))),'C_min_exact_energy_mF':float(Cexact*1000),'C_min_linearized_mF':float(expected/(2*np.pi*freq*V0*(.1*V0))*1000) if freq else 0.,'buffer_voltage':voltages,'max_phase_voltage_V':float(abs(v).max()),'neutral_current_max_A':float(abs(i.sum(axis=2)).max())}
    results.append(rec); traces[name]=(P[:,0],ripple[:,0],e)
# Numerical convergence of energy integral against its closed form.
A=results[0]; analytical_E=A['cross_power_peak_W']/(2*np.pi*A['frequency_Hz'])
energy_error=abs(A['buffer_energy_amplitude_J']-analytical_E)/analytical_E
assert energy_error<1e-4
# Winding-pitch screen from project construction. Only pitch factor, not a full
# harmonic-loss or end-winding model; full distribution factor assumed.
pitch=[]
for name,m,a,b in cases[:3]:
    Q=m*N; ys=np.arange(1,Q//2+1)
    kwa=abs(np.sin(np.pi*a*ys/Q)); kwb=abs(np.sin(np.pi*b*ys/Q)); score=np.minimum(kwa,kwb)
    best=int(np.argmax(score)); short=ys<=Q/(2*a)
    si=int(np.argmax(np.where(short,score,-1)))
    pitch.append({'case':name,'Q':Q,'best_y_slots':int(ys[best]),'best_span_mech_deg':float(360*ys[best]/Q),'best_min_pitch_factor':float(score[best]),'high_pole_full_pitch_max_slots':float(Q/(2*a)),'short_y_slots':int(ys[si]),'short_min_pitch_factor':float(score[si])})
# Plot 1: spatial screen and original SPB schematic.
fig=plt.figure(figsize=(6.3,3.2)); ax=fig.add_axes([.02,.06,.47,.88]); ax.set_xlim(0,10);ax.set_ylim(0,10);ax.axis('off')
from matplotlib.patches import Rectangle, FancyArrowPatch
ax.text(.1,9.6,'(a) Series DC cells and isolated groups',fontsize=10)

for lo,hi in [(8.75,9),(5.75,7.5),(2.75,4.5),(1,1.5)]: ax.plot([1.2,1.2],[lo,hi],color='black',lw=1)
for j,yy in enumerate([7.5,4.5,1.5]):
    ax.add_patch(Rectangle((.2,yy),2,1.25,facecolor='#e9f0f7',edgecolor='black'))
    ax.text(1.2,yy+.62,('Cell 1' if j==0 else 'Cell 2' if j==1 else 'Cell N'),ha='center',va='center')
    ax.add_patch(FancyArrowPatch((2.3,yy+.62),(4.1,yy+.62),arrowstyle='->',mutation_scale=10,color='black'))
    ax.add_patch(Rectangle((4.2,yy),4.9,1.25,facecolor='#f3f3f3',edgecolor='black'))
    ax.text(6.65,yy+.62,'m-phase group\nisolated neutral',ha='center',va='center',fontsize=9)
ax.text(.2,.2,'N = 16     Vdc = 1200 V     Vcell = 75 V',fontsize=9)
ax=fig.add_axes([.61,.31,.35,.55]); matrix=np.array([[int((a+b)%m==0 or (a-b)%m==0) for a,b in [(2,1),(3,1),(4,2)]] for m in [3,5,7]])
ax.imshow(matrix,cmap=matplotlib.colors.ListedColormap(['#e7f0e7','#b7cce1']),vmin=0,vmax=1,aspect='auto')
for ri,m in enumerate([3,5,7]):
 for ci,(a,b) in enumerate([(2,1),(3,1),(4,2)]):
    valid=a%m!=0 and b%m!=0
    ax.text(ci,ri,'couples' if matrix[ri,ci] and valid else 'cancels' if valid else 'reject*',ha='center',va='center',fontsize=9)
ax.set_xticks(range(3),['4/2','6/2','8/4']);ax.set_yticks(range(3),['m = 3','m = 5','m = 7']);ax.set_xlabel('Total pole combination');ax.set_title('(b) Ideal spatial screen',fontsize=10)
fig.text(.58,.025,'*Order 3 is zero sequence for m = 3.\nLabels apply to the stated interleaved winding.',fontsize=8)
fig.savefig(FIG/'fig1_architecture_and_modes.png',bbox_inches='tight');fig.savefig(FIG/'fig1_architecture_and_modes.svg',bbox_inches='tight');plt.close(fig)
# Plot 2 direct phase sums and buffer voltages.
fig,axes=plt.subplots(2,1,figsize=(6.3,4.4),sharex=True)
colors={'A':'#174b78','B':'#b05a18','C':'#2c7b45'}
for n in ['A','B','C']:
    axes[0].plot(t*1000,traces[n][1]/1000,label=n+': '+('3 phases, 4/2 poles' if n=='A' else '5 phases, 6/2 poles' if n=='B' else '5 phases, 4/2 poles'),color=colors[n],lw=1.5,ls='--' if n=='C' else '-')
for cm,style in [(10,'--'),(30,'-')]:
    vv=np.sqrt(V0**2+2*traces['A'][2]/(cm/1000))
    axes[1].plot(t*1000,vv,label=f'A: C = {cm} mF',lw=1.5,ls=style,color='#174b78' if cm==30 else '#b05a18')
axes[1].axhspan(67.5,82.5,color='#dcebdc',alpha=.65,label='Allowed band +/-10%')
axes[1].axhline(75,color='black',lw=.6)
axes[0].set_ylabel('Cell power mismatch (kW)');axes[1].set_ylabel('Buffer voltage (V)');axes[1].set_xlabel('Time (ms)')
axes[0].legend(loc='upper right',ncol=1,frameon=True);axes[1].legend(loc='upper right',ncol=1,frameon=True)
for ax in axes:ax.set_xlim(0,40);ax.grid(alpha=.2)
fig.tight_layout();fig.savefig(FIG/'fig2_phase_power_and_energy.png');fig.savefig(FIG/'fig2_phase_power_and_energy.svg');plt.close(fig)
# Plot 3 winding pitch geometry: avoid presenting this as a machine optimum.
fig,ax=plt.subplots(figsize=(6.3,2.8));span=np.linspace(0,180,1001);s=span/360
for a,b,col,label in [(2,1,'#174b78','4/2 poles'),(3,1,'#b05a18','6/2 poles')]:
    score=np.minimum(abs(np.sin(np.pi*a*s)),abs(np.sin(np.pi*b*s)))
    ax.plot(span,score,color=col,label=label,lw=1.8)
ax.axvline(90,color='#174b78',ls=':',lw=1);ax.axvline(60,color='#b05a18',ls=':',lw=1)
ax.text(94,.18,'4-pole full pitch',color='#174b78',fontsize=8);ax.text(13,.92,'6-pole full pitch = 60 deg',color='#b05a18',fontsize=8)
ax.set(xlim=(0,180),ylim=(0,1.05),xlabel='Coil span in mechanical degrees',ylabel='Minimum of two pitch factors');ax.grid(alpha=.2);ax.legend(loc='lower right');fig.tight_layout();fig.savefig(FIG/'fig3_pitch_tradeoff.png');fig.savefig(FIG/'fig3_pitch_tradeoff.svg');plt.close(fig)
metadata={'model':'Ideal phase-domain superposition and nominal-recharge energy-buffer sizing','not_modelled':['rotor dynamics','PWM','saturation','thermal limits','end winding loss','closed-loop series-cell balancing','motor efficiency or drive-cycle benefit'],'parameters':{'N':N,'Vdc_V':N*V0,'Vcell_V':V0,'rpm':RPM,'duration_s':T,'dt_s':dt,'power_factor_per_mode':1,'equal_mean_cell_power_W':9600,'equal_sum_phase_Irms_squared_A2':120000},'verification':{'phase_sum_cross_identity':'passed','neutral_voltage_and_current_sums':'passed','total_stack_output_power_constant':'passed','spatial_rule_matches_phase_sum':'passed','energy_integral_relative_error':energy_error},'cases':results,'winding_pitch':pitch}
(OUT/'simplified_screen.json').write_text(json.dumps(metadata,indent=2))
with (OUT/'case_summary.csv').open('w',newline='') as f:
    fields=['case','m','poles','Q','cell_mean_power_W','cross_power_peak_W','frequency_Hz','C_min_exact_energy_mF'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in results)
np.savez_compressed(OUT/'traces.npz',time_s=t,**{n+'_power_mismatch_W':traces[n][1] for n in traces},A_energy_J=traces['A'][2])
print(json.dumps({'cases':[{k:r[k] for k in ['case','cross_power_peak_W','C_min_exact_energy_mF']} for r in results],'winding_pitch':pitch,'energy_error':energy_error},indent=2))


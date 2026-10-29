"""Refresh the review's Rev-B screening results from archived slide data.
Sources: reports/slides/spb_revb_design_flow.pptx (28 October 2026),
revb_flow_numbers.json, final_numbers.json, q3d_spice_numbers.json.
This is a semiconductor-only screening estimate, not measured inverter efficiency.
"""
from pathlib import Path
import json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
OUT=Path(__file__).resolve().parent;D=OUT/'revb'
f=json.loads((D/'revb_flow_numbers.json').read_text());row=f['npar']['0.5nH'][3]
current=2*math.sqrt(2)*300000/(3*1.15*1200*.9)
cap=20*6.35+40*.18
result={'power_W':300000,'Vbus_V':1200,'power_factor':.9,'M':1.15,'N':16,'n_parallel':4,'current_rms_A':current,'current_peak_A':current*math.sqrt(2),'leg_semiconductor_loss_W':row['tot'],'stack_semiconductor_loss_W':48*row['tot'],'efficiency_screen_percent':100*row['eta'],'Tj_screen_C':row['tj'],'C_leg_nominal_uF':480,'C_leg_effective_uF':cap,'C_cell_nominal_uF':1440,'C_cell_effective_uF':3*cap,'estimated_ripple_V':382.04988425504024*2.25/(3*cap),'loss_scope':'conduction, switching, dead time, gate; excludes board/busbar/capacitor/control/cooling/machine losses'}
(OUT/'case_results.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'case_numbers.tex').write_text('% Rev-B slide data, 2026-10-28; semiconductor-only screening.\n'+ '\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in {'CaseCurrent':f'{current:.1f}','CaseLegLoss':f"{row['tot']:.2f}",'CaseTotalLoss':f"{48*row['tot']/1000:.3f}",'CaseEfficiency':f"{100*row['eta']:.2f}",'CaseCellCap':f'{3*cap:.1f}'}.items())+'\n')
(OUT/'loss_rows.tex').write_text('\\newcommand{\\CaseLossRows}{%\n'+''.join(f'{label} & {row[key]:.2f} & {48*row[key]:.1f} \\\\\n' for key,label in [('cond','Conduction'),('sw','Switching'),('dead','Dead time'),('gate','Gate drive')])+'}\n')
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman'],'font.size':8,'mathtext.fontset':'stix','pdf.fonttype':42,'axes.linewidth':.5,'xtick.direction':'in','ytick.direction':'in'})
fig,ax=plt.subplots(figsize=(3.1,1.8));rows=f['npar']['0.5nH'][1:];x=np.arange(2,9);bottom=np.zeros(7)
for key,label,color in [('cond','Conduction','#287fb7'),('sw','Switching','#df6b36'),('dead','Dead time','#e3ad31'),('gate','Gate','#813568')]:
 v=np.array([r[key] for r in rows]);ax.bar(x,v,bottom=bottom,color=color,width=.62,label=label);bottom+=v
ax.axvspan(3.55,4.45,color='#26926f',alpha=.10,zorder=-1);ax.text(4,22,'Selected',ha='center',fontsize=7,color='#176d50');ax.set(xlabel='Devices per switch',ylabel='Loss per leg (W)',ylim=(0,47),xticks=x);ax.legend(frameon=False,fontsize=6.5,loc='upper right');ax.grid(axis='y',alpha=.2);fig.tight_layout(pad=.3);fig.savefig(D/'parallel_losses.pdf');plt.close(fig)
fig,ax=plt.subplots(figsize=(3.1,1.8));labels=['$L_D$\n+0.3 nH','$L_G$\n2 / 8 nH','No Kelvin\nsymmetric','No Kelvin\n$L_{CS}$ +0.2 nH','$V_{th}$\n+0.3 V'];values=[2,19,0,29,7];ax.bar(range(5),values,color=['#287fb7','#df6b36','#287fb7','#df6b36','#287fb7'],width=.6)
for i,v in enumerate(values):ax.text(i,v+1,str(v)+'%',ha='center',fontsize=7)
ax.set_xticks(range(5),labels,fontsize=6.5);ax.set(ylabel='Energy imbalance (%)',ylim=(0,35));ax.grid(axis='y',alpha=.2);fig.tight_layout(pad=.3);fig.savefig(D/'sharing_sensitivity.pdf');plt.close(fig)
print(json.dumps(result,indent=2))

"""Fig. 12: conceptual analytical small-signal balancing response.
From C*V0*dVtilde/dt = I0*Vtilde - DeltaP; motoring I0>0.
s=t/tau0, tau0=C*V0/I0, kappa=Kp/I0. Balancing switches on at s=1.
Illustrative initial deviations and gain are not hardware parameters.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent
s=np.linspace(0,3.5,1401);sb=1.;kappa=3.
e0=np.array([.012,-.015,.003])
factor=np.exp(np.minimum(s,sb)+(1-kappa)*np.maximum(s-sb,0))
e=factor[:,None]*e0
assert np.max(abs(e.sum(axis=1)))<1e-12
assert np.max(abs(e[-1]))<.01*np.max(abs(e[np.argmin(abs(s-sb))]))
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman'],
    'mathtext.fontset':'stix','font.size':8.5,'axes.linewidth':.5,
    'xtick.direction':'in','ytick.direction':'in','pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(8.8/2.54,5.1/2.54))
ax.axvspan(sb,s[-1],color='#378959',alpha=.06,lw=0)
ax.axhline(0,color='.6',lw=.5)
ax.axvline(sb,color='.4',ls=':',lw=.7)
for k,(col,sty) in enumerate(zip(['#3070be','#da4d2a','#378959'],['-','--','-.'])):
    ax.plot(s,e[:,k],color=col,ls=sty,lw=1.1,label=f'Cell {k+1}')
ax.text(.5,.048,'Equal cell\npower',ha='center',va='bottom')
ax.text(2.25,.048,'Power balancing\nenabled',ha='center',va='bottom')
ax.set(xlim=(0,3.5),ylim=(-.048,.07),yticks=[0],xticks=[0,sb])
ax.set_xticklabels(['0',r'$t_b/\tau_0$'])
ax.set_ylabel(r'$\widetilde V_k/V_0$',labelpad=7)
ax.set_xlabel(r'Normalized time $t/\tau_0$',labelpad=5)
ax.spines[['top','right']].set_visible(False)
fig.legend(*ax.get_legend_handles_labels(),loc='lower center',ncol=3,
           frameon=False,fontsize=8.5,handlelength=1.7,columnspacing=1.)
fig.subplots_adjust(left=.17,right=.97,bottom=.32,top=.96)
fig.savefig(OUT/'fig_dclink_balancing.pdf')
fig.savefig(OUT/'fig_dclink_balancing_preview.png',dpi=220)
plt.close(fig)
print('Analytical balancing figure: zero-sum deviations and convergence verified.')

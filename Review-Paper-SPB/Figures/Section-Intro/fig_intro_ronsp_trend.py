"""Fig. 2: original semiconductor curves on one dual-axis graph."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
OUT=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman'],
 'mathtext.fontset':'stix','font.size':8.5,'axes.linewidth':.5,
 'xtick.direction':'in','ytick.direction':'in','pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(8.8/2.54,5.2/2.54));right=ax.twinx()
foms=[];handles=[]
for name,col,coef,expo,epsr,crit,vmin in [('Si','#3070be',5e-6,2.5,11.7,.3e6,10),('4H-SiC','#da4d2a',2e-7,2,9.7,2.2e6,22.4),('GaN','#378959',5e-8,2,9,3.3e6,44.7)]:
 v=np.logspace(np.log10(vmin),3,200)
 ron=coef*v**expo;coss=8.8541878128e-14*epsr*crit/(2*v)
 fom=1/np.sqrt(ron*1e-3*coss)/1000;foms.extend(fom)
 ax.loglog(v,ron,color=col,lw=1)
 right.loglog(v,fom,color=col,lw=1,ls='--')
 handles.append(Line2D([],[],color=col,lw=1.5,label=name))
ax.set(xlim=(10,1000),ylim=(1e-4,1e4),yticks=10.**np.arange(-4,5,2))
right.set_ylim(10**np.floor(np.log10(min(foms))),10**np.ceil(np.log10(max(foms))))
ax.grid(which='major',color='.88',lw=.35)
ax.set_ylabel(r'$R_{\mathrm{on,sp}}$ (m$\Omega$ cm$^2$)',labelpad=3)
right.set_ylabel(r'D-FOM ($\sqrt{\mathrm{MHz}}$)',labelpad=3)
ax.set_xlabel('Blocking voltage (V)',labelpad=3)
fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.51,1.015),ncol=3,frameon=False,columnspacing=1,handlelength=1.5)
fig.legend(handles=[Line2D([],[],color='black',lw=1,label=r'$R_{\mathrm{on,sp}}$ (left)'),Line2D([],[],color='black',lw=1,ls='--',label='D-FOM (right)')],loc='upper center',bbox_to_anchor=(.51,.915),ncol=2,frameon=False,columnspacing=1,handlelength=1.8)
fig.subplots_adjust(left=.20,right=.80,bottom=.22,top=.74)
fig.savefig(OUT/'fig_intro_ronsp_trend.pdf')
fig.savefig(OUT/'fig_intro_ronsp_trend_preview.png',dpi=220)
plt.close(fig)

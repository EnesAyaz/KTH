"""Empirical fits: Azurza Anderson et al., OJPEL 1 (2020), 322-338.
DOI 10.1109/OJPEL.2020.3018220, Tables I-II, Eqs. (2), (5), (9).
kR produces mOhm mm^2; kC produces pF/mm^2; UB in volts.
Ranges follow the approximate device-survey coverage in Figs. 3 and 5.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
OUT=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman'],'mathtext.fontset':'stix','font.size':8.5,'axes.linewidth':.5,'xtick.direction':'in','ytick.direction':'in','pdf.fonttype':42})
# name, color, kR, alphaR, kC, alphaC, minimum and maximum UB
PARAMETERS=[('Si','#3070be',4.8e-4,2.5,2.4e5,-1.6,100,250),('SiC','#da4d2a',7.2e-3,1.6,1.6e4,-1.0,900,10000),('GaN','#378959',.26,1.1,2.7e3,-.7,100,650)]
fig,ax=plt.subplots(figsize=(8.8/2.54,5.2/2.54));right=ax.twinx();handles=[]
for name,col,kr,ar,kc,ac,lo,hi in PARAMETERS:
 v=np.geomspace(lo,hi,200);ron=kr*v**ar;cap=kc*v**ac
 # Convert mOhm mm^2 to Ohm mm^2 and pF/mm^2 to F/mm^2.
 fom=1/np.sqrt(ron*1e-3*cap*1e-12)/1e3
 ax.loglog(v,ron/100,color=col,lw=1.2)
 right.loglog(v,fom,color=col,lw=1.2,ls='--')
 handles.append(Line2D([],[],color=col,lw=1.5,label=name))
ax.set(xlim=(100,10000),ylim=(.1,1000),yticks=[.1,1,10,100,1000]);right.set_ylim(150,600);right.set_yticks([150,200,300,400,600]);right.set_yticklabels(['150','200','300','400','600']);right.minorticks_off()
ax.grid(which='major',color='.88',lw=.35)
ax.set_ylabel(r'$R_{\mathrm{on,sp}}$ (m$\Omega$ cm$^2$)',labelpad=3)
right.set_ylabel(r'D-FOM ($\sqrt{\mathrm{MHz}}$)',labelpad=3)
ax.set_xlabel(r'Blocking voltage $U_B$ (V)',labelpad=3)
material_legend=ax.legend(handles=handles,loc='lower right',bbox_to_anchor=(.99,.02),ncol=3,frameon=True,facecolor='white',edgecolor='none',framealpha=.95,columnspacing=.7,handlelength=1.2,handletextpad=.4,fontsize=7)
ax.add_artist(material_legend)
ax.legend(handles=[Line2D([],[],color='black',lw=1,label=r'$R_{\mathrm{on,sp}}$ (left)'),Line2D([],[],color='black',lw=1,ls='--',label='D-FOM (right)')],loc='upper center',bbox_to_anchor=(.5,.995),ncol=2,frameon=True,facecolor='white',edgecolor='none',framealpha=.95,columnspacing=.8,handlelength=1.5,fontsize=7)
fig.subplots_adjust(left=.19,right=.81,bottom=.23,top=.95)
fig.savefig(OUT/'fig_intro_ronsp_trend.pdf');fig.savefig(OUT/'fig_intro_ronsp_trend_preview.png',dpi=300)
plt.close(fig)

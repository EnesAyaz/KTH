"""Vector fallback for MATLAB license outages. Analytical ripple and original models for other plots.
Run: python Figures/Style/render_vector_plots.py
MATLAB sources beside each output provide editable equivalents.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
BLUE='#3070be';RED='#da4d2a';GREEN='#378959'
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman'],'mathtext.fontset':'stix',
 'font.size':8.5,'axes.linewidth':.5,'xtick.direction':'in','ytick.direction':'in',
 'xtick.major.width':.5,'ytick.major.width':.5,'pdf.fonttype':42,'legend.frameon':False})
def save(fig,path):
 fig.savefig(ROOT/path,facecolor='white');plt.close(fig)
# Radar: unchanged illustrative values.
a=np.deg2rad(90-np.arange(10)*36)
h=np.array([.90,.85,.35,.45,.60,.95,.45,.25,.20,.80]);l=np.array([.45,.40,.85,.80,.35,.30,.75,.80,.65,.35])
labels=['Motor power\ndensity','Faster\ncharging','BMS\nsimplicity','Lower\nswitching\nlosses','Lower\nconduction\nlosses','Lighter\ncables','Lower\nEMI','Lower\ninsulation\nstress','Lower\nsemiconductor\nvoltage','Lower capacitor\nvolume']
fig=plt.figure(figsize=(8.8/2.54,7/2.54));ax=fig.add_axes([.02,.02,.96,.96]);ax.set_aspect('equal');ax.axis('off')
aa=np.r_[a,a[0]]
for r in [.2,.4,.6,.8,1]:ax.plot(r*np.cos(aa),r*np.sin(aa),color='.75',lw=.4)
for angle in a:ax.plot([0,np.cos(angle)],[0,np.sin(angle)],color='.65',lw=.45)
for v,col,mark,sty,label in [(h,BLUE,'o','-','HV'),(l,RED,'s','--','LV')]:
 ax.fill(v*np.cos(a),v*np.sin(a),color=col,alpha=.14)
 ax.plot(np.r_[v,v[0]]*np.cos(aa),np.r_[v,v[0]]*np.sin(aa),color=col,marker=mark,ms=3,lw=1,ls=sty,label=label)
for k,angle in enumerate(a):
 x,y=1.45*np.cos(angle),1.45*np.sin(angle)
 if k==9:x-=.18
 ax.text(x,y,labels[k],ha='center',va='center',fontsize=8.5)
ax.set_xlim(-2.15,2.15);ax.set_ylim(-1.95,1.95)
ax.legend(loc='upper right',bbox_to_anchor=(1,1.06),fontsize=8.5,handlelength=1.8)
save(fig,Path('Figures/Section-Intro/fig_intro_hv_motivation.pdf'))
# Semiconductor: shared voltage axis, resistance left and FOM right.
import runpy
runpy.run_path(str(ROOT/'Figures/Section-Intro/fig_intro_ronsp_trend.py'),run_name='__main__')
# Balancing: analytical small-signal illustration.
import runpy
runpy.run_path(str(ROOT/'Figures/Section-DCLinkBalancing/fig_dclink_balancing_analytical.py'),run_name='__main__')
# Ripple: analytical switching-interval spectrum and steady-state response.
import runpy
runpy.run_path(str(ROOT/'Figures/Section-Modulation/fig_dclink_ripple_analytical.py'),run_name='__main__')
print('Four vector plots generated.')

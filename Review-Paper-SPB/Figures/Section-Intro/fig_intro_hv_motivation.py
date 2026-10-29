from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman'],'font.size':8.5,'pdf.fonttype':42})
out=Path(__file__).parent
labels=['Motor power\ndensity','Faster\ncharging','BMS\nsimplicity','Lower\nswitching\nlosses','Lower\nconduction\nlosses','Lighter\ncables','Lower\nEMI','Lower\ninsulation\nstress','Lower\nsemiconductor\nvoltage','Lower capacitor\nvolume']
hv=np.array([.90,.85,.35,.45,.60,.95,.45,.25,.20,.80]);lv=np.array([.45,.40,.85,.80,.35,.30,.75,.80,.65,.35])
a=np.deg2rad(90-np.arange(10)*36);x=np.cos(a);y=np.sin(a)
fig,ax=plt.subplots(figsize=(3.8,2.65));ax.set_aspect('equal');ax.axis('off')
for r in [.2,.4,.6,.8,1]: ax.plot(np.r_[r*x,r*x[0]],np.r_[r*y,r*y[0]],color='.78',lw=.45)
for xx,yy in zip(x,y): ax.plot([0,xx],[0,yy],color='.72',lw=.4)
for v,c,marker,ls,label in [(hv,'#3177c7','o','-','HV'),(lv,'#dc5635','s','--','LV')]:
 ax.fill(v*x,v*y,color=c,alpha=.13)
 ax.plot(np.r_[v*x,v[0]*x[0]],np.r_[v*y,v[0]*y[0]],color=c,marker=marker,ms=3,lw=1,ls=ls,label=label)
for i,label in enumerate(labels):
 xx,yy=1.45*x[i],1.45*y[i]
 if i==9: xx-=.18
 ax.text(xx,yy,label,ha='center',va='center',linespacing=1.0)
ax.set_xlim(-2,2.7);ax.set_ylim(-1.85,1.85)
ax.legend(loc='center',bbox_to_anchor=(.91,.54),frameon=False,handlelength=1.6,borderpad=0,labelspacing=.4)
fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
fig.savefig(out/'fig_intro_hv_motivation.pdf',bbox_inches='tight',pad_inches=.01)

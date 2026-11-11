"""Physical coil-span example replacing the harder normalized ratio plot."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'simulation/vendor'))
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
for name in ['times.ttf','timesbd.ttf']:
 p=Path('C:/Windows/Fonts')/name
 if p.exists():font_manager.fontManager.addfont(p)
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'mathtext.fontset':'stix','svg.fonttype':'none','axes.linewidth':.6,'xtick.direction':'in','ytick.direction':'in'})
y=np.linspace(0,6,1201);kh=abs(np.sin(np.pi*6*y/36));kl=abs(np.sin(np.pi*3*y/36))
fig,ax=plt.subplots(figsize=(6.5,1.95))
ax.fill_between(y,0,np.minimum(kh,kl),color='#eeeeee',label='Lower of the two factors')
ax.plot(y,kh,color='#111111',lw=1.4,label='12-pole mode');ax.plot(y,kl,color='#184a78',ls='--',lw=1.4,label='6-pole mode')
ax.axvline(3,color='#888888',lw=.7,ls=':');ax.text(2.9,.18,'One 12-pole pitch\n= 3 slots',ha='right',fontsize=9,color='#555555')
ax.plot(4,np.sqrt(3)/2,'o',ms=4,color='#a53520');ax.annotate('4-slot coil: 0.866\nin both modes',xy=(4,np.sqrt(3)/2),xytext=(4.45,.67),fontsize=9,arrowprops={'arrowstyle':'->','lw':.6,'color':'#a53520'},color='#a53520')
ax.set(xlim=(0,6),ylim=(0,1.06),xlabel='Coil span (number of slots)',ylabel='Coil pitch factor');ax.set_xticks(np.arange(7));ax.set_yticks([0,.5,1]);ax.grid(color='#dddddd',lw=.4);ax.set_axisbelow(True)
ax.legend(loc='upper left',fontsize=9,frameon=False,ncol=1,handlelength=2.5,labelspacing=.25)
fig.subplots_adjust(left=.08,right=.99,bottom=.29,top=.97)
for ext in ['png','svg']:fig.savefig(ROOT/'figures'/('ieee_fig2_pitch_choice.'+ext),dpi=600,bbox_inches='tight',pad_inches=.035)
print('Created coil-span figure with actual slot units.')

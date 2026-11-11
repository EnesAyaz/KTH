"""Qualitative normalized mode trade-off; no predicted machine performance."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'simulation/vendor'))
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in ['times.ttf','timesi.ttf','timesbd.ttf']:
 p=Path('C:/Windows/Fonts')/f
 if p.exists():font_manager.fontManager.addfont(p)
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'mathtext.fontset':'stix','axes.linewidth':.6,'xtick.direction':'in','ytick.direction':'in','svg.fonttype':'none'})
x=np.linspace(0,3.2,1201)
def sketch(t,base,stop):
 y=np.where(x<=base,t,np.where(x<stop,t*(1+np.cos(np.pi*np.clip((x-base)/(stop-base),0,1)))/2,0))
 return y
high=sketch(1,1,1.45);low=sketch(.45,2,2.9)
def draw(axes):
 for y,label,col,ls in [(high,'12 poles','#111111','-'),(low,'6 poles','#184a78','--')]:
  axes[0].plot(x,y,color=col,ls=ls,lw=1.4,label=label)
  axes[1].plot(x,x*y,color=col,ls=ls,lw=1.4,label=label)
 for a in axes:
  a.set_xlim(0,3.2);a.set_xticks([0,1,2,3]);a.set_xlabel(r'Normalized speed $\omega_m/\omega_{\rm ref}$');a.grid(color='#dddddd',lw=.4);a.tick_params(labelsize=9)
 axes[0].set_ylim(0,1.17);axes[0].set_yticks([0,.5,1]);axes[0].set_ylabel(r'$T/T_{\rm ref}$')
 axes[1].set_ylim(0,1.17);axes[1].set_yticks([0,.5,1]);axes[1].set_ylabel(r'$P/(T_{\rm ref}\omega_{\rm ref})$')
 axes[0].set_title('(a) Torque — conceptual',fontsize=10,pad=4);axes[1].set_title('(b) Power — conceptual',fontsize=10,pad=4)
 axes[0].annotate('12 poles',(.60,1),(.45,1.08),fontsize=9,arrowprops={'arrowstyle':'-','lw':.5})
 axes[0].annotate('6 poles',(1.70,.45),(1.95,.68),fontsize=9,color='#184a78',arrowprops={'arrowstyle':'-','lw':.5,'color':'#184a78'})
 axes[1].legend(loc='upper right',fontsize=9,frameon=False)
def save(fig,name):
 for ext in ['png','svg']:fig.savefig(ROOT/'figures'/(name+'.'+ext),dpi=600,bbox_inches='tight',pad_inches=.035)
 plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(6.5,1.65));draw(axes);fig.subplots_adjust(left=.065,right=.99,bottom=.31,top=.83,wspace=.28);save(fig,'ieee_fig5_mode_tradeoff')
fig,axes=plt.subplots(2,1,figsize=(4.3,5.1));draw(axes);fig.subplots_adjust(left=.18,right=.98,bottom=.10,top=.94,hspace=.55);save(fig,'he_ipm_mode_tradeoff_schematic')
(ROOT/'simulation/results_basic_fea/mode_sketch_definition.json').write_text(json.dumps({'purpose':'Conceptual normalized high-torque/low-speed versus lower-torque/higher-speed illustration','not_FEA_or_dq_prediction':True,'high':[1,1,1.45],'low':[.45,2,2.9],'formula':'constant torque to base; cosine roll-off to stop; P = T omega; reference scales arbitrary','numerical_speed_or_torque_claim':None},indent=2))
print('Created schematic separate-mode torque and power figures.')

"""Publication figures for the ECCE Asia digest; reads numerical results only."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'simulation/vendor'))
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle,Circle
from matplotlib.lines import Line2D
for file in ['C:/Windows/Fonts/times.ttf','C:/Windows/Fonts/timesi.ttf','C:/Windows/Fonts/timesbd.ttf']:
 if Path(file).exists():font_manager.fontManager.addfont(file)
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'mathtext.fontset':'stix','axes.labelsize':10,'axes.titlesize':10,'axes.linewidth':.65,'axes.edgecolor':'black','axes.facecolor':'white','figure.facecolor':'white','axes.spines.top':True,'axes.spines.right':True,'xtick.direction':'in','ytick.direction':'in','xtick.major.width':.65,'ytick.major.width':.65,'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':9,'legend.frameon':False,'savefig.dpi':600,'svg.fonttype':'none','lines.linewidth':1.35})
R=json.loads((ROOT/'simulation/results_selection/design_selection.json').read_text())
F=ROOT/'figures';F.mkdir(exist_ok=True)
BLUE='#184a78';GRAY='#7b7b7b';ORANGE='#9b4f16';BLACK='#111111'
def save(fig,name):
 fig.savefig(F/(name+'.png'),dpi=600,bbox_inches='tight',pad_inches=.035)
 fig.savefig(F/(name+'.svg'),bbox_inches='tight',pad_inches=.035)
 plt.close(fig)
def grid(ax):
 ax.grid(True,color='#d9d9d9',linewidth=.4,zorder=0);ax.set_axisbelow(True)
# 1. Electrical architecture. Only local floating star points are shown.
fig=plt.figure(figsize=(6.6,2.5))
a=fig.add_axes([.015,.08,.46,.87]);a.set_xlim(-.65,4.1);a.set_ylim(-.18,3.08);a.axis('off')
a.text(1.9,2.96,'(a) Series dc stack',ha='center',va='center',fontsize=10)
centers=[2.32,1.42,.52]
a.plot([.35,.35],[.08,2.75],color=BLACK,lw=.8,zorder=0)
a.text(.35,2.82,'+',ha='center',fontsize=11);a.text(.35,-.05,'−',ha='center',fontsize=11)
a.annotate('',xy=(-.30,2.7),xytext=(-.30,.12),arrowprops={'arrowstyle':'<->','lw':.7,'shrinkA':0,'shrinkB':0})
a.text(-.45,1.43,r'$V_{\mathrm{dc}}$',rotation=90,ha='center',va='center',fontsize=10)
for j,y in enumerate(centers):
 lab=['1','j','N'][j]
 # Replace a section of the series bus by local dc capacitor plates.
 a.plot([.35,.35],[y-.055,y+.055],color='white',lw=3,zorder=2)
 for yy in [y-.045,y+.045]:a.plot([.22,.48],[yy,yy],color=BLACK,lw=.8,zorder=3)
 a.text(.1,y,r'$C_{'+lab+'}$',ha='right',va='center',fontsize=8.5)
 for sgn in [-1,1]:
  yy=y+sgn*.31;a.plot([.35,.77,.77,1.0],[yy,yy,y+sgn*.13,y+sgn*.13],color=BLACK,lw=.7)
 a.add_patch(Rectangle((1,y-.27),1.15,.54,fill=False,lw=.8))
 a.text(1.575,y,'Cell '+lab,ha='center',va='center',fontsize=9)
 for kk,dy in enumerate([.13,0,-.13]):
  a.plot([2.15,3.28-np.sqrt(.31**2-dy**2)],[y+dy,y+dy],color=BLACK,lw=.75)
  a.text(2.5,y+dy+.018,'abc'[kk]+'$_{'+lab+'}$',fontsize=7.5,ha='center',va='bottom')
 a.add_patch(Circle((3.28,y),.31,fill=False,lw=.8));a.text(3.28,y,r'$W_{'+lab+'}$',ha='center',va='center',fontsize=9)
a.text(2.12,.02,r'$V_{c,j}\approx V_{\mathrm{dc}}/N$',ha='center',fontsize=9)
b=fig.add_axes([.53,.08,.46,.87]);b.set_xlim(.05,3.8);b.set_ylim(-.18,3.08);b.axis('off')
b.text(1.9,2.96,'(b) Three-phase cell and winding set',ha='center',va='center',fontsize=10)
b.plot([.35,3.45],[2.52,2.52],color=BLACK,lw=.8);b.plot([.35,3.45],[1.13,1.13],color=BLACK,lw=.8)
b.text(3.51,2.52,'+',va='center',fontsize=10);b.text(3.51,1.13,'−',va='center',fontsize=10)
b.text(.35,2.65,r'$V_{c,j}$',ha='left',fontsize=9)
for x,ph in zip([.65,1.65,2.65],'abc'):
 for yc in [2.23,1.41]:
  b.add_patch(Rectangle((x-.075,yc-.14),.15,.28,fill=False,lw=.75))
  b.plot([x-.19,x-.075],[yc,yc],color=BLACK,lw=.65)
 b.plot([x,x],[2.37,2.52],color=BLACK,lw=.8)
 b.plot([x,x],[1.55,2.09],color=BLACK,lw=.8)
 b.plot([x,x],[1.13,1.27],color=BLACK,lw=.8)
 b.add_patch(Circle((x,1.82),.026,color=BLACK))
 xx=x+.30;b.plot([x,xx,xx],[1.82,1.82,1.19],color=BLACK,lw=.8)
 theta=np.linspace(np.pi/2,-np.pi/2,31);b.plot(xx+.06*np.cos(theta),1.13+.06*np.sin(theta),color=BLACK,lw=.8)
 b.plot([xx,xx],[1.07,.88],color=BLACK,lw=.8)
 b.text(xx+.07,.98,r'$i_{'+ph+',j}$',fontsize=8.5)
 tt=np.linspace(0,1,121);b.plot(xx+.065*np.sin(8*np.pi*tt),.8-.48*tt,color=BLACK,lw=.8)
 b.plot([xx,xx],[.88,.8],color=BLACK,lw=.8);b.plot([xx,xx],[.32,.17],color=BLACK,lw=.8)
b.plot([.95,2.95],[.17,.17],color=BLACK,lw=.8);b.add_patch(Circle((1.95,.17),.028,color=BLACK));b.text(2.02,.02,r'$n_j$',fontsize=9)
b.text(1.93,-.15,'Local star point; no inter-set neutral connection',ha='center',fontsize=8.5)
save(fig,'ieee_fig1_spb_architecture')
# 2. Coil pitch. Line styles remain distinguishable in grayscale.
fig,ax=plt.subplots(figsize=(6.5,2.45));rho=np.linspace(0,3,2401)
for r,label,col,ls in [(2,'2:1',BLACK,'-'),(2.5,'5:2',BLUE,'--'),(3,'3:1 (pitch only)',GRAY,'-.')]:
 k=np.minimum(abs(np.sin(np.pi*rho/2)),abs(np.sin(np.pi*rho/(2*r))))
 ax.plot(rho,k,label=label,color=col,ls=ls,lw=1.4)
ax.axvline(1.5,color='#888888',ls=':',lw=.8)
ax.set(xlim=(0,3),ylim=(0,1.04),xlabel=r'Normalized coil span $\rho=y/\tau_H$',ylabel=r'$\min(k_{p,H},k_{p,L})$')
ax.set_xticks(np.arange(0,3.01,.5));ax.set_yticks(np.arange(0,1.01,.2));ax.legend(loc='upper left',ncol=3,handlelength=2.7,columnspacing=1.5)
grid(ax);fig.tight_layout(pad=.55);save(fig,'ieee_fig2_pitch_ratio')
# 3. Feasible N-Q region, not a heatmap of narrative labels.
fig,axes=plt.subplots(1,2,figsize=(6.5,2.85),sharey=True)
styles={100:('o',BLUE),150:('^',BLACK),200:('s',ORANGE),650:('D',GRAY)}
for ax,pair,letter in zip(axes,[(8,4),(12,6)],'ab'):
 rec=[x for x in R['records'] if (x['PH'],x['PL'])==pair]
 ax.scatter([x['N'] for x in rec],[x['Q'] for x in rec],s=8,color='#b7b7b7',edgecolors='none',zorder=2)
 for bound,ls in [(60,'--'),(72,':')]:ax.axhline(bound,color='#777777',ls=ls,lw=.7,zorder=1)
 for rating,(marker,col) in styles.items():
  cap=72 if rating==100 and pair==(12,6) else 60
  best=next(s['candidate'] for s in R['shortlists'] if (s['PH'],s['PL'])==pair and s['rating_V']==rating and s['slot_cap']==cap)
  if best:
   x,y=best['N'],best['Q'];ax.scatter(x,y,s=35,marker=marker,facecolor='white',edgecolor=col,linewidth=1.1,zorder=4)
   off={100:(-24,7),150:(4,7),200:(4,7),650:(4,7)}[rating]
   if (x,y)==(18,54):off=(4,-12)
   ax.annotate(f'({x}, {y})',(x,y),xytext=off,textcoords='offset points',fontsize=8,color=col)
 ax.set(xlim=(0,33),ylim=(12,100),xlabel=r'Number of cells $N$')
 ax.set_xticks([0,8,16,24,32]);ax.set_yticks([24,36,48,60,72,84,96]);ax.set_title(f'({letter}) {pair[0]}/{pair[1]}-pole operation',pad=6);grid(ax)
axes[0].set_ylabel(r'Number of slots $Q$')
handles=[Line2D([],[],ls='none',marker=m,markerfacecolor='white',markeredgecolor=c,markersize=5,label=f'{v} V') for v,(m,c) in styles.items()]
handles.insert(0,Line2D([],[],ls='none',marker='o',color='#b7b7b7',markersize=3,label='Admissible winding'))
fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,-.01),ncol=5,columnspacing=1.4,handletextpad=.5)
fig.subplots_adjust(left=.08,right=.99,top=.88,bottom=.25,wspace=.16);save(fig,'ieee_fig3_feasible_region')
# 4. Conditional machine envelopes, two adjacent panels with one shared legend.
fig,axes=plt.subplots(1,2,figsize=(6.5,2.0))
styles=[('IPMSM 12 poles','IPMSM reference',BLACK,'--'),('HEPM selectable 12 or 6','HEPM, 12/6 poles',BLUE,'-'),('IPMSM stronger FW','IPMSM, FW sensitivity',GRAY,'-.')]
for key,label,col,ls in styles:
 curve=R['illustrative_terminal_model']['curves'][key];n=np.array([x['rpm'] for x in curve])/1000
 axes[0].plot(n,np.array([x['torque_Nm'] for x in curve])/1000,label=label,color=col,ls=ls,lw=1.45)
 axes[1].plot(n,[x['power_kW'] for x in curve],label=label,color=col,ls=ls,lw=1.45)
for ax in axes:ax.set_xlim(0,9);ax.set_ylim(bottom=0);ax.set_xticks([0,3,6,9]);ax.set_xlabel(r'Speed $n$ (kr/min)');grid(ax)
axes[0].set_ylabel(r'Torque $T_e$ (kN$\cdot$m)');axes[0].set_title('(a) Electromagnetic torque',pad=6)
axes[1].set_ylabel(r'Power $P_e$ (kW)');axes[1].set_title('(b) Electromagnetic power',pad=6);axes[1].set_yticks([0,100,200,300])
fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.5,-.015),ncol=3,columnspacing=1.5,handlelength=2.8)
fig.subplots_adjust(left=.09,right=.99,top=.87,bottom=.32,wspace=.34);save(fig,'ieee_fig4_speed_envelopes')
print('Created four publication figures as 600 dpi PNG and editable SVG.')

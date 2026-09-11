"""Generate conceptual commutation loops and shared gate-driver fanout."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
OUT=Path(__file__).resolve().parents[1]/'results/layout_concepts'
OUT.mkdir(parents=True,exist_ok=True)
def block(a,x,y,w,h,s,c):
 a.add_patch(Rectangle((x,y),w,h,fc=c,ec='white',zorder=3));a.text(x+w/2,y+h/2,s,ha='center',va='center',color='white',fontsize=9,zorder=4)
def arrow(a,p,q,c):a.annotate('',xy=q,xytext=p,arrowprops=dict(arrowstyle='->',color=c,lw=2),zorder=5)
fig,axs=plt.subplots(3,1,figsize=(13,13),layout='constrained')
for a,n in zip(axs,(4,5,6)):
 a.set_xlim(-1,6*n+1);a.set_ylim(-1.5,10);a.axis('off');a.set_title(f'{n} parallel per position: {n} local commutation cells in one phase leg',loc='left',fontweight='bold')
 for y,col in [(8,'#c74646'),(1,'#2864a0')]:a.plot([0,6*n-.5],[y,y],color=col,lw=2)
 a.text(6*n-.4,8,'+',color='#c74646');a.text(6*n-.4,1,'−',color='#2864a0')
 for i in range(n):
  x=6*i
  a.plot([x+1,x+1],[1,8],color='#657589',lw=2)
  block(a,x+.35,4.1,1.3,1.6,f'C{i+1}','#657589')
  a.plot([x+4,x+4],[1,8],color='#253c53',lw=2)
  block(a,x+3.1,5.8,1.8,1.3,f'H{i+1}','#253c53');block(a,x+3.1,2.4,1.8,1.3,f'L{i+1}','#253c53')
  a.plot([x+4,x+5.2],[4.8,4.8],color='#df9c24',lw=2);a.text(x+5.25,4.8,'SW',fontsize=8,va='center')
  # Offset arrows indicate commutation-loop contour, not additional conductors.
  arrow(a,(x+1.4,7.5),(x+3.5,7.5),'#ae46a4')
  arrow(a,(x+5.2,7.2),(x+5.2,5.3),'#ae46a4')
  arrow(a,(x+5.2,4.1),(x+5.2,1.6),'#ae46a4')
  arrow(a,(x+3.5,1.5),(x+1.4,1.5),'#ae46a4')
  arrow(a,(x+.1,2),(x+.1,7),'#ae46a4')
  a.text(x+2.8,-.05,f'Loop {i+1}',color='#ae46a4',ha='center',fontsize=10)
 a.text(0,-1,'All SW taps connect to the same phase node; cross-cell current paths also exist.',fontsize=10)
fig.suptitle('Power-loop contours | 4, 5 and 6 parallel EPC2361',fontsize=19,fontweight='bold')
fig.supxlabel('Purple arrows: reference direction of high-frequency commutation-current change, NOT simultaneous ON-state current through both FETs.\nC → upper device → lower device → C return. Actual paths use copper + close inner return; direction reverses with the switching event.\nConceptual electrical view, not a copper layout. Shared paths and mutual coupling must be retained in extraction.',fontsize=10)
for ext in ('png','svg'):fig.savefig(OUT/f'power_loops_4_5_6.{ext}',dpi=160)
plt.close(fig)
fig,axs=plt.subplots(3,1,figsize=(13,12),layout='constrained')
for a,n in zip(axs,(4,5,6)):
 a.set_xlim(0,18);a.set_ylim(-1,n+1);a.axis('off');a.set_title(f'One driver channel → {n} parallel gates in ONE switch position',loc='left',fontweight='bold')
 block(a,.2,n/2-1,3,2,'Driver channel\n5 V / 0 V','#253c53')
 a.plot([3.2,5,5],[n/2,n/2,n-.1],color='#29876d',lw=2);a.plot([5,5],[0,n-.1],color='#29876d',lw=2)
 for i in range(n):
  y=i+.4
  a.plot([5,11],[y,y],color='#29876d',lw=1.6)
  block(a,7,y-.27,2.7,.54,f'Ron{i+1} / Roff{i+1}','#29876d')
  block(a,11,y-.3,1.8,.6,f'Q{i+1}','#253c53')
  a.plot([12.8,14,14],[y,y,-.3],color='#29876d',ls=':',lw=1.2)
 a.plot([14,1.7,1.7],[-.3,-.3,n/2-1],color='#29876d',ls=':',lw=1.4)
 a.text(14.3,n/2,'Dedicated source\nKelvin returns\n\nReference:\nHS bank → SW\nLS bank → DC−',fontsize=10,va='center')
fig.suptitle('Gate-drive architecture | Repeat for upper AND lower bank',fontsize=18,fontweight='bold')
fig.supxlabel('Six channels per three-phase inverter, often three half-bridge driver ICs. Diagram shows one channel only.\nRon/Roff blocks require separate driver outputs or a directional resistor/diode network; not two plain resistors in parallel.\nFanout is functional, not routing: minimize and match each gate/return pair. Do not parallel separate driver outputs.',fontsize=10)
for ext in ('png','svg'):fig.savefig(OUT/f'gate_driver_4_5_6.{ext}',dpi=160)

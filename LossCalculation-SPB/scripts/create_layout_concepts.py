from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'/'layout_concepts'
OUT.mkdir(parents=True,exist_ok=True)
C={'plus':'#c74646','minus':'#2864a0','sw':'#df9c24','gate':'#28866e','fet':'#24374d'}
def box(ax,x,y,w,h,label,color,fs=9):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=color,edgecolor='white',lw=1.2))
    ax.text(x+w/2,y+h/2,label,ha='center',va='center',color='white',fontsize=fs)
def panel(ax,n):
    width=7*n+3
    ax.set_xlim(-6,width+2); ax.set_ylim(-5,23); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(f'{n} parallel per switch | {2*n} FETs per leg',loc='left',fontsize=13,fontweight='bold',pad=12)
    ax.add_patch(Rectangle((0,0),width,20,facecolor='#f0f4f6',edgecolor='#9babba'))
    box(ax,1,18,width-2,1.2,'DC+ distribution',C['plus'])
    box(ax,1,1,width-2,1.2,'DC− distribution / close return layer',C['minus'],8)
    box(ax,1,9.4,width-2,1.2,'SW → phase output',C['sw'],8)
    for i in range(n):
        x=3+7*i
        box(ax,x,12,3,5,f'H{i+1}',C['fet'])
        box(ax,x,3,3,5,f'L{i+1}',C['fet'])
        box(ax,x,20.1,3,1.5,f'C{i+1}',C['plus'],8)
        ax.plot([x+1.5,x+1.5],[17,18],color=C['plus'],lw=2)
        ax.plot([x+1.5,x+1.5],[10.6,12],color=C['sw'],lw=2)
        ax.plot([x+1.5,x+1.5],[8,9.4],color=C['sw'],lw=2)
        ax.plot([x+1.5,x+1.5],[2.2,3],color=C['minus'],lw=2)
        # Local capacitor positive terminal and conceptual inner-layer return.
        ax.plot([x+.7,x+.7],[19.2,20.1],color=C['plus'],lw=1.5)
        ax.plot([x+2.3,x+4.2,x+4.2],[20.1,20.1,1.6],color=C['minus'],lw=1.4,ls='--')
        for y in (5.5,14.5):
            box(ax,x-1.8,y-.9,1.4,1.8,'Rg',C['gate'],6)
            ax.plot([x-.4,x],[y,y],color=C['gate'],lw=1.5)
            ax.plot([x-1.8,x],[y-1.2,y-1.2],color=C['gate'],ls=':',lw=1.5)
        ax.text(x+1.5,-1,f'cell {i+1}',ha='center',fontsize=8,color='#526275')
    ax.text(width/2,-3.3,f'Repeat this leg three times: {6*n} FETs per inverter',ha='center',fontsize=10)
fig,axes=plt.subplots(3,1,figsize=(12,15),layout='constrained')
for ax,n in zip(axes,(4,5,6)): panel(ax,n)
fig.suptitle('EPC2361 | Distributed half-bridge placement concepts',fontsize=19,fontweight='bold')
fig.supxlabel('CONCEPT ONLY • FET envelopes 3 × 5 mm; pitch 7 mm assumed • Lines show connectivity, not manufacturable routing\nBlue dashed: local capacitor return on inner layer • Green: individual gate resistor network + Kelvin return • Drivers omitted',fontsize=10)
for ext in ('png','svg'): fig.savefig(OUT/f'parallel_4_5_6.{ext}',dpi=180)
plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(14,7),layout='constrained')
a=axes[0]; a.set_xlim(0,12);a.set_ylim(0,15);a.axis('off');a.set_title('One repeated cell: electrical intent',loc='left',fontweight='bold')
box(a,5,9,3,2,'Upper FET',C['fet']);box(a,5,4,3,2,'Lower FET',C['fet'])
for y,label,col in [(13,'DC+',C['plus']),(7.5,'SW',C['sw']),(2,'DC−',C['minus'])]:
    a.plot([6.5 if label=='SW' else 4,10],[y,y],color=col,lw=3);a.text(10.2,y,label,va='center',color=col)
a.plot([6.5,6.5],[11,13],color=C['plus'],lw=2);a.plot([6.5,6.5],[6,9],color=C['sw'],lw=2);a.plot([6.5,6.5],[2,4],color=C['minus'],lw=2)
a.plot([4,4],[13,9],color=C['plus'],lw=2);a.plot([4,4],[6,2],color=C['minus'],lw=2)
box(a,3.3,6,1.4,3,'C HF',C['plus'])
a.text(.2,13,'Local MLCC across\nDC+ and DC−',fontsize=10)
for y,ref in [(10,'SW'),(5,'DC−')]:
    box(a,.2,y-.4,2.2,.9,'Ron / Roff',C['gate'])
    a.plot([2.4,5],[y,y],color=C['gate'],lw=2)
    a.plot([.2,5],[y-.8,y-.8],color=C['gate'],ls=':',lw=2)
    a.text(.2,y-1.5,f'Kelvin return → {ref}',fontsize=9,color=C['gate'])
a.text(.2,.3,'Each FET gets its own split-resistor network.\nShared driver fanout/return must be balanced;\ndriver impedance is counted once per bank.',fontsize=10)
b=axes[1];b.set_xlim(0,12);b.set_ylim(0,15);b.axis('off');b.set_title('Section: return layer and water cooling',loc='left',fontweight='bold')
box(b,1,10,10,2,'Water cold plate', '#668599')
box(b,1,9.2,10,.65,'Electrically insulating TIM','#9776a6')
box(b,2,7.4,3,1.7,'Upper FET\ntop = SW',C['fet'])
box(b,7,7.4,3,1.7,'Lower FET\ntop = DC−',C['fet'])
box(b,1,6.8,10,.35,'',C['plus']);box(b,1,5.9,10,.65,'PCB dielectric','#d4c899');box(b,1,5.5,10,.3,'',C['minus'])
b.text(1,4.7,'L1: power copper / pads (segmented by net)',fontsize=10)
b.text(1,4,'L2: close return beneath commutation path',fontsize=10)
b.annotate('h: use actual stackup',xy=(10.5,6.5),xytext=(6,3),arrowprops={'arrowstyle':'->'},fontsize=10)
b.text(1,1,'Do not join SW and DC− through the cold plate.\nKeep fasteners clear of power copper; define\nTIM compression and mechanical stops.\nLayer thicknesses shown exaggerated.',fontsize=10)
fig.suptitle('Layout details to preserve when increasing parallel count',fontsize=17,fontweight='bold')
fig.supxlabel('Functional diagrams only — package pin geometry, copper clearances, via arrays and driver routing require PCB CAD.',fontsize=10)
for ext in ('png','svg'):fig.savefig(OUT/f'cell_and_cooling.{ext}',dpi=180)

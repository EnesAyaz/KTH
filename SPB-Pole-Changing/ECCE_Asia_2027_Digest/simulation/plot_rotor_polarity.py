"""Diagnose physical rotor polarity using signed FEM fields, not |B| colors."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'simulation/vendor'))
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from matplotlib.patches import Circle
from matplotlib import font_manager
for f in ['times.ttf','timesbd.ttf']:
 p=Path('C:/Windows/Fonts')/f
 if p.exists():font_manager.fontManager.addfont(p)
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'mathtext.fontset':'stix','svg.fonttype':'none'})
data=np.load(ROOT/'simulation/results_basic_fea/basic_fea_fields.npz');xy=data['xy'];tri=data['tri'];center=xy[tri].mean(axis=1);rad=np.linalg.norm(center,axis=1)
mesh=mtri.Triangulation(xy[:,0],xy[:,1],tri);finder=mesh.get_trifinder();theta=np.linspace(0,2*np.pi,2880,endpoint=False)
idx=finder(.0805*np.cos(theta),.0805*np.sin(theta));assert (idx>=0).all()
fig=plt.figure(figsize=(7,5.4));gs=fig.add_gridspec(2,2,height_ratios=[1.3,1],hspace=.35,wspace=.18);bottom=fig.add_subplot(gs[1,:]);report={}
for k,(field,mode,color) in enumerate([('B12','12-pole setting','#111111'),('B6','6-pole setting','#b31b1b')]):
 ax=fig.add_subplot(gs[0,k]);B=data[field];br=(B*center/rad[:,None]).sum(axis=1)
 tr=mtri.Triangulation(xy[:,0]*1000,xy[:,1]*1000,tri);tr.set_mask((data['material']!=1)|(rad>.080))
 im=ax.tripcolor(tr,facecolors=br,cmap='coolwarm',vmin=-1.5,vmax=1.5,rasterized=True)
 for radius in [25,80]:ax.add_patch(Circle((0,0),radius,fill=False,color='#333333',lw=.5))
 sampled=B[idx];gap=sampled[:,0]*np.cos(theta)+sampled[:,1]*np.sin(theta)
 signs=[]
 for j in range(12):
  a=j*np.pi/6;delta=(theta-a+np.pi)%(2*np.pi)-np.pi;sgn=np.sign(gap[abs(delta)<np.deg2rad(3)].mean());signs.append('N' if sgn>0 else 'S')
  start,end=(81,91) if sgn>0 else (91,81)
  ax.annotate('',xy=(end*np.cos(a),end*np.sin(a)),xytext=(start*np.cos(a),start*np.sin(a)),arrowprops={'arrowstyle':'->','lw':.8,'color':'#b31b1b' if sgn>0 else '#184a78'})
  ax.text(101*np.cos(a),101*np.sin(a),signs[-1],ha='center',va='center',color='#b31b1b' if sgn>0 else '#184a78',fontsize=9,fontweight='bold')
 ax.set_aspect('equal');ax.set_xlim(-112,112);ax.set_ylim(-112,112);ax.axis('off');ax.set_title(mode+' — rotor only',fontsize=11,pad=1)
 bottom.plot(theta*180/np.pi,gap,color=color,lw=1.05,label=mode)
 harmonics={str(p):float(2*abs(np.mean(gap*np.exp(-1j*p*theta)))) for p in range(1,19)}
 crossings=int(np.sum(np.sign(gap)!=np.sign(np.roll(gap,1))));assert crossings==[12,6][k],crossings
 report[mode]={'signs_at_12_physical_rotor_sites':signs,'signed_airgap_zero_crossings':crossings,'harmonic_amplitudes_T_by_pole_pair_order':harmonics,'gap_sample_radius_mm':80.5}
bottom.axhline(0,color='#777777',lw=.65);bottom.set(xlim=(0,360),xlabel='Mechanical angle (degrees)',ylabel=r'Signed air-gap $B_r$ (T)');bottom.set_xticks(np.arange(0,361,60));bottom.grid(color='#dddddd',lw=.4);bottom.legend(loc='upper center',bbox_to_anchor=(.5,1.16),ncol=2,frameon=False,fontsize=9)
fig.subplots_adjust(left=.10,right=.86,bottom=.15,top=.94)
cax=fig.add_axes([.89,.57,.018,.30]);cb=fig.colorbar(im,cax=cax,extend='both');cb.set_ticks([-1.5,0,1.5]);cb.set_label(r'Rotor steel $B_r$ (T)')
fig.text(.48,.025,'Red: outward flux (N); blue: inward flux (S). Same physical rotor sites in both modes.',ha='center',fontsize=9)
for ext in ['png','svg']:fig.savefig(ROOT/'figures'/('rotor_polarity_check.'+ext),dpi=450,bbox_inches='tight')
(ROOT/'simulation/results_saturation_screen/rotor_polarity_check.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:{'signs':v['signs_at_12_physical_rotor_sites'],'crossings':v['signed_airgap_zero_crossings']} for k,v in report.items()},indent=2))

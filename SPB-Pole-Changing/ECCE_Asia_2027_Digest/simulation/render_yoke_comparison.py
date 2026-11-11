"""Matched fine-mesh, unchanged-excitation baseline/candidate comparison."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'simulation/vendor'))
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from matplotlib.colors import LinearSegmentedColormap,BoundaryNorm
from matplotlib.patches import Circle
from matplotlib import font_manager
for f in ['times.ttf','timesbd.ttf']:
 p=Path('C:/Windows/Fonts')/f
 if p.exists():font_manager.fontManager.addfont(p)
plt.rcParams.update({'font.family':'Times New Roman','font.size':11,'svg.fonttype':'none'})
folder=ROOT/'simulation/results_saturation_screen'
datasets=[np.load(ROOT/'simulation/results_basic_fea/basic_fea_fields.npz'),np.load(folder/'thinner_yoke_fine.npz')]
cmap=LinearSegmentedColormap.from_list('reference_style',['#00ffff','#00eebb','#8dff00','#ffff00','#ff9b00','#ff1a00','#ff00ee'],N=20)
levels=np.linspace(0,2,21);norm=BoundaryNorm(levels,cmap.N,clip=True)
fig,axes=plt.subplots(2,2,figsize=(6.8,6.6));report={}
for col,(f,outer,label) in enumerate(zip(datasets,[140,125],['Baseline: 25-mm stator yoke','Candidate: 10-mm stator yoke'])):
 xy=f['xy'];tri=f['tri'];v=xy[tri];c=v.mean(axis=1);r=np.linalg.norm(c,axis=1);u=v[:,1]-v[:,0];w=v[:,2]-v[:,0];area=(u[:,0]*w[:,1]-u[:,1]*w[:,0])/2;steel=f['material']==1
 key=['baseline','candidate'][col];report[key]={}
 for row,(name,mode) in enumerate([('B12','12-pole setting'),('B6','6-pole setting')]):
  ax=axes[row,col];b=np.linalg.norm(f[name],axis=1);tr=mtri.Triangulation(xy[:,0]*1000,xy[:,1]*1000,tri);tr.set_mask(~steel)
  im=ax.tripcolor(tr,facecolors=b,cmap=cmap,norm=norm,rasterized=True)
  lines=mtri.Triangulation(xy[:,0]*1000,xy[:,1]*1000,tri);lines.set_mask(r>outer/1000);az=f['A12' if row==0 else 'A6']
  ax.tricontour(lines,az,levels=np.linspace(az.min()*.95,az.max()*.95,23),colors='#222',linewidths=.25,linestyles='solid')
  for radius in [25,80,81,outer]:ax.add_patch(Circle((0,0),radius,fill=False,color='#333',lw=.4))
  ax.set_aspect('equal');ax.set_xlim(-145,145);ax.set_ylim(-145,145);ax.axis('off')
  if row==0:ax.set_title(label,fontsize=11,pad=3)
  if col==0:ax.text(-155,0,mode,rotation=90,ha='center',va='center',fontsize=11)
  result={}
  for region,sel in [('yoke',r>=.115),('teeth',(r>=.081)&(r<.115)),('rotor',r<.080)]:
   m=steel&sel;z=b[m];a=area[m];order=np.argsort(z);cum=np.cumsum(a[order])/a.sum()
   result[region]={'mean_T':float(z@a/a.sum()),'p95_T':float(np.interp(.95,cum,z[order])),'max_T':float(z.max()),'area_mm2':float(a.sum()*1e6),'area_above_1p5T_percent':float(a[z>1.5].sum()/a.sum()*100)}
  report[key][mode]=result
fig.subplots_adjust(left=.06,right=.87,bottom=.065,top=.94,wspace=.05,hspace=.05)
cb=fig.colorbar(im,cax=fig.add_axes([.91,.28,.02,.46]),boundaries=levels,extend='max');cb.set_ticks([0,.5,1,1.5,2]);cb.set_label('|B| in steel (T)')
fig.text(.48,.025,'Same no-load excitation, synthetic B–H law, and fine mesh; colors clipped above 2 T',ha='center',fontsize=9)
for ext in ['png','svg']:fig.savefig(ROOT/'figures'/('stator_yoke_comparison.'+ext),dpi=450,bbox_inches='tight')
report['scope']='Same 720 angular divisions, unchanged excitation, no-load only; not loaded torque or loss validation'
base=report['baseline']['6-pole setting'];new=report['candidate']['6-pole setting']
report['stator_steel_area_reduction_percent']=100*(1-(new['yoke']['area_mm2']+new['teeth']['area_mm2'])/(base['yoke']['area_mm2']+base['teeth']['area_mm2']))
(folder/'fine_mesh_region_comparison.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'stator_steel_area_reduction_percent':report['stator_steel_area_reduction_percent'],'six_pole_yoke_p95_T':[base['yoke']['p95_T'],new['yoke']['p95_T']]},indent=2))

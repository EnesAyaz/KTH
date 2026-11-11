"""Controlled no-load sizing sensitivity; no change to the digest baseline."""
from pathlib import Path
import sys,ast,json
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'simulation/vendor'))
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from matplotlib.colors import LinearSegmentedColormap,BoundaryNorm
from matplotlib.patches import Circle
from matplotlib import font_manager
MU0=4*np.pi*1e-7;FIXED=np.array([0,3,4,7,8,11]);WOUND=np.array([1,2,5,6,9,10])
# Load only the solver definition: do not execute the baseline output workflow.
tree=ast.parse((ROOT/'simulation/basic_he_ipm_fea.py').read_text(encoding='utf-8'))
definition=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='solve')
exec(compile(ast.Module(body=[definition],type_ignores=[]),'shared_fea_solver','exec'))
OUT=ROOT/'simulation/results_saturation_screen';OUT.mkdir(exist_ok=True)
for f in ['times.ttf','timesbd.ttf']:
 p=Path('C:/Windows/Fonts')/f
 if p.exists():font_manager.fontManager.addfont(p)
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'svg.fonttype':'none'})

def stats(data,outer):
 c=data['center'];rad=np.linalg.norm(c,axis=1);steel=data['mat']==1;result={}
 for name,case in data['cases'].items():
  b=np.linalg.norm(case['B'],axis=1);result[name]={}
  for region,sel in [('yoke',rad>=.115),('teeth',(rad>=.081)&(rad<.115)),('rotor',rad<.080)]:
   m=steel&sel;z=b[m];a=data['area'][m];order=np.argsort(z);cum=np.cumsum(a[order])/a.sum()
   result[name][region]={'mean_T':float(z@a/a.sum()),'area_weighted_p95_T':float(np.interp(.95,cum,z[order])),'maximum_T':float(z.max()),'area_above_1p5T_percent':float(a[z>1.5].sum()/a.sum()*100),'area_above_2T_percent':float(a[z>2].sum()/a.sum()*100),'steel_area_mm2':float(a.sum()*1e6)}
  result[name]['selected_airgap_harmonic_T']=case['selected_airgap_amplitude_T'];result[name]['alternate_harmonic_ratio']=case['alternate_ratio'];result[name]['nonlinear_residual']=case['nonlinear_residual']
 return result

configs=[('baseline',140,2.4,'25-mm yoke; baseline teeth'),('thinner_yoke',125,2.4,'10-mm yoke; same teeth'),('thinner_yoke_narrower_teeth',125,3.2,'10-mm yoke; narrower teeth')]
results={};allfields={}
for key,outer,slot,label in configs:
 if '--fine-yoke' in sys.argv and key=='thinner_yoke':
  data=solve(720,1,outer,slot)
 elif '--fine-yoke' in sys.argv:
  continue
 else:
  data=solve(360,1,outer,slot)
 allfields[key]=data
 results[key]={'stator_outer_radius_mm':outer,'yoke_thickness_mm':outer-115,'slot_half_angle_deg':slot,'tooth_angle_deg':10-2*slot,'angular_divisions':720 if '--fine-yoke' in sys.argv else 360,'stats':stats(data,outer)}
 np.savez_compressed(OUT/(key+('_fine' if '--fine-yoke' in sys.argv else '')+'.npz'),xy=data['xy'],tri=data['tri'],material=data['mat'],A12=data['cases']['12_pole']['A'],B12=data['cases']['12_pole']['B'],A6=data['cases']['6_pole']['A'],B6=data['cases']['6_pole']['B'])
 print(key,json.dumps(results[key]['stats']),flush=True)
if '--fine-yoke' in sys.argv:
 (OUT/'thinner_yoke_fine.json').write_text(json.dumps(results,indent=2))
 sys.exit(0)
report={'scope':'Three controlled nonlinear no-load cases, same coarse mesh, fixed PMs and field-current densities; not rated-load optimization','display':'Identical 0-2 T discrete palette, steel only; white nonsteel; colorbar extension marks values >2 T','saturation_caveat':'Area above 1.5 or 2 T is a flux-density diagnostic, not a universal saturation criterion; material law is synthetic','cases':results}
(OUT/'sizing_comparison.json').write_text(json.dumps(report,indent=2))

cmap=LinearSegmentedColormap.from_list('reference_style',['#00ffff','#00eebb','#8dff00','#ffff00','#ff9b00','#ff1a00','#ff00ee'],N=20)
levels=np.linspace(0,2,21);norm=BoundaryNorm(levels,cmap.N,clip=True)
fig,axes=plt.subplots(2,3,figsize=(9,6.1))
for col,(key,outer,slot,label) in enumerate(configs):
 data=allfields[key];c=data['center'];rad=np.linalg.norm(c,axis=1)
 for row,name in enumerate(['12_pole','6_pole']):
  ax=axes[row,col];tr=mtri.Triangulation(data['xy'][:,0]*1000,data['xy'][:,1]*1000,data['tri']);tr.set_mask(data['mat']!=1)
  b=np.linalg.norm(data['cases'][name]['B'],axis=1);im=ax.tripcolor(tr,facecolors=b,cmap=cmap,norm=norm,rasterized=True)
  lines=mtri.Triangulation(data['xy'][:,0]*1000,data['xy'][:,1]*1000,data['tri']);lines.set_mask(rad>outer/1000)
  az=data['cases'][name]['A'];ax.tricontour(lines,az,levels=np.linspace(az.min()*.95,az.max()*.95,23),colors='#222222',linewidths=.25,linestyles='solid')
  for r in [25,80,81,outer]:ax.add_patch(Circle((0,0),r,fill=False,lw=.5,color='#333333'))
  ax.set_aspect('equal');ax.set_xlim(-145,145);ax.set_ylim(-145,145);ax.axis('off')
  if row==0:ax.set_title(label,fontsize=10,pad=5)
  if col==0:ax.text(-155,0,name.replace('_',' '),rotation=90,ha='center',va='center',fontsize=11)
fig.subplots_adjust(left=.05,right=.91,bottom=.07,top=.93,hspace=.06,wspace=.04)
cb=fig.colorbar(im,cax=fig.add_axes([.94,.27,.015,.47]),boundaries=levels,extend='max');cb.set_label('|B| in steel (T)');cb.set_ticks([0,.5,1,1.5,2])
fig.text(.49,.025,'Same no-load excitation and material law; not a rated-load design comparison',ha='center',fontsize=10)
for ext in ['png','svg']:fig.savefig(ROOT/'figures'/('stator_sizing_sensitivity.'+ext),dpi=450,bbox_inches='tight')
print('Saved sizing comparison and identical-scale flux maps.',flush=True)

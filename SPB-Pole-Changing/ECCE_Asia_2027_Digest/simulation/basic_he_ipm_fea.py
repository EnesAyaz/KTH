"""Exploratory 2-D nonlinear magnetostatic FEM; not a validated truck motor.

P1 triangular Az elements on a conforming polar grid; material interfaces are
classified at centroids. Fixed PM poles and wound poles follow ++-- / +-+-
patterns. Nonlinear synthetic steel; no stator current, torque, losses, or speed solve.
"""
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'simulation/vendor'))
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from matplotlib.patches import Circle,Wedge
from matplotlib import font_manager
for f in ['times.ttf','timesi.ttf','timesbd.ttf']:
 p=Path('C:/Windows/Fonts')/f
 if p.exists():font_manager.fontManager.addfont(p)
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'mathtext.fontset':'stix','svg.fonttype':'none','axes.linewidth':.6})
OUT=ROOT/'simulation/results_basic_fea';OUT.mkdir(exist_ok=True)
FIG=ROOT/'figures'
SELECTED_YOKE='--yoke-17p5' in sys.argv
MU0=4*np.pi*1e-7
FIXED=np.array([0,3,4,7,8,11]);WOUND=np.array([1,2,5,6,9,10])
PARAM={'slots':36,'rotor_pole_sites':12,'shaft_radius_mm':25,'rotor_radius_mm':80,'airgap_mm':1,'stator_outer_radius_mm':140,'slot_outer_radius_mm':115,'PM_remanence_T':.7,'steel_initial_mu_r':1000,'synthetic_BH_knee_T':1.5,'synthetic_BH_extra_H_at_knee_A_m':300,'PM_mu_r':1.05,'coil_basis_J_A_m2':1e6,'stator_current_A':0,'outer_boundary':'Az = 0 at r = 150 mm','interface':'polar mesh, centroid-classified material interfaces','material_model':'nonlinear isotropic synthetic B-H curve; no losses'}

def solve(nt,refine,stator_outer_mm=140,slot_half_angle_deg=2.4):
 anchors=[(0,25,8),(25,55,12),(55,64,5),(64,70,6),(70,76,6),(76,80,5),(80,81,5),(81,84,4),(84,115,12),(115,140,10),(140,150,4)]
 radii=np.unique(np.concatenate([np.linspace(a,b,n*refine+1) for a,b,n in anchors]))[1:]/1000
 theta=np.arange(nt)*2*np.pi/nt
 xy=np.vstack([[[0,0]],np.stack([(radii[:,None]*np.cos(theta)).ravel(),(radii[:,None]*np.sin(theta)).ravel()],axis=1)])
 triangles=[]
 for k in range(nt):triangles.append([0,1+k,1+(k+1)%nt])
 for ir in range(len(radii)-1):
  a=1+ir*nt;b=a+nt
  for k in range(nt):
   k1=(k+1)%nt
   triangles.extend([[a+k,b+k,b+k1],[a+k,b+k1,a+k1]])
 tri=np.asarray(triangles);v=xy[tri];center=v.mean(axis=1);rad=np.linalg.norm(center,axis=1);ang=np.arctan2(center[:,1],center[:,0])%(2*np.pi)
 det=(v[:,1,0]-v[:,0,0])*(v[:,2,1]-v[:,0,1])-(v[:,2,0]-v[:,0,0])*(v[:,1,1]-v[:,0,1]);area=det/2
 assert area.min()>0
 grad=np.stack([np.stack([v[:,1,1]-v[:,2,1],v[:,2,0]-v[:,1,0]],axis=1),np.stack([v[:,2,1]-v[:,0,1],v[:,0,0]-v[:,2,0]],axis=1),np.stack([v[:,0,1]-v[:,1,1],v[:,1,0]-v[:,0,0]],axis=1)],axis=1)/det[:,None,None]
 mat=np.zeros(len(tri),dtype=int) # 0 air, 1 steel, 2 PM, 3 rotor copper, 4 stator copper
 mat[((rad>=.025)&(rad<.080))|((rad>=.081)&(rad<stator_outer_mm/1000))]=1
 slotdelta=(ang+np.pi/36)%(2*np.pi/36)-np.pi/36
 slots=(rad>=.081)&(rad<.115)&(abs(slotdelta)<np.deg2rad(slot_half_angle_deg));mat[slots]=4
 pole=np.floor((ang+np.pi/12)/(np.pi/6)).astype(int)%12
 delta=(ang-pole*np.pi/6+np.pi)%(2*np.pi)-np.pi
 barrier=(rad>=.064)&(rad<.080)&(abs(delta)>=np.deg2rad(13));mat[barrier]=0
 pm=np.isin(pole,FIXED)&(rad>=.064)&(rad<.070)&(abs(delta)<np.deg2rad(13));mat[pm]=2
 coils=np.isin(pole,WOUND)&(rad>=.055)&(rad<.076)&(abs(abs(delta)-np.deg2rad(10))<np.deg2rad(2.1));mat[coils]=3
 mur=np.ones(len(tri));mur[mat==1]=1000;mur[mat==2]=1.05;nu=1/(MU0*mur)
 sign=(-1.)**pole
 br=np.zeros((len(tri),2));br[pm]=.7*sign[pm,None]*center[pm]/rad[pm,None]
 J=np.zeros(len(tri));J[coils]=1e6*sign[coils]*np.sign(delta[coils])
 local=area[:,None,None]*nu[:,None,None]*np.einsum('tik,tjk->tij',grad,grad)
 K=coo_matrix((local.ravel(),(np.repeat(tri,3,axis=1).ravel(),np.tile(tri,(1,3)).ravel())),shape=(len(xy),len(xy))).tocsc()
 # curl(v Az) = (d_y v, -d_x v): RHS int nu Br dot curl(v) + J v.
 fpm=area[:,None]*nu[:,None]*(br[:,0,None]*grad[:,:,1]-br[:,1,None]*grad[:,:,0]);fc=area[:,None]*J[:,None]*np.ones((1,3))/3
 F=np.zeros((len(xy),2))
 for k in range(3):np.add.at(F[:,0],tri[:,k],fpm[:,k]);np.add.at(F[:,1],tri[:,k],fc[:,k])
 free=np.arange(1+(len(radii)-1)*nt);lu=splu(K[free][:,free]);A=np.zeros_like(F);A[free]=lu.solve(F[free])
 residual=float(np.linalg.norm((K@A-F)[free])/np.linalg.norm(F[free]));assert residual<1e-8
 B=np.stack([np.einsum('tik,ti->tk',grad,A[tri,j]) for j in range(2)],axis=2)
 B=np.stack([B[:,1,:],-B[:,0,:]],axis=1)
 # An exact mesh ring lies at midgap; obtain Br from the derivative of Az along it.
 gap=rad>=.080;gap&=rad<.081
 th=ang[gap];brgap=(B[gap,:,0]*center[gap]/rad[gap,None]).sum(axis=1);brcoil=(B[gap,:,1]*center[gap]/rad[gap,None]).sum(axis=1)
 weights=area[gap]/area[gap].sum()
 def harmonic(values,p):return 2*np.sum(weights*values*np.exp(-1j*p*th))
 # Select field current by minimizing the alternate selected airgap harmonic.
 cases={}
 for name,target,other,expect in [('12_pole',6,3,1),('6_pole',3,6,-1)]:
  z=harmonic(brgap,other);w=harmonic(brcoil,other);alpha=float(-np.real(z*np.conj(w))/abs(w)**2)
  assert np.sign(alpha)==expect,(name,alpha)
  screened_alpha=alpha
  alpha={'12_pole':6.2,'6_pole':-6.7}[name]
  # Monotone synthetic steel law H = nu0 B + c |B|^8 B.
  # Newton solve of the convex magnetic energy with backtracking.
  C=np.stack([grad[:,:,1],-grad[:,:,0]],axis=2)
  hard=np.where(mat==1,300/1.5**9,0.);rhs=F[:,0]+alpha*F[:,1]
  az=np.zeros(len(xy));hist=[]
  def state(a):
   bv=np.einsum('tik,ti->tk',C,a[tri]);b2=(bv*bv).sum(axis=1)
   rel=nu+hard*b2**4
   energy=float(np.sum(area*(.5*nu*b2+hard*b2**5/10))-a@rhs)
   return bv,b2,rel,energy
  for iteration in range(45):
   bv,b2,rel,energy=state(az);dot=np.einsum('tik,tk->ti',C,bv)
   localr=area[:,None]*rel[:,None]*dot;res=-rhs.copy()
   for k in range(3):np.add.at(res,tri[:,k],localr[:,k])
   err=float(np.linalg.norm(res[free])/np.linalg.norm(rhs[free]));hist.append(err)
   if err<2e-8:break
   tangent=area[:,None,None]*(rel[:,None,None]*np.einsum('tik,tjk->tij',C,C)+(8*hard*b2**3)[:,None,None]*dot[:,:,None]*dot[:,None,:])
   jac=coo_matrix((tangent.ravel(),(np.repeat(tri,3,axis=1).ravel(),np.tile(tri,(1,3)).ravel())),shape=K.shape).tocsc()
   step=np.zeros(len(xy));step[free]=splu(jac[free][:,free]).solve(-res[free]);dec=float(res@step);factor=1.
   for back in range(35):
    trial=az+factor*step
    if state(trial)[3]<=energy+1e-4*factor*dec+1e-12:break
    factor*=.5
   az=trial
  assert err<1e-6,(name,err,hist)
  bfield=state(az)[0];bg=(bfield[gap]*center[gap]/rad[gap,None]).sum(axis=1)
  h={str(p):float(abs(harmonic(bg,p))) for p in range(1,19)}
  cases[name]={'alpha':alpha,'linear_screen_alpha':screened_alpha,'nonlinear_residual':err,'Newton_iterations':iteration,'A':az,'B':bfield,'harmonics_T':h,'selected_airgap_amplitude_T':h[str(target)],'alternate_ratio':h[str(other)]/h[str(target)],'Bmax_T':float(np.linalg.norm(bfield,axis=1).max()),'Jpeak_A_m2':abs(alpha)*1e6}
  print(nt,name,'excitation',alpha,'target B',h[str(target)],'alternate ratio',cases[name]['alternate_ratio'],flush=True)
 return {'xy':xy,'tri':tri,'mat':mat,'center':center,'area':area,'cases':cases,'nodes':len(xy),'elements':len(tri),'residual':residual}

if '--plot-only' not in sys.argv and not SELECTED_YOKE:
 coarse=solve(360,1);fine=solve(720,1)
 summary={'parameters':PARAM,'fixed_PM_sites_zero_based':FIXED.tolist(),'wound_sites_zero_based':WOUND.tolist(),'source_pattern':'12-pole +-+-; 6-pole ++--; reverse wound sites; PM polarities fixed','excitation_choice':'Fixed +6.2 and -6.7 A/mm2 excitations on both meshes, selected after the preliminary linear screen; nonlinear residual harmonics are reported, not forced to zero','coarse':{},'fine':{},'mesh_sensitivity':{}}
 for label,data in [('coarse',coarse),('fine',fine)]:
  summary[label]={'nodes':data['nodes'],'elements':data['elements'],'relative_linear_residual':data['residual'],'cases':{n:{k:v for k,v in c.items() if k not in ['A','B']} for n,c in data['cases'].items()}}
 for n in fine['cases']:
  summary['mesh_sensitivity'][n]=abs(fine['cases'][n]['selected_airgap_amplitude_T']/coarse['cases'][n]['selected_airgap_amplitude_T']-1)
 summary['limits']=['Exploratory geometry, not copied dimensions from Conto/Bianchi','Synthetic monotone B-H law; no measured steel curve or loss coefficients','Only no-load magnetostatics; no torque, losses, back-EMF or speed curves derived','Centroid-classified geometry and one angular mesh refinement are not a complete convergence study','No demagnetization, coil insulation, centrifugal stress, cooling, end winding or field supply feasibility','Rotor excitation amplitude is tuned per mode; fixed magnitude reversal is not demonstrated']
 (OUT/'basic_fea_results.json').write_text(json.dumps(summary,indent=2))
 np.savez_compressed(OUT/'basic_fea_fields.npz',xy=fine['xy'],tri=fine['tri'],material=fine['mat'],A12=fine['cases']['12_pole']['A'],A6=fine['cases']['6_pole']['A'],B12=fine['cases']['12_pole']['B'],B6=fine['cases']['6_pole']['B'])
 
else:
 cache=np.load(ROOT/'simulation/results_saturation_screen/yoke_17.5mm_fine.npz' if SELECTED_YOKE else OUT/'basic_fea_fields.npz')
 fine={'xy':cache['xy'],'tri':cache['tri'],'mat':cache['material'],'center':cache['xy'][cache['tri']].mean(axis=1),'cases':{'12_pole':{'A':cache['A12'],'B':cache['B12']},'6_pole':{'A':cache['A6'],'B':cache['B6']}}}

def save(fig,name):
 if SELECTED_YOKE:name+='_17p5mm'
 fig.savefig(FIG/(name+'.png'),dpi=600,bbox_inches='tight',pad_inches=.035);fig.savefig(FIG/(name+'.svg'),bbox_inches='tight',pad_inches=.035);plt.close(fig)
def outlines(ax):
 for radius in [25,80,81,115,132.5 if SELECTED_YOKE else 140]:ax.add_patch(Circle((0,0),radius,fill=False,edgecolor='#303030',lw=.35))
 for k in range(36):
  ax.add_patch(Wedge((0,0),115,k*10-2.4,k*10+2.4,width=34,fill=False,edgecolor='#303030',lw=.3))
 for j in FIXED:ax.add_patch(Wedge((0,0),70,j*30-13,j*30+13,width=6,fill=False,edgecolor='black',lw=.45))
 for j in range(12):
  for sg in [-1,1]:ax.add_patch(Wedge((0,0),80,j*30+sg*14-1,j*30+sg*14+1,width=16,fill=False,edgecolor='black',lw=.3))
 for j in WOUND:
  for sg in [-1,1]:ax.add_patch(Wedge((0,0),76,j*30+sg*10-2.1,j*30+sg*10+2.1,width=21,fill=False,edgecolor='black',lw=.35))
 ax.set_aspect('equal');ax.set_xlim(-144,144);ax.set_ylim(-144,144);ax.axis('off')

def pole_labels(ax,name):
 center=fine['center'];radius=np.linalg.norm(center,axis=1);theta=np.arctan2(center[:,1],center[:,0]);gap=(radius>.080)&(radius<.081)
 br=(fine['cases'][name]['B']*center/radius[:,None]).sum(axis=1)
 groups=[[j] for j in range(12)] if name=='12_pole' else [[2*j,2*j+1] for j in range(6)]
 for group in groups:
  values=[]
  for j in group:
   delta=(theta-j*np.pi/6+np.pi)%(2*np.pi)-np.pi
   values.append(float(br[gap&(abs(delta)<np.deg2rad(3))].mean()))
  assert all(np.sign(v)==np.sign(values[0]) for v in values)
  angle=np.mean(group)*np.pi/6;label='N' if np.mean(values)>0 else 'S'
  ax.text(150*np.cos(angle),150*np.sin(angle),label,ha='center',va='center',fontsize=8.5,fontweight='bold',color='#b31b1b' if label=='N' else '#111111',bbox={'facecolor':'white','edgecolor':'none','pad':.25},zorder=10)
 ax.set_xlim(-162,162);ax.set_ylim(-162,162)

triang=mtri.Triangulation(fine['xy'][:,0]*1000,fine['xy'][:,1]*1000,fine['tri']);triang.set_mask(np.linalg.norm(fine['center'],axis=1)>(.1325 if SELECTED_YOKE else .140))
fieldtri=mtri.Triangulation(fine['xy'][:,0]*1000,fine['xy'][:,1]*1000,fine['tri'])
fieldtri.set_mask(fine['mat']!=1) if SELECTED_YOKE else fieldtri.set_mask(np.linalg.norm(fine['center'],axis=1)>.140)
field_cmap=matplotlib.colors.LinearSegmentedColormap.from_list('reference_style',['#00ffff','#00eebb','#8dff00','#ffff00','#ff9b00','#ff1a00','#ff00ee'],N=20) if SELECTED_YOKE else 'turbo'
fig,axes=plt.subplots(1,3,figsize=(7.0,2.2))
axes[0].tripcolor(triang,facecolors=fine['mat'],cmap=matplotlib.colors.ListedColormap(['white','#dddddd','#111111','#c78739','#f0ddbd']),vmin=0,vmax=4,shading='flat',rasterized=True)
outlines(axes[0])
for text,target,position in [('Buried PM',(0,67),(-125,120)),('Rotor winding',(65*np.cos(np.deg2rad(20)),65*np.sin(np.deg2rad(20))),(24,57)),('Stator winding',(-64,-77),(-140,-136))]:
 axes[0].annotate(text,xy=target,xytext=position,fontsize=8,ha='left',va='center',bbox={'facecolor':'white','edgecolor':'none','alpha':.9,'pad':.4},arrowprops={'arrowstyle':'->','lw':.6,'color':'black'},zorder=12)
axes[0].set_xlim(-162,162);axes[0].set_ylim(-162,162);axes[0].set_title('(a) Exploratory 36-slot geometry',fontsize=9,pad=2)
for ax,name,title in zip(axes[1:],['12_pole','6_pole'],['(b) 12-pole field setting','(c) 6-pole field setting']):
 c=fine['cases'][name];norm=np.linalg.norm(c['B'],axis=1)
 im=ax.tripcolor(fieldtri,facecolors=norm,cmap=field_cmap,vmin=0,vmax=2,shading='flat',rasterized=True)
 vals=c['A'];levels=np.linspace(vals.min()*.95,vals.max()*.95,25)
 ax.tricontour(triang,vals,levels=levels,colors='#303030',linewidths=.24,linestyles='solid');outlines(ax);pole_labels(ax,name);ax.set_title(title,fontsize=9,pad=2)
fig.subplots_adjust(left=.005,right=.93,top=.88,bottom=.08,wspace=.04)
cax=fig.add_axes([.947,.22,.014,.53]);cb=fig.colorbar(im,cax=cax,extend='max');cb.set_label(r'$|B|$ (T)',fontsize=9);cb.ax.tick_params(labelsize=8,width=.5);cb.set_ticks([0,1,2])
save(fig,'ieee_fig4_basic_he_ipm_fea')
# Standalone larger field map, useful outside the digest.
fig,axes=plt.subplots(1,2,figsize=(7,3.5))
for ax,name in zip(axes,['12_pole','6_pole']):
 c=fine['cases'][name];im=ax.tripcolor(fieldtri,facecolors=np.linalg.norm(c['B'],axis=1),cmap=field_cmap,vmin=0,vmax=2,shading='flat',rasterized=True);ax.tricontour(triang,c['A'],levels=np.linspace(c['A'].min()*.95,c['A'].max()*.95,29),colors='#222',linewidths=.3,linestyles='solid');outlines(ax);pole_labels(ax,name);ax.set_title(name.replace('_',' ')+' — nonlinear no-load FEA',fontsize=11)
fig.subplots_adjust(left=.01,right=.91,top=.91,bottom=.03,wspace=.05);cb=fig.colorbar(im,cax=fig.add_axes([.93,.20,.02,.57]),extend='max');cb.set_label('|B| (T)');save(fig,'basic_he_ipm_flux_maps')
print('Saved nonlinear magnetostatic FEM fields and figures.',flush=True)

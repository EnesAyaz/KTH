"""Independent uniform-current disk benchmark for the P1 assembly convention."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'simulation/vendor'))
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
f=np.load(ROOT/'simulation/results_basic_fea/basic_fea_fields.npz')
xy=f['xy'];tri=f['tri'];v=xy[tri]
u=v[:,1]-v[:,0];w=v[:,2]-v[:,0];det=u[:,0]*w[:,1]-u[:,1]*w[:,0];area=det/2
grad=np.stack([np.stack([v[:,1,1]-v[:,2,1],v[:,2,0]-v[:,1,0]],1),np.stack([v[:,2,1]-v[:,0,1],v[:,0,0]-v[:,2,0]],1),np.stack([v[:,0,1]-v[:,1,1],v[:,1,0]-v[:,0,0]],1)],1)/det[:,None,None]
mu=4*np.pi*1e-7;J=1e6;R=.150
local=area[:,None,None]/mu*np.einsum('tik,tjk->tij',grad,grad)
K=coo_matrix((local.ravel(),(np.repeat(tri,3,axis=1).ravel(),np.tile(tri,(1,3)).ravel())),shape=(len(xy),len(xy))).tocsr()
rhs=np.zeros(len(xy))
for k in range(3):np.add.at(rhs,tri[:,k],area*J/3)
radius=np.linalg.norm(xy,axis=1);free=np.flatnonzero(radius<R-1e-9);A=np.zeros(len(xy));A[free]=spsolve(K[free][:,free],rhs[free])
exact=mu*J*(R*R-radius**2)/4
error=float(np.linalg.norm(A-exact)/np.linalg.norm(exact));assert error<.001,error
res=float(np.linalg.norm((K@A-rhs)[free])/np.linalg.norm(rhs[free]));assert res<1e-7,res
model=json.loads((ROOT/'simulation/results_basic_fea/basic_fea_results.json').read_text())
for case in model['fine']['cases'].values():assert case['nonlinear_residual']<1e-6
assert max(model['mesh_sensitivity'].values())<.01
report={'benchmark':'uniform-current circular domain, Az(R)=0','analytic_Az':'mu J (R^2-r^2)/4','relative_nodal_L2_error':error,'relative_linear_residual':res,'nonlinear_case_residuals_passed':True,'selected_harmonic_angular_mesh_change_below_1_percent':True,'scope':'Assembly and numerical consistency checks, not physical motor validation'}
(ROOT/'qa/basic_fem_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

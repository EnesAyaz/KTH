"""15/20-mm no-load yoke checks with unchanged rotor and excitation."""
from pathlib import Path
import sys,ast,json
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'simulation/vendor'))
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
MU0=4*np.pi*1e-7;FIXED=np.array([0,3,4,7,8,11]);WOUND=np.array([1,2,5,6,9,10])
for source,function in [('basic_he_ipm_fea.py','solve'),('screen_stator_sizing.py','stats')]:
 tree=ast.parse((ROOT/'simulation'/source).read_text(encoding='utf-8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==function)
 exec(compile(ast.Module(body=[node],type_ignores=[]),source,'exec'))
OUT=ROOT/'simulation/results_saturation_screen';result={}
for thickness in [17.5]:
 key=f'yoke_{thickness}mm';data=solve(720,1,115+thickness,2.4)
 result[key]={'yoke_thickness_mm':thickness,'angular_divisions':720,'stats':stats(data,115+thickness)}
 np.savez_compressed(OUT/(key+'_fine.npz'),xy=data['xy'],tri=data['tri'],material=data['mat'],A12=data['cases']['12_pole']['A'],B12=data['cases']['12_pole']['B'],A6=data['cases']['6_pole']['A'],B6=data['cases']['6_pole']['B'])
 (OUT/'yoke_17p5mm_fine.json').write_text(json.dumps(result,indent=2))
 print(thickness,json.dumps(result[key]['stats']),flush=True)

import sys,subprocess,json
from pathlib import Path
sys.path.insert(0,r'C:\Github\KTH\DPT\DPT-GaN')
import dpt_gui as d
from test_dpt import read_log
cases=[('baseline',{},''),('step_250ps',{'Maxstep':'250p'},''),('gear_250ps',{'Maxstep':'250p'},'gear'),('layout_1n',{'Lloop':'1n'},''),('resistance_50m',{'Rloop':'50m'},''),('gate_on_5ohm',{'Rg_on':'5'},'')]
report={}
for name,changes,method in cases:
 path=d.export(dict(d.DEFAULTS,**changes),d.BASE/'ringing_diagnosis'/name/'DPT.asc').with_suffix('.cir')
 if method:path.write_text(path.read_text().replace('.options plotwinsize=0','.options plotwinsize=0 method=gear'))
 r=subprocess.run([d.find_ltspice(),'-b',str(path)],cwd=path.parent,capture_output=True,timeout=45)
 if r.returncode:raise RuntimeError(read_log(path.with_suffix('.log')))
 m=d.parse_measurements(read_log(path.with_suffix('.log')));report[name]=m
 print(name,{k:v for k,v in m.items() if k in ['vds_hs_peak','vgs_hs_peak','vgs_hs_min','eon2_uj','psw_dut_w']},flush=True)
(d.BASE/'ringing_diagnosis/results.json').write_text(json.dumps(report,indent=2))

import sys,subprocess,json
sys.path.insert(0,r'C:\Github\KTH\DPT\DPT-GaN')
import dpt_gui as d
from test_dpt import read_log
root=d.BASE/'study_75V_50A';root.mkdir(exist_ok=True)
cases=[('existing',{}),('gate10',{'Rg_on':'10','Rg_off':'5'}),('gate22',{'Rg_on':'22','Rg_off':'10'}),('layout1_gate10',{'Lloop':'1n','ESL':'200p','Rg_on':'10','Rg_off':'5'}),('layout1_gate22',{'Lloop':'1n','ESL':'200p','Rg_on':'22','Rg_off':'10'})]
report={}
for name,changes in cases:
 v=dict(d.DEFAULTS,Vin='75',Itest='50',Cin='470u',**changes)
 p=d.export(v,root/name/'DPT.asc').with_suffix('.cir')
 r=subprocess.run([d.find_ltspice(),'-b',str(p)],cwd=p.parent,capture_output=True,timeout=50)
 m=d.parse_measurements(read_log(p.with_suffix('.log')))
 report[name]={'values':v,'measurements':m,'exit_code':r.returncode}
 print(name,{k:m.get(k) for k in ['i_first_off','i_second_on','vds_peak','vds_hs_peak','vgs_hs_peak','psw_dut_w']},flush=True)
 (root/'screening.json').write_text(json.dumps(report,indent=2))

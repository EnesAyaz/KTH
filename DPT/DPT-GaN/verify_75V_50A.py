import sys,subprocess,json
sys.path.insert(0,r'C:\Github\KTH\DPT\DPT-GaN')
import dpt_gui as d
from test_dpt import read_log
root=d.BASE/'study_75V_50A'
base=dict(d.DEFAULTS,Vin='75',Itest='50',Cin='470u',AutoT1='0',Tcharge='13.537u',Lloop='1n',ESL='200p',Rg_on='10',Rg_off='5')
cases=[('candidate',{}),('candidate_250ps',{'Maxstep':'250p'}),('candidate_corner',{'Vin':'82.5','Tj':'150','Lloop':'1.5n','ESL':'300p','Maxstep':'250p'}),('original_layout_slow',{'Lloop':'5n','ESL':'1n','Rg_on':'22','Rg_off':'22'})]
results={}
for name,changes in cases:
 v=dict(base,**changes);p=d.export(v,root/name/'DPT.asc').with_suffix('.cir')
 r=subprocess.run([d.find_ltspice(),'-b',str(p)],cwd=p.parent,capture_output=True,timeout=60)
 m=d.parse_measurements(read_log(p.with_suffix('.log')))
 results[name]={'values':v,'measurements':m,'exit_code':r.returncode}
 print(name,{k:m.get(k) for k in ['i_first_off','i_second_on','vds_peak','vds_hs_peak','psw_dut_w']},flush=True)
 (root/'verification.json').write_text(json.dumps(results,indent=2))

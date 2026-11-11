from pathlib import Path
import json,hashlib
from pypdf import PdfReader
root=Path(__file__).resolve().parent.parent
sources=[
('ORNL_Prius_2017.pdf','https://www.energy.gov/sites/prod/files/2017/06/f34/edt087_burress_2017_o.pdf','ORNL2017 Prius benchmark',[18]),
('DOE_FY2016_report.pdf','https://www.energy.gov/sites/prod/files/2017/08/f36/FY16%20EDT%20Annual%20Report_FINAL.pdf','DOE BMW i3 assessment',[200,202]),
('Nissan_LEAF_ePOWER_2024.pdf','https://www.jstage.jst.go.jp/article/ieejjia/13/1/13_23006552/_pdf/-char/ja','Nissan authors motor evolution',[5]),
('EPC2361.pdf','https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2361_datasheet.pdf','100 V device',[1]),
('EPC2305.pdf','https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2305_datasheet.pdf','150 V device',[1,2]),
('EPC2304.pdf','https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2304_datasheet.pdf','200 V device',[1]),
('EPC2050.pdf','https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2050_datasheet.pdf','350 V device',[1])]
register=[]
for filename,url,purpose,pages in sources:
 p=root/'sources'/filename;assert p.exists() and p.stat().st_size>10000
 register.append({'file':filename,'url':url,'purpose':purpose,'pdf_pages_1based':pages,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'checked_on':'2026-11-09'})
(root/'sources/source_register.json').write_text(json.dumps(register,indent=2))
# Verify the exact terminal-equivalent normalization rather than recomputing an
# identical optimization problem with scaled voltages and magnetic equivalents.
r=json.loads((root/'simulation/results_selection/design_selection.json').read_text())
old=json.loads((root/'simulation/results_three_phase/three_phase_codesign.json').read_text())
new=r['illustrative_terminal_model']
assert new['N']*2==24
for a,b in zip(old['models'],new['models']):
 for k in ['psi_Wb','Ld_H','Lq_H']:assert abs(b[k]-2*a[k])<1e-12
assert abs(new['V_phase_peak_V']-2*old['inputs']['V_phase_peak_limit_V'])<1e-12
assert abs(new['phase_R_ohm']-2*old['inputs']['phase_R_ohm'])<1e-12
assert [d['N_voltage_min'] for d in r['device_classes']]==[20,14,10,6]
assert r['two_cell_control_example']['N']==2 and r['two_cell_control_example']['y']==4
assert r['one_cell_rejection']['supported']==False
for rec in r['records']:
 assert rec['mode_leakage_max']<1e-8
 assert rec['Q']%(3*rec['N'])==0
assert any(x['N']==16 and x['Q']==48 and x['PH']==8 and x['PL']==4 for x in r['records'])
(root/'qa/numerical_verification_selection.json').write_text(json.dumps({'winding_balance_and_other_mode_rejection':'passed in generator','two_cell_control_example':'passed','one_cell_specific_layout_rejected':True,'voltage_floors':'passed','terminal_equivalent_scaling':'passed','limitations':'Constructive exact balanced family, not universal winding feasibility or a validated magnetic motor model'},indent=2))
print('Primary sources retained:',len(register));print('Current numerical consistency checks passed.')

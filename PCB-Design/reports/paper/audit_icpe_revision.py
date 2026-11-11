from pathlib import Path
import sys,json,hashlib,re
import numpy as np
from docx import Document
ROOT=Path.cwd();A=ROOT/'reports/paper/icpe/revised_blue_2026-11-06';P=ROOT/'reports/paper/Submission-Final'
sys.path.insert(0,str(ROOT/'scripts'));from icpe_gate_results import read_raw,window
source=json.loads((A/'protected_sources.json').read_text())
checks={f:hashlib.sha256((P/f).read_bytes()).hexdigest()==h for f,h in source.items()};assert all(checks.values()),checks
out=P/'ICPE_Digest_revised_blue_2026-11-06.docx';d=Document(out)
assert len(d.inline_shapes)==8
assert len(d._element.xpath('.//m:oMath'))==4
colors={};texts=[]
for p in d.paragraphs:
 texts.append(p.text)
 for r in p.runs:
  if r.text.strip():c=str(r.font.color.rgb);colors[c]=colors.get(c,0)+1
text='\n'.join(texts)
assert not any(s in text.lower() for s in ['1.7 nh','dpt board','load board','56%','25%'])
assert '17%' in text and '9%' in text and '2%' in text
assert colors.get('0057B8',0)>40
R=ROOT/'simulation/bb_spice/icpe_digest_revision_2026-11-06/controlled_current'
new=json.loads((R/'results_complete_windows.json').read_text())
for k in new:
 log=(R/(k+'.log')).read_bytes().decode('utf-16' if (R/(k+'.log')).read_bytes()[:2]==b'\xff\xfe' else 'utf-8',errors='replace')
 assert 'Unknown control card' not in log
 assert 'RGOFF=1' in (R/(k+'.cir')).read_text()
# Check the controlled-current approximation against the prior inductive transition.
z=read_raw(ROOT/'simulation/bb_spice/icpe_gate_loop_2026-11-02/board_load_g20_on3_revised_drive.raw')[0];t=z['time'];t1=11.167e-6;t2=12.167e-6
peaks=[];energies=[]
for k in range(1,5):
 vl=z[f'v(dl{k})']-z[f'v(ql_s_{k})'];vh=z[f'v(dh{k})']-z[f'v(qh_s_{k})'];il=z[f'i(vil{k})']
 peaks.extend([float(vl[(t>=t1)&(t<t2)].max()),float(vh[(t>=t2)&(t<=t2+.5e-6)].max())])
 es=0
 for lo,hi in [(t1,t2-1e-9),(t2,t2+150e-9)]:
  tt,pp=window(z,vl*il,lo,hi);es+=np.trapezoid(pp,tt)*1e6
 energies.append(float(es))
b=new['proto_g20_r3_off-1_i315.946_v75_t27_dt0.1'];eb=b['Eon_mean_uJ']+b['Eoff_mean_uJ'];vold=max(peaks);eold=float(np.mean(energies))
benchmark={'inductive_peak_V':vold,'controlled_peak_V':b['vds_peak'],'voltage_difference_pct':100*(b['vds_peak']/vold-1),'inductive_energy_uJ':eold,'controlled_energy_uJ':eb,'energy_difference_pct':100*(eb/eold-1)}
assert abs(benchmark['voltage_difference_pct'])<2 and abs(benchmark['energy_difference_pct'])<2,benchmark
report={'source_files_unchanged':checks,'word_inline_figures':len(d.inline_shapes),'native_equations':4,'paragraph_run_colors':colors,'controlled_cases_used':len(new),'benchmark':benchmark,'simulation_evidence':'results_complete_windows.json; sharing_final_conditions.json; single_and_sizing.json','scope':'Positive-current sampled commutation points. No experimental validation or complete operating-envelope claim.'}
(A/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

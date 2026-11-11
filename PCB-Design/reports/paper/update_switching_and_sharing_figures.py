from pathlib import Path
import sys,json,re,hashlib,csv
from copy import deepcopy
from docx import Document
from docx.shared import Pt,RGBColor,Inches
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
ROOT=Path.cwd();P=ROOT/'reports/paper';SRC=P/'Submission-Files/Digest_LowVoltageGaN_SPB_PrototypeBoard_2026-11-05.docx';OUT=P/'Submission-Files/Digest_LowVoltageGaN_SPB_PrototypeBoard_switching_update_2026-11-05.docx'
A=P/'icpe/switching_figures_update_2026-11-05';A.mkdir(exist_ok=True)
base=P/'icpe/make_compact_digest_figures.py';ns={'__file__':str(base)};source=base.read_text(encoding='utf-8');exec(source.split('dimensions={}')[0],ns);ns['A']=A;ns['dimensions']={}
Fig=ns['Fig'];
original_finish=Fig.finish
def finish_if_needed(self,name):
 if not (A/(name+'.png')).exists():original_finish(self,name)
Fig.finish=finish_if_needed
D=ns['D'];INK=ns['INK'];TEAL=ns['TEAL'];WINE=ns['WINE'];OCHRE=ns['OCHRE'];GREY=ns['GREY']
S=json.loads((ROOT/'simulation/sharing/gate_10_20_2026-11-05/results.json').read_text())
shares={r['case']:r for r in S['cases']}
styles=[(10,.5,TEAL,None),(10,1,TEAL,'3 2'),(20,.5,WINE,None),(20,1,WINE,'3 2')]
# Four individual panels: no maximum across different switching transitions.
f=Fig(454,138)
panels=[('vdsl_pk',(40,200),[50,100,150,200],'Peak voltage (V)','(a) Low side'),('vdsh_pk',(75,150),[75,100,125,150],'Peak voltage (V)','(b) High side'),('eon',(0,100),[0,50,100],'Energy (µJ)','(c) Turn-on'),('eoff',(0,20),[0,10,20],'Energy (µJ)','(d) Turn-off')]
for j,(key,ylim,yt,ylab,tag) in enumerate(panels):
 x=31+113.5*j;t=f.axes(x,22,78,75,(0,170),ylim,[0,80,160],yt,'Current (A)',ylab);f.text(x+39,10,tag,7.5,'middle')
 if j<2:f.line([t(0,90),t(170,90)],GREY,'2 2',.6)
 for g,p,c,dash in styles:
  rows=D['single'][f'g{g}_p{p:g}'];pts=[t(r['iload'],r[key]*(1e6 if j>=2 else 1)) for r in rows];f.line(pts,c,dash,lw=.85)
  for xx,yy in pts:f.dot(xx,yy,c,1.4,g==20)
for j,(g,p,c,dash) in enumerate(styles):
 x=29+113.5*j;f.line([(x,131),(x+13,131)],c,dash);f.text(x+17,134,f'{g} / {p:g} nH',7.5)
f.finish('fig03_separate_voltage_energies')
# Fig. 4 retains the original loss comparison but uses low-side turn-off voltage only.
f=Fig(320,141)
for j,(label,col) in enumerate([('Conduction',INK),('Switching',TEAL),('Dead time',WINE),('Gate',OCHRE)]):
 x=8+80*j;f.rect(x,2,5,4,col);f.text(x+8,7,label,7)
t=f.axes(31,27,112,80,(1.4,8.6),(0,60),list(range(2,9)),[0,20,40,60],'Parallel count, n','Phase-leg loss (W)');f.text(31,20,'(a) 10 nH / 0.5 nH',7)
for r in D['parallel']['g10_p0.5']:
 v=0
 for key,c in [('cond',INK),('sw',TEAL),('dead',WINE),('gate',OCHRE)]:
  val=r[key];x,y=t(r['n']-.28,v+val);xx,yy=t(r['n']+.28,v);f.rect(x,y,xx-x,yy-y,c);v+=val
t=f.axes(192,27,112,80,(1.7,8.3),(75,185),list(range(2,9)),[90,120,150,180],'Parallel count, n','Low-side peak (V)');f.text(192,20,'(b) Turn-off',7);f.line([t(1.7,90),t(8.3,90)],GREY,'2 2',.6)
for g,p,c,dash in styles:
 pts=[t(r['n'],r['vls']) for r in D['parallel'][f'g{g}_p{p:g}']];f.line(pts,c,dash,lw=.85)
 for xx,yy in pts:f.dot(xx,yy,c,1.4,g==20)
for j,(g,p,c,dash) in enumerate(styles):
 x=15+j*78;f.line([(x,138),(x+11,138)],c,dash);f.text(x+14,140,f'{g}/{p:g} nH',7)
f.finish('fig04_low_side_turnoff')
# Keep the established schematic/Kelvin panels and redraw only the sharing panel from the new simulations.
part=source.split('# 5. Three panels in one row,')[1].split('# 6. Same six stages;')[0]
part=part[part.index('f=Fig'):]
old="for y,label,v in [(23,'Power loop: ΔL = 0.3 nH',2),(47,'Gate loop: 2 / 8 nH',19),(71,'No Kelvin: ΔLs = 0.2 nH',29)]:"
new="for y,label,v in [(23,'Power loop: ΔL = 0.3 nH',shares[1]['peak_current_imbalance_pct']),(47,'Gate loop: 10 / 20 nH',shares[2]['peak_current_imbalance_pct']),(71,'No Kelvin: ΔLs = 0.2 nH',shares[4]['peak_current_imbalance_pct'])]:"
assert old in part;part=part.replace(old,new).replace('v*3','v*2').replace("f'{v}%'","f'{v:.0f}%'").replace('GREY if v==2 else WINE','GREY if y==23 else WINE').replace("'75 V / 120 A; energy imbalance'","'75 V / 120 A; peak-current imbalance'").replace("f.finish('fig05_gate_drive')","f.finish('fig05_sharing_10_20')")
ns['shares']=shares;exec(part,ns)
# Record the plotted numerical data independently of the rendering.
with (A/'fig03_source_data.csv').open('w',newline='') as stream:
 w=csv.writer(stream);w.writerow(['Gate_loop_nH','Power_loop_nH','Current_A','LS_turnoff_peak_V','HS_peak_at_LS_turnon_V','LS_Eon_uJ','LS_Eoff_uJ'])
 for g,p,c,dash in styles:
  for r in D['single'][f'g{g}_p{p:g}']:w.writerow([g,p,r['iload'],r['vdsl_pk'],r['vdsh_pk'],r['eon']*1e6,r['eoff']*1e6])
with (A/'fig04_voltage_data.csv').open('w',newline='') as stream:
 w=csv.writer(stream);w.writerow(['Gate_loop_nH','Power_loop_nH','Parallel_count','LS_turnoff_peak_V'])
 for g,p,c,dash in styles:
  for r in D['parallel'][f'g{g}_p{p:g}']:w.writerow([g,p,r['n'],r['vls']])
# Read the user's CURRENT edited document; preserve all unrelated paragraphs, tables and equations.
source_hash=hashlib.sha256(SRC.read_bytes()).hexdigest();doc=Document(SRC);pars=list(doc.paragraphs);before=[q.text for q in pars]
updates={
36:'Fig. 3 separates the low-side drain–source voltage peak at turn-off from the high-side peak during low-side turn-on and reports both low-side switching energies. The low-side peak generally rises at higher current, whereas the high-side peak is largest at low current, where rapid capacitive commutation excites ringing. Near 80 A per device, the compact power path meets the drain-voltage target for both events, but the higher-inductance path does not. Increasing gate resistance can slow the relevant transition and reduce overshoot, but generally increases switching energy. Minimizing commutation inductance is therefore important for retaining voltage margin and the device’s switching-loss advantage.',
39:'Fig. 3. Single-cell results at 75 V: (a) low-side voltage peak at turn-off; (b) high-side voltage peak during low-side turn-on; (c) low-side turn-on energy; (d) low-side turn-off energy. Legend: gate-loop / commutation-loop inductance. Grey lines: 90 V target.',
44:'Fig. 4(a) shows the loss distribution for the nominal gate-loop case and compact commutation path. Additional parallel devices reduce conduction loss, while switching charge, gate loading and layout complexity limit the benefit of further paralleling. Fig. 4(b) compares only the low-side drain–source voltage peak at turn-off, evaluated at the peak current per device. The high-side peak is assessed separately in Fig. 3(b); both transitions must satisfy the voltage constraint before a parallel count can be accepted.',
46:'Fig. 4. (a) Phase-leg losses and (b) low-side voltage peak at turn-off versus parallel count at 75 V and 50 kHz. Inductance encoding follows Fig. 3.',
51:f"The preliminary parallel-count choice assumes equal current sharing. Fig. 5(a) compares two parallel devices at 75 V and 120 A nominal total current, using 0/5 V gate commands, 2 Ω gate resistors and nominal 10 nH gate loops. A power-loop mismatch of 0.3 nH produces approximately {shares[1]['peak_current_imbalance_pct']:.0f}% peak-current imbalance; 10/20 nH gate loops produce approximately {shares[2]['peak_current_imbalance_pct']:.0f}%; and removing the Kelvin return with a 0.2 nH source-inductance mismatch produces approximately {shares[4]['peak_current_imbalance_pct']:.0f}%. The metric is 100|Ipk1 − Ipk2|/(Ipk1 + Ipk2), where Ipk1 and Ipk2 are the individual turn-on peak drain currents. The power- and source-mismatch cases retain 10/10 nH gate loops. The gate-loop mismatch is the most sensitive of these evaluated cases, motivating matched gate paths and dedicated Kelvin returns.",
53:'Fig. 5. (a) Peak-current imbalance with a nominal 10 nH gate loop; (b) paired gate drive; (c) device pads and Kelvin return. HO/LO denote high-/low-side driver outputs.'
}
assert pars[36].text.startswith('Fig. 3 compares') and pars[51].text.startswith('The preliminary parallel-count choice')
for i,txt in updates.items():
 q=pars[i];q.clear();r=q.add_run(txt);r.font.name='Times New Roman';r.font.size=Pt(10);r.font.color.rgb=RGBColor(0,0,0)
images={38:('fig03_separate_voltage_energies',454,138),45:('fig04_low_side_turnoff',320,141),52:('fig05_sharing_10_20',454,117)}
for i,(name,w,h) in images.items():
 q=pars[i];q.clear();q.alignment=WD_ALIGN_PARAGRAPH.CENTER;q.add_run().add_picture(str(A/(name+'.png')),width=Inches(w/72));q.paragraph_format.keep_with_next=True
changed=set(updates)|set(images)
assert all(q.text==before[i] for i,q in enumerate(doc.paragraphs) if i not in changed)
used={n.get(qn('r:embed')) for n in doc.element.xpath('.//a:blip')}
for rid,rel in list(doc.part.rels.items()):
 if rel.reltype.endswith('/image') and rid not in used:doc.part.drop_rel(rid)
# Recent author edits overflow the old manually assigned pages. Let content flow without cutting text.
for q in doc.paragraphs:
 if q.paragraph_format.page_break_before:q.paragraph_format.page_break_before=False
 # Compact leading at the existing 10-pt body size; preserve full height for drawings and equations.
 if q.style.name!='Title' and not q._p.xpath('.//w:drawing | .//m:oMath'):
  q.paragraph_format.line_spacing=Pt(10.5 if q.text.strip() else 2)
for table in doc.tables:
 for row in table.rows:
  for cell in row.cells:
   for q in cell.paragraphs:q.paragraph_format.line_spacing=Pt(10.5)
# Typeset the defined peak-current symbols in the changed sharing paragraph.
q=pars[51]
for rr in list(q.runs):
 parts=re.split(r'(Ipk[12])',rr.text)
 if len(parts)==1:continue
 anchor=rr._r
 for part in parts:
  values=[(part,False,False)] if not re.fullmatch(r'Ipk[12]',part) else [('I',False,True),('pk,'+part[-1],True,False)]
  for val,sub,it in values:
   r=q.add_run(val);r.font.name='Times New Roman';r.font.size=Pt(10);r.font.subscript=sub;r.italic=it;anchor.addprevious(r._r)
 q._p.remove(rr._r)
doc.save(OUT)
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==source_hash
s='\n'.join(q.text for q in doc.paragraphs)
assert not re.search(r'2 nH versus 8 nH|19% imbalance|switching-energy imbalance|load[- ]board|\bDPT\b',s)
assert len(doc.inline_shapes)==8 and len(doc.element.xpath('.//m:oMath'))==4
(A/'artifact.md').write_text(f'''Narrow revision of the author's latest edited digest: {SRC}. SHA256 {source_hash}. Source file left unchanged. Preserve all paragraphs and tables except the three specified figures and their six related explanatory/caption paragraphs. User's revised introduction, voltage-utilization rationale, gate-resistor description, selection note and all other edits retained verbatim. Fig3 now shows LS Vds at turn-off, HS Vds during LS turn-on, LS Eon and Eoff separately. Fig4b uses ONLY LS turn-off peak; losses unchanged. Simulated points not altered to force monotonicity. Fig5 nominal gate loops changed to 10/10 nH; gate mismatch 10/20 nH. All five sharing cases rerun; plotted cases1,2,4 yield about8%,56%,25% peak-current imbalance. Prior label energy imbalance was incorrect: old2/19/29% came from peak currents. Definition now explicit. Fine time-step check of case2 at0.05ns gives56.0% vs55.7% at0.1ns. Simulation source {ROOT/'simulation/sharing/gate_10_20_2026-11-05/results.json'}. IEEE-style existing layout and font retained. Remove only obsolete manual page-break-before formatting to avoid nearly empty overflow pages after author edits; no body cuts. Set body/table leading to10.5pt at unchanged10pt font and reduce empty spacer leading to2pt; drawings/equations retain automatic height. Native figure widths454/320/454pt; 7–7.5pt labels. Export SVG/PDF/PNG. Render using Word/Poppler if bundled renderer lacks soffice.\n''',encoding='utf-8')
(A/'update_audit.json').write_text(json.dumps({'source':str(SRC),'source_sha256':source_hash,'updated_paragraph_indices':sorted(changed),'unrelated_paragraphs_preserved':True,'output':str(OUT)},indent=2))
print(OUT);print('Words',len(s.split()))

from pathlib import Path
from copy import deepcopy
import re,hashlib,json
from docx import Document
from docx.shared import Pt,Inches,RGBColor,Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.text.paragraph import Paragraph
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path.cwd();P=ROOT/'reports/paper';SRC=P/'Submission-Files/Digest-ParasiticAwareSPB_revised_2026-11-02.docx'
OUT=P/'Submission-Files/Digest_LowVoltageGaN_SPB_reframed_6page_2026-11-05.docx'
A=P/'icpe/reframed_6page_load_digest_2026-11-05';A.mkdir(exist_ok=True)
F=P/'icpe/latest_digest_figures';L=P/'icpe/low_voltage_gan_digest_2026-11-05'
source_hash=hashlib.sha256(SRC.read_bytes()).hexdigest();doc=Document(SRC);pars=list(doc.paragraphs)
replacements={
1:'Low-Voltage GaN Utilization for High-Voltage Stacked Polyphase Bridge Traction Inverters',
2:'Abstract—The stacked polyphase bridge (SPB) enables a high-voltage traction drive to use low-voltage gallium nitride (GaN) transistors by partitioning the dc-link voltage among series-connected submodules. Realizing the device-level advantage requires a building block that retains switching margin at high phase current. This paper examines that requirement for a 300-kW, 1200-V drive. A charge-based device comparison motivates the 100-V EPC2361, and a single-cell switching and loss assessment identifies four parallel transistors per switch position as a candidate for sixteen submodules. Current-sharing sensitivity motivates symmetric transistor pairs and dedicated Kelvin returns. The candidate is then assessed through the KiCad–Ansys Q3D–LTspice design loop of the load board. Although its estimated local commutation loop is approximately 0.41 nH, the simulated held-off gate peak reaches approximately 1.4 V with zero off-state bias. Revised drive settings reduce this disturbance, while the 20-nH gate-loop case remains near the 90-V drain-voltage target. The study connects low-voltage GaN selection to the joint power- and gate-network constraints that govern its utilization in an SPB traction building block. Testing of one building block is planned for the full paper.',
5:'High dc-link voltages support traction power levels of several hundred kilowatts, but conventional two-level inverter switches must block the full dc-link voltage while conducting substantial phase current. The stacked polyphase bridge (SPB) changes the available device choice by connecting three-phase bridges in series on the dc side, with each bridge supplying an isolated winding set of a common machine [1], [2]. Fig. 1 shows the voltage partition and the phase-leg building block considered here.',
6:'Voltage partitioning allows each submodule to use a lower semiconductor voltage class. This creates an opportunity to use low-voltage gallium nitride (GaN) devices with favorable resistance and switching charge in a high-voltage traction drive. The opportunity depends on a physical building block that can carry the required current without consuming the available switching margin.',
10:'Increasing the submodule count reduces the voltage across each bridge but does not reduce the phase-current requirement for fixed total power, dc-link voltage, modulation index and power factor. Several devices may therefore be needed in parallel. Their current sharing, gate-drive impedance and commutation paths determine whether the expected device advantage can be retained.',
11:'Previous studies establish SPB modulation and losses [2], dc-link stability [3], and comparisons with alternative GaN converter systems [4]. Work on paralleled GaN stages identifies the importance of commutation inductance, source coupling and unequal gate impedances [5]–[7]. Together, these results motivate examining low-voltage GaN utilization through the physical constraints of the SPB building block.',
12:'The question is whether the selected device remains usable at traction current once parallel devices, gate drive and routing are included. Device figure of merit alone cannot establish the available drain- and gate-voltage margins.',
13:'This paper follows device selection through single-cell characterization, parallel-count selection and symmetric cell arrangement to a routed load-board phase leg. Its contribution is the resulting assessment of switching margins for low-voltage GaN in this SPB application, using the KiCad–Ansys Q3D–LTspice workflow to connect device choice to implementation.',
14:'II. Traction Requirements and Low Voltage Device Selection',
28:'Because of the digest page limit, device-data normalization and screening limits will be detailed in the full paper.',
33:'III. Single Cell Characterization and Selection of the Parallel Count',
35:'The selected EPC2361 is evaluated in a half-bridge model with one device per switch position. Inductive-load switching simulations are performed at a submodule voltage of 75 V over a device-current sweep. Gate-loop inductances of 10 nH and 20 nH represent the preliminary range of interest. Commutation-loop inductances of 0.5 nH and 1 nH separately represent a compact power path and a higher-inductance sensitivity case.',
37:'Because of the digest page limit, the full paper will expand the current-range assessment and simulation details.',
43:'The single-cell switching-energy maps are evaluated over the sinusoidal phase-current waveform to estimate average switching losses.',
48:'Four parallel transistors are retained as an initial implementation choice: this count meets the preliminary peak-current voltage screen with the compact commutation path and permits two symmetric transistor pairs. It is not the minimum-loss count in the sweep. Its suitability is therefore checked in the routed load board rather than inferred from the single-cell model alone.',
51:'The preliminary parallel-count choice assumes equal current sharing. Differences in gate-loop inductance, common-source inductance and driver timing can produce unequal transient loading even when on-state resistances are similar. Fig. 5(a) summarizes sensitivity simulations for two parallel devices at 75 V and 120 A total current. A power-loop mismatch of 0.3 nH produces approximately 2% switching-energy imbalance in this case. A gate-loop difference of 2 nH versus 8 nH produces approximately 19% imbalance; without a Kelvin return, a common-source mismatch of 0.2 nH produces approximately 29% imbalance. These perturbation cases motivate matching the gate paths and separating the gate return from the power-source path.',
57:'The four-device arrangement is divided into two transistor pairs per switch position. As illustrated in Fig. 5(b), each pair of switching cells is served by one dual-channel 2EDF7275K driver [10]. One channel drives two high-side transistors and the other drives two low-side transistors. The phase leg uses two drivers, with an individual gate resistor for each transistor.',
59:'Because of the digest page limit, the full paper will detail layout symmetry, Kelvin returns and driver loading.',
61:'Because of the digest page limit, inter-driver timing and additional routed-network checks will be presented in the full paper.',
62:'V. Low Voltage GaN Utilization in the Routed Load Board',
64:'Initial sizing identifies a voltage class and parallel-count candidate. The load board must then show whether this device arrangement can retain sufficient switching margin at traction current. Fig. 6 links KiCad placement and routing to Ansys Q3D extraction and LTspice assessment. Drain stress, gate disturbance and branch behavior guide changes to the layout or drive settings. If sufficient margin cannot be recovered, the submodule voltage or device class must be reconsidered. The workflow thus checks the selected SPB operating point against the intended building-block implementation.',
66:'Fig. 6. Load-board design loop linking voltage choice, routing, parasitic extraction and the joint drain- and gate-voltage assessment.',
67:'The following results use only the load board representing the intended converter phase leg. Its local capacitors and paired drive arrangement are evaluated together with the routed copper network.',
68:'B. Load Board Layout and Extracted Network',
69:'Fig. 7 shows the KiCad load-board assembly and the Q3D conductor geometry. The estimated local commutation loop is approximately 0.41 nH per cell, including capacitor equivalent series inductance. This supports the compact-path assumption used for initial sizing. The geometry also shows why the outgoing and return conductors must be considered together, rather than assigning an independent inductance to each visible connection.',
71:'Fig. 7. (a) KiCad load-board assembly. (b) Q3D load-board power conductors; colours identify the dc rails, switch node and device/capacitor terminals.',
72:'The LTspice power-network model retains 29 branches, the extracted copper resistance matrix and mutual inductive coupling. It uses dc resistance and partial inductances extracted at 100 MHz. Gate-loop inductances of 10 nH and 20 nH are sensitivity assumptions, distinct from the extracted copper power network. The local loop estimate alone therefore does not describe the complete switching model.',
75:'C. Load Board Switching Assessment',
76:'Fig. 8 compares load-board responses using the same extracted power network. The local bus is 75 V and the saved inductive-load transition occurs near 316 A total current. The device model temperature is 27 °C. A 5-V on-state command, 1-Ω external turn-off resistance and 0.85-Ω/0.35-Ω driver pull-up/pull-down resistances are used. External turn-on resistance and off-state bias are varied to assess the drain and gate constraints together.',
81:'Fig. 8. Load-board waveforms at 75 V near 316 A: (a) worst-device high-side drain voltage and (b) largest held-off gate response. Grey references mark 90 V and 0.8 V.',
82:'Table II reports the maximum drain voltage across the four parallel devices and both assessed commutations, the largest held-off high-side gate peak, and the minimum gate voltage across the saved transitions. With zero off-state bias, increasing turn-on resistance reduces the drain peak but leaves the gate disturbance above the minimum threshold of 0.8 V [9]. This indicates a risk of unintended conduction; it does not quantify a shoot-through current. Negative off-state bias reduces the positive gate excursion, but the 20-nH case remains approximately at the drain-voltage target. The negative gate excursion must also be checked against the −4-V device limit.',
83:'D. Implications for Low Voltage GaN Utilization',
84:'The load-board results show that a compact power loop is necessary but does not by itself establish usable switching margin. Parallel count, branch symmetry and gate-drive settings determine whether the selected voltage class remains practical. The higher gate-inductance case leaves no useful drain-voltage margin for tolerances or operating-point variation. If layout and drive changes cannot provide that margin, reducing the submodule voltage feeds back into the SPB series count. The lower gate-inductance case provides more headroom at this operating point, without establishing compliance over a complete traction operating envelope.',
85:'VI. Experimental Validation and Scope of the Full Paper',
86:'A. Testing of One Building Block',
87:'Because of the digest page limit, experimental validation is reserved for the full paper. One load-board building block will be tested to compare drain and gate transients and switching energy with the simulation predictions. These measurements are planned and have not yet been performed.',
89:'Because of the digest page limit, system integration and insulation details will be presented in the full paper.',
91:'The SPB voltage partition enables low-voltage GaN to be considered for a high-voltage traction drive, but its utilization depends on a realizable high-current building block. The device comparison, single-cell study and parallel-count assessment lead to a symmetric four-device candidate. Load-board extraction and switching simulations then expose the remaining joint drain- and gate-voltage constraints. These results connect device-level selection to implementation feasibility; they do not establish a final loss optimum or full-drive efficiency. Testing one building block in the full paper will assess the simulation predictions and remaining switching margin.'
}
red_indices={28,37,59,61,87,89}
# Keep source paragraph identities while replacing the requested story and measurement-board content.
for i,t in replacements.items():
 q=pars[i];q.clear();r=q.add_run(t);r.font.name='Times New Roman';r.font.size=Pt(10);r.font.color.rgb=RGBColor.from_string('EE0000' if i in red_indices else '000000')
 if i==2:r.bold=True
 if i==1:r.font.size=Pt(16);r.bold=True
# Fix remaining red scope-note grammar without reopening omitted derivations.
q=pars[22];q.clear();q.add_run('Voltage partitioning allows the semiconductor voltage class to be selected together with the submodule count. The comparison considers conduction and switching characteristics rather than on-state resistance alone. Fig. 2 compares the typical on-state resistance RDS(on) at 25 °C and charge-equivalent output capacitance Coss,Q of the surveyed GaN devices. ')
r=q.add_run('Because of the digest page limit, the capacitance derivation will be presented in the full paper.');r.font.color.rgb=RGBColor.from_string('EE0000')
# Keep future loss-model detail locally in red.
r=pars[43].add_run(' Because of the digest page limit, energy integration and the thermal model will be detailed in the full paper.');r.font.color.rgb=RGBColor.from_string('EE0000')
# Replace the embedded plots with readable versions of the same retained topics.
images={7:(F/'fig01_topology.png',454),26:(F/'fig02_devices.png',252),38:(F/'fig03_single_cell.png',320),45:(F/'fig04_parallel_count.png',320),53:(F/'fig05_gate_drive.png',454),65:(L/'load_workflow.png',454),70:(L/'load_layout_q3d.png',454),77:(L/'load_switching.png',454)}
for i,(path,w) in images.items():
 q=pars[i];q.clear();q.alignment=WD_ALIGN_PARAGRAPH.CENTER;q.add_run().add_picture(str(path),width=Inches(w/72));q.paragraph_format.keep_with_next=True;q.paragraph_format.space_after=Pt(0)
# The two original board-comparison figures are now one load-board-only figure.
for i in [73,74,78,79,80]:
 q=pars[i]
 if q._p.getparent() is not None:q._p.getparent().remove(q._p)
# Add load-board results; values are derived directly from the existing completed simulations.
values=json.loads((L/'load_results.json').read_text());caption=OxmlElement('w:p');pars[82]._p.addnext(caption);cq=Paragraph(caption,pars[82]._parent);cq.add_run('TABLE II  LOAD-BOARD SIMULATION RESULTS');cq.alignment=WD_ALIGN_PARAGRAPH.CENTER
headers=['Gate loop\n(nH)','Turn-on R\n(Ω)','Off bias\n(V)','Drain peak\n(V)','Gate peak\n(V)','Gate min.\n(V)']
table=doc.add_table(rows=1,cols=6)
for c,t in zip(table.rows[0].cells,headers):c.text=t
for setting,b in zip([(10,3,-1),(20,2,0),(20,3,0),(20,3,-1)],values):
 vals=list(setting)+[f"{b['Vpk']:.1f}",f"{b['gate_bump']:.2f}",f"{b['gate_min']:.2f}"]
 for c,v in zip(table.add_row().cells,vals):c.text=str(v)
caption.addnext(table._tbl)
pr=table._tbl.tblPr;borders=OxmlElement('w:tblBorders')
for edge in ['top','bottom','insideH','left','right','insideV']:
 e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single' if edge in ['top','bottom'] else 'nil');e.set(qn('w:sz'),'6');borders.append(e)
pr.append(borders)
for c in table.rows[0].cells:
 bd=OxmlElement('w:tcBorders');e=OxmlElement('w:bottom');e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');bd.append(e);c._tc.get_or_add_tcPr().append(bd)
 for r in c.paragraphs[0].runs:r.bold=True
# Use the original hierarchy and venue typography, with a six-page digest flow.
for q in doc.paragraphs:
 q.paragraph_format.space_before=Pt(2 if q.style.name.startswith('Heading') else 0);q.paragraph_format.space_after=Pt(0);q.paragraph_format.line_spacing=1;q.paragraph_format.widow_control=True
 if q.style.name.startswith('Heading'):q.paragraph_format.keep_with_next=True
 for r in q.runs:
  r.font.name='Times New Roman';r.font.size=Pt(16 if q.style.name=='Title' else 10)
 if not q.text.strip() and not q._p.xpath('.//w:drawing | .//m:oMath'):
  if q._p.getparent() is not None:q._p.getparent().remove(q._p)
for i in [14,33,49,68,82]:pars[i].paragraph_format.page_break_before=True
pars[83].paragraph_format.page_break_before=False
for t in doc.tables:
 for row in t.rows:
  for c in row.cells:
   for q in c.paragraphs:
    q.paragraph_format.space_before=Pt(0);q.paragraph_format.space_after=Pt(0);q.paragraph_format.line_spacing=1
    for r in q.runs:r.font.name='Times New Roman';r.font.size=Pt(10)
# Format symbols in rewritten paragraphs while preserving the native equations and untouched rich text.
tokens={'Vdc':('V','dc'),'Vm':('V','m'),'Iph,rms':('I','ph,rms'),'Coss,Q':('C','oss,Q'),'RDS(on)':('R','DS(on)')}
for i in [18,22]:
 q=pars[i]
 for rr in list(q.runs):
  txt=rr.text;parts=re.split(r'(RDS\(on\)|Iph,rms|Coss,Q|Vdc|Vm)',txt)
  if len(parts)==1:continue
  anchor=rr._r
  for part in parts:
   components=[(part,False,False)] if part not in tokens else [(tokens[part][0],False,True),(tokens[part][1],True,False)]
   for v,sub,it in components:
    r=q.add_run(v);r.font.name='Times New Roman';r.font.size=Pt(10);r.italic=it;r.font.subscript=sub
    anchor.addprevious(r._r)
  q._p.remove(rr._r)
# Remove unused source media, including all removed board comparison images.
used={n.get(qn('r:embed')) for n in doc.element.xpath('.//a:blip')}
for rid,rel in list(doc.part.rels.items()):
 if rel.reltype.endswith('/image') and rid not in used:doc.part.drop_rel(rid)
doc.core_properties.title=replacements[1];doc.core_properties.subject='Low-voltage GaN utilization in an SPB traction building block using load-board results';doc.core_properties.comments=''
doc.save(OUT)
s='\n'.join(q.text for q in doc.paragraphs)
assert not re.search(r'DPT|double.pulse|1\.7\s*nH',s,re.I)
assert len(doc.inline_shapes)==8 and len(doc.element.xpath('.//m:oMath'))==4
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==source_hash
(A/'artifact.md').write_text(f'''Revision based directly on the user's six-page digest, not the separately condensed five-page alternative. Source {SRC}; SHA256 {source_hash}. Original digest preserved. Retain original main sequence: traction requirements/device choice, single-cell characterization/parallel count, sharing/paired drive, layout/Q3D/circuit assessment, planned validation and conclusion. First five figure topics, original operating-point table and all four native equations retained. Reframe the story around low-voltage GaN utilization and conditional switching feasibility. Replace board comparisons with load-board assembly/Q3D geometry and load-board-only switching. Two original geometry comparisons combined, resulting in eight figures. Add a four-case load-board results table from existing completed simulations. No new simulation run or measured results. Gate-loop 10/20 nH assumptions distinguished from extracted power network. Planned one-building-block validation in red. Times 10 pt, original A4 margins, original hierarchy, six-page planned flow. Packaged renderer fallback: Word PDF export and bundled Poppler if soffice is absent.\n''')
print(OUT);print('WORDS',len(s.split()),'FIGURES',len(doc.inline_shapes),'HEADINGS',len([q for q in doc.paragraphs if q.style.name.startswith('Heading')]))

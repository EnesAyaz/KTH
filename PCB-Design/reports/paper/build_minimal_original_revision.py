from pathlib import Path
from copy import deepcopy
from difflib import SequenceMatcher
import re,json,hashlib
from docx import Document
from docx.shared import Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path.cwd();P=ROOT/'reports/paper';A=P/'icpe/minimal_original_revision_2026-11-06';A.mkdir(parents=True,exist_ok=True)
SRC=P/'Submission-Final/ICPE_Template.docx';OUT=P/'Submission-Final/ICPE_Digest_restored_targeted_edits_blue_2026-11-06.docx'
old=Document(SRC);d=Document(SRC);body=d._element.body
for e in list(body):
 if e.tag!=qn('w:sectPr'):body.remove(e)
for sty in ['Normal','Abstract','Caption','Heading 1','Heading 2']:
 s=d.styles[sty];s.font.name='Times New Roman';s.paragraph_format.space_after=Pt(0);s.paragraph_format.space_before=Pt(0)
blue=RGBColor.from_string('0057B8');black=RGBColor(0,0,0)
repls={
1:'Low-Voltage GaN Utilization in High-Voltage Stacked Polyphase Bridge Inverters for Truck Propulsion',
}
def change(i,a,b):
 s=repls.get(i,old.paragraphs[i].text);assert a in s,(i,a);repls[i]=s.replace(a,b)
# Restore the original story, with the minimum qualifications needed for technical accuracy.
change(4,'Its isolated machine winding sets also support continued operation following submodule bypass, distinguishing it from multilevel inverter topologies that require additional redundancy for fault tolerance.','With suitable bypass hardware and winding control, its isolated machine winding sets also support continued operation following submodule bypass, unlike multilevel implementations without provisions for fault-tolerant operation.')
change(4,'With an estimated local commutation-loop inductance of 0.41 nH, optimization of the gate-drive settings achieves a simulated peak drain–source voltage of approximately 90 V while retaining fast switching at the assessed operating point.','With an estimated local commutation-loop inductance of 0.41 nH and a 10-nH gate loop, revised gate-drive settings achieve a simulated peak drain–source voltage of 88.8 V and a 5.9-ns voltage fall time at 75 V and 322 A. A 5% bus-voltage increase exceeds the 90-V design target.')
change(7,'High dc-link voltages support megawatt charging and traction power levels of several hundred kilowatts, but conventional two-level inverter switches must block the full dc-link voltage while conducting substantial phase current [1].','High dc-link voltages support megawatt charging and truck propulsion power levels of several hundred kilowatts [1]. In propulsion operation, conventional two-level inverter switches must block the full dc-link voltage while conducting substantial phase current.')
change(7,'A faulty submodule can be bypassed while the remaining submodules and winding sets continue operating at reduced capability.','With suitable bypass hardware and winding control, a faulty submodule can be bypassed while the remaining submodules and winding sets continue operating at reduced capability, subject to their voltage and current limits.')
change(19,'poly-phase machine; (b) Three-phase','multiphase machine; (b) three-phase')
change(22,'The contribution is a quantitative assessment of how the power network and gate-drive settings jointly constrain the selection of the number of cells and the design of the SPB building block.','The contribution is a quantitative assessment of how the power network and gate-drive settings jointly constrain the submodule voltage and the design of the SPB building block. Current-range and bus-voltage checks expose constraints that a peak-current sizing screen alone does not capture.')
change(27,'The specified operating point requires approximately 228 A rms phase current.','Space-vector modulation is assumed, with M below 2/√3. The specified operating point requires approximately 228 A rms and 322 A peak phase current.')
change(32,'Because of the digest page limit, the capacitance derivation will be presented in the full paper.','Here, Coss,Q = Qoss(Vtest)/Vtest; Fig. 2 lists the quoted test voltages. For EPC2361, 90 nC at 50 V gives 1800 pF, distinct from its differential Coss of 1019 pF [10].')
change(35,'Because of the digest page limit, device-data normalization and screening limits will be detailed in the full paper.','The quoted test voltages differ between classes and are not a common fraction of rating; this is a device screen, not a normalized loss optimum. Because of the digest page limit, detailed screening limits will be given in the full paper.')
change(38,'for the surveyed GaN voltage classes.','for the surveyed GaN voltage classes, with device identities and quoted capacitance test voltages.')
change(45,'Inductive-load switching (uni-directional current)','Inductive-load switching (unidirectional current)')
change(45,'The aim is to retain fast switching','The manufacturer’s device model [10] uses 27 °C, −1/5-V gate commands, 0.85/0.35-Ω driver pull-up/down resistances, and 0.03-nH common-source inductance. Gate-loop values are assumed bounds, not extracted measurements. The aim is to retain fast switching')
change(46,'Near 80 A per device,','Voltage peaks cover the complete off interval and subsequent on interval. Near 80 A per device,')
change(46,'Increasing gate resistance can slow','At lower current, the high-side peak can exceed the target even with the compact path, so the peak-current screen does not establish full-current-range feasibility. Increasing gate resistance can slow')
change(52,'Because of the digest page limit, energy integration and the thermal model will be provided in the full paper.','Turn-on energy is integrated over 150 ns and turn-off energy over the full 1-µs off interval to capture slow low-current capacitance charging. The first-pass cooling estimate assumes 7.62 K/W per device from junction to sink and 0.65 K/W from the shared phase-leg sink to 40 °C ambient. Loss accounting includes 10-ns dead time and a provisional 2.9-µJ capacitive freewheeling term per device per cycle. These assumptions require validation; the detailed model will be given in the full paper because of the digest page limit.')
change(58,'It is not the minimum-loss count in the sweep.','The 10-nH/0.5-nH case estimates 18.6 W per phase leg and 70 °C junction temperature under the assumed cooling conditions. It is not the minimum-loss count in the sweep.')
change(61,'approximately 8%','approximately 2%');change(61,'approximately 56%','approximately 17%');change(61,'approximately 25%','approximately 9%')
change(61,'The gate-loop mismatch is the most sensitive of these evaluated cases, motivating matched gate paths and dedicated Kelvin returns.','Imbalance is 100|Ipk,1 − Ipk,2|/(Ipk,1 + Ipk,2), using each branch’s turn-on maximum. These different perturbations motivate matched gate paths and dedicated Kelvin returns, without establishing a universal sensitivity ranking.')
change(64,'HO/LO denote high-/low-side driver outputs.','HO/LO denote high-/low-side driver outputs. S denotes the power-source terminal, K the Kelvin-source return, and Lₛ the power-source inductance.')
change(66,'driver [10]','driver [11]');change(66,'high-side GaNs','high-side devices');change(66,'low-side GaNs','low-side devices');change(66,'for each GaN.','for each device.')
change(70,'inter-driver timing and additional routed-network checks','inter-driver timing (synchronous commands are presently assumed) and additional routed-network checks')
change(77,'Fig. 7 shows the KiCad prototype board assembly','Fig. 7 shows a CAD rendering of the KiCad prototype board assembly')
change(77,'This supports the compact-path assumption used for initial sizing.','The coupled power network contains 29 branches and 406 mutual terms, using dc resistance and partial inductances at 100 MHz. The scalar comprises 0.347 nH of copper and 0.062 nH of capacitor ESL at device/capacitor ports under equal branch excitation. Package and gate-path inductances were not separately extracted; gate loops remain assumed 10/20-nH bounds. This supports the compact-path assumption used for initial sizing.')
change(77,'Q3d','Q3D');change(80,'Prototype PCB without heatsink.','Prototype PCB CAD rendering without heatsink.')
change(83,'The local bus is 75 V and the saved inductive-load transition occurs near 316 A total current.','The local bus is 75 V; controlled-current commutations sample 1, 40, 80, 160, 240, and 322 A total positive current. A check near 316 A agrees with the inductive-load case within 2% in peak voltage and summed switching energy.')
change(83,'External turn-on resistance and off-state bias are varied to assess the drain and gate constraints together.','External turn-on resistance and off-state bias are varied to assess the drain and gate constraints together. Settings A/B/C use a 20-nH gate loop with turn-on resistance/off bias of 2 Ω/0 V, 3 Ω/0 V, and 3 Ω/−1 V; D uses 10 nH and 3 Ω/−1 V. All cases keep 1-Ω turn-off resistance. The maximum time step is 0.2 ns.')
change(85,'at 75 V near 316 A: (a) worst-device high-side drain voltage and (b) largest held-off gate response.','at 75 V: (a) high-side drain voltage and (b) held-off gate response for A–C at 322 A; (c) maximum drain stress over both transitions across the sampled current range for C and D.')
change(87,'The lower gate-inductance case provides more headroom at this operating point, without establishing compliance over a complete traction operating envelope.','With revised drive settings, the 10-nH case gives 88.0–88.8-V drain peaks at sampled nominal-current points; the 20-nH case reaches 91.8 V at lower current. At rated current, the 10-nH case has a 5.9-ns voltage fall time and 38.7-µJ summed low-side switching energy per device. Raising its local bus by 5% gives a 92.2-V peak, exceeding the target. The nominal result therefore does not establish the proposed voltage-variation allowance or compliance over a complete truck propulsion operating envelope. The 0.8-V reference is a minimum static threshold, not an absolute gate rating or proof against dynamic turn-on.')
change(90,'These measurements are planned and have not yet been performed.','Measurements will include Kelvin-referenced gate voltage, branch currents, and deskewed switching energy, with probe loading and timing uncertainty reported. Negative-bias implementation and driver compatibility will also be checked. These measurements are planned and have not yet been performed.')
change(94,'These results connect device-level selection to implementation feasibility;','The bus-voltage sensitivity leaves further switching-margin work. These results connect device-level selection to implementation feasibility;')
# Terminology applies to the manuscript, not the titles of cited publications.
terminology=[('high-voltage traction drives','high-voltage truck propulsion systems'),('traction-current levels','the required phase-current levels'),('SPB traction inverter','SPB inverter for truck propulsion'),('SPB traction building block','SPB truck propulsion building block'),('traction inverter.','truck propulsion.'),('Traction Requirements','Truck Propulsion Requirements'),('Traction Drive Requirements','Truck Propulsion Requirements'),('traction operating point','truck propulsion operating point'),('at traction current','at the required phase current'),('a high-voltage traction drive','a high-voltage truck propulsion system')]
for i,op in enumerate(old.paragraphs):
 if i>=96:continue
 s=repls.get(i,op.text)
 for a,b in terminology:s=s.replace(a,b)
 if s!=op.text:repls[i]=s

figs={19:(P/'icpe/latest_digest_figures/fig01_topology.png',454),38:(P/'icpe/revised_blue_2026-11-06/fig02_device_survey_explicit_basis.png',500),48:(P/'icpe/revised_blue_2026-11-06/fig03_complete_switching_maps.png',500),55:(P/'icpe/revised_blue_2026-11-06/fig04_sizing_remeasured.png',500),64:(P/'icpe/source_label_ai_ack_2026-11-06/fig05_source_terminal_corrected.png',454),75:(P/'icpe/revised_blue_2026-11-06/fig06_design_feedback.png',500),80:(P/'icpe/revised_blue_2026-11-06/fig07_cad_q3d_readable.png',500),85:(P/'icpe/revised_blue_2026-11-06/fig08_routed_margin_map.png',500)}
figs.update({75:(A/'fig06_compact.png',500),80:(A/'fig07_compact.png',500)})
repls[83]=repls[83].replace(' All cases keep 1-Ω turn-off resistance.','')
audit=[]
def tokens(s):return re.findall(r'\s+|[^\s]+',s)
def emit(i):
 op=old.paragraphs[i];s=repls.get(i,op.text);x=d.add_paragraph();x._p.getparent().replace(x._p,deepcopy(op._p));x=d.paragraphs[-1]
 pp=x._p.get_or_add_pPr()
 for el in list(pp):
  if el.tag in [qn('w:sectPr'),qn('w:pageBreakBefore')]:pp.remove(el)
 if s!=op.text:
  props=[]
  for r in op.runs:props.extend([deepcopy(r._r.rPr)]*len(r.text))
  for el in list(x._p):
   if el.tag!=qn('w:pPr'):x._p.remove(el)
  aa,bb=tokens(op.text),tokens(s);offset=[0]
  for a in aa:offset.append(offset[-1]+len(a))
  for tag,a,b,c,e in SequenceMatcher(None,aa,bb,autojunk=False).get_opcodes():
   if tag=='delete':continue
   txt=''.join(bb[c:e])
   if not txt:continue
   if tag=='equal':
    j=0
    while j<len(txt):
     pos=min(offset[a]+j,len(props)-1);prop=props[pos] if props else None;e0=j+1
     while e0<len(txt) and props and props[min(offset[a]+e0,len(props)-1)] is prop:e0+=1
     r=x.add_run(txt[j:e0])
     if prop is not None:r._r.insert(0,deepcopy(prop))
     if r.font.color.rgb is None:r.font.color.rgb=black
     j=e0
   else:
    r=x.add_run(txt)
    default=next((rr._r.rPr for rr in op.runs if rr.text.strip() and rr._r.rPr is not None),None)
    if default is not None:r._r.insert(0,deepcopy(default))
    if not op.style.name.startswith('Heading') and i!=1:
     r.font.bold=False;r.font.italic=False
    r.font.color.rgb=blue
  audit.append({'index':i,'before':op.text,'after':s})
 ishead=op.style.name.startswith('Heading');iscap=i in figs
 size=16 if i==1 else 8.5 if i>=96 else 9 if (iscap or i==29) else 10
 for r in x.runs:
  r.font.name='Times New Roman';r.font.size=Pt(size)
  if iscap:r.font.color.rgb=blue
 x.paragraph_format.space_before=Pt(1 if ishead else 0);x.paragraph_format.space_after=Pt(0)
 x.paragraph_format.line_spacing=Pt(10 if size==10 else size+.5)
 if op._p.xpath('.//m:oMath'):
  x.paragraph_format.line_spacing=1.0
 x.paragraph_format.widow_control=True
 x.paragraph_format.keep_with_next=ishead or i in [25,29,33,40,50]
 if i==1:x.style='Title';x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(7);x.paragraph_format.line_spacing=Pt(18)
 if ishead:
  x.paragraph_format.first_line_indent=Pt(0)
  if op.style.name=='Heading 2':
   labels={24:'A',31:'B',39:'C',44:'A',49:'B',57:'C',60:'A',65:'B',67:'C',69:'D',72:'A',76:'B',82:'C',86:'D',89:'A',91:'B'}
   if i in labels and not re.match(r'^\s*[A-D]\.',x.text):
    r=x.add_run(labels[i]+'. ');r.font.name='Times New Roman';r.font.size=Pt(10);r.font.color.rgb=black
    x._p.remove(r._r);x._p.insert(1,r._r)
   ni=OxmlElement('w:numPr');n=OxmlElement('w:numId');n.set(qn('w:val'),'0');ni.append(n);pp.append(ni)
 if i==95:
  ni=OxmlElement('w:numPr');n=OxmlElement('w:numId');n.set(qn('w:val'),'0');ni.append(n);pp.append(ni)
 return x
for i,op in enumerate(old.paragraphs):
 if not op.text.strip() and not op._p.xpath('.//m:oMath'):continue
 if i==95:
  h=d.add_paragraph('ACKNOWLEDGMENT');h.alignment=WD_ALIGN_PARAGRAPH.CENTER;h.paragraph_format.space_before=Pt(4);h.paragraph_format.space_after=Pt(1)
  for r in h.runs:r.bold=True;r.font.name='Times New Roman';r.font.size=Pt(10);r.font.color.rgb=blue
  x=d.add_paragraph('OpenAI Codex assisted with drafting and language editing throughout this manuscript, preparation of Figs. 1–8 from project data, and scripting for LTspice runs and result processing in Sections III–V. The authors retain responsibility for the technical content and its verification.')
  x.paragraph_format.line_spacing=Pt(10.5);x.paragraph_format.space_after=Pt(0)
  for r in x.runs:r.font.name='Times New Roman';r.font.size=Pt(10);r.font.color.rgb=blue
 if i in figs:
  img,w=figs[i];x=d.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_before=Pt(0);x.paragraph_format.space_after=Pt(0);x.paragraph_format.line_spacing=1;x.paragraph_format.keep_with_next=True;x.add_run().add_picture(str(img),width=Pt(w))
 x=emit(i)
 if i==29:
  tb=deepcopy(old.tables[0]._tbl);body.insert(len(body)-1,tb)
  for table in d.tables:
   for row in table.rows:
    for cell in row.cells:
     for cp in cell.paragraphs:
      cp.paragraph_format.space_before=Pt(0);cp.paragraph_format.space_after=Pt(0);cp.paragraph_format.line_spacing=Pt(10)
      for r in cp.runs:r.font.name='Times New Roman';r.font.size=Pt(9)
for sec in d.sections:
 for ft in [sec.footer,sec.first_page_footer]:
  for el in list(ft._element):ft._element.remove(el)
  x=ft.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');x._p.append(f)
d.core_properties.title=repls[1];d.save(OUT)
retained=sum(sum(b-a for tag,a,b,c,e in SequenceMatcher(None,tokens(old.paragraphs[i].text),tokens(repls.get(i,old.paragraphs[i].text)),autojunk=False).get_opcodes() if tag=='equal') for i in range(len(old.paragraphs)))
total=sum(len(tokens(p.text)) for p in old.paragraphs)
(A/'targeted_changes.json').write_text(json.dumps({'baseline_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'retained_original_token_fraction':retained/total,'changes':audit},ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT);print('Original tokens retained',round(100*retained/total,1),'%');print('WORDS',sum(len(p.text.split()) for p in d.paragraphs))

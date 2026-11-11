from pathlib import Path
from copy import deepcopy
import json,re,hashlib
from docx import Document
from docx.shared import Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH,WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path.cwd();P=ROOT/'reports/paper';A=P/'icpe/revised_blue_2026-11-06';SRC=P/'Submission-Final/ICPE_Template.docx';OUT=P/'Submission-Final/ICPE_Digest_revised_blue_2026-11-06.docx'
original=Document(SRC);old=list(original.paragraphs);doc=Document(SRC);body=doc._element.body
for e in list(body):
 if e.tag!=qn('w:sectPr'):body.remove(e)
BLUE='0057B8';BLACK='000000'
for sty in ['Normal','Abstract','Caption','Heading 1','Heading 2','Title']:
 s=doc.styles[sty];s.font.name='Times New Roman';s.font.color.rgb=RGBColor.from_string(BLACK);s.paragraph_format.space_before=Pt(0);s.paragraph_format.space_after=Pt(0)
doc.styles['Normal'].font.size=Pt(10)
for sec in doc.sections:
 sec.header_distance=Pt(18);sec.footer_distance=Pt(18)
def p(text='',blue=True,style='Normal',size=10,bold=False,center=False,before=0,after=0,keep=False):
 x=doc.add_paragraph(style=style);x.paragraph_format.line_spacing=Pt(10.8 if size==10 else size+1);x.paragraph_format.space_before=Pt(before);x.paragraph_format.space_after=Pt(after);x.paragraph_format.first_line_indent=Pt(0);x.paragraph_format.keep_with_next=keep;x.paragraph_format.widow_control=True
 if center:x.alignment=WD_ALIGN_PARAGRAPH.CENTER
 else:x.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
 r=x.add_run(text);r.font.name='Times New Roman';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(BLUE if blue else BLACK);return x
def h(text,level=1,blue=True):
 x=p(text,blue,'Heading '+str(level),10,level==1,level==1,before=5 if level==1 else 4,after=2,keep=True)
 pp=x._p.get_or_add_pPr();np=OxmlElement('w:numPr');ni=OxmlElement('w:numId');ni.set(qn('w:val'),'0');np.append(ni);pp.append(np)
 return x
def eq(index):
 e=deepcopy(old[index]._p);body.insert(len(body)-1,e)
 for r in e.findall('.//'+qn('w:color')):r.set(qn('w:val'),BLACK)
def fig(name,w,caption):
 x=p('',False,center=True,after=1,keep=True);x.paragraph_format.line_spacing=1;x.add_run().add_picture(str(A/(name+'.png')) if (A/(name+'.png')).exists() else str(P/'icpe/latest_digest_figures'/f'{name}.png'),width=Pt(w))
 p(caption,True,'Caption',9,after=3)
def table(rows,widths,unchanged=False):
 doc.paragraphs[-1].paragraph_format.keep_with_next=True
 t=doc.add_table(rows=0,cols=len(rows[0]));t.autofit=False
 for row in rows:
  c=t.add_row().cells
  for j,(cell,txt) in enumerate(zip(c,row)):
   cell.width=Pt(widths[j]);x=cell.paragraphs[0];x.paragraph_format.space_after=Pt(0);x.paragraph_format.space_before=Pt(0);x.paragraph_format.line_spacing=Pt(10);x.alignment=WD_ALIGN_PARAGRAPH.CENTER if j else WD_ALIGN_PARAGRAPH.LEFT;r=x.add_run(txt);r.font.name='Times New Roman';r.font.size=Pt(9);r.font.color.rgb=RGBColor.from_string(BLACK if unchanged else BLUE);r.bold=row is rows[0]
  trpr=t.rows[-1]._tr.get_or_add_trPr();el=OxmlElement('w:cantSplit');trpr.append(el)
 pr=t._tbl.tblPr;bd=OxmlElement('w:tblBorders')
 for k in ['top','bottom','insideH']:
  el=OxmlElement('w:'+k);el.set(qn('w:val'),'single' if k!='insideH' else 'nil');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'000000');bd.append(el)
 for k in ['left','right','insideV']:
  el=OxmlElement('w:'+k);el.set(qn('w:val'),'nil');bd.append(el)
 pr.append(bd);return t
def page():
 return
 x=doc.add_paragraph();x.paragraph_format.space_after=Pt(0);x.paragraph_format.space_before=Pt(0);x.paragraph_format.line_spacing=Pt(1);x.add_run().add_break(WD_BREAK.PAGE)

# Page 1: architectural motivation and precise contribution.
p(old[1].text,False,'Title',16,True,True,after=7)
p(old[3].text,False,size=10,bold=True,center=True,after=3)
p('Abstract—The stacked polyphase bridge (SPB) partitions a high-voltage traction dc link among series-connected submodules, enabling the use of low-voltage gallium nitride (GaN) devices. Retaining their loss advantages at traction current requires sufficient drain- and gate-voltage margins in the physical building block. This paper evaluates a phase leg for a 300-kW, 1200-V drive, starting with a charge-based device comparison and a preliminary four-device parallel arrangement using the 100-V EPC2361. A KiCad–Ansys Q3D–LTspice workflow connects the routed prototype to a coupled parasitic network. Despite an estimated local commutation-loop inductance of 0.41 nH, the simulated voltage margin depends on gate-loop inductance, drive settings, and operating current. With a 10-nH gate loop and revised drive settings, sampled positive-current points from 1 A to 322 A remain below the 90-V drain–source target at a 75-V local bus; a 5% bus increase exceeds that target at rated current. The contribution is a quantified assessment of how implementation constraints feed back into SPB voltage partitioning. Experimental validation of one building block is planned for the full paper.',style='Abstract')
p(old[5].text,False,size=9,after=3)
h('I. INTRODUCTION')
p('High dc-link voltages support traction power levels of several hundred kilowatts while requiring substantial phase current [1]. In a conventional two-level bridge, the switches block the full dc-link voltage. The stacked polyphase bridge (SPB) instead connects three-phase bridges in series on the dc side, each supplying an isolated winding set of a common machine [2], [3]. With suitable bypass hardware and winding control, its modular structure can support operation after a submodule fault at reduced capability. This benefit is conditional on the remaining submodules’ voltage and current margins; bypass operation is not evaluated here. Fig. 1 shows the topology and the building block considered.')
fig('fig01_topology',454,'Fig. 1. (a) SPB and isolated winding sets of a common multiphase machine. (b) Three-phase submodule; each switch represents four parallel GaN devices. The diode denotes reverse conduction, not an intrinsic p–n body diode.')
p(old[21].text,False)
p('Previous work establishes SPB modulation and losses [3], dc-link stability [5], and comparisons with alternative GaN converters [6]. Studies of paralleled GaN stages identify commutation inductance, source coupling, and unequal gate impedance as important constraints [7]–[9]. The contribution here is to connect these implementation constraints to the SPB voltage choice quantitatively. A peak-current sizing screen is followed by a routed-network current sweep and voltage/temperature sensitivities. The resulting margins show why a favorable device figure of merit and a small local power loop do not alone establish a usable submodule voltage. The current-range and voltage-variation checks close the gap between preliminary sizing and the routed implementation.')
page()

# Page 2: device choice and initial conditions.
h('II. TRACTION REQUIREMENTS AND LOW-VOLTAGE DEVICE SELECTION')
h('A. Traction Drive Requirements',2)
p(old[25].text,False);eq(26)
p('Here, Vdc is the total dc-link voltage, Iph,rms is the rms phase current, and cosφ is the power factor. The modulation index M defines the fundamental phase-voltage peak as M Vm/2. Space-vector modulation is assumed, for which M = 1.15 is below 2/√3. These specifications establish the phase-current requirement for device selection and parallel-count assessment.')
p('TABLE I. DESIGN OPERATING POINT AND PRELIMINARY CONSTRAINTS',True,size=9,center=True,before=3,after=2)
table([['Quantity','Symbol','Value'],['Active power / dc-link voltage','P / Vdc','300 kW / 1200 V'],['Modulation index / power factor','M / cosφ','1.15 / 0.9'],['Phase current, rms / peak','Iph','227.7 A / 322.1 A'],['Switching frequency','fsw','50 kHz'],['Junction limit / ambient','Tj,max / Ta','125 °C / 40 °C'],['Initial submodules / local bus','N / Vm','16 / 75 V'],['Drain–source peak target','VDS,target','90 V']],[242,112,146])
h('B. Semiconductor Voltage-Class Comparison',2)
p('Fig. 2 screens the surveyed devices using typical 25 °C on-resistance and charge-equivalent output capacitance, Coss,Q = Qoss(Vtest)/Vtest. Following [4], the charge-based device figure of merit is');eq(34)
p('Lower τ = RDS(on) Coss,Q gives higher D-FOM. Quoted test voltages differ between classes and are not a common fraction of rating, so this comparison is a screening tool. The EPC2361 has the lowest product in this set, 1.35 ps. Its 90-nC output charge at 50 V gives 1800 pF, distinct from its 1019-pF differential Coss [10]. Subsequent switching assessment uses nonlinear device models.')
fig('fig02_device_survey_explicit_basis',500,'Fig. 2. Device screening basis and quoted capacitance test voltages. Dashed contours denote constant RDS(on) Coss,Q; device IDs link the plot to the data.')
h('C. Initial Submodule Voltage',2)
p(old[40].text,False);eq(41)
p('The 100-V candidate starts at Vm = 75 V and N = 16. The 90-V peak target reserves 15 V above nominal and 10 V below the device rating. Layout and switching assessment must establish these allowances. Inadequate margin requires a lower Vm and higher N. Bypassing one of sixteen submodules at unchanged total voltage would raise the remaining local buses to 80 V, requiring a separate fault-operation assessment.')
h('III. SINGLE-CELL CHARACTERIZATION AND PARALLEL COUNT')
h('A. Single-Cell Switching Characterization',2)
p('The manufacturer’s EPC2361 model [10] is assessed at 27 °C and 75 V with one device per switch and positive inductive-load current. Gate/power-loop combinations are 10/20 nH and 0.5/1 nH, respectively. Gate commands are −1/5 V; external turn-on/off and driver pull-up/down resistances are 3/1 Ω and 0.85/0.35 Ω. Common-source inductance is 0.03 nH and the maximum time step is 0.5 ns. Gate-loop values are assumed bounds, not extracted measurements.')
page()

# Page 3: first-pass sizing and physical arrangement.
fig('fig03_complete_switching_maps',500,'Fig. 3. Single-cell voltage peaks and low-side switching energies at 75 V. Legend: gate/power-loop inductance. LS/HS denote low/high side; the 90-V target is shown in (a) and (b).')
p('Fig. 3 separates low-side turn-off stress from high-side stress during low-side turn-on. Voltage peaks cover the complete 1-µs off interval and the following 0.5-µs on interval. Signed terminal-energy integrals use 150 ns for turn-on and the complete off interval, ending 1 ns before turn-on, for turn-off. The longer window captures slow output-capacitance charging at low current. The compact path passes the 90-V screen near 80 A per device, but high-side stress can exceed the target at lower current. Thus, peak-current compliance alone is insufficient. Increasing gate resistance can reduce overshoot at the cost of switching energy.')
h('B. Loss and Thermal Assessment',2)
p(old[50].text,False);eq(51)
p('Fig. 4 uses the energy maps averaged over a sinusoidal phase-current magnitude for a first-pass loss estimate at 50 kHz. Conduction uses 0.75 mΩ at 25 °C with the datasheet temperature factor; the model also includes 10-ns dead time, gate charge of 28 nC, a 6-V gate swing, and a provisional 2.9-µJ capacitive freewheeling term per device per cycle. Cooling is assumed to provide 0.65 K/W from the shared phase-leg sink to ambient and 7.62 K/W from each junction to the sink, including a provisional interface/spreader contribution. These assumed resistances are not validated thermal measurements.')
fig('fig04_sizing_remeasured',500,'Fig. 4. First-pass (a) phase-leg loss and (b) low-side turn-off peak at the peak current per device. Legend in (b): gate/power-loop inductance. Grey line: 90 V.')
h('C. Selection of Four Parallel Devices',2)
p('At 10 nH/0.5 nH, four devices give an estimated 18.6-W phase-leg loss and 70 °C junction temperature at 40 °C ambient under the assumed cooling model. Two devices exceed the 125 °C limit (approximately 144 °C), while three exceed the peak-current voltage screen (approximately 99 V). Four is therefore the smallest count passing this preliminary screen, not the minimum-loss count or proof of full-cycle feasibility. The routed-network assessment must resolve the remaining current-range constraint.')
h('IV. GATE-DRIVE CONFIGURATION AND CELL ARRANGEMENT')
h('A. Current-Sharing Sensitivity',2)
p('The two-device comparison in Fig. 5 uses 75 V, 120 A nominal total current, 0/5-V commands, 3-Ω gate resistors, and nominal 10-nH gate loops. Imbalance is defined as 100|Ipk,1 − Ipk,2|/(Ipk,1 + Ipk,2), using each branch’s turn-on maximum. A 0.1-nH power-path mismatch gives 2%; 10/15-nH gate loops give 17%; and a 0.05-nH source mismatch without Kelvin returns gives 9%. These are responses to different perturbations, not a universal ranking of sensitivities.')
fig('fig05_sharing_final_conditions',454,'Fig. 5. (a) Recomputed peak-current imbalance. (b) Paired gate drive. (c) Gate and Kelvin-source connections. HO/LO denote high-/low-side driver outputs.')
h('B. Paired Gate Drive and Kelvin Returns',2)
p('Four devices per switch position are arranged as two symmetric pairs. Each 2EDF7275K dual-channel driver [11] drives two high-side devices and two low-side devices, with an individual gate resistor per device. Two drivers serve the phase leg. Dedicated Kelvin returns separate gate and power-current paths; matched gate impedances and symmetric copper paths limit transient inequality. Present simulations assume synchronous driver commands; timing skew and physical realization of the negative gate bias remain validation items.')
page()

# Page 4: extracted prototype and reproducible settings.
h('V. LOW-VOLTAGE GaN UTILIZATION IN THE ROUTED PROTOTYPE')
h('A. Layout and Parasitic Extraction',2)
p('The initial voltage and parallel count are checked using the routed prototype phase leg. Fig. 6 connects KiCad placement and routing, Ansys Q3D extraction, and LTspice assessment. Drain stress, gate disturbance, and branch currents guide layout and drive changes; insufficient margin feeds back into the submodule voltage rather than being hidden by the nominal device rating.')
fig('fig06_design_feedback',500,'Fig. 6. Design feedback from routed switching margins to the SPB voltage partition.')
p('Fig. 7 shows the printed circuit board (PCB) as a computer-aided design (CAD) rendering and the extracted conductor geometry.')
fig('fig07_cad_q3d_readable',500,'Fig. 7. (a) Prototype CAD rendering without heatsink. (b) Q3D copper model; colours identify rails, switch node, and terminals.')
p('The extracted power network contains 29 branches and 406 mutual-inductance terms, using dc resistance and partial inductances at 100 MHz. The approximately 0.41-nH local loop comprises 0.347 nH of copper and 0.062 nH of capacitor equivalent series inductance (ESL) under equal branch excitation at the device/capacitor ports. This scalar covers the PCB/capacitor contribution; device-package and gate-path inductances were not separately extracted. Switching simulations retain the coupled network, not only this scalar value. Gate-loop bounds remain 10/20 nH, split 70% in the forward path and 30% in the return.')
h('B. Prototype Switching Assessment',2)
p('A controlled-current commutation model evaluates the same eight-device power network at 1, 40, 80, 160, 240, and 322.1 A total positive current. The current source approximates a large load inductance during the transition. At approximately 316 A, its peak voltage and summed switching energy agree within 2% with the inductive-load case. Unless stated otherwise, Vm = 75 V and model temperature is 27 °C; all settings use a 5-V on command, 1-Ω turn-off resistance, and 0.85/0.35-Ω driver pull-up/down resistance. The maximum time step is 0.2 ns. Table II compares the drive settings on this common basis.')
p('TABLE II. MATCHED DRIVE COMPARISON AT 322.1 A AND 75 V',True,size=9,center=True,before=3,after=2)
table([['Setting','Lg / Rgon / Voff','VDS,pk','VGS,off,pk','Eon / Eoff'],['A','20 nH / 2 Ω / 0 V','97.2 V','1.43 V','25.6 / 7.3 µJ'],['B','20 nH / 3 Ω / 0 V','90.1 V','1.42 V','30.9 / 7.3 µJ'],['C','20 nH / 3 Ω / −1 V','90.7 V','0.45 V','30.5 / 6.2 µJ'],['D','10 nH / 3 Ω / −1 V','88.8 V','0.43 V','32.9 / 5.8 µJ']],[46,166,75,91,122])
p('VDS,pk is the largest device peak across both assessed transitions; VGS,off,pk is the largest held-off high-side gate peak. Energies are mean low-side per-device terminal integrals, not total phase-leg losses.',True,size=9,after=2)
fig('fig08_routed_margin_map',500,'Fig. 8. (a), (b) High-side drain and held-off gate waveforms for settings A–C at rated current. (c) Maximum device drain stress over both transitions for C and D. References: 90 V and 0.8 V.')
page()

# Page 5: quantitative design feedback, validation boundary, references.
h('C. Switching Margins and Feedback to Voltage Partitioning',2)
p('Table II shows that increasing turn-on resistance reduces rated-current drain stress at an energy cost. Negative off-state bias suppresses the held-off gate disturbance but does not independently recover the drain margin. Setting D reduces the rated-current peak to 88.8 V, with a mean low-side 90%–10% voltage fall time of 5.9 ns and a 38.7-µJ sum of turn-on/off energies. Its simulated positive branch-current peak spread is 1.15%, using (Ipk,max − Ipk,min)/(Ipk,max + Ipk,min). These values quantify the switching-speed/energy tradeoff rather than establish a global optimum.')
p('For setting D, sampled nominal-current points remain between 88.0 and 88.8 V, whereas setting C reaches 91.8 V near 80 A total current (Fig. 8(c)). The low-current high-side transient therefore remains relevant even when the rated-current result is close to target. The 0.8-V reference is the minimum static threshold at 25 °C [10], not an absolute gate-voltage rating or proof against dynamic turn-on. The revised cases reach approximately −2.4 V minimum gate voltage, within the stated −4/+6-V ratings, but driver compatibility and dynamic behavior require measurement.')
p('At rated current, raising the local bus by 5% to 78.75 V increases setting D’s drain peak to 92.2 V at 27 °C, exceeding the design target. Forced 125 °C device-model cases give 84.6 V at 75 V and 88.4 V at 78.75 V; the extracted copper network is held fixed. Thus, the nominal sixteen-submodule result does not demonstrate the proposed voltage-variation allowance. An illustrative seventeen-submodule allocation gives 74.12 V per module at +5% total bus and 88.1/83.8-V rated-current peaks at 27/125 °C. This is an electrical headroom comparison, not validation of a seventeen-winding machine or its full current range. It demonstrates the architectural consequence of unresolved switching margin: either the network/drive must improve or the voltage partition must change.')
h('VI. EXPERIMENTAL VALIDATION AND FULL-PAPER SCOPE')
p('One building block will be tested at controlled bus voltage, current, and temperature. Drain and Kelvin-referenced gate transients, individual branch currents, and deskewed switching-energy measurements will be compared with predictions. The planned voltage acquisition bandwidth is at least 500 MHz; current-sensor bandwidth, probe loading, and timing uncertainty will be reported. Negative-bias implementation and driver compatibility will be verified before operation. Because of the digest page limit, the detailed experimental procedure and resulting comparisons are reserved for the full paper; no experimental result is claimed here. Regenerative current, inter-driver skew, parasitic tolerances, insulation, and temperature-dependent dynamic losses remain outside the present simulation evidence.')
h('VII. CONCLUSION')
p('The study links low-voltage GaN selection to the switching margins of an SPB phase leg. A four-device candidate and a 0.41-nH local loop do not by themselves establish feasibility. The routed model identifies a 10-nH gate-loop candidate meeting the sampled nominal 90-V target, but its +5% bus case requires further design change or voltage repartitioning. This quantified feedback, rather than device figure of merit alone, governs the proposed low-voltage GaN utilization.')
h('REFERENCES',blue=True)
refs=[
'[1] J. Schneider et al., “The novel megawatt charging system standard: Impact on battery size and cell requirements for battery-electric long-haul trucks,” eTransportation, vol. 17, Art. no. 100253, Jul. 2023.',
'[2] S. Norrga et al., “A novel inverter topology for compact EV and HEV drive systems,” in Proc. IECON, 2013, pp. 6590–6595.',
'[3] L. Jin et al., “Modulation and power losses of a stacked polyphase bridge converter,” IEEE J. Emerg. Sel. Topics Power Electron., vol. 5, no. 1, pp. 409–418, Mar. 2017.',
'[4] J. Azurza Anderson et al., “New figure-of-merit combining semiconductor and multi-level converter properties,” IEEE Open J. Power Electron., vol. 1, pp. 322–338, 2020, doi: 10.1109/OJPEL.2020.3018220.',
'[5] M. Nikouie et al., “DC-link stability analysis and controller design for the stacked polyphase bridges converter,” IEEE Trans. Power Electron., vol. 32, no. 2, pp. 1666–1674, Feb. 2017.',
'[6] G. Rohner et al., “Comparative evaluation of three-phase three-level flying capacitor and stacked polyphase bridge GaN inverter systems for integrated motor drives,” Electronics, vol. 13, Art. no. 1259, 2024.',
'[7] J. A. Brothers et al., “GaN module design recommendations based on the analysis of a commercial 3-phase GaN module,” in Proc. IEEE ECCE, 2019, pp. 4109–4116.',
'[8] J. L. Lu and D. Chen, “Paralleling GaN E-HEMTs in 10kW–100kW systems,” in Proc. IEEE APEC, 2017, pp. 3049–3056.',
'[9] M. Tuan Tran et al., “A high-performance GaN power module with parallel packaging for high-current and low-voltage traction inverter applications,” IEEE J. Emerg. Sel. Topics Power Electron., vol. 13, no. 1, pp. 1188–1209, Feb. 2025.',
'[10] Efficient Power Conversion, “EPC2361 eGaN FET datasheet,” Jul. 20, 2026.',
'[11] Infineon Technologies, “2EDF7275K data sheet,” rev. 2.8, Aug. 8, 2022.'
]
for s in refs:p(s,True,size=9)
for sec in doc.sections:
 for footer in [sec.footer,sec.first_page_footer]:
  for element in list(footer._element):footer._element.remove(element)
  x=footer.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER
  r=x.add_run();r.font.name='Times New Roman';r.font.size=Pt(9);r.font.color.rgb=RGBColor(0,0,0)
  fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');x._p.append(fld)
doc.core_properties.title=old[1].text;doc.core_properties.comments='Review revision: additions and revised text in blue. Original submission files preserved.'
doc.save(OUT)
(A/'revision_text.txt').write_text('\n'.join(x.text for x in doc.paragraphs),encoding='utf-8')
print(OUT);print('Words',sum(len(x.text.split()) for x in doc.paragraphs))

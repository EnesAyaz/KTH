from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parent
REF=ROOT/'template/ICPE_2027_Digest_Template.docx'
D=Document(REF)
R=json.loads((ROOT/'simulation/results_selection/design_selection.json').read_text())
assert R['two_cell_control_example']['N']==2
assert R['illustrative_selected_winding']['N']==12
assert [d['N_voltage_min'] for d in R['device_classes']]==[20,14,10,4]
raw=REF.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
with ZipFile(REF) as z:
 inventory={n:{'bytes':len(z.read(n)),'sha256':hashlib.sha256(z.read(n)).hexdigest()} for n in z.namelist()}
(ROOT/'template/template_inventory.json').write_text(json.dumps({'reference_sha256':sha,'parts':inventory},indent=2))
# Preserve the source package; only body slots and documented additions change.
sect=deepcopy(D.sections[-1]._sectPr)
sect.insert(0,deepcopy(D.sections[0]._sectPr.find(qn('w:footerReference'))))
for ch in list(D._element.body):D._element.body.remove(ch)
D._element.body.append(sect)
s=D.sections[0];s.left_margin=Cm(2.5);s.right_margin=Cm(2.5)
cols=sect.find(qn('w:cols'))
if cols is not None:cols.set(qn('w:num'),'1')
style=D.styles['Title']; style.font.name='Times New Roman';style.font.size=Pt(16);style.font.bold=True;style.font.color.rgb=RGBColor(0,0,0)
style.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
style.paragraph_format.space_after=Pt(12);style.paragraph_format.space_before=Pt(0)
style.paragraph_format.line_spacing=1.0
D.core_properties.author='';D.core_properties.last_modified_by='';D.core_properties.title='Joint Selection of GaN SPB Cells and Pole-Changing Windings for Truck Propulsion'
D.core_properties.subject='ICPE 2027 ECCE Asia digest'

def p(text='',style='Text',size=10,bold=False):
 x=D.add_paragraph(style=style);x.paragraph_format.space_after=Pt(3);x.paragraph_format.line_spacing=1.0
 if style=='Caption':x.alignment=WD_ALIGN_PARAGRAPH.CENTER
 if style=='Text':x.paragraph_format.first_line_indent=Cm(.35);x.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
 r=x.add_run(text);r.font.name='Times New Roman';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor(0,0,0)
 return x

def future(text):
 x=p(text,'Text',10)
 for run in x.runs:run.font.color.rgb=RGBColor(192,0,0)
 return x

sub_counter=0
pending_page=False
def h(text):
 global sub_counter,pending_page
 sub_counter=0
 x=p(text,'Heading 1',12,True)
 if pending_page:x.paragraph_format.page_break_before=True;pending_page=False
 x.paragraph_format.space_before=Pt(8);x.paragraph_format.space_after=Pt(6)
 return x

def sub(text):
 global sub_counter
 label=chr(65+sub_counter); sub_counter+=1
 x=p(label+'. '+text,'Heading 2',11,True)
 np=OxmlElement('w:numPr');ni=OxmlElement('w:numId');ni.set(qn('w:val'),'0');np.append(ni);x._p.get_or_add_pPr().append(np);x.paragraph_format.space_before=Pt(5);x.paragraph_format.space_after=Pt(3)
 # Use source subsection typography without accidental numbering repetition.
 return x

def eq(text,num):
 def mr(txt,normal=False):
  r=OxmlElement('m:r')
  if normal:
   pr=OxmlElement('m:rPr');normalel=OxmlElement('m:nor');pr.append(normalel);r.append(pr)
  t=OxmlElement('m:t');t.text=txt;r.append(t);return r
 def sb(base,idx):
  el=OxmlElement('m:sSub');e=OxmlElement('m:e');e.append(mr(base));el.append(e);ss=OxmlElement('m:sub');ss.append(mr(idx));el.append(ss);return el
 def frac(numerator,denominator):
  f=OxmlElement('m:f');nu=OxmlElement('m:num');de=OxmlElement('m:den')
  for obj in numerator:nu.append(obj)
  for obj in denominator:de.append(obj)
  f.append(nu);f.append(de);return f
 x=D.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(6)
 math=OxmlElement('m:oMath')
 if num==1:
  for k,ph in enumerate('abc'):
   if k:math.append(mr(' + '))
   math.append(sb('i',ph+',j'))
  math.append(mr(' = 0'))
 elif num==2:
  math.append(sb('N','V'));math.append(mr(' = ⌈'));math.append(frac([sb('V','dc,max'),sb('k','imb'),sb('k','ov')],[mr('u'),sb('V','r')]));math.append(mr('⌉'))
 elif num==3:
  math.append(mr('a, b ∉ 3ℤ;   Q/(3g) ∈ ℕ;   Q/(3N) ∈ ℕ'))
 elif num==4:
  math.append(sb('k','p,ν'));math.append(mr(' = |sin('));math.append(frac([mr('πνy')],[mr('Q')]));math.append(mr(')|'))
 else:
  math.append(sb('T','e'));math.append(mr(' = '));math.append(frac([mr('3N')],[mr('2')]));math.append(mr('p['));math.append(sb('ψ','f'));math.append(mr(' + ('));math.append(sb('L','d'));math.append(mr(' − '));math.append(sb('L','q'));math.append(mr(')'));math.append(sb('i','d'));math.append(mr(']'));math.append(sb('i','q'))
 x._p.append(math);rr=x.add_run('    ('+str(num)+')');rr.font.name='Times New Roman';rr.font.size=Pt(11)
 return x

def fig(name,caption,width=16):
 x=D.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(2);x.paragraph_format.keep_with_next=True
 x.paragraph_format.space_before=Pt(6)
 x.add_run().add_picture(str(ROOT/'figures'/name),width=Cm(width))
 docPr=x._p.xpath('.//wp:docPr')[0];docPr.set('descr',caption)
 x=p(caption,'Caption',10);x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(6)
 return x

def table(headers,rows,widths):
 t=D.add_table(rows=1,cols=len(headers));t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
 for c,w in zip(t.columns,widths):c.width=Cm(w)
 for cell,txt,w in zip(t.rows[0].cells,headers,widths):cell.width=Cm(w);cell.text=txt
 for row in rows:
  cells=t.add_row().cells
  for c,txt,w in zip(cells,row,widths):c.width=Cm(w);c.text=str(txt)
 for ri,row in enumerate(t.rows):
  trpr=row._tr.get_or_add_trPr();avoid=OxmlElement('w:cantSplit');trpr.append(avoid)
  if ri==0:
   repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
  for cell in row.cells:
   pr=cell._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
   for edge in ['top','left','bottom','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'nil');b.append(e)
   
   for edge in (['top','bottom'] if ri==0 else ['bottom'] if ri==len(t.rows)-1 else []):
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'5' if ri==0 else '4');e.set(qn('w:color'),'000000');b.append(e)
   pr.append(b)
   if ri==0:
    pass
   margins=OxmlElement('w:tcMar')
   for edge in ['top','left','bottom','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:w'),'30' if edge in ['top','bottom'] else '65');e.set(qn('w:type'),'dxa');margins.append(e)
   pr.append(margins)
   for para in cell.paragraphs:
    para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.space_after=Pt(1);para.paragraph_format.space_before=Pt(1);para.paragraph_format.line_spacing=1
    for r in para.runs:r.font.name='Times New Roman';r.font.size=Pt(10);r.bold=ri==0
 return t

def page():
 global pending_page
 pending_page=True
# PAGE ONE
p('Joint Selection of GaN SPB Cells and Pole-Changing\nWindings for Truck Propulsion','Title',16,True)
p('Abstract—Stacked polyphase bridges (SPBs) enable low-voltage power devices to supply high-voltage truck propulsion systems while independently controlling multiple stator winding groups. This paper presents a device–winding co-design method that exploits these groups for electronic pole changing. Discrete GaN voltage ratings, cell-voltage stress, coil allocation, three-phase balance, and pole ratio are treated as coupled constraints. A constructive winding analysis compares 2:1, 3:1, and 5:2 pole ratios. For a 1.2-kV link, the investigated design space includes 200-V/12-cell and 650-V/4-cell configurations sharing a 36-slot 12/6-pole winding basis. An explicit 36-slot construction gives a winding factor of 0.866 in both 12- and 6-pole modes while cancelling the alternate selected stator order. The resulting candidates establish selected-order winding and voltage compatibility within the investigated family. A preliminary two-dimensional magnetostatic model illustrates two rotor-field settings. Loss analysis and machine-based HE-IPM torque–speed and power–speed characteristics will be developed in the full paper.','Abstract',10)
keywords=p('Index Terms—Electric truck propulsion, gallium nitride, hybrid excitation, pole changing, stacked polyphase bridge.','Text',10);keywords.paragraph_format.first_line_indent=Cm(0)
h('Introduction')
p('Megawatt-level charging of battery-electric trucks motivates higher battery and dc-link voltages to limit current and cable loss at a given power [1]. In a conventional two-level truck propulsion inverter, each switch must block the full dc-link voltage together with switching overshoot. Increasing the blocking-voltage requirement introduces conduction- and switching-loss trade-offs that constrain the simultaneous improvement of efficiency and switching frequency. Limited switching frequency increases current-ripple-related machine losses, while common-mode voltage (CMV), high dv/dt, and associated insulation and bearing stress must also be addressed.')
p('Multilevel inverters provide an alternative to full-link-voltage switching. Three-, five-, and seven-level neutral-point-clamped (NPC) or flying-capacitor (FC) implementations can employ lower-blocking-voltage devices and generate smaller output-voltage steps. With appropriate modulation, these steps can reduce current distortion and CMV [2]. However, the additional switches, clamping or flying-capacitor networks, and balancing functions introduce further failure mechanisms and implementation complexity. Fault-tolerant operation requires explicit redundancy, fault isolation, or reconfiguration; it does not follow inherently from the number of voltage levels.')
p('The SPB offers a modular route to voltage partitioning: series-connected dc cells supply separate polyphase winding groups [2]. Low cell voltages permit suitable low-voltage GaN devices, while the machine is implemented with multiple three-phase winding sets whose neutral points remain isolated. The resulting independently controlled inverter units are already required by the voltage architecture. Their current phase and sequence can therefore be used as additional machine-control degrees of freedom.')
p('Pole changing can exploit this flexibility to trade low-speed torque against high-speed capability and operating-point losses. Variable-pole induction drives have demonstrated partial-load and high-speed loss benefits [3], and pole-changing electric-vehicle drives have been investigated for wide-speed propulsion requirements [4]. Such benefits motivate drive-cycle-dependent pole selection, although net cycle savings must include converter and excitation losses. Conventional implementations use Dahlander-type stator reconnection or multiple inverter units to reverse selected coil-group currents. Purpose-designed synchronous and hybrid-excited rotors can change their field polarity accordingly [5]. An SPB can reuse its inverter units for this stator rephasing without adding dedicated stator converters, provided the winding is admissible in both modes.')
p('Prior SPB voltage partitioning [2] and electronic pole changing [3]–[5] do not alone determine compatible cell and winding counts. This paper adds a construction-specific selection method: balanced isolated three-phase groups and alternate-order stator-MMF cancellation are checked jointly with discrete device ratings and coil allocation. The analytical result is a reproducible admissibility frontier, rather than a manufactured machine or an efficiency optimum.')
future('The introduction is abbreviated for the digest. The full paper will expand the comparison with prior SPB and synchronous pole-changing drives and relate the design objectives to truck propulsion duty.')
# PAGE TWO
page();h('SPB Drive Architecture and Design Constraints')
fig('ieee_fig1_spb_architecture.png','Fig. 1. SPB truck-propulsion architecture. (a) Series dc cells supply separate winding sets. (b) Each cell contains a three-phase bridge and supplies a winding set with a local floating star point.',16)
p('The considered drive contains N series-connected dc cells, each supplying a three-phase winding group through a two-level bridge. The nominal cell voltage is Vdc/N. The star point of one winding set is not connected to another set or to the dc link. Consequently, each group satisfies')
eq('',1)
p('The 3N controlled phase branches therefore provide 2N independent instantaneous current coordinates. Balanced current commands are insufficient by themselves: the phase back-EMF magnitudes, phase displacement, and impedance must also be compatible with balanced operation at both selected pole counts. Equal modal gain and current amplitude, with a common current angle relative to each selected modal EMF, give equal ideal electromagnetic conversion power. This does not establish balance under additional rotor harmonics, regeneration, or transitions; capacitor sizing and active balance control remain design tasks.')
sub('Device voltage and coil allocation')
p('Let Vr be the device blocking-voltage rating, u its allowable utilization, and kimb and kov the assumed imbalance and overshoot factors. The voltage-dependent lower bound is')
eq('',2)
p('A 1200-V nominal link and a 1320-V maximum link are considered with kimb = kov = 1.10 and u = 0.80. Table I gives the resulting lower bounds for four verified device classes [6]. The selected parts illustrate discrete voltage and resistance trade-offs; their current, package, thermal, and switching characteristics are not interchangeable.')
cap=p('TABLE I\nDEVICE CLASSES AND CELL-COUNT LOWER BOUNDS','Caption',10);cap.paragraph_format.keep_with_next=True
table(['Rating','Device [6]','Minimum N','Phase branches','RDS(on), max'],[['100 V','EPC2361','20','60','1 mΩ'],['150 V','EPC2305','14','42','3 mΩ'],['200 V','EPC2304','10','30','5 mΩ'],['650 V','IGLT65R025D2','4','12','30 mΩ']],[1.8,3.1,2,3.3,3.3])
p('For Q conventional double-layer coil positions, the assumed one-coil-per-position construction gives C = Q independently connected coils. At least one coil per phase branch requires 3N ≤ C; equal allocation additionally requires integer c = C/(3N). A conventional single-layer arrangement instead gives C = Q/2. Additional independently fed conductor subdivisions can change these bounds, but require separate lead, insulation, and manufacturing analysis. The slot bounds used here are therefore construction specific.')
future('The full paper will expand this section with truck operating requirements, sensitivity to voltage margins, winding insulation and lead constraints, and dc-cell power-balance control. The present bounds are preliminary selection constraints.')
# PAGE THREE
page();h('Winding Admissibility for Pole Changing')
p('Let PH and PL denote total pole counts, with pH = PH/2 and pL = PL/2. Define g = gcd(pH,pL), a = pH/g, and b = pL/g. In the investigated family, the three phase-coil axes are displaced by 120°/g mechanically. Their electrical phase displacements are therefore 120a and 120b degrees. The uniform phase-axis triple has balanced selected-order induced-voltage phasors when')
eq('',3)
p('Equation (3) is a phase-axis and allocation screen, not a sufficient machine-feasibility theorem. Define d = Q/(3g). Primitive triples have start slots 1 + q + 3dt + kd for q = 0, …, d − 1, t = 0, …, g − 1, and k = 0, 1, 2. Order triples by q, then t; consecutive blocks of c = Q/(3N) triples form each cell, with identical coil polarity and modulo-Q return slots at pitch y. Equal modal magnitudes across phases and cells and alternate-order rejection are checked to 10⁻⁸ relative tolerance. Current commands align with the selected-order coil phasors. Balanced impedance, mutual coupling, and rotor-harmonic back-EMF are not established by this check.')
sub('Pole ratio and coil span')
p('The reduced orders of a 2:1 combination are 2 and 1, yielding opposite phase sequences. The 5:2 combination also satisfies (3), with equal sequences. A 3:1 combination gives a zero-sequence spatial order within this uniform-triple family and is excluded by the three-wire connection. This result applies to the stated construction; it does not exclude alternative distributed, reconfigurable, or nonuniform winding families.')
fig('ieee_fig2_pitch_ratio.png','Fig. 2. Minimum pitch factor of the two pole modes versus normalized coil span. The vertical line denotes 1.5 high-pole pitches. The 3:1 curve describes pitch utilization only; it does not satisfy the balanced-cell condition of this construction.',14.8)
p('For coil pitch y in slots, spatial pole-pair order ν, and high-pole pitch τH = Q/PH, the pitch factor is')
eq('',4)
p('The continuous 2:1 case maximizes the smaller modal pitch factor at 0.866 at y/τH = 4/3. The unrestricted 5:2 case reaches approximately 0.975 at y/τH = 20/7; imposing y/τH ≤ 1.5 reduces its optimum to approximately 0.782. Thus, the highest pitch factor can require a substantially longer end winding. Slot discretization, leakage, resistance, and manufacturability must be included before a pitch optimum is selected.')
future('The full paper will expand the ratio comparison with discrete coil-span choices, end-winding length, leakage, and harmonic MMF. The digest presents only the analytical pitch trade-off.')
sub('Reproducible 12 Cell Winding')
p('For Q = 36, N = 12, and coil pitch y = 4, define q = 0, …, 3, t = 0, …, 2, and phase index k = 0, 1, 2. Cell j = 3q + t + 1 has start slot s = 1 + q + 12t + 4k and return slot 1 + [(s + 3) mod 36], with identical coil polarity. Relative current phases are 60q + 240k degrees for 12 poles and 30q + 120k degrees for 6 poles; a common torque-angle offset is allowed. Table II checks this construction.')
p('With θs = 2π(s − 1)/36, define Gν = Σs Is[exp(−iνθs) − exp(−iνθreturn)]/72 and Is = exp(ipθs). Thus |Gp| is the winding factor and max(|Gother|, |G−other|)/|Gp| is the alternate-order residual. Connecting the three t-indexed coils in series for each (q,k) gives a four-cell version with the same 0.866 factors. Two-cell control is also possible, but does not satisfy the present 650-V voltage bound; it is not a universal minimum theorem.')
future('The full paper will add winding diagrams, complete connections, impedance matrices, and rotor-harmonic checks for this example.')
# PAGE FOUR
page();h('Cell and Winding Selection Results')
p('The search uses N = 1–32, Q = 18, 24, …, 96, and pole counts H/L = 8/4, 12/6, 16/8, 24/12, 32/16, 12/4, 24/8, 10/4, and 20/8. The frontier uses unrestricted integer pitches 1–Q/2, maximizing the smaller winding factor; the 1.5-pitch cap is a separate sensitivity. For each rating and pole pair, accepted candidates are ranked by lowest N, then Q. Passenger-car examples (48 slots/8 poles [7], [8]; 72/12 [9]) motivate a sensitivity range, not truck design limits. Q ≤ 60 and Q ≤ 72 are study constraints.')
cap=p('TABLE II\nDIRECT COIL-SIDE FOURIER CHECK FOR THE 36-SLOT CONSTRUCTION','Caption',10);cap.paragraph_format.keep_with_next=True
table(['Total poles','Complex desired gain Gp','Winding factor','Alternate-order residual'],[['12','0.750 − i0.433','0.866','< 10⁻¹²'],['6','0.750 + i0.433','0.866','< 10⁻¹²']],[2,4.5,2.7,4.3])
fig('ieee_fig3_feasible_region.png','Fig. 3. Screened windings in the investigated family: (a) 8/4 and (b) 12/6 poles. Labels give (N, Q); dashed/dotted lines mark 60/72 slots.',12.7)
p('For 650-V devices, (2) gives stresses of 798.6, 532.4, and 399.3 V for two, three, and four cells. Two exceed the continuous rating; three remain below it but exceed the chosen 520-V allowance (0.8 × 650). Four pass this voltage screen and admit a 36-slot 12/6-pole winding.')
cap=p('TABLE III\nREPRESENTATIVE DEVICE–WINDING COMBINATIONS','Caption',10);cap.paragraph_format.keep_with_next=True
table(['Device class','N','Q','Total poles H/L','Design status'],[['200 V','12','36','12/6','Reference candidate'],['650 V','2','36','12/6','Exceeds continuous rating'],['650 V','3','54','12/6','Exceeds chosen 80% allowance'],['650 V','4','36','12/6','Passes voltage screen']],[2.1,.8,.8,3,6.8])
p('For the accepted 200-V/12-cell and 650-V/4-cell candidates, N RDS(on) gives 60 and 120 mΩ at equal group current and paralleling. These arithmetic indices are not equal-output-power losses or a final device ranking.')
future('The full paper will expand the shortlist with temperature-dependent converter and winding losses, parallel-device area, and cooling. Both the 200-V/12-cell and 650-V/4-cell cases remain preliminary.')
h('Converter and Machine Design to Be Expanded')
sub('GaN Building Block Comparison')
future('The full paper will compare 200-V and 650-V building blocks, including paralleling, gate driving, dc capacitance, voltage balancing, and cooling.')
sub('Hybrid Excited Machine Design and FEA')
future('The full paper will balance PM/wound-pole flux and add geometry optimization with measured material data, loaded FEA, and loss maps.')
# PAGE FIVE
page();h('Preliminary HE IPM Model and Propulsion Concept')
p('The 36-slot model uses a 17.5-mm stator yoke, 1-mm gap, 0.7-T PMs, and synthetic nonlinear steel. Its 6-pole yoke peak is 1.70 T; the selected air-gap harmonic is 0.55% below the 25-mm-yoke baseline. Residual rotor harmonics and unequal PM/wound-pole flux remain optimization targets.')
fig('ieee_fig4_basic_he_ipm_fea_17p5mm.png','Fig. 4. HE-IPM geometry and no-load FEA fields; colors clipped above 2 T (computed local peak: 2.95 T).',14.5)
p('Figure 5 is a conceptual mode trade-off, not a prediction from the FEA geometry.')
fig('ieee_fig5_mode_tradeoff.png','Fig. 5. Conceptual mode curves: P = Tωm; arbitrary reference scales, not FEA performance predictions.',14.5)
future('The full paper will report HE-IPM loss analysis and FEA-based torque–speed/power–speed curves, including excitation, inverter losses, current/voltage and thermal limits, truck duty, and pole transitions.')
h('Conclusion')
p('The preliminary winding and field results motivate coupled converter–machine optimization in the full paper.')
future('The conclusion will be updated with the full-paper results.')
x=h('References');num=x._p.get_or_add_pPr();n=OxmlElement('w:numPr');i=OxmlElement('w:numId');i.set(qn('w:val'),'0');n.append(i);num.append(n)
refs=[
'[1] CharIN, "Megawatt Charging System—Recommendations and Requirements," white paper, ver. 2.0, May 2025.',
'[2] G. Rohner, J. Huber, S. Miric, and J. W. Kolar, "Comparative Evaluation of Three-Phase Three-Level Flying Capacitor and Stacked Polyphase Bridge GaN Inverter Systems for Integrated Motor Drives," Electronics, vol. 13, art. 1259, 2024, doi: 10.3390/electronics13071259.',
'[3] E. Libbos, E. Krause, A. Banerjee, and P. T. Krein, "Inverter Design Considerations for Variable-Pole Induction Machines in Electric Vehicles," IEEE Trans. Power Electron., vol. 37, no. 11, pp. 13554–13565, 2022, doi: 10.1109/TPEL.2022.3177082.',
'[4] Rohith, L. Umanand, and B. Subba Reddy, "Pole Changing Wide Speed Range Induction Motor Drive for Electric Vehicles," in Proc. IEEE PEDES, 2018, pp. 1–5, doi: 10.1109/PEDES.2018.8707677.',
'[5] C. Conto and N. Bianchi, "On the Possibility to Achieve a Pole Change in Synchronous Motors," in Proc. IEEE ECCE, 2022, doi: 10.1109/ECCE50734.2022.9947754.',
'[6] Efficient Power Conversion, EPC2361/EPC2305/EPC2304 datasheets; Infineon, IGLT65R025D2 datasheet, rev. 1.1, 2026.',
'[7] T. Burress, "Electrical Performance, Reliability Analysis, and Characterization," ORNL, DOE Vehicle Technologies Annual Merit Review, project EDT087, 2017, slide 18.',
'[8] S. Oki and Y. Sato, "Nissan LEAF and e-POWER: Evolution of Motors and Inverters," IEEJ J. Ind. Appl., vol. 13, no. 1, pp. 8–16, 2024, doi: 10.1541/ieejjia.23006552.',
'[9] U.S. DOE, FY 2016 Annual Progress Report for Electric Drive Technologies, pp. 200–202, 2017.'
]
for text in refs:
 x=p(text,'Text',10);x.paragraph_format.first_line_indent=Cm(0);x.paragraph_format.space_after=Pt(2);x.paragraph_format.line_spacing=1

# Final controls: all author metadata empty; Word updates PAGE fields in memory.
u=OxmlElement('w:updateFields');u.set(qn('w:val'),'true');D.settings.element.append(u)
TEMP=ROOT/'qa/build_intermediate.docx';D.save(TEMP)
allow={'word/document.xml','word/_rels/document.xml.rels','word/styles.xml','word/settings.xml','[Content_Types].xml','docProps/core.xml'}
FINAL=ROOT/'ECCE_Asia_2027_Digest_17p5mm_650V.docx'
with ZipFile(REF) as src,ZipFile(TEMP) as new,ZipFile(FINAL,'w',ZIP_DEFLATED) as dest:
 for info in src.infolist():dest.writestr(info,new.read(info.filename) if info.filename in allow else src.read(info.filename))
 for name in new.namelist():
  if name not in src.namelist():dest.writestr(name,new.read(name))
with ZipFile(FINAL) as z:
 changed=[n for n in inventory if hashlib.sha256(z.read(n)).hexdigest()!=inventory[n]['sha256']]
 assert set(changed)<=allow,changed
 assert 'word/footer1.xml' not in changed
assert hashlib.sha256(REF.read_bytes()).hexdigest()==sha
text='\n'.join(p.text for p in Document(FINAL).paragraphs)
assert 'Preparation of Digest' not in text and 'Guideline for Digest Submission' not in text
(ROOT/'qa/package_audit.json').write_text(json.dumps({'template_sha256':sha,'reference_unchanged':True,'changed_original_parts':changed,'preserve_only_parts_unchanged':True,'figures':5,'tables':3,'heading_page_breaks':4,'body_word_count':len(text.split()),'expected_pages':5,'study':'ieee_device_winding_codesign'},indent=2))
print(FINAL); print('Body words:',len(text.split()))

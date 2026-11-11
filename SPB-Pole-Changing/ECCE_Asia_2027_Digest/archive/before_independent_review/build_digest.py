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
assert [d['N_voltage_min'] for d in R['device_classes']]==[20,14,10,6]
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
D.core_properties.author='';D.core_properties.last_modified_by='';D.core_properties.title='Co-Design of GaN Stacked Polyphase Bridges and Pole-Changing Traction Machines'
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
    e=OxmlElement('w:'+edge);e.set(qn('w:w'),'65');e.set(qn('w:type'),'dxa');margins.append(e)
   pr.append(margins)
   for para in cell.paragraphs:
    para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.space_after=Pt(1);para.paragraph_format.space_before=Pt(1);para.paragraph_format.line_spacing=1
    for r in para.runs:r.font.name='Times New Roman';r.font.size=Pt(10);r.bold=ri==0
 return t

def page():
 global pending_page
 pending_page=True
# PAGE ONE
p('Co-Design of GaN Stacked Polyphase Bridges\nand Pole-Changing Traction Machines','Title',16,True)
p('Abstract—Stacked polyphase bridges (SPBs) enable low-voltage power devices to supply high-voltage traction systems while independently controlling multiple stator winding groups. This paper presents a device–winding co-design method that exploits these groups for electronic pole changing. Discrete GaN voltage ratings, cell-voltage stress, coil allocation, three-phase balance, and pole ratio are treated as coupled constraints. A constructive winding analysis compares 2:1, 3:1, and 5:2 pole ratios. For a 1.2-kV link, the investigated design space includes a 150-V, 16-cell, 48-slot 8/4-pole configuration and a 200-V, 12-cell, 36-slot 12/6-pole configuration. The 2:1 ratio provides a minimum pitch factor of 0.866 with moderate coil span; 5:2 permits higher pitch utilization at substantially longer span. Parametric torque–speed results identify the machine conditions under which the selected pole modes extend the operating range.','Abstract',10)
keywords=p('Index Terms—Electric vehicle drives, gallium nitride, hybrid excitation, pole changing, stacked polyphase bridge.','Text',10);keywords.paragraph_format.first_line_indent=Cm(0)
h('Introduction')
p('Megawatt-level charging of heavy-duty electric vehicles (EVs) motivates higher battery and dc-link voltages to limit current and cable loss at a given power [1]. In a conventional two-level traction inverter, each switch must block the full dc-link voltage together with switching overshoot. Increasing the blocking-voltage requirement introduces conduction- and switching-loss trade-offs that constrain the simultaneous improvement of efficiency and switching frequency. Limited switching frequency increases current-ripple-related machine losses, while common-mode voltage (CMV), high dv/dt, and associated insulation and bearing stress must also be addressed.')
p('Multilevel inverters provide an alternative to full-link-voltage switching. Three-, five-, and seven-level neutral-point-clamped (NPC) or flying-capacitor (FC) implementations can employ lower-blocking-voltage devices and generate smaller output-voltage steps. With appropriate modulation, these steps can reduce current distortion and CMV [2]. However, the additional switches, clamping or flying-capacitor networks, and balancing functions introduce further failure mechanisms and implementation complexity. Fault-tolerant operation requires explicit redundancy, fault isolation, or reconfiguration; it does not follow inherently from the number of voltage levels.')
p('The SPB offers a modular route to voltage partitioning: series-connected dc cells supply separate polyphase winding groups [2]. Low cell voltages permit suitable low-voltage GaN devices, while the machine is implemented with multiple three-phase winding sets whose neutral points remain isolated. The resulting independently controlled inverter units are already required by the voltage architecture. Their current phase and sequence can therefore be used as additional machine-control degrees of freedom.')
p('Pole changing can exploit this flexibility to trade low-speed torque against high-speed capability and operating-point losses. Variable-pole induction drives have demonstrated partial-load and high-speed loss benefits [3], and pole-changing EV drives have been investigated for wide-speed traction requirements [4]. Such benefits motivate drive-cycle-dependent pole selection, although net cycle savings must include converter and excitation losses. Conventional implementations use Dahlander-type stator reconnection or multiple inverter units to reverse selected coil-group currents. Purpose-designed synchronous and hybrid-excited rotors can change their field polarity accordingly [5]. An SPB can reuse its inverter units for this stator rephasing without adding dedicated stator converters, provided the winding is admissible in both modes.')
p('This paper establishes the admissibility conditions for balanced three-wire SPB groups and intersects them with discrete device ratings and slot/coil constraints. The resulting co-design space is evaluated for 2:1, 3:1, and 5:2 pole ratios. Candidate device–winding combinations are then assessed using a parametric synchronous-machine envelope. The contribution is the coupled selection method; arbitrary phase grouping and a predetermined cell or pole count are not assumed.')
# PAGE TWO
page();h('SPB Drive Architecture and Design Constraints')
fig('ieee_fig1_spb_architecture.png','Fig. 1. SPB traction-drive architecture. (a) Series dc cells supply separate winding sets. (b) Each cell contains a three-phase bridge and supplies a winding set with a local floating star point.',16)
p('The considered drive contains N series-connected dc cells, each supplying a three-phase winding group through a two-level bridge. The nominal cell voltage is Vdc/N. The star point of one winding set is not connected to another set or to the dc link. Consequently, each group satisfies')
eq('',1)
p('The 3N controlled phase branches therefore provide 2N independent instantaneous current coordinates. Balanced current commands are insufficient by themselves: the phase back-EMF magnitudes, phase displacement, and impedance must also be compatible with balanced operation at both selected pole counts. The following construction enforces equal modal phase gain within each cell and across the stack.')
sub('Device voltage and coil allocation')
p('Let Vr be the device blocking-voltage rating, u its allowable utilization, and kimb and kov the assumed imbalance and overshoot factors. The voltage-dependent lower bound is')
eq('',2)
p('A 1200-V nominal link and a 1320-V maximum link are considered with kimb = kov = 1.10 and u = 0.80. Table I gives the resulting lower bounds for four verified device classes [6]. The selected parts illustrate discrete voltage and resistance trade-offs; their current, package, thermal, and switching characteristics are not interchangeable.')
cap=p('TABLE I\nDEVICE CLASSES AND CELL-COUNT LOWER BOUNDS','Caption',10);cap.paragraph_format.keep_with_next=True
table(['Rating','Device [6]','Minimum N','Phase branches','RDS(on), max'],[['100 V','EPC2361','20','60','1 mΩ'],['150 V','EPC2305','14','42','3 mΩ'],['200 V','EPC2304','10','30','5 mΩ'],['350 V','EPC2050','6','18','80 mΩ']],[1.8,3.1,2,3.3,3.3])
p('For Q conventional double-layer coil positions, the assumed one-coil-per-position construction gives C = Q independently connected coils. At least one coil per phase branch requires 3N ≤ C; equal allocation additionally requires integer c = C/(3N). A conventional single-layer arrangement instead gives C = Q/2. Additional independently fed conductor subdivisions can change these bounds, but require separate lead, insulation, and manufacturing analysis. The slot bounds used here are therefore construction specific.')
p('Device voltage sets a lower bound on N, whereas winding allocation limits the admissible values. Neither criterion alone determines the final cell count. The number of switch positions is 6N before device paralleling, so increasing N also increases gate-drive and interconnection requirements.','Text',10.5)
# PAGE THREE
page();h('Winding Admissibility for Pole Changing')
p('Let PH and PL denote total pole counts, with pH = PH/2 and pL = PL/2. Define g = gcd(pH,pL), a = pH/g, and b = pL/g. In the investigated family, the three phase-coil axes are displaced by 120°/g mechanically. Their electrical phase displacements are therefore 120a and 120b degrees. Balanced positive- or negative-sequence operation is obtained when')
eq('',3)
p('The slot grid must also contain these axes, and the grouped series coils must retain equal modal gain. The algorithm constructs the coil-to-cell assignment, evaluates each phase winding phasor at both spatial orders, and rejects unequal cell gain or loss of phase balance. Direct full-stator Fourier summation checks that excitation of either selected mode suppresses the other selected spatial order.')
sub('Pole ratio and coil span')
p('The reduced orders of a 2:1 combination are 2 and 1, yielding opposite phase sequences. The 5:2 combination also satisfies (3), with equal sequences. A 3:1 combination gives a zero-sequence spatial order within this uniform-triple family and is excluded by the three-wire connection. This result applies to the stated construction; it does not exclude alternative distributed, reconfigurable, or nonuniform winding families.')
fig('ieee_fig2_pitch_ratio.png','Fig. 2. Minimum pitch factor of the two pole modes versus normalized coil span. The vertical line denotes 1.5 high-pole pitches. The 3:1 curve describes pitch utilization only; it does not satisfy the balanced-cell condition of this construction.',15.7)
p('For coil pitch y in slots, the pitch factor of spatial order ν is')
eq('',4)
p('The continuous 2:1 case reaches a minimum pitch factor of 0.866 at y/τH = 4/3. The unrestricted 5:2 case reaches approximately 0.975 at y/τH = 20/7; imposing y/τH ≤ 1.5 reduces its optimum to approximately 0.782. Thus, the highest pitch factor can require a substantially longer end winding. Slot discretization, leakage, resistance, and manufacturability must be included before a pitch optimum is selected.')
sub('Control requirement and voltage requirement')
p('For 12/6 poles, a calculated 36-slot, two-cell layout with six series coils per phase leg and y = 4 gives total winding factors of 0.750 and 0.837. It satisfies phase balance and rejects the other selected spatial order. The corresponding one-cell layout cannot independently suppress that order. Two cells are therefore sufficient in this demonstrated construction, while the device-voltage bound may require more. This distinction prevents the cell count needed for low-voltage devices from being mistaken for a pole-changing control requirement.')
future('In the full paper, this section will be expanded with slot-by-slot coil connections, cell assignments, and current-phase commands for both pole modes. The selected winding will be checked for harmonic MMF and compatibility with a pole-changing hybrid-excited rotor.')
# PAGE FOUR
page();h('Device and Winding Co Design Results')
p('The enumeration covers N = 1–32, Q = 18, 24, …, 96, and 2:1, 3:1, and 5:2 ratios. Table II provides production benchmarks [7]–[9], rather than market-share statistics or a universal slot ceiling. Q ≤ 60 is a compactness constraint; Q ≤ 72 tests sensitivity. Pole counts denote total poles, not pole pairs.')
cap=p('TABLE II\nPRODUCTION TRACTION-MACHINE BENCHMARKS','Caption',10);cap.paragraph_format.keep_with_next=True
table(['Machine','Slots Q','Total poles P','Pole pairs p'],[['2017 Toyota Prius [7]','48','8','4'],['Nissan LEAF generations [8]','48','8','4'],['2016 BMW i3 [9]','72','12','6']],[6.6,2,2.4,2.5])
fig('ieee_fig3_feasible_region.png','Fig. 3. Admissible cell/slot combinations and representative device-class candidates: (a) 8/4-pole and (b) 12/6-pole operation. Dashed and dotted lines denote the 60- and 72-slot constraints, respectively. Marker labels give (N, Q).',13.5)
p('Figure 3 shows that semiconductor class and winding compatibility select different frontiers. With Q ≤ 60, the 100-V class admits a 20-cell/60-slot 8/4-pole layout but no 12/6-pole layout in the tested family. The 12/6-pole combination instead admits 150-V devices with 18 cells/54 slots or 200-V devices with 12 cells/36 slots. Relaxing the slot constraint to 72 admits the 100-V, 24-cell/72-slot case. The cell count is consequently an outcome of the joint constraints, rather than a fixed property of the pole ratio.')
cap=p('TABLE III\nREPRESENTATIVE DEVICE–WINDING COMBINATIONS','Caption',10);cap.paragraph_format.keep_with_next=True
table(['Device class','N','Q','Total poles H/L','Design characteristic'],[['100 V','20','60','8/4','Low channel resistance'],['150 V','16','48','8/4','48-slot winding basis'],['200 V','12','36','12/6','Reduced group count'],['350 V','6','18','12/6','Higher parallel-die demand']],[2.1,.8,.8,3,6.8])
p('At equal phase current and parallel count, N RDS(on) gives voltage-floor indices of 20, 42, 50, and 480 mΩ. These exclude switching, thermal, and gate-drive effects. The 2:1 ratio offers moderate coil span and a compatible rotor concept [5].')
sub('Planned Building Block and Machine Design')
future('The full paper will design a three-phase building block using 200-V GaN devices for the 12-cell candidate, addressing paralleling, gate driving, dc capacitance, voltage balance, and electrothermal losses. The corresponding 36-slot 12/6-pole hybrid-excited machine will be designed using finite-element analysis (FEA), evaluating saturation, back-EMF, torque ripple, and modal inductances in both modes.')
# PAGE FIVE
page();h('Performance Assessment and Discussion')
p('A linear desired-order dq model evaluates the electrical implications of the 200-V, 12-cell/36-slot 12/6-pole example. The peak phase limits are 54.85 V and 376.31 A. The high-pole parameters are ψf = 0.052 Wb and Ld/Lq = 90/180 µH; the low-pole values are 0.0862 Wb and 540/540 µH. The parameters are illustrative and uncalibrated. All cases permit negative d-axis current and use a 300-kW electromagnetic ceiling.')
eq('',5)
fig('ieee_fig4_speed_envelopes.png','Fig. 4. Parametric (a) torque and (b) power envelopes for the reference IPMSM, selectable-pole HEPM, and IPMSM field-weakening sensitivity. The 9-kr/min study limit is not a validated mechanical limit.',13.5)
p('The selectable-pole example retains 150 kW to 9 kr/min versus 4.45 kr/min for the matched IPMSM; the 300-kW endpoint stays at 3.30 kr/min. Stronger IPMSM field weakening removes this advantage. The comparison omits saturation, unused-harmonic EMFs, losses, thermal duty, transitions, and rotor stress; physical-machine benefits require identified flux maps.')
h('Conclusion')
p('The proposed method separates winding-control requirements from voltage-driven cell counts. Candidates include 150-V/16-cell/48-slot 8/4-pole and 200-V/12-cell/36-slot 12/6-pole designs. The 2:1 ratio offers moderate coil span; 5:2 needs longer span for comparable pitch utilization.')
future('The full paper will replace the illustrative parameters with FEA-derived flux maps and compare loss-aware torque–speed envelopes and representative drive-cycle energy against a matched IPMSM, including excitation demand and pole-transition constraints.')
x=h('References');num=x._p.get_or_add_pPr();n=OxmlElement('w:numPr');i=OxmlElement('w:numId');i.set(qn('w:val'),'0');n.append(i);num.append(n)
refs=[
'[1] CharIN, "Megawatt Charging System—Recommendations and Requirements," white paper, ver. 2.0, May 2025.',
'[2] G. Rohner, J. Huber, S. Miric, and J. W. Kolar, "Comparative Evaluation of Three-Phase Three-Level Flying Capacitor and Stacked Polyphase Bridge GaN Inverter Systems for Integrated Motor Drives," Electronics, vol. 13, art. 1259, 2024, doi: 10.3390/electronics13071259.',
'[3] E. Libbos, E. Krause, A. Banerjee, and P. T. Krein, "Inverter Design Considerations for Variable-Pole Induction Machines in Electric Vehicles," IEEE Trans. Power Electron., vol. 37, no. 11, pp. 13554–13565, 2022, doi: 10.1109/TPEL.2022.3177082.',
'[4] Rohith, L. Umanand, and B. Subba Reddy, "Pole Changing Wide Speed Range Induction Motor Drive for Electric Vehicles," in Proc. IEEE PEDES, 2018, pp. 1–5, doi: 10.1109/PEDES.2018.8707677.',
'[5] C. Conto and N. Bianchi, "On the Possibility to Achieve a Pole Change in Synchronous Motors," in Proc. IEEE ECCE, 2022, doi: 10.1109/ECCE50734.2022.9947754.',
'[6] Efficient Power Conversion, EPC2361, EPC2305, EPC2304, and EPC2050 datasheets, 2025–2026, epc-co.com.',
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
FINAL=ROOT/'ECCE_Asia_2027_Digest.docx'
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
(ROOT/'qa/package_audit.json').write_text(json.dumps({'template_sha256':sha,'reference_unchanged':True,'changed_original_parts':changed,'preserve_only_parts_unchanged':True,'figures':4,'tables':3,'heading_page_breaks':4,'body_word_count':len(text.split()),'expected_pages':5,'study':'ieee_device_winding_codesign'},indent=2))
print(FINAL); print('Body words:',len(text.split()))

from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parent
REF=ROOT/'template/ICPE_2027_Digest_Template.docx'
D=Document(REF)
R=json.loads((ROOT/'simulation/results/simplified_screen.json').read_text())
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
style.paragraph_format.line_spacing=1.05
D.core_properties.author='';D.core_properties.last_modified_by='';D.core_properties.title='Co Design of Pole Changing Machines and Stacked Polyphase Bridges'
D.core_properties.subject='ICPE 2027 ECCE Asia digest'

def p(text='',style='Text',size=11,bold=False):
 x=D.add_paragraph(style=style);x.paragraph_format.space_after=Pt(5);x.paragraph_format.line_spacing=1.05
 if style=='Text':x.paragraph_format.first_line_indent=Cm(.35);x.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
 r=x.add_run(text);r.font.name='Times New Roman';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor(0,0,0)
 return x

sub_counter=0
def h(text):
 global sub_counter
 sub_counter=0
 x=p(text,'Heading 1',12,True);x.paragraph_format.space_before=Pt(8);x.paragraph_format.space_after=Pt(6)
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
   pr=OxmlElement('m:rPr');norm=OxmlElement('m:nor');pr.append(norm);r.append(pr)
  t=OxmlElement('m:t');t.text=txt;r.append(t);return r
 def sub(base,idx):
  v=OxmlElement('m:sSub');e=OxmlElement('m:e');e.append(mr(base));v.append(e);ss=OxmlElement('m:sub');ss.append(mr(idx));v.append(ss);return v
 def sup(obj,power):
  v=OxmlElement('m:sSup');e=OxmlElement('m:e');e.append(obj if not isinstance(obj,str) else mr(obj));v.append(e);ss=OxmlElement('m:sup');ss.append(mr(power));v.append(ss);return v
 x=D.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(6)
 math=OxmlElement('m:oMath')
 if num==1:
  math.append(sub('S','r'));math.append(mr(' = '))
  n=OxmlElement('m:nary');pr=OxmlElement('m:naryPr');ch=OxmlElement('m:chr');ch.set(qn('m:val'),'∑');pr.append(ch);loc=OxmlElement('m:limLoc');loc.set(qn('m:val'),'undOvr');pr.append(loc);n.append(pr)
  for tag,txt in [('sub','k = 0'),('sup','m − 1'),('e','exp(j2πrk/m)')]:
   el=OxmlElement('m:'+tag);el.append(mr(txt));n.append(el)
  math.append(n);math.append(mr(' = 0'));math.append(mr('  if m does not divide r',True))
 else:
  math.append(sub('C','min'));math.append(mr(' = '));f=OxmlElement('m:f');nu=OxmlElement('m:num');nu.append(mr('2ΔE'));f.append(nu);de=OxmlElement('m:den');de.append(sup(sub('V','0'),'2'));de.append(mr(' − '));de.append(sup('(0.9V₀)','2'));f.append(de);math.append(f)
 x._p.append(math);r=x.add_run('    ('+str(num)+')');r.font.name='Times New Roman';r.font.size=Pt(11)
 return x

def fig(name,caption,width=16):
 x=D.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(2);x.paragraph_format.keep_with_next=True
 x.add_run().add_picture(str(ROOT/'figures'/name),width=Cm(width))
 docPr=x._p.xpath('.//wp:docPr')[0];docPr.set('descr',caption)
 x=p(caption,'Caption',10);x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(6)
 return x

def table(headers,rows,widths):
 t=D.add_table(rows=1,cols=len(headers));t.autofit=False
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
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');b.append(e)
   pr.append(b)
   if ri==0:
    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EEEEEE');pr.append(sh)
   margins=OxmlElement('w:tcMar')
   for edge in ['top','left','bottom','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:w'),'65');e.set(qn('w:type'),'dxa');margins.append(e)
   pr.append(margins)
   for para in cell.paragraphs:
    para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.space_after=Pt(1);para.paragraph_format.space_before=Pt(1);para.paragraph_format.line_spacing=1
    for r in para.runs:r.font.name='Times New Roman';r.font.size=Pt(10);r.bold=ri==0
 return t

def page():D.add_page_break()
# PAGE ONE
p('Co Design of Pole Changing Machines\nand Stacked Polyphase Bridges','Title',16,True)
p('Abstract - Series-stacked low-voltage inverter modules can provide the independent winding-group control needed for electronic pole changing. Their DC cells, however, must also accommodate the instantaneous power exchanged between spatial orders. This paper presents a preliminary co-design screen combining phase-domain power summation, capacitor-energy sizing and winding-pitch utilization. Three-phase 4/2-pole and five-phase 6/2-pole candidates are compared with a five-phase 4/2-pole control. At equal mean cell power and summed squared phase current, the ideal three-phase case produces a 9.6 kW cross-power component at 105 Hz, while both five-phase cases cancel that component. A pitch sweep identifies a competing limitation: restricting coil span to the high-pole full pitch reduces the minimum pitch factor of the 6/2-pole candidate to 0.489. The results establish a tractable design trade-off, rather than a claim of improved motor efficiency or torque-continuous pole changing.','Abstract',11)
h('Introduction')
p('Megawatt charging for heavy-duty electric vehicles motivates renewed attention to high-voltage electrical architectures [1]. Raising voltage reduces current at a given power, although charging power alone does not determine the traction DC-link voltage. In a conventional two-level inverter, each switch must block the full DC voltage together with a transient margin. Voltage rating, switching energy, cooling and electromagnetic compatibility consequently constrain the usable switching frequency and affect current ripple, machine harmonic losses and common-mode excitation.')
p('Multilevel topologies, including neutral-point-clamped and flying-capacitor converters with three, five or seven levels, can reduce output-voltage steps and semiconductor voltage stress. Their common-mode performance depends on modulation and grounding, while additional balancing and protection requirements must be considered. A published comparison of flying-capacitor and stacked polyphase bridge converters illustrates why semiconductor-loss and common-mode advantages must be evaluated for a specific implementation [2]. Neither multilevel construction nor modularity alone establishes fault tolerance.')
p('A stacked polyphase bridge (SPB) divides the DC link among series-connected cells, each supplying an isolated polyphase winding group. This architecture enables lower-voltage devices and creates independently controllable current groups. The same control freedom can support pole changing without stator contactors if the winding, rotor and cell-energy constraints are satisfied. Low-voltage GaN selection must still include maximum battery voltage, capacitor ripple, imbalance and switching overshoot.')
p('The contribution examined here is the joint feasibility screen for these constraints. The study asks whether five-phase grouping can alleviate a series-cell power penalty without imposing an unacceptable winding penalty. It compares the 4/2- and 6/2-pole candidates and adds a matched-pole control to separate the effects of phase number and pole ratio.')
# PAGE TWO
page();h('Machine and Converter Feasibility')
p('Electronic pole changing is established for induction machines, whose cage rotor adapts to the applied stator field [3]. It is also possible in purpose-designed synchronous machines. Conto and Bianchi investigate wound-rotor and specialized hybrid configurations and demonstrate that the stator and rotor must support compatible pole structures [4]. Thus, SPB control freedom does not make an arbitrary permanent-magnet rotor pole-changeable. A synchronous implementation must account for field grouping, reversal voltage, excitation losses and rotor magnetic paths.')
fig('fig1_architecture_and_modes.png','Fig. 1. SPB grouping and ideal cross-power screen. Pole labels denote total poles; m denotes phases per module. A rejected entry concerns the stated isolated-neutral construction.')
sub('Winding group and spatial order constraints')
p('Let N be the number of DC cells, m the phases per cell, Q the coil-position count and p the pole-pair order. For the interleaved construction, cell j supplies positions j + kN, with k = 0, ..., m - 1. This study uses Q = mN, so each phase leg supplies one coil. The within-cell angles are equally spaced. A spatial order divisible by m is zero sequence and is excluded by the isolated neutral. General windings and multiple coils per leg require a separate winding-function calculation.')
eq('S(r) = sum over k of exp(j 2πrk/m) = 0 unless m divides r',1)
p('The product of orders a and b contains spatial orders a + b and a - b. Their cell-power terms survive phase summation only when the corresponding order is divisible by m. For m = 3, orders 2 and 1 couple through their sum. For m = 5, neither 3 ± 1 nor 2 ± 1 is divisible by five. This is an application of spatial orthogonality; the engineering question is its consequence for SPB storage and winding design.')
# PAGE THREE
page();h('Simplified Phase Domain Simulation')
p('We directly sum instantaneous phase powers for 16 cells at 75 V nominal each, corresponding to a 1200 V stack. Two equal-amplitude, unity-power-factor sinusoidal orders rotate in the same direction at a nominal mechanical speed of 2100 rpm. The total per-phase RMS voltage and current are 16√(3/m) V and 200√(3/m) A; each modal RMS value is smaller by √2. All candidates therefore have 9.6 kW mean power per cell and the same sum of squared phase RMS currents. These are prescribed waveforms, not a solved motor operating point.')
fig('fig2_phase_power_and_energy.png','Fig. 2. Direct phase-sum mismatch for cases A to C and the energy-buffer voltage estimate for A. The shaded band is 75 V ±10%. This is a nominal-recharge storage screen, not closed-loop stack dynamics.',15.5)
cap=p('TABLE I  Ideal phase power and buffer sizing','Caption',10);cap.paragraph_format.keep_with_next=True
table(['Case','m','Poles','Cross power','Frequency','Buffer C'],[['A','3','4/2','9.60 kW','105 Hz','27.23 mF'],['B','5','6/2','< 10⁻⁶ W','None','No cross term'],['C','5','4/2','< 10⁻⁶ W','None','No cross term']],[1.1,.8,1.5,3.1,2.3,3.7])
p('The sampling interval is 10 µs over 0.2 s. Direct phase summation agrees with the spatial condition to floating-point precision; current and voltage neutral sums vanish. The integrated energy amplitude agrees with the sinusoidal expression within 0.0004%. Cancellation concerns only the modeled cross term: B and C still require DC capacitors for switching ripple, transients and control. Equal squared current does not establish equal copper loss when actual winding resistances differ.','Text',10.5)
# PAGE FOUR
page();h('Energy Storage and Winding Pitch Trade Off')
sub('Cell energy buffer requirement')
p('For an actual cell, d(CV²/2)/dt = VIstack - Pout, with losses included consistently. Here the recharge power is approximated by the nominal mean, and only the periodic power mismatch is integrated. For a sinusoidal mismatch of peak P̂ at angular frequency Ω, the energy excursion amplitude is ΔE = P̂/Ω. Converting that prescribed energy excursion through E = CV²/2 gives the storage screen below; it does not validate series-stack stability or a balancing controller.')
eq('Cmin = 2ΔE / [V₀² - (0.9V₀)²]   for a centered energy excursion',2)
p('Case A has ΔE = 14.55 J and requires 27.23 mF per cell for the lower 10% voltage bound. The linear small-ripple estimate is 25.87 mF. The energy conversion gives 68.23 to 81.21 V at 30 mF, whereas 10 mF leaves the allowed band. The buffer requirement scales inversely with mismatch frequency at fixed power amplitude, so low-speed overlap deserves particular attention.')
sub('Pitch utilization in both pole modes')
fig('fig3_pitch_tradeoff.png','Fig. 3. Minimum absolute pitch factor of the two spatial orders versus mechanical coil span. The calculation assumes unit distribution factor and excludes end-winding and harmonic losses.',15.5)
p('With kₚ(p,y) = |sin(πpy/Q)|, the discrete pitch sweep gives the following results. The short-span restriction is y ≤ Q/(2pH), the full pitch of the higher-pole mode. It is a comparison constraint, not a universal winding requirement.')
cap=p('TABLE II  Discrete coil pitch comparison','Caption',10);cap.paragraph_format.keep_with_next=True
table(['Case','Q','Short y','Short min kₚ','Best y ≤ Q/2','Best min kₚ'],[['A','48','12','0.707','16','0.866'],['B','80','13','0.489','40','1.000'],['C','80','20','0.707','27','0.853']],[1,1,1.8,3,3.1,2.6])
p('The unit pitch factor of B requires a 180° mechanical coil span. Its magnetic utilization therefore cannot be credited without evaluating end-winding length, leakage, resistance and manufacturability. The five-phase 4/2-pole control cancels the ideal cross-power term while retaining the same short-span minimum pitch factor as A.','Text',10.5)
# PAGE FIVE
page();h('Discussion and Validation Limits')
p('The simplified results reveal two separate gates. First, the phase-group choice determines whether the selected spatial orders exchange pulsating power within each series DC cell. Second, the pole ratio and coil span determine how effectively a common winding produces both fields. A five-phase 6/2-pole design passes the ideal cross-power screen, but it is not automatically preferable to a five-phase 4/2-pole design. Conversely, a three-phase 4/2-pole design may remain attractive if a costed capacitor and transition schedule is preferable to additional inverter legs.')
p('The present normalization holds mean cell power and the current-square sum constant, which isolates the phase-sum effect. It does not impose equal active volume, equal copper mass, equal winding resistance or equal cooling. A final comparison must optimize turns, slot geometry, conductor area, yoke thickness and converter current rating together. Rotor compatibility must be established separately: the winding screen applies to both induction and synchronous candidates, but it does not prove that a synchronous rotor can generate both requested pole fields.')
p('Existing project simulations provide a further caution. In an independently formulated nonlinear magnetic-equivalent-circuit replay of an 8/4-pole induction-machine transition, five-phase grouping reduced the dominant cell-power pulsation, yet a substantial torque dip remained because residual rotor flux consumed the shared voltage budget. Those legacy simulations concern different pole counts and winding geometries; they motivate the present screen and are not validation of the new 4/2- or 6/2-pole motor designs.')
p('The new calculations omit rotor dynamics, PWM, saturation, magnetic loss, thermal constraints and closed-loop cell balancing. The energy-buffer calculation assumes nominal recharge power; the exact series-connected constant-power system can exhibit drift or instability and requires a balancing model. Consequently, no motor efficiency, drive-cycle saving, optimum phase count or torque-continuous transition is claimed. The next validation step is a winding-function and selected-point field calculation for the same machine envelope, followed by cell-voltage and torque-constrained transition simulations.')
h('Conclusion')
p('Independent phase-domain summation and a pitch sweep provide initial numerical evidence for SPB and pole-changing machine co-design. The ideal three-phase 4/2-pole overlap generates a 9.6 kW, 105 Hz cell-power term under the stated normalization, corresponding to a 27.23 mF nominal-recharge energy-buffer requirement for ±10% voltage. Five-phase 6/2- and 4/2-pole groupings cancel this ideal term. However, the short-span minimum pitch factors are 0.489 and 0.707 respectively. The defensible outcome is a constrained candidate selection: evaluate the five-phase 4/2-pole control alongside the other candidates before committing to a 6/2-pole machine.')
x=h('References');num=x._p.get_or_add_pPr();n=OxmlElement('w:numPr');i=OxmlElement('w:numId');i.set(qn('w:val'),'0');n.append(i);num.append(n)
refs=[
'[1] CharIN, Whitepaper Ruggedized Megawatt Charging System, version 1.3, 2024. Available at charin.global, Technology and Knowledge Base.',
'[2] G. Rohner, J. Huber, S. Miric, and J. W. Kolar, "Comparative Evaluation of Three-Phase Three-Level Flying Capacitor and Stacked Polyphase Bridge GaN Inverter Systems for Integrated Motor Drives," Electronics, vol. 13, no. 7, art. 1259, 2024, doi: 10.3390/electronics13071259.',
'[3] B. Ge, D. Sun, W. Wu, and F. Z. Peng, "Winding Design, Modeling, and Control for Pole-Phase Modulation Induction Motors," IEEE Trans. Magn., vol. 49, no. 2, pp. 898-911, 2013, doi: 10.1109/TMAG.2012.2208652.',
'[4] C. Conto and N. Bianchi, "On the Possibility to Achieve a Pole Change in Synchronous Motors," IEEE ECCE, 2022, doi: 10.1109/ECCE50734.2022.9947754.'
]
for text in refs:
 x=p(text,'Text',10);x.paragraph_format.first_line_indent=Cm(0);x.paragraph_format.space_after=Pt(3);x.paragraph_format.line_spacing=1
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
(ROOT/'qa/package_audit.json').write_text(json.dumps({'template_sha256':sha,'reference_unchanged':True,'changed_original_parts':changed,'preserve_only_parts_unchanged':True,'figures':3,'tables':2,'explicit_page_breaks':4,'body_word_count':len(text.split()),'expected_pages':5},indent=2))
print(FINAL); print('Body words:',len(text.split()))

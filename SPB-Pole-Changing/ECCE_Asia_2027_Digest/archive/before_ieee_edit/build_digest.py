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
style.paragraph_format.line_spacing=1.05
D.core_properties.author='';D.core_properties.last_modified_by='';D.core_properties.title='Selecting Stacked Three Phase Cells and Pole Ratios for Traction Drives'
D.core_properties.subject='ICPE 2027 ECCE Asia digest'

def p(text='',style='Text',size=11,bold=False):
 x=D.add_paragraph(style=style);x.paragraph_format.space_after=Pt(5);x.paragraph_format.line_spacing=1.05
 if style=='Text':x.paragraph_format.first_line_indent=Cm(.35);x.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
 r=x.add_run(text);r.font.name='Times New Roman';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor(0,0,0)
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
 x=D.add_paragraph();x.alignment=WD_ALIGN_PARAGRAPH.CENTER;x.paragraph_format.space_after=Pt(6)
 math=OxmlElement('m:oMath');r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);math.append(r);x._p.append(math)
 rr=x.add_run('    ('+str(num)+')');rr.font.name='Times New Roman';rr.font.size=Pt(11)
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

def page():
 global pending_page
 pending_page=True
# PAGE ONE
p('Selecting Stacked Three Phase Cells\nand Pole Ratios for Traction Drives','Title',16,True)
p('Abstract - Stacked polyphase bridges permit low-voltage devices to supply a high-voltage traction link, but cell count cannot be selected independently of the winding. Each three-wire cell requires balanced phase loading at both pole counts, while the available device ratings and coil positions are discrete. This paper develops a constructive selection screen linking device class, cell count, slot budget and pole ratio. Two cells are sufficient for the demonstrated 12/6-pole stator rephasing; a 24-cell arrangement is not a control requirement. Under an illustrative voltage margin, 100, 150, 200 and 350 V devices instead require at least 20, 14, 10 and 6 cells. The resulting winding constraints favour a 2:1 starting case for the investigated hybrid-rotor concept, with 5:2 retained as a longer-pitch alternative and 3:1 requiring a different winding family.','Abstract',11)
h('Motivation and Literature Based Design Space')
p('Megawatt charging motivates higher-voltage heavy-duty vehicle architectures [1]. Two-level converter switches block the full DC link plus transients; device voltage rating, switching energy, cooling and electromagnetic compatibility constrain the switching frequency. Modular SPB converters distribute that voltage among cells, allowing lower-voltage GaN devices and independently supplied stator groups. Their existing group control can also support pole changing, provided the winding and synchronous rotor are compatible.')
p('The design should therefore start from practical device and machine options, rather than assume a particular cell count or pole combination. Conventional multilevel converters also offer smaller voltage steps, but their balancing and protection requirements differ; SPB loss and common-mode benefits remain implementation dependent [7]. The objective here is to identify a feasible shortlist before a detailed magnetic and loss optimization.')
cap=p('TABLE I  Verified production traction benchmarks','Caption',10);cap.paragraph_format.keep_with_next=True
table(['Machine and source','Slots Q','Total poles P','Pole pairs p'],[['2017 Toyota Prius [2]','48','8','4'],['Nissan LEAF motor generations [3]','48','8','4'],['2016 BMW i3 [4]','72','12','6']],[6.6,2,2.4,2.5])
p('These primary-source examples establish useful starting points, not a statistical market distribution. They also show that 60 slots is not a general EV limit. We use Q ≤ 60 as a compact-design scenario and Q ≤ 72 as a sensitivity. Throughout, P = 2p: 8, 12 and 16 pole pairs would mean 16, 24 and 32 total poles. Higher-pole variants are also screened. At 12000 rpm, 8 total poles gives 800 Hz electrical frequency, whereas 24 total poles gives 2400 Hz; allowable frequency is another design constraint.')
p('The independent design variables are the voltage class, cell count N, coil/slot arrangement, pole combination and coil pitch. A manufacturable rotor and useful torque-speed envelope are subsequent gates. The supplied synchronous-machine study [6] supports the hybrid polarity-change principle, but does not make one stator winding or cell count universally necessary.')
# PAGE TWO
page();h('Cell Voltage and Winding Capacity')
p('Each building block has three controlled inverter legs, but the separate neutral points are not interconnected. For a three-wire group, iA + iB + iC = 0; hence 3N phase branches provide 2N instantaneous current coordinates, not 3N unconstrained currents. The winding must also give equal phase back-EMF magnitudes with ±120° displacement in each selected mode. Balanced current commands alone do not prove balanced loading.')
fig('fig_selection_workflow.png','Fig. 1. Cell count is selected by intersecting device stress, available coil branches and balanced loading at both pole counts. C denotes independently connected coils under the chosen construction.',15.5)
p('The voltage lower bound is distinct from the minimum number of groups needed for stator rephasing. For an illustrative 1200 V nominal link, we assume 1320 V maximum, factors of 1.10 each for cell imbalance and overshoot, and a maximum working stress of 80% of device rating. These are explicit screening assumptions; measured parasitics and a different margin change the result.')
eq('Nᵥ = ⌈1320 × 1.10 × 1.10 / (0.80 Vᵣ)⌉',1)
cap=p('TABLE II  Discrete device choices and voltage floors','Caption',10);cap.paragraph_format.keep_with_next=True
table(['Rating','Example [5]','Min N','Branches 3N','Rmax at 25 C'],[['100 V','EPC2361','20','60','1 mΩ'],['150 V','EPC2305','14','42','3 mΩ'],['200 V','EPC2304','10','30','5 mΩ'],['350 V','EPC2050','6','18','80 mΩ']],[1.8,3.5,1.3,3.2,3.7])
p('For a conventional double-layer arrangement with one independent coil per coil position, C = Q and 3N ≤ Q. For a single-layer arrangement, C = Q/2 and 6N ≤ Q. Thus the 100 V floor needs at least 60 or 120 slots respectively in these constructions. Splitting turns or conductor groups into additional independently fed coils can alter the bound, with added insulation and connection requirements. Slot count is therefore a construction-dependent constraint, not an absolute limit on inverter channels.')
p('6N switch positions and 3N leg commands also grow with cell count; paralleled devices add further hardware. The study does not assume that the lowest voltage class or the fewest cells is optimal.','Text',10.5)
# PAGE THREE
page();h('Balanced Winding and Pole Ratio Screen')
p('For a constructive family, let g = gcd(pH,pL), a = pH/g and b = pL/g. Three phase-coil axes spaced by 120°/g mechanically produce phase shifts of 120a and 120b degrees. Both sets are balanced when neither reduced order is divisible by three. Series coils are grouped into the same three-wire cell, and induced-voltage magnitude and equal loading across cells are checked directly. The slot grid and integer coil count must also fit.')
eq('a ∉ 3ℤ,    b ∉ 3ℤ,    Q/(3N) is an integer',2)
p('A 2:1 pair has reduced orders 2 and 1, so it passes with opposite phase sequences. A 5:2 pair also passes, with the same sequence. A 3:1 pair makes one order zero sequence in this uniform-triple family; it is outside the demonstrated layout. This is not an impossibility theorem for other multi-coil windings, reconnection schemes or pole-changing machines.')
fig('fig_ratio_pitch.png','Fig. 2. Pitch utilization of the two modes versus coil span. The dashed 3:1 curve is a pitch calculation only and does not establish a balanced cell layout. The 1.5-pitch line is a stated short-span preference.',15.5)
p('With kp = |sin(πpy/Q)|, the continuous pitch screen gives a best minimum factor of 0.866 for 2:1 at 1.333 high-pole pitches. For 5:2 the unrestricted factor can approach 0.975, but the span is about 2.857 pitches; restricting span to 1.5 pitches reduces it to about 0.782. A high winding factor alone therefore does not settle end-winding length, leakage or manufacturability.')
sub('Minimum control example for 12 and 6 total poles')
p('A calculated two-cell, 36-slot double-layer construction uses six series coils per leg and pitch y = 4. The total winding factors are 0.750 and 0.837 in the 12- and 6-pole modes. Direct phase-domain summation confirms balanced module phasors and suppression of the other selected spatial order. The corresponding single-cell layout cannot independently suppress that order. Two cells are therefore the demonstrated minimum within this selection method, not a universal minimum for every harmonic or rotor-only pole-changing concept.')
p('The complete two-cell coil map is retained with the numerical results. At a 1200 V link these two cells would each operate near 600 V nominal, so they are not a 100 V GaN solution. More cells may be needed for device stress or winding utilization even though the rephasing itself needs only two.','Text',10.5)
# PAGE FOUR
page();h('Feasible Shortlist Before Machine Optimization')
fig('fig_device_slot_shortlist.png','Fig. 3. Minimum-count candidates in the tested even-slot set, at each device rating. Entries are N/Q. A dash means no solution in the equal-loaded uniform-triple screen, not impossibility for all winding types.',15.7)
p('The sweep covers N = 1 to 32 and Q = 18, 24, ..., 96, with 2:1, 3:1 and 5:2 pole combinations. Each candidate must satisfy phase balance in both modes, equal modal gain across cells and direct Fourier rejection of the other selected pole order. The figure selects the lowest N, then the lowest Q, within each voltage and slot constraint. This is a transparent shortlist rule, not an efficiency optimum.')
p('For a 60-slot double-layer cap, 100 V devices yield a 20-cell/60-slot 8/4-pole candidate but no 12/6 candidate in this family. The 12/6 option instead admits 200 V devices with 12 cells and 36 slots, or 150 V devices with 18 cells and 54 slots. Allowing 72 slots admits a 100 V, 24-cell/72-slot 12/6 option in the even-slot set. Here 24 cells arises from intersecting the 100 V class with this 72-slot construction; rephasing does not require that count.')
cap=p('TABLE III  Candidates worth further physical comparison','Caption',10);cap.paragraph_format.keep_with_next=True
table(['Device class','N','Q','Total poles H/L','Reason to retain'],[['100 V','20','60','8/4','Low R; many groups'],['150 V','16','48','8/4','48-slot benchmark basis'],['200 V','12','36','12/6','Compact higher-pole option'],['350 V','6','18','12/6','Few groups; device penalty']],[2.1,.8,.8,3,6.8])
p('The last column is a screening rationale. The 350 V example is particularly important: its datasheet resistance is 80 mΩ, versus 1, 3 and 5 mΩ for the other selected parts [5]. At equal phase RMS current and equal parallel count, conduction loss scales with N RDS(on). At the voltage floors the normalized indices are 20, 42, 50 and 480 mΩ. These part-specific 25 C values do not include hot resistance, switching loss, device area or current capability. They show why fewer cells can still require substantially more parallel die.')
p('A 2:1 ratio is the leading starting point because it combines balanced groups, moderate pitch and the published hybrid reversal concept [6]. The 5:2 stator candidate remains open, but needs a distinct rotor design and end-winding evaluation. More phase counts are future work; no common neutral or zero-sequence current is used.')
# PAGE FIVE
page();h('Speed Range as a Subsequent Verification Gate')
p('The 200 V, 12-cell/36-slot 12/6 illustration uses a linear dq model: phase limits 54.85 V peak and 376.31 A peak; high-mode flux 0.052 Wb and Ld/Lq = 90/180 µH; low-mode flux 0.0862 Wb and Ld/Lq = 540/540 µH. These are illustrative terminal equivalents, not identified geometry. Every model permits negative d-axis current and has a 300 kW electromagnetic output ceiling.')
fig('fig_selected_diagnostic_envelope.png','Fig. 4. Conditional speed envelopes after the winding/device screen. The stronger-field-weakening IPMSM is a parameter sensitivity. The 9000 rpm endpoint is an electrical study ceiling, not a validated safe rotor speed.',14.5)
p('The illustrative hybrid selection extends the 150 kW envelope from 4450 rpm to the study ceiling, while the 300 kW endpoint remains 3300 rpm. A stronger-field-weakening IPMSM removes the advantage. This demonstrates why candidate ranking must include the actual rotor flux, back-iron capacity and modal inductances. Core, field and inverter losses, unused-harmonic EMFs, thermal duty, transition dynamics and rotor stress remain to be verified; no shaft-efficiency or general IPMSM superiority claim follows.')
p('The contribution is a device, winding and pole-ratio selection method. A comparison of 150 V and 200 V against 100 V, with a 2:1 starting ratio, merits magnetic, loss and drive-cycle optimization. Neither 24 cells nor 12/6 poles is fixed in advance.')
x=h('References');num=x._p.get_or_add_pPr();n=OxmlElement('w:numPr');i=OxmlElement('w:numId');i.set(qn('w:val'),'0');n.append(i);num.append(n)
refs=[
'[1] CharIN, Whitepaper Ruggedized Megawatt Charging System, version 1.3, 2024, charin.global.',
'[2] T. Burress, "Electrical Performance, Reliability Analysis, and Characterization," ORNL, DOE Vehicle Technologies Annual Merit Review, 2017, slide 18, DOE project EDT087.',
'[3] S. Oki and Y. Sato, "Nissan LEAF and e-POWER: Evolution of Motors and Inverters," IEEJ Journal of Industry Applications, vol. 13, no. 1, pp. 8–16, 2024, doi: 10.1541/ieejjia.23006552.',
'[4] U.S. DOE, FY 2016 Annual Progress Report for Electric Drive Technologies, pp. 200–202, 2017, energy.gov, BMW i3 motor assessments.',
'[5] Efficient Power Conversion, EPC2361, EPC2305, EPC2304 and EPC2050 datasheets, revisions 2026/2025, epc-co.com.',
'[6] C. Conto and N. Bianchi, "On the Possibility to Achieve a Pole Change in Synchronous Motors," IEEE ECCE, 2022, doi: 10.1109/ECCE50734.2022.9947754.',
'[7] G. Rohner et al., "Comparative Evaluation of Three-Phase Three-Level Flying Capacitor and Stacked Polyphase Bridge GaN Inverter Systems for Integrated Motor Drives," Electronics, vol. 13, art. 1259, 2024, doi: 10.3390/electronics13071259.'
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
(ROOT/'qa/package_audit.json').write_text(json.dumps({'template_sha256':sha,'reference_unchanged':True,'changed_original_parts':changed,'preserve_only_parts_unchanged':True,'figures':4,'tables':3,'heading_page_breaks':4,'body_word_count':len(text.split()),'expected_pages':5,'study':'discrete_device_slot_and_ratio_selection'},indent=2))
print(FINAL); print('Body words:',len(text.split()))

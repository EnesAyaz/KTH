from pathlib import Path
from copy import deepcopy
import re,json,hashlib
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

P=Path(r'C:\Github\KTH\PCB-Design\reports\paper');A=P/'icpe/digest_5page_assets';QA=P/'icpe/digest_expanded_qa'
SRC=P/'SPB_ICPE_complete_manuscript_with_Q3D_2026-10-29.docx'
OUT=P/'SPB_ICPE_digest_expanded_citation_checked_2026-10-29.docx'
source=Document(SRC);sp=[q.text.strip() for q in source.paragraphs]
QA.mkdir(exist_ok=True)
(QA/'artifact.md').write_text(f'''# Complete ICPE manuscript contract
Reference content: {SRC}
SHA256: {hashlib.sha256(SRC.read_bytes()).hexdigest()}
Reference render: manual_reference.pdf (10 pages), reference_contact.png.
Reference roles: Times New Roman body, numbered centered section headings, italic lettered subsections, centered title, single-column anonymous paper. New manuscript replaces all body content and template placeholders; original file stays unchanged. The user authorized consolidation and remaining sections.
Page system: A4, 3 cm top and 2.5 cm other margins, single column; explicit venue instructions override inconsistent sample section geometry. Body and captions 10 pt; title 16 pt. Page field in footer. Expanded working manuscript, not a five-page submission.
Components: eight figures at 16 cm width, three IEEE-style tables without vertical rules, five editable Word equations, eleven numbered references. Black heading text. No author or affiliation.
Content: manual sections I–IV edited for coherence, corrected D-FOM and numbering; completed sections V–VII. Only simulated results are reported, DPT experiments pending. Existing manuscripts and figure masters preserved.
Rendering: packaged renderer unavailable because LibreOffice is absent; Word PDF export and Poppler page images provide visual verification.
''',encoding='utf-8')
# Reuse the retained manual template styles; clear only the content being replaced.
doc=Document(SRC);body=doc._element.body
for el in list(body):
 if el.tag!=qn('w:sectPr'):body.remove(el)
sec=doc.sections[0];sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=Cm(3);sec.bottom_margin=Cm(2.5);sec.left_margin=sec.right_margin=Cm(2.5)
sec.header_distance=Cm(1.2);sec.footer_distance=Cm(1.2)
for t in ['w:headerReference','w:footerReference','w:pgNumType']:
 for el in sec._sectPr.findall(qn(t)):sec._sectPr.remove(el)
cols=sec._sectPr.find(qn('w:cols'))
if cols is None:cols=OxmlElement('w:cols');sec._sectPr.append(cols)
cols.set(qn('w:num'),'1');cols.set(qn('w:space'),'0')
for st in doc.styles:
 if st.type==1:
  st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
  for el in st.element.xpath('.//w:pBdr | .//w:framePr | .//w:numPr'):el.getparent().remove(el)
  for el in st.element.xpath('.//w:rFonts'):
   for key in list(el.attrib):
    if 'Theme' in key:el.attrib.pop(key)
  st.paragraph_format.page_break_before=False
normal=doc.styles['Normal'];normal.font.size=Pt(10);normal.paragraph_format.line_spacing=1;normal.paragraph_format.space_before=Pt(0);normal.paragraph_format.space_after=Pt(1.5);normal.paragraph_format.first_line_indent=Cm(.35);normal.paragraph_format.widow_control=True
for n in ['Title','Heading 1','Heading 2','Caption']:
 st=doc.styles[n];st.paragraph_format.first_line_indent=Pt(0);st.paragraph_format.line_spacing=1
st=doc.styles['Title'];st.font.size=Pt(16);st.font.bold=True;st.paragraph_format.space_after=Pt(9)
st=doc.styles['Heading 1'];st.font.size=Pt(10);st.font.bold=True;st.font.italic=False;st.paragraph_format.space_before=Pt(8);st.paragraph_format.space_after=Pt(4);st.paragraph_format.keep_with_next=True
st=doc.styles['Heading 2'];st.font.size=Pt(10);st.font.italic=True;st.font.bold=False;st.paragraph_format.space_before=Pt(5);st.paragraph_format.space_after=Pt(3);st.paragraph_format.keep_with_next=True
st=doc.styles['Caption'];st.font.size=Pt(10);st.font.bold=False;st.paragraph_format.space_after=Pt(6)
def p(t='',style=None):
 q=doc.add_paragraph(t,style);q.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
 q.paragraph_format.keep_together=False
 return q
def h(t):
 q=p(t,'Heading 1');q.alignment=1

def sub(t):p(t,'Heading 2')
def fig(name,caption):
 q=p();q.alignment=1;q.paragraph_format.first_line_indent=Pt(0);q.paragraph_format.keep_with_next=True;q.paragraph_format.space_after=Pt(0)
 q.add_run().add_picture(str(A/(name+'.png')),width=Cm(15))
 q=p(caption,'Caption');q.paragraph_format.keep_together=True

def table(num,title,headers,rows,widths):
 q=p('TABLE '+num+'\n'+title.upper());q.alignment=1;q.paragraph_format.first_line_indent=Pt(0);q.paragraph_format.keep_with_next=True
 t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
 for c,v in zip(t.rows[0].cells,headers):c.text=v
 for rr in rows:
  for c,v in zip(t.add_row().cells,rr):c.text=str(v)
 for c,w in zip(t.columns,widths):c.width=Cm(w)
 for i,row in enumerate(t.rows):
  row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
  if i==0:row._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
  for j,c in enumerate(row.cells):
   c.width=Cm(widths[j]);c.vertical_alignment=1
   for q in c.paragraphs:
    q.paragraph_format.first_line_indent=Pt(0);q.paragraph_format.space_before=Pt(1);q.paragraph_format.space_after=Pt(1);q.paragraph_format.keep_with_next=i<len(t.rows)-1;q.alignment=0 if j==0 else 1
    for r in q.runs:r.font.size=Pt(10);r.bold=i==0
 borders=OxmlElement('w:tblBorders')
 for edge in ['top','bottom','left','right','insideH','insideV']:
  z=OxmlElement('w:'+edge);z.set(qn('w:val'),'single' if edge in ['top','bottom'] else 'nil');z.set(qn('w:sz'),'6');borders.append(z)
 t._tbl.tblPr.append(borders)
 for c in t.rows[0].cells:
  bb=OxmlElement('w:tcBorders');z=OxmlElement('w:bottom');z.set(qn('w:val'),'single');z.set(qn('w:sz'),'4');bb.append(z);c._tc.get_or_add_tcPr().append(bb)
 return t
# Native editable OMML equations.
def mr(t,plain=False):
 z=OxmlElement('m:r');rpr=OxmlElement('m:rPr');sty=OxmlElement('m:sty');sty.set(qn('m:val'),'p' if plain else 'i');rpr.append(sty);z.append(rpr);v=OxmlElement('m:t');v.text=t;z.append(v);return z
def sm(a,b):
 z=OxmlElement('m:sSub');e=OxmlElement('m:e');e.append(mr(a));ss=OxmlElement('m:sub');ss.append(mr(b,True));z.extend([e,ss]);return z
def fraction(a,b):
 z=OxmlElement('m:f')
 for tag,seq in [('m:num',a),('m:den',b)]:
  e=OxmlElement(tag)
  for v in seq:e.append(v)
  z.append(e)
 return z
def sqrt(a):
 z=OxmlElement('m:rad');pr=OxmlElement('m:radPr');v=OxmlElement('m:degHide');v.set(qn('m:val'),'1');pr.append(v);z.append(pr);z.append(OxmlElement('m:deg'));e=OxmlElement('m:e')
 for v in a:e.append(v)
 z.append(e);return z
def eq(no,seq):
 q=p();q.alignment=1;q.paragraph_format.first_line_indent=Pt(0);q.paragraph_format.space_before=Pt(3);q.paragraph_format.space_after=Pt(6);q.paragraph_format.keep_together=True
 z=OxmlElement('m:oMath')
 for v in seq:z.append(v)
 q._p.append(z);q.add_run('     ('+str(no)+')')


import shutil
for n in ['SPB_introduction_topology','extracted_network_switching']:
 shutil.copyfile(P/'icpe'/(n+'.png'),A/(n+'.png'))
(QA/'artifact.md').write_text('Expanded five-page ICPE digest from the preserved manuscripts. Staffan Norrga self-citation audit: two Norrga references among ten total (20 percent); two among eight scholarly papers if datasheets are excluded (25 percent). The 10-point venue minimum is retained; figures are reduced to 15 cm width. A4 single column, top 3 cm, other margins 2.5 cm, Times 10 pt body and captions, title 16 pt, anonymous, numbered pages. The user authorizes cuts and red full-paper expansion notes. Five figures, two tables, two native equations. PCB and Q3D views retained. No experiments claimed; remaining voltage and gate-network constraints remain explicit. Word export and Poppler used for visual QA because LibreOffice is absent.',encoding='utf-8')
def red(t):
 q=p(t)
 for r in q.runs:r.font.color.rgb=RGBColor.from_string('C00000')
 return q
def page():doc.add_page_break()
q=p('Topic 17 — Power Electronics for Transportation Electrification');q.paragraph_format.first_line_indent=Pt(0)
for r in q.runs:r.italic=True
q=p('Parasitic Aware Building Block Design for Stacked Polyphase Bridge Traction Inverters','Title');q.alignment=1
q=p('Abstract—The stacked polyphase bridge (SPB) partitions the dc-link voltage while retaining the phase-current requirement of the drive operating point. This paper connects that architectural freedom to the physical design of a high-current phase-leg building block. Charge-based device screening selects the 100 V EPC2361, and single-cell simulations support four parallel transistors per switch position for a candidate sixteen-submodule traction inverter. Current-sharing sensitivity motivates paired gate drive and Kelvin-source returns. A KiCad–Ansys Q3D–LTspice workflow then evaluates the routed networks. The operating and instrumented double-pulse test boards have evaluated commutation-loop inductances of 0.41 nH and 0.65 nH, respectively. The extracted test-board gate network changes the required drive settings and reveals a remaining gap to the project voltage target. Experimental correlation is planned for the full paper.');q.paragraph_format.first_line_indent=Pt(0)
for r in q.runs:r.bold=True
h('I. Introduction')
p('High-voltage traction inverters must combine high power with substantial phase current. In a conventional two-level bridge, each switch blocks the full dc-link voltage. The stacked polyphase bridge (SPB) instead connects three-phase bridges in series on the dc side, each feeding an isolated winding set of a common machine [1], [2]. Fig. 1 shows how voltage partitioning links the architecture to the semiconductor voltage class and the phase-leg implementation.')
p('Previous studies establish SPB modulation and losses [2], dc-link stability [3], and comparisons with alternative GaN converter systems [4]. Paralleled gallium nitride (GaN) stages introduce complementary constraints through commutation inductance, gate impedance, and common-source coupling [5]–[7]. Increasing the submodule count reduces each bridge voltage but does not reduce phase current at fixed total power, dc-link voltage, modulation index, and power factor. Device-level benefits therefore depend on a realizable high-current building block.')
p('The contribution is a sequential sizing procedure followed by extraction-based refinement. Voltage class and parallel count establish a candidate; cell symmetry and gate drive translate it into hardware; extracted networks then test the assumed switching margin. A favorable device comparison is useful only if the bridge retains sufficient switching margin at traction current. Excessive parasitic impedance can require slower commutation or a lower submodule voltage, feeding hardware constraints back into the architecture. The procedure identifies these constraints rather than claiming a globally optimum SPB architecture.')
fig('SPB_introduction_topology','Fig. 1. (a) SPB with N series-connected submodules and isolated winding sets. (b) One three-phase submodule with the studied leg highlighted. Each switch position contains four parallel GaN transistors; the diode symbol denotes equivalent reverse conduction.')
page()
h('II. Device and Parallel Count Selection')
p('The design point is 300 kW, Vdc = 1200 V, modulation index M = 1.15, power factor cosφ = 0.9, and fsw = 50 kHz. Defining M by a fundamental phase-voltage peak M Vm/2 gives')
eq(1,[mr('P = '),fraction([mr('3 M '),sm('V','dc'),mr(' '),sm('I','ph,rms'),mr(' cos ',True),mr('φ')],[mr('2'),sqrt([mr('2')])])])
p('The resulting phase current is approximately 228 A rms and 322 A peak, independent of submodule count under these assumptions. A junction limit of 125 °C and a peak drain–source voltage target of 90 V are adopted.')
p('Voltage classes are screened using the charge-based device figure of merit in [8]:')
eq(2,[mr('D-FOM = ',True),fraction([mr('1')],[sqrt([sm('R','DS(on)'),mr(' '),sm('C','oss,Q')])]),mr(',    ',True),sm('C','oss,Q'),mr(' = '),fraction([sm('Q','oss')],[sm('V','test')])])
p('Here, RDS(on) is on-state resistance and Qoss is output charge at test voltage Vtest. Higher D-FOM is favorable. Fig. 2(a) ranks the best surveyed candidate in each class relative to EPC2361. This device is selected [9], and N = 16 gives the candidate submodule voltage Vm = Vdc/N = 75 V. The survey uses typical 25 °C resistance and charge data at the respective datasheet test voltages.')
p('Charge-equivalent capacitance differs from differential datasheet capacitance. For EPC2361, the rounded output-charge quotient is 1800 pF at 50 V, consistent with the listed time-related value of 1796 pF; differential Coss is 1019 pF. This screening value is not a capacitance evaluated at the 75 V operating point.')
p('A single-transistor half bridge is simulated at 75 V with 2 Ω turn-on resistance, a preliminary 1.7 nH gate loop, and assumed power-loop inductances of 0.5 nH and 1 nH. The compact-loop case identifies approximately 80 A per device as a useful current scale, suggesting four devices. Neighboring counts are checked rather than treating this division as sufficient justification. Switching energies are evaluated over the sinusoidal current waveform; the peak-current event is not applied uniformly throughout the fundamental period.')
fig('digest_selection','Fig. 2. Initial selection: (a) highest surveyed D-FOM in each voltage class, normalized to EPC2361; (b) calculated phase-leg losses at 0.5 nH; and (c) voltage stress for two assumed commutation inductances. The dotted reference in (c) is the 90 V target.')
table('I','Preliminary parallel count comparison',['n','Device peak current (A)','Leg loss (W)','Tj (°C)','Peak VDS 0.5 / 1 nH (V)'],[['2','161','39.5','141','131 / 180'],['3','107','23.2','84','96 / 123'],['4','80.5','18.0','69','83 / 93'],['6','53.7','14.8','59','86 / 84']],[.8,4.0,2.5,2.5,6.2])
p('Table I uses fundamental-period averaging of switching energies and temperature-dependent resistance. The thermal assumptions are 40 °C ambient, 0.65 K/W heatsink-to-ambient for the leg, and 7.6 K/W junction-to-heatsink per device. Four is the smallest tested count passing both limits at 0.5 nH, not the absolute minimum-loss count; at 1 nH it misses the voltage target.')
red('The full paper will expand the device survey, single-cell energy maps, and thermal model, including their operating-condition dependence.')
page()
h('III. Gate Drive and Iterative Layout Design')
p('Four parallel devices require controlled dynamic current sharing. In the evaluated two-device case at 75 V and 120 A total current, a 0.3 nH power-loop mismatch has little influence on energy sharing, whereas gate loops of 2 nH versus 8 nH produce approximately 19% switching-energy imbalance. Without a Kelvin return, a 0.2 nH common-source mismatch produces approximately 29% imbalance. The gate and source-reference paths therefore require attention alongside the power paths.')
p('Fig. 3(a) divides the four switching cells into two pairs. Each cell contains one high-side device, one low-side device, and local decoupling. One dual-channel 2EDF7275K driver serves each pair, with separate high-side and low-side outputs, individual gate resistors, and dedicated Kelvin returns. Each output drives two gates; two driver ICs serve the complete leg [10].')
p('The selected output provides an 8 A peak sink capability. The preliminary four-gate loading study gives approximately 12–14 A peak sink demand and approximately 31% greater turn-on energy than the two-gate configuration. Pairing limits output loading and allows shorter gate branches. Symmetric placement and star connections aim to limit branch mismatch and shared impedance.')
fig('digest_gate_workflow','Fig. 3. (a) Four cells arranged as two driven pairs; HO and LO denote high-side and low-side outputs. Supply and Kelvin-return connections are omitted for clarity. (b) Routed-network refinement, with feedback to placement and drive settings. Wine and teal identify high-side and low-side gate paths in (a).')
p('The Kelvin return is taken from the dedicated source-reference pad rather than through the power-source conductors. This keeps the main source-current inductance outside the gate-return path, although the remaining gate-loop impedance still requires extraction. Symmetry within a pair also does not remove timing differences between the two driver ICs.')
p('Fig. 3(b) closes the initial assumptions through KiCad layout, Ansys Q3D extraction, and LTspice switching simulations. Conductor resistance, self-inductance, and mutual coupling are used to assess overshoot, held-off gate voltage, current sharing, and energy distribution. Failure to meet a target feeds back to geometry or drive settings and, where necessary, voltage partition or parallel count.')
p('Dynamic sharing and held-off gate disturbance impose different requirements. Matched branch impedance limits unequal transient loading, while a low-impedance sink path removes current coupled through the gate–drain capacitance. A symmetric layout can therefore share current well yet still develop excessive gate-voltage disturbance or voltage overshoot. Both quantities must be checked in the extracted-network model.')
p('The two driver ICs also introduce a separate timing sensitivity. A common command does not guarantee simultaneous device transitions when input routing and propagation delays differ. Within-pair matching and between-pair timing must consequently be assessed separately. Reducing shared routing length remains important because local branch symmetry does not remove inductance common to both driven gates.')
red('The full paper will detail gate-loop sensitivity, inter-driver timing, and the layout iterations. Operating-board verification with its corresponding extracted gate network remains required.')
page()
h('IV. Routed Building Block and Q3D Extraction')
p('Fig. 4 retains both physical board variants and their Q3D conductor models. The operating board represents the intended converter leg; the instrumented double-pulse test (DPT) board includes current-measurement provisions. Separating the variants prevents measurement-induced parasitics from being assigned to the intended converter.')
fig('digest_hardware_q3d','Fig. 4. (a) Operating-board and (b) DPT-board renderings; corresponding Q3D power networks in (c) and (d). Colors in the extraction models distinguish electrical nets and terminals, not field magnitude. The source-to-shunt path appears only in the DPT model.')
p('Table II separates the power-loop contributions. The evaluated operating-board loop supports the compact-loop sizing assumption, while the DPT geometry and shunt increase commutation inductance. The capacitor equivalent series inductance (ESL) is included separately from the extracted conductors.')
table('II','Evaluated loop inductances',['Quantity','Operating board (nH)','DPT board (nH)'],[['Power conductors','0.35','0.47'],['Capacitor ESL','0.06','0.06'],['Shunt contribution','—','0.12'],['Total commutation loop','0.41','0.65'],['Individual gate loop, HS / LS','Not extracted','12.5 / 7.6'],['Pair-driven gate loop, HS / LS','Not extracted','20.6 / 12.3']],[7.8,4.1,4.1])
p('The DPT gate network departs substantially from the preliminary 1.7 nH assumption. The pair-driven values include the shared-path effect: matched branches can retain a large common gate inductance. The power-loop result alone therefore cannot establish switching feasibility. DPT simulations include the extracted gate network, whereas the saved operating-board cases retain the preliminary gate model.')
p('The extraction is used to test the assumptions behind sizing, not merely to report a small loop value. The operating-board power path meets the initial compact-loop objective, but the instrumented-board gate network changes the switching transition. Measurement provisions must therefore be included in the DPT simulation, and the resulting switching energies cannot be substituted into the operating-board loss model without considering its different network.')
red('The full paper will provide extraction boundaries, branch and mutual-inductance matrices, gate-loop geometry, and correlation with the measurement arrangement. The revised switching energies will also be used to update the initial loss and temperature estimates.')
page()
h('V. Switching Assessment and Full Paper Validation')
p('Fig. 5 compares simulations at 75 V and approximately 316 A. Increasing the extracted-network DPT turn-on resistance from 2.5 Ω to 3.5 Ω reduces peak drain voltage from approximately 105 V to 93 V, while mean turn-on event energy per device increases from 24.3 µJ to 31.2 µJ.')
fig('digest_switching','Fig. 5. Simulated (a) high-side drain voltage and (b) held-off gate voltage. Operating cases retain the preliminary gate model; DPT cases use the extracted gate network. Cases in (b) differ in both network and bias.')
p('The evaluated 3.5 Ω DPT case remains above the project voltage target. Negative turn-off bias improves held-off gate margin in that configuration, but further shared-gate-path refinement is required. The operating-board switching margin must be reassessed with its extracted gate network.')
p('In the evaluated negative-bias DPT case, the maximum held-off gate excursion is approximately −0.5 V and the negative ringing reaches approximately −3.4 V over the assessed transitions. Positive and negative excursions must both be checked against the device limits; the minimum gate rating is −4 V [9].')
red('The full paper will report planned DPT correlation of voltage stress, current sharing, and switching energy. Experimental validation remains pending.')
h('VI. Conclusion')
p('Device screening and single-cell sizing support a four-device SPB building block. Paired drive and extracted-network assessment reveal constraints hidden by the initial lumped model, linking voltage partitioning to physical implementation. The remaining voltage-target gap requires gate-network refinement and experimental validation.')
h('References')
refs=[
'[1] S. Norrga et al., “A novel inverter topology for compact EV and HEV drive systems,” Proc. IECON, 2013, pp. 6590–6595.',
'[2] L. Jin et al., “Modulation and power losses of a stacked polyphase bridge converter,” IEEE J. Emerg. Sel. Topics Power Electron., vol. 5, no. 1, pp. 409–418, 2017.',
'[3] M. Nikouie et al., “DC-link stability analysis and controller design for the stacked polyphase bridges converter,” IEEE Trans. Power Electron., vol. 32, no. 2, pp. 1666–1674, 2017.',
'[4] G. Rohner et al., “Comparative evaluation of three-phase three-level flying capacitor and stacked polyphase bridge GaN inverter systems for integrated motor drives,” Electronics, vol. 13, Art. 1259, 2024.',
'[5] J. A. Brothers and T. Beechner, “GaN module design recommendations based on the analysis of a commercial 3-phase GaN module,” Proc. IEEE ECCE, 2019, pp. 4109–4116.',
'[6] J. Lu and D. Chen, “Paralleling GaN E-HEMTs in 10 kW–100 kW systems,” Proc. IEEE APEC, 2017, pp. 3049–3056.',
'[7] M. T. Tran et al., “A high-performance GaN power module with parallel packaging for high-current and low-voltage traction inverter applications,” IEEE J. Emerg. Sel. Topics Power Electron., vol. 13, no. 1, pp. 1188–1209, 2025.',
'[8] J. Azurza Anderson et al., “New figure-of-merit combining semiconductor and multi-level converter properties,” IEEE Open J. Power Electron., vol. 1, pp. 322–338, 2020, doi: 10.1109/OJPEL.2020.3018220.',
'[9] Efficient Power Conversion, “EPC2361 eGaN FET datasheet,” July 20, 2026.',
'[10] Infineon Technologies, “2EDF7275K data sheet,” rev. 2.8.']
for rr in refs:
 q=p(rr);q.paragraph_format.first_line_indent=Cm(-.55);q.paragraph_format.left_indent=Cm(.55);q.paragraph_format.space_after=Pt(0);q.alignment=0

# Symbols remain editable, with true subscripts throughout prose and tables.
symbols={'Tj':('T','j'),'Iph,rms':('I','ph,rms'),'Iph,pk':('I','ph,pk'),'Idev,pk':('I','dev,pk'),'VDS,pk':('V','DS,pk'),'RDS(on)':('R','DS(on)'),'Coss,Q':('C','oss,Q'),'Vtest':('V','test'),'Qoss':('Q','oss'),'Rg,on':('R','g,on'),'Tj,max':('T','j,max'),'Vdc':('V','dc'),'Vm':('V','m'),'fsw':('f','sw'),'VDS':('V','DS'),'Eon':('E','on'),'Ta':('T','a')}
pat=re.compile(r'(?<![A-Za-z])('+'|'.join(re.escape(k) for k in sorted(symbols,key=len,reverse=True))+r')(?![A-Za-z])')
paras=list(doc.paragraphs)+[q for t in doc.tables for row in t.rows for c in row.cells for q in c.paragraphs]
for q in paras:
 if re.match(r'^\[\d+\]',q.text):continue
 for rr in list(q.runs):
  old=rr.text
  if not pat.search(old):continue
  base=deepcopy(rr._r.rPr) if rr._r.rPr is not None else None;pos=0
  chunks=[]
  for m in pat.finditer(old):
   chunks.extend([(old[pos:m.start()],False,False),(symbols[m.group()][0],False,True),(symbols[m.group()][1],True,False)]);pos=m.end()
  chunks.append((old[pos:],False,False))
  for val,isub,ital in chunks:
   if not val:continue
   r=OxmlElement('w:r')
   if base is not None:r.append(deepcopy(base))
   rp=r.find(qn('w:rPr'))
   if rp is None:rp=OxmlElement('w:rPr');r.append(rp)
   if isub:
    z=OxmlElement('w:vertAlign');z.set(qn('w:val'),'subscript');rp.append(z)
   if ital:rp.append(OxmlElement('w:i'))
   z=OxmlElement('w:t');z.set(qn('xml:space'),'preserve');z.text=val;r.append(z);rr._r.addprevious(r)
  rr._r.getparent().remove(rr._r)
footer=sec.footer.paragraphs[0];footer.alignment=1;footer.paragraph_format.first_line_indent=Pt(0)
r=footer.add_run();fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');r._r.addnext(fld)
doc.core_properties.title='Parasitic Aware Building Block Design for Stacked Polyphase Bridge Traction Inverters';doc.core_properties.author='';doc.core_properties.last_modified_by='';doc.core_properties.subject='Five-page ICPE digest with red full-paper expansion notes'
settings=doc.settings.element;u=OxmlElement('w:updateFields');u.set(qn('w:val'),'true');settings.append(u)
doc.save(OUT)
print(OUT)
print('Words:',sum(len(q.text.split()) for q in doc.paragraphs),'Figures:',len(doc.inline_shapes),'Tables:',len(doc.tables),'Equations:',len(doc.element.xpath('.//m:oMath')))

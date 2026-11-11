from pathlib import Path
from copy import deepcopy
import json,sys,hashlib,re
from docx import Document
from docx.shared import Pt,Cm,Inches,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path.cwd();P=ROOT/'reports/paper'
SRC=P/'Submission-Files/Digest-ParasiticAwareSPB_revised_2026-11-02.docx'
OUT=P/'Submission-Files/Digest_LowVoltageGaN_SPB_LoadBoard_2026-11-05.docx'
A=P/'icpe/low_voltage_gan_digest_2026-11-05';A.mkdir(exist_ok=True)
# Reuse the existing native-vector drawing primitives, without executing old figures.
base=P/'icpe/make_compact_digest_figures.py'
ns={'__file__':str(base)};exec(base.read_text().split('dimensions={}')[0],ns)
ns['A']=A;ns['dimensions']={}
Fig=ns['Fig'];
original_finish=Fig.finish
def finish_selectively(self,name):
 if name=='load_paired_drive' or not (A/(name+'.png')).exists():original_finish(self,name)
Fig.finish=finish_selectively
D=ns['D'];read_raw=ns['read_raw'];RUN=ns['RUN'];T2=ns['T2'];np=ns['np']
INK=ns['INK'];TEAL=ns['TEAL'];WINE=ns['WINE'];GREY=ns['GREY']
# Workflow for the load board only.
f=Fig(454,86)
blocks=[('Voltage partition','Device and current'),('KiCad','Load-board layout'),('Ansys Q3D','Copper R and L matrix'),('LTspice','Drain and gate stress'),('Feasibility check','Voltage and gate margin')]
for i,lines in enumerate(blocks):
 x=2+91*i;f.rect(x,5,86,35,'white',INK)
 for j,t in enumerate(lines):f.text(x+43,19+j*12,t,7.5,'middle')
 if i<4:f.arrow([(x+86,23),(x+91,23)])
f.arrow([(408,40),(408,58),(136,58),(136,40)],WINE);f.text(272,55,'Revise layout or gate drive',7.5,'middle',WINE)
f.arrow([(408,58),(408,76),(45,76),(45,40)],WINE,'3 2');f.text(226,84,'Revisit submodule voltage if switching margin is insufficient',7.5,'middle',WINE)
f.finish('load_workflow')
# A pure load-board drawing and its extracted conductor geometry.
f=Fig(454,174)
f.text(4,9,'(a) KiCad load-board assembly',8);f.image(P/'figures/revb/r3d_load.png',0,13,165,140)
f.text(178,9,'(b) Q3D load-board power conductors',8);f.image(P/'figures/revb/q3d_loop_load.png',175,13,276,140)
for x,t,c in [(178,'DC+','#d92c27'),(231,'DC−','#2167b7'),(284,'Switch node','#ed9c20'),(370,'Terminals','#d5b85b')]:f.rect(x,158,6,6,c);f.text(x+10,164,t,8)
f.finish('load_layout_q3d')
# Gate arrangement uses only the existing paired-drive / Kelvin panels.
old=(P/'icpe/latest_digest_figures/fig05_gate_drive.svg').read_text()
# Keep vector groups with a clipped window; the sharing-sensitivity panel is omitted.
from html import escape
inner=old[old.index('<g font-family'):old.rfind('</svg>')]
# It has its own closing g; place whole artwork at a shifted origin, with clipping.
svg='<svg xmlns="http://www.w3.org/2000/svg" width="6.3055555556in" height="1.625in" viewBox="0 0 454 117"><rect width="454" height="117" fill="white"/><svg x="0" y="0" width="454" height="117" viewBox="155 0 299 117">'+inner+'</svg></svg>'
# Retain native size rather than magnifying only one set of figure lettering.
# New paired-drive-only schematic drawn directly, at printed size.
f=Fig(454,124)
f.text(4,10,'Two independently driven transistor pairs',8)
for idx,cx in enumerate([116,337]):
 f.rect(cx-29,30,58,54,'#F5F5F3',INK);f.text(cx,41,'Driver '+str(idx+1),8,'middle');f.text(cx,53,'HO',8,'middle',WINE);f.text(cx,79,'LO',8,'middle',TEAL)
 for side,x in [(0,cx-69),(1,cx+69)]:
  n=2*idx+side+1
  for y,c,lab in [(50,WINE,'QH'),(76,TEAL,'QL')]:
   a=cx-29 if side==0 else cx+29;b=x+8 if side==0 else x-8
   f.line([(a,y),(b,y)],c);rx=(a+b)/2;f.rect(rx-3,y-2,6,4,'white',c)
   f.line([(x-4,y-6),(x-4,y+6)]);f.line([(x,y-6),(x,y+6)]);f.line([(x,y-6),(x+6,y-6),(x+6,y-11)]);f.line([(x,y+6),(x+6,y+6),(x+6,y+11)])
   f.text(x-9 if side==0 else x+11,y-6,lab+str(n),7.5,'end' if side==0 else 'start')
f.text(226,105,'Each output drives two gates through individual resistors',8,'middle')
f.text(226,119,'Dedicated Kelvin returns; matched paths within each pair',8,'middle',TEAL)
f.finish('load_paired_drive')
# Scientific plots from already completed load-board simulations only.
f=Fig(454,173)
caseinfo=[('board_load_g20_on2',GREY,'3 2','2 Ω / 0 V'),('board_load_g20_on3',WINE,'4 2','3 Ω / 0 V'),('board_load_g20_on3_revised_drive',TEAL,None,'3 Ω / −1 V')]
for panel,(x,yl,ylim,yt) in enumerate([(35,'Worst-cell drain voltage (V)',(-5,120),[0,60,90,120]),(264,'Held-off gate voltage (V)',(-3,2),[-3,-2,-1,0,1,2])]):
 t=f.axes(x,20,175,87,(-5,65),ylim,[0,30,60],yt,'Time from command (ns)',yl);f.text(x,10,'(a)' if panel==0 else '(b)',8)
 for name,c,dash,lab in caseinfo:
  z=read_raw(RUN/(name+'.raw'))[0];tt=z['time'];mask=(tt>=T2)&(tt<=T2+150e-9)
  if panel==0:
   k=max(range(1,5),key=lambda k:np.max((z[f'v(dh{k})']-z[f'v(qh_s_{k})'])[mask]));v=z[f'v(dh{k})']-z[f'v(qh_s_{k})']
  else:
   # Device 1 has the largest held-off positive gate peak in every plotted case.
   k=max(range(1,5),key=lambda k:np.max((z[f'v(gh{k})']-z[f'v(qh_s_{k})'])[mask]));v=z[f'v(gh{k})']-z[f'v(qh_s_{k})']
  ii=np.flatnonzero((tt>=T2-5e-9)&(tt<=T2+65e-9))[::2];f.line([t((tt[i]-T2)*1e9,v[i]) for i in ii],c,dash,lw=.85)
 limit=90 if panel==0 else .8;f.line([t(-5,limit),t(65,limit)],GREY,'2 2',.6)
for x,(name,c,dash,lab) in zip([43,187,331],caseinfo):f.line([(x,143),(x+16,143)],c,dash);f.text(x+21,146,lab,8)
f.text(227,163,'Legend: external turn-on resistance / off-state gate bias; gate loop 20 nH',8,'middle')
f.finish('load_switching')
# Derive worst-device quantities for a compact results table.
rows=[]
for name in ['board_load_g10_on3_revised_drive','board_load_g20_on2','board_load_g20_on3','board_load_g20_on3_revised_drive']:
 b=D['boards'][name]
 vals={'case':name,'Vpk':max(b[f'{q}{k}'] for q in ['vpk','vhpk'] for k in range(1,5)), 'gate_bump':max(b[f'bump{k}'] for k in range(1,5)), 'gate_min':min(b[f'{q}{k}'] for q in ['glmin','ghmin'] for k in range(1,5)),'Eon_mean_uJ':sum(b[f'eon{k}'] for k in range(1,5))*1e6/4}
 rows.append(vals)
(A/'load_results.json').write_text(json.dumps(rows,indent=2))
# Preserve the user's latest digest and use its venue styles as the basis for a separate draft.
source_hash=hashlib.sha256(SRC.read_bytes()).hexdigest();doc=Document(SRC)
# Retain the native equation, operating table, citation strings, styles and page system.
source_pars=list(doc.paragraphs)
eqs=[deepcopy(p._p) for p in source_pars if p._p.xpath('.//m:oMath')]
table1=deepcopy(doc.tables[0]._tbl)
refs=[p.text for p in source_pars if re.match(r'^\[\d+\]',p.text)]
for el in list(doc.element.body):
 if el.tag!=qn('w:sectPr'):doc.element.body.remove(el)
for name in ['Normal','Caption','Heading 1','Heading 2']:
 st=doc.styles[name];st.font.name='Times New Roman';st.font.size=Pt(10);st.font.color.rgb=RGBColor(0,0,0)
 st.paragraph_format.space_after=Pt(2);st.paragraph_format.space_before=Pt(0);st.paragraph_format.line_spacing=1
 st.paragraph_format.keep_with_next=name.startswith('Heading')
for s in doc.sections:
 s.page_width=Cm(21);s.page_height=Cm(29.7);s.top_margin=Cm(3);s.bottom_margin=Cm(2.5);s.left_margin=Cm(2.5);s.right_margin=Cm(2.5)

def p(t='',style=None,bold=False,red=False):
 q=doc.add_paragraph(style=style);r=q.add_run(t);r.bold=bold;r.font.name='Times New Roman';r.font.size=Pt(10);r.font.color.rgb=RGBColor.from_string('EE0000' if red else '000000');q.paragraph_format.widow_control=True
 if style not in ['Heading 1','Heading 2','Title','Caption']:q.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;q.paragraph_format.first_line_indent=Cm(.35)
 # Apply inline mathematical typography without changing wording.
 tokens={'Vdc':('V','dc'),'Vm':('V','m'),'Iph,rms':('I','ph,rms'),'Coss,Q':('C','oss,Q')}
 if style not in ['Title','Caption','Heading 1','Heading 2'] and not t.startswith('['):
  parts=re.split(r'(Iph,rms|Coss,Q|Vdc|Vm|\bM\b|\bN\b)',t)
  if len(parts)>1:
   for rr in list(q.runs):q._p.remove(rr._r)
   for part in parts:
    pieces=[(part,False,part in ['M','N'])] if part not in tokens else [(tokens[part][0],False,True),(tokens[part][1],True,False)]
    for val,sub,it in pieces:
     rr=q.add_run(val);rr.font.name='Times New Roman';rr.font.size=Pt(10);rr.bold=bold;rr.italic=it;rr.font.subscript=sub;rr.font.color.rgb=RGBColor.from_string('EE0000' if red else '000000')
 return q

def h(t,level=1):
 q=p(t,'Heading '+str(level));q.alignment=WD_ALIGN_PARAGRAPH.CENTER if level==1 else WD_ALIGN_PARAGRAPH.LEFT;return q

def eq(i):
 el=deepcopy(eqs[i]);doc.element.body.insert(-1,el)

def fig(path,caption,widthpt):
 q=doc.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER;q.paragraph_format.space_after=Pt(0);q.paragraph_format.keep_with_next=True
 q.add_run().add_picture(str(path),width=Inches(widthpt/72));c=p(caption,'Caption');c.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;c.paragraph_format.keep_with_next=False

def page():doc.add_page_break()
# Page 1
p('Topic 17 — Power Electronics for Transportation Electrification')
q=p('Low-Voltage GaN Utilization for High-Voltage Stacked Polyphase Bridge Traction Inverters','Title');q.alignment=WD_ALIGN_PARAGRAPH.CENTER
for r in q.runs:r.font.size=Pt(16);r.bold=True
p('Abstract—The stacked polyphase bridge (SPB) permits a high-voltage traction drive to use low-voltage gallium nitride (GaN) transistors by distributing the dc-link voltage among series-connected submodules. The resulting device advantage depends on retaining switching margin at the required phase current. This paper investigates that constraint through a load-board phase leg for a 300-kW, 1200-V drive. A sixteen-submodule arrangement and four parallel 100-V transistors per switch position form the candidate implementation. A KiCad–Ansys Q3D–LTspice workflow relates the routed copper network to drain overshoot and gate disturbance. The extracted local commutation-loop estimate is approximately 0.41 nH, but the simulated off-state gate peak still reaches approximately 1.4 V with zero off-state bias. A revised gate drive reduces this peak to approximately 0.44 V; the 20-nH gate-loop case remains near the 90-V drain-voltage target. These results identify the joint power-loop and gate-drive constraints on low-voltage GaN utilization in an SPB building block. Experimental testing of one building block is planned for the full paper.',bold=True)
p('Index Terms—Gallium nitride, gate drive, parasitic inductance, stacked polyphase bridge, traction inverter.')
h('I. Introduction')
p('A high dc-link voltage reduces the dc current associated with traction power, but a conventional two-level inverter still requires each switch to block the full dc-link voltage and conduct the phase current. The stacked polyphase bridge (SPB) distributes this voltage among three-phase submodules, each supplying an isolated winding set of a common machine [1], [2]. Fig. 1 shows the architecture and the phase leg investigated here.')
fig(P/'icpe/latest_digest_figures/fig01_topology.png','Fig. 1. (a) SPB voltage partition and isolated winding sets. (b) One submodule; each switch symbol represents four parallel GaN transistors.',454)
p('Voltage partitioning opens access to low-voltage gallium nitride (GaN) devices, whose resistance and switching charge can be favorable. It does not remove the high-current requirement. The useful voltage class therefore depends on whether a physical building block can switch the phase current without consuming the available drain- and gate-voltage margins.')
p('SPB studies address modulation, losses, stability and comparisons with other converter systems [2]–[4]. Research on paralleled GaN stages establishes the importance of commutation paths, gate impedance and source coupling [5]–[7]. This work connects those implementation constraints to a selected SPB voltage partition. Its contribution is a quantified assessment of the load-board switching margins, showing why a low commutation inductance must be accompanied by suitable gate-drive settings. The study evaluates one routed phase-leg design and does not establish complete-drive performance.')
# Page 2
page();h('II. Voltage Partition and Building Block Requirements')
p('Table I defines the traction operating point and the preliminary design constraints. For equal submodule voltages and balanced sinusoidal operation, the total active power is given by (1).')
eq(0)
p('Here, Vdc is the total dc-link voltage, Iph,rms is the rms phase current, and cosφ is the power factor. The modulation index M is defined by a fundamental phase-voltage peak M Vm/2 for each submodule. Increasing the number N of series-connected submodules reduces Vm while increasing the number of contributing winding sets. The phase-current requirement therefore remains unchanged for a fixed total power, dc-link voltage, M and power factor.')
p('TABLE I  DESIGN OPERATING POINT AND PRELIMINARY CONSTRAINTS').alignment=WD_ALIGN_PARAGRAPH.CENTER
doc.element.body.insert(-1,table1)
h('A. Semiconductor Voltage Class and Submodule Voltage',2)
p('Fig. 2 compares on-state resistance and charge-equivalent output capacitance for the surveyed GaN devices. The charge-based device figure of merit in [8] is given by (2), where Coss,Q denotes charge-equivalent capacitance rather than the differential capacitance at one drain voltage. A higher value favors a lower resistance–capacitance product under the underlying switching model.')
eq(1)
fig(P/'icpe/latest_digest_figures/fig02_devices.png','Fig. 2. Surveyed GaN voltage classes. Dashed contours indicate constant resistance–capacitance products; lower products correspond to higher device figure of merit.',252)
p('The surveyed comparison motivates the EPC2361 as the 100-V candidate [9]. For the selected voltage partition, Vm = Vdc/N leaves a nominal overshoot allowance below the project drain-voltage target. This allowance must accommodate switching transients and submodule-voltage variation; the device rating alone does not establish suitability.')
h('B. Parallel Devices as an Initial Design Choice',2)
p('Four parallel transistors per switch position are retained as the starting arrangement from the preliminary current and loss assessment. Ideal current sharing gives approximately 80 A per device at peak phase current. Two transistor pairs permit a symmetric placement and paired gate drive. The parallel count is treated as a candidate to be checked against the routed network, rather than as a substitute for controlling commutation inductance.')
# Page 3
page();h('III. Load Board Design and Parasitic Extraction')
p('Fig. 3 defines the design loop for the load board, which is the phase-leg building block intended to carry the converter current. Initial voltage and current choices set the device arrangement. The layout and circuit model then determine whether that arrangement retains sufficient switching margin. If it does not, the design returns to the layout, gate drive or voltage partition.')
fig(A/'load_workflow.png','Fig. 3. Load-board design loop. Q3D supplies the copper resistance and inductance matrices; gate-loop inductance is evaluated over the stated sensitivity range.',454)
h('A. Symmetric Layout and Paired Gate Drive',2)
p('The power stage uses four parallel high-side and four parallel low-side transistors. Local dc-link capacitors and closely coupled outgoing and return conductors shorten the commutation path. Similar connection lengths within each transistor pair reduce avoidable gate- and power-path asymmetry. Dedicated Kelvin returns separate the gate-current return from the main source-current path.')
p('Fig. 4 shows the paired gate-drive arrangement. Two dual-channel driver integrated circuits serve the phase leg: each channel drives two transistors through individual gate resistors [10]. The turn-off path must sink the gate–drain displacement current generated during drain-voltage transitions. Matching gate paths is therefore required together with a low-impedance sink path; matching only the dc resistance of the power branches is insufficient.')
fig(A/'load_paired_drive.png','Fig. 4. Two independently driven transistor pairs. HO and LO denote high- and low-side driver outputs; each transistor uses an individual gate resistor and Kelvin return.',454)
h('B. Q3D Network and LTspice Model',2)
p('The KiCad geometry is transferred to Ansys Q3D with terminals at device and capacitor connections. The load-board power network contains 29 branches and retains the extracted resistance matrix and mutual inductive coupling. The present circuit representation uses dc copper resistance and partial inductances extracted at 100 MHz. It is an approximation of the routed network, not a broadband identification of the complete assembly.')
p('The equivalent local commutation-loop estimate includes capacitor equivalent series inductance and is approximately 0.41 nH per cell. This supports using a compact power path in the initial screen, but the full coupled network is retained for the load-board switching assessment. Replacing that network by one loop-inductance value would discard branch interactions relevant to parallel devices.')
p('The gate network is evaluated with representative total loop inductances of 10 nH and 20 nH. These are sensitivity assumptions, distinct from the extracted copper power network. Nonlinear device models are used in LTspice, with voltages evaluated at the individual transistor terminals. The model checks drain stress and gate excursions together, because improving one may leave the other constraint unresolved.')
# Page 4
page();h('IV. Load Board Switching Assessment')
p('Fig. 5 connects the physical load-board assembly to the Q3D conductor model. The conductor overlap and interlayer connections provide a compact local commutation path. The assessment uses the same routed power network for every gate-drive case, so the resulting differences isolate the effect of the drive settings and assumed gate-loop inductance.')
fig(A/'load_layout_q3d.png','Fig. 5. (a) KiCad load-board assembly. (b) Q3D load-board power conductors. Colours identify the dc rails, switch node and device/capacitor terminals.',454)
h('A. Assessment Conditions and Comparison Basis',2)
p('The switching study uses a 75-V local bus and an inductive-load transient. The saved transition occurs near 316 A total current, close to the specified phase-current peak. The transistor model temperature is 27 °C. All cases use a 5-V on-state command, an external turn-off resistance of 1 Ω and driver pull-up/pull-down resistances of 0.85 Ω/0.35 Ω. External turn-on resistance and off-state bias are varied as listed in Table II.')
p('The drain-voltage metric is the maximum across all four parallel devices and both assessed commutations: low-side turn-off and high-side voltage rise during low-side turn-on. The gate metric is the highest held-off high-side gate voltage during the latter transition. The minimum gate voltage is checked across both sides and the saved transitions. This avoids accepting the stage from a favorable device or one switching edge.')
h('B. Coupled Drain and Gate Constraints',2)
p('Table II shows that increasing turn-on resistance reduces the worst-device drain peak with zero off-state bias. The held-off gate disturbance remains above the datasheet minimum threshold of 0.8 V [9]. Crossing that threshold is a warning of possible unintended conduction; the waveform alone does not quantify a shoot-through current. Drain-voltage compliance therefore cannot serve as the sole acceptance criterion.')
p('TABLE II  LOAD-BOARD SIMULATION RESULTS').alignment=WD_ALIGN_PARAGRAPH.CENTER
headers=['Gate loop\n(nH)','Turn-on R\n(Ω)','Off bias\n(V)','Drain peak\n(V)','Gate peak\n(V)','Gate minimum\n(V)']
t=doc.add_table(rows=1, cols=6)
for c,txt in zip(t.rows[0].cells,headers):c.text=txt
for setting,r in zip([(10,3,-1),(20,2,0),(20,3,0),(20,3,-1)],rows):
 values=list(setting)+[f"{r['Vpk']:.1f}",f"{r['gate_bump']:.2f}",f"{r['gate_min']:.2f}"]
 for c,v in zip(t.add_row().cells,values):c.text=str(v)
# IEEE booktabs-like treatment.
pr=t._tbl.tblPr;borders=OxmlElement('w:tblBorders')
for edge in ['top','bottom','insideH','left','right','insideV']:
 e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single' if edge in ['top','bottom'] else 'nil');e.set(qn('w:sz'),'6');borders.append(e)
pr.append(borders)
for c in t.rows[0].cells:
 cp=c._tc.get_or_add_tcPr();bd=OxmlElement('w:tcBorders');e=OxmlElement('w:bottom');e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');bd.append(e);cp.append(bd)
 for r in c.paragraphs[0].runs:r.bold=True
p('A negative off-state command reduces the gate peak, but it also changes the switching transient and requires a check of the negative gate excursion. The revised 20-nH case remains approximately at the drain-voltage target, leaving no useful margin for tolerances or operating-point variation. The lower gate-inductance case provides more headroom at this operating point, without establishing compliance over a full traction operating envelope.')
# Page 5
page();h('V. Implications and Planned Experimental Validation')
p('Fig. 6 shows the load-board response for the higher gate-inductance assumption. Increasing turn-on resistance suppresses the drain peak, whereas the off-state bias controls the positive gate excursion more directly. The two actions must be assessed together. A local commutation loop below a nanohenry does not by itself establish that a 100-V device can be used reliably in the selected SPB voltage partition.')
fig(A/'load_switching.png','Fig. 6. Load-board waveforms near 316 A and 75 V: (a) worst-device high-side drain voltage and (b) largest held-off gate response. Grey references mark 90 V and 0.8 V.',454)
p('The architectural implication is that the permissible submodule voltage depends on the implemented gate and power paths. If sufficient margin cannot be recovered through routing and drive settings, the nominal submodule voltage must be reduced or the device class reconsidered. These changes feed back into the SPB submodule count and the expected device benefit. The present results support this design feedback, but they do not demonstrate a final loss optimum or full-drive efficiency.')
p('Because of the digest page limit, experimental validation is reserved for the full paper. One load-board building block will be tested to compare measured drain and gate transients and switching energy with the simulation predictions. The planned assessment will check the remaining voltage margin and the effect of drive settings at representative current levels. These measurements have not yet been performed.',red=True)
h('VI. Conclusion')
p('Low-voltage GaN utilization in a high-voltage SPB traction inverter requires a feasible high-current building block. The load-board study connects voltage partition and parallel devices to the routed copper network and gate-drive constraints. The simulations show that low commutation inductance must be accompanied by control of the held-off gate disturbance, and that the selected voltage partition still requires additional operating margin and experimental confirmation. The resulting design basis is the joint drain- and gate-voltage assessment, rather than the nominal device rating or an isolated loop-inductance target.')
h('References')
for ref in refs:
 q=p(ref);q.paragraph_format.first_line_indent=Cm(-.5);q.paragraph_format.left_indent=Cm(.5);q.paragraph_format.space_after=Pt(0)
# Uniform table text; allow rows to expand and keep figures with captions.
for table in doc.tables:
 for row in table.rows:
  for c in row.cells:
   for q in c.paragraphs:
    q.paragraph_format.space_after=Pt(0);q.paragraph_format.space_before=Pt(0);q.paragraph_format.line_spacing=1
    for r in q.runs:r.font.name='Times New Roman';r.font.size=Pt(10);r.font.color.rgb=RGBColor(0,0,0)
# Remove unused relationships and media so the new package contains only included assets.
used={n.get(qn('r:embed')) for n in doc.element.xpath('.//a:blip')}
for rid,rel in list(doc.part.rels.items()):
 if rel.reltype.endswith('/image') and rid not in used:doc.part.drop_rel(rid)
doc.core_properties.title='Low-Voltage GaN Utilization for High-Voltage Stacked Polyphase Bridge Traction Inverters'
doc.core_properties.subject='Load-board design and switching constraints for an SPB traction inverter'
doc.core_properties.comments='';doc.save(OUT)
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==source_hash
s='\n'.join(x.text for x in doc.paragraphs)
assert not re.search(r'\bDPT\b|double.pulse|1\.7\s*nH',s,re.I)
(A/'artifact.md').write_text(f'''Separate IEEE-style ICPE digest. User's current digest preserved: {SRC}; SHA256 {source_hash}.\nNew focus: low-voltage GaN utilization constrained jointly by load-board power network and gate drive. A4, original margins, single column; Times New Roman 10 pt, title 16 pt; native venue styles, operating table and two equations retained. Five planned pages with explicit page breaks. Six figures: topology, device screening, workflow, paired gate drive, load-board assembly/Q3D, and load-board-only switching. Existing completed simulations reused, not rerun. Gate inductances 10/20 nH are assumptions, not extracted load-board gate values. No experimental results claimed; one building block planned for testing in full paper, in red. No measurement-board content.\nVisual QA via packaged renderer if available, otherwise Word PDF export and Poppler.\n''')
print(OUT);print('Words',len(s.split()),'Figures',len(doc.inline_shapes),'Equations',len(doc.element.xpath('.//m:oMath')))

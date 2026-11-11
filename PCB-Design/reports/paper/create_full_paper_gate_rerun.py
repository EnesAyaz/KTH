"""Update the full ICPE manuscript from completed LTspice gate-loop reruns."""
from pathlib import Path
from copy import deepcopy
import json,re
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image

P=Path(__file__).parent
A=P/'icpe/gate_loop_rerun_2026-11-02'
D=json.loads((A/'results.json').read_text())
OUT=P/'SPB_ICPE_full_paper_LTspice_rerun_2026-11-02.docx'
doc=Document(P/'SPB_ICPE_complete_manuscript_with_Q3D_2026-10-29.docx')
ps=doc.paragraphs

def put(i,t):
 q=ps[i];fmt=deepcopy(q.runs[0]._r.rPr) if q.runs and q.runs[0]._r.rPr is not None else None
 q.clear();r=q.add_run(t)
 if fmt is not None:r._r.insert(0,fmt)

put(2,'Abstract—The stacked polyphase bridge (SPB) introduces a voltage-partitioning degree of freedom into high-voltage traction inverters: the number of series-connected submodules determines the semiconductor voltage class, while the phase-current requirement remains high. This paper presents a hardware-constrained design procedure for an SPB phase-leg building block. A charge-based device figure of merit identifies the 100 V EPC2361 as the preferred candidate among the surveyed devices. Single-cell simulations use gate-loop inductances of 10 nH and 20 nH and commutation-loop inductances of 0.5 nH and 1 nH. A peak-current voltage screen and electrothermal comparison identify four parallel transistors per switch position as an initial candidate for sixteen submodules. Current-sharing sensitivity motivates symmetric transistor pairs and dedicated Kelvin returns. An iterative KiCad–Ansys Q3D–LTspice workflow replaces the assumed paths with routed networks. The extracted double-pulse test (DPT) network requires a joint assessment of resistance, gate disturbance, and switching energy. Low-current resonance and the remaining gap to the 90 V drain-voltage target require further drive refinement. The contribution is to connect SPB voltage selection to the physical switching constraints governing low-voltage devices at traction-current levels. Experimental double-pulse tests are planned for the full paper.')
put(9,'This paper presents a hardware-constrained design procedure for an SPB phase-leg building block. Single-cell switching simulations establish an initial current range using representative gate-loop and commutation-loop inductances. Losses, junction temperature, and the voltage stress of both switches then determine the parallel-count candidate. Current-sharing sensitivity guides the symmetric cell arrangement and paired gate drive. An iterative layout, parasitic-extraction, and circuit-simulation workflow evaluates whether the assumed switching conditions can be maintained in the routed building block. Separate operating and double-pulse test (DPT) boards distinguish the intended converter layout from measurement-related parasitics. The contribution is to connect SPB voltage partitioning and device selection to the physical constraints governing high-current implementation.')
put(35,'The selected EPC2361 is evaluated in a half-bridge model with one device per switch position. Double-pulse simulations are performed at a submodule voltage of 75 V over a device-current sweep. Gate-loop inductances of 10 nH and 20 nH represent the preliminary range of interest. Commutation-loop inductances of 0.5 nH and 1 nH separately represent a compact power path and a higher-inductance sensitivity case. The lumped gate-loop value includes the outgoing gate path and its return; it is distinct from the power-loop inductance. The gate drive uses +5 V on-state bias, −1 V off-state bias, 3 Ω external turn-on resistance, and 1 Ω external turn-off resistance. The pulsed driver model uses source and sink resistances of 0.85 Ω and 0.35 Ω; driver current limiting and propagation-delay spread are outside this preliminary model. Switching maps are evaluated at the device model’s nominal temperature of 27 °C.')
put(36,'Fig. 3 compares the voltage-stress and turn-on-energy results for the four combinations of power- and gate-loop inductance. Voltage stress is evaluated as the larger of the low-side drain-voltage peak at turn-off and the high-side peak during low-side turn-on. This avoids selecting the device current from only one switching transition. With the compact commutation path, operation near 80 A per device satisfies the drain-voltage target for both gate-loop cases. The larger power-loop case exceeds the target and cannot be accepted solely by increasing the parallel count.')
put(37,'The single-cell results establish approximately 80 A as a preliminary current scale for the compact-loop case, rather than an absolute device-current limit. Dividing the required phase-current peak by this value suggests four parallel transistors per switch position. Neighboring counts are compared on the same drive and thermal basis. This is a peak-current screen: Fig. 3 also shows resonant overshoot at low current, so compliance over the full sinusoidal current range still requires drive refinement. Held-off gate disturbance is checked separately against the minimum threshold; a passing drain-voltage result alone does not establish gate-drive margin.')
put(39,'Fig. 3. Simulated single-cell characteristics at 75 V: (a) the larger drain–source voltage peak across the two evaluated switching transitions and (b) turn-on energy. Legend entries give gate-loop / commutation-loop inductance. Teal and wine distinguish the 10 nH and 20 nH gate cases; solid and dashed lines distinguish 0.5 nH and 1 nH power loops. Markers denote simulated operating points, with connecting lines guiding the eye. The dashed grey line denotes the 90 V target. Cases exceeding the constraints are sensitivity results, not recommended operating points.')
put(43,'The single-cell switching-energy maps are evaluated over the sinusoidal phase-current waveform to estimate average switching losses. The measured current at the first turn-off, rather than the programmed current parameter, is used for interpolation. Turn-on and turn-off energies are obtained by integrating terminal voltage multiplied by drain current over 150 ns windows, and piecewise-linear interpolation supplies intermediate current points. The phase-leg switching estimate includes the complementary-device output-energy contribution in addition to the hard-switching energy maps. Conduction losses use temperature-dependent on-state resistance, with resistance and junction temperature solved iteratively. Switching-energy temperature dependence is not included in these first-pass thermal estimates.')
put(45,'Fig. 4(a) shows the loss distribution for the nominal gate-loop case and compact commutation path. Additional parallel devices reduce conduction loss, while switching charge, gate loading, and layout complexity limit the benefit of further paralleling. The corresponding voltage-stress comparison in Fig. 4(b) shows that overshoot is not necessarily monotonic with parallel count. Gate-network dynamics therefore have to be checked alongside the reduction in current per device.')
put(47,'Fig. 4. Parallel-count comparison at 75 V, 228 A rms phase current, and 50 kHz: (a) phase-leg loss distribution for a 10 nH gate loop and 0.5 nH commutation loop; (b) the larger drain-voltage peak across the two switching transitions at the required phase-current peak. Voltage-panel legend entries give gate-loop / commutation-loop inductance in nH, using the encoding of Fig. 3. The grey line denotes the 90 V target. The loss components are identified by the shared legend above the panels.')
put(49,'Table II compares the candidate parallel counts for both gate-loop cases. Two devices exceed the thermal limit, while three fail the compact-loop drain-voltage target. Four are the smallest tested count passing the peak-current voltage screen and thermal estimate for both gate-loop cases at the compact power-loop assumption. This establishes an implementation candidate; it does not demonstrate voltage compliance over the entire current waveform. The assumed gate bias and resistances are part of the selection.')
put(51,'Loss and junction-temperature estimates in Table II use the 0.5 nH commutation-loop case and the cooling assumptions stated above. The voltage columns show the larger of the evaluated low-side turn-off and high-side turn-on peaks. Values are interpolated at the required peak current per device. Gate-loop inductance is a screening parameter; final acceptance requires the routed network.')
put(52,'Four devices are selected as the implementation candidate and arranged as two identical transistor pairs. This is not the absolute minimum-loss count: further devices can reduce calculated conduction loss but increase the device count and gate-drive burden. Moreover, the higher gate-loop case demonstrates that a lower per-device current does not guarantee a lower drain-voltage peak. The selected arrangement must consequently be verified with the complete power and gate networks.')
put(53,'The higher commutation-inductance cases fail the voltage target, including at the selected parallel count. The design therefore requires a compact power path and controlled gate-drive dynamics; paralleling alone does not recover the available blocking-voltage margin. Current sharing is still assumed equal in the first-pass comparison. The following stage translates the selected count into a symmetric arrangement and evaluates whether the routed geometry preserves those conditions.')
put(56,ps[56].text+' These perturbation cases isolate mismatch mechanisms; their branch values do not replace the 10 nH and 20 nH gate-loop cases used for preliminary sizing. The complete routed network is subsequently used to account for shared paths and coupling.')
put(62,'The selected driver provides a peak sink-current capability of 8 A per channel [11]. Driving two gates from each channel limits the charge handled by one output and permits short, matched branches about the driver. A low-impedance turn-off path is needed to remove displacement current coupled through the gate–drain capacitance, but its damping and bias must also control negative ringing. The nominal current capability alone does not establish gate-voltage margin; both the driven and held-off gate waveforms must be checked with the complete network.')
put(69,'The paired configuration is translated into a routed board and evaluated through the extraction-based workflow in Section V. The 10 nH and 20 nH lumped gate-loop cases provide an initial design basis. Extraction then replaces them with individual and shared branches, allowing the current capability, switching margin, and loss estimate to be reassessed for the physical building block.')
put(72,'Initial sizing establishes a candidate voltage and parallel count using the two gate-loop and two commutation-loop cases. The routed building block must then be assessed to determine whether the associated voltage and gate-drive margins can be retained. Fig. 6 connects the KiCad layout, Ansys Q3D parasitic extraction, and LTspice switching assessment. Its feedback is used to revise placement, routing, or drive settings when the complete network changes the switching response.')
put(79,'The DPT gate-network extraction in Fig. 7(d) places the individual and pair-driven paths in the same order of magnitude as the preliminary gate-loop cases. The pair-driven paths include the effect of shared routing, so matching the individual branches does not eliminate common inductance. The 20 nH screening case is representative rather than a guaranteed upper bound. A scalar loop estimate cannot reproduce every shared-path and mutual-coupling effect; the extracted network is therefore used for the final switching assessment.')
put(86,'Switching simulations near the required phase-current peak compare the routed power paths with the assumed and extracted gate networks. Table III reports the complete drive configurations and their results. For the operating board, the assumed gate and Kelvin-return inductances are split in a fixed 70:30 ratio, with their sum equal to the stated gate-loop value. This split is a modeling assumption, not an extraction result. The 10 nH and 20 nH cases assess sensitivity until the operating-board gate network is extracted. The DPT cases use either the same lumped branch representation or the extracted gate network. Shared paths make these network models more informative than an isolated scalar inductance.')
put(88,'Table III reports the maximum high-side drain–source voltage across the four cells during low-side turn-on and the mean turn-on energy per transistor for that event. These event energies are not fundamental-period average losses. The revised operating-board drive uses the preliminary sizing settings; the zero-bias case shows the gate-disturbance problem. In the extracted DPT gate network, a shared turn-on resistor of 1 Ω or 1.5 Ω feeds two individual 0.5 Ω gate resistors. The listed turn-on values are the corresponding effective per-device resistances under equal pair currents; the individual resistors also remain in the turn-off path. The lumped DPT comparison uses zero external turn-off resistance. Extracted power paths are used in all cases; gate-network extraction applies only to the cases identified in the table.')
put(89,'Fig. 9(a) shows the high-side drain-voltage transients for the revised operating-board drive and two extracted-network DPT resistance settings. Increasing turn-on resistance reduces voltage stress at the cost of greater switching energy. The extracted-network DPT configuration remains above the project drain-voltage target, so additional gate-network or drive optimization is required before accepting it.')
put(90,'Fig. 9(b) compares the held-off high-side gate voltage. On the same operating-board gate model, negative turn-off bias and the revised turn-off resistance suppress the positive disturbance observed with zero bias. The operating-board drain-voltage peak approaches the target in the larger gate-loop case, leaving no useful design margin. The lumped DPT cases also show why negative bias cannot be selected from the positive gate bump alone: their minimum gate voltage violates the negative rating. The extracted DPT trace represents its complete network and separate drive settings. Positive disturbance, negative ringing, and driven-gate overshoot must all be assessed against their respective limits.')
put(92,'Fig. 9. Switching simulations at 75 V and approximately 316 A: (a) worst-cell high-side drain–source voltage during low-side turn-on and (b) cell-1 held-off high-side gate voltage. The revised operating-board drive uses a 20 nH lumped gate branch, 3 Ω turn-on resistance, 1 Ω turn-off resistance, and −1 V bias. Its zero-bias reference uses zero external turn-off resistance. DPT curves use the extracted gate network with individual 0.5 Ω gate resistors and −1.9 V bias; legend turn-on values are effective per-device resistances. Grey lines denote the 90 V drain-voltage target and the 0.8 V minimum gate threshold.')
put(95,'The routed power-network results support a compact commutation path, while the gate-network results show why that result alone is insufficient. The operating-board gate model remains an assumed network, and the extracted-network DPT case still requires refinement to meet the drain-voltage target. Shorter shared gate paths and driver outputs closer to each pair are the next layout objectives. Symmetry and absolute loop impedance must be addressed together.')
put(96,'The initial gate-loop range makes the loss and voltage assessment realistic before layout, while extraction checks the network topology that those scalar values cannot represent. Updated switching energies from the accepted routed configuration must feed back into the loss and thermal estimates. The operating-board gate network must also be extracted before its final margin is established. This feedback links the physical building block to the SPB voltage choice: the usefulness of low-voltage devices depends on the achievable power and gate paths at the required traction current.')
put(106,'A hardware-constrained design procedure has been presented for a phase-leg building block of an SPB traction inverter. Charge-based screening selects the 100 V EPC2361. Switching maps with representative gate- and power-loop inductances and an electrothermal comparison identify four parallel devices as the smallest tested count passing the peak-current screen for a compact commutation path. Current-sharing sensitivity motivates symmetric transistor pairs, paired gate drive, and dedicated Kelvin returns. Low-current resonance remains a separate drive-optimization requirement.')
put(107,'The routed-network assessment shows why device selection and voltage partitioning cannot be finalized independently of implementation. A compact power loop is achievable in the evaluated geometry, but gate-network topology and drive settings determine the remaining voltage and gate-disturbance margins. The extracted DPT case remains above the voltage target and requires further refinement, followed by updated loss estimates and experimental correlation. The contribution is the traceable connection between SPB voltage choice and the switching constraints that determine the practical use of low-voltage devices at traction-current levels.')

# Refresh the parallel-count table from the new current-dependent energy maps.
table=doc.tables[1]
for row in list(table.rows)[1:]:table._tbl.remove(row._tr)
headers=['Gate loop (nH)','Parallel count n','Leg loss (W)','Junction temperature (°C)','Peak VDS at 0.5 nH (V)','Peak VDS at 1 nH (V)']
for c,t in zip(table.rows[0].cells,headers):c.text=t
for g in [10,20]:
 for a,b in zip(D['parallel'][f'g{g}_p0.5'][:5],D['parallel'][f'g{g}_p1'][:5]):
  row=table.add_row()
  vals=[str(g),str(a['n']),f"{a['tot']:.1f}",f"{a['tj']:.0f}" if a['thermal_valid'] else '>150',f"{a['vpk']:.0f}",f"{b['vpk']:.0f}"]
  for c,t in zip(row.cells,vals):c.text=t

# Recreate the routed-network table in the order used by the new comparison figure.
table=doc.tables[2]
for row in list(table.rows)[1:]:table._tbl.remove(row._tr)
for c,t in zip(table.rows[0].cells,['Board / gate model','Rg,on / Rg,off (Ω)','Off bias (V)','Peak VDS (V)','Mean Eon per device (µJ)','Minimum VGS (V)']):c.text=t
cases=[('board_load_g10_on3_revised_drive','Operating / 10 nH','3 / 1',-1),('board_load_g20_on3_revised_drive','Operating / 20 nH','3 / 1',-1),('board_load_g20_on3','Operating / 20 nH','3 / 0',0),('board_dpt_g10_on3.5','DPT / 10 nH','3.5 / 0',-1.9),('board_dpt_g20_on3.5','DPT / 20 nH','3.5 / 0',-1.9),('board_extracted_g0_on2.5','DPT / extracted','2.5 / 0.5',-1.9),('board_extracted_g0_on3.5','DPT / extracted','3.5 / 0.5',-1.9)]
for key,label,res,bias in cases:
 r=D['boards'][key]
 vals=[label,res,f'{bias:g}',f"{max(r[f'vhpk{k}'] for k in range(1,5)):.0f}",f"{sum(r[f'eon{k}'] for k in range(1,5))/4e-6:.1f}",f"{min(min(r[f'glmin{k}'],r[f'ghmin{k}']) for k in range(1,5)):.1f}"]
 for c,t in zip(table.add_row().cells,vals):c.text=t

# Gate-voltage extrema are taken from the newly executed extracted-network case.
r=D['boards']['board_extracted_g0_on3.5']
mx=max(r[f'bump{k}'] for k in range(1,5));mn=min(min(r[f'glmin{k}'],r[f'ghmin{k}']) for k in range(1,5))
put(93,f'The extracted-network DPT case with the larger turn-on resistance has a maximum held-off gate excursion of approximately {mx:.1f} V and a minimum gate voltage of approximately {mn:.1f} V across the saved transitions and cells. Both positive and negative gate excursions must be checked against the device ratings of −4 V and +6 V [10]. These waveform checks remain conditional on the modeled network and do not replace experimental correlation.')

# Replace only the three numerical figures affected by the rerun.
for i,name in [(38,'single_cell_characterization'),(46,'parallel_count_selection'),(91,'extracted_network_switching')]:
 q=ps[i];inline=q._p.xpath('.//wp:inline')[0];rid=inline.xpath('.//a:blip')[0].get(qn('r:embed'))
 path=A/(name+'.png');doc.part.related_parts[rid]._blob=path.read_bytes()
 ext=inline.find(qn('wp:extent'));cx=int(ext.get('cx'))
 with Image.open(path) as image:cy=round(cx*image.height/image.width)
 ext.set('cy',str(cy))
 for e in inline.xpath('.//a:xfrm/a:ext'):e.set('cy',str(cy))

# Keep the previously audited bibliography and citation balance.
refdoc=Document(P/'SPB_ICPE_digest_expanded_citation_checked_2026-10-29.docx')
refs=[q.text for q in refdoc.paragraphs if re.match(r'^\[\d+\]',q.text)]
mapping={1:1,3:2,4:3,5:4,6:5,7:6,8:7,9:8,10:9,11:10}
for q in doc.paragraphs[:109]:
 for r in q.runs:
  value=r.text.replace('[2], [3]','[3]')
  value=re.sub(r'\[(\d+)\]',lambda m:'['+str(mapping.get(int(m[1]),int(m[1])))+']',value)
  if value!=r.text:r.text=value
for q,t in zip(ps[109:119],refs):q.clear();q.add_run(t)
ps[119]._element.getparent().remove(ps[119]._element)

# Restore typographic subscripts in newly written prose while preserving equations.
symbols={'VDS':('V','DS'),'VGS':('V','GS'),'Coss':('C','oss'),'Eon':('E','on'),'Rg,on':('R','g,on'),'Rg,off':('R','g,off')}
pattern=re.compile(r'(?<![A-Za-z])('+'|'.join(re.escape(k) for k in symbols)+r')(?![A-Za-z])')
allpars=list(doc.paragraphs)+[q for t in doc.tables for row in t.rows for c in row.cells for q in c.paragraphs]
from docx.shared import Pt
for table in doc.tables:
 for j,row in enumerate(table.rows):
  for cell in row.cells:
   for q in cell.paragraphs:
    q.paragraph_format.first_line_indent=Pt(0)
    q.paragraph_format.space_before=Pt(0);q.paragraph_format.space_after=Pt(0)
    q.paragraph_format.line_spacing=1
    q.paragraph_format.keep_with_next=j<len(table.rows)-1
    if j==0:
     for r in q.runs:r.bold=True
for q in allpars:
 if q._p.xpath('.//m:oMath | .//w:drawing'):continue
 for rr in list(q.runs):
  value=rr.text
  if not pattern.search(value):continue
  base=deepcopy(rr._r.rPr) if rr._r.rPr is not None else None
  pos=0;chunks=[]
  for m in pattern.finditer(value):chunks.extend([(value[pos:m.start()],False,False),(symbols[m[0]][0],False,True),(symbols[m[0]][1],True,False)]);pos=m.end()
  chunks.append((value[pos:],False,False))
  for val,sub,ital in chunks:
   if not val:continue
   run=OxmlElement('w:r');rp=deepcopy(base) if base is not None else OxmlElement('w:rPr');run.append(rp)
   if sub:z=OxmlElement('w:vertAlign');z.set(qn('w:val'),'subscript');rp.append(z)
   if ital:rp.append(OxmlElement('w:i'))
   z=OxmlElement('w:t');z.set(qn('xml:space'),'preserve');z.text=val;run.append(z);rr._r.addprevious(run)
  rr._r.getparent().remove(rr._r)

assert not any('1.7' in q.text or '1.7' in q._p.xml for q in allpars)
doc.save(OUT)
(A/'artifact.md').write_text('Full manuscript updated using completed LTspice reruns. All source headings, native equations, topology/gate-layout/PCB/Q3D/workflow figures retained. Figures 3, 4, 9 replaced by rerun plots; Tables II and III refreshed. Gate range 10/20 nH, realistic damped preliminary drive, both switching-transition voltage peaks checked. Reference balance 2/10 or 2/8 scholarly works. Prior documents preserved. Nominal model temperature 27 C; conduction-only thermal update. All numerical results traceable to saved netlists, RAW waveforms, and JSON/CSV analysis. Visual QA via Word PDF export and Poppler because bundled LibreOffice is unavailable.',encoding='utf-8')
print(OUT)

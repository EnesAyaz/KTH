"""Revise the manuscript around the deck's sequential engineering decisions."""
from pathlib import Path
import re

source=Path(__file__).with_name('create_icpe_coherent_revision.py').read_text(encoding='utf8')
source=source.replace('coherent_revision_assets','realistic_flow_assets')
source=source.replace('SPB_BB_ICPE2027_coherent_revision_2026-10-23.docx','SPB_BB_ICPE2027_realistic_design_flow_2026-10-23.docx')

# Shift existing figure/table references once, before inserting the new content.
source=re.sub(r'Fig\. ([345])',lambda m:'Fig. '+str(int(m.group(1))+1),source)
source=re.sub(r'Table (III|II)\b',lambda m:'Table '+{'II':'III','III':'IV'}[m.group(1)],source)
source=source.replace('prefix=shared.split("topic=p(",1)[0]', 'prefix=shared.split("topic=p(",1)[0]\nprefix=prefix.replace("Configurations in Table III","Configurations in Table IV")')
source=source.replace("tab('II','Sensitivity", "tab('III','Sensitivity")
source=source.replace("tab('III','Extracted", "tab('IV','Extracted")
for old,new in [
 ('III. Translating the Parallel Count into a Gate Drive and Cell Layout','IV. Translating the Parallel Count into a Gate Drive and Cell Layout'),
 ('IV. Closing the Design Loop with the Routed Building Block','V. Closing the Design Loop with the Routed Building Block'),
 ('V. Switching Results and Feedback to the SPB Design','VI. Switching Results and Feedback to the SPB Design'),
 ('VI. Importance for SPB Traction Optimization and Experimental Validation','VII. Implications for SPB Traction Optimization and Experimental Validation'),
 ('VII. Conclusion','VIII. Conclusion')]:source=source.replace(old,new)

graphics=r'''
# Device screening is separate from the subsequent single-cell and n sweep.
c=canvas.Canvas(str(A/'device_voltage.pdf'),pagesize=(W,167))
t=axes(c,(38,40,155,105),(.5,4.5),(0,8),[1,2,3,4],[0,2,4,6,8],'Voltage class (V)','D-FoM (ps)')
for i,v in enumerate([1.35,4.14,6.88,4.90],1):
 x0,y0=t(i-.26,0);x1,y1=t(i+.26,v);c.setFillColor(TEAL);c.rect(x0,y0,x1-x0,y1-y0,stroke=0,fill=1)
 text(c,*t(i,v+.2),f'{v:.2f}',align='center')
for i,st in enumerate(['100','200','350','650'],1):
 xx,_=t(i,0);c.setFillColor('white');c.rect(xx-8,23,17,11,stroke=0,fill=1);text(c,xx,27,st,align='center')
text(c,115,5,'(a)',align='center')
t=axes(c,(276,40,166,105),(11,21),(50,110),[12,14,16,18,20],[50,70,90,110],'Number of submodules N','Submodule voltage (V)')
line(c,[t(n,1200/n) for n in range(12,21)],INK)
line(c,[t(11,75),t(21,75)],GREY,[1,2],.6)
for n in [12,14,16,18,20]:
 x,y=t(n,1200/n);c.setFillColor(TEAL if n==16 else INK);c.circle(x,y,2,stroke=0,fill=1)
text(c,*t(16.5,79),'Candidate',col=TEAL)
text(c,359,5,'(b)',align='center')
finish(c,'device_voltage')

c=canvas.Canvas(str(A/'cell_parallel.pdf'),pagesize=(W,174))
t=axes(c,(37,41,155,110),(30,130),(75,145),[40,60,80,100,120],[80,100,120,140],'Single-cell current (A)','Peak drain voltage (V)')
for key,col,dash in [('0.5nH',INK,[]),('1nH',WINE,[4,2])]:
 pairs=[(i,v) for i,v in zip(rf['single'][key]['I'],rf['single'][key]['vpk']) if 30<i<130]
 line(c,[t(i,v) for i,v in pairs],col,dash)
 for i,v in pairs:
  x,y=t(i,v);c.setFillColor(col);c.circle(x,y,1.7,stroke=0,fill=1)
line(c,[t(30,90),t(130,90)],GREY,[1,2],.6)
text(c,50,148,'0.5 nH: solid; 1 nH: dashed')
text(c,115,6,'(a)',align='center')
t=axes(c,(277,41,165,110),(2,8),(0,45),[2,3,4,5,6,7,8],[0,15,30,45],'Transistors per switch n','Leg semiconductor loss (W)')
nr=[v for v in rf['npar']['0.5nH'] if v['n']>=2]
line(c,[t(v['n'],v['tot']) for v in nr],TEAL)
line(c,[t(v['n'],v['cond']) for v in nr],INK,[4,2])
text(c,335,138,'Total',col=TEAL);text(c,335,126,'Conduction')
x,y=t(4,next(v['tot'] for v in nr if v['n']==4));c.setFillColor(TEAL);c.circle(x,y,2.2,stroke=0,fill=1)
text(c,359,6,'(b)',align='center')
finish(c,'cell_parallel')

# The first pass is sequential. Extraction supplies the refinement loop.
c=canvas.Canvas(str(A/'workflow.pdf'),pagesize=(W,302))
steps=[
 (5,247,['1  Traction specification','Derive phase current']),
 (5,181,['2  Device and voltage screen','Select EPC2361; candidate Vm and N']),
 (5,115,['3  Single-cell DPT model','Current range and switching-energy map']),
 (5,49,['4  Compare parallel counts','Loss, temperature and drain-voltage margin']),
 (258,247,['5  Switching frequency and dc link','Ripple, effective capacitance and bypass']),
 (258,181,['6  Paired drive and KiCad layout','Symmetric cells and Kelvin returns']),
 (258,115,['7  Q3D extraction and LTspice','Verify power and gate networks']),
 (258,49,['8  Instrumented DPT board','Experimental correlation in the full paper'])]
for x,y,ls in steps:box(x,y,190,43,ls)
for x in [100,353]:
 for a,b in [(247,224),(181,158),(115,92)]:arrow((x,a),(x,b))
line(c,[(195,70),(227,70),(227,269)]);arrow((227,269),(258,269))
line(c,[(448,136),(452,136),(452,202)]);arrow((452,202),(448,202))
text(c,W/2,26,'Extraction refines the gate settings and layout; insufficient margin returns to Vm or n.',align='center')
text(c,W/2,11,'The initial parallel count is selected from the single-cell study before detailed layout extraction.',align='center')
finish(c,'workflow')
'''
main_start=source.index("\ntopic=p(")
source=source[:main_start]+graphics+'\n'+source[main_start:]

new_selection=r'''
h('II. Traction Requirements and the Initial Device and Voltage Choice')
sub('A. Phase current before the device count')
p('Fig. 1 relates the SPB voltage partition to the phase-leg building block. With N equally loaded submodules, the nominal submodule voltage is Vm = Vdc/N, where Vdc is the total dc-link voltage. Each submodule supplies one three-phase winding set. For sinusoidal phase current, the active power is')
eq('P = 3 M Vdc Iph,rms cos φ / (2√2).',1)
p('Here, P is the total active power, M is the modulation index, Iph,rms is the phase rms current, and φ is the displacement angle. The phase-current requirement follows from (1) before selecting the semiconductor or the parallel count. Increasing N lowers the voltage across a bridge but does not reduce this current. The device selection must therefore provide a high-current switch at the chosen submodule voltage.')
fig('architecture','Fig. 1. SPB voltage partition and building-block hierarchy. Series-connected dc inputs distribute the traction voltage among N three-phase submodules. Each submodule supplies an isolated winding set. Each phase leg uses n parallel transistors per switch to carry the required phase current. The parallel count is an implementation choice, whereas N also determines the converter voltage partition.')
p('Table I gives the drive specification and the provisional voltage partition used for the switching study. The latter is a candidate to be tested, not a conclusion that the selected device can already withstand all commutation events.')
tab('I','Drive specification and candidate voltage partition',['Parameter','Value','Parameter','Value'],[
['Vdc / P','1200 V / 300 kW','Switching frequency','50 kHz'],['M / cos φ','1.15 / 0.90','Phase rms / peak current','228 A / 322 A'],['Candidate N / Vm','16 / 75 V','Drain-voltage target','90 V'],['Junction-temperature limit','125 °C','Ambient temperature','40 °C']], [3.3,3.1,5.5,4.1])

sub('B. Voltage class and device screening')
p('For n parallel transistors per switch, stack conduction loss scales with N Iph,rms² RDS(on)/n, while output-charge loss scales with N n fsw Coss,tr Vm². The on-resistance is RDS(on), fsw is the switching frequency, and Coss,tr = Qoss/Vtest is the charge-equivalent output capacitance obtained from datasheet charge Qoss at test voltage Vtest. Defining the device figure of merit (D-FoM) as RDS(on) Coss,tr, minimization of this simplified sum over a continuous parallel count gives')
eq('Pmin ∝ Vdc Iph,rms √(fsw D-FoM),    D-FoM = RDS(on) Coss,tr.',2)
p('This screening step compares device technologies at the stack level before committing to an integer device count. Fig. 2(a) shows the best surveyed candidate in each voltage class: EPC2361, EPC2215, EPC2050, and IGT65R140D2, respectively. EPC2361 gives the lowest D-FoM in the surveyed set and includes a Kelvin source connection [9]. It is selected for the single-cell switching study. Typical room-temperature on-resistance and charge-equivalent capacitance at the respective datasheet test voltages are used; temperature dependence and nonlinear switching behavior are evaluated subsequently.')
fig('device_voltage','Fig. 2. Initial device and voltage-partition screens. (a) Minimum surveyed D-FoM in each voltage class. (b) Submodule voltage for a fixed traction dc bus; the highlighted point is the provisional partition in Table I. The grey dotted line marks the candidate submodule voltage. Neither screen establishes the final switching margin.')

sub('C. A candidate voltage with an explicit inductance target')
p('The candidate submodule voltage is chosen with switching headroom, rather than by applying a fixed fraction of the device rating alone. The peak drain-to-source voltage VDS,pk is screened using VDS,pk ≈ Vm + Lloop |di/dt|, where Lloop and di/dt refer to the inductance and current slew rate of the same cell path. A compact loop of 0.5 nH is used as the initial layout target, with 1 nH as a pessimistic comparison. The candidate partition is retained as a practical starting point that avoids adding further complete submodules.')
p('The analytical screen is not a proof of compliance. For example, the gate-charge estimate around 80 A per device gives a submodule ceiling near 73 V at the smaller assumed inductance, slightly below the candidate voltage. The difference makes switching speed an explicit design variable. Detailed single-cell simulation must therefore determine the usable current range, and the routed-board model must ultimately confirm or revise the voltage and drive choice. Even N is retained for the intended symmetric winding arrangement; it is not a general requirement of every SPB implementation.')

h('III. Single Cell Characterization and Selection of the Parallel Count')
sub('A. A single-cell model establishes the current scale')
p('One EPC2361 is first modeled in each position of a half bridge at the candidate submodule voltage. This model uses the selected driver output impedances, a preliminary 1.7 nH gate loop, and 2 Ω turn-on resistance with a low-impedance turn-off path. The two assumed commutation inductances are evaluated over device current. Switching energies from these runs provide the loss map used in the parallel-count comparison. The model intentionally precedes the detailed multi-device layout, so the initial count can be selected without first building and extracting every candidate board.')
p('Fig. 3(a) shows the resulting voltage stress. The compact-loop case supports operation in the vicinity of 80 A per device, whereas a higher device current loses the intended margin. This establishes a useful current scale rather than a hard current rating. Dividing the required phase-current peak by that scale points to approximately four transistors per switch. The neighboring counts are then checked instead of accepting this division as sufficient justification.')
fig('cell_parallel','Fig. 3. Selection of the parallel count from single-cell data. (a) Simulated single-cell peak drain voltage for 0.5 nH (black solid) and 1 nH (wine dashed); markers denote simulated operating points and the grey dotted line is the voltage target. (b) Fundamental-period total semiconductor loss (teal solid) and conduction loss (black dashed) versus n at 0.5 nH, with the selected count marked. Losses use the design point in Table I and the preliminary drive model.')

sub('B. A short electrical and thermal comparison')
p('Table II compares the relevant parallel counts using equal phase current, switching frequency, and single-cell drive assumptions. Conduction loss is calculated with temperature-dependent on-resistance. Switching energies are averaged over the fundamental current waveform, and junction temperature and on-resistance are solved together. The thermal boundary uses the ambient and temperature limit in Table I, a 0.65 K/W heatsink for the complete leg, and a 7.6 K/W junction-to-heatsink path per device. The same per-device path is assumed for the count comparison.')
tab('II','Parallel-count comparison from the preliminary single-cell model',
 ['n','Peak current per device (A)','Leg loss (W)','Estimated Tj (°C)','Peak VDS at 0.5 / 1 nH (V)'],[
 ['2','161','39.5','141','131 / 180'],
 ['3','107','23.2','84','96 / 123'],
 ['4','80.5','18.0','69','83 / 93'],
 ['5','64.4','15.8','62','86 / 85'],
 ['6','53.7','14.8','59','86 / 84']], [0.7,3.8,2.4,3.4,5.7])
p('Two devices fail both the thermal and voltage screens. Three reduce temperature sufficiently but still exceed the drain-voltage target even with the compact loop. Four are the smallest tested count satisfying the preliminary electrical and thermal requirements in that case. Additional devices reduce loss further, as Fig. 3(b) shows, but are not needed to pass the initial screens. The choice of four is therefore the smallest adequate candidate under the stated assumptions, not the absolute minimum of semiconductor loss.')
p('This decision also has a straightforward implementation: four devices can be divided into two identical driver pairs. Pairing does not replace the electrical check; it provides a practical arrangement for the count already indicated by that check. The higher-inductance result remains outside the target for the selected count, so a low commutation inductance and controlled switching speed become requirements for the detailed board. Current sharing and gate-drive loading are evaluated next to determine whether the assumed single-device behavior can be retained when the devices operate together.')

sub('C. Switching frequency and local energy storage')
p('Before routing the cells, the switching frequency and capacitor arrangement establish the remaining local current paths. The study uses a design frequency of 50 kHz, balancing semiconductor loss against dc-link charge ripple and winding-current ripple. The final allowable frequency depends on the machine leakage inductance and operating point. The capacitor bank is sized for the three-phase submodule, because its three leg banks share the switching-frequency ripple through the common dc bus.')
p('A 3% peak-to-peak voltage-ripple target requires approximately 127 µF effective bank capacitance per leg board in the switching-function calculation. The selected bank uses twenty nominal 22 µF, 100 V multilayer ceramic capacitors, with their dc-bias derating included. A separate set of ten nominal 1 µF bypass capacitors per cell supplies the fast commutation edge. Bank charge capacity and local loop inductance are therefore addressed separately. These capacitor placements are carried into the routed geometry and the extracted switching model; detailed ripple-sharing and capacitor comparisons can be reported in the full paper.')
'''
start=source.index("h('II. From Traction Requirements")
end=source.index("h('IV. Translating the Parallel Count")
source=source[:start]+new_selection+'\n'+source[end:]

source=source.replace(
 "p('The selected driver provides 4 A source and 8 A sink capability per channel [10]. Dividing the transistors into pairs limits the gate charge presented to one output and keeps the routing local. A strong sink path is particularly important when the opposite switch commutates, because Miller current can raise the gate voltage of a transistor that should remain off. The sink-current rating is only one part of that path: shared inductance between the driver and the star point can still allow a substantial gate excursion.')",
 "p('The selected driver provides 4 A source and 8 A sink capability per channel [10]. The driver-loading study gives a quantitative reason to divide the selected count into pairs: driving four devices from one channel increases turn-on energy by approximately 31% relative to two, and the predicted sink-current demand exceeds the channel rating. One channel per device avoids the common gate-charge load but increases driver and supply count. One channel per pair is therefore the intermediate arrangement that retains a short, symmetric gate network without assigning all four gates to one output.')\np('A strong sink path is particularly important when the opposite switch commutates, because Miller current can raise the held-off gate voltage. The sink-current rating is only one part of that path. The common driver-to-star inductance must also be limited; it is checked by extraction after the branch geometry has been made symmetric.')")

skew=r'''
sub('C. Timing between the two driver pairs')
p('Pairing introduces a second sharing question: the two driver blocks must commutate together. Symmetry within one pair does not remove a delay between the blocks. For a delay Δt, a reduced model gives a current redistribution ΔI ≈ Vm Δt/Lx, where Lx is the inductance between the two pair switch nodes. The extracted load-board path predicts a low-side current change of order 14 A per nanosecond of skew in this model. The actual imbalance depends on the switching trajectory and the driver delays.')
p('Both blocks consequently use a common pulse-width modulation source and matched input paths. The DPT arrangement measures the individual cell currents and the gate voltages of both blocks, allowing the inter-pair timing to be checked. Timing mismatch remains a validation requirement; equal nominal gate branches alone are not presented as proof of robust four-device sharing.')
'''
at=source.index("h('V. Closing the Design Loop")
source=source[:at]+skew+'\n'+source[at:]

source=source.replace(
 "p('Fig. 4 shows how the hardware implementation feeds back into the SPB selection. The initial voltage class, N, and n define the current and voltage stress that each cell must support. KiCad establishes the component placement, current paths, and gate returns. Ansys Q3D extracts the resulting impedances, which are then inserted into LTspice switching simulations. Local violations lead to layout or drive changes. If those changes cannot recover the margin without an unacceptable loss penalty, the outer iteration returns to the submodule voltage or parallel count.')",
 "p('Fig. 4 summarizes the resulting sequence. The first pass selects the device and candidate submodule voltage, characterizes one cell, and compares a small number of parallel counts. The capacitor arrangement and paired gate drive then translate that candidate into a KiCad layout. Only at this stage are the routed power and gate networks extracted in Ansys Q3D and inserted into LTspice. Extraction verifies the initial assumptions and supplies the revision loop; it is not required to justify the first parallel-count estimate. A failed stress or sharing check first leads to gate-drive or layout changes, and returns to Vm or n if the required margin cannot be recovered locally.')")
source=source.replace(
 "fig('workflow','Fig. 4. Design iteration linking SPB voltage selection to physical implementation. R and L denote the extracted resistance and inductance, including mutual terms. Solid arrows denote hardware development and local revision. The dashed path denotes feedback to the voltage partition or parallel count when the required operating margin cannot be recovered locally. Experimental DPT correlation is planned for the full paper.')",
 "fig('workflow','Fig. 4. Sequential first-pass design and subsequent extraction-based refinement. A single-cell model supplies the current range and switching-energy data for the initial parallel-count comparison. Frequency, capacitance, and paired drive define the geometry to be routed. Extracted-network switching simulations then refine the layout and gate settings, with feedback to the candidate voltage or count if needed. DPT measurements are planned for the full paper.')")

# Isolate the effect of gate extraction at equal DPT resistance as in slide 47.
source=source.replace(
 "['Operating, lumped gate','0.41','3.0','86','32.8'],['DPT, extracted gate','0.65','2.5','105','24.3']",
 "['Operating, lumped gate','0.41','3.0','86','32.8'],['DPT, lumped gate','0.65','3.5','90','34.1'],['DPT, extracted gate','0.65','2.5','105','24.3']")
source=source.replace("'Mean Eon (µJ)'","'Mean Eon per device (µJ)'")
source=source.replace(
 "p('Increasing turn-on resistance reduces the drain stress of the operating-board power network, at the cost of higher turn-on energy. Including the extracted DPT gate network shows that the preliminary gate assumption is insufficient for the instrumented stage. The slower setting reduces its peak below the device blocking rating, but it still exceeds the design target in Table I. The result therefore distinguishes a useful hardware candidate from a fully closed voltage-margin design.')",
 "p('Table IV first shows the loss-versus-stress tradeoff when the operating-board turn-on resistance is increased. The DPT rows then isolate the importance of the gate model: at equal effective resistance, replacing the lumped gate loop by the extracted network raises the peak stress. The lower-resistance extracted case exceeds the device blocking rating, while the implemented slower setting brings the peak below that rating but not below the target in Table I. The initial choice of four devices remains supported, but the routed DPT board requires further voltage-margin refinement. These are distinct conclusions: selecting the parallel count is an initial sizing decision, whereas closing the switching margin requires the extracted network.')")

source=source.replace(
 'Loss and voltage-stress studies motivate four parallel transistors per switch and a candidate arrangement of sixteen submodules.',
 'Single-cell switching simulations establish a usable current range. A short comparison of loss, temperature, and drain stress then selects four parallel transistors per switch for a candidate arrangement of sixteen submodules.')
source=source.replace(
 'Its contribution is a linked design procedure that translates the traction specification into a voltage-class and parallel-count choice, derives the required symmetry and gate-drive arrangement from current-sharing sensitivity, and checks the resulting choice using extraction of the routed power and gate networks.',
 'Its contribution is a design sequence that turns the traction-current requirement into a single-cell switching study and a small parallel-count comparison, then translates the selected count into a paired gate drive and a routed board. Extraction of the power and gate networks closes the assumptions made during this first-pass sizing.')

source=source.replace('suffix=shared[shared.index("h(\'References\')"):]', 'suffix=shared[shared.index("h(\'References\')"):]\nsuffix=suffix.replace("\'Pmin\':(\'P\',\'min\')", "\'Pmin\':(\'P\',\'min\'),\'Tj\':(\'T\',\'j\'),\'Lx\':(\'L\',\'x\')")')
exec(compile(source,str(__file__),'exec'),globals())
# Keep the short selection and sensitivity comparisons intact in the expanded draft.
for table in doc.tables:
 for row in table.rows[:-1]:
  for cell in row.cells:
   for pp in cell.paragraphs:pp.paragraph_format.keep_with_next=True
doc.save(OUT)

# EPC2361 half-bridge module: detailed design and validation plan

**Objective:** select a buildable half bridge with 4, 5 or 6 EPC2361 devices per switch position that enables the highest practical switching frequency, preferably near 100 kHz, while the complete balanced three-phase inverter exceeds 99.5% efficiency and every junction remains below 125 C.

**Scope:** this is a staged engineering plan, not a claim that the current analytical model or drawings meet those requirements. The source papers are evidence and design references, not operating instructions. The working sequence is requirements -> device evidence -> architecture -> layout/extraction -> parallel switching model -> cycle losses/thermal iteration -> prototype validation.

## 1. Design basis and decisions to resolve first

| Item | Current basis | Required resolution |
|---|---|---|
| Device | EPC2361, supplied datasheet and vendor SPICE library | Freeze revision/model hash and package footprint |
| Module | One half bridge, 2N devices | Define module boundaries, terminals and available area |
| Parallel count | N = 4, 5, 6 per position | Select after electrical, thermal and manufacturing comparison |
| Operating point | 75 V DC link; 18.75 kW for three legs | Add minimum/maximum bus, ripple, regeneration and overload envelope |
| Fundamental modulation | Centered SVM, m=1.15, Vphase,pk=mVdc/2 | Confirm controller convention and minimum-pulse behavior |
| Frequency | 10-100 kHz, maximize feasible frequency | Treat 100 kHz as target, not an input that overrides constraints |
| Current | About 205 A RMS / 290 A peak at unity PF, before ripple | Obtain PF range, fundamental frequency range and ripple versus frequency |
| Efficiency | >99.5% for defined complete inverter boundary | Include copper, capacitors, gate supplies, sensing/control and auxiliaries consistently |
| Cooling | Water approximately 60 C | Clarify inlet versus local water; coolant mixture, flow, pressure drop and temperature tolerance |
| Junction | Instantaneous maximum below 125 C | Establish operating margin and thermal-model uncertainty |
| Gate drive | Start at 5 V ON / 0 V OFF | Select actual driver, supply architecture, timing and protection |
| Voltage screen | Present 90 V design ceiling on 100 V device | Reassess against maximum bus, component tolerances and measured overshoot |

At the stated point, ideal device peak currents for N=4/5/6 are 72.5/58.0/48.3 A. The present 60 A/device screen is a provisional engineering choice, not a datasheet absolute limit. Four devices must remain a comparison candidate until its permissible current and thermal envelope are justified.

The total loss budget is Pout*(1/eta-1): **94.22 W for three phases**, or **31.41 W per balanced half bridge**. Allocate this among conduction, switching, reverse conduction, gate power, copper, capacitor ESR and auxiliaries before optimizing. Reserve uncertainty and unmodeled-loss allowance explicitly; do not use a zero allowance as evidence of compliance.

**Deliverable:** a requirements table containing nominal, worst-case, transient and acceptance values. No fabrication release until these are resolved.

## 2. What to use from the supplied literature

The Tran et al. paper (JESTPE 2025, DOI 10.1109/JESTPE.2024.3477743) provides a useful process in Sections II-A and IV: PCB CAD -> ODB++/SIwave -> Q3D parasitics -> LTspice double pulses -> Icepak thermal analysis -> fabrication and experiments. Its distributed local capacitor boards, matched commutation paths, explicit mutual terms and symmetric gate fanout are transferable design ideas.

Its equation (11) includes mutual inductance and gives 1.14 nH from the reported partial-inductance matrix. The displayed arithmetic is consistent. Appendix B estimates about 1.175 nH from ringing with **one populated high/low device pair**. That is a useful cross-check for that geometry; it does not establish every dynamic mode of a fully populated bank. Probe capacitance, nonlinear Coss, capacitor mounting/ESL and common connections all affect the inferred value. The assumption ESL/N requires independent, similar capacitor branches and does not remove shared mounting inductance.

Do not copy the paper's GS61008P gate voltages, package thermal path or resistor values into EPC2361. Its bottom-cooled IMS/DBC hybrid solution differs from EPC2361's strong junction-to-top path and source-connected exposed top. Its reported laboratory operating points do not prove 75 V, 18.75 kW, 100 kHz and 99.5% operation for our design.

Also treat simple damping and Miller equations as initial estimates. In particular, damping ratio 0.707 is an underdamped design choice; mathematical critical damping is 1. Neither is a universal gate-resistance prescription for a nonlinear coupled GaN bank.

**Deliverable:** source-to-design decision log: which idea is adopted, why it applies, what must be re-derived, and how it will be verified.

## 3. Device characterization: establish trustworthy inputs

### 3.1 Static and capacitive behavior

- Verify symbol/subcircuit pin mapping, footprint pad numbering, package orientation and model temperature behavior against the supplied EPC2361 datasheet.
- Sweep Rds(on) at 25, 60, 90 and 125 C, with additional points where needed, and across the relevant branch-current range. Keep typical SPICE curves separate from maximum datasheet resistance and engineering derating.
- Check Vgs sensitivity around the selected 5 V supply tolerance. Characterize reverse conduction at 0 V gate and relevant current/temperature; include deadtime consequences.
- Inspect Coss(V), Qoss(V), Eoss(V), Cgd(V) and Qg. Use charge/energy-consistent quantities: energy-equivalent Coss is not the same as small-signal Coss used in ringing estimates.
- Document what the vendor model omits: package parasitics, thermal feedback, trapping/dynamic resistance, breakdown or other effects as applicable. Do not extrapolate its numerical behavior into an unsupported operating region.

### 3.2 Single-device DPT baseline

Retain the existing LTspice pipeline as the baseline. Expand only where needed to cover low current, both polarities/commutation directions and temperatures. Save raw traces and extraction definitions. Establish numerical convergence before interpreting energy differences smaller than numerical error.

**Deliverables:** DC curves, reverse-conduction curves, capacitance/charge comparison, model limitations, and a reproducible baseline report. **Exit criterion:** datasheet/model discrepancies are explained and the baseline energy measurement passes timestep and integration-window checks.

## 4. Choose electrical, mechanical and cooling architectures together

Compare the same three N values under two practical architectures:

**A. Multilayer PCB with top cold plate:** preferred baseline to investigate for EPC2361. Use repeated local upper/lower commutation cells, local high-frequency DC-link capacitors, close inner returns and electrically insulating top TIM. Assess routing access around the plate and screws, package coplanarity and assembly pressure.

**B. Hybrid power substrate/capacitor structure:** keep as an alternative if ordinary PCB copper, current distribution or thermal spreading becomes limiting. Adapt the paper's distributed-capacitor idea, but only after evaluating its effect on EPC2361 top cooling, connection inductance, assembly complexity and repairability.

Compare module footprint, branch length spread, capacitor volume, copper loss, gate routing, cooling area, fabrication cost and inspectability. Do not choose solely by nominal inductance.

**Deliverable:** architecture comparison with dimensioned placement concepts and a mechanical envelope. **Exit criterion:** select one primary architecture and one fallback with explicit reasons.

## 5. Gate driver and protection design

Use one high-side and one low-side driver channel per half bridge as the baseline, each driving its N-device bank. Each device receives local on/off resistor paths and a dedicated source-reference connection. Maintain close outgoing/return pairs; matching trace length alone is insufficient if loop areas and coupling differ.

- Calculate bank gate charge N*Qg, source/sink current versus gate voltage, output impedance, current limiting, supply droop and total driver dissipation. Qg/t is a preliminary charge-transfer check, not a complete switching-time model.
- Include driver propagation delays, high/low skew, minimum pulse width, deadtime, UVLO and startup/shutdown behavior. High-side drive requires a suitable floating supply/reference and common-mode transient capability.
- Evaluate bootstrap operation over the actual modulation range, including long high-side on-times; compare an isolated supply if required. Include isolation supply parasitic capacitance in common-mode analysis.
- Start at EPC2361's 5/0 V baseline. Consider negative bias only after proving that it is necessary and checking increased reverse loss and gate excursion margins.
- Sweep Ron and Roff separately. Keep shared driver impedance separate from per-device resistance. Do not parallel separate driver outputs.
- If one channel cannot drive six short, balanced paths adequately, compare two local channels driving three devices each. Include propagation-delay mismatch and worst-case current stealing explicitly.
- Design overcurrent response, shoot-through prevention and fault shutdown from available device fault capability. Do not assume a generic Si/SiC short-circuit withstand time for this GaN.

**Deliverables:** driver schematic/BOM, supply budget, timing diagram, protection sequence and candidate resistance ranges. **Exit criterion:** driver operating limits and timing margins are satisfied over modeled tolerances; resistor values remain provisional until extracted-layout DPT.

## 6. PCB layout variants and manufacturing constraints

Create separate N=4/5/6 layouts rather than stretching one row and assuming performance scales ideally.

1. Import the manufacturer's exact land pattern; verify pad mapping, solder mask/stencil requirements and assembly rules.
2. Place paired upper/lower devices and local MLCC groups. Keep the capacitor-to-switch commutation loop compact and its return directly adjacent in the stackup.
3. Size each capacitor group for effective capacitance under DC bias, voltage ripple, pulse current, ESR and ESL. Distinguish local high-frequency capacitors from bulk energy storage.
4. Design symmetric power feeds and phase takeoff so edge devices do not receive systematically shorter paths. Include actual terminal/connector geometry.
5. Route matched gate/return pairs, keep them away from the switch-node electric field, and minimize common-source coupling. Resolve gate-driver placement in real copper, not only connection diagrams.
6. Select a manufacturable stackup with documented copper thickness, layer separation, via geometry, clearance and tolerance. Coordinate with the fabricator before extraction.
7. Provide practical probe access with minimal added loop area. Include voltage measurement pads and a plan for branch-current instrumentation that does not dominate branch inductance.
8. Include cold-plate mounting, insulating TIM, controlled compression, keep-outs, creepage/clearance and mechanical support. Determine insulation requirements from actual working voltage and environment; do not copy a paper's tape thickness as an insulation specification.

**Deliverables:** native CAD, schematic, stackup, BOM, manufacturing drawings, ODB++ or equivalent geometry and revision tags. **Exit criterion:** schematic/PCB connectivity and manufacturing checks pass; every candidate has defined current-return paths.

## 7. Extract parasitics as a network

Use Q3D or another suitable validated field/PEEC extractor if available. Q3D can export resistance, partial-inductance and capacitance matrices as SPICE equivalents [S2]. Availability/licensing must be checked; none is assumed installed by this plan. If unavailable, geometry estimates plus measurement remain preliminary evidence, not a substitute labeled as field extraction.

- Start with a simple paired-copper geometry and reproduce the analytical L approximately equal to mu0*h*l/w result to verify units, terminals and current directions.
- Import actual copper, vias, terminals, capacitor pads and relevant mechanical conductors. Define extraction boundaries at component terminals so package/MLCC models are not counted twice.
- Extract DC resistance, frequency-dependent AC resistance/inductance, gate and common-source paths, mutual terms, and relevant switch-node-to-gate/cold-plate capacitance.
- Choose an extraction frequency band from switching rise/fall times and observed ringing, not merely the 100 kHz carrier. Examine a suitable range spanning MHz to hundreds of MHz as warranted by edge time; verify quasi-static validity and export-model bandwidth.
- Record port directions and reference conductors. Compute loop inductance using a consistent signed loop vector, Lloop = a^T L a. Keep the full network when branches share paths or couple strongly.
- Check mesh convergence, resistance sanity, matrix symmetry/passivity, signed mutual terms and reduction accuracy. Compare the exported network's impedance with the source model across the relevant band.
- Report each branch's self/common-source/gate path and mismatch, not just one attractive total L. Repeat for each N and stackup tolerance.

**Deliverables:** extraction project, port map, R/L/C matrices, circuit export, convergence plots and comparison table. **Proposed numerical review target:** key loop values change by less than roughly 5% with mesh refinement, and smaller if the design margin requires it; this is a project criterion, not a universal standard.

## 8. Actual parallel-bank LTspice DPT

Instantiate all 2N EPC2361 models. Include the actual driver source/sink behavior, individual Ron/Roff, extracted parasitic network, realistic local capacitors and the external DPT fixture. Package parasitics belong exactly once.

Use a staged sweep to avoid an unmanageable Cartesian grid:

| Stage | Sweep | Purpose |
|---|---|---|
| Nominal | N=4/5/6, 75 V, hot devices, low-to-rated current | Compare architecture and detect instability |
| Gate optimization | Coarse Ron/Roff grid, then refine useful regions | Find loss/stress tradeoff |
| Voltage/temperature | Include 50/75 V plus actual bus bounds; 25/60/90/125 C | Establish energy interpolation domain |
| Current | Cover zero to worst-case peak branch current, with dense transition-region points | Support sinusoidal averaging without extrapolation |
| Tolerances | Driver skew, Rds/Vth variation where supported, Rg tolerance, unequal branch L, capacitor variation | Find worst-device stress |
| Validation | Smaller timesteps, different windows and solver settings on critical cases | Quantify numerical uncertainty |

At each point record both devices' Vds/Vgs excursions, individual branch currents, current imbalance, Eon/Eoff per device, reverse loss, local driver supply behavior, and clearly defined dv/dt and di/dt metrics. Observe the complementary device as carefully as the actively switched one.

For energy, state whether the result is terminal energy or dissipated heat. Correct for conduction baseline and changes in stored capacitor/inductor energy. Keep negative reactive energy distinct from negative dissipation. Preserve heat dissipated in the complementary bank; do not simply assign all bank heat to one switch if thermal imbalance matters.

**Deliverables:** matched parallel-bank energy/stress maps with raw waveforms, metadata, model hashes and validity flags. **Exit criterion:** no unsupported extrapolation; all tested tolerance corners satisfy defined voltage/current/gate limits and numerical uncertainty is smaller than the available design margin.

## 9. Fundamental-cycle inverter averaging and optimization

Replace the current fixed-overlap assumption with the matched parallel-bank dataset. At each fundamental angle compute phase current, carrier ripple estimate, PWM duty, current direction and commutation type. Interpolate Eon/Eoff at that instantaneous operating point and integrate over the complete fundamental period.

Compute upper/lower conduction using actual duty and temperature-dependent resistance, deadtime reverse conduction with the selected OFF voltage, and switching-event count appropriate to continuous SVM or SPWM. Near zero current, identify soft or incomplete commutation instead of assuming every event is hard switching. If pulse suppression, discontinuous PWM or overmodulation is introduced, update event counts and duty rather than changing only a limit flag.

Add gate-drive supply loss, PCB/terminal I-squared-R loss, capacitor ESR loss, auxiliary power and output-filter losses if within the declared efficiency boundary. Report semiconductor-only and complete-boundary efficiency separately.

Optimize N, Ron, Roff, stackup/layout, deadtime and frequency together. Retain a tradeoff table rather than selecting the lowest switching energy alone. Highest feasible frequency must satisfy loss budget, electrical stress, current sharing, pulse timing, junction temperature, cooling and specified motor dv/dt/EMI limits.

**Special issue:** SVM m=1.15 has very short zero-vector intervals. Resolve the present 67 kHz timing screen with the actual controller before claiming 100 kHz. SPWM m=0.99 is not an equivalent-output-voltage comparison; for fair PWM comparison use a common achievable fundamental voltage, or explicitly report the different operating points.

**Deliverables:** loss breakdown versus frequency, highest feasible frequency per design, remaining uncertainty budget and traceable selection. **Exit criterion:** the worst-case complete loss plus its uncertainty remains below 94.22 W at the stated rated point.

## 10. Thermal, hydraulic and mechanical modelling

### Level 1: resistance budget

Use per-device power from cycle averaging. Start with Rtim = t/(kA) + Rcontact and Tj = Twater + Pleg*Rplate + Pdevice*(Rjc+Rtim). For a shared three-phase plate use all relevant heat. Datasheet Rjc, package spreading, effective contact area and contact pressure need consistent definitions; do not double-count package thermal resistance inside a detailed package model.

### Level 2: three-dimensional steady state

Build the actual package/PCB/TIM/plate geometry in Icepak, an available thermal FEA/CFD tool or an equivalent validated workflow. Apply unequal per-device heat, material properties versus temperature where relevant, TIM contact/compression and real coolant conditions. Include the PCB thermal path and thermal coupling between devices. Do not substitute a generic heat-transfer coefficient for a validated cold-plate model without documenting its origin.

### Level 3: transient and electrothermal iteration

Extract a coupled thermal resistance/impedance network from unit-power responses. Iterate electrical losses and temperature until stable. Use the fundamental frequency and load profile to calculate junction ripple, startup and overload peaks. Include local coolant warming, flow tolerance and the hottest downstream device. Require peak, not just mean, Tj below 125 C with agreed margin.

Estimate coolant temperature rise using Q/(mass-flow*cp), then verify pressure drop and pump operating point. Check assembly preload, board bending, source-top insulation, TIM aging and thickness tolerance. Thermal maxima for TIM and plate are conditional tradeoffs, not independently available allowances.

**Deliverables:** temperature maps, hottest-device identification, thermal impedance network, required TIM/plate specifications, flow/pressure requirements and tolerance cases. **Exit criterion:** peak junction and all material/component temperatures pass at worst specified cooling and load conditions.

## 11. Prototype release and laboratory correlation

Fabricate one selected half bridge and useful measurement coupons before committing to a three-phase build. Review the schematic, layout, extraction model, fabrication stackup, reflow/assembly process, probe access and cooling fixture together.

Bring-up sequence: unpowered inspection and continuity -> driver supplies and timing -> low-voltage, energy-limited DPT -> progressively higher current/voltage -> thermal steady-state half-bridge testing -> three-phase sinusoidal load/motor operation. Use suitable laboratory equipment and qualified personnel for stored-energy and fault tests; this plan does not authorize unattended hardware energization.

Measure Vds/Vgs with adequate bandwidth and low parasitic connections; deskew voltage/current channels before switching-energy integration. Account for probe capacitance and current-sensor insertion inductance. Use ringing only as a cross-check with known effective capacitance and identified mode. Measure device sharing directly where practical; similar surface temperatures alone do not establish equal transient current.

Correlate extracted and measured impedance/ringing, switching energies, temperatures and losses. At 99.5% efficiency, the loss is small relative to transferred power: document the power-analyzer uncertainty and use calorimetric/cooling power measurements as an independent check where practical. Include coolant flow and inlet/outlet temperature uncertainty in calorimetry.

**Deliverables:** instrument/calibration log, measured waveforms, uncertainty budget, model-versus-measurement comparison and revised model. **Exit criterion:** discrepancies are explained and the combined uncertainty is small enough to substantiate the efficiency and thermal margins.

## 12. Practical milestones and work order

| Milestone | Output | Dependency |
|---|---|---|
| M0 | Requirements and efficiency boundary frozen | User/system inputs |
| M1 | Device model and single-device evidence reviewed | M0 |
| M2 | Driver and 4/5/6 dimensioned architectures | M1, fabrication/cooling constraints |
| M3 | Extracted RLC networks and candidate layouts | M2, CAD and extraction tools |
| M4 | Parallel-bank energy/stress lookup maps | M3 |
| M5 | Coupled sinusoidal-loss and transient thermal optimization | M4, thermal geometry and operating profile |
| M6 | Prototype release package | M5 plus independent design review |
| M7 | Correlated half-bridge and three-phase measurements | M6 and laboratory capability |
| M8 | Final frequency/N/Rg/cooling specification with margins | M7 |

Do not assign calendar commitments until CAD licenses, fabrication lead times, cold-plate supply and laboratory access are known. M1 baseline characterization and M2 mechanical/driver planning can overlap. Final M4 must use M3 parasitics; final M5 must use characterized M4 losses.

## 13. Workspace implementation and immediate priorities

Keep the existing focused project. Do not add alternative scripts for the same task without replacing or integrating their functionality.

- data/inputs/design.json: design and operating envelope; extend with actual bus bounds, fundamental frequency, PF/ripple and uncertainty.
- data/devices and data/spice: versioned source evidence and vendor models.
- models/half_bridge.py: cycle integration, later extended with validated energy interpolation and electrothermal coupling.
- Existing DPT scripts: baseline measurement routines to reuse when adding a true parallel-bank netlist.
- Proposed cad/, extraction/ and thermal/ folders: add when real CAD or solver projects exist, not as empty clutter.
- results/: each generated study stores inputs, hashes, units, tool version and validity domain alongside results.
- reports/: maintain separate characterization and design reports; this plan is the master roadmap.

**Next five actions:** (1) resolve the operating envelope and controller pulse timing; (2) verify available CAD/extraction/thermal tools; (3) specify the driver and cold-plate/TIM mechanical envelope; (4) develop dimensioned 4/5/6 layouts with real stackup; (5) extract their networks and replace the analytical switching placeholder with actual parallel-bank DPT maps.

## Sources

[S1] Supplied Tran et al. paper, A High-Performance GaN Power Module With Parallel Packaging for High-Current and Low-Voltage Traction Inverter Applications, JESTPE 13(1), 1188-1209, February 2025, DOI https://doi.org/10.1109/JESTPE.2024.3477743. Relevant: Sections II-A, III, IV and Appendix B. Different device/package; adopted for methodology.

[S2] Ansys Q3D documentation, extraction matrices and SPICE equivalents: https://ansyshelp.ansys.com/public/Views/Secured/Electronics/v251/en/Subsystems/Q3DExtractor/Content/Variables/GettingStartedwithQ3DExtractor.htm

[S3] Supplied EPC2361 datasheet, revision 2.4, 20 July 2026, data/datasheets/EPC2361_datasheet.pdf. Local supplied revision controls device limits. Online reference: https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2361_datasheet.pdf

[S4] Supplied EPC9186 guide and Cooke/Rogers paper; prior discussion and geometry limitations are retained in reports/cooke_rogers_inductance_review.md. Their numerical values are not substituted for our geometry or device characteristics.

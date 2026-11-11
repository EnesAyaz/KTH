# Research plan and evidence

## 1. Proposed contribution and scope
The paper should answer: when low-voltage SPB modules are already required by a high-voltage drive, which module phase number and winding/pole combination permit useful pole changing without stator reconnection, and what energy storage and machine penalties remain?

Recommended core: a constrained feasibility map and two worked designs. Keep synchronous pole changing as a distinct rotor-feasibility gate. Use an IM as the initial validation vehicle because the cage adapts to the stator poles. A synchronous extension requires an explicit reconfigurable field or hybrid rotor and its excitation hardware, losses and reversal dynamics. Do not generalize fixed-pole PMSM behaviour to every synchronous rotor.

Novelty remains provisional. Existing project reviews identify vector-space decomposition as prior art underlying the cross-power identity. Novelty must lie in SPB-specific sizing consequences, matched designs and validation, not claiming a newly discovered orthogonality theorem.

## 2. Candidate matrix
Here m is phases PER MODULE, N is series DC modules, Q is the slot/coil-position count of the project winding model, P is total poles and p=P/2. For the particular interleaved spaced winding, c=Q/(mN) is an integer. Its full-distribution-factor screen requires c dividing p, m not dividing p/c, and m not dividing 2p/c for constant single-mode cell power. This is a sufficient construction-specific screen, not an impossibility theorem for all windings.

For c=1, simultaneous spatial orders a,b have a potentially nonzero cell cross-power term if m divides a+b or a-b. Sequence and temporal frequencies determine which term appears; equal temporal frequencies can produce average imbalance. Cancellation of the ideal term does not guarantee zero nonlinear residual.

| Case | m | Total poles | Spatial orders | Ideal cross-power screen | Status |
|---|---:|---|---|---|---|
| A (requested) | 3 | 4/2 | 2,1 | 2+1=3: coupling allowed | Candidate; winding factors and torque maps not computed |
| B (requested) | 5 | 6/2 | 3,1 | 3+1=4 and 3-1=2: neither divisible by 5 | Candidate; rotor and winding design not established |
| C (control) | 5 | 4/2 | 2,1 | 3 and 1: neither divisible by 5 | Separates phase-count effect from pole ratio |
| D (negative control) | 3 | 6/2 | 3,1 | p=3 violates this winding's isolated-neutral screen | Reject this construction; do not declare all 6/2 drives impossible |
| E (existing anchor) | 3 vs 5 | 8/4 | 4,2 | m=3 couples; m=5 cancels ideal terms | Existing Q48/Q80 nonlinear MEC evidence |

With N=16 and c=1, m=3 gives Q48 and m=5 Q80. These have different slot geometries: equal per-unit loading is not proof of equal manufacturing cost or equal optimized performance. For a final comparison fix active dimensions, copper temperature/current density, thermal budget, torque-speed duty, bus range, allowed ripple and device voltage margins. Allow integer N, Q and coil pitch to vary; optimize each baseline fairly. Compare same-pole-ratio controls before crediting phase count.

## 3. Evidence register (read-only source paths relative to project root)
| Source | What it supports | Limitation |
|---|---|---|
| `02_analytics/results/screen_H01_R01.json`, field `rule`, `rule_check` | Construction-specific winding rule; 1221 enumeration agreements | Analytical enumeration, not FEA/manufacturing validation |
| `03_simulation/confirm_H10.md` and `03_simulation/results/confirm_H10_mec_Q48.json`, `confirm_H10_mec_Q80.json` | Independently formulated nonlinear MEC replay and linearized cell-energy model for existing 8/4 case | Not independent experimental validation; Q48/Q80 differ |
| `02_analytics/results/screen_H11_R01.json` | Analytical capacitor/scheduling alternatives | Naive crossfade differs from MEC schedules; do not average their results |
| `03_simulation/reconcile_R01.md`, `data/machine_geometry.json` | Geometry, corrected leakage, WRSM air gap/field dynamics | Shared assumptions and no FEA; older headline results superseded where corrected |
| `06_reviews/H11_review.md` | Novelty objections and required cost comparison | Review predates subsequent confirm_H10 work; its missing-confirmation statement is stale |
| `board/hypotheses.md` | Research trajectory and rejected claims | Index/interpretation, not primary numerical evidence |

Existing anchor numbers, from confirm_H10 section 1: 16 cells, 1200 V stack, 75 V nominal cell, 2100 rpm, 8/4 poles, 350 kW current-limit basis (310 A rms). Flat-road m=3 peak pulsation 9244 W at 210 Hz, requiring 12.5 mF per cell for +/-10% ripple under the single-frequency linearized estimate. m=5 residual 7 W flat and 39 W on 2% grade, mainly at 350 Hz. These are NOT new 4/2 or 6/2 results, and not all are 300 kW runs.

The very large calculated ripple at 1 mF is an infeasibility indicator: the linearized model is invalid for large excursions and negative voltages are not physical predictions. Use nonlinear cell energy dynamics and device limits for final admissibility.

Counterexample that must remain visible: the best tested m=5 overlap retained 0.84 of requested torque on flat road and approximately -0.15 on 2% grade. Removing cell-power pulsation did not remove the voltage-limited torque dip. At 300 kW, the 0.25 ms H11s schedule had 0.178 s flat and 0.372 s grade intervals below 90% torque; grade reversal persisted. Do not use the earlier optimistic linear scheduling result as independently confirmed.

## 4. Reference paper
Provided PDF: C:/Github/OPT-Bipolar-Field-Excitation/Sources/On_the_Possibility_to_Achieve_a_Pole_Change_in_Synchronous_Motors.pdf
Conto and Bianchi, ECCE 2022, DOI https://doi.org/10.1109/ECCE50734.2022.9947754 . Eight pages extracted and reviewed as reference content.
Sections II-III explain dual-inverter stator current reversal and wound-rotor polarity changes; sections V-VI discuss specialized hybrid rotors and FEA/experimental investigation. Low-pole operation increases back-iron saturation. This establishes possibility for designed rotors, not guaranteed traction-cycle improvement, nor compatibility of an arbitrary PMSM with electronic pole changing. The 2022 experiments are the authors' results, not ours.

## 5. Reusable sibling material inspected
- `../Airgap Harmonics/MMF_trials.m`: available winding/MMF starting point; numerical output not audited in this pass.
- `../Drive Cycle/basic_vehicle_dynamics.m`, `drive_cycle.m`, `Gearbox.m`, `motor_torque_efficiency.m`: available vehicle/gear models; do not claim new cycle savings from their existence.
- `../Analytical Loss Calculations - GaN/LOSS_MODELING.md`: identified established loss-model source; integrate after checking input/device basis. No independent new converter-efficiency calculation performed here.
- `../VariablePolePaper/`: no files returned by the directory inspection; no result taken from it.

## 6. Corrections to the introduction
1. Megawatt charging motivates attention to higher-voltage vehicle architectures; charging power alone does not require a particular traction DC voltage. Separate heavy-duty vehicles from all passenger EVs.
2. Two-level switches block the full link plus transients. Voltage rating, switching loss, thermal design and EMI constrain switching frequency; do not claim efficiency/frequency cannot improve further.
3. NPC/flying-capacitor converters can reduce voltage steps and device stress. CMV depends on topology, grounding and modulation; lower phase-voltage steps do not guarantee lower bearing current.
4. Higher component count adds failure mechanisms but is not a reliability calculation. Multilevel and SPB systems can have fault-tolerant variants. SPB needs fault detection, isolation/bypass, post-fault voltage headroom and winding/control provisions; modularity alone is insufficient.
5. Vcell=Vdc/N is nominal, not the transistor rating. Check maximum battery voltage, imbalance, ripple and overshoot with derating before choosing GaN devices. Do not equate a 75 V operating point with adequate 75 V-rated switches.
6. Multiple inverter outputs provide controllability, not arbitrary pole counts. Isolated neutrals, winding factors, series-stack balance and rotor physics restrict the useful set.

## 7. Minimum publishable study without a manufactured motor
- Reproduce the winding rule by an independent winding-function calculation and show explicit coil/module/neutral maps for A-C.
- Derive signed-order cross-power terms with consistent peak/rms conventions. Validate with direct phase-domain sums.
- Use d(Cj Vj^2/2)/dt = Vj Istack - Pj, including losses consistently, alongside total-link constraints and a documented balancing controller. Integrate energy over finite transitions; the sinusoidal capacitance formula is only a screening estimate.
- Sweep N, m, Q, pitch, turns, yoke and, for WRSM, rotor excitation grouping. Reject designs for voltage, current, saturation, slot fill, insulation or thermal violations before ranking efficiency.
- Compare fixed-pole SPB optimized for the same duty, m=3 with added capacitance, and m=5 with added legs. Price/volume/lifetime inputs require verified sources and sensitivity bands.
- Compute torque-speed and loss maps. Add drive-cycle energy only after feasible maps and transition penalties exist; do not make a favorable cycle result a prerequisite for honesty.
- Obtain selected-point FEA or a documented cross-check against published data; report calibration and validation separately. A converter-only dual-frequency RL experiment is an optional strengthening step, not a motor prototype claim.
- Keep all scripts, generated outputs and figures inside this folder. Do not alter live review files or commit unrelated work.

## 8. Checked external references
- Official ICPE digest instructions: https://www.icpe-conf.org/main/au_digest.htm
- IEEE PELS open calls (historical deadline; current final deadline is 22 November 2026, confirmed by Enes on 9 November): https://www.ieee-pels.org/conferences/calls-for-conference-papers/
- CharIN ruggedized MCS white paper (distinguishes ordinary and ruggedized voltage ranges): https://www.charin.global/media/pages/technology/knowledge-base/c01eecf546-1730122175/whitepaper_ruggedized_megawatt_charging_system_1.3.pdf
- Primary converter comparison, Electronics 2024, 13(7), 1259: https://doi.org/10.3390/electronics13071259 . Supports treating SPB/FC loss and CMV benefits as design-dependent rather than automatic.
- Dynamic multi-agent dc-bus reconfiguration in modular motor drives with a stacked polyphase bridge converter: https://doi.org/10.1049/elp2.12376 . Prior art to check in full before fault-reconfiguration novelty claims.


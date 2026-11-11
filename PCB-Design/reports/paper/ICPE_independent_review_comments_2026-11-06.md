# Independent ICPE digest review comments

Reviewed on 6 November 2026. The supplied PDF and Word manuscript were not edited. Their SHA-256 hashes were recorded before review and checked again afterward.

## Review method and decisions

Three independent agents received no conversation history. Each reviewed only the final manuscript and its page images, from a different professional perspective. The coordinating review separately checked arithmetic, the existing simulation records and selected primary sources. These are simulated reviewer judgments, not actual conference decisions or an estimate of the probability of acceptance.

| Reviewer background | Recommendation | Confidence | Main reason |
|---|---|---|---|
| GaN switching, parasitic modeling and losses | Weak reject | High, 4/5 | Contradictory sensitivity conditions and insufficient model/operating-range evidence |
| Traction drives, modular converters and multiphase machines | Weak reject | High, 4/5 | Unclear quantitative novelty and incomplete connection between architecture and feasible implementation |
| Prototype validation and scientific presentation | Weak reject | High, 4/5 | Evidence does not yet support all interpretations; validation and uncertainty are underspecified |

All three regard the subject as relevant and the design progression as sensible. None rejects the digest solely because experiments are planned for the full paper. Their main concern is the reliability and sufficiency of the evidence already presented.

## Coordinating review — definite corrections before submission

### 1. The Fig. 5 conditions conflict with the prose

**Location:** p. 3, Section IV-A; p. 4, Fig. 5(a).

| Condition | Section IV-A | Fig. 5(a) | Existing simulation that produced the plotted values |
|---|---:|---:|---:|
| Power-loop mismatch for about 8% imbalance | 0.1 nH | 0.3 nH | 0.3 nH |
| Gate loops for about 56% imbalance | 10/15 nH | 10/20 nH | 10/20 nH |
| Source-inductance mismatch without Kelvin return for about 25% imbalance | 0.05 nH | 0.2 nH | 0.2 nH |
| Gate resistance in this sharing study | 3 ohms | Not stated | 2 ohms per device |

This is a result-to-condition mismatch, not a grammar issue. The three percentages correspond to the conditions in the final column. If the intended conditions are now those in the prose, they need new simulations and new results. Otherwise, restore the conditions that generated the plotted values. Do not change labels alone while retaining the percentages.

The exact results in the existing records are 7.6198%, 55.6959% and 24.8463%. The 10/20-nH case was checked at a finer maximum time step and gives approximately 56.0%.

The metric also needs a definition. The recorded metric is

`100 × abs(Ipk1 − Ipk2)/(Ipk1 + Ipk2)`,

where each Ipk is that branch's individual maximum turn-on drain current. These peaks need not occur at the same instant. It is a peak-current imbalance metric, not an energy-imbalance metric. Equal peaks alone would not prove equal transient current waveforms.

### 2. A driver citation is wrong

**Location:** p. 4, Section IV-B.

The 2EDF7275K driver is cited as [10]. Reference [10] is the EPC2361 datasheet. The driver is reference **[11]**.

### 3. The interpretation of Fig. 8 invokes a case that is not shown

**Location:** p. 5, Section V-D and Fig. 8.

All three displayed traces use a **20-nH gate loop**. The legend varies external turn-on resistance and off-state bias. The text then contrasts higher and lower gate-inductance cases and says the lower-inductance case has more headroom. That comparison is absent from the submitted evidence.

This does not mean the lower-inductance conclusion is necessarily false. Existing internal results contain a comparison at the same 3-ohm turn-on resistance and -1-V off bias:

| Assumed gate-loop inductance | Worst drain peak | Largest held-off gate peak | Minimum gate voltage |
|---|---:|---:|---:|
| 10 nH | 87.98 V | 0.427 V | -2.427 V |
| 20 nH | 90.06 V | 0.441 V | -2.501 V |

Those results are not currently supplied in the digest. Either include a compact comparison or restrict Section V-D to the resistance/bias comparison actually shown. Values are simulation predictions at the assessed nominal conditions, not measured margins.

### 4. The peak-current screen does not cover the complete current range

**Location:** p. 3, Fig. 3(b), Sections III-A/C and Fig. 4(b).

The high-side voltage peak at low-side turn-on is nonmonotonic with current. Some compact-path cases exceed the 90-V target at lower current even though the point near 80 A passes. Fig. 4(b) deliberately reports only low-side turn-off stress.

It is therefore correct to call four devices a **peak-current-screened candidate**. It would be incorrect to interpret that screen as proof of voltage compliance throughout a sinusoidal current cycle. The unresolved low-current region needs explicit acknowledgment or a final-setting sweep. Both drain-stress events, both current polarities and the relevant operating corners must ultimately be considered.

### 5. The approximate 90-V result is not a robustness demonstration

**Location:** abstract; p. 5, Section V and Fig. 8.

The stored revised 20-nH result is approximately **90.06 V**, so “approximately 90 V” is a reasonable rounded statement. It does not show useful margin to an exact 90-V design target. The manuscript already acknowledges this in Section V-D; the abstract should not sound more conclusive than that interpretation.

“Optimization” and “retaining fast switching” need either a stated objective and numerical speed/loss comparison, or more modest wording such as “adjustment of gate-drive settings.” At present the reader sees a few settings rather than a demonstrated optimum.

## Coordinating review — checks that passed

- Equation (1), with the stated modulation-index definition, gives **227.73 A rms** and **322.06 A peak**. The reported approximately 228 A rms is correct.
- Four ideally sharing devices correspond to **80.52 A peak per device**. The approximately 80-A screening point is consistent with the drive specification.
- **1200/16 = 75 V**. The nominal submodule calculation is correct.
- Equation (2), **D-FOM = 1/sqrt(RDS(on) Coss,Q)**, agrees with the cited device-FOM paper. The resistance-capacitance product itself is the inverse-performance quantity; the manuscript correctly says lower product corresponds to higher D-FOM.
- For EPC2361, the plotted charge-equivalent capacitance near **1.8 nF** is consistent with Qoss = 90 nC at 50 V: 90 nC/50 V = 1.8 nF. The manufacturer also lists approximately 1796 pF time-related output capacitance. This is different from the differential Coss value around 1019 pF; that distinction is not an error.
- The EPC2361 reference date of **20 July 2026** agrees with the current official datasheet. The driver datasheet revision/date also agrees with the official document.
- The digest clearly distinguishes simulation from planned measurements and does not claim measured full-drive efficiency.

Primary checks: [device-FOM paper](https://www.ams-publications.ee.ethz.ch/uploads/tx_ethpublications/3_CFOM_FINAL-FINAL_Azurza.pdf), [EPC2361 datasheet](https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2361_datasheet.pdf), [2EDF7275K datasheet](https://www.infineon.com/assets/row/public/documents/24/49/infineon-2edf7275k-datasheet-en.pdf).

## Reviewer 1 — GaN switching and parasitic modeling

**Recommendation: Weak reject. Confidence: high, 4/5.**

### Summary and strengths

The study addresses a useful implementation problem: obtaining credible switching margins from a low-voltage, high-current GaN phase leg intended for a high-voltage SPB drive. It appropriately examines both low-side turn-off and opposite-device drain stress at turn-on. Connecting extracted PCB parasitics to circuit simulation is stronger than selecting devices from a figure of merit alone. Calling four devices a candidate rather than a global optimum is appropriate.

### Major comments

1. Reconcile Section IV-A with Fig. 5 and define the imbalance calculation and switching event. The contradictory parameters prevent assessment of a central quantitative result.
2. Show the lower-gate-inductance prototype case referenced in Section V-D or remove that comparison. Tabulate the selected operating point and its exact drain/gate peaks.
3. Evaluate the final drive setting over the relevant current range. The high-side low-current overshoot in Fig. 3 already shows that peak-current screening alone is insufficient.
4. Supply essential simulation details: device-model identification, inductive-load test circuit, freewheeling conditions, gate-inductance placement, switching-energy integration limits and treatment of the extracted network's shared/mutual impedances. These are needed in the digest even if long derivations are deferred.
5. Define the 0.41-nH loop precisely. Give extraction frequency, ports/return paths and whether package and capacitor contributions are included. A local per-cell number is not automatically the equivalent inductance of simultaneous four-branch commutation.
6. Support the device comparison, loss model and thermal suitability. The capacitance evaluation voltage is missing; the thermal section reports no temperature; and the contribution beyond applying standard design practice is not sharply quantified.

### Minor comments

- Correct the driver citation [10] to [11].
- Explain the 0.8-V gate reference and report negative gate excursions as well as positive peaks.
- A two-device perturbation study motivates symmetry but does not verify sharing among four routed devices driven by two separate drivers. Show branch-current evidence for the actual building block.
- Explain 316-A transient current relative to the 322-A specified peak.
- Consolidate repeated page-limit notices and enlarge small figure labels.

## Reviewer 2 — Traction drives and modular converter architectures

**Recommendation: Weak reject. Confidence: high, 4/5.**

### Summary and strengths

The architecture-to-device-to-layout sequence is sensible, and the phase-current equation is correct under balanced equal-voltage operation. The title and application are relevant to the conference. The conclusion appropriately avoids claiming a full-drive loss optimum or complete operating-envelope validation.

### Major comments

1. The sensitivity-study contradictions are a definite error. The same percentages cannot be assigned to the different perturbations stated in the figure and prose.
2. The prototype's higher/lower gate-inductance comparison is unsupported by the displayed traces. Distinguish assumptions, extracted quantities and the parameters actually swept.
3. Device screening is not reproducible without Coss,Q's definition/evaluation voltage, normalization basis and device identities. A compact table or short conditions statement is sufficient; a long derivation is not necessary.
4. Report a quantitative reason for retaining four devices. It is not the minimum-loss option, while the device-count, area, gate-loading and thermal tradeoff is deferred. A thermal constraint is listed but no predicted junction temperature or cooling requirement is supplied.
5. The decisive routed result is restricted to 27 °C and one approximately 316-A transition. Show which operating corners have actually been assessed and retain a clear nominal-feasibility limitation.
6. Qualify fault tolerance. Isolated winding sets and modularity support fault-tolerant architectures, but bypass hardware/control and management of a faulty winding still matter. At a fixed 1200-V bus, bypassing one of sixteen equal modules increases the remaining nominal voltage from **75 to 80 V**. This directly affects the voltage margin under discussion. Derating or bus-voltage reduction could change that conclusion and should be stated if assumed.
7. State the new transferable result more clearly. The workflow, Kelvin returns and symmetry are established methods. Quantify how the implementation changes an allowable voltage, parallel-count choice or speed/loss tradeoff relative to the initial assumptions and cited work, especially the closely related paralleled-GaN traction study [9].

### Minor comments

- State the modulation strategy supporting M = 1.15; it is consistent with an extended linear modulation range but readers should not have to infer the method.
- Explain the gate reference criteria and 316-A versus 322-A operating point.
- Reduce placeholder subsections and improve printed figure-label readability.
- Fault tolerance is architectural motivation here, not a result demonstrated by the building-block simulations.

## Reviewer 3 — Prototype validation and scientific presentation

**Recommendation: Weak reject. Confidence: high, 4/5.**

### Summary and strengths

The digest is a coherent simulation-led prototype design study. The concrete voltage/current and local-loop estimate give it engineering substance. It is scientifically appropriate to identify measurements as planned and to avoid presenting CAD renderings or simulation predictions as experimental proof.

### Major comments

1. Resolve the conflicting sensitivity conditions and explicitly define the reported metric. Ranking unequal perturbations is a comparison of selected scenarios, not a normalized sensitivity analysis. The present “of these evaluated cases” qualification is helpful and should remain.
2. Align the prototype interpretation with the resistance/off-bias sweep actually displayed. Add exact peak values and switching energy for the retained setting; define what is optimized and what “fast” means.
3. Assess the current range, both relevant commutations and current polarity. The low-current voltage limitation is already visible in the supplied data.
4. Bound the margin claim. Explain extraction/model boundaries, the 90-V drain target and 0.8-V gate threshold reference, and the remaining uncertainty at hot junction, bus variation, parasitic variation and inter-driver skew.
5. Make the planned experiment concrete. Briefly specify the test arrangement, bus/current/temperature points, per-branch measurements, gate-voltage reference, bandwidth and voltage/current deskew for energy integration. A long experimental-method section is unnecessary, but the validation plan needs more than a list of quantities to compare.
6. Support “Loss and Thermal Assessment” with a thermal result and key assumptions, or rename it to match the loss estimate actually presented.

### Minor comments

- Explicitly call Fig. 7(a) a CAD assembly rendering so it cannot be mistaken for a fabricated-board photograph.
- Identify which transistor/branch gives each worst-case voltage peak and whether the panels refer to the same switching event.
- Improve the readability of Figs. 2, 4, 7 and 8 at printed size.
- Repeated red future-work notes make the digest appear incomplete. Retain any conference-required scope markers, but use the available space for assumptions and decisive numerical results.

## Grammar and presentation corrections

These are secondary to the numerical contradictions. Suggested edits do not require changing the technical story.

| Location | Current wording | Suggested wording |
|---|---|---|
| Fig. 1 caption | “for poly-phase machine” | “for a polyphase machine” |
| Fig. 1 caption | “(b) Three-phase submodule” after a semicolon | “(b) three-phase submodule” |
| End of introduction | “The introduction part will be extended in the final paper; the reduced version is given in the digest due to the page limitation.” | “The full paper will provide an expanded discussion of the relevant literature.” If a scope marker is not required, this can be omitted. |
| Section III-A | “uni-directional current” | “unidirectional current” |
| Section IV-B | “two high-side GaNs” / “two low-side GaNs” / “each GaN” | “two high-side GaN devices” / “two low-side GaN devices” / “each device” |
| Section V-B | “the full paper will detail layout and Q3d results” | “The full paper will present the PCB layout and Q3D extraction results.” |
| Section VI-A | “One prototype board building block will be tested” | “One prototype phase-leg building block will be tested.” |
| Section III-B heading | “Loss and Thermal Assessment” without thermal results | Include a thermal result or use “Loss Assessment.” |
| References | Mixed quotation marks, title capitalization, journal formats and comma before “et al.” | Apply one consistent IEEE reference style; do not number the References heading unless the venue template requires it. |

The larger writing issue is repetition, not severe grammar. Numerous versions of “because of the digest page limit” and several one-sentence promise-only subsections consume space without adding evidence. This is a presentation concern, not a claim that red scope notes violate an official conference rule.

Several figure labels are very small in the submitted layout. For example, Fig. 4's originally 7-pt labels are reduced to roughly 5 pt by the current printed scaling; Fig. 8's labels are roughly 4–5 pt. Enlarge lettering at the intended printed size rather than simply shrinking a completed figure.

## Additional reference and comparison checks

- The core D-FOM expression is correct, but the internal comparison data use Coss,Q evaluation voltages of 50 V for the 100-V class, 100 V for the 200-V class, 280 V for the 350-V device and 400 V for the 650-V class. These correspond to different fractions of device rating. The digest must state the comparison basis and its limitations. The cited FOM paper's example survey uses a consistent two-thirds-of-rating evaluation point; copying that exact fraction is not mandatory, but an explicitly justified basis is.
- The two references involving Staffan Norrga appear to be [2] and [3]. That is 2/11 = 18.2% of all listed references, or 2/9 = 22.2% if both manufacturer datasheets are excluded. This is a Norrga-only count, not a verified conference-policy compliance result: the full author list and the venue's denominator/rule would have to be checked.
- The fault-tolerance comparison should avoid implying that other multilevel topologies categorically lack fault-handling options. A safer statement is that the SPB's isolated winding sets and modular structure facilitate fault-tolerant operation when suitable bypass and fault-management provisions are included.

## Suggested order of action

1. Reconcile the Fig. 5 conditions with the simulations and define the metric.
2. Correct the driver citation.
3. Supply the missing gate-inductance comparison or revise Section V-D accordingly.
4. Add the essential extraction/model assumptions and a compact retained-setting results table.
5. State the low-current limitation and nominal-condition scope; quantify a thermal result or narrow the thermal claim.
6. Sharpen the quantitative novelty and planned validation, then perform the grammar/figure-readability pass.

These corrections would address the strongest common reasons for the simulated weak-reject decisions. They do not guarantee a particular conference outcome.

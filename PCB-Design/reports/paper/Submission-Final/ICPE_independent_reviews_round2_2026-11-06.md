# Independent ICPE digest reviews — round 2

Reviewed files: `ICPE_Digest.pdf` and `ICPE_Template.docx` in `reports/paper/Submission-Final`, as supplied on 6 November 2026. The PDF contains five pages and is the authority for these comments.

Four fresh agents were created without conversation history. Each received only a separate submission packet containing copies of these two files, their extracted text, and rendered PDF pages. They were instructed not to consult the repository, project data, memory, earlier reviews, other conversations, external sources, or other reviewers' outputs. Each inspected all five rendered pages. All were explicitly told that this is a **five-page digest**, with experiments permitted to follow in the full paper. The manuscript files were not modified.

These are simulated independent reviewer assessments, not conference decisions. The report compiles their comments; no simulation reruns or external reference verification were performed.

## Recommendations

| Reviewer | Perspective | Recommendation | Confidence |
|---|---|---|---|
| 1 | GaN switching, device modeling, and parasitic extraction | Borderline | 4/5 |
| 2 | Truck propulsion, modular converters, and architectural significance | Borderline | 4/5 |
| 3 | Validation, loss/thermal accounting, and reproducibility | Borderline | 4/5 |
| 4 | Grammar, structure, mathematical typography, and figures | Copy-editing review; no acceptance vote | — |

## Overall assessment

The technical reviewers see a credible simulation-led engineering study and a plausible full-paper contribution. They find the progression from requirements to device selection, parallel count, layout, and switching response coherent. The strongest finding is that satisfactory switching near peak current does not establish feasibility across the current range or bus-voltage variation.

Their borderline recommendations concern the evidence supporting the proposed implementation, not the absence of experiments at the digest stage. The shared concerns are an unauditable loss allocation, the physical basis for the successful 10-nH gate-loop assumption, missing selected-case gate/sharing results, and an insufficiently explicit architectural consequence of the limited voltage margin. These do not require rewriting the paper throughout.

### Numerical consistency checks

- Equation (1) gives approximately **227.7 A rms and 322.1 A peak**, consistent with the reported rounded values.
- Four parallel devices imply approximately **80.5 A peak per device** under ideal sharing.
- Sixteen submodules at 75 V give a 1200-V total dc link.
- With eight devices sharing 18.6 W equally, the stated thermal assumptions give approximately **40 + 0.65(18.6) + 7.62(18.6/8) = 69.8 °C**, consistent with 70 °C.
- The reported 92.2-V peak exceeds the paper's **90-V design target**, but does **not** demonstrate violation of the 100-V device rating.

These checks establish internal arithmetic consistency only; they do not validate the models or physical assumptions. Reviewers 1 and 2 found no demonstrable substantive Word/PDF text mismatch. Missing equation objects in plain Word text extraction were not treated as document errors.

## Reviewer 1 — GaN switching and parasitic modeling

**Recommendation: Borderline; confidence 4/5.**

### Strengths

- The system-current calculation and design sequence are coherent.
- Figs. 3 and 8 examine both drain-stress events and adverse low-current behavior.
- The extraction description identifies network size, frequency, capacitor ESL, and equal-branch excitation.
- The paper explicitly acknowledges operating-margin limitations.
- The proposed Kelvin-referenced voltage, branch-current, and deskewed-energy measurements are relevant to the claims.

### Major comments

1. **The favorable result depends on an assumed gate network.** Page 4, V-B states that “gate loops remain assumed 10/20-nH bounds.” These alternatives determine whether the 90-V target is met. Power extraction alone therefore does not establish the favorable complete switching network. A physical estimate or extraction of the actual gate/Kelvin path, with a precise definition of what the loop value includes, would strengthen the digest. This is missing evidence, not a demonstrated extraction mistake.

2. **The final selected setting lacks corresponding gate and branch evidence.** Fig. 8(a–b) shows A–C, while the favorable drain sweep uses D. The reader cannot inspect D's held-off gate response. The two-device sensitivity study also does not verify current sharing in the four-device routed network. A small summary of D's worst gate extrema and branch-current imbalance would suffice; a large new study is unnecessary.

3. **The identified margin failure needs a concrete design consequence.** Page 5, V-D reports that a 5% local-bus increase produces a 92.2-V peak. This is correctly acknowledged as a failure against the chosen target. A revised allowable bus range or candidate voltage/count choice would connect the limitation to an implementation decision. Full-envelope qualification can remain future work.

4. **The extraction/device-model interface needs clarification.** “Package and gate-path inductances were not separately extracted” does not establish whether package/source parasitics are embedded in the manufacturer model, added externally, or omitted. Their inclusion matters relative to a 0.41-nH copper/capacitor loop. The packet does not establish either omission or double counting; a short accounting statement is needed.

5. **The preliminary thermal screen is not transferred to the final routed settings.** Page 3 gives 18.6 W and 70 °C, while page 5 gives a rated-current switching-energy result for the routed network. These are not inherently contradictory, but the paper does not show how final drive settings affect sinusoidal-average loss. State explicitly whether the preliminary thermal result remains unverified for the routed case, or provide a compact updated estimate.

### Minor comments and questions

- Fig. 2 needs device identifiers and charge-evaluation voltages for the surveyed devices.
- Give a brief rationale for the 90-V target relative to the 100-V rating.
- Explain the allocation of the provisional capacitive freewheeling term relative to integrated switching energy.
- State D's gate extrema and, when available, induced channel current; static threshold crossing is not a complete dynamic-turn-on criterion.
- Driver skew is a relevant full-paper sensitivity, particularly for a 5.9-ns transition, but its absence alone is not a digest rejection reason.
- Some figure annotations are small, and repeated deferral statements occupy space that could hold decisive clarifications.

**Novelty assessment:** Application-specific implementation and quantitative constraint assessment, rather than a new topology, device metric, or extraction workflow. State more concretely what the findings add beyond existing high-current parallel GaN modules.

## Reviewer 2 — Propulsion architecture and significance

**Recommendation: Borderline; confidence 4/5.**

### Strengths

- Equation (1), the modulation convention, and the reported current are consistent.
- The fault-tolerance motivation is appropriately qualified by bypass hardware, control, and device limits.
- The low-current stress assessment is more informative than a rated-current-only waveform.
- Extracted power parasitics and assumed gate parasitics are clearly distinguished.
- The limitations are transparent, and the planned building-block measurements are appropriate for a digest-stage study.

### Major comments

1. **The sixteen-submodule architecture remains a candidate.** Section II-C sets 75 V to allow overshoot and voltage variation, but V-D shows the +5% case failing the 90-V target. The paper acknowledges this; it is not a hidden contradiction. A viable next design point or an explicit admissible operating range would strengthen the architectural conclusion.

2. **Isolate the novelty relative to the cited work.** The contribution is described as a quantitative coupling between power/gate networks and submodule voltage. Symmetry, Kelvin returns, paired drivers, and extraction-to-simulation are established implementation practices. Explain the particular new finding or design rule relative to the SPB GaN comparison [6] and high-current module work [9]. A short distinction is sufficient; an extensive literature expansion is unnecessary.

3. **Include one quantitative architectural consequence.** Sixteen three-phase submodules imply 48 phase legs and 384 power devices for the proposed arrangement. The voltage-class benefit entails repeated winding sets, drivers, and interconnections. A full machine demonstration is unnecessary, but a bounded semiconductor-loss comparison or concise accounting of the dominant architectural tradeoff would strengthen system significance.

4. **The 10-nH gate path and synchronized drivers are decisive assumptions.** A preliminary achievable gate-loop estimate and a modest delay-skew sensitivity would better substantiate the paired-driver choice. These could remain simulations at digest stage.

5. **Close the loss argument around the final routed case.** The single-cell-based preliminary loss estimate and routed rated-current energy do not establish the same average operating loss. A compact final-settings estimate, clearly identified as preliminary, would show whether recovering voltage margin changes the original justification.

### Questions and minor comments

- What local-bus range and submodule-voltage imbalance must normal operation accommodate?
- Is 10 nH achievable for every device with the actual drivers, negative-bias supply, and Kelvin routing?
- What changes when the two drivers have realistic delay differences?
- What total-bus derating or voltage redistribution is intended after bypass? At unchanged 1200 V, fifteen equal submodules would average **80 V**, above the tested 78.75-V condition. This does not invalidate the qualified fault-tolerance motivation; it defines an operating restriction needing discussion.
- Give Fig. 2's device identities/evaluation conditions and the rationale for 90 V.
- Figure labels and the unlettered thermal subsection need attention.
- Repeated scope notes could be consolidated if space is needed, but a wholesale rewrite is not requested.

**Novelty assessment:** The potential contribution is the quantitative connection between this high-current building block and SPB voltage-class feasibility. Figs. 3 and 8 provide credible digest-level evidence, especially for the inadequacy of peak-current-only screening. The distinction from prior work and viable voltage allowance remain insufficiently developed.

## Reviewer 3 — Validation and reproducibility

**Recommendation: Borderline; confidence 4/5.**

### Strengths

- The operating-point, parallel-current, and preliminary thermal arithmetic are internally consistent.
- The plotted switching events support the stated limitations of peak-current screening.
- The network description provides useful extraction details.
- The adverse +5% bus result and limits of the conclusions are disclosed.
- The planned measurement observables are relevant.

### Major comments

1. **Make the loss budget auditable.** Page 3 combines integrated switching energies with a “provisional 2.9-µJ capacitive freewheeling term per device per cycle.” It does not establish which stored-capacitance energy the integrals already contain or why the extra term is independent. This is an accounting ambiguity, **not demonstrated double counting**. Under a literal eight-device, 50-kHz interpretation, the extra term represents 1.16 W, which is material relative to 18.6 W. A compact loss equation and component totals for n = 4 should identify device/event counts, integration boundaries, resistance temperature, and capacitance-energy allocation.

2. **Substantiate or bound the successful gate-loop assumption.** The best nominal peak is only 1.2 V below the 90-V target, and the result changes materially with gate inductance. Give a physical basis for 10 nH or state the admissible gate-loop range as a design requirement. Distinguish the design target from the device rating.

3. **Report selected-case gate/sharing metrics.** Include D's worst gate extrema and maximum branch imbalance at rated current and one low-current point. Clarify package-model inclusion. This would substantiate the joint drain/gate assessment for the implemented four-device arrangement.

4. **Tie the planned experiment to the identified weaknesses.** A compact test matrix should include nominal/raised bus voltage, low/rated current, selected gate settings, and at least one elevated-temperature condition. State how probe loading and timing uncertainty will be assessed. Hardware results themselves can remain full-paper work.

### Minor comments

- State Fig. 2 device identities and how charge-evaluation voltage is chosen across classes.
- A 0.2-ns maximum time step is not itself a convergence demonstration. A finer-step comparison of peaks and energies would strengthen confidence.
- State directly that the cold switching simulations and preliminary 70 °C cooling estimate do not constitute an electrothermal iteration.
- Numerical loss-component labels would improve Fig. 4's auditability; several figure labels are small.
- Repeated deferral statements occupy space that could hold essential numerical summaries.

### Appropriate division between digest and full paper

**Minimum digest clarifications:** auditable n = 4 loss accounting; package/model inclusion; physical support or an admissible bound for gate-loop inductance; D gate/sharing metrics; a short validation matrix.

**Reasonable full-paper work:** hardware tests, thermal validation, probe uncertainty assessment, driver skew and component tolerances, expanded temperature/current-polarity coverage, and fuller extraction/model reproducibility.

## Reviewer 4 — Grammar, structure, and figure presentation

The editor found the digest readable, with a coherent progression and no clear contradiction between plotted trends and the accompanying numerical discussion. Equations are visually intact. The editor excluded PDF extraction artifacts such as artificial internal spaces from the error list.

### Objective errors and local corrections

| Priority | Location | Original wording or item | Minimal correction |
|---|---|---|---|
| Must fix | p. 3, Section III | Unlettered “Loss and Thermal Assessment,” followed by “B. Selection of Four Parallel Devices” | Use “B. Loss and Thermal Assessment” and “C. Selection of Four Parallel Devices.” |
| Should fix | p. 2, II-B | Baseline `Coss,Q = Qoss(Vtest)/Vtest` and `Coss` | Apply proper subscripts consistently with equation (2). |
| Should fix | p. 3, IV-A | Baseline `Ipk,1` and `Ipk,2` in the imbalance expression | Format the peak-current indices as subscripts. |
| Should fix | p. 2, equation (3) | N is not explicitly defined | Add “where N is the number of series-connected submodules.” |
| Should fix | p. 2, II-B | Vtest has no verbal definition | Add “where Vtest is the voltage at which output charge is evaluated.” |
| Should fix | p. 4, V-B | “The estimated local commutation loop is approximately 0.41 nH per cell” | Insert “inductance” after “loop.” |
| Should fix | p. 4, V-B | “capacitor ESL” | Introduce “capacitor equivalent series inductance (ESL)” at first use. |
| Should fix | p. 5, reference [1] | Ends with “Art. no. 100253” | Add a final period. |
| Should fix | p. 5, references [1]–[5], [7] | Comma before “et al.” | Remove the comma before “et al.” consistently. |
| Should fix | Figs. 2 and 4 | Small labels, especially pale Fig. 2 contours | Increase embedded label fonts and darken pale contour labels without changing the plotted information. |
| Should fix | Fig. 7(b) | Tiny upper-right conductor legend duplicates the clearer bottom legend | Remove the tiny duplicate or enlarge it. |

### Optional polish, not objective errors

- Use lowercase “gallium nitride” in the index terms.
- Shorten the introduction's full-paper note to “The introduction will be expanded in the full paper.”
- Apply compound-modifier hyphens consistently: Low-Voltage, Single-Cell, Gate-Drive, Current-Sharing, Kelvin-Source.
- Delete “Conclusion will be updated in the full paper”; the following sentence already explains planned work.
- Consolidate repeated “Because of the digest page limit” statements if space is needed. Red text is visibly present; whether to retain that colour depends on the intended submission format.
- Use Iph,rms in Table I for consistency with (1); the existing “A rms” qualifier already makes the numerical meaning clear.

## Suggested order of targeted revision

1. Correct subsection numbering, inline symbols, definitions, references, and the duplicate tiny legend. These are local edits.
2. Add a short, auditable n = 4 loss accounting summary and state whether the final routed settings have an updated average-loss estimate.
3. Clarify package inclusion and support the 10-nH requirement; report D's gate extrema and branch imbalance.
4. Explain the 90-V criterion and the practical consequence of the unsuccessful voltage-variation case.
5. Sharpen the distinction from [6] and [9] in one or two sentences, and specify a compact experimental test matrix.

The reviewers' suggestions should not be interpreted as a requirement to implement every optional sensitivity study in this five-page digest or to rewrite all of its paragraphs. Their common request is to make the decisive quantitative evidence and its boundaries easier to assess.

## Reviewed-file fingerprints

- ICPE_Digest.pdf: SHA-256 `a444f9d16f3cb6f587c395b9fe5e695ac22c89a954d999e1433a778ed4aa5360`
- ICPE_Template.docx: SHA-256 `13aca1e593565eda65c05726126f427c3418366373bd9a515a67c50e68071ea7`

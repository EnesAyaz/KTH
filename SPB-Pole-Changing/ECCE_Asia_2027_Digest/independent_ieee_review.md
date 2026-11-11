# Independent IEEE digest review and response

The reviewer was a fresh agent with no inherited conversation or repository context. It was instructed to inspect only a manuscript copy and manuscript page images, to leave all files unchanged, and to assess the work as an IEEE ECCE digest. This is an internal critical review, not a conference decision or an acceptance prediction.

## Initial assessment

The reviewer considered the analytical contribution defensible, but judged the original manuscript borderline or weak reject because the main winding construction was described without enough evidence to reproduce it. Lack of a manufactured prototype was not the central objection.

The recommended contribution was a construction-specific feasibility method that jointly selects semiconductor voltage class, SPB cell count, slot allocation, and two pole orders while enforcing balanced isolated three-phase groups and cancellation of the alternate selected stator spatial order.

## Comments and implemented revisions

| Reviewer comment | Revision in the current digest |
|---|---|
| Make the principal winding example reproducible now, rather than promising its connections in the full paper. | Section III-B gives the 12-cell/36-slot coil start and return slots, polarity, cell assignment, pitch, and current phases for both pole modes. Table II reports normalized complex desired-order gains, winding factors, and alternate-order residuals. |
| Define the general construction, enumeration, and scope of rejection. | Section III defines the primitive triple slot formula and ordering, then consecutive grouping into cells. Sections III-IV specify the acceptance tolerance, pole-count set, slot and cell ranges, integer pitch domain, and ranking rule. The phase-axis condition is not presented as a universal machine-feasibility theorem. |
| Separate selected-order MMF admissibility from machine feasibility. | The digest explicitly leaves complete harmonic MMF, impedance and mutual coupling, rotor-harmonic back-EMF, saturation, and physical rotor compatibility to subsequent analysis. Cancellation is confined to the alternate selected stator order. |
| Do not use arbitrary dq parameters as evidence of a realized propulsion benefit. | Section V is titled Illustrative Propulsion Envelope Sensitivity. It gives per-group parameters, voltage derivation, current/voltage constraints, resistance, electrical speed, power ceiling, reference matching, and the stronger-field-weakening sensitivity parameters. It explicitly does not establish an optimized truck propulsion machine. |
| Connect winding checks with series-cell power balance. | Section II restricts the statement to equal ideal electromagnetic conversion power with equal modal gain, equal current amplitude, and a common current angle relative to modal EMF. It does not claim completed dc balancing under additional harmonics or transitions. |
| Correct the device resistance comparison. | The index now uses actual Table III counts: 20, 48, 60, and 480 milliohms. It is labelled a fixed-current, equal-paralleling arithmetic index, not equal-output-power loss. The unsupported parallel-die-demand label was replaced by higher tabulated resistance. |
| Distinguish the contribution from prior SPB partitioning and electronic pole changing. | The introduction states that the added result is the admissibility construction and its intersection with discrete device/coil constraints. The title emphasizes joint selection. |
| Use truck propulsion, without mislabelling passenger-car evidence. | Author-written application wording and the title now use truck propulsion. Published reference titles are preserved. Passenger-car slot/pole examples are expressly illustrative, not truck constraints. |

## Follow-up review

After inspecting the revised manuscript, the reviewer confirmed that the original major reproducibility criticism was addressed for the principal 12-cell/36-slot example. It found the start/return coverage, current phases, and reported complex Fourier gains internally consistent, and found no clear arithmetic error in that example.

The follow-up requested an explicit general primitive-triple formula, a more precise current-angle condition for power balance, and clarification that the frontier uses unrestricted integer coil pitches rather than the separate 1.5-pitch sensitivity. These were added to the final revision. The general consecutive-block construction also makes the retained two-cell grouping reconstructible.

## Verification and remaining work

A separate direct coil-side Fourier calculation, using the exported coil connections, reproduced winding factors of 0.8660254 for both modes and alternate-order residuals below 1e-12. Its numerical record is in `qa/independent_winding_check.json`. This checks the stator construction; it does not validate a manufactured motor.

Red full-paper notes remain for the 200-V GaN three-phase building block, electrothermal design, machine FEA, identified flux maps, loss-aware truck drive-cycle comparison against an equal-volume IPMSM, excitation demand, and pole-transition constraints. These are planned work, not completed validation. The final digest remains five pages.

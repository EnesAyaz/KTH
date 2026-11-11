# Active research plan

The current three-phase scope and evidence are in README.md and simulation/THREE_PHASE_METHOD.md. The official-template Word paper is ECCE_Asia_2027_Digest.docx.

## Contribution
Identify usable combinations of stacked-cell count, three-wire winding layout and pole ratio for a hybrid-excited synchronous drive. Demonstrate an explicit higher-pole example and quantify the magnetic/electrical conditions required for a speed-range benefit. Other phase counts are future work.

## Completed preliminary work
- Exact balanced winding construction with N=2..40, pole combinations8/4,12/6,16/8,20/10 and ratio checks16/4 and12/4.
- Complete72-coil mapping for a24-cell12/6-pole candidate; both pitch factors0.866; no neutral conductor.
- Device-voltage margin scenario and slot-count map; candidate selection is not a loss or manufacturing optimum.
- Hybrid12-segment polarity concept and Fourier flux/yoke check, based on the principle in the supplied paper.
- Desired-order dq torque/power envelopes, matched12-pole baseline, stronger-field-weakening IPMSM sensitivity and lower-mode inductance sensitivity.

## Evidence status
The numerical source is simulation/results_three_phase/three_phase_codesign.json and its CSVs. Geometry, rotor materials, inductances and operating points are not validated by FEA or test. The new study is independent code inside Digest; it does not reuse older optimistic HESM scaling as verified machine data. The earlier assumptions and reviews remain read-only reference context.

The supplied Conto/Bianchi paper establishes specialized synchronous pole-changing possibilities; its Section VI hybrid speed curves are simulation-based. It does not experimentally validate this12/6 design, SPB cell selection or the adopted traction-scale modal parameters. The initial pole-changing hybrid proof and an optimized production IPMSM are different comparison levels.

## Next steps
1. Freeze the physical72-slot stator, conductor layout and12-segment rotor geometry; validate the actual coil topology and lack of neutral lead against the intended hardware.
2. Establish a manufacturable field circuit and derive high/low flux maps with saturation and unused harmonics. Confirm the1.659 back-iron demand and whether a low-mode inductance near140µH is physically attainable.
3. Optimize the fixed-pole IPMSM against the same dimensions, current density, magnet and thermal limits; include inverter, field and mechanical loss in equal DC-input-power comparisons.
4. Add a transition schedule and DC-cell energy/balancing simulation. Do not infer smooth transitions from the maximum-of-two-steady-envelopes curve.
5. Rank cell counts with the established loss and device models, not voltage class alone; check fractional-slot candidates and NVH/manufacturing constraints.
6. Add other phase counts only after the three-phase design is established.

The prior phase-count outline and evidence review are retained under archive/phase_count_study and are superseded for the active manuscript.

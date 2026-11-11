# Active research plan

The active paper selects cell count and pole ratio from constraints rather than assuming24 cells or12/6 poles. Read README.md and simulation/DESIGN_SELECTION_METHOD.md. The numerical source is simulation/results_selection/design_selection.json.

Completed: primary EV slot/pole benchmarking; manufacturer100/150/200/350 V ratings and device parameters; voltage and construction-specific slot/coil bounds; exact balanced winding screening at two pole orders; two-cell12/6 control demonstration; 2:1,3:1,5:2 comparison; pitch/coil-span trade-off; voltage/winding shortlist; retained conditional torque/power diagnostic.

Important correction:24 cells was not the control minimum. Two cells suffice in the demonstrated36-slot12/6 layout. Device voltage and winding compatibility can require more. Also,3N phase branches are not3N unconstrained currents; neutral isolation leaves2N instantaneous current coordinates. The slot bound changes with single/double layer and independently split conductor groups.

No global sweet spot has yet been established. The150–200 V versus100 V Pareto shortlist requires full hot conduction/switching loss, parallel die, driver, capacitor, winding, thermal and cost modeling.350 V is not rejected as a class; the retained example device has a large resistance/current-scale penalty.3:1 is not declared impossible; it is outside the demonstrated balanced uniform-triple family.5:2 still needs a compatible rotor.

Next milestones:
1. Verify full electromagnetic winding functions and manufacturable lead/insulation arrangements for the shortlisted48-slot8/4 and36-slot12/6 cases, alongside the60-slot100 V case.
2. Evaluate detailed device loss and thermal/parallel-area cost using the established read-only GaN model as the equation source. Do not modify or execute its existing outputs in place.
3. Identify synchronous/hybrid rotor maps with saturation, yoke and parasitic-harmonic EMFs. Do not treat the illustrative terminal-equivalent model as identified geometry.
4. Compare against optimized equal-volume IPMSMs, including excitation and mechanical losses, then transient cell balancing and drive-cycle results.
5. Broaden winding families if3:1 or odd/fractional-slot designs offer enough benefit to justify additional complexity.

Earlier24-cell-centered planning is retained in archive/single_example_study. Existing project research and reviews remain read-only.

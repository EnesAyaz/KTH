# No-load stator sizing check

The baseline should not be called an optimized HE-IPM design. Its 25-mm stator yoke is lightly utilized at the current no-load excitation, while some rotor regions already reach approximately 2.95 T. Thus underused stator iron and local rotor bottlenecks coexist.

## Controlled cases

`screen_stator_sizing.py` reuses only the shared solver function, without executing the baseline output workflow. The baseline defaults remain unchanged. Cases have the same 1-mm air gap, rotor geometry, 0.7-T remanence, synthetic nonlinear B-H law, +6.2/-6.7 A/mm² rotor excitation, and zero stator current.

The coarse screen compares:

1. 25-mm yoke, existing teeth: stator outer radius 140 mm.
2. 10-mm yoke, identical slots and teeth: outer radius 125 mm.
3. 10-mm yoke with wider slot openings/narrower teeth.

All three use 360 angular divisions. The second case is then checked at 720 divisions with `--fine-yoke`. `render_yoke_comparison.py` compares that fine-grid result with the retained fine-grid baseline. All nonlinear solves pass a relative residual below 1e-6.

## Findings

For the matched fine grids, reducing the yoke to 10 mm raises the 6-pole yoke's area-weighted 95th-percentile flux density from approximately 0.67 T to 1.44 T. Its local yoke maximum rises from 1.56 T to 1.94 T, and about 1.86% of yoke area exceeds 1.5 T. The selected air-gap harmonic changes from 0.507 T to 0.496 T, a reduction of about 2.2%. In the 12-pole setting, the selected air-gap harmonic changes from 0.502 T to 0.500 T, about 0.5% lower.

The stator steel cross-sectional area decreases by about 41% with identical slot geometry. This is a geometrical no-load opportunity, not a demonstrated equal-torque, equal-loss or thermal-performance improvement. Rotor hot spots remain near 2.95 T. Merely reducing the yoke does not resolve those local concentrations.

The narrower-tooth coarse case reduces the selected air-gap harmonic by roughly 10–12% relative to the coarse baseline. It therefore cannot be selected simply because its colors look warmer. Tooth width and slot opening also affect gap permeance and flux; rated-load torque, ripple, loss and thermal constraints remain necessary.

The coarse and fine tooth-tip maxima differ substantially, owing to centroid-classified interfaces. Local peaks should not be treated as mesh-converged design limits. Area-weighted yoke statistics and selected harmonic amplitudes are more stable here. A fitted mesh, measured steel curve, and loaded FEA are needed before finalizing dimensions.

## Reading the comparison figure

The comparison uses the same 0–2 T scale for every case and a discrete cyan–green–yellow–red–magenta palette similar to the supplied reference. Only steel is colored; nonmagnetic slots and shaft regions are white. Values above 2 T use the top color and are marked by the extended colorbar. This changes visual presentation, not the calculated field.

Warm colors alone do not establish saturation: the magnetic operating point must be interpreted with the material B-H relation. This model's curve is synthetic. General material-model guidance is available in the [FEMM manual](https://www.femm.info/Archives/doc/manual42.pdf).

## Files

- `results_saturation_screen/sizing_comparison.json`: controlled three-case coarse screen.
- `results_saturation_screen/thinner_yoke_fine.json`: finer candidate solve.
- `results_saturation_screen/fine_mesh_region_comparison.json`: matched fine-grid region statistics.
- `../figures/stator_yoke_comparison.png` and `.svg`: baseline versus 10-mm-yoke fine-grid fields.
- `../figures/stator_sizing_sensitivity.png` and `.svg`: all three coarse cases.

The existing digest baseline is retained. The 10-mm yoke is a candidate for the subsequent constrained design study, not an automatically accepted replacement or a globally optimized machine.

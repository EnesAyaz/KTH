# Preliminary HE-IPM field model

This is an executed 2D magnetostatic finite-element model, not an image-generation illustration and not a validated truck motor. Its purpose is to establish a basic geometry and show two dominant rotor-field orders. It does not generate torque, loss, back-EMF, or speed envelopes.

The field-reversal principle is motivated by Conto and Bianchi, ECCE 2022, DOI 10.1109/ECCE50734.2022.9947754, Section VI. The geometry and dimensions here are exploratory; they were not recovered from that paper or optimized from a truck specification. General vector-potential and permanent-magnet formulation background is available in the [FEMM documentation](https://www.femm.info/doku/doku.php?id=Documentation). The solver here is a task-local Python implementation, not FEMM, Maxwell, or an externally validated commercial model.

## Geometry and excitation

- 36 open stator slots; rotor radius 80 mm, bore radius 81 mm, stator outer radius 140 mm, shaft-hole radius 25 mm.
- Twelve potential rotor pole sites at 30-degree spacing. Zero-based PM sites are 0, 3, 4, 7, 8, 11; wound sites are 1, 2, 5, 6, 9, 10.
- PM arcs occupy radii 64–70 mm and +/-13 degrees about their pole centers. Their remanence is 0.7 T with radial magnetization; recoil relative permeability is 1.05.
- Rotor excitation coil sections occupy radii 55–76 mm, centered +/-10 degrees from wound-pole axes, with 4.2-degree angular width. Their opposite axial current densities represent coil sides. Flux barriers occupy radii 64–80 mm at pole flanks.
- PM signs remain fixed. Reversing the wound sites changes the nominal sign pattern from +-+-+- to ++--++--, corresponding to 12 and 6 poles. Final excitation magnitude differs between modes; equal-magnitude field reversal is not demonstrated.
- The selected current-density magnitudes are approximately 6.20 and 6.70 A/mm² with opposite signs. These fixed settings were selected after a preliminary linear-field harmonic screen and applied unchanged on both meshes. Field-supply, copper-temperature, and rotor-mechanical feasibility are not established.
- The stator current is zero in every FEA solve. Stator copper is therefore represented as a nonmagnetic region without impressed current.

## Governing problem and steel law

The unknown is axial magnetic vector potential Az, with B = (dAz/dy, -dAz/dx). The weak form is

    integral H(B) dot curl(v) dS = integral Jz v dS + integral nu_PM Br dot curl(v) dS.

Nonmagnetic and PM regions use linear permeability. Steel uses the synthetic isotropic monotone relation

    H(B) = B/(mu0 * 1000) + [300/(1.5 T)^9] |B|^8 B.

This is an analyst-selected saturation law, not a measured lamination curve. No hysteresis, eddy-current, or excess-loss model is included. Local peak B is approximately 2.94–2.95 T, identifying regions requiring geometry/material optimization; it is not a demonstrated acceptable operating flux density.

The outer circular boundary at radius 150 mm has Az = 0. A polar grid is triangulated with first-order elements. Material interfaces are classified at triangle centroids; the mesh is not a fully interface-fitted CAD mesh. PM edges and coil corners are approximate. A convex-energy Newton iteration with backtracking solves each nonlinear state.

## Numerical evidence

The fine grid has 55,441 nodes and 110,160 triangles. The coarse angular grid has 360 angular divisions; the fine grid has 720, with unchanged radial sampling. Thus this is an angular mesh sensitivity check, not a complete radial/geometry/boundary convergence study.

Fine-grid selected air-gap radial harmonic amplitudes are about 0.502 T (12-pole setting) and 0.507 T (6-pole setting). Their coarse-to-fine changes are 0.98% and 0.71%. The unwanted alternate selected rotor harmonics remain 8.43% and 8.98%. Other harmonics also remain and are exported. These rotor-field results are distinct from the stator winding Fourier-cancellation result in the digest.

The nonlinear relative residuals are below 2e-8. An independent uniform-current disk benchmark checks the P1 assembly against Az = mu J (R²-r²)/4: relative nodal error 5.6e-5 and linear residual 2.9e-11. This verifies numerical implementation consistency; it does not validate the physical motor.

## Files and reproduction

- `basic_he_ipm_fea.py`: mesh, material assignment, magnet/coil sources, nonlinear solve, Fourier processing, plots.
- `results_basic_fea/basic_fea_results.json`: parameters, excitation signs, residuals, harmonics, and mesh sensitivity.
- `results_basic_fea/basic_fea_fields.npz`: full mesh, material labels, Az and B for both fine-grid states.
- `../qa/verify_basic_fem.py`: analytical disk benchmark and numerical assertions.
- `../figures/ieee_fig4_basic_he_ipm_fea.png` and `.svg`: geometry and two calculated field maps.
- `../figures/basic_he_ipm_flux_maps.png` and `.svg`: larger standalone field maps.

Run the solver with the configured bundled Python. `--plot-only` regenerates plots from saved fields without solving again. NumPy, SciPy, and Matplotlib are resolved from `simulation/vendor`.

## Separate conceptual mode figure

`../figures/render_mode_tradeoff.py` creates the new high-pole/low-pole torque and power sketches. They use arbitrary normalized scales, constant torque followed by a cosine roll-off, and P = T omega. They have no physical torque, rpm, or power rating and are not calculated from the FEA geometry. Their definition is retained in `results_basic_fea/mode_sketch_definition.json`. The earlier uncalibrated IPMSM/FW comparison remains historical and is no longer the digest performance figure.

## Full-paper work

Use a justified truck design point, measured material data, manufacturable barriers/bridges and rotor-coil geometry, nonlinear loaded angle/current sweeps, flux-linkage maps, demagnetization checks, and mechanical limits. Then derive MTPA/field-weakening torque–speed and power–speed envelopes under actual current/voltage constraints. Include stator and rotor copper, iron, magnet, excitation-supply, and inverter losses plus thermal duty, cell balancing, and pole transitions. None of these are claimed completed by the no-load field maps.


## Annotated display

The current field figures use a shared 0–2 T display range. Values above 2 T are clipped to the top color; the colorbar extension triangle marks this clipping. The computed local peak remains about 2.95 T and is stated in the digest caption. Component arrows identify buried PMs, rotor winding, and stator winding. N/S labels are derived from the calculated radial air-gap field: 12 alternating sites in the high-pole setting, and six alternating groups of two same-polarity sites in the low-pole setting. These plotting changes do not alter the computed fields.


## Selected 17.5-mm-yoke digest candidate

The current digest uses the separate17.5-mm-yoke fine-grid result (`results_saturation_screen/yoke_17.5mm_fine.npz`). Stator outer radius is132.5mm; slot outer radius remains115mm. Rotor,1-mm gap,0.7-T PMs and+6.2/-6.7A/mm² excitation remain unchanged. The6-pole yoke maximum is1.695T, its area-weighted95th percentile is0.906T, and its selected air-gap harmonic is0.50436T (about0.55% below the25-mm baseline). The12-pole selected harmonic is0.50146T. Both nonlinear residuals pass1e-6. Rotor peaks remain2.95T and flux matching/harmonics remain open design tasks.

Run `basic_he_ipm_fea.py --yoke-17p5` to regenerate the annotated, steel-only, reference-style plots from cached fields. Their names end in `_17p5mm`. Earlier25-mm results are retained for comparison.

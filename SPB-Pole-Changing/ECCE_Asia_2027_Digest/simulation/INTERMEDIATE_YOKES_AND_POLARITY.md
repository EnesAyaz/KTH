# Intermediate yokes and rotor-polarity diagnostic

## Intermediate yokes

The 15-mm and 20-mm cases retain the same slots, rotor, excitation currents, synthetic B-H curve, 1-mm air gap, and 720-division angular mesh. Results are no-load comparisons, not equal-torque or thermal optimization.

| Yoke thickness | 6-pole yoke B, area-weighted 95th percentile | 6-pole yoke local maximum | Selected air-gap harmonic reduction from baseline | Stator steel area reduction |
|---|---:|---:|---:|---:|
| 25 mm | 0.671 T | 1.560 T | baseline | baseline |
| 20 mm | 0.801 T | 1.643 T | 0.32% | 14.17% |
| 15 mm | 1.043 T | 1.757 T | 0.87% | 27.81% |
| 10 mm | 1.444 T | 1.940 T | 2.24% | 40.95% |

Both intermediate cases solve to nonlinear relative residual below 1e-6. The 15-mm case offers a useful next candidate for loaded FEA; 20 mm retains more stator iron margin. No final dimension is selected from these no-load data alone. Rotor local concentrations remain close to 2.95 T throughout.

## Why the magnitude maps look alike inside the rotor

The physical rotor geometry, fixed magnet locations, and excitation-coil locations do not move between states. The six wound sites reverse polarity; magnet polarities remain fixed. Magnitude |B| is nonnegative, so reversing a local field can leave its magnitude nearly unchanged. Local flux concentrations and return/leakage paths can therefore look similar even while the external field order changes.

At the twelve physical rotor sites, the calculated air-gap signs are:

- 12-pole setting: N S N S N S N S N S N S.
- 6-pole setting: N N S S N N S S N N S S.

Adjacent equal-polarity sites form one wider magnetic pole in the second state. The actual signed radial air-gap waveform at radius 80.5 mm has 12 versus 6 zero crossings around one mechanical revolution. The dominant Fourier order changes from 6 pole pairs to 3 pole pairs. This is a rotor-field result, not an assumption from the stator winding.

The independent circular sampling gives approximately:

| Field setting | 3-pair component | 6-pair component | 9-pair component |
|---|---:|---:|---:|
| 12-pole | 0.0419 T | 0.5007 T | 0.0207 T |
| 6-pole | 0.5065 T | 0.0448 T | 0.2208 T |

The 9-pair component is the third spatial harmonic of the 6-pole fundamental and is about 44% of that fundamental. Thus the exploratory rotor has a real harmonic-quality problem even though the principal pole count changes correctly. This reinforces the need for barrier, magnet, excitation and pole-shape optimization before torque, ripple, losses or speed capability are claimed. It is not enough to inspect warm colors or verify only cancellation between the two selected orders.

`plot_rotor_polarity.py` makes a signed radial-field plot (red outward/N, blue inward/S) and the actual air-gap waveform. Values outside +/-1.5 T in the rotor-only display are clipped and identified by colorbar extensions. N/S labels and arrow directions are derived from sampled FEM fields. Signed radial flux is a polarity diagnostic; it is not interchangeable with the magnitude |B| saturation display.

## Files

- `results_saturation_screen/intermediate_yokes_fine.json` and `yoke_15mm_fine.npz`, `yoke_20mm_fine.npz`.
- `results_saturation_screen/rotor_polarity_check.json`.
- `../figures/rotor_polarity_check.png` and `.svg`.

The current digest remains the earlier baseline. These results provide additional design and validation evidence for a subsequent revision rather than silently replacing its geometry.

# ICPE gate-loop rerun

The full paper uses actual LTspice 10 nH and 20 nH gate-loop reruns with separate 0.5 nH and 1 nH commutation loops. Original drafts and source models are preserved.

## Reproduction

Run `scripts/icpe_gate_loop_rerun.py`, `scripts/icpe_board_gate_rerun.py`, `scripts/icpe_gate_analysis.py`, `reports/paper/icpe/make_rerun_figures.py`, and `reports/paper/create_full_paper_gate_rerun.py` in that order with the bundled Python runtime. LTspice and Inkscape use their local installations.

The simulation folder contains the exact netlists and saved waveforms. Some executed netlists retain native `.meas` declarations whose windows fail after LTspice applies the RAW save-time offset; those declarations do not supply any manuscript numbers. All published measurements are recomputed from RAW waveforms by `icpe_gate_results.py`, which adds the header Offset before selecting the absolute-time windows. The current runner omits these unused native declarations. RAW integration was independently checked against an unchanged original native measurement. The input hashes document the files used for this manuscript.

## Modeling and interpretation

The nominal device-model temperature is 27 C. Preliminary drive: +5/-1 V, 3/1 ohm external on/off resistors, 0.85/0.35 ohm driver source/sink resistance. Driver current limiting and timing spread are not represented. Screening losses use sinusoidal interpolation of simulated event energies and the established complementary-device output-energy term; conduction resistance and temperature iterate with ambient 40 C, shared heatsink resistance 0.65 K/W, and per-device junction-to-heatsink resistance 7.6167 K/W. Switching-energy temperature dependence is not modeled.

Four devices pass the peak-current screen at 0.5 nH for both gate-loop cases. This is not full-current-range voltage compliance: low-current resonant peaks exceed the project target. The 1 nH power-loop cases fail. Routed operating-board gate models remain assumed branches; the DPT gate model is extracted. In the extracted driver path, 1/1.5 ohm shared turn-on resistance plus 0.5 ohm individual gate resistors gives effective on resistance 2.5/3.5 ohm under equal pair currents. The individual resistors remain in the off path. Lumped DPT cases can violate the negative gate rating, and the extracted DPT case still exceeds the 90 V drain target.

SVG files are editable in Inkscape. PDF and PNG exports are included alongside each SVG. Word layout was checked on all 13 pages. Prior documents are unchanged.

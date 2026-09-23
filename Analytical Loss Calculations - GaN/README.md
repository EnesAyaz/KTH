# EPC2361 analytical loss calculator

Defaults: **75 V DC bus, 40 A AC RMS, one EPC2361 per switch position**, 100 kHz sinusoidal PWM, modulation index 1.0. The half bridge contains two FETs total.

- `python loss_calculator.py` opens the loss calculator.
- `python waveform_plotter.py` opens the waveform plotter.
- `python -c "from waveform_plotter import save_waveforms; save_waveforms()"` exports `output/switching_waveforms.png`.
- `python -m unittest -v test_loss_model.py` runs the numerical checks.

Requires Python, NumPy, Matplotlib, and Tkinter for the GUIs. Headless export/testing supports `MPLBACKEND=Agg`.

The side-by-side waveform drawing follows AN030 Figures 2/3: red VDS, dashed green IDS, blue VGS, and gray instantaneous overlap power. Signed dv/dt and di/dt plus the separate turn-on/off overshoot estimates appear below each panel. Each trace has its own vertical scale. Time spacing is schematic to keep the short intervals visible; the labeled ns durations are calculated. `build_waveforms()` returns physical seconds, volts and amps, and its power integral matches the analytical overlap energy. The power at turn-off is correctly labeled Poff.

40 A retains the original calculator's AC RMS interpretation: sinusoidal peak is 56.57 A and mean absolute current is 36.01 A. The plot defaults to peak current. Set `waveform_current_a=40` (GUI: Plot current) to illustrate a 40 A switching event without changing the RMS loss calculation. A DC-load loss model is not implemented.

See [LOSS_MODELING.md](LOSS_MODELING.md) for corrected equations, assumptions, and source references; [APPLICATION_NOTE_REVIEW.md](APPLICATION_NOTE_REVIEW.md) records the review of all 59 notes. The updated `LOSS_MODELING.tex` and `LOSS_MODELING.pdf` document the current model without a table of contents or a paralleling section.

The preserved 2 nH loop inductance produces a rough L*di/dt stress estimate above the 100 V device rating. It is reported, not hidden. Gate-charge timing and curve-derived parameters are first-order estimates, not measured switching/thermal performance.

The default iterative thermal mode updates RDS(on) from the datasheet temperature curve until thermal balance converges. The GUI reports Tj and updated RDS(on). Default case-mode results: 50.4922 C, 1.16335 mOhm, and 4.95047 W total loss. Select manual RDS mode to use the fixed multiplier instead. The solver rejects temperatures outside the supported 0..150 C curve and reports nonconvergence explicitly.

# LMG1210 PWM and independent-input tests

Double-click `Open-PWM.cmd` or `Open-IIM.cmd` to open and run the respective schematic with the Alternate solver. Alternatively open the .asc, select Alternate solver in LTspice settings, then Run. Normal solver stalled on the PWM test. Keep this folder and its sibling `../models` folder together. Local symbols and the model wrapper are included.

Verified at both 50 and 100 kHz: VDD approximately 5.003 V, gate outputs approximately 0 to 5 V, and no simultaneous outputs above 2.5 V for the supplied commands. IIM measured dead intervals are 197.9-201.6 ns. PWM intervals are 2.85-6.80 ns at 2.5 V crossings, shorter than the nominal 7.2 ns resistor formula; do not treat this adapted model as precision dead-time validation. See mode-test-results.json for each run.

Both schematics sweep 50 kHz and 100 kHz. Saved `.plt` settings display inputs and gate outputs; if no traces appear, use Plot Settings > Open Plot Settings File and select the corresponding `.plt`. Plot `V(HO,HS)` for the high-side gate voltage, not HO relative to ground. With HS fixed at 75 V, HO itself is near 75-80 V. The low-side gate voltage is `V(LO)`.

## Test arrangements

| Test | Inputs | Mode selection | Dead time |
|---|---|---|---|
| IIM | Independent HI and LI pulses | DLH and DHL connected to VDD | Controller pulse sources provide nominal 200 ns |
| PWM | EN and single PWM | DHL and DLH each have 100 kohm to ground | Internal timing; nominal formula gives about 7.2 ns |

VIN ramps to 12 V. The internal regulator supplies VDD and has a 1 uF output capacitor. Inputs start at 300 us, allowing the regulator and mode-selection circuitry to settle. Outputs each drive a 1 nF capacitor. HB is supplied by an ideal 5 V source relative to HS; HS is held at 75 V DC. BST is unloaded. Thus these tests check mode behavior and output drive under a static high-side common-mode voltage, not a complete bootstrap circuit, moving switch node or EPC2361 half bridge.

In IIM there is no separate enable input and no automatic prevention of overlapping commands. Both inputs low turns both outputs off. Do not tie HI high as if it were EN in this mode.

## Model provenance and limits

Original: TI SNOM677 unencrypted PSpice LMG1210 model, Final 2.2. https://www.ti.com/lit/zip/snom677

The separate local LTspice adaptation normalizes nested braces in behavioral VALUE expressions, handles continuation lines across comments, and removes an inline PSpice comment marker. It does not intentionally replace the driver's circuit with ideal logic. The original library remains preserved under `../models/ti-lmg1210/original`.

LTspice warns that two internal diode models have N=0.01 and clamps this to 0.1. The tests can establish functional behavior of this adaptation; they do not establish exact equivalence to PSpice or guarantee nanosecond timing accuracy of real hardware. Gear integration is used for numerical stability. Measured output dead time depends on output load, threshold and propagation mismatch, and need not equal the resistor formula exactly.

`mode-test-results.json`, when present, records waveform-derived checks. `scripts/check_lmg1210_modes.py` checks regulator voltage, output swing, simultaneous conduction at the 2.5 V gate threshold and measured dead intervals at both frequencies. These driver-only tests cannot establish power-stage shoot-through or switching energy.

Batch command: `LTspice.exe -b -Run -alt <absolute-path-to-test.asc>`. Both `-b` and `-Run` were needed for the installed version to run a schematic from the command line.

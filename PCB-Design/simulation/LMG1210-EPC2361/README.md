# LMG1210 + EPC2361 half bridge
Open Open-HalfBridge.cmd to run using LTspice Alternate solver, or open LMG1210_EPC2361_halfbridge.asc and choose Alternate solver before Run. Keep this directory beside ../models. Local symbols and model dependencies are supplied.

Two transistors total: QH high-side and QL low-side, each the user's EPC2361 model copied unchanged. Subcircuit pin order is gate, drain, source. The LMG1210 uses independent-input mode: DHL and DLH tied to VDD. HI and LI are separate nonoverlapping 3.3 V pulse sources with nominal 200 ns dead time. There is no independent enable/interlock in this mode.

Initial operating point: 75 V bus, 12 V driver input, 50 kHz, approximately 50% duty, 10 uH series inductor and 2 ohm grounded load. Low-side pulses start at 300 us, high-side pulses half a period later, providing bootstrap precharge. This is a synchronous buck-style test load connected to a half bridge, not a complete AC inverter or the earlier 36.7 A RMS qualification.

Bootstrap: BST -> generic diode -> HB, with 100 nF from HB to SW. VDD decoupling is 1 uF. Gate resistors are 2 ohms externally, in addition to resistance internal to the supplied EPC model. The generic diode is a simulation placeholder, not a selected or validated BOM component. Bus resistance is 10 milliohms with 10 uF local decoupling. No extracted PCB/package interconnect inductance or capacitor ESL is added.

Saved plots show HI/LI, both VGS voltages and bootstrap voltage, switch/load voltage and inductor current. Always measure high-side gate as V(GH,SW), not GH relative to ground. To see VDS, plot V(BUS,SW) for QH and V(SW) for QL. Zoom around a switching edge to inspect gate transitions.

Model limitations: TI's unencrypted PSpice driver model is locally adapted for LTspice, as documented in ../LMG1210-modes/README.md. LTspice clamps internal diode emission coefficients; precision dead-time, overshoot and loss predictions are not validated. This test adds moving-switch-node and bootstrap behavior but does not establish actual hardware parasitics, thermal limits or robustness.

FSW is a parameter. If changed to 100k, the pulse period and first high-side pulse automatically follow it. Only frequencies explicitly recorded in the results have been tested.
## Verified run (50 kHz)
LTspice Alternate solver completed in 86.3 seconds. Source stepping recovered the initial operating point after direct Newton/Gmin attempts failed.
- VDD at 399 us: 5.003 V.
- Bootstrap HB-SW: 4.353 to 4.619 V.
- High-side VGS: -0.045 to 4.398 V.
- Low-side VGS: -1.034 to 5.044 V.
- Switch node: -3.256 to 74.976 V.
- Load current: 4.139 to 32.679 A; average over the final period: 18.303 A.
- No sampled simultaneous gate voltages above 2.5 V in the checked 330-400 us interval. This is a waveform check, not proof of absence of device cross-conduction.
- Functional switching check passed; not a hardware sign-off. The low-side negative VGS transient warrants investigation. High-side gate drive is below 5 V because the bootstrap diode and discharge reduce its supply.

The current run logs four internal TI-model diode emission-coefficient warnings (displayed as a near-zero value and clamped to 0.1), rather than the two reported in the earlier standalone test. The unmodified log is preserved. This reinforces that the adapted model is exploratory, not timing-qualified. Do not use these waveforms as validated loss or peak-stress predictions.

Recheck with scripts/check_epc_halfbridge.py from the repository root. Detailed extrema are saved in results.json; simulator measurements are in the .log. The EPC2361 library is copied unchanged from the user's supplied path.

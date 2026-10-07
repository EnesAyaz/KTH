# Building block: LTspice loss and gate-resistor model

One phase leg, 2 x EPC2361 per switch, LT8418-like driver in the middle, with the Q3D copper of the building block (`../bb_q3d/results/BB_PL.lib` power loop, `BB_GL.lib` gate star). Report: `reports/building-block/bb_report.pdf`.

| File | Purpose |
| --- | --- |
| `BB_circuit.inc` | shared circuit: Q3D subcircuits, 4 x EPC2361, local + bank MLCCs, 20 nH bus + bulk, load, split-output driver with per-FET Rg_on / Rg_off, measurements |
| `BB_DPT.cir` | **open this one**: single double pulse at 141 A, Rg_on 2 ohm / Rg_off 0 ohm |
| `BB_rg_sweep.cir` | 160 A, Rg_on 0.5-4 ohm x Rg_off 0-1 ohm (18 runs, ~12 min) |
| `BB_energy_sweep.cir` | Eon / Eoff vs current 10-160 A with the selected Rg (~5 min) |

Results, gate-resistor choice and losses: `python scripts/bb_losses.py` (reads the two sweep logs), waveforms: `python scripts/bb_waveforms.py`.

Two LTspice pitfalls this model avoids:

* Node names are case-insensitive: the gate-star output `GLL` and the FET gate `gLL` would be the same node. FET gate nodes are named `gtLL`, `gtLR`, `gtHL`, `gtHR`.
* `.meas` time windows are evaluated once, not per `.step`. For a current sweep, keep `TON1` fixed and step the load inductance (`LLOAD = TON1*VBUS/IPK`), as in `BB_energy_sweep.cir`.

Selected: Rg_on = 2 ohm, Rg_off = 0 ohm per FET (peak VDS <= 90 V and off-state gate bump <= 1 V at 160 A). At 141 A: Eon 42 uJ, Eoff 8 uJ per switch position.

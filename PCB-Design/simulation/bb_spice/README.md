# Building block: LTspice loss and gate-resistor model

One phase leg, 2 x EPC2361 per switch, LT8418-like driver in the middle, with the Q3D copper of the building block (`../bb_q3d/results/BB_PL.lib` power loop, `BB_GL.lib` gate star). Report: `reports/building-block/bb_report.pdf`.

| File | Purpose |
| --- | --- |
| `BB_circuit.inc` | shared circuit: Q3D subcircuits, 4 x EPC2361, local + bank MLCCs, 20 nH bus + bulk, load, split-output driver with per-FET Rg_on / Rg_off, measurements |
| `BB_DPT.cir` | **open this one**: single double pulse at 141 A, Rg_on 2 ohm / Rg_off 0 ohm |
| `BB_rg_sweep.cir` | 160 A, Rg_on 0.5-4 ohm x Rg_off 0-1 ohm (18 runs, ~12 min) |
| `BB_energy_sweep.cir` | Eon / Eoff vs current 10-160 A with the selected Rg (~5 min) |

Results, gate-resistor choice and losses: `python scripts/bb_losses.py` (reads the two sweep logs), waveforms: `python scripts/bb_waveforms.py`.

## Schematics (open in LTspice)

Double-click `Open-BB.cmd` (opens `BB_DPT.asc`), or open any `.asc` in LTspice and press Run. The symbols `BB_PL.asy`, `BB_GL.asy` and `EPC2361.asy` sit next to the schematics.

| Schematic | What it runs |
| --- | --- |
| `BB_DPT.asc` | single double pulse at 141 A, Rg_on/Rg_off = 2/0 ohm (~1 min) |
| `BB_energy_sweep.asc` | Eon / Eoff vs current, 10-160 A (~5 min) |
| `BB_rg_slow.asc` | slow switching at 141 A: `.step` Rg_on 2 / 10 ohm x Rg_off 0 / 2 / 5 / 10 ohm (8 runs) |

Parameters are at the top of the directive column on the right (VBUS, IPK, RGON, RGOFF, ...). Results: View > SPICE Error Log
(Ctrl+L) lists the `.meas` values; with `.step`, right-click in the log > Plot .step'ed .meas data. Use `Eon400` / `Eoff400`
(400 ns window, only while V_DS > 1 V) for slow switching; `Eon` / `Eoff` are the original 150 ns windows.
Useful probes: `V(QL_D_L,QL_S_L)`, `I(VILL)`, `I(VILR)`, `V(gtLL,QL_S_L)`, `V(gtHL,QH_S_L)`, `I(Lload)`.

Every element is placed with net-label flags on its pins (no wires); nets with the same name are connected. The
schematics are generated from `BB_circuit.inc` by `python scripts/make_bb_asc.py`; edit the netlist and rerun the script.
LTspice's netlist of `BB_DPT.asc` was checked against `BB_circuit.inc` (49 elements, identical connections) and gives
the same results (Eon 42.1 uJ, Eoff 8.1 uJ, QL peak 86.6 V at 139 A).

The slow-switching netlists used for the report (6 Rg pairs x 7 currents) are in `slow/`; post-processing:
`python scripts/slow_switching.py`.

Two LTspice pitfalls this model avoids:

* Node names are case-insensitive: the gate-star output `GLL` and the FET gate `gLL` would be the same node. FET gate nodes are named `gtLL`, `gtLR`, `gtHL`, `gtHR`.
* `.meas` time windows are evaluated once, not per `.step`. For a current sweep, keep `TON1` fixed and step the load inductance (`LLOAD = TON1*VBUS/IPK`), as in `BB_energy_sweep.cir`.

Selected: Rg_on = 2 ohm, Rg_off = 0 ohm per FET (peak VDS <= 90 V and off-state gate bump <= 1 V at 160 A). At 141 A: Eon 42 uJ, Eoff 8 uJ per switch position.

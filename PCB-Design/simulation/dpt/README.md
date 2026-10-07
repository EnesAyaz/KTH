# LTspice double-pulse test: Q3D PL_A loop + EPC2361

`DPT_PL_A.cir`: low-side DPT of the board's half bridge, two cells in parallel. Each cell uses the Q3D copper matrix `../q3d/results/PL_A.lib` (one MLCC bank next to QH, L2 = DC−), with an EPC2361 QH and QL (`../LMG1210-EPC2361/EPC2361.lib`, EPC model) and a local MLCC bank.

**Run:** double-click `Open-DPT.cmd` (or open `DPT_PL_A.asc` in LTspice) and press Run. It takes about 2 min for both gate-routing steps; the Alternate solver is used by the launcher. For results only, run `run_dpt.cmd` and read `DPT_PL_A.log`. Then `python plot_dpt.py` writes `DPT_PL_A.png`.

**Schematic:** `DPT_PL_A.asc` is generated from `DPT_PL_A.cir` by `python scripts/make_dpt_asc.py`. Every part is a symbol with net-label flags on its pins (no drawn wires), grouped by section; the `.param`, `.step` and `.meas` directives are on the right. `PL_A.asy` (Q3D copper block) and `EPC2361.asy` must stay in this folder. Edit the `.param` directives directly in the schematic, or change the netlist and regenerate. Both give identical results (checked: 86.29 V / 117.0 V QH peak for star / direct routing).

Useful plots: `V(qld1,qls1)`, `V(qhd1,qhs1)`, `I(Vidl1)`, `I(Vidl2)`, `V(gl1x,qls1)`, `V(gh1x,qhs1)`, `I(Lload)`.

## Circuit

| Part | Model | Parameter |
| --- | --- | --- |
| Bus | 75 V supply, 1 µH / 50 mΩ cable, 1.54 mF bulk (15 mΩ, 3 nH) | VBUS, CBULK, RBULK, LBULK |
| Load | 20 µH, 5 mΩ, 20 pF, SW to DC+ | LLOAD, IPK sets TON1 = L·I/V = 32 µs |
| Copper | 2 × PL_A subcircuit (Q3D, 100 MHz partial R/L + K) | rerun `../q3d/run_q3d.cmd` to update |
| Between cells | DC+ / DC− distribution 1 nH each, AC collector 0.5 nH, no cell-to-cell coupling | LDIST, LAC |
| MLCC bank / cell | 3 µF effective at 75 V (6 × 1 µF, 50 % DC bias assumed), 1 mΩ, 0.08 nH | CMLCC, RMLCC, LMLCC |
| Driver | LT8418-like: 5 V, 0.6 Ω pull-up / 0.2 Ω pull-down (split outputs, ideal diodes), 0.5 nH trunk | VDRV, RPU, RPD, LTRUNK |
| Gate branch / FET | Rg_on 2 Ω, Rg_off 0.01 Ω, gate loop L from Q3D, Kelvin returns 0.1 Ω to the driver star | RGON, RGOFF, LG1/LG2, RKS |
| QH | held off at 0 V through the pull-down | |

`.step param GATEMODE list 0 1`: 0 = star routing (2.1 / 2.1 nH), 1 = direct from a left driver (2.0 / 7.7 nH, Q3D GL_near / GL_far).

## Results (1 Oct 2026, 117 A switched)

Rg_on sweep, star routing:

| Rg_on | QH VDS peak | QL peak ID | Eon per FET | VDS fall |
| --- | --- | --- | --- | --- |
| 1 Ω | 104 V (over rating) | 146 A | 13.9 µJ | 3.9 ns |
| 1.5 Ω | 92.5 V | 132 A | 16.2 µJ | 4.3 ns |
| **2 Ω (default)** | **86.3 V** | 121 A | 18.4 µJ | 4.8 ns |
| 3 Ω | 80.2 V | 107 A | 22.1 µJ | 5.7 ns |
| 4 Ω | 77.8 V | 101 A | 25.5 µJ | 6.4 ns |

Turn-off does not depend on Rg_on: QL VDS 82.3 V, Eoff 3.9 µJ per FET, rise 3.3 ns.

Rg_on = 2 Ω, star vs direct gate routing:

| | Star | Direct |
| --- | --- | --- |
| QL VDS at turn-off | 82.3 V | 86.9 V |
| QH VDS at QL turn-on | 86.3 V | 117 V |
| Peak ID QL1 / QL2 (turn-on) | 121 / 121 A | 138 / 163 A |
| Eoff QL1 / QL2 | 3.9 / 3.9 µJ | 6.9 / 4.5 µJ |
| Eon QL1 / QL2 | 18.4 / 18.4 µJ | 23.0 / 18.5 µJ |
| QH VGS bump (QL turn-on) | 1.00 V | 0.55 V (cell 1) |
| QL VGS minimum (turn-off) | −0.88 V | −1.77 V |

## Limits of this model

* The EPC model has no package inductance; the copper matrix is at 100 MHz only (no frequency-dependent R), so ringing is under-damped compared with hardware.
* MLCC DC-bias derating (CMLCC) is assumed, not from TDK data.
* The high-side off-state gate bump (~1 V at Rg_on 2 Ω) is near the 0.8 V minimum threshold. If the hardware shows shoot-through current, lower the high-side gate loop inductance or slow turn-on further.
* Cell-to-cell mutual inductance is not in the model (only one Q3D cell); a two-cell Q3D run would add it.

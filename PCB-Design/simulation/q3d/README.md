# Q3D model: EPC2361 DPT power loop, three MLCC arrangements

Parametric pre-layout model of one vertical cell (no shunt, no gate loop). Same method as the SiC busbar model (`DC-Bus Current Modelling/Ansys/Busbarfinal.aedt`): **only copper is modelled; every component (MLCC bank, QH, QL) is a gap with a source/sink terminal on each of its pads.** Each copper region is one Q3D net (one sink, one or more sources), so the result is the partial R/L matrix of the copper. `q3d_to_spice.py` turns that into an LTspice subcircuit. Sketches with every variable: `docs/q3d-geometry-sketches.html`.

| Design | MLCC placement | Inner layers |
| --- | --- | --- |
| PL_A | one bank next to QH (EPC "optimal" loop) | L2 = DC− |
| PL_B | one bank between QH and QL | L2 = AC (switch node) |
| PL_C | bank A next to QH + bank B next to QL | L2 = DC−, L3 = DC+, spacing `h_23` |

## Run

Needs AEDT 2024 R2 and the KTH licence server (`ANSYS-STUD-LIC.UG.KTH.SE:1055`), i.e. campus network or KTH VPN.

```
simulation\q3d\run_q3d.cmd              # all designs + h_23 sweep + LTspice files (~15 min)
simulation\q3d\run_q3d.cmd only PL_C    # rebuild/solve one design in the existing project
simulation\q3d\run_q3d.cmd spice        # only rebuild LTspice files from results\*_matrix.txt
```

Change geometry in `results\dpt_cell_q3d.aedt` (Design Properties → Local Variables) or in the `VARS_*` lists at the top of `q3d_dpt_cell.py`. Sweeps: the `SWEEP` dict near the end of the script (each point is one extra solve).

## Results (100 MHz, all converged, 1 Oct 2026, h_diel = 0.1 mm)

Effective loop inductance at the QL switch, with QH shorted and each MLCC bank shorted (ideal, or with 0.48 nH / 6 = 0.08 nH ESL per bank). The EPC2361 package is not included.

| Design | Banks | L copper | L with MLCC ESL | R (100 MHz) |
| --- | --- | --- | --- | --- |
| PL_A | 1 | 0.310 nH | 0.390 nH | 7.8 mΩ |
| PL_B | 1 | 0.303 nH | 0.383 nH | 7.6 mΩ |
| **PL_C, h_23 = 0.1 mm** | 2 | **0.288 nH** | **0.333 nH** | 7.3 mΩ |
| PL_C, h_23 = 0.5 mm | 2 | 0.303 nH | 0.362 nH | 7.5 mΩ |
| PL_C, h_23 = 1.2 mm (standard 4-layer core) | 2 | 0.306 nH | 0.372 nH | 7.7 mΩ |

LTspice (`*_test.cir`) reproduces every "L copper" value to 4 digits.

## Using the matrix in LTspice

`results/<design>.lib` contains `.subckt <design> <terminals>`: one R–L branch per Q3D source (source terminal → its net's sink terminal) plus a `K` line for every mutual inductance. `results/<design>_L.csv` is the same inductance matrix as a table.

```
.include PL_A.lib
X1 CapN CapP QH_D QH_S QL_D QL_S PL_A
```

Connect the real parts between the terminals, for example for PL_A:

* MLCC bank (6 × 1 µF, ESR, 0.08 nH) between `CapP` and `CapN`
* QH (EPC2361 model): drain `QH_D`, source `QH_S`; QL: drain `QL_D`, source `QL_S`
* DC supply / bulk to `CapP`/`CapN`, load inductor between `QH_S` (= switch node) and DC+ (`CapP`) for the low-side DPT
* PL_C: bank A between `CapAP`/`CapAN`, bank B between `CapBP`/`CapBN`

Pin order is the `.subckt` line (alphabetical). The values are AC (100 MHz) partial inductances, which are right for switching edges. The DC/low-frequency inductance is higher (current spreads), so do not use this model for the slow inductor ramp.

## Files

`q3d_dpt_cell.py` (Q3D model), `q3d_to_spice.py` (matrix → `.lib`, `_L.csv`, `_test.cir`, `summary.csv`), `run_q3d.cmd`. `results/<design>_terminals.txt` lists net, sink, sources and the variable values used.

# Q3D model: EPC2361 DPT cell loop inductance

Parametric pre-layout model of one vertical cell (MLCC → QH → QL → 1 mΩ shunt → In1 return) and the low-side gate loop. Same method as the SiC busbar model (`DC-Bus Current Modelling/Ansys/Busbarfinal.aedt`): **only copper is modelled; every component is a gap with a source/sink terminal on each of its pads.** Each copper region between two components is its own net, so Q3D gives the partial self/mutual inductance matrix, which converts to an LTspice subcircuit. Rerun with the real geometry once the KiCad layout exists.

## Run it

Needs AEDT 2024 R2 and the KTH licence server (`ANSYS-STUD-LIC.UG.KTH.SE:1055`): campus network or KTH VPN.

```
simulation\q3d\run_q3d.cmd          # build + solve + h_diel sweep + export + SPICE (~25 min)
simulation\q3d\run_q3d.cmd export   # only re-export from results\dpt_cell_q3d.aedt, then SPICE
python simulation\q3d\q3d_to_spice.py   # only rebuild .lib files and summary.csv
```

To change geometry, open `results\dpt_cell_q3d.aedt` in AEDT, select a design, open Design Properties (Local Variables tab), edit, then Analyze All and `run_q3d.cmd export`. To sweep, use Optimetrics → Parametric on any variable, or edit `SWEEP` near the end of `q3d_dpt_cell.py`. Defaults live in `POWER_VARS` / `GATE_VARS` at the top of that file.

## Nets and terminals

| Design | Net | Source → Sink | What it is |
| --- | --- | --- | --- |
| PL_* | DCP | CapP (6 MLCC + pads) → QH_D | DC+ copper, caps to high-side drain |
| PL_* | AC | QH_S → QL_D | Switch node copper |
| PL_shunt | SQL | QL_S → SH_in (5 pads) | QL source island to shunt input |
| PL_shunt | DCN | SH_out (5 pads) → CapN (6 MLCC − pads) | DC− landing, vias, In1 return, cap vias |
| PL_noshunt | DCN | QL_S → CapN | Same without shunt |
| GL_* | G | DrvOut → Gate | Gate trace on L1 |
| GL_* | KS | Kelvin → DrvGnd | Kelvin via, return on In1 under the trace |

All sources point along the loop, so **Lloop = sum of all ACL(i,j)** (output variable `Lloop` in each design). The components themselves are not in Lloop. Add them in SPICE: MLCC ESL 0.48 nH / 6, EPC2361 package, shunt R + ESL.

## Main variables (power loop)

| Variable | Default | Meaning |
| --- | --- | --- |
| h_diel | 0.1 mm | L1–In1 dielectric: vertical spacing of + (L1) and − (In1) copper, the PCB equivalent of the busbar insulation |
| gap | 0.6 mm | Lateral gap between L1 islands (DC−/DC+/AC/source), i.e. component pad spacing |
| w_cell / w_sh | 9 / 17 mm | Island widths (cell / shunt region) |
| l_dcp, l_ac, l_s, l_dcn | 3.1 / 3.7 / 2.4 / 1.4 mm | Copper lengths along the loop |
| t_L1, t_L2 | 70 / 35 µm | Copper thickness |
| fet_w, fet_pad, cap_p, sh_p | 5 / 1 / 1.4 / 3.4 mm | Pad geometry and pitches |

## Results (100 MHz AC, all designs converged, 1 Oct 2026)

| Design | Lloop (copper) | Main self terms |
| --- | --- | --- |
| PL_shunt, h_diel 0.075 mm | 0.299 nH | DCN 0.464, AC 0.078, DCP 0.060, SQL 0.025 |
| **PL_shunt, h_diel 0.1 mm** | **0.341 nH** | DCN 0.502, AC 0.078, DCP 0.060, SQL 0.025 |
| PL_shunt, h_diel 0.2 mm | 0.496 nH | DCN 0.647 |
| PL_noshunt, h_diel 0.1 mm | 0.311 nH | DCN 0.466, AC 0.080, DCP 0.061 |
| GL_near (8 mm) | 2.01 nH | G 4.89, KS 4.03 |
| GL_far (25 mm) | 7.67 nH | G 23.8, KS 18.9 |

Outputs in `results/`: `<design>.csv` (Lloop + full ACL matrix + ACR), `<design>_matrix.txt` (full Q3D export), `<design>.lib` (LTspice subcircuit: R–L per net + K couplings), `summary.csv`.

v1 of this model (before 1 Oct 12:00) merged everything into one net with caps/QH as copper blocks; its numbers (0.248 / 0.223 nH) are superseded.

# Building block: Q3D extraction

Symmetric phase leg (2 x EPC2361 per switch, driver in the middle). Geometry: `bb_geometry.py` (shared with the layout drawings in `scripts/bb_layout_drawings.py` and `docs/building-block-layout.html`). Stack-up thicknesses are AEDT design variables.

```
simulation\bb_q3d\run_bb_q3d.cmd          # BB_PL + BB_GL, then LTspice subcircuits (~60 min, KTH VPN)
simulation\bb_q3d\run_bb_q3d.cmd spice    # only rebuild results\*.lib and summary.json
```

2 oz inner-layer variant (as used for the copper loss): set `BB_STACK=t_L2=0.07,t_L3=0.07`, `BB_SUFFIX=_2oz`, `BB_ONLY=BB_PL` and run `ansysedt -ng -RunScriptAndExit bb_q3d.py`.

| Design | Nets / terminals |
| --- | --- |
| BB_PL | DCP: CapB1P..3P, CapPL, CapPR, QH_D_L/R -> T_DCP; DCN: CapB1N..3N, CapNL, CapNR, QL_S_L/R -> T_DCN; AC: QH_S_L/R, QL_D_L/R -> T_AC |
| BB_GL | G: Gate_L, Gate_R -> DrvOut; KS: Kelvin_L, Kelvin_R -> DrvGnd (low-side gate star, return on L2) |

Results (1 oz inner / 2 oz inner): commutation loop per cell 0.312 nH copper, 0.374 / 0.376 nH with MLCC ESL; gate loop 1.70 nH per FET (2.21 nH both driven); DC resistance terminal-to-FETs DC+ 0.353 / 0.216 mOhm, DC- 0.420 / 0.226 mOhm, AC 0.146 mOhm.

The capacitance solve is set to 4 passes / 5 % to keep the run time down; inductance (AC) converges to 1 %.

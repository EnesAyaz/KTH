# Building block: Ansys Icepak thermal model

Steady-state, conduction-only model (AEDT 2024 R2 Icepak) of one phase leg at the rated point (50 kHz, 100 A rms),
built from `../bb_q3d/bb_geometry.py`. Needs the KTH licence (campus or VPN).

| Item | Model |
| --- | --- |
| board | anisotropic FR-4/Cu equivalent (in-plane 55 W/mK, through-plane 0.36 W/mK; 3.5 W/mK in the cell regions with via arrays) |
| EPC2361 x 4 | 1.91 W each; body R_th,jc ~ 0.2 K/W (top), bump layer R_th,jb ~ 1.5 K/W |
| cooling | 0.5 mm gap pad (17.8 W/mK, 1.9 K/W per device), Al pedestals, 3 mm Al plate, top face 60 C |
| losses | PCB copper 4.37 W (1 W in each cell region, rest uniform), MLCC ESR per group, driver 0.08 W |
| option `BB_COOL=both` | 1 mm bottom gap pad (3 W/mK) to a second Al plate at 60 C |

Run: `run_bb_icepak.cmd` (top cooling). Bottom cooling: set `BB_COOL=both` and run `bb_icepak.py` with
`ansysedt -ng -RunScriptAndExit` (the .cmd deletes the top-cooled project). `BB_POST=1` re-runs only the post-processing.

Results (max temperature):

| | top cooling | top + bottom |
| --- | --- | --- |
| EPC2361 | 71.8 C | 66.7 C |
| board | 103.9 C | 83.3 C |
| 1210 MLCC | 103.1 C | 83.1 C |
| driver | 91.5 C | 75.4 C |

Temperature maps: `python scripts/plot_icepak.py` (reads `results/grid_*.fld`). The board temperatures are conservative:
the copper loss is spread over the board thickness and convection is neglected.

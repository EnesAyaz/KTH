# SPB building block: KiCad placement

**PLACEMENT ONLY. NOT NETTED, NOT ROUTED. DO NOT FABRICATE.**

30 x 28.2 mm, 4 layers (2 oz), 2 x EPC2361 per switch in two mirrored cells, centre gate driver (LT8418), 24 x 10 uF 1210
bank + 12 x 1 uF 0805 local MLCCs, split gate resistors (0402), probe pads, busbar contact pads (DC+, DC- top; AC bottom).

The board is generated from the same geometry as the Q3D and Icepak models (`simulation/bb_q3d/bb_geometry.py`):
copper of all four layers is drawn as the graphic shapes used in Q3D (L1 strips and cell islands, L2 DC-, L3 DC+, L4 AC)
with the via rows.

| File | |
| --- | --- |
| `spb-building-block.kicad_pcb` | board (open in KiCad 7) |
| `models/` | EPC2361 and LT8418 envelope 3D models (VRML) |
| `render_iso.png`, `render_top.png` | 3D renders from the KiCad board and the footprints' 3D models |

Regenerate:

```
"C:\Program Files\KiCad\7.0\bin\python.exe" scripts\make_kicad_bb.py      # board
"C:\Program Files\KiCad\7.0\bin\python.exe" scripts\kicad_dump.py         # board + 3D model references -> JSON
python scripts\render_board.py                                             # 3D renders
```

KiCad 7 cannot export VRML without its GUI, so the renders are drawn by `render_board.py` from the board data and the
KiCad VRML models. In the KiCad GUI, View > 3D Viewer shows the same board.

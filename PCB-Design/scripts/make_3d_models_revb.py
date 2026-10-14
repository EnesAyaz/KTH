"""
Simple box 3D models (STEP + VRML) for the Rev B leg board parts that have no KiCad library model, written with the
Rev A writer (make_3d_models.py). Same conventions: mm, footprint origin, z = 0 on the board top, KiCad y down.

    python scripts/make_3d_models_revb.py  ->  hardware/spb-bb-revb-dpt/3d, hardware/spb-bb-revb-load/3d (*.step, *.wrl)

Dimensions (envelopes, NOT manufacturer CAD):
  2EDF7275K            5.0 x 5.0 x 1.0 mm (PG-TFLGA-13-4), as Rev A
  C_2220_5750Metric    TDK C5750X7S2A226M280KB: 5.7 x 5.0 x 2.8 mm, 0.6 mm terminations (KiCad has no 2220 5750 model)
  WE-CNSW 1206         Wurth 744232601: 3.2 x 1.6 x 1.9 mm (KiCad footprint has no model file)
  PMK_UFCS             PMK UFCS-R001: 0.7 mm blade 15 mm long up to 4.1 mm (soldered by its fillets to the two lands), body
                       22 x 7.5 mm above it (outline from the footprint fab layer), SMA jack on top (approximate)
  AC_BOLT_M6           M6 hex bolt (10 mm AF) + washer, 12 x 5 mm Cu bar from the pad off the board edge (y -7 .. 38.4),
                       nut + washer under the board
  HS_LAM4K5012_revb    Fischer LAM 4 K 50 12, tube along x (x -25 .. 25, y -28.7 .. 11.3, 40 x 40 mm) with the 12 V fan
                       at x -35 .. -25; Al spreader 89.5 x 12.8 x 3 mm (y -1.5 .. 11.3) on 0.6 mm pedestals over the four
                       FET pairs, 0.4 mm gap pads (compressed); spreader top at 4.68 mm clears the 2.8 mm 2220 bank
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_3d_models import MODELS, write_step, write_wrl, BLACK, SILVER, DARK, ALU, PAD, FAN  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTS = [os.path.join(ROOT, "hardware", b, "3d") for b in ("spb-bb-revb-dpt", "spb-bb-revb-load")]

CERAMIC = (0.62, 0.52, 0.38)
TIN = (0.80, 0.80, 0.78)
COPPER = (0.85, 0.50, 0.25)
STEEL = (0.65, 0.66, 0.68)
GOLD = (0.85, 0.70, 0.30)
FERRITE = (0.15, 0.15, 0.15)
WHITE = (0.92, 0.92, 0.90)

# FET pair centres (board coordinates; the heatsink footprint is placed at the origin)
PAIRS = [(-33.25, 7.05), (-14.25, 7.05), (14.25, 7.05), (33.25, 7.05)]
hs = []
for x, y in PAIRS:                                     # gap pad + pedestal over both FETs of a cell (y 4.9 and 9.2)
    hs.append((x - 2.8, y - 3.85, 0.68, x + 2.8, y + 3.85, 1.08, PAD))
    hs.append((x - 2.8, y - 3.85, 1.08, x + 2.8, y + 3.85, 1.68, ALU))
hs += [(-44.75, -1.5, 1.68, 44.75, 11.3, 4.68, ALU),   # spreader
       (-25.0, -28.7, 4.68, 25.0, 11.3, 44.68, ALU),   # LAM 4 K 50 tube (along x)
       (-35.0, -28.7, 4.68, -25.0, 11.3, 44.68, FAN)]  # fan

M = {
    "2EDF7275K_PG-TFLGA-13-4": MODELS["2EDF7275K_PG-TFLGA-13-4"],
    "C_2220_5750Metric_TDK": [(-2.85, -2.5, 0.0, -2.25, 2.5, 2.8, TIN), (-2.25, -2.5, 0.0, 2.25, 2.5, 2.8, CERAMIC),
                              (2.25, -2.5, 0.0, 2.85, 2.5, 2.8, TIN)],
    "L_CommonMode_Wurth_WE-CNSW-1206": [(-1.6, -0.8, 0.0, 1.6, 0.8, 1.9, FERRITE)],
    "PMK_UFCS": [(-7.5, -0.35, 0.0, 7.5, 0.35, 4.1, COPPER),
                 (-11.0, -3.75, 4.1, 11.0, 3.75, 9.1, BLACK),
                 (-3.2, -3.2, 9.1, 3.2, 3.2, 18.6, GOLD)],
    "AC_BOLT_M6": [(-6.0, -7.0, 0.035, 6.0, 38.4, 5.035, COPPER),
                   (-6.0, -6.0, 5.035, 6.0, 6.0, 6.235, STEEL), (-5.0, -5.0, 6.235, 5.0, 5.0, 10.235, STEEL),
                   (-6.0, -6.0, -2.835, 6.0, 6.0, -1.635, STEEL), (-5.0, -5.0, -7.835, 5.0, 5.0, -2.835, STEEL)],
    "HS_LAM4K5012_revb": hs,
}

if __name__ == "__main__":
    for OUT in OUTS:
        os.makedirs(OUT, exist_ok=True)
        for name, boxes in M.items():
            write_step(os.path.join(OUT, name + ".step"), name, boxes)
            write_wrl(os.path.join(OUT, name + ".wrl"), boxes)
    print("models", sorted(M), "->", OUTS)

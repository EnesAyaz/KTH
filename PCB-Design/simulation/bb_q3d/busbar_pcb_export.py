"""
Export the PCB busbar (hardware/spb-busbar) for Q3D (BB_BUS_PCB).

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" simulation\\bb_q3d\\busbar_pcb_export.py
    -> simulation/bb_q3d/results/busbar_pcb_geometry.json

mm, x = 0 at the centre of the middle leg, y in leg-board coordinates (same as the leg export).
  outline [x0, y0, x1, y1] (board), planes [layer, net] (L1 DCP, L2 DCN, L3 DCP, L4 DCN), pullback
  bolts [name, net, x, y, pad_d, hole_d]   name = L<leg>_<leg-board terminal ref> (J1, J2, J12, J13)
  lugs  [name, net, x, y, size, hole_d]    vias [net, x, y, r, pad_r]    keepouts [x, y, r] (all copper removed)
  pad_vias: bolt-pad via ring [net, x, y, r]
"""
import json
import math
import os

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BRD = os.path.join(ROOT, "hardware", "spb-busbar", "spb-busbar.kicad_pcb")
OX, OY = 160.0, 80.0
LEG_TERM = {-6.0: "J1", 6.0: "J2"}      # leg-board refs of the DC terminals (J1 DC+, J2 DC-)
PITCH = 94.5


def mm(v):
    return pcbnew.ToMM(v)


b = pcbnew.LoadBoard(BRD)
bb = b.GetBoardEdgesBoundingBox()
outline = [mm(bb.GetLeft()) - OX, mm(bb.GetTop()) - OY, mm(bb.GetRight()) - OX, mm(bb.GetBottom()) - OY]
bolts, lugs, pad_vias, keep = [], [], [], []
for f in b.GetFootprints():
    name = f.GetFPID().GetLibItemName().wx_str()
    x, y = mm(f.GetPosition().x) - OX, mm(f.GetPosition().y) - OY
    pads = [p for p in f.Pads() if p.GetNumber()]
    if name == "BUS_M4_REDCUBE":
        leg = int(round(x / PITCH))
        ref = LEG_TERM[min(LEG_TERM, key=lambda k: abs(x - leg * PITCH - k))]
        main = max(pads, key=lambda p: p.GetSize().x)
        bolts.append(["L%d_%s" % (leg + 2, ref), main.GetNetname(), round(x, 4), round(y, 4),
                      mm(main.GetSize().x), mm(main.GetDrillSize().x)])
        for p in pads:
            if p is not main:
                pad_vias.append([p.GetNetname(), round(mm(p.GetPosition().x) - OX, 4),
                                 round(mm(p.GetPosition().y) - OY, 4), mm(p.GetDrillSize().x) / 2])
    elif name == "BUS_LUG_M6":
        main = max(pads, key=lambda p: p.GetSize().x)
        lugs.append(["LUG_P" if main.GetNetname() == "DCP" else "LUG_N", main.GetNetname(), round(x, 4), round(y, 4),
                     mm(main.GetSize().x), mm(main.GetDrillSize().x)])
    elif name.startswith("MountingHole_3.2"):
        keep.append([round(x, 4), round(y, 4), 8.0])
vias = [[t.GetNetname(), round(mm(t.GetPosition().x) - OX, 4), round(mm(t.GetPosition().y) - OY, 4),
         mm(t.GetDrill()) / 2, mm(t.GetWidth()) / 2] for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
est = json.load(open(os.path.join(ROOT, "hardware", "spb-busbar", "estimates.json")))
out = dict(outline=outline, pullback=1.0, clearance=0.5,
           planes=[["L1", "DCP"], ["L2", "DCN"], ["L3", "DCP"], ["L4", "DCN"]],
           bolts=sorted(bolts), lugs=lugs, vias=vias, pad_vias=pad_vias, keepouts=keep, estimates=est)
json.dump(out, open(os.path.join(HERE, "results", "busbar_pcb_geometry.json"), "w"), indent=0)
print("outline", outline, "bolts", len(bolts), "lugs", len(lugs), "vias", len(vias), "pad vias", len(pad_vias),
      "keepouts", len(keep))
for bo in sorted(bolts):
    print(bo)

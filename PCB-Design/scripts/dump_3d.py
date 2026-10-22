"""
Dump the 3D content of a KiCad board for scripts/render_3d.py: every footprint's model (resolved path, offset,
rotation), its placement, the pads and the board outline, all in board-local mm (origin subtracted, KiCad y down).

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\dump_3d.py
      -> hardware/<board>/plots/models3d.json for spb-bb-revb-dpt, spb-bb-revb-load (origin = leg centre) and
         spb-busbar (origin = centre leg, leg-local y)
"""
import json
import os
import sys

import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KI3D = "C:/Program Files/KiCad/7.0/share/kicad/3dmodels"
BOARDS = {"spb-bb-revb-dpt": (150.0, 100.0), "spb-bb-revb-load": (150.0, 100.0), "spb-busbar": (160.0, 80.0)}
T = 1.6


def dump(name, ox, oy):
    brd = os.path.join(ROOT, "hardware", name)
    b = pcbnew.LoadBoard(os.path.join(brd, name + ".kicad_pcb"))
    mm = pcbnew.ToMM
    parts, pads = [], []
    for f in b.GetFootprints():
        ms = []
        for m in f.Models():
            p = m.m_Filename
            for var in ("${KICAD6_3DMODEL_DIR}", "${KICAD7_3DMODEL_DIR}"):
                p = p.replace(var, KI3D)
            p = p.replace("${KIPRJMOD}", brd.replace("\\", "/"))
            ms.append(dict(path=os.path.normpath(p), off=[m.m_Offset.x, m.m_Offset.y, m.m_Offset.z],
                           rot=[m.m_Rotation.x, m.m_Rotation.y, m.m_Rotation.z], scale=[m.m_Scale.x, m.m_Scale.y,
                                                                                        m.m_Scale.z]))
        pos = f.GetPosition()
        parts.append(dict(ref=f.GetReference(), value=f.GetValue(), x=mm(pos.x) - ox, y=mm(pos.y) - oy,
                          rot=f.GetOrientationDegrees(), bottom=f.IsFlipped(), models=ms))
        for q in f.Pads():
            bb = q.GetBoundingBox()
            box = [mm(bb.GetLeft()) - ox, mm(bb.GetTop()) - oy, mm(bb.GetRight()) - ox, mm(bb.GetBottom()) - oy]
            circ = q.GetShape() == pcbnew.PAD_SHAPE_CIRCLE
            drill = mm(q.GetDrillSize().x) if q.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else 0.0
            for lay, side in ((pcbnew.F_Cu, "top"), (pcbnew.B_Cu, "bottom")):
                if q.IsOnLayer(lay):
                    pads.append(box + [side, circ, drill])
    holes = []
    for f in b.GetFootprints():
        for q in f.Pads():
            if q.GetDrillSize().x > pcbnew.FromMM(2.0):
                holes.append([mm(q.GetPosition().x) - ox, mm(q.GetPosition().y) - oy, mm(q.GetDrillSize().x) / 2])
    e = b.GetBoardEdgesBoundingBox()
    out = dict(name=name, edge=[mm(e.GetLeft()) - ox, mm(e.GetTop()) - oy, mm(e.GetRight()) - ox,
                                mm(e.GetBottom()) - oy], thickness=T, parts=parts, pads=pads, holes=holes)
    os.makedirs(os.path.join(brd, "plots"), exist_ok=True)
    path = os.path.join(brd, "plots", "models3d.json")
    json.dump(out, open(path, "w"))
    print("dumped", name, len(parts), "footprints", len(pads), "pads ->", path)


if __name__ == "__main__":
    for n, (ox, oy) in BOARDS.items():
        if len(sys.argv) < 2 or n in sys.argv[1:]:        # optional board names: dump only those
            dump(n, ox, oy)

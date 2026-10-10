"""
Dump a KiCad board (outline, copper shapes, pads, vias, footprints with 3D models) to JSON for render_board.py.

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\kicad_dump.py [board.kicad_pcb] [out.json]
"""
import json
import os
import sys

KI = "C:/Program Files/KiCad/7.0/share/kicad"
os.environ.setdefault("KICAD7_3DMODEL_DIR", KI + "/3dmodels")
import pcbnew  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "hardware", "spb-building-block", "spb-building-block.kicad_pcb")
dst = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + "_3d.json"
b = pcbnew.LoadBoard(src)
mm = pcbnew.ToMM
LN = {pcbnew.F_Cu: "F.Cu", pcbnew.In1_Cu: "In1.Cu", pcbnew.In2_Cu: "In2.Cu", pcbnew.B_Cu: "B.Cu",
      pcbnew.Edge_Cuts: "Edge.Cuts", pcbnew.F_SilkS: "F.SilkS"}


def resolve(path):
    for var, val in (("${KICAD7_3DMODEL_DIR}", KI + "/3dmodels"), ("${KICAD6_3DMODEL_DIR}", KI + "/3dmodels"),
                     ("${KIPRJMOD}", os.path.dirname(src))):
        path = path.replace(var, val)
    if path.lower().endswith((".step", ".stp")):
        path = path[: path.rfind(".")] + ".wrl"
    return path


out = dict(thickness=mm(b.GetDesignSettings().GetBoardThickness()), shapes=[], pads=[], vias=[], parts=[])
for d in b.GetDrawings():
    if d.GetLayer() in LN and d.GetClass() == "PCB_SHAPE" and d.GetShape() == pcbnew.SHAPE_T_RECT:
        s, e = d.GetStart(), d.GetEnd()
        out["shapes"].append(dict(layer=LN[d.GetLayer()], x0=mm(s.x), y0=mm(s.y), x1=mm(e.x), y1=mm(e.y),
                                  filled=bool(d.IsFilled())))
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        p = t.GetPosition()
        out["vias"].append(dict(x=mm(p.x), y=mm(p.y), d=mm(t.GetWidth()), drill=mm(t.GetDrillValue())))
for fp in b.GetFootprints():
    p = fp.GetPosition()
    bottom = fp.GetLayer() == pcbnew.B_Cu
    models = []
    for m in fp.Models():
        models.append(dict(file=resolve(m.m_Filename), offset=[m.m_Offset.x, m.m_Offset.y, m.m_Offset.z],
                           rotation=[m.m_Rotation.x, m.m_Rotation.y, m.m_Rotation.z], scale=[m.m_Scale.x, m.m_Scale.y, m.m_Scale.z]))
    out["parts"].append(dict(ref=fp.GetReference(), value=fp.GetValue(), x=mm(p.x), y=mm(p.y),
                             rot=fp.GetOrientationDegrees(), bottom=bottom, models=models))
    for pad in fp.Pads():
        q = pad.GetPosition()
        sz = pad.GetSize()
        out["pads"].append(dict(x=mm(q.x), y=mm(q.y), w=mm(sz.x), h=mm(sz.y), rot=pad.GetOrientationDegrees(),
                                shape="circle" if pad.GetShape() == pcbnew.PAD_SHAPE_CIRCLE else "rect",
                                bottom=bottom))
json.dump(out, open(dst, "w"), indent=0)
print("dumped", dst, {k: len(v) for k, v in out.items() if isinstance(v, list)})

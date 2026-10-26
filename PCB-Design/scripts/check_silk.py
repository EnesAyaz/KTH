"""
Silkscreen audit of a board, beyond KiCad's DRC (which does not flag silk drawn over drilled holes):
every visible silk text (board texts and footprint reference / value texts) is checked, stroke by stroke
(KiCad's own text shapes), against
  - drilled holes (vias, plated and non-plated pad holes) + 0.10 mm      -> the drill removes the silk
  - solder-mask openings of pads and graphical mask shapes              -> the fab clips silk on exposed copper
  - other silk texts on the same side                                    -> unreadable
  - the board outline (0.25 mm)
and for its size (height >= 0.8 mm, stroke >= 0.15 mm; JLCPCB minimum line width 0.153 mm).

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\check_silk.py [board]
Exit code 1 when anything is found.
"""
import os
import sys

import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = sys.argv[1] if len(sys.argv) > 1 else "spb-bb-revb-dpt"
MM = pcbnew.FromMM
TO = pcbnew.ToMM
b = pcbnew.LoadBoard(os.path.join(ROOT, "hardware", NAME, NAME + ".kicad_pcb"))
SIDES = {pcbnew.F_SilkS: (pcbnew.F_Mask, "top"), pcbnew.B_SilkS: (pcbnew.B_Mask, "bottom")}

texts = []
for d in b.GetDrawings():
    if d.GetClass() == "PCB_TEXT" and d.GetLayer() in SIDES:
        texts.append(("board", d))
for f in b.GetFootprints():
    for t in [f.Reference(), f.Value()] + [g for g in f.GraphicalItems() if g.GetClass() == "FP_TEXT"]:
        if t.IsVisible() and t.GetLayer() in SIDES and t.GetText() not in ("${REFERENCE}", ""):
            texts.append((f.GetReference(), t))

holes = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        holes.append((pcbnew.SHAPE_CIRCLE(t.GetPosition(), t.GetDrillValue() // 2), "via " + t.GetNetname()))
masks = {pcbnew.F_Mask: [], pcbnew.B_Mask: []}
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetDrillSize().x > 0:
            holes.append((pcbnew.SHAPE_CIRCLE(p.GetPosition(), max(p.GetDrillSize().x, p.GetDrillSize().y) // 2),
                          "hole %s.%s" % (f.GetReference(), p.GetNumber())))
        for ml, cu in ((pcbnew.F_Mask, pcbnew.F_Cu), (pcbnew.B_Mask, pcbnew.B_Cu)):
            if p.IsOnLayer(ml):
                masks[ml].append((p.GetEffectiveShape(cu), max(p.GetSolderMaskExpansion(), 0),
                                  "pad %s.%s" % (f.GetReference(), p.GetNumber())))
    for g in f.GraphicalItems():
        if g.GetLayer() in masks and g.GetClass() == "FP_SHAPE":
            masks[g.GetLayer()].append((g.GetEffectiveShape(), 0, "mask shape %s" % f.GetReference()))
edge = b.GetBoardEdgesBoundingBox()

problems = []
shp = [(owner, t, t.GetEffectiveTextShape()) for owner, t in texts]
for owner, t, s in shp:
    side_mask, side = SIDES[t.GetLayer()]
    lab = "%s '%s' (%s, %.2f, %.2f)" % (owner, t.GetText(), side, TO(t.GetPosition().x), TO(t.GetPosition().y))
    h, w = TO(t.GetTextHeight()), TO(t.GetTextThickness())
    if h < 0.8 - 1e-6 or w < 0.15 - 1e-6:
        problems.append((lab, "size %.2f mm / stroke %.2f mm" % (h, w)))
    bb = s.BBox()
    for c, what in holes:
        if s.Collide(c, MM(0.10)):
            problems.append((lab, "over a drilled hole (%s)" % what))
    for m, exp, what in masks[side_mask]:
        if m.BBox().Intersects(bb) and s.Collide(m, exp):
            problems.append((lab, "clipped by a mask opening (%s)" % what))
    if bb.GetLeft() < edge.GetLeft() + MM(0.25) or bb.GetRight() > edge.GetRight() - MM(0.25) or \
            bb.GetTop() < edge.GetTop() + MM(0.25) or bb.GetBottom() > edge.GetBottom() - MM(0.25):
        problems.append((lab, "closer than 0.25 mm to the board edge"))
for i, (o1, t1, s1) in enumerate(shp):
    for o2, t2, s2 in shp[i + 1:]:
        if t1.GetLayer() == t2.GetLayer() and s1.BBox().Intersects(s2.BBox()) and s1.Collide(s2, 0):
            problems.append(("%s '%s'" % (o1, t1.GetText()), "overlaps %s '%s'" % (o2, t2.GetText())))
seen = []
for p in problems:
    if p not in seen:
        seen.append(p)
        print("%-58s %s" % p)
print("%s: %d silk texts checked, %d problems" % (NAME, len(texts), len(seen)))
sys.exit(1 if seen else 0)

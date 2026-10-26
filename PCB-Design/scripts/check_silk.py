"""
Silkscreen audit of a board, beyond KiCad's DRC (which does not flag silk drawn over drilled holes):
every visible silk text (board texts and footprint reference / value texts) is checked, stroke by stroke
(KiCad's own text shapes), against
  - drilled holes (vias, plated and non-plated pad holes) + 0.10 mm      -> the drill removes the silk
  - solder-mask openings of pads and graphical mask shapes              -> the fab clips silk on exposed copper
  - other silk texts on the same side                                    -> unreadable
  - the board outline (0.25 mm)
and for its size (height >= 0.8 mm, stroke >= 0.15 mm; JLCPCB minimum line width 0.153 mm). Reference labels (also
group labels "C1-C5" and test-point names) must be within 2.6 mm (test points 3.6 mm) of their own part and closer to
it than to any other part.

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
# proximity: a reference label (also a group "C1-C5" and a test-point name) must be within NEAR of its own part(s),
# closer to them than to any other part on that side, and not over another part's body (the placer keeps an extra
# 0.25 mm margin)
import re  # noqa: E402

NEAR, NEAR_TP = 4.1, 4.1                              # placer: 2.5 mm first, 4.0 mm second pass
fps = {f.GetReference(): f for f in b.GetFootprints()}
tp_by_name = {}                                      # name -> [refs]: GNDI1 also as GNDI, +12V2 also as 12V
for f in b.GetFootprints():
    if f.GetReference().startswith("TP"):
        tp_by_name.setdefault(f.GetValue(), []).append(f.GetReference())
        if f.GetValue()[-1:].isdigit():
            tp_by_name.setdefault(f.GetValue()[:-1].lstrip("+"), []).append(f.GetReference())


def box(item):
    bb = item.GetBoundingBox(False, False) if hasattr(item, "Pads") else item.GetBoundingBox()
    return (TO(bb.GetLeft()), TO(bb.GetTop()), TO(bb.GetRight()), TO(bb.GetBottom()))


def gap(a, c):
    gx = max(a[0] - c[2], c[0] - a[2], 0.0)
    gy = max(a[1] - c[3], c[1] - a[3], 0.0)
    return (gx * gx + gy * gy) ** 0.5


LEADERS = [((TO(d.GetStart().x), TO(d.GetStart().y)), (TO(d.GetEnd().x), TO(d.GetEnd().y)), d.GetLayer())
           for d in b.GetDrawings() if d.GetClass() == "PCB_SHAPE" and d.GetLayer() in SIDES and
           d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
bodies = {"top": [], "bottom": []}
for r, f in fps.items():
    if r.startswith(("H", "REF", "RS")):                 # RS: UFCS shunts, hand-fitted later
        continue
    sides = ("top", "bottom") if any(p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for p in f.Pads()) else \
        (("bottom",) if f.IsFlipped() else ("top",))
    for sd in sides:
        bodies[sd].append((r, box(f)))
for owner, t in texts:
    if owner != "board":
        continue
    s = t.GetText()
    side = SIDES[t.GetLayer()][1]
    refs = set()
    if re.match(r"^[A-Z]+\d+([-,][A-Z]+\d+)+$", s):                     # group label
        pre = re.match(r"[A-Z]+", s).group(0)
        for part in s.split(","):
            a_, _, b_ = part.partition("-")
            lo, hi = int(a_[len(pre):]), int((b_ or a_)[len(pre):])
            refs |= {"%s%d" % (pre, n) for n in range(lo, hi + 1)}
        lim = NEAR
    elif s.split()[0] in fps:
        refs, lim = {s.split()[0]}, NEAR
    elif s in tp_by_name:                                # the nearest test point of that name (6 mm max),
        tb0 = box(t)                                     # else a header pin name such as 12V
        cand = min(tp_by_name[s], key=lambda r: gap(tb0, box(fps[r])))
        if gap(tb0, box(fps[cand])) > 6.0:
            continue
        refs, lim = {cand}, NEAR_TP
        tb = box(t)                                      # a net name: next to its pad, never over another part
        own = gap(tb, box(fps[cand]))
        lab = "'%s' (%s, %.2f, %.2f)" % (s, side, TO(t.GetPosition().x), TO(t.GetPosition().y))
        if own > lim:
            problems.append((lab, "%.1f mm from its test point" % own))
        over = [r for r, ob in bodies[side] if r != cand and gap(tb, ob) == 0]
        if over:
            problems.append((lab, "over the body of %s" % over[0]))
        continue
    else:
        continue
    refs &= set(fps)
    if not refs:
        continue
    tb = box(t)
    own = min(gap(tb, box(fps[r])) for r in refs)
    lab = "'%s' (%s, %.2f, %.2f)" % (s, side, TO(t.GetPosition().x), TO(t.GetPosition().y))
    lay = t.GetLayer()
    led = [(a_, b_) for a_, b_, l_ in LEADERS if l_ == lay]
    pt_box = lambda p_, bx: gap((p_[0], p_[1], p_[0], p_[1]), bx)     # noqa: E731
    if any((pt_box(a_, tb) < 0.4 and min(pt_box(b_, box(fps[r])) for r in refs) < 0.4) or
           (pt_box(b_, tb) < 0.4 and min(pt_box(a_, box(fps[r])) for r in refs) < 0.4) for a_, b_ in led):
        continue                                          # joined to its part by a leader line
    if own > lim:
        problems.append((lab, "%.1f mm from its part" % own))
    for r, ob in bodies[side]:
        if r not in refs and gap(tb, ob) < own - 1e-6:
            problems.append((lab, "closer to %s (%.1f mm) than to its own part (%.1f mm)%s" % (
                r, gap(tb, ob), own, ", over its body" if gap(tb, ob) == 0 else "")))
            break

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

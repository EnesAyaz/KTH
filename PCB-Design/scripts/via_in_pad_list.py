"""
Via-in-pad list (fab/via_in_pad.csv) of a Rev B board: the vias that must be filled + capped (IPC-4761 type VII); all
other vias are tented. Used by make_kicad_bb_revb.py (after generation) and by make_fab_outputs_revb.py (on the saved
board, so the list always belongs to the board that is fabricated and no board regeneration is needed):

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" scripts\\via_in_pad_list.py spb-bb-revb-dpt

RULE (pre-fab layout review 2026-11-03, minor item "via-in-pad list is four vias short"): a via is listed when its
DRILL HOLE overlaps a solder-mask opening on either side, the openings taken as the plotter makes them: pad shapes
plus their mask expansion, mask-layer footprint graphics (EPC2361 mask polygons), and openings closer than the
solder-mask minimum web (board setting, 0.2 mm) MERGED into one (inflate by web/2, union, deflate by web/2). The old
rule (via centre inside an SMD pad) missed vias whose centre is outside a pad but whose drill is not: the DC+ vias
between the 0805 pads of the cell rows (drill reaches 0.06 mm into C5.1 etc. on top and 0.11 mm into C28.2/C29.2
on the bottom) and vias at the edge of an SMD test pad (TP1, TP33). Vias found by this extra rule are labelled
by side, e.g. "F:C5.1 B:C28.2+C29.2", "(merged)" when only a merged gap between pads exposes the drill.
NEAR-PAD (Enes, 2026-11-03): a drill whose edge only touches an opening edge, or stays within NEAR of it, is listed
too, reason "near_pad" (all others "in_pad"): mask registration at the fab (~+-0.05 mm) can expose part of the hole.
NEAR = 0.02 mm takes exactly the tangent drills (gap 0.000 mm: 24 DC- vias at y 61.3 next to the 0805s, VEEA/VDDB at
y 44.65); the next-closest drills are 0.047 mm (KH/KL, y 24.2) and 0.068 / 0.093 mm (DC-, y 61.3) away, not listed.
An exposed annular ring alone (drill clear of every opening) is not listed.
Coordinates: drill / place (aux) origin = board bottom-left, x right, y up (the origin of the Gerbers, drills and CPL).
"""
import os
import sys

import pcbnew

TOL = pcbnew.FromMM(0.005)        # numeric tolerance of the polygon approximation (drill tangent to an opening = out)
ERR = pcbnew.FromMM(0.002)        # arc approximation error of the pad polygons
NEAR = pcbnew.FromMM(0.02)        # near-pad margin: drill edge within this of an opening -> listed, "near_pad"


def _mask_graphic(g, f):
    """Footprint mask graphic -> polygon in board coordinates (KiCad 7 keeps fp_poly points footprint-local)."""
    if g.GetShape() != pcbnew.SHAPE_T_POLY or not g.IsFilled():
        raise SystemExit("via_in_pad_list: mask graphic %s on %s is not a filled polygon: extend the rule"
                         % (g.GetShapeStr(), f.GetReference()))
    gb = g.GetBoundingBox()
    for sign in (1, -1):              # rotation sense checked against KiCad's own bounding box of the graphic
        q = g.GetPolyShape().CloneDropTriangulation()
        if f.IsFlipped():
            q.Mirror(False, True)
        q.Rotate(pcbnew.EDA_ANGLE(sign * f.GetOrientationDegrees(), pcbnew.DEGREES_T), pcbnew.VECTOR2I(0, 0))
        q.Move(f.GetPosition())
        c = q.BBox().Centre()
        if abs(c.x - gb.Centre().x) < pcbnew.FromMM(0.01) and abs(c.y - gb.Centre().y) < pcbnew.FromMM(0.01):
            return q
    raise SystemExit("via_in_pad_list: cannot place the mask polygon of %s" % f.GetReference())


def mask_openings(board, layer):
    """Solder-mask openings of one side, merged with the minimum web like the Gerber plotter does."""
    web = board.GetDesignSettings().m_SolderMaskMinWidth
    ps = pcbnew.SHAPE_POLY_SET()
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.IsOnLayer(layer):
                p.TransformShapeToPolygon(ps, layer, p.GetSolderMaskExpansion() + web // 2, ERR)
        for g in f.GraphicalItems():
            if g.GetLayer() == layer and g.GetClass() != "PCB_TEXT" and "TEXT" not in g.GetClass():
                q = _mask_graphic(g, f)
                q.Inflate(web // 2, 16)
                ps.BooleanAdd(q, pcbnew.SHAPE_POLY_SET.PM_FAST)
    for g in board.GetDrawings():
        if g.GetLayer() == layer:
            raise SystemExit("via_in_pad_list: board graphic on %s: extend the rule" % board.GetLayerName(layer))
    for z in board.Zones():
        if z.IsOnLayer(layer):
            raise SystemExit("via_in_pad_list: zone on %s: extend the rule" % board.GetLayerName(layer))
    ps.Simplify(pcbnew.SHAPE_POLY_SET.PM_FAST)
    if web:
        ps.Deflate(web // 2, 16)
    return ps


def pad_opening(p, layer):
    q = pcbnew.SHAPE_POLY_SET()
    p.TransformShapeToPolygon(q, layer, p.GetSolderMaskExpansion(), ERR)
    return q


def via_list(board):
    aux = board.GetDesignSettings().GetAuxOrigin()
    web = board.GetDesignSettings().m_SolderMaskMinWidth
    sides = [(L, mask_openings(board, L)) for L in (pcbnew.F_Mask, pcbnew.B_Mask)]
    smd = [q for f in board.GetFootprints() for q in f.Pads() if q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    rows = []
    for t in board.GetTracks():
        if t.GetClass() != "PCB_VIA":
            continue
        c, r = t.GetPosition(), t.GetDrillValue() // 2
        hit = next((q for q in smd if q.HitTest(c)), None)              # centre in an SMD pad (the original rule)
        reason = "in_pad"
        if hit is not None:
            where = "%s.%s" % (hit.GetParent().GetReference(), hit.GetNumber())
        else:
            clr = r - TOL
            exp = [L for L, ps in sides if ps.Collide(c, clr)]         # drill overlaps a (merged) mask opening
            if not exp:                                                 # drill tangent to / within NEAR of one
                clr, reason = r + NEAR, "near_pad"
                exp = [L for L, ps in sides if ps.Collide(c, clr)]
            if not exp:
                continue
            names = []
            for L in exp:                                               # F:C5.1 B:C28.2+C29.2
                own = [q for q in smd if q.IsOnLayer(L) and pad_opening(q, L).Collide(c, clr)]
                tag = ""
                if not own:                                             # only the merged gap between pads covers it
                    own = [q for q in smd if q.IsOnLayer(L) and pad_opening(q, L).Collide(c, r + web)]
                    tag = "(merged)"
                names.append("%s:%s%s" % ("F" if L == pcbnew.F_Mask else "B", "+".join(sorted(
                    "%s.%s" % (q.GetParent().GetReference(), q.GetNumber()) for q in own)), tag))
            where = " ".join(names)
        rows.append(("%.3f" % pcbnew.ToMM(c.x - aux.x), "%.3f" % -pcbnew.ToMM(c.y - aux.y),
                     "%.2f" % pcbnew.ToMM(t.GetDrillValue()), "%.2f" % pcbnew.ToMM(t.GetWidth()), t.GetNetname(), where,
                     reason))
    return sorted(rows, key=lambda r: (r[5].replace("F:", "").replace("B:", ""), float(r[0]), float(r[1])))


def write(board, path):
    rows = via_list(board)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        f.write("x_mm,y_mm,drill_mm,diameter_mm,net,in_pad,reason\n")
        for r in rows:
            f.write(",".join(r) + "\n")
    near = sum(r[6] == "near_pad" for r in rows)
    print("via-in-pad (filled + capped): %d vias (%d in_pad, %d near_pad) in %d pads -> %s"
          % (len(rows), len(rows) - near, near, len(set(r[5] for r in rows)), path), flush=True)
    return rows


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "spb-bb-revb-dpt"
    D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hardware", name)
    write(pcbnew.LoadBoard(os.path.join(D, name + ".kicad_pcb")), os.path.join(D, "fab", "via_in_pad.csv"))

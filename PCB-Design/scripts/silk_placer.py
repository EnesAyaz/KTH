"""
Silkscreen placement for the generated Rev B boards (used by make_kicad_bb_revb.py before saving).

Every text is a board-level PCB_TEXT. A text is placed at the first candidate position whose bounding box
  - stays inside the board outline (margin EDGE),
  - keeps CLR from every pad of that side (THT pads on both sides) - silk is never printed on solder pads,
  - keeps HOLE_CLR from every drilled via hole (both sides: the drill would cut the text),
  - does not overlap any silkscreen already on that side (footprint silk graphics and placed texts).
Reference labels (label_fp / label_near) must also be unambiguous: within NEAR mm of their own part, closer to it
than to any other part by MARGIN, never over another part's body; rows of identical parts get one group label
("C1-C5"). Texts that find no such spot go to the Fab layer (assembly drawing) and are reported.
Coordinates: board mm before the final move (same frame as the generator).
"""
import re

import pcbnew

MM = pcbnew.FromMM
EDGE, CLR, GAP = 0.35, 0.18, 0.12
HOLE_CLR = 0.12                              # mm around a drilled via hole
NEAR, MARGIN = 2.5, 0.25                     # a label: <= NEAR mm from its part, MARGIN closer to it than to others
NEAR2, MARGIN2 = 4.0, 0.0                    # second pass: further out, still closer to its own part than to any other
LAB_FITTED = ("RS",)                         # hand-fitted later (UFCS shunts): their bodies do not hide the labels
SIZE, MIN_SIZE = 0.8, 0.8                    # mm text height (JLCPCB: >= 0.8 mm, line >= 0.153 mm)


def _box(bb, m=0.0):
    return (pcbnew.ToMM(bb.GetLeft()) - m, pcbnew.ToMM(bb.GetTop()) - m, pcbnew.ToMM(bb.GetRight()) + m,
            pcbnew.ToMM(bb.GetBottom()) + m)


def _gap(a, b):
    """distance between two boxes (0 if they touch or overlap)"""
    gx = max(a[0] - b[2], b[0] - a[2], 0.0)
    gy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return (gx * gx + gy * gy) ** 0.5


def _hit(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


class Silk:
    def __init__(self, board, outline):
        self.b = board
        self.outline = outline                    # (x0, y0, x1, y1)
        self.obst = {"top": [], "bottom": []}     # copper pads (+CLR)
        self.silk = {"top": [], "bottom": []}     # existing silk
        self.failed = []
        self.leaders = []                         # (text, side, start, end) of the leader lines
        for t in board.GetTracks():                 # drilled holes cut the silk on both sides (vias are tented,
            if t.GetClass() == "PCB_VIA":           # so they are not pads, but the drill still removes the text)
                r = pcbnew.ToMM(t.GetDrillValue()) / 2 + HOLE_CLR
                x, y = pcbnew.ToMM(t.GetPosition().x), pcbnew.ToMM(t.GetPosition().y)
                for side in ("top", "bottom"):
                    self.obst[side].append((x - r, y - r, x + r, y + r))
        for fp in board.GetFootprints():
            for p in fp.Pads():
                bb = _box(p.GetBoundingBox(), CLR)
                tht = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
                for side, lay in (("top", pcbnew.F_Cu), ("bottom", pcbnew.B_Cu)):
                    if tht or p.IsOnLayer(lay):
                        self.obst[side].append(bb)
            for g in fp.GraphicalItems():
                if g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and g.GetClass() != "MTEXT":
                    side = "top" if g.GetLayer() == pcbnew.F_SilkS else "bottom"
                    self.silk[side].append(_box(g.GetBoundingBox(), GAP / 2))
        for d in board.GetDrawings():
            if d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
                side = "top" if d.GetLayer() == pcbnew.F_SilkS else "bottom"
                self.silk[side].append(_box(d.GetBoundingBox(), GAP / 2))

    def _make(self, s, x, y, side, size, angle):
        t = pcbnew.PCB_TEXT(self.b)
        t.SetText(s)
        t.SetLayer(pcbnew.F_SilkS if side == "top" else pcbnew.B_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
        t.SetTextThickness(MM(max(0.16, size * 0.15)))
        if side == "bottom":
            t.SetMirrored(True)
        t.SetTextAngle(pcbnew.EDA_ANGLE(angle, pcbnew.DEGREES_T))
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        return t

    def _ok(self, bb, side):
        x0, y0, x1, y1 = self.outline
        if bb[0] < x0 + EDGE or bb[1] < y0 + EDGE or bb[2] > x1 - EDGE or bb[3] > y1 - EDGE:
            return False
        return not any(_hit(bb, o) for o in self.obst[side]) and not any(_hit(bb, o) for o in self.silk[side])

    def size_of(self, s, size, angle):
        t = self._make(s, 0.0, 0.0, "top", size, angle)
        bb = _box(t.GetBoundingBox())
        return bb[2] - bb[0], bb[3] - bb[1]

    def put(self, s, cands, side, size=SIZE, fab_at=None):
        """cands: [(x, y, angle)] text centres, tried in order; returns True if placed on silk."""
        dims = {a: self.size_of(s, size, a) for a in set(c[2] for c in cands)}
        if cands:
            xs = [c[0] for c in cands]
            ys = [c[1] for c in cands]
            m = max(max(d) for d in dims.values())
            reg = (min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m)
            near = [o for o in self.obst[side] + self.silk[side] if _hit(o, reg)]
        x0, y0, x1, y1 = self.outline
        for x, y, ang in cands:
            w, h = dims[ang]
            bb = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            if bb[0] < x0 + EDGE or bb[1] < y0 + EDGE or bb[2] > x1 - EDGE or bb[3] > y1 - EDGE:
                continue
            if any(_hit(bb, o) for o in near):
                continue
            t = self._make(s, x, y, side, size, ang)
            bb = _box(t.GetBoundingBox())
            if not self._ok(bb, side):
                continue
            self.b.Add(t)
            self.silk[side].append((bb[0] - GAP, bb[1] - GAP, bb[2] + GAP, bb[3] + GAP))
            return True
        if fab_at is not None:
            t = self._make(s, fab_at[0], fab_at[1], side, size, 0)
            t.SetLayer(pcbnew.F_Fab if side == "top" else pcbnew.B_Fab)
            self.b.Add(t)
        self.failed.append(s)
        return False

    def around(self, box, s, size=SIZE, rings=(0.15, 0.9, 1.8), centre=True, reach=4.5, step=0.3):
        """candidate centres around a box (x0, y0, x1, y1): the four sides first, then a grid out to `reach` mm
        sorted by the gap to the box (horizontal before vertical text), finally the box centre."""
        x0, y0, x1, y1 = box
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        out = []
        for ang in (0, 90):
            w, h = self.size_of(s, size, ang)
            for d in rings:
                out += [(cx, y0 - h / 2 - d, ang), (cx, y1 + h / 2 + d, ang), (x0 - w / 2 - d, cy, ang),
                        (x1 + w / 2 + d, cy, ang)]
        grid = []
        for ang in (0, 90):
            w, h = self.size_of(s, size, ang)
            n = int(reach / step)
            for i in range(-n - int(w / step), n + int(w / step) + 1):
                for j in range(-n - int(h / step), n + int(h / step) + 1):
                    x, y = cx + i * step, cy + j * step
                    tb = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
                    if _hit(tb, box):
                        continue
                    gx = max(x0 - tb[2], tb[0] - x1, 0.0)
                    gy = max(y0 - tb[3], tb[1] - y1, 0.0)
                    g = (gx * gx + gy * gy) ** 0.5
                    if g <= reach:
                        grid.append((g + (0.6 if ang else 0.0), (x, y, ang)))
        out += [c for _, c in sorted(grid)]
        if centre:
            out += [(cx, cy, 0), (cx, cy, 90)]
        return out

    def _bodies(self, side):
        """(ref, box) of every part on that side (pads + body graphics; through-hole parts on both sides)"""
        if not hasattr(self, "_bod"):
            self._bod = {"top": [], "bottom": []}
            for fp in self.b.GetFootprints():
                r = fp.GetReference()
                if r.startswith(("H", "REF") + LAB_FITTED) or r in ("",):
                    continue
                bb = _box(fp.GetBoundingBox(False, False))
                sides = ("bottom",) if fp.IsFlipped() else ("top",)
                if any(p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for p in fp.Pads()):
                    sides = ("top", "bottom")
                for sd in sides:
                    self._bod[sd].append((r, bb))
        return self._bod[side]

    def leader(self, box, owners, s, side, size=SIZE, reach=10.0):
        """label at the nearest free spot within `reach` plus a 0.15 mm silk line from the label to its part (box);
        the label and the line keep clear of pads, holes, other silk and other parts' bodies. True if placed."""
        bodies = [ob for r, ob in self._bodies(side) if r not in owners]
        lw, clr = 0.15, 0.12

        def seg_free(p, q):
            n = max(2, int(((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2) ** 0.5 / 0.1))
            for k in range(n + 1):
                x, y = p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n
                pt = (x - lw / 2 - clr, y - lw / 2 - clr, x + lw / 2 + clr, y + lw / 2 + clr)
                if any(_hit(pt, o) for o in self.obst[side]) or any(_hit(pt, o) for o in self.silk[side]) or \
                        any(_hit(pt, o) for o in bodies):
                    return False
            return True
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        for x, y, ang in self.around(box, s, size, rings=(0.8, 1.5, 2.5), centre=False, reach=reach, step=0.3):
            w, h = self.size_of(s, size, ang)
            tb = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            if any(_gap(tb, ob) == 0 for ob in bodies) or not self._ok(tb, side):
                continue
            # line from the text box edge (towards the part) to the part outline
            p = (min(max(cx, tb[0]), tb[2]), min(max(cy, tb[1]), tb[3]))
            q = (min(max(p[0], box[0]), box[2]), min(max(p[1], box[1]), box[3]))
            if ((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2) ** 0.5 < 0.4:
                continue                                  # touching: a plain label would have been found
            # start the line 0.15 mm outside the text box
            L = ((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2) ** 0.5
            p0 = (p[0] + (q[0] - p[0]) * 0.15 / L, p[1] + (q[1] - p[1]) * 0.15 / L)
            q0 = (q[0] - (q[0] - p[0]) * 0.05 / L, q[1] - (q[1] - p[1]) * 0.05 / L)
            if not seg_free(p0, q0):
                continue
            if not self.put(s, [(x, y, ang)], side, size):
                self.failed.pop()
                continue
            ln = pcbnew.PCB_SHAPE(self.b)
            ln.SetShape(pcbnew.SHAPE_T_SEGMENT)
            ln.SetLayer(pcbnew.F_SilkS if side == "top" else pcbnew.B_SilkS)
            ln.SetWidth(MM(lw))
            ln.SetStart(pcbnew.VECTOR2I(MM(p0[0]), MM(p0[1])))
            ln.SetEnd(pcbnew.VECTOR2I(MM(q0[0]), MM(q0[1])))
            self.b.Add(ln)
            self.silk[side].append((min(p0[0], q0[0]) - lw, min(p0[1], q0[1]) - lw, max(p0[0], q0[0]) + lw,
                                    max(p0[1], q0[1]) + lw))
            self.leaders.append((s, side, p0, q0))
            return True
        return False

    def near_ok(self, s, size, ang, x, y, box, owners, side, max_d, margin=MARGIN, strict=True):
        """the text at (x, y) is unambiguous: at most max_d from its own part(s) `box`, closer to it than to any other
        part (by MARGIN), and not over another part's body"""
        w, h = self.size_of(s, size, ang)
        tb = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        own = _gap(tb, box)
        if own > max_d:
            return False
        for r, ob in self._bodies(side):
            if r in owners:
                continue
            g = _gap(tb, ob)
            if g == 0 or (strict and g <= own + margin):   # never over another part; strict: also nearest to own
                return False
        return True

    def label_near(self, box, owners, s, side, size=SIZE, max_d=NEAR, fab_at=None):
        """place s next to box (the part or a group of parts `owners`), unambiguously (near_ok); a second pass further
        out (still nearer to its own part than to any other); else on Fab"""
        for md, mg in ((max_d, MARGIN), (NEAR2, MARGIN2)):
            cands = [c for c in self.around(box, s, size, rings=(0.12, 0.3, 0.6), centre=False, reach=md, step=0.2)
                     if self.near_ok(s, size, c[2], c[0], c[1], box, owners, side, md, mg)]
            if self.put(s, cands, side, size):
                return True
            self.failed.pop()
        if self.leader(box, owners, s, side, size):    # a free spot further out, joined to the part by a line
            return True
        return self.put(s, [], side, size, fab_at=fab_at)

    def label_fp(self, fp, s, size=SIZE):
        side = "bottom" if fp.IsFlipped() else "top"
        bb = _box(fp.GetBoundingBox(False, False))
        pos = (pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y))
        return self.label_near(bb, {fp.GetReference()}, s, side, size, fab_at=pos)

    def pin_labels(self, fp, names, size=SIZE):
        """names {pad number: text}: each text next to its pad, the side away from the part centre first."""
        side = "bottom" if fp.IsFlipped() else "top"
        fx, fy = pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y)
        for p in fp.Pads():
            n = p.GetNumber()
            if n not in names:
                continue
            px, py = pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)
            pb = _box(p.GetBoundingBox())
            ox, oy = px - fx, py - fy
            c = self.around(pb, names[n], size, rings=(0.15, 0.6), centre=False, reach=4.0, step=0.25)
            c.sort(key=lambda q: (((q[0] - px) * ox + (q[1] - py) * oy) < 0, abs(q[0] - px) + abs(q[1] - py)))
            self.put(names[n], c, side, size)


def pins_from_value(value):
    """'CTRL1: 1 12V 2 GND 3 PWM_H ...' / 'V_ISO,HS in: 1 +, 2 -' / '1:NTC 2:DC-' -> {pin: name}."""
    body = value.split(":", 1)[1] if re.match(r"^[A-Za-z_ ,0-9]+:\s*\d", value) else value
    out = {}
    for m in re.finditer(r"(?<!\d)(\d+)\s*[: ]\s*([^\s,()]+)", body):
        out[m.group(1)] = m.group(2).replace("_", "")
    return out

"""
Silkscreen placement for the generated Rev B boards (used by make_kicad_bb_revb.py before saving).

Every text is a board-level PCB_TEXT. A text is placed at the first candidate position whose bounding box
  - stays inside the board outline (margin EDGE),
  - keeps CLR from every pad of that side (THT pads on both sides) - silk is never printed on solder pads,
  - does not overlap any silkscreen already on that side (footprint silk graphics and placed texts).
Candidates around a footprint: above, below, left, right (also rotated 90 deg), the four corners, a second ring
further out, and finally the centre of the part (under the body, between its pads). Texts that find no free spot go
to the Fab layer (assembly drawing) and are reported.
Coordinates: board mm before the final move (same frame as the generator).
"""
import re

import pcbnew

MM = pcbnew.FromMM
EDGE, CLR, GAP = 0.35, 0.18, 0.12
SIZE, MIN_SIZE = 0.8, 0.8                    # mm text height (JLCPCB: >= 0.8 mm, line >= 0.153 mm)


def _box(bb, m=0.0):
    return (pcbnew.ToMM(bb.GetLeft()) - m, pcbnew.ToMM(bb.GetTop()) - m, pcbnew.ToMM(bb.GetRight()) + m,
            pcbnew.ToMM(bb.GetBottom()) + m)


def _hit(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


class Silk:
    def __init__(self, board, outline):
        self.b = board
        self.outline = outline                    # (x0, y0, x1, y1)
        self.obst = {"top": [], "bottom": []}     # copper pads (+CLR)
        self.silk = {"top": [], "bottom": []}     # existing silk
        self.failed = []
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

    def label_fp(self, fp, s, size=SIZE):
        side = "bottom" if fp.IsFlipped() else "top"
        bb = _box(fp.GetBoundingBox(False, False))
        pos = (pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y))
        if self.put(s, self.around(bb, s, size), side, size):
            return True
        self.failed.pop()                                # second pass: further out
        return self.put(s, self.around(bb, s, size, reach=8.0, step=0.4), side, size, fab_at=pos)

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
            c = self.around(pb, names[n], size, rings=(0.15,), centre=False, reach=3.0, step=0.25)
            c.sort(key=lambda q: (((q[0] - px) * ox + (q[1] - py) * oy) < 0, abs(q[0] - px) + abs(q[1] - py)))
            self.put(names[n], c, side, size)


def pins_from_value(value):
    """'CTRL1: 1 12V 2 GND 3 PWM_H ...' / 'V_ISO,HS in: 1 +, 2 -' / '1:NTC 2:DC-' -> {pin: name}."""
    body = value.split(":", 1)[1] if re.match(r"^[A-Za-z_ ,0-9]+:\s*\d", value) else value
    out = {}
    for m in re.finditer(r"(\d)\s*[: ]\s*([^\s,()]+)", body):
        out[m.group(1)] = m.group(2).replace("_", "")
    return out

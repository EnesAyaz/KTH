"""
Bring-up test points and spring-tip probe pads for the Rev B leg boards (called by make_kicad_bb_revb.py on the
filled board, before the final fill and DRC).

  TP      single round SMD pad, 1.0 mm, mask opening only (board-only footprint: not in BOM / pick-and-place)
  SPRING  signal pad 1.0 mm + ground pad 1.0 x 4.5 mm oval, 1.5 .. 6.0 mm from the signal pad centre: a probe tip on
          the signal pad and the ground spring anywhere on the ground pad (springs of about 2 .. 5.5 mm)

Each pad is placed on copper of its own net (filled zone or track, outer layer) near an anchor part and kept clear of
every other net by the rule-set distances (same domain 0.25 mm, different power domains 0.5 mm bare-pad rule,
control vs power 4.0 mm barrier), of all other pads, and of the courtyards. The candidates are searched on a 0.2 mm
grid around the anchor, nearest first, bottom side before top where both are allowed.
"""
import math

import pcbnew

MM = pcbnew.FromMM
TO = pcbnew.ToMM


def _pad(fp, num, shape, size, pos):
    p = pcbnew.PAD(fp)
    p.SetNumber(num)
    p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    p.SetShape(shape)
    p.SetSize(pcbnew.VECTOR2I(MM(size[0]), MM(size[1])))
    ls = pcbnew.LSET()
    ls.AddLayer(pcbnew.F_Cu)
    ls.AddLayer(pcbnew.F_Mask)
    p.SetLayerSet(ls)
    p.SetPos0(pcbnew.VECTOR2I(MM(pos[0]), MM(pos[1])))
    p.SetPosition(pcbnew.VECTOR2I(MM(pos[0]), MM(pos[1])))
    fp.Add(p)
    return p


MMCX_FP = ("Connector_Coaxial.pretty", "WR-MMCX_Wuerth_66012102111404_Vertical")


def make(board, kind, ref, value):
    if kind == "MMCX":                                 # Wurth WR-MMCX vertical SMT jack, 170 V rms working voltage
        import os
        fp = pcbnew.FootprintLoad(os.path.join(os.environ["KICAD7_FOOTPRINT_DIR"], MMCX_FP[0]), MMCX_FP[1])
        fp.SetReference(ref)
        fp.SetValue(value)
        fp.SetFPID(pcbnew.LIB_ID("spb_fab", MMCX_FP[1]))
        fp.SetParent(board)                            # a library footprint without a parent board crashes Flip()
        fp.Reference().SetVisible(False)               # the board silk label "Jx VDS-Ly" names it
        return fp
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetAttributes(pcbnew.FP_SMD | pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_BOM |
                     pcbnew.FP_EXCLUDE_FROM_POS_FILES)
    fp.SetFPID(pcbnew.LIB_ID("spb_fab", "TestPoint_Spring_1.0_GND1.5-6.0" if kind == "SPRING" else
                             "TestPoint_Pad_D1.0mm"))
    _pad(fp, "1", pcbnew.PAD_SHAPE_CIRCLE, (1.0, 1.0), (0.0, 0.0))
    if kind == "SPRING":
        _pad(fp, "2", pcbnew.PAD_SHAPE_OVAL, (4.5, 1.0), (3.75, 0.0))
    x0, x1, h = -0.6, (6.6 if kind == "SPRING" else 0.6), 0.6     # courtyard 0.1 mm around the pads
    for (a, b), (c, d) in (((x0, -h), (x1, -h)), ((x1, -h), (x1, h)), ((x1, h), (x0, h)), ((x0, h), (x0, -h))):
        sh = pcbnew.FP_SHAPE(fp)
        sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
        sh.SetLayer(pcbnew.F_CrtYd)
        sh.SetWidth(MM(0.05))
        sh.SetStart0(pcbnew.VECTOR2I(MM(a), MM(b)))
        sh.SetEnd0(pcbnew.VECTOR2I(MM(c), MM(d)))
        sh.SetStart(pcbnew.VECTOR2I(MM(a), MM(b)))
        sh.SetEnd(pcbnew.VECTOR2I(MM(c), MM(d)))
        fp.Add(sh)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    fp.Reference().SetLayer(pcbnew.F_Fab)
    fp.Value().SetLayer(pcbnew.F_Fab)
    return fp


class Placer:
    def __init__(self, board, dom_of, outline, log=print):
        self.b = board
        self.dom = dom_of
        self.outline = outline                       # (x0, y0, x1, y1) mm, absolute
        self.log = log
        self.placed = []
        self.banned = set()
        self.soft_vias = set()                           # nets whose vias may be removed under a placed part
        self.via_fallback = False                        # allow a via to the other outer layer for a connection
        self.zone_conn = True                            # False: a pour under a pad does not count as its connection
        self.removed_vias = []

    def req(self, a, b):
        if a == b:
            return 0.0
        da, db = self.dom(a), self.dom(b)
        if da == "CTRL" and db == "CTRL":
            return 0.25
        if "CTRL" in (da, db) and (da or db) and da != db and None not in (da, db):
            return 4.0
        if da and db and da != db:
            return 0.5
        return 0.25

    def _window(self, x, y, r):
        win = (MM(x - r), MM(y - r), MM(x + r), MM(y + r))

        def near(bb):
            return bb.GetRight() > win[0] and bb.GetLeft() < win[2] and bb.GetBottom() > win[1] and bb.GetTop() < win[3]
        items = {"pads": [], "tracks": [], "zones": [], "crt": [], "tp": set()}
        for fp in self.b.GetFootprints():
            if not near(fp.GetBoundingBox(False, False)):
                continue
            for p in fp.Pads():
                items["pads"].append(p)
                if fp.GetReference().startswith("TP"):      # other test points: never a connection target
                    items["tp"].add((p.GetPosition().x, p.GetPosition().y))
            items["crt"].append(fp)
        for t in self.b.GetTracks():
            if near(t.GetBoundingBox()):
                items["tracks"].append(t)
        for z in self.b.Zones():
            if not z.GetIsRuleArea() and near(z.GetBoundingBox()):
                items["zones"].append(z)
        return items

    def _on_own(self, items, net, layer, pt, zones=True):
        v = pcbnew.VECTOR2I(MM(pt[0]), MM(pt[1]))
        for z in (items["zones"] if zones else []):
            if z.GetNetname() == net and z.IsOnLayer(layer) and z.GetFilledPolysList(layer).Contains(v):
                return True
        for t in items["tracks"]:
            if t.GetNetname() == net and t.GetClass() == "PCB_TRACK" and t.GetLayer() == layer and t.HitTest(v, 0):
                return True
        return False

    def req_track(self, a, b):
        """masked track (stub) to foreign copper: functional 0.2 mm between power domains, the 4.0 mm barrier to the
        control side (the 0.5 mm rule is for bare pads only)"""
        r = self.req(a, b)
        return r if r > 0.5 else (0.0 if a == b else 0.2)

    def _hard_zone(self, a, b):
        """foreign pours pull back around a new pad by the rule distance, except across the 1200 V barrier"""
        return self.req(a, b) > 0.5

    def _seg_clear(self, items, net, layer, a, b, w=0.25, avoid=()):
        if getattr(self, "_scratch", None) is None:     # one scratch track for all tests (no per-test allocation)
            self._scratch = pcbnew.PCB_TRACK(self.b)
        t = self._scratch
        t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        t.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
        t.SetWidth(MM(w))
        t.SetLayer(layer)
        sh = t.GetEffectiveShape(layer)
        for q, qn in avoid:
            if qn != net and q.GetEffectiveShape(layer).Collide(sh, MM(max(self.req_track(net, qn), 0.2))):
                return None
        for q in items["pads"]:
            if q.IsOnLayer(layer) and q.GetNetname() != net and                     q.GetEffectiveShape(layer).Collide(sh, MM(max(self.req_track(net, q.GetNetname()), 0.2))):
                return None
        for u in items["tracks"]:
            if u.IsOnLayer(layer) and u.GetNetname() != net and                     u.GetEffectiveShape(layer).Collide(sh, MM(self.req_track(net, u.GetNetname()))):
                return None
        for z in items["zones"]:
            if z.IsOnLayer(layer) and z.GetNetname() != net and self._hard_zone(net, z.GetNetname()) and                     z.GetFilledPolysList(layer).Collide(sh, MM(self.req(net, z.GetNetname()))):
                return None
        new = pcbnew.PCB_TRACK(self.b)                 # the accepted stub: a fresh object for the board
        new.SetStart(t.GetStart())
        new.SetEnd(t.GetEnd())
        new.SetWidth(t.GetWidth())
        new.SetLayer(layer)
        return new

    def _connect(self, items, net, layer, pt, reach=4.0, avoid=()):
        """None if pt already sits on copper of the net, a stub track to the nearest own trace / pad / via, or False"""
        if self._on_own(items, net, layer, pt, zones=self.zone_conn):
            return None
        targets = []
        for t in items["tracks"]:
            if t.GetNetname() != net or not t.IsOnLayer(layer):
                continue
            if t.GetClass() == "PCB_VIA":
                targets.append((TO(t.GetPosition().x), TO(t.GetPosition().y)))
                continue
            ax, ay, bx, by = TO(t.GetStart().x), TO(t.GetStart().y), TO(t.GetEnd().x), TO(t.GetEnd().y)
            L2 = (bx - ax) ** 2 + (by - ay) ** 2 or 1e-9
            u = max(0.0, min(1.0, ((pt[0] - ax) * (bx - ax) + (pt[1] - ay) * (by - ay)) / L2))
            targets.append((ax + u * (bx - ax), ay + u * (by - ay)))
            targets += [(ax, ay), (bx, by)]
        for q in items["pads"]:
            if q.GetNetname() == net and q.IsOnLayer(layer) and (q.GetPosition().x, q.GetPosition().y) not in items["tp"]:
                targets.append((TO(q.GetPosition().x), TO(q.GetPosition().y)))
        for tx, ty in sorted(targets, key=lambda q: (q[0] - pt[0]) ** 2 + (q[1] - pt[1]) ** 2):
            if (tx - pt[0]) ** 2 + (ty - pt[1]) ** 2 > reach * reach:
                break
            t = self._seg_clear(items, net, layer, pt, (tx, ty), avoid=avoid)
            if t is not None:
                return [t]
        if not self.zone_conn:                           # a stub out of the part into the open pour (>= 3 mm away)
            import math as _m
            for d in (3.0, 3.5, 4.0):
                for k in range(16):
                    tx = pt[0] + d * _m.cos(k * _m.pi / 8)
                    ty = pt[1] + d * _m.sin(k * _m.pi / 8)
                    if self._on_own(items, net, layer, (tx, ty)) and                             all(self._on_own(items, net, layer, (tx + ox, ty + oy))
                                for ox, oy in ((0.5, 0), (-0.5, 0), (0, 0.5), (0, -0.5))):
                        t = self._seg_clear(items, net, layer, pt, (tx, ty), avoid=avoid)
                        if t is not None:
                            return [t]
        if self.via_fallback:
            return self._via_to_other_side(items, net, layer, pt, avoid=avoid)
        return False

    def _via_ok(self, items, net, x, y):
        """a 0.6 / 0.3 mm through via at (x, y) clear of every foreign pad, track and via on all copper layers
        (tented: functional spacing, the barrier to the control side)"""
        if getattr(self, "_scratch_via", None) is None:
            self._scratch_via = pcbnew.PCB_VIA(self.b)
            self._scratch_via.SetWidth(MM(0.6))
            self._scratch_via.SetDrill(MM(0.3))
        v = self._scratch_via
        v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        pt = pcbnew.VECTOR2I(MM(x), MM(y))
        for z in self.b.Zones():                         # keepouts that forbid vias (1200 V barrier moats)
            if z.GetIsRuleArea() and z.GetDoNotAllowVias() and z.Outline().Collide(pt, MM(0.35)):
                return False
        for lay in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
            sh = v.GetEffectiveShape(lay)
            for q in items["pads"]:
                if q.IsOnLayer(lay) and q.GetNetname() != net and \
                        q.GetEffectiveShape(lay).Collide(sh, MM(max(self.req_track(net, q.GetNetname()), 0.2))):
                    return False
            for u in items["tracks"]:
                if u.IsOnLayer(lay) and u.GetNetname() != net and \
                        u.GetEffectiveShape(lay).Collide(sh, MM(max(self.req_track(net, u.GetNetname()), 0.2))):
                    return False
            for z in items["zones"]:
                if z.IsOnLayer(lay) and z.GetNetname() != net and self._hard_zone(net, z.GetNetname()) and \
                        z.GetFilledPolysList(lay).Collide(sh, MM(self.req(net, z.GetNetname()))):
                    return False
        return True

    def _via_to_other_side(self, items, net, layer, pt, reach=3.0, step=0.25, avoid=()):
        """stub from pt to a new through via whose other outer layer sits on copper of the net"""
        other = pcbnew.F_Cu if layer == pcbnew.B_Cu else pcbnew.B_Cu
        n = int(reach / step)
        cand = sorted(((pt[0] + i * step, pt[1] + j * step) for i in range(-n, n + 1) for j in range(-n, n + 1)
                       if (i * i + j * j) * step * step <= reach * reach),
                      key=lambda q: (q[0] - pt[0]) ** 2 + (q[1] - pt[1]) ** 2)
        for vx, vy in cand:
            if not self._on_own(items, net, other, (vx, vy)) or not self._via_ok(items, net, vx, vy):
                continue
            t = self._seg_clear(items, net, layer, pt, (vx, vy), avoid=avoid) if (vx, vy) != pt else None
            if t is None and (vx, vy) != pt:
                continue
            v = pcbnew.PCB_VIA(self.b)
            v.SetPosition(pcbnew.VECTOR2I(MM(vx), MM(vy)))
            v.SetWidth(MM(0.6))
            v.SetDrill(MM(0.3))
            v.SetRemoveUnconnected(True)
            v.SetKeepStartEnd(True)
            return [x for x in (t, v) if x is not None]
        return False

    def _clear(self, items, fp, nets, layer, side):
        """every pad of fp clear of all foreign copper and all existing pads; fp clear of courtyards"""
        for p, net in zip(sorted(fp.Pads(), key=lambda q: q.GetNumber()), nets):
            sh = p.GetEffectiveShape(layer)
            for q in items["pads"]:
                if not q.IsOnLayer(layer):
                    continue
                c = max(self.req(net, q.GetNetname()), 0.2)
                if q.GetEffectiveShape(layer).Collide(sh, MM(c)):
                    return False
            for t in items["tracks"]:
                if t.GetNetname() == net or not t.IsOnLayer(layer):
                    continue
                if t.GetClass() == "PCB_VIA" and t.GetNetname() in self.soft_vias:
                    continue                            # may be removed under the part (see try_at)
                if t.GetEffectiveShape(layer).Collide(sh, MM(self.req(net, t.GetNetname()))):
                    return False
            for z in items["zones"]:
                if z.GetNetname() == net or not z.IsOnLayer(layer) or not self._hard_zone(net, z.GetNetname()):
                    continue
                if z.GetFilledPolysList(layer).Collide(sh, MM(self.req(net, z.GetNetname()))):
                    return False
        cl = pcbnew.F_CrtYd if side == "top" else pcbnew.B_CrtYd
        fp.BuildCourtyardCaches()
        own = fp.GetCourtyard(cl)
        for f in items["crt"]:
            cy = f.GetCourtyard(cl)
            if cy.OutlineCount() == 0:
                continue
            for p in fp.Pads():
                if cy.Collide(p.GetEffectiveShape(layer), MM(0.15)):
                    return False
            if own.OutlineCount():
                c = pcbnew.SHAPE_POLY_SET(cy)
                c.BooleanIntersection(own, pcbnew.SHAPE_POLY_SET.PM_FAST)
                if c.OutlineCount():
                    return False
        bb = fp.GetBoundingBox(False, False)
        x0, y0, x1, y1 = self.outline
        return TO(bb.GetLeft()) > x0 + 0.6 and TO(bb.GetRight()) < x1 - 0.6 and TO(bb.GetTop()) > y0 + 0.6 and \
            TO(bb.GetBottom()) < y1 - 0.6

    def try_at(self, kind, ref, value, pnets, side, x, y, rot):
        """place at a given spot if it is still valid (cache), True / False"""
        layer = pcbnew.B_Cu if side == "bottom" else pcbnew.F_Cu
        items = self._window(x, y, 12.0)
        fp = make(self.b, kind, ref, value)
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetOrientationDegrees(rot)
        if side == "bottom":
            fp.Flip(fp.GetPosition(), False)
        gpos = [(TO(p.GetPosition().x), TO(p.GetPosition().y)) for p in sorted(fp.Pads(), key=lambda q: q.GetNumber())]
        if not self._clear(items, fp, pnets, layer, side):
            return False
        own = list(zip(sorted(fp.Pads(), key=lambda q: q.GetNumber()), pnets))
        stubs = [self._connect(items, net, layer, gp, avoid=own) for net, gp in zip(pnets, gpos)]
        if any(st is False for st in stubs):
            return False
        for st, net in zip(stubs, pnets):              # a stub must not pass the part's own pads of another net
            for obj in (st or []):
                for q, qn in own:
                    if qn != net and any(q.GetEffectiveShape(L).Collide(obj.GetEffectiveShape(L),
                                                                         MM(max(self.req_track(net, qn), 0.2)))
                                         for L in (layer,) if obj.IsOnLayer(L)):
                        return False
        for p, net in zip(sorted(fp.Pads(), key=lambda q: q.GetNumber()), pnets):
            p.SetNet(self.b.FindNet(net))
        for t in items["tracks"]:                       # soft vias under the part go
            if t.GetClass() == "PCB_VIA" and t.GetNetname() in self.soft_vias and t.GetNetname() not in pnets and any(
                    t.GetEffectiveShape(layer).Collide(p.GetEffectiveShape(layer),
                                                       MM(self.req(net, t.GetNetname())))
                    for p, net in zip(sorted(fp.Pads(), key=lambda q: q.GetNumber()), pnets)):
                self.removed_vias.append((ref, t.GetNetname(), TO(t.GetPosition().x), TO(t.GetPosition().y)))
                self.b.Remove(t)
        self.b.Add(fp)
        added = [fp]
        for st, net in zip(stubs, pnets):
            for obj in (st or []):
                obj.SetNet(self.b.FindNet(net))
                self.b.Add(obj)
                added.append(obj)
        self.placed.append(dict(ref=ref, kind=kind, value=value, nets=list(pnets), side=side, x=x, y=y, rot=rot,
                                pads=gpos, items=added))
        return True

    def remove(self, ref):
        for d in [d for d in self.placed if d["ref"] == ref]:
            for it in d["items"]:
                self.b.Remove(it)
            self.placed.remove(d)
            self.banned.add((d["value"], d["side"], round(d["x"], 2), round(d["y"], 2)))

    def place(self, kind, ref, value, nets, anchor, sides=("bottom", "top"), reach=(6.0, 11.0), step=0.2):
        """nets: (signal,) for TP, (signal, ground) for SPRING; alternative signal nets may be given as a tuple"""
        sig_opts = nets[0] if isinstance(nets[0], tuple) else (nets[0],)
        ax, ay = anchor
        tpl = {}
        for r in reach:
            items = self._window(ax, ay, r + 7.0)
            n = int(r / step)
            cand = sorted(((i * step, j * step) for i in range(-n, n + 1) for j in range(-n, n + 1)
                           if (i * i + j * j) * step * step <= r * r), key=lambda d: d[0] ** 2 + d[1] ** 2)
            for side in sides:
                layer = pcbnew.B_Cu if side == "bottom" else pcbnew.F_Cu
                for sig in sig_opts:
                    pnets = (sig,) + tuple(nets[1:])
                    for dx, dy in cand:
                        x, y = ax + dx, ay + dy
                        if (value, side, round(x, 2), round(y, 2)) in self.banned:
                            continue
                        for rot in ((0, 90, 180, 270) if kind in ("SPRING", "MMCX") else (0,)):
                            fp = tpl.get((side, rot))          # one template per side / rotation, moved around
                            if fp is None:
                                fp = make(self.b, kind, ref, value)
                                fp.SetOrientationDegrees(rot)
                                if side == "bottom":
                                    fp.Flip(fp.GetPosition(), False)
                                tpl[(side, rot)] = fp
                            fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
                            if not self._clear(items, fp, pnets, layer, side):
                                continue
                            gpos = [(TO(p.GetPosition().x), TO(p.GetPosition().y))
                                    for p in sorted(fp.Pads(), key=lambda q: q.GetNumber())]
                            own = list(zip(sorted(fp.Pads(), key=lambda q: q.GetNumber()), pnets))
                            if any(self._connect(items, net, layer, gp, avoid=own) is False
                                   for net, gp in zip(pnets, gpos)):
                                continue
                            if self.try_at(kind, ref, value, pnets, side, x, y, rot):   # the real objects, once
                                return True
        self.log("test point %s (%s) not placed" % (ref, value))
        return False


DOMAINS = {
    "CTRL": ("GNDI", "+12V", "12V_CM", "C_", "PWM_", "DIS", "INA", "INB", "VDDI", "NTC"),
    "HS": ("SW", "KH", "VDDA", "VEEA", "GH_", "OUTA", "OFFA", "VINA_", "UFL_H"),
    "LS": ("DCN", "LSRC", "KL", "VDDB", "VEEB", "GL_", "OUTB", "OFFB", "VINB_", "UFL_L", "UFL_D"),
    "DCP": ("DCP", "HVA", "HVB"),
}


def dom_of(net):
    for d, pre in DOMAINS.items():
        if net.startswith(pre):
            return d
    return None


def plan(board):
    """[(kind, value, nets, anchor (x, y) mm, sides)] for both driver blocks and the board-level points"""
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    nets = set(board.GetNetsByName().keys())
    nets = set(str(n) for n in nets)

    def at(ref, dx=0.0, dy=0.0):
        p = fps[ref].GetPosition()
        return (TO(p.x) + dx, TO(p.y) + dy)

    def fet_of(gate):
        return [r for r, f in fps.items() if r.startswith("Q") and
                any(p.GetNumber() == "1" and p.GetNetname() == gate for p in f.Pads())][0]

    def ref_on(net, prefix):
        return [r for r, f in fps.items() if r.startswith(prefix) and any(p.GetNetname() == net for p in f.Pads())]

    out = []
    for b in (1, 2):
        u = ref_on("VDDI%d" % b, "U")[0]                   # the driver of the block
        for n in ("GNDI", "+12V", "VDDI", "INA", "INB", "DIS"):     # bottom: through a via (room for the label)
            out.append(("TP", n + str(b), (n + str(b),), at(u, 0.0, 6.0), ("top",)))   # no vias into the GNDI area
        for ch, kk in (("A", "KH"), ("B", "KL")):
            cap = ref_on("VDD%s%d" % (ch, b), "C")[0]
            for n in ("VDD" + ch, "VEE" + ch, kk, "OUT" + ch):
                out.append(("TP", n + str(b), (n + str(b),), at(cap), ("bottom", "top")))
        for g, side_name in (("GH_L", "H"), ("GH_R", "H"), ("GL_L", "L"), ("GL_R", "L")):
            gate = g + str(b)
            q = fet_of(gate)
            k = ("KH" if side_name == "H" else "KL") + str(b)
            ufl = [n for n in nets if n.startswith("UFL_" + side_name)]
            alt = tuple([gate] + [n for n in ufl if any(p.GetNetname() == n for r in ref_on(gate, "R")
                                                          for p in fps[r].Pads())])
            out.append(("SPRING", "VGS " + q, (alt, k), at(q), ("bottom", "top")))
    cells = sorted((r for r, f in fps.items() if r.startswith("Q") and
                    any(p.GetNetname().startswith("GL_") and p.GetNumber() == "1" for p in f.Pads())),
                   key=lambda r: TO(fps[r].GetPosition().x))
    for c, ql in enumerate(cells, 1):
        src = "LSRC%d" % c if "LSRC%d" % c in nets else "DCN"
        qh = min((r for r, f in fps.items() if r.startswith("Q") and r != ql and
                  any(p.GetNetname().startswith("GH_") and p.GetNumber() == "1" for p in f.Pads())),
                 key=lambda r: abs(TO(fps[r].GetPosition().x) - TO(fps[ql].GetPosition().x)))
        out.append(("SPRING", "VDS " + ql, ("SW", src), at(ql), ("bottom", "top")))
        out.append(("SPRING", "VDS " + qh, ("DCP", "SW"), at(qh), ("bottom", "top")))
    term = {f.GetValue(): r for r, f in fps.items() if f.GetValue() in ("DC+", "DC-", "AC")}
    out.append(("TP", "DC+", ("DCP",), at(term["DC+"]), ("bottom", "top")))
    out.append(("TP", "DC-", ("DCN",), at(term["DC-"]), ("bottom", "top")))
    out.append(("TP", "SW", ("SW",), at(term["AC"]), ("bottom", "top")))
    if "NTC" in nets:
        out.append(("TP", "NTC", ("NTC",), at(ref_on("NTC", "RT")[0]), ("top",)))
    return out


def _unconnected(board, tmp_report):
    """refill, DRC; [(text, [(x, y), ...])] of the unconnected-item entries"""
    import re
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    pcbnew.WriteDRCReport(board, tmp_report, pcbnew.EDA_UNITS_MILLIMETRES, True)
    txt = open(tmp_report, encoding="utf-8", errors="replace").read()
    out = []
    for blk in re.split(r"\n(?=\[)", txt):
        if blk.startswith("[unconnected_items]"):
            pts = [(float(a), float(b)) for a, b in re.findall(r"@\(([-0-9.]+) mm, ([-0-9.]+) mm\)", blk)]
            out.append((blk, pts))
    return out


def _unconnected_tps(board, tmp_report, placed=(), base=()):
    """test points that are unconnected themselves or sit within 10 mm of a new unconnected item (pour split)"""
    import re
    bad = set()
    basekeys = set(re.sub(r"\s+", " ", b_) for b_, _ in base)
    for blk, pts in _unconnected(board, tmp_report):
        named = set(re.findall(r"of (TP\d+)", blk))
        bad |= named
        if named or re.sub(r"\s+", " ", blk) in basekeys:
            continue                                      # a test point that is itself open: only that one goes
        for x, y in pts:                                  # nearest of everything a test point added (pads, stubs, vias)
            near = []
            for d in placed:
                pts_ = list(d["pads"])
                for it in d.get("items", [])[1:]:
                    if it.GetClass() == "PCB_VIA":
                        pts_.append((TO(it.GetPosition().x), TO(it.GetPosition().y)))
                    else:
                        pts_ += [(TO(it.GetStart().x), TO(it.GetStart().y)), (TO(it.GetEnd().x), TO(it.GetEnd().y))]
                near.append((min((px - x) ** 2 + (py - y) ** 2 for px, py in pts_), d["ref"]))
            near = [n for n in near if n[0] < 100.0]
            if near:
                bad.add(min(near)[1])
    return bad


def _fallback(board, net, anchor):
    """nearest existing outer-layer pad of a net (not a test point) for probing instead"""
    best = None
    for fp in board.GetFootprints():
        if fp.GetReference().startswith(("TP", "Q", "U")):   # LGA pads of the FETs / drivers cannot be probed
            continue
        for p in fp.Pads():
            if p.GetNetname() != net or not (p.IsOnLayer(pcbnew.F_Cu) or p.IsOnLayer(pcbnew.B_Cu)):
                continue
            d = (TO(p.GetPosition().x) - anchor[0]) ** 2 + (TO(p.GetPosition().y) - anchor[1]) ** 2
            if best is None or d < best[0]:
                best = (d, "%s pad %s (%s)" % (fp.GetReference(), p.GetNumber(),
                                               "bottom" if fp.IsFlipped() else "top"))
    return best[1] if best else "-"


def save_footprints(board, lib_path):
    """the test-point footprints into the board's own library (library check of the DRC); the MMCX jack is placed
    and saved by the board generator (with its project 3D model)"""
    for kind in ("TP", "SPRING"):
        fp = make(board, kind, "REF**", "TestPoint")
        pcbnew.FootprintSave(lib_path, fp)


def place_cached(P, cache, kind, ref, val, nets, anc, sides):
    """cached spot first, then a search; returns True if placed"""
    c = cache.get(val)
    if c and not c.get("failed") and P.try_at(kind, ref, val, tuple(c["nets"]), c["side"], c["x"], c["y"], c["rot"]):
        return True
    if c and c.get("failed"):
        return False
    return P.place(kind, ref, val, nets, anc, sides)


def mmcx_vds(board, outline, cache_path, lib_path, log=print):
    """one MMCX jack per cell for V_DS of the low-side switch: centre = SW (drain), shield = LSRCx (source, device side
    of the shunt), on the bottom next to the LS FET. Returns [(ref, value, x, y, rot)] for the parts list."""
    import json
    import os
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    nets = set(str(n) for n in board.GetNetsByName().keys())
    ls = sorted((r for r, f in fps.items() if r.startswith("Q") and
                 any(p.GetNumber() == "1" and p.GetNetname().startswith("GL_") for p in f.Pads())),
                key=lambda r: TO(fps[r].GetPosition().x))
    nj = max(int(r[1:]) for r in fps if r.startswith("J") and r[1:].isdigit()) + 1
    P = Placer(board, dom_of, outline, log)
    P.soft_vias = {"DCN"}                              # DC- via fields: the vias under the jack are removed
    P.via_fallback = True                              # shield to LSRC: through a via to the shunt IN land (top)
    P.zone_conn = False                                # explicit stub / via for every pin (pour fragments get dropped)
    cx = [TO(fps[q].GetPosition().x) for q in ls]
    xb = (cx[0] + cx[1]) / 2, (cx[0] + cx[3]) / 2      # block-1 centre and board centre (mirror axes)
    mirror = {2: lambda x: 2 * xb[0] - x, 4: lambda x: 2 * xb[1] - x, 3: lambda x: 2 * xb[1] - (2 * xb[0] - x)}
    out, new = [], {}
    first = None
    for c, q in enumerate(ls, 1):
        src = "LSRC%d" % c if "LSRC%d" % c in nets else "DCN"
        ref, val = "J%d" % nj, "MMCX VDS L%d" % c
        p = fps[q].GetPosition()
        ok = False
        if first is not None and c in mirror:           # cells are mirror images: same spot, mirrored
            for rot in (first["rot"], (180 - first["rot"]) % 360):
                if P.try_at("MMCX", ref, val, ("SW", src, src), "bottom", mirror[c](first["x"]), first["y"], rot):
                    ok = True
                    break
            if not ok:
                log("MMCX %s: mirrored spot of cell 1 not free, searching" % val)
        if ok or place_cached(P, cache, "MMCX", ref, val, ("SW", src, src), (TO(p.x), TO(p.y)), ("bottom",)):
            if c == 1:
                first = P.placed[-1]
            d = P.placed[-1]
            new[val] = {k: d[k] for k in ("nets", "side", "x", "y", "rot")}
            out.append((ref, val, d["x"], d["y"], d["rot"]))
            nj += 1
        else:
            new[val] = {"failed": True}
            log("MMCX %s: no spot" % val)
    json.dump(new, open(cache_path, "w"), indent=1)
    for rf in sorted(set(r[0] for r in P.removed_vias)):
        log("MMCX %s: %d DC- vias removed under the jack" % (rf, sum(1 for r in P.removed_vias if r[0] == rf)))
    return out


def run(board, outline, cache_path, csv_path, tmp_report, origin, log=print, lib_path=None, label_fn=None):
    """place the planned points (cache first), drop and re-place those that end up unconnected after the fill,
    write the cache and the bring-up list. origin: (x, y) mm subtracted for the list coordinates."""
    import json
    import os
    if lib_path:
        save_footprints(board, lib_path)
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    base = _unconnected(board, tmp_report)               # what is open before the test points (should be nothing)
    P = Placer(board, dom_of, outline, log)

    todo = plan(board)
    meta = {}
    for k, (kind, val, nets, anc, sides) in enumerate(todo):
        ref = "TP%d" % (k + 1)
        meta[ref] = (kind, val, nets, anc, sides)
        c = cache.get(val)
        ok = bool(c) and not c.get("failed") and P.try_at(kind, ref, val, tuple(c["nets"]), c["side"], c["x"], c["y"],
                                                          c["rot"])
        if not ok and not (c and c.get("failed")):
            ok = P.place(kind, ref, val, nets, anc, sides)
        if not ok:
            log("test point %s (%s): no spot, fallback pad listed" % (ref, val))
    for it in range(3):
        bad = _unconnected_tps(board, tmp_report, P.placed, base)
        if not bad:
            break
        last = it >= 1                                   # second time: give up, list a fallback pad instead
        log("test points disconnected after the fill (pour split), %s: %s" % ("dropped" if last else "re-placed",
                                                                            " ".join(sorted(bad))))
        for ref in bad:
            P.remove(ref)
            if not last:
                kind, val, nets, anc, sides = meta[ref]
                P.place(kind, ref, val, nets, anc, sides)
    labelled = {}
    if label_fn:                                         # name on the silk right at the pad, or the point moves
        for rnd in range(3):
            moved = []
            for d in list(P.placed):
                if d["ref"] in labelled:
                    continue
                lab = label_fn(d, last=(rnd == 2))
                if lab:
                    labelled[d["ref"]] = lab
                elif rnd < 2:
                    moved.append(d["ref"])
            if not moved:
                break
            log("test points moved for room for their silk label: %s" % " ".join(moved))
            for ref in moved:
                P.remove(ref)
                kind, val, nets, anc, sides = meta[ref]
                P.place(kind, ref, val, nets, anc, sides)
            if moved:                                    # the moves may split pours again
                bad = _unconnected_tps(board, tmp_report, P.placed, base)
                for ref in bad:
                    P.remove(ref)
                    log("test point %s dropped (pour split after the label move)" % ref)
    if label_fn:                                         # every test point on the board carries its name
        for d in [d for d in P.placed if d["ref"] not in labelled]:
            log("test point %s (%s): no room for its silk label, not placed (fallback pad listed)" % (d["ref"], d["value"]))
            P.remove(d["ref"])
    placed = {d["value"]: d for d in P.placed}
    new_cache = {}
    rows = ["ref,kind,name,signal net,ground net,side,x mm,y mm,note"]
    for ref, (kind, val, nets, anc, sides) in meta.items():
        d = placed.get(val)
        if d:
            new_cache[val] = {k: d[k] for k in ("nets", "side", "x", "y", "rot")}
            rows.append("%s,%s,%s,%s,%s,%s,%.2f,%.2f,%s" % (
                ref, "spring pad" if kind == "SPRING" else "test point", val, d["nets"][0],
                d["nets"][1] if len(d["nets"]) > 1 else "", d["side"], d["x"] - origin[0], d["y"] - origin[1],
                ("ground pad = oval, 1.5..6.0 mm from the signal pad; " if kind == "SPRING" else "") +
                ("silk label '%s'" % labelled[d["ref"]] if d["ref"] in labelled else "no silk label (no room)")))
        else:
            new_cache[val] = {"failed": True}
            sig = nets[0][0] if isinstance(nets[0], tuple) else nets[0]
            note = "no labelled test point fits: probe " + _fallback(board, sig, anc)
            if kind == "SPRING":
                note += " / ground " + _fallback(board, nets[1], anc)
            rows.append("%s,%s,%s,%s,%s,-,-,-,%s" % ("-", "spring pad" if kind == "SPRING" else "test point", val,
                                                     sig, nets[1] if kind == "SPRING" else "", note))
    json.dump(new_cache, open(cache_path, "w"), indent=1)
    open(csv_path, "w", encoding="utf-8").write("\n".join(rows) + "\n")
    return P.placed

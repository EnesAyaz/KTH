"""
Small grid router (A*, 0.1 mm grid, octilinear moves + string pulling, through vias) for the auxiliary nets of the
SPB fabrication board (scripts/make_kicad_bb_fab.py). Power copper and the gate loops are placed by hand; this
router only connects the gate-supply, primary-side and sensing nets inside per-net allowed regions, so that the
isolation domains (HS = SW, LS = DC-, primary = GNDI) never mix.

Obstacles are every pad, track, via and zone of another net, inflated by clearance + half trace width (+ margin).
Own-net copper (pads, tracks, vias and the zones listed as targets) is source/target.
"""
import heapq
import math

import numpy as np
import pcbnew

RES = 0.1
MARGIN = 0.03


def mm(v):
    return pcbnew.ToMM(v)


class Router:
    def __init__(self, board, box, layers, clearance=0.15, edge=0.5):
        self.b = board
        self.x0, self.y0, x1, y1 = box
        self.nx = int(round((x1 - self.x0) / RES)) + 1
        self.ny = int(round((y1 - self.y0) / RES)) + 1
        self.layers = layers
        self.cl = clearance
        self.edge = edge
        self.box = box
        self.X = self.x0 + np.arange(self.nx) * RES
        self.Y = self.y0 + np.arange(self.ny) * RES
        self.objs = []
        self._collect()

    # ------------------------------------------------------------------ geometry
    def _collect(self):
        L = self.layers
        for fp in self.b.GetFootprints():
            for p in fp.Pads():
                bb = p.GetBoundingBox()
                r = (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))
                lays = [i for i, l in enumerate(L) if p.IsOnLayer(l)]
                extra = 0.12 if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else 0.0
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    lays = list(range(len(L)))
                self.objs.append(dict(net=p.GetNetname(), lays=lays, kind="rect", g=r, extra=extra, pad=p))
        for t in self.b.GetTracks():
            if t.GetClass() == "PCB_VIA":
                c = (mm(t.GetPosition().x), mm(t.GetPosition().y))
                self.objs.append(dict(net=t.GetNetname(), lays=list(range(len(L))), kind="circ",
                                      g=(c[0], c[1], mm(t.GetWidth()) / 2), extra=0.0))
            else:
                if t.GetLayer() not in L:
                    continue
                s, e = t.GetStart(), t.GetEnd()
                self.objs.append(dict(net=t.GetNetname(), lays=[L.index(t.GetLayer())], kind="seg",
                                      g=(mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(t.GetWidth()) / 2), extra=0.0))
        for z in self.b.Zones():
            if z.GetIsRuleArea():
                continue
            if z.GetLayer() not in L:
                continue
            bb = z.GetBoundingBox()
            r = (mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom()))
            self.objs.append(dict(net=z.GetNetname(), lays=[L.index(z.GetLayer())], kind="rect", g=r,
                                  extra=max(0.0, mm(z.GetLocalClearance()) - self.cl), zone=True))

    def _window(self, xa, ya, xb, yb):
        i0 = max(0, int(math.floor((xa - self.x0) / RES)))
        i1 = min(self.nx, int(math.ceil((xb - self.x0) / RES)) + 1)
        j0 = max(0, int(math.floor((ya - self.y0) / RES)))
        j1 = min(self.ny, int(math.ceil((yb - self.y0) / RES)) + 1)
        return i0, i1, j0, j1

    def _dist(self, o, i0, i1, j0, j1):
        X = self.X[i0:i1][None, :]
        Y = self.Y[j0:j1][:, None]
        if o["kind"] == "rect":
            xa, ya, xb, yb = o["g"]
            dx = np.maximum(np.maximum(xa - X, X - xb), 0)
            dy = np.maximum(np.maximum(ya - Y, Y - yb), 0)
            return np.hypot(dx, dy)
        if o["kind"] == "circ":
            cx, cy, r = o["g"]
            return np.maximum(np.hypot(X - cx, Y - cy) - r, 0)
        xa, ya, xb, yb, hw = o["g"]
        vx, vy = xb - xa, yb - ya
        ll = vx * vx + vy * vy
        if ll < 1e-12:
            t = np.zeros_like(X + Y)
        else:
            t = np.clip(((X - xa) * vx + (Y - ya) * vy) / ll, 0, 1)
        return np.maximum(np.hypot(X - (xa + t * vx), Y - (ya + t * vy)) - hw, 0)

    def _bounds(self, o, infl):
        if o["kind"] == "rect":
            xa, ya, xb, yb = o["g"]
        elif o["kind"] == "circ":
            cx, cy, r = o["g"]
            xa, ya, xb, yb = cx - r, cy - r, cx + r, cy + r
        else:
            xa_, ya_, xb_, yb_, hw = o["g"]
            xa, xb = min(xa_, xb_) - hw, max(xa_, xb_) + hw
            ya, yb = min(ya_, yb_) - hw, max(ya_, yb_) + hw
        return xa - infl, ya - infl, xb + infl, yb + infl

    def _mark(self, arr, o, infl, value=True):
        i0, i1, j0, j1 = self._window(*self._bounds(o, infl))
        if i0 >= i1 or j0 >= j1:
            return
        d = self._dist(o, i0, i1, j0, j1)
        arr[j0:j1, i0:i1] |= d < infl

    # ------------------------------------------------------------------ routing
    def route_net(self, net, regions, width=0.25, via=(0.6, 0.3), targets_zones=True, vias_ok=True):
        """regions: list of (layer index, x0, x1, y0, y1) allowed for this net. Connect every pad of `net` that lies
        inside the regions to the net's copper inside the regions. Returns number of failed connections."""
        nL = len(self.layers)
        it = self.cl + width / 2 + MARGIN
        iv = self.cl + via[0] / 2 + MARGIN
        blk_t = [np.zeros((self.ny, self.nx), bool) for _ in range(nL)]
        blk_v = np.zeros((self.ny, self.nx), bool)
        allow = [np.zeros((self.ny, self.nx), bool) for _ in range(nL)]
        for li, xa, xb, ya, yb in regions:
            i0, i1, j0, j1 = self._window(xa, ya, xb, yb)
            allow[li][j0:j1, i0:i1] = True
        # board edge
        e = int(round(self.edge / RES))
        for a in allow:
            a[:e, :] = False
            a[-e:, :] = False
            a[:, :e] = False
            a[:, -e:] = False
        own = [np.zeros((self.ny, self.nx), bool) for _ in range(nL)]
        pads = []
        for o in self.objs:
            if o["net"] == net:
                if o.get("pad") is not None:
                    pads.append(o)
                    continue
                for li in o["lays"]:
                    if o.get("zone") and not targets_zones:
                        continue
                    self._mark(own[li], o, 1e-6 + (0.0 if o["kind"] != "rect" else 0.0))
                continue
            if o.get("zone") and o["net"] not in ("DCP", "DCN", "SW"):
                continue                        # domain pours yield to tracks/vias of other nets
            for li in o["lays"]:
                self._mark(blk_t[li], o, it + o["extra"])
            self._mark(blk_v, o, iv + o["extra"])
        free = [allow[li] & ~blk_t[li] for li in range(nL)]
        vfree = np.logical_and.reduce([allow[li] for li in range(nL) if True]) if False else None
        # vias: need via clearance on every layer and to be inside at least one allowed layer at both ends;
        # through vias pierce every layer, so require ~blk_v everywhere
        vfree = ~blk_v
        # pads inside the regions
        todo = []
        for o in pads:
            cells = np.zeros((self.ny, self.nx), bool)
            xa, ya, xb, yb = o["g"]
            i0, i1, j0, j1 = self._window(xa + 0.02, ya + 0.02, xb - 0.02, yb - 0.02)
            ok = False
            for li in o["lays"]:
                if allow[li][j0:j1, i0:i1].any():
                    ok = True
            if ok:
                todo.append(o)
        print("  route", net, "pads", len(pads), "in-region", len(todo), flush=True)
        if not todo:
            return 0
        # tree = own copper inside allowed region (existing tracks, zones, pads already joined)
        tree = [own[li] & allow[li] for li in range(nL)]

        def pad_cells(o):
            xa, ya, xb, yb = o["g"]
            out = []
            for li in o["lays"]:
                a = np.zeros((self.ny, self.nx), bool)
                cx, cy = (xa + xb) / 2, (ya + yb) / 2
                hx, hy = max((xb - xa) / 2 - 0.05, 0.02), max((yb - ya) / 2 - 0.05, 0.02)
                if o["pad"].GetShape() in (pcbnew.PAD_SHAPE_CIRCLE, pcbnew.PAD_SHAPE_OVAL):
                    hx, hy = hx * 0.68, hy * 0.68
                i0 = int(math.ceil((cx - hx - self.x0) / RES - 1e-9))
                i1 = int(math.floor((cx + hx - self.x0) / RES + 1e-9)) + 1
                j0 = int(math.ceil((cy - hy - self.y0) / RES - 1e-9))
                j1 = int(math.floor((cy + hy - self.y0) / RES + 1e-9)) + 1
                if i1 <= i0:
                    i0, i1 = int(round((cx - self.x0) / RES)), int(round((cx - self.x0) / RES)) + 1
                if j1 <= j0:
                    j0, j1 = int(round((cy - self.y0) / RES)), int(round((cy - self.y0) / RES)) + 1
                a[j0:j1, i0:i1] = True
                out.append((li, a))
            return out

        def touches(o):
            # pad connected already if tree copper (other than the pad itself) overlaps it
            return False

        # seed: if tree is empty, use the first pad
        if not any(t.any() for t in tree):
            for li, a in pad_cells(todo[0]):
                tree[li] |= a
            todo = todo[1:]
        fails = 0
        # order: nearest first
        while todo:
            tcells = [(li, np.argwhere(tree[li])) for li in range(nL)]
            best = None
            for k, o in enumerate(todo):
                xa, ya, xb, yb = o["g"]
                cx, cy = (xa + xb) / 2, (ya + yb) / 2
                ci, cj = (cx - self.x0) / RES, (cy - self.y0) / RES
                d = min((np.min(np.hypot(c[:, 1] - ci, c[:, 0] - cj)) for li, c in tcells if len(c)), default=1e9)
                if best is None or d < best[0]:
                    best = (d, k)
            o = todo.pop(best[1])
            tgt = pad_cells(o)
            # already touching tree?
            if any((tree[li] & a).any() for li, a in tgt):
                for li, a in tgt:
                    tree[li] |= a
                continue
            path = self._astar(tree, tgt, free, vfree, vias_ok)
            if path is None:
                fails += 1
                print("  ROUTE FAIL", net, "pad", o["pad"].GetParent().GetReference(), o["pad"].GetNumber(), flush=True)
                continue
            n0 = len(self.objs)
            self._emit(path, net, width, via, free)
            for ob in self.objs[n0:]:
                for li in ob["lays"]:
                    self._mark(tree[li], ob, 1e-6)
            for li, a in tgt:
                tree[li] |= a
        return fails

    def _astar(self, tree, tgt, free, vfree, vias_ok):
        nL = len(self.layers)
        goal = [np.zeros((self.ny, self.nx), bool) for _ in range(nL)]
        for li, a in tgt:
            goal[li] |= a
        gl = [(li, np.argwhere(goal[li])) for li in range(nL)]
        gpts = np.vstack([c for li, c in gl if len(c)])
        gc = gpts.mean(axis=0)

        def h(j, i):
            return math.hypot(j - gc[0], i - gc[1]) * 0.9

        openh = []
        g = {}
        prev = {}
        for li in range(nL):
            for j, i in np.argwhere(tree[li]):
                s = (li, int(j), int(i))
                g[s] = 0.0
                heapq.heappush(openh, (h(j, i), 0.0, s))
        moves = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
                 (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
        lcost = [1.0] + [1.15] * (nL - 2) + [1.3]
        VIA = 18.0
        n = 0
        while openh:
            f, gs, s = heapq.heappop(openh)
            if gs > g.get(s, 1e18):
                continue
            li, j, i = s
            if goal[li][j, i]:
                path = [s]
                while s in prev:
                    s = prev[s]
                    path.append(s)
                return path[::-1]
            n += 1
            if n > 1500000:
                return None
            for dj, di, c in moves:
                jj, ii = j + dj, i + di
                if not (0 <= jj < self.ny and 0 <= ii < self.nx):
                    continue
                if not (free[li][jj, ii] or goal[li][jj, ii]):
                    continue
                if dj and di and not ((free[li][j, ii] or goal[li][j, ii]) and (free[li][jj, i] or goal[li][jj, i])):
                    continue
                t = (li, jj, ii)
                ng = gs + c * lcost[li]
                if ng < g.get(t, 1e18):
                    g[t] = ng
                    prev[t] = s
                    heapq.heappush(openh, (ng + h(jj, ii), ng, t))
            if vias_ok and vfree[j, i]:
                for lj in range(nL):
                    if lj == li or not (free[lj][j, i] or goal[lj][j, i]):
                        continue
                    t = (lj, j, i)
                    ng = gs + VIA
                    if ng < g.get(t, 1e18):
                        g[t] = ng
                        prev[t] = s
                        heapq.heappush(openh, (ng + h(j, i), ng, t))
        return None

    def _xy(self, j, i):
        return self.x0 + i * RES, self.y0 + j * RES

    def _clear_line(self, free, li, a, b, ok=()):
        (ja, ia), (jb, ib) = a, b
        n = int(max(abs(jb - ja), abs(ib - ia)) * 2) + 1
        for k in range(n + 1):
            t = k / n
            j = int(round(ja + (jb - ja) * t))
            i = int(round(ia + (ib - ia) * t))
            if not free[li][j, i] and (j, i) not in ok:
                return False
        return True

    def _emit(self, path, net, width, via, free):
        # split into same-layer runs, string-pull each run (only through free cells, endpoints may be in pads)
        runs = []
        cur = [path[0]]
        for s in path[1:]:
            if s[0] != cur[-1][0]:
                runs.append(cur)
                cur = [s]
            else:
                cur.append(s)
        runs.append(cur)
        board = self.b
        netinfo = board.FindNet(net)
        for r in runs:
            li = r[0][0]
            pts = [(s[1], s[2]) for s in r]
            okc = set(pts)
            out = [pts[0]]
            k = 0
            while k < len(pts) - 1:
                m = len(pts) - 1
                while m > k + 1 and not self._clear_line(free, li, pts[k], pts[m], okc):
                    m -= 1
                out.append(pts[m])
                k = m
            for a, b in zip(out[:-1], out[1:]):
                if a == b:
                    continue
                t = pcbnew.PCB_TRACK(board)
                xa, ya = self._xy(*a)
                xb, yb = self._xy(*b)
                t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(xa), pcbnew.FromMM(ya)))
                t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(xb), pcbnew.FromMM(yb)))
                t.SetWidth(pcbnew.FromMM(width))
                t.SetLayer(self.layers[li])
                t.SetNet(netinfo)
                board.Add(t)
                self.objs.append(dict(net=net, lays=[li], kind="seg", g=(xa, ya, xb, yb, width / 2), extra=0.0))
        for a, b in zip(path[:-1], path[1:]):
            if a[0] != b[0]:
                v = pcbnew.PCB_VIA(board)
                x, y = self._xy(a[1], a[2])
                v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
                v.SetWidth(pcbnew.FromMM(via[0]))
                v.SetDrill(pcbnew.FromMM(via[1]))
                v.SetNet(netinfo)
                v.SetIsFree(True)
                board.Add(v)
                self.objs.append(dict(net=net, lays=list(range(len(self.layers))), kind="circ",
                                      g=(x, y, via[0] / 2), extra=0.0))

    def _add_path_objs(self, path, net, width, via):
        for a, b in zip(path[:-1], path[1:]):
            if a[0] != b[0]:
                x, y = self._xy(a[1], a[2])
                self.objs.append(dict(net=net, lays=list(range(len(self.layers))), kind="circ",
                                      g=(x, y, via[0] / 2), extra=0.0))
            else:
                xa, ya = self._xy(a[1], a[2])
                xb, yb = self._xy(b[1], b[2])
                self.objs.append(dict(net=net, lays=[a[0]], kind="seg", g=(xa, ya, xb, yb, width / 2), extra=0.0))

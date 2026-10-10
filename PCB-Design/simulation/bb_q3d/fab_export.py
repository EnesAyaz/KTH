"""
Export the power-stage copper of the routed fabrication board for Q3D (BB_PL_FAB).

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" simulation\\bb_q3d\\fab_export.py
    -> simulation/bb_q3d/results/fab_geometry.json

Contents (mm, board coordinates with the origin on the symmetry line, y down, as in bb_geometry.py):
  polys:  [net, layer, outline, [holes]]   filled copper of DCP / DCN / SW in the power region, simplified
  vias:   [net, x, y, r]                   power vias (through, L1-L4)
  pads:   [net, name, x0, x1, y0, y1]      FET stripes and capacitor pads (PAD layer, terminal faces)
  terminals: [kind, name, net, [[x, y], ...], side]   same names as BB_PL (bb_to_spice.py loop definition)
"""
import json
import math
import os

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BRD = os.path.join(ROOT, "hardware", "spb-bb-fab", "spb-bb-fab.kicad_pcb")
OX, OY = 100.0, 100.0
REGION = (-16.5, -13.8, 16.5, 14.0)               # x0, y0, x1, y1: bank strips, cells, AC terminal area
NETS = {"DCP": "DCP", "DCN": "DCN", "SW": "AC"}
LAYERS = {pcbnew.F_Cu: "L1", pcbnew.In1_Cu: "L2", pcbnew.In2_Cu: "L3", pcbnew.B_Cu: "L4"}
TOL = 0.03                                         # mm, polygon simplification


def mm(v):
    return pcbnew.ToMM(v)


def dp(pts, tol):
    """Douglas-Peucker on a closed ring."""
    if len(pts) < 5:
        return pts

    def rec(a, b):
        (x0, y0), (x1, y1) = pts[a], pts[b]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1e-12
        imax, dmax = None, 0.0
        for i in range(a + 1, b):
            d = abs(dy * pts[i][0] - dx * pts[i][1] + x1 * y0 - y1 * x0) / L
            if d > dmax:
                imax, dmax = i, d
        if dmax > tol:
            return rec(a, imax)[:-1] + rec(imax, b)
        return [pts[a], pts[b]]

    n = len(pts)
    k = max(range(n), key=lambda i: math.hypot(pts[i][0] - pts[0][0], pts[i][1] - pts[0][1]))
    out = rec(0, k)[:-1] + rec(k, n - 1)[:-1] + [pts[n - 1]]
    return out if len(out) >= 3 else pts


def ring(chain):
    pts = [(round(mm(chain.CPoint(i).x) - OX, 4), round(mm(chain.CPoint(i).y) - OY, 4)) for i in range(chain.PointCount())]
    return [list(p) for p in dp(pts, TOL)]


b = pcbnew.LoadBoard(BRD)
reg = pcbnew.SHAPE_POLY_SET()
reg.NewOutline()
for x, y in ((REGION[0], REGION[1]), (REGION[2], REGION[1]), (REGION[2], REGION[3]), (REGION[0], REGION[3])):
    reg.Append(pcbnew.FromMM(x + OX), pcbnew.FromMM(y + OY))
polys = []
for z in b.Zones():
    if z.GetIsRuleArea() or z.GetNetname() not in NETS or z.GetLayer() not in LAYERS:
        continue
    fp = z.GetFilledPolysList(z.GetLayer())
    ps = pcbnew.SHAPE_POLY_SET(fp)
    ps.Unfracture(pcbnew.SHAPE_POLY_SET.PM_FAST)
    ps.BooleanIntersection(reg, pcbnew.SHAPE_POLY_SET.PM_FAST)
    for i in range(ps.OutlineCount()):
        outl = ring(ps.Outline(i))
        holes = [ring(ps.Hole(i, h)) for h in range(ps.HoleCount(i))]
        holes = [hh for hh in holes if len(hh) >= 3]
        polys.append([NETS[z.GetNetname()], LAYERS[z.GetLayer()], outl, holes])
vias = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA" and t.GetNetname() in NETS:
        x, y = mm(t.GetPosition().x) - OX, mm(t.GetPosition().y) - OY
        if REGION[0] <= x <= REGION[2] and REGION[1] <= y <= REGION[3]:
            vias.append([NETS[t.GetNetname()], round(x, 4), round(y, 4), round(mm(t.GetDrill()) / 2, 4)])

pads, terms = [], []
groups = {}


def add_pad(net, name, p):
    bb = p.GetBoundingBox()
    x0, y0, x1, y1 = mm(bb.GetLeft()) - OX, mm(bb.GetTop()) - OY, mm(bb.GetRight()) - OX, mm(bb.GetBottom()) - OY
    pads.append([net, name, round(x0, 4), round(x1, 4), round(y0, 4), round(y1, 4)])
    return ((x0 + x1) / 2, (y0 + y1) / 2)


for fp in b.GetFootprints():
    ref = fp.GetReference()
    x, y = mm(fp.GetPosition().x) - OX, mm(fp.GetPosition().y) - OY
    if ref in ("Q1", "Q2", "Q3", "Q4"):
        side = "L" if x < 0 else "R"
        hs = ref in ("Q1", "Q2")
        for p in fp.Pads():
            n = p.GetNumber()
            if n == "1":
                continue
            net = NETS[p.GetNetname()]
            drain = n in ("3", "5", "7")
            tname = ("QH_D_" if hs else "QL_D_") + side if drain else ("QH_S_" if hs else "QL_S_") + side
            c = add_pad(net, "%s_%s" % (ref, n), p)
            groups.setdefault(tname, [net, []])[1].append(list(c))
    elif ref.startswith("C") and ref[1:].isdigit() and int(ref[1:]) <= 36:
        k = int(ref[1:])
        if k <= 12:
            grp = "L" if x < 0 else "R"
        else:
            grp = "B%d" % (1 + min(range(3), key=lambda i: abs(y - (-10.7, -6.7, -2.7)[i])))
        for p in fp.Pads():
            net = NETS[p.GetNetname()]
            c = add_pad(net, "%s_%s" % (ref, p.GetNumber()), p)
            pol = "P" if net == "DCP" else "N"
            tname = ("Cap%s%s" % (pol, grp)) if k <= 12 else ("Cap%s%s" % (grp, pol))
            groups.setdefault(tname, [net, []])[1].append(list(c))
for tname, (net, pts) in sorted(groups.items()):
    terms.append(["Source", tname, net, pts, "top"])
# sinks on small pads, as in BB_PL: DC+ on the outer strip P1, DC- on N1, AC on the bottom of the right AC terminal zone
pads.append(["DCP", "T_DCP", -3.0, 3.0, -13.2, -12.6])
pads.append(["DCN", "T_DCN", -3.0, 3.0, -9.6, -7.8])
pads.append(["AC", "T_AC", 6.0, 9.0, 12.6, 13.2])
terms.append(["Sink", "T_DCP", "DCP", [[0.0, -12.9]], "top"])
terms.append(["Sink", "T_DCN", "DCN", [[0.0, -8.7]], "top"])
terms.append(["Sink", "T_AC", "AC", [[7.5, 12.9]], "bottom"])
out = dict(polys=polys, vias=vias, pads=pads, terminals=terms, region=REGION,
           note="routed board %s, simplification %.2f mm" % (os.path.basename(BRD), TOL))
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "fab_geometry.json"), "w"))
npts = sum(len(p[2]) + sum(len(h) for h in p[3]) for p in polys)
print("polys %d (holes %d, points %d), vias %d, pads %d, terminals %d" % (
    len(polys), sum(len(p[3]) for p in polys), npts, len(vias), len(pads), len(terms)))
for t in terms:
    print(t[0], t[1], t[2], len(t[3]))

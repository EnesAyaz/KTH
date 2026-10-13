"""
Export the power copper of the routed Rev B leg board (4 x EPC2361 per switch, UFCS shunt per cell) for Q3D (BB_PL_REVB).

    "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" simulation\\bb_q3d\\revb_export.py
    -> simulation/bb_q3d/results/revb_geometry.json

Same format as fab_export.py (mm, board centre at x = 0, y down, leg-board coordinates):
  polys [net, layer, outline, holes], vias [net, x, y, r], pads [net, name, x0, x1, y0, y1, side], terminals
Nets: DCP, DCN, AC (= SW), LSRC1..4 (low-side source of cell 1..4, ends at the shunt IN pad).
Cells: 1 = block 1 left (Q1/Q3, RS1), 2 = block 1 right (Q2/Q4, RS2), 3 = block 2 left (Q5/Q7), 4 = block 2 right.
Terminals (one sink per net, every other group a source):
  DCP: QH_D_c, CapP_c, BankP_g -> sink J_DCP         DCN: RSN_c (shunt SHLD pad), CapN_c, BankN_g -> sink J_DCN
  AC:  QH_S_c, QL_D_c -> sink J_AC (M6 bolt pad)      LSRCc: QL_S_c -> sink RSI_c (shunt IN pad)
"""
import json
import math
import os

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BRD = os.path.join(ROOT, "hardware", "spb-bb-revb", "spb-bb-revb.kicad_pcb")
OX, OY = 150.0, 100.0
NETS = {"DCP": "DCP", "DCN": "DCN", "SW": "AC", "LSRC1": "LSRC1", "LSRC2": "LSRC2", "LSRC3": "LSRC3", "LSRC4": "LSRC4"}
LAYERS = {pcbnew.F_Cu: "L1", pcbnew.In1_Cu: "L2", pcbnew.In2_Cu: "L3", pcbnew.B_Cu: "L4"}
TOL = 0.05                                         # mm, polygon simplification
MIN_AREA = 0.5                                     # mm^2, drop slivers


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


def area(r):
    return abs(sum(r[i][0] * r[i - 1][1] - r[i - 1][0] * r[i][1] for i in range(len(r)))) / 2


def ring(chain):
    pts = [(round(mm(chain.CPoint(i).x) - OX, 4), round(mm(chain.CPoint(i).y) - OY, 4)) for i in range(chain.PointCount())]
    return [list(p) for p in dp(pts, TOL)]


b = pcbnew.LoadBoard(BRD)
# copper per net and layer: filled zones + tracks, merged
acc = {}
for z in b.Zones():
    if z.GetIsRuleArea() or z.GetNetname() not in NETS:
        continue
    for lay in z.GetLayerSet().Seq():
        if lay not in LAYERS:
            continue
        ps = acc.setdefault((z.GetNetname(), lay), pcbnew.SHAPE_POLY_SET())
        ps.Append(pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(lay)))
for t in b.GetTracks():
    if t.GetClass() == "PCB_TRACK" and t.GetNetname() in NETS and t.GetLayer() in LAYERS:
        ps = acc.setdefault((t.GetNetname(), t.GetLayer()), pcbnew.SHAPE_POLY_SET())
        # track as a rectangle extended by half the width at both ends (round caps approximated)
        x0, y0, x1, y1 = t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y
        L = math.hypot(x1 - x0, y1 - y0) or 1.0
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        h = t.GetWidth() / 2
        ps.NewOutline()
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            ex = (x1 if sx > 0 else x0) + sx * h * ux
            ey = (y1 if sx > 0 else y0) + sx * h * uy
            ps.Append(int(ex - sy * h * uy), int(ey + sy * h * ux))
polys = []
for (n, lay), ps in sorted(acc.items(), key=lambda kv: (kv[0][0], kv[0][1])):
    ps.Simplify(pcbnew.SHAPE_POLY_SET.PM_FAST)
    for i in range(ps.OutlineCount()):
        outl = ring(ps.Outline(i))
        if len(outl) < 3 or area(outl) < MIN_AREA:
            continue
        holes = [ring(ps.Hole(i, h)) for h in range(ps.HoleCount(i))]
        holes = [hh for hh in holes if len(hh) >= 3 and area(hh) > 0.05]
        polys.append([NETS[n], LAYERS[lay], outl, holes])
vias = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA" and t.GetNetname() in NETS:
        vias.append([NETS[t.GetNetname()], round(mm(t.GetPosition().x) - OX, 4), round(mm(t.GetPosition().y) - OY, 4),
                     round(mm(t.GetDrill()) / 2, 4)])

pads, groups = [], {}
fps = {f.GetReference(): f for f in b.GetFootprints()}


def bbox(p):
    bb = p.GetBoundingBox()
    return mm(bb.GetLeft()) - OX, mm(bb.GetRight()) - OX, mm(bb.GetTop()) - OY, mm(bb.GetBottom()) - OY


def add_pad(net, name, box, tname, side="top"):
    x0, x1, y0, y1 = box
    pads.append([net, name, round(x0, 4), round(x1, 4), round(y0, 4), round(y1, 4), side])
    groups.setdefault(tname, [net, [], side])[1].append([(x0 + x1) / 2, (y0 + y1) / 2])


# cells from the gate nets: GH_L1 -> 1, GH_R1 -> 2, GH_L2 -> 3, GH_R2 -> 4
CELL = {"L1": 1, "R1": 2, "L2": 3, "R2": 4}
cell_x = {}
for ref, f in fps.items():
    if not ref.startswith("Q"):
        continue
    g = [p.GetNetname() for p in f.Pads() if p.GetNumber() == "1"][0]
    c = CELL[g[3:]]
    hs = g.startswith("GH")
    cell_x[c] = mm(f.GetPosition().x) - OX
    for p in f.Pads():
        n = p.GetNumber()
        if n in ("1", "2"):
            continue
        net = NETS[p.GetNetname()]
        drain = n in ("3", "5", "7")
        tname = ("QH_" if hs else "QL_") + ("D_" if drain else "S_") + str(c)
        add_pad(net, "%s_%s" % (ref, n), bbox(p), tname)
for ref, f in fps.items():
    if ref.startswith("C") and ref[1:].isdigit():
        nets = set(p.GetNetname() for p in f.Pads())
        if nets != {"DCP", "DCN"}:
            continue
        x = mm(f.GetPosition().x) - OX
        local = f.GetValue().startswith("1uF")
        c = min(cell_x, key=lambda k: abs(cell_x[k] - x))
        g = str(c) if (local or abs(x) > 6.0) else "C"
        for p in f.Pads():
            net = NETS[p.GetNetname()]
            pol = "P" if net == "DCP" else "N"
            tname = ("Cap%s_%s" if local else "Bank%s_%s") % (pol, g)
            add_pad(net, "%s_%s" % (ref, p.GetNumber()), bbox(p), tname)
    elif ref.startswith("RS"):
        c = int(ref[2:])
        for p in f.Pads():
            net = NETS[p.GetNetname()]
            add_pad(net, "%s_%s" % (ref, p.GetNumber()), bbox(p), ("RSI_%d" if net.startswith("LSRC") else "RSN_%d") % c)
    elif ref.startswith("J") and f.GetValue() in ("DC+", "DC-", "AC"):
        # DC: REDCUBE body = solid 7 x 7 mm block on the bottom shorting the four press-in pins (pins as vias);
        # AC: M6 bolt pad, contact face 12 x 12 mm (bar + washer) on the bottom, hole barrel and via rings as vias
        x, y = mm(f.GetPosition().x) - OX, mm(f.GetPosition().y) - OY
        net = NETS[[p for p in f.Pads() if p.GetNumber()][0].GetNetname()]
        for p in f.Pads():
            if p.GetNumber():
                vias.append([net, round(mm(p.GetPosition().x) - OX, 4), round(mm(p.GetPosition().y) - OY, 4),
                             round(mm(p.GetDrillSize().x) / 2, 4)])
        h = 6.0 if f.GetValue() == "AC" else 3.5
        tname = {"DC+": "J_DCP", "DC-": "J_DCN", "AC": "J_AC"}[f.GetValue()]
        add_pad(net, tname, (x - h, x + h, y - h, y + h), tname, "bottom")
SINK = {"DCP": "J_DCP", "DCN": "J_DCN", "AC": "J_AC"}
for c in range(1, 5):
    SINK["LSRC%d" % c] = "RSI_%d" % c
terms = []
for tname, (net, pts, side) in sorted(groups.items()):
    terms.append(["Sink" if SINK.get(net) == tname else "Source", tname, net, pts, side])
assert all(any(t[0] == "Sink" and t[2] == n for t in terms) for n in set(NETS.values()))
out = dict(polys=polys, vias=vias, pads=pads, terminals=terms,
           note="routed board %s, simplification %.2f mm" % (os.path.basename(BRD), TOL))
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "revb_geometry.json"), "w"))
npts = sum(len(p[2]) + sum(len(h) for h in p[3]) for p in polys)
print("polys %d (holes %d, points %d), vias %d, pads %d, terminals %d" % (
    len(polys), sum(len(p[3]) for p in polys), npts, len(vias), len(pads), len(terms)))
for t in terms:
    print(t[0], t[1], t[2], len(t[3]), t[4])

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
BRD = os.environ.get("REVB_BOARD") or os.path.join(ROOT, "hardware", "spb-bb-revb-dpt", "spb-bb-revb-dpt.kicad_pcb")
TAGS = os.environ.get("REVB_LOOP_TAG", "")             # variant tag of the loop model (file names)
OX, OY = 150.0, 100.0
NETS = {"DCP": "DCP", "DCN": "DCN", "SW": "AC", "LSRC1": "LSRC1", "LSRC2": "LSRC2", "LSRC3": "LSRC3", "LSRC4": "LSRC4"}
REGION = os.environ.get("REVB_REGION", "")
# GATE model (REVB_REGION=gate): driver block 1 (cells 1 + 2, driver U1; x = -46 .. -1.5, y = -4.6 .. 22) with the
# power nets as in the loop model plus both gate networks (gate, star, OUT / OFF, Kelvin, VDD / VEE). Terminals at the
# pads of the parts in the gate loops: FET gate / Kelvin pads, R_G, R_ON, R_OFF, D_OFF, driver outputs / supplies and
# the 1 uF output-side bypass capacitors -> gate-loop inductance and its coupling to the power loop (gate_post.py).
GATE = REGION == "gate"
GATE_NETS = ("GH_L1", "GH_R1", "GH_STAR1", "OUTA1", "OFFA1", "KH1", "VDDA1", "VEEA1",
             "GL_L1", "GL_R1", "GL_STAR1", "OUTB1", "OFFB1", "KL1", "VDDB1", "VEEB1")
GATE_PARTS = ("R1", "R2", "R3", "R4", "R7", "R8", "R9", "R10", "D1", "D2", "U1", "C13", "C14", "C15", "C16")
if GATE:
    NETS.update({n: n for n in GATE_NETS})
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


def ring(chain, tol=TOL):
    pts = [(round(mm(chain.CPoint(i).x) - OX, 4), round(mm(chain.CPoint(i).y) - OY, 4)) for i in range(chain.PointCount())]
    return [list(p) for p in dp(pts, tol)]


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
        if GATE and t.GetNetname() in GATE_NETS:
            # a trace a few degrees off the axis meets the axis-aligned pad boxes at a shallow angle; the union leaves
            # sliver faces that crashed the Q3D DC solve (exit 9999) -> snap to the axis (<= 0.06 mm shift per end, inside the pads)
            if abs(y1 - y0) <= pcbnew.FromMM(0.12) and abs(x1 - x0) > 10 * abs(y1 - y0):
                y0 = y1 = (y0 + y1) // 2
            elif abs(x1 - x0) <= pcbnew.FromMM(0.12) and abs(y1 - y0) > 10 * abs(x1 - x0):
                x0 = x1 = (x0 + x1) // 2
        L = math.hypot(x1 - x0, y1 - y0) or 1.0
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        h = t.GetWidth() / 2
        ps.NewOutline()
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            ex = (x1 if sx > 0 else x0) + sx * h * ux
            ey = (y1 if sx > 0 else y0) + sx * h * uy
            ps.Append(int(ex - sy * h * uy), int(ey + sy * h * ux))
# LOOP model (REVB_REGION=loop): only the cell band from the bypass row to the shunts (y = -4.6 .. 20.6), the bank and
# the terminals are left out; the switch node is split per cell (AC1..AC4: the cells meet only at the AC bus).
# LX model (REVB_REGION=lx): cell band + AC columns + AC bus (y = -4.6 .. 61.2, whole bus since D_BUS = 5.2), no bank, no terminals, AC joined:
# inductance between the switch nodes of the two driver pairs (driver skew).
REGION = os.environ.get("REVB_REGION", "")
LOOP = REGION in ("loop", "gate")                  # gate model: cell band handled as in the loop model
# BANK model (REVB_REGION=bank): DC terminals, terminal row, bank and both bypass rows (y = -25 .. 4.3), no cells:
# DC-link port of the leg (terminals -> bank -> bypass) for the three-phase network and the hand-over L_b.
CROP = REGION in ("loop", "lx", "bank", "gate")
BANK = REGION == "bank"
REG = {"loop": (-46.0, -4.6, 46.0, 20.6), "gate": (-46.0, -4.6, -1.5, 22.0), "lx": (-46.0, -4.6, 46.0, 61.2), "bank": (-46.0, -25.0, 46.0, 4.3)}.get(
    REGION, (-46.0, -25.0, 46.0, 61.2))                # loop: below 20.6 (AC columns from 20.8)
CELLX = (-33.25, -14.25, 14.25, 33.25)


def in_reg(x, y):
    return REG[0] <= x <= REG[2] and REG[1] <= y <= REG[3]


def cell_of(x):
    return 1 + min(range(4), key=lambda k: abs(x - CELLX[k]))


if CROP:
    rp = pcbnew.SHAPE_POLY_SET()
    rp.NewOutline()
    for x, y in ((REG[0], REG[1]), (REG[2], REG[1]), (REG[2], REG[3]), (REG[0], REG[3])):
        rp.Append(pcbnew.FromMM(x + OX), pcbnew.FromMM(y + OY))
polys = []
for (n, lay), ps in sorted(acc.items(), key=lambda kv: (kv[0][0], kv[0][1])):
    ps.Simplify(pcbnew.SHAPE_POLY_SET.PM_FAST)
    if CROP:
        ps.BooleanIntersection(rp, pcbnew.SHAPE_POLY_SET.PM_FAST)
    for i in range(ps.OutlineCount()):
        tol = 0.002 if GATE and n in GATE_NETS else TOL   # gate nets: keep the steps, no tilted edges
        outl = ring(ps.Outline(i), tol)
        if len(outl) < 3 or area(outl) < (0.005 if GATE and n in GATE_NETS else MIN_AREA):   # gate traces are thin
            continue
        holes = [ring(ps.Hole(i, h), tol) for h in range(ps.HoleCount(i))]
        holes = [hh for hh in holes if len(hh) >= 3 and area(hh) > 0.05]
        nn = NETS[n]
        if BANK and nn not in ("DCP", "DCN"):
            continue
        if LOOP and nn == "AC":
            nn = "AC%d" % cell_of(sum(p[0] for p in outl) / len(outl))
        polys.append([nn, LAYERS[lay], outl, holes])
vias = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA" and t.GetNetname() in NETS:
        vx, vy = round(mm(t.GetPosition().x) - OX, 4), round(mm(t.GetPosition().y) - OY, 4)
        if CROP and not in_reg(vx, vy):
            continue
        nn = NETS[t.GetNetname()]
        if LOOP and nn == "AC":
            nn = "AC%d" % cell_of(vx)
        lt, lb = LAYERS.get(t.TopLayer(), "L1"), LAYERS.get(t.BottomLayer(), "L4")
        vias.append([nn, vx, vy, round(mm(t.GetDrill()) / 2, 4), lt, lb])     # layer span (blind vias)

pads, groups = [], {}
fps = {f.GetReference(): f for f in b.GetFootprints()}


def bbox(p):
    bb = p.GetBoundingBox()
    return mm(bb.GetLeft()) - OX, mm(bb.GetRight()) - OX, mm(bb.GetTop()) - OY, mm(bb.GetBottom()) - OY


def add_pad(net, name, box, tname, side="top"):
    x0, x1, y0, y1 = box
    if GATE and not in_reg((x0 + x1) / 2, (y0 + y1) / 2):
        return                                     # gate model: block 1 only
    pads.append([net, name, round(x0, 4), round(x1, 4), round(y0, 4), round(y1, 4), side])
    groups.setdefault(tname, [net, [], side])[1].append([(x0 + x1) / 2, (y0 + y1) / 2])


# cells from the gate nets: GH_L1 -> 1, GH_R1 -> 2, GH_L2 -> 3, GH_R2 -> 4
CELL = {"L1": 1, "R1": 2, "L2": 3, "R2": 4}
cell_x = {}
for ref, f in fps.items():
    if not ref.startswith("Q"):
        continue
    if BANK:                                       # bank model: cells not modelled, only their x for the groups
        cell_x[CELL[[p.GetNetname() for p in f.Pads() if p.GetNumber() == "1"][0][3:]]] = mm(f.GetPosition().x) - OX
        continue
    g = [p.GetNetname() for p in f.Pads() if p.GetNumber() == "1"][0]
    c = CELL[g[3:]]
    hs = g.startswith("GH")
    cell_x[c] = mm(f.GetPosition().x) - OX
    for p in f.Pads():
        n = p.GetNumber()
        if n in ("1", "2"):
            if GATE:                               # gate (1) and Kelvin source (2) pads as terminals G_Qk / K_Qk
                add_pad(p.GetNetname(), "%s_%s" % (ref, n), bbox(p), ("G_" if n == "1" else "K_") + ref)
            continue
        net = NETS[p.GetNetname()]
        if LOOP and net == "AC":
            net = "AC%d" % c
        drain = n in ("3", "5", "7")
        tname = ("QH_" if hs else "QL_") + ("D_" if drain else "S_") + str(c)
        add_pad(net, "%s_%s" % (ref, n), bbox(p), tname)
for ref, f in fps.items():
    if ref.startswith("C") and ref[1:].isdigit() and not (GATE and ref in GATE_PARTS):
        nets = set(p.GetNetname() for p in f.Pads())
        if nets != {"DCP", "DCN"}:
            continue
        x = mm(f.GetPosition().x) - OX
        local = f.GetValue().startswith("1uF")
        if CROP and not local and not BANK:
            continue                               # loop / lx model: bypass only
        c = min(cell_x, key=lambda k: abs(cell_x[k] - x))
        g = str(c) if (local or abs(x) > 6.0) else "C"
        for p in f.Pads():
            net = NETS[p.GetNetname()]
            pol = "P" if net == "DCP" else "N"
            bot = f.IsFlipped()                    # second bypass row on the bottom side: own terminal group
            tname = ("Cap%s%s_%s" % (pol, "b" if bot else "", g)) if local else ("Bank%s_%s" % (pol, g))
            add_pad(net, "%s_%s" % (ref, p.GetNumber()), bbox(p), tname, "bottom" if bot else "top")
    elif GATE and ref in GATE_PARTS:
        for p in f.Pads():
            if p.GetNetname() in GATE_NETS:
                add_pad(p.GetNetname(), "%s_%s" % (ref, p.GetNumber()), bbox(p), "%s_%s" % (ref, p.GetNumber()),
                        "bottom" if f.IsFlipped() else "top")
    elif ref.startswith("RS") and not BANK:
        c = int(ref[2:])
        for p in f.Pads():
            net = NETS[p.GetNetname()]
            add_pad(net, "%s_%s" % (ref, p.GetNumber()), bbox(p), ("RSI_%d" if net.startswith("LSRC") else "RSN_%d") % c)
    elif ref.startswith("J") and f.GetValue() in ("DC+", "DC-", "AC") and (not CROP or (BANK and f.GetValue() != "AC")):
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
if LOOP:                                           # sinks inside the cell band
    SC = os.environ.get("REVB_LOOP_SINKCELL", "1")      # cell that holds the DC sinks (model check)
    SINK = {"DCP": "CapP_" + SC, "DCN": "CapN_" + SC}
    SINK.update({"AC%d" % c: "QH_S_%d" % c for c in range(1, 5)})
elif REGION == "lx":
    SINK = {"DCP": "CapP_1", "DCN": "CapN_1", "AC": "QH_S_1"}
for c in range(1, 5):
    SINK["LSRC%d" % c] = "RSI_%d" % c
if GATE:                                           # gate nets: sink at the driver-side pad
    SINK.update({"GH_L1": "R1_1", "GH_R1": "R2_2", "GH_STAR1": "R7_2", "OUTA1": "U1_12", "OFFA1": "D1_2",
                 "KH1": "C13_1", "VDDA1": "U1_13", "VEEA1": "U1_11",
                 "GL_L1": "R3_1", "GL_R1": "R4_2", "GL_STAR1": "R9_2", "OUTB1": "U1_9", "OFFB1": "D2_2",
                 "KL1": "C16_1", "VDDB1": "U1_10", "VEEB1": "U1_8"})
terms = []
for tname, (net, pts, side) in sorted(groups.items()):
    terms.append(["Sink" if SINK.get(net) == tname else "Source", tname, net, pts, side])
_nosink = sorted(n for n in set(t_[2] for t_ in terms) if not any(t[0] == "Sink" and t[2] == n for t in terms))
assert not _nosink, "nets without a sink terminal: %s; terminals %s" % (_nosink, sorted(t[1] for t in terms if t[2] in _nosink))
if os.environ.get("REVB_MIRROR"):                  # model check: mirror the whole geometry x -> -x
    polys = [[n, l, [[-p[0], p[1]] for p in o][::-1], [[[-p[0], p[1]] for p in h][::-1] for h in hs]]
             for n, l, o, hs in polys]
    vias = [[v[0], -v[1]] + v[2:] for v in vias]
    pads = [[n, nm, -x1, -x0, y0, y1, sd] for n, nm, x0, x1, y0, y1, sd in pads]
    terms = [[k, nm, n, [[-p[0], p[1]] for p in pts], sd] for k, nm, n, pts, sd in terms]
out = dict(polys=polys, vias=vias, pads=pads, terminals=terms,
           note="routed board %s, simplification %.2f mm" % (os.path.basename(BRD), TOL))
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
GEO = {"loop": "revb_loop_geometry", "gate": "revb_gate_geometry", "lx": "revb_lx_geometry", "bank": "revb_bank_geometry"}.get(REGION, "revb_geometry") + ("_" + TAGS if TAGS else "")
json.dump(out, open(os.path.join(HERE, "results", GEO + ".json"), "w"))
npts = sum(len(p[2]) + sum(len(h) for h in p[3]) for p in polys)
print("polys %d (holes %d, points %d), vias %d, pads %d, terminals %d" % (
    len(polys), sum(len(p[3]) for p in polys), npts, len(vias), len(pads), len(terms)))
for t in terms:
    print(t[0], t[1], t[2], len(t[3]), t[4])

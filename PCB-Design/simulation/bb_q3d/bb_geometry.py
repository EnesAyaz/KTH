# -*- coding: utf-8 -*-
"""
Geometry of the symmetric building block: one phase leg, 2 x EPC2361 per switch,
gate driver in the middle. Python 2 (AEDT IronPython) and Python 3 compatible.

Coordinates in mm: x across the board (0 = symmetry line), y along the loop (down),
z up. Layers: L1 top copper (+ pads), L2 DC- plane, L3 DC+ plane, L4 AC plane (+ bottom pads).
Stack-up thicknesses are AEDT design variables in the Q3D script (h_diel, h_23, h_34, t_*).

build() returns a dict:
  boxes:     (net, name, layer, x0, x1, y0, y1)        layer in L1, L2, L3, L4, PAD, PADB
  vias:      (net, x, y, to_layer)                       L1 -> L2 / L3 / L4
  holes:     (plane_name, x, y)                          anti-pads in L2 / L3
  terminals: (kind, name, net, [(x, y), ...], side)      side 'top' or 'bottom'
"""

P = dict(
    xc=7.5,          # cell centre |x|; corridor for the driver is |x| < xc - w_cell/2
    w_cell=9.0,      # cell island width
    x_edge=15.0,     # board half width
    fet_w=5.0, fet_pad=1.0,
    cap_p=1.4, cap_w=1.25,          # 6 x 0805 local caps per cell
    bank_x=(4.75, 7.75, 10.75, 13.75), bank_w=2.0,   # 8 x 1210 per row (both sides of the centre)
    gap=0.6,
    via_pitch_cell=0.9, via_pitch_strip=1.2,
)

# cell rows (y), PL_A geometry
Y = dict(
    n2=(-2.4, 0.9),        # DC- strip / MLCC landing (shared by both cells and bank row 3)
    capn=(0.2, 0.7), capp=(1.7, 2.2),
    dcp=(1.5, 4.6), qhd=(3.4, 4.4), dcp_via=2.8,
    ac=(5.2, 8.9), qhs=(5.4, 6.4), qld=(7.7, 8.7), ac_via=7.05,
    src=(9.5, 11.5), qls=(9.7, 10.7), src_via=11.1,
    n2_via=-0.5,
    # bank strips above the cells (alternating polarity)
    p1=(-13.4, -11.0), n1=(-10.4, -7.0), p2=(-6.4, -3.0),
    p1_via=-12.9, n1_via=-8.7, p2_via=-4.7,
    # planes
    l2=(-10.4, 11.9), l3=(-13.4, 4.6), l4=(4.6, 15.0),
    # terminals
    t_dcp=(-13.4, -12.6), t_dcn=(-9.6, -7.8), t_ac=(13.6, 14.8),
)


def _row_pads(g0):
    """Bank row in the gap that starts at y = g0 (strip above ends at g0): upper and lower pad y."""
    gc = g0 + P["gap"] / 2
    return (gc - 1.7, gc - 0.9), (gc + 0.9, gc + 1.7)


def build(p=None):
    p = dict(P, **(p or {}))
    boxes, vias, holes, terms = [], [], [], []
    xe = p["x_edge"]

    def box(net, name, layer, x0, x1, y0, y1):
        boxes.append((net, name, layer, x0, x1, y0, y1))

    def via_row(net, y, x0, x1, pitch, to_layer, hole_planes=()):
        n = int(round((x1 - x0) / pitch))
        for i in range(n + 1):
            x = x0 + i * (x1 - x0) / float(n)
            vias.append((net, x, y, to_layer))
            for pl in hole_planes:
                holes.append((pl, x, y))

    # ---------------- bank strips + rows (top area) ----------------
    box("DCP", "P1", "L1", -xe, xe, Y["p1"][0], Y["p1"][1])
    box("DCN", "N1", "L1", -xe, xe, Y["n1"][0], Y["n1"][1])
    box("DCP", "P2", "L1", -xe, xe, Y["p2"][0], Y["p2"][1])
    box("DCN", "N2", "L1", -xe, xe, Y["n2"][0], Y["n2"][1])
    via_row("DCP", Y["p1_via"], -xe + 0.6, xe - 0.6, p["via_pitch_strip"], "L3")
    via_row("DCN", Y["n1_via"], -xe + 0.6, xe - 0.6, p["via_pitch_strip"], "L2")
    via_row("DCP", Y["p2_via"], -xe + 0.6, xe - 0.6, p["via_pitch_strip"], "L3", ("L2",))
    rows = [(Y["p1"][1], "DCP", "DCN"), (Y["n1"][1], "DCN", "DCP"), (Y["p2"][1], "DCP", "DCN")]
    for r, (g0, up_net, lo_net) in enumerate(rows, 1):
        (u0, u1), (l0, l1) = _row_pads(g0)
        up_pts, lo_pts = [], []
        k = 0
        for s in (-1, 1):
            for xb in p["bank_x"]:
                x = s * xb
                hw = p["bank_w"] / 2
                k += 1
                box(up_net, "B%d%s_u%d" % (r, "PN"[up_net == "DCN"], k), "PAD", x - hw, x + hw, u0, u1)
                box(lo_net, "B%d%s_l%d" % (r, "PN"[lo_net == "DCN"], k), "PAD", x - hw, x + hw, l0, l1)
                up_pts.append((x, (u0 + u1) / 2))
                lo_pts.append((x, (l0 + l1) / 2))
        pos, neg = (up_pts, lo_pts) if up_net == "DCP" else (lo_pts, up_pts)
        terms.append(("Source", "CapB%dP" % r, "DCP", pos, "top"))
        terms.append(("Source", "CapB%dN" % r, "DCN", neg, "top"))

    # ---------------- two mirrored cells ----------------
    via_row("DCN", Y["n2_via"], -xe + 0.6, xe - 0.6, p["via_pitch_strip"], "L2")
    for side, s in (("L", -1), ("R", 1)):
        xc = s * p["xc"]
        hw = p["w_cell"] / 2
        x0, x1 = xc - hw, xc + hw
        cp, cn = [], []
        for i in range(6):
            x = xc + (i - 2.5) * p["cap_p"]
            box("DCN", "CapN%s%d" % (side, i), "PAD", x - p["cap_w"] / 2, x + p["cap_w"] / 2, Y["capn"][0], Y["capn"][1])
            box("DCP", "CapP%s%d" % (side, i), "PAD", x - p["cap_w"] / 2, x + p["cap_w"] / 2, Y["capp"][0], Y["capp"][1])
            cn.append((x, sum(Y["capn"]) / 2))
            cp.append((x, sum(Y["capp"]) / 2))
        box("DCP", "DCP_%s" % side, "L1", x0, x1, Y["dcp"][0], Y["dcp"][1])
        box("AC", "AC_%s" % side, "L1", x0, x1, Y["ac"][0], Y["ac"][1])
        box("DCN", "SRC_%s" % side, "L1", x0, x1, Y["src"][0], Y["src"][1])
        fx0, fx1 = xc - p["fet_w"] / 2, xc + p["fet_w"] / 2
        for name, net, (y0, y1) in (("QH_D", "DCP", Y["qhd"]), ("QH_S", "AC", Y["qhs"]),
                                    ("QL_D", "AC", Y["qld"]), ("QL_S", "DCN", Y["qls"])):
            box(net, "%s_%s" % (name, side), "PAD", fx0, fx1, y0, y1)
        via_row("DCP", Y["dcp_via"], x0 + 0.45, x1 - 0.45, p["via_pitch_cell"], "L3", ("L2",))
        via_row("AC", Y["ac_via"], x0 + 0.45, x1 - 0.45, p["via_pitch_cell"], "L4", ("L2",))
        via_row("DCN", Y["src_via"], x0 + 0.45, x1 - 0.45, p["via_pitch_cell"], "L2")
        terms.append(("Source", "CapP%s" % side, "DCP", cp, "top"))
        terms.append(("Source", "CapN%s" % side, "DCN", cn, "top"))
        terms.append(("Source", "QH_D_%s" % side, "DCP", [(xc, sum(Y["qhd"]) / 2)], "top"))
        terms.append(("Source", "QH_S_%s" % side, "AC", [(xc, sum(Y["qhs"]) / 2)], "top"))
        terms.append(("Source", "QL_D_%s" % side, "AC", [(xc, sum(Y["qld"]) / 2)], "top"))
        terms.append(("Source", "QL_S_%s" % side, "DCN", [(xc, sum(Y["qls"]) / 2)], "top"))

    # ---------------- planes and terminals ----------------
    box("DCN", "L2_DCN", "L2", -xe, xe, Y["l2"][0], Y["l2"][1])
    box("DCP", "L3_DCP", "L3", -xe, xe, Y["l3"][0], Y["l3"][1])
    ac_w = p["xc"] + p["w_cell"] / 2
    box("AC", "L4_AC", "L4", -ac_w, ac_w, Y["l4"][0], Y["l4"][1])
    box("DCP", "T_DCP", "PAD", -3.0, 3.0, Y["t_dcp"][0], Y["t_dcp"][1])
    box("DCN", "T_DCN", "PAD", -3.0, 3.0, Y["t_dcn"][0], Y["t_dcn"][1])
    box("AC", "T_AC", "PADB", -4.0, 4.0, Y["t_ac"][0], Y["t_ac"][1])
    terms.append(("Sink", "T_DCP", "DCP", [(0.0, sum(Y["t_dcp"]) / 2)], "top"))
    terms.append(("Sink", "T_DCN", "DCN", [(0.0, sum(Y["t_dcn"]) / 2)], "top"))
    terms.append(("Sink", "T_AC", "AC", [(0.0, sum(Y["t_ac"]) / 2)], "bottom"))
    return dict(boxes=boxes, vias=vias, holes=holes, terminals=terms, params=p, rows=Y)


# low-side gate loop: star from the centre driver (trunk on x = 0, branches to both QL gates)
GATE = dict(
    y_drv=8.0,        # driver LO pin
    y_gate=10.2,      # QL gate pad row (next to the QL source pad)
    x_gate=5.0,       # |x| of the QL gate pads (inner end of each QL)
    w_g=0.25, w_ret=0.6, s_gk=0.5,
)

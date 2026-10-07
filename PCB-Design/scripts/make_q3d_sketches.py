"""
Draw 2D sketches of the Q3D DPT-cell model (top views L1/L2, side view, scenarios)
from the same default variables as simulation/q3d/q3d_dpt_cell.py.

    python scripts/make_q3d_sketches.py   -> docs/q3d-geometry-sketches.html
"""
import os

V = dict(h_diel=0.1, t_L1=0.07, t_L2=0.035, t_pad=0.035, gap=0.6, w_cell=9.0, w_sh=17.0,
         l_vrow=0.8, l_capn=0.9, l_dcp=3.1, l_ac=3.7, l_s=2.4, g_sh=0.8, l_dcn=1.4,
         fet_w=5.0, fet_pad=1.0, cap_p=1.4, cap_w=1.25, sh_p=3.4, sh_w=2.8, via_r=0.15)
V["y_dcp0"] = V["l_capn"] + V["gap"]
V["y_dcp1"] = V["y_dcp0"] + V["l_dcp"]
V["y_ac0"] = V["y_dcp1"] + V["gap"]
V["y_ac1"] = V["y_ac0"] + V["l_ac"]
V["y_s0"] = V["y_ac1"] + V["gap"]
V["y_s1"] = V["y_s0"] + V["l_s"]
V["y_dn0"] = V["y_s1"] + V["g_sh"]
V["y_dn1"] = V["y_dn0"] + V["l_dcn"]

COL = {"DCP": "#e4572e", "AC": "#f3a712", "SQL": "#9b5de5", "DCN": "#2e86de",
       "pad": "#333", "comp": "#555", "param": "#c0392b", "dim": "#666"}


class Svg(object):
    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def add(self, s):
        self.items.append(s)

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1, dash=None, op=1.0, rx=0):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%g" fill="%s" '
                 'fill-opacity="%.2f" stroke="%s" stroke-width="%g"%s/>'
                 % (x, y, w, h, rx, fill, op, stroke, sw, d))

    def line(self, x1, y1, x2, y2, stroke="#666", sw=1, dash=None, arrow=False):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ' marker-end="url(#arr)"' if arrow else ""
        self.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%g"%s%s/>'
                 % (x1, y1, x2, y2, stroke, sw, d, m))

    def circle(self, x, y, r, fill="#222"):
        self.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (x, y, r, fill))

    def text(self, x, y, s, size=11, fill="#222", anchor="start", weight="normal", rot=None):
        t = ' transform="rotate(%g %.1f %.1f)"' % (rot, x, y) if rot else ""
        self.add('<text x="%.1f" y="%.1f" font-size="%g" fill="%s" text-anchor="%s" '
                 'font-weight="%s"%s>%s</text>' % (x, y, size, fill, anchor, weight, t, s))

    def path(self, d, stroke, sw=2, dash=None, arrow=True):
        da = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ' marker-end="url(#arr_%s)"' % stroke[1:] if arrow else ""
        self.add('<path d="%s" fill="none" stroke="%s" stroke-width="%g"%s%s/>'
                 % (d, stroke, sw, da, m))

    def render(self):
        markers = "".join(
            '<marker id="arr_%s" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
            '<path d="M0,0 L8,4 L0,8 z" fill="%s"/></marker>' % (c[1:], c)
            for c in ("#e4572e", "#2e86de", "#2a9d8f", "#9b5de5"))
        markers += ('<marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
                    '<path d="M0,0 L8,4 L0,8 z" fill="#666"/></marker>')
        return ('<svg viewBox="0 0 %d %d" width="100%%" style="max-width:%dpx" '
                'xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, Arial, sans-serif">'
                '<defs>%s</defs>%s</svg>' % (self.w, self.h, self.w, markers, "".join(self.items)))


def vdim(s, x, y0, y1, label, side=1):
    """Vertical dimension at pixel x between pixel y0..y1."""
    s.line(x, y0, x, y1, COL["dim"], 1)
    s.line(x - 4, y0, x + 4, y0, COL["dim"], 1)
    s.line(x - 4, y1, x + 4, y1, COL["dim"], 1)
    s.text(x + 7 * side, (y0 + y1) / 2 + 4, label, 11, COL["param"],
           "start" if side > 0 else "end", "bold")


def hdim(s, x0, x1, y, label):
    s.line(x0, y, x1, y, COL["dim"], 1)
    s.line(x0, y - 4, x0, y + 4, COL["dim"], 1)
    s.line(x1, y - 4, x1, y + 4, COL["dim"], 1)
    s.text((x0 + x1) / 2, y - 5, label, 11, COL["param"], "middle", "bold")


# ---------------------------------------------------------------- top view L1 + L2
def top_views():
    S = 26.0
    W, H = 1180, 560
    s = Svg(W, H)

    def X(ox, x):
        return ox + x * S

    def Y(y):
        return 50 + (y + 1.0) * S

    # ---- L1 (left panel)
    ox = 300
    s.text(ox, 22, "Top view, L1 (F.Cu) + pads: scenario A (MLCC bank at QH)", 14, "#111", "middle", "bold")
    isl = [("DCN", "DCN_cap", -V["w_cell"] / 2, V["w_cell"] / 2, -V["l_vrow"], V["l_capn"]),
           ("DCP", "DCP", -V["w_cell"] / 2, V["w_cell"] / 2, V["y_dcp0"], V["y_dcp1"]),
           ("AC", "AC", -V["w_cell"] / 2, V["w_cell"] / 2, V["y_ac0"], V["y_ac1"]),
           ("SQL", "SQL", -V["w_sh"] / 2, V["w_sh"] / 2, V["y_s0"], V["y_s1"]),
           ("DCN", "DCN_sh", -V["w_sh"] / 2, V["w_sh"] / 2, V["y_dn0"], V["y_dn1"])]
    for net, name, x0, x1, y0, y1 in isl:
        s.rect(X(ox, x0), Y(y0), (x1 - x0) * S, (y1 - y0) * S, COL[net], "none", op=0.30)
        s.text(X(ox, x0) - 6, (Y(y0) + Y(y1)) / 2 + 4, name, 10, COL[net], "end", "bold")
    # MLCCs
    for i in range(6):
        xc = (i - 2.5) * V["cap_p"]
        cw = V["cap_w"]
        s.rect(X(ox, xc - cw / 2), Y(0.2), cw * S, 2.0 * S, "none", COL["comp"], 1, "3,2")
        s.rect(X(ox, xc - cw / 2), Y(0.2), cw * S, 0.5 * S, COL["pad"], op=0.85)
        s.rect(X(ox, xc - cw / 2), Y(1.7), cw * S, 0.5 * S, COL["pad"], op=0.85)
    s.text(X(ox, 4.2), Y(1.2), "6 &#215; MLCC", 10, COL["comp"])
    # FETs
    for name, y0 in (("QH", V["y_dcp1"] - 0.2 - V["fet_pad"]), ("QL", V["y_ac1"] - 0.2 - V["fet_pad"])):
        fw = V["fet_w"]
        s.rect(X(ox, -fw / 2), Y(y0), fw * S, 3.0 * S, "none", "#111", 1.5, "5,3")
        s.rect(X(ox, -fw / 2), Y(y0), fw * S, V["fet_pad"] * S, COL["pad"], op=0.85)
        s.rect(X(ox, -fw / 2), Y(y0 + 2.0), fw * S, V["fet_pad"] * S, COL["pad"], op=0.85)
        s.text(X(ox, fw / 2) + 6, Y(y0 + 1.6), name + " (EPC2361)", 11, "#111", weight="bold")
        s.text(X(ox, -fw / 2) - 4, Y(y0 + 0.65), name + "_D", 9, "#111", "end")
        s.text(X(ox, -fw / 2) - 4, Y(y0 + 2.65), name + "_S", 9, "#111", "end")
    # shunts
    for i in range(5):
        xc = (i - 2) * V["sh_p"]
        sw = V["sh_w"]
        s.rect(X(ox, xc - sw / 2), Y(V["y_s1"] - 0.5), sw * S, (V["g_sh"] + 1.0) * S, "none", COL["comp"], 1, "3,2")
        s.rect(X(ox, xc - sw / 2), Y(V["y_s1"] - 0.5), sw * S, 0.4 * S, COL["pad"], op=0.85)
        s.rect(X(ox, xc - sw / 2), Y(V["y_dn0"] + 0.1), sw * S, 0.4 * S, COL["pad"], op=0.85)
    s.text(X(ox, -8.5), Y(V["y_dn1"]) + 16, "5 &#215; PRL1632 5 m&#937; = 1 m&#937; shunt", 10, COL["comp"])
    # vias
    for i in range(9):
        s.circle(X(ox, (i - 4) * V["w_cell"] / 10), Y(-V["l_vrow"] / 2), V["via_r"] * S + 1)
    for i in range(17):
        s.circle(X(ox, (i - 8) * V["w_sh"] / 18), Y(V["y_dn0"] + 0.9), V["via_r"] * S + 1)
    # loop arrow on L1
    s.path("M %.1f %.1f L %.1f %.1f" % (X(ox, 5.0), Y(1.2), X(ox, 5.0), Y(V["y_dn0"] + 0.6)), "#e4572e", 2.5)
    s.text(X(ox, 5.2), Y(V["y_ac0"] + 1.6), "loop current on L1", 10, "#e4572e")
    # dimensions (right of L1 panel)
    dx = X(ox, 8.5) + 18
    edges = [(-V["l_vrow"], 0.0, "l_vrow"), (0.0, V["l_capn"], "l_capn"),
             (V["l_capn"], V["y_dcp0"], "gap"), (V["y_dcp0"], V["y_dcp1"], "l_dcp"),
             (V["y_dcp1"], V["y_ac0"], "gap"), (V["y_ac0"], V["y_ac1"], "l_ac"),
             (V["y_ac1"], V["y_s0"], "gap"), (V["y_s0"], V["y_s1"], "l_s"),
             (V["y_s1"], V["y_dn0"], "g_sh"), (V["y_dn0"], V["y_dn1"], "l_dcn")]
    for i, (a, b, lab) in enumerate(edges):
        vdim(s, dx + (0 if i % 2 == 0 else 46), Y(a), Y(b), "%s %.1f" % (lab, b - a))
    hdim(s, X(ox, -V["w_cell"] / 2), X(ox, V["w_cell"] / 2), Y(-V["l_vrow"]) - 8, "w_cell 9.0")
    hdim(s, X(ox, -V["w_sh"] / 2), X(ox, V["w_sh"] / 2), Y(V["y_dn1"]) + 34, "w_sh 17.0")
    hdim(s, X(ox, -2.5), X(ox, 2.5), Y(V["y_ac0"] + 1.9), "fet_w 5.0")
    hdim(s, X(ox, -0.7), X(ox, 0.7), Y(2.2) + 14, "cap_p 1.4")

    # ---- L2 (right panel)
    ox2 = 930
    s.text(ox2, 22, "Top view, L2 (In1.Cu): solid DC− return", 14, "#111", "middle", "bold")
    s.rect(X(ox2, -8.5), Y(-1.0), 17 * S, (V["y_dn1"] + 1.5) * S, COL["DCN"], "none", op=0.30)
    s.text(X(ox2, 0), Y(V["y_dcp0"]), "L2_DCN (net DCN): solid, no cuts under the cell", 11, COL["DCN"], "middle", "bold")
    for i in range(9):
        s.circle(X(ox2, (i - 4) * V["w_cell"] / 10), Y(-V["l_vrow"] / 2), V["via_r"] * S + 1)
    for i in range(17):
        s.circle(X(ox2, (i - 8) * V["w_sh"] / 18), Y(V["y_dn0"] + 0.9), V["via_r"] * S + 1)
    s.text(X(ox2, 0), Y(-0.4) + 18, "9 vias to MLCC − (y = −l_vrow/2)", 10, "#222", "middle")
    s.text(X(ox2, 0), Y(V["y_dn0"] + 0.9) - 10, "17 vias from shunt output (y = y_dn0 + 0.9)", 10, "#222", "middle")
    # footprint ghosts of the L1 parts
    for y0 in (V["y_dcp1"] - 1.2, V["y_ac1"] - 1.2):
        s.rect(X(ox2, -2.5), Y(y0), 5 * S, 3 * S, "none", "#555", 1, "4,3")
    s.text(X(ox2, 2.7), Y(V["y_dcp1"] + 0.4), "QH above", 9, "#555")
    s.text(X(ox2, 2.7), Y(V["y_ac1"] + 0.4), "QL above", 9, "#555")
    s.path("M %.1f %.1f L %.1f %.1f" % (X(ox2, -5.5), Y(V["y_dn0"] + 0.6), X(ox2, -5.5), Y(0.0)),
           "#2e86de", 2.5, "6,4")
    s.text(X(ox2, -5.7), Y(V["y_ac0"]), "return current on L2", 10, "#2e86de", "end")
    s.text(ox2, H - 12, "L2 extends l_vrow/2 + 0.2 before the cap vias and 0.5 mm past y_dn1. "
                         "Width = w_sh (shunt) or w_cell (no shunt).", 10, "#444", "middle")
    s.text(ox, H - 12, "All lengths in mm (defaults). Red labels are Q3D design variables. "
                       "Dashed outlines = components = gaps in copper.", 10, "#444", "middle")
    return s.render()


# ---------------------------------------------------------------- side view
def side_view():
    W, H = 1180, 330
    s = Svg(W, H)
    S = 62.0
    x0 = 150

    def X(y):
        return x0 + (y + 1.0) * S

    zL2b, zL2t = 250, 238      # z exaggerated, not to scale
    zL1b, zL1t = 190, 176
    zpad = 170
    s.text(W / 2, 22, "Side view along the loop (y); thickness exaggerated, lengths to scale", 14, "#111", "middle", "bold")
    # core below
    s.rect(X(-1.0), zL2b, (V["y_dn1"] + 1.5) * S, 40, "#d9c9a3", op=0.5)
    s.text(X(-1.0) + 6, zL2b + 26, "core ~1.2 mm, L3/L4 (not in model)", 10, "#6b5a2e")
    # dielectric
    s.rect(X(-1.0), zL2t, (V["y_dn1"] + 1.5) * S, zL1b - zL2t, "#efe3c2", op=0.7)
    # L2
    s.rect(X(-1.0), zL2t, (V["y_dn1"] + 1.5) * S, zL2b - zL2t, COL["DCN"], op=0.8)
    # L1 islands
    for net, a, b in (("DCN", -V["l_vrow"], V["l_capn"]), ("DCP", V["y_dcp0"], V["y_dcp1"]),
                      ("AC", V["y_ac0"], V["y_ac1"]), ("SQL", V["y_s0"], V["y_s1"]),
                      ("DCN", V["y_dn0"], V["y_dn1"])):
        s.rect(X(a), zL1t, (b - a) * S, zL1b - zL1t, COL[net], op=0.85)
        s.text(X((a + b) / 2), zL1b + 14, net, 10, COL[net], "middle", "bold")
    # vias
    for yv in (-V["l_vrow"] / 2, V["y_dn0"] + 0.9):
        s.rect(X(yv) - 5, zL1t, 10, zL2b - zL1t, "#444", op=0.9)
    # components
    comps = [("MLCC", 0.2, 2.2, 70), ("QH", V["y_dcp1"] - 1.2, V["y_dcp1"] + 1.8, 34),
             ("QL", V["y_ac1"] - 1.2, V["y_ac1"] + 1.8, 34), ("shunt", V["y_s1"] - 0.5, V["y_dn0"] + 0.5, 40)]
    for name, a, b, h in comps:
        s.rect(X(a), zpad - h, (b - a) * S, h, "#ffffff", "#333", 1.2, "4,3")
        s.text(X((a + b) / 2), zpad - h / 2 + 4, name, 11, "#111", "middle", "bold")
        s.rect(X(a), zpad, 0.5 * S if name == "MLCC" else (0.4 if name == "shunt" else 1.0) * S, zL1t - zpad, COL["pad"])
        w = 0.5 if name == "MLCC" else (0.4 if name == "shunt" else 1.0)
        s.rect(X(b) - w * S, zpad, w * S, zL1t - zpad, COL["pad"])
    # loop arrows
    s.path("M %.1f %.1f L %.1f %.1f" % (X(1.0), zpad - 80, X(V["y_dn0"] + 0.9), zpad - 80), "#e4572e", 2.5)
    s.text(X(6.5), zpad - 86, "forward: MLCC + → QH → AC → QL → shunt → vias", 11, "#e4572e", "middle")
    s.path("M %.1f %.1f L %.1f %.1f" % (X(V["y_dn0"] + 0.9), zL2b + 50, X(-0.4), zL2b + 50), "#2e86de", 2.5, "6,4")
    s.text(X(6.5), zL2b + 66, "return: L2 directly underneath, 0.1 mm away (flux cancellation)", 11, "#2e86de", "middle")
    # z dims (left)
    vdim(s, 120, zL1t, zL1b, "t_L1 0.070", -1)
    vdim(s, 120, zL1b, zL2t, "h_diel 0.100", -1)
    vdim(s, 120, zL2t, zL2b, "t_L2 0.035", -1)
    vdim(s, X(V["y_dcp1"] - 1.2) - 10, zpad, zL1t, "t_pad", -1)
    s.text(W - 10, H - 10, "terminals (source/sink faces) are the tops of the dark pads", 10, "#444", "end")
    return s.render()


# ---------------------------------------------------------------- scenarios
def scenario(title, layers, comps, vias, loops, note, h=250):
    """Generic schematic side view. layers: list of (label, net, z_top, z_bot, segments[(a,b)]).
    comps: (label, a, b). vias: (y, z_top, z_bot). loops: (svg path, colour, dashed, label, lx, ly)."""
    W = 1180
    s = Svg(W, h)
    S = 62.0
    x0 = 140

    def X(y):
        return x0 + (y + 1.0) * S

    s.text(W / 2, 20, title, 13, "#111", "middle", "bold")
    for label, net, zt, zb, segs in layers:
        for a, b in segs:
            s.rect(X(a), zt, (b - a) * S, zb - zt, COL.get(net, net), op=0.8)
        s.text(x0 - 8, (zt + zb) / 2 + 4, label, 10, "#222", "end")
    for label, a, b in comps:
        s.rect(X(a), 70, (b - a) * S, 32, "#fff", "#333", 1.2, "4,3")
        s.text(X((a + b) / 2), 90, label, 11, "#111", "middle", "bold")
    for y, zt, zb in vias:
        s.rect(X(y) - 4, zt, 8, zb - zt, "#444")
    for d, colr, dash, lab, lx, ly in loops:
        s.path(d(X), colr, 2.5, "6,4" if dash else None)
        s.text(X(lx), ly, lab, 10, colr, "middle")
    s.text(x0, h - 10, note, 10, "#444")
    return s.render()


def scenarios():
    """Exact default geometry of PL_A / PL_B / PL_C in q3d_dpt_cell.py (no shunt)."""
    out = []
    out.append(scenario(
        "PL_A: MLCC bank next to QH, L2 = DC− (EPC optimal vertical loop)",
        [("L1", "DCN", 104, 112, [(-0.8, 0.9)]), ("", "DCP", 104, 112, [(1.5, 4.6)]),
         ("", "AC", 104, 112, [(5.2, 8.9)]), ("", "DCN", 104, 112, [(9.5, 11.5)]),
         ("L2 DC−", "DCN", 140, 148, [(-1.0, 11.7)])],
        [("MLCC", 0.2, 2.2), ("QH", 3.4, 6.4), ("QL", 7.7, 10.7)],
        [(-0.4, 104, 148), (11.1, 104, 148)],
        [(lambda X: "M %.1f 60 L %.1f 60" % (X(0.5), X(11.1)), "#e4572e", False,
          "caps + → QH → AC → QL → DC− vias (L1 + parts)", 5.5, 54),
         (lambda X: "M %.1f 172 L %.1f 172" % (X(11.1), X(-0.4)), "#2e86de", True,
          "return on L2 (DC−) to caps − vias", 5.5, 188)],
        "Terminals: DCP CapP→QH_D, AC QH_S→QL_D, DCN QL_S→CapN. Variables: l_vrow, l_capn, gap, l_dcp, "
        "l_ac, l_src, w_cell, h_diel, …"))
    out.append(scenario(
        "PL_B: MLCC bank between QH and QL, L2 = AC (switch node)",
        [("L1", "AC", 104, 112, [(0.0, 1.8)]), ("", "DCP", 104, 112, [(2.4, 5.5)]),
         ("", "DCN", 104, 112, [(6.1, 9.2)]), ("", "AC", 104, 112, [(9.8, 11.6)]),
         ("L2 AC", "AC", 140, 148, [(-0.2, 11.8)])],
        [("QH", 0.6, 3.6), ("MLCC", 4.8, 6.8), ("QL", 8.0, 11.0)],
        [(0.3, 104, 148), (11.3, 104, 148)],
        [(lambda X: "M %.1f 60 L %.1f 60" % (X(11.3), X(0.3)), "#e4572e", False,
          "QL → caps − … caps + → QH → QH source vias (L1 + parts)", 5.8, 54),
         (lambda X: "M %.1f 172 L %.1f 172" % (X(0.3), X(11.3)), "#f3a712", True,
          "return on L2 = AC: QH source → QL drain", 5.8, 188)],
        "Terminals as PL_A. New variables: l_ach (AC landings with via rows), l_dcp, l_dcn. "
        "Note: a large switch-node plane on L2 adds capacitance to DC+/DC− (common-mode / Coss-like)."))
    out.append(scenario(
        "PL_C: two banks (A next to QH, B next to QL): L2 = DC−, L3 = DC+",
        [("L1", "DCN", 104, 112, [(-0.8, 0.9)]), ("", "DCP", 104, 112, [(1.5, 4.6)]),
         ("", "AC", 104, 112, [(5.2, 8.9)]), ("", "DCN", 104, 112, [(9.5, 11.9)]),
         ("", "DCP", 104, 112, [(12.5, 14.2)]),
         ("L2 DC−", "DCN", 134, 142, [(-1.0, 2.45), (3.15, 13.45), (14.15, 14.4)]),
         ("L3 DC+ (h_23)", "DCP", 166, 174, [(-1.0, 14.4)])],
        [("MLCC A", 0.2, 2.2), ("QH", 3.4, 6.4), ("QL", 7.7, 10.7), ("MLCC B", 11.2, 13.2)],
        [(-0.4, 104, 142), (11.0, 104, 142), (2.8, 104, 174), (13.8, 104, 174)],
        [(lambda X: "M %.1f 60 L %.1f 60" % (X(0.5), X(11.0)), "#e4572e", False,
          "loop A on L1: caps A → QH → QL → DC− vias", 5.0, 54),
         (lambda X: "M %.1f 156 L %.1f 156" % (X(11.0), X(-0.4)), "#2e86de", True,
          "loop A returns on L2 (DC−)", 2.0, 128),
         (lambda X: "M %.1f 190 L %.1f 190" % (X(13.8), X(2.8)), "#2a9d8f", True,
          "loop B returns on L3 (DC+): caps B + → QH drain", 8.3, 206)],
        "Terminals: DCP CapAP, CapBP→QH_D; AC QH_S→QL_D; DCN CapAN, CapBN→QL_S. New variables: l_src, "
        "l_capbp, h_23 (sweep 0.1 / 0.5 / 1.2 mm), t_L3, r_anti (L2 clearance around DC+ vias).", 240))
    return out


TABLE = [
    ("h_diel", "0.100", "L1–L2 dielectric (DC+/AC on L1 over DC− on L2)", "side view", "0.075 → 0.299, 0.2 → 0.496 nH"),
    ("t_L1 / t_L2", "0.070 / 0.035", "copper thickness", "side view", "small (skin depth 6.5 µm at 100 MHz)"),
    ("t_pad", "0.035", "pad/solder height; terminal faces sit on top", "side view", "very small"),
    ("gap", "0.600", "spacing between L1 islands = pad gap under each component", "L1 top view, 3 places", "loop length (+gap × 3)"),
    ("w_cell", "9.0", "width of DC− cap landing, DC+ and AC islands; cap via row spread", "L1 top view", "wider → lower L"),
    ("w_sh", "17.0", "width of shunt island, DC− landing, L2 plane; shunt via row spread", "L1/L2 top view", "set by 5 × PRL1632"),
    ("l_vrow / l_capn", "0.8 / 0.9", "DC− cap landing: via strip + cap − pad strip", "L1 top view", "cap return path"),
    ("l_dcp", "3.1", "DC+ island: caps + pads to QH drain pad", "L1 top view", "forward path length"),
    ("l_ac", "3.7", "AC island: QH source pad to QL drain pad", "L1 top view", "forward path length"),
    ("l_s", "2.4", "QL source island to shunt input pads", "L1 top view", "shunt neck"),
    ("g_sh", "0.8", "copper gap under the shunt bodies", "L1 top view", "shunt length"),
    ("l_dcn", "1.4", "DC− landing after the shunt (via row at +0.9)", "L1 top view", "return entry"),
    ("fet_w / fet_pad", "5.0 / 1.0", "EPC2361 pad width / pad length along the loop", "L1 top view", "simplified 2-bar pads"),
    ("cap_p / cap_w", "1.4 / 1.25", "MLCC pitch / pad width (6 caps)", "L1 top view", "bank width"),
    ("sh_p / sh_w", "3.4 / 2.8", "shunt pitch / pad width (5 shunts)", "L1 top view", "array width"),
    ("via_r", "0.150", "via radius (0.3 mm drill)", "both views", "via-transition L"),
]


def main():
    rows = "".join("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % r for r in TABLE)
    html = """<!doctype html><html><head><meta charset="utf-8">
<title>Q3D cell geometry</title>
<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:24px;color:#222;background:#fff;max-width:1220px}
h1{font-size:20px} h2{font-size:16px;margin-top:28px}
table{border-collapse:collapse;font-size:13px} td,th{border:1px solid #ccc;padding:4px 8px;text-align:left}
th{background:#f3f3f3} .key span{display:inline-block;width:14px;height:10px;margin:0 4px 0 12px}
.note{background:#fff8e1;border-left:4px solid #f3a712;padding:8px 12px;font-size:13px}
</style></head><body>
<h1>EPC2361 DPT cell: Q3D model geometry (simulation/q3d/q3d_dpt_cell.py)</h1>
<p class="key">Nets: <span style="background:#e4572e"></span>DCP (DC+)<span style="background:#f3a712"></span>AC
<span style="background:#9b5de5"></span>SQL (QL source / shunt in)<span style="background:#2e86de"></span>DCN (DC−)
<span style="background:#333"></span>pads = terminals</p>
<p class="note">Q3D results (no shunt, h_diel = 0.1 mm, 100 MHz), effective loop at the QL switch, copper / with MLCC ESL:
PL_A 0.310 / 0.390 nH, PL_B 0.303 / 0.383 nH, PL_C (h_23 0.1 mm) 0.288 / 0.333 nH, PL_C (h_23 1.2 mm) 0.306 / 0.372 nH.
The EPC2361 package is not included. EPC's "optimal power loop" (WP010, 4 mil) is 0.35&#8211;0.4 nH including parts,
so these designs are close to the EPC optimum.</p>
<h2>Base cell geometry (shown with the 1 m&#937; shunt; PL_A replaces the shunt section by a 2 mm DC&#8722; source island, l_src)</h2>
%s
%s
<h2>Design variables (mm) and where they act</h2>
<table><tr><th>Variable</th><th>Default</th><th>What it sets</th><th>Where</th><th>Effect on Lloop</th></tr>%s</table>
<h2>Power-loop scenarios in the Q3D script (no shunt, exact default geometry)</h2>
%s
</body></html>""" % (top_views(), side_view(), rows, "".join(scenarios()))
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs",
                        "q3d-geometry-sketches.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(path)


if __name__ == "__main__":
    main()

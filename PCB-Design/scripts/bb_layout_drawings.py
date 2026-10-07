"""
Layout drawings of the building block from simulation/bb_q3d/bb_geometry.py (the same geometry Q3D uses).

    python scripts/bb_layout_drawings.py
      -> reports/building-block/figures/layout_*.pdf|png
      -> docs/building-block-layout.html
"""
import os
import sys

import matplotlib
import matplotlib.patches as mp

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "simulation", "bb_q3d"))
import bb_geometry as geo  # noqa: E402

FIG = os.path.join(ROOT, "reports", "building-block", "figures")
os.makedirs(FIG, exist_ok=True)
COL = {"DCP": "#e4572e", "DCN": "#2e86de", "AC": "#f3a712", "G": "#2a9d8f", "KS": "#7a5c99"}
G = geo.build()
P, Y, GT = G["params"], G["rows"], geo.GATE
XE = P["x_edge"]


def rect(ax, x0, x1, y0, y1, fc="none", ec="none", lw=0.8, ls="-", alpha=1.0, z=1, hatch=None):
    ax.add_patch(mp.Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=fc, edgecolor=ec, lw=lw, ls=ls,
                              alpha=alpha, zorder=z, hatch=hatch))


def frame(ax, title):
    ax.set_xlim(-XE - 1.5, XE + 5.5)
    ax.set_ylim(Y["l4"][1] + 1.0, Y["p1"][0] - 1.5)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.grid(alpha=0.15)
    rect(ax, -XE, XE, Y["p1"][0], Y["l4"][1], ec="k", lw=1.0, z=0)


def vias(ax, layer_filter=None, holes_on=None):
    for net, x, y, to in G["vias"]:
        if layer_filter and to not in layer_filter:
            continue
        ax.add_patch(mp.Circle((x, y), 0.15, color="k", zorder=5))
    if holes_on:
        for pl, x, y in G["holes"]:
            if pl == holes_on:
                ax.add_patch(mp.Circle((x, y), 0.35, facecolor="white", edgecolor="grey", lw=0.5, zorder=4))


def gate_traces(ax):
    yd, yg, xg = GT["y_drv"], GT["y_gate"], GT["x_gate"]
    for (y0, y1) in ((yd, yg), (yd - 1.4, 5.9)):           # LO star down to QL gates, HO star up to QH gates
        ax.plot([0, 0], [y0, y1], color=COL["G"], lw=2, zorder=6)
        ax.plot([-xg, xg], [y1, y1], color=COL["G"], lw=2, zorder=6)
        for s in (-1, 1):
            ax.add_patch(mp.Circle((s * xg, y1), 0.3, color=COL["G"], zorder=7))
    rect(ax, -1.0, 1.0, yd - 1.9, yd + 0.5, fc="#333", z=8)
    ax.text(0, yd - 0.7, "LT8418", color="w", ha="center", va="center", fontsize=6, zorder=9)
    ax.text(0.2, yg + 0.9, "LO star", color=COL["G"], fontsize=6, ha="center")
    ax.text(0.2, 5.4, "HO star", color=COL["G"], fontsize=6, ha="center")


def top_view(ax):
    frame(ax, "L1 (top copper) + parts")
    for net, name, layer, x0, x1, y0, y1 in G["boxes"]:
        if layer == "L1":
            rect(ax, x0, x1, y0, y1, fc=COL[net], alpha=0.35)
        elif layer == "PAD":
            rect(ax, x0, x1, y0, y1, fc="#333", alpha=0.85, z=3)
    # component bodies
    for s in (-1, 1):
        xc = s * P["xc"]
        for name, (y0, y1) in (("QH", (Y["qhd"][0], Y["qhs"][1])), ("QL", (Y["qld"][0], Y["qls"][1]))):
            rect(ax, xc - 2.5, xc + 2.5, y0, y1, ec="k", lw=1.2, ls="--", z=4)
            ax.text(xc + s * 1.2, (y0 + y1) / 2, "%s_%s" % (name, "LR"[s > 0]), ha="center", va="center",
                    fontsize=7, zorder=9, bbox=dict(fc="w", ec="none", alpha=0.7, pad=0.5))
        for i in range(6):
            x = xc + (i - 2.5) * P["cap_p"]
            rect(ax, x - 0.62, x + 0.62, Y["capn"][0], Y["capp"][1], ec="#555", ls=":", z=4)
    for g0 in (Y["p1"][1], Y["n1"][1], Y["p2"][1]):
        (u0, u1), (l0, l1) = geo._row_pads(g0)
        for s in (-1, 1):
            for xb in P["bank_x"]:
                rect(ax, s * xb - 1.25, s * xb + 1.25, u0, l1, ec="#555", ls=":", z=4)
    vias(ax)
    gate_traces(ax)
    for lab, y in (("P1 (DC+)", sum(Y["p1"]) / 2), ("N1 (DC-)", sum(Y["n1"]) / 2), ("P2 (DC+)", sum(Y["p2"]) / 2),
                   ("N2 (DC-)", sum(Y["n2"]) / 2), ("DCP", sum(Y["dcp"]) / 2), ("AC", sum(Y["ac"]) / 2),
                   ("SRC (DC-)", sum(Y["src"]) / 2)):
        ax.text(XE + 0.5, y, lab, fontsize=7, va="center")
    ax.text(0, sum(Y["t_dcp"]) / 2, "T_DC+", color="w", ha="center", va="center", fontsize=6, zorder=9)
    ax.text(0, sum(Y["t_dcn"]) / 2, "T_DC-", color="w", ha="center", va="center", fontsize=6, zorder=9)


def plane_view(ax, layer, net, title, holes_on=None, extra=None):
    frame(ax, title)
    for n, name, lay, x0, x1, y0, y1 in G["boxes"]:
        if lay == layer:
            rect(ax, x0, x1, y0, y1, fc=COL[n], alpha=0.35)
        if lay == "PADB" and layer == "L4":
            rect(ax, x0, x1, y0, y1, fc="#333", alpha=0.85, z=3)
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, "T_AC (bottom)", color="w", ha="center", va="center", fontsize=6, zorder=9)
    vias(ax, holes_on=holes_on)
    for s in (-1, 1):
        for y0, y1 in ((Y["qhd"][0], Y["qhs"][1]), (Y["qld"][0], Y["qls"][1])):
            rect(ax, s * P["xc"] - 2.5, s * P["xc"] + 2.5, y0, y1, ec="grey", ls="--", z=2)
    if extra:
        extra(ax)


def stackup(ax):
    layers = [("L1  top: cells, bank strips, pads  (70 um)", 0.07, "#e4572e"),
              ("prepreg h_diel = 0.10 mm", 0.10, "#efe3c2"),
              ("L2  DC- plane  (70 um, 2 oz)", 0.07, "#2e86de"),
              ("core h_23 = 1.20 mm", 1.2, "#d9c9a3"),
              ("L3  DC+ plane  (70 um, 2 oz)", 0.07, "#e4572e"),
              ("prepreg h_34 = 0.10 mm", 0.10, "#efe3c2"),
              ("L4  AC plane + AC terminal  (70 um)", 0.07, "#f3a712")]
    y = 0
    for lab, t, c in layers:
        h = max(t, 0.12) * (1 if t < 1 else 0.35)
        ax.add_patch(mp.Rectangle((0, y - h), 6, h, color=c, alpha=0.85))
        ax.text(6.2, y - h / 2, lab, va="center", fontsize=8)
        y -= h
    ax.set_xlim(0, 16)
    ax.set_ylim(y - 0.1, 0.1)
    ax.axis("off")
    ax.set_title("Stack-up (thickness not to scale), 1.6 mm, 4 layers", fontsize=10)


def main():
    figs = {}
    fig, ax = plt.subplots(figsize=(8, 8.4))
    top_view(ax)
    figs["layout_top"] = fig
    fig, axs = plt.subplots(1, 3, figsize=(16, 7.2))
    plane_view(axs[0], "L2", "DCN", "L2: DC- plane (anti-pads for DC+ / AC vias)", holes_on="L2")
    plane_view(axs[1], "L3", "DCP", "L3: DC+ plane (bank strips -> cells)", holes_on="L3")
    plane_view(axs[2], "L4", "AC", "L4: AC plane, AC terminal bottom centre")
    fig.tight_layout()
    figs["layout_inner"] = fig
    fig, ax = plt.subplots(figsize=(8, 3))
    stackup(ax)
    figs["layout_stackup"] = fig
    for name, f in figs.items():
        f.savefig(os.path.join(FIG, name + ".pdf"), bbox_inches="tight")
        f.savefig(os.path.join(FIG, name + ".png"), dpi=140, bbox_inches="tight")
    rel = os.path.relpath(FIG, os.path.join(ROOT, "docs")).replace("\\", "/")
    rows = "".join("<tr><td>%s</td><td>%s</td></tr>" % kv for kv in (
        ("Board", "30 x 28.2 mm, 4 layers, 1.6 mm; mirror-symmetric about x = 0"),
        ("Cells", "2 x PL_A vertical loops at x = +/-%.1f mm, island width %.1f mm" % (P["xc"], P["w_cell"])),
        ("Driver", "LT8418 in the 6 mm centre corridor at the AC-island height; HO and LO stars to both FETs"),
        ("Local caps", "6 x 1 uF 0805 per cell next to QH (commutation loop over L2)"),
        ("Bank", "24 x 10 uF 1210 in three rows between alternating DC+/DC- strips (P1, N1, P2, N2)"),
        ("L2", "solid DC- under everything, anti-pads for DC+ and AC vias"),
        ("L3", "DC+ plane: bank strips P1/P2 and both cell DC+ islands"),
        ("L4", "AC plane joining both switch nodes; AC terminal pad bottom centre"),
        ("Terminals", "T_DC+ (P1 centre), T_DC- (N1 centre), T_AC (bottom side, centre)")))
    html = """<!doctype html><html><head><meta charset="utf-8"><title>Building block layout</title>
<style>body{font-family:Segoe UI,Arial,sans-serif;margin:24px;max-width:1300px;color:#222}
img{max-width:100%%;border:1px solid #ddd;margin:8px 0} td{border:1px solid #ccc;padding:4px 8px;font-size:13px}
table{border-collapse:collapse}</style></head><body>
<h1>Symmetric building block: 2 x EPC2361 per switch, driver in the middle</h1>
<p>Generated from <code>simulation/bb_q3d/bb_geometry.py</code>, the same geometry used by the Q3D model
(<code>simulation/bb_q3d/bb_q3d.py</code>). Colours: red DC+, blue DC-, orange AC, green gate, dark pads = Q3D terminals,
dashed = component bodies (gaps in copper).</p>
<table>%s</table>
<h2>Top layer</h2><img src="%s/layout_top.png">
<h2>Inner and bottom layers</h2><img src="%s/layout_inner.png">
<h2>Stack-up</h2><img src="%s/layout_stackup.png">
</body></html>""" % (rows, rel, rel, rel)
    with open(os.path.join(ROOT, "docs", "building-block-layout.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("ok")


if __name__ == "__main__":
    main()

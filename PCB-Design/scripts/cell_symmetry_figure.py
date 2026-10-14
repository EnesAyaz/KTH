"""
Left vs right cell of one block (Rev B, block 1): EPC2361 pads by function and the Kelvin collector routes,
before (on L2, the DC- return plane) and after the fix (on L4). Reads the board through kicad-cli free text:
pad data via KiCad python is not available in the matplotlib venv, so pads are taken from hardware/spb-bb-revb-dpt/
parts.json + the EPC2361 footprint (rot 180 left, 0 right), exactly as placed by make_kicad_bb_revb.py.

    C:\\Github\\KTH\\LossCalculation-SPB\\.venv\\Scripts\\python.exe scripts\\cell_symmetry_figure.py
      -> reports/shunt-loop/figs/cell_symmetry.png
"""
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = {p["ref"]: p for p in json.load(open(os.path.join(ROOT, "hardware", "spb-bb-revb-dpt", "parts.json")))}
# EPC2361 footprint (epc2361-cell.pretty): number, x, y, w, h, function
PADS = [("1", -2.352, -1.23, 1.102, 1.14, "G"), ("2", -2.352, 0.67, 1.102, 2.26, "K"),
        ("3", -1.275, 0, 0.65, 3.6, "D"), ("4", -0.425, 0, 0.65, 3.6, "S"), ("5", 0.425, 0, 0.65, 3.6, "D"),
        ("6", 1.275, 0, 0.65, 3.6, "S"), ("7", 2.352, 0, 1.102, 3.6, "D")]
COL = {"G": "#2CA02C", "K": "#9467BD", "D": "#D62728", "S": "#1F77B4"}
BX = -23.75                                    # block 1 centre
XB, YSH, YSL = 4.3, 4.9, 9.2                   # (make_kicad_bb_revb.py: XB = XC - 5.2, YSH/YSL)
KROW = {"H": YSH + 0.85, "L": YSL - 0.85}


def place(ax, ref):
    p = PARTS[ref]
    x0, y0, rot = p["x"] - BX, p["y"], p["rot"]
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = {}
    for num, px, py, w, h, f in PADS:
        # KiCad: y down, rotation counter-clockwise on screen
        rx, ry = px * c + py * s, -px * s + py * c
        if abs(round(s)) == 1:
            w, h = h, w
        ax.add_patch(Rectangle((x0 + rx - w / 2, y0 + ry - h / 2), w, h, color=COL[f], alpha=0.9))
        ax.text(x0 + rx, y0 + ry, f, ha="center", va="center", fontsize=7, color="white", weight="bold")
        out[f + num] = (x0 + rx, y0 + ry, w, h)
    ax.text(x0, y0 - 2.6, "%s (rot %d°)" % (ref, rot), ha="center", fontsize=8)
    return out


fig, axs = plt.subplots(1, 2, figsize=(11.5, 5.6), dpi=200)
for k, (ax, title, layer) in enumerate(zip(axs, ("before: Kelvin collectors on L2 (DC$-$ return plane)",
                                                    "after: Kelvin collectors on L4 (bottom)"), ("L2", "L4"))):
    ax.add_patch(Rectangle((-16, -1.5), 32, 14, color="#5B8BD0", alpha=0.10))
    ax.text(-15.6, 12.1, "L2: DC$-$ plane (return of the commutation loop)", fontsize=7, color="#3060A0")
    for ref in ("Q1", "Q2", "Q3", "Q4"):
        pads = place(ax, ref)
        kx, ky = pads["K2"][0], pads["K2"][1]
        sgn = -1 if PARTS[ref]["x"] - BX < 0 else 1
        tag = "H" if ref in ("Q1", "Q2") else "L"
        kvx = kx - sgn * 1.05 * 0 + (0 if True else 0)
        pts = [(kx, ky), (sgn * XB, ky), (sgn * XB, KROW[tag]), (0, KROW[tag])]
        if k == 0:
            for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
                ax.add_patch(Rectangle((min(xa, xb) - 0.65, min(ya, yb) - 0.65), abs(xb - xa) + 1.3, abs(yb - ya) + 1.3,
                                       facecolor="white", edgecolor="#555555", hatch="////", lw=0.6))
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=COL["K"], lw=2.0, ls="-" if k == 0 else "--")
    # driver and gate stars
    ax.add_patch(FancyBboxPatch((-1.2, 17.5), 2.4, 2.4, boxstyle="round,pad=0.1", color="#444444"))
    ax.text(0, 18.7, "2EDF", color="white", ha="center", va="center", fontsize=7)
    ax.annotate("", (0, 13.5), (0, 17.3), arrowprops=dict(arrowstyle="-|>", color="gray"))
    ax.text(0.4, 15.5, "gate stars", fontsize=7, color="gray")
    ax.axvline(0, color="gray", lw=0.6, ls=":")
    ax.text(0.2, -2.6, "mirror line", fontsize=7, color="gray")
    ax.set_title(title, fontsize=9)
    ax.set_xlim(-16, 16)
    ax.set_ylim(20.5, -4)
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm, block-local)")
    ax.set_ylabel("y (mm)")
    for f_, lab in (("D", "drain"), ("S", "source"), ("G", "gate"), ("K", "Kelvin (source, own net)")):
        ax.plot([], [], "s", color=COL[f_], label=lab)
    ax.plot([], [], color=COL["K"], lw=2, label="Kelvin collector")
    if k == 0:
        ax.add_patch(Rectangle((0, 0), 0, 0, facecolor="white", edgecolor="#555555", hatch="////", label="slot in L2"))
    ax.legend(fontsize=6.5, loc="lower left")
fig.suptitle("Left cell rot 180°, right cell rot 0°: drain/source stripes mirror-symmetric, gate and Kelvin pads swap "
             "top/bottom", fontsize=9.5)
fig.tight_layout()
out = os.path.join(ROOT, "reports", "shunt-loop", "figs", "cell_symmetry.png")
fig.savefig(out)
print(out)

"""
Concept drawing of one SPB cell (submodule): three leg boards on one long liquid cold plate, laminated DC busbar,
phase leads, cell aux/control board; (b) cross-section of the cooling and insulation stack.

    python scripts/cell_concept.py -> hardware/spb-building-block/cell_concept.pdf|png
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import eth_style as es  # noqa: E402

es.setup()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch  # noqa: E402

C = es.C
OUT = os.path.join(ROOT, "hardware", "spb-building-block")
W, H = 33.0, 52.7               # leg board outline (mm), from make_kicad_bb.py
GAP, AUX = 3.0, 24.0            # gap between boards, aux/control board length
L_CELL = 3 * W + 2 * GAP + GAP + AUX


def box(ax, x, y, w, h, fc, ec="k", lw=0.6, z=1, alpha=1.0, ls="-", r=0.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=%g" % r, fc=fc, ec=ec, lw=lw,
                                zorder=z, alpha=alpha, ls=ls))


fig = plt.figure(figsize=(es.TXT_W, 3.3))
ax = fig.add_axes([0.01, 0.06, 0.62, 0.9])
ax.set_aspect("equal")
ax.axis("off")
# cold plate
box(ax, -8, -6, L_CELL + 16, H + 12, (0.80, 0.86, 0.92), ec=(0.35, 0.5, 0.65), lw=0.8, z=0, r=3)
ax.text(L_CELL / 2, H + 3.2, "liquid cold plate (grounded), AlN insulator strip under the boards", ha="center", fontsize=6.5,
        color=(0.2, 0.35, 0.5))
for xx, lab in ((-8, "coolant in"), (L_CELL + 8, "coolant out")):
    ax.add_patch(Rectangle((xx - 3, 20), 6, 8, fc=C["blue"], ec="k", lw=0.5, zorder=1))
    ax.text(xx, 31, lab, ha="center", fontsize=6, color=C["blue"])
ax.plot([-5, L_CELL + 5], [24, 24], color=C["blue"], lw=0.8, ls=(0, (6, 3)), zorder=1)
# boards
for k, leg in enumerate("ABC"):
    x0 = k * (W + GAP)
    box(ax, x0, 0, W, H, (0.13, 0.45, 0.25), z=2, r=1)
    ax.add_patch(Rectangle((x0 + 1.5, 13.2), W - 3, 28.2, fc=(0.12, 0.55, 0.28), ec="none", zorder=3))   # power stage
    for i in range(4):
        ax.add_patch(Rectangle((x0 + 6 + (i % 2) * 16, 17 + (i // 2) * 6.5), 5, 3, fc="0.15", ec="none", zorder=4))
    ax.add_patch(Rectangle((x0 + W / 2 - 2.5, 19.5), 5, 5, fc="k", ec="none", zorder=4))
    for xc in (x0 + 10.5, x0 + 22.5):                    # DC terminals (bottom side, dashed)
        ax.add_patch(Circle((xc, H - 6.0), 2.6, fc="0.6", ec="k", lw=0.4, zorder=5, ls="--"))
    ax.add_patch(Circle((x0 + 10.6, 6.6), 3.8, fc="0.6", ec="k", lw=0.4, zorder=5, ls="--"))       # AC terminal
    ax.add_patch(Rectangle((x0 + 19, 4.0), 9, 2.5, fc=(0.85, 0.75, 0.45), ec="k", lw=0.3, zorder=5))  # FFC
    ax.text(x0 + W / 2, 33, "leg %s" % leg, ha="center", color="w", fontsize=7, zorder=6, fontweight="bold")
    # phase lead
    ax.plot([x0 + 10.6, x0 + 10.6], [6.6, -14 - 4 * k], color=[C["yellow"], C["purple"], "0.3"][k], lw=2.2, zorder=6)
    ax.plot([x0 + 10.6, L_CELL + 14], [-14 - 4 * k] * 2, color=[C["yellow"], C["purple"], "0.3"][k], lw=2.2, zorder=6)
ax.text(L_CELL + 14, -29, "phase leads A, B, C to the end winding", fontsize=6, va="center", ha="right")
# busbar (bottom side, under the DC terminal zones)
ax.add_patch(Rectangle((-2, H - 10.5), 3 * W + 2 * GAP + 4, 9, fc=(0.85, 0.3, 0.2), ec="k", lw=0.5, zorder=4.5, alpha=0.45))
ax.text(-3, H - 6, "laminated DC busbar\n(DC+/DC$-$, bottom side)", ha="right", va="center", fontsize=6, color=C["dred"])
for side, yy, lab in ((-1, H - 3.5, "to SM $k{-}1$ (DC+)"), (1, H - 8.5, "to SM $k{+}1$ (DC$-$)")):
    pass
# aux / control board
xa = 3 * (W + GAP)
box(ax, xa, 4, AUX, H - 8, (0.25, 0.35, 0.55), z=2, r=1)
ax.text(xa + AUX / 2, H / 2 + 6, "cell aux /\ncontrol", ha="center", va="center", color="w", fontsize=6.5, zorder=6)
ax.text(xa + AUX / 2, H / 2 - 6, "75 V$\\rightarrow$12 V\n3$\\times$ iso 6 V (HS)\n1$\\times$ 6 V (LS)\nMCU, fibre", ha="center",
        va="center", color="w", fontsize=5.2, zorder=6)
ax.plot([3 * W + 2 * GAP - 2, xa + 2], [5.2, 5.2], color=(0.85, 0.75, 0.45), lw=1.5, zorder=6)
ax.text(xa - 1.5, 1.2, "FFC", fontsize=5.5, ha="right")
ax.annotate("", xy=(L_CELL + 2, -32), xytext=(0, -32), arrowprops=dict(arrowstyle="->", lw=0.7))
ax.text(L_CELL / 2, -36, "axial direction, cell length about %.0f mm" % L_CELL, ha="center", fontsize=6.5)
ax.text(-16, 8, "%.0f mm" % H, rotation=90, va="center", ha="center", fontsize=6.5)
ax.set_xlim(-30, L_CELL + 32)
ax.set_ylim(-40, H + 8)
ax.text(-30, -40, "(a)", fontsize=7.5, fontweight="bold")

# ---------------- (b) cross-section
ax = fig.add_axes([0.64, 0.08, 0.36, 0.86])
ax.axis("off")
ax.set_xlim(-3, 58)
ax.set_ylim(-2, 34)
layers = [  # (y0, h, color, label)
    (30.0, 3.0, (0.75, 0.82, 0.90), "Al cold plate, liquid channels (grounded)"),
    (28.8, 1.2, (0.95, 0.95, 0.88), "AlN 0.63 mm (insulation)"),
    (28.3, 0.5, C["cyan"], "thin compliant TIM"),
]
for y0, h, col, lab in layers:
    ax.add_patch(Rectangle((2, y0), 26, h, fc=col, ec="k", lw=0.4))
    ax.text(29, y0 + h / 2 + {"AlN 0.63 mm (insulation)": 0.5, "thin compliant TIM": -0.3}.get(lab, 0), lab, fontsize=5.6, va="center")
for x0 in (5, 15):
    ax.add_patch(Rectangle((x0, 26.6), 4.5, 1.7, fc="0.7", ec="k", lw=0.3))     # pedestal (part of plate)
    ax.add_patch(Rectangle((x0 + 0.5, 25.8), 3.5, 0.8, fc="0.15", ec="k", lw=0.3))  # EPC2361 (top-cooled)
ax.add_patch(Rectangle((21, 24.3), 6, 2.0, fc=(0.35, 0.25, 0.2), ec="k", lw=0.3))   # MLCC bank
ax.add_patch(Rectangle((21, 26.3), 6, 2.0, fc="0.7", ec="k", lw=0.3))
ax.text(29, 26.6, "pedestals over FETs and MLCC bank", fontsize=5.6, va="center")
ax.add_patch(Rectangle((2, 24.1), 26, 1.7, fc=(0.13, 0.45, 0.25), ec="k", lw=0.4))
ax.text(29, 25.0, "leg PCB (4 layers)", fontsize=5.6, va="center")
ax.add_patch(Rectangle((3, 20.3), 4.0, 3.8, fc="0.55", ec="k", lw=0.3))
ax.text(29, 22.4, "REDCUBE terminals (bottom)", fontsize=5.6, va="center")
for y0, col in ((19.3, C["red"]), (18.6, (0.95, 0.95, 0.88)), (17.9, C["blue"])):
    ax.add_patch(Rectangle((1, y0), 14, 0.7, fc=col, ec="k", lw=0.3))
ax.text(29, 18.7, "laminated busbar DC+/DC$-$", fontsize=5.6, va="center")
ax.add_patch(Rectangle((1, 15.6), 27, 1.4, fc=(0.95, 0.95, 0.88), ec="k", lw=0.3, hatch="////"))
ax.text(29, 16.3, "insulation sheet / air gap", fontsize=5.6, va="center")
ax.add_patch(Rectangle((0, 7.0), 30, 8.0, fc=(0.62, 0.66, 0.70), ec="k", lw=0.4))
ax.text(15, 11, "motor housing (stator)", fontsize=6, ha="center", va="center")
ax.annotate("", xy=(-1.5, 33), xytext=(-1.5, 8), arrowprops=dict(arrowstyle="->", lw=0.6))
ax.text(-2.6, 20, "radial", rotation=90, fontsize=6, va="center", ha="center")
ax.text(-3, -1.5, "(b)", fontsize=7.5, fontweight="bold")
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(OUT, "cell_concept." + ext), dpi=220)
print("cell length %.0f mm" % L_CELL)

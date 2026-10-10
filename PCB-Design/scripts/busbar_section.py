"""
Section of the laminated DC busbar through the DC+ (J1) and DC- (J2) terminals of one leg board, same parameters as
the Fusion script (hardware/cell-assembly/SPB_Cell_Assembly/SPB_Cell_Assembly.py).

    python scripts/busbar_section.py -> hardware/cell-assembly/busbar_section.png|pdf
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import eth_style as es  # noqa: E402
import cell_render as cr  # noqa: E402  (parameters parsed from the Fusion script)

es.setup()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

P, J1, J2 = cr.P, cr.J1, cr.J2
CU, CU2, INS, GREY, PCB = (0.86, 0.50, 0.30), (0.72, 0.40, 0.22), (0.95, 0.80, 0.25), (0.6, 0.62, 0.65), (0.10, 0.42, 0.22)


def r(ax, x0, x1, z0, z1, fc, ec="k", lw=0.4, hatch=None, z=1):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw, hatch=hatch, zorder=z))


def slab(ax, x0, x1, z0, z1, holes, fc, z=1):
    """horizontal plate from x0 to x1 with gaps (hole centre, diameter)."""
    cuts = sorted((c - d / 2, c + d / 2) for c, d in holes)
    x = x0
    for a, b in cuts:
        if a > x:
            r(ax, x, a, z0, z1, fc, z=z)
        x = max(x, b)
    if x < x1:
        r(ax, x, x1, z0, z1, fc, z=z)


fig, ax = plt.subplots(figsize=(es.TXT_W, 2.9))
zt = -P["term_dc_h"]
zp0 = zt - P["bb_cu"]
zi0 = zp0 - P["bb_ins"]
zn0 = zi0 - P["bb_cu"]
x1, x2 = J1[0], J2[0]
# board and terminals
r(ax, -16.5, 16.5, 0, P["bt"], PCB)
for xc in (x1, x2):
    r(ax, xc - 3.5, xc + 3.5, zt, 0, GREY)
    r(ax, xc - 2.0, xc + 2.0, zt, -1.0, "w", ec="0.3", lw=0.3, hatch="////")          # M4 internal thread
# DC+ plate (on the DC+ terminal), film, DC- plate with boss
slab(ax, -22, 22, zp0, zt, [(x1, P["scr_d"] + 0.4), (x2, P["clr_hole"])], CU, z=2)
slab(ax, -22, 22, zi0, zp0, [(x1, P["head_d"] + 3.0), (x2, P["boss_d"] + 2.0)], INS, z=2)
slab(ax, -22, 22, zn0, zi0, [(x1, P["head_d"] + 3.0), (x2, P["scr_d"] + 0.4)], CU2, z=2)
slab(ax, x2 - P["boss_d"] / 2, x2 + P["boss_d"] / 2, zi0, zt, [(x2, P["scr_d"] + 0.4)], CU2, z=2)
# screws (shaft + head)
for xc, zh in ((x1, zp0), (x2, zn0)):
    r(ax, xc - P["scr_d"] / 2, xc + P["scr_d"] / 2, zh, -1.2, "0.45", z=3)
    r(ax, xc - P["head_d"] / 2, xc + P["head_d"] / 2, zh - P["head_h"], zh, "0.45", z=3)
# annotations
def lab(x, y, tx, ty, s):
    ax.annotate(s, xy=(x, y), xytext=(tx, ty), fontsize=6.6, arrowprops=dict(arrowstyle="-", lw=0.5, color="0.3"),
                va="center")


lab(-14, 0.8, -31, 2.2, "leg PCB (DC terminal zone)")
lab(x1 - 3.5, -3.2, -31, -2.8, "REDCUBE M4, DC+ (J1)")
lab(-18, (zp0 + zt) / 2, -31, -6.4, "DC+ Cu 1.5 mm")
lab(-18, (zi0 + zp0) / 2, -31, -8.9, "insulation film 0.25 mm")
lab(-18, (zn0 + zi0) / 2, -31, -11.2, "DC$-$ Cu 1.5 mm")
lab(x1, zp0 - 1.5, -31, -13.6, "M4 head clamps DC+ through\nan access hole in DC$-$")
lab(x2 + 3.5, -3.2, 25, -2.8, "REDCUBE M4, DC$-$ (J2)")
lab(x2 + P["boss_d"] / 2, -7.4, 25, -6.0, "DC$-$ boss (1.75 mm) through")
ax.text(25, -7.6, "an %.0f mm clearance hole in DC+" % P["clr_hole"], fontsize=6.6, va="center")
lab(x2, zn0 - 1.5, 25, -11.5, "M4 head on DC$-$")
ax.annotate("", xy=(x2 + P["boss_d"] / 2, -7.2), xytext=(x2 + P["clr_hole"] / 2, -7.2),
            arrowprops=dict(arrowstyle="<->", lw=0.5))
ax.text(x2 + 4.5, -6.6, "%.0f mm" % ((P["clr_hole"] - P["boss_d"]) / 2), fontsize=6, ha="center")
ax.set_xlim(-32, 46)
ax.set_ylim(-16, 3.5)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Section through the DC terminals of one leg (dimensions in mm, film thickness exaggerated in colour only)",
             fontsize=7.5)
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(cr.OUT, "busbar_section." + ext), dpi=220, bbox_inches="tight")
print("wrote busbar_section")

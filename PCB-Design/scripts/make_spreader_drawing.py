"""
Workshop drawing of the aluminium heat spreader for the SPB building block (HS1).

    python scripts/make_spreader_drawing.py  -> hardware/spb-bb-fab/fab/spb-bb-fab-spreader-drawing.pdf

Geometry is the one used in make_3d_models.py (HS_LAM4K5012_assembly), origin at the centre between the two
cells (board y = 6.1 mm). Heatsink holes H5-H8 on the board are at (+-19.2, -1.6) and (+-19.2, 14.8), i.e. at
y = -7.7 and +8.7 in spreader coordinates.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "hardware", "spb-bb-fab", "fab", "spb-bb-fab-spreader-drawing.pdf")

PLATE = (-21.0, -6.95, 21.0, 6.95)
EARS = [(-21.0, -10.15, -16.5, -6.95), (16.5, -10.15, 21.0, -6.95),
        (-21.0, 6.95, -16.5, 11.25), (16.5, 6.95, 21.0, 11.25)]
PEDS = [(-13.5, -4.0, -5.5, 6.0), (5.5, -4.0, 13.5, 6.0)]
HOLES = [(-19.2, -7.7), (19.2, -7.7), (-19.2, 8.7), (19.2, 8.7)]
T_PLATE, T_PED = 3.0, 0.6
LW = 0.8


def outline():
    """Plate plus ears as one polygon (counter-clockwise in drawing coordinates, y up)."""
    return [(-21.0, -10.15), (-16.5, -10.15), (-16.5, -6.95), (16.5, -6.95), (16.5, -10.15), (21.0, -10.15),
            (21.0, 11.25), (16.5, 11.25), (16.5, 6.95), (-16.5, 6.95), (-16.5, 11.25), (-21.0, 11.25)]


def dim(ax, p0, p1, off, text, vertical=False, fs=7):
    (x0, y0), (x1, y1) = p0, p1
    kw = dict(arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0))
    if vertical:
        xd = x0 + off
        ax.plot([x0, xd + (0.6 if off > 0 else -0.6)], [y0, y0], lw=0.3, color="k")
        ax.plot([x1, xd + (0.6 if off > 0 else -0.6)], [y1, y1], lw=0.3, color="k")
        ax.annotate("", (xd, y0), (xd, y1), **kw)
        ax.text(xd + (0.5 if off > 0 else -0.5), (y0 + y1) / 2, text, fontsize=fs, rotation=90,
                ha="left" if off > 0 else "right", va="center")
    else:
        yd = y0 + off
        ax.plot([x0, x0], [y0, yd + (0.6 if off > 0 else -0.6)], lw=0.3, color="k")
        ax.plot([x1, x1], [y1, yd + (0.6 if off > 0 else -0.6)], lw=0.3, color="k")
        ax.annotate("", (x0, yd), (x1, yd), **kw)
        ax.text((x0 + x1) / 2, yd + (0.4 if off > 0 else -0.4), text, fontsize=fs, ha="center",
                va="bottom" if off > 0 else "top")


fig = plt.figure(figsize=(11.69, 8.27))
# ---- view from the board side (pedestals towards the viewer); drawing y up = board y down is mirrored, so
# flip y to keep the board orientation: drawing y = -spreader y
top = fig.add_axes([0.04, 0.33, 0.58, 0.62])
top.set_aspect("equal")
top.axis("off")
top.add_patch(Polygon([(x, -y) for x, y in outline()], closed=True, fill=False, lw=LW))
for x0, y0, x1, y1 in PEDS:
    top.add_patch(Rectangle((x0, -y1), x1 - x0, y1 - y0, fill=True, fc="0.85", ec="k", lw=LW))
for x, y in HOLES:
    top.add_patch(Circle((x, -y), 1.25, fill=False, lw=LW))
    top.plot([x - 2, x + 2], [-y, -y], lw=0.3, color="k", ls="-.")
    top.plot([x, x], [-y - 2, -y + 2], lw=0.3, color="k", ls="-.")
top.plot([-23, 23], [0, 0], lw=0.3, color="k", ls="-.")
top.plot([0, 0], [-13, 12], lw=0.3, color="k", ls="-.")
dim(top, (-21, 10.15), (21, 10.15), 5.0, "42.0")
dim(top, (-21, 6.95), (-21, -6.95), -4.5, "13.9", vertical=True)
dim(top, (21, 10.15), (21, -11.25), 9.0, "21.4", vertical=True)
dim(top, (-16.5, 10.15), (-21, 10.15), 2.4, "4.5")
dim(top, (-19.2, -8.7), (19.2, -8.7), -5.5, "38.4 (hole pitch)")
dim(top, (19.2, 7.7), (19.2, -8.7), 7.3, "16.4", vertical=True)
dim(top, (-13.5, 4.0), (-5.5, 4.0), 7.0, "8.0")
dim(top, (5.5, 4.0), (-5.5, 4.0), 7.0, "11.0")
dim(top, (13.5, 4.0), (13.5, -6.0), 1.8, "10.0", vertical=True)
dim(top, (-13.5, 4.0), (-13.5, 0.0), -2.2, "4.0", vertical=True)
top.text(-19.2, -14.0, "4x M2.5 thread, through\n(screw from the PCB side)", fontsize=7, ha="center")
top.text(-9.5, -1.0, "pedestal\n0.6 high", fontsize=7, ha="center", va="center")
top.text(9.5, -1.0, "pedestal\n0.6 high", fontsize=7, ha="center", va="center")
top.text(0.5, 12.6, "symmetry", fontsize=6, ha="left")
top.set_title("View A: face towards the PCB (pedestals up). Board orientation: driver side at the top.", fontsize=9)
top.set_xlim(-27, 33)
top.set_ylim(-19, 18)

# ---- section B-B through the pedestals (y = 1)
sec = fig.add_axes([0.04, 0.06, 0.58, 0.24])
sec.set_aspect("equal")
sec.axis("off")
sec.add_patch(Rectangle((-21, 0), 42, T_PLATE, fill=True, fc="0.92", ec="k", lw=LW, hatch="////"))
for x0, _, x1, _ in PEDS:
    sec.add_patch(Rectangle((x0, -T_PED), x1 - x0, T_PED, fill=True, fc="0.92", ec="k", lw=LW, hatch="////"))
dim(sec, (-21, 3.0), (-21, 0.0), -2.0, "3.0", vertical=True)
dim(sec, (13.5, 0.0), (13.5, -0.6), 4.0, "0.6", vertical=True)
sec.text(0, 4.2, "Section B-B (through the pedestals), heatsink side up", fontsize=9, ha="center")
sec.set_xlim(-27, 31)
sec.set_ylim(-3, 6)

# ---- notes / title block
nt = fig.add_axes([0.63, 0.06, 0.36, 0.89])
nt.axis("off")
notes = [
    ("Part", "HS1 heat spreader, SPB GaN building block rev A"),
    ("Material", "Aluminium EN AW-6061-T6 (6082-T6 acceptable)"),
    ("Quantity", "1 per board (+1 spare)"),
    ("Units / tolerance", "mm; general ISO 2768-m"),
    ("Flatness", "pedestal faces 0.02 mm, top face 0.05 mm"),
    ("Pedestal height", "0.60 +-0.02, both pedestals equal within 0.02"),
    ("Surface", "pedestal faces and top face Ra <= 0.8, as machined;\nno anodising (thermal contact)"),
    ("Edges", "break 0.2 x 45 deg, deburr; no burrs on the pedestals"),
    ("Holes", "4x M2.5 thread through, at (+-19.2, -7.7) and (+-19.2, +8.7)\nfrom the centre between the cells"),
    ("Mating", "gap pad 8 x 10 mm, 0.5 mm, >= 5 W/mK, insulating,\none per pedestal (Bergquist TGP 5000 / Gap Pad 5000S35,\n0.020 in, or equivalent)"),
    ("Assembly stack", "PCB / EPC2361 (0.68) / gap pad 0.5 -> 0.4 /\npedestal 0.6 / plate 3.0 / thermal compound / LAM 4 K 50 12"),
    ("Note", "EPC2361 top is at source potential: the pad is the only\ninsulation between the cells and the spreader. Check that no\nparts other than the FETs are higher than 1.6 mm under the plate."),
    ("Ref.", "scripts/make_3d_models.py (HS_LAM4K5012_assembly),\nreports/pcb-fab/pcb_fab_report.tex, cooling section"),
]
y = 0.98
for k, v in notes:
    nt.text(0.0, y, k, fontsize=7, weight="bold", va="top")
    nt.text(0.25, y, v, fontsize=7, va="top")
    y -= 0.035 + 0.026 * v.count("\n") + 0.012
nt.add_patch(Rectangle((0, 0), 1, 0.13, fill=False, lw=LW, transform=nt.transAxes))
nt.text(0.03, 0.095, "KTH  SPB GaN building block", fontsize=10, weight="bold")
nt.text(0.03, 0.05, "Heat spreader HS1   rev A   not to scale, use dimensions", fontsize=8)
nt.text(0.03, 0.015, "Drawn by: E. Ayaz   (generated by scripts/make_spreader_drawing.py)", fontsize=7)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT)
print("wrote", OUT)

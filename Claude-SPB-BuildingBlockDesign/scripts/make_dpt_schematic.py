"""Draws the exact double-pulse test circuit implemented in
src/spb_bb/ltspice/double_pulse.py (topology, node names match build_double_pulse_netlist()
one-for-one). Pure-matplotlib line drawing (full manual coordinate control) rather than a
schematic-capture library, styled as a rectangular power/gate-loop layout.

Outputs reports/figures/dpt_schematic.pdf and .png.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrow

PROJECT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT / "reports" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LW = 1.6


def line(ax, x0, y0, x1, y1, **kw):
    ax.plot([x0, x1], [y0, y1], color="black", linewidth=LW, **kw)


def dot(ax, x, y, r=0.045):
    ax.add_patch(plt.Circle((x, y), r, color="black", zorder=5))


def ground(ax, x, y):
    line(ax, x, y, x, y - 0.25)
    for i, w in enumerate([0.22, 0.14, 0.06]):
        yy = y - 0.25 - i * 0.09
        line(ax, x - w, yy, x + w, yy)


def resistor(ax, x0, y0, x1, y1, label=None, label_side="left", n=6):
    """Zig-zag resistor between two points (must be axis-aligned: horizontal or vertical)."""
    if abs(x1 - x0) > abs(y1 - y0):  # horizontal
        length = x1 - x0
        seg = length / (n + 1)
        pts_x = [x0 + seg * 0.5]
        pts_y = [y0]
        for i in range(n):
            pts_x.append(x0 + seg * (i + 1))
            pts_y.append(y0 + (0.12 if i % 2 == 0 else -0.12))
        pts_x.append(x1 - seg * 0.5)
        pts_y.append(y1)
        xs = [x0] + pts_x + [x1]
        ys = [y0] + pts_y + [y1]
        ax.plot(xs, ys, color="black", linewidth=LW)
        if label:
            ax.text((x0 + x1) / 2, y0 + (0.32 if label_side == "top" else -0.32), label,
                    ha="center", va="center", fontsize=9)
    else:  # vertical
        length = y1 - y0
        seg = length / (n + 1)
        pts_x = [x0]
        pts_y = [y0 + seg * 0.5]
        for i in range(n):
            pts_y.append(y0 + seg * (i + 1))
            pts_x.append(x0 + (0.12 if i % 2 == 0 else -0.12))
        pts_x.append(x1)
        pts_y.append(y1 - seg * 0.5)
        xs = [x0] + pts_x + [x1]
        ys = [y0] + pts_y + [y1]
        ax.plot(xs, ys, color="black", linewidth=LW)
        if label:
            ax.text(x0 + (0.4 if label_side == "right" else -0.4), (y0 + y1) / 2, label,
                    ha="center", va="center", fontsize=9, rotation=90)


def inductor(ax, x0, y0, x1, y1, label=None, label_side="top", n=5):
    """Coil (series of bumps) between two axis-aligned points."""
    horizontal = abs(x1 - x0) > abs(y1 - y0)
    length = (x1 - x0) if horizontal else (y1 - y0)
    seg = length / n
    t = np.linspace(0, 1, 200)
    for i in range(n):
        theta = np.pi * t
        bump = 0.16 * np.sin(theta)
        if horizontal:
            xs = x0 + seg * i + seg * t
            ys = y0 + bump
        else:
            ys = y0 + seg * i + seg * t
            xs = x0 + bump
        ax.plot(xs, ys, color="black", linewidth=LW)
    if label:
        if horizontal:
            ax.text((x0 + x1) / 2, y0 + (0.38 if label_side == "top" else -0.38), label,
                    ha="center", va="center", fontsize=9)
        else:
            ax.text(x0 + (0.4 if label_side == "right" else -0.4), (y0 + y1) / 2, label,
                    ha="center", va="center", fontsize=9, rotation=90)


def capacitor(ax, x0, y0, x1, y1, label=None, label_side="left"):
    """Two parallel plates, vertical branch only (x0==x1)."""
    ym = (y0 + y1) / 2
    line(ax, x0, y0, x0, ym - 0.08)
    line(ax, x0 - 0.22, ym - 0.08, x0 + 0.22, ym - 0.08)
    line(ax, x0 - 0.22, ym + 0.08, x0 + 0.22, ym + 0.08)
    line(ax, x0, ym + 0.08, x1, y1)
    if label:
        ax.text(x0 + (0.4 if label_side == "right" else -0.4), ym, label,
                ha="center", va="center", fontsize=9)


def vsource(ax, x, y, label=None, r=0.28, label_dx=0.5):
    circle = plt.Circle((x, y), r, fill=False, linewidth=LW)
    ax.add_patch(circle)
    ax.text(x, y + r * 0.45, "+", ha="center", va="center", fontsize=10)
    ax.text(x, y - r * 0.45, "−", ha="center", va="center", fontsize=10)
    if label:
        ax.text(x + label_dx, y, label, ha="left", va="center", fontsize=9)
    return r


def diode(ax, x0, y0, x1, y1, label=None, forward="right"):
    """Diode symbol on a horizontal segment; forward='right' means it conducts left->right
    (anode on the left)."""
    xm = (x0 + x1) / 2
    h = 0.16
    line(ax, x0, y0, xm - 0.1, y0)
    if forward == "right":
        tri = plt.Polygon([(xm - 0.1, y0 - h), (xm - 0.1, y0 + h), (xm + 0.1, y0)],
                           closed=True, fill=True, color="black")
        ax.add_patch(tri)
        line(ax, xm + 0.1, y0 - h, xm + 0.1, y0 + h)
    else:
        tri = plt.Polygon([(xm + 0.1, y0 - h), (xm + 0.1, y0 + h), (xm - 0.1, y0)],
                           closed=True, fill=True, color="black")
        ax.add_patch(tri)
        line(ax, xm - 0.1, y0 - h, xm - 0.1, y0 + h)
    line(ax, xm + 0.1, y0, x1, y1)
    if label:
        ax.text(xm, y0 + 0.32, label, ha="center", va="center", fontsize=9)


def nfet(ax, x, y_bottom, y_top, label=None, gate_y_frac=0.5, gate_len=0.5):
    """Simple vertical N-channel FET: drain lead from top, source lead from bottom, gate
    stub to the right at mid-height. (x, y_bottom)=source terminal, (x, y_top)=drain terminal."""
    body_h = y_top - y_bottom
    bar_half = body_h * 0.22
    y_mid = y_bottom + gate_y_frac * body_h

    line(ax, x, y_top, x, y_mid + bar_half)
    line(ax, x - 0.18, y_mid + bar_half, x - 0.18, y_mid - bar_half)  # channel bar (drain side)
    line(ax, x - 0.18, y_mid + 0.05, x, y_mid + 0.05)
    line(ax, x - 0.18, y_mid - 0.05, x, y_mid - 0.05)
    line(ax, x, y_mid - bar_half, x, y_bottom)
    # gate plate + stub
    line(ax, x - 0.30, y_mid - bar_half, x - 0.30, y_mid + bar_half)
    line(ax, x - 0.30, y_mid, x - 0.30 - gate_len, y_mid)
    # arrow on source lead indicating N-channel (current out of source)
    ax.add_patch(FancyArrow(x - 0.16, y_mid - bar_half * 0.55, 0.10, -0.10,
                             width=0.0, head_width=0.09, head_length=0.09, color="black"))
    if label:
        ax.text(x + 0.35, y_mid, label, ha="left", va="center", fontsize=9)
    return {
        "drain": (x, y_top),
        "source": (x, y_bottom),
        "gate": (x - 0.30 - gate_len, y_mid),
    }


# ============================================================================
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(-1.5, 11)
ax.set_ylim(-2.5, 9)
ax.set_aspect("equal")
ax.axis("off")

# --- Coordinates -------------------------------------------------------
Y_BUS = 8.0
Y_GND = -1.5
X_VDC = 0.0
X_CDC = 1.6
X_LLOOP0 = 2.6
X_LLOOP1 = 4.4
X_A = 4.4
X_LOAD = 7.6
Y_SW = 4.0
Y_SWQL = 2.2
Y_QL_TOP = Y_SWQL
Y_QL_BOT = 0.4

# --- Vdc + bus rail ------------------------------------------------------
vsource(ax, X_VDC, (Y_BUS + Y_GND) / 2, label=None)
line(ax, X_VDC, (Y_BUS + Y_GND) / 2 + 0.28, X_VDC, Y_BUS)
line(ax, X_VDC, (Y_BUS + Y_GND) / 2 - 0.28, X_VDC, Y_GND)
ax.text(X_VDC - 0.55, (Y_BUS + Y_GND) / 2, "Vdc\n75V", ha="center", va="center", fontsize=9)
line(ax, X_VDC, Y_BUS, X_LLOOP1, Y_BUS)
dot(ax, X_CDC, Y_BUS)
ax.text(X_VDC + 0.15, Y_BUS + 0.2, "VBUS", fontsize=9)

# --- Cdc + Resr branch -----------------------------------------------------
capacitor(ax, X_CDC, Y_BUS, X_CDC, Y_BUS - 1.3, label="Cdc\n100uF")
line(ax, X_CDC, Y_BUS - 1.3, X_CDC, Y_BUS - 1.7)
resistor(ax, X_CDC, Y_BUS - 1.7, X_CDC, Y_BUS - 2.7, label="Resr\n10mOhm", label_side="right")
line(ax, X_CDC, Y_BUS - 2.7, X_CDC, Y_GND)

# --- ground rail ------------------------------------------------------
line(ax, X_VDC, Y_GND, X_A + 0.1, Y_GND)
ground(ax, X_VDC, Y_GND)

# --- Lloop, node A ----------------------------------------------------
inductor(ax, X_LLOOP0, Y_BUS, X_LLOOP1, Y_BUS, label="Lloop", n=5)
dot(ax, X_A, Y_BUS)
ax.text(X_A, Y_BUS + 0.28, "A", ha="center", fontsize=10, fontweight="bold")
line(ax, X_A, Y_BUS, X_A, Y_SW + 1.0)

# --- XQH (held off), from A down to SW ---------------------------------
qh = nfet(ax, X_A, Y_SW, Y_SW + 1.0, label="XQH\n(held OFF, Vgh=0V)")
dot(ax, X_A, Y_SW)
ax.text(X_A - 0.35, Y_SW - 0.05, "SW", ha="right", fontsize=10, fontweight="bold")

# Vgh: gate to source (=SW)
gx, gy = qh["gate"]
gx -= 0.9  # extra clearance so its label doesn't crowd Vsense_id or Rg_on
line(ax, qh["gate"][0], gy, gx, gy)
line(ax, gx, gy, gx, Y_SW - 0.8)
vsource(ax, gx, Y_SW - 0.8)
ax.text(gx - 0.55, Y_SW - 0.8, "Vgh\n0V", ha="center", va="center", fontsize=9)
line(ax, gx, Y_SW - 0.8 - 0.28, gx, Y_SW - 1.6)
line(ax, gx, Y_SW - 1.6, X_A, Y_SW - 1.6)
line(ax, X_A, Y_SW - 1.6, X_A, Y_SW)

# --- Lload branch: A -> SW, parallel to XQH -----------------------------
line(ax, X_A, Y_BUS, X_LOAD, Y_BUS)
inductor(ax, X_LOAD, Y_BUS, X_LOAD, Y_SW + 1.4, label="Lload\n(sets I_test)", label_side="right")
line(ax, X_LOAD, Y_SW + 1.4, X_LOAD, Y_SW)
line(ax, X_LOAD, Y_SW, X_A, Y_SW)

# --- Vsense_id, SWQL, XQL (DUT) -----------------------------------------
line(ax, X_A, Y_SW, X_A, Y_SW - 0.3)
vsource(ax, X_A, Y_SWQL + (Y_SW - 0.3 - Y_SWQL) / 2 + 0.3, label="Vsense_id\n0V (ammeter)", label_dx=0.35)
line(ax, X_A, Y_SW - 0.3 - 0.56, X_A, Y_SWQL)
dot(ax, X_A, Y_SWQL)
ax.text(X_A - 0.35, Y_SWQL, "SWQL", ha="right", fontsize=10, fontweight="bold")

ql = nfet(ax, X_A, Y_QL_BOT, Y_QL_TOP, label="XQL = DUT")
line(ax, X_A, Y_QL_BOT, X_A, Y_GND)
ground(ax, X_A, Y_GND)

# --- Gate drive network for XQL -----------------------------------------
glx, gly = ql["gate"]
X_GL = glx
dot(ax, X_GL, gly)
ax.text(X_GL - 0.15, gly - 0.3, "GL", ha="center", fontsize=9)

X_DRV = X_GL - 3.2
Y_ON = gly + 0.9
Y_OFF = gly - 0.9

line(ax, X_GL, gly, X_GL, Y_ON)
resistor(ax, X_GL - 1.6, Y_ON, X_GL, Y_ON, label="Rg_on", label_side="top")
diode(ax, X_DRV, Y_ON, X_GL - 1.6, Y_ON, label="Don (anode=DRV)", forward="right")

line(ax, X_GL, gly, X_GL, Y_OFF)
diode(ax, X_GL - 1.6, Y_OFF, X_GL, Y_OFF, label="Doff (anode=GL)", forward="left")
resistor(ax, X_DRV, Y_OFF, X_GL - 1.6, Y_OFF, label="Rg_off", label_side="top")

line(ax, X_DRV, Y_ON, X_DRV, Y_OFF)
vsource(ax, X_DRV - 0.6, gly, label=None, r=0.32)
line(ax, X_DRV - 0.6, gly + 0.32, X_DRV - 0.6, Y_ON)
line(ax, X_DRV - 0.6, Y_ON, X_DRV, Y_ON)
line(ax, X_DRV - 0.6, gly - 0.32, X_DRV - 0.6, Y_OFF)
line(ax, X_DRV - 0.6, Y_OFF, X_DRV, Y_OFF)
ax.text(X_DRV - 0.6 - 0.45, gly, "Vdrv\nPWL\ndouble\npulse", ha="right", va="center", fontsize=9)

ax.set_title(
    "Double-pulse test netlist (src/spb_bb/ltspice/double_pulse.py) -- node names match the\n"
    "generated LTSpice deck exactly",
    fontsize=10,
)

fig.tight_layout()
fig.savefig(OUT_DIR / "dpt_schematic.pdf")
fig.savefig(OUT_DIR / "dpt_schematic.png", dpi=200)
print("Saved", OUT_DIR / "dpt_schematic.pdf")

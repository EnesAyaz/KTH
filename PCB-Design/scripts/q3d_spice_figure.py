"""
Figure of the simulation validation with the Q3D copper (simulation/bb_q3d/revb_q3d_spice.py):
  (a) low-side turn-off, load-test board: drain current and v_DS of the four low-side devices
  (b) low-side turn-on, load-test board: drain currents, v_DS of the high-side devices
  (c) high-side v_DS at the low-side turn-on: load-test / DPT board (Q3D) and the lumped reference
  (d) turn-on / turn-off energy per device of every cell, Q3D vs lumped

    python scripts/q3d_spice_figure.py           -> reports/slides/revb_pptx/img/q3d_spice.png
    PAPER=1 python scripts/q3d_spice_figure.py   -> reports/paper/figures/revb/q3d_spice.pdf
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "simulation", "dpt"))
import eth_style as es  # noqa: E402

es.setup()
import matplotlib.pyplot as plt  # noqa: E402
from plot_dpt import read_raw  # noqa: E402

PAPER = os.environ.get("PAPER", "") == "1"
_k = 1.55 if PAPER else 1.0
plt.rcParams.update({"font.size": 9.5 * _k, "axes.labelsize": 9.5 * _k, "xtick.labelsize": 8.5 * _k,
                     "ytick.labelsize": 8.5 * _k, "legend.fontsize": 7.5 * _k, "axes.titlesize": 9.5 * _k,
                     "lines.linewidth": 1.3 * (1.2 if PAPER else 1.0)})
C = es.C
SP = os.path.join(ROOT, "simulation", "bb_spice")
Q = json.load(open(os.path.join(ROOT, "reports", "slides", "data", "q3d_spice_numbers.json")))
T1 = 0.5e-6 + 10.667e-6
T2 = T1 + 1e-6
CELL = [C["blue"], C["red"], C["green"], C["purple"]]


def trace(path, step=0):
    names, steps = read_raw(path)
    arr = steps[step]
    idx = {n.lower(): i for i, n in enumerate(names)}

    def g(n):
        return arr[:, idx[n.lower()]]
    return arr[:, 0], g


def window(t, t0, a, b):
    m = (t > t0 + a) & (t < t0 + b)
    return m, (t[m] - t0) * 1e9


def panel(ax, s):
    ax.text(0.5, -0.30, s, transform=ax.transAxes, fontsize=9.5 * _k, fontweight="bold", ha="center", va="top")


tl, gl = trace(os.path.join(SP, "REVB_Q3D_load.raw"))
fig, axs = plt.subplots(1, 4, figsize=(15.5, 3.6))

# (a) turn-off, load-test board
ax = axs[0]
m, x = window(tl, T1, -5e-9, 25e-9)
ax2 = ax.twinx()
for c in range(4):
    ax.plot(x, gl("I(VIL%d)" % (c + 1))[m], color=CELL[c], label="cell %d" % (c + 1))
    ax2.plot(x, gl("V(dL%d)" % (c + 1))[m] - gl("V(QL_S_%d)" % (c + 1))[m], color=CELL[c], ls="--", lw=1.0 * _k)
ax.set_xlabel("time (ns)")
ax.set_ylabel("$i_\\mathrm{D}$ (A), solid")
ax2.set_ylabel("$v_\\mathrm{DS}$ (V), dashed")
ax2.axhline(90, color="k", lw=0.8, ls=":")
ax.set_ylim(-10, 100)
ax2.set_ylim(-10, 100)
ax.legend(loc="center left", frameon=False)
panel(ax, "(a)")

# (b) turn-on, load-test board
ax = axs[1]
m, x = window(tl, T2, -5e-9, 25e-9)
ax2 = ax.twinx()
for c in range(4):
    ax.plot(x, gl("I(VIL%d)" % (c + 1))[m], color=CELL[c])
    ax2.plot(x, gl("V(dH%d)" % (c + 1))[m] - gl("V(QH_S_%d)" % (c + 1))[m], color=CELL[c], ls="--", lw=1.0 * _k)
ax.set_xlabel("time (ns)")
ax.set_ylabel("low-side $i_\\mathrm{D}$ (A), solid")
ax2.set_ylabel("high-side $v_\\mathrm{DS}$ (V), dashed")
ax2.axhline(90, color="k", lw=0.8, ls=":")
ax.set_ylim(-10, 150)
ax2.set_ylim(-10, 100)
panel(ax, "(b)")

# (c) high-side v_DS at the low-side turn-on, Q3D boards vs lumped (cell with the highest peak)
ax = axs[2]
lum = os.path.join(SP, "REVB_lumped_ref.raw")
cases = [("REVB_Q3D_load.raw", "load", "load-test, Q3D", C["blue"], "-"),
         ("REVB_Q3D_dpt.raw", "dpt", "DPT, Q3D", C["red"], "-"),
         ("REVB_Q3D_dpt_rg3.raw", "dpt_rg3", "DPT, Q3D, $R_\\mathrm{g,on}$ 3 $\\Omega$", C["red"], ":")]
for f, key, lab, col, ls in cases:
    if not os.path.exists(os.path.join(SP, f)) or key not in Q:
        continue
    t, g = trace(os.path.join(SP, f))
    c = int(np.argmax([cc["VHpk"] for cc in Q[key]["cells"]])) + 1
    m, x = window(t, T2, -5e-9, 25e-9)
    ax.plot(x, g("V(dH%d)" % c)[m] - g("V(QH_S_%d)" % c)[m], color=col, ls=ls, label=lab)
for s, lab, ls in ((0, "lumped %.2f nH" % Q["lumped"]["loop_nH"][0], "--"), (1, "lumped %.2f nH" % Q["lumped"]["loop_nH"][1], "-.")):
    t, g = trace(lum, s)
    m, x = window(t, T2, -5e-9, 25e-9)
    ax.plot(x, g("V(dH)")[m] - g("V(SW)")[m], color="k", ls=ls, lw=1.0 * _k, label=lab)
ax.axhline(90, color="k", lw=0.8, ls=":")
ax.set_ylim(0, 100)
ax.set_xlabel("time (ns)")
ax.set_ylabel("high-side $v_\\mathrm{DS}$ (V)")
ax.legend(loc="center left", frameon=False)
panel(ax, "(c)")

# (d) energies per device per cell
ax = axs[3]
w = 0.18
for j, (key, col, lab) in enumerate((("load", C["blue"], "load-test"), ("dpt", C["red"], "DPT"))):
    if key not in Q:
        continue
    eon = [c["Eon_uJ"] for c in Q[key]["cells"]]
    eoff = [c["Eoff_uJ"] for c in Q[key]["cells"]]
    xs = np.arange(4) + (j - 0.5) * 2 * w
    ax.bar(xs - w / 2, eon, w, color=col, label="$E_\\mathrm{on}$, " + lab)
    ax.bar(xs + w / 2, eoff, w, color=col, alpha=0.45, hatch="//", label="$E_\\mathrm{off}$, " + lab)
for v, ls, lab in ((Q["lumped"]["Eon_uJ"][0], "--", "lumped %.2f nH" % Q["lumped"]["loop_nH"][0]),
                   (Q["lumped"]["Eon_uJ"][1], "-.", "lumped %.2f nH" % Q["lumped"]["loop_nH"][1])):
    ax.axhline(v, color="k", ls=ls, lw=1.0 * _k, label=lab)
ax.axhline(Q["lumped"]["Eoff_uJ"][0], color="k", ls="--", lw=1.0 * _k)
ax.set_xticks(range(4))
ax.set_xticklabels(["cell %d" % c for c in range(1, 5)])
ax.set_ylabel("energy per device ($\\mu$J)")
ax.set_ylim(0, 58)
ax.legend(loc="upper center", ncol=2, frameon=False, fontsize=6.3 * _k)
panel(ax, "(d)")

fig.tight_layout(w_pad=1.2)
if PAPER:
    out = os.path.join(ROOT, "reports", "paper", "figures", "revb", "q3d_spice.pdf")
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02)
else:
    out = os.path.join(ROOT, "reports", "slides", "revb_pptx", "img", "q3d_spice.png")
    fig.savefig(out, dpi=220)
print("wrote", out)

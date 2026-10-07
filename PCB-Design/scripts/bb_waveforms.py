"""
Switching waveforms of the building block at the rated peak current (step IPK = 141 A of BB_energy_sweep).

    python scripts/bb_waveforms.py  -> reports/building-block/figures/waveforms_141A.pdf|png
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "simulation", "dpt"))
from plot_dpt import read_raw  # noqa: E402

RAW = os.path.join(ROOT, "simulation", "bb_spice", "BB_energy_sweep.raw")
FIG = os.path.join(ROOT, "reports", "building-block", "figures")
STEP = 5                     # IPK list 10 30 60 90 120 141 160 -> index 5 = 141 A
T1 = 0.5e-6 + 10.667e-6     # TSTART + TON1
T2 = T1 + 1e-6

names, steps = read_raw(RAW)
col = {n.lower(): i for i, n in enumerate(names)}
a = steps[STEP]
t = a[:, 0]


def s(n):
    return a[:, col[n.lower()]]


fig, ax = plt.subplots(3, 2, figsize=(11, 7.5), sharex="col")
for j, (tc, title) in enumerate(((T1, "QL turn-off at 139 A"), (T2, "QL turn-on at 139 A"))):
    m = (t > tc - 5e-9) & (t < tc + 45e-9)
    tn = (t[m] - tc) * 1e9
    ax[0, j].plot(tn, s("V(QL_D_L)")[m] - s("V(QL_S_L)")[m], label="QL_L VDS")
    ax[0, j].plot(tn, s("V(QH_D_L)")[m] - s("V(QH_S_L)")[m], label="QH_L VDS")
    ax[0, j].axhline(90, color="grey", ls=":", lw=1)
    ax[1, j].plot(tn, s("I(VILL)")[m], label="QL_L drain current")
    ax[1, j].plot(tn, s("I(VILR)")[m], "--", label="QL_R drain current")
    ax[2, j].plot(tn, s("V(gtLL)")[m] - s("V(QL_S_L)")[m], label="QL_L VGS")
    ax[2, j].plot(tn, s("V(gtLR)")[m] - s("V(QL_S_R)")[m], "--", label="QL_R VGS")
    ax[2, j].plot(tn, s("V(gtHL)")[m] - s("V(QH_S_L)")[m], label="QH_L VGS (off)")
    ax[2, j].axhline(0.8, color="grey", ls=":", lw=1)
    ax[0, j].set_title(title)
    ax[2, j].set_xlabel("time from gate command [ns]")
for i, lab in enumerate(("VDS [V]", "drain current [A]", "VGS at die [V]")):
    ax[i, 0].set_ylabel(lab)
    for j in range(2):
        ax[i, j].grid(alpha=0.3)
        ax[i, j].legend(fontsize=7, loc="best")
fig.suptitle("Building block, 75 V, Rg_on 2 ohm / Rg_off 0 ohm, Q3D parasitics (left and right FETs overlap)", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "waveforms_141A.pdf"))
fig.savefig(os.path.join(FIG, "waveforms_141A.png"), dpi=130)
print("ok")

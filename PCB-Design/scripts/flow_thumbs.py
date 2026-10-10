"""
Small thumbnail plots for the design-procedure flowchart (Fig. 2 of the paper).

    python scripts/flow_thumbs.py  -> reports/paper/figures/thumbs/*.png
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import eth_style as es  # noqa: E402

es.setup()
import matplotlib.pyplot as plt  # noqa: E402

C = es.C
OUT = os.path.join(ROOT, "reports", "paper", "figures", "thumbs")
os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(ROOT, "reports", "building-block", "data")
rs = json.load(open(os.path.join(DATA, "results.json")))
sz = json.load(open(os.path.join(DATA, "sizing.json")))


def thumb(name, fn, w=1.25, h=0.85):
    fig, ax = plt.subplots(figsize=(w, h))
    fn(ax)
    ax.tick_params(labelsize=5, length=1.5, pad=1)
    ax.xaxis.label.set_size(5.5)
    ax.yaxis.label.set_size(5.5)
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=300, bbox_inches="tight", pad_inches=0.01)
    plt.close(fig)


DEV = [(100, 0.75, 1800), (100, 1.4, 1700), (100, 1.7, 1420), (100, 2.4, 860), (200, 3.5, 1200), (200, 6.0, 690),
       (200, 6.0, 960), (350, 55, 125), (650, 25, 205), (650, 140, 35)]
KC = {100: C["red"], 200: C["blue"], 350: C["green"], 650: C["yellow"]}


def devices(ax):
    cc = np.logspace(1.3, 3.5, 20)
    for tau in (1, 5):
        ax.loglog(cc, tau / cc * 1e3, color="0.6", lw=0.5, ls="--")
    for v, r, c in DEV:
        ax.loglog(c, r, "o", color=KC[v], ms=2.5, mec="k", mew=0.3)
    ax.set_xlabel(r"$C_\mathrm{oss,tr}$")
    ax.set_ylabel(r"$R_\mathrm{DS(on)}$")
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.minorticks_off()


def sharing(ax):
    sys.path.insert(0, os.path.join(ROOT, "simulation", "sharing"))
    import plot_sharing as psh
    col, steps = psh.read_raw(os.path.join(ROOT, "simulation", "sharing", "paper_run", "Sharing_paper.raw"))
    T2 = 0.5e-6 + 5e-6 * 120 / 75 + 1e-6
    a = steps[2]
    t = a[:, 0]
    m = (t > T2 - 2e-9) & (t < T2 + 20e-9)
    ax.plot((t[m] - T2) * 1e9, a[m, col["i(ld1)"]], color=C["blue"], lw=0.8)
    ax.plot((t[m] - T2) * 1e9, a[m, col["i(ld2)"]], color=C["red"], lw=0.8, ls="--")
    ax.set_xlabel("$t$")
    ax.set_ylabel("$i_D$")
    ax.set_xticklabels([])
    ax.set_yticklabels([])


def npar(ax):
    ns = [1, 2, 3, 4]
    ax.plot(ns, [17.5, 12.5, 11.2, 10.7], "-o", color=C["red"], ms=2.5, lw=0.8)
    ax.axhline(13.3, color="k", ls="--", lw=0.6)
    ax.set_xticks(ns)
    ax.set_xlabel("$n$")
    ax.set_ylabel(r"$P_\mathrm{loss}$")
    ax.set_yticklabels([])


def dclink(ax):
    fs = np.linspace(15, 200, 100)
    n_v = 77 * 50 / fs / 3.0
    ax.plot(fs, n_v, color=C["blue"], lw=0.8)
    ax.axhline(11.5, color=C["red"], lw=0.8)
    ax.plot(fs, np.maximum(n_v, 11.5), "k", lw=1.2)
    ax.set_ylim(0, 60)
    ax.set_xlabel(r"$f_\mathrm{sw}$")
    ax.set_ylabel(r"$n_C$")
    ax.set_xticklabels([])
    ax.set_yticklabels([])


def switching(ax):
    sl = json.load(open(os.path.join(DATA, "slow_switching.json")))["cases"]
    for k, c in (("2/0", "k"), ("2/5", C["yellow"]), ("2/10", C["red"])):
        ax.plot([x["I"] for x in sl[k]], [x["Eoff"] * 1e6 for x in sl[k]], "-", color=c, lw=0.8)
    ax.set_xlabel("$I$")
    ax.set_ylabel(r"$E_\mathrm{off}$")
    ax.set_xticklabels([])
    ax.set_yticklabels([])


def losses(ax):
    lf = rs["loss_vs_f"]
    f = np.array([x["f"] for x in lf]) / 1e3
    parts = [("cond", C["blue"]), ("cu", C["green"]), ("cu_hf", C["cyan"]), ("sw", C["red"]), ("dead", C["yellow"]),
             ("cap", C["purple"])]
    ax.stackplot(f, *[np.array([x[k] for x in lf]) for k, _ in parts], colors=[c for _, c in parts], lw=0)
    ax.axhline(sz["P_loss_budget"], color="k", ls="--", lw=0.6)
    ax.set_xlabel(r"$f_\mathrm{sw}$")
    ax.set_ylabel(r"$P_\mathrm{loss}$")
    ax.set_xticklabels([])
    ax.set_yticklabels([])


for name, fn in (("devices", devices), ("sharing", sharing), ("npar", npar), ("dclink", dclink),
                 ("switching", switching), ("losses", losses)):
    thumb(name, fn)
    print("wrote", name)

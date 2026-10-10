"""
All data figures of the IEEE paper in one consistent style (scripts/eth_style.py):
  fig_devices    (a) R_DS(on) vs C_oss,tr of off-the-shelf GaN, (b) radar: 100 / 200 / 650 V SPB building blocks
  fig_parasitics (a) loop inductance vs dielectric, (b) gate-resistor window, (c) current-sharing sensitivity
  fig_switching  (a) E_off and overlap formula, (b) E_on, (c) turn-off dv/dt (slow-switching study)
  fig_losses     (a) R(f)/R_dc of the board, (b) loss vs f_sw, (c) loss breakdown at 50 kHz
  fig_thermal    (a)-(d) Icepak temperature maps

    python scripts/paper_figures_eth.py  -> reports/paper/figures/fig_*.pdf
"""
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import eth_style as es  # noqa: E402

es.setup()
import matplotlib.pyplot as plt  # noqa: E402

OUT = os.path.join(ROOT, "reports", "paper", "figures")
os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(ROOT, "reports", "building-block", "data")
rs = json.load(open(os.path.join(DATA, "results.json")))
sz = json.load(open(os.path.join(DATA, "sizing.json")))
C = es.C


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".pdf"))
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=200)
    plt.close(fig)
    print("wrote", name)


# =====================================================================================================================
# 1. devices: scatter + radar
DEV = [("EPC2361", 100, 0.75, 90, 50), ("EPC2302", 100, 1.4, 85, 50), ("EPC2071", 100, 1.7, 71, 50),
       ("IGC033S10S1", 100, 2.4, 43, 50), ("EPC2304", 200, 3.5, 120, 100), ("EPC2215", 200, 6.0, 69, 100),
       ("EPC2034C", 200, 6.0, 96, 100), ("EPC2050", 350, 55.0, 35, 280), ("IGT65R025D2", 650, 25.0, 82, 400),
       ("IGT65R140D2", 650, 140.0, 14, 400)]
VM = {100: 75.0, 200: 150.0, 350: 240.0, 650: 400.0}
KC = {100: C["red"], 200: C["blue"], 350: C["green"], 650: C["yellow"]}
I, F, VB = 100.0, 50e3, 1200.0
fig = plt.figure(figsize=(es.TXT_W, 2.1))
ax = fig.add_axes([0.065, 0.17, 0.42, 0.78])
cc = np.logspace(1.2, 3.65, 40)
for tau in (1, 2, 5, 10):
    ax.loglog(cc, tau / cc * 1e3, color="0.55", lw=0.5, ls=(0, (4, 2)))
    ax.text(19, tau / 19 * 1e3 * 1.12, r"$\tau$ = %g ps" % tau, rotation=-27, fontsize=6, color="0.35")
for pn, v, r, q, vt in DEV:
    ctr = q / vt * 1e3
    ax.loglog(ctr, r, "o" if pn.startswith("EPC") else "s", color=KC[v], mec="k", mew=0.4, ms=4.2)
    off = {"IGC033S10S1": (-4, -7, "right"), "EPC2215": (-4, -6, "right"), "EPC2034C": (4, 4, "left"),
           "EPC2071": (4, 3, "left")}.get(pn, (4, -2, "left"))
    ax.annotate(pn, (ctr, r), textcoords="offset points", xytext=off[:2], ha=off[2], fontsize=5.8)
for v, lbl in ((100, "100 V"), (200, "200 V"), (350, "350 V"), (650, "650 V")):
    ax.plot([], [], "o", color=KC[v], mec="k", mew=0.4, label=lbl)
ax.legend(loc="upper right", ncol=2, columnspacing=0.8, handletextpad=0.3)
ax.set_xlim(15, 4000)
ax.set_ylim(0.4, 900)
ax.set_xlabel(r"$C_\mathrm{oss,tr}=Q_\mathrm{oss}/V_\mathrm{test}$ (pF)")
ax.set_ylabel(r"$R_\mathrm{DS(on)}$ (m$\Omega$)")
es.panel(ax, "(a)", dx=-0.13, dy=-0.12)

# radar: best device per class, normalized to the maximum of each axis
best = {}
for pn, v, r, q, vt in DEV:
    tau = r * q / vt
    if v in (100, 200, 650) and (v not in best or tau < best[v]["tau"]):
        n_mod = VB / VM[v]
        qv = q / vt * 1e-9 * VM[v]
        nopt = I * math.sqrt(r * 1e-3 / (F * qv * VM[v]))
        best[v] = dict(pn=pn, tau=tau, pmin=math.sqrt(tau), n_mod=n_mod, nopt=nopt, step=VM[v],
                       switches=n_mod * 6 * nopt, chip=n_mod * 6 * nopt)
axes_def = [("pmin", "min. semicond.\nloss"), ("nopt", "devices\nper switch"), ("n_mod", "no. of\nsubmodules"),
            ("step", "winding\nvoltage step"), ("switches", "no. of\ntransistors")]
ang = (np.linspace(0, 2 * np.pi, len(axes_def), endpoint=False) + np.pi / 2) % (2 * np.pi)
axr = fig.add_axes([0.69, 0.16, 0.24, 0.68], polar=True)
for v in (100, 200, 650):
    vals = np.array([best[v][k] / max(best[w][k] for w in best) for k, _ in axes_def])
    axr.plot(np.r_[ang, ang[0]], np.r_[vals, vals[0]], "-o", color=KC[v], lw=1.1, ms=3, label="%d V (%s)" % (v, best[v]["pn"]))
    axr.fill(np.r_[ang, ang[0]], np.r_[vals, vals[0]], color=KC[v], alpha=0.12)
axr.set_xticks(ang)
axr.set_thetalim(0, 2 * np.pi)
axr.set_xticklabels([t for _, t in axes_def], fontsize=6.3)
axr.set_ylim(0, 1.05)
axr.set_yticks([0.25, 0.5, 0.75, 1.0])
axr.set_yticklabels(["25%", "50%", "75%", "100%"], fontsize=5.5, color="0.4")
axr.tick_params(axis="x", pad=4)
axr.set_rlabel_position(126)
axr.grid(color="#bdbdbd", lw=0.4)
axr.legend(loc="upper left", bbox_to_anchor=(-0.95, 1.25), fontsize=6)
es.panel(axr, "(b)", dx=-0.95, dy=-0.10)
save(fig, "fig_devices")
print({v: {k: round(val, 2) if isinstance(val, float) else val for k, val in b.items()} for v, b in best.items()})

# =====================================================================================================================
# 2. parasitics: loop vs h, Rg window, sharing sensitivity
fig, axs = plt.subplots(1, 2, figsize=(es.COL_W, 1.75), gridspec_kw=dict(wspace=0.48))
ax = axs[0]
h = np.array([0.075, 0.1, 0.2])
Lq = np.array([0.30, 0.34, 0.50])
k_an = 4e-7 * math.pi * 10.0 / 9.0 * 1e-3 * 1e9
fit = np.polyfit(h, Lq, 1)
hh = np.linspace(0, 0.25, 50)
ax.fill_between(hh, k_an * hh, np.polyval(fit, hh), color=C["grey"], alpha=0.12, lw=0)
ax.plot(hh, np.polyval(fit, hh), color=C["red"], ls="--", lw=0.9)
ax.plot(h, Lq, "o", color=C["red"], mec="k", mew=0.4)
ax.plot(hh, k_an * hh, color=C["blue"])
es.tag(ax, 0.2, 0.58, "Q3D", C["red"], ha="right")
es.tag(ax, 0.235, 0.27, r"$\mu_0 h l/w$", C["blue"], ha="right")
ax.annotate("vias,\npads", xy=(0.03, 0.15), xytext=(0.012, 0.42), fontsize=5.8,
            arrowprops=dict(arrowstyle="->", lw=0.5))
ax.set_xlim(0, 0.25)
ax.set_ylim(0, 0.62)
ax.set_xlabel(r"L1–L2 dielectric $h$ (mm)")
ax.set_ylabel(r"$L_\mathrm{loop}$ per cell (nH)")
es.panel(ax, "(a)", dx=-0.32, dy=-0.17)

ax = axs[1]
CISS, CRSS = 3.599e-9, 13e-12
Lg = np.linspace(0.2, 10, 120) * 1e-9
dvdt = rs["rg_choice"]["dvdt_off"] * 1e9
ax.fill_between(Lg * 1e9, 2 * 0.707 * np.sqrt(Lg / CISS), 6, color=C["green"], alpha=0.13, lw=0)
ax.fill_between(Lg * 1e9, 0, 0.8 / (CRSS * dvdt), color=C["blue"], alpha=0.13, lw=0)
ax.plot(Lg * 1e9, 2 * 0.707 * np.sqrt(Lg / CISS), color=C["green"])
ax.axhline(0.8 / (CRSS * dvdt), color=C["blue"], lw=0.9)
ax.axhline(1.1 / (CRSS * dvdt), color=C["blue"], lw=0.7, ls="--")
ax.plot(1.7, 3.0, "*", color=C["red"], mec="k", mew=0.4, ms=8)
ax.plot(1.7, 0.8, "s", color=C["red"], mec="k", mew=0.4, ms=4)
es.tag(ax, 2.2, 3.25, "on: 2 $\\Omega$ ext.\n(3.0 $\\Omega$ total)", C["red"], va="bottom", fontsize=5.8)
es.tag(ax, 2.2, 0.2, "off: 0 $\\Omega$ ext. (0.8 total)", C["red"], va="bottom", fontsize=5.8)
es.tag(ax, 9.8, 5.1, r"$\zeta\geq0.707$", C["green"], ha="right")
es.tag(ax, 9.8, 1.45, "Miller limit", C["blue"], ha="right")
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.set_xlabel(r"gate loop $L_G$ (nH)")
ax.set_ylabel(r"total gate resistance ($\Omega$)")
es.panel(ax, "(b)", dx=-0.30, dy=-0.17)

save(fig, "fig_parasitics")

# =====================================================================================================================
# 3. switching / slow switching
sl = json.load(open(os.path.join(DATA, "slow_switching.json")))
res = sl["cases"]
VB75 = 75.0
cols = {"2/0": "k", "2/2": C["blue"], "2/5": C["yellow"], "2/10": C["red"], "10/2": C["green"], "10/10": C["purple"]}
fig, axs = plt.subplots(1, 3, figsize=(es.TXT_W, 1.75), gridspec_kw=dict(wspace=0.32))
ax = axs[0]
for k in ("2/0", "2/2", "2/5", "2/10"):
    Ii = [x["I"] for x in res[k]]
    ax.plot(Ii, [x["Eoff"] * 1e6 for x in res[k]], "-o", color=cols[k], ms=2.5)
    ax.plot(Ii, [0.5 * VB75 ** 2 * x["I"] / (x["dvdt_off"] * 1e9) * 1e6 for x in res[k]], ls="--", color=cols[k], lw=0.8)
for k, yy in (("2/0", 5.2), ("2/2", 24), ("2/5", 50), ("2/10", 86)):
    es.tag(ax, 161, yy, r"%s $\Omega$" % k.split("/")[1], cols[k], ha="left")
es.tag(ax, 12, 80, r"$R_\mathrm{g,off}$:", "k")
es.tag(ax, 12, 68, r"— LTspice" + "\n" + r"-- $V^2I/(2\,dv/dt)$", "0.25", va="top")
ax.set_xlim(0, 185)
ax.set_ylim(0, 100)
ax.set_xlabel(r"switched current $I$ (A)")
ax.set_ylabel(r"$E_\mathrm{off}$ ($\mu$J)")
es.panel(ax, "(a)", dx=-0.27, dy=-0.17)
ax = axs[1]
for k in ("2/0", "10/2"):
    Ii = [x["I"] for x in res[k]]
    e0 = min(x["Eon"] for x in res[k])
    ax.plot(Ii, [x["Eon"] * 1e6 for x in res[k]], "-o", color=cols[k], ms=2.5)
    ax.plot(Ii, [(e0 + 0.5 * VB75 ** 2 * x["i_on"] / (x["dvdt_on"] * 1e9)) * 1e6 for x in res[k]], "--", color=cols[k], lw=0.8)
    ax.plot(Ii, [(e0 + x["Evi_on"]) * 1e6 for x in res[k]], ":", color=cols[k], lw=1.0)
es.tag(ax, 120, 22, r"$R_\mathrm{g,on}$ = 2 $\Omega$", "k")
es.tag(ax, 6, 82, r"$R_\mathrm{g,on}$ = 10 $\Omega$", cols["10/2"], ha="left")
es.tag(ax, 5, 112, r"-- $E_\mathrm{on}(0)$ + $dv/dt$ term" + "\n" + r"$\cdots$ + $di/dt$ term", "0.25", va="top")
ax.set_xlim(0, 170)
ax.set_ylim(0, 125)
ax.set_xlabel(r"switched current $I$ (A)")
ax.set_ylabel(r"$E_\mathrm{on}$ ($\mu$J)")
es.panel(ax, "(b)", dx=-0.27, dy=-0.17)
ax = axs[2]
for k in ("2/0", "2/2", "2/5", "2/10"):
    ax.plot([x["I"] for x in res[k]], [x["dvdt_off"] for x in res[k]], "-o", color=cols[k], ms=2.5)
ce = np.median([x["I"] / (x["dvdt_off"] * 1e9) for x in res["2/0"]])
ii = np.linspace(0, 170, 30)
ax.plot(ii, ii / ce / 1e9, ":", color="0.3", lw=0.9)
es.tag(ax, 110, 30.5, r"$I/C_\mathrm{oss,tot}$", "0.3", ha="right")
for k, yy in (("2/0", 31.5), ("2/2", 15.6), ("2/5", 9.6), ("2/10", 5.9)):
    es.tag(ax, 165, yy, r"%s $\Omega$" % k.split("/")[1], cols[k], ha="left")
ax.set_xlim(0, 190)
ax.set_ylim(0, 36)
ax.set_xlabel(r"switched current $I$ (A)")
ax.set_ylabel(r"turn-off $dv/dt$ (V/ns)")
es.panel(ax, "(c)", dx=-0.27, dy=-0.17)
save(fig, "fig_switching")

# =====================================================================================================================
# 4. losses
import bb_copper_hf as cu  # noqa: E402

names, br, rl, src = cu.load_rl()
fig, axs = plt.subplots(1, 3, figsize=(es.TXT_W, 1.75), gridspec_kw=dict(width_ratios=[1, 1, 1.05], wspace=0.36))
ax = axs[0]
fr = np.logspace(2, 8, 150)
lab = [("DCP:QH_D_L", "dc+ to QH drain", C["red"]), ("DCN:QL_S_L", "dc$-$ to QL source", C["blue"]),
       ("AC:QH_S_L", "ac to QH source", C["yellow"]), ("DCP:CapB1P", "dc+ to bank", C["purple"])]
for kn, l_, c in lab:
    k = names.index(kn)
    r0 = rl(0)[0][k, k]
    ax.semilogx(fr, [rl(x)[0][k, k] / r0 for x in fr], color=c, label=l_)
ax.axvspan(50e3, 1e6, color=C["yellow"], alpha=0.12, lw=0)
ax.text(2.2e5, 30, r"$f_\mathrm{sw}$ harm.", ha="center", fontsize=6.3, color="0.3")
ax.set_yscale("log")
ax.set_ylim(0.9, 45)
ax.set_xlim(1e2, 1e8)
ax.set_xlabel(r"frequency $f$ (Hz)")
ax.set_ylabel(r"$R(f)/R_\mathrm{dc}$")
ax.legend(loc="lower right", fontsize=5.8)
es.panel(ax, "(a)", dx=-0.27, dy=-0.17)
ax = axs[1]
lf = rs["loss_vs_f"]
f = np.array([x["f"] for x in lf]) / 1e3
parts = [("cond", "conduction", C["blue"]), ("cu", "Cu, load", C["green"]), ("cu_hf", "Cu, harmonics", C["cyan"]),
         ("sw", "switching", C["red"]), ("dead", "dead time", C["yellow"]), ("cap", "MLCC", C["purple"]),
         ("gate", "gate", C["dred"])]
ax.stackplot(f, *[np.array([x[k] for x in lf]) for k, _, _ in parts], colors=[c for _, _, c in parts], alpha=0.85,
             edgecolor="k", lw=0.3)
ax.axhline(sz["P_loss_budget"], color="k", ls="--", lw=0.8)
es.tag(ax, 22, sz["P_loss_budget"] + 0.6, r"$\eta$ = 99.5 %", "k")
for txt, yy, col in (("conduction", 2.8, "w"), ("Cu, load", 7.2, "w"), ("Cu, harmonics", 9.4, "k"), ("switching", 11.3, "w")):
    ax.text(60, yy, txt, ha="center", va="center", fontsize=6.3, color=col)
ax.set_xlim(20, 100)
ax.set_ylim(0, 16)
ax.set_xlabel(r"switching frequency $f_\mathrm{sw}$ (kHz)")
ax.set_ylabel(r"loss per leg (W)")
es.panel(ax, "(b)", dx=-0.27, dy=-0.17)
ax = axs[2]
r50 = [x for x in lf if x["f"] == 50e3][0]
left = 0.0
for k, l_, c in parts:
    ax.barh(0, r50[k], left=left, color=c, edgecolor="k", lw=0.4, height=0.55, label=l_)
    left += r50[k]
ax.set_ylim(-0.6, 2.4)
ax.set_xlim(0, 14)
ax.set_yticks([])
ax.set_xlabel("loss per leg at 50 kHz (W)")
ax.grid(axis="y", visible=False)
ax.legend(loc="upper center", ncol=2, fontsize=6, columnspacing=0.8)
ax.text(r50["total"] + 0.2, 0, "%.1f W\n%.2f %%" % (r50["total"], 100 * r50["eta"]), va="center", fontsize=6.3)
es.panel(ax, "(c)", dx=-0.05, dy=-0.17)
save(fig, "fig_losses")

# =====================================================================================================================
# 5. thermal maps
import plot_icepak as pi  # noqa: E402

RES = os.path.join(ROOT, "simulation", "bb_icepak", "results")
fig, axs = plt.subplots(1, 4, figsize=(es.TXT_W, 1.75), gridspec_kw=dict(wspace=0.12))
panels = [("devices", "", "(a)"), ("board", "", "(b)"), ("devices", "_both", "(c)"), ("board", "_both", "(d)")]
for ax, (tg, suf, lb) in zip(axs, panels):
    xs, ys, T = pi.load(os.path.join(RES, "grid_%s%s.fld" % (tg, suf)))
    im = ax.imshow(T, origin="lower", extent=(xs[0], xs[-1], ys[0], ys[-1]), cmap="inferno", vmin=60, vmax=105,
                   aspect="equal")
    pi.outlines(ax)
    ax.invert_yaxis()
    ax.grid(False)
    ax.set_xticks([-10, 0, 10])
    ax.set_yticks([-10, 0, 10])
    ax.set_xlabel("$x$ (mm)")
    if lb == "(a)":
        ax.set_ylabel("$y$ (mm)")
    else:
        ax.set_yticklabels([])
    ax.text(0.03, 0.97, "max %.0f $^\\circ$C" % np.nanmax(T), transform=ax.transAxes, color="k", fontsize=6, va="top",
            bbox=dict(fc="w", ec="none", pad=0.8, alpha=0.85))
    es.panel(ax, lb, dx=-0.05 if lb != "(a)" else -0.30, dy=-0.2)
cb = fig.colorbar(im, ax=axs, fraction=0.012, pad=0.01)
cb.set_label(r"$T$ ($^\circ$C)")
cb.ax.tick_params(labelsize=6, direction="in")
cb.outline.set_linewidth(0.5)
save(fig, "fig_thermal")


# =====================================================================================================================
# 6. number of parallel devices: layout scaling, loss, drivers
import matplotlib.patches as mp  # noqa: E402

S = sz["spec"]
I_PK = sz["I_pk"]
pon, poff = np.array(rs["energy"]["fit_on"]), np.array(rs["energy"]["fit_off"])
th = np.linspace(0, np.pi, 4001)
i_abs = I_PK * np.sin(th)
P_CU = rs["P_cu"] + rs.get("P_cu_hf", 0.0)
P_OTHER = rs.get("P_cap_net", sz["P_cap_rated"])


def e_avg(n):
    e2 = np.polyval(pon, i_abs) + np.polyval(poff, i_abs)
    e0 = np.polyval(pon, 0) + np.polyval(poff, 0)
    return float(np.mean(e2 - e0 + e0 * n / 2))


def leg_loss(n, f):
    cond = S["I_rms"] ** 2 * S["Rds_25_typ"] * S["Rds_factor_100C"] / n
    sw = e_avg(n) * f
    dead = sz["P_dead_50k"] * f / 50e3
    gate = (sz["P_gate_50k"] + sz["P_ldo_50k"]) * f / 50e3 * n / 2
    return dict(cond=cond, sw=sw, tot=cond + sw + dead + gate + P_CU + P_OTHER, dev=(cond + sw + dead) / (2 * n))


DRV = {1: 1, 2: 1, 3: 2, 4: 2}
LEGS = 16 * 3
fig = plt.figure(figsize=(es.TXT_W, 1.75))
ax = fig.add_axes([0.0, 0.17, 0.30, 0.80])
ax.set_xlim(0, 10)
ax.set_ylim(-0.3, 8.2)
ax.axis("off")
ax.grid(False)
LAY = {1: "CD", 2: "CDC", 3: "CDC DC", 4: "CDC CDC"}
for n, row in LAY.items():
    y = 8 - 2 * n
    x = 1.6
    ax.text(0.0, y + 0.5, "$n$ = %d" % n, va="center", fontsize=7)
    for ch in row:
        if ch == " ":
            x += 0.35
            continue
        if ch == "C":
            ax.add_patch(mp.FancyBboxPatch((x, y), 1.0, 1.0, boxstyle="round,pad=0.02,rounding_size=0.08",
                                           fc=(*C["red"], 0.18), ec=C["red"], lw=0.6))
            ax.text(x + 0.5, y + 0.5, "QH\nQL", ha="center", va="center", fontsize=4.8, linespacing=0.9)
            x += 1.0
        else:
            ax.add_patch(mp.Rectangle((x + 0.12, y + 0.22), 0.56, 0.56, fc=(*C["green"], 0.35), ec=C["green"], lw=0.6))
            ax.text(x + 0.4, y + 0.5, "D", ha="center", va="center", fontsize=5.5)
            x += 0.8
    ax.text(9.95, y + 0.5, "%d driver%s" % (DRV[n], "s" if DRV[n] > 1 else ""), ha="right", va="center",
            fontsize=6.3, color=C["green"])
ax.text(-0.05, -0.75, "(a)", fontsize=7.5, fontweight="bold", transform=ax.transData)

ax = fig.add_axes([0.40, 0.21, 0.25, 0.74])
ns = np.array([1, 2, 3, 4])
for f, c, yl in ((20e3, C["blue"], None), (50e3, C["red"], None), (100e3, C["yellow"], None)):
    ax.plot(ns, [leg_loss(n, f)["tot"] for n in ns], "-o", color=c, ms=3)
    es.tag(ax, 4.1, leg_loss(4, f)["tot"] + 0.4, "%.0f kHz" % (f / 1e3), c)
ax.axhline(sz["P_loss_budget"], color="k", ls="--", lw=0.8)
es.tag(ax, 3.05, sz["P_loss_budget"] - 0.8, r"$\eta$ = 99.5 %", "k")
ax.axvspan(1.85, 2.15, color=C["green"], alpha=0.15, lw=0)
ax.set_xticks(ns)
ax.set_xlim(0.8, 5.0)
ax.set_ylim(8, 22)
ax.set_xlabel(r"EPC2361 per switch $n$")
ax.set_ylabel("loss per leg (W)")
es.panel(ax, "(b)", dx=-0.30, dy=-0.17)

ax = fig.add_axes([0.75, 0.21, 0.19, 0.74])
ax.bar(ns, [DRV[n] * LEGS for n in ns], color=(*C["green"], 0.55), edgecolor="k", lw=0.4, width=0.55)
ax.set_xticks(ns)
ax.set_xlim(0.4, 4.6)
ax.set_ylim(0, 120)
ax.set_xlabel(r"EPC2361 per switch $n$")
ax.set_ylabel("gate drivers per inverter")
ax.grid(axis="x", visible=False)
ax2 = ax.twinx()
ax2.plot(ns, [leg_loss(n, 50e3)["dev"] for n in ns], "-o", color=C["red"], ms=3)
ax2.set_ylim(0, 8)
ax2.set_ylabel("loss per transistor (W)", color=C["red"])
ax2.tick_params(axis="y", colors=C["red"])
ax2.grid(False)
es.panel(ax, "(c)", dx=-0.42, dy=-0.17)
save(fig, "fig_npar")
for n in ns:
    print("n=%d" % n, {k: round(v, 2) for k, v in leg_loss(n, 50e3).items()})

# =====================================================================================================================
# 7. DC link: capacitor count vs f, impedance, current and loss per capacitor
bank = sz["bank"]
fig, axs = plt.subplots(1, 3, figsize=(es.TXT_W, 1.75), gridspec_kw=dict(wspace=0.42))
ax = axs[0]
fs = np.linspace(10e3, 200e3, 200)
c_req = sz["C_eff_per_block_shared_uF"] * 1e-6 * 50e3 / fs
I_CAP = 2.5
n_v = np.maximum((c_req - bank["hf_n"] * bank["hf_C_eff_each"]) / bank["bulk_C_eff_each"], 0)
n_i = np.full_like(fs, sz["I_leg_hf_rated"] / I_CAP)
ax.fill_between(fs / 1e3, np.maximum(n_v, n_i), 80, color=C["green"], alpha=0.12, lw=0)
ax.plot(fs / 1e3, n_v, color=C["blue"])
ax.plot(fs / 1e3, n_i, color=C["red"])
ax.plot(50, bank["bulk_n"], "*", color="k", ms=8)
es.tag(ax, 20, 66, r"$C_v$: $\Delta v_\mathrm{pp}$ = 4 %", C["blue"])
es.tag(ax, 140, n_i[0] + 4, r"$C_i$: %.1f A per MLCC" % I_CAP, C["red"], ha="center")
es.tag(ax, 58, bank["bulk_n"] + 4, "24 selected", "k")
es.tag(ax, 150, 60, "feasible", C["green"], ha="center")
ax.set_xlim(10, 200)
ax.set_ylim(0, 80)
ax.set_xlabel(r"switching frequency $f_\mathrm{sw}$ (kHz)")
ax.set_ylabel(r"number of 10 $\mu$F 1210 MLCCs")
es.panel(ax, "(a)", dx=-0.30, dy=-0.17)

ax = axs[1]
fz = np.logspace(3, 8.3, 400)
w = 2 * np.pi * fz
PARTS = [("1210, 10 $\\mu$F", bank["bulk_C_eff_each"], bank["esr_bulk_each"], 0.5e-9, 1, C["blue"], "-"),
         ("0805, 1 $\\mu$F", bank["hf_C_eff_each"], bank["esr_hf_each"], 0.48e-9, 1, C["red"], "-"),
         ("24 $\\times$ 1210", bank["bulk_C_eff_each"], bank["esr_bulk_each"], 0.5e-9, 24, C["blue"], "--"),
         ("6 $\\times$ 0805 (cell)", bank["hf_C_eff_each"], bank["esr_hf_each"], 0.48e-9, 6, C["red"], "--")]
for lab, Cc, R, L, n, c, ls in PARTS:
    z = np.abs(R + 1 / (1j * w * Cc) + 1j * w * L) / n
    ax.loglog(fz, z * 1e3, color=c, ls=ls, label=lab)
ax.axvspan(50e3, 1e6, color=C["yellow"], alpha=0.12, lw=0)
ax.set_xlim(1e3, 2e8)
ax.set_ylim(0.05, 1e5)
ax.set_xlabel(r"frequency $f$ (Hz)")
ax.set_ylabel(r"$|Z|$ (m$\Omega$)")
ax.legend(loc="upper right", fontsize=5.6)
es.panel(ax, "(b)", dx=-0.30, dy=-0.17)

ax = axs[2]
cu = json.load(open(os.path.join(DATA, "copper_hf.json")))
case = [c_ for c_ in cu["cases"] if c_["mode"] == "SVM" and c_["M"] == 1.0 and c_["pf"] == 1.0][0]
grp = [("local_L", "0805\ncell L", 6), ("local_R", "0805\ncell R", 6), ("row1", "1210\nrow 1", 8),
       ("row2", "1210\nrow 2", 8), ("row3", "1210\nrow 3", 8)]
x = np.arange(len(grp))
ip = [case["cap_I_rms"][g] / n for g, _, n in grp]
pp = [case["cap_P"][g] / n * 1e3 for g, _, n in grp]
ax.bar(x, ip, color=[C["red"], C["red"], C["blue"], C["blue"], C["blue"]], alpha=0.75, edgecolor="k", lw=0.4, width=0.6)
ax.axhline(I_CAP, color="k", ls="--", lw=0.7)
es.tag(ax, -0.4, I_CAP + 0.15, "assumed 1210 rating", "k")
for xi, i_, p_ in zip(x, ip, pp):
    ax.text(xi, i_ + 0.08, "%.0f mW" % p_, ha="center", fontsize=5.6)
ax.set_xticks(x)
ax.set_xticklabels([g[1] for g in grp], fontsize=5.8)
ax.set_ylim(0, 3.2)
ax.set_ylabel("rms current per capacitor (A)")
ax.grid(axis="x", visible=False)
es.panel(ax, "(c)", dx=-0.30, dy=-0.17)
save(fig, "fig_dclink")
print("cap I per part", [round(v, 2) for v in ip], "P mW", [round(v, 1) for v in pp], "total W", round(case["cap_P_total"], 3))


# =====================================================================================================================
# 8. current-sharing sensitivity (simulation/sharing/paper_run, LTspice, 2 x EPC2361 low side, 75 V / 120 A)
sys.path.insert(0, os.path.join(ROOT, "simulation", "sharing"))
import plot_sharing as psh  # noqa: E402

colsh, steps = psh.read_raw(os.path.join(ROOT, "simulation", "sharing", "paper_run", "Sharing_paper.raw"))
T1s = 0.5e-6 + 5e-6 * 120 / 75
T2s = T1s + 1e-6
CASE_LAB = ["symmetric,\nKelvin", "$L_D$ +0.3 nH", "$L_G$ 2 vs 8 nH", "no Kelvin,\nsymmetric", "no Kelvin,\n$L_{CS}$ +0.2 nH",
            "$V_\\mathrm{th}$ +0.3 V"]
fig = plt.figure(figsize=(es.TXT_W, 1.85))
xs0, w0 = 0.055, 0.155
for k, (case, lab) in enumerate(((0, "(a.i)"), (2, "(a.ii)"), (4, "(a.iii)"))):
    ax = fig.add_axes([xs0 + k * (w0 + 0.035), 0.22, w0, 0.72])
    a = steps[case]
    t = a[:, 0]
    m = (t > T2s - 3e-9) & (t < T2s + 22e-9)
    ax.plot((t[m] - T2s) * 1e9, a[m, colsh["i(ld1)"]], color=C["blue"])
    ax.plot((t[m] - T2s) * 1e9, a[m, colsh["i(ld2)"]], color=C["red"], ls="--")
    ax.set_xlim(-3, 22)
    ax.set_ylim(-10, 160)
    ax.set_xlabel("time (ns)")
    if k == 0:
        ax.set_ylabel(r"drain current (A)")
        es.tag(ax, 14, 145, "$i_\\mathrm{D1}$", C["blue"])
        es.tag(ax, 19, 145, "$i_\\mathrm{D2}$", C["red"])
    else:
        ax.set_yticklabels([])
    ax.text(0.04, 0.96, CASE_LAB[case].replace("\n", " "), transform=ax.transAxes, fontsize=6.2, va="top",
            bbox=dict(fc="w", ec="none", pad=0.5))
    es.panel(ax, lab, dx=-0.12 if k else -0.38, dy=-0.2)
ax = fig.add_axes([0.66, 0.22, 0.33, 0.72])
eon = np.array([[9.31, 9.31], [10.54, 6.70], [19.19, 4.87], [13.70, 13.70], [28.30, 10.24], [13.55, 7.09]])
eoff = np.array([[7.53, 7.53], [7.42, 7.46], [6.73, 7.40], [8.02, 8.02], [7.73, 18.03], [10.20, 5.33]])
x = np.arange(6)
for j, (c, hatch) in enumerate(((C["blue"], None), (C["red"], None))):
    ax.bar(x + (j - 0.5) * 0.36, eon[:, j], 0.36, color=c, alpha=0.8, edgecolor="k", lw=0.4)
    ax.bar(x + (j - 0.5) * 0.36, eoff[:, j], 0.36, bottom=eon[:, j], color="w", edgecolor=c, hatch="////", lw=0.6)
ax.set_xticks(x)
ax.set_xticklabels(CASE_LAB, fontsize=5.0, rotation=0)
ax.set_xlim(-0.6, 5.6)
ax.set_ylim(0, 42)
ax.set_ylabel(r"$E_\mathrm{on}$ + $E_\mathrm{off}$ ($\mu$J)")
ax.grid(axis="x", visible=False)
es.tag(ax, 0.0, 38, "solid: $E_\\mathrm{on}$, hatched: $E_\\mathrm{off}$", "0.25")
es.tag(ax, 0.0, 33, "Q1", C["blue"])
es.tag(ax, 0.6, 33, "Q2", C["red"])
idiff = [0, 2, 19, 0, 29, 7]
for xi, v in zip(x, idiff):
    ax.text(xi, max(eon[xi] + eoff[xi]) + 1.0, "%d %%" % v, ha="center", fontsize=5.8)
es.panel(ax, "(b)", dx=-0.14, dy=-0.2)
save(fig, "fig_sharing")

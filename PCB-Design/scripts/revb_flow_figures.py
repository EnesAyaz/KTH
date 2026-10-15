"""
Design-flow figures of the Rev B deck (slide-sized, larger fonts), updated to the final design:

  dev_compare     (a) R_DS(on) vs C_oss,tr, (b) per-unit: R_DS(on)/V_DS,max vs C_oss,tr/V_DS,max, (c) radar
  epc_kelvin      EPC2361 land pattern (gate, Kelvin source, drain/source stripes) and the gate / power loop symbol
  flow_vm2        (a) max. V_m = 90 V - L di/dt for 0.5 / 1 nH with the turn-on di/dt at 60 / 80 / 120 A per device
                  (analytical gate-charge model), (b) V_m = 1200 V / N
  flow_single2    lumped half bridge, one EPC2361 per switch, 0.5 / 1 nH (LTspice FLOW_lumped2): (a) peak V_DS,
                  (b) E_on / E_off, (c) |di/dt|, (d) conduction loss vs current per device
  flow_npar2      n cells per switch: (a) loss per leg, (b) T_j, (c) peak V_DS for 0.5 / 1 nH
  flow_wave2      loss over the line period for n = 4 at 0.5 / 1 nH, conduction loss vs T_j
  flow_fsw2       (a) efficiency, (b) 22 uF 2220 per leg vs f_sw (3 % ripple), (c) winding current ripple
  dclink2         22 uF 2220 per leg vs allowed ripple for 50 / 75 / 100 kHz (three legs share the level)
  drv_layouts     driver arrangement for n = 1 .. 4 EPC2361 per switch (one dual-channel driver per pair)

    C:\\Github\\KTH\\LossCalculation-SPB\\.venv\\Scripts\\python.exe scripts\\revb_flow_figures.py
      -> reports/slides/revb_pptx/img/*.png, reports/slides/data/revb_flow_numbers.json
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
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch  # noqa: E402

plt.rcParams.update({"font.size": 9.5, "axes.labelsize": 9.5, "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
                     "legend.fontsize": 8.5, "axes.titlesize": 9.5})
ANA = os.path.join(os.path.dirname(ROOT), "Analytical Loss Calculations - GaN")
sys.path.insert(0, ANA)
from epc2361_loss import LossInputs, calculate, rds_temperature_factor  # noqa: E402

C = es.C
IMG = os.path.join(ROOT, "reports", "slides", "revb_pptx", "img")
DATA = os.path.join(ROOT, "reports", "slides", "data")
os.makedirs(IMG, exist_ok=True)
sz = json.load(open(os.path.join(ROOT, "reports", "building-block", "data", "sizing.json")))
S = sz["spec"]
fl = json.load(open(os.path.join(DATA, "flow_spice.json")))
NUM = {}

VBUS, P_SYS, M, PF = 1200.0, 300e3, 1.15, 0.9
VM = 75.0
N_SM = VBUS / VM
V_PH = M * VM / (2 * math.sqrt(2))
I_RMS = P_SYS / (3 * N_SM * V_PH * PF)
I_PK = I_RMS * math.sqrt(2)
F_SW = 50e3
P_LEG = P_SYS / (3 * N_SM)
T_COOL = 60.0
VDS_LIM, TJ_LIM = 90.0, 125.0
RDS25 = S["Rds_25_typ"]
EOSS = S["Eoss_75"]
QG, VG = S["Qg_typ"], 6.29
RTH = 3.4
RTH_SET = [(2.1, "2.1 K/W (optimistic)", C["green"]), (RTH, "3.4 K/W (AlN + cold plate)", C["red"]),
           (8.0, "8 K/W (gap pad)", C["purple"])]
LS_ = (0.5e-9, 1.0e-9)
LCOL = {0.5e-9: C["red"], 1.0e-9: C["blue"]}


def rds(tj):
    return RDS25 * rds_temperature_factor(min(max(tj, 0.0), 150.0))


def save(fig, name):
    fig.savefig(os.path.join(IMG, name + ".png"), dpi=220)
    plt.close(fig)
    print("wrote", name)


def panel(ax, s):
    ax.text(-0.02, -0.2, s, transform=ax.transAxes, fontsize=10, fontweight="bold", ha="right", va="top")


# ===================================================================================================== devices
DEV = [("EPC2361", 100, 0.75, 90, 50), ("EPC2302", 100, 1.4, 85, 50), ("EPC2071", 100, 1.7, 71, 50),
       ("IGC033S10S1", 100, 2.4, 43, 50), ("EPC2304", 200, 3.5, 120, 100), ("EPC2215", 200, 6.0, 69, 100),
       ("EPC2034C", 200, 6.0, 96, 100), ("EPC2050", 350, 55.0, 35, 280), ("IGT65R025D2", 650, 25.0, 82, 400),
       ("IGT65R140D2", 650, 140.0, 14, 400)]
VMC = {100: 75.0, 200: 150.0, 350: 240.0, 650: 400.0}
KC = {100: C["red"], 200: C["blue"], 350: C["green"], 650: C["yellow"]}
fig = plt.figure(figsize=(12.0, 3.9))
for k, (pu, lab) in enumerate(((False, "(a)"), (True, "(b)"))):
    ax = fig.add_axes([0.06 + k * 0.33, 0.16, 0.27, 0.78])
    for pn, v, r, q, vt in DEV:
        ctr = q / vt * 1e3
        x, y = (ctr / v, r / v) if pu else (ctr, r)
        ax.loglog(x, y, "o" if pn.startswith("EPC") else "s", color=KC[v], mec="k", mew=0.4, ms=6)
        off = {"EPC2215": (-6, -3, "right"), "EPC2034C": (6, 3, "left"), "EPC2304": (6, -6, "left"),
               "IGC033S10S1": (6, 2, "left"), "EPC2071": (6, 2, "left"), "EPC2302": (6, -5, "left")}.get(pn, (6, -3, "left"))
        ax.annotate(pn, (x, y), textcoords="offset points", xytext=off[:2], ha=off[2], fontsize=7.5)
    if pu:
        ax.set_xlabel(r"$C_\mathrm{oss,tr}\,/\,V_\mathrm{DS,max}$ (pF/V)")
        ax.set_ylabel(r"$R_\mathrm{DS(on)}\,/\,V_\mathrm{DS,max}$ (m$\Omega$/V)")
        ax.set_title("per unit of blocking voltage", fontsize=9.5)
    else:
        cc = np.logspace(1.2, 3.65, 40)
        for tau in (1, 2, 5, 10):
            ax.loglog(cc, tau / cc * 1e3, color="0.6", lw=0.6, ls=(0, (4, 2)))
            ax.text(19, tau / 19 * 1e3 * 1.15, r"$\tau$ = %g ps" % tau, rotation=-27, fontsize=7.5, color="0.35")
        ax.set_xlim(15, 4000)
        ax.set_ylim(0.4, 900)
        ax.set_xlabel(r"$C_\mathrm{oss,tr}=Q_\mathrm{oss}/V_\mathrm{test}$ (pF)")
        ax.set_ylabel(r"$R_\mathrm{DS(on)}$ (m$\Omega$)")
        ax.set_title("absolute", fontsize=9.5)
        for v in (100, 200, 350, 650):
            ax.plot([], [], "o", color=KC[v], mec="k", mew=0.4, label="%d V" % v)
        ax.legend(loc="upper right", ncol=2)
    panel(ax, lab)
best = {}
for pn, v, r, q, vt in DEV:
    tau = r * q / vt
    if v in (100, 200, 650) and (v not in best or tau < best[v]["tau"]):
        n_mod = VBUS / VMC[v]
        qv = q / vt * 1e-9 * VMC[v]
        nopt = 100.0 * math.sqrt(r * 1e-3 / (50e3 * qv * VMC[v]))
        best[v] = dict(pn=pn, tau=tau, pmin=math.sqrt(tau), n_mod=n_mod, nopt=nopt, step=VMC[v],
                       switches=n_mod * 6 * nopt)
axes_def = [("pmin", "min. semicond.\nloss"), ("nopt", "devices\nper switch"), ("n_mod", "no. of\nsubmodules"),
            ("step", "winding\nvoltage step"), ("switches", "no. of\ntransistors")]
ang = (np.linspace(0, 2 * np.pi, len(axes_def), endpoint=False) + np.pi / 2) % (2 * np.pi)
axr = fig.add_axes([0.775, 0.2, 0.17, 0.6], polar=True)
for v in (100, 200, 650):
    vals = np.array([best[v][k] / max(best[w][k] for w in best) for k, _ in axes_def])
    axr.plot(np.r_[ang, ang[0]], np.r_[vals, vals[0]], "-o", color=KC[v], lw=1.3, ms=4,
             label="%d V (%s)" % (v, best[v]["pn"]))
    axr.fill(np.r_[ang, ang[0]], np.r_[vals, vals[0]], color=KC[v], alpha=0.12)
axr.set_xticks(ang)
axr.set_xticklabels([t for _, t in axes_def], fontsize=7.5)
axr.set_ylim(0, 1.05)
axr.set_yticks([0.25, 0.5, 0.75, 1.0])
axr.set_yticklabels(["25%", "50%", "75%", "100%"], fontsize=6.5, color="0.4")
axr.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), fontsize=7.5, ncol=1)
axr.text(-0.55, -0.2, "(c)", transform=axr.transAxes, fontsize=10, fontweight="bold")
axr.set_title("best device per class, normalized", fontsize=9.5, pad=22)
save(fig, "dev_compare")
NUM["devices"] = {pn: dict(V=v, R_pu=r / v, C_pu=q / vt * 1e3 / v) for pn, v, r, q, vt in DEV}

# ===================================================================================================== EPC2361 Kelvin
PADS = [("1", -2.352, -1.23, 1.102, 1.14, "G"), ("2", -2.352, 0.67, 1.102, 2.26, "K"),
        ("3", -1.275, 0, 0.65, 3.6, "D"), ("4", -0.425, 0, 0.65, 3.6, "S"), ("5", 0.425, 0, 0.65, 3.6, "D"),
        ("6", 1.275, 0, 0.65, 3.6, "S"), ("7", 2.352, 0, 1.102, 3.6, "D")]
PC = {"G": C["green"], "K": C["purple"], "D": C["red"], "S": C["blue"]}
fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.2), gridspec_kw=dict(width_ratios=[1.0, 1.25], wspace=0.08))
ax = axs[0]
ax.add_patch(Rectangle((-2.5, -1.5), 5.0, 3.0, fc="0.93", ec="0.4", lw=1.0, ls="--"))
for num, x, y, w, h, f in PADS:
    ax.add_patch(Rectangle((x - w / 2, -y - h / 2), w, h, color=PC[f], alpha=0.9))
    ax.text(x, -y, {"G": "G", "K": "K", "D": "D", "S": "S"}[f], ha="center", va="center", color="w", fontsize=12,
            fontweight="bold")
    ax.text(x, -1.95 if f in "DS" else (-y + (0.85 if f == "G" else -1.35)), "pad %s" % num, ha="center",
            fontsize=7.5, color="0.3")
ax.annotate("Kelvin source (pad 2):\nreturn of the gate loop only", (-2.35, -0.67), (-4.7, -2.6), fontsize=9,
            color=C["purple"], arrowprops=dict(arrowstyle="-|>", color=C["purple"]))
ax.annotate("gate (pad 1)", (-2.35, 1.23), (-4.7, 2.2), fontsize=9, color=C["green"],
            arrowprops=dict(arrowstyle="-|>", color=C["green"]))
ax.annotate("interleaved drain / source\nstripes: power loop", (1.3, 1.6), (0.3, 2.55), fontsize=9, color="0.2",
            arrowprops=dict(arrowstyle="-|>", color="0.3"))
ax.set_xlim(-5.0, 3.4)
ax.set_ylim(-3.2, 3.2)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("EPC2361 land pattern (top view, 5 × 3 mm)", fontsize=10)
ax.text(-5.0, -3.15, "(a)", fontsize=10, fontweight="bold")
ax = axs[1]
ax.axis("off")
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)
lw = 2.2
# transistor symbol
ax.plot([6.0, 6.0], [2.2, 4.8], color="k", lw=lw)                  # channel
ax.plot([5.6, 5.6], [2.6, 4.4], color="k", lw=lw)                  # gate plate
ax.plot([3.2, 5.6], [3.5, 3.5], color=C["green"], lw=lw)           # gate lead
ax.plot([6.0, 7.2, 7.2], [4.4, 4.4, 6.4], color=C["red"], lw=lw)   # drain
ax.plot([6.0, 7.2, 7.2], [2.6, 2.6, 0.6], color=C["blue"], lw=lw)  # power source
ax.plot([7.2, 7.8], [1.8, 1.8], color=C["blue"], lw=0)
for yy in np.linspace(1.0, 1.9, 4):                                # L_s of the power source path (coil)
    ax.add_patch(plt.matplotlib.patches.Arc((7.2, yy), 0.45, 0.3, theta1=270, theta2=90, color=C["blue"], lw=1.6))
ax.plot([6.6, 6.6, 3.2], [2.6, 2.0, 2.0], color=C["purple"], lw=lw)   # Kelvin taken at the die, before L_s
ax.plot([6.6], [2.6], "o", color=C["purple"], ms=6)
ax.text(7.45, 6.2, "D (pads 3, 5, 7)", fontsize=9.5, color=C["red"])
ax.text(7.45, 0.35, "S, power (pads 4, 6)", fontsize=9.5, color=C["blue"])
ax.text(7.6, 1.45, "$L_S$ (stripes, vias)", fontsize=9, color=C["blue"])
ax.text(3.2, 3.65, "G (pad 1)", fontsize=9.5, color=C["green"])
ax.text(3.2, 1.55, "K, Kelvin source (pad 2)", fontsize=9.5, color=C["purple"])
ax.add_patch(FancyBboxPatch((0.4, 1.7), 2.2, 2.1, boxstyle="round,pad=0.05", fc="#E8EEF7", ec="0.3"))
ax.text(1.5, 2.75, "driver\noutput", ha="center", va="center", fontsize=9.5)
ax.plot([2.6, 3.2], [3.5, 3.5], color=C["green"], lw=lw)
ax.plot([2.6, 3.2], [2.0, 2.0], color=C["purple"], lw=lw)
ax.text(1.0, 5.2, "gate loop: driver → G → die → K → driver\n$L_S$ is not inside the gate loop", fontsize=9,
        color=C["green"])
ax.add_patch(FancyArrowPatch((9.6, 5.9), (9.6, 0.9), arrowstyle="-|>", mutation_scale=16, color=C["red"],
                             connectionstyle="arc3,rad=-0.15"))
ax.text(9.75, 3.4, "power\nloop", fontsize=9, color=C["red"], va="center")
ax.text(0.0, 6.6, "(b)", fontsize=10, fontweight="bold")
save(fig, "epc_kelvin")


# ===================================================================================================== V_m
def ana(i_dev, rgon, L_nh=0.5):
    r = calculate(LossInputs(vbus=75, ac_rms=i_dev / math.sqrt(2), fsw=F_SW, rg_on=rgon, rg_off=0.0,
                             driver_source_r=0.85, driver_sink_r=0.35, driver_source_a=4, driver_sink_a=8,
                             loop_inductance_nh=L_nh, waveform_current_a=i_dev, case_c=60))
    return r["didt_on_a_ns"]


RG = 2.0
CUR = (60, 80, 120)
DIDT = {(i, L): ana(i, RG, L * 1e9) for i in CUR for L in LS_}
fig, axs = plt.subplots(1, 2, figsize=(11.5, 3.9), gridspec_kw=dict(wspace=0.25, width_ratios=[1.25, 1]))
ax = axs[0]
dd = np.linspace(0, 80, 100)
mk = {60: "s", 80: "o", 120: "^"}
for L in LS_:
    ax.plot(dd, VDS_LIM - L * 1e9 * dd, color=LCOL[L], lw=1.6, label="$L_\\mathrm{loop}$ = %g nH" % (L * 1e9))
    for i in CUR:
        d = DIDT[(i, L)]
        ax.plot(d, VDS_LIM - L * 1e9 * d, mk[i], color=LCOL[L], mec="k", mew=0.5, ms=8)
        ax.annotate("%d A: %.0f A/ns → %.0f V" % (i, d, VDS_LIM - L * 1e9 * d), (d, VDS_LIM - L * 1e9 * d),
                    textcoords="offset points", xytext=(7, 4 if L < 0.7e-9 else -12), fontsize=8, color=LCOL[L])
ax.axhline(75, color="k", lw=0.8, ls=":")
ax.text(1, 75.8, "75 V", fontsize=8.5)
ax.set_xlim(0, 80)
ax.set_ylim(0, 95)
ax.set_xlabel("turn-on $di/dt$ (A/ns)")
ax.set_ylabel(r"max. $V_m$ = 90 V $- L_\mathrm{loop}\,di/dt$ (V)")
ax.legend(loc="lower left")
ax.text(0.98, 0.04, "markers: di/dt at 60 / 80 / 120 A per device\n(analytical gate-charge model, $R_{g,on}$ = 2 Ω)",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color="0.3")
panel(ax, "(a)")
ax = axs[1]
Ns = np.arange(12, 21)
vmN = VBUS / Ns
cols = [C["green"] if (v <= 75.0 + 1e-9 and n_ % 2 == 0) else (C["yellow"] if v <= 75.0 + 1e-9 else C["grey"])
        for n_, v in zip(Ns, vmN)]
ax.bar(Ns, vmN, 0.65, color=[(*c, 0.75) for c in cols], edgecolor="k", lw=0.4)
for n_, v in zip(Ns, vmN):
    ax.text(n_, v + 1.5, "%.1f" % v if abs(v - round(v)) > 0.05 else "%.0f" % v, ha="center", fontsize=8)
ax.axhline(75, color=C["red"], ls="--", lw=0.9)
ax.bar([16], [75], 0.65, fill=False, edgecolor=C["red"], lw=1.6)
ax.set_xticks(Ns)
ax.set_xlabel("number of submodules $N$")
ax.set_ylabel("$V_m$ = 1200 V / $N$ (V)")
ax.set_ylim(0, 118)
ax.grid(axis="x", visible=False)
ax.text(11.6, 110, "grey: $V_m$ > 75 V   yellow: odd $N$   green: allowed", fontsize=8, color="0.3")
panel(ax, "(b)")
save(fig, "flow_vm2")
NUM["vm"] = {"%d_A_%gnH" % (i, L * 1e9): dict(didt=d, vm_max=VDS_LIM - L * 1e9 * d) for (i, L), d in DIDT.items()}

# ===================================================================================================== one device
lm, lst = fl["lumped2"]["meas"], fl["lumped2"]["steps"]


def lcol(L, key):
    idx = [k for k, s in enumerate(lst) if abs(s["lloop"] - L) < 1e-13]
    return np.abs(np.array([lm["iload"][k] for k in idx])), np.array([lm[key][k] for k in idx])


FIT = {}
for L in LS_:
    ii, eon = lcol(L, "eon")
    _, eoff = lcol(L, "eoff")
    FIT[L] = (np.polyfit(ii, eon, 2), np.polyfit(ii, eoff, 2))
fig, axs = plt.subplots(1, 4, figsize=(13.0, 3.5), gridspec_kw=dict(wspace=0.42))
ax = axs[0]
for L in LS_:
    ii, v = lcol(L, "vdsl_pk")
    ax.plot(ii, v, "-o", color=LCOL[L], ms=4, label="%g nH" % (L * 1e9))
ax.axhline(VDS_LIM, color="k", ls="--", lw=0.9)
ax.axhline(100, color="k", lw=0.9)
ax.text(5, VDS_LIM + 2, "90 V", fontsize=8.5)
for i in CUR:
    ax.axvline(i, color="0.6", lw=0.6, ls=":")
ax.set_xlabel("current per device (A)")
ax.set_ylabel(r"peak $V_\mathrm{DS}$ at turn-off (V)")
ax.set_xlim(0, 340)
ax.set_ylim(70, 220)
ax.legend(loc="upper left")
panel(ax, "(a)")
ax = axs[1]
xx = np.linspace(0, 330, 100)
for L in LS_:
    ii, eon = lcol(L, "eon")
    _, eoff = lcol(L, "eoff")
    ax.plot(ii, eon * 1e6, "o", color=LCOL[L], ms=4)
    ax.plot(ii, eoff * 1e6, "s", color=LCOL[L], ms=4, mfc="w")
    ax.plot(xx, np.polyval(FIT[L][0], xx) * 1e6, color=LCOL[L], lw=1.0, label="$E_\\mathrm{on}$, %g nH" % (L * 1e9))
    ax.plot(xx, np.polyval(FIT[L][1], xx) * 1e6, color=LCOL[L], lw=1.0, ls="--",
            label="$E_\\mathrm{off}$, %g nH" % (L * 1e9))
ax.set_xlabel("current per device (A)")
ax.set_ylabel(r"energy per device ($\mu$J)")
ax.set_xlim(0, 340)
ax.legend(loc="upper left", fontsize=7.5)
panel(ax, "(b)")
ax = axs[2]
for L in LS_:
    ii, don = lcol(L, "didt_on")
    _, doff = lcol(L, "didt_off")
    ok = (ii > 20) & (don / 1e9 < 150)                 # first edges: meas. window artefacts
    ax.plot(ii[ok], don[ok] / 1e9, "-o", color=LCOL[L], ms=4, label="turn-on, %g nH" % (L * 1e9))
    ax.plot(ii, -doff / 1e9, "--s", color=LCOL[L], ms=4, mfc="w", label="turn-off, %g nH" % (L * 1e9))
ax.set_xlabel("current per device (A)")
ax.set_ylabel("$|di/dt|$ (A/ns)")
ax.set_xlim(0, 340)
ax.legend(loc="upper left", fontsize=7.5)
panel(ax, "(c)")
ax = axs[3]
ii = np.linspace(0, 130, 100)
for tj, c in ((25, C["green"]), (100, C["red"]), (150, C["purple"])):
    ax.plot(ii, ii ** 2 * rds(tj), color=c, lw=1.6, label="$T_j$ = %d °C" % tj)
for i in CUR:
    ax.axvline(i, color="0.6", lw=0.6, ls=":")
    ax.text(i, 2, " %d A" % i, fontsize=7.5, color="0.35", rotation=90)
ax.set_xlabel("RMS current per device (A)")
ax.set_ylabel("conduction loss per device (W)")
ax.set_xlim(0, 130)
ax.legend(loc="upper left")
panel(ax, "(d)")
save(fig, "flow_single2")
NUM["single"] = {"%gnH" % (L * 1e9): dict(I=lcol(L, "vdsl_pk")[0].tolist(), vpk=lcol(L, "vdsl_pk")[1].tolist(),
                                           eon=lcol(L, "eon")[1].tolist(), eoff=lcol(L, "eoff")[1].tolist())
                 for L in LS_}
NUM["cond"] = {"%d" % i: dict(P25=i ** 2 * rds(25), P100=i ** 2 * rds(100)) for i in CUR}

# ===================================================================================================== n in parallel
th = np.linspace(0, np.pi, 2001)


# thermal path of the LOAD-TEST board (LAM 4 K 50 12 in air): all transistor loss of the leg through the heatsink
# (0.65 K/W), per device R_thJC top 0.2 K/W + gap pad 0.4 mm, 5 W/mK over the 15 mm2 package top (5.3 K/W) + the Al
# spreader from the outer cell to the 50 mm tube (8 mm in 12.8 x 3 mm Al, 1.04 K/W per cell = 2 devices -> 2.1 K/W)
R_HS, R_JC, R_PAD, R_SPR = 0.65, 0.2, 0.4e-3 / (5.0 * 15e-6), 2 * 0.008 / (200.0 * 12.8e-3 * 3e-3)
R_JH = R_JC + R_PAD + R_SPR
T_AMB = 40.0
TH_SET = [(25.0, R_JH, "ambient 25 °C", C["green"]), (40.0, R_JH, "ambient 40 °C", C["red"]),
          (40.0, R_JC + 0.4e-3 / (3.0 * 15e-6) + R_SPR, "40 °C, 3 W/mK pad", C["purple"])]


def leg(n, f=F_SW, amb=T_AMB, rjh=R_JH, L=0.5e-9):
    ia = I_PK * np.sin(th)
    irms = I_PK / math.sqrt(2)
    pon, poff = FIT[L]
    sw = n * f * float(np.mean(np.polyval(pon, ia / n) + np.polyval(poff, ia / n))) + n * EOSS * f
    dead = 2 * f * S["t_dead"] * float(np.mean(ia * (S["Vsd0"] + S["Rsd"] / n * ia)))
    gate = 2 * n * QG * VG * f
    tj = amb
    for _ in range(80):
        cond = irms ** 2 * rds(tj) / n
        pdev = (cond + sw + dead) / (2 * n)
        tj_new = amb + R_HS * (cond + sw + dead) + rjh * pdev
        if tj_new > 200:
            tj = 200.0
            break
        tj = tj_new
    ii, vv = lcol(L, "vdsl_pk")
    tot = cond + sw + dead + gate
    return dict(n=n, cond=cond, cond25=irms ** 2 * RDS25 / n, sw=sw, dead=dead, gate=gate, tot=tot, pdev=pdev, tj=tj,
                eta=1 - tot / P_LEG, vpk=float(np.interp(I_PK / n, ii, vv)))


ns = np.arange(1, 9)
fig, axs = plt.subplots(1, 3, figsize=(12.5, 3.7), gridspec_kw=dict(wspace=0.32))
ax = axs[0]
w_ = 0.38
for k, L in enumerate(LS_):
    R = [leg(int(n), L=L) for n in ns]
    bottom = np.zeros(len(ns))
    for key, lab, c in (("cond", "conduction ($T_j$)", C["blue"]), ("sw", "switching", C["red"]),
                        ("dead", "dead time", C["yellow"]), ("gate", "gate", C["dred"])):
        v = np.array([r[key] for r in R])
        ax.bar(ns + (k - 0.5) * w_, v, w_, bottom=bottom, color=c, alpha=0.9 if k == 0 else 0.5, edgecolor="k", lw=0.3,
               label=lab if k == 0 else None, hatch=None if k == 0 else "//")
        bottom += v
ax.bar([], [], color="w", edgecolor="k", label="left 0.5 nH, right 1 nH (hatched)")
if leg(1)["tj"] >= 199:
    ax.text(1, 56, "n = 1:\nthermal\nrunaway", ha="center", fontsize=8, color=C["red"])
ax.set_xticks(ns)
ax.set_xlabel("EPC2361 per switch $n$")
ax.set_ylabel("semiconductor loss per leg (W)")
ax.set_ylim(0, 85)
ax.legend(loc="upper right", fontsize=7.5)
ax.grid(axis="x", visible=False)
panel(ax, "(a)")
ax = axs[1]
for amb, rjh, lab, c in TH_SET:
    ax.plot(ns, [leg(int(n), amb=amb, rjh=rjh)["tj"] for n in ns], "-o", color=c, ms=4, label=lab)
ax.axhline(TJ_LIM, color="k", ls="--", lw=0.9)
ax.set_ylim(55, 180)
ax.set_xticks(ns)
ax.set_xlabel("EPC2361 per switch $n$")
ax.set_ylabel("$T_j$ (°C), load-test board, 0.5 nH")
ax.legend(loc="upper right")
panel(ax, "(b)")
ax = axs[2]
for L in LS_:
    ax.plot(ns, [leg(int(n), L=L)["vpk"] for n in ns], "-o", color=LCOL[L], ms=4, label="%g nH" % (L * 1e9))
ax.axhline(VDS_LIM, color="k", ls="--", lw=0.9)
ax.set_xticks(ns)
ax.set_xlabel("EPC2361 per switch $n$")
ax.set_ylabel(r"peak $V_\mathrm{DS}$ at $I_\mathrm{pk}/n$ (V)")
ax.set_ylim(75, 160)
ax.legend(loc="upper right")
panel(ax, "(c)")
save(fig, "flow_npar2")
NUM["npar"] = {"%gnH" % (L * 1e9): [leg(int(n), L=L) for n in ns] for L in LS_}
NUM["thermal"] = dict(R_HS=R_HS, R_JC=R_JC, R_PAD=R_PAD, R_SPR=R_SPR, R_JH=R_JH, T_AMB=T_AMB,
                      tj4_25=leg(4, amb=25.0)["tj"], tj4_40=leg(4)["tj"],
                      tj4_40_3W=leg(4, rjh=TH_SET[2][1])["tj"])

# ===================================================================================================== loss over the period
deg = np.linspace(0, 360, 721)
ia = I_PK * np.abs(np.sin(np.radians(deg)))
fig, axs = plt.subplots(1, 2, figsize=(12.0, 3.8), gridspec_kw=dict(wspace=0.3, width_ratios=[1.35, 1]))
ax = axs[0]
n4 = {L: leg(4, L=L) for L in LS_}
p_cd = ia ** 2 * rds(n4[0.5e-9]["tj"]) / 4
ax.fill_between(deg, 0, p_cd, color=C["blue"], alpha=0.3, lw=0)
ax.plot(deg, p_cd, color=C["blue"], lw=1.1, label="conduction")
for L in LS_:
    pon, poff = FIT[L]
    p_sw = 4 * F_SW * (np.polyval(pon, ia / 4) + np.polyval(poff, ia / 4) + EOSS)
    ax.plot(deg, p_cd + p_sw, color=LCOL[L], lw=1.4,
            label="total, %g nH: avg. %.1f W (switching %.1f W)" % (L * 1e9, np.mean(p_cd + p_sw), np.mean(p_sw)))
    NUM.setdefault("wave", {})["%gnH" % (L * 1e9)] = dict(p_cond=float(np.mean(p_cd)), p_sw=float(np.mean(p_sw)))
ax2 = ax.twinx()
ax2.plot(deg, I_PK * np.sin(np.radians(deg)), color="0.5", lw=0.8)
ax2.set_ylim(-400, 400)
ax2.set_ylabel("leg current (A)", color="0.4")
ax2.tick_params(axis="y", colors="0.4")
ax2.grid(False)
ax.set_xlim(0, 360)
ax.set_xticks([0, 90, 180, 270, 360])
ax.set_ylim(0, 42)
ax.set_xlabel("line angle (deg)")
ax.set_ylabel("loss per leg, 50 kHz avg. (W)")
ax.legend(loc="upper center", fontsize=8)
panel(ax, "(a)")
ax = axs[1]
tt = np.linspace(25, 150, 60)
for n, c in ((2, C["purple"]), (4, C["red"]), (6, C["blue"])):
    ax.plot(tt, [I_RMS ** 2 * rds(t) / n for t in tt], color=c, lw=1.4)
    r = leg(n)
    ax.plot(r["tj"], r["cond"], "o", color=c, mec="k", mew=0.4, ms=6)
    ax.text(151, I_RMS ** 2 * rds(150) / n, " $n$=%d" % n, color=c, fontsize=9, va="center")
ax.set_xlim(25, 168)
ax.set_xlabel("$T_j$ (°C)")
ax.set_ylabel("conduction loss per leg (W)")
ax.text(30, 33, "dots: operating point (load-test board, 40 °C ambient)", fontsize=8.5, va="top")
panel(ax, "(b)")
save(fig, "flow_wave2")

# ===================================================================================================== switching frequency, DC link
DS = json.load(open(os.path.join(DATA, "dclink_sizing.json")))
CC = json.load(open(os.path.join(DATA, "capacitor_compare.json")))
C2220 = [p for p in CC["parts"] if "226" in p["part"]][0]["C_eff_uF"] * 1e-6
BYP_LEG = CC["bypass"]["C_eff_leg"]
I_PART = [p for p in CC["parts"] if "226" in p["part"]][0]["I_10K_A"]
DQ = {f: DS["cases"]["%dkHz_1pct" % f]["C_eff_level_uF"] * 1e-6 * 0.01 * VM for f in (50, 75, 100)}


def n2220(f_khz, pct):
    dq = DQ[50] * 50.0 / f_khz
    return max(0, math.ceil((dq / (pct / 100 * VM) / 3 - BYP_LEG) / C2220))


fs = np.linspace(10e3, 150e3, 57)
L_SIG = (10e-6, 25e-6, 50e-6)
fig, axs = plt.subplots(1, 3, figsize=(12.5, 3.7), gridspec_kw=dict(wspace=0.32))
ax = axs[0]
for n, c in ((3, C["purple"]), (4, C["red"]), (6, C["blue"])):
    ax.plot(fs / 1e3, [100 * (1 - (leg(n, f=f)["tot"]) / P_LEG) for f in fs], color=c, lw=1.4, label="$n$ = %d" % n)
ax.axhline(99.5, color="k", ls="--", lw=0.9)
ax.set_xlabel("$f_\\mathrm{sw}$ (kHz)")
ax.set_ylabel("semiconductor efficiency (%)")
ax.set_ylim(99.0, 100)
ax.legend(loc="lower left")
panel(ax, "(a)")
ax = axs[1]
n_v = [n2220(f / 1e3, 3) for f in fs]
n_i = math.ceil(CC["I_ripple_leg"] / I_PART)
ax.fill_between(fs / 1e3, np.maximum(n_v, n_i), 60, color=C["green"], alpha=0.12, lw=0)
ax.plot(fs / 1e3, n_v, color=C["blue"], lw=1.4, label="ripple ΔV$_{pp}$ = 3 %")
ax.axhline(n_i, color=C["red"], lw=1.4, label="ripple current, %.1f A per part (+10 K)" % I_PART)
ax.plot(50, 20, "*", color="k", ms=11)
ax.text(54, 21.5, "selected: 20 per leg", fontsize=8.5)
ax.set_xlabel("$f_\\mathrm{sw}$ (kHz)")
ax.set_ylabel("22 µF 2220 MLCCs per leg")
ax.set_ylim(0, 60)
ax.legend(loc="upper right", fontsize=8)
panel(ax, "(b)")
ax = axs[2]
for L, c in zip(L_SIG, (C["red"], C["yellow"], C["blue"])):
    ax.plot(fs / 1e3, VM / (4 * L * fs) / I_PK * 100, color=c, lw=1.4, label="$L_\\sigma$ = %g µH" % (L * 1e6))
ax.axhline(10, color="k", ls="--", lw=0.9)
ax.set_xlabel("$f_\\mathrm{sw}$ (kHz)")
ax.set_ylabel("$\\Delta i_\\mathrm{pp}$ / $I_\\mathrm{pk}$ (%)")
ax.set_ylim(0, 40)
ax.legend(loc="upper right")
panel(ax, "(c)")
save(fig, "flow_fsw2")
NUM["fsw"] = dict(n_i=n_i, n_v50=n2220(50, 3), eta4={"%d" % f: 100 * leg(4, f=f * 1e3)["eta"] for f in (20, 50, 100)})

fig, ax = plt.subplots(figsize=(6.4, 3.9))
pct = np.linspace(0.5, 4.0, 60)
for f, c in ((50, C["blue"]), (75, C["green"]), (100, C["red"])):
    ax.plot(pct, [n2220(f, p) for p in pct], color=c, lw=1.6, label="%d kHz" % f)
ax.axhline(20, color="k", ls="--", lw=0.9)
ax.text(3.95, 21, "selected: 20 × 22 µF 2220 per leg", ha="right", fontsize=8.5)
ax.plot(3, n2220(50, 3), "*", color="k", ms=11)
ax.set_xlabel("allowed ripple ΔV$_{pp}$ (% of 75 V)")
ax.set_ylabel("22 µF 2220 per leg board\n(three legs share the level)")
ax.set_ylim(0, 70)
ax.legend(loc="upper right")
save(fig, "dclink2")

# ===================================================================================================== driver layouts
fig, ax = plt.subplots(figsize=(8.0, 4.4))
ax.axis("off")
ax.set_xlim(0, 16)
ax.set_ylim(-0.2, 8.6)


def cell(x, y):
    ax.add_patch(FancyBboxPatch((x, y), 1.3, 1.1, boxstyle="round,pad=0.04", fc="#FBE3D6", ec=C["red"], lw=1.2))
    ax.text(x + 0.65, y + 0.55, "HS\nLS", ha="center", va="center", fontsize=8.5)


def drv(x, y, lab="2EDF"):
    ax.add_patch(FancyBboxPatch((x, y + 0.2), 0.9, 0.7, boxstyle="round,pad=0.03", fc="#DDEBD3", ec=C["green"], lw=1.2))
    ax.text(x + 0.45, y + 0.55, lab, ha="center", va="center", fontsize=7)


def star(x0, y, xs):
    for xx in xs:
        ax.plot([x0, xx], [y + 0.55, y + 0.55], color=C["green"], lw=1.2)


rows = [(1, [("c", 1.5), ("d", 3.0)], "1 driver, 1 transistor per channel"),
        (2, [("c", 1.5), ("d", 3.0), ("c", 4.1)], "1 driver, star to 2 (pair)"),
        (3, [("c", 1.5), ("d", 3.0), ("c", 4.1), ("d", 6.6), ("c", 7.7)], "2 drivers: pair + single (asymmetric)"),
        (4, [("c", 1.5), ("d", 3.0), ("c", 4.1), ("c", 6.0), ("d", 7.5), ("c", 8.6)],
         "2 drivers, one star per pair ← selected")]
for k, (n, items, lab) in enumerate(rows):
    y = 6.8 - 2.2 * k
    ax.text(0.0, y + 0.55, "$n$ = %d" % n, fontsize=11, va="center")
    for kind, x in items:
        if kind == "c":
            cell(x, y)
        else:
            drv(x + 0.05, y)
    ax.text(10.4, y + 0.55, lab, fontsize=9.5, va="center", color=C["green"] if n == 4 else "0.2",
            fontweight="bold" if n == 4 else None)
ax.text(0.0, 8.35, "Each box HS/LS = one cell (high- and low-side EPC2361); each driver IC = 2 channels (HS + LS)",
        fontsize=9)
save(fig, "drv_layouts")

# ===================================================================================================== loop of one cell (Q3D)
LBP = os.path.join(ROOT, "simulation", "bb_q3d", "results", "loop_breakdown.json")
if os.path.exists(LBP):
    LB = json.load(open(LBP))
    BC = {"load": (C["blue"], "load-test board (no shunt)"), "dpt": (C["red"], "DPT board (UFCS shunt)")}
    fig, axs = plt.subplots(1, 2, figsize=(12.0, 3.6), gridspec_kw=dict(wspace=0.25, width_ratios=[1.1, 1]))
    ax = axs[0]
    for b in ("load", "dpt"):
        if b not in LB:
            continue
        nn = np.arange(1, 13)
        ax.plot(nn, [LB[b]["vs_n_top"][str(n)] for n in nn], "-o", color=BC[b][0], ms=4, label=BC[b][1])
        ax.axhline(LB[b]["copper"], color=BC[b][0], ls=":", lw=1)
        ax.plot(6, LB[b]["total"], "*", color="k", ms=11)
    ax.axhline(0.5, color=C["green"], ls="--", lw=1, label="0.5 nH design value")
    ax.text(12, 0.352, "copper only (dotted)", ha="right", fontsize=8, color="0.3")
    ax.set_xlabel("top-row bypass 0805 per cell (+ 4 on the bottom)")
    ax.set_ylabel("loop per cell (nH), Q3D")
    ax.set_xlim(0.5, 12.5)
    ax.set_ylim(0.3, 1.0)
    ax.legend(loc="upper right")
    ax.text(1.0, 0.62, "black stars: as built (6 top + 4 bottom)", fontsize=8.5)
    panel(ax, "(a)")
    ax = axs[1]
    yy = 0
    for b in ("load", "dpt"):
        if b not in LB:
            continue
        d = LB[b]
        left = 0.0
        for v, c, lab in ((d["copper"], C["blue"], "copper (DPT: incl. the path to the shunt)"), (d["esl_part"], C["yellow"], "bypass ESL"),
                          (d["shunt_part"], C["red"], "UFCS 120 pH + its path")):
            if v > 1e-4:
                ax.barh(yy, v, left=left, color=c, alpha=0.85, edgecolor="k", lw=0.4, height=0.55,
                        label=lab if b == "dpt" else None)
                ax.text(left + v / 2, yy, "%.2f" % v, ha="center", va="center", fontsize=9, color="k")
            left += v
        ax.text(left + 0.01, yy, " %.2f nH" % left, va="center", fontsize=10, fontweight="bold")
        yy += 1
    ax.axvline(0.5, color=C["green"], ls="--", lw=1)
    ax.set_yticks(range(yy))
    ax.set_yticklabels([BC[b][1].replace(" (", "\n(") for b in ("load", "dpt") if b in LB])
    ax.set_xlim(0, 0.85)
    ax.set_xlabel("loop inductance per cell (nH), mean of 4 cells")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="y", visible=False)
    panel(ax, "(b)")
    save(fig, "loop_breakdown")

json.dump(NUM, open(os.path.join(DATA, "revb_flow_numbers.json"), "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in NUM.items() if k in ("vm", "cond", "fsw", "wave")}, indent=1, default=float)[:2500])

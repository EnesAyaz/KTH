"""
Figures and numbers for the decision-driven slides (reports/slides/spb_design_flow.tex), 1200 V / 300 kW system.

  flow_vm        submodule voltage from L_loop*di/dt (analytical gate-charge model, KTH/Analytical Loss Calculations
                 - GaN/epc2361_loss.py) and the discrete, even number of submodules
  flow_cells     parts count and relative conduction loss vs submodule voltage (fixed bus voltage and phase current)
  flow_loop      first-cut power loop of one cell: PCB copper + MLCC ESL vs number of local MLCCs
  flow_single    one EPC2361 per switch, lumped loop 0.3 / 0.5 / 0.8 nH (LTspice FLOW_lumped): V_DS, Eon/Eoff, di/dt
  flow_npar      n identical cells per switch at 228 A_rms: loss per leg, T_j for three R_th, peak V_DS
  flow_wave      switching and conduction loss over the line period (n = 4) and conduction loss vs T_j
  flow_fsw       loss per leg, DC-link MLCC count and winding current ripple vs switching frequency
  flow_twoblock  two building blocks per leg (LTspice FLOW_two): block currents for driver skew and AC interconnect

    python scripts/design_flow_figures.py   (after scripts/design_flow_spice.py)
      -> reports/slides/figs/flow_*.pdf, reports/slides/data/flow_numbers.json
"""
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "simulation", "sharing"))
import eth_style as es  # noqa: E402

es.setup()
import matplotlib.pyplot as plt  # noqa: E402
from plot_sharing import read_raw  # noqa: E402

ANA = os.path.join(os.path.dirname(ROOT), "Analytical Loss Calculations - GaN")
sys.path.insert(0, ANA)
from epc2361_loss import LossInputs, calculate, rds_temperature_factor  # noqa: E402

C = es.C
FIG = os.path.join(ROOT, "reports", "slides", "figs")
DATA = os.path.join(ROOT, "reports", "slides", "data")
SP = os.path.join(ROOT, "simulation", "bb_spice")
os.makedirs(FIG, exist_ok=True)
sz = json.load(open(os.path.join(ROOT, "reports", "building-block", "data", "sizing.json")))
S = sz["spec"]
fl = json.load(open(os.path.join(DATA, "flow_spice.json")))
NUM = {}

# ---------------------------------------------------------------------------------------------------- design inputs
VBUS, P_SYS, M, PF = 1200.0, 300e3, 1.15, 0.9    # 300 kW output at 1200 V, max. modulation 1.15, PMSM cos phi assumed
VM = 75.0
N_SM = VBUS / VM
V_PH = M * VM / (2 * math.sqrt(2))               # rms phase voltage of one leg
I_RMS = P_SYS / (3 * N_SM * V_PH * PF)           # per leg, ~228 A_rms (two blocks of ~114 A_rms)
I_PK = I_RMS * math.sqrt(2)
F_SW = 50e3
P_LEG = P_SYS / (3 * N_SM)                       # 6.25 kW per leg
I_PF = {pf: P_SYS / (3 * N_SM * V_PH * pf) for pf in (0.85, 0.9, 0.95, 1.0)}
T_COOL = 60.0
VDS_LIM, TJ_LIM = 90.0, 125.0
L_EST = 0.5e-9                                   # first-cut loop inductance per cell incl. MLCC ESL
RDS25 = S["Rds_25_typ"]
EOSS = S["Eoss_75"]
QG, VG = S["Qg_typ"], 6.29
# junction-coolant thermal resistance per device (top-side cooling), see RTH_STACK
RTH_STACK = [("$R_{\\theta JC}$ (top), datasheet", 0.2),
             ("TIM 1, 50 $\\mu$m, 3 W/mK, 15 mm$^2$", 0.05e-3 / (3 * 15e-6)),
             ("AlN 0.635 mm, 170 W/mK, 25 mm$^2$", 0.635e-3 / (170 * 25e-6)),
             ("TIM 2, 50 $\\mu$m, 3 W/mK, 50 mm$^2$", 0.05e-3 / (3 * 50e-6)),
             ("cold plate, $h$ = 10 kW/m$^2$K, 100 mm$^2$", 1 / (1e4 * 100e-6)),
             ("coupling to neighbours, coolant rise (+20 %)", 0.0)]
_s = sum(v for _, v in RTH_STACK)
RTH_STACK[-1] = (RTH_STACK[-1][0], 0.2 * _s)
RTH = round(sum(v for _, v in RTH_STACK), 1)     # ~3.4 K/W, used for the decisions
RTH_SET = [(2.1, "2.1 K/W (optimistic)", C["green"]), (RTH, "%.1f K/W (AlN + cold plate)" % RTH, C["red"]),
           (8.0, "8 K/W (gap pad)", C["purple"])]
NUM.update(I_rms_leg=I_RMS, I_pk=I_PK, P_leg=P_LEG, V_ph=V_PH, I_vs_pf=I_PF, Rth=RTH,
           Rth_stack=[(k, v) for k, v in RTH_STACK])
print("I_rms per leg %.1f A, peak %.1f A, P_leg %.0f W, R_th %.2f K/W" % (I_RMS, I_PK, P_LEG, RTH),
      {k: round(v, 1) for k, v in I_PF.items()})


def rds(tj):
    return RDS25 * rds_temperature_factor(min(max(tj, 0.0), 150.0))


def save(fig, name):
    fig.savefig(os.path.join(FIG, name + ".pdf"))
    fig.savefig(os.path.join(FIG, name + ".png"), dpi=200)
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------------------------------------------- 1. V_m
def ana(i_dev, rgon, rgoff=0.0):
    r = calculate(LossInputs(vbus=75, ac_rms=i_dev / math.sqrt(2), fsw=F_SW, rg_on=rgon, rg_off=rgoff,
                             driver_source_r=0.85, driver_sink_r=0.35, driver_source_a=4, driver_sink_a=8,
                             loop_inductance_nh=0.5, waveform_current_a=i_dev, case_c=60))
    return r["didt_on_a_ns"], r["didt_off_a_ns"]


ANA_PTS = {(rg, i): ana(i, rg) for rg in (0.5, 2.0) for i in (40, 80)}
DIDT_FAST = 30.0                                  # A/ns, "fast switching" design value
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.2), gridspec_kw=dict(wspace=0.32, width_ratios=[1.1, 1]))
ax = axs[0]
dd = np.linspace(0, 80, 100)
for L, c in ((0.3, C["green"]), (0.5, C["red"]), (0.8, C["blue"])):
    ax.plot(dd, VDS_LIM - L * dd, color=c)
    xt = min(79, (VDS_LIM - 46) / L)
    es.tag(ax, xt, VDS_LIM - L * xt + 1.5, "%.1f nH" % L, c, ha="right", va="bottom", fontsize=6.5)
ax.axhline(75, color="k", lw=0.6, ls=":")
ax.plot(DIDT_FAST, VDS_LIM - 0.5 * DIDT_FAST, "*", color=C["red"], mec="k", mew=0.4, ms=9)
es.tag(ax, DIDT_FAST + 2, 77, "0.5 nH, 30 A/ns $\\rightarrow$ 75 V", C["red"], fontsize=6.5, va="bottom")
for (rg, i), (on, off) in ANA_PTS.items():
    if i == 40:
        ax.axvline(on, color="0.5", lw=0.6, ls="--")
        es.tag(ax, on + 0.8, 46, "$R_g$ = %g $\\Omega$" % rg, "0.35", fontsize=5.6, rotation=90, va="bottom")
ax.text(2, 42, "turn-on $di/dt$ at 40 A per device,\nanalytical gate-charge model", fontsize=5.6, color="0.35")
ax.set_xlim(0, 80)
ax.set_ylim(40, 95)
ax.set_xlabel("$di/dt$ (A/ns)")
ax.set_ylabel(r"max. $V_m$ = 90 V $- L_\mathrm{loop}\,di/dt$ (V)")
es.panel(ax, "(a)", dx=-0.2, dy=-0.2)
ax = axs[1]
Ns = np.arange(12, 21)
vmN = VBUS / Ns
cols = []
for n_, v in zip(Ns, vmN):
    ok_v = v <= 75.0 + 1e-9
    cols.append(C["green"] if (ok_v and n_ % 2 == 0) else (C["yellow"] if ok_v else C["grey"]))
ax.bar(Ns, vmN, 0.65, color=[(*c, 0.75) for c in cols], edgecolor="k", lw=0.4)
for n_, v in zip(Ns, vmN):
    ax.text(n_, v + 1, "%.1f" % v if abs(v - round(v)) > 0.05 else "%.0f" % v, ha="center", fontsize=5.6)
ax.axhline(75, color=C["red"], ls="--", lw=0.8)
ax.bar([16], [75], 0.65, fill=False, edgecolor=C["red"], lw=1.4)
ax.set_xticks(Ns)
ax.set_xlabel("number of submodules $N$")
ax.set_ylabel("$V_m$ = 1200 V / $N$ (V)")
ax.set_ylim(0, 115)
ax.grid(axis="x", visible=False)
es.tag(ax, 11.6, 108, "grey: $V_m$ > 75 V   yellow: odd $N$   green: allowed", "0.3", fontsize=5.6)
es.panel(ax, "(b)", dx=-0.2, dy=-0.2)
save(fig, "flow_vm")
NUM["vm"] = dict(ana={"%g/%d" % k: v for k, v in ANA_PTS.items()}, didt=DIDT_FAST)

# ---------------------------------------------------------------------------------------------------- 1b. parts vs V_m
vms = np.array([50.0, 60.0, 66.7, 75.0, 85.7])
N = VBUS / vms
trans = N * 3 * 2 * 4
drivers = N * 3 * 2
p_cond_rel = N / 16.0
fig, ax = plt.subplots(figsize=(3.4, 2.2))
x = np.arange(len(vms))
ax.bar(x - 0.2, trans, 0.4, color=(*C["blue"], 0.75), edgecolor="k", lw=0.4, label="EPC2361")
ax.bar(x + 0.2, drivers * 2, 0.4, color=(*C["green"], 0.75), edgecolor="k", lw=0.4, label="driver ICs + iso. supplies")
for xi, t in zip(x, trans):
    ax.text(xi - 0.2, t + 12, "%d" % round(t), ha="center", fontsize=5.6)
ax.set_xticks(x)
ax.set_xticklabels(["%g V\n$N$=%d" % (round(v, 1), round(n)) for v, n in zip(vms, N)], fontsize=6)
ax.set_ylabel("parts per inverter (4 per switch)")
ax.set_ylim(0, 700)
ax.legend(loc="upper right", fontsize=5.8)
ax.grid(axis="x", visible=False)
ax2 = ax.twinx()
ax2.plot(x, p_cond_rel, "-s", color=C["red"], ms=3)
ax2.set_ylim(0, 2)
ax2.set_ylabel("conduction loss rel. to $N$ = 16", color=C["red"])
ax2.tick_params(axis="y", colors=C["red"])
ax2.grid(False)
save(fig, "flow_cells")

# ---------------------------------------------------------------------------------------------------- 2. power loop
L_CU = 0.31e-9                                    # vertical loop over 0.1 mm, vias and pads (first-cut estimate)
ESL = {"0805, 1 $\\mu$F": 0.48e-9, "1210, 10 $\\mu$F": 0.5e-9, "0402, 0.1 $\\mu$F": 0.3e-9}
nc = np.arange(1, 13)
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.1), gridspec_kw=dict(wspace=0.35, width_ratios=[1.2, 1]))
ax = axs[0]
for (lab, esl), c in zip(ESL.items(), (C["red"], C["blue"], C["green"])):
    ax.plot(nc, (L_CU + esl / nc) * 1e9, "-o", color=c, ms=2.5, label=lab)
ax.axhline(0.5, color="k", ls="--", lw=0.8)
ax.axhline(L_CU * 1e9, color="0.4", ls=":", lw=0.8)
es.tag(ax, 12, 0.52, "0.5 nH estimate", "k", ha="right", va="bottom", fontsize=6)
es.tag(ax, 12, L_CU * 1e9 - 0.02, "PCB copper only", "0.35", ha="right", va="top", fontsize=6)
ax.set_xlabel("local MLCCs per cell")
ax.set_ylabel("$L_\\mathrm{loop}$ per cell (nH)")
ax.set_ylim(0.2, 0.9)
ax.set_xlim(0.5, 12.5)
ax.legend(loc="upper right", fontsize=5.8)
es.panel(ax, "(a)", dx=-0.2, dy=-0.2)
ax = axs[1]
parts = [("PCB copper\n(0.1 mm, vias)", L_CU * 1e9, C["blue"]), ("MLCC ESL\n(6 $\\times$ 0805)", 0.48 / 6, C["red"]),
         ("package\n(in model)", 0.0, C["grey"])]
left = 0
for lab, v, c in parts[:2]:
    ax.barh(0, v, left=left, color=c, alpha=0.8, edgecolor="k", lw=0.4, height=0.6)
    ax.text(left + v / 2, 0.36, lab, ha="center", va="bottom", fontsize=5.8)
    left += v
ax.barh(0, 0.5 - left, left=left, color="w", edgecolor="k", lw=0.4, hatch="////", height=0.6)
ax.text(left + (0.5 - left) / 2, -0.36, "margin to\n0.5 nH", ha="center", va="top", fontsize=5.8)
ax.set_xlim(0, 0.55)
ax.set_ylim(-1, 1)
ax.set_yticks([])
ax.set_xlabel("loop inductance per cell (nH)")
ax.grid(axis="y", visible=False)
es.panel(ax, "(b)", dx=-0.05, dy=-0.2)
save(fig, "flow_loop")
NUM["loop"] = dict(L_cu=L_CU, L6=L_CU + 0.48e-9 / 6, L1=L_CU + 0.48e-9, L2=L_CU + 0.24e-9, L4=L_CU + 0.12e-9)

# ---------------------------------------------------------------------------------------------------- 3. one device (lumped)
lm, lst = fl["lumped"]["meas"], fl["lumped"]["steps"]
LL = sorted(set(round(s["lloop"], 12) for s in lst))


def lcol(L, key):
    idx = [k for k, s in enumerate(lst) if abs(s["lloop"] - L) < 1e-13]
    return np.abs(np.array([lm["iload"][k] for k in idx])), np.array([lm[key][k] for k in idx])


I05, Eon05 = lcol(L_EST, "eon")
_, Eoff05 = lcol(L_EST, "eoff")
pon1, poff1 = np.polyfit(I05, Eon05, 2), np.polyfit(I05, Eoff05, 2)
fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.0), gridspec_kw=dict(wspace=0.45))
ax = axs[0]
for L, c in zip(LL, (C["green"], C["red"], C["blue"])):
    ii, v = lcol(L, "vdsl_pk")
    ax.plot(ii, v, "-o", color=c, ms=2.5)
    es.tag(ax, ii[-1] - 5, v[-1], "%.1f nH" % (L * 1e9), c, ha="right", fontsize=6)
ax.axhline(VDS_LIM, color="k", ls="--", lw=0.8)
ax.axhline(100, color="k", lw=0.8)
es.tag(ax, 5, VDS_LIM + 2, "90 V", "k", fontsize=6, va="bottom")
ax.set_xlabel("current per device (A)")
ax.set_ylabel(r"peak $V_\mathrm{DS}$ at turn-off (V)")
ax.set_xlim(0, 340)
ax.set_ylim(70, 200)
es.panel(ax, "(a)", dx=-0.3, dy=-0.2)
ax = axs[1]
ii = np.linspace(0, 330, 100)
ax.plot(I05, Eon05 * 1e6, "o", color=C["red"], ms=3)
ax.plot(I05, Eoff05 * 1e6, "s", color=C["blue"], ms=3)
ax.plot(ii, np.polyval(pon1, ii) * 1e6, color=C["red"], lw=0.8)
ax.plot(ii, np.polyval(poff1, ii) * 1e6, color=C["blue"], lw=0.8)
es.tag(ax, 30, 200, "$E_\\mathrm{on}$", C["red"])
es.tag(ax, 240, 50, "$E_\\mathrm{off}$", C["blue"])
ax.set_xlabel("current per device (A)")
ax.set_ylabel(r"energy per device ($\mu$J), 0.5 nH")
ax.set_xlim(0, 340)
es.panel(ax, "(b)", dx=-0.3, dy=-0.2)
ax = axs[2]
_, don = lcol(L_EST, "didt_on")
_, doff = lcol(L_EST, "didt_off")
ax.plot(I05[1:], don[1:] / 1e9, "-o", color=C["red"], ms=3)
ax.plot(I05, -doff / 1e9, "-s", color=C["blue"], ms=3)
es.tag(ax, 330, don[-1] / 1e9 + 8, "turn-on", C["red"], ha="right", fontsize=6)
es.tag(ax, 200, -doff[5] / 1e9 + 25, "turn-off", C["blue"], ha="right", fontsize=6)
ax.set_xlabel("current per device (A)")
ax.set_ylabel("$|di/dt|$ (A/ns), 0.5 nH")
ax.set_xlim(0, 340)
es.panel(ax, "(c)", dx=-0.3, dy=-0.2)
save(fig, "flow_single")
vpk05 = lcol(L_EST, "vdsl_pk")[1]
NUM["single"] = dict(I=I05.tolist(), Eon=Eon05.tolist(), Eoff=Eoff05.tolist(), vpk05=vpk05.tolist(),
                     vpk={"%.1f" % (L * 1e9): lcol(L, "vdsl_pk")[1].tolist() for L in LL},
                     didt_on=(don / 1e9).tolist(), didt_off=(-doff / 1e9).tolist())

# ---------------------------------------------------------------------------------------------------- 4. n in parallel
th = np.linspace(0, np.pi, 2001)
i_abs = I_PK * np.sin(th)


def leg(n, f=F_SW, rth=RTH, i_pk=I_PK):
    """Loss per leg with n identical cells (one device each) per switch, T_j iterated with R_DS(on)(T)."""
    ia = i_pk * np.sin(th)
    irms = i_pk / math.sqrt(2)
    sw = n * f * float(np.mean(np.polyval(pon1, ia / n) + np.polyval(poff1, ia / n))) + n * EOSS * f
    dead = 2 * f * S["t_dead"] * float(np.mean(ia * (S["Vsd0"] + S["Rsd"] / n * ia)))
    gate = 2 * n * QG * VG * f
    tj = T_COOL
    for _ in range(80):
        cond = irms ** 2 * rds(tj) / n
        pdev = (cond + sw + dead) / (2 * n)
        tj_new = T_COOL + rth * pdev
        if tj_new > 200:
            tj = 200.0
            break
        tj = tj_new
    vpk = float(np.interp(i_pk / n, I05, vpk05))
    tot = cond + sw + dead + gate
    return dict(n=n, f=f, rth=rth, cond=cond, cond25=irms ** 2 * RDS25 / n, sw=sw, dead=dead, gate=gate, tot=tot,
                pdev=pdev, tj=tj, eta=1 - tot / P_LEG, vpk=vpk, drivers=2 * n)


ns = np.arange(1, 9)
R = [leg(int(n)) for n in ns]
fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.1), gridspec_kw=dict(wspace=0.55))
ax = axs[0]
bottom = np.zeros(len(ns))
for k, lab, c in (("cond", "conduction ($T_j$)", C["blue"]), ("sw", "switching", C["red"]),
                  ("dead", "dead time", C["yellow"]), ("gate", "gate", C["dred"])):
    v = np.array([r[k] for r in R])
    ax.bar(ns, v, 0.6, bottom=bottom, color=c, alpha=0.85, edgecolor="k", lw=0.3, label=lab)
    bottom += v
ax.plot(ns, [r["cond25"] for r in R], "k_", ms=9, mew=1.2, label="conduction at 25 $^\\circ$C")
ax.set_xticks(ns)
ax.set_xlabel("EPC2361 per switch $n$")
ax.set_ylabel("semiconductor loss per leg (W)")
ax.set_ylim(0, 80)
ax.legend(loc="upper right", fontsize=5.6)
ax.grid(axis="x", visible=False)
es.panel(ax, "(a)", dx=-0.3, dy=-0.2)
ax = axs[1]
for rth, lab, c in RTH_SET:
    tjs = [leg(int(n), rth=rth)["tj"] for n in ns]
    ax.plot(ns, tjs, "-o", color=c, ms=2.5, label=lab)
ax.axhline(TJ_LIM, color="k", ls="--", lw=0.8)
ax.set_ylim(55, 180)
ax.set_xticks(ns)
ax.set_xlabel("EPC2361 per switch $n$")
ax.set_ylabel("$T_j$ ($^\\circ$C), coolant 60 $^\\circ$C")
ax.legend(loc="upper right", fontsize=5.4)
es.panel(ax, "(b)", dx=-0.3, dy=-0.2)
ax = axs[2]
for L, c in zip(LL, (C["green"], C["red"], C["blue"])):
    ii, v = lcol(L, "vdsl_pk")
    ax.plot(ns, [float(np.interp(I_PK / n, ii, v)) for n in ns], "-o", color=c, ms=2.5, label="%.1f nH" % (L * 1e9))
ax.axhline(VDS_LIM, color="k", ls="--", lw=0.8)
ax.set_xticks(ns)
ax.set_xlabel("EPC2361 per switch $n$")
ax.set_ylabel(r"peak $V_\mathrm{DS}$ at $I_\mathrm{pk}/n$ (V)")
ax.set_ylim(75, 140)
ax.legend(loc="upper right", fontsize=5.6)
es.panel(ax, "(c)", dx=-0.3, dy=-0.2)
save(fig, "flow_npar")
NUM["npar"] = R
NUM["npar_rth"] = {"%.1f" % rth: [leg(int(n), rth=rth) for n in ns] for rth, _, _ in RTH_SET}
for r in R:
    print("n=%d tot %.1f W (cond %.1f @Tj, %.1f @25C, sw %.1f) eta %.3f %%, Tj %.0f C, P_dev %.1f W, Vpk %.1f V" % (
        r["n"], r["tot"], r["cond"], r["cond25"], r["sw"], 100 * r["eta"], r["tj"], r["pdev"], r["vpk"]))

# ---------------------------------------------------------------------------------------------------- 5. loss over the period
n4 = leg(4)
deg = np.linspace(0, 360, 721)
ii = I_PK * np.abs(np.sin(np.radians(deg)))
p_sw = 4 * F_SW * (np.polyval(pon1, ii / 4) + np.polyval(poff1, ii / 4) + EOSS)
p_cd = ii ** 2 * rds(n4["tj"]) / 4
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.1), gridspec_kw=dict(wspace=0.35, width_ratios=[1.3, 1]))
ax = axs[0]
ax.fill_between(deg, 0, p_cd, color=C["blue"], alpha=0.35, lw=0)
ax.fill_between(deg, p_cd, p_cd + p_sw, color=C["red"], alpha=0.35, lw=0)
ax.plot(deg, p_cd, color=C["blue"], lw=0.9)
ax.plot(deg, p_cd + p_sw, color=C["red"], lw=0.9)
ax.axhline(np.mean(p_cd), color=C["blue"], ls="--", lw=0.8)
ax.axhline(np.mean(p_cd + p_sw), color=C["red"], ls="--", lw=0.8)
es.tag(ax, 180, np.mean(p_cd) - 0.6, "avg. conduction %.1f W" % np.mean(p_cd), C["blue"], fontsize=6, ha="center", va="top",
       bbox=dict(fc="w", ec="none", pad=0.3))
es.tag(ax, 180, np.mean(p_cd + p_sw) + 0.6, "avg. total %.1f W (switching %.1f W)" % (np.mean(p_cd + p_sw), np.mean(p_sw)),
       C["red"], fontsize=6, ha="center", va="bottom", bbox=dict(fc="w", ec="none", pad=0.3))
es.tag(ax, 90, max(p_cd) * 0.25, "conduction", C["blue"], ha="center", fontsize=6.5)
es.tag(ax, 90, max(p_cd) + max(p_sw) * 0.5, "switching", C["red"], ha="center", fontsize=6.5)
ax2 = ax.twinx()
ax2.plot(deg, I_PK * np.sin(np.radians(deg)), color="0.4", lw=0.7)
ax2.set_ylim(-400, 400)
ax2.set_ylabel("leg current (A)", color="0.4")
ax2.tick_params(axis="y", colors="0.4")
ax2.grid(False)
ax.set_xlim(0, 360)
ax.set_xticks([0, 90, 180, 270, 360])
ax.set_ylim(0, max(p_cd + p_sw) * 1.15)
ax.set_xlabel("line angle (deg)")
ax.set_ylabel("loss per leg, 50 kHz avg. (W)")
es.panel(ax, "(a)", dx=-0.15, dy=-0.2)
ax = axs[1]
tt = np.linspace(25, 150, 60)
for n, c in ((2, C["purple"]), (4, C["red"]), (6, C["blue"])):
    ax.plot(tt, [I_RMS ** 2 * rds(t) / n for t in tt], color=c)
    r = leg(n)
    ax.plot(r["tj"], r["cond"], "o", color=c, mec="k", mew=0.4, ms=4)
    es.tag(ax, 150, I_RMS ** 2 * rds(150) / n, " $n$=%d" % n, c, fontsize=6)
ax.set_xlim(25, 165)
ax.set_xlabel("$T_j$ ($^\\circ$C)")
ax.set_ylabel("conduction loss per leg (W)")
ax.text(30, 0.92 * I_RMS ** 2 * rds(150) / 2, "dots: operating point\n(%.1f K/W, 60 $^\\circ$C)" % RTH, fontsize=5.8, va="top")
es.panel(ax, "(b)", dx=-0.2, dy=-0.2)
save(fig, "flow_wave")
NUM["wave"] = dict(p_cond=float(np.mean(p_cd)), p_sw=float(np.mean(p_sw)), tj4=n4["tj"])

# ---------------------------------------------------------------------------------------------------- 6. switching frequency
fs = np.linspace(10e3, 150e3, 57)
I_B = I_RMS / 2                                   # per building block
k_i = I_B / S["I_rms"]
c_req = sz["C_eff_per_block_shared_uF"] * 1e-6 * k_i * 50e3 / fs     # 4 % voltage ripple, scaled from 100 A
bank = sz["bank"]
n_v = np.maximum((c_req - bank["hf_n"] * bank["hf_C_eff_each"]) / bank["bulk_C_eff_each"], 0)
I_CAP = 2.5
n_i = sz["I_leg_hf_rated"] * k_i / I_CAP
L_SIG = (10e-6, 25e-6, 50e-6)
fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.1), gridspec_kw=dict(wspace=0.5))
ax = axs[0]
for n, c in ((3, C["purple"]), (4, C["red"]), (6, C["blue"])):
    ax.plot(fs / 1e3, [100 * leg(n, f=f)["eta"] for f in fs], color=c, label="$n$ = %d" % n)
ax.axhline(99.5, color="k", ls="--", lw=0.8)
ax.set_xlabel("$f_\\mathrm{sw}$ (kHz)")
ax.set_ylabel("semicond. efficiency (%)")
ax.set_ylim(99.0, 100)
ax.legend(loc="lower left", fontsize=5.8)
es.panel(ax, "(a)", dx=-0.3, dy=-0.2)
ax = axs[1]
ax.fill_between(fs / 1e3, np.maximum(n_v, n_i), 120, color=C["green"], alpha=0.12, lw=0)
ax.plot(fs / 1e3, n_v, color=C["blue"])
ax.axhline(n_i, color=C["red"])
ax.plot(50, bank["bulk_n"], "*", color="k", ms=8)
es.tag(ax, 60, 95, "$\\Delta v_\\mathrm{pp}$ = 4 %", C["blue"], fontsize=6)
es.tag(ax, 12, n_i - 2, "ripple current, 2.5 A per MLCC", C["red"], ha="left", va="top", fontsize=6)
es.tag(ax, 56, bank["bulk_n"] + 4, "Rev A: 24", "k", fontsize=6, va="bottom")
ax.set_xlabel("$f_\\mathrm{sw}$ (kHz)")
ax.set_ylabel("10 $\\mu$F 1210 MLCCs per block")
ax.set_ylim(0, 120)
es.panel(ax, "(b)", dx=-0.3, dy=-0.2)
ax = axs[2]
for L, c in zip(L_SIG, (C["red"], C["yellow"], C["blue"])):
    ax.plot(fs / 1e3, VM / (4 * L * fs) / I_PK * 100, color=c, label="$L_\\sigma$ = %g $\\mu$H" % (L * 1e6))
ax.axhline(10, color="k", ls="--", lw=0.8)
ax.set_xlabel("$f_\\mathrm{sw}$ (kHz)")
ax.set_ylabel("$\\Delta i_\\mathrm{pp}$ / $I_\\mathrm{pk}$ (%)")
ax.set_ylim(0, 40)
ax.legend(loc="upper right", fontsize=5.6)
es.panel(ax, "(c)", dx=-0.3, dy=-0.2)
save(fig, "flow_fsw")
f_cross = float(np.interp(-n_i, -n_v, fs))
NUM["fsw"] = dict(n_v50=float(np.interp(50e3, fs, n_v)), n_i=float(n_i), f_cross=f_cross,
                  eta4={"%d" % (f / 1e3): leg(4, f=f)["eta"] for f in (20e3, 50e3, 100e3)},
                  ripple={"%g" % (L * 1e6): VM / (4 * L * 50e3) for L in L_SIG})
print("DC link per block: n_v(50k) %.1f, n_i %.1f, crossing %.0f kHz" % (NUM["fsw"]["n_v50"], n_i, f_cross / 1e3))

# ---------------------------------------------------------------------------------------------------- 6b. bypass capacitors
# per cell: edge charge and hand-over of the load-current step to the bank through L_b
I_DEV = I_PK / 4                                   # peak current per device (n = 4)
DIDT_ON, DVDT = 45.0, 15.0                         # A/ns (LTspice turn-on, driver limited), V/ns
QOSS = S["Qoss_75"]
t_ri, t_vf = I_DEV / DIDT_ON, VM / DVDT            # ns
dQ = I_DEV * (t_ri / 2 + t_vf) * 1e-9 + QOSS
C_EFF_PART = 0.45e-6                               # 1 uF 100 V X7S 0805 at 75 V
dv = np.linspace(0.5, 5.0, 100)
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.1), gridspec_kw=dict(wspace=0.38))
ax = axs[0]
for Lb, c in ((0.5e-9, C["green"]), (1e-9, C["red"]), (2e-9, C["blue"])):
    ax.plot(dv, Lb * (I_DEV / dv) ** 2 * 1e6, color=c, label="hand-over, $L_b$ = %g nH" % (Lb * 1e9))
ax.plot(dv, dQ / dv * 1e6, color="k", ls="--", label="edge charge")
ax.axhline(6 * C_EFF_PART * 1e6, color=C["purple"], lw=0.8)
es.tag(ax, 4.9, 6 * C_EFF_PART * 1e6 + 0.15, "6 $\\times$ 1 $\\mu$F 0805 (2.7 $\\mu$F eff.)", C["purple"], ha="right",
       va="bottom", fontsize=6)
ax.set_xlabel(r"allowed dip $\Delta V$ (V)")
ax.set_ylabel(r"$C_\mathrm{bp,min}$ per cell ($\mu$F eff.)")
ax.set_ylim(0, 8)
ax.set_xlim(0.5, 5)
ax.legend(loc="upper right", fontsize=5.6)
es.panel(ax, "(a)", dx=-0.2, dy=-0.2)
ax = axs[1]
cb = np.linspace(0.5e-6, 15e-6, 100)
for Lb, c in ((0.5e-9, C["green"]), (1e-9, C["red"]), (2e-9, C["blue"])):
    ax.plot(cb * 1e6, 1 / (2 * np.pi * np.sqrt(Lb * cb)) / 1e6, color=c, label="$L_b$ = %g nH" % (Lb * 1e9))
ax.axvline(6 * C_EFF_PART * 1e6, color=C["purple"], lw=0.8)
ax.set_yscale("log")
ax.set_xlabel(r"$C_\mathrm{bp}$ per cell ($\mu$F eff.)")
ax.set_ylabel(r"bypass--bank resonance $f_r$ (MHz)")
ax.legend(loc="upper right", fontsize=5.6)
es.panel(ax, "(b)", dx=-0.2, dy=-0.2)
save(fig, "flow_bypass")
NUM["bypass"] = dict(I_dev=I_DEV, t_ri=t_ri, t_vf=t_vf, dQ=dQ, C_edge_15=dQ / 1.5, C_ho_1n_15=1e-9 * (I_DEV / 1.5) ** 2,
                     C_6=6 * C_EFF_PART, f_r=1 / (2 * np.pi * np.sqrt(1e-9 * 6 * C_EFF_PART)), n_esl=4,
                     I_oss=QOSS / VM * DVDT * 1e9)
print("bypass:", {k: (round(v * 1e6, 3) if k.startswith("C") or k == "dQ" else round(v, 3)) for k, v in NUM["bypass"].items()})

# ---------------------------------------------------------------------------------------------------- 7. one block
rs = json.load(open(os.path.join(ROOT, "reports", "building-block", "data", "results.json")))
pon2, poff2 = np.array(rs["energy"]["fit_on"]), np.array(rs["energy"]["fit_off"])


def block(i_rms, rth=RTH):
    ib = i_rms * math.sqrt(2) * np.sin(th)
    sw = F_SW * float(np.mean(np.polyval(pon2, ib) + np.polyval(poff2, ib))) + 2 * EOSS * F_SW
    dead = 2 * F_SW * S["t_dead"] * float(np.mean(ib * (S["Vsd0"] + S["Rsd"] / 2 * ib)))
    gate = (sz["P_gate_50k"] + sz["P_ldo_50k"])
    k = (i_rms / S["I_rms"]) ** 2
    cu, cap = (rs["P_cu"] + rs["P_cu_hf"]) * k, rs["P_cap_net"] * k
    tj = T_COOL
    for _ in range(60):
        cond = i_rms ** 2 * rds(tj) / 2
        pdev = (cond + sw + dead) / 4
        tj = T_COOL + rth * pdev
    tot = cond + sw + dead + gate + cu + cap
    return dict(I=i_rms, cond=cond, sw=sw, dead=dead, gate=gate, cu=cu, cap=cap, tot=tot, pdev=pdev, tj=tj,
                eta=1 - tot / (P_LEG / 2))


NUM["block"] = {"%.2f" % pf: block(i / 2) for pf, i in I_PF.items()}
for pf, b in NUM["block"].items():
    print("block pf %s: I %.1f A, cond %.1f sw %.1f dead %.2f cu %.1f cap %.2f -> %.1f W, eta %.2f %%, P_dev %.2f W, Tj %.0f C" % (
        pf, b["I"], b["cond"], b["sw"], b["dead"], b["cu"], b["cap"], b["tot"], 100 * b["eta"], b["pdev"], b["tj"]))

# ---------------------------------------------------------------------------------------------------- 8. two blocks
if "two" in fl:
    tm, tst = fl["two"]["meas"], fl["two"]["steps"]
    NUM["two"] = dict(steps=tst, meas=tm)
    col, steps = read_raw(os.path.join(SP, "FLOW_two.raw"))
    T1 = 0.5e-6 + 10.667e-6
    T2 = T1 + 1e-6
    fig = plt.figure(figsize=(6.3, 2.1))
    sel = [k for k, s in enumerate(tst) if abs(s["lx"] - 5e-9) < 1e-12]
    cols = {0.0: "k", 2e-9: C["blue"], 5e-9: C["red"]}
    for j, (tc, lab) in enumerate(((T1, "QL turn-off"), (T2, "QL turn-on"))):
        ax = fig.add_axes([0.07 + j * 0.25, 0.2, 0.2, 0.72])
        for k in sel:
            a = steps[k]
            t = a[:, 0]
            m = (t > tc - 5e-9) & (t < tc + 60e-9)
            c = cols.get(round(tst[k]["dly"], 12), "0.5")
            ax.plot((t[m] - tc) * 1e9, -a[m, col["i(la1)"]], color=c, lw=0.9)
            ax.plot((t[m] - tc) * 1e9, -a[m, col["i(la2)"]], color=c, lw=0.9, ls="--")
        ax.set_xlabel("time (ns)")
        if j == 0:
            ax.set_ylabel("block AC current (A)")
        ax.set_xlim(-5, 60)
        ax.text(0.03, 0.97, lab + ", $L_x$ = 5 nH", transform=ax.transAxes, fontsize=6, va="top",
                bbox=dict(fc="w", ec="none", pad=0.5))
        es.panel(ax, "(%s)" % "ab"[j], dx=-0.25 if j == 0 else -0.12, dy=-0.2)
    ax.text(1.02, 0.75, "solid: block 1\ndashed: block 2\n(delayed)", transform=ax.transAxes, fontsize=6)
    for dl, c in ((0, "k"), (2, C["blue"]), (5, C["red"])):
        ax.plot([], [], color=c, label="$\\Delta t$ = %d ns" % dl)
    ax.legend(loc="lower right", fontsize=5.5)
    ax = fig.add_axes([0.70, 0.2, 0.29, 0.72])
    lbl, d_on, d_off = [], [], []
    for k, s in enumerate(tst):
        lbl.append("%g ns\n%g nH" % (s["dly"] * 1e9, s["lx"] * 1e9))
        d_on.append(abs(tm["i1_on"][k]) - abs(tm["i2_on"][k]))
        d_off.append(abs(tm["i2_off"][k]) - abs(tm["i1_off"][k]))
    x = np.arange(len(tst))
    ax.bar(x - 0.2, d_on, 0.4, color=C["red"], alpha=0.8, edgecolor="k", lw=0.3, label="after turn-on")
    ax.bar(x + 0.2, d_off, 0.4, color=C["blue"], alpha=0.8, edgecolor="k", lw=0.3, label="after turn-off")
    ax.set_xticks(x)
    ax.set_xticklabels(lbl, fontsize=5.5)
    ax.set_ylabel(r"current difference between blocks (A)")
    ax.legend(loc="upper left", fontsize=5.6)
    ax.grid(axis="x", visible=False)
    es.panel(ax, "(c)", dx=-0.2, dy=-0.2)
    save(fig, "flow_twoblock")
json.dump(NUM, open(os.path.join(DATA, "flow_numbers.json"), "w"), indent=1, default=float)

"""
Figures and numbers for the methodology-style design report (reports/design-report-v2), structured after the
reviewed literature (Tran 2025 JESTPE, Zou 2025 TPEL, Cooke 2026, Wattenberg 2023, Lu 2017, Brothers 2019, ...):
  benchmark       power-loop inductance of published paralleled-GaN half bridges vs switched current
  loop_vs_h       analytical vs Q3D loop inductance vs L1-L2 dielectric
  overshoot_map   V_DS overshoot design space (L_loop x di/dt per cell) with device limits
  rg_window       gate-resistor design window (damping lower bound, Miller upper bound)
  sharing         current-sharing sensitivity (tornado), from the 2 x EPC2361 LTspice study
  loss_stack      loss breakdown vs f_sw
  dclink_space    DC-link: C_v (ripple voltage) vs C_i (ripple current) bound and bank area vs f_sw
  eta_rho         efficiency - power density design space vs f_sw (Pareto), inverter leg
  thermal_req     required heat-sink thermal resistance vs f_sw
  margins         design utilisation radar (value / limit)

    python scripts/design_report_v2.py -> reports/design-report-v2/figures/*.pdf|png, numbers.tex
"""
import json
import math
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BB = os.path.join(ROOT, "reports", "building-block", "data")
OUT = os.path.join(ROOT, "reports", "design-report-v2")
FIG = os.path.join(OUT, "figures")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3, "legend.fontsize": 7.5})

sz = json.load(open(os.path.join(BB, "sizing.json")))
rs = json.load(open(os.path.join(BB, "results.json")))
S = sz["spec"]
VDC, I_RMS, I_PK, P_RATED = S["Vdc"], S["I_rms"], sz["I_pk"], sz["P_rated"]
mac = {}


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, name + ".pdf"))
    fig.savefig(os.path.join(FIG, name + ".png"), dpi=140)
    plt.close(fig)


# EPC2361 datasheet (Rev. July 2026)
CISS, CRSS, RG_INT = 3.599e-9, 13e-12, 0.4
VTH_MIN, VTH_TYP = 0.8, 1.1
COSS50 = 1.019e-9
RJC = 0.2
# design values (building-block study)
L_CELL, L_GATE = 0.374e-9, 1.70e-9      # Q3D commutation loop per cell (copper + MLCC ESL), gate loop per FET
RGON, RPU, RPD = 2.0, 0.6, 0.2
VDS_PK_160 = 85.1                      # QL, LTspice at 160 A with Q3D parasitics
DVDT_OFF = rs["rg_choice"]["dvdt_off"]  # V/ns
DVDT_ON = rs["rg_choice"]["dvdt_on"]

# ------------------------------------------------------------------ 1. literature benchmark
# (label, devices per switch, voltage class [V], switched / peak current [A], power-loop L [nH], note)
lit = [
    ("Lu & Chen 2017 (PCB, 4x GS66516T)", 4, 650, 240, 0.70, "Q3D"),
    ("Tran 2025 (IMS hybrid, 4x GS61008P)", 4, 100, 328, 1.14, "Q3D; 1.175 meas."),
    ("Brothers 2019 (commercial DBC module)", 3, 100, 292, 11.4, "CST, closest dies"),
    ("Cooke 2026 (PCB, 8x EPC2304)", 8, 200, 155, 0.34, "analytical, short path"),
    ("Zou 2025 (PCB+Cu blocks, 3x V08TC65)", 3, 650, 370, 6.4, "FEA"),
    ("Rahman 2025 (multilayer, 2x GS-065-150)", 2, 650, 300, 5.52, "Q3D"),
    ("Novo 2024 (VisIC VM022, 4x D3GaN)", 4, 650, 495, 3.9, "measured"),
    ("Satpathy 2022 (3L-ANPC, 2x GS66516B)", 2, 650, 68, 6.3, "Q3D, short loop"),
]
fig, ax = plt.subplots(figsize=(7.2, 3.9))
for lab, n, v, i, l, note in lit:
    c = "C0" if v <= 200 else "C1"
    ax.scatter(i, l, s=30 + 12 * n, color=c, alpha=0.75, edgecolor="k", lw=0.5)
    ax.annotate(lab.split(" (")[0], (i, l), textcoords="offset points", xytext=(6, -3), fontsize=7)
ax.scatter(I_PK, L_CELL * 1e9, s=30 + 12 * 2, marker="*", color="C3", edgecolor="k", lw=0.6, zorder=5)
ax.annotate("this work (Q3D, per commutation cell, incl. ESL)", (I_PK, L_CELL * 1e9), textcoords="offset points",
            xytext=(6, -10), fontsize=7.5, color="C3", weight="bold")
ax.scatter([], [], color="C0", label="100-200 V devices")
ax.scatter([], [], color="C1", label="650 V devices")
ax.scatter([], [], color="w", edgecolor="k", s=30 + 12 * 4, label="marker size ~ devices per switch")
ax.set_yscale("log")
ax.set_xlabel("switched / peak current of the half bridge [A]")
ax.set_ylabel("power-loop inductance [nH]")
ax.set_xlim(40, 560)
ax.legend(loc="lower right")
save(fig, "benchmark")

# Device Power Utilisation, Cooke & Rogers eq. (1): DPU = Vdc Iph / (n Vds^2 / Rds) * 1e4
dpu_max = VDC * I_RMS / (2 * 100.0 ** 2 / S["Rds_25_max"]) * 1e4
dpu_typ = VDC * I_RMS / (2 * 100.0 ** 2 / S["Rds_25_typ"]) * 1e4
mac.update(DpuMax="%.2f" % dpu_max, DpuTyp="%.2f" % dpu_typ)

# ------------------------------------------------------------------ 2. loop inductance vs dielectric
h = np.array([0.075, 0.1, 0.2])            # mm, Q3D PL_A sweep (copper, single cell)
Lq = np.array([0.30, 0.34, 0.50])          # nH
l_loop, w_loop = 10.0, 9.0                 # mm, commutation path length and cell width (bb_geometry)
mu0 = 4e-7 * math.pi
k_an = mu0 * l_loop / w_loop * 1e-3 * 1e9  # nH per mm of dielectric
fit = np.polyfit(h, Lq, 1)
hh = np.linspace(0, 0.25, 50)
fig, ax = plt.subplots(figsize=(4.6, 3.3))
ax.plot(h, Lq, "o", color="C3", label="Q3D (PL_A cell)")
ax.plot(hh, np.polyval(fit, hh), "C3--", lw=1, label="linear fit: %.2f nH + %.2f nH/mm $\\cdot h$" % (fit[1], fit[0]))
ax.plot(hh, k_an * hh, "C0", label="parallel plate $\\mu_0 h l/w$ (%.2f nH/mm)" % k_an)
ax.fill_between(hh, k_an * hh, np.polyval(fit, hh), color="C7", alpha=0.15)
ax.text(0.03, 0.20, "fixed part: vias, pads,\npackage, terminals", fontsize=7)
ax.set_xlabel("L1-L2 dielectric $h$ [mm]")
ax.set_ylabel("loop inductance per cell [nH]")
ax.set_xlim(0, 0.25)
ax.set_ylim(0, 0.6)
ax.legend(loc="upper left")
save(fig, "loop_vs_h")
mac.update(KanNHmm="%.2f" % k_an, KqNHmm="%.2f" % fit[0], LfixNH="%.2f" % fit[1],
           LanCell="%.2f" % (k_an * 0.1))

# ------------------------------------------------------------------ 3. overshoot design space
didt_eff = (VDS_PK_160 - VDC) / (L_CELL * 1e9)  # A/ns, effective di/dt through one cell loop at 160 A
di = np.linspace(5, 200, 300)
Lsw = np.logspace(np.log10(0.05), np.log10(2.0), 300)
D, LL = np.meshgrid(di, Lsw)
V = VDC + LL * D
fig, ax = plt.subplots(figsize=(5.2, 3.6))
cs = ax.contourf(D, LL, V, levels=[75, 90, 100, 120, 200], colors=["#cfe8cf", "#fff2b3", "#ffd2a6", "#f4a6a6"])
cl = ax.contour(D, LL, V, levels=[90, 100, 120], colors="k", linewidths=0.8)
ax.clabel(cl, fmt={90: "90 V design", 100: "100 V rating", 120: "120 V transient"}, fontsize=7)
ax.plot(didt_eff, L_CELL * 1e9, "*", ms=12, color="C3", mec="k")
ax.annotate("this work: one cell, 160 A total\n(%.0f A/ns per cell)" % didt_eff, (didt_eff, L_CELL * 1e9), xytext=(60, 0.09),
            arrowprops=dict(arrowstyle="->", lw=0.7), fontsize=7.5)
ax.plot(2 * didt_eff, 0.34, "o", color="C0", mec="k")
ax.annotate("one loop for both FETs (PL_A,\n0.34 nH Cu), full di/dt", (2 * didt_eff, 0.34), xytext=(110, 0.6),
            arrowprops=dict(arrowstyle="->", lw=0.7), fontsize=7)
ax.set_yscale("log")
ax.set_xlabel("$di/dt$ through the commutation loop [A/ns]")
ax.set_ylabel("commutation-loop inductance $L_\\mathrm{loop}$ [nH]")
ax.set_title("$V_\\mathrm{DS,pk} \\approx V_\\mathrm{dc} + L_\\mathrm{loop}\\,di/dt$  ($V_\\mathrm{dc}$ = 75 V)", fontsize=8.5)
save(fig, "overshoot_map")
mac.update(DidtCell="%.0f" % didt_eff, LloopMaxNine="%.2f" % (15 / didt_eff))

# ------------------------------------------------------------------ 4. gate-resistor design window
Lg = np.linspace(0.2, 10, 200) * 1e-9
r_damp = lambda z: 2 * z * np.sqrt(Lg / CISS)  # noqa: E731
roff_max_min = VTH_MIN / (CRSS * DVDT_OFF * 1e9)
roff_max_typ = VTH_TYP / (CRSS * DVDT_OFF * 1e9)
r_on_tot = RGON + RG_INT + RPU
r_off_tot = 0.0 + RG_INT + 2 * RPD       # driver pull-down shared by the two Miller currents
fig, ax = plt.subplots(figsize=(5.2, 3.6))
ax.fill_between(Lg * 1e9, r_damp(0.707), 8, color="C2", alpha=0.12, label="turn-on: $\\zeta\\geq0.707$ (no $V_{GS}$ overshoot)")
ax.plot(Lg * 1e9, r_damp(0.707), "C2", lw=1.2)
ax.plot(Lg * 1e9, r_damp(1.0), "C2--", lw=0.8, label="critical damping $\\zeta = 1$")
ax.fill_between(Lg * 1e9, 0, roff_max_min, color="C0", alpha=0.12,
                label="turn-off: $R \\leq V_{th}/(C_{rss}\\,dv/dt)$ at %.0f V/ns" % DVDT_OFF)
ax.axhline(roff_max_min, color="C0", lw=1.2)
ax.axhline(roff_max_typ, color="C0", lw=0.8, ls="--")
ax.text(7.2, roff_max_min - 0.35, "$V_{th,min}$ = 0.8 V", fontsize=7, color="C0")
ax.text(7.2, roff_max_typ + 0.1, "$V_{th,typ}$ = 1.1 V", fontsize=7, color="C0")
ax.plot(L_GATE * 1e9, r_on_tot, "*", ms=12, color="C3", mec="k")
ax.annotate("turn-on: %.1f $\\Omega$ ($\\zeta$ = %.1f)" % (r_on_tot, r_on_tot / 2 * math.sqrt(CISS / L_GATE)),
            (L_GATE * 1e9, r_on_tot), xytext=(2.6, 4.4), arrowprops=dict(arrowstyle="->", lw=0.7), fontsize=7.5)
ax.plot(L_GATE * 1e9, r_off_tot, "s", ms=7, color="C3", mec="k")
ax.annotate("turn-off: %.1f $\\Omega$ ($\\zeta$ = %.2f)" % (r_off_tot, r_off_tot / 2 * math.sqrt(CISS / L_GATE)),
            (L_GATE * 1e9, r_off_tot), xytext=(3.0, 0.5), arrowprops=dict(arrowstyle="->", lw=0.7), fontsize=7.5)
ax.set_xlabel("gate-loop inductance per FET $L_G$ [nH]")
ax.set_ylabel("total gate-loop resistance [$\\Omega$]")
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.legend(loc="upper left")
save(fig, "rg_window")
mac.update(RoffMaxMin="%.1f" % roff_max_min, RoffMaxTyp="%.1f" % roff_max_typ, RonTot="%.1f" % r_on_tot,
           RoffTot="%.1f" % r_off_tot, RdampMin="%.2f" % (2 * 0.707 * math.sqrt(L_GATE / CISS)),
           ZetaOn="%.1f" % (r_on_tot / 2 * math.sqrt(CISS / L_GATE)),
           ZetaOff="%.2f" % (r_off_tot / 2 * math.sqrt(CISS / L_GATE)),
           VbumpMiller="%.2f" % (CRSS * DVDT_OFF * 1e9 * r_off_tot))

# ------------------------------------------------------------------ 5. current-sharing sensitivity
cases = [("$V_{th}$ +0.3 V on one FET", 7, "2:1 $E_{off}$ split"),
         ("drain inductance +0.3 nH", 2, "small energy shift"),
         ("gate loop 2 $\\rightarrow$ 8 nH on one FET", 19, "4:1 $E_{on}$ split"),
         ("no Kelvin, symmetric", 0, "+47 % $E_{on}$, both slower"),
         ("no Kelvin, common-source mismatch", 29, "largest imbalance")]
fig, ax = plt.subplots(figsize=(5.6, 2.6))
y = np.arange(len(cases))
vals = [c[1] for c in cases]
cols = ["C1" if v >= 15 else ("C0" if v > 0 else "C7") for v in vals]
ax.barh(y, vals, color=cols, edgecolor="k", lw=0.5)
for yi, (lab, v, note) in zip(y, cases):
    ax.text(v + 0.6, yi, "%d %%  (%s)" % (v, note), va="center", fontsize=7)
ax.set_yticks(y)
ax.set_yticklabels([c[0] for c in cases], fontsize=7.5)
ax.set_xlabel("peak current imbalance between the paralleled FETs [%]")
ax.set_xlim(0, 58)
ax.axvline(0, color="k", lw=0.5)
save(fig, "sharing_tornado")

# ------------------------------------------------------------------ 6. loss breakdown vs f
lf = rs["loss_vs_f"]
f = np.array([x["f"] for x in lf]) / 1e3
parts = [("cond", "conduction ($R_{DS(on)}$, 100 $^\\circ$C)"), ("cu", "PCB copper, load current"), ("cu_hf", "PCB copper, switching harmonics"), ("sw", "switching"),
         ("dead", "dead time"), ("gate", "gate drive"), ("cap", "MLCC ESR")]
fig, ax = plt.subplots(figsize=(5.2, 3.3))
ax.stackplot(f, *[np.array([x[k] for x in lf]) for k, _ in parts], labels=[l for _, l in parts], alpha=0.85)
ax.axhline(sz["P_loss_budget"], color="k", ls=":", lw=1)
ax.text(f[0] + 2, sz["P_loss_budget"] + 0.3, "99.5 %% budget (%.1f W)" % sz["P_loss_budget"], fontsize=7)
ax.axvline(50, color="C3", lw=0.8, ls="--")
ax.set_xlabel("switching frequency [kHz]")
ax.set_ylabel("loss per phase leg [W]")
ax.set_xlim(f[0], f[-1])
ax.legend(loc="upper left", ncol=2)
save(fig, "loss_stack")

# ------------------------------------------------------------------ 7. DC-link design space (C_v vs C_i)
fs = np.linspace(10e3, 200e3, 200)
c_eff_bulk = sz["bank"]["bulk_C_eff_each"]
c_hf = sz["bank"]["hf_n"] * sz["bank"]["hf_C_eff_each"]
c_req = sz["C_eff_per_block_shared_uF"] * 1e-6 * 50e3 / fs      # +/-2 % ripple on a shared 3-leg bus
I_CAP = 2.5                                                      # A rms per 1210 (assumption, check datasheet)
n_v = np.maximum((c_req - c_hf) / c_eff_bulk, 0)
n_i = np.full_like(fs, sz["I_leg_hf_rated"] / I_CAP)
n_bank = np.maximum(n_v, n_i)
A_FIXED, A_CAP = 4.2, (8.46 - 4.2) / 24                          # cm2: cells + driver corridor; per 1210 incl. strips
area = A_FIXED + A_CAP * n_bank
f_cross = float(fs[np.argmin(np.abs(n_v - n_i))])
fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.0))
ax[0].plot(fs / 1e3, n_v, label="$C_v$: ripple voltage ($\\pm$2 %, shared bus)")
ax[0].plot(fs / 1e3, n_i, label="$C_i$: ripple current (%.1f A per MLCC)" % I_CAP)
ax[0].plot(fs / 1e3, n_bank, "k", lw=2, label="required = max($C_v$, $C_i$)")
ax[0].plot(50, 24, "*", color="C3", ms=11, mec="k", label="selected: 24 x 10 $\\mu$F 1210")
ax[0].set_ylim(0, 80)
ax[0].set_xlabel("switching frequency [kHz]")
ax[0].set_ylabel("number of 10 $\\mu$F 1210 MLCCs per leg")
ax[0].legend()
ax[1].plot(fs / 1e3, area, "k", lw=2)
ax[1].axhline(A_FIXED, color="C7", ls="--", lw=1)
ax[1].text(120, A_FIXED + 0.2, "cells + driver (fixed)", fontsize=7)
ax[1].plot(50, 8.46, "*", color="C3", ms=11, mec="k")
ax[1].set_xlabel("switching frequency [kHz]")
ax[1].set_ylabel("board area per leg [cm$^2$]")
ax[1].set_ylim(0, 16)
save(fig, "dclink_space")
mac.update(Fcross="%.0f" % (f_cross / 1e3), Icap="%.1f" % I_CAP, NcapHundred="%.0f" % math.ceil(np.interp(100e3, fs, n_bank)),
           AreaHundred="%.1f" % np.interp(100e3, fs, area), Afixed="%.1f" % A_FIXED)

# ------------------------------------------------------------------ 8. efficiency - power density (Pareto)
ftab = np.array([x["f"] for x in lf])
ptab = np.array([x["total"] for x in lf])
p_inv = np.polyval(np.polyfit(ftab, ptab, 1), fs)   # loss is linear in f_sw (LTspice table 20-100 kHz)
eta_inv = P_RATED / (P_RATED + p_inv)
rho = P_RATED / 1e3 / area
fig, ax = plt.subplots(figsize=(5.4, 3.6))
sc = ax.scatter(rho, 100 * eta_inv, c=fs / 1e3, cmap="viridis", s=8, label="inverter leg")
for fm, mk in ((20e3, "o"), (50e3, "*"), (100e3, "s"), (200e3, "^")):
    k = int(np.argmin(np.abs(fs - fm)))
    ax.plot(rho[k], 100 * eta_inv[k], mk, color="C3", mec="k", ms=8 if mk == "*" else 5)
    ax.annotate("%.0f kHz" % (fm / 1e3), (rho[k], 100 * eta_inv[k]), textcoords="offset points", xytext=(5, 4), fontsize=7)
ax.axhline(99.5, color="k", ls=":", lw=1)
cb = fig.colorbar(sc, ax=ax)
cb.set_label("$f_{sw}$ [kHz]")
ax.set_xlabel("board-level power density [kW/cm$^2$]")
ax.set_ylabel("efficiency [%]")
ax.set_xlim(0.08, 0.50)
ax.legend(loc="lower left")
save(fig, "eta_rho")
k50, k100 = int(np.argmin(np.abs(fs - 50e3))), int(np.argmin(np.abs(fs - 100e3)))
mac.update(RhoFifty="%.2f" % rho[k50], RhoHundred="%.2f" % rho[k100], EtaHundred="%.2f" % (100 * eta_inv[k100]),
           RhoMaxCi="%.2f" % (P_RATED / 1e3 / (A_FIXED + A_CAP * n_i[0])))

# ------------------------------------------------------------------ 9. heat-sink requirement
R_TIM = 1.9           # K/W per device (0.5 mm pad, 17.8 W/mK, 3 x 5 mm)
TJ_MAX = 125.0
fig, ax = plt.subplots(figsize=(5.0, 3.3))
p_dev_tot = np.array([x["cond"] + x["sw"] + x["dead"] for x in lf])  # four devices of one leg
p_dev = p_dev_tot / 4
rth = {}
for ta, c in ((25, "C0"), (45, "C1"), (65, "C3")):
    r = (TJ_MAX - ta - p_dev * (RJC + R_TIM)) / p_dev_tot
    rth[ta] = r
    ax.plot(f, r, color=c, label="ambient / coolant %d $^\\circ$C" % ta)
ax.axvline(50, color="k", lw=0.8, ls="--")
ax.set_xlabel("switching frequency [kHz]")
ax.set_ylabel("max. heat-sink $R_{th,hs-a}$ per leg [K/W]")
ax.set_ylim(0, None)
ax.legend()
save(fig, "thermal_req")
mac.update(RthHsFifty="%.1f" % np.interp(50, f, rth[65]), RthHsFiftyCool="%.1f" % np.interp(50, f, rth[45]),
           Rtim="%.1f" % R_TIM)

# ------------------------------------------------------------------ 10. utilisation radar
ch = rs["rg_choice"]
util = [
    ("V$_{DS}$ overshoot\n(of 15 V)", (VDS_PK_160 - VDC) / 15.0),
    ("high-side gate bump\n(of $V_{th,typ}$)", ch["VGSH"] / VTH_TYP),
    ("negative $V_{GS}$\n(of -4 V)", abs(ch["VGSHmin"]) / 4.0),
    ("loss\n(of 99.5 % budget)", rs["loss_vs_f"][3]["total"] / sz["P_loss_budget"] if rs["loss_vs_f"][3]["f"] == 50e3
     else float(np.interp(50e3, ftab, ptab)) / sz["P_loss_budget"]),
    ("DC-link ripple\n(of $\\pm$2 %)", sz["bank"]["dVpp_shared_3ph"] / sz["dV_allowed"]),
    ("device RMS current\n(of 133 A cont.)", sz["I_dev_rms"] / 133.0),
    ("max-$R_{DS(on)}$ loss\n(of budget)", rs["worst_50k_maxRds"]["total"] / sz["P_loss_budget"]),
]
ang = np.linspace(0, 2 * np.pi, len(util), endpoint=False)
vals = np.array([u[1] for u in util])
fig = plt.figure(figsize=(4.8, 4.2))
ax = fig.add_subplot(111, polar=True)
ax.plot(np.r_[ang, ang[0]], np.r_[vals, vals[0]], "C3", lw=1.5)
ax.fill(np.r_[ang, ang[0]], np.r_[vals, vals[0]], color="C3", alpha=0.2)
ax.plot(np.r_[ang, ang[0]], np.ones(len(ang) + 1), "k--", lw=0.8)
ax.set_xticks(ang)
ax.set_xticklabels([u[0] for u in util], fontsize=7)
ax.set_ylim(0, 1.2)
ax.set_yticks([0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(["25 %", "50 %", "75 %", "limit"], fontsize=6)
ax.tick_params(axis="x", pad=9)
save(fig, "margins")
mac.update(UtilBump="%.0f" % (100 * util[1][1]), UtilRipple="%.0f" % (100 * util[4][1]),
           UtilVds="%.0f" % (100 * util[0][1]), UtilWorst="%.0f" % (100 * util[6][1]))

# ------------------------------------------------------------------ 11. DPT sizing and measurement
L_DPT, I_DPT = 5e-6, 160.0
t1 = L_DPT * I_DPT / VDC
c_dpt = lambda dv: L_DPT * I_DPT ** 2 / (2 * VDC * dv - dv ** 2)  # noqa: E731  (Tran 2025, eq. 13)
f_ring = 1 / (2 * math.pi * math.sqrt(L_CELL * COSS50))   # one cell: L_loop with C_oss of its off-state FET
mac.update(Tone="%.1f" % (t1 * 1e6), CdptTwo="%.0f" % (c_dpt(0.02 * VDC) * 1e6), CdptFive="%.0f" % (c_dpt(0.05 * VDC) * 1e6),
           Fring="%.0f" % (f_ring / 1e6), Trise="%.1f" % (VDC / DVDT_OFF))

# winding-ripple requirement handed to the machine design: L >= Vdc / (4 f dI), dI = 10 % of the peak current
for fq, key in ((25e3, "LreqTwentyFive"), (50e3, "LreqFifty"), (100e3, "LreqHundred")):
    mac[key] = "%.0f" % (VDC / (4 * fq * 0.1 * I_PK) * 1e6)

with open(os.path.join(OUT, "numbers.tex"), "w") as fh:
    fh.write("% generated by scripts/design_report_v2.py\n")
    for k, v in mac.items():
        fh.write("\\newcommand{\\%s}{%s}\n" % (k, v))
print(json.dumps(mac, indent=1))

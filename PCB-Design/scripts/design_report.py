"""
Extra analyses for the step-by-step design report (reports/design-report):
  1. number of parallel EPC2361 per switch (n = 1..4): conduction / switching / dead-time loss, area, heat per device
  2. switching-frequency choice including PWM-ripple losses in the machine (illustrative machine parameters)
  3. power-density figures of the building block

    python scripts/design_report.py -> reports/design-report/figures/*.pdf|png, reports/design-report/numbers.tex
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
OUT = os.path.join(ROOT, "reports", "design-report")
FIG = os.path.join(OUT, "figures")
os.makedirs(FIG, exist_ok=True)

sz = json.load(open(os.path.join(BB, "sizing.json")))
rs = json.load(open(os.path.join(BB, "results.json")))
S = sz["spec"]
I_RMS, I_PK, VDC = S["I_rms"], sz["I_pk"], S["Vdc"]
P_RATED = sz["P_rated"]
pon, poff = np.array(rs["energy"]["fit_on"]), np.array(rs["energy"]["fit_off"])
th = np.linspace(0, np.pi, 4001)
i_abs = I_PK * np.sin(th)


def e_avg(n):
    """Average switching energy per period for n devices per switch. The LTspice fit is for n = 2; split it into a
    current-independent part (output charge, ~proportional to n) and a current-dependent part (kept)."""
    e2 = np.polyval(pon, i_abs) + np.polyval(poff, i_abs)
    e0_2 = np.polyval(pon, 0) + np.polyval(poff, 0)       # zero-current energy of the n = 2 switch position
    return float(np.mean(e2 - e0_2 + e0_2 * n / 2))


P_CU = rs["P_cu"]
P_OTHER = sz["P_cap_rated"]
mac = {}

# ------------------------------------------------------------- 1. number of parallel devices
fs = np.array([20e3, 50e3, 100e3])
rows = []
for n in (1, 2, 3, 4):
    cond = I_RMS ** 2 * S["Rds_25_typ"] * S["Rds_factor_100C"] / n
    for f in fs:
        sw = e_avg(n) * f
        dead = sz["P_dead_50k"] * f / 50e3
        gate = (sz["P_gate_50k"] + sz["P_ldo_50k"]) * f / 50e3 * n / 2
        tot = cond + sw + dead + gate + P_CU + P_OTHER
        rows.append(dict(n=n, f=f, cond=cond, sw=sw, total=tot, eta=P_RATED / (P_RATED + tot),
                         p_dev=(cond + sw + dead) / (2 * n)))
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
for f, c in zip(fs, ("C0", "C1", "C2")):
    r = [x for x in rows if x["f"] == f]
    ax[0].plot([x["n"] for x in r], [x["total"] for x in r], "-o", color=c, label="%.0f kHz" % (f / 1e3))
    ax[1].plot([x["n"] for x in r], [x["p_dev"] for x in r], "-o", color=c, label="%.0f kHz" % (f / 1e3))
ax[0].axhline(sz["P_loss_budget"], color="k", ls=":", lw=1)
ax[0].set_ylabel("loss per phase leg [W]  (dotted: 99.5 % budget)")
ax[1].set_ylabel("loss per device [W]")
for a in ax:
    a.set_xlabel("EPC2361 in parallel per switch")
    a.set_xticks([1, 2, 3, 4])
    a.grid(alpha=0.3)
    a.legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "n_parallel.pdf"))
fig.savefig(os.path.join(FIG, "n_parallel.png"), dpi=130)
WORD = {1: "one", 2: "two", 3: "three", 4: "four"}     # LaTeX macro names cannot contain digits
for r in rows:
    if r["f"] == 50e3:
        w = WORD[r["n"]]
        mac["TotN" + w] = "%.1f" % r["total"]
        mac["EtaN" + w] = "%.2f" % (100 * r["eta"])
        mac["PdevN" + w] = "%.1f" % r["p_dev"]
        mac["CondN" + w] = "%.1f" % r["cond"]
        mac["SwN" + w] = "%.1f" % r["sw"]

# ------------------------------------------------------------- 2. switching frequency incl. machine ripple losses
# ILLUSTRATIVE machine parameters (replace with machine data): phase leakage inductance and harmonic resistance
L_PH = 15e-6          # H, per phase
R_AC20 = 15e-3        # ohm, harmonic (AC) resistance at 20 kHz, grows ~ sqrt(f) (skin / proximity)
K_FE = 0.6            # iron loss from PWM ripple as a multiple of the ripple copper loss at 20 kHz (assumption)
M = 1.0


def ripple_rms(f, n_inter=1):
    """RMS PWM current ripple of one phase, 2-level leg, SPWM, averaged over the fundamental.
    di = Vdc d(1-d)/(L f) peak-peak (triangular) -> rms = pp / (2 sqrt 3). n_inter: carriers phase-shifted between
    stacked modules feeding one winding set (effective ripple frequency x n, amplitude / n)."""
    d = 0.5 * (1 + M * np.sin(th))
    pp = VDC * d * (1 - d) / (L_PH * f)
    return float(np.sqrt(np.mean((pp / (2 * math.sqrt(3))) ** 2))) / n_inter


fgrid = np.linspace(10e3, 200e3, 60)
inv, mach, mach2 = [], [], []
for f in fgrid:
    inv.append(rs["energy"] and (I_RMS ** 2 * S["Rds_25_typ"] * S["Rds_factor_100C"] / 2 + e_avg(2) * f
                                 + sz["P_dead_50k"] * f / 50e3 + P_CU + P_OTHER))
    r_ac = R_AC20 * math.sqrt(f / 20e3)
    pcu = ripple_rms(f) ** 2 * r_ac
    pfe = K_FE * ripple_rms(20e3) ** 2 * R_AC20 * (20e3 / f) ** 1.5      # falls with ripple amplitude
    mach.append(pcu + pfe)
    pcu2 = ripple_rms(f, 2) ** 2 * R_AC20 * math.sqrt(2 * f / 20e3)
    pfe2 = K_FE * ripple_rms(20e3) ** 2 * R_AC20 * (20e3 / (2 * f)) ** 1.5
    mach2.append(pcu2 + pfe2)
inv, mach, mach2 = map(np.array, (inv, mach, mach2))
tot, tot2 = inv + mach, inv + mach2
k1, k2 = int(np.argmin(tot)), int(np.argmin(tot2))
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(fgrid / 1e3, inv, label="inverter leg (this design)")
ax.plot(fgrid / 1e3, mach, label="machine PWM-ripple loss, per phase (illustrative)")
ax.plot(fgrid / 1e3, tot, "k", lw=2, label="sum")
ax.plot(fgrid / 1e3, tot2, "k--", lw=1.5, label="sum, 2 interleaved modules per winding set")
ax.plot(fgrid[k1] / 1e3, tot[k1], "ko")
ax.plot(fgrid[k2] / 1e3, tot2[k2], "ks")
ax.set_xlabel("switching frequency [kHz]")
ax.set_ylabel("loss per phase [W]")
ax.set_ylim(0, max(tot[0], 30))
ax.grid(alpha=0.3)
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fsw_system.pdf"))
fig.savefig(os.path.join(FIG, "fsw_system.png"), dpi=130)
mac.update(FoptSingle="%.0f" % (fgrid[k1] / 1e3), FoptInter="%.0f" % (fgrid[k2] / 1e3),
           LossOptSingle="%.1f" % tot[k1], RipRmsFifty="%.1f" % ripple_rms(50e3), RipRmsTwenty="%.1f" % ripple_rms(20e3),
           Lph="%.0f" % (L_PH * 1e6), Rac="%.0f" % (R_AC20 * 1e3), Kfe="%.1f" % K_FE)

# ------------------------------------------------------------- 3. power density
area_cm2 = 3.0 * 2.82                       # 30 x 28.2 mm board
height_cm = 0.16 + 0.25                     # PCB + tallest parts (1210, ~2.5 mm)
P_max = (1.15 * VDC / (2 * math.sqrt(2))) * I_RMS     # M = 1.15, cos phi = 1
mac.update(Area="%.1f" % area_cm2, PdArea="%.2f" % (P_RATED / 1e3 / area_cm2),
           PdVol="%.0f" % (P_RATED / 1e3 / (area_cm2 * height_cm) * 1e3), Pmax="%.2f" % (P_max / 1e3),
           PdAreaMax="%.2f" % (P_max / 1e3 / area_cm2))

with open(os.path.join(OUT, "numbers.tex"), "w") as f:
    f.write("% generated by scripts/design_report.py\n")
    for k, v in mac.items():
        f.write("\\newcommand{\\%s}{%s}\n" % (k, v))
print(json.dumps(mac, indent=1))
for r in rows:
    print("n=%d f=%3.0fk cond %.2f sw %.2f total %.2f eta %.3f Pdev %.2f" % (r["n"], r["f"] / 1e3, r["cond"], r["sw"], r["total"], 100 * r["eta"], r["p_dev"]))

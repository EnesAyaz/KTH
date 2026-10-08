"""
Loss characterisation graphs for the building block (in the style of the 2 kV SiC inverter slides):
  1. switching energies vs current (LTspice with Q3D parasitics, 2 x EPC2361 per switch, Rg 2/0 ohm)
  2. switching energy per event over one fundamental period, with the average switching loss
  3. R_DS(on) vs junction temperature (EPC2361 datasheet Fig. 9, linear)
  4. conduction loss vs junction temperature, and total loss / efficiency at 75 / 100 / 125 / 150 C
  5. E_on / E_off decomposition: output-capacitance part vs overlap part (analytic V^2 I / (2 dv/dt))

    python scripts/loss_characterization.py -> reports/design-report-v2/figures/lc_*.pdf|png, lc_numbers.tex
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
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3, "legend.fontsize": 8})

sz = json.load(open(os.path.join(BB, "sizing.json")))
rs = json.load(open(os.path.join(BB, "results.json")))
S = sz["spec"]
VDC, I_RMS, I_PK, P = S["Vdc"], S["I_rms"], sz["I_pk"], sz["P_rated"]
F_SW, N_PAR = S["f_sw"], S["n_par"]
E = rs["energy"]
I_meas, Eon, Eoff = np.array(E["I"]), np.array(E["Eon"]), np.array(E["Eoff"])
pon, poff = np.array(E["fit_on"]), np.array(E["fit_off"])
dv_on, dv_off = np.array(E["dvdt_on"]), np.array(E["dvdt_off"])
r50 = [r for r in rs["loss_vs_f"] if r["f"] == 50e3][0]
mac = {}


def kT(t):
    """EPC2361 datasheet Fig. 9: normalised R_DS(on), linear 0.84 (0 C) ... 1.81 (150 C)."""
    return 0.84 + (1.81 - 0.84) / 150.0 * t


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, name + ".pdf"))
    fig.savefig(os.path.join(FIG, name + ".png"), dpi=140)
    plt.close(fig)


# ---------------------------------------------------------------- 1. switching energies vs current
ii = np.linspace(0, 170, 200)
e_on_pk, e_off_pk = np.polyval(pon, I_PK), np.polyval(poff, I_PK)
fig, ax = plt.subplots(figsize=(5.6, 3.8))
ax.plot(ii, np.polyval(pon, ii) * 1e6, "r", lw=2.5, label="$E_{on}$ (fit)")
ax.plot(ii, np.polyval(poff, ii) * 1e6, "b", lw=2.5, label="$E_{off}$ (fit)")
ax.plot(I_meas, Eon * 1e6, "rx", ms=6, label="LTspice")
ax.plot(I_meas, Eoff * 1e6, "bx", ms=6)
ax.axvline(I_PK, color="k", ls=":", lw=0.8)
ax.annotate("%.0f $\\mu$J at %.0f A" % (e_on_pk * 1e6, I_PK), (I_PK, e_on_pk * 1e6), xytext=(40, 47),
            color="r", fontsize=10, weight="bold", arrowprops=dict(arrowstyle="->", color="r"))
ax.annotate("%.1f $\\mu$J at %.0f A" % (e_off_pk * 1e6, I_PK), (I_PK, e_off_pk * 1e6), xytext=(60, 20),
            color="b", fontsize=10, weight="bold", arrowprops=dict(arrowstyle="->", color="b"))
ax.annotate("%.0f $\\mu$J at 0 A:\noutput capacitance" % (np.polyval(pon, 0) * 1e6), (0, np.polyval(pon, 0) * 1e6),
            xytext=(8, 30), fontsize=8, arrowprops=dict(arrowstyle="->"))
ax.set_xlabel("switched current per switch position [A]  (2 x EPC2361)")
ax.set_ylabel("switching energy [$\\mu$J]")
ax.set_title("75 V, $R_{g,on}/R_{g,off}$ = 2/0 $\\Omega$, Q3D layout parasitics", fontsize=9)
ax.set_xlim(0, 170)
ax.set_ylim(0, 60)
ax.legend(loc="upper left")
save(fig, "lc_energy")
mac.update(LcEonPk="%.0f" % (e_on_pk * 1e6), LcEoffPk="%.1f" % (e_off_pk * 1e6), LcEonZero="%.0f" % (np.polyval(pon, 0) * 1e6))

# ---------------------------------------------------------------- 2. energy per event over one fundamental period
F1_DISP = 1e3                                   # display only: 50 events per period at 50 kHz
n_ev = int(F_SW / F1_DISP)
t_ev = (np.arange(n_ev) + 0.5) / F_SW
i_ev = np.abs(I_PK * np.sin(2 * np.pi * F1_DISP * t_ev))
e_on_ev, e_off_ev = np.polyval(pon, i_ev), np.polyval(poff, i_ev)
p_on, p_off = float(np.mean(e_on_ev) * F_SW), float(np.mean(e_off_ev) * F_SW)
fig, ax = plt.subplots(2, 1, figsize=(5.6, 4.6), sharex=True)
for a, e, p, c, lab in ((ax[0], e_on_ev, p_on, "r", "on"), (ax[1], e_off_ev, p_off, "b", "off")):
    a.stem(t_ev * 1e3, e * 1e6, linefmt=c + "-", markerfmt=c + "x", basefmt=" ")
    a.set_ylabel("$E_{%s}$ per event [$\\mu$J]" % lab, color=c)
    a2 = a.twinx()
    a2.axhline(p, color="C4", lw=1.5)
    a2.set_ylim(0, p * 1.6)
    a.set_ylim(0, e.max() * 1.35 * 1e6)
    a2.set_ylabel("$P_{sw,%s}$ [W]" % lab, color="C4")
    a2.grid(False)
    a.text(0.5, 0.9, "average $P_{sw,%s}$ = %.2f W" % (lab, p), transform=a.transAxes, color="C4", fontsize=9,
           ha="center", bbox=dict(facecolor="white", edgecolor="none", alpha=0.9))
ax[1].set_xlabel("time over one fundamental period [ms]  (sinusoidal current, %.0f A$_{pk}$, $f_{sw}$ = 50 kHz)" % I_PK)
save(fig, "lc_events")
mac.update(LcPon="%.2f" % p_on, LcPoff="%.2f" % p_off)

# ---------------------------------------------------------------- 3 + 4. R_DS(on) and conduction loss vs Tj
T = np.linspace(0, 150, 151)
r_typ, r_max = S["Rds_25_typ"] * kT(T), S["Rds_25_max"] * kT(T)
p_cond_typ = I_RMS ** 2 * r_typ / N_PAR
p_cond_max = I_RMS ** 2 * r_max / N_PAR
fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.5))
ax[0].plot(T, r_typ * 1e3, "r", lw=2, label="typical (0.75 m$\\Omega$ at 25 $^\\circ$C)")
ax[0].plot(T, r_max * 1e3, "r--", lw=1, label="maximum (1.0 m$\\Omega$ at 25 $^\\circ$C)")
ax[0].plot(T, r_typ / N_PAR * 1e3, "k", lw=1.2, label="switch position (2 in parallel), typical")
for t in (25, 100, 125):
    ax[0].plot(t, S["Rds_25_typ"] * kT(t) * 1e3, "ro")
    ax[0].annotate("%.2f m$\\Omega$" % (S["Rds_25_typ"] * kT(t) * 1e3), (t, S["Rds_25_typ"] * kT(t) * 1e3),
                   textcoords="offset points", xytext=(-14, 7), fontsize=7)
ax[0].set_xlabel("junction temperature $T_j$ [$^\\circ$C]")
ax[0].set_ylabel("$R_{DS(on)}$ [m$\\Omega$]")
ax[0].set_title("EPC2361 (datasheet Fig. 9, $I_D$ = 50 A, $V_{GS}$ = 5 V)", fontsize=9)
ax[0].legend(loc="upper left", fontsize=7)
ax[1].plot(T, p_cond_typ, "r", lw=2, label="typical $R_{DS(on)}$")
ax[1].plot(T, p_cond_max, "r--", lw=1, label="maximum $R_{DS(on)}$")
ax[1].fill_between(T, p_cond_typ, p_cond_max, color="r", alpha=0.1)
ax[1].set_xlabel("junction temperature $T_j$ [$^\\circ$C]")
ax[1].set_ylabel("conduction loss per leg [W]")
ax[1].set_title("$I_{rms}$ = 100 A, $P_{cond} = I_{rms}^2 R_{DS(on)}(T_j)/2$ (SPWM = SVM)", fontsize=9)
ax[1].legend(loc="upper left")
save(fig, "lc_rds_cond")

# total loss and efficiency vs Tj (only conduction changes with Tj, as in the 2 kV study)
other = r50["total"] - r50["cond"]
rows = []
for t in (75, 100, 125, 150):
    pc = I_RMS ** 2 * S["Rds_25_typ"] * kT(t) / N_PAR
    tot = pc + other
    rows.append(dict(Tj=t, cond=pc, total=tot, eta=100 * P / (P + tot),
                     total_max=I_RMS ** 2 * S["Rds_25_max"] * kT(t) / N_PAR + other))
for r in rows:
    r["eta_max"] = 100 * P / (P + r["total_max"])
parts = [("cond", "conduction"), ("sw", "switching"), ("cu", "copper, load"), ("cu_hf", "copper, harmonics"),
         ("dead", "dead time"), ("cap", "MLCC ESR"), ("gate", "gate")]
fig, ax = plt.subplots(figsize=(5.8, 3.6))
x = np.arange(len(rows))
bottom = np.zeros(len(rows))
for k, lab in parts:
    v = np.array([r["cond"] if k == "cond" else r50[k] for r in rows])
    ax.bar(x, v, 0.6, bottom=bottom, label=lab)
    bottom += v
ax.axhline(sz["P_loss_budget"], color="k", ls=":", lw=1, label="99.5 %% budget (%.1f W)" % sz["P_loss_budget"])
for xi, r in zip(x, rows):
    ax.text(xi, r["total"] + 0.25, "%.1f W\n%.2f %%" % (r["total"], r["eta"]), ha="center", fontsize=8,
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1))
ax.set_xticks(x)
ax.set_xticklabels(["$T_j$ = %d $^\\circ$C" % r["Tj"] for r in rows])
ax.set_ylabel("loss per leg [W]")
ax.set_ylim(0, 17)
ax.set_title("50 kHz, 100 A$_{rms}$, typical $R_{DS(on)}$; only conduction varies with $T_j$", fontsize=9)
ax.legend(fontsize=7, ncol=2, loc="lower right")
save(fig, "lc_tj")
for r in rows:
    tag = {75: "SeventyFive", 100: "Hundred", 125: "OneTwentyFive", 150: "OneFifty"}[r["Tj"]]
    mac["LcTot" + tag] = "%.1f" % r["total"]
    mac["LcEta" + tag] = "%.2f" % r["eta"]
    mac["LcEtaMax" + tag] = "%.2f" % r["eta_max"]
    mac["LcCond" + tag] = "%.2f" % r["cond"]

# ---------------------------------------------------------------- 5. decomposition of the switching energy
e0_on, e0_off = np.polyval(pon, 0), np.polyval(poff, 0)
qoss_v = N_PAR * S["Qoss_75"] * VDC
ov_on = 0.5 * VDC ** 2 * I_meas / (dv_on * 1e9)
ov_off = 0.5 * VDC ** 2 * I_meas / (dv_off * 1e9)
fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.5))
ax[0].plot(I_meas, Eon * 1e6, "rx-", label="$E_{on}$ LTspice")
ax[0].plot(I_meas, (e0_on + ov_on) * 1e6, "r--", label="$E_{on}(0)$ + $V^2 I/(2\\,dv/dt_{on})$")
ax[0].axhline(e0_on * 1e6, color="gray", ls=":", lw=1)
ax[0].set_ylim(10, None)
ax[0].text(95, e0_on * 1e6 + 0.6, "$E_{on}(0)$ = %.0f $\\mu$J  ($Q_{oss}V$ = %.0f $\\mu$J for 2 FETs)" % (e0_on * 1e6, qoss_v * 1e6),
           fontsize=7, ha="center")
ax[0].set_xlabel("switched current [A]")
ax[0].set_ylabel("energy [$\\mu$J]")
ax[0].set_title("turn-on: capacitive part + $dv/dt$-limited overlap", fontsize=9)
ax[0].legend(fontsize=7, loc="upper left")
ax[1].plot(I_meas, Eoff * 1e6, "bx-", label="$E_{off}$ LTspice")
ax[1].plot(I_meas, ov_off * 1e6, "b--", label="$V^2 I/(2\\,dv/dt_{off})$ (overlap formula)")
ax[1].set_xlabel("switched current [A]")
ax[1].set_ylabel("energy [$\\mu$J]")
ax[1].set_title("turn-off: channel closes before $V_{DS}$ rises", fontsize=9)
ax[1].legend(fontsize=7, loc="center left")
ax1b = ax[1].twinx()
ax1b.plot(I_meas, dv_off, "k:", lw=1)
ax1b.set_ylabel("$dv/dt_{off}$ [V/ns] (dotted)")
ax1b.grid(False)
save(fig, "lc_decomp")
k = int(np.argmax(I_meas))
mac.update(LcEonZeroFit="%.0f" % (e0_on * 1e6), LcQossV="%.0f" % (qoss_v * 1e6),
           LcOvOnPk="%.0f" % (ov_on[k] * 1e6), LcEonMinusZeroPk="%.0f" % ((Eon[k] - e0_on) * 1e6),
           LcOvOffPk="%.0f" % (ov_off[k] * 1e6), LcEoffMeasPk="%.1f" % (Eoff[k] * 1e6), LcIpkMeas="%.0f" % I_meas[k],
           LcDvOnPk="%.0f" % dv_on[k], LcDvOffPk="%.0f" % dv_off[k])

with open(os.path.join(OUT, "lc_numbers.tex"), "w") as fh:
    fh.write("% generated by scripts/loss_characterization.py\n")
    for k_, v in mac.items():
        fh.write("\\newcommand{\\%s}{%s}\n" % (k_, v))
print(json.dumps(mac, indent=1))
print(json.dumps(rows, indent=1))

"""
Voltage-class selection for the SPB building block: off-the-shelf GaN transistors (datasheet values, Datasheet/).

    python scripts/device_survey.py
    -> reports/design-report-v2/figures/device_fom.pdf|png, reports/design-report-v2/device_numbers.tex,
       reports/paper/device_table.tex

Argument: in an SPB with bus voltage V_bus, N = V_bus/V_m modules all carry the same phase current I. With n devices
per switch, the conduction loss of all modules scales with N I^2 R/n and the output-charge loss with
N n f Q_oss V_m, Q_oss ~ C_oss,tr V_m. Minimising over n gives
    P_min = 6 I sqrt(f) V_bus sqrt(R_DS(on) C_oss,tr)       (three legs per module, both switches)
i.e. the voltage class drops out and the device time constant tau = R_DS(on) C_oss,tr ranks the candidates.
C_oss,tr = Q_oss / V_test at the datasheet test voltage (identical to the datasheet C_oss,tr where given).
"""
import math
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "reports", "design-report-v2")
plt.rcParams.update({"font.size": 8, "axes.grid": True, "grid.alpha": 0.3, "legend.fontsize": 7})

# part, maker, V_rated, R_typ [mOhm] (25 C), Q_oss typ [nC], V_test [V], C_oss typ [pF] at V_test, package
DEV = [
    ("EPC2361", "EPC", 100, 0.75, 90, 50, 1019, "QFN 3x5"),
    ("EPC2302", "EPC", 100, 1.4, 85, 50, 1000, "QFN 3x5"),
    ("EPC2071", "EPC", 100, 1.7, 71, 50, 878, "BGA"),
    ("IGC033S10S1", "Infineon", 100, 2.4, 43, 50, 540, "TSON 3x5"),
    ("EPC2304", "EPC", 200, 3.5, 120, 100, 704, "QFN 3x5"),
    ("EPC2215", "EPC", 200, 6.0, 69, 100, 390, "BGA"),
    ("EPC2034C", "EPC", 200, 6.0, 96, 100, 641, "BGA"),
    ("EPC2050", "EPC", 350, 55.0, 35, 280, 81, "BGA"),
    ("IGT65R025D2", "Infineon", 650, 25.0, 82, 400, 130, "HSOF"),
    ("IGT65R140D2", "Infineon", 650, 140.0, 14, 400, 22, "HSOF"),
]
V_M = {100: 75.0, 200: 150.0, 350: 240.0, 650: 400.0}       # submodule voltage used for each class
COL = {100: "C3", 200: "C0", 350: "C2", 650: "C1"}
V_BUS, I_RMS, F_SW = 1200.0, 100.0, 50e3

rows = []
for pn, mk, v, r, q, vt, coss, pkg in DEV:
    ctr = q / vt * 1e3                     # pF  (C_oss,tr = Q_oss / V_test)
    tau = r * 1e-3 * ctr * 1e-12           # s
    vm = V_M[v]
    n_mod = V_BUS / vm
    q_vm = ctr * 1e-12 * vm                # Q_oss at V_m (C_oss,tr approximation)
    n_opt = I_RMS * math.sqrt(r * 1e-3 / (F_SW * q_vm * vm))
    p_min = 6 * I_RMS * math.sqrt(F_SW) * V_BUS * math.sqrt(tau)
    rows.append(dict(pn=pn, mk=mk, v=v, r=r, q=q, vt=vt, coss=coss, ctr=ctr, tau=tau * 1e12, vm=vm, n_mod=n_mod,
                     n_opt=n_opt, p_min=p_min, pkg=pkg))
ref = [r for r in rows if r["pn"] == "EPC2361"][0]

fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1.15, 1]))
cc = np.logspace(1, 3.6, 50)
for tau in (1, 2, 5, 10):
    ax[0].loglog(cc, tau / (cc * 1e-12) * 1e-12 * 1e3 * 1e0, color="0.6", lw=0.7, ls="--")
    ax[0].text(20, tau / 20e-12 * 1e-9 * 1.1, "$\\tau$ = %g ps" % tau, fontsize=6.5, color="0.4", rotation=-31)
for r in rows:
    ax[0].loglog(r["ctr"], r["r"], "o" if r["mk"] == "EPC" else "s", color=COL[r["v"]], ms=6, mec="k", mew=0.5)
    off = {"IGC033S10S1": (-6, -9, "right"), "EPC2215": (-6, -8, "right"), "EPC2034C": (5, 4, "left"),
           "EPC2071": (5, 3, "left")}.get(r["pn"], (6, -3, "left"))
    ax[0].annotate(r["pn"], (r["ctr"], r["r"]), textcoords="offset points", xytext=off[:2], fontsize=6, ha=off[2])
for v in (100, 200, 350, 650):
    ax[0].plot([], [], "o", color=COL[v], mec="k", mew=0.5, label="%d V class" % v)
ax[0].plot([], [], "s", color="w", mec="k", label="Infineon (circles: EPC)")
ax[0].set_xlabel("$C_{oss,tr}$ = $Q_{oss}/V_{test}$ [pF]")
ax[0].set_ylabel("$R_{DS(on)}$ typ. at 25 $^\\circ$C [m$\\Omega$]")
ax[0].set_xlim(15, 4000)
ax[0].set_ylim(0.4, 900)
ax[0].legend(loc="upper right", fontsize=6.5)
ax[0].set_title("(a) off-the-shelf GaN transistors", fontsize=8)
order = sorted(rows, key=lambda r: (r["v"], r["tau"]))
x = np.arange(len(order))
ax[1].bar(x, [r["p_min"] / ref["p_min"] for r in order], color=[COL[r["v"]] for r in order], edgecolor="k", lw=0.5)
for xi, r in zip(x, order):
    ax[1].text(xi, r["p_min"] / ref["p_min"] + 0.04, "%.1f" % (r["p_min"] / ref["p_min"]), ha="center", fontsize=6)
ax[1].set_xticks(x)
ax[1].set_xticklabels([r["pn"] for r in order], rotation=60, ha="right", fontsize=6)
ax[1].set_ylabel("min. $P_{cond}+P_{oss}$ of an SPB, rel. to EPC2361")
ax[1].set_title("(b) $\\propto\\sqrt{R_{DS(on)}C_{oss,tr}}$, any voltage class", fontsize=8)
ax[1].set_ylim(0, 2.8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "figures", "device_fom.pdf"))
fig.savefig(os.path.join(OUT, "figures", "device_fom.png"), dpi=160)

by_class = {v: min(r["tau"] for r in rows if r["v"] == v) for v in (100, 200, 350, 650)}
mac = {"TauEPC": "%.2f" % ref["tau"], "TauBestTwo": "%.1f" % by_class[200], "TauBestThree": "%.1f" % by_class[350],
       "TauBestSix": "%.1f" % by_class[650],
       "PminTwo": "%.1f" % math.sqrt(by_class[200] / ref["tau"]), "PminSix": "%.1f" % math.sqrt(by_class[650] / ref["tau"]),
       "PminThree": "%.1f" % math.sqrt(by_class[350] / ref["tau"]),
       "NoptEPC": "%.1f" % ref["n_opt"],
       "NoptIGT": "%.0f" % [r for r in rows if r["pn"] == "IGT65R025D2"][0]["n_opt"]}
with open(os.path.join(OUT, "device_numbers.tex"), "w") as f:
    f.write("% generated by scripts/device_survey.py\n")
    for k, v in mac.items():
        f.write("\\newcommand{\\%s}{%s}\n" % (k, v))
with open(os.path.join(ROOT, "reports", "paper", "device_table.tex"), "w") as f:
    f.write("% generated by scripts/device_survey.py (\\input is not allowed inside tabular: use \\DeviceRows)\n")
    f.write("\\newcommand{\\DeviceRows}{%\n")
    for r in order:
        f.write("%s & %d & %.3g & %d & %.0f & %.2f & %.1f & %.1f \\\\\n" % (
            r["pn"], r["v"], r["r"], round(r["ctr"]), r["vm"], r["tau"], r["n_mod"], r["p_min"] / ref["p_min"]))
    f.write("}\n")
for r in order:
    print("%-12s %3d V  R %6.2f mOhm  Coss,tr %6.0f pF  tau %5.2f ps  N %4.1f  n_opt %5.1f  Pmin rel %.2f" % (
        r["pn"], r["v"], r["r"], r["ctr"], r["tau"], r["n_mod"], r["n_opt"], r["p_min"] / ref["p_min"]))
print(mac)

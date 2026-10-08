"""
Slow-switching study: switching energies vs current for larger gate resistances, and when the classical
overlap formula  E_vi = V^2 I / (2 dv/dt) + I^2 V / (2 di/dt)  is valid for GaN.

    (run the LTspice sweeps in simulation/bb_spice/slow first)
    python scripts/slow_switching.py -> reports/design-report-v2/figures/slow_*.pdf|png, slow_numbers.tex,
                                        reports/building-block/data/slow_switching.json

Energies are integrated from the raw waveforms (sum of both low-side FETs, drain-terminal current) over 400 ns
from the gate command, only while V_DS > 1 V, so the conduction tail is excluded. The terminal measurement
includes the energy that charges C_oss at turn-off (stored, dissipated at the next turn-on inside the device).
"""
import glob
import json
import math
import os
import re
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "simulation", "dpt"))
from plot_dpt import read_raw  # noqa: E402

SL = os.path.join(ROOT, "simulation", "bb_spice", "slow")
OUT = os.path.join(ROOT, "reports", "design-report-v2")
FIG = os.path.join(OUT, "figures")
DATA = os.path.join(ROOT, "reports", "building-block", "data")
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3, "legend.fontsize": 7.5})

VBUS, TSTART, TON1, TOFF = 75.0, 0.5e-6, 10.667e-6, 1e-6
T1, T2 = TSTART + TON1, TSTART + TON1 + TOFF
WIN = 400e-9
IPK_LIST = [10, 30, 60, 90, 120, 141, 160]
EOSS_2 = 2 * 2.9e-6                      # E_oss(75 V) of the two low-side FETs (datasheet Q_oss / E_oss curve)
sz = json.load(open(os.path.join(DATA, "sizing.json")))
rs = json.load(open(os.path.join(DATA, "results.json")))


def cross(t, y, level, rising, t0):
    """First crossing time of y through level after t0 (linear interpolation)."""
    k0 = np.searchsorted(t, t0)
    yy = y[k0:] - level
    s = np.where((yy[:-1] < 0) & (yy[1:] >= 0))[0] if rising else np.where((yy[:-1] > 0) & (yy[1:] <= 0))[0]
    if len(s) == 0:
        return float("nan")
    k = k0 + s[0]
    return t[k] + (level - y[k]) * (t[k + 1] - t[k]) / (y[k + 1] - y[k])


def analyse(path):
    names, steps = read_raw(path)
    ix = {n.lower(): i for i, n in enumerate(names)}

    def col(a, n):
        return a[:, ix[n.lower()]]
    rows = []
    for a, ipk in zip(steps, IPK_LIST):
        t = a[:, 0]
        vl = col(a, "V(ql_d_l)") - col(a, "V(ql_s_l)")
        vr = col(a, "V(ql_d_r)") - col(a, "V(ql_s_r)")
        il, ir = col(a, "I(VILL)"), col(a, "I(VILR)")
        p = (vl * il + vr * ir) * (vl > 1.0)
        i_tot = il + ir

        def integ(ta):
            m = (t >= ta) & (t <= ta + WIN)
            return float(np.trapezoid(p[m], t[m]))
        isw = float(np.interp(T1, t, i_tot))
        # turn-off: V rise 20-80 %, terminal current fall 90-10 %
        tv = cross(t, vl, 0.8 * VBUS, True, T1) - cross(t, vl, 0.2 * VBUS, True, T1)
        ti = cross(t, i_tot, 0.1 * isw, False, T1) - cross(t, i_tot, 0.9 * isw, False, T1)
        dv_off, di_off = 0.6 * VBUS / tv, 0.8 * isw / ti
        # turn-on: V fall 80-20 %, current rise 10-90 % of the load current
        ion = abs(float(np.interp(T2, t, col(a, "I(Lload)"))))    # LTspice sign: current flows T_DCP -> T_AC
        tvn = cross(t, vl, 0.2 * VBUS, False, T2) - cross(t, vl, 0.8 * VBUS, False, T2)
        tin = cross(t, i_tot, 0.9 * ion, True, T2) - cross(t, i_tot, 0.1 * ion, True, T2)
        dv_on, di_on = 0.6 * VBUS / tvn, 0.8 * ion / tin
        m1, m2 = (t >= T1) & (t <= T1 + WIN), (t >= T2) & (t <= T2 + WIN)
        rows.append(dict(
            I=isw, Eoff=integ(T1), Eon=integ(T2), dvdt_off=dv_off / 1e9, didt_off=di_off / 1e9,
            dvdt_on=dv_on / 1e9, didt_on=di_on / 1e9,
            Evi_off=0.5 * VBUS ** 2 * isw / dv_off + 0.5 * isw ** 2 * VBUS / di_off,
            Evi_on=0.5 * VBUS ** 2 * ion / dv_on + 0.5 * ion ** 2 * VBUS / di_on,
            Evi_off_v=0.5 * VBUS ** 2 * isw / dv_off,
            vds_pk=float(vl[m1].max()), vdsh_pk=float((col(a, "V(qh_d_l)") - col(a, "V(qh_s_l)"))[m2].max()),
            vgsh_bump=float((col(a, "V(gthl)") - col(a, "V(qh_s_l)"))[m2].max()),
            id_pk=float(i_tot[m2].max()), i_on=ion))
    return rows


def main():
    res = {}
    for f in sorted(glob.glob(os.path.join(SL, "BB_slow_on*_off*.raw"))):
        if f.endswith(".op.raw") or f.endswith(".log.raw"):
            continue
        m = re.search(r"on(\d+)_off(\d+)", os.path.basename(f))
        key = "%s/%s" % (m.group(1), m.group(2))
        res[key] = analyse(f)
        r = [x for x in res[key] if abs(x["I"] - 141) < 8][0]
        print("Rg %-5s  I %5.1f  Eon %5.1f  Eoff %5.1f uJ | formula off %5.1f (dv %4.1f V/ns, di %5.1f A/ns) on %5.1f | "
              "Vds %5.1f VdsH %5.1f bump %4.2f Idpk %5.0f" % (
                  key, r["I"], r["Eon"] * 1e6, r["Eoff"] * 1e6, r["Evi_off"] * 1e6, r["dvdt_off"], r["didt_off"],
                  r["Evi_on"] * 1e6, r["vds_pk"], r["vdsh_pk"], r["vgsh_bump"], r["id_pk"]))
    order = [k for k in ("2/0", "2/2", "2/5", "2/10", "10/2", "10/10") if k in res]
    json.dump(dict(cases=res, order=order), open(os.path.join(DATA, "slow_switching.json"), "w"), indent=1)

    # ---------------- losses at the rated point for each case (fits, sinusoid, 50 kHz) ----------------
    th = np.linspace(0, np.pi, 2001)
    S = sz["spec"]
    r50 = [r for r in rs["loss_vs_f"] if r["f"] == 50e3][0]
    other = r50["total"] - r50["sw"]
    summ = {}
    for k in order:
        I = np.array([x["I"] for x in res[k]])
        pon = np.polyfit(I, [x["Eon"] for x in res[k]], 2)
        poff = np.polyfit(I, [x["Eoff"] for x in res[k]], 2)
        ia = sz["I_pk"] * np.sin(th)
        psw = float(np.mean(np.polyval(pon, ia) + np.polyval(poff, ia)) * 50e3)
        tot = other + psw
        r = [x for x in res[k] if abs(x["I"] - 141) < 8][0]
        summ[k] = dict(Psw=psw, total=tot, eta=100 * sz["P_rated"] / (sz["P_rated"] + tot), at141=r)

    # ---------------- figures ----------------
    cols = dict(zip(order, ("k", "C0", "C1", "C3", "C2", "C4")))
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for k in order:
        I = [x["I"] for x in res[k]]
        ax[0].plot(I, [x["Eon"] * 1e6 for x in res[k]], "o-", color=cols[k], ms=3, label="$R_{g,on}/R_{g,off}$ = %s $\\Omega$" % k)
        ax[1].plot(I, [x["Eoff"] * 1e6 for x in res[k]], "o-", color=cols[k], ms=3, label="%s $\\Omega$" % k)
    ax[1].axhline(EOSS_2 * 1e6, color="gray", ls=":", lw=1)
    ax[1].text(165, EOSS_2 * 1e6 - 3.5, "$E_{oss}$ of 2 FETs (stored, not lost)", fontsize=7, color="gray", ha="right")
    ax[0].set_title("turn-on energy (2 x EPC2361, 75 V)", fontsize=9)
    ax[1].set_title("turn-off energy", fontsize=9)
    for a in ax:
        a.set_xlabel("switched current [A]")
        a.set_ylabel("energy [$\\mu$J]")
        a.legend()
    save(fig, "slow_energy")

    # formula check: (a) turn-off, (b) turn-on, (c) turn-off dv/dt vs the load-driven limit
    c_eff = np.median([x["I"] / (x["dvdt_off"] * 1e9) for x in res["2/0"]]) if "2/0" in res else 5e-9
    fig, ax = plt.subplots(1, 3, figsize=(13.5, 3.9))
    for k in [k for k in ("2/0", "2/2", "2/5", "2/10") if k in res]:
        I = np.array([x["I"] for x in res[k]])
        ax[0].plot(I, [x["Eoff"] * 1e6 for x in res[k]], "o-", color=cols[k], ms=3, label="LTspice %s $\\Omega$" % k)
        ax[0].plot(I, [0.5 * VBUS ** 2 * x["I"] / (x["dvdt_off"] * 1e9) * 1e6 for x in res[k]], "--", color=cols[k], lw=1)
    if "2/10" in res:
        ax[0].plot([x["I"] for x in res["2/10"]], [x["Evi_off"] * 1e6 for x in res["2/10"]], ":", color=cols["2/10"], lw=1.2,
                   label="2/10: + $I^2V/(2\\,di/dt)$ term")
    ax[0].plot([], [], "k--", lw=1, label="$V^2I/(2\\,dv/dt)$ with LTspice $dv/dt$")
    ax[0].set_xlabel("switched current [A]")
    ax[0].set_ylabel("$E_{off}$ [$\\mu$J]")
    ax[0].set_title("turn-off: $dv/dt$ term only, valid when gate-driven", fontsize=9)
    ax[0].legend(fontsize=6.5)
    for k in [k for k in ("2/0", "10/2") if k in res]:
        I = np.array([x["I"] for x in res[k]])
        e0 = min(x["Eon"] for x in res[k])
        ax[1].plot(I, [x["Eon"] * 1e6 for x in res[k]], "o-", color=cols[k], ms=3, label="LTspice %s $\\Omega$" % k)
        ax[1].plot(I, [(e0 + 0.5 * VBUS ** 2 * x["i_on"] / (x["dvdt_on"] * 1e9)) * 1e6 for x in res[k]], "--", color=cols[k], lw=1,
                   label="%s: $E_{on}(0)$ + $dv/dt$ term" % k)
        ax[1].plot(I, [(e0 + x["Evi_on"]) * 1e6 for x in res[k]], ":", color=cols[k], lw=1.2,
                   label="%s: $E_{on}(0)$ + $dv/dt$ + $di/dt$ terms" % k)
    ax[1].set_xlabel("switched current [A]")
    ax[1].set_ylabel("$E_{on}$ [$\\mu$J]")
    ax[1].set_title("turn-on: $di/dt$ term needed only when slow", fontsize=9)
    ax[1].legend(fontsize=6.5)
    for k in order:
        ax[2].plot([x["I"] for x in res[k]], [x["dvdt_off"] for x in res[k]], "o-", color=cols[k], ms=3, label="%s $\\Omega$" % k)
    ii = np.linspace(0, 165, 50)
    ax[2].plot(ii, ii / c_eff / 1e9, "k:", lw=1, label="load-driven limit $I/C_{oss,tot}$ (%.1f nF)" % (c_eff * 1e9))
    ax[2].set_xlabel("switched current [A]")
    ax[2].set_ylabel("turn-off $dv/dt$ [V/ns]")
    ax[2].set_title("turn-off $dv/dt$: load-driven vs gate-driven", fontsize=9)
    ax[2].legend(fontsize=6.5)
    save(fig, "slow_formula")

    mac = {"SlowCoss": "%.1f" % (c_eff * 1e9)}
    tags = {"2/0": "Base", "2/2": "OffTwo", "2/5": "OffFive", "2/10": "OffTen", "10/2": "OnTen", "10/10": "Both"}
    for k in order:
        s = summ[k]
        a = s["at141"]
        t = tags[k]
        mac.update({"SlEon" + t: "%.1f" % (a["Eon"] * 1e6), "SlEoff" + t: "%.1f" % (a["Eoff"] * 1e6),
                    "SlFoff" + t: "%.1f" % (a["Evi_off"] * 1e6), "SlDvOff" + t: "%.0f" % a["dvdt_off"],
                    "SlDvOn" + t: "%.0f" % a["dvdt_on"], "SlVds" + t: "%.1f" % max(a["vds_pk"], a["vdsh_pk"]),
                    "SlBump" + t: "%.2f" % a["vgsh_bump"], "SlIdpk" + t: "%.0f" % a["id_pk"],
                    "SlPsw" + t: "%.2f" % s["Psw"], "SlEta" + t: "%.2f" % s["eta"], "SlTot" + t: "%.1f" % s["total"]})
    with open(os.path.join(OUT, "slow_numbers.tex"), "w") as fh:
        fh.write("% generated by scripts/slow_switching.py\n")
        for k_, v in mac.items():
            fh.write("\\newcommand{\\%s}{%s}\n" % (k_, v))
    print(json.dumps({k: dict(Psw=round(v["Psw"], 2), eta=round(v["eta"], 3)) for k, v in summ.items()}, indent=1))


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, name + ".pdf"))
    fig.savefig(os.path.join(FIG, name + ".png"), dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()

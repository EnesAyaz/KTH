"""
Gate-bump (Miller turn-on) study of the building block and voltage utilization of the 100 V transistors.

    LTspice: simulation/bb_spice/BB_bump.cir (bus 48/60/75 V x off-bias 0/-1/-2 V x external C_GS 0/1/2 nF, 141 A)
    python scripts/gate_bump_study.py -> reports/gate-bump/figures/*.pdf, reports/gate-bump/numbers.tex,
                                         reports/gate-bump/data/bump.json
"""
import json
import math
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "simulation", "dpt"))
import eth_style as es  # noqa: E402
from plot_dpt import read_raw  # noqa: E402

es.setup()
import matplotlib.pyplot as plt  # noqa: E402

C = es.C
SP = os.path.join(ROOT, "simulation", "bb_spice")
OUT = os.path.join(ROOT, "reports", "gate-bump")
for d in ("figures", "data"):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)
DATA = os.path.join(ROOT, "reports", "building-block", "data")
sz = json.load(open(os.path.join(DATA, "sizing.json")))
sl = json.load(open(os.path.join(DATA, "slow_switching.json")))["cases"]

# EPC2361 datasheet
QGD, CISS, CRSS, VTH_MIN, VTH_TYP, VGS_MIN, QG = 3.8e-9, 3.599e-9, 13e-12, 0.8, 1.1, -4.0, 28e-9
CGS = CISS - CRSS
I_RMS, I_PK, F_SW, T_DEAD, VDRV = 100.0, 141.4, 50e3, 10e-9, 5.0
VSD0, RSD, NPAR = 1.95, 5e-3, 2
P_BASE = dict(cond=5.55, cu=4.37, cap=0.39, sw=1.91, dead=0.20, gate=0.078)   # per leg at 75 V, 50 kHz (paper)
V_BUS_INV = 1200.0


def save(fig, name):
    fig.savefig(os.path.join(OUT, "figures", name + ".pdf"))
    fig.savefig(os.path.join(OUT, "figures", name + ".png"), dpi=200)
    plt.close(fig)
    print("wrote", name)


# ------------------------------------------------------------------ parse the LTspice log
def parse_log(path):
    raw = open(path, "rb").read()
    txt = raw.decode("utf-16-le", errors="ignore") if raw[1:2] == b"\x00" else raw.decode("latin-1")
    steps = [dict((k, float(v)) for k, v in re.findall(r"(\w+)=([-\deE.+]+)", l))
             for l in re.findall(r"^\.step (.*)$", txt, re.M)]
    meas = {}
    for block in re.split(r"\nMeasurement: ", txt)[1:]:
        lines = block.splitlines()
        name = lines[0].strip().lower()
        vals = []
        for l in lines[2:]:
            m = re.match(r"\s+(\d+)\s+([-\deE.+]+)", l)
            if not m:
                if vals:
                    break
                continue
            vals.append(float(m.group(2)))
        meas[name] = vals
    return steps, meas


steps, meas = parse_log(os.path.join(SP, "BB_bump.log"))
rows = []
for k, st in enumerate(steps):
    r = dict(V=st["vbus"], Vneg=st["vneg"], Cx=st["cgsx"])
    for m in ("vgsh_bump", "bump_amp", "vgsh_min", "vgsl_min", "vdsl_pk", "vdsh_pk", "eon_g", "eoff_g", "dvdt_on",
              "dvdt_off"):
        r[m] = meas[m][k] if m in meas and k < len(meas[m]) else float("nan")
    rows.append(r)
json.dump(rows, open(os.path.join(OUT, "data", "bump.json"), "w"), indent=1)


def get(V, Vneg, Cx):
    return [r for r in rows if r["V"] == V and r["Vneg"] == Vneg and abs(r["Cx"] - Cx) < 1e-12][0]


for r in rows:
    print("V=%2.0f Vneg=%.0f Cx=%.0fn  VGS,max %5.2f  amp %4.2f  VGS,min H %5.2f L %5.2f  VDS pk L %5.1f H %5.1f  "
          "Eon %5.1f Eoff %5.1f uJ  dv/dt %5.1f/%5.1f" % (
              r["V"], r["Vneg"], r["Cx"] * 1e9, r["vgsh_bump"], r["bump_amp"], r["vgsh_min"], r["vgsl_min"],
              r["vdsl_pk"], r["vdsh_pk"], r["eon_g"] * 1e6, r["eoff_g"] * 1e6, r["dvdt_on"], r["dvdt_off"]))

# ------------------------------------------------------------------ leg losses for every option
iabs_mean = 2 * I_PK / math.pi


def leg_loss(V, Vneg, Cx):
    r, b = get(V, Vneg, Cx), get(75, 0, 0)
    sw = P_BASE["sw"] * (r["eon_g"] + r["eoff_g"]) / (b["eon_g"] + b["eoff_g"])
    th = np.linspace(0, np.pi, 2001)
    i_abs = I_PK * np.sin(th)
    dead = 2 * F_SW * T_DEAD * np.mean((VSD0 + Vneg + RSD * i_abs / NPAR) * i_abs)
    # gate drive: four transistors, charge from -Vneg to VDRV incl. the external capacitor
    gate = 4 * F_SW * (QG + (CISS + Cx) * Vneg + Cx * VDRV) * (VDRV + Vneg)
    p = dict(cond=P_BASE["cond"], cu=P_BASE["cu"], cap=P_BASE["cap"], sw=sw, dead=dead, gate=gate)
    p["total"] = sum(p.values())
    p["P_leg"] = 1.0 * V / (2 * math.sqrt(2)) * I_RMS
    p["eta"] = p["P_leg"] / (p["P_leg"] + p["total"])
    return p


LOSS = {(V, n, c): leg_loss(V, n, c) for V in (48, 60, 75) for n in (0, 1, 2) for c in (0, 1e-9, 2e-9)}

# ------------------------------------------------------------------ Fig. 1: mechanism
names, wsteps = read_raw(os.path.join(SP, "BB_bump.raw"))
col = {n.lower(): i for i, n in enumerate(names)}
TON1 = 10.667e-6
T2 = 0.5e-6 + TON1 + 1e-6
k75 = steps.index([s for s in steps if s["vbus"] == 75 and s["vneg"] == 0 and s["cgsx"] == 0][0])
a = wsteps[k75]
t = a[:, 0]
m = (t > T2 - 2e-9) & (t < T2 + 25e-9)
vdsh = a[m, col["v(qh_d_l)"]] - a[m, col["v(qh_s_l)"]]
vgsh = a[m, col["v(gthl)"]] - a[m, col["v(qh_s_l)"]]
fig = plt.figure(figsize=(es.TXT_W, 1.9))
ax = fig.add_axes([0.06, 0.2, 0.25, 0.74])
ax.plot((t[m] - T2) * 1e9, vdsh, color=C["blue"])
ax.set_ylabel(r"$v_\mathrm{DS,H}$ (V)", color=C["blue"])
ax.set_ylim(-5, 100)
ax.set_xlabel("time after LS turn-on command (ns)")
ax2 = ax.twinx()
ax2.plot((t[m] - T2) * 1e9, vgsh, color=C["red"])
ax2.axhline(VTH_MIN, color=C["red"], ls="--", lw=0.7)
ax2.axhline(QGD / CGS, color="0.4", ls=":", lw=0.8)
ax2.set_ylim(-1.5, 2.0)
ax2.set_ylabel(r"$v_\mathrm{GS,H}$ (V)", color=C["red"])
ax2.grid(False)
es.tag(ax2, 24, VTH_MIN - 0.17, r"$V_\mathrm{th,min}$", C["red"], ha="right", fontsize=6.3)
es.tag(ax2, 24, QGD / CGS + 0.15, r"$Q_\mathrm{GD}/C_\mathrm{GS}$", "0.35", ha="right", fontsize=6.3)
es.panel(ax, "(a)", dx=-0.25, dy=-0.17)

ax = fig.add_axes([0.42, 0.2, 0.24, 0.74])
for k, c in (("2/0", "k"), ("2/2", C["blue"]), ("2/5", C["yellow"]), ("2/10", C["red"]), ("10/2", C["green"])):
    ax.plot([x["I"] for x in sl[k]], [x["vgsh_bump"] for x in sl[k]], "-o", color=c, ms=2.5)
    es.tag(ax, 162, sl[k][-1]["vgsh_bump"], k + r" $\Omega$", c, fontsize=6)
ax.axhline(VTH_MIN, color=C["red"], ls="--", lw=0.7)
ax.set_xlim(0, 200)
ax.set_ylim(0.6, 1.4)
ax.set_xlabel(r"switched current $I$ (A)")
ax.set_ylabel(r"$v_\mathrm{GS,H,max}$ (V)")
es.panel(ax, "(b)", dx=-0.25, dy=-0.17)

ax = fig.add_axes([0.76, 0.2, 0.22, 0.74])
Vs = [48, 60, 75]
ax.plot(Vs, [get(V, 0, 0)["vgsh_bump"] for V in Vs], "-o", color="k", ms=3)
ax.axhline(VTH_MIN, color=C["red"], ls="--", lw=0.7)
ax.set_xlim(40, 80)
ax.set_ylim(0.4, 1.2)
ax.set_xlabel(r"bus voltage $V_m$ (V)")
ax.set_ylabel(r"$v_\mathrm{GS,H,max}$ (V)")
es.panel(ax, "(c)", dx=-0.3, dy=-0.17)
save(fig, "bump_mechanism")

# ------------------------------------------------------------------ Fig. 2: mitigation
fig, axs = plt.subplots(1, 3, figsize=(es.TXT_W, 1.9), gridspec_kw=dict(wspace=0.38))
for ax, V, lab in ((axs[0], 75, "(a)"), (axs[1], 60, "(b)")):
    for n, c in ((0, "k"), (1, C["blue"]), (2, C["green"])):
        ys = [get(V, n, cx)["vgsh_bump"] for cx in (0, 1e-9, 2e-9)]
        ax.plot([0, 1, 2], ys, "-o", color=c, ms=3)
        es.tag(ax, 2.08, ys[-1], r"$-%d$ V" % n if n else "0 V", c, fontsize=6.3)
    ax.axhline(VTH_MIN, color=C["red"], ls="--", lw=0.7)
    ax.axhline(0, color="0.5", lw=0.5)
    ax.set_xlim(-0.2, 2.6)
    ax.set_ylim(-2.3, 1.3)
    ax.set_xticks([0, 1, 2])
    ax.set_xlabel(r"external $C_\mathrm{GS}$ (nF)")
    ax.set_ylabel(r"$v_\mathrm{GS,H,max}$ (V)")
    ax.text(0.04, 0.05, "$V_m$ = %d V" % V, transform=ax.transAxes, fontsize=6.5)
    es.panel(ax, lab, dx=-0.3, dy=-0.17)
ax = axs[2]
opts = [("0 V, 0 nF", 0, 0), ("$-$1 V", 1, 0), ("$-$2 V", 2, 0), ("1 nF", 0, 1e-9), ("2 nF", 0, 2e-9), ("$-$1 V, 1 nF", 1, 1e-9)]
x = np.arange(len(opts))
for j, (V, c) in enumerate(((75, C["blue"]), (60, C["red"]))):
    ax.bar(x + (j - 0.5) * 0.38, [100 * LOSS[(V, n, cx)]["eta"] for _, n, cx in opts], 0.38, color=c, alpha=0.8,
           edgecolor="k", lw=0.4)
    es.tag(ax, 3.9 + j * 1.0, 99.66, "%d V" % V, c, fontsize=6.3)
ax.axhline(99.5, color="k", ls="--", lw=0.7)
ax.set_xticks(x)
ax.set_xticklabels([o[0] for o in opts], rotation=35, ha="right", fontsize=5.6)
ax.set_ylim(99.3, 99.7)
ax.set_ylabel(r"leg efficiency (%)")
ax.grid(axis="x", visible=False)
es.panel(ax, "(c)", dx=-0.3, dy=-0.3)
save(fig, "bump_mitigation")

# ------------------------------------------------------------------ Fig. 3: voltage utilization
OVS = {V: max(get(V, 0, 0)["vdsl_pk"], get(V, 0, 0)["vdsh_pk"]) - V for V in Vs}   # overshoot at 141 A
ovs_fit = np.polyfit(Vs, [OVS[V] for V in Vs], 1)
K_BATT = 1.2                                       # maximum / nominal submodule voltage (75 V -> 90 V)
vm = np.linspace(40, 85, 200)
vpk = K_BATT * vm + np.polyval(ovs_fit, K_BATT * vm)
bump = np.polyfit(Vs, [get(V, 0, 0)["vgsh_bump"] for V in Vs], 1)
vm_80 = float(np.interp(80, vpk, vm))
vm_90 = float(np.interp(90, vpk, vm))
vpk1 = vm + np.polyval(ovs_fit, vm)
vm_80_k1 = float(np.interp(80, vpk1, vm))
vm_90_k1 = float(np.interp(90, vpk1, vm))
vpk_75 = 1.2 * 75 + np.polyval(ovs_fit, 90)
vpk_60 = 1.2 * 60 + np.polyval(ovs_fit, 72)
fig, axs = plt.subplots(1, 3, figsize=(es.TXT_W, 1.9), gridspec_kw=dict(wspace=0.45))
ax = axs[0]
for kb, c in ((1.0, C["blue"]), (1.1, C["purple"]), (1.2, "k")):
    vp = kb * vm + np.polyval(ovs_fit, kb * vm)
    ax.plot(vm, vp, color=c)
    es.tag(ax, 47, kb * 47 + np.polyval(ovs_fit, kb * 47) + 2.5, r"$k$=%.1f" % kb, c, ha="center", fontsize=6)
ax.axhline(100, color=C["red"], lw=0.9)
ax.axhline(90, color=C["yellow"], ls="--", lw=0.8)
ax.axhline(80, color=C["green"], ls="--", lw=0.8)
ax.axvline(75, color="0.5", ls=":", lw=0.7)
ax.axvline(60, color="0.5", ls=":", lw=0.7)
es.tag(ax, 41, 102, "rating 100 V", C["red"], fontsize=6)
es.tag(ax, 41, 91.5, "90 V", C["yellow"], fontsize=6)
es.tag(ax, 41, 81.5, "80 V (80 %)", C["green"], fontsize=6)
ax.set_xlim(40, 85)
ax.set_ylim(40, 115)
ax.set_xlabel(r"nominal submodule voltage $V_m$ (V)")
ax.set_ylabel(r"peak $v_\mathrm{DS}$ at $k\,V_m$ (V)")
es.panel(ax, "(a)", dx=-0.3, dy=-0.17)
ax = axs[1]
VMS = np.array([48, 60, 75])
eta_inv = [100 * LOSS[(V, 0, 0)]["eta"] for V in VMS]
eta_neg = [100 * LOSS[(V, 2, 0)]["eta"] for V in VMS]
ax.plot(VMS, eta_inv, "-o", color=C["blue"], ms=3)
ax.plot(VMS, eta_neg, "--s", color=C["green"], ms=3)
es.tag(ax, 49, eta_inv[0] + 0.04, "0 V off", C["blue"], fontsize=6)
es.tag(ax, 60, eta_neg[1] - 0.06, r"$-$2 V off", C["green"], fontsize=6)
ax.set_xlabel(r"$V_m$ (V)")
ax.set_ylabel(r"inverter efficiency (%)")
ax.set_xlim(44, 80)
es.panel(ax, "(b)", dx=-0.3, dy=-0.17)
ax = axs[2]
N = V_BUS_INV / VMS
ax.bar(VMS, 12 * N, width=6, color=(*C["red"], 0.6), edgecolor="k", lw=0.4)
for v, n in zip(VMS, N):
    ax.text(v, 12 * n + 6, "$N$=%d" % round(n), ha="center", fontsize=6)
ax.set_ylim(0, 360)
ax.set_xlabel(r"$V_m$ (V)")
ax.set_ylabel("transistors per inverter")
ax.grid(axis="x", visible=False)
ax2 = ax.twinx()
ax2.plot(VMS, [V * I_RMS / (2 * math.sqrt(2)) / 4 for V in VMS], "-o", color=C["blue"], ms=3)
ax2.set_ylim(0, 1000)
ax2.set_ylabel("power per transistor (W)", color=C["blue"])
ax2.tick_params(axis="y", colors=C["blue"])
ax2.grid(False)
es.panel(ax, "(c)", dx=-0.32, dy=-0.17)
save(fig, "utilization")

# ------------------------------------------------------------------ numbers
b75, b60, b48 = get(75, 0, 0), get(60, 0, 0), get(48, 0, 0)
mac = dict(BmpSeventyFive="%.2f" % b75["vgsh_bump"], BmpSixty="%.2f" % b60["vgsh_bump"], BmpFortyEight="%.2f" % b48["vgsh_bump"],
           BmpDivider="%.2f" % (QGD / CGS),
           BmpNegOneSF="%.2f" % get(75, 1, 0)["vgsh_bump"], BmpNegTwoSF="%.2f" % get(75, 2, 0)["vgsh_bump"],
           BmpCOneSF="%.2f" % get(75, 0, 1e-9)["vgsh_bump"], BmpCTwoSF="%.2f" % get(75, 0, 2e-9)["vgsh_bump"],
           BmpNegOneCOneSF="%.2f" % get(75, 1, 1e-9)["vgsh_bump"],
           BmpNegOneSix="%.2f" % get(60, 1, 0)["vgsh_bump"], BmpNegTwoSix="%.2f" % get(60, 2, 0)["vgsh_bump"],
           BmpCTwoSix="%.2f" % get(60, 0, 2e-9)["vgsh_bump"],
           VgsMinNegTwo="%.2f" % min(get(V, 2, c)["vgsh_min"] for V in Vs for c in (0, 1e-9, 2e-9)),
           VgsLMinNegTwo="%.2f" % min(get(V, 2, c)["vgsl_min"] for V in Vs for c in (0, 1e-9, 2e-9)),
           OvsSF="%.1f" % OVS[75], OvsSix="%.1f" % OVS[60], OvsFE="%.1f" % OVS[48],
           VmEighty="%.0f" % vm_80, VmNinety="%.0f" % vm_90, VmEightyK="%.0f" % vm_80_k1, VmNinetyK="%.0f" % vm_90_k1,
           VpkSF="%.0f" % vpk_75, VpkSix="%.0f" % vpk_60,
           EtaSF="%.2f" % (100 * LOSS[(75, 0, 0)]["eta"]), EtaSix="%.2f" % (100 * LOSS[(60, 0, 0)]["eta"]),
           EtaFE="%.2f" % (100 * LOSS[(48, 0, 0)]["eta"]),
           EtaSFNegTwo="%.2f" % (100 * LOSS[(75, 2, 0)]["eta"]), EtaSixNegTwo="%.2f" % (100 * LOSS[(60, 2, 0)]["eta"]),
           EtaSFCTwo="%.2f" % (100 * LOSS[(75, 0, 2e-9)]["eta"]),
           PswSix="%.2f" % LOSS[(60, 0, 0)]["sw"], PswFE="%.2f" % LOSS[(48, 0, 0)]["sw"],
           PdeadNegTwo="%.2f" % LOSS[(75, 2, 0)]["dead"], PgateNegTwo="%.2f" % LOSS[(75, 2, 0)]["gate"],
           PgateCTwo="%.2f" % LOSS[(75, 0, 2e-9)]["gate"],
           EonSF="%.1f" % (b75["eon_g"] * 1e6), EonSix="%.1f" % (b60["eon_g"] * 1e6), EoffSF="%.1f" % (b75["eoff_g"] * 1e6),
           EonSFCTwo="%.1f" % (get(75, 0, 2e-9)["eon_g"] * 1e6), EoffSFCTwo="%.1f" % (get(75, 0, 2e-9)["eoff_g"] * 1e6),
           EonSFNegTwo="%.1f" % (get(75, 2, 0)["eon_g"] * 1e6), EoffSFNegTwo="%.1f" % (get(75, 2, 0)["eoff_g"] * 1e6),
           DvOnSF="%.0f" % b75["dvdt_on"], DvOnSix="%.0f" % b60["dvdt_on"])
for V, w in ((75, "SF"), (60, "Six"), (48, "FE")):
    eta = LOSS[(V, 0, 0)]["eta"]
    n_sm = V_BUS_INV / V
    mac["InvLoss" + w] = "%.0f" % (150e3 * (1 / eta - 1))
    mac["Nsm" + w] = "%.0f" % n_sm
    mac["Ntr" + w] = "%.0f" % (12 * n_sm)
    mac["Ndrv" + w] = "%.0f" % (3 * n_sm)
    mac["Ptr" + w] = "%.0f" % (V * I_RMS / (2 * math.sqrt(2)) * 1.15 / 4)
    mac["Vpk" + w + "k"] = "%.0f" % (1.2 * V + np.polyval(ovs_fit, 1.2 * V))
    mac["Vpk" + w + "one"] = "%.0f" % (V + np.polyval(ovs_fit, V))
    mac["Util" + w] = "%.0f" % (V)
with open(os.path.join(OUT, "numbers.tex"), "w") as f:
    f.write("% generated by scripts/gate_bump_study.py\n")
    for k, v in mac.items():
        f.write("\\newcommand{\\%s}{%s}\n" % (k, v))
rows_tex = []
for V in (75, 60, 48):
    for n, cx, lab in ((0, 0, "0\\,V, --"), (1, 0, "$-1$\\,V, --"), (2, 0, "$-2$\\,V, --"), (0, 1e-9, "0\\,V, 1\\,nF"),
                       (0, 2e-9, "0\\,V, 2\\,nF"), (1, 1e-9, "$-1$\\,V, 1\\,nF")):
        r, p = get(V, n, cx), LOSS[(V, n, cx)]
        rows_tex.append("%d & %s & %.2f & %.2f & %.1f & %.1f & %.2f & %.2f & %.2f & %.2f \\\\" % (
            V, lab, r["vgsh_bump"], r["vgsh_min"], r["eon_g"] * 1e6, r["eoff_g"] * 1e6, p["sw"], p["dead"], p["gate"],
            100 * p["eta"]))
    rows_tex.append("\\midrule")
with open(os.path.join(OUT, "table.tex"), "w") as f:
    f.write("\\newcommand{\\BumpRows}{%\n" + "\n".join(rows_tex[:-1]) + "\n}\n")
print(json.dumps(mac, indent=0))

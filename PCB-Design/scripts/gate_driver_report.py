"""
Figures and numbers for the gate-driver report (reports/gate-driver):
  driver output stage (sink / source), negative off-voltage (gate bump vs dead-time loss), scaling of the number of
  paralleled transistors per driver channel and gate-loop length.

LTspice inputs (simulation/bb_spice): BB_bump.log, BB_bump_rpd.log, BB_2EDF7275K.log, BB_drv_share.log, BB_gate_len.log
    python scripts/gate_driver_report.py -> reports/gate-driver/figures/*.pdf, reports/gate-driver/numbers.tex
"""
import math
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import eth_style as es  # noqa: E402

es.setup()
import matplotlib.pyplot as plt  # noqa: E402

C = es.C
SP = os.path.join(ROOT, "simulation", "bb_spice")
OUT = os.path.join(ROOT, "reports", "gate-driver")
os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
VTH_MIN, VGS_MIN = 0.8, -4.0
F_SW, I_PK, VSD0, RSD, NPAR = 50e3, 141.4, 1.95, 5e-3, 2
R_INT, VDRV = 0.4, 5.0
P_LEG = 75 / (2 * math.sqrt(2)) * 100.0
P_OTHER = 5.55 + 4.37 + 0.39 + 0.078            # conduction, copper, MLCC, gate (paper, 50 kHz)
PSW_REF, E_REF = 1.91, 48.9e-6                  # switching loss per leg and E_on + E_off of the reference model


def parse(name):
    raw = open(os.path.join(SP, name), "rb").read()
    txt = raw.decode("utf-16-le", errors="ignore") if raw[1:2] == b"\x00" else raw.decode("latin-1")
    steps = [dict((k, float(v)) for k, v in re.findall(r"(\w+)=([-\deE.+]+)", l))
             for l in re.findall(r"^\.step (.*)$", txt, re.M)]
    meas = {}
    for block in re.split(r"\nMeasurement: ", txt)[1:]:
        lines = block.splitlines()
        vals = []
        for l in lines[2:]:
            m = re.match(r"\s+(\d+)\s+([-\deE.+]+)", l)
            if not m:
                if vals:
                    break
                continue
            vals.append(float(m.group(2)))
        meas[lines[0].strip().lower()] = vals
    return [dict(st, **{k: v[i] for k, v in meas.items() if i < len(v)}) for i, st in enumerate(steps)]


def dead_loss(vneg, t_dead, f=F_SW):
    th = np.linspace(0, np.pi, 2001)
    i = I_PK * np.sin(th)
    return 2 * f * t_dead * float(np.mean((VSD0 + vneg + RSD * i / NPAR) * i))


def save(fig, name):
    fig.savefig(os.path.join(OUT, "figures", name + ".pdf"))
    fig.savefig(os.path.join(OUT, "figures", name + ".png"), dpi=200)
    plt.close(fig)
    print("wrote", name)


bump = parse("BB_bump.log")
rpd = parse("BB_bump_rpd.log")
edf = parse("BB_2EDF7275K.log")
share = parse("BB_drv_share.log")
glen = parse("BB_gate_len.log")
mac = {}

# ------------------------------------------------------------------ Fig. 1: driver output stage
fig, axs = plt.subplots(1, 3, figsize=(es.TXT_W, 1.95), gridspec_kw=dict(wspace=0.5))
ax = axs[0]
r = [x["rpd"] for x in rpd]
ax.plot(r, [x["eoff_g"] * 1e6 for x in rpd], "-o", color=C["blue"], ms=3)
ax.set_xlabel(r"driver pull-down $R_\mathrm{pd}$ ($\Omega$)")
ax.set_ylabel(r"$E_\mathrm{off}$ ($\mu$J)", color=C["blue"])
ax.set_ylim(6, 12)
ax2 = ax.twinx()
ax2.plot(r, [x["vgsh_bump"] for x in rpd], "-s", color=C["red"], ms=3)
ax2.axhline(VTH_MIN, color=C["red"], ls="--", lw=0.7)
ax2.set_ylim(0.6, 1.3)
ax2.set_ylabel(r"$v_\mathrm{GS,H,max}$ (V)", color=C["red"])
ax2.grid(False)
es.panel(ax, "(a)", dx=-0.3, dy=-0.18)
ax = axs[1]
labs = ["ref\n0", "typ\n0", "max\n0", "ref\n$-$1", "typ\n$-$1", "max\n$-$1"]
sel = [x for x in edf if x["vbus"] == 75]
sel = sorted(sel, key=lambda x: (x["vneg"], x["drv"]))
xx = np.arange(len(sel))
ax.bar(xx, [x["eon_g"] * 1e6 for x in sel], 0.6, color=C["red"], alpha=0.8, edgecolor="k", lw=0.4)
ax.bar(xx, [x["eoff_g"] * 1e6 for x in sel], 0.6, bottom=[x["eon_g"] * 1e6 for x in sel], color="w", edgecolor=C["blue"],
       hatch="////", lw=0.6)
ax.set_xticks(xx)
ax.set_xticklabels(labs, fontsize=6)
ax.set_xlabel("driver, off-state voltage (V)")
ax.set_ylabel(r"$E_\mathrm{on}$ + $E_\mathrm{off}$ ($\mu$J)")
ax.grid(axis="x", visible=False)
es.tag(ax, -0.4, 72, "solid: $E_\\mathrm{on}$, hatched: $E_\\mathrm{off}$", "0.3", fontsize=6)
ax.set_ylim(0, 80)
es.panel(ax, "(b)", dx=-0.3, dy=-0.18)
ax = axs[2]
nn = np.arange(1, 7)
for vb, c, lab in ((1.0, C["blue"], "+5/$-$1 V"), (0.0, C["green"], "+5/0 V")):
    ax.plot(nn, (VDRV + vb) / (0.35 + R_INT / nn), "-o", color=c, ms=3)
    es.tag(ax, 6.15, (VDRV + vb) / (0.35 + R_INT / 6), lab, c, fontsize=6)
ax.axhline(8.0, color="k", ls="--", lw=0.7)
ax.axhline(10.2, color="k", ls=":", lw=0.7)
es.tag(ax, 1.0, 8.5, "8 A rated", "k", fontsize=6)
es.tag(ax, 1.0, 10.7, "10.2 A limit", "k", fontsize=6)
ax.set_xlim(0.7, 7.6)
ax.set_ylim(0, 18)
ax.set_xlabel("transistors per driver channel $n$")
ax.set_ylabel("peak sink current (A)")
es.panel(ax, "(c)", dx=-0.3, dy=-0.18)
save(fig, "drv_output_stage")

# ------------------------------------------------------------------ Fig. 2: negative off-voltage
fig, axs = plt.subplots(1, 3, figsize=(es.TXT_W, 1.95), gridspec_kw=dict(wspace=0.45))
ax = axs[0]
b75 = sorted([x for x in bump if x["vbus"] == 75 and x["cgsx"] == 0], key=lambda x: x["vneg"])
vn = [x["vneg"] for x in b75]
ax.plot(vn, [x["vgsh_bump"] for x in b75], "-o", color=C["red"], ms=3)
ax.plot(vn, [x["vgsh_min"] for x in b75], "-s", color=C["blue"], ms=3)
ax.axhline(VTH_MIN, color=C["red"], ls="--", lw=0.7)
ax.axhline(VGS_MIN, color=C["blue"], ls="--", lw=0.7)
es.tag(ax, 0.05, VTH_MIN + 0.3, r"$V_\mathrm{th,min}$", C["red"], fontsize=6)
es.tag(ax, 0.05, VGS_MIN + 0.3, r"$V_\mathrm{GS,min}$ rating", C["blue"], fontsize=6)
es.tag(ax, 1.3, 0.45, "peak (bump)", C["red"], fontsize=6)
es.tag(ax, 1.25, -2.0, "undershoot", C["blue"], fontsize=6)
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(["0", "$-1$", "$-2$"])
ax.set_xlabel(r"off-state gate voltage (V)")
ax.set_ylabel(r"high-side $v_\mathrm{GS}$ (V)")
ax.set_ylim(-4.5, 1.6)
es.panel(ax, "(a)", dx=-0.3, dy=-0.18)
ax = axs[1]
td = np.linspace(2e-9, 25e-9, 50)
for v, c in ((0, C["green"]), (1, C["blue"]), (2, C["purple"])):
    ax.plot(td * 1e9, [dead_loss(v, t) for t in td], color=c)
    es.tag(ax, 25.3, dead_loss(v, 25e-9), ("0 V", "$-$1 V", "$-$2 V")[v], c, fontsize=6)
ax.axvline(10, color="0.5", ls=":", lw=0.7)
ax.set_xlim(0, 29)
ax.set_xlabel(r"dead time $t_\mathrm{d}$ (ns)")
ax.set_ylabel(r"dead-time loss per leg (W)")
es.panel(ax, "(b)", dx=-0.3, dy=-0.18)
ax = axs[2]
fs = np.linspace(20e3, 100e3, 30)
e0 = {v: [x for x in edf if x["vbus"] == 75 and x["drv"] == 1 and x["vneg"] == min(v, 1)][0] for v in (0, 1)}
for v, c in ((0, C["green"]), (1, C["blue"]), (2, C["purple"])):
    ee = e0[min(v, 1)]
    psw = PSW_REF * (ee["eon_g"] + ee["eoff_g"]) / E_REF
    if v == 2:                                    # 2EDF -2 V not simulated: scale the reference -2 V / -1 V energies
        b2 = [x for x in bump if x["vbus"] == 75 and x["cgsx"] == 0 and x["vneg"] == 2][0]
        b1 = [x for x in bump if x["vbus"] == 75 and x["cgsx"] == 0 and x["vneg"] == 1][0]
        psw *= (b2["eon_g"] + b2["eoff_g"]) / (b1["eon_g"] + b1["eoff_g"])
    eta = [100 * P_LEG / (P_LEG + P_OTHER + psw * f / 50e3 + dead_loss(v, 10e-9, f)) for f in fs]
    ax.plot(fs / 1e3, eta, color=c)
    es.tag(ax, 101, eta[-1], ("0 V", "$-$1 V", "$-$2 V")[v], c, fontsize=6)
ax.axhline(99.5, color="k", ls="--", lw=0.7)
ax.set_xlim(20, 115)
ax.set_xlabel(r"$f_\mathrm{sw}$ (kHz)")
ax.set_ylabel(r"leg efficiency (%)")
es.panel(ax, "(c)", dx=-0.3, dy=-0.18)
save(fig, "drv_negative_rail")

# ------------------------------------------------------------------ Fig. 3: more transistors per driver
fig, axs = plt.subplots(1, 3, figsize=(es.TXT_W, 1.95), gridspec_kw=dict(wspace=0.45))
ax = axs[0]
ns = [x["nsh"] for x in share]
ax.plot(ns, [x["eon_g"] / 2 * 1e6 for x in share], "-o", color=C["red"], ms=3)
ax.plot(ns, [x["eoff_g"] / 2 * 1e6 for x in share], "-s", color=C["blue"], ms=3)
es.tag(ax, 4.2, share[2]["eon_g"] / 2 * 1e6 + 2.5, r"$E_\mathrm{on}$", C["red"], fontsize=6.5)
es.tag(ax, 4.2, share[2]["eoff_g"] / 2 * 1e6 + 2.5, r"$E_\mathrm{off}$", C["blue"], fontsize=6.5)
ax.set_xticks(ns)
ax.set_xlabel("transistors per driver channel $n$")
ax.set_ylabel(r"energy per transistor ($\mu$J)")
es.panel(ax, "(a)", dx=-0.3, dy=-0.18)
ax = axs[1]
lg = [x["lgx"] * 1e9 for x in glen]
ax.plot(lg, [x["eon_g"] / 2 * 1e6 for x in glen], "-o", color=C["red"], ms=3)
ax.plot(lg, [x["eoff_g"] / 2 * 1e6 for x in glen], "-s", color=C["blue"], ms=3)
es.tag(ax, 0.3, glen[0]["eon_g"] / 2 * 1e6 - 2.5, r"$E_\mathrm{on}$", C["red"], fontsize=6.5)
es.tag(ax, 0.3, glen[0]["eoff_g"] / 2 * 1e6 + 2.0, r"$E_\mathrm{off}$", C["blue"], fontsize=6.5)
ax2 = ax.twinx()
ax2.plot(lg, [x["vgsh_bump"] for x in glen], "-^", color=C["purple"], ms=3)
ax2.set_ylabel(r"$v_\mathrm{GS,H,max}$ (V)", color=C["purple"])
ax2.grid(False)
ax.set_xlabel(r"extra gate-loop inductance (nH)")
ax.set_ylabel(r"energy per transistor ($\mu$J)")
es.panel(ax, "(b)", dx=-0.3, dy=-0.18)
ax = axs[2]
nn = np.array([1, 2, 3, 4, 6])
legs = 48
one = legs * 1 * np.ones_like(nn)
pair = legs * np.ceil(nn / 2)
ax.plot(nn, pair, "-o", color=C["green"], ms=3)
ax.plot(nn, one, "--s", color="0.4", ms=3)
es.tag(ax, 4.3, pair[3] + 12, "one channel\nper pair", C["green"], fontsize=6)
es.tag(ax, 3.5, 30, "one channel per switch\n(shared output stage)", "0.4", fontsize=6)
ax.set_xticks(nn)
ax.set_xlabel("transistors per switch $n$")
ax.set_ylabel("dual-channel drivers per inverter")
ax.set_ylim(0, 170)
es.panel(ax, "(c)", dx=-0.3, dy=-0.18)
save(fig, "drv_scaling")

# ------------------------------------------------------------------ numbers
g = lambda lst, **kw: [x for x in lst if all(abs(x[k] - v) < 1e-12 for k, v in kw.items())][0]
mac.update(
    RpdBumpLo="%.2f" % rpd[0]["vgsh_bump"], RpdBumpHi="%.2f" % rpd[-1]["vgsh_bump"],
    RpdEoffLo="%.1f" % (rpd[0]["eoff_g"] * 1e6), RpdEoffMid="%.1f" % (rpd[1]["eoff_g"] * 1e6), RpdEoffHi="%.1f" % (rpd[-1]["eoff_g"] * 1e6),
    DeadZero="%.2f" % dead_loss(0, 10e-9), DeadOne="%.2f" % dead_loss(1, 10e-9), DeadTwo="%.2f" % dead_loss(2, 10e-9),
    DeadOneTwenty="%.2f" % dead_loss(1, 20e-9), DeadOneFive="%.2f" % dead_loss(1, 5e-9),
    SnkTwo="%.1f" % (6 / (0.35 + R_INT / 2)), SnkOne="%.1f" % (6 / (0.35 + R_INT)), SnkFour="%.1f" % (6 / (0.35 + R_INT / 4)),
    SnkTwoZero="%.1f" % (5 / (0.35 + R_INT / 2)),
)
for x in share:
    w = {2: "Two", 3: "Three", 4: "Four", 6: "Six"}[int(x["nsh"])]
    mac["ShEon" + w] = "%.1f" % (x["eon_g"] / 2 * 1e6)
    mac["ShEoff" + w] = "%.1f" % (x["eoff_g"] / 2 * 1e6)
    mac["ShBump" + w] = "%.2f" % x["vgsh_bump"]
for x in glen:
    w = {0: "Zero", 2: "Two", 4: "Four", 8: "Eight"}[int(round(x["lgx"] * 1e9))]
    mac["LgEon" + w] = "%.1f" % (x["eon_g"] / 2 * 1e6)
    mac["LgEoff" + w] = "%.1f" % (x["eoff_g"] / 2 * 1e6)
    mac["LgBump" + w] = "%.2f" % x["vgsh_bump"]
    mac["LgVdsl" + w] = "%.1f" % x["vdsl_pk"]
with open(os.path.join(OUT, "numbers.tex"), "w") as f:
    f.write("% generated by scripts/gate_driver_report.py\n")
    for k, v in mac.items():
        f.write("\\newcommand{\\%s}{%s}\n" % (k, v))
for k, v in mac.items():
    print(k, v)
for lst, nm in ((share, "share"), (glen, "gate length")):
    print(nm)
    for x in lst:
        print({k: (round(v, 3) if abs(v) > 1e-3 else v) for k, v in x.items() if k in ("nsh", "lgx", "vgsh_bump", "vgsh_min",
                                                                                          "eon_g", "eoff_g", "vdsl_pk", "vdsh_pk", "dvdt_on", "dvdt_off")})

"""
Build reports/slides/spb_design_flow.tex from the template spb_design_flow.tpl.tex:
  %%FRAME{title}  -> the frame with that title from spb_bb_slides.tex (verification and fabrication slides)
  %%NTABLE        -> loss table vs n (reports/slides/data/flow_numbers.json)
  %%TWOTEXT       -> two-block LTspice summary
  \\IRMS ...       -> number macros, defined in the preamble

    python scripts/make_flow_slides.py   (after scripts/design_flow_figures.py)
"""
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SL = os.path.join(ROOT, "reports", "slides")
tpl = io.open(os.path.join(SL, "spb_design_flow.tpl.tex"), encoding="utf-8").read()
old = io.open(os.path.join(SL, "spb_bb_slides.tex"), encoding="utf-8").read()
N = json.load(open(os.path.join(SL, "data", "flow_numbers.json")))

# frames reused from the building-block deck, with the 300 kW remarks adapted to the new operating point
PATCH = {
    r"\item 300\,kW: two blocks per leg, 25\,W per leg, same efficiency": r"\item At 300\,kW ($\cos\varphi$ = 0.9) the block carries 114\,A$_\mathrm{rms}$: see the previous slide",
    r"\item Total capacitor loss $\approx$\,0.39\,W per block (0.78\,W per leg at 300\,kW)": r"\item Total capacitor loss $\approx$\,0.39\,W per block at 100\,A$_\mathrm{rms}$",
}


def frame(title):
    k = old.find(r"\begin{frame}{%s}" % title)
    if k < 0:
        raise KeyError(title)
    e = old.index(r"\end{frame}", k) + len(r"\end{frame}")
    f = old[k:e]
    for a, b in PATCH.items():
        f = f.replace(a, b)
    return f


out = re.sub(r"^%%FRAME\{(.*)\}\s*$", lambda m: frame(m.group(1)), tpl, flags=re.M)

# loss table vs n
R = N["npar"]
rows = [("Loss per leg (W)", "tot", "%.1f"), ("\\quad conduction at $T_j$ (W)", "cond", "%.1f"),
        ("\\quad conduction at 25\\,$^\\circ$C (W)", "cond25", "%.1f"), ("\\quad switching (W)", "sw", "%.1f"),
        ("Efficiency (\\%)", "eta", "%.2f"), ("Loss per device (W)", "pdev", "%.1f"), ("$T_j$ ($^\\circ$C)", "tj", "%.0f"),
        ("Peak $V_\\mathrm{DS}$ (V)", "vpk", "%.0f"), ("Driver channels per leg", "drivers", "%d")]
tab = []
for lab, k, fmt in rows:
    vals = [fmt % (100 * r[k] if k == "eta" else r[k]) for r in R]
    if k == "vpk":
        vals = ["\\alert{%s}" % v if r[k] > 90 else v for v, r in zip(vals, R)]
    tab.append(lab + " & " + " & ".join(vals) + r" \\")
out = out.replace("%%NTABLE", "\n".join(tab))

# two blocks
tm, st = N["two"]["meas"], N["two"]["steps"]


def dI(dly, lx):
    k = [i for i, s in enumerate(st) if abs(s["dly"] - dly) < 1e-12 and abs(s["lx"] - lx) < 1e-12][0]
    return abs(tm["i1_on"][k]) - abs(tm["i2_on"][k]), tm["eon1"][k] * 1e6, tm["eon2"][k] * 1e6


a, b, c, d = dI(2e-9, 5e-9), dI(2e-9, 20e-9), dI(5e-9, 5e-9), dI(5e-9, 20e-9)
out = out.replace("%%TWOTEXT", (
    r"$\Delta t$ = 2\,ns: $\Delta I$ = %.0f\,A ($L_x$ = 5\,nH) / %.0f\,A (20\,nH); $\Delta t$ = 5\,ns: %.0f / %.0f\,A;"
    r" $E_\mathrm{on}$ %.0f vs %.0f\,$\mu$J per block at 5\,ns, 5\,nH (%.0f vs %.0f\,$\mu$J at 2\,ns, 20\,nH)"
    % (a[0], b[0], c[0], d[0], c[1], c[2], b[1], b[2])).replace(r"$\mu$", r"\textmu "))

# thermal stack table
out = out.replace("%%RTHTABLE", "\n".join(r"%s & %.2f \\" % (k.replace("%", r"\%"), v) for k, v in N["Rth_stack"]))

# number macros
s1 = N["single"]
I1 = s1["I"]
k80 = min(range(len(I1)), key=lambda i: abs(I1[i] - 80))
k120 = min(range(len(I1)), key=lambda i: abs(I1[i] - 120))
blk = N["block"]["0.90"]
lp = N["loop"]
fw = N["fsw"]
R4 = R[3]
# Rev A bank (24 x 10 uF at 3 uF + 12 x 0.45 uF) at the block current: ripple at 50 kHz and frequency for 4 %
c_bank = 24 * 3.0 + 12 * 0.45
c_req50 = fw["n_v50"] * 3.0 + 12 * 0.45
mac = dict(IRMS="%.0f" % N["I_rms_leg"], IPK="%.0f" % N["I_pk"], IBLK="%.0f" % (N["I_rms_leg"] / 2),
           IPFa="%.0f" % N["I_vs_pf"]["1.0"], IPFb="%.0f" % N["I_vs_pf"]["0.95"], IPFc="%.0f" % N["I_vs_pf"]["0.9"],
           IPFd="%.0f" % N["I_vs_pf"]["0.85"], RTH="%.1f" % N["Rth"],
           LCU="%.2f" % (lp["L_cu"] * 1e9), LONE="%.2f" % (lp["L1"] * 1e9), LTWO="%.2f" % (lp["L2"] * 1e9),
           LFOUR="%.2f" % (lp["L4"] * 1e9), LSIX="%.2f" % (lp["L6"] * 1e9),
           VLeighty="%.0f" % s1["vpk05"][k80], ILeighty="%.0f" % I1[k80],
           VLonetwenty="%.0f" % s1["vpk05"][k120], ILonetwenty="%.0f" % I1[k120],
           Pb="%.0f" % R[1]["tot"], Vb="%.0f" % R[1]["vpk"], Vc="%.0f" % R[2]["vpk"], Pc="%.0f" % R[2]["tot"],
           Pd="%.0f" % R4["tot"], Ph="%.0f" % R[7]["tot"],
           CONDINC="%.0f" % (100 * (R4["cond"] / R4["cond25"] - 1)),
           ETAtwenty="%.2f" % (100 * fw["eta4"]["20"]), ETAfifty="%.2f" % (100 * fw["eta4"]["50"]),
           ETAhundred="%.2f" % (100 * fw["eta4"]["100"]), FCROSS="%.0f" % (fw["f_cross"] / 1e3),
           NVfifty="%.0f" % fw["n_v50"], DVREVA="%.1f" % (4.0 * c_req50 / c_bank),
           FREVA="%.0f" % (50 * c_req50 / c_bank),
           BCOND="%.1f" % blk["cond"], BSW="%.1f" % blk["sw"], BDEAD="%.1f" % (blk["dead"] + blk["gate"]),
           BCU="%.1f" % blk["cu"], BCAP="%.1f" % blk["cap"], BTOT="%.1f" % blk["tot"], BETA="%.2f" % (100 * blk["eta"]),
           BPDEV="%.1f" % blk["pdev"], BTJ="%.0f" % blk["tj"], BTOTpfa="%.1f" % N["block"]["1.00"]["tot"],
           BTOTpfd="%.1f" % N["block"]["0.85"]["tot"])
defs = "\n".join(r"\newcommand{\%s}{%s}" % kv for kv in mac.items())
out = out.replace(r"\begin{document}", "%% numbers from scripts/design_flow_figures.py\n" + defs + "\n\\begin{document}", 1)
io.open(os.path.join(SL, "spb_design_flow.tex"), "w", encoding="utf-8").write(
    "% generated by scripts/make_flow_slides.py from spb_design_flow.tpl.tex; edit the template\n" + out)
print("wrote spb_design_flow.tex", mac)

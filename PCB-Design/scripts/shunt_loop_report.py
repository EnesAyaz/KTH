"""
Effect of the UFCS shunt on the commutation loop of the Rev B leg: figures + LaTeX numbers for
reports/shunt-loop/shunt_loop.tex, from the fast loop-only Q3D runs (simulation/bb_q3d/loop_post.py).

    C:\\Github\\KTH\\LossCalculation-SPB\\.venv\\Scripts\\python.exe scripts\\shunt_loop_report.py
    (then pdflatex reports/shunt-loop/shunt_loop.tex)
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "simulation", "bb_q3d", "results")
REP = os.path.join(ROOT, "reports", "shunt-loop")
os.makedirs(os.path.join(REP, "figs"), exist_ok=True)
V = {"base": ("loop_summary.json", "Rev B as routed"),
     "vip": ("loop_summary_vip.json", "return vias in the shunt DC$-$ pad"),
     "notch": ("loop_summary_notch.json", "blade 1.45 mm from the source (notched heatsink)"),
     "noshunt": ("loop_summary_noshunt.json", "no shunt (source vias to L2)")}
S = {k: json.load(open(os.path.join(RES, f))) for k, (f, _) in V.items() if os.path.exists(os.path.join(RES, f))}
REVA = 0.374
DIDT = 30.0          # A/ns
VM, VMAX = 75.0, 90.0

# ---------------------------------------------------------------- bar chart: loop per cell
fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
cells = ["cell1", "cell2", "cell3", "cell4"]
rows = [("base", "all_switching", "Rev B, with shunt", "#C84632"),
        ("base", "all_switching_shunt_0pH", "Rev B, shunt as 0 pH", "#E8A090"),
        ("vip", "all_switching", "vias in shunt pad, with shunt", "#1954A6"),
        ("notch", "all_switching", "notched heatsink: blade at the source", "#9467BD"),
        ("noshunt", "all_switching", "no shunt", "#3C8C50")]
rows = [r for r in rows if r[0] in S]
wbar = 0.8 / len(rows)
for k, (v, key, lab, col) in enumerate(rows):
    vals = [S[v][key][c] for c in cells]
    ax.bar(np.arange(4) + (k - (len(rows) - 1) / 2) * wbar, vals, wbar, color=col, label=lab)
ax.axhline(REVA, color="gray", ls="--", lw=1)
ax.text(3.45, REVA + 0.01, "Rev A 0.374", color="gray", fontsize=8, ha="right")
ax.axhline((VMAX - VM) / DIDT, color="black", ls=":", lw=1)
ax.text(3.45, (VMAX - VM) / DIDT + 0.01, "90 V at 30 A/ns", fontsize=8, ha="right")
ax.set_xticks(range(4))
ax.set_xticklabels(["cell 1", "cell 2", "cell 3", "cell 4"])
ax.set_ylabel("commutation loop (nH)")
ax.legend(fontsize=7, loc="upper center", ncol=2)
ax.set_ylim(0, 1.15)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(REP, "figs", "loop_per_cell.pdf"))

# ---------------------------------------------------------------- loop paths (exploded side view along the loop)
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

ZL = {"L1": 3.0, "L2": 2.0, "L3": 1.0, "L4": 0.0}          # exaggerated layer heights
COL = {"L1": "#C87533", "L2": "#5B8BD0", "L3": "#C87533", "L4": "#888888"}
NAME = {"L1": "L1 (top): DC+ / AC / source / shunt pads", "L2": "L2: DC$-$ plane", "L3": "L3: DC+ plane",
        "L4": "L4: AC"}


def arrow(ax, pts, col="#D62728", ls="-", lw=2.2):
    for a, b in zip(pts[:-1], pts[1:]):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11, color=col, lw=lw, ls=ls,
                                     shrinkA=0, shrinkB=0))


def panel(ax, title, path_ret, shunt=None, via_y=None, note=""):
    for lay, z in ZL.items():
        ax.add_patch(Rectangle((-2.5, z - 0.06), 24.0, 0.12, color=COL[lay], alpha=0.55, lw=0))
        ax.text(21.7, z, lay, va="center", fontsize=7, color="#444444")
    # parts on top: bypass cap, HS FET, LS FET, shunt
    for x0, x1, lab, c in ((0.2, 2.2, "C$_\\mathrm{bp}$", "#DDDDDD"), (3.0, 6.8, "Q$_H$", "#222222"),
                           (7.4, 11.0, "Q$_L$", "#222222")):
        ax.add_patch(Rectangle((x0, 3.15), x1 - x0, 0.45, color=c))
        ax.text((x0 + x1) / 2, 3.38, lab, ha="center", va="center", fontsize=7, color="white" if c != "#DDDDDD" else "black")
    if shunt:
        # UFCS: thin blade (0.7 mm) standing on the 0.5 mm gap between the IN pad (3 mm) and the SHLD pad (3 mm);
        # the current crosses ONLY at the blade, the pads are solder landings
        gap = shunt[1] if len(shunt) == 3 else (shunt[0] + shunt[1]) / 2
        for x0, x1, lab in ((shunt[0], gap - 0.25, "IN"), (gap + 0.25, shunt[-1], "SHLD pad")):
            ax.add_patch(Rectangle((x0, 3.06), x1 - x0, 0.1, color="#9467BD"))
            ax.text((x0 + x1) / 2, 2.82, lab, ha="center", fontsize=6.5, color="#6A3D9A")
        ax.add_patch(Rectangle((gap - 0.35, 3.16), 0.7, 1.35, color="#9467BD", alpha=0.85))
        ax.text(gap + 0.55, 4.25, "UFCS blade (0.7 mm)", fontsize=6.5, color="#6A3D9A")
    # outgoing path on L1 (and through the parts), return in L2
    arrow(ax, [(1.9, 3.12), (3.4, 3.12)])
    arrow(ax, [(6.4, 3.12), (7.8, 3.12)])
    if shunt:
        gap = shunt[1] if len(shunt) == 3 else (shunt[0] + shunt[1]) / 2
        arrow(ax, [(10.6, 3.12), (gap - 0.4, 3.12)])
        arrow(ax, [(gap - 0.18, 3.2), (gap - 0.18, 4.4), (gap + 0.18, 4.4), (gap + 0.18, 3.2)], lw=1.4)
        arrow(ax, [(gap + 0.4, 3.12), (via_y, 3.12)])
    arrow(ax, [(via_y, 3.0), (via_y, 2.08)])
    arrow(ax, [(via_y, 2.0), (-0.5, 2.0)], col="#1F77B4", ls="--")
    arrow(ax, [(-0.5, 2.08), (-0.5, 3.0), (0.4, 3.12)])
    ax.annotate("", (via_y, 1.55), (-0.5, 1.55), arrowprops=dict(arrowstyle="<->", color="gray", lw=0.8))
    ax.text((via_y - 0.5) / 2, 1.3, "loop length %.0f mm (L1 over L2, 0.1 mm apart)" % (via_y + 0.5), ha="center",
            fontsize=7, color="gray")
    ax.text(-2.4, 4.75, title, fontsize=9, weight="bold", va="top")
    ax.text(-2.4, 4.3, note, fontsize=7.5, va="top")
    ax.set_xlim(-2.6, 23.0)
    ax.set_ylim(-0.3, 4.9)
    ax.axis("off")


def mean_or(v, key="all_switching"):
    return ("%.2f nH" % mean(S[v][key])) if v in S else "pending"


def mean(d):
    return sum(d.values()) / len(d)


fig, axs = plt.subplots(5, 1, figsize=(7.4, 10.4), dpi=200)
panel(axs[0], "(a) Rev A model: source vias into L2 at the transistor", None, None, 11.1,
      "ideal geometry (FET pads as blocks), 0.374 nH per cell")
panel(axs[1], "(b) Rev B as routed: source $\\rightarrow$ IN pad $\\rightarrow$ blade $\\rightarrow$ vias beyond the SHLD pad", None,
      (12.0, 15.25, 18.5), 19.4, "mean %s (shunt 120 pH included)" % mean_or("base"))
panel(axs[2], "(c) return vias inside the shunt DC$-$ pad (next to the blade)", None, (12.0, 15.25, 18.5), 16.0,
      "mean %s" % mean_or("vip"))
panel(axs[3], "(d) notched heatsink: 1.2 mm IN land, blade 1.45 mm from the source, vias in the pad", None,
      (11.2, 12.65, 15.9), 13.4, "mean %s" % mean_or("notch"))
panel(axs[4], "(e) no shunt: vias inside the low-side source stripes (L1$\\rightarrow$L2)", None, None, 9.6,
      "mean %s" % mean_or("noshunt"))
for ax in axs[:1]:
    for lay in ZL:
        pass
fig.text(0.5, 0.005, "red: outgoing current (L1, transistors, shunt), blue dashed: return in the L2 DC$-$ plane; "
         "vertical scale exaggerated", ha="center", fontsize=7.5)
fig.tight_layout(rect=(0, 0.02, 1, 1))
fig.savefig(os.path.join(REP, "figs", "loop_paths.pdf"))

# ---------------------------------------------------------------- numbers for LaTeX
mac = ["% generated by scripts/shunt_loop_report.py"]


def nc(name, val):
    mac.append("\\newcommand{\\%s}{%s}" % (name, val))


def mean(d):
    return sum(d.values()) / len(d)


tab = []
for v, key, lab in (("base", "all_switching", "Rev B as routed (UFCS 120\\,pH)"),
                    ("base", "all_switching_shunt_0pH", "Rev B, shunt replaced by 0\\,pH"),
                    ("base", "all_switching_top_bypass_only", "Rev B, without the bottom bypass row"),
                    ("vip", "all_switching", "Return vias in the shunt DC$-$ pad (UFCS 120\\,pH)"),
                    ("vip", "all_switching_shunt_0pH", "Return vias in the pad, shunt 0\\,pH"),
                    ("notch", "all_switching", "Blade 1.45\\,mm from the source + vias in pad (notch)"),
                    ("noshunt", "all_switching", "No shunt, source vias to L2")):
    if v not in S:
        continue
    d = S[v][key]
    m = mean(d)
    tab.append("%s & %s & %.3f & %.0f & %.0f \\\\" % (
        lab, " & ".join("%.3f" % d[c] for c in cells), m, VM + m * DIDT, (VMAX - VM) / m))
head = ["\\begin{tabular}{@{}lrrrrrrr@{}}", "\\toprule",
        "Variant & cell 1 & cell 2 & cell 3 & cell 4 & mean & $\\hat v_\\mathrm{DS}$ (V) & $di/dt$ for \\\\",
        " & \\multicolumn{5}{c}{nH} & at 30\\,A/ns & 90\\,V (A/ns) \\\\", "\\midrule"]
tail = ["\\midrule", "Rev A geometry model & \\multicolumn{4}{c}{0.374} & 0.374 & 86 & 40 \\\\", "\\bottomrule",
        "\\end{tabular}"]
open(os.path.join(REP, "loop_table.tex"), "w").write("\n".join(head + tab + tail) + "\n")
if "base" in S:
    b = S["base"]
    nc("Lbase", "%.2f" % mean(b["all_switching"]))
    nc("Lbasezero", "%.2f" % mean(b["all_switching_shunt_0pH"]))
    nc("Ltoponly", "%.3f" % (mean(b["all_switching_top_bypass_only"]) - mean(b["all_switching"])))
    nc("Vbase", "%.0f" % (VM + mean(b["all_switching"]) * DIDT))
    nc("Dibase", "%.0f" % ((VMAX - VM) / mean(b["all_switching"])))
    asym = (b["all_switching"]["cell1"] + b["all_switching"]["cell3"] - b["all_switching"]["cell2"]
            - b["all_switching"]["cell4"]) / 2
    nc("Lasym", "%.2f" % asym)
if "vip" in S:
    nc("Lvip", "%.2f" % mean(S["vip"]["all_switching"]))
    nc("Vvip", "%.0f" % (VM + mean(S["vip"]["all_switching"]) * DIDT))
    nc("Divip", "%.0f" % ((VMAX - VM) / mean(S["vip"]["all_switching"])))
if "notch" in S:
    nc("Lnotch", "%.2f" % mean(S["notch"]["all_switching"]))
    nc("Vnotch", "%.0f" % (VM + mean(S["notch"]["all_switching"]) * DIDT))
    nc("Dinotch", "%.0f" % ((VMAX - VM) / mean(S["notch"]["all_switching"])))
if "noshunt" in S:
    nc("Lnoshunt", "%.2f" % mean(S["noshunt"]["all_switching"]))
    nc("Vnoshunt", "%.0f" % (VM + mean(S["noshunt"]["all_switching"]) * DIDT))
    nc("Dinoshunt", "%.0f" % ((VMAX - VM) / mean(S["noshunt"]["all_switching"])))
    if "base" in S:
        nc("Lcopper", "%.2f" % (mean(S["base"]["all_switching_shunt_0pH"]) - mean(S["noshunt"]["all_switching"])))
open(os.path.join(REP, "loop_numbers.tex"), "w").write("\n".join(mac) + "\n")
print("\n".join(mac))

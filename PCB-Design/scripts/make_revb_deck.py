"""
Rev B design-flow deck (4 x EPC2361 per switch on one board, three legs on a PCB busbar) as an editable PPTX.

    C:\\Github\\KTH\\LossCalculation-SPB\\.venv\\Scripts\\python.exe scripts\\make_revb_deck.py
    powershell -ExecutionPolicy Bypass -File scripts\\build_pptx.ps1
      -> reports/slides/revb_pptx/deck.json, img/*.png  ->  reports/slides/spb_revb_design_flow.pptx

Steps 1-7 follow spb_design_flow_v3 (same figures, converted to PNG in revb_pptx/img); steps 8-12 are the Rev B
board, supplies and measurement, the three-phase DC bus (PCB busbar) and the Q3D verification of leg + busbar
(numbers from reports/slides/data/revb_numbers.json, written by simulation/bb_q3d/revb_post.py).
Markup in texts: **bold**, !!alert!!, _{sub}, ^{sup}. Coordinates in points on a 960 x 540 slide.
"""
import json
import os
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SL = os.path.join(ROOT, "reports", "slides")
OUT = os.path.join(SL, "revb_pptx")
IMG = os.path.join(OUT, "img")
os.makedirs(IMG, exist_ok=True)
FN = json.load(open(os.path.join(SL, "data", "flow_numbers.json")))
RB_PATH = os.path.join(SL, "data", "revb_numbers.json")
RB = json.load(open(RB_PATH)) if os.path.exists(RB_PATH) else {}
EST = json.load(open(os.path.join(ROOT, "hardware", "spb-busbar", "estimates.json")))
PDFTOPPM = "pdftoppm"


def get(d, *keys, fmt="%.2f", pending="(Q3D pending)"):
    try:
        for k in keys:
            d = d[k]
        return fmt % d
    except (KeyError, TypeError, IndexError):
        return pending


# ------------------------------------------------------------------ images: crops of schematic, boards; plots
def autocrop(path, pad=12):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im)
    mask = (a < 245).any(axis=2)
    ys, xs = np.where(mask)
    if len(xs):
        im = im.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, im.width),
                      min(ys.max() + pad, im.height)))
    im.save(path)


def pdf_crop(pdf, name, box_mm=None, dpi=150):
    out = os.path.join(IMG, name)
    args = [PDFTOPPM, "-r", str(dpi), "-png", "-singlefile"]
    if box_mm:
        k = dpi / 25.4
        x0, y0, x1, y1 = box_mm
        args += ["-x", str(int(x0 * k)), "-y", str(int(y0 * k)), "-W", str(int((x1 - x0) * k)), "-H",
                 str(int((y1 - y0) * k))]
    subprocess.run(args + [pdf, out], check=True)
    autocrop(out + ".png")
    return "img/%s.png" % name


KCLI = r"C:\Program Files\KiCad\7.0\bin\kicad-cli.exe"
HWB = os.path.join(ROOT, "hardware", "spb-bb-revb")
SCH = os.path.join(HWB, "spb-bb-revb_schematic.pdf")
subprocess.run([KCLI, "sch", "export", "pdf", "-o", SCH, os.path.join(HWB, "spb-bb-revb.kicad_sch")], check=True)
for side, lays, extra in (("top", "F.Cu,F.SilkS,Edge.Cuts", []), ("bottom", "B.Cu,B.SilkS,Edge.Cuts", ["--mirror"])):
    pdf = os.path.join(HWB, "plots", "revb_%s.pdf" % side)
    subprocess.run([KCLI, "pcb", "export", "pdf", "--layers", lays, "-o", pdf] + extra +
                   [os.path.join(HWB, "spb-bb-revb.kicad_pcb")], check=True)
    pdf_crop(pdf, "revb_%s" % side, None, 200)
pdf_crop(SCH, "sch_power", (380, 25, 745, 160))
pdf_crop(SCH, "sch_driver", (25, 180, 262, 258))
pdf_crop(SCH, "sch_islands", (25, 262, 228, 322))
pdf_crop(SCH, "sch_ufl", (25, 322, 245, 352))
pdf_crop(os.path.join(ROOT, "hardware", "spb-busbar", "plots", "spb-busbar-busbar_view.pdf"), "busbar_top", None, 200)
for n in ("top", "bottom", "revb_overview", "revb_3d_noheatsink", "revb_3d_iso", "revb_3d_bottom"):
    p = os.path.join(IMG, n + ".png")
    if os.path.exists(p):
        autocrop(p)

plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3})
sweep = os.path.join(ROOT, "simulation", "bb_q3d", "results", "revb_sweep.csv")
HAVE_SWEEP = os.path.exists(sweep)
if HAVE_SWEEP:
    d = np.loadtxt(sweep, delimiter=",", skiprows=1)
    fig, ax = plt.subplots(figsize=(7.0, 3.6), dpi=200)
    ax.loglog(d[:, 0], d[:, 2] * 1e3, color="#888888", lw=1.8, label="leg 1 alone")
    ax.loglog(d[:, 0], d[:, 1] * 1e3, color="#1954A6", lw=2.2, label="three legs on the PCB busbar")
    ax.axvline(50e3, color="#C84632", ls="--", lw=1)
    ax.text(52e3, ax.get_ylim()[0] * 1.5 if ax.get_ylim()[0] > 0 else 0.01, "50 kHz", color="#C84632")
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("|Z| seen by the cells of leg 1 (mΩ)")
    ax.legend(loc="upper center")
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "revb_sweep.png"))
    plt.close(fig)

# fast loop-only Q3D (run_bb_q3d_loop.cmd): per-cell loop of the study variants and of the final layout
RES = os.path.join(ROOT, "simulation", "bb_q3d", "results")
LS = {}
for tag in ("", "_vip", "_notch", "_noshunt", "_symv", "_noshunt_symv"):
    p_ = os.path.join(RES, "loop_summary%s.json" % tag)
    if os.path.exists(p_):
        LS[tag.strip("_") or "base"] = json.load(open(p_))


def cells(tag, key="all_switching"):
    return [LS[tag][key]["cell%d" % c] for c in range(1, 5)]


fig, ax = plt.subplots(figsize=(7.0, 3.7), dpi=200)
xs = np.arange(4)
for k, (tag, lab, col, hatch) in enumerate((("base", "with shunt, before the fix", "#E6A0A0", "//"),
                                            ("symv", "with shunt, final", "#C84632", ""),
                                            ("noshunt", "no shunt, before the fix", "#9DB8E0", "//"),
                                            ("noshunt_symv", "no shunt, final", "#1954A6", ""))):
    v = cells(tag)
    ax.bar(xs + (k - 1.5) * 0.2, v, 0.19, color=col, hatch=hatch, edgecolor="white", label=lab)
    if not hatch:
        for x_, y_ in zip(xs + (k - 1.5) * 0.2, v):
            ax.text(x_, y_ + 0.01, "%.2f" % y_, ha="center", va="bottom", fontsize=7)
ax.axhline(0.374, color="gray", ls="--", lw=1, label="Rev A model, 0.374 nH")
ax.set_xticks(xs)
ax.set_xticklabels(["cell 1\n(left, block 1)", "cell 2\n(right, block 1)", "cell 3\n(left, block 2)",
                    "cell 4\n(right, block 2)"])
ax.set_ylabel("commutation loop per cell (nH)")
ax.set_ylim(0, 1.2)
ax.legend(fontsize=8, ncol=3, loc="upper center")
fig.tight_layout()
fig.savefig(os.path.join(IMG, "revb_loop_cells.png"))
plt.close(fig)

fig, ax = plt.subplots(figsize=(7.0, 3.7), dpi=200)
bars = [("as routed\n(shunt)", LS["base"]["mean_nH"], "#E6A0A0"),
        ("vias in\nshunt pad", LS["vip"]["mean_nH"], "#E6A0A0"),
        ("notched\nheatsink", LS["notch"]["mean_nH"], "#E6A0A0"),
        ("final\n(shunt)", LS["symv"]["mean_nH"], "#C84632"),
        ("final, shunt\nas 0 pH", float(np.mean(cells("symv", "all_switching_shunt_0pH"))), "#D9A441"),
        ("final\nno shunt", LS["noshunt_symv"]["mean_nH"], "#1954A6")]
for k, (lab, v, col) in enumerate(bars):
    ax.bar(k, v, 0.6, color=col)
    ax.text(k, v + 0.01, "%.2f nH\n%.0f V" % (v, 75 + 30 * v), ha="center", va="bottom", fontsize=8)
ax.axhline(0.5, color="#2CA02C", ls="--", lw=1, label="0.5 nH design value (90 V at 30 A/ns)")
ax.legend(fontsize=8, loc="upper right")
ax.set_xticks(range(len(bars)))
ax.set_xticklabels([b[0] for b in bars], fontsize=8.5)
ax.set_ylabel("mean loop per cell (nH)")
ax.set_ylim(0, 1.05)
fig.tight_layout()
fig.savefig(os.path.join(IMG, "revb_shunt_study.png"))
plt.close(fig)

# bypass hand-over with the Rev B numbers: TDK 0805 1 uF keeps 18 % at 75 V, L_b from Q3D
I_DEV, C_PART = FN["bypass"]["I_dev"], 0.178e-6
dv = np.linspace(0.5, 5.0, 200)
fig, ax = plt.subplots(figsize=(6.0, 4.6), dpi=200)
ax.fill_between(dv, 0.65e-9 * (I_DEV / dv) ** 2 * 1e6, 0.77e-9 * (I_DEV / dv) ** 2 * 1e6, color="#1954A6", alpha=0.35,
                label="hand-over, $L_b$ = 0.65–0.77 nH (Q3D)")
ax.plot(dv, 1e-9 * (I_DEV / dv) ** 2 * 1e6, color="#C84632", lw=1.2, ls=":", label="hand-over, $L_b$ = 1 nH (assumed before)")
ax.plot(dv, FN["bypass"]["dQ"] / dv * 1e6, color="k", ls="--", lw=1.2, label="edge charge")
for n, col in ((6, "#9467BD"), (10, "#2CA02C")):
    ax.axhline(n * C_PART * 1e6, color=col, lw=1.2)
    ax.text(4.95, n * C_PART * 1e6 + 0.05, "%d × 1 µF 0805 = %.2f µF eff." % (n, n * C_PART * 1e6), color=col,
            fontsize=8, ha="right", va="bottom")
ax.set_xlabel("allowed dip ΔV at the hand-over (V)")
ax.set_ylabel(r"$C_\mathrm{bp,min}$ per cell (µF effective at 75 V)")
ax.set_xlim(0.5, 5)
ax.set_ylim(0, 5)
ax.legend(fontsize=8, loc="upper right")
fig.tight_layout()
fig.savefig(os.path.join(IMG, "revb_bypass.png"))
plt.close(fig)
pdf_crop(os.path.join(ROOT, "reports", "shunt-loop", "figs", "loop_paths.pdf"), "loop_paths", None, 200)

# ------------------------------------------------------------------ slide helpers
STEPS = ["Inputs", "Device", "Submodule\nvoltage", "One device,\none driver", "n in\nparallel", "f_sw,\nDC link",
         "Gate drive\n→ block", "Four on\none board", "Supplies,\nmeasurement", "Three-phase\nDC bus",
         "Verify\n(Q3D)", "Rev B\nboard"]
SLIDES = []
X0, W = 30, 900                     # body area
Y0 = 92


def slide(title, step=None, section=None):
    s = dict(title=title, step=step, section=section, items=[])
    SLIDES.append(s)
    return s


def text(s, box, paras, size=14):
    s["items"].append(dict(type="text", box=box, paras=[[p[0], p[1]] if isinstance(p, (list, tuple)) else [0, p]
                                                         for p in paras], size=size))


def image(s, file, box):
    s["items"].append(dict(type="image", file=file, box=box))


def table(s, box, rows, size=12, colw=None, bold_last=False):
    s["items"].append(dict(type="table", box=box, rows=rows, size=size, colw=colw, bold_last=bold_last))


def decision(s, txt, box=None):
    s["items"].append(dict(type="decision", box=box or [X0, 470, W, 42], text=txt))


def note(s, txt):
    s["items"].append(dict(type="note", text=txt))


def rect(s, box, txt="", fill="kth10", line="kth", size=11, bold=False, color="black", round_=True):
    s["items"].append(dict(type="rect", box=box, text=txt, fill=fill, line=line, size=size, bold=bold, color=color,
                           round=round_))


def line(s, pts, color="black", w=2.0, arrow=False):
    s["items"].append(dict(type="line", pts=pts, color=color, w=w, arrow=arrow))


def label(s, box, txt, size=10, color="black", bold=False, align="left"):
    s["items"].append(dict(type="label", box=box, text=txt, size=size, color=color, bold=bold, align=align))


L2 = [X0, Y0, 430, 370]             # left half
R2 = [X0 + 450, Y0, 450, 370]       # right half

# ================================================================== title and overview
s = slide("GaN Building Block Rev B")
s["kind"] = "title"
s["subtitle"] = "Four EPC2361 per switch on one board, three legs on a PCB busbar:\na decision-driven design for a 1200 V, 300 kW Stacked Polyphase Bridge inverter"
s["author"] = "Enes Ayaz · KTH Royal Institute of Technology · October 2026"

s = slide("Design flow", 0)
table(s, [X0, Y0, W, 410], [
    ["", "Step", "Question → decision"],
    ["1", "Design inputs", "1200 V, 300 kW, M ≤ 1.15, PMSM cos φ = 0.9 → 228 A_{rms} per leg"],
    ["2", "Device", "100–650 V Si/SiC/GaN survey → 100 V GaN, EPC2361"],
    ["3", "Submodule voltage", "V_{m} + L·di/dt ≤ 90 V, even integer N → 75 V, N = 16"],
    ["4", "One device, one driver", "first-cut loop + LTspice → ≤ 80 A per device"],
    ["5", "n in parallel", "loss, T_{j}, V_{DS} vs n → 4 EPC2361 per switch"],
    ["6", "f_{sw}, DC link", "≥ 50 kHz; 3 % ripple → 20 × 22 µF 2220 bank + 10 × 1 µF bypass per cell (DC bias at 75 V)"],
    ["7", "Gate drive → block", "one driver per pair (star, Kelvin) → building block of two cells"],
    ["8", "Four on one board", "two pairs, one driver each (star); one DC pair, one bank, one AC output → Rev B leg"],
    ["9", "Supplies, measurement", "two isolated supplies + Zener bias, UFCS shunt per cell, U.FL, HO 250-S"],
    ["10", "Three-phase DC bus", "legs share the 75 V bus → laminated PCB busbar under the legs"],
    ["11–12", "Verification, board", "Q3D of leg + busbar, KiCad schematic = PCB, Rev B fab files"],
], size=12, colw=[50, 190, 660])

# ================================================================== 1 inputs
s = slide("Design inputs", 1, "1  Design inputs")
image(s, "img/fig_spb_standalone.png", L2)
table(s, [X0 + 460, Y0 + 10, 440, 250], [
    ["Quantity", "Value"],
    ["DC bus", "1200 V nominal"],
    ["Output power", "300 kW"],
    ["Modulation index", "M ≤ 1.15 (SVM)"],
    ["Machine", "PMSM, cos φ assumed 0.9"],
    ["Switching frequency", "≥ 50 kHz (step 6)"],
    ["Coolant / T_{j}", "60 °C / ≤ 125 °C"],
    ["Device stress", "V_{DS} ≤ 90 V at nominal bus (100 V part)"],
], size=13, colw=[180, 260])
text(s, [X0 + 460, Y0 + 280, 440, 80], ["SPB: N three-phase submodules in series on the DC side, each feeding one "
                                        "winding set; V_{m} = 1200 V / N."], 12)

s = slide("Phase current follows from the inputs", 1)
text(s, [X0, Y0, 520, 330], [
    "Each of the 3N legs delivers P/3N at V_{ph} = M·V_{m}/(2√2):",
    "I_{rms} = P / (3 · M·V_{bus}/(2√2) · cos φ)",
    (1, "N·V_{m} = V_{bus}: the phase current does !!not!! depend on N"),
    (1, "V_{ph} = 1.15 · 75 V / 2√2 = 30.5 V; 6.25 kW per leg"),
    (1, "**%.0f A_{rms} per leg**, %.0f A peak (cos φ = 0.9)" % (FN["I_rms_leg"], FN["I_pk"])),
    (1, "DC current per leg 83 A; series DC chain 250 A"),
], 15)
table(s, [X0 + 560, Y0 + 10, 300, 200], [["cos φ", "I_{rms} per leg"]] +
      [[k, "%.0f A" % FN["I_vs_pf"][k]] for k in ("1.0", "0.95", "0.9", "0.85")], size=14)
note(s, "Losses below are for cos φ = 0.9; the PMSM operating point must be confirmed with the machine design.")

# ================================================================== 2 device
s = slide("Voltage class: why 100 V GaN", 2, "2  Device")
image(s, "img/fig_devices.png", [X0, Y0, 520, 370])
text(s, [X0 + 540, Y0, 360, 370], [
    "At fixed bus voltage and phase current the minimum semiconductor loss scales with R_{DS(on)}·C_{oss,tr}",
    "100 V GaN gives the lowest product among 100–650 V Si/SiC/GaN candidates",
    "Selected: **EPC2361**, 100 V, 0.75 mΩ typ, 3 × 5 mm, top-side cooling",
], 14)

s = slide("EPC2361 key data", 2)
table(s, [X0, Y0, 470, 330], [
    ["Parameter", "Value"],
    ["V_{DS} / transient", "100 / 120 V"], ["R_{DS(on)}", "0.75 mΩ typ (1.0 max)"],
    ["V_{GS} range", "−4 … +6 V"], ["V_{GS(th)}", "0.8 / 1.1 / 2.5 V"],
    ["C_{iss} / C_{oss} / C_{rss}", "3599 / 1019 / 13 pF"], ["Q_{G} / Q_{GD} / Q_{OSS}", "28 / 3.8 / 90 nC"],
    ["R_{G,int}", "0.4 Ω"], ["R_{θJC} top / R_{θJB}", "0.2 / 1.5 K/W"]], size=13, colw=[220, 250])
text(s, [X0 + 500, Y0, 400, 330], [
    "Low threshold and −4 V limit: gate drive needs care (bump, negative bias)",
    "Top of the package at !!source potential!!: the thermal interface must insulate",
    "Seven interleaved stripes; pad 2 next to the gate is the natural Kelvin point (own net KH/KL on Rev B)",
], 14)

# ================================================================== 3 submodule voltage
s = slide("Submodule voltage from L·di/dt", 3, "3  Submodule voltage")
image(s, "img/flow_vm.png", [X0, Y0, 500, 370])
text(s, [X0 + 515, Y0, 385, 370], [
    "Peak stress v̂_{DS} = V_{m} + L_{loop}·di/dt ≤ 90 V (10 % below the rating)",
    "First-cut loop with MLCCs: ≈ 0.5 nH per cell",
    "Fast switching (≈ 30 A/ns, analytical gate-charge model) ⇒ 15 V overshoot ⇒ V_{m} ≤ 75 V",
    "N integer and even (symmetric submodules and winding sets): 14 → 86 V, 18 → 67 V and 12.5 % more parts",
], 13)
decision(s, "V_{m} = 75 V, N = 16")

s = slide("Why not lower: every submodule costs parts and loss", 3)
image(s, "img/flow_cells.png", L2)
text(s, R2, [
    "Phase current is fixed by P, V_{bus}, M, cos φ, not by N",
    "Each submodule carries the full phase current ⇒ conduction loss, transistors, drivers and supplies scale with N",
    "60 V (N = 20): +25 % parts and conduction loss",
    "Overshoot margin rechecked with the final layout (Q3D, 0.374 nH per cell on Rev A; Rev B in step 11)",
], 14)

# ================================================================== 4 one device
s = slide("First-cut power loop of one cell", 4, "4  One device, one driver")
image(s, "img/flow_loop.png", [X0, Y0, 500, 370])
text(s, [X0 + 515, Y0, 385, 370], [
    "Loop = PCB copper (vertical loop over 0.1 mm dielectric, vias, pads) + ESL of the local MLCCs",
    "Copper alone ≈ 0.31 nH; MLCCs in parallel add ESL/n_{c}",
    "1 / 2 / 4 / 6 MLCCs: 0.79 / 0.55 / 0.43 / 0.39 nH: beyond ≈ 4 the number hardly matters",
    "Part: 1 µF 100 V X7S 0805 next to the drains",
], 13)
decision(s, "Design with L_{loop} = 0.5 nH per cell (0.3 and 0.8 nH as bounds)")

s = slide("One EPC2361 per switch: how fast and how much overshoot", 4)
image(s, "img/flow_single.png", [X0, Y0, W, 230])
text(s, [X0, Y0 + 240, W, 170], [
    "LTspice half bridge, double pulse at 75 V: lumped loop, 1.7 nH gate loop, 0.03 nH common source, 2 Ω on / 0 Ω off",
    "Turn-on di/dt set by the driver (≈ 45 A/ns); turn-off di/dt grows with current",
    "0.5 nH: 83 V at 79 A, !!101 V at 119 A!! per device",
    "One device would carry 322 A peak ⇒ **current per device ≤ 80 A**",
], 13)

# ================================================================== 5 n parallel
s = slide("Thermal path per device", 5, "5  Devices in parallel")
table(s, [X0, Y0, 520, 300], [["Layer (top-side cooling, per device)", "K/W"],
                              ["R_{θJC} (top), datasheet", "0.20"], ["TIM 1, 50 µm, 3 W/mK, 15 mm²", "1.11"],
                              ["AlN 0.635 mm, 170 W/mK, 25 mm²", "0.15"], ["TIM 2, 50 µm, 3 W/mK, 50 mm²", "0.33"],
                              ["cold plate, h = 10 kW/m²K, 100 mm²", "1.00"],
                              ["coupling to neighbours, coolant rise (+20 %)", "0.56"],
                              ["Junction–coolant", "3.4"]], size=13, colw=[420, 100], bold_last=True)
text(s, [X0 + 545, Y0, 355, 330], [
    "Two TIM layers and the cold plate dominate",
    "Used for the decisions: **3.4 K/W**, coolant 60 °C",
    "Bounds: 2.1 K/W (sintered stack), 8 K/W (gap pad)",
    "R_{DS(on)}(T_{j}) from the datasheet: 1.49 at 100 °C, 1.80 at 150 °C",
], 14)

s = slide("n identical cells per switch (one device and one driver each)", 5)
image(s, "img/flow_npar.png", [X0, Y0, W, 250])
text(s, [X0, Y0 + 255, W, 120], [
    "228 A_{rms} per leg, 50 kHz, T_{j} and R_{DS(on)} solved together; LTspice energies at 0.5 nH",
    "n = 1: T_{j} > 150 °C; n = 2: 33 W and 131 V; n = 3: 96 V at 0.5 nH; n = 4 / 8: 18 / 15 W per leg",
], 13)
decision(s, "**4 EPC2361 per switch** (V_{DS} and T_{j} for all three R_{th}; 4 splits into two equal pairs)")

s = slide("Where the loss comes from: line period and junction temperature", 5)
image(s, "img/flow_wave.png", [X0, Y0, W, 290])
text(s, [X0, Y0 + 300, W, 90], [
    "n = 4, 50 kHz: switching loss follows |i| (plus a constant E_{oss} part), conduction loss follows i²",
    "Conduction loss at the operating point is 28 % above its 25 °C value",
], 13)

s = slide("Losses vs number in parallel", 5)
table(s, [X0, Y0, W, 300], [
    ["n per switch", "1", "2", "3", "4", "5", "6", "7", "8"],
    ["Loss per leg (W)", "79.1", "33.0", "22.1", "17.8", "15.8", "14.9", "14.5", "14.5"],
    ["  conduction at T_{j} (W)", "70.0", "27.5", "17.0", "12.4", "9.8", "8.1", "7.0", "6.1"],
    ["  switching (W)", "8.4", "5.0", "4.5", "4.8", "5.4", "6.2", "7.0", "7.9"],
    ["Efficiency (%)", "98.73", "99.47", "99.65", "99.72", "99.75", "99.76", "99.77", "99.77"],
    ["Loss per device (W)", "39.5", "8.2", "3.7", "2.2", "1.6", "1.2", "1.0", "0.9"],
    ["T_{j} (°C)", "194", "88", "72", "68", "65", "64", "63", "63"],
    ["Peak V_{DS} (V)", "194", "131", "96", "83", "83", "83", "83", "83"],
    ["Driver channels per leg", "2", "4", "6", "8", "10", "12", "14", "16"]], size=12,
      colw=[220] + [85] * 8)
note(s, "Semiconductor losses only, 3.4 K/W, 60 °C coolant, 0.5 nH, 50 kHz; efficiency relative to 6.25 kW per leg.")

# ================================================================== 6 fsw, DC link
s = slide("Switching frequency: losses, DC-link capacitors, current ripple", 6, "6  Switching frequency and DC link")
image(s, "img/flow_fsw.png", [X0, Y0, W, 220])
text(s, [X0, Y0 + 225, W, 150], [
    "(a) n = 4: 99.77 / 99.72 / 99.63 % at 20 / 50 / 100 kHz",
    "(b) Voltage ripple sets the MLCC count below ≈ 99 kHz, ripple current above",
    "(c) Winding current ripple Δi_{pp} = V_{m}/(4 L_{σ} f_{sw}) depends on the machine leakage inductance",
], 13)
decision(s, "f_{sw} ≥ 50 kHz (higher allowed by the machine); the DC link below is sized for 50 kHz")

CC = json.load(open(os.path.join(SL, "data", "capacitor_compare.json")))
s = slide("DC-link sizing for a three-phase level", 6)
image(s, "img/dclink_sizing.png", [X0, Y0, 520, 200])
text(s, [X0, Y0 + 210, 520, 170], [
    "One 75 V level = three legs on one bus; SVPWM M = 1.15, cos φ = 0.9, 322 A peak, switching function per period",
    "Balanced three-phase: no 2f ripple; capacitor RMS current **85 A per level** (≈ 28 A per leg)",
    "Worst charge excursion per period **860 µC at 50 kHz** (≈ Î/(8 f_{sw})) ⇒ ripple, not current, sets C",
], 13)
table(s, [X0 + 545, Y0, 355, 200], [
    ["f_{sw}", "ΔV_{pp}", "C_{eff} per level", "per leg"],
    ["50 kHz", "2 %", "573 µF", "191 µF"], ["50 kHz", "**3 %**", "**382 µF**", "**127 µF**"],
    ["100 kHz", "2 %", "287 µF", "96 µF"], ["100 kHz", "3 %", "191 µF", "64 µF"]], size=12, colw=[80, 70, 115, 90])
decision(s, "ΔV_{pp} ≤ 3 % (2.25 V) at 50 kHz ⇒ 127 µF **effective** per leg board (three legs share the level)")

s = slide("Capacitor selection: effective capacitance at 75 V", 6)
rows = [["Part (100 V X7S)", "Size", "C_{nom} → C at 75 V", "Kept", "ESR 50 kHz", "Parts / leg (3 %)"]]
for p_ in CC["parts"]:
    rows.append([("**%s**" % p_["part"]) if "226" in p_["part"] else p_["part"], p_["size"],
                 "%.1f → %.2f µF" % (p_["C_nom_uF"], p_["C_eff_uF"]), "%.0f %%" % (100 * p_["retention"]),
                 ("%.1f mΩ" % p_["ESR50k_mOhm"]) if p_["ESR50k_mOhm"] else "–", str(p_["n_50kHz_3pct"])])
table(s, [X0, Y0, W, 170], rows, size=12, colw=[260, 60, 170, 70, 120, 220])
text(s, [X0, Y0 + 185, W, 190], [
    "DC bias at 75 V from the manufacturers' characteristic data (TDK product centre, Murata): 100 V class-II MLCCs keep "
    "only 15–29 %; the current Murata 1210 keeps !!15 %!!, not the 30 % assumed before",
    "TDK C5750X7S2A226M280KB (2220, 22 µF): highest C per part and per area (0.22 µF/mm²), 2.8 mΩ, 4.5 A for +10 K",
    "Checks: 2.8 mm height under the heatsink spreader; 2220 flex cracking ⇒ away from board edge and mounting holes",
], 13)
decision(s, "Bank: **20 × TDK C5750X7S2A226M280KB** per leg (2 rows), 127 µF effective, 1.4 A ripple per part")

s = slide("Bypass capacitors: how many and how large", 6)
image(s, "img/revb_bypass.png", [X0, Y0, 400, 370])
text(s, [X0 + 420, Y0, 480, 370], [
    "**Bypass** (1 µF 0805 at the drains) supplies the edge, **bank** the f_{sw} ripple; per cell 81 A:",
    (1, "di/dt → number: L_{Cu} + ESL/n ≤ 0.5 nH ⇒ n ≥ 4"),
    (1, "Hand-over to the bank through L_{b}: C_{bp} ≥ L_{b}(ΔI/ΔV)²: !!sets the value!!"),
    (1, "L_{b} from Q3D (Rev B copper): **0.65–0.77 nH** (1 nH assumed before)"),
    (1, "0805 1 µF 100 V X7S keeps only **18 %** at 75 V (TDK data): 0.18 µF per part"),
    (1, "6 per cell = 1.1 µF ⇒ 2.2 V dip; 10 per cell = 1.8 µF ⇒ **1.7 V** dip"),
], 13)
decision(s, "10 × 1 µF 0805 per cell: 6 on top at the drains (loop unchanged) + 4 on the bottom, identical in all cells")

s = slide("DC link of the Rev B leg", 6)
table(s, [X0, Y0, 470, 200], [
    ["Per leg board", "Parts", "Nominal", "At 75 V"],
    ["Bypass, 10 per cell × 4", "40 × 1 µF 0805", "40 µF", "7 µF"],
    ["Bank, rows A (8) + B (12)", "20 × 22 µF 2220", "440 µF", "127 µF"],
    ["Total", "60", "480 µF", "134 µF"]], size=13, colw=[170, 120, 80, 100], bold_last=True)
text(s, [X0 + 495, Y0, 405, 370], [
    "Ripple at 50 kHz with the three legs of a level sharing: **2.1 V (2.9 %)**",
    "Leg alone (DPT / back-to-back test without the busbar): ≈ 2× higher, acceptable for the lab tests",
    "60 instead of 99 MLCCs, bank ≥ 10 × bypass (127 vs 7 µF eff.): fulfilled",
    "Row A leaves the board centre free: the DC terminal pins are there",
], 13)
decision(s, "Bank and bypass as above; the Rev B layout is updated to these parts (DRC clean, schematic = PCB)")

# ================================================================== 7 gate drive
s = slide("Can one driver drive all four?", 7, "7  Gate drive: from 4 devices to a building block")
image(s, "img/drv_scaling.png", [X0, Y0, 540, 370])
text(s, [X0 + 555, Y0, 345, 370], [
    "One channel for 3 / 4 / 6 transistors: E_{on} per transistor +16 / +31 / +60 %",
    "Peak sink current 12–14 A, above the 8 A rating",
    "Longer gate tree brings the gate bump back",
    "One driver per device: symmetric, but 4 channels and supplies per switch",
], 14)

s = slide("Why symmetry: current-sharing sensitivity", 7)
image(s, "img/fig_sharing.png", [X0, Y0, 540, 370])
text(s, [X0 + 555, Y0, 345, 370], [
    "Static sharing is fine (R_{DS(on)} has a positive TC)",
    "Dynamic sharing is set by the gate circuits:",
    (1, "gate-loop mismatch 2 vs 8 nH → 19 % imbalance, 4:1 E_{on}"),
    (1, "common source without Kelvin → 29 %, 2.8 × E_{on}"),
    "⇒ star gate network with Kelvin returns, one driver channel per pair",
], 14)

s = slide("Gate bump and negative off-voltage", 7)
image(s, "img/bump_mechanism.png", [X0, Y0, 440, 300])
image(s, "img/bump_mitigation.png", [X0 + 460, Y0, 440, 300])
text(s, [X0, Y0 + 305, W, 80], [
    "Bump ≈ Q_{GD}/C_{GS} ≈ 1.06 V, independent of current and voltage; close to the 0.8 V minimum threshold",
    "With ≈ −1.2 V off-voltage the peak falls to ≈ 0 V; undershoot −2.3 V (rating −4 V); dead-time loss +0.1 W per leg",
], 13)

s = slide("Building block: two mirrored cells, one centre driver", 7)
image(s, "img/q3d_model.png", L2)
text(s, R2, [
    "Two cells mirrored about the driver: identical gate loops and Kelvin returns",
    "One 2EDF7275K channel drives a **pair** symmetrically (star network, R_{G} 0.5 Ω per transistor)",
    "Each cell keeps its own commutation loop (0.374 nH per cell, Rev A Q3D)",
    "Driver: 4 A / 8 A, separate turn-on (0.75 Ω) and turn-off (diode + 0 Ω) paths",
], 14)
decision(s, "2 × EPC2361 per driver channel (star per pair); **4 per switch = two pairs, two drivers, one leg board**")

# ================================================================== 8 four on one board
s = slide("Rev B: four cells per switch, two drivers, one leg", 8, "8  Four per switch on one board")
# native diagram: one leg, four cells, two drivers (one per pair), one DC pair, one AC output
bx, by = X0 + 10, Y0 + 20
rect(s, [bx, by, 470, 330], "", fill="white", line="gray", round_=False)
label(s, [bx + 5, by + 3, 300, 18], "Rev B leg board, 89.5 × 80 mm, 4 layers", 11, "gray", True)
rect(s, [bx + 185, by + 22, 45, 22], "DC+", "hs10", "hs", 10, True)
rect(s, [bx + 240, by + 22, 45, 22], "DC−", "kth10", "ls", 10, True)
line(s, [bx + 20, by + 52, bx + 450, by + 52], "hs", 4)
line(s, [bx + 20, by + 64, bx + 450, by + 64], "ls", 4)
line(s, [bx + 207, by + 44, bx + 207, by + 52], "hs", 3)
line(s, [bx + 262, by + 44, bx + 262, by + 64], "ls", 3)
label(s, [bx + 20, by + 30, 160, 16], "laminated terminal row + one bank", 9, "gray")
for k in range(4):
    cx = bx + 30 + k * 110
    rect(s, [cx, by + 85, 90, 65], "cell %d\nHS + LS\nEPC2361" % (k + 1), "hs10", "hs", 10)
    rect(s, [cx + 15, by + 160, 60, 26], "UFCS %d" % (k + 1), "meas10", "meas", 9)
    line(s, [cx + 30, by + 52, cx + 30, by + 85], "hs", 2)
    line(s, [cx + 60, by + 64, cx + 60, by + 85], "ls", 2)
    line(s, [cx + 45, by + 150, cx + 45, by + 160], "black", 1.5)
    line(s, [cx + 45, by + 225, cx + 45, by + 245], "black", 3)
for b in range(2):
    rect(s, [bx + 70 + b * 220, by + 193, 110, 28], "2EDF7275K #%d\nHS + LS, star" % (b + 1), "pri10", "pri", 9)
line(s, [bx + 50, by + 245, bx + 405, by + 245], "black", 5)
label(s, [bx + 40, by + 250, 180, 18], "AC joined in copper (all layers)", 10, "black", True)
line(s, [bx + 235, by + 245, bx + 235, by + 290], "black", 5, True)
label(s, [bx + 245, by + 270, 220, 40], "ONE M6 AC bolt pad → Cu bar\n→ LEM HO 250-S → load", 10)
text(s, [X0 + 500, Y0, 400, 380], [
    "One leg: 4 EPC2361 per switch, **two 2EDF7275K**, each drives one pair (HS + LS channel) through a star",
    "Why one driver per pair (option B): the driver sits between its two cells ⇒ short, identical gate loops (1.7 nH); "
    "one HS + one LS isolated supply, split per driver",
    "**One DC+ / DC− pair** at the centre: laminated terminal row (L1/L3 +, L2/L4 −) feeds one continuous bank",
    "**One AC output**: all four switch nodes joined, one M6 bolt pad, Cu bar through the HO 250-S",
    "UFCS shunt in every LS source: same board for DPT and back-to-back load test; no short-circuit protection",
], 13)

s = slide("Rev B leg board layout", 8)
image(s, "img/revb_top.png", [X0, Y0, 440, 390])
image(s, "img/revb_bottom.png", [X0 + 450, Y0, 230, 390])
text(s, [X0 + 690, Y0, 210, 400], [
    "89.5 × 80 mm, 4 layers, 204 parts",
    "Top edge: one DC+ / DC− pair (REDCUBE M4, bottom side), 20 × 2220 bank in two rows",
    "Bottom edge: one M6 AC bolt pad",
    "Heatsink LAM 4 rotated 90° over cells and bank",
    "DRC 0 / 0 / 0; schematic = PCB (0 problems)",
], 12)

s = slide("Rev B leg board in 3D (KiCad models)", 8)
image(s, "img/revb_3d_noheatsink.png", [X0, Y0, 445, 300])
image(s, "img/revb_3d_iso.png", [X0 + 455, Y0, 445, 300])
text(s, [X0, Y0 + 305, W, 90], [
    "Every footprint has a 3D model: KiCad library parts, plus box models for EPC2361, 2EDF7275K, PMK UFCS, TDK 2220 "
    "(2.8 mm), WE-CNSW, M6 bolt + 12 × 5 mm Cu bar, LAM 4 + Al spreader (scripts/make_3d_models_revb.py)",
    "Board STEP for the mechanics: hardware/spb-bb-revb/fab/spb-bb-revb.step. Spreader underside 1.68 mm, top 4.68 mm: "
    "clears the 2.8 mm bank; the shunts stay in front of the heatsink",
], 12)
note(s, "Box models are dimensioned envelopes, not manufacturer CAD (UFCS SMA jack position approximate).")

s = slide("Rev B leg board in 3D: bottom side", 8)
image(s, "img/revb_3d_bottom.png", [X0, Y0, 560, 380])
text(s, [X0 + 580, Y0, 320, 380], [
    "REDCUBE M4 DC terminals on the bottom: the leg stands on the PCB busbar",
    "4 bypass 0805 per cell under the drains, mirrored in all cells",
    "U.FL probes per cell: V_{GS} HS / LS, V_{DS} LS",
    "M6 nut of the AC bolt under the 14 mm pad",
], 13)
s = slide("Two driver pairs on one switch node: driver skew", 8)
lx_hs = get(RB, "block_to_block", "HS", fmt="%.2f")
lx_ls = get(RB, "block_to_block", "LS", fmt="%.2f")
di = get(RB, "block_to_block", "dI_per_ns_A", fmt="%.0f")
text(s, [X0, Y0, 520, 370], [
    "Joining the AC in copper makes the inductance between the switch nodes of the two driver pairs (L_{x}) small",
    "If driver 2 switches Δt later, pair 1 takes ΔI ≈ V_{m}·Δt / L_{x} until pair 2 follows",
    "Q3D (previous Rev B layout, rerun pending): L_{x} = %s nH (HS on) / %s nH (LS on) ⇒ **≈ %s A per ns of skew**" % (lx_hs, lx_ls, di),
    "Rev A deck required L_{x} ≳ 20 nH for two separate blocks; on one board the skew must be small instead",
], 14)
table(s, [X0 + 545, Y0 + 10, 355, 190], [
    ["Measure", "Rev B"],
    ["One PWM source", "C2000 drives both headers"],
    ["Matched traces", "same PCB, same CMC per block"],
    ["Driver skew", "2EDF7275K part-to-part: check datasheet"],
    ["Verify", "U.FL V_{GS} of both blocks, UFCS per cell"]], size=12, colw=[130, 225])
decision(s, "Measure the per-cell current (UFCS) with both blocks switching; add delay trim in the C2000 if needed")

# ================================================================== 9 supplies, measurement
s = slide("Gate supplies: two isolated supplies, Zener split", 9, "9  Supplies and measurement")
image(s, "img/sch_islands.png", [X0, Y0, 520, 300])
text(s, [X0 + 540, Y0, 360, 370], [
    "One external isolated supply for all HS drivers and one for all LS drivers; each splits per driver through a WE-CNSW common-mode choke",
    "5.1 V Zener VDD–S and 150 Ω bias resistor S–VEE (Karakaya, METU 2020, Fig. 4.1): V_{GS,on} = +5.1 V, V_{GS,off} = −(V_{ISO} − 5.1 V)",
    "e.g. V_{ISO} = 6.3 V ⇒ −1.2 V off (bump mitigation); island decoupling 1 µF + 4.7 µF per rail",
], 13)

s = slide("Driver block: input filters, turn-on / turn-off paths, star", 9)
image(s, "img/sch_driver.png", [X0, Y0, W, 260])
text(s, [X0, Y0 + 270, W, 110], [
    "Per block a 2×3 control header (12 V, GND, PWM_H, PWM_L, DIS) with common-mode chokes on each pair",
    "47 Ω / 100 pF input filters, 10 k pull-downs, R_{ON} 0.75 Ω, R_{OFF} 0 Ω + Schottky, R_{G} 0.5 Ω per transistor",
], 13)

s = slide("Measurement and control", 9)
table(s, [X0, Y0, 520, 270], [
    ["Quantity", "How", "Where"],
    ["Cell current (DPT + load)", "PMK UFCS-R001, 1 mΩ, 120 pH", "LS source of each cell"],
    ["Phase current (control)", "LEM HO 250-S, ±625 A, 3.2 mV/A", "Cu bar on the M6 AC pad"],
    ["V_{GS} HS / LS", "U.FL, 0 Ω, shield = Kelvin", "bottom, at each cell"],
    ["V_{DS} LS", "U.FL, 953 Ω (20:1 into 50 Ω)", "bottom, at each cell"],
    ["Heatsink temperature", "NTC 10 k", "DC− domain"]], size=12, colw=[150, 210, 160])
image(s, "img/sch_ufl.png", [X0 + 545, Y0, 355, 130])
text(s, [X0 + 545, Y0 + 150, 355, 220], [
    "Back-to-back load test, closed loop on a TI TMS320F28379D",
    "UFCS continuous rating 50 A only up to +30 °C ambient: short load-test runs or forced air",
    "No short-circuit protection on the board",
], 13)

s = slide("Power stage schematic (generated, identical to the PCB)", 9)
image(s, "img/sch_power.png", [X0, Y0, W, 330])
note(s, "scripts/make_kicad_sch_revb.py; check_sch_vs_pcb.py: 89 PCB nets, 0 problems")

# ================================================================== 10 three-phase bus
s = slide("Three legs on one 75 V bus: what the bus must do", 10, "10  Three-phase DC bus")
text(s, [X0, Y0, 520, 370], [
    "The switching edge closes on each board (bypass + bank); the bus only carries the f_{sw} ripple between the leg banks",
    "Sharing needs ωL_{bus} ≪ 1/(ωC): at 50 kHz and ≈ 250 µF eff. per leg L ≪ 40 nH ⇒ **target ≤ 5 nH leg to leg**",
    "DC: 250 A stack current enters the level, 83 A per leg",
    "All-MLCC banks joined by nH copper form a high-Q resonator ⇒ damping footprints",
], 14)
bx, by = X0 + 545, Y0 + 20
for k in range(3):
    rect(s, [bx + k * 120, by, 105, 90], "leg %d\n(phase %s)\nRev B board" % (k + 1, "abc"[k]), "kth10", "kth", 10)
    line(s, [bx + 30 + k * 120, by + 90, bx + 30 + k * 120, by + 130], "hs", 3)
    line(s, [bx + 75 + k * 120, by + 90, bx + 75 + k * 120, by + 140], "ls", 3)
line(s, [bx - 5, by + 130, bx + 350, by + 130], "hs", 5)
line(s, [bx - 5, by + 140, bx + 350, by + 140], "ls", 5)
label(s, [bx, by + 148, 350, 18], "laminated PCB busbar (L1 + / L2 − / L3 + / L4 −)", 10, "black", True, "center")
line(s, [bx + 160, by + 140, bx + 160, by + 200], "black", 3, True)
label(s, [bx + 60, by + 205, 220, 30], "stack lugs at the centre leg\nto the levels above / below", 10, "gray", False, "center")

s = slide("PCB busbar: easy to manufacture", 10)
image(s, "img/busbar_top.png", [X0, Y0, W, 140])
table(s, [X0, Y0 + 155, 430, 220], [
    ["Item", "Value"],
    ["Size", "298.5 × 45 mm, 1.6 mm, 4 layers"],
    ["Copper", "2 oz all layers (JLCPCB JLC3313); 3–4 oz option"],
    ["Stack-up", "L1 DC+ / ≤ 0.2 mm / L2 DC− / core / L3 DC+ / ≤ 0.2 mm / L4 DC−"],
    ["Leg contact", "6 × M4: one DC pair per leg (REDCUBE, 6.5 mm)"],
    ["Stack contact", "2 × M6 lug pads at the centre leg (92 vias each)"],
    ["Insulation", "frame holes with 8 mm Cu keep-out (1200 V)"]], size=11, colw=[110, 320])
text(s, [X0 + 455, Y0 + 155, 445, 220], [
    "Estimate (μ_{0}·d·l/w): **%.2f nH** leg to leg" % EST["L_leg_to_leg_nH"],
    "R per polarity and leg segment %.2f mΩ (2 oz) ⇒ %.1f W at 83 A per leg (3 oz: %.1f W, 4 oz: %.1f W)" % (
        EST["R_seg_per_polarity_mOhm"], EST["P_bus_W"], EST.get("P_bus_W_3oz", 5.0), EST.get("P_bus_W_4oz", 3.7)),
    "Damping caps (100 V hybrid polymer) as DNP footprints; nylon standoffs at the leg corner holes",
    "Generated: scripts/make_kicad_busbar.py, DRC clean",
], 13)

# ================================================================== 11 verification (Q3D)
# ================================================================== 11 verification (Q3D), main PCB first
_mx = os.path.join(ROOT, "simulation", "bb_q3d", "results", "BB_PL_REVB_matrix.txt")
AC_SRC = open(_mx).readline().strip() if os.path.exists(_mx) else ""
_m = __import__("re").search(r"MACL(\d+)", AC_SRC)
AC_PASS = ("AC adaptive pass %s (solve still converging)" % _m.group(1)) if _m and "from Q3D solution" in AC_SRC else \
    "converged AC solve"
FS, FN_ = LS["symv"], LS["noshunt_symv"]
s = slide("Q3D: commutation loop per cell, final layout", 11, "11  Verification (Q3D)")
image(s, "img/revb_loop_cells.png", [X0, Y0, 540, 285])
table(s, [X0 + 555, Y0, 345, 150], [
    ["Final layout (nH)", "with shunt", "no shunt"],
    ["cell 1 / 2", "%.2f / %.2f" % tuple(cells("symv")[:2]), "%.2f / %.2f" % tuple(cells("noshunt_symv")[:2])],
    ["cell 3 / 4", "%.2f / %.2f" % tuple(cells("symv")[2:]), "%.2f / %.2f" % tuple(cells("noshunt_symv")[2:])],
    ["**mean**", "**%.2f**" % FS["mean_nH"], "**%.2f**" % FN_["mean_nH"]],
    ["v̂_{DS} at 30 A/ns", "!!%.0f V!!" % FS["overshoot_30Apns_V"], "%.0f V" % FN_["overshoot_30Apns_V"]]],
      size=12, colw=[135, 105, 105])
text(s, [X0 + 555, Y0 + 160, 345, 220], [
    "Four cells within **2 %** (shunt) and **1 %** (no shunt); before the fix the left cells were 0.13–0.14 nH higher",
    "Shunt costs ≈ 0.29 nH: 120 pH part + the LS source detour to the 15 × 3 mm pads",
    "≤ 90 V with the shunt: turn-on ≤ %.0f A/ns" % (15 / FS["mean_nH"]),
], 12)
text(s, [X0, Y0 + 295, 540, 90], [
    "Fast loop-only model: routed copper of the FET band (y −4.6 … 20.6 mm), all 8 FETs, per-cell AC and source nets, "
    "bypass groups as sinks; 2 % convergence, ≈ 45 min per run (run_bb_q3d_loop.cmd)",
], 11)
note(s, "Loop per cell with all four LS FETs switching together (cell coupling included); simulation/bb_q3d/results/loop_summary_*.json")

s = slide("Where the loop current flows (exploded side view)", 11)
image(s, "img/loop_paths.png", [X0, Y0, W, 330])
text(s, [X0, Y0 + 340, W, 50], [
    "Bypass → L1 drain stripes → HS FET → switch node → LS FET → source → (shunt) → L2 DC− plane under the cell → bypass. "
    "The return on L2 directly below L1 makes the loop vertical and small (Karakaya, METU 2020, Design 3)",
], 12)

s = slide("Shunt in the loop: study of the options", 11)
image(s, "img/revb_shunt_study.png", [X0, Y0, 540, 290])
text(s, [X0 + 555, Y0, 345, 380], [
    "UFCS = 0.7 mm blade on two 15 × 3 mm pads: current crosses only at the blade ⇒ fixed geometry",
    "Vias in the shunt DC− pad and a notched heatsink (IN pad shortened, blade 1.45 mm from the source) gain only 0.05–0.08 nH",
    "Largest gain on the routed board: **source via-in-pad** and **symmetric via pruning** (final, 0.69 nH)",
    "Without the shunt, LS source vias straight to L2 (blind L1–L2): **0.41 nH**, close to the 0.374 nH model",
    "Bypass on both sides: the bottom row lowers the loop by only ≈ 0.02 nH; it is there for capacitance",
], 12)
decision(s, "Proposal: two assemblies of the same design: **DPT board with UFCS** (di/dt ≤ 22 A/ns) and **load-test board "
            "without shunt** (source via-in-pad, 30 A/ns)")

s = slide("Left/right symmetry: cause and fix", 11)
table(s, [X0, Y0, 520, 220], [
    ["Test (no-shunt board, nH)", "cell 1", "cell 2", "cell 3", "cell 4"],
    ["as routed", "0.56", "0.42", "0.55", "0.42"],
    ["left FETs not rotated (rot 0)", "0.55", "0.41", "0.54", "0.41"],
    ["Kelvin collectors moved L2 → L4", "0.57", "0.41", "0.55", "0.41"],
    ["mirrored model (solver check)", "0.57", "0.41", "0.56", "0.41"],
    ["**power vias pruned in mirror pairs**", "**0.41**", "**0.41**", "**0.41**", "**0.41**"]],
      size=12, colw=[240, 70, 70, 70, 70])
text(s, [X0 + 545, Y0, 355, 380], [
    "Cause: the clearance clean-up removed power vias near pads one by one; a few vias from the source copper to the L2 "
    "DC− plane survived only in the right cells ⇒ shorter return path there",
    "Not the cause: FET rotation (180° vs 0°), Kelvin routing, solver (mirrored model shows the same)",
    "Fix: a via that fails clearance takes its mirror twin with it (make_kicad_bb_revb.py) ⇒ identical via sets in every "
    "cell; Kelvin collectors stay on L4 (L2 plane uncut)",
], 12)
decision(s, "Symmetric cells ⇒ equal dynamic current sharing by layout; verify with the UFCS per cell in the DPT")

s = slide("Q3D: static current sharing and copper loss (previous layout)", 11)
dcl = RB.get("dc_leg", {})
rows = [["Path (DC)", "R total (mΩ)", "R copper (mΩ)", "current share cell 1 / 2 / 3 / 4", "max/min"]]
for p, lab in (("HS", "DC+ → HS FETs → AC"), ("LS", "AC → LS FETs → shunts → DC−")):
    d = dcl.get(p)
    rows.append([lab] + ([("%.2f" % d["R_total_mOhm"]), ("%.2f" % d["R_copper_mOhm"]),
                          " / ".join("%.0f %%" % (100 * x) for x in d["share"]), "%.2f" % (1 + d["imbalance_pct"] / 100)]
                         if d else ["–"] * 4))
table(s, [X0, Y0, W, 80], rows, size=12, colw=[230, 110, 120, 330, 110])
text(s, [X0, Y0 + 100, W, 270], [
    "!!Previous layout (13 Oct: two DC pairs, four AC terminals, 1210 bank)!!: full-board rerun on the final layout pending",
    "Converged DC solve; FET 0.75 mΩ × 1.49 (100 °C), shunt 1 mΩ; DC terminals joined (bus), AC terminals joined (bar)",
    "Board copper loss at 228 A_{rms}: !!%s W per leg!! (semiconductors ≈ 18 W); shunts ≈ %s W" % (
        get(dcl, "P_copper_W", fmt="%.0f"), get(dcl, "P_shunts_W", fmt="%.1f")),
    "Static sharing is uneven: the inner cells (2, 4) carry ≈ 29 %, the outer cells (1, 3) ≈ 20–23 % ⇒ hotter inner cells",
    "Cause: the copper path from each cell to the joined AC bus and to the DC terminals differs (cell position, AC columns on L3/L4)",
    "Next layout iteration: widen the outer-cell AC columns / add AC copper on L1–L2, 2 oz → 3 oz, symmetric DC terminal placement",
], 13)

s = slide("Main PCB: findings from the Q3D extraction", 11)
bb = RB.get("block_to_block", {})
table(s, [X0, Y0, W, 170], [
    ["Quantity", "Rev B (Q3D)", "Target / Rev A", "Consequence"],
    ["Loop per cell, with shunt", "%.2f nH (4 cells within 2 %%)" % FS["mean_nH"], "0.5 nH design, 0.374 nH Rev A",
     "DPT at ≤ 22 A/ns"],
    ["Loop per cell, no shunt", "%.2f nH (4 cells within 1 %%)" % FN_["mean_nH"], "0.5 nH design",
     "load test at 30 A/ns: 87 V"],
    ["Static sharing, max/min *", get(dcl, "HS", "imbalance_pct", fmt="%.0f") + " % above", "< 10 %",
     "rerun on the final layout"],
    ["Board copper loss *", "%s W per leg" % get(dcl, "P_copper_W", fmt="%.0f"), "≈ 11 W (2 × Rev A block)",
     "rerun on the final layout"],
    ["Block-to-block L_{x} *", "%s nH" % get(bb, "HS", fmt="%.1f"), "≳ 20 nH (Rev A deck)",
     "%s A per ns driver skew" % get(bb, "dI_per_ns_A", fmt="%.0f")],
], size=12, colw=[200, 170, 230, 300])
text(s, [X0, Y0 + 210, W, 180], [
    "Loop: symmetric and within the design value without the shunt; with the shunt the turn-on must be slowed for the DPT",
    "The Rev B board is a good !!measurement!! board: UFCS per cell, U.FL V_{GS} / V_{DS}, both drivers from one C2000",
    "Next Q3D: full board on the final layout (DC sharing, copper loss, L_{x}) and the busbar with one DC pair per leg",
], 13)
note(s, "* previous layout (13 Oct); values in nH unless noted")

s = slide("Q3D: three legs on the PCB busbar", 11)
sysr = RB.get("system", {})
rows = [["Quantity", "Value"],
        ["Leg-to-leg loop 1 → 2 (DC / 1 MHz)", "%s / %s nH" % (get(sysr, "bus_dc", "L_leg12_nH"), get(sysr, "bus_ac", "L_leg12_nH"))],
        ["Leg-to-leg loop 1 → 3 (DC / 1 MHz)", "%s / %s nH" % (get(sysr, "bus_dc", "L_leg13_nH"), get(sysr, "bus_ac", "L_leg13_nH"))],
        ["Ripple of leg 1 at 50 kHz from legs 1 / 2 / 3", " / ".join(
            "%.0f %%" % (100 * x) for x in sysr["ripple_50kHz"]["share_of_leg"]) if "ripple_50kHz" in sysr else "–"],
        ["Busbar DC loss (250 A in, 3 × 83 A)", "%s W" % get(sysr, "dc", "P_bus_W", fmt="%.1f")],
        ["Highest REDCUBE terminal current", "%s A" % get(sysr, "dc", "I_terminal_max_A", fmt="%.0f")]]
table(s, [X0, Y0, 470, 240], rows, size=12, colw=[300, 170])
if HAVE_SWEEP:
    image(s, "img/revb_sweep.png", [X0 + 485, Y0, 415, 240])
text(s, [X0, Y0 + 255, W, 120], [
    "Target ≤ 5 nH leg to leg met at 1 MHz; DC values are the low-frequency limit (current spread through all layers)",
    "!!Busbar version with two DC pairs per leg!!; the busbar is regenerated with one pair per leg, rerun pending",
    "Network: Q3D matrices of three Rev B legs + busbar, MLCC banks with ESR/ESL and 35 % of C at 75 V; peaks in |Z| = inter-leg resonance",
], 13)

# ================================================================== 12 board, status
s = slide("Rev B fabrication files", 12, "12  Rev B board")
image(s, "img/top.png", [X0, Y0, 440, 300])
image(s, "img/bottom.png", [X0 + 460, Y0, 440, 300])
text(s, [X0, Y0 + 310, W, 80], [
    "Generated: make_kicad_bb_revb.py (board), make_kicad_sch_revb.py (schematic), make_kicad_busbar.py (busbar)",
    "3D models for all parts and the board STEP (fab/spb-bb-revb.step); next: Gerbers, drill, BOM and placement for Rev B "
    "and the busbar, LAM 4 100 mm order code",
], 13)

s = slide("Status and next steps", 12, "Status")
table(s, [X0, Y0, 520, 360], [
    ["Item", "Status"],
    ["DC link: 20 × 22 µF 2220 + 10 × 1 µF per cell", "decided, in the layout"],
    ["Rev B leg board (one leg, 4 per switch)", "routed, DRC 0 / 0 / 0"],
    ["Rev B schematic", "generated, = PCB (0 problems)"],
    ["Loop per cell (fast Q3D)", "0.69 nH shunt / 0.41 nH no shunt, symmetric"],
    ["3D models + board STEP", "done"],
    ["PCB busbar (one DC pair per leg)", "routed, DRC clean, 2 oz"],
    ["Q3D full board + busbar, final layout", "next"],
    ["Fab outputs, BOM (Rev B, busbar)", "next"],
    ["DPT (shunt) + load test (no shunt)", "after assembly"]], size=12, colw=[300, 220])
text(s, [X0 + 545, Y0, 355, 370], [
    "Decide: two assemblies (DPT with UFCS, load test without shunt and with source via-in-pad)",
    "Measure: per-cell current sharing (UFCS), V_{GS} of both drivers (skew), V_{DS} overshoot, bus ripple and ringing",
    "Decide after measurement: bank depopulation, damping caps, copper weight of the busbar",
    "Machine: L_{σ}, cos φ and the final f_{sw}",
], 13)

s = slide("Thank you")
s["kind"] = "end"

json.dump(dict(steps=STEPS, slides=SLIDES), open(os.path.join(OUT, "deck.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("slides", len(SLIDES), "Q3D numbers", "yes" if RB else "no")

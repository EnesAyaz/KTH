"""
Rev B design-flow deck (4 x EPC2361 per switch on one board, three legs on a PCB busbar) as an editable PPTX.

    C:\\Github\\KTH\\LossCalculation-SPB\\.venv\\Scripts\\python.exe scripts\\make_revb_deck.py
    powershell -ExecutionPolicy Bypass -File scripts\\build_pptx.ps1
      -> reports/slides/revb_pptx/deck.json, img/*.png  ->  reports/slides/spb_revb_design_flow.pptx

Steps 1-7 follow spb_design_flow_v3 (same figures, converted to PNG in revb_pptx/img); steps 8-12 are the Rev B
board, supplies and measurement, the three-phase DC bus (PCB busbar) and the Q3D verification of leg + busbar
(numbers from reports/slides/data/final_numbers.json, written by simulation/bb_q3d/final_post.py).
Markup in texts: **bold**, !!alert!!, _{sub}, ^{sup}. Coordinates in points on a 960 x 540 slide.
"""
import json
import shutil
import math
import os
import subprocess
import time

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
    retry(lambda: im.save(path))


def retry(fn, n=6):
    # a freshly written image is sometimes held open by another process for a moment (Windows)
    for i in range(n):
        try:
            return fn()
        except (OSError, subprocess.CalledProcessError):
            if i == n - 1:
                raise
            time.sleep(3)


def pdf_crop(pdf, name, box_mm=None, dpi=150):
    out = os.path.join(IMG, name)
    args = [PDFTOPPM, "-r", str(dpi), "-png", "-singlefile"]
    if box_mm:
        k = dpi / 25.4
        x0, y0, x1, y1 = box_mm
        args += ["-x", str(int(x0 * k)), "-y", str(int(y0 * k)), "-W", str(int((x1 - x0) * k)), "-H",
                 str(int((y1 - y0) * k))]
    retry(lambda: subprocess.run(args + [pdf, out], check=True, capture_output=True))
    autocrop(out + ".png")
    return "img/%s.png" % name


KCLI = r"C:\Program Files\KiCad\7.0\bin\kicad-cli.exe"
HW = {b: os.path.join(ROOT, "hardware", "spb-bb-revb-" + b) for b in ("dpt", "load")}
for b, hw in HW.items():
    nm = "spb-bb-revb-" + b
    os.makedirs(os.path.join(hw, "plots"), exist_ok=True)
    subprocess.run([KCLI, "sch", "export", "pdf", "-o", os.path.join(hw, "plots", nm + "_schematic.pdf"),
                    os.path.join(hw, nm + ".kicad_sch")], check=True)
    for side, lays, extra in (("top", "F.Cu,F.SilkS,Edge.Cuts", []), ("bottom", "B.Cu,B.SilkS,Edge.Cuts", ["--mirror"])):
        pdf = os.path.join(hw, "plots", "%s_%s.pdf" % (nm, side))
        subprocess.run([KCLI, "pcb", "export", "pdf", "--layers", lays, "-o", pdf] + extra +
                       [os.path.join(hw, nm + ".kicad_pcb")], check=True)
        pdf_crop(pdf, "revb_%s_%s" % (b, side), None, 200)
SCH = os.path.join(HW["dpt"], "plots", "spb-bb-revb-dpt_schematic.pdf")
pdf_crop(SCH, "sch_power", (380, 25, 745, 160))
pdf_crop(os.path.join(HW["load"], "plots", "spb-bb-revb-load_schematic.pdf"), "sch_power_load", (380, 25, 745, 160))
pdf_crop(SCH, "sch_driver", (25, 180, 262, 258))
pdf_crop(SCH, "sch_islands", (25, 262, 228, 322))
pdf_crop(SCH, "sch_ufl", (25, 322, 245, 352))
pdf_crop(os.path.join(ROOT, "hardware", "spb-busbar", "plots", "spb-busbar-busbar_view.pdf"), "busbar_top", None, 200)
for n in os.listdir(IMG):
    if n.startswith("r3d_"):
        autocrop(os.path.join(IMG, n))

# results of the fast Q3D set (simulation/bb_q3d/run_bb_q3d_final.cmd -> final_post.py); nothing older is used
FP_ = os.path.join(SL, "data", "final_numbers.json")
FQ = json.load(open(FP_)) if os.path.exists(FP_) else {}

plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3})
RES = os.path.join(ROOT, "simulation", "bb_q3d", "results")
sweep = os.path.join(RES, "final_sweep.csv")
HAVE_SWEEP = os.path.exists(sweep)
if HAVE_SWEEP:
    d = np.loadtxt(sweep, delimiter=",", skiprows=1)
    fig, ax = plt.subplots(figsize=(7.0, 3.6), dpi=200)
    ax.loglog(d[:, 0], d[:, 2] * 1e3, color="#888888", lw=1.8, label="leg a alone")
    ax.loglog(d[:, 0], d[:, 1] * 1e3, color="#1954A6", lw=2.2, label="three legs on the PCB busbar")
    ax.axvline(50e3, color="#C84632", ls="--", lw=1)
    ax.text(52e3, d[:, 1].min() * 1e3 * 1.3, "50 kHz", color="#C84632")
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("|Z| seen by the cells of leg a (mΩ)")
    ax.legend(loc="upper center")
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "final_sweep.png"))
    plt.close(fig)


def lcells(b, key="all_switching"):
    return [FQ[b]["loop"][key]["cell%d" % c] for c in range(1, 5)]


HAVE_LOOP = all(b in FQ and "loop" in FQ[b] for b in ("dpt", "load"))
if HAVE_LOOP:
    fig, ax = plt.subplots(figsize=(7.0, 3.7), dpi=200)
    xs = np.arange(4)
    for k, (b, lab, col) in enumerate((("dpt", "DPT board (UFCS shunt, short IN land)", "#C84632"),
                                       ("load", "load-test board (no shunt, source via-in-pad)", "#1954A6"))):
        v = lcells(b)
        ax.bar(xs + (k - 0.5) * 0.36, v, 0.34, color=col, label=lab)
        for x_, y_ in zip(xs + (k - 0.5) * 0.36, v):
            ax.text(x_, y_ + 0.01, "%.3f" % y_, ha="center", va="bottom", fontsize=8)
    ax.axhline(0.5, color="#2CA02C", ls="--", lw=1, label="0.5 nH design value")
    ax.set_xticks(xs)
    ax.set_xticklabels(["cell 1\n(left, block 1)", "cell 2\n(right, block 1)", "cell 3\n(left, block 2)",
                        "cell 4\n(right, block 2)"])
    ax.set_ylabel("commutation loop per cell (nH)")
    ax.set_ylim(0, 1.0)
    ax.legend(fontsize=8, loc="upper center", ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "final_loop_cells.png"))
    plt.close(fig)

# bypass hand-over: TDK 0805 1 uF keeps 18 % at 75 V; L_b from the bank Q3D model of the final boards
LB = FQ.get("bank", {}).get("L_b_nH", [])        # bank model (same copper on both boards), AC 1 MHz
LB_LO, LB_HI = (min(LB), max(LB)) if LB else (None, None)
I_DEV, C_PART = FN["bypass"]["I_dev"], 0.178e-6
dv = np.linspace(0.5, 5.0, 200)
fig, ax = plt.subplots(figsize=(6.0, 4.6), dpi=200)
if LB:
    ax.fill_between(dv, LB_LO * 1e-9 * (I_DEV / dv) ** 2 * 1e6, max(LB_HI, LB_LO * 1.02) * 1e-9 * (I_DEV / dv) ** 2 * 1e6,
                    color="#1954A6", alpha=0.35, label="hand-over, $L_b$ = %.2f–%.2f nH (Q3D)" % (LB_LO, LB_HI))
ax.plot(dv, 1e-9 * (I_DEV / dv) ** 2 * 1e6, color="#C84632", lw=1.2, ls=":", label="hand-over, $L_b$ = 1 nH")
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


def dip(n):
    return I_DEV * math.sqrt((LB_HI if LB else 0.7) * 1e-9 / (n * C_PART))


# ------------------------------------------------------------------ slide helpers
STEPS = ["Inputs", "Device", "Submodule\nvoltage", "One device,\none driver", "n in\nparallel", "f_sw,\nDC link",
         "Gate drive\n→ block", "Four on\none board", "Supplies,\nmeasurement", "Three-phase\nDC bus",
         "Verify\n(Q3D)", "Rev B\nboard"]
SLIDES = []
X0, W = 25, 910                     # body area (960 x 540 design frame, KTH template below the title)
Y0 = 100


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
    s["items"].append(dict(type="decision", box=box or [X0, 462, W, 40], text=txt))


def note(s, txt):
    s["items"].append(dict(type="note", text=txt))


def rect(s, box, txt="", fill="kth10", line="kth", size=11, bold=False, color="black", round_=True):
    s["items"].append(dict(type="rect", box=box, text=txt, fill=fill, line=line, size=size, bold=bold, color=color,
                           round=round_))


def line(s, pts, color="black", w=2.0, arrow=False):
    s["items"].append(dict(type="line", pts=pts, color=color, w=w, arrow=arrow))


def label(s, box, txt, size=10, color="black", bold=False, align="left"):
    s["items"].append(dict(type="label", box=box, text=txt, size=size, color=color, bold=bold, align=align))


def q(*keys, fmt="%.2f", d=None):
    """value from the final Q3D numbers, or '(pending)'."""
    v = FQ if d is None else d
    try:
        for k in keys:
            v = v[k]
        return fmt % v
    except (KeyError, TypeError, IndexError):
        return "(pending)"


L2 = [X0, Y0, 450, 400]             # left half
R2 = [X0 + 465, Y0, 445, 400]       # right half
RF = json.load(open(os.path.join(SL, "data", "revb_flow_numbers.json")))
NP = {k: RF["npar"][k] for k in ("0.5nH", "1nH")}


def npv(L, n, key, fmt="%.1f"):
    if NP[L][n - 1]["tj"] >= 199.0 and key != "vpk":     # thermal runaway on the air heatsink: no steady state
        return "runaway"
    return fmt % NP[L][n - 1][key]


# ================================================================== title and overview
s = slide("SPB Leg Building Block: Design Flow")
s["kind"] = "title"
s["subtitle"] = "Four EPC2361 per switch: DPT and load-test boards, 1200 V / 300 kW SPB inverter"
s["author"] = "Enes Ayaz, KTH Royal Institute of Technology, October 2026"

s = slide("Design flow", 0)
table(s, [X0, Y0, W, 400], [
    ["", "Step", "Question → decision"],
    ["1", "Design inputs", "1200 V, 300 kW, M ≤ 1.15, PMSM cos φ = 0.9 → 228 A_{rms} per leg"],
    ["2", "Device", "100–650 V GaN survey, absolute and per volt → 100 V GaN, EPC2361 (Kelvin pad)"],
    ["3", "Submodule voltage", "V_{m} + L·di/dt ≤ 90 V for 0.5 / 1 nH, even N → 75 V, N = 16"],
    ["4", "One device, one driver", "loop of one cell + LTspice at 0.5 / 1 nH → ≤ 80 A per device"],
    ["5", "n in parallel", "loss, T_{j}, V_{DS} vs n → 4 EPC2361 per switch"],
    ["6", "f_{sw}, DC link", "≥ 50 kHz; 3 % ripple → 20 × 22 µF 2220 + 10 × 1 µF bypass per cell"],
    ["7", "Gate drive → block", "one 2EDF7275K per pair (star, Kelvin) → building block of two cells"],
    ["8", "Four on one board", "two pairs, one DC pair, one AC output → DPT board and load-test board"],
    ["9", "Supplies, measurement", "two isolated supplies + Zener bias, UFCS per cell (DPT), U.FL V_{GS}, MMCX V_{DS}, HO 250-S"],
    ["10", "Three-phase DC bus", "legs share the 75 V bus → laminated PCB busbar; 3D level and 16-level stack"],
    ["11–12", "Verification, boards", "fast Q3D set on the final boards and the busbar; fab files"],
], size=15, colw=[60, 230, 620])

# ================================================================== 1 inputs
s = slide("Design inputs", 1, "1  Design inputs")
image(s, "img/fig_spb_standalone.png", [X0, Y0, W, 215])
table(s, [X0, Y0 + 220, 520, 180], [
    ["Quantity", "Value"],
    ["DC bus", "1200 V nominal"],
    ["Output power", "300 kW"],
    ["Modulation index", "M ≤ 1.15 (SVM)"],
    ["Machine", "PMSM, cos φ assumed 0.9"],
    ["Switching frequency", "≥ 50 kHz (step 6)"],
    ["Cooling / T_{j}", "load test: air 25–40 °C / ≤ 125 °C"],
    ["Device stress", "V_{DS} ≤ 90 V at nominal bus (100 V part)"],
], size=13, colw=[190, 330])
text(s, [X0 + 545, Y0 + 225, 365, 175], [
    "SPB: N three-phase submodules in series on the DC side, each feeding one winding set of the machine",
    "V_{m} = 1200 V / N per submodule; each submodule = 3 legs on one DC link",
], 16)

s = slide("Phase current follows from the inputs", 1)
text(s, [X0, Y0, 540, 400], [
    "Each of the 3N legs delivers P/3N at V_{ph} = M·V_{m}/(2√2):",
    "I_{rms} = P / (3 · M·V_{bus}/(2√2) · cos φ)",
    (1, "N·V_{m} = V_{bus}: the phase current does !!not!! depend on N"),
    (1, "V_{ph} = 1.15 · 75 V / 2√2 = 30.5 V; 6.25 kW per leg"),
    (1, "**%.0f A_{rms} per leg**, %.0f A peak (cos φ = 0.9)" % (FN["I_rms_leg"], FN["I_pk"])),
    (1, "DC current per leg 83 A; series DC chain 250 A"),
    "Losses in this deck are for cos φ = 0.9; the PMSM operating point is confirmed with the machine design",
], 17)
table(s, [X0 + 570, Y0, 340, 200], [["cos φ", "I_{rms} per leg"]] +
      [[k, "%.0f A" % FN["I_vs_pf"][k]] for k in ("1.0", "0.95", "0.9", "0.85")], size=17)

# ================================================================== 2 device
s = slide("Voltage class: why 100 V GaN", 2, "2  Device")
image(s, "img/dev_compare.png", [X0, Y0, W, 270])
text(s, [X0, Y0 + 272, W, 130], [
    "(a) At fixed bus voltage and phase current the minimum semiconductor loss scales with √(R_{DS(on)}·C_{oss,tr}): "
    "the 100 V GaN parts have the lowest product",
    "(b) Per volt of blocking capability: 100 V GaN has the lowest R_{DS(on)}/V_{DS,max} (EPC2361 7.5 µΩ/V, 3–30× "
    "below 200–650 V) at a higher C_{oss}/V; conduction dominates here (12.4 W vs 4–5 W switching per leg, step 5)",
    "(c) Best device per class: 100 V needs more submodules but the fewest devices per switch and the smallest voltage "
    "step → **EPC2361**, 100 V, 0.75 mΩ typ, 3 × 5 mm, top-side cooling",
], 13)

s = slide("EPC2361: key data and the Kelvin source", 2)
image(s, "img/epc_kelvin.png", [X0 + 60, Y0, 790, 255])
table(s, [X0, Y0 + 262, 470, 140], [
    ["Parameter", "Value"],
    ["V_{DS} / transient", "100 / 120 V"], ["R_{DS(on)}", "0.75 mΩ typ (1.0 max)"],
    ["V_{GS} range / V_{GS(th)}", "−4 … +6 V / 0.8 – 2.5 V"],
    ["C_{iss} / C_{oss} / C_{rss}", "3599 / 1019 / 13 pF"], ["Q_{G} / Q_{GD} / Q_{OSS}", "28 / 3.8 / 90 nC"]],
      size=12, colw=[220, 250])
text(s, [X0 + 485, Y0 + 262, 425, 140], [
    "Kelvin pad 2 next to the gate: the gate loop returns at the die, the source stripes and vias (L_{S}) stay in the "
    "power loop only ⇒ no L_{S}·di/dt feedback into v_{GS}",
    "Low threshold and −4 V limit: gate bump and negative bias need care (step 7)",
    "Top of the package at !!source potential!!: the thermal interface must insulate",
], 13)

# ================================================================== 3 submodule voltage
s = slide("Submodule voltage from L·di/dt", 3, "3  Submodule voltage")
image(s, "img/flow_vm2.png", [X0, Y0, W, 268])
v05 = RF["vm"]["80_A_0.5nH"]
v1 = RF["vm"]["80_A_1nH"]
text(s, [X0, Y0 + 270, W, 90], [
    "Peak stress v̂_{DS} = V_{m} + L_{loop}·di/dt ≤ 90 V; turn-on di/dt (gate-charge model, R_{g,on} 2 Ω): %.0f / %.0f / "
    "%.0f A/ns at 60 / 80 / 120 A per device" % (RF["vm"]["60_A_0.5nH"]["didt"], v05["didt"],
                                                 RF["vm"]["120_A_0.5nH"]["didt"]),
    "At 80 A per device: V_{m} ≤ **%.0f V** with 0.5 nH, only %.0f V with 1 nH ⇒ the loop must stay near 0.5 nH (or the "
    "turn-on is slowed); N even (symmetric winding sets): 16 → 75 V" % (v05["vm_max"], v1["vm_max"]),
], 14)
decision(s, "V_{m} = 75 V, N = 16; layout target 0.5 nH per cell")

s = slide("Why not lower: every submodule costs parts and loss", 3)
image(s, "img/flow_cells.png", [X0, Y0, 520, 400])
text(s, [X0 + 540, Y0, 370, 400], [
    "Phase current is fixed by P, V_{bus}, M, cos φ, not by N",
    "Each submodule carries the full phase current ⇒ conduction loss, transistors, drivers and supplies scale with N",
    "60 V (N = 20): +25 % parts and conduction loss",
    "Overshoot margin rechecked on the final boards (Q3D, step 11)",
], 17)

# ================================================================== 4 one device
s = slide("Power loop of one cell: copper, bypass ESL and shunt", 4, "4  One device, one driver")
if os.path.exists(os.path.join(IMG, "loop_breakdown.png")):
    image(s, "img/loop_breakdown.png", [X0, Y0, W, 262])
LBK = json.load(open(os.path.join(RES, "loop_breakdown.json"))) if os.path.exists(
    os.path.join(RES, "loop_breakdown.json")) else {}


def lbk(b, key, fmt="%.2f"):
    try:
        return fmt % LBK[b][key]
    except KeyError:
        return "(pending)"


text(s, [X0, Y0 + 265, W, 95], [
    "Q3D of the final boards (cell band): loop = copper of the vertical loop over 0.1 mm (vias, pads) + bypass ESL/n "
    "(+ UFCS 120 pH on the DPT board)",
    "Copper alone: %s nH (load) / %s nH (DPT, shunt path); with 6 + 4 bypass 0805 per cell: **%s / %s nH**" % (
        lbk("load", "copper"), lbk("dpt", "copper"), lbk("load", "total"), lbk("dpt", "total")),
    "Beyond ≈ 4 bypass parts per cell the number hardly matters; part: 1 µF 100 V X7S 0805 next to the drains",
], 14)
decision(s, "Design value L_{loop} = 0.5 nH per cell; 1 nH as the pessimistic bound")

FL1 = RF["single"]


def vpk(L, i):
    d = FL1[L]
    return float(np.interp(i, d["I"], d["vpk"]))


s = slide("One EPC2361 per switch: how fast and how much overshoot", 4)
image(s, "img/flow_single2.png", [X0, Y0, W, 255])
text(s, [X0, Y0 + 258, W, 150], [
    "LTspice half bridge at 75 V, lumped loop 0.5 / 1 nH, 1.7 nH gate loop, 2 Ω on / 0 Ω off, 4 A / 8 A driver",
    "(a) Peak V_{DS} at 60 / 80 / 120 A: %.0f / %.0f / %.0f V (0.5 nH), %.0f / %.0f / %.0f V (1 nH)" % (
        vpk("0.5nH", 60), vpk("0.5nH", 80), vpk("0.5nH", 120), vpk("1nH", 60), vpk("1nH", 80), vpk("1nH", 120)),
    "(b, c) A larger loop lowers E_{on} (the loop takes L·di/dt of the voltage while the current rises) but raises E_{off} "
    "and the overshoot; turn-on di/dt is set by the driver (≈ 45 A/ns)",
    "(d) Conduction per device at 100 °C: %.1f / %.1f / %.1f W at 60 / 80 / 120 A_{rms}; one device would carry 322 A "
    "peak ⇒ **current per device ≤ 80 A**" % (RF["cond"]["60"]["P100"], RF["cond"]["80"]["P100"],
                                              RF["cond"]["120"]["P100"]),
], 13)

# ================================================================== 5 n parallel
TH = RF["thermal"]
s = slide("Thermal path per device: load-test board", 5, "5  Devices in parallel")
table(s, [X0, Y0, 590, 230], [["Path (LAM 4 K 50 12 in air, per device)", "K/W"],
                              ["R_{θJC} (top), datasheet", "%.2f" % TH["R_JC"]],
                              ["gap pad 0.4 mm, 5 W/mK, over the 15 mm² package top", "%.1f" % TH["R_PAD"]],
                              ["Al spreader, outer cell → tube (8 mm in 12.8 × 3 mm, 2 devices)", "%.1f" % TH["R_SPR"]],
                              ["**Junction → heatsink, per device**", "**%.1f**" % TH["R_JH"]],
                              ["Heatsink → air, whole leg (Fischer LAM 4 K 50 12)", "%.2f" % TH["R_HS"]]],
      size=15, colw=[500, 90])
text(s, [X0 + 610, Y0, 300, 400], [
    "T_{j} = T_{amb} + 0.65 K/W · P_{leg} + %.1f K/W · P_{device}" % TH["R_JH"],
    "The gap pad dominates (insulation is needed: the package top is at source potential)",
    "n = 4 at full load: **%.0f °C** (40 °C ambient), %.0f °C (25 °C), %.0f °C with a 3 W/mK pad" % (
        TH["tj4_40"], TH["tj4_25"], TH["tj4_40_3W"]),
    "R_{DS(on)}(T_{j}): ×1.49 at 100 °C, ×1.80 at 150 °C",
], 15)
note(s, "Spreader and pad values are hand estimates from the dimensions; for n ≠ 4 the same per-device path is assumed.")

s = slide("n identical cells per switch (one device and one driver each)", 5)
image(s, "img/flow_npar2.png", [X0, Y0, W, 280])
text(s, [X0, Y0 + 282, W, 80], [
    "228 A_{rms} per leg, 50 kHz, T_{j} and R_{DS(on)} solved together (load-test board in air, previous slide); LTspice "
    "energies at 0.5 nH (left bars) and 1 nH (hatched)",
    "n = 4: %s W (0.5 nH) / %s W (1 nH) per leg, T_{j} %s °C; peak V_{DS} at 80 A: **%s V (0.5 nH), %s V (1 nH)**" % (
        npv("0.5nH", 4, "tot"), npv("1nH", 4, "tot"), npv("0.5nH", 4, "tj", "%.0f"), npv("0.5nH", 4, "vpk", "%.0f"),
        npv("1nH", 4, "vpk", "%.0f")),
], 14)
decision(s, "**4 EPC2361 per switch** (T_{j} < 80 °C in all three cases; ≤ 90 V needs ≈ 0.5 nH; two equal pairs)")

s = slide("Where the loss comes from: line period and junction temperature", 5)
image(s, "img/flow_wave2.png", [X0, Y0, W, 310])
w05, w1 = RF["wave"]["0.5nH"], RF["wave"]["1nH"]
text(s, [X0, Y0 + 312, W, 95], [
    "n = 4, 50 kHz: switching loss follows |i| (plus a constant E_{oss} part), conduction loss follows i²",
    "Conduction %.1f W per leg (at the load-test T_{j}); switching %.1f W at 0.5 nH, %.1f W at 1 nH (lower E_{on}, "
    "higher E_{off} and overshoot)" % (w05["p_cond"], w05["p_sw"], w1["p_sw"]),
], 15)

s = slide("Losses vs number in parallel", 5)
rows = [["n per switch"] + [str(n) for n in range(1, 9)]]
for L, lab in (("0.5nH", "0.5 nH"), ("1nH", "1 nH")):
    rows.append(["Loss per leg, %s (W)" % lab] + [npv(L, n, "tot") for n in range(1, 9)])
rows += [["  conduction at T_{j} (W)"] + [npv("0.5nH", n, "cond") for n in range(1, 9)],
         ["  switching 0.5 / 1 nH (W)"] + [("%s / %s" % (npv("0.5nH", n, "sw"), npv("1nH", n, "sw")))
                                          if NP["0.5nH"][n - 1]["tj"] < 199 else "–" for n in range(1, 9)],
         ["Efficiency, 0.5 nH (%)"] + [("%.2f" % (100 * NP["0.5nH"][n - 1]["eta"])) if NP["0.5nH"][n - 1]["tj"] < 199
                                       else "–" for n in range(1, 9)],
         ["Loss per device (W)"] + [npv("0.5nH", n, "pdev") for n in range(1, 9)],
         ["T_{j} (°C)"] + [npv("0.5nH", n, "tj", "%.0f") for n in range(1, 9)],
         ["Peak V_{DS} 0.5 / 1 nH (V)"] + ["%s / %s" % (npv("0.5nH", n, "vpk", "%.0f"), npv("1nH", n, "vpk", "%.0f"))
                                         for n in range(1, 9)],
         ["Driver channels per leg"] + [str(2 * n) for n in range(1, 9)]]
table(s, [X0, Y0, W, 330], rows, size=14, colw=[270] + [80] * 8)
note(s, "Semiconductor losses only; leg loss / (2 n) = loss per device; T_j on the load-test board at 40 °C ambient, 50 kHz; efficiency relative to 6.25 kW per leg.")

# ================================================================== 6 fsw, DC link
s = slide("Switching frequency: losses, DC-link capacitors, current ripple", 6, "6  Switching frequency and DC link")
image(s, "img/flow_fsw2.png", [X0, Y0, W, 280])
text(s, [X0, Y0 + 282, W, 80], [
    "(a) n = 4: %.2f / %.2f / %.2f %% at 20 / 50 / 100 kHz; (b) the voltage ripple sets the 2220 count (20 per leg at "
    "50 kHz), ripple current needs only %d; (c) winding ripple Δi_{pp} = V_{m}/(4 L_{σ} f_{sw}) depends on the machine" % (
        RF["fsw"]["eta4"]["20"], RF["fsw"]["eta4"]["50"], RF["fsw"]["eta4"]["100"], RF["fsw"]["n_i"]),
], 14)
decision(s, "f_{sw} ≥ 50 kHz (higher allowed by the machine); the DC link is sized for 50 kHz")

CC = json.load(open(os.path.join(SL, "data", "capacitor_compare.json")))
s = slide("DC-link sizing for a three-phase level", 6)
image(s, "img/dclink2.png", [X0, Y0, 520, 330])
table(s, [X0 + 540, Y0, 370, 120], [
    ["f_{sw}", "ΔV_{pp}", "C_{eff} level", "per leg"],
    ["50 kHz", "2 %", "573 µF", "191 µF"], ["50 kHz", "**3 %**", "**382 µF**", "**127 µF**"],
    ["100 kHz", "2 %", "287 µF", "96 µF"], ["100 kHz", "3 %", "191 µF", "64 µF"]], size=14, colw=[85, 75, 115, 95])
text(s, [X0 + 540, Y0 + 145, 370, 230], [
    "One 75 V level = three legs on one bus (SVPWM, M = 1.15, cos φ = 0.9)",
    "Balanced three-phase: no 2f ripple; capacitor RMS current 85 A per level (≈ 28 A per leg)",
    "Per switching period the bank supplies the difference between the cell current and its average: ΔV_{pp} = ΔQ / C",
], 14)
decision(s, "ΔV_{pp} ≤ 3 % (2.25 V) at 50 kHz ⇒ 127 µF **effective** per leg board ⇒ 20 × 22 µF 2220")

s = slide("Capacitor selection: effective capacitance at 75 V", 6)
rows = [["Part (100 V X7S)", "Size", "C_{nom} → C at 75 V", "Kept", "ESR 50 kHz", "Parts / leg (3 %)"]]
for p_ in CC["parts"]:
    rows.append([("**%s**" % p_["part"]) if "226" in p_["part"] else p_["part"], p_["size"],
                 "%.1f → %.2f µF" % (p_["C_nom_uF"], p_["C_eff_uF"]), "%.0f %%" % (100 * p_["retention"]),
                 ("%.1f mΩ" % p_["ESR50k_mOhm"]) if p_["ESR50k_mOhm"] else "–", str(p_["n_50kHz_3pct"])])
table(s, [X0, Y0, W, 190], rows, size=14, colw=[290, 70, 180, 75, 120, 175])
text(s, [X0, Y0 + 200, W, 160], [
    "DC bias at 75 V from the manufacturers' characteristic data (TDK, Murata): 100 V class-II MLCCs keep only 15–29 %",
    "TDK C5750X7S2A226M280KB (2220, 22 µF): highest C per part and per area (0.22 µF/mm²), 2.8 mΩ, 4.5 A for +10 K",
    "Checks: 2.8 mm height under the heatsink spreader; 2220 flex cracking ⇒ away from the board edge and holes",
], 15)
decision(s, "Bank: **20 × TDK C5750X7S2A226M280KB** per leg (2 rows), 127 µF effective, 1.4 A ripple per part")

s = slide("Bypass capacitors: how many and how large", 6)
image(s, "img/revb_bypass.png", [X0, Y0, 440, 360])
text(s, [X0 + 455, Y0, 455, 360], [
    "**Bypass** (1 µF 0805 at the drains) supplies the edge, **bank** the f_{sw} ripple; per cell 81 A:",
    (1, "di/dt → number: L_{Cu} + ESL/n ≈ 0.5 nH ⇒ n ≥ 4"),
    (1, "Hand-over to the bank through L_{b}: C_{bp} ≥ L_{b}(ΔI/ΔV)² !!sets the value!!"),
    (1, ("L_{b} from Q3D (final boards, bypass → bank, 1 MHz): **%.2f–%.2f nH**" % (LB_LO, LB_HI))
     if LB else "L_{b} from Q3D: (pending)"),
    (1, "0805 1 µF 100 V X7S keeps only **18 %** at 75 V (TDK data): 0.18 µF per part"),
    (1, ("6 per cell = 1.1 µF ⇒ %.1f V dip; 10 per cell = 1.8 µF ⇒ **%.1f V** dip" % (dip(6), dip(10))) if LB else
     "dip for 6 / 10 per cell: (pending bank model)"),
], 15)
decision(s, "10 × 1 µF 0805 per cell: 6 on top at the drains + 4 on the bottom, identical in all cells")

s = slide("DC link of one leg board", 6)
table(s, [X0, Y0, 520, 120], [
    ["Per leg board", "Parts", "Nominal", "At 75 V"],
    ["Bypass, 10 per cell × 4", "40 × 1 µF 0805", "40 µF", "7 µF"],
    ["Bank, rows A (8) + B (12)", "20 × 22 µF 2220", "440 µF", "127 µF"],
    ["Total", "60", "480 µF", "134 µF"]], size=13, colw=[205, 145, 80, 90], bold_last=True)
text(s, [X0, Y0 + 150, 520, 300], [
    "Ripple at 50 kHz with the three legs of a level sharing: **2.1 V (2.9 %)**",
    "Leg alone (DPT, back-to-back test without the busbar): ≈ 2× higher, acceptable for the lab tests",
    "Bank ≥ 10 × bypass (127 vs 7 µF eff.): fulfilled",
    "Row A leaves the board centre free for the DC terminal pins",
], 16)
image(s, "img/r3d_load_nohs.png", [X0 + 540, Y0, 370, 360])
decision(s, "Same DC link on the DPT and load-test boards")

# ================================================================== 7 gate drive
s = slide("Can one driver drive all four?", 7, "7  Gate drive: from 4 devices to a building block")
image(s, "img/drv_scaling.png", [X0, Y0, W, 245])
text(s, [X0, Y0 + 250, W, 155], [
    "Why E_{on} per transistor rises with n per channel: the n gate capacitances (n × 3.6 nF C_{iss}) charge through one "
    "driver output (4 A source, 0.85 Ω) and a longer shared gate trace ⇒ v_{GS} rises n× slower ⇒ lower di/dt and dv/dt at "
    "turn-on ⇒ longer V–I overlap: **+16 / +31 / +60 %** E_{on} for 3 / 4 / 6",
    "(b) Extra gate-loop inductance of the longer tree raises the gate bump; (a) peak sink current 12–14 A for 4–6 "
    "devices exceeds the 8 A rating",
    "(c) One channel per device is symmetric but needs 4 channels and supplies per switch",
], 14)

s = slide("Driver arrangement for 1 … 4 EPC2361 per switch", 7)
image(s, "img/drv_layouts.png", [X0, Y0, 560, 330])
text(s, [X0 + 575, Y0, 335, 400], [
    "One dual-channel driver (HS + LS) between two cells: both gate loops equal and with their own Kelvin return "
    "(design value ≈ 1.7 nH; extracted on the routed board: step 11)",
    "n = 3 breaks the symmetry (pair + single)",
    "n = 4: two pairs, two drivers, one star per pair ⇒ the building block of two point-symmetric cells",
], 16)
decision(s, "2 × EPC2361 per driver channel; 4 per switch = two pairs = two drivers")

s = slide("Gate driver selection: why the 2EDF7275K", 7)
table(s, [X0, Y0, W, 175], [
    ["", "**2EDF7275K** (Infineon)", "1EDF5673K (Infineon)", "LMG1210 (TI)"],
    ["Channels / isolation", "2, each output isolated (functional)", "1, isolated", "half bridge, bootstrap HS"],
    ["Peak source / sink", "4 A / 8 A", "0.85 Ω / 0.35 Ω output", "1.5 A / 3 A class"],
    ["Prop. delay / mismatch", "37 ns / ≤ 3 ns ch-ch", "37 ns", "≤ 21 ns / ≤ 3.4 ns"],
    ["CMTI", "150 V/ns", "> 200 V/ns", "300 V/ns (HS dv/dt)"],
    ["Off-voltage", "external (Zener split)", "built-in negative (RC)", "0 V only"],
    ["ICs per switch (4 EPC2361)", "**2** (one per pair)", "4", "2 (weak for a pair)"]],
      size=13, colw=[220, 240, 225, 225])
text(s, [X0, Y0 + 225, W, 180], [
    "A pair needs ≈ 2 × 3.6 nF: 4 A / 8 A drives it at the single-device speed; the 1.5 A / 3 A half-bridge driver does not",
    "Two isolated outputs in one 5 × 5 mm LGA: HS and LS of the same pair from one IC, ≤ 3 ns channel mismatch",
    "Floating outputs: each output gets its own supply split (5.1 V Zener on, −1.9 V off) for the bump margin (next)",
], 15)
note(s, "Data: Infineon / TI product pages and datasheets (2EDF7275K, 1EDF5673K, LMG1210); check the current revision.")

s = slide("Why symmetry: what sets the current sharing", 7)
image(s, "img/fig_sharing.png", [X0, Y0, W, 175])
table(s, [X0, Y0 + 180, W, 180], [
    ["Asymmetry (LTspice, two EPC2361 in parallel)", "Case", "E_{on}+E_{off} imbalance", "Layout measure"],
    ["Power-loop inductance mismatch", "L_{D} +0.3 nH", "2 %", "symmetric cells, identical via sets"],
    ["Gate-loop inductance mismatch", "L_{G} 2 vs 8 nH", "**19 %** (E_{on} 4 : 1)", "star network, equal gate traces"],
    ["Common-source inductance, no Kelvin", "symmetric", "0 %, both +47 % E_{on}", "Kelvin pad per device"],
    ["Common-source mismatch, no Kelvin", "L_{CS} +0.2 nH", "**29 %**", "Kelvin return per device"],
    ["Threshold spread", "V_{th} +0.3 V", "7 %", "same driver channel per pair"],
    ["Static (conduction): copper / R_{DS(on)}", "–", "self-limiting (positive TC)", "symmetric copper (Q3D, step 11)"]],
      size=12, colw=[300, 130, 210, 270])
decision(s, "Star gate network with Kelvin returns, one driver channel per pair, point-symmetric cells")

s = slide("Gate bump and negative off-voltage", 7)
image(s, "img/bump_mechanism.png", [X0, Y0, 560, 195])
image(s, "img/bump_mitigation.png", [X0, Y0 + 200, 560, 205])
text(s, [X0 + 575, Y0, 335, 400], [
    "**Bump:** when the other device of the leg turns on, the off device sees dv/dt; C_{GD}·dv/dt flows through its gate "
    "loop and lifts v_{GS} by ≈ Q_{GD}/C_{GS} ≈ 1.06 V",
    "Independent of load current and bus voltage (top b, c); close to the 0.8 V minimum threshold ⇒ shoot-through risk",
    "**Negative off-voltage** shifts the whole bump down: −1 V ⇒ peak ≈ 0 V; extra C_{GS} divides it further (bottom)",
    "Cost: reverse conduction in the dead time at V_{SD} + |V_{off}|; off-state ringing must stay above the −4 V limit",
    "Implemented: V_{GS,off} = −(V_{ISO} − 5.1 V) = **−1.9 V** (V_{ISO} = 7 V), set with the extracted gate loop "
    "(step 11): bump ≤ −0.5 V, ringing ≈ −3.4 V",
], 13)

s = slide("Building block: two point-symmetric cells, one centre driver", 7)
if os.path.exists(os.path.join(IMG, "q3d_model_cells.png")):
    image(s, "img/q3d_model_cells.png", [X0, Y0, 540, 355])
text(s, [X0 + 555, Y0, 355, 355], [
    "Q3D model of the final board (cell band): copper per net, vias, FET pads and bypass terminals",
    "Two cells rotated by 180° about the driver (point symmetry): identical gate loops and Kelvin returns",
    "One 2EDF7275K channel drives a **pair** (star network, R_{G} 0.5 Ω per transistor)",
    "Each cell keeps its own commutation loop (step 11: %s nH load board, %s nH DPT board)" % (
        q("load", "loop", "mean_nH"), q("dpt", "loop", "mean_nH")),
], 15)
decision(s, "2 × EPC2361 per channel; **4 per switch = two pairs, two drivers, one leg board**")

# ================================================================== 8 four on one board


def durations():
    """minutes per Q3D step from results/final_progress.txt: gaps between consecutive 'done' stamps (the batch
    writes the 'step' stamps with the queue start time)."""
    import re as _re
    p = os.path.join(RES, "final_progress.txt")
    out, last = {}, None
    if not os.path.exists(p):
        return out
    for line in open(p):
        m = _re.match(r"\[\s*(\d+):(\d+):(\d+)[,.](\d+)\] (step|done) (\S+)", line.strip())
        if not m:
            continue
        t = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
        if m.group(5) == "step" and last is None:
            last = t
        elif m.group(5) == "done" and last is not None:
            out[m.group(6)] = ((t - last) % 86400) / 60.0
            last = t
    return out


DUR = durations()

s = slide("Rev B: four cells per switch, two drivers, one leg", 8, "8  Four per switch on one board")
bx, by = X0 + 10, Y0 + 20
rect(s, [bx, by, 470, 330], "", fill="white", line="gray", round_=False)
label(s, [bx + 5, by + 3, 300, 18], "Rev B leg board, 89.5 × 85.2 mm, 4 layers", 11, "gray", True)
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
    rect(s, [cx + 5, by + 160, 80, 26], "UFCS (DPT only)", "meas10", "meas", 8)
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
    "Why one driver per pair: the driver sits between its two cells ⇒ short, identical gate loops; one HS + one LS "
    "isolated supply, split per driver",
    "**One DC+ / DC− pair** at the centre: laminated terminal row (L1/L3 +, L2/L4 −) feeds one continuous bank",
    "**One AC output**: all four switch nodes joined, one M6 bolt pad, Cu bar through the HO 250-S",
    "Built as **two boards** from the same generator: DPT (UFCS shunt per cell) and load test (no shunt)",
], 15)

s = slide("Two boards from one design: double-pulse test and load test", 8)
table(s, [X0, Y0, W, 300], [
    ["", "DPT board (spb-bb-revb-dpt)", "Load-test board (spb-bb-revb-load)"],
    ["Purpose", "switching energies, per-cell current, overshoot", "back-to-back / three-phase load test"],
    ["LS source path", "PMK UFCS-R001 per cell (1 mΩ, 120 pH)", "source stripes via-in-pad (blind L1–L2) to DC−"],
    ["UFCS land", "IN land shortened to 1.2 mm: blade 1.45 mm from the source", "–"],
    ["Cooling", "none (pulsed test)", "Fischer LAM 4 K 50 12 on an Al spreader"],
    ["Loop per cell (Q3D)", "%s nH (mean)" % q("dpt", "loop", "mean_nH", fmt="%.2f"),
     "%s nH (mean)" % q("load", "loop", "mean_nH", fmt="%.2f")],
    ["v̂_{DS} at 30 A/ns", "%s V" % q("dpt", "loop", "overshoot_30Apns_V", fmt="%.0f"),
     "%s V" % q("load", "loop", "overshoot_30Apns_V", fmt="%.0f")],
    ["Parts / DRC / schematic", "200 footprints, DRC 0 / 0 / 0, schematic = PCB", "200 footprints, DRC 0 / 0 / 0, "
                                                                              "schematic = PCB"]],
      size=13, colw=[170, 365, 365])
decision(s, "Same copper, drivers, bank and terminals; only the LS source path and the cooling differ")

s = slide("DPT board layout (UFCS shunts, no heatsink)", 8)
image(s, "img/revb_dpt_top.png", [X0, Y0, 440, 390])
image(s, "img/revb_dpt_bottom.png", [X0 + 450, Y0, 230, 390])
text(s, [X0 + 690, Y0, 210, 400], [
    "89.5 × 85.2 mm, 4 layers",
    "UFCS-R001 per cell, IN land 1.2 mm (blade at the source edge), return vias in the SHLD pad",
    "No heatsink, no spreader holes",
    "DRC 0 / 0 / 0, schematic = PCB",
], 14)

s = slide("Load-test board layout (no shunt, heatsink)", 8)
image(s, "img/revb_load_top.png", [X0, Y0, 440, 390])
image(s, "img/revb_load_bottom.png", [X0 + 450, Y0, 230, 390])
text(s, [X0 + 690, Y0, 210, 400], [
    "89.5 × 85.2 mm, 4 layers",
    "LS source stripes: 3 blind L1–L2 vias each (filled, capped) into the DC− plane",
    "LAM 4 K 50 12 over the cells, 3 spreader holes (H5–H7)",
    "DRC 0 / 0 / 0, schematic = PCB",
], 14)

s = slide("The two boards in 3D (KiCad models)", 8)
image(s, "img/r3d_dpt.png", [X0, Y0, 445, 300])
image(s, "img/r3d_load.png", [X0 + 455, Y0, 445, 300])
label(s, [X0, Y0 + 300, 445, 18], "DPT board: UFCS shunts over the LS FETs, M6 AC bolt + Cu bar", 11, "gray", False,
      "center")
label(s, [X0 + 455, Y0 + 300, 445, 18], "Load-test board: LAM 4 K 50 12 + Al spreader", 11, "gray", False, "center")
text(s, [X0, Y0 + 325, W, 70], [
    "Every footprint has a 3D model (KiCad library + box models: EPC2361, 2EDF7275K, UFCS, TDK 2220, WE-CNSW, M6 bolt "
    "+ bar, heatsink); board STEPs in hardware/spb-bb-revb-*/fab; rendered with pyvista (scripts/render_3d.py)",
], 14)
note(s, "Box models are dimensioned envelopes, not manufacturer CAD (UFCS SMA jack position approximate).")

s = slide("Top view with the silkscreen: DPT and load-test boards", 8)
image(s, "img/r3d_dpt_top.png", [X0, Y0, 450, 360])
image(s, "img/r3d_load_top.png", [X0 + 460, Y0, 450, 360])
label(s, [X0, Y0 + 365, 450, 20], "DPT board (UFCS shunts over the LS FETs)", 13, "gray", False, "center")
label(s, [X0 + 460, Y0 + 365, 450, 20], "load-test board (heatsink removed for the view)", 13, "gray", False, "center")

s = slide("Bottom side and the load board without heatsink", 8)
image(s, "img/r3d_dpt_bottom.png", [X0, Y0, 445, 300])
image(s, "img/r3d_load_nohs.png", [X0 + 455, Y0, 445, 300])
text(s, [X0, Y0 + 310, W, 80], [
    "Bottom: REDCUBE M4 DC terminals (the leg stands on the busbar), 4 bypass 0805 per cell, U.FL V_{GS} and MMCX V_{DS} ports, M6 AC nut",
    "Top without heatsink: 20 × 2220 bank in two rows, 8 EPC2361 under the spreader pedestals, 2 drivers",
], 14)

s = slide("Two driver pairs on one switch node: driver skew", 8)
text(s, [X0, Y0, 520, 370], [
    "The four switch nodes are joined in copper; L_{x} = inductance between the switch nodes of the two driver pairs",
    "If driver 2 switches Δt later, pair 1 takes ΔI ≈ V_{m}·Δt / L_{x} until pair 2 follows",
    "Q3D (fast lx model, final boards): L_{x} = **%s nH** (HS on) / **%s nH** (LS on) on the load board, %s / %s nH on "
    "the DPT board" % (q("load", "lx", "HS"), q("load", "lx", "LS"), q("dpt", "lx", "HS"), q("dpt", "lx", "LS")),
    "⇒ **≈ %s A per ns of skew** (load board)" % q("load", "lx", "dI_per_ns_A", fmt="%.0f"),
], 14)
table(s, [X0 + 545, Y0 + 10, 355, 190], [
    ["Measure", "Rev B"],
    ["One PWM source", "C2000 drives both headers"],
    ["Matched traces", "same PCB, same CMC per block"],
    ["Driver skew", "2EDF7275K part-to-part: check datasheet"],
    ["Verify", "U.FL V_{GS} of both blocks, UFCS per cell (DPT)"]], size=13, colw=[130, 225])
image(s, "img/q3d_full_load.png", [X0 + 545, Y0 + 205, 365, 250])
decision(s, "Measure the per-cell current (UFCS) with both drivers switching; delay trim in the C2000 if needed",
         [X0, 462, 530, 40])

# ================================================================== 9 supplies, measurement
s = slide("Gate supplies: two isolated supplies, Zener split", 9, "9  Supplies and measurement")
image(s, "img/sch_islands.png", [X0, Y0, 560, 400])
text(s, [X0 + 540, Y0, 360, 370], [
    "One external isolated supply for all HS drivers and one for all LS drivers; each splits per driver through a WE-CNSW common-mode choke",
    "5.1 V Zener VDD–S and 150 Ω bias resistor S–VEE (Karakaya, METU 2020, Fig. 4.1): V_{GS,on} = +5.1 V, V_{GS,off} = −(V_{ISO} − 5.1 V)",
    "V_{ISO} = 7.0 V ⇒ −1.9 V off (bump mitigation, inside the −4 V limit); island decoupling 1 µF + 4.7 µF per rail",
], 15)

s = slide("Driver block: input filters, turn-on / turn-off paths, star", 9)
image(s, "img/sch_driver.png", [X0, Y0, W, 260])
text(s, [X0, Y0 + 270, W, 110], [
    "Per block a 2×5 control header (each signal next to its return); common-mode chokes on 12 V, DIS and NTC, none on "
    "PWM_H / PWM_L (no extra delay or LC ringing with the 100 pF input filter; removed after the PWM review)",
    "47 Ω / 100 pF input filters, 10 k pull-downs, R_{ON} 1.5 Ω (shared by the pair), R_{OFF} 0 Ω + Schottky, "
    "R_{G} 0.5 Ω per transistor ⇒ R_{g,on} = 3.5 Ω per device",
], 15)

s = slide("Measurement and control", 9)
table(s, [X0, Y0, 520, 270], [
    ["Quantity", "How", "Where"],
    ["Cell current (DPT)", "PMK UFCS-R001, 1 mΩ, 120 pH", "LS source of each cell, DPT board"],
    ["Phase current (control)", "LEM HO 250-S, ±625 A, 3.2 mV/A", "Cu bar on the M6 AC pad"],
    ["V_{GS} HS / LS", "U.FL, 0 Ω, shield = Kelvin", "bottom, at each cell (both boards)"],
    ["V_{DS} LS (DPT)", "MMCX (WR-MMCX, 170 V rms): SW / LSRC, rated isolated probe (e.g. IsoVu TIVPMX50X)",
     "bottom, next to each LS FET"],
    ["Bring-up", "test points + spring-tip pads (V_{GS}, V_{DS}), list in fab/testpoints.csv", "both sides"],
    ["Board temperature", "NTC 10 k at the driver", "control side (GNDI)"]], size=13, colw=[150, 200, 170])
image(s, "img/sch_ufl.png", [X0, Y0 + 285, 540, 120])
text(s, [X0 + 545, Y0 + 150, 355, 220], [
    "Back-to-back load test, closed loop on a TI TMS320F28379D",
    "Load board: no shunt ⇒ phase current from the HO 250-S, cell sharing from the DPT board",
    "No short-circuit protection on the boards",
], 15)

s = slide("Power stage schematics (generated, identical to the PCBs)", 9)
image(s, "img/sch_power.png", [X0, Y0, W, 175])
image(s, "img/sch_power_load.png", [X0, Y0 + 185, W, 175])
note(s, "Top: DPT board (UFCS in each LS source). Bottom: load-test board (LS source to DC−). "
        "make_kicad_sch_revb.py; check_sch_vs_pcb.py: 0 problems on both")

# ================================================================== 10 three-phase bus
s = slide("Three legs on one 75 V bus: what the bus must do", 10, "10  Three-phase DC bus")
text(s, [X0, Y0, 520, 370], [
    "The switching edge closes on each board (bypass + bank); the bus only carries the f_{sw} ripple between the leg banks",
    "Sharing needs ωL_{bus} ≪ 1/(ωC): at 50 kHz and ≈ 127 µF eff. per leg L ≪ 80 nH ⇒ **target ≤ 5 nH leg to leg**",
    "DC: 250 A stack current enters the level, 83 A per leg",
    "All-MLCC banks joined by nH copper form a high-Q resonator ⇒ damping footprints",
], 14)
bx, by = X0 + 545, Y0 + 20
for k in range(3):
    rect(s, [bx + k * 120, by, 105, 90], "leg %s\n(phase %s)\nload board" % ("abc"[k], "abc"[k]), "kth10", "kth", 10)
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
    ["Stack contact", "2 × M6 lug pads at the centre leg"],
    ["Insulation", "frame holes with 8 mm Cu keep-out (1200 V)"]], size=12, colw=[110, 320])
text(s, [X0 + 455, Y0 + 155, 445, 220], [
    "Q3D (step 11): leg-to-leg loop **%s nH** at 1 MHz (a–b), DC busbar loss **%s W**" % (
        q("level", "bus_ac", "L_leg12_nH"), q("level", "dc", "P_bus_W", fmt="%.1f")),
    "Damping caps (100 V hybrid polymer) as DNP footprints; nylon standoffs at the leg corner holes",
    "Generated: scripts/make_kicad_busbar.py, DRC clean; fab files in hardware/spb-busbar/fab",
], 15)

s = slide("One 75 V level in 3D: busbar + three load-test legs", 10)
image(s, "img/r3d_level_iso.png", [X0, Y0, W, 330])
text(s, [X0, Y0 + 335, W, 60], [
    "Legs a, b, c (pitch 94.5 mm, 5 mm gaps) stand on their REDCUBE DC terminals (6.5 mm) on the PCB busbar; M4 × 8 "
    "screws from below; AC bar of each leg through its LEM HO 250-S; heatsinks stay inside each board outline",
], 14)

s = slide("Level assembly: busbar side and DC connection", 10)
image(s, "img/r3d_level_back.png", [X0, Y0, 445, 250])
image(s, "img/r3d_level_detail.png", [X0 + 455, Y0, 445, 250])
image(s, "img/r3d_level_side.png", [X0, Y0 + 260, 445, 130])
text(s, [X0 + 455, Y0 + 260, 445, 130], [
    "Right: middle leg on the bus: REDCUBE + M4, nylon standoffs, M6 stack lugs, DNP damping caps, level header",
    "Left bottom: side view (z stack): busbar top z = 0, leg bottom 6.5 mm, heatsink top 52.8 mm",
], 14)

s = slide("Mechanics: heatsink length fixed by the leg pitch", 10)
text(s, [X0, Y0, 520, 370], [
    "LAM 4 (100 mm) + fan = 110 mm: wider than the 89.5 mm board ⇒ with 5 mm gaps the heatsinks of neighbouring legs "
    "would overlap by ≈ 15 mm",
    "**LAM 4 K 50 12** (Farnell 4708974, 0.65 K/W): 50 mm tube + fan centred over the cells (x −35 … 25 mm), inside the "
    "board outline",
    "Al spreader 89.5 × 12.8 × 3 mm carries the outer cells (x ±33 mm) to the tube; ≈ 18 W FET loss per leg ⇒ ≈ 12 K "
    "heatsink rise",
    "Spreader underside 1.68 mm, top 4.68 mm: clears the 2.8 mm bank and all bypass parts",
], 15)
image(s, "img/r3d_load.png", [X0 + 540, Y0, 360, 260])
decision(s, "Load board heatsink: LAM 4 K 50 12, centred; leg pitch stays 94.5 mm (busbar unchanged)")

s = slide("Full inverter: 16 levels on one 1200 V stack", 10)
image(s, "img/r3d_stack.png", [X0, Y0, 300, 400])
text(s, [X0 + 320, Y0, 580, 380], [
    "16 identical levels (75 V each) stacked in z, pitch 72 mm ⇒ ≈ 1.15 m",
    "DC+ lug of level k ↔ DC− lug of level k + 1 by a Cu braid (8 × 1.5 mm in the model); stack ends = 1200 V DC+ / DC−",
    "Each level: 3 legs = one three-phase winding set; AC bars + HO 250-S per leg",
    "Every level floats up to 1200 V above the frame: insulating standoffs with 8 mm Cu keep-out on the busbar",
    "Assembly STEP: hardware/assembly/spb-level-assembly.step (1 level), spb-stack-assembly.step (16 levels), "
    "scripts/make_assembly_step.py (OpenCascade)",
], 15)
note(s, "Stack direction and frame are illustrative: the machine-side layout (winding terminals) sets the final arrangement.")

# ================================================================== 11 verification (Q3D)
s = slide("Fast Q3D set on the final boards", 11, "11  Verification (Q3D)")
table(s, [X0, Y0, W, 230], [
    ["Model", "Region", "Solve", "Gives", "Run time"],
    ["loop (per board)", "cell band y −4.6 … 20.6 mm, AC split per cell", "AC 100 MHz",
     "commutation loop per cell", "%s / %s min" % (q("loop_dpt", fmt="%.0f", d=DUR), q("loop_load", fmt="%.0f", d=DUR))],
    ["full board", "whole board, all terminals", "DC R only", "current sharing, copper loss",
     "%s / %s min" % (q("dc_dpt", fmt="%.0f", d=DUR), q("dc_load", fmt="%.0f", d=DUR))],
    ["bank", "DC terminals + bank + bypass (y −25 … 4.3 mm)", "AC 1 MHz", "leg DC-link port, L_{b} bypass → bank",
     "%s min" % q("bank", fmt="%.0f", d=DUR)],
    ["lx", "cells + AC columns + AC bus, no bank / terminals", "AC 100 MHz", "L_{x} between the driver pairs",
     "%s / %s min" % (q("lx_dpt", fmt="%.0f", d=DUR), q("lx_load", fmt="%.0f", d=DUR))],
    ["busbar", "PCB busbar, stitching vias every 2nd", "DC + AC 1 MHz, 2 %", "leg-to-leg loop, DC distribution",
     "%s min" % q("bus", fmt="%.0f", d=DUR)],
    ["three-phase level", "3 × bank model + busbar matrices", "network (MNA)", "ripple sharing, |Z|, terminal currents",
     "seconds"]], size=12, colw=[120, 270, 120, 270, 120])
text(s, [X0, Y0 + 290, W, 120], [
    "Instead of one large model (> 3 h, not converged): small models, each solved only for what it is used for; DC is "
    "solved for R only (the DC-inductance solve alone ran > 19 h on the first attempt)",
    "Run: simulation/bb_q3d/run_bb_q3d_final.cmd (KTH licence) → final_post.py → reports/slides/data/final_numbers.json",
    "Run times: DPT / load board",
], 14)

s = slide("Q3D: commutation loop per cell, final boards", 11)
if HAVE_LOOP:
    image(s, "img/final_loop_cells.png", [X0, Y0, 540, 285])
table(s, [X0 + 555, Y0, 345, 170], [
    ["Loop per cell (nH)", "DPT", "load test"],
    ["cell 1 / 2", "%s / %s" % (q("dpt", "loop", "all_switching", "cell1", fmt="%.3f"),
                                q("dpt", "loop", "all_switching", "cell2", fmt="%.3f")),
     "%s / %s" % (q("load", "loop", "all_switching", "cell1", fmt="%.3f"),
                  q("load", "loop", "all_switching", "cell2", fmt="%.3f"))],
    ["cell 3 / 4", "%s / %s" % (q("dpt", "loop", "all_switching", "cell3", fmt="%.3f"),
                                q("dpt", "loop", "all_switching", "cell4", fmt="%.3f")),
     "%s / %s" % (q("load", "loop", "all_switching", "cell3", fmt="%.3f"),
                  q("load", "loop", "all_switching", "cell4", fmt="%.3f"))],
    ["**mean**", "**%s**" % q("dpt", "loop", "mean_nH", fmt="%.2f"), "**%s**" % q("load", "loop", "mean_nH", fmt="%.2f")],
    ["v̂_{DS} at 30 A/ns", "!!%s V!!" % q("dpt", "loop", "overshoot_30Apns_V", fmt="%.0f"),
     "%s V" % q("load", "loop", "overshoot_30Apns_V", fmt="%.0f")]], size=13, colw=[135, 105, 105])
_lm = FQ.get("dpt", {}).get("loop", {}).get("mean_nH")
text(s, [X0 + 555, Y0 + 180, 345, 200], [
    "All four LS switching together; HS shorted, bypass as its ESL, UFCS 120 pH",
    "Cells within %s %% (DPT) and %s %% (load): left/right symmetric by layout (power vias pruned in mirror pairs)" % (
        q("dpt", fmt="%.0f", d={"dpt": (max(lcells("dpt")) / min(lcells("dpt")) - 1) * 100} if HAVE_LOOP else {}),
        q("load", fmt="%.0f", d={"load": (max(lcells("load")) / min(lcells("load")) - 1) * 100} if HAVE_LOOP else {})),
    ("DPT ≤ 90 V: turn-on ≤ **%.0f A/ns**" % (15.0 / _lm)) if _lm else "DPT di/dt limit: (pending)",
], 14)

# cell-to-cell coupling and gate loops (loop_post.py / gate_post.py), gate drive from the extracted network (SPICE)
_GS = json.load(open(os.path.join(ROOT, "simulation", "bb_q3d", "results", "gate_summary_dpt.json")))
_QS = json.load(open(os.path.join(SL, "data", "q3d_spice_numbers.json")))
shutil.copy(os.path.join(ROOT, "reports", "pcb-rules", "figures", "dpt_gate_layout_block1.png"),
            os.path.join(IMG, "gate_layout_block1.png"))
_mc = FQ["dpt"]["loop"]["mutual_cell_nH"]
_kc = FQ["dpt"]["loop"]["coupling_k"]
_g0 = {k_: v_["esl0.0"] for k_, v_ in _GS["gate_loop_nH"].items()}
_sp = _GS["split_nH"]["esl0.0"]
_cmax = max(abs(v_) for st_ in _GS["coupling_pH"].values() for v_ in st_["both_cells"].values())
_vmax = max(abs(v_) for st_ in _GS["v_gk_at_30Apns_V"].values() for v_ in st_.values())
s = slide("Q3D: coupling between the cells and the gate loops (DPT board)", 11)
table(s, [X0, Y0, 400, 140], [["M (pH), k", "cell 2", "cell 3", "cell 4"]] + [
    ["cell %d" % i] + [("%.0f, %.3f" % (1000 * _mc["cell%d" % i]["cell%d" % j], _kc["cell%d" % i]["cell%d" % j]))
                       if j > i else "" for j in (2, 3, 4)] for i in (1, 2, 3)], size=12, colw=[85, 105, 105, 105])
table(s, [X0, Y0 + 150, 400, 150], [
    ["Gate loop (nH, copper)", "HS Q1 / Q2", "LS Q3 / Q4"],
    ["one device driven", "%.2f / %.2f" % (_g0["Q1"]["on"], _g0["Q2"]["on"]),
     "%.2f / %.2f" % (_g0["Q3"]["on"], _g0["Q4"]["on"])],
    ["pair driven (operation)", "%.1f / %.1f" % (_g0["Q1"]["on_pair_driven"], _g0["Q2"]["on_pair_driven"]),
     "%.1f / %.1f" % (_g0["Q3"]["on_pair_driven"], _g0["Q4"]["on_pair_driven"])],
    ["branch / shared star-driver", "%.1f / %.1f" % (_sp["Q1"]["branch"], _sp["Q1"]["common_on"]),
     "%.1f / %.1f" % (_sp["Q3"]["branch"], _sp["Q3"]["common_on"])],
    ["gate-power coupling, both cells", "max %.0f pH" % _cmax, "max %.2f V at 30 A/ns" % _vmax]],
    size=12, colw=[170, 115, 115])
image(s, "img/gate_layout_block1.png", [X0 + 410, Y0, 500, 310])
text(s, [X0, Y0 + 310, W, 95], [
    "Cells: at most %.0f pH between neighbours (k ≤ %.3f) ⇒ each cell commutates through its own loop" % (
        1000 * max(_mc[i][j] for i in _mc for j in _mc[i] if i != j),
        max(_kc[i][j] for i in _kc for j in _kc[i] if i != j)),
    "Gate: Kelvin return on the adjacent layer from every gate pad to the driver caps; Q1 = Q2, Q3 = Q4 within 0.3 %, "
    "block 2 an identical copy ⇒ all four paralleled devices equal; but ≈ 10× the 1.7 nH design value (driver behind "
    "the barrier)",
], 13)

s = slide("Gate drive from the extracted gate network (SPICE, DPT board, 75 V, 322 A)", 11)
_rows = [["Case", "R_{g,on}", "off", "v̂_{DS} HS", "E_{on} / E_{off} (4 cells)", "di/dt on", "bump, held-off gate"]]
for k_, lab_ in (("dpt_lumpgate", "lumped 1.7 nH gate, R_{ON} 1.5 Ω"), ("dpt_rg2.5", "extracted, R_{ON} 1.0 Ω"),
                 ("dpt", "**extracted, R_{ON} 1.5 Ω (board)**")):
    c_ = _QS.get(k_)
    if c_:
        _rows.append([lab_, "%.1f Ω" % c_["RGON"], "−1.9 V", "%.1f V" % c_["VHpk_max"],
                      "%.0f / %.0f µJ" % (c_["Eon_tot_uJ"], c_["Eoff_tot_uJ"]),
                      "%.0f A/ns" % (sum(x_["didt_on"] for x_ in c_["cells"]) / 4),
                      "%.2f … %.2f V" % (min(x_["bump"] for x_ in c_["cells"]), max(x_["bump"] for x_ in c_["cells"]))])
table(s, [X0, Y0, W, 140], _rows, size=12, colw=[250, 80, 60, 95, 160, 90, 175])
text(s, [X0, Y0 + 155, W, 250], [
    "Extracted gate network: Q3D copper + 0.4 nH per 0603 resistor body + 1 nH D_{OFF}; UFCS 120 pH as its own inductor",
    "The larger gate loop **speeds up** the turn-on ⇒ HS overshoot ≈ 75 V + 0.65 nH × di/dt: R_{ON} 1.0 Ω gives 105 V",
    "−1.9 V off: bump of the held-off gate ≤ −0.5 V (≥ 1.3 V below V_{th,min} 0.8 V); with 0 V off it was +1.2 … +1.4 V",
    "Off-state ringing ≈ −3.4 V against the −4 V limit (EPC2361) ⇒ no larger negative bias",
    "Turn-on of the four cells within 0.2 %; turn-off current inner vs outer cells ±1.5 % (power side)",
], 14)
decision(s, "DPT: R_{ON} 1.5 Ω (R_{g,on} 3.5 Ω), V_{ISO} 7 V (−1.9 / +5.1 V); next revision: driver stage next to each pair")

s = slide("Q3D model of the cell band (fast loop model)", 11)
image(s, "img/q3d_loop_dpt.png", [X0, Y0, 450, 300])
image(s, "img/q3d_loop_load.png", [X0 + 460, Y0, 450, 300])
label(s, [X0, Y0 + 300, 450, 20], "DPT board: LS source (green) to the UFCS land", 13, "gray", False, "center")
label(s, [X0 + 460, Y0 + 300, 450, 20], "load-test board: LS source straight to DC−", 13, "gray", False, "center")
text(s, [X0, Y0 + 330, W, 75], [
    "Geometry exported from the routed KiCad boards (revb_export.py): copper per net and layer with clearance holes, "
    "vias with their layer span (blind L1–L2 on the load board), FET and bypass terminal pads; z stretched 4×",
], 14)

s = slide("Q3D: static current sharing and copper loss", 11)
rows = [["Board, path (DC)", "R total (mΩ)", "R copper (mΩ)", "share cell 1 / 2 / 3 / 4", "max/min"]]
for b, bl in (("dpt", "DPT"), ("load", "load")):
    for p, lab in (("HS", "DC+ → HS FETs → AC"), ("LS", "AC → LS FETs%s → DC−" % (" → shunts" if b == "dpt" else ""))):
        d_ = FQ.get(b, {}).get("dc", {}).get(p)
        rows.append(["%s: %s" % (bl, lab)] + ([("%.2f" % d_["R_total_mOhm"]), ("%.2f" % d_["R_copper_mOhm"]),
                                                 " / ".join("%.0f %%" % (100 * x) for x in d_["share"]),
                                                 "%.2f" % (1 + d_["imbalance_pct"] / 100)] if d_ else ["–"] * 4))
table(s, [X0, Y0, W, 150], rows, size=13, colw=[260, 110, 120, 290, 120])
text(s, [X0, Y0 + 165, W, 220], [
    "**Static sharing** = how the conduction (DC) current splits between the four parallel cells: set by each cell's copper "
    "path (DC terminals → cell → AC pad) plus R_{DS(on)}; dynamic sharing during the edges is set by the gate loops (step 7)",
    "Full-board DC model; FET 0.75 mΩ × 1.49 (100 °C), UFCS 1 mΩ; DC terminals as one pair, AC at the M6 bolt pad",
    "Board copper loss at 228 A_{rms}: **%s W** (DPT, + %s W in the shunts) / **%s W** (load board)" % (
        q("dpt", "dc", "P_copper_W", fmt="%.0f"), q("dpt", "dc", "P_shunts_W", fmt="%.1f"),
        q("load", "dc", "P_copper_W", fmt="%.0f")),
    "Hand-over inductance bypass → bank L_{b} = %s (bank model, 1 MHz) ⇒ used for the bypass sizing (step 6)" % (
        ("%.2f–%.2f nH" % (LB_LO, LB_HI)) if LB else "(pending)"),
], 15)

s = slide("Q3D: three load-test legs on the PCB busbar", 11)
lv = FQ.get("level", {})
rows = [["Quantity", "Value"],
        ["Leg-to-leg loop a–b / a–c, 1 MHz", "%s / %s nH" % (q("bus_ac", "L_leg12_nH", d=lv), q("bus_ac", "L_leg13_nH", d=lv))],
        ["Leg-to-leg loop a–b / a–c, DC", "%s / %s nH" % (q("bus_dc", "L_leg12_nH", d=lv), q("bus_dc", "L_leg13_nH", d=lv))],
        ["Ripple of leg a at 50 kHz from banks a / b / c", " / ".join(
            "%.0f %%" % (100 * x) for x in lv["ripple_50kHz"]["share_of_leg"]) if "ripple_50kHz" in lv else "(pending)"],
        ["Busbar DC loss (250 A in, 3 × 83 A)", "%s W" % q("dc", "P_bus_W", fmt="%.1f", d=lv)],
        ["Highest REDCUBE terminal current", "%s A" % q("dc", "I_terminal_max_A", fmt="%.0f", d=lv)]]
table(s, [X0, Y0, 470, 240], rows, size=13, colw=[300, 170])
if HAVE_SWEEP:
    image(s, "img/final_sweep.png", [X0 + 485, Y0, 415, 240])
text(s, [X0, Y0 + 255, W, 120], [
    "Network: Q3D bank-model matrices of three load-test legs (cells draw at their bypass; MLCCs with ESR/ESL, C at 75 V) "
    "+ busbar (DC below 1 MHz, AC above); peaks in |Z| = inter-leg resonance",
    "Target ≤ 5 nH leg to leg (step 10)",
], 15)

s = slide("Main findings on the final boards", 11)
table(s, [X0, Y0, W, 230], [
    ["Quantity", "DPT board", "Load-test board", "Consequence"],
    ["Loop per cell", "%s nH" % q("dpt", "loop", "mean_nH"), "%s nH" % q("load", "loop", "mean_nH"),
     "DPT: limit di/dt; load: 30 A/ns ok"],
    ["Static sharing, max/min (HS / LS)",
     "%s / %s" % (q("dpt", "dc", "HS", "imbalance_pct", fmt="+%.0f %%"), q("dpt", "dc", "LS", "imbalance_pct", fmt="+%.0f %%")),
     "%s / %s" % (q("load", "dc", "HS", "imbalance_pct", fmt="+%.0f %%"), q("load", "dc", "LS", "imbalance_pct", fmt="+%.0f %%")),
     "verify with the UFCS per cell"],
    ["Board copper loss at 228 A_{rms}", "%s W" % q("dpt", "dc", "P_copper_W", fmt="%.0f"),
     "%s W" % q("load", "dc", "P_copper_W", fmt="%.0f"), "heats the board, not the FETs"],
    ["L_{x} between driver pairs (HS / LS)", "%s / %s nH" % (q("dpt", "lx", "HS"), q("dpt", "lx", "LS")),
     "%s / %s nH" % (q("load", "lx", "HS"), q("load", "lx", "LS")), "skew → ΔI = V_{m}Δt / L_{x}"],
    ["Bus leg-to-leg loop (1 MHz)", "–", "%s nH" % q("level", "bus_ac", "L_leg12_nH"), "target ≤ 5 nH"]],
      size=13, colw=[230, 180, 180, 310])
image(s, "img/q3d_full_load.png", [X0 + 200, Y0 + 205, 510, 250])
note(s, "All values from the fast Q3D set on the final layouts (run_bb_q3d_final.cmd, final_post.py).")

# ================================================================== 12 boards, status
s = slide("Fabrication files", 12, "12  Rev B boards")
table(s, [X0, Y0, W, 230], [
    ["Board", "Fab set (hardware/<board>/fab)", "Notes for the fab house"],
    ["spb-bb-revb-dpt", "Gerber zip, drill, pos, BOM, STEP, assembly + schematic PDF",
     "2 oz all layers, 0.1 mm prepreg, via-in-pad filled + capped"],
    ["spb-bb-revb-load", "same", "+ blind vias L1–L2 (0.25 mm) filled + capped"],
    ["spb-busbar", "Gerber zip, drill, pos, BOM, STEP", "2 oz all layers (JLC3313), bolt pads without mask"],
    ["assembly", "spb-level-assembly.step, spb-stack-assembly.step", "mechanics / frame design"]],
      size=13, colw=[160, 380, 360])
text(s, [X0, Y0 + 140, W, 140], [
    "Generated: make_kicad_bb_revb.py (BOARD=dpt | load), make_kicad_sch_revb.py, make_kicad_busbar.py, "
    "make_3d_models_revb.py, make_fab_outputs_revb.py, make_assembly_step.py, render_3d.py",
    "Mechanical items (screws, spreader, gap pads, heatsink, lugs) are listed at the end of each BOM",
], 14)
image(s, "img/revb_dpt_top.png", [X0, Y0 + 215, 220, 190])
image(s, "img/revb_load_top.png", [X0 + 230, Y0 + 215, 220, 190])
image(s, "img/busbar_top.png", [X0 + 460, Y0 + 215, 450, 190])

s = slide("Status and next steps", 12, "Status")
table(s, [X0, Y0, 520, 330], [
    ["Item", "Status"],
    ["DC link: 20 × 22 µF 2220 + 10 × 1 µF per cell", "in both layouts"],
    ["DPT board (UFCS, no heatsink)", "DRC 0 / 0 / 0, schematic = PCB"],
    ["Load-test board (no shunt, LAM 4 K 50)", "DRC 0 / 0 / 0, schematic = PCB"],
    ["PCB busbar", "DRC clean, fab files"],
    ["Fast Q3D: loop, DC, L_{x}, busbar, level", "done (this deck)" if FQ.get("level") else "running"],
    ["3D models, board + assembly STEP", "done"],
    ["Fab outputs + BOMs", "done"],
    ["DPT and three-phase load test", "after assembly"]], size=13, colw=[300, 220])
text(s, [X0 + 545, Y0, 355, 370], [
    "Order: DPT board first (switching energies, per-cell current, overshoot vs di/dt), then 3 load boards + busbar",
    "Mechanics: spreader drawing, frame and stack insulation from the assembly STEP",
    "Decide after measurement: bank depopulation, damping caps, busbar copper weight",
    "Machine: L_{σ}, cos φ and the final f_{sw}",
], 15)

s = slide("Thank you")
s["kind"] = "end"

json.dump(dict(steps=STEPS, slides=SLIDES), open(os.path.join(OUT, "deck.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("slides", len(SLIDES), "final Q3D numbers:", sorted(FQ))

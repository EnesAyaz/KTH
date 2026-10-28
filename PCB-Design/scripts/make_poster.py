"""
A0 poster, Moore4Power General Assembly (Nov 2026): SPB review + iterative GaN building-block design.
Layout and content follow Enes's hand-edited version of 2026-10-28; this script redraws it in one style.

    python scripts/make_poster.py      (LossCalculation venv: matplotlib, PIL)
      -> reports/poster/spb_project_poster_A0.svg, .pdf, .png (150 dpi preview)

Units: mm (viewBox 841 x 1189). Everything is vector except the two 3D renders and the KTH logo:
  - review figures 3 and 16 are imported from their PDFs (Inkscape, glyphs as paths);
  - line charts are matplotlib SVG (text kept as text, Segoe UI), bar charts are drawn here;
  - numbers come from the result files (reports/slides/data/*.json, simulation/bb_q3d/results).
Type scale: section title 8.6, panel title 6.8, body 6.4, chart text 4.6 (13 pt), caption 5.6.
"""
import base64
import io
import json
import os
import re
import subprocess
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KTH = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "reports", "poster")
IMG = os.path.join(OUT, "img")
SLI = os.path.join(ROOT, "reports", "slides", "revb_pptx", "img")
DATA = os.path.join(ROOT, "reports", "slides", "data")
REV = os.path.join(KTH, "Review-Paper-SPB", "Figures", "Exported")
INK = r"C:\Program Files\Inkscape\bin\inkscape.exe"

RF = json.load(open(os.path.join(DATA, "revb_flow_numbers.json")))
FQ = json.load(open(os.path.join(DATA, "final_numbers.json")))
QS = json.load(open(os.path.join(DATA, "q3d_spice_numbers.json")))
GS = json.load(open(os.path.join(ROOT, "simulation", "bb_q3d", "results", "gate_summary_dpt.json")))

NAVY, TEAL, BG, TXT, MUTED, CARD, LINE = "#0b3a6e", "#16968a", "#eef2f5", "#1d2b3a", "#66727c", "#ffffff", "#c9d3db"
TINT, AMBER, RED, BLUE, GREY = "#e3f2ef", "#e39b2d", "#c8423b", "#3a6ea5", "#b9c2ca"
OKF, BADF = "#e3f2ef", "#fbe9e7"
FONT = "'Segoe UI',Arial,sans-serif"
W, H, M, G = 841, 1189, 30, 12
S = []
B, P, C, T = 6.4, 6.8, 4.6, 8.6          # body, panel title, chart text, section title


# ------------------------------------------------------------------------------------------------ primitives
def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rich(t):
    """V_{dc} -> subscript, x^{2} -> superscript, **bold**."""
    t = esc(t)
    t = re.sub(r"_\{([^}]*)\}", r'<tspan style="font-size:70%;baseline-shift:sub">\1</tspan>', t)
    t = re.sub(r"\^\{([^}]*)\}", r'<tspan style="font-size:70%;baseline-shift:super">\1</tspan>', t)
    return re.sub(r"\*\*(.*?)\*\*", r'<tspan style="font-weight:700">\1</tspan>', t)


def plain(t):
    return re.sub(r"[_^]\{([^}]*)\}", r"\1", t).replace("**", "")


def wrap(t, width, size):
    """Greedy wrap on the plain-text width (Segoe UI ~0.52 em per character on average)."""
    lines, cur = [], ""
    for word in t.split(" "):
        cand = (cur + " " + word).strip()
        if len(plain(cand)) * 0.52 * size > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = cand
    return lines + [cur]


def text(x, y, t, size=B, color=TXT, weight=400, anchor="start", width=None, lh=1.3):
    lines = wrap(t, width, size) if width else [t]
    for i, ln in enumerate(lines):
        S.append('<text x="%.2f" y="%.2f" style="font-family:%s;font-size:%.2fpx;fill:%s;font-weight:%d;'
                 'text-anchor:%s">%s</text>' % (x, y + i * size * lh, FONT, size, color, weight, anchor, rich(ln)))
    return y + (len(lines) - 1) * size * lh


def rect(x, y, w, h, fill, rx=0, stroke="none", sw=0.0, dash=None):
    S.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" style="fill:%s;stroke:%s;stroke-width:%.2f%s"/>'
             % (x, y, w, h, rx, fill, stroke, sw, ";stroke-dasharray:%s" % dash if dash else ""))


def line(x1, y1, x2, y2, color, sw=0.4, dash=None):
    S.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" style="stroke:%s;stroke-width:%.2f%s"/>'
             % (x1, y1, x2, y2, color, sw, ";stroke-dasharray:%s" % dash if dash else ""))


def circle(cx, cy, r, fill):
    S.append('<circle cx="%.2f" cy="%.2f" r="%.2f" style="fill:%s"/>' % (cx, cy, r, fill))


def bullets(x, y, items, width, size=B, gap=2.4):
    for it in items:
        circle(x + 1.2, y - size * 0.33, 0.95, TEAL)
        y = text(x + 4.5, y, it, size, width=width - 4.5) + size * 1.3 + gap
    return y


def section(x, y, w, h, num, title):
    rect(x, y, w, h, CARD, rx=3, stroke=LINE, sw=0.4)
    rect(x, y, w, 15, NAVY, rx=3)
    rect(x, y + 8, w, 7, NAVY)
    circle(x + 9, y + 7.5, 4.6, TEAL)
    text(x + 9, y + 10.1, num, 7.0, "#ffffff", 700, "middle")
    text(x + 17, y + 10.4, title, T, "#ffffff", 600)
    return y + 15


def ptitle(x, y, t, anchor="start"):
    return text(x, y, t, P, NAVY, 700, anchor)


def caption(x, y, t, anchor="middle", width=None):
    return text(x, y, t, 5.6, MUTED, anchor=anchor, width=width)


def note_box(x, y, w, h):
    rect(x, y, w, h, TINT, rx=2)
    rect(x, y, 1.8, h, TEAL)


def autocrop(im, pad=4):
    bg = Image.new("RGB", im.size, (255, 255, 255))
    box = ImageChops.difference(im.convert("RGB"), bg).point(lambda v: 255 if v > 12 else 0).getbbox()
    l, t, r, b = box
    return im.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, im.size[0]), min(b + pad, im.size[1])))


def image(im, x, y, w, h, fmt="JPEG"):
    """Raster scaled to fit (w x h), centred; returns the drawn box."""
    k = min(w / im.width, h / im.height)
    dw, dh = im.width * k, im.height * k
    buf = io.BytesIO()
    im.save(buf, fmt, **({"quality": 92} if fmt == "JPEG" else {"optimize": True}))
    dx, dy = x + (w - dw) / 2, y + (h - dh) / 2
    S.append('<image x="%.2f" y="%.2f" width="%.2f" height="%.2f" preserveAspectRatio="xMidYMid meet" '
             'xlink:href="data:image/%s;base64,%s"/>' % (dx, dy, dw, dh, fmt.lower(), base64.b64encode(buf.getvalue()).decode()))
    print("  raster %4d px over %5.1f mm = %3.0f dpi" % (im.width, dw, im.width / (dw / 25.4)))
    return dx, dy, dw, dh


_n = [0]


def nested(svg, x, y, w, h):
    """Place an SVG document (string) in the box; ids are prefixed so several documents can coexist."""
    _n[0] += 1
    p = "e%d_" % _n[0]
    svg = svg[svg.index("<svg"):]
    svg = re.sub(r"<style.*?</style>", "", svg, flags=re.S)
    svg = re.sub(r"<metadata.*?</metadata>", "", svg, flags=re.S)
    svg = re.sub(r'\bid="([^"]+)"', r'id="%s\1"' % p, svg)
    svg = re.sub(r"url\(#([^)]+)\)", r"url(#%s\1)" % p, svg)
    svg = re.sub(r'href="#([^"]+)"', r'href="#%s\1"' % p, svg)
    head, rest = svg.split(">", 1)
    head = re.sub(r'\s(width|height|x|y|preserveAspectRatio)="[^"]*"', "", head)
    head += ' x="%.2f" y="%.2f" width="%.2f" height="%.2f" preserveAspectRatio="xMidYMid meet" overflow="visible"' % (x, y, w, h)
    S.append(head + ">" + rest)


def pdf_figure(name, x, y, w, h):
    """Review figure from its PDF as vector (glyphs drawn as paths); returns the drawn box."""
    with tempfile.TemporaryDirectory() as d:
        o = os.path.join(d, name + ".svg")
        subprocess.run([INK, os.path.join(REV, name + ".pdf"), "--pdf-font-strategy=draw-all", "--export-type=svg",
                        "--export-plain-svg", "--export-filename=" + o], capture_output=True)
        svg = open(o, encoding="utf-8").read()
    vw, vh = [float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups()]
    k = min(w / vw, h / vh)
    dw, dh = vw * k, vh * k
    nested(svg, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh)
    return x + (w - dw) / 2, y + (h - dh) / 2, dw, dh


plt.rcParams.update({"font.family": "Segoe UI", "font.size": 13, "svg.fonttype": "none", "axes.edgecolor": MUTED,
                     "axes.labelcolor": TXT, "xtick.color": TXT, "ytick.color": TXT, "axes.linewidth": 0.9,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#dfe5ea",
                     "grid.linewidth": 0.7, "lines.linewidth": 2.0, "legend.frameon": False, "legend.fontsize": 12})


def chart(w, h):
    fig, ax = plt.subplots(figsize=(w / 25.4, h / 25.4))
    return fig, ax


def place(fig, x, y, w, h):
    buf = io.StringIO()
    fig.savefig(buf, format="svg", transparent=True)
    plt.close(fig)
    nested(buf.getvalue(), x, y, w, h)


def hbars(x, y, rows, lw, bw, vmax, rowh=7.6, refs=()):
    """Horizontal bars: rows of (label, value, colour, value text); refs = [(value, colour, label)] dashed lines."""
    for i, (lab, v, col, vt) in enumerate(rows):
        yy = y + i * rowh
        text(x + lw - 2, yy + 3.4, lab, C, TXT, anchor="end")
        rect(x + lw, yy, max(bw * v / vmax, 0.8), 4.6, col)
        text(x + lw + bw * v / vmax + 1.5, yy + 3.6, vt, C, col, 700)
    for v, col, lab in refs:
        xx = x + lw + bw * v / vmax
        line(xx, y - 2, xx, y + len(rows) * rowh, col, 0.5, "1.2,1")
        text(xx, y + len(rows) * rowh + 4.2, lab, C - 0.4, col, anchor="middle")
    return y + len(rows) * rowh


def pill(x, y, w, ok, t):
    rect(x, y, w, 7, OKF if ok else BADF, rx=3.5, stroke=TEAL if ok else RED, sw=0.45)
    text(x + w / 2, y + 4.9, ("✓ " if ok else "✗ ") + t, C, TEAL if ok else RED, 700, "middle")


# ------------------------------------------------------------------------------------------------ page and header
rect(0, 0, W, H, BG)
rect(0, 0, W, 150, NAVY)
rect(0, 146, W, 4, TEAL)
image(Image.open(os.path.join(IMG, "kth_logo.png")), 24, 25, 86, 96, "PNG")
CX = 407.5
text(CX, 31, "Moore4Power General Assembly · November 2026", 7.5, "#cfe3ef", anchor="middle")
text(CX, 62, "Stacked Polyphase Bridge Traction Drives:", 23, "#ffffff", 600, "middle")
text(CX, 88, "Iterative GaN Building Block Design", 23, "#ffffff", 600, "middle")
text(CX, 110, "Enes Ayaz, Shahriar Sarmast Ghahfarokhi, Kevin Klarin, Staffan Norrga", 10, "#ffffff", 600, "middle")
text(CX, 125, "Department of Electric Power and Energy Systems, KTH Royal Institute of Technology, Stockholm, Sweden",
     7.5, "#cfe3ef", anchor="middle")
for i, lab in enumerate(("Cell N", "...", "Cell 2", "Cell 1")):          # stack icon
    yy = 22 + i * 27
    if lab == "...":
        text(728, yy + 14, "⋮", 12, "#cfe3ef", anchor="middle")
        continue
    rect(700, yy, 56, 20, "#16508f", rx=2, stroke="#9fc3e6", sw=0.5)
    text(728, yy + 8.5, lab, 6.5, "#ffffff", 600, "middle")
    text(728, yy + 16, "75 V · 3-phase", 5.6, "#cfe3ef", anchor="middle")
    line(756, yy + 10, 770, yy + 10, "#9fc3e6", 0.6)
    circle(774, yy + 10, 4, TEAL)
text(728, 136, "16 × 75 V = 1200 V", 6.2, "#cfe3ef", anchor="middle")

# ------------------------------------------------------------------------------------------------ KPI cards
NP = RF["npar"]["0.5nH"]
n4 = NP[3]
LOOP = {b: [FQ[b]["loop"]["all_switching"]["cell%d" % c] for c in range(1, 5)] for b in ("dpt", "load")}
KPI = [("1200 V", "dc link, 300 kW traction"), ("16 × 75 V", "series cells, own winding groups"),
       ("4 × GaN", "EPC2361 100 V devices per switch"), ("%.2f nH" % np.mean(LOOP["load"]), "commutation loop per cell"),
       ("%.2f %%" % (100 * n4["eta"]), "semiconductor efficiency"), ("2.85 %", "shared-bus dc ripple, 50 kHz")]
cw = (W - 2 * M - 5 * 10) / 6
for i, (v, d) in enumerate(KPI):
    x = M + i * (cw + 10)
    rect(x, 160, cw, 44, CARD, rx=3, stroke=LINE, sw=0.4)
    rect(x, 160, 2.2, 44, TEAL)
    text(x + 9, 181, v, 13, NAVY, 600)
    text(x + 9, 195, d, 5.9, MUTED)

# ------------------------------------------------------------------------------------------------ 1 concept
y1 = 216
cy = section(M, y1, W - 2 * M, 236, "1", "Concept: split the dc voltage, keep one machine")
ptitle(M + 110, cy + 12, "N-cell SPB", "middle")
fx, fy, fw, fh = pdf_figure("fig03", M + 8, cy + 18, 205, 168)
caption(fx + fw / 2, cy + 200, "Series dc links, one three-phase winding group per cell")
for frac, lab, col in ((0.215, "Module N", "#2f8f4e"), (0.545, "Module 2", "#e8822d"), (0.875, "Module 1", "#2f7fc1")):
    text(fx + fw + 22, fy + frac * fh + 2.5, lab, 7.0, col, 700, "middle")
mx = fx + fw + 46
ptitle(mx + 66, cy + 12, "Machine: N isolated winding sets", "middle")
frag = open(os.path.join(IMG, "machine_windings.svgfrag"), encoding="utf-8").read()
# fragment bbox in poster units (Inkscape query on the hand-edited poster): x 321.0, y 301.8, 129.1 x 130.3
k = 150 / 130.3
S.append('<g transform="translate(%.2f,%.2f) scale(%.4f) translate(-321.0,-301.8)">%s</g>' % (mx, cy + 24, k, frag))
cx1 = mx + 160
ptitle(cx1 + 95, cy + 12, "Device voltage class and cell count", "middle")
Ns = np.array([1, 2, 3, 4, 5, 8, 10, 12, 16, 20])
fig, ax = chart(190, 160)
ax.semilogy(Ns, 1200 / Ns, "o-", color=BLUE, ms=6)
ax.set_xlabel("cell count N")
ax.set_xticks([1, 4, 8, 12, 16, 20])
ax.set_ylabel("V$_{cell}$ = 1200 V / N", color=BLUE)
ax.set_yticks([50, 100, 200, 500, 1000])
ax.set_yticklabels(["50", "100", "200", "500", "1000"])
ax.axhline(100, color=RED, ls="--", lw=1.3)
ax.text(20.5, 104, "100 V class", color=RED, ha="right", va="bottom", fontsize=12)
ax.plot([16], [75], "o", color=TEAL, ms=11, zorder=5)
ax.annotate("N = 16: 75 V", (16, 75), (9.5, 58), color=TEAL, fontsize=13, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color=TEAL, lw=1.2))
a2 = ax.twinx()
a2.plot(Ns, 6 * Ns, "s--", color=AMBER, ms=5)
a2.set_ylabel("active switches 6N", color=AMBER)
a2.spines["right"].set_visible(True)
a2.grid(False)
fig.tight_layout(pad=0.3)
place(fig, cx1, cy + 18, 190, 160)
caption(cx1 + 95, cy + 200, "1200 V link: lower cell voltage, more switches")
px = cx1 + 200
note_box(px, cy + 6, W - M - 8 - px, 206)
bullets(px + 7, cy + 17, [
    "N two-level bridges in series on the dc side; each feeds its own three-phase winding group.",
    "V_{dc,k} ≈ V_{dc}/N: the device voltage class follows the cell, not the full link.",
    "All cells carry the same dc current; P_{ac} = ΣP_{k}, so cell voltages must be balanced actively.",
    "6N switches, N drivers and capacitors: complexity moves to the system.",
    "Rating with margin: V_{rated} ≥ k_{rel}(V_{dc,max}/N + ΔV_{imb} + ΔV_{sw}).",
    "N = 16 gives 75 V cells for 100 V GaN; the overshoot L·di/dt sets the usable margin.",
], W - M - 8 - px - 12, 6.9, 2.6)

# ------------------------------------------------------------------------------------------------ row 2
y2 = y1 + 236 + G
h2 = 252
w2 = (W - 2 * M - 2 * G) / 3
# 2 voltage class and single-cell screen
x = M
cy = section(x, y2, w2, h2, "2", "Voltage class, cell count, single cell")
pw, ph = (w2 - 20) / 2, 82
panels = [(x + 8, cy + 10), (x + 12 + pw, cy + 10), (x + 8, cy + 108), (x + 12 + pw, cy + 108)]
# (a) lowest D-FoM per voltage class (device survey of the design-flow slides)
(ax_, ay_) = panels[0]
ptitle(ax_, ay_, "(a) Lowest D-FoM per class (ps)")
DF = [("100", 1.35), ("200", 4.14), ("350", 6.88), ("650", 4.90)]
bx0, by0, bh0, bwid = ax_ + 8, ay_ + 66, 52, 18
line(bx0 - 2, by0, bx0 + 4 * (bwid + 4), by0, MUTED, 0.4)
for i, (v, f) in enumerate(DF):
    hh = bh0 * f / 7.0
    rect(bx0 + i * (bwid + 4), by0 - hh, bwid, hh, TEAL if i == 0 else GREY)
    text(bx0 + i * (bwid + 4) + bwid / 2, by0 - hh - 1.8, "%.2f" % f, C, TEAL if i == 0 else TXT, 700, "middle")
    text(bx0 + i * (bwid + 4) + bwid / 2, by0 + 5, v, C, TXT, anchor="middle")
text(bx0 + 2 * (bwid + 4), by0 + 11, "voltage class (V)", C, MUTED, anchor="middle")
# (b) cell voltage
(ax_, ay_) = panels[1]
ptitle(ax_, ay_, "(b) V_{cell} = 1200 V / N")
N2 = np.arange(12, 21)
fig, ax = chart(pw, ph - 6)
ax.plot(N2, 1200 / N2, "o-", color=TXT, ms=4)
ax.axhline(100, color=RED, ls="--", lw=1.2)
ax.axhline(90, color=MUTED, ls=":", lw=1.2)
ax.text(20, 101.5, "100 V rating", color=RED, ha="right", fontsize=11)
ax.text(20, 86, "90 V target", color=MUTED, ha="right", fontsize=11)
ax.plot([16], [75], "o", color=TEAL, ms=9, zorder=5)
ax.text(16.4, 78, "N = 16: 75 V", color=TEAL, fontsize=12, fontweight="bold")
ax.set_xlabel("cells N")
ax.set_ylim(55, 108)
fig.tight_layout(pad=0.2)
place(fig, ax_, ay_ + 3, pw, ph - 6)
# (c) peak V_DS, one device
(ax_, ay_) = panels[2]
ptitle(ax_, ay_, "(c) Peak V_{DS}, one device (V)")
fig, ax = chart(pw, ph - 6)
for L, col, ls in (("0.5nH", TXT, "-"), ("1nH", RED, "--")):
    d = RF["single"][L]
    ax.plot(d["I"], d["vpk"], ls, color=col, label=L.replace("nH", " nH"))
ax.axhline(90, color=MUTED, ls=":", lw=1.2)
ax.plot([80], [np.interp(80, RF["single"]["0.5nH"]["I"], RF["single"]["0.5nH"]["vpk"])], "o", color=TEAL, ms=9, zorder=5)
ax.text(84, 70, "80 A: n = 4", color=TEAL, fontsize=12, fontweight="bold")
ax.set_xlim(30, 170)
ax.set_ylim(60, 190)
ax.set_xlabel("current per device (A)")
ax.legend(loc="upper left", handlelength=1.4)
fig.tight_layout(pad=0.2)
place(fig, ax_, ay_ + 3, pw, ph - 6)
# (d) leg loss vs devices per switch
(ax_, ay_) = panels[3]
ptitle(ax_, ay_, "(d) Leg loss (W)")
fig, ax = chart(pw, ph - 6)
nn = [d_["n"] for d_ in NP[1:]]
ax.plot(nn, [d_["tot"] for d_ in NP[1:]], "-", color=TEAL, label="total")
ax.plot(nn, [d_["cond"] for d_ in NP[1:]], "--", color=TXT, label="conduction")
ax.plot([4], [n4["tot"]], "o", color=TEAL, ms=9, zorder=5)
ax.set_xlabel("devices per switch n")
ax.set_ylim(0, 45)
ax.legend(loc="upper right", handlelength=1.4)
fig.tight_layout(pad=0.2)
place(fig, ax_, ay_ + 3, pw, ph - 6)
yy = cy + 206
text(x + w2 / 2, yy, "Lower blocking voltage gives the best figure of merit (D-FoM).", B, TXT, anchor="middle", width=w2 - 16)
text(x + w2 / 2, yy + 13, "Four devices: %.0f W per leg, the knee of the loss curve" % n4["tot"], B, TEAL, 700, "middle",
     width=w2 - 16)

# 3 why four devices per switch
x = M + w2 + G
cy = section(x, y2, w2, h2, "3", "Why four devices per switch")
ptitle(x + 8, cy + 10, "(a) Leg loss at 228 A_{rms}, 50 kHz (W)")
sel = [d_ for d_ in NP if d_["n"] in (2, 3, 4, 6, 8)]
bx0, by0, bh0 = x + 20, cy + 104, 78
slot = (w2 - 30) / len(sel)
bw_ = slot * 0.58
line(bx0 - 4, by0, x + w2 - 8, by0, MUTED, 0.4)
for v in (0, 10, 20, 30, 40):
    yv = by0 - bh0 * v / 42
    if v:
        line(bx0 - 4, yv, x + w2 - 8, yv, "#dfe5ea", 0.3)
    text(bx0 - 6, yv + 1.6, str(v), C, MUTED, anchor="end")
for i, d_ in enumerate(sel):
    cx_ = bx0 + i * slot + slot / 2 - 2
    y_ = by0
    for key, col in (("cond", BLUE), ("sw", AMBER), ("dg", GREY)):
        v = d_["dead"] + d_["gate"] if key == "dg" else d_[key]
        hh = bh0 * v / 42
        rect(cx_ - bw_ / 2, y_ - hh, bw_, hh, col)
        y_ -= hh
    hl = d_["n"] == 4
    text(cx_, y_ - 2, "%.1f" % d_["tot"], C, TEAL if hl else TXT, 700, "middle")
    text(cx_, by0 + 6, "n = %d" % d_["n"], C + 0.2, TEAL if hl else TXT, 700, "middle")
    text(cx_, by0 + 11.5, "%.2f %%" % (100 * d_["eta"]), C - 0.3, MUTED, anchor="middle")
    if hl:
        rect(cx_ - slot / 2 + 1, cy + 18, slot - 2, 153, "none", rx=3, stroke=TEAL, sw=0.7)
lx = x + w2 - 64
for j, (lab, col) in enumerate((("conduction", BLUE), ("switching", AMBER), ("dead time, gate", GREY))):
    rect(lx, cy + 20 + j * 6.5, 4, 4, col)
    text(lx + 6, cy + 23.6 + j * 6.5, lab, C, TXT)
ptitle(x + 8, cy + 136, "(b) Screens")
for r_, (lab, key, lim, unit) in enumerate((("T_{j}", "tj", 125, "°C"), ("V_{DS}", "vpk", 90, "V"))):
    yy = cy + 143 + r_ * 11
    text(x + 10, yy + 5, lab, B, TXT, 700)
    for i, d_ in enumerate(sel):
        cx_ = bx0 + i * slot + slot / 2 - 2
        pill(cx_ - slot * 0.42, yy, slot * 0.84, d_[key] <= lim, "%.0f %s" % (d_[key], unit))
text(x + w2 / 2, cy + 180, "Limits: T_{j} ≤ 125 °C, V_{DS} ≤ 90 V at 0.5 nH.", B, TXT, anchor="middle")
text(x + w2 / 2, cy + 193, "n = 4 is the smallest count that passes both.", B, TEAL, 700, "middle")
note_box(x + 8, cy + 202, w2 - 16, 29)
bullets(x + 15, cy + 211, ["n = 4: T_{j} %.0f °C, %.2f W per device, %d driver channels per leg" % (
    n4["tj"], n4["pdev"], 8), "1 nH instead of 0.5 nH: %.0f V peak, still below the rating" % RF["npar"]["1nH"][3]["vpk"]],
    w2 - 30, B - 0.3, 1.2)

# 4 extracted parasitics
x = M + 2 * (w2 + G)
cy = section(x, y2, w2, h2, "4", "Extracted parasitics (Ansys Q3D)")
ptitle(x + 8, cy + 10, "Commutation loop per cell (nH)")
bx0, by0, bh0 = x + 18, cy + 74, 50
gw = 30
line(bx0 - 4, by0, bx0 + 4 * gw + 4, by0, MUTED, 0.4)
for v in (0.2, 0.4, 0.6):
    line(bx0 - 4, by0 - bh0 * v / 0.7, bx0 + 4 * gw + 4, by0 - bh0 * v / 0.7, "#dfe5ea", 0.3)
    text(bx0 - 6, by0 - bh0 * v / 0.7 + 1.6, "%.1f" % v, C, MUTED, anchor="end")
yd = by0 - bh0 * 0.5 / 0.7
line(bx0 - 4, yd, bx0 + 4 * gw + 4, yd, "#2CA02C", 0.5, "1.5,1")
for c in range(4):
    for k_, (b_, col) in enumerate((("dpt", RED), ("load", BLUE))):
        v = LOOP[b_][c]
        rect(bx0 + c * gw + 2 + k_ * 13, by0 - bh0 * v / 0.7, 12, bh0 * v / 0.7, col)
        text(bx0 + c * gw + 8 + k_ * 13, by0 - bh0 * v / 0.7 - 1.5, "%.2f" % v, C - 0.6, col, 700, "middle")
    text(bx0 + c * gw + 14.5, by0 + 5, "cell %d" % (c + 1), C, TXT, anchor="middle")
for j, (lab, col) in enumerate((("DPT board", RED), ("load board", BLUE), ("0.5 nH design", "#2CA02C"))):
    rect(bx0 + j * 40, by0 + 9, 4, 4, col)
    text(bx0 + j * 40 + 6, by0 + 12.6, lab, C, TXT)
spread = max((max(v) - min(v)) / min(v) for v in LOOP.values())
bullets(x + 150, cy + 22, [
    "**%.2f nH** load board, %.2f nH DPT (shunt)" % (np.mean(LOOP["load"]), np.mean(LOOP["dpt"])),
    "Cells within %.1f %%" % (100 * spread),
    "Cell coupling k ≤ 0.034",
], w2 - 156, B, 1.6)
ptitle(x + 8, cy + 104, "(a) Switching-energy imbalance, two devices")
hbars(x + 8, cy + 110, [("Power loop +0.3 nH", 2, GREY, "2 %"), ("Gate loops 2 vs 8 nH", 19, AMBER, "19 %"),
                        ("No Kelvin, L_{CS} +0.2 nH", 29, AMBER, "29 %")], 82, w2 - 120, 29)
gl = GS["gate_loop_nH"]
ptitle(x + 8, cy + 147, "(b) Gate-loop inductance (nH)")
hbars(x + 8, cy + 153, [("High side, alone", gl["Q1"]["esl0.0"]["on"], BLUE, "%.1f" % gl["Q1"]["esl0.0"]["on"]),
                        ("High side, pair driven", gl["Q1"]["esl0.0"]["on_pair_driven"], RED,
                         "%.1f" % gl["Q1"]["esl0.0"]["on_pair_driven"]),
                        ("Low side, pair driven", gl["Q3"]["esl0.0"]["on_pair_driven"], BLUE,
                         "%.1f" % gl["Q3"]["esl0.0"]["on_pair_driven"])], 82, w2 - 120, 21)
note_box(x + 8, cy + 202, w2 - 16, 29)
text(x + w2 / 2, cy + 214, "One 2EDF7275K channel per device pair,", B, TEAL, 700, "middle")
text(x + w2 / 2, cy + 223, "star gate network with Kelvin returns", B, TEAL, 700, "middle")

# ------------------------------------------------------------------------------------------------ row 3
y3 = y2 + h2 + G
h3 = 274
w5 = 300
cy = section(M, y3, w5, h3, "5", "Iterative system design (review)")
fx, fy, fw, fh = pdf_figure("fig16", M + 6, cy + 6, w5 - 12, h3 - 34)
caption(M + w5 / 2, y3 + h3 - 6, "Constraints → device, layout, parallel count, dc link, machine → coupled verification")

x6, w6 = M + w5 + G, W - 2 * M - w5 - G
cy = section(x6, y3, w6, h3, "6", "Building block: double-pulse-test board and extracted network")
im = autocrop(Image.open(os.path.join(SLI, "r3d_dpt.png")).convert("RGB"))
image(im, x6 + 6, cy + 8, 178, 124)
caption(x6 + 95, cy + 140, "DPT board: four cells, eight EPC2361")
q = Image.open(os.path.join(SLI, "q3d_full_load.png")).convert("RGB")
q.paste((255, 255, 255), (1780, 0, q.size[0], 380))          # drop the render's legend, drawn below as text
image(autocrop(q), x6 + 190, cy + 8, 168, 124)
caption(x6 + 274, cy + 140, "Ansys Q3D model of the four cells")
kx = x6 + 368
text(kx, cy + 22, "%.2f / %.2f nH" % (np.mean(LOOP["load"]), np.mean(LOOP["dpt"])), 11, NAVY, 700)
text(kx, cy + 30, "loop per cell, load / DPT", 5.8, MUTED)
text(kx, cy + 48, "%.1f / %.1f nH" % (gl["Q1"]["esl0.0"]["on_pair_driven"], gl["Q3"]["esl0.0"]["on_pair_driven"]),
     11, RED, 700)
text(kx, cy + 56, "gate loop, HS / LS pair", 5.8, MUTED)
for j, (col, lab) in enumerate((("#d22b23", "DC+"), ("#1f5fb4", "DC−"), ("#ee9a22", "switch node"),
                                ("#d4b060", "FET / MLCC"))):
    rect(kx, cy + 72 + j * 7, 4, 4, col)
    text(kx + 6, cy + 75.6 + j * 7, lab, C + 0.4, TXT)
caption(kx, cy + 108, "Q3D model colours", "start")
yb = cy + 156
note_box(x6 + 8, yb, 196, 74)
text(x6 + 15, yb + 11, "LTspice with the extracted network", P, NAVY, 700)
text(x6 + 15, yb + 19, "75 V, 322 A, four cells, extracted gate loops", 5.8, MUTED)
bullets(x6 + 15, yb + 31, ["High-side v_{DS} peak **%.0f V** < 100 V rating at R_{g,on} %.1f Ω" % (
    QS["dpt"]["VHpk_max"], QS["dpt"]["RGON"]),
    "Four parallel high-side gate loops equal within 0.3 %",
    "Turn-on energy shared within %.1f %%" % QS["dpt"]["share_Eon_pct"]], 182, B, 1.6)
hx = x6 + 214
ptitle(hx, yb + 6, "Peak high-side V_{DS} (V)")
cases = [("Load board · 2.0 Ω", QS["load"]["VHpk_max"]), ("Load board · 3.0 Ω", QS["load_rg3"]["VHpk_max"]),
         ("DPT, lumped gate · 3.5 Ω", QS["dpt_lumpgate"]["VHpk_max"]), ("DPT · 2.5 Ω", QS["dpt_rg2.5"]["VHpk_max"]),
         ("DPT · 3.5 Ω (chosen)", QS["dpt"]["VHpk_max"])]
rows = [(l_, v - 60, TEAL if v <= 90 else (AMBER if v <= 100 else RED), "%.0f" % v) for l_, v in cases]
hbars(hx, yb + 13, rows, 92, w6 - 214 - 92 - 22, 50, 9.0, refs=[(30, MUTED, "90"), (40, RED, "100")])
caption(hx + 92, yb + 70, "axis from 60 V; dashed: 90 V target, 100 V rating", "start")

# ------------------------------------------------------------------------------------------------ conclusions
y4 = y3 + h3 + G
h4 = 58
rect(M, y4, W - 2 * M, h4, CARD, rx=3, stroke=LINE, sw=0.4)
rect(M, y4, W - 2 * M, 15, NAVY, rx=3)
rect(M, y4 + 8, W - 2 * M, 7, NAVY)
circle(M + 9, y4 + 7.5, 4.6, TEAL)
text(M + 9, y4 + 10.1, "✓", 7.0, "#ffffff", 700, "middle")
text(M + 17, y4 + 10.4, "Conclusions", T, "#ffffff", 600)
cc = [("16 × 75 V cells let 100 V GaN serve a 1200 V, 300 kW drive",
       "The 100 V class has the lowest D-FoM; EPC2361 is the device."),
      ("Four devices per switch: %.0f W per leg (%.2f %%)" % (n4["tot"], 100 * n4["eta"]),
       "%.0f °C junction and %.0f V peak at 0.5 nH loop inductance." % (n4["tj"], n4["vpk"])),
      ("The extracted gate loop (%.1f nH) sets the margin" % gl["Q1"]["esl0.0"]["on_pair_driven"],
       "%.1f Ω turn-on and −1.9 V off-state bias keep the peak at %.0f V." % (QS["dpt"]["RGON"], QS["dpt"]["VHpk_max"]))]
w4 = (W - 2 * M) / 3
for i, (h_, b_) in enumerate(cc):
    xx = M + 10 + i * w4
    circle(xx + 5, y4 + 33, 5, TEAL)
    text(xx + 5, y4 + 35.4, str(i + 1), 7, "#ffffff", 700, "middle")
    yy = text(xx + 14, y4 + 30, h_, B + 0.6, NAVY, 700, width=w4 - 26)
    text(xx + 14, yy + 10, b_, B + 0.2, TXT, width=w4 - 26)

# ------------------------------------------------------------------------------------------------ status, questions
y5 = y4 + h4 + G
h5 = 64
w5_ = (W - 2 * M - G) / 2
for i, (num, title, items) in enumerate((
        ("7", "Project status and next steps", [
            "DPT board: waiting for PCB manufacturing and assembly (JLCPCB).",
            "Double-pulse tests at 75 V up to 322 A: per-cell current sharing, overshoot, E_{on}/E_{off}, gate bump.",
            "Then three load-test legs + PCB busbar: one 75 V three-phase level, continuous and thermal tests."]),
        ("8", "Open research questions", [
            "Optimum N: device class versus component count shifts with SiC, GaN and cooling.",
            "Joint battery–converter–machine design on vehicle energy, mass, cost and reliability.",
            "Stack-position common-mode voltage, bearing currents and insulation across the full stack."]))):
    x = M + i * (w5_ + G)
    cy = section(x, y5, w5_, h5, num, title)
    bullets(x + 9, cy + 13, items, w5_ - 18, B + 0.4, 2.6)

# ------------------------------------------------------------------------------------------------ footer
fy = y5 + h5 + 10
rect(0, fy, W, H - fy, NAVY)
rect(0, fy, W, 3, TEAL)
text(M, fy + 14, "KTH Royal Institute of Technology · Division of Electric Power and Energy Systems", 7, "#cfe3ef")
text(W - M, fy + 14, "Enes Ayaz · Moore4Power General Assembly 2026", 7, "#ffffff", 600, "end")
print("footer at %.0f mm (page %d)" % (fy, H))
assert fy + 18 < H, "content runs into the page bottom"

svg = ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
       'xmlns:xlink="http://www.w3.org/1999/xlink" width="841mm" height="1189mm" viewBox="0 0 841 1189">\n'
       + "\n".join(S) + "\n</svg>\n")
p = os.path.join(OUT, "spb_project_poster_A0.svg")
open(p, "w", encoding="utf-8").write(svg)
print("wrote", p, "%.1f MB" % (len(svg) / 1e6))
for ext, extra in (("pdf", []), ("png", ["--export-dpi=150"])):
    subprocess.run([INK, p, "--export-type=" + ext, "--export-filename=" + p[:-3] + ext] + extra, capture_output=True)
    print("exported", ext)

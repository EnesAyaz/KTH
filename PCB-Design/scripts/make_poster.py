"""
A0 project-meeting poster: SPB review (Review-Paper-SPB/main.pdf) + Rev B building block (design-flow deck).
Style follows Enes's ICPE poster (VisualizationScience/Assignment-3/poster_A0.svg): navy header, teal accents,
numbered section bars, KPI cards, Segoe UI. Units: mm (viewBox 841 x 1189).

    python scripts/make_poster.py  ->  reports/poster/spb_project_poster_A0.svg
    "C:\\Program Files\\Inkscape\\bin\\inkscape.exe" <svg> --export-type=pdf  (and png for a preview)
"""
import base64
import io
import os
import re

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KTH = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "reports", "poster")
SLI = os.path.join(ROOT, "reports", "slides", "revb_pptx", "img")
REV = os.path.join(KTH, "Review-Paper-SPB", "Figures", "Exported")
TPL = os.path.join(OUT, "img")

NAVY, TEAL, BG, INK, MUTED, CARD, LINE = "#0b3a6e", "#16968a", "#eef2f5", "#1d2b3a", "#66727c", "#ffffff", "#c9d3db"
TINT, AMBER, RED = "#e3f2ef", "#e39b2d", "#c8423b"
FONT = "'Segoe UI',Arial,sans-serif"
W, H, M = 841, 1189, 40
S = []


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rich(t):
    """V_{dc} -> subscript, x^{2} -> superscript, **bold**."""
    t = esc(t)
    t = re.sub(r"_\{([^}]*)\}", r'<tspan baseline-shift="sub" style="font-size:70%">\1</tspan>', t)
    t = re.sub(r"\^\{([^}]*)\}", r'<tspan baseline-shift="super" style="font-size:70%">\1</tspan>', t)
    return re.sub(r"\*\*(.*?)\*\*", r'<tspan style="font-weight:600">\1</tspan>', t)


def plain(t):
    return re.sub(r"[_^]\{([^}]*)\}", r"\1", t).replace("**", "")


def wrap(t, width, size):
    """Greedy wrap on the plain-text width (Segoe UI ~0.53 em per character on average)."""
    lines, cur = [], ""
    for word in t.split(" "):
        cand = (cur + " " + word).strip()
        if len(plain(cand)) * 0.53 * size > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = cand
    return lines + [cur]


def text(x, y, t, size=7, color=INK, weight=400, anchor="start", width=None, lh=1.32):
    lines = wrap(t, width, size) if width else [t]
    for i, ln in enumerate(lines):
        S.append('<text x="%.2f" y="%.2f" style="font-family:%s;font-size:%.2fpx;fill:%s;font-weight:%d;'
                 'text-anchor:%s">%s</text>' % (x, y + i * size * lh, FONT, size, color, weight, anchor, rich(ln)))
    return y + len(lines) * size * lh


def rect(x, y, w, h, fill, rx=0, stroke="none", sw=0.0):
    S.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" style="fill:%s;stroke:%s;stroke-width:%.2f"/>'
             % (x, y, w, h, rx, fill, stroke, sw))


def circle(cx, cy, r, fill):
    S.append('<circle cx="%.2f" cy="%.2f" r="%.2f" style="fill:%s"/>' % (cx, cy, r, fill))


def bullets(x, y, items, width, size=6.8, gap=2.2, color=INK):
    for it in items:
        circle(x + 1.3, y - size * 0.32, 1.0, TEAL)
        y = text(x + 5, y, it, size, color, width=width - 5) + gap
    return y


def autocrop(im, pad=6):
    g = im.convert("L")
    box = Image.eval(g, lambda v: 255 if v < 245 else 0).getbbox()
    if box:
        im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width),
                      min(box[3] + pad, im.height)))
    return im


def image(path, x, y, w, h, crop=True, jpeg=False, maxpx=1800):
    """Embed an image scaled to fit (w x h), centred; returns the drawn box."""
    im = Image.open(path).convert("RGB")
    if crop:
        im = autocrop(im)
    k = min(w / im.width, h / im.height)
    dw, dh = im.width * k, im.height * k
    if max(im.size) > maxpx:
        im.thumbnail((maxpx, maxpx), Image.LANCZOS)
    buf = io.BytesIO()
    if jpeg:
        im.save(buf, "JPEG", quality=90)
        mime = "jpeg"
    else:
        im.save(buf, "PNG", optimize=True)
        mime = "png"
    dx, dy = x + (w - dw) / 2, y + (h - dh) / 2
    S.append('<image x="%.2f" y="%.2f" width="%.2f" height="%.2f" preserveAspectRatio="none" '
             'xlink:href="data:image/%s;base64,%s"/>' % (dx, dy, dw, dh, mime, base64.b64encode(buf.getvalue()).decode()))
    return dx, dy, dw, dh


def caption(x, y, w, t):
    return text(x + w / 2, y, t, 6.0, MUTED, anchor="middle")


def section(x, y, w, h, num, title, fill=CARD):
    rect(x, y, w, h, fill, rx=3, stroke=LINE, sw=0.4)
    rect(x, y, w, 15, NAVY, rx=3)
    rect(x, y + 8, w, 7, NAVY)
    circle(x + 9, y + 7.5, 4.6, TEAL)
    text(x + 9, y + 10.2, num, 7.2, "#ffffff", 600, "middle")
    text(x + 17, y + 10.4, title, 8.6, "#ffffff", 600)
    return y + 23


def band(y, t):
    text(M, y, t, 9.5, NAVY, 600)
    S.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" style="stroke:%s;stroke-width:0.6"/>'
             % (M + len(t) * 0.55 * 9.5 + 4, y - 3, W - M, y - 3, TEAL))


# ------------------------------------------------------------------------------------------------ page and header
rect(0, 0, W, H, BG)
rect(0, 0, W, 150, NAVY)
rect(0, 146, W, 4, TEAL)
text(M, 27, "Project meeting · KTH Electric Power and Energy Systems · October 2026", 7.5, "#cfe3ef")
text(M, 63, "Stacked Polyphase Bridge Traction Drives:", 23, "#ffffff", 600)
text(M, 92, "from System Review to a GaN Building Block", 23, "#ffffff", 600)
text(M, 118, "Enes Ayaz, Shahriar Sarmast Ghahfarokhi, Kevin Klarin, Staffan Norrga", 10, "#ffffff", 600)
text(M, 134, "Division of Electric Power and Energy Systems, KTH Royal Institute of Technology, Stockholm, Sweden",
     7.5, "#cfe3ef")
# stack icon: N series cells, each with its winding group
for i, lab in enumerate(("Cell N", "...", "Cell 2", "Cell 1")):
    yy = 22 + i * 27
    if lab == "...":
        text(728, yy + 14, "⋮", 12, "#cfe3ef", anchor="middle")
        continue
    rect(700, yy, 56, 20, "#16508f", rx=2, stroke="#9fc3e6", sw=0.5)
    text(728, yy + 8.5, lab, 6.5, "#ffffff", 600, "middle")
    text(728, yy + 16, "75 V · 3-phase", 5.6, "#cfe3ef", anchor="middle")
    S.append('<line x1="756" y1="%.1f" x2="770" y2="%.1f" style="stroke:#9fc3e6;stroke-width:0.6"/>' % (yy + 10, yy + 10))
    circle(774, yy + 10, 4, TEAL)
text(774, 136, "16 × 75 V = 1200 V", 6.2, "#cfe3ef", anchor="middle")

# ------------------------------------------------------------------------------------------------ KPI cards
KPI = [("1200 V", "dc link, 300 kW traction"), ("16 × 75 V", "series cells, own winding groups"),
       ("4 × EPC2361", "100 V GaN per switch"), ("0.41 nH", "commutation loop per cell"),
       ("99.71 %", "semiconductor efficiency"), ("2.85 %", "shared-bus dc ripple, 50 kHz")]
cw = (W - 2 * M - 5 * 10) / 6
for i, (v, d) in enumerate(KPI):
    x = M + i * (cw + 10)
    rect(x, 163, cw, 50, CARD, rx=3, stroke=LINE, sw=0.4)
    rect(x, 163, 2.2, 50, TEAL)
    text(x + 9, 186, v, 13, NAVY, 600)
    text(x + 9, 200, d, 6.3, MUTED)

# ------------------------------------------------------------------------------------------------ part A: review
band(234, "A · Review: what the SPB architecture demands")
y0 = 242
cy = section(M, y0, W - 2 * M, 222, "1", "Concept: split the dc voltage, keep one machine")
image(os.path.join(REV, "fig03.png"), M + 8, cy, 222, 160)
caption(M + 8, cy + 168, 222, "N-cell SPB: series dc links, separate winding groups")
image(os.path.join(REV, "fig04.png"), M + 242, cy + 2, 210, 152)
caption(M + 242, cy + 168, 210, "SPB research, 2013 to present")
image(os.path.join(TPL, "tpl_0.jpg"), M + 462, cy, 150, 160, jpeg=True)
caption(M + 462, cy + 168, 150, "Integration concept: cold plate, legs, busbar")
rect(M + 622, cy - 2, 133, 182, TINT, rx=2)
rect(M + 622, cy - 2, 1.8, 182, TEAL)
bullets(M + 629, cy + 9, [
    "N two-level bridges in series on the dc side; each feeds its own three-phase winding group.",
    "V_{dc,k} ≈ V_{dc}/N: the device voltage class follows the cell, not the full link.",
    "All cells carry the same dc current; P_{ac} = ΣP_{k}, so cell voltages must be balanced actively.",
    "6N switches, N drivers and capacitors: complexity moves to the system, it does not vanish.",
], 122, 6.7)

y1 = y0 + 222 + 14
cw3 = (W - 2 * M - 2 * 12) / 3
cols = [
    ("2", "Device voltage class and cell count", "fig13.png",
     "1200 V link: V_{cell} = V_{dc}/N versus active switches 6N",
     ["Lower blocking voltage raises the device figure of merit (D-FOM) within each technology.",
      "Rating with margin: V_{rated} ≥ k_{rel}(V_{dc,max}/N + ΔV_{imb} + ΔV_{sw}).",
      "N = 16 gives 75 V cells for 100 V GaN; the overshoot L·di/dt sets the usable margin."]),
    ("3", "Modulation, ripple and common mode", "fig09.png",
     "Shared dc current of three cells, with and without interleaving",
     ["Carrier interleaving δ_{k} = 2π(k−1)/N cancels carrier orders that are not multiples of N.",
      "Cell k sits at the offset (k−1)V_{dc}/N: a stack-position common-mode voltage modulation cannot remove.",
      "Complementary two-cell switching cancels the switching CMV only with matched timing."]),
    ("4", "Voltage balancing and fault handling", "fig12.png",
     "Differential power ΔP_{k} restores equal cell voltages (motoring)",
     ["The open-loop series stack is unstable in motoring: N−1 positive real eigenvalues.",
      "Centralized, common-duty-ratio and distributed control trade authority against communication.",
      "A faulted cell must be bypassed without breaking the series dc path; survivors then carry V_{dc}/M."]),
]
for i, (num, title, fig, cap, items) in enumerate(cols):
    x = M + i * (cw3 + 12)
    cy = section(x, y1, cw3, 240, num, title)
    image(os.path.join(REV, fig), x + 8, cy, cw3 - 16, 125)
    yy = caption(x + 8, cy + 132, cw3 - 16, cap) + 5
    bullets(x + 8, yy + 3, items, cw3 - 16, 6.7)

# ------------------------------------------------------------------------------------------------ part B: building block
y2 = y1 + 240 + 22
band(y2 - 8, "B · Design flow and the four-parallel GaN building block")
cy = section(M, y2, 300, 248, "5", "Iterative system design (review Fig. 16)")
image(os.path.join(REV, "fig16.png"), M + 6, cy, 288, 188)
yy = caption(M + 6, cy + 195, 288, "Constraints → device, layout, parallel count, dc link, machine → coupled verification") + 4
bullets(M + 8, yy + 3, ["This project: EPC2361, N = 16, n_{p} = 4 per switch, 50 kHz, 134 µF effective per leg; "
                        "Q3D-extracted loops feed the LTspice double-pulse model."], 284, 6.6)

bx, bw = M + 314, W - 2 * M - 314
cy = section(bx, y2, bw, 248, "6", "Building block: final double-pulse-test board (Rev B)")
image(os.path.join(SLI, "r3d_dpt.png"), bx + 6, cy, 200, 138, jpeg=True)
caption(bx + 6, cy + 145, 200, "DPT board: four cells, M6 ac bolt and copper bar")
image(os.path.join(SLI, "r3d_dpt_fets_row.png"), bx + 214, cy, bw - 222, 64, crop=False, jpeg=True)
caption(bx + 214, cy + 70, bw - 222, "Eight EPC2361 from above (heatsink, shunts hidden)")
bullets(bx + 216, cy + 82, [
    "89.5 × 85.2 mm, 4 layers, 2 oz, 0.1 mm L1–L2 dielectric: every loop closes vertically on the dc− plane.",
    "Four cells in two point-symmetric blocks; one 2EDF7275K per device pair, Kelvin gate returns.",
    "Per cell 20 × 22 µF 2220 + 10 × 1 µF; R_{g,on} 3.5 Ω, −1.9 V off-state bias.",
    "1 mΩ coaxial shunt per cell; MMCX and spring-probe pads for v_{DS}, v_{GS} of all eight devices.",
], bw - 222, 6.5, 1.8)
rect(bx + 6, cy + 153, 200, 64, TINT, rx=2)
rect(bx + 6, cy + 153, 1.8, 64, TEAL)
text(bx + 13, cy + 164, "LTspice with the extracted network (75 V, 322 A)", 6.6, NAVY, 600)
bullets(bx + 13, cy + 174, ["High-side v_{DS} peak **92.9 V** < 100 V rating", "Four parallel high-side gate loops equal within 0.3 %",
                            "Released for JLCPCB fabrication + assembly (DRC 0, final review 26 Oct)"], 190, 6.4, 1.4)

# ------------------------------------------------------------------------------------------------ results and outlook
y3 = y2 + 248 + 14
cards = [
    ("7", "Extracted parasitics (Ansys Q3D)"),
    ("8", "Project status and next steps"),
    ("9", "Open research questions (review)"),
]
hh = 108
for i, (num, title) in enumerate(cards):
    x = M + i * (cw3 + 12)
    cy = section(x, y3, cw3, hh, num, title)
    if num == "7":
        image(os.path.join(SLI, "final_loop_cells.png"), x + 4, cy - 3, 132, 82)
        bullets(x + 140, cy + 5, [
            "Loop per cell: **0.41 nH** load board, 0.65 nH DPT (shunt); cells within 1.6 %",
            "Cell coupling k ≤ 0.034",
            "Gate loop, pair driven: 20.6 nH HS, 12.3 nH LS",
        ], cw3 - 146, 6.2, 1.6)
    elif num == "8":
        bullets(x + 8, cy + 5, [
            "DPT board released for JLCPCB PCB + assembly; shunts and loop test points fitted in the lab.",
            "Double-pulse tests at 75 V up to 322 A: per-cell current sharing, overshoot, E_{on}/E_{off}, gate bump.",
            "Then three load-test legs + PCB busbar: one 75 V three-phase level, continuous and thermal tests.",
        ], cw3 - 16, 6.5, 2.0)
    else:
        bullets(x + 8, cy + 5, [
            "Optimum N: device class versus component count shifts with SiC, GaN and cooling.",
            "Joint battery–converter–machine design on vehicle energy, mass, cost and reliability.",
            "Stack-position CMV, bearing currents and insulation across the full stack.",
        ], cw3 - 16, 6.5, 2.0)

# ------------------------------------------------------------------------------------------------ footer
fy = H - 52
rect(0, fy, W, 52, NAVY)
rect(0, fy, W, 3, TEAL)
text(M, fy + 18, "SPB moves the voltage problem from the device to the system: the building block shows that a 100 V GaN "
     "cell meets its loop and overshoot budget;", 7.6, "#ffffff", 600)
text(M, fy + 29, "the review sets out what the full stack must still prove — balancing, common mode, faults and machine "
     "co-design.", 7.6, "#ffffff", 600)
text(M, fy + 43, "[1] E. Ayaz et al., Stacked polyphase bridge converters for high-voltage traction drives: a review, IEEE OJPEL "
     "(submitted)  [2] S. Norrga et al., IECON 2013  [3] EPC2361 datasheet  [4] Rev B design-flow slides, 2026",
     5.8, "#cfe3ef")
text(W - M, fy + 18, "Enes Ayaz · KTH", 8, "#ffffff", 600, "end")

svg = ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
       'xmlns:xlink="http://www.w3.org/1999/xlink" width="841mm" height="1189mm" viewBox="0 0 841 1189">\n'
       + "\n".join(S) + "\n</svg>\n")
os.makedirs(OUT, exist_ok=True)
p = os.path.join(OUT, "spb_project_poster_A0.svg")
open(p, "w", encoding="utf-8").write(svg)
print("wrote", p, "%.1f MB" % (len(svg) / 1e6))

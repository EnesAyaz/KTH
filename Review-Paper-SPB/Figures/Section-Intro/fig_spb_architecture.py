#!/usr/bin/env python3
"""
fig_spb_architecture.py

Generates fig_spb_architecture.svg: the four-stage SPB traction-drive
architecture diagram (DC source/battery -> stacked dc-link -> SPB
inverter cells -> multiphase traction machine), in the style of the
reference block diagram the user supplied, but with black text (not
blue) and matching this paper's existing convention of showing cell 1,
cell 2, an ellipsis, and cell N rather than literally N cells.

Pure standard library (no svgwrite dependency) -- just string-built SVG,
so it is easy to read/edit by hand and easy to re-run. Edit the
PARAMETERS block below and re-run to change colors, spacing, or the
number of explicitly drawn cells.

Output is native SVG (Inkscape's own file format), openable and
further editable directly in Inkscape. Run this script, then convert
to PDF for LaTeX embedding with:

    inkscape fig_spb_architecture.svg --export-pdf=fig_spb_architecture.pdf   (Inkscape 0.9x)
    inkscape fig_spb_architecture.svg --export-type=pdf                       (Inkscape 1.x)
"""

import os

# ===========================================================================
# PARAMETERS
# ===========================================================================
W, H = 1500, 900                # canvas size
STROKE = "black"
TEXT_COLOR = "black"            # user explicitly wants black, not blue
FONT = "Times New Roman, Times, serif"
LW = 2.0                        # default line width
LW_THICK = 3.0
LW_DASH = "8,5"

# Header row
HEAD_CY = 50
HEAD_R = 17

# Vertical dc-link node levels (bus at x = BUS_X)
BUS_X = 300
NODE_PLUS = 150
NODE_1 = 330
NODE_2 = 510
NODE_NM1 = 610
NODE_MINUS = 790
ELLIPSIS_Y0, ELLIPSIS_Y1 = NODE_2, NODE_NM1

# Column extents
SRC_X0, SRC_X1 = 20, 170
DCLINK_X0, DCLINK_X1 = 245, 420
CELL_X0, CELL_X1 = 440, 900
MACH_X0, MACH_X1 = 920, 1300
MOTOR_CX = 1400

svg_parts = []


def add(s):
    svg_parts.append(s)


def line(x1, y1, x2, y2, stroke=STROKE, w=LW, dash=None, marker=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#arrow)"' if marker else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="{w}"{d}{m}/>')


def rect(x, y, w, h, rx=6, fill="white", stroke=STROKE, sw=LW, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def text(x, y, s, size=20, anchor="start", weight="normal", style="normal",
         color=TEXT_COLOR):
    add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" font-style="{style}" fill="{color}" '
        f'text-anchor="{anchor}">{s}</text>')


def circle(cx, cy, r, fill="white", stroke=STROKE, sw=LW):
    add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}"/>')


def dot(cx, cy, r=4.5):
    add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{STROKE}"/>')


def header_stage(cx, num, lines, title_x):
    circle(cx, HEAD_CY, HEAD_R, fill="white", sw=2.2)
    text(cx, HEAD_CY + 7, str(num), size=19, anchor="middle", weight="bold")
    ty = HEAD_CY - 4 if len(lines) > 1 else HEAD_CY + 6
    for ln in lines:
        text(title_x, ty, ln, size=19, weight="bold")
        ty += 22


def arrow_between(x1, x2, y=HEAD_CY):
    line(x1, y, x2 - 10, y, w=LW_THICK, marker=True)


def capacitor(x, y, label_top, label_bottom):
    """Capacitor plates centered at (x, y), oriented across the vertical bus."""
    line(x - 16, y - 6, x + 16, y - 6, w=2.4)
    line(x - 16, y + 6, x + 16, y + 6, w=2.4)
    text(x - 24, y + 5, label_top, size=17, anchor="end")
    # small up/down arrow to the right, indicating the approx per-cell voltage
    ax = x + 34
    line(ax, y - 26, ax, y + 26, w=1.6)
    line(ax, y - 26, ax - 5, y - 18, w=1.6)
    line(ax, y - 26, ax + 5, y - 18, w=1.6)
    line(ax, y + 26, ax - 5, y + 18, w=1.6)
    line(ax, y + 26, ax + 5, y + 18, w=1.6)
    text(ax + 10, y + 5, label_bottom, size=15, style="italic")


def switch(cx, cy, flip=False):
    """Small IGBT + antiparallel-diode symbol, collector at top."""
    s = -1 if flip else 1
    # vertical leads
    line(cx, cy - 22, cx, cy - 6, w=1.8)
    line(cx, cy + 6, cx, cy + 22, w=1.8)
    # switch body: collector bar, emitter bar, diagonal channel + gate arrow
    line(cx - 8, cy - 6, cx + 8, cy - 6, w=1.8)
    line(cx - 8, cy + 6, cx + 8, cy + 6, w=1.8)
    line(cx - 8, cy - 6, cx - 8, cy + 6, w=1.8)
    line(cx - 8, cy, cx - 16, cy, w=1.6)
    add(f'<polygon points="{cx-16},{cy-4} {cx-16},{cy+4} {cx-24},{cy}" '
        f'fill="{STROKE}"/>')
    # antiparallel diode to the right of the switch
    dx = cx + 20
    line(dx, cy - 22, dx, cy - 10, w=1.6)
    line(dx, cy + 10, dx, cy + 22, w=1.6)
    tri_dir = 1 if not flip else -1
    add(f'<polygon points="{dx-6},{cy-10} {dx+6},{cy-10} {dx},{cy+2}" '
        f'fill="none" stroke="{STROKE}" stroke-width="1.4"/>')
    line(dx - 6, cy + 10, dx + 6, cy + 10, w=1.6)
    line(cx, cy - 16, dx, cy - 16, w=1.2)
    line(cx, cy + 16, dx, cy + 16, w=1.2)


CELL_MARGIN = 22   # gap left above/below each cell box so labels never
                    # collide with the neighboring cell


def bridge_cell(x0, x1, y0, y1, label, dc_left_x):
    """One three-phase two-level bridge cell with 3 legs (6 switches).

    y0, y1 are the electrical dc-link node levels (shared with the
    stacked dc-link taps); the box itself is inset by CELL_MARGIN so
    consecutive cells never touch and the title label always has room.
    """
    by0, by1 = y0 + CELL_MARGIN, y1 - CELL_MARGIN
    # stub connectors from the dc-link tap (arriving at dc_left_x) up/down
    # to the inset box corners
    line(dc_left_x, y0, x0, by0 + 14, w=LW_THICK)
    line(dc_left_x, y1, x0, by1 - 14, w=LW_THICK)
    rect(x0, by0, x1 - x0, by1 - by0, rx=8, fill="white", sw=2.0)
    text((x0 + x1) / 2, by0 - 10, label, size=17, anchor="middle", weight="bold")
    ymid = (by0 + by1) / 2
    leg_xs = [x0 + (x1 - x0) * f for f in (0.28, 0.5, 0.72)]
    phase_labels = ["a", "b", "c"]
    top_rail_y, bot_rail_y = by0 + 14, by1 - 14
    line(x0 + 10, top_rail_y, x1 - 10, top_rail_y, w=1.6)
    line(x0 + 10, bot_rail_y, x1 - 10, bot_rail_y, w=1.6)
    outs = []
    for lx, lab in zip(leg_xs, phase_labels):
        line(lx, top_rail_y, lx, top_rail_y + 20, w=1.6)
        switch(lx, top_rail_y + 34)
        line(lx, top_rail_y + 50, lx, ymid, w=1.6)
        dot(lx, ymid, 3)
        line(lx, ymid, lx, bot_rail_y - 50, w=1.6)
        switch(lx, bot_rail_y - 34)
        line(lx, bot_rail_y - 20, lx, bot_rail_y, w=1.6)
        line(lx, ymid, x1 + 26, ymid, w=1.6)
        outs.append((x1 + 26, ymid, lab))
    return outs, top_rail_y, bot_rail_y


def coil(cx, cy, n=3, r=7):
    """Simple winding/inductor symbol: a row of small arcs."""
    path = f'M {cx-3*r} {cy}'
    for i in range(n):
        path += f' A {r} {r} 0 0 1 {cx - 3*r + (2*i+2)*r} {cy}'
    add(f'<path d="{path}" fill="none" stroke="{STROKE}" stroke-width="1.8"/>')
    return cx - 3 * r, cx + 3 * r


# ===========================================================================
# Build the drawing
# ===========================================================================
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}">')
add(f'<defs><marker id="arrow" markerWidth="10" markerHeight="10" '
    f'refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" '
    f'fill="{STROKE}"/></marker></defs>')
add(f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>')

# ---- headers -------------------------------------------------------------
header_stage(35, 1, ["DC Source /", "Battery"], 62)
arrow_between(300, 390)
header_stage(390, 2, ["Stacked DC-Link"], 417)
arrow_between(650, 745)
header_stage(770, 3, ["SPB Inverter Cells"], 797)
arrow_between(1040, 1130)
header_stage(1150, 4, ["Multiphase Traction Machine", "(Polyphase Machine)"], 1177)

# ---- Stage 1: DC source / battery ----------------------------------------
rect(SRC_X0, NODE_PLUS, SRC_X1 - SRC_X0, NODE_MINUS - NODE_PLUS, rx=8, sw=2.2)
cxsrc = (SRC_X0 + SRC_X1) / 2
text(cxsrc, (NODE_PLUS + NODE_MINUS) / 2 - 40, "DC Source /", size=18, anchor="middle")
text(cxsrc, (NODE_PLUS + NODE_MINUS) / 2 - 18, "Battery", size=18, anchor="middle")
text(cxsrc, (NODE_PLUS + NODE_MINUS) / 2 + 20, "V", size=22, anchor="middle", style="italic")
text(cxsrc + 8, (NODE_PLUS + NODE_MINUS) / 2 + 26, "dc", size=13, style="italic")

vx = SRC_X1 + 18
line(vx, NODE_PLUS, vx, NODE_MINUS, w=1.6, marker=True)
line(vx, NODE_MINUS, vx, NODE_PLUS, w=1.6, marker=True)
text(vx - 10, (NODE_PLUS + NODE_MINUS) / 2, "V", size=18, anchor="middle", style="italic")
text(vx - 2, (NODE_PLUS + NODE_MINUS) / 2 + 5, "dc", size=11, style="italic")

line(SRC_X1, NODE_PLUS, BUS_X, NODE_PLUS, w=LW_THICK)
line(SRC_X1, NODE_MINUS, BUS_X, NODE_MINUS, w=LW_THICK)
text(cxsrc + 60, NODE_PLUS - 10, "+", size=22, anchor="middle", weight="bold")
text(cxsrc + 60, NODE_MINUS + 26, "−", size=22, anchor="middle", weight="bold")

# ---- Stage 2: stacked dc-link ---------------------------------------------
rect(DCLINK_X0, NODE_PLUS - 30, DCLINK_X1 - DCLINK_X0, NODE_MINUS - NODE_PLUS + 60,
     rx=10, fill="none", sw=1.6, dash="10,6")

line(BUS_X, NODE_PLUS, BUS_X, NODE_1, w=LW_THICK)
line(BUS_X, NODE_1, BUS_X, NODE_2, w=LW_THICK)
line(BUS_X, ELLIPSIS_Y0, BUS_X, ELLIPSIS_Y1, w=1.4, dash="4,5")
line(BUS_X, NODE_NM1, BUS_X, NODE_MINUS, w=LW_THICK)

dot(BUS_X, NODE_PLUS); dot(BUS_X, NODE_1); dot(BUS_X, NODE_2)
dot(BUS_X, NODE_NM1); dot(BUS_X, NODE_MINUS)

capacitor(BUS_X, (NODE_PLUS + NODE_1) / 2, "C1", "≈Vdc/N")
capacitor(BUS_X, (NODE_1 + NODE_2) / 2, "C2", "≈Vdc/N")
capacitor(BUS_X, (NODE_NM1 + NODE_MINUS) / 2, "CN", "≈Vdc/N")
text(BUS_X, (ELLIPSIS_Y0 + ELLIPSIS_Y1) / 2 + 6, "⋮", size=22, anchor="middle")

for ny in (NODE_PLUS, NODE_1, NODE_2, NODE_NM1, NODE_MINUS):
    line(BUS_X, ny, DCLINK_X1, ny, w=LW_THICK)

text((DCLINK_X0 + DCLINK_X1) / 2, H - 40, "Stacked DC-Link", size=17,
     anchor="middle", weight="bold")

# ---- Stage 3: SPB inverter cells ------------------------------------------
rect(CELL_X0, NODE_PLUS - 30, CELL_X1 - CELL_X0, NODE_MINUS - NODE_PLUS + 60,
     rx=10, fill="none", sw=1.6, dash="10,6")

cell1_out, _, _ = bridge_cell(CELL_X0 + 30, CELL_X1 - 40, NODE_PLUS, NODE_1, "Bridge Cell 1", DCLINK_X1)
cell2_out, _, _ = bridge_cell(CELL_X0 + 30, CELL_X1 - 40, NODE_1, NODE_2, "Bridge Cell 2", DCLINK_X1)
text((CELL_X0 + CELL_X1) / 2, (ELLIPSIS_Y0 + ELLIPSIS_Y1) / 2 + 6, "⋮",
     size=22, anchor="middle")
cellN_out, _, _ = bridge_cell(CELL_X0 + 30, CELL_X1 - 40, NODE_NM1, NODE_MINUS, "Bridge Cell N", DCLINK_X1)

text((CELL_X0 + CELL_X1) / 2, H - 40, "SPB Inverter Cells", size=17,
     anchor="middle", weight="bold")

# ---- Stage 4: multiphase traction machine ---------------------------------
rect(MACH_X0, NODE_PLUS - 30, MACH_X1 - MACH_X0, NODE_MINUS - NODE_PLUS + 60,
     rx=10, fill="none", sw=1.6, dash="10,6")

bus_right_x = MACH_X1 - 60


def emit_winding(cell_outs, k):
    ys = [p[1] for p in cell_outs]
    x0 = MACH_X0 + 10
    for (ox, oy, lab), y in zip(cell_outs, ys):
        line(ox, oy, x0 + 46 - 21, y, w=1.6)
    x_coil = x0 + 46
    coil(x_coil, ys[0]); coil(x_coil, ys[1]); coil(x_coil, ys[2])
    text(x0 + 92, ys[1] - 22, "Three-phase", size=16)
    text(x0 + 92, ys[1] - 2, f"winding set {k}", size=16)
    text(x0 + 92, ys[1] + 20, f"(a{k}, b{k}, c{k})", size=15, style="italic")
    for y in ys:
        line(x_coil + 21, y, bus_right_x, y, w=1.4)


emit_winding(cell1_out, 1)
emit_winding(cell2_out, 2)
text((MACH_X0 + MACH_X1) / 2 - 40, (ELLIPSIS_Y0 + ELLIPSIS_Y1) / 2 + 6, "⋮",
     size=22, anchor="middle")
emit_winding(cellN_out, "N")

line(bus_right_x, NODE_PLUS + 40, bus_right_x, NODE_MINUS - 40, w=1.6)
text((MACH_X0 + MACH_X1) / 2, H - 40, "Multiphase Traction Machine", size=17,
     anchor="middle", weight="bold")
text((MACH_X0 + MACH_X1) / 2, H - 18, "(Polyphase Machine)", size=15, anchor="middle")

# ---- Motor -----------------------------------------------------------------
mcy = (NODE_PLUS + NODE_MINUS) / 2
line(bus_right_x, mcy, MOTOR_CX - 40, mcy, w=1.8, marker=True)
circle(MOTOR_CX, mcy, 42, fill="white", sw=2.4)
text(MOTOR_CX, mcy + 12, "M", size=30, anchor="middle", weight="bold")
line(MOTOR_CX + 42, mcy, MOTOR_CX + 100, mcy, w=2.2, marker=True)
text(MOTOR_CX + 108, mcy + 6, "T", size=20, style="italic")
text(MOTOR_CX + 122, mcy + 12, "e", size=13, style="italic")

add('</svg>')

out_svg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fig_spb_architecture.svg")
with open(out_svg, "w", encoding="utf-8") as f:
    f.write("\n".join(svg_parts))
print("Saved", out_svg)

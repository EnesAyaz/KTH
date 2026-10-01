#!/usr/bin/env python3
"""
fig_winding_options.py

Generates fig_winding_options.svg: the three-panel schematic comparing
SPB winding-group spatial arrangements -- (a) aligned, (b) spatially
shifted, (c) physically segmented -- reproducing Fig. 6 of the paper
(previously drawn inline in TikZ/circuitikz in
Sections/Section_IV_Machine_Integration.tex), now as native Inkscape
SVG. Colors match Fig. 1 / Fig. 2's blue/red palette.

Pure standard library (no svgwrite dependency) -- just string-built
SVG, easy to read/edit by hand and easy to re-run. Edit the PARAMETERS
block below and re-run to change spacing, colors, or angles.

Convert to PDF for LaTeX embedding with:
    inkscape fig_winding_options.svg --export-pdf=fig_winding_options.pdf   (Inkscape 0.9x)
    inkscape fig_winding_options.svg --export-type=pdf                      (Inkscape 1.x)
"""

import math
import os

# ===========================================================================
# PARAMETERS
# ===========================================================================
R = 110                          # panel circle radius
PANEL_CX = [150, 470, 790]       # panel circle centers (x)
PANEL_CY = 175
PANEL_SPACING = PANEL_CX[1] - PANEL_CX[0]
W = PANEL_CX[-1] + R + 90
H = 430

BLUE = "#1a3399"                 # same blue family as Fig. 1 / Fig. 2
RED = "#a60f0f"                  # same red family as Fig. 1 / Fig. 2
GRAY = "#737373"
FONT = "Times New Roman, Times, serif"

svg_parts = []


def add(s):
    svg_parts.append(s)


def line(x1, y1, x2, y2, color="black", w=2.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>')


def circle(cx, cy, r, fill="none", stroke="black", w=2.2):
    add(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{w}"/>')


def dot(cx, cy, r, color):
    add(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{color}"/>')


def text(x, y, s, size=17, anchor="middle", weight="normal", color="black",
         style="normal"):
    add(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" font-style="{style}" '
        f'fill="{color}" text-anchor="{anchor}">{s}</text>')


def coil_spoke(cx, cy, angle_deg, length, color, coil_frac=(0.42, 0.80),
               n_loops=3, loop_amp=5.5):
    """A phase-axis spoke drawn as a lead-in wire, a small coil (loop
    train) matching circuitikz's 'cute inductor' bipole look, and a
    lead-out wire to the panel boundary."""
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), -math.sin(a)   # SVG y is flipped vs. TikZ
    nx, ny = -uy, ux                      # perpendicular (for loop bulge)
    x0, y0 = cx, cy
    x_c0 = cx + ux * length * coil_frac[0]
    y_c0 = cy + uy * length * coil_frac[0]
    x_c1 = cx + ux * length * coil_frac[1]
    y_c1 = cy + uy * length * coil_frac[1]
    x1, y1 = cx + ux * length, cy + uy * length

    line(x0, y0, x_c0, y_c0, color=color, w=2.2)
    # coil body: n_loops small semicircular bumps between x_c0..x_c1
    seg = (coil_frac[1] - coil_frac[0]) / n_loops
    path = f'M {x_c0:.2f} {y_c0:.2f} '
    for i in range(n_loops):
        f0 = coil_frac[0] + i * seg
        f1 = coil_frac[0] + (i + 1) * seg
        fm = (f0 + f1) / 2
        pmx = cx + ux * length * fm + nx * loop_amp
        pmy = cy + uy * length * fm + ny * loop_amp
        px1 = cx + ux * length * f1
        py1 = cy + uy * length * f1
        path += f'Q {pmx:.2f} {pmy:.2f} {px1:.2f} {py1:.2f} '
    add(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.2" '
        f'stroke-linecap="round"/>')
    line(x_c1, y_c1, x1, y1, color=color, w=2.2)


def panel_circle_outline(cx, cy):
    circle(cx, cy, R, stroke=GRAY, w=2.4)


def panel_label(cx, cy, s):
    text(cx, cy + R + 40, s, size=19, weight="normal")


# ===========================================================================
# Build
# ===========================================================================
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}">')
add('<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="5" '
    f'refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{GRAY}"/></marker></defs>')
add(f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>')

# ---- Panel (a): Aligned ---------------------------------------------------
cx, cy = PANEL_CX[0], PANEL_CY
panel_circle_outline(cx, cy)
offs = 6
bx, by = cx - offs, cy - offs
rx, ry = cx + offs, cy + offs
for ang in (90, 210, 330):
    coil_spoke(bx, by, ang, R * 0.79, BLUE)
    coil_spoke(rx, ry, ang, R * 0.79, RED)
dot(bx, by, 5, BLUE)
dot(rx, ry, 5, RED)
panel_label(cx, cy, "(a) Aligned")

# ---- Panel (b): Shifted ----------------------------------------------------
cx, cy = PANEL_CX[1], PANEL_CY
panel_circle_outline(cx, cy)
bx, by = cx - offs, cy - offs
rx, ry = cx + offs, cy + offs
for ang in (90, 210, 330):
    coil_spoke(bx, by, ang, R * 0.84, BLUE)
for ang in (30, 150, 270):
    coil_spoke(rx, ry, ang, R * 0.84, RED)
dot(bx, by, 5, BLUE)
dot(rx, ry, 5, RED)
# Delta-theta arc from the 90-degree (blue) axis to the 30-degree (red) axis
arc_r = R * 0.84 - 8
a0, a1 = 90, 30
x_start = cx + arc_r * math.cos(math.radians(a0))
y_start = cy - arc_r * math.sin(math.radians(a0))
x_end = cx + arc_r * math.cos(math.radians(a1))
y_end = cy - arc_r * math.sin(math.radians(a1))
add(f'<path d="M {x_start:.2f} {y_start:.2f} A {arc_r:.2f} {arc_r:.2f} 0 0 1 '
    f'{x_end:.2f} {y_end:.2f}" fill="none" stroke="{GRAY}" stroke-width="1.6" '
    f'marker-end="url(#arrow)"/>')
mid_a = math.radians(63)
text(cx + (arc_r + 20) * math.cos(mid_a), cy - (arc_r + 20) * math.sin(mid_a),
     "&#916;&#952;", size=17)
panel_label(cx, cy, "(b) Shifted")

# ---- Panel (c): Segmented ---------------------------------------------------
cx, cy = PANEL_CX[2], PANEL_CY
panel_circle_outline(cx, cy)
seg_off = R * 0.32
bx, by = cx - seg_off, cy
rx, ry = cx + seg_off, cy
for ang in (90, 210, 330):
    coil_spoke(bx, by, ang, R * 0.46, BLUE)
    coil_spoke(rx, ry, ang, R * 0.46, RED)
dot(bx, by, 5, BLUE)
dot(rx, ry, 5, RED)
panel_label(cx, cy, "(c) Segmented")

# ---- Legend -----------------------------------------------------------------
leg_y = H - 32
leg_x0 = PANEL_CX[0] - 40
dot(leg_x0, leg_y, 6, BLUE)
text(leg_x0 + 16, leg_y + 6, "Winding group 1", size=17, anchor="start")
leg_x1 = PANEL_CX[1] + 60
dot(leg_x1, leg_y, 6, RED)
text(leg_x1 + 16, leg_y + 6, "Winding group 2", size=17, anchor="start")

add('</svg>')

out_svg = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fig_winding_options.svg")
with open(out_svg, "w", encoding="utf-8") as f:
    f.write("\n".join(svg_parts))
print("Saved", out_svg)

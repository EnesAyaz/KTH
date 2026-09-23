"""Circular vertical CWTUM geometry screen, NOT a drilling release.
Excludes closure, cable, copper topology and mechanical obstructions.
One candidate shape only; these are not universal hole-spacing bounds.
"""
import json
import math
from pathlib import Path

rows = []
for circumference in (80.0, 83.0):
    radius = circumference / (2 * math.pi)
    rows.append(dict(
        circumference_mm=circumference,
        bend_radius_mm=radius,
        face_intersection_pitch_mm=2 * math.sqrt(radius**2 - 0.8**2),
        outer_envelope_diameter_mm=2 * (radius + 0.85),
        protrusion_beyond_each_board_face_mm=radius + 0.85 - 0.8,
        two_coplanar_circles_at_18mm_centres_intersect=18 < 2 * radius,
    ))
result = dict(
    status='Geometry study only; not installation or electrical validation',
    source='PEM CWTUM dimensions March 2024 issue 03',
    assumptions='Vertical circular winding centred at PCB mid-plane; 1.6mm board; 1.7mm maximum winding diameter',
    cases=rows,
    outstanding=['Closure and free-end passage', 'Two-channel winding collision',
                 'Signed current crossings on all copper layers',
                 'Cooling and underside clearance', 'Complete loop-inductance comparison'],
)
# Elevated circular candidates preserve bend radius while narrowing the
# board crossing. These are winding-only slot envelopes, not drill sizes.
elevated = []
for circumference in (80.0, 83.0):
    r = circumference / (2 * math.pi)
    wire = 0.85
    zc = r - 0.8 - 1.0 - wire
    xmin = math.sqrt((r-wire)**2 - (-0.8-zc)**2)
    xmax = math.sqrt((r+wire)**2 - (0.8-zc)**2)
    elevated.append(dict(
        circumference_mm=circumference,
        circle_centre_above_midplane_mm=zc,
        positive_x_slab_intersection_mm=[xmin, xmax],
        negative_x_slab_intersection_mm=[-xmax, -xmin],
        slot_y_width_without_clearance_mm=2*wire,
        winding_top_above_board_top_mm=zc+r+wire-0.8,
        winding_bottom_below_board_bottom_mm=2.7,
        underside_clearance_to_upper_surface_of_bottom_arc_mm=1.0,
    ))
result['elevated_circular_candidates'] = elevated
result['elevated_candidate_limitations'] = (
    'Paired slot envelopes exclude assembly clearance and closure passage. '
    'Circles at 18mm branch pitch intersect if coplanar; spatial separation is required. '
    'Narrower board crossings retain the 10mm minimum bend radius but do not resolve '
    'enclosed return current, component collisions or heatsink interference.'
)
out = Path(__file__).resolve().parents[1] / 'docs/p8-coil-geometry-screen.json'
out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))

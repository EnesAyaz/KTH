# P6 mechanical candidate

Separate candidate in `hardware/epc2361-prototype-p6-mechanical`; source P5 is preserved. Open the PCB in KiCad and its 3D viewer to see the raised spreader envelope. `p6-mechanical-drawing.svg` gives a plan and stack section. This is a fit study, not a machining drawing or qualified liquid cold plate.

## Arrangement

Board outline remains x5..83.5,y5..56 (78.5x51mm). Two separate spreader rails cover x38..76, with upper y6..33.25 and lower y36.75..55. Underside z9mm, thickness3mm is a geometry starting point. Four boss feet4x2mm are centered on QH1(48,32),QL1(48,38),QH2(66,32),QL2(66,38), with nominal bottom z1.05mm. Each foot is smaller than the4.47x2.60mm exposed die; lateral alignment remains subject to tolerance review.

Each source-connected device top requires insulating TIM. The model shows a5.5x3.5mm TIM envelope, nominal free thickness0.5mm and illustrative compressed thickness0.35mm. No TIM material has been selected. Its dielectric, thermal and compression properties must be verified.

Support holes are Ø2.4mm NPTH at(40,8),(74,8),(40,53),(74,53), provisionally for M2 hardware. The drawn5mm hardware envelopes do not specify washer, torque or insulating-bushing selection. Plate bolt openings in the3D envelope are rectangular approximations; they are not machining definitions.

Gate access windows are x39.2..42.8 and57.2..60.8, y29..40. Probe windows are x50.8..54 and68.8..72, y29..40. These preserve vertical access to the P5 gate headers and drain/source probe pads. The9mm underside addresses unmated component heights only; plug shells, cable exits and probe-tip geometry still need physical checks.

## Current probe compatibility

The parent review identified the selected PEM CWT Ultra Mini with80mm circumference,1.6mm cable and10mm minimum bend radius. An upright circular centreline has radius12.73mm. At y35, centered x55, an outer cable bottom z1mm gives an outer top about28.06mm. The actual closing head and cable exit must also fit; a circular envelope alone does not establish compatibility.

The full-width3.5mm gap y33.25..36.75 permits the upright cable through the spreader plane, with nominal0.95mm lateral clearance each side. A continuous plate at z9mm would intersect it. The candidate therefore uses two separate rails. The raised current link is part of the parent layout work, not this mechanical PCB.

Each separate rail has only two mounting points far from its contact row. This leaves a cantilever and uncertain preload. A rigid external frame, additional near-contact supports or an engineered spring/clamp arrangement is required before assembly. Rail thickness and window ligaments need strength/flatness calculations; four depicted bolts alone do not qualify contact pressure. The envelopes represent spreaders to interface with cooling hardware, not finished pressure-containing liquid blocks.

## Stack tolerance

EPC package height is0.60..0.70mm. Assume, for this study only, solder standoff0.02..0.08mm above the PCB. Boss bottom1.05±0.05mm then gives0.22..0.48mm TIM gap:4..56% compression of nominal0.5mm TIM, before TIM thickness tolerance, PCB warp and plate flatness. That range is not an acceptable released assembly specification.

Measure assembled device-top heights and select TIM using its supplier compression curve. Set final gap with measured/shimmed supports. A provisional20..30% compression target would mean0.35..0.40mm gap for exactly0.5mm TIM, but the material supplier must approve the actual range and force. Do not pull the PCB into the plate using screw torque to absorb an uncontrolled gap. Add backing support so mounting load does not bend the PCB/ceramics or concentrate force on device corners.

## Clearance evidence

The generator scans existing track/via widths and pad bounding boxes against each drilled-hole edge. Minimum existing copper-feature distances are2.010mm at(40,8),12.322mm at(74,8),2.505mm at(40,53),2.648mm at(74,53). There is no direct track/pad drilling collision in the scanned P5 data. The scan excludes copper zones and is not an insulation check. Refill zones and run DRC after integration, providing clearance for all mounting hardware rather than just the drill.

This separate PCB adds holes, non-copper outlines and a3D mechanical envelope only; P5 tracks are preserved. Recheck these results after sensing/layout revisions. Thermal losses, TIM/spreading resistance, coolant temperature/flow, fluid fittings, pressure integrity, insulation, mounting force and rail stiffness remain unverified. No thermal capability or maximum-current rating is established by this study.

Validation on the saved candidate: after zone refill, KiCad7 reports zero electrical DRC errors and zero unconnected pads. Five warnings identify generated mechanical footprints without library IDs. This confirms the new holes clear refilled copper under current design rules; it does not qualify mounting-hardware insulation or loading.

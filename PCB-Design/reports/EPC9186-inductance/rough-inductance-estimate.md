# EPC9186 rough loop-inductance estimate
## Scope and confidence
Analytical engineering estimate using Gerber placement geometry and an assumed stackup, not a 3D field-solver extraction. The approximate Gerber preview handles linear paths, regions and approximate macro apertures, but is not polarity/connectivity accurate; it is used only for placement and distance context. No routed net length, return-plane continuity or layer connectivity is claimed to have been fully extracted. Ranges below are sensitivity allowances, not statistical confidence limits.

Applies to the supplied B5453 Rev1.0 Gerbers and EPC2302 BOM. The downloaded quick-start guide covers newer revisions/variants and is not used to assign copper geometry. No PCB or simulation files have been changed.

## Geometry observations
Top-layer aperture D92 contains 0.700 x 3.600 mm pads. Their repeated groups, together with the overlay, identify four device columns approximately 10 mm apart and opposing switch rows approximately 10 mm apart. The underside driver is to the left of those columns. The nearest/farthest driver-to-device route lengths are therefore approximated as 15/45 mm, with intermediate 25/35 mm routes; these are assumed electrical lengths informed by placement, not traced route measurements.

## Assumed ten-layer stackup
Nominal total thickness 1.60 mm, excluding soldermask.
Outer copper: 70 um each. Eight inner copper layers: 35 um each.
Nine dielectric gaps top-to-bottom, mm:
0.10 / 0.12 / 0.14 / 0.15 / 0.16 / 0.15 / 0.14 / 0.12 / 0.10.
Copper totals 0.42 mm and dielectric totals 1.18 mm.
Critical assumption: the main high-frequency return lies in the adjacent layer. Sweep the relevant outer gap from 0.075 to 0.20 mm. A remote return or slotted plane can produce values outside the stated ranges.

## Calculation
For broad overlapping paths:
L(nH) = 1.256637 * spacing(mm) * length(mm) / effective_width(mm).
This estimates external loop inductance of the paired conductors; the return must not be added again. Finite-width effects, current spreading and coupling make this approximate, particularly for gate paths. Copper thickness mainly affects resistance/internal inductance here and is not explicitly present in this high-frequency external-inductance formula.

Power loop, representative local commutation path:
Assumed effective overlap length 20 mm, width 5 mm, spacing 0.10 mm.
Planar contribution = 0.503 nH.
Assumed via/vertical transition allowance = 0.7 nH.
Assumed pad constriction/current-spreading allowance = 0.8 nH.
Total = 2.003 nH, rounded to 2 nH PCB-only.
Use 1-4 nH as an initial exploration range. The 0.7 and 0.8 nH allowances are engineering assumptions, not separately extracted quantities. Neither capacitor intrinsic ESL nor package/internal inductance is included.
This is a representative local branch loop; it is not a demonstrated equivalent inductance of the four-device parallel bank. Shared paths and mutual coupling prevent simple division by four.

Gate loop, each individual FET:
Assume adjacent return spacing 0.10 mm and effective width 0.70 mm.
Assume 2 nH for transitions and local gate/return routing beyond the long paired section.
Position from driver | assumed route length | planar term | PCB gate-loop estimate
1 nearest | 15 mm | 2.69 nH | 4.69 nH
2 | 25 mm | 4.49 nH | 6.49 nH
3 | 35 mm | 6.28 nH | 8.28 nH
4 farthest | 45 mm | 8.08 nH | 10.08 nH
Practical exploration brackets respectively: 3-8, 4-12, 5-16 and 6-20 nH.
These are independent-path approximations. The gate network shares driver-side conductors and has distinct source/sink paths. A full model needs common segments, branch segments, source return and mutual coupling. Do not simply place all four estimates in independent branches if accurate current sharing is the objective.
Driver and transistor internal/package inductances are excluded.

## Suggested LTspice exploratory cases
For a single representative device pair:
LGATE: 5n, 10n, 20n (near, far, pessimistic sensitivity cases).
LPOWER: 1n, 2n, 4n (PCB loop).
LCAP: retain a separate placeholder, e.g. 0.5n, until the selected capacitor bank impedance model is available.
LCAP=0.5n is NOT extracted from this BOM. Do not divide an arbitrary single-capacitor ESL by all 72 bulk capacitors; shared connections and uneven high-frequency participation matter.
With nominal LPOWER=2n and placeholder LCAP=0.5n, simulated total interconnect-plus-capacitor loop = 2.5 nH, excluding any separately added package terms.
These EPC9186 assumptions must not be presented as extracted values for the user's compact EPC2361/LMG1210 PCB.

## What would change the estimate most
Actual return-layer assignment/spacing; exact driver-to-gate/source paths; via return pairing; which local/bulk capacitors participate; shared conductor mutual coupling. A numerical field solution has not been performed. Absolute accuracy cannot be guaranteed from these assumptions; roughly factor-of-two variation is plausible and poor return continuity can be worse.

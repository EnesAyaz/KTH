# Pole-flux balance and published yoke context

## Current rotor

The exploratory rotor has repeating sector symmetry, but PM and wound sites are not identical magnetic poles. Pole-integrated radial air-gap flux was evaluated at r = 80.5 mm, integrating over each physical site's 30-degree mechanical pitch. Since stack length is unspecified, values are flux per unit axial length, Wb/m, not total Wb.

| Mode | Typical absolute flux at PM site | Typical absolute flux at wound site | Interpretation |
|---|---:|---:|---|
| 12-pole | 0.0135 Wb/m | 0.0162 Wb/m | Wound-pole flux approximately 20% higher; individual pole amplitudes are not yet balanced. |
| 6-pole | 0.0150 Wb/m | 0.0176 Wb/m | Adjacent same-polarity PM and wound sites combine to about 0.0326 Wb/m per magnetic pole. Their constituent contributions differ, but the six combined pole fluxes are approximately equal. |

These values are calculated from the retained baseline nonlinear FEM fields, not from separate PM-only/field-only nonlinear superposition. Saturation means these contributions cannot generally be separated by adding independent source solutions. "PM site" and "wound site" refer to where the air-gap flux is integrated, not an assertion that all flux at a site comes only from its local source.

The approximately 20% high-mode imbalance and the residual spatial harmonics are reasons to optimize rotor excitation and geometry. Balanced stator winding phasors do not prove balanced rotor-field amplitudes. Matching integrated high-mode pole flux and controlling harmful harmonics should precede loaded torque/loss performance claims.

## Published yoke context

Drexler et al., *Advances in electric motors: a review and benchmarking of product design and manufacturing technologies*, 2025, DOI 10.1007/s00502-025-01331-3, reports a yoke-thickness sample of 34 traction motors in Fig. 11(b), PDF page 10:

- Mean 18.60 mm; range 11.2–27.35 mm.
- BMW iX1 xDrive30 Premium: 11.2 mm.
- Tesla Model Y AWD Standard Range front motor: 27.35 mm.

Source: https://www.hub-edrive.de/fileadmin/media/Publikation/Advances_in_electricmotors.pdf

The authors use databases, teardown studies and literature to benchmark production motors. These are mostly passenger-EV machines, not directly matched truck HE-IPM designs. The range is useful context for a 15–20-mm initial search, not a sizing criterion. Actual pole flux, bore, stack length, steel curve, armature loading, cooling and mechanical constraints must determine final dimensions.

## Working decision

Retain 15 mm as a compact candidate for the next loaded comparison and 20 mm as the more conservative sensitivity. Neither is declared optimal. The 10-mm case has less yoke flux margin in the 6-pole mode and remains a lower-bound sensitivity. The existing Word digest has not been silently changed to a new geometry by these diagnostics.

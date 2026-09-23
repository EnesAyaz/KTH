# P1 analytical commutation-inductance estimate

Calculated 2026-09-21 from `scripts/build_cell_p1.py`. This is a geometry-based screening calculation, not a field extraction or a measured total.

## Result

The broad-plane envelope gives **0.24-0.48 nH** for the PCB path under deliberately optimistic current-spreading assumptions. Inspecting the actual 0.5 mm comb connections instead gives approximately **0.39 nH for those exposed comb segments alone**. Capacitor branches, broad rails, lateral redistribution, vias, solder and internal device current paths remain additional regions. Consequently **0.24 nH must not be presented as the actual layout inductance**. A defensible complete-loop number cannot be established from this hand calculation alone.

Six top capacitors contribute **0.080 nH capacitor-only** in an ideal equal-current, uncoupled model, using the TDK simple-model 0.480 nH/component. Twelve give 0.040 nH only if the bottom branches are equally effective; this is not justified for the present stackup.

## Geometry and formula

- F.Cu / In1.Cu dielectric: 0.100 mm; copper thicknesses 0.070 / 0.035 mm.
- Capacitors: y = 10 mm, x = 9.75, 11.85, 13.95, 16.05, 18.15, 20.25 mm.
- Main capacitor negative vias: y = 7.8 mm (additional vias y = 7.1 mm).
- High-side centre: (15,16) mm; low-side centre: (15,22) mm.
- Low-side source vias: y = 25.8 mm.
- Return polygon extends x = 11.7 to 21 mm over the device region: 9.3 mm width.
- Actual current is funnelled into three 0.5 mm drain fingers and three 0.5 mm source fingers for each device; the plane width is not the effective forward width.

For closely spaced overlapping opposing currents:

`L[nH] = 1.256637 * h[mm] * length[mm] / width[mm]`

This includes the return and magnetic cancellation; do not double length for the return or add an independent plane self-inductance. It assumes width much greater than separation, uniform current, negligible end effects, and no holes or constrictions. Dielectric permittivity does not multiply this magnetic inductance.

Reference: [University of Texas, parallel-strip transmission line, equation 6.70](https://farside.ph.utexas.edu/teaching/315/Waves/node44.html).

## Broad envelope: optimistic screening only

Taking length = 25.8 - 7.8 = 18.0 mm and h = 0.100 mm:

| Assumed continuously conducting forward width | Result |
|---|---:|
| 9.3 mm, full return-polygon corridor | 0.243 nH |
| 4.7 mm, approximate power-pad spread | 0.481 nH |

Neither width describes a continuous solid top plane through the FETs. This calculation is a comparison baseline, not a rigorous lower bound and not an extracted PCB value. The 18 mm envelope also crosses capacitors/device regions where a PCB-only parallel-plate model does not describe the physical current path.

## Actual narrow external combs

Use the pad edges, not pad centres: the main EPC copper lands extend approximately 1.8 mm above/below each device centre. These short portions lie outside the device land arrays.

For three equal parallel fingers, neglecting mutual coupling, approximate effective width as 3 x 0.5 = 1.5 mm. This approximation is deliberately explicit: coupled, unequal finger currents need a field solution.

| Segment | External length | Effective width | Approximate L |
|---|---:|---:|---:|
| High-side drain bar y13.2 to land edge y14.2 | 1.0 mm | 1.5 mm | 0.0838 nH |
| High-side source land edge y17.8 to AC bar y19 | 1.2 mm | 1.5 mm | 0.1005 nH |
| AC bar y19 to low-side drain edge y20.2 | 1.2 mm | 1.5 mm | 0.1005 nH |
| Low-side source edge y23.8 to bar y25 | 1.2 mm | 1.5 mm | 0.1005 nH |
| **Subtotal, these external combs only** | **4.6 mm** | | **0.3854 nH** |

The edges have rounding and the leftmost source land differs slightly in length; this precision describes arithmetic, not model accuracy. Fringing, mutual coupling, interdigitated drain/source current, lateral current in each 1 mm bar and nonuniform current sharing are omitted. Do not add this subtotal to the broad-envelope estimate: they are alternative descriptions of overlapping regions.

Other explicit copper features still to model include the six 0.85 mm capacitor necks, DC+ spreading from the 10.5 mm capacitor-row span to the roughly 3.6 mm drain-bar span, negative-capacitor mounting paths, and the six 0.55 mm source-to-via fan-outs. A nominal figure such as 0.5 nH for PCB copper could be used only as an unverified simulation trial, not as the calculated total.

## Capacitor ESL and bottom bank

For six identical uncoupled top branches:

`L_cap_only = 0.480 / 6 = 0.080 nH`

Mounting and shared copper are excluded. Source: [TDK C2012 model table](https://product.tdk.com/system/files/dam/technicalsupport/tvcl/pdf/capacitor_mlcc_com_midvoltage_c2012_ecm.pdf), C2012X7S2A105K125AB. The model L is typical, not a guaranteed mounted maximum. See `docs/capacitor-selection-p1.md` for voltage-bias and ripple limits.

The bottom capacitors connect through a roughly 1.6 mm board; the DC-minus return is near the top, on In1. Their transition path is therefore much longer than a top capacitor's F.Cu-to-In1 return. They must not simply be counted as twelve equally effective high-frequency capacitors. Bottom-bank advantage requires impedance extraction with the actual via geometry. Through-via barrel segments below a top-to-In1 current transfer are stubs rather than the entire series-current path; using full barrel self-inductance for each top branch would also be wrong.

## Practical interpretation

The narrow combs already account for around 0.39 nH in this approximate model, and ideal top-bank component ESL adds 0.08 nH. Thus **about 0.47 nH accounts only for these selected regions**, not the full loop. This subtotal is not a rigorous lower bound because the approximations omit coupling and fringing. No package or via inductance was invented to turn it into a falsely precise total.

At 51.9 A changing in 10 ns, an assumed total 1 nH would contribute about 5.19 V through L di/dt. An assumed 0.5 nH would contribute 2.60 V. These are sensitivity examples, not predictions of Vds peak or measured slew rate.

Next: extract the actual coupled structure with ports across the local capacitor terminals and device power terminal groups, include capacitor models without double-counting their mounting structures, then check using a controlled double-pulse test. Evaluate the six-cell common buses separately: six local loops do not remove shared-bus inductance.

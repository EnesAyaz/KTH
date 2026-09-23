# P2 prototype: analytical local power-loop estimate

2026-09-21. Geometry source: `scripts/build_prototype_board.py`; same local power geometry as P1, translated and rotated. Scope: **four EPC2361 devices, two in parallel per switch, 75 V bus, 36.7 A RMS total sinusoidal output**. This is an analytical screening estimate, not electromagnetic extraction or a verified loop-inductance measurement.

## Geometry actually used

The left local loop is rotated 180 degrees using `(x,y) -> (49-x,54-y)`. The right is translated using `(x,y) -> (41+x,16+y)`.

| Feature | Left loop | Right loop |
|---|---|---|
| High-side centre | (34,38) mm | (56,32) mm |
| Low-side centre | (34,32) mm | (56,38) mm |
| Capacitor row | y44 mm, x28.75 to39.25 mm | y26 mm, x50.75 to61.25 mm |
| Capacitor negative main via row | y46.2 mm | y23.8 mm |
| Low-side source via row | y28.2 mm | y41.8 mm |
| AC comb bar | y35 mm | y35 mm |

Each capacitor row has six 1 uF/100 V 0805 candidates, all on F.Cu. Each FET pair has 6 mm centre spacing. Each forward/return envelope spans 18 mm between capacitor negative main vias and source vias. F.Cu/In1.Cu dielectric spacing is 0.100 mm; nominal copper thicknesses are 0.070/0.035 mm. The three drain and three source fingers are 0.5 mm wide; transverse bars are 1 mm wide. The DC+ top polygon spans 11.9 mm at its broad section; the capacitor centre span is 10.5 mm. These are not the effective width through the narrower FET connections.

In1.Cu is the common DC-minus plane. In2.Cu is the DC-plus collector; B.Cu carries the AC collector. Shared collector inductance and current redistribution are additional to the local-loop estimate. The large common return plane does not mean the forward current spreads uniformly over its entire width.

## Formula and local estimates

For a broad conductor over a closely coupled return:

`L[nH] = 1.256637 * h[mm] * length[mm] / width[mm]`

It already includes forward and return magnetic cancellation. Do not double length or add independent return-plane inductance. Width must be much larger than separation; finite ends, current crowding, slots, package current and via transitions are excluded. [Parallel-strip derivation, equation 6.70](https://farside.ph.utexas.edu/teaching/315/Waves/node44.html).

An artificial continuous forward width of 9.3 mm over 18 mm gives **0.243 nH**; 4.7 mm gives **0.481 nH**. These are only envelopes for comparison with P1. P2 does not possess that continuous forward plane through the devices, so neither is the actual complete-loop result or a rigorous lower bound.

A more informative partial calculation uses the actual external narrow fingers. EPC main copper lands extend approximately 1.8 mm above/below each device centre. Treating three equal 0.5 mm fingers as a 1.5 mm effective width, while neglecting mutual coupling between them:

| External section, per local loop | Length | Approximate L |
|---|---:|---:|
| High-side drain bar to upper drain land edges | 1.0 mm | 0.0838 nH |
| High-side source land edges to AC bar | 1.2 mm | 0.1005 nH |
| AC bar to low-side drain land edges | 1.2 mm | 0.1005 nH |
| Low-side source land edges to return bar | 1.2 mm | 0.1005 nH |
| **External comb subtotal** | **4.6 mm** | **0.3854 nH** |

Rotation does not change this local geometry. Both loops therefore have the same nominal partial estimate. Real currents need not split equally between the three fingers or between the two cells. The 0.3854 nH is arithmetic precision, not model accuracy. Do not add this number to the plane-envelope results: they describe overlapping regions.

Still excluded: capacitor necks, lateral bar currents, DC+ spreading, source-via fan-outs, via transitions, solder, device internal current paths, inter-region coupling and common collectors. These omissions prevent a reliable complete-loop numerical claim.

## Capacitor-only contribution

The selected TDK C2012X7S2A105K125AB simple model specifies typical L1 = 0.480 nH/component. [TDK model table](https://product.tdk.com/system/files/dam/technicalsupport/tvcl/pdf/capacitor_mlcc_com_midvoltage_c2012_ecm.pdf).

Six ideal equal, uncoupled capacitor branches per local loop give:

`L_cap_local = 0.480/6 = 0.080 nH`

Thus the selected external combs plus ideal component ESL total **approximately 0.465 nH per local loop**. This is a partial model, not the full layout inductance and not a rigorous lower bound. Mutual coupling and unequal branch currents can change the result. Nominal 6 uF per local bank is not effective capacitance at 75 V; bias and ripple heating remain unqualified.

All twelve capacitors are top-side in P2, so the P1 bottom-bank long-transition caveat no longer applies. Nevertheless, treating all twelve as one ideal 0.040 nH bank excludes their two distinct mounting paths and common network. It is not the inductance seen by either FET pair.

## Two parallel coupled loops

For two identical complete local loops of self-inductance L, equal currents, and signed mutual inductance M:

`L_eq_local = (L + M)/2`

This follows from `v = L*di1/dt + M*di2/dt` with `i1=i2=I/2`. With `M=kL`, it becomes `L_eq_local = L*(1+k)/2`. The sign of M depends on actual field orientation and current references. A rotated drawing alone does not establish its sign or magnitude.

- M = 0: local contribution halves.
- Positive M: the reduction is smaller.
- Negative M: ideal local reduction is larger, but cannot be assumed without extraction.

With a distinct common current path:

`L_seen = L_common + (L + M)/2`

This compact formula assumes L_common is separable; it omits coupling of common collectors to local loops. A full network model needs the inductance matrix and actual terminal current distribution.

For arithmetic illustration only, applying M=0 to the incomplete 0.465 nH local model gives 0.233 nH for those selected regions at total-current reference. **It does not establish a 0.233 nH module loop.** The complete L and M are unknown, and common collector inductance is not divided by two.

## Current and overshoot sensitivity

At 36.7 A RMS sinusoidal output:

- Total peak current: `36.7*sqrt(2) = 51.9 A`.
- Ideal current per parallel branch: **25.95 A peak**.

Use 25.95 A for each local branch, not the earlier 51.9 A per-branch assumption. If one local branch changes by 25.95 A in 10 ns, an assumed complete local 1 nH would contribute about **2.60 V**; an assumed 0.5 nH would contribute 1.30 V. A shared 1 nH carrying the full 51.9 A change in 10 ns would contribute 5.19 V. These are L di/dt sensitivity examples, not a Vds peak prediction or a measured switching time.

## Engineering conclusion

The local geometry remains a reasonable low-inductance starting arrangement, but its narrow interdigitated pad escapes are materially different from a solid parallel plate. Use approximately 0.39 nH external-comb contribution and 0.08 nH ideal capacitor-component contribution **as explicitly partial estimates**. Before claiming a complete value, extract both local loops and common collectors together, include capacitor models without double-counting mounting regions, then validate switching waveforms in controlled testing.

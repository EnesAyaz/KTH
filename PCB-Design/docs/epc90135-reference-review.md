# EPC90135 reference review and next-revision decisions

Reviewed 22 September 2026 against the user-provided EPC90135 schematic, BOM, quick-start guide and extracted Gerber package. These files are engineering references; their instructions to EPC's fabricator do not govern this project.

## Scope and verified findings

The reference is four parallel half-bridge cells (eight EPC2218s), sharing VIN, VSW and GND and one uP1966E driver. It is not a conventional full bridge with two independent switch nodes. Our target remains two EPC2361s per switch, four total, 75 V maximum bus, 36.7 A RMS / 51.9 A peak prototype output, 50 kHz nominal and 100 kHz maximum.

The reference guide specifies 80 V maximum bus and a conditional 45 A output rating. Its thermal tests and other plotted currents are test conditions, not a transferable connector or continuous-current rating.

Gerber evidence: GTL + G1 through G6 + GBL establish eight copper layers. GTP and GBP both contain populated paste artwork (195 and 141 D03 flash commands respectively; these are not component counts). The schematic explicitly marks J3 for bottom-side installation. The supplied layout PDF has 18 pages; page 1 was visually inspected. Exact dielectric thicknesses in the legacy XLS stackup have not yet been decoded, and no extracted loop-inductance result is claimed.

## Component and mechanical decisions

| Function | Reference evidence | Decision for our board |
|---|---|---|
| Gate driver | One uP1966E; separate turn-on and turn-off outputs; per-FET 1 ohm turn-on and 0 ohm turn-off resistors | Retain LMG1210 as the current baseline pending detailed placement comparison. Preserve individual damping footprints. Do not substitute the driver solely because the reference has a similar current rating. |
| Local HF capacitors | Seven HMK107C7224KAHTE, 220 nF / 100 V / 0603, per cell; 28 total | Screen a small local 0603 bank in addition to the 0805 reservoir. Compare mounted ESL and effective capacitance at 75 V before changing the BOM. A smaller package alone does not establish lower total loop inductance. |
| Intermediate capacitors | Ten AVX 08051C105K4Z2A, 1 uF / 100 V / 0805 | Keep the distinction between the closest commutation capacitors and supplementary reservoir capacitance. Do not divide all capacitor ESLs by total quantity irrespective of routing. |
| Power connection | J3, Amphenol 67997-272HLF; 24 installed contacts, eight per net | Use the same general 2.54 mm parallel-header style, with a verified mating receptacle and current-sharing/temperature test. Keep DC+/DC- on the left and AC on the right as requested. |
| Thermal supports | Four Wurth 9774010243R, 1 mm threaded M2 supports | Use a four-point mounting concept, but calculate support height from EPC2361 height, TIM compression and tolerances. Do not copy the 1 mm height without checking. |
| Heat spreader | Custom 32 x 32 mm spreader, insulated TIM, M2 screws | Adapt spreader footprint to our four FET positions; reserve probe access and clear tall gate headers. The existing wide P5 FET spacing and top headers are not yet a checked mechanical fit. |

### Driver voltage margin

The uP1966E datasheet gives 85 V absolute maximum for both PHASE-to-GND and BOOT-to-GND. A 75 V switch node with approximately 5 V bootstrap supply puts BOOT near 80 V before overshoot, leaving only approximately 5 V to the absolute limit. This is a strong reason to retain the LMG1210's higher-voltage architecture for the present prototype. Absolute maximum is not a design operating target. The EPC guide also contains an erratum stating boost operation is unsupported; the reference is not blanket validation for bidirectional operation.

The reference's 1 ohm / 0 ohm split-output network cannot be copied literally onto LMG1210's single output per channel. Individual series resistor footprints remain useful for tuning and isolating each gate branch. Onboard drive must be disconnected before an external driver is attached to a gate/source access header.

### Connector discrepancy to resolve before purchasing

The BOM describes a two-row, 12-position installed header, while Amphenol's exact 67997-272HLF product page describes a 72-contact, two-row strip. The schematic uses pins 1-8 for VIN, 9-16 for VSW, and 17-24 for GND. A cut-to-length strip is a plausible explanation, not confirmed assembly documentation. The manufacturer page presently lists 5 A, whereas distributor data encountered during the review lists 3 A. Use the manufacturer's full product specification and the selected receptacle's derating data before approval; neither number times the number of pins proves the assembled rating.

At 36.7 A RMS, eight equally sharing AC contacts would each carry 4.59 A RMS; 24 contacts would each carry 1.53 A RMS. These are arithmetic averages only, excluding unequal contact resistance, mating limits and local heating. The existing P5 choice of 24 contacts per power net provides more sharing opportunities than the reference's eight; downsizing is not justified by the reference alone.

### Cooling

The reference recommends electrically insulating TIM, for example t-Global TG-A1780 at 0.5 mm nominal thickness, and no more than 2:1 compression. It warns that the FET backside is source connected and the high-side device therefore sits at switch-node potential. It also uses a separate thin insulating sheet around the TIM and a controlled grounded mounting point. Verify these details against the EPC2361 package before final mechanical release.

The guide's tested heatsink is Wakefield-Vette 567-24AB with a spreader, whereas the optional BOM lists 960-31-33-S-AB-0. Those are different assemblies; do not represent them as the same qualified cooling solution. A liquid cold plate can replace the external heatsink while retaining the insulated, tolerance-controlled spreader interface. The reference asks removal of components over 1 mm under its spreader; our selected capacitors and headers require explicit height and keepout checks.

## Four-layer adaptation and measurement

Use top-side short FET/capacitor connections over a nearby uninterrupted power-return layer. Preserve adjacent-layer gate/source routing with controlled return paths. Moving the driver or auxiliary components underneath may free the top for cooling, but gate vias and a four-layer stack must be evaluated together; an eight-layer layout cannot simply be collapsed into four layers. Separate 12 V and 5 V driver copper from the DC+ bus while sharing the intended DC- reference.

The present P5 holes enclose an AC/output-current conductor. They do not measure an individual device's commutating current. For the requested device-current measurement, the next revision needs an explicitly named sensing branch, initially one low-side FET source: all power source pads of that FET must reach DC- through a sole coil-linked conductor, with no parallel plane/via bypass. Take the gate-driver reference from the device side of that conductor. This adds common-source parasitics and changes current sharing, so measure/model the instrumented arrangement separately from the compact reference arrangement. A common two-FET source bridge instead measures bank current, not individual FET current.

Reserve adjacent drain/source spring-tip contacts outside the spreader edge or behind dedicated probe-access openings. High-side VDS probing requires a suitably rated differential/isolated probe. Final PEM coil holes depend on coil closure and bend radius as well as cable diameter. A provisional drill diameter cannot establish fit. Output current alone is insufficient for credible switching-energy integration during commutation.

## Status and required continuation

This review does not modify or release P5 for fabrication. The earlier P5 checks established zero copper DRC violations and zero unconnected pads before final mechanical changes, with 221 connected schematic pin assignments checked. Remaining work includes the instrumented device-current path, spreader/support geometry, connector mating qualification, manufacturer four-layer stackup, updated layout/DRC, native ERC, annotated loops, and the requested LaTeX report. Exact component CAD remains incomplete; existing FET and driver models are approximate envelopes.

## Sources

- Local EPC90135_qsg.pdf: pages 2, 6-8 and 12 (topology/rating, cooling, test setup, erratum).
- Local EPC90135_Schematic.pdf: sheets 1-3 (parallel cells, J3 mapping, local capacitors and driver).
- Local EPC90135BOM.xlsx: component and optional mechanical BOM.
- Local EPC90135_B5257_Rev1_0_Gerbers.REP, GTL, G1-G6, GBL, GTP, GBP, and Layout.PDF.
- [uP1966E manufacturer-hosted datasheet](https://epc-co.com/epc/Portals/0/epc/documents/datasheets/uP1966E_datasheet.pdf), pages 1, 5, 7 and 11.
- [Amphenol 67997-272HLF](https://www.amphenol-cs.com/product/67997272hlf.html), accessed 22 September 2026.
- [TI LMG1210 datasheet](https://www.ti.com/lit/ds/symlink/lmg1210.pdf).

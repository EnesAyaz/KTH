# P6 individual-device current measurement plan

22 September 2026. Independent read-only review of P5 construction scripts, the candidate PCB and the EPC90135 reference review. No PCB has been changed by this review. Coordinates below are engineering placement proposals, not released drilling dimensions.

## Decision

Measure QL1 drain current using a separately named `D_QL1` island and one raised copper sensing link to AC. This preserves the existing common low-side source reference and is the minimum electrical-topology change that gives individual device current without a source-return bypass. It adds drain/power-loop inductance and will alter dynamic current sharing. Treat it as an instrumented variant, not the optimized production power loop.

The present P5 holes H1/H2 at (75,27)/(75,43), 3.2 mm NPTH, enclose the AC output bridge. They measure output/inductor current, not QL1 current. Their coil fit remains provisional. P5's candidate DRC report showed zero violations, but that does not qualify these holes mechanically or the current sensor dynamically.

## Why the source-only edit is insufficient

QL1 is centred at (48,38). Its source pads 2/4/6 are presently DC− and connect through these paths:

- The local source comb to y41 and six return vias at y41.8, centred around x45.648,47.575,49.275 with ±0.35 mm offsets.
- The continuous L2 DC− plane through those vias and any new same-net vias.
- JGL1 pin 2, connected directly to source pad 2 by a top trace; a connected external probe/driver can add another return.
- TP9, picked up from source pad 6; its bare copper alone is a stub, but an earth-referenced probe can become a bypass.
- The gate-return pickup via at (43.19,38.67), then the L3 source branch/star to driver VSS near (32.8,35).
- The shared driver source star also returns to QL2/DC−. Driver grounds, bypasses, exposed pad 20, control ground and auxiliary supply ground provide further common-ground connectivity.

Renaming QL1 source to `S_QL1` while leaving any of these conductive paths to DC− bypasses the sensor. Routing a thin Kelvin trace around the coil still provides a bypass; calling it Kelvin does not remove its current. One shared LMG1210 VSS cannot independently reference two sources separated by an instrumented source impedance. The alternatives are separate low-side drivers/references, a common two-device source bridge (bank current only), or accepting un-Kelvin-referenced drive for the isolated QL1 source. The drain-link variant avoids this specific conflict.

## Minimum drain-link implementation

1. Rename only QL1 drain pads 3/5/7 and TP8 from AC to `D_QL1`. Their x positions are 46.725,48.425,50.352; each drain pad spans the device y38 region. Keep QL1 source, gate, JGL1 and TP9 unchanged.
2. Remove the three original QL1 drain fingers joining the AC bar at y35. Keep QH1 source on AC. The builder currently generates the two adjoining devices' conductors together; edit the low-side drain case explicitly, rather than globally replacing AC in the cell.
3. Move the QH1 source AC crossbar from y35 to approximately y34.5, maintaining its source-finger connections. Rebuild the QL1 drain crossbar on `D_QL1` at approximately y35.9, initially 0.4 mm wide, with fingers to the drain pads. These are clearance starting points: the high-current crossbar must be widened or otherwise improved after DRC/current-crowding review. This proposal sacrifices local geometry and has not been electrothermally qualified.
4. Reserve a raised link along x54 from approximately (54,32) AC to (54,38) D_QL1. Relocate the existing AC via cluster at (54,35) so it does not contact or obstruct the link/coil. Route the lower land only to the D_QL1 crossbar; route the upper land only to QH1 source/AC. The six-millimetre span uses the space between the two cells. Check TP7 and TP9 access on x52 and the adjacent gate headers before adopting it.
5. Define the link as a real two-terminal component in the schematic, with distinct AC and D_QL1 pins and a specified copper-link assembly. Do not use a hidden same-net copper short or an unrecorded zero-ohm trace. The physical conductor must be the sole AC↔D_QL1 connection. Keep D_QL1 out of every global AC zone. With the link omitted, D_QL1 must remain a separate connected component from AC in the PCB graph.
6. Use a removable/forked Rogowski coil around the raised link, with enough clearance below the link to install it. A preliminary 2.5–3 mm standoff is only a packaging envelope; actual minimum bend radius, closure and insulating clearances depend on the selected coil. The current 3.2 mm holes cannot simply be copied next to this link: one side conflicts with FET/crossbar/probe geometry. A raised link can provide threading access without board holes. If holes are mandatory, enlarge/rearrange the intercell region and reroute the affected copper first.

No wire diameter, plating, terminal land, solder fillet or assembly height is released by this plan. Select and document the link mechanically, including current pulse capability, resistance, rigidity and clearance to the cold plate. A generic pin-header jumper is not a qualified current link.

## Required audit of the drain variant

- QL1 pads 3/5/7, TP8, the crossbar and link device-side land are D_QL1 on all layers.
- QH1 source pads, AC vias/collector, QL2 drains, JAC1 and the other VDS drain taps remain AC.
- No segment, via, zone fill, thermal relief, probe attachment or mounting hardware bypasses the link.
- TP8 continues to sense the transistor drain on D_QL1. Measuring AC upstream of the link would include the link's L di/dt error in reported transistor VDS.
- The coil encloses the link once and no opposite-current return. Probe calibration, polarity, delay/deskew and bandwidth are recorded.
- Update the power-loop illustration and calculation to include the link. Do not retain the earlier partial 0.47 nH value as the new complete loop inductance. Even a few additional nH materially changes GaN overshoot and current sharing.

The source-to-source current-sharing asymmetry is not solved by the drain variant: one device now has additional drain impedance. Measure the resulting sharing explicitly, or build equally instrumented branches if comparable device-current measurements are needed. A single instrumented device does not establish the behaviour of the unmodified compact design.

## Fabrication status

Not ready for release: exact sensor and link assembly, probe accessory, coil/cold-plate interference, copper current crowding, and revised filled-board connectivity/DRC remain open. A source-current topology retaining the existing shared source-star bypass is specifically rejected. A raised D_QL1 link is electrically coherent but must be implemented and checked before claiming fabrication readiness.

Sources: local `scripts/build_p5_board.py`, `scripts/p5_data.py`, `scripts/route_p5_gates.py`, P5 candidate PCB and DRC, `docs/epc90135-reference-review.md`, and `docs/dpt-measurement-review.md`. Sensor specifications and bandwidth discussion are in the latter, with manufacturer links.

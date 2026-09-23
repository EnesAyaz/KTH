# P3 four-layer allocation and left-side driver review

Reviewed 2026-09-21. This note recommends the requested revision; it does not certify the resulting routed board. Scope: four EPC2361s (two per switch), 75 V maximum bus, 36.7 A RMS / 51.9 A peak total, 50 kHz nominal / 100 kHz maximum. Documents are references, not instructions overriding the user.

## Layer allocation

The first layer is not a continuous DC+ plane. A half bridge needs separate DC+, AC/switch-node and DC- copper on the component face.

| Layer | Recommended function | Constraint |
|---|---|---|
| L1 / F.Cu | Components, short local DC+ to high-side paths, compact AC connection between high-side source and low-side drain, local low-side source/DC- copper; shortest driver bypass and gate escapes | Keep the two local commutation cells compact; do not expand the switching-node island simply to fill empty board area |
| L2 / In1.Cu | Closely coupled DC- power return directly below both local commutation loops | Preserve uninterrupted return under the FET/capacitor power paths; no signal-routing slots through these regions |
| L3 / In2.Cu | Broad DC+ collector from left terminals and bounded AC collector to right; locally reserved source-reference corridors below bottom gate routes | These are separate copper regions, not a single plane. Do not create narrow power bottlenecks by weaving gate/control tracks through the collector |
| L4 / B.Cu | Short paired gate/local-source routing where L1 cannot accommodate it, HI/LI/12 V in the quiet left region; supplemental power copper only outside these corridors | A high-side gate route needs its own AC/local-source return, not DC- as its intended return. Keep corresponding gate and return transitions adjacent |

Propose 0.10 mm dielectric from L1 to L2 and 0.10 mm from L3 to L4, with the thicker core in the middle; confirm an achievable approximately 1.6 mm finished stack with the chosen fabricator. Existing 70/35/35/70 um copper is a starting request, not a proven thermal design. Finished copper and minimum trace/space must be compatible with the fine LMG1210 pitch. The same close outer-to-inner spacing helps both the top power loop and bottom gate-reference routing.

EPC's optimal-loop arrangement relies on a nearby inner return rather than overall board thinness. Changing the outer-to-inner dielectric changes inductance even if the top view is unchanged. [EPC WP010](https://epc-co.com/epc/Portals/0/epc/documents/papers/Optimizing%20PCB%20Layout%20with%20eGaN%20FETs.pdf)

## Placement and gate-return topology

Place the driver on the left edge of the switch group, with its output side facing the FETs; do not move it all the way to the far-left external connector merely for visual alignment. Put DC terminals on the left edge and control/auxiliary pins nearby, but use distinct power and control routing corridors. Upper and lower capacitor rows remain on F.Cu, with each bank returning through nearby DC- vias to L2.

Use one shared output splitting into two independently damped gate branches for each switch. Preserve one gate resistor directly at each FET. Match the two branches' loop geometry, number of transitions and source return treatment; equal trace lengths alone are insufficient. Avoid a daisy chain in which the first gate connection is the feed to the second. A star junction beside the driver is preferable to a long output trace with arbitrary taps, provided it does not force excessive overall length.

Route each gate with a source pickup taken from its own device source pad, before the high-current spreading region. High-side source pickups return to HS; low-side pickups return to VSS. These are Kelvin-style PCB pickups, not a claim that EPC2361 has an independent internal Kelvin-source terminal. Source branches should follow their gate branches and converge at the associated driver return. Adjacent vias should accompany gate layer transitions.

A source return drawn on the same net as a global copper pour is not automatically isolated from power current. Same-net fills can merge with that track all along its length. Where a defined return corridor is intended, keep the collector pour out of the corridor except at deliberate source/driver connection regions, or implement explicit net ties. Inspect filled copper rather than just track centerlines. The high-side return corridor is electrically at the switching node: minimize its area and keep it away from HI/LI and external control pins.

TI calls for short driver-to-gate connections, nearby bootstrap and bypass components, and separation between power/output and input routing. Retain the 100 nF VDD bypass directly at VDD/VSS and the HB/HS capacitor directly at the high-side supply pins. The split exposed pads remain separate HS and VSS nets. [LMG1210 datasheet, layout section](https://www.ti.com/lit/ds/symlink/lmg1210.pdf)

## Labels and manufacturing package

Show every component reference on silkscreen with legible, nonoverlapping placement. Label each external pin by function, not only connector reference: DC+, DC-, AC; HI, LI, +12V and return; GH1/SH1, GH2/SH2, GL1/SL1, GL2/SL2. Keep text off exposed pads, mask openings and M4 terminal hardware. Put full values in the assembly drawing/BOM if all values cannot fit comfortably on silk. Include board revision, pin-1 indications and a layer/stack drawing.

Export copper, solder mask, silkscreen, outline, plated/nonplated drills and top paste from one final saved board. Include stackup, copper, board thickness, surface finish and assembly notes; verify Gerbers against the board. Do not describe passing DRC as fabrication qualification.

## Remaining release decisions

1. Agree fabricator stackup and manufacturing limits; re-run DRC after assigning actual minimum clearance, drills and annular rings. Confirm that the 75 V nominal bus plus measured overshoot is addressed by the spacing/environment assumptions.
2. Review power-via arrays, narrow pad escapes and collectors for resistance, current crowding and temperature rise. Terminal current capability does not rate PCB copper.
3. Verify effective bus capacitance at 75 V and expected temperature, capacitor RMS ripple and external bulk-capacitor interface. Twelve nominal microfarads is not twelve effective microfarads.
4. Review actual gate-loop branch geometry after moving the driver left. This placement change invalidates any assertion that central-driver gate paths remain balanced.
5. Verify package land patterns, mask and paste against manufacturer drawings and reconcile EPC, TI and terminal stencil requirements. Generic 3D bodies do not perform this check.
6. Resolve cold-plate mounting, insulation/TIM, contact pressure and component-height clearance before committing a mechanical production design. A first electrical prototype can be manufactured with an explicit separate cooling fixture plan.
7. Independent-input mode still requires externally enforced nonoverlap and a defined startup/bootstrap-refresh sequence; there is no onboard short-circuit/current-limit shutdown in the current circuit. State the intended current-limited test setup.

Pre-fabrication checks should finish geometry, connectivity, manufacturability and first-test provisions. Final electrical current rating, dynamic sharing, gate overshoot and thermal performance require prototype testing and cannot be proven by Gerbers or DRC. A newly routed board also needs an updated inductance estimate; the prior 0.47 nH subtotal only survives where the same local geometry and stackup survive, and never represented full-loop inductance.

## Actual P3 implementation review (intermediate, 2026-09-21)

The allocation table above is a recommendation, not a statement that every item is already implemented. The initial P3 builder actually uses L1 local islands, a nearly board-wide L2 DC- return, a nearly board-wide L3 DC+ collector interrupted by VDD/AC/VIN/HI/LI routes, and a large L4 AC collector with HO/LO tracks routed around obstacles. It does not provide the recommended isolated source-reference corridors by default.

In the first mirrored P3 placement, measured B.Cu output-via to resistor-via path lengths were HO1 18.36 mm versus HO2 35.54 mm and LO1 20.36 mm versus LO2 44.16 mm. These excluded local F.Cu escapes and were not full gate-loop inductances. The A* routing used a nearest-node tree, not an intentionally balanced star. Independently routed AC on L3 and global DC- on L2 did not establish matched gate/source loops. This was a release blocker even with a clean clearance/connectivity report.

The layout author subsequently changed both switch cells to face their gates left, eliminating crossed high-side/low-side endpoint ordering. The four gate-feed vias are now x43.19 and x61.19, high-side y31.5 and low-side y35.7. The driver remains at (36,35). A new candidate-only routing script, `scripts/route_p3_gates.py`, is being evaluated against that aligned placement. Its output is a separate gate-candidate board, not the primary P3 file. It attempts explicit B.Cu gate stars and nearby L3 source tracks with copper-only exclusion corridors, while leaving the L2 power return intact. Its JSON and DRC report determine whether the attempt succeeded; merely having the script is not evidence that the paired routing is complete. These same-net source traces are not isolated Kelvin nets.

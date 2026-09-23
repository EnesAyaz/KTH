# Revised compact layout and continuous spreader requirements

User reference images and correction, 23 September 2026. These requirements supersede the tall split-rail spreader and raised sensing links of P6/P7. Existing boards remain historical studies, not fabrication releases.

## Thermal arrangement

Use one continuous, low-mounted top heat spreader over the four EPC2361 devices, with electrically insulating TIM and controlled mounting height/preload. A heatsink or liquid cold plate can mount to this spreader. The evaluation board covers the central power stage; its connectors remain accessible at the perimeter. Do not interpret this as a metal plate covering all connectors.

Package-height comparison must include maximum component body height, solder standoff, PCB warp, spreader flatness and minimum assembled clearance. EPC2361 body height is 0.60-0.70 mm. The current C2012X7S2A105K125AB capacitor selection is nominally 1.25 mm tall and cannot simply be treated as lower than these switches. Recheck its tolerance before selecting mounting clearance. Move tall reservoir capacitors outside the spreader footprint or underneath; screen lower-profile local capacitors without lengthening the commutation path. An insulating sheet is not a substitute for mechanical clearance or qualified TIM insulation.

Keep the driver left of the switches as requested; move auxiliary parts underneath where this improves clearance without unacceptable gate-loop routing. Keep gate/source access and VDS spring-tip pads outside the spreader perimeter, close to their devices. Prefer downward-facing or perimeter connectors over tall headers beneath the plate. Recalculate gate return geometry after any move.

## Device-current sensing

Two coils must independently measure QL1 and QL2 current through flat PCB conductors. No raised power links. The preferred mechanical study is to route most of each coil below the PCB, with only its short upper arc above the board, to preserve the continuous top spreader. This is the vertical mirror of the elevated-circle geometry study; it is not yet a validated installed shape. Even that candidate requires about 2.7 mm above-board envelope before installation clearance, so a roughly 1 mm underside spreader would collide unless the sensing aperture lies outside its footprint or a different verified coil shape is used.

Do not drill speculative holes under an overlapping return plane: each complete coil aperture must be audited for current crossing on all four layers. Routing the opposite return outside the aperture can increase loop inductance. Minimize and quantify that change rather than promising an unchanged loop. Both coil assemblies, closures, cables and minimum bend radius must fit simultaneously. Keep any sensing neck outside the FET thermal contact area and as short/wide as feasible; compare its loop against the compact unsensed baseline.

## Compactness and markings

Repack the four-device power stage around the local capacitor banks and common spreader, instead of retaining the old wide pitch by default. Final size follows verified thermal, sensing and connector envelopes; no arbitrary dimension is released. Preserve DC+/DC- and control connections on the left and AC on the right. Use bottom-side population deliberately while retaining the four-layer constraint.

Provide visible DC+, DC-, AC, 12V, HI, LI, GND, gate/source pin assignments, device reference designators, individual QL1/QL2 current-sensing labels, VDS drain/source labels, connector pin-1 marks, board revision and bus-voltage limit. Place labels where readable with the heatsink installed. Check both silkscreens against solder-mask openings, holes, component bodies and mating connectors; do not rely only on electrical DRC.

Next release requires coordinated PCB, schematic, BOM, thermal drawing, current-path audit and report updates. This document changes requirements only; it does not certify existing Gerbers.

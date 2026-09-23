# P7 - two individual low-side current measurements

**Superseded design approach:** the user requested hole-threaded coils around flat PCB current paths instead of raised links. P7 is retained as a previous study and must not be manufactured. See docs/p8-hole-sensing-requirements.md for the corrected constraints; a completed P8 layout does not yet exist.

P7 replaces the single-channel P6 instrumentation. It retains four EPC2361s, two per half-bridge switch. Open epc2361-prototype-p7.kicad_pcb; Alt+3 opens the two-coil and cooling-envelope view. P6 and its fabrication files are preserved as older revisions.

| Current channel | Sole sensing link | Isolated transistor drain | Local VDS contacts |
|---|---|---|---|
| QL1, first low-side MOSFET | LK1 | D_QL1 | TP8 drain, TP9 source |
| QL2, second low-side MOSFET | LK2 | D_QL2 | TP12 drain, TP13 source |

Each link connects AC to only its own transistor drain pads 3/5/7. Both source networks remain DC-minus, preserving the shared driver reference. The obsolete output-current holes H1/H2 are removed. The coils measure individual low-side device drain currents, not output current and not the combined low-side-bank current.

Both branches now use the same local drain-bar and link geometry, translated by 18 mm. Match fabricated link width, thickness, formed height, fillets and solder volume; identical drawing dimensions do not guarantee identical parasitic impedance. LK1 and LK2 are provisional 2 mm wide, 0.5 mm thick copper straps with 6 mm land pitch and 5 mm underside clearance. Raising both links makes space above the AC connector housing; it adds inductance to both measured branches. Characterize this instrumented assembly separately from an optimized compact power stage.

## Simultaneous coil arrangement

Two PEM CWT Ultra Mini winding envelopes are shown in parallel vertical planes at y=34 and y=36 mm, centred laterally at x=55 and x=73 mm. With 80 mm circumference and 1.6 mm winding diameter, their nominal winding-to-winding clearance is 0.4 mm; the outer vertical extent is approximately z=3..30.06 mm. The second coil extends outside the right board edge. Allow that external space in the test fixture.

The cooling-rail opening is widened to y=32.9..37.1 mm. Boss contact footprints are reduced to 4 x 1.6 mm to avoid that opening. Support force, thermal performance and dimensional tolerances must be reassessed. The circular models omit the closing heads and cable exits. They are layout envelopes, not verified sensor fit: simultaneous closure, adjacent AC connector pins and mating plugs remain to be checked against actual sensor CAD/accessories. No fabrication release is claimed.

## Comparing current sharing

Record both currents at the same time, with matched probe models/ranges and oscilloscope settings. Calibrate gains and polarity on the same known conductor, then deskew the channels. Compare both steady conduction and transitions. During an established low-side conduction interval, a useful normalized imbalance is (i_QL1-i_QL2)/(i_QL1+i_QL2); exclude intervals near zero denominator. Do not equate their sum with output current throughout commutation or the high-side interval. Probe response, displacement currents and the inserted link impedances affect fast-edge interpretation.

The earlier P6 report is historical: its single sensing link, coil placement, output holes and link-height calculations do not describe P7. Refer to the current schematic, BOM, dual-current-audit.json, verification.json and final-drc.rpt for this revision. No P7 Gerbers are released; do not order P6 files as the two-channel design.

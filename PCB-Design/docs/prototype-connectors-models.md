# Prototype connectors and 3D model provenance

Scope: 75 V maximum, 36.7 A RMS / 51.9 A peak prototype, two EPC2361s per half-bridge switch. Reviewed 2026-09-21.

## Power connections: DC+, DC- and AC

Recommended candidate: **Wurth Elektronik 74650094**, three pieces. This is a tin-plated brass REDCUBE THR terminal with M4 internal through-thread, 10 x 10 mm body, and eight solder pins. The manufacturer lists 85 A maximum at 20 C; operating current depends on PCB, cable lug and cable cross-section. This is a component rating, not certification of the board's current capability. It has more connector-rating headroom than the four-pin 50 A 74650074.

Use installed KiCad footprint `TerminalBlock_Wuerth:Wuerth_REDCUBE-THR_WP-THRBU_74650094_THR`. Eight electrically common pads numbered 1 use 1.85 mm finished holes, 3.2 mm pad diameter, and 8.87 mm outer spacing. Body thickness is 6 mm. Keep mounting access and lug sweep clear of gate circuitry and the cold plate. An M4 bolt, washer and cable lug are separate hardware, with bolt length chosen after lug thickness and assembly clearance are fixed.

Assembly conditions from the manufacturer: PCB thickness 1.6 to 2.0 mm, 1.2 N m tightening torque, suggested 150 um solder-paste thickness. EPC's finer-pitch stencil may require a stepped stencil or separately qualified terminal soldering process. Support the board during bolting; do not transfer tightening loads into nearby ceramic capacitors.

Sources: [manufacturer datasheet](https://www.we-online.com/components/products/datasheet/74650094.pdf), [manufacturer product and CAD list](https://www.we-online.com/en/components/products/em/redcube_terminals/redcube_thr).

## Gate/source connector

Candidate: **Samtec TSW-102-07-G-S**, a two-position single-row 2.54 mm through-hole header, 0.635 mm square contacts. Suggested footprint `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical`; pin 1 gate, pin 2 local source. Four headers can provide one local pair per FET. Use short paired connections for testing; these are not a recommendation to drive GaN gates through long flying wires. With an onboard driver, do not attach an external driver simultaneously. These pads can instead be populated as test access.

The installed generic header model is a visualization substitute, not the exact Samtec mechanical model. Exact model download requests an email address; no personal data were submitted. Final mechanical dimensions must be compared to the manufacturer's configured drawing before fabrication.

Source: [Samtec product page](https://www.samtec.com/products/tsw-102-07-g-s?v=2).

## Downloaded and available models

| Component | Model | Status |
|---|---|---|
| Wurth 74650094 | `hardware/epc2361-prototype/models/74650094-manufacturer.stp` | Exact manufacturer STEP downloaded; origin and orientation must be aligned to footprint before attachment. |
| Wurth 74650094 | `hardware/epc2361-prototype/models/Wuerth_74650094-KiCad.step` | Installed KiCad model copied; intended orientation matches installed footprint. |
| Gate/source header | `hardware/epc2361-prototype/models/PinHeader_1x02_P2.54mm_Vertical.step` | Generic KiCad geometry; not exact Samtec certification. |
| EPC2361 | Existing `EPC2361-envelope.wrl` | Dimensioned approximate envelope only. Exact manufacturer model not obtained. |
| 0805 MLCC | Installed `Capacitor_SMD.3dshapes/C_0805_2012Metric.step` | Generic package model. Check selected capacitor height; nominal footprint model can understate tall 100 V parts. |
| 0402 resistor | Installed `Resistor_SMD.3dshapes/R_0402_1005Metric.step` | Generic package model. |
| LMG1210 | No matching installed 19-pin package model found | Requires custom dimensioned package envelope or manufacturer CAD acquisition, once exact driver is fixed. |

The EPC2361 product page's STEP link unexpectedly resolves to **EPC2367.step**, a different device. It was deliberately not relabeled or used as EPC2361. The official EPC KiCad library ZIP returned HTTP 403 during download. The exact EPC2361 CAD model therefore remains unresolved, although its datasheet supplies the mechanical dimensions needed for a clearly marked envelope.

Sources: [EPC2361 product page](https://epc-co.com/epc/products/gan-fets-and-ics/epc2361), [EPC model library](https://epc-co.com/epc/design-support/device-models), [terminal STEP source](https://www.we-online.com/components/products/download/74650094%20%28rev1%29.stp).

The 3D scene cannot certify electrical clearance, creepage, thermal contact or current capability. Cable lugs, bolts, insulating sheet and cold plate still require selected mechanical parts and collision checks.

## Final P2 selection update
The final gate/source headers are four fitted Samtec FTS-102-01-L-S, 1.27 mm pitch, replacing the earlier 2.54 mm candidate above. Their footprint and visualization use the generic KiCad 1x02 1.27 mm vertical header; verify the configured manufacturer mechanical drawing before release. Product source: https://www.samtec.com/products/fts-102-01-l-s . The LMG1210 now has a local approximate envelope. See the prototype model-coverage report for actual attached model files.

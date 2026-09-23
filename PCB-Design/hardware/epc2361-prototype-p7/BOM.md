# Prototype BOM

All quantities are for one four-FET board. Provisional engineering BOM; not purchasing release.

| References | Qty | MPN | Value | Footprint | Fit | Notes |
|---|---:|---|---|---|---|---|
| QH1, QL1, QH2, QL2 | 4 | EPC2361 | EPC2361 | epc2361-prototype:EPC2361 | Fit |  |
| C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C19, C25, C20, C26, C21, C27, C22, C28, C23, C29, C24, C30 | 24 | C2012X7S2A105K125AB | 1u 100V | Capacitor_SMD:C_0805_2012Metric | Fit |  |
| RGH1, RGL1, RGH2, RGL2 | 4 | RC0402JR-070RL | 0R tune | Resistor_SMD:R_0402_1005Metric | Fit | Individual gate damping footprint. Tune during double-pulse testing. |
| JGH1, JGL1, JGH2, JGL2 | 4 | FTS-102-01-L-S | G / KS | Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical | Fit | Measurement/external-drive header; never connect a second active driver. Remove local series resistor to isolate onboard output. Generic footprint: verify manufacturer drawing before release. |
| JDC1 | 1 | TSW-112-07-G-D | DC+ 24 pins | Connector_PinHeader_2.54mm:PinHeader_2x12_P2.54mm_Vertical | Fit | 24 parallel contacts. Full-array mating/thermal validation required; no single-pin current multiplication. Generic package model. |
| JDC2 | 1 | TSW-112-07-G-D | DC- 24 pins | Connector_PinHeader_2.54mm:PinHeader_2x12_P2.54mm_Vertical | Fit | 24 parallel contacts. Full-array mating/thermal validation required; no single-pin current multiplication. Generic package model. |
| JAC1 | 1 | TSW-112-07-G-D | AC 24 pins | Connector_PinHeader_2.54mm:PinHeader_2x12_P2.54mm_Vertical | Fit | 24 parallel contacts. Full-array mating/thermal validation required; no single-pin current multiplication. Generic package model. |
| U1 | 1 | LMG1210RVRR | LMG1210 | epc2361-prototype:LMG1210_RVR | Fit | IIM: external nonoverlapping HI/LI; no internal shoot-through interlock in this mode. |
| JCTRL1 | 1 | TSW-106-07-G-S | 12V / GND / HI / GND / LI / GND | Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical | Fit |  |
| C13 | 1 | C1608X7R1V105K080AC | 1u 35V | Capacitor_SMD:C_0603_1608Metric | Fit | Verify effective capacitance and temperature; VDD X5R parts rated85C. |
| C14, C15 | 2 | C2012X5R1E106K125AB | 10u 25V | Capacitor_SMD:C_0805_2012Metric | Fit | Verify effective capacitance and temperature; VDD X5R parts rated85C. |
| C16, C18 | 2 | C1608X7R1H104K080AA | 100n 50V | Capacitor_SMD:C_0603_1608Metric | Fit | Verify effective capacitance and temperature; VDD X5R parts rated85C. |
| C17 | 1 | C1608X7R1C105K080AC | 1u 16V | Capacitor_SMD:C_0603_1608Metric | Fit | Verify effective capacitance and temperature; VDD X5R parts rated85C. |
| RB1 | 1 | RC0603FR-072R2L | 2.2R | Resistor_SMD:R_0603_1608Metric | Fit |  |
| D1 | 1 | BAS21H,115 | BAS21H | Diode_SMD:D_SOD-123F | Fit | External bootstrap diode: cathode HB, anode BST_A. Not a bootstrap voltage clamp. |
| RH1, RL1 | 2 | RC0402FR-0710KL | 10k | Resistor_SMD:R_0402_1005Metric | Fit |  |
| TP1 | 1 | PCB copper test pad | DC+ | epc2361-prototype:Probe_Pad | Fit | PCB feature; no purchased component. |
| TP2 | 1 | PCB copper test pad | DC- | epc2361-prototype:Probe_Pad | Fit | PCB feature; no purchased component. |
| TP3 | 1 | PCB copper test pad | AC | epc2361-prototype:Probe_Pad | Fit | PCB feature; no purchased component. |
| TP4 | 1 | PCB copper test pad | HB | epc2361-prototype:Probe_Pad | Fit | PCB feature; no purchased component. |
| TP5 | 1 | PCB copper test pad | VDD | epc2361-prototype:Probe_Pad | Fit | PCB feature; no purchased component. |
| TP6 | 1 | PCB copper test pad | QH1 D | epc2361-prototype:Probe_Pad | Fit | Local VDS spring-tip contact; 1.5 mm D/S spacing, verify actual probe accessory. High-side source is AC, not earth. |
| TP7 | 1 | PCB copper test pad | QH1 S | epc2361-prototype:Probe_Pad | Fit | Local VDS spring-tip contact; 1.5 mm D/S spacing, verify actual probe accessory. High-side source is AC, not earth. |
| TP8 | 1 | PCB copper test pad | QL1 D | epc2361-prototype:Probe_Pad | Fit | Local VDS spring-tip contact; 1.5 mm D/S spacing, verify actual probe accessory. High-side source is AC, not earth. |
| TP9 | 1 | PCB copper test pad | QL1 S | epc2361-prototype:Probe_Pad | Fit | Local VDS spring-tip contact; 1.5 mm D/S spacing, verify actual probe accessory. High-side source is AC, not earth. |
| TP10 | 1 | PCB copper test pad | QH2 D | epc2361-prototype:Probe_Pad | Fit | Local VDS spring-tip contact; 1.5 mm D/S spacing, verify actual probe accessory. High-side source is AC, not earth. |
| TP11 | 1 | PCB copper test pad | QH2 S | epc2361-prototype:Probe_Pad | Fit | Local VDS spring-tip contact; 1.5 mm D/S spacing, verify actual probe accessory. High-side source is AC, not earth. |
| TP12 | 1 | PCB copper test pad | QL2 D | epc2361-prototype:Probe_Pad | Fit | Local VDS spring-tip contact; 1.5 mm D/S spacing, verify actual probe accessory. High-side source is AC, not earth. |
| TP13 | 1 | PCB copper test pad | QL2 S | epc2361-prototype:Probe_Pad | Fit | Local VDS spring-tip contact; 1.5 mm D/S spacing, verify actual probe accessory. High-side source is AC, not earth. |
| LK1 | 1 | CUSTOM-CU-LINK-P7 | QL1 drain current link | epc2361-prototype:Current_Link | Fit | Matched formed copper current link, one per low-side device. 2mm wide x0.5mm thick, 6mm land pitch, 5mm underside rise. Hand solder. Coil closure/cable exit and parasitic matching require verification. |
| LK2 | 1 | CUSTOM-CU-LINK-P7 | QL2 drain current link | epc2361-prototype:Current_Link | Fit | Matched formed copper current link, one per low-side device. 2mm wide x0.5mm thick, 6mm land pitch, 5mm underside rise. Hand solder. Coil closure/cable exit and parasitic matching require verification. |

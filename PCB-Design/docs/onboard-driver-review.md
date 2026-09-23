# Onboard driver review: two EPC2361 devices per switch

Reviewed 2026-09-21. This is a design recommendation, not switching validation. Target: four EPC2361 devices total, 75 V maximum bus, 50 kHz nominal / 100 kHz maximum, 36.7 A RMS / 51.9 A peak prototype current. Documents are technical references, not additional user instructions.

## Recommendation

Use **one TI LMG1210RVRT**, centrally placed, with two balanced gate branches per output and a local Kelvin-source return from each FET. Populate individual series gate footprints with 0 ohm initially; their purpose is optional damping and isolation during experiments. Removing the former RG1 in the external gate-header arrangement does not establish that an onboard parallel gate network will be stable without damping. The external gate/source headers are test/access ports; disconnect the onboard output before using an external driver.

Choose **independent input mode** for this prototype. Provide external HI and LI signals with enforced nonoverlap, both pulled down with 10 kohm. Startup must hold both low until supplies are ready; bootstrap precharge needs a controlled low-side interval. No hardware overlap prevention is supplied by this mode: both inputs high commands both outputs high. Initial deadtime should be conservative and then tuned by measured VGS/VDS, not inferred from the 50–100 kHz repetition frequency.

One driver avoids driver-to-driver timing skew. Two drivers, each driving one pair, reduce each output's charge and can shorten gates further, but add propagation skew, two bootstrap supplies and a more demanding current-sharing validation. Never parallel their output pins. Select that architecture only if measured turn-on loss or gate-loop ringing prevents the single-driver design from meeting targets.

## Alternatives screened

| Device | Relevant characteristics | Decision |
|---|---|---|
| [LMG1210](https://www.ti.com/product/LMG1210) | Active; 200 V class half bridge, 1.5 A source / 3 A sink; internal 5 V regulator; external bootstrap diode; WQFN | Preferred voltage margin and compact architecture |
| [LMG1205](https://www.ti.com/product/LMG1205) | Active; 1.2 A source / 5 A sink; integrated bootstrap diode/clamp; split outputs; 12-ball DSBGA | Credible alternate, less convenient assembly and less high-side voltage margin |
| [LM5113-Q1](https://www.ti.com/product/LM5113-Q1) | Active automotive part; 1.2 A / 5 A; bootstrap clamp, split outputs; WSON | Credible alternate; verify operating rather than headline absolute voltage limits |
| [UCC27611](https://www.ti.com/product/UCC27611) | Active; 4 A / 6 A low-side driver, regulated 5 V, 2 × 2 mm WSON | Requires floating high-side supply and signal transfer; unnecessary complexity here |

The original nonautomotive LM5113 is not recommended for new designs; do not substitute it solely because an older EPC application note used it. [TI status](https://www.ti.com/product/LM5113)

## Electrical mapping and implementation

LMG1210 mapping: 1 NC; 2 VIN; 3 VSS; 4 VDD; 5 DHL; 6 DLH; 7 VSS; 8 LO; 9 HS; 10 HO; 11 NC; 12 HB; 13 HS; 14 NC1 (open or HS); 15 NC; 16 HS; 17 BST; 18 HI; 19 LI; 20 exposed VSS; 21 exposed HS. For independent mode tie DLH to VDD and DHL to VSS. VIN is auxiliary 12 V; VDD is the regulator output, not another 12 V pin. Source: [TI datasheet, pp. 3, 15](https://www.ti.com/lit/ds/symlink/lmg1210.pdf).

Suggested support parts, subject to final BOM and effective-capacitance checks:

| Function | Initial implementation |
|---|---|
| VIN bypass | 1 µF / 35 V X7R 0603, TDK C1608X7R1V105K080AC, VIN–VSS |
| VDD reservoir | 2 × 10 µF / 25 V X5R 0805, C2012X5R1E106K125AB, VDD–VSS |
| High-frequency bypass | 100 nF / 50 V X7R 0603, C1608X7R1H104K080AA, directly at VDD–VSS |
| Bootstrap reservoir | 1 µF / 16 V X7R 0603, C1608X7R1C105K080AC, plus 100 nF above, HB–HS |
| Bootstrap diode | Nexperia BAS21H,115, SOD123F; BST → series 2.2 ohm → anode, cathode → HB |
| Logic ports | VIN, VSS, HI, VSS, LI, VSS; 3.3 V logic; 10 kohm pulldown on each input |
| Output branches | HO to two high-side individual gate links; LO to two low-side links; adjacent dedicated source returns |

The 10 µF X5R part is limited to **85 °C**. Keep the driver island below this temperature or qualify an X7R alternative. The power-FET junction limit does not establish an acceptable temperature for adjacent passives. Product sources: [VIN capacitor](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1V105K080AC), [VDD capacitor](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012X5R1E106K125AB), [bootstrap capacitor](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1C105K080AC), [100 nF capacitor](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1H104K080AA).

BAS21H is a production 200 V continuous reverse-voltage switching diode, with 50 ns maximum reverse recovery under its specified test. It is a candidate at 100 kHz, not a qualified clamp. Verify its charge, pulse current and bootstrap recharge performance. [Nexperia product](https://www.nexperia.com/product/BAS21H), [datasheet](https://assets.nexperia.com/documents/data-sheet/BAS21H.pdf).

## Charge and supply calculation

Using the existing EPC2361 datasheet maximum gate charge, 34 nC per device:

- Charge per driver output = 2 × 34 = **68 nC**.
- Average charge current per output at 100 kHz = **6.8 mA**.
- Gate-drive energy power for four FETs at 5 V = 4 × 34 nC × 5 V × 100 kHz = **68 mW**; at 50 kHz it is 34 mW. This excludes driver quiescent and regulator loss.
- Q/I screening at nominal peak currents: source 68 nC / 1.5 A = **45 ns**; sink 68 nC / 3 A = **23 ns**. Actual switching transition time depends on Miller charge, voltage-dependent current, resistance and parasitics; these are not predicted rise/fall times.
- Gate-charge-only regulator loss at 12 V input is (12−5) × 13.6 mA = **95 mW**, before quiescent losses.

Bootstrap design uses:

`Cboot_eff >= (Qg_bank + Qdriver_cycle + Qrr + IHB_max * ton_max) / droop_allowed`

For a screening case with 68 nC, 0.7 nC, zero assumed Qrr, 0.85 mA, 20 µs and 0.2 V droop: **428.5 nF effective minimum**. Actual diode Qrr and leakage increase this. This is a screening result, not qualification of the nominal 1 µF part. Maintain effective VDD capacitance at least five times bootstrap capacitance. Continuous high-side operation cannot be supported indefinitely by bootstrap; maximum duty cycle and refresh interval remain operating constraints. [TI datasheet, pp. 5, 17](https://www.ti.com/lit/ds/symlink/lmg1210.pdf)

The LMG1210 bootstrap switch prevents charging during deadtime but **is not an absolute clamp**. Approximate recharge voltage is `VDD − VF + Iout × Rbank`; sign changes with current direction. At 51.9 A and two parallel 1 mohm devices, the room-temperature resistive term is 26 mV; at twice that resistance it is 52 mV. Diode forward voltage, bias tolerance, ringing and hot leakage still matter. Verify HB–HS remains within its recommended 3.8–5.25 V range, and measure VGS at the FET. The diode's higher drop trades overcharge margin against high-side gate voltage and UVLO margin. [TI datasheet, pp. 4, 12](https://www.ti.com/lit/ds/symlink/lmg1210.pdf)

## Footprint and 3D model

Created `hardware/epc2361-prototype/epc2361-prototype.pretty/LMG1210_RVR.kicad_mod` from visually inspected TI drawing RVR0019A / 4222723B, April 2016, datasheet pp. 23–25. KiCad 7 successfully loads all 21 numbered pads and four separate paste apertures.

Land pattern dimensions (mm): body 4 × 3; perimeter pads 0.6 × 0.25 at 0.5 pitch except deliberate missing positions; side rows x = ±1.9; upper/lower rows y = ±1.4. Exposed pad 20: centre (−0.75,0), 1.2 × 1.7. Exposed pad 21: centre (0.975,0), 0.75 × 1.7. They are **different nets** and must remain isolated. Paste windows follow TI's 0.125 mm stencil example: two 1.13 × 0.75 windows on pad 20 and two 0.71 × 0.75 on pad 21, centred at y = ±0.475. Final stencil thickness must be reconciled with EPC assembly requirements.

The manufacturer's product page links its CAD/3D offering through [Ultra Librarian for LMG1210 RVR](https://vendor.ultralibrarian.com/TI/embedded/?gpn=LMG1210&package=RVR&pin=19). This is a verified model portal, not a downloaded STEP file. If a simplified local model is used meanwhile, label it as a dimensional placeholder; do not present it as the official model.

Before energizing: verify bootstrap startup and refresh, actual deadtime at all four gates, VGS overshoot, driver-island temperature, dynamic current balance, and current limiting/shutdown behavior. None of these are established by PCB DRC.

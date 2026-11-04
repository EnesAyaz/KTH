# Independent review of the Rev B DPT board: electrical correctness

Date: 2026-11-04. Board file SHA-256 `bdcca1a3...65a` (last board commit 1b464f3e). The reviewer had no earlier history with the
board. All checks ran on copies in a scratch folder; the generator was not run and nothing in `hardware/` changed.

**Result: 0 blockers, 3 should fix, 10 notes.** I found no wrong pin, polarity, net, short, split or neck. The change in
1b464f3e does what it claims. The should-fix items need no copper change: they concern the test source, one BOM line and how
the V_DS ports may be used. As far as electrical correctness goes, the board can be ordered as it stands.

Coordinates are KiCad board mm unless marked. Block-local x is x - 126.25 or x - 173.75.

## How the numbers were obtained

- **Fresh DRC:** KiCad 7.0.10 `WriteDRCReport` on the saved fill, then again after a full refill: 0 violations, 0 unconnected,
  0 footprint errors both times. The refill left the total zone area unchanged and no single zone changed by more than 1 nm2.
- **Independent geometry:** all pads, tracks, vias and filled zones exported, rasterised at 0.02 mm per layer. Clearances come
  from a distance transform, with via and pad barrels added on every layer. Raster error is about +-0.02 mm.
- **Current model:** own finite-difference DC solution at 0.1 mm, four layers plus each via as a resistor. Assumptions: 70 um
  copper on all layers, 20 um via plating, 20 C, 80.5 A per cell (322 A / 4), non-conductive fill. SW sink at y = 145 (top of the
  AC bus); DC+ and DC- sink at the 2220 bank pads. The model gives DC resistance and current distribution, not inductance.
- **Pulse:** `simulation/bb_q3d/revb_q3d_spice.py`: TON1 10.67 us, so L_load = 2.48 uH. Effective capacitance at 75 V from
  `revb_post.py`: 6.35 uF per 2220, 0.178 uF per 0805.

## Findings

### Should fix

**S1. The DC link cannot hold 75 V at 322 A with the hardware that is documented.**
- Evidence: charge and energy per first pulse are 1.72 mC and 0.129 J. The board holds 20 x 6.35 + 40 x 0.178 = 134 uF
  effective, 0.377 J at 75 V. The SPICE deck has `Cbulk VS 0 1m` behind `Lbus 20n` (`revb_q3d_spice.py`, supply lines of the deck).
  No such bulk capacitor is in the BOM or in `DPT_measurement_setup.md`, and neither names the load inductor or the pulse length.
  A bench supply behind cables cannot deliver 322 A within 11 us.
- Bench consequence: with the board bank alone (lossless LC) the current reaches 322 A at 11.4 us with the bus at about **61 V**,
  not 75 V. The turn-off, E_off, the second pulse and the overshoot are then measured about 14 V low, so results labelled
  "75 V, 322 A" are not that operating point, and the 92.9 V peak prediction is not actually tested.
- Action, no board change: write the source into the setup note. Either a low-inductance bulk capacitor at J1/J2 (the deck
  assumes 1 mF at 20 nH), or pre-charge to about 87 V so that the bus falls to 75 V at turn-off, or a smaller L_load (1 uH gives
  about 70 V at about 4.5 us). Record V(DC+, DC-) at the end of pulse 1 in every test.

**S2. BOM screw M4 x 8 is too long for the REDCUBE thread.**
- Evidence: `fab/spb-bb-revb-dpt-bom.csv`, mechanical section: "M4 x 8 screw + washer into REDCUBE". Wuerth 74650174 drawing p. 1:
  blind-hole thread, 4.0 mm deep. A lug plus washer of about 2 to 3 mm leaves 5 to 6 mm of screw for 4 mm of thread.
- Bench consequence: the screw bottoms before it clamps the lug. The joint feels tight but has no contact pressure, on the path
  that carries the load current. Forcing it stresses the four pin joints next to the 2220 bank, which the bring-up note already
  warns about.
- Action: choose the length from the real stack so that thread engagement stays below 4 mm (typically M4 x 6), at the datasheet
  1.2 N m. Rated current is 50 A; pulses are fine, but keep this in mind for any continuous test.

**S3. The V_DS ports are not Kelvin to the die and must not be used for on-state values.**
- Evidence (model, LS on at 80.5 A, mV below the AC bus): drain pads Q3/Q4/Q7/Q8 117.1/118.5/117.3/118.0; MMCX centre pins
  J6/J9/J15/J18 37.8/38.1/38.0/37.6; spring pads TP37/TP41 66.8/67.0. All tap B.Cu, behind the island vias and in the planes that
  carry the full load current. The shield side is also off the die: the LSRC via (for example 112.775, 111.8) is in the shunt IN
  land, 20 to 21 mV below the source pads.
- Bench consequence: the MMCX reads the true V_DS plus about **99 mV**, the spring pads plus about 70 mV. The true value is 60 to
  80 mV (0.75 to 1 mOhm), so R_DS(on) reads about 2.3 times too high through J6 and conduction energy is wrong. HS pads
  TP38/40/42/44 are similar: the oval sits 40 to 80 mV from the source pads during HS conduction. Switching waveforms are little
  affected on the drain side, because the SW tap carries only the constant load current; the shield tap does sit in the
  commutation path, so its reading includes part of the source strip inductance.
- Action: add to `DPT_measurement_setup.md` that these ports are for switching transients only, and take R_DS(on) from the
  datasheet or a separate four-wire measurement. No copper change proposed; there is no free Kelvin route at the drain pads.

### Notes

| # | Finding and evidence | Bench consequence | Action |
|---|---|---|---|
| N1 | The Zener runs at (7 - 5.1)/150 = 12.7 mA, but the 4.8 to 5.4 V tolerance in the setup note is at 5 mA. I could not fetch the Nexperia rdif value. | V_GS,on lies above the 5.4 V worst case of the table by rdif x 7.7 mA, and the off level moves with it. Margin to +6 V is smaller than the stated 0.6 V. | Extend the bring-up check to static V_GS,on on all 8 pads, with a limit. |
| N2 | Q4 and Q8 have no V_DS spring pad (`fab/testpoints.csv`: "no labelled test point fits"). The fallback, J9 pad 1 (bottom) to RS2 pad 1 (top), is on opposite board sides. Q3 and Q7 have one. | Cells 2 and 4 can only be probed through the MMCX, so a spring-tip comparison across cells is not possible. V_GS: all 8 covered. | Accept for the prototype; use the MMCX tip on all four cells for like-for-like data. |
| N3 | Shunt gain is 0.957 mV/A into 50 Ohm (PMK Rev 02A), not 1 mV/A. It appears in no project document. | Scaling at 1 mV/A reads current 4.3 % low (14 A of 322 A). | State the gain in the setup note. |
| N4 | IN land cut to 1.2 mm against the 15 x 3 mm PMK land; PMK warns that performance may differ off the recommended footprint. The FET is 2.9 mm off the blade centre. | Gain and bandwidth are not certain to be the datasheet values. | Check gain once with a known DC current; compare the four shunts. |
| N5 | All four SMA shells are DC- (SHLD), at four points, through the scope to earth. PMK offers a UFCS-Choke for CMRR; the setup note does not mention it. | Shield currents can add error on a 77 mV signal, and this looks like cell mismatch. | Try one channel with and without the choke before trusting mismatch data. |
| N6 | KL1 joins Q3.2 and Q4.2, so it links LSRC1 and LSRC2 through the packages, around the shunts (same for KL2). About 20 mm of 0.3 mm track, about 16 mOhm (estimate). RS1 and RS2 sides differ by 13 mV in the model. | About 0.7 A (under 1 %) of cell current bypasses a shunt; more under skew. Does not harm the FETs. | None; read small shunt differences with this in mind. |
| N7 | The DC- path to the bank is longer for outer cells: 32 mV (RS1, RS4) against 19 mV (RS2, RS3) at 80.5 A. Total cell resistance about 3.85 against 3.69 mOhm. | About 4 % static spread between outer and inner cells late in the pulse, on top of FET spread. Not a fault. | Expect it when reading the shunts. |
| N8 | J3, J4, J12, J13 are unkeyed 1x2 headers with no reverse protection. INA/INB have no interlock (datasheet Table 4: H, H gives both outputs high). | A reversed plug takes VDD below the -0.3 V driver limit. Both PWM inputs high shoots through the leg at 75 V. | Set a current limit on V_ISO. For the LS DPT, tie PWM_H1/2 to RTN at the connector. |
| N9 | The LS island shield on In1 (KL1, KL2) overlaps In2 SW by 58 to 62 mm2, about 2 pF through the core. The KH shields are at SW potential, so only the LS side is affected. | About 0.1 A displacement current in the Kelvin path at 50 V/ns, not in the SPICE gate model, so it may add to the V_GS bump. | Covered by the V_GS bump measurement; compare with simulation. |
| N10 | Pad 2 of each EPC2361 (a source pad) is used only as Kelvin, so source current uses pads 4 and 6 alone. Good for gate decoupling, but not the full source connection of the datasheet land pattern. | 40 A per stripe in the pulse, no problem. On-resistance may differ slightly from the datasheet. | None for the DPT. |

## Commit 1b464f3e checked on its own

Text diff of the board before and after: 56 vias added (14 per cell, 0.6/0.3, net SW), none removed; 4 F.Cu SW zones added; the
four 0.25 mm SW tracks to the V_DS ovals removed (now zone); TP37 and TP41 oval tracks shortened by 0.2 mm, plus two small control
track moves (VDDI1, DIS2).

- **Connectivity:** all 60 island vias have pads on F.Cu, In2 and B.Cu and none on In1. They all carry current in the model, so the
  new zone is joined to the old island.
- **Via sharing at 80.5 A:** the 14 new vias carry 3.3 to 5.6 A each. The old via at (120.8, 107.05) still takes 19.5 A (LS on) to
  22.9 A (HS on), about a quarter. Pulse heating of that via is about 0.09 K per 11 us pulse, so this is harmless for the DPT.
- **Resistance:** TP38 oval to the bus 0.95 mOhm, consistent with the claimed 1.02 mOhm.
- **Neck:** read from the raster, the join between FET bar and extension is about 3.3 mm high, about 18 A/mm. Not limiting.
- **In1:** slot in cells 2 and 3 only, at x 144.65/145.65 and 154.35/155.35, about 6 mm from the FET. DC- stays one plane, with a
  peak of 31 A/mm elsewhere. Outer cells have no In1 copper there.
- **Near-shorts:** SW to DC- on F.Cu 0.6 mm at minimum; SW island to the DC+ tip 0.6 mm and to the shunt IN land 0.6 mm by the zone
  outline; bare-pad minimum between the HS and LS domains on F.Cu 0.72 mm. No SW via touches DC- on In1.
- **Loop:** the vias are outside the commutation loop, which stays on F.Cu, so an almost unchanged loop inductance per cell is
  plausible. I did not re-run Q3D.

## Verified as correct

| Item | Result | How |
|---|---|---|
| Schematic against PCB | All nets match; the PCB adds only 25 test points | Fresh netlist export, compared as pin sets |
| 2EDF7275K pinout | All 13 pins correct: pin 4 SLDON to GNDI, pin 6 open, pins 8/11 as VEE (GNDB/GNDA) | Datasheet Rev 3.0 Fig. 2, Table 2 |
| 2EDF land pattern | +-1.95, 0.65 pitch, +-2.05, 0.35 x 0.75, gap in the upper row, pin 1 lower left | Fig. 21, 22 (p. 33) |
| Input side | R_VDDI 3 k at 12 V (2.9 mA) and 22 nF as in the datasheet; VDDI 3.3 V via SLDO | Section 3.3.1 |
| Output supply and UVLO | 7 V is above the 4.5 V minimum and the 4.0 to 4.4 V UVLO of this 4 V variant. Supplies are isolated, no bootstrap | Tables 7, 12 |
| Gate network | V_GS +5.1/-1.9 V within -4/+6 V statically; R_G 0.5 Ohm per FET, R_ON 1.5 Ohm, R_OFF 0 Ohm match BOM and setup note; D_OFF cathode at OUT, turn-off path correct; 10 k star to Kelvin | Nets; EPC2361 p. 1 |
| Power-up transient | Capacitor divider gives -3.5 V briefly at 7 V, inside -4 V, relaxing through 150 Ohm | Hand calculation |
| Floating inputs | INA, INB, DISABLE have 150 k pull-downs: outputs low, V_GS at the off level. No 12 V: input UVLO holds outputs low. No V_ISO: 10 k holds the gate to Kelvin. DIS has no RC, but a glitch only fails towards off | Tables 4, 13; sections 3.4, 3.6 |
| Logic levels | V_INH max 2.35 V, so 3.3 V drive is fine; 47 Ohm / 100 pF filter as stated | Table 13 |
| EPC2361 footprint | Pad positions, mask bars incl. side tabs, pad numbering, G/S/D map, rot 180 on left cells | Datasheet pp. 10-12 against the footprint file |
| Choke pinout | Windings 1-2 and 3-4, dots on 1 and 4: all 9 chokes wired common-mode, no winding crossed; land pattern matches | Wuerth 744232601 p. 1 |
| Shunt polarity | IN to LSRC, SHLD to DC-, the direction PMK requires. 80.5 A against 1250 A at 100 us | PMK Rev 02A pp. 2-3 |
| MMCX | Centre 1.47, ring 2.59/4.21 x 4.22, slot 1.07; centre SW, shield LSRC; 0.56 mm bare gap | Wuerth p. 1 |
| REDCUBE | 4 pins, 5.87 pitch, 1.85 drill, 3.2 pad. The 7 mm body is inside the 8.5 mm DC+ island on B.Cu | Wuerth p. 1 |
| Diodes | PMEG3020EJ pin 1 cathode from datasheet copies. Turn-off peak can exceed the 4.5 A I_FRM (estimate up to about 7 A) for tens of ns only; I_FSM 9 A; accepted. BZX384 and LED cathode pad 1 by KiCad convention, not read on a datasheet page | Search results, nets |
| Headers | J5, J14 pin order matches the BOM text; J3/J4/J12/J13 pin 1 is V_ISO+ into VDD | Nets |
| Power nets | DC+, DC-, SW, LSRC1-4 are each one connected net. Terminal-row pieces of DC+ and DC- at J1/J2 join through the terminal pins | Solver components, pad list |
| Current capacity | No neck. Peak sheet current 89 A/mm in FET stripes (189 at one corner), planes under 40 A/mm. Hottest DC+ via 14.3 A, DC- via 8.6 A. Adiabatic rise under 1 K per pulse | Current model |
| Voltage rating | HS peak 92.9 V (simulated) is under the 100 V rating and 120 V transient rating; this holds only as a prediction until S1 is resolved | EPC2361 p. 1 |
| Power clearance | Inner and masked outer planes about 0.2 mm or more (raster 0.18 to 0.22), above IPC-2221B 0.1/0.13 mm at 100 V. Includes DC+ to DC- along 80 mm on F.Cu. EPC stripes 0.2 mm by the land pattern | Distance transform |
| Bare pads, different domains | Minimum 0.54 mm against the 0.5 mm rule (EPC pads excluded) | Distance transform |
| 1200 V barrier | F.Cu 3.34 mm at the driver (package states 3.4), In1 4.0, In2 3.32, B.Cu 4.0, across layers at least 3.0. Barrels included | Distance transform |
| Sense paths | Gate taps after R_G, Kelvin taps at the FET; LSRC and SW sense tracks carry no power current; supply bias current closes inside the island | Nets, tracks |
| V_GS coverage | All 8 spring pads on the right gate and Kelvin nets, oval centre 3.75 mm from the signal pad | Pad list |
| Scope rules | Setup note returns match the board nets for every port | Nets against the table |
| Cell symmetry | 66/66/66/65 SW vias per cell above y 146 (the difference is in the row at y 145.2). 6 top + 4 bottom 1 uF per cell. Power vias of the two blocks match by translation down to the AC bus. Copper differences between cells 1/3 and 2/4 are at most 5 mm2 on F.Cu, B.Cu and In2 SW; In1 DC- and In2 DC+ differ by about 58 and 23 mm2 because inner cells have plane between the blocks (see N7). Left and right cells are point-symmetric, not mirrored, as designed; the SW column vias on the 1.2 mm grid are not mirrored, which only affects DC resistance | Via list, raster XOR |

The 1200 V figures meet the IPC spacing numbers the project chose. That is not an insulation claim: the driver limit is 460 V
working with 3.4 mm, and the checklist already says so. It has no effect at 75 V on the bench.

Stale comment only: the generator says 12 bypass capacitors per cell; the board and BOM have 10.

## Not checked

- Loop and gate inductance, and all switching waveforms: no Q3D or SPICE re-run.
- Gerbers, drills, CPL, stencil and fab limits (covered by the other two reviews; I did not read those reports).
- Physical stack-up: the 0.1 mm prepreg is assumed. Thermal behaviour beyond adiabatic pulse heating.
- Bank capacitance is the project value of 6.35 uF per part, not checked against TDK bias curves. A higher real value reduces the
  sag in S1.
- BZX384 rdif and pinning, and the LED pinning, could not be read on a datasheet page. Samtec TSM pin numbering not checked.
- The current model is DC at 0.1 mm and gives no skin-effect or transient distribution.
- The DRC custom rules were not tested by injecting a fault; the clearances above were measured separately for that reason.

## Sources

- Local: `Datasheet/EPC2361_datasheet.pdf`; `Datasheet/webfetch-1790845229554-qzkde0.pdf_datasheet.pdf` (2EDi Rev 3.0).
- [Wuerth 744232601](https://www.we-online.com/components/products/datasheet/744232601.pdf),
  [66012102111404](https://www.we-online.com/components/products/datasheet/66012102111404.pdf),
  [74650174](https://www.we-online.com/components/products/datasheet/74650174.pdf).
- [PMK UFCS datasheet Rev 02A](https://www.iwatsu.co.jp/wp-content/uploads/2026/01/UFCS_current-shunt-series_datasheet-Rev02A_J.pdf).
- [PMEG3020EJ datasheet copy](https://datasheetspdf.com/pdf/1387754/nexperia/PMEG3020EJ/1).
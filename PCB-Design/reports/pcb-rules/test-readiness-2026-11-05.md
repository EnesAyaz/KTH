# Rev B DPT board: test readiness audit

Date: 2026-11-05. Question: once built, can the board be tested safely and give valid results? This covers what is missing
for the test, not board layout. Reviewer with no earlier history on the board. Read-only: no generator and no SPICE were run, and
the running 1 µH / 80 V simulation was neither opened nor used. Hand calculations ran in a scratch folder.

**Short answer.** Not yet. The board itself is fine for a staged test up to low current, and it is forgiving in one useful way: the
134 µF bank limits every fault to under 1 J. But the bench around it does not exist on paper. Six items block the test, and
five of them are equipment nobody has chosen yet. The sixth is more serious: **the two numbers that decided R_ON and the gate bias (the high-side V_DS
peak and the held-off high-side V_GS) cannot be measured with the planned kit.** No item needs a board change.

| Class | Count |
|---|---|
| Blocker for test | 6 |
| Should prepare | 16 |
| Note | 13 |

`DPT_test_procedure.md` (draft, read at 12:17 today) appeared while I worked. It already covers several points, and I say so per finding,
so nothing is reported twice. Its open values T1-T21 get proposals in section 5. `DPT_measurement_setup.md` (MS below) was also
edited at 12:16 (high-side V_GS is now isolated-only in all places), and I used that version.

Labels: **[source]** = from a document or datasheet. **[hand]** = my arithmetic, inputs shown. **[proposal]** = my suggestion, no source.
Datasheet graph readings are approximate.

## Blockers for test

### B1. No DC bus source, and nothing says what happens to it during a pulse
- **Evidence:** BOM has no supply. MS bring-up 4 says only "current-limited supply". The procedure lists a floating supply as "model to be set",
  connects it straight to J1/J2 (step 5.1), and no step says whether it stays connected during shots.
- **Failure:** (a) Standard lab supplies stop at 30 or 60 V, so 80 V may simply not be available. Two in series add an earth question. (b) A 100 V / 10 A
  supply with its limit set high stays on the bus after a FET fails short: 800 W into a melted die until someone reacts, on a shot fired from a distance.
  A supply limit alone also does not cover the output capacitor of the supply, which dumps into the fault before the limit acts.
- **Action, no board change [proposal]:** supply at least 90 V, floating, current limit 100 mA, OVP 85 V. **Series resistor 1 kΩ, 25 W wirewound, between supply and J1,
  left in for all shots.** It decouples the supply from the pulse (80 mA against 322 A), so no disconnect relay is needed, and it holds a dead short to 80 mA / 6.4 W.
  Recharge after a shot takes under 1 s (τ = 1 kΩ x 134 µF = 0.13 s, 6 V sag to 0.1 V in about 4 τ). It also makes leakage readable: a meter across the resistor reads 1 V per mA.
  Side effect: the bleeder drops 1.37 V across it at 80 V, so set the bus from the TP45-TP46 reading, never from the supply display.

### B2. High-side gate supply is undefined, and SW sits at the full bus at rest
- **Evidence:** the load inductor ties SW to DC+ (`Lload ACO BP`), so with the bus up, SW, KH1/KH2 and J3/J12 sit at **+80 V against earth** all the time, not
  only during edges. MS line 5 says "controller and bench supplies referenced to DC−", which is wrong for the HS supply. Schematic: "external isolated supply
  (one HS, one LS, split per block)", no part. The Murata MGN1 the checklist assumed (2.5-4 pF, `PCB_rules_and_checklist.md` line 95) is not on this board, and its output is fixed.
- **Failure 1:** HS supply with an earth link, or a shared negative with the LS output. Path DC+ → inductor → SW → KH → R14 (150 Ω, 0.1 W) → L1 → J3 → earth → scope → DC−: 0.53 A, 43 W in
  a 0603 [hand: 80 V / 150 Ω]. R14 burns and the HS off-bias is gone. Procedure step 3.7 tests for this link, which is good, but the step should say why.
- **Failure 2:** a bench supply has hundreds of pF to nF to earth, against the 2.5-4 pF the design assumed. At 50 V/ns even 100 pF is 5 A of peak demand into the CM choke [hand: C dV/dt]. KH then rings against earth
  on the held-off gate, the one gate nobody can observe (B5). Not quantified: no CM model of the supply exists.
- **Failure 3, touch:** the terminals of a "7 V" supply are at 80 V, above the 60 V DC usually taken as touch-safe.
- **Action [proposal]:** HS: battery-fed adjustable regulator (9 V battery and LM317 class; 13.4 mA per driver channel, so about 30 mA) or a low-capacitance isolated DC/DC with an adjustable post-regulator, below 10 pF to earth. LS can be a
  floating bench channel, galvanically apart from the HS one. Fix the MS sentence. Add "J3/J12 and the HS supply are at bus potential" to the rules.

### B3. No pulse source, and no requirement that would let one be chosen
- **Evidence:** BOM none; procedure "to be set". MS asks for one source for J5 and J14. The project controller is the TMS320F28379D (schematic note), not set up for this.
- **Failure:** a plain function generator burst gives equal pulses, not 4.1 µs + 0.75 µs gap + 0.3 µs. A generator left in continuous mode, or one that idles high or starts with a nonzero output, fires the leg unattended.
- **Requirements:**

| Requirement | Value | Source |
|---|---|---|
| High level at the board | above 2.35 V, up to 15 V operating, 17 V absolute maximum | 2EDF Tables 5, 7, 13 |
| Low level | 0 V, never below −0.3 V: no bipolar output | Table 5 |
| Waveform | two pulses of different width, single shot, manual trigger, idle low | [proposal] |
| Timing | step 10 ns or better, jitter below 1 ns (80 A/µs at 1 µH: 10 ns = 0.8 A) | [hand] |
| Max pulse | hard limit about 6 µs, if the source can enforce it | [proposal], see N2 |
| Sync output | to the scope EXT input, so shots can be stacked across channels | [proposal] |
| Outputs | two, with ns delay trim, one for J5 and one for J14 (see S4) | [proposal] |
| Drive | generator set to High-Z load. 50 Ω source + 47 Ω into 100 pF is τ about 10 ns, not the 4.7 ns in MS; same on both headers if the cables match | [hand] |

Candidates: two-channel arbitrary generator, or a LaunchPad with ePWM one-shot and a buffer. PWM_H tied to RTN (ER N8) is in the procedure (step 4.14) but not in MS.

### B4. No load inductor: no design, no build, no measurement plan with numbers
- **Evidence:** BOM has only "AC bar ... length to the load inductor". Procedure 6.1: "to be set by Enes". J21 (44.75, 8.4, top side) and J1 (38.75, 79.6, bottom side) are 71 mm apart on opposite sides [pos file].
- **Failure:** the leads are a large part of 1 µH: wire is roughly 1 nH/mm, so 0.2 to 0.3 m of leads is 0.2 to 0.3 µH. With a fixed 4.1 µs, L +10 % gives 293 A, −10 % gives 356 A, and 1.2 µH gives 269 A [hand, table below]. A coil measured alone lands the test off the point. A shorted or bypassed coil behaves like a short circuit on the first shot.
- **Action [proposal]:** air core, no saturation. Flexible 16 mm² cable (300 V insulation), **3 turns on a 90-100 mm former at 12 mm pitch: 0.94-1.09 µH by Wheeler, about 1 m of cable**, or 5 turns on 60 mm. Allow for the leads: wind about 0.8 µH, then spread turns to trim the total. Clamp to a non-metal board at least 100 mm from metal, with strain relief so J21 and J1 carry no weight.
  Measure in the final position with an LCR meter at 100 kHz between J21 and J1 (bus discharged), then confirm from the current slope (procedure 6.6). The load current does not change during commutation, so stray field of the leads is not an edge problem; only the slope couples.

| L (µH) | C (µF) | I at 4.1 µs (A) | Bus then (V) | Time to 322 A (µs) | Bus at 322 A (V) |
|---|---|---|---|---|---|
| 0.9 | 134 | 356 | 74.5 | 3.69 | 75.5 |
| 1.0 | 107 | 319 | 73.8 | 4.13 | 73.7 |
| **1.0** | **134** | **321** | **75.0** | **4.11** | **75.0** |
| 1.0 | 160 | 322 | 75.8 | 4.10 | 75.8 |
| 1.1 | 134 | 293 | 75.5 | 4.53 | 74.5 |
| 1.2 | 134 | 269 | 75.9 | 4.96 | 74.0 |

Lossless LC, V0 = 80 V [hand]. This confirms the hand calculation in the log. L sets the current; C only sets the bus. Resistive drops (about 1 V) are ignored.

### B5. The high side cannot be observed where it matters
- **Evidence:** the 92.9 V is `VHpk`, the **high-side** peak in the window after LS turn-on (`revb_q3d_spice.py` line 210; `q3d_spice_numbers.json` case `dpt`). The MMCX ports are low side only, with an LS peak of 86.7 V in the same run. R_ON 1.5 Ω was chosen on the 92.9 V
  (MS line 26). In a low-side DPT the held-off device is the HS, so the MS stop rule "record the minimum V_GS of the held-off device ... within 0.3 V of −4 V" (lines 54-57) applies to Q1, Q2, Q5, Q6, which rule 2 says need an isolated probe. Procedure holds H1 and H4 record this correctly.
- **Failure:** the ringing is simulated at −3.45 V, tolerance case −3.85 V (MS). A gate overstressed past −4 V is damaged with no reading to warn of it, and HS overvoltage is equally unseen, while the test report reads "86 V, fine".
- **Why a differential probe does not solve it:** CMRR of a good HV differential probe is about 26 dB at 100 MHz (THDP0200 listing). An 80 V common-mode step then leaves **about 4 V of error**, against a 0.3 V stop margin, at exactly the instant of interest. Its input capacitance to earth also injects about 0.5 A per 10 pF at 50 V/ns into the thin KH track [hand], so it disturbs what it measures. Static HS levels are not affected and are already done with the battery meter (procedure M0).
- **Action, in order of value:**
  1. **Borrow an optically isolated probe for one session.** PMK FireFly FF-1500A (1.5 GHz, 124 dB CMRR at 100 MHz; `FF-MMCX-250V` ±250 V and `FF-MMCX-10V` ±10 V tip cables) is the family PMK names for these shunts; Tektronix IsoVu is the other. MMCX fits J6-J18. V_GS needs an adapter to U.FL or the spring pads. Ask KTH labs and PMK/Tek loan pools first.
  2. **HS V_DS with low common mode [hand, not validated]:** V_DS,HS ≈ V(TP38 DC+ pad, LSRC1) − V(J6). The first term has no 80 V step on it, so the CMRR of the probe hardly matters. Two shots with the same probe and shared sync. Needs short wires to TP38 and an LSRC point, and it is bandwidth-limited like S1.
  3. **Role swap for the gate question:** load from J21 to J2, pulse PWM_H, tie PWM_L low. Then the LS is the held-off device, bump and ringing are at low common mode on KL, and the sync-device overshoot shows on the MMCX. It is a different gate loop, so it bounds the HS result but does not replace it. Needs a gate-loop SPICE comparison before use.
- Until closed, I agree with the gate in the procedure (no stage above S1). If Enes accepts risk at a reduced level, it should be a recorded decision.

### B6. Oscilloscope and differential probe are not identified
- **Evidence:** no document in the repository names a scope ("confirm the available oscilloscope", 10-19 review, still open). Probe: BOM "not chosen yet", procedure hold H2.
- **Failure:** on a scope with 1 MΩ-only inputs or below 500 MHz, the shunts read with the wrong gain and edges are filtered, so every sharing and loss number is wrong without any visible sign. A 4-channel scope also cannot do everything the note lists at once (S6).
- **Minimum [proposal]:** 4 channels, 500 MHz or more (1 GHz better), 50 Ω per channel (or PMK D010031 feed-through x 4, rated 500 MHz, UFCS Rev 02A p. 5), 2.5 GS/s or more per channel with four active, EXT trigger. Differential probe: 200 MHz or better, lowest range covering ±150 V, not a 25 MHz power-electronics probe, with its own power. If only 100 MHz is at hand, S1 applies strongly.

## Should prepare

| # | Finding and evidence | Failure scenario | Action | Procedure draft |
|---|---|---|---|---|
| S1 | **Overshoot reads low by a known factor.** Ring frequency about 208 MHz [hand: 0.646 nH per cell with C_oss about 0.9 nF, EPC Fig. 5a]. A first-order probe passes 0.43 at 100 MHz bandwidth, 0.69 at 200 MHz, 0.92 at 500 MHz. | True 86.7 V reads about 80 V on a 100 MHz probe, and a true 100 V reads 85.8 V. A stop line at "100 V minus a small margin" never fires. | Use the read limits in section 5 (T15). Check the real factor once: measure probe plus cable with a fast step. | Says "reads low", T15 open |
| S2 | **Deskew has no method, and E_off is out of reach.** Sensitivity [hand]: about 4 µJ per ns on E_on (31 µJ per cell, SIM), about 3 µJ per ns on E_off (5 µJ per cell). Probe rise time 1.75 to 3.5 ns against about 2 ns edges. | ±1 ns skew: E_on ±13 %, E_off ±60 %. E_off published from this chain would be noise. | Fast step from the generator through a T into a shunt channel and the probe gives the chain delays; check against the first turn-on at 20 V. Report E_on with its error. Do not publish E_off without a 500 MHz+ probe. | Method open (7.1) |
| S3 | **SPICE and bench do not measure the same thing.** The deck reads V(dL, QL_S) at the die, unfiltered. The bench reads at the port (not Kelvin; shield tap in the commutation path, ER S3) through a low-pass. Committed numbers: 0.6511 nH (0.6457 now), 315.5 A not 322 A, 1 mF bulk, file dated 10-23, before the SW vias. | A 6 V difference gets read as model error, or a true problem is explained away. | Ask sim-analyst for: V_DS at the nearest port terminals (QL_D to RSI), the same trace through 100/200 MHz first-order filters, and E computed like the bench (same 150 ns window). | Warns against the old values. Good |
| S4 | **U1 to U2 skew: up to 13 ns between packages** (t_PD 31-44 ns, 2EDF Table 16; the 3 ns mismatch is between channels of one package). The deck uses the same PWM for both pairs, so "E_on share 0.2 %" and "±1.5 %" assume zero skew. | At 36-40 A/ns, 13 ns is several commutation times: one pair takes the whole hard turn-on, about 161 A per cell plus C_oss. It looks like a sharing defect and stresses Q3/Q4 or Q7/Q8 alone. | Sim-analyst: sweep skew 0-13 ns to get a limit (T7). Two generator channels let the bench trim it to zero. | Measured, limit T7 open |
| S5 | **No hardware arm.** With V_ISO rising and PWM_L high, VDD passes UVLO at 4.0-4.4 V (Table 12) and the LS turns on at about +4.3 V with no command. Below V_ISO 5.1 V the Zener is off, so V_GS,off = 0 V and the bump (+1.2 to +1.4 V at 0 V off, MS) crosses V_th. | A generator power-up glitch or a stale setting with the bus up gives an unplanned pulse. | Use DIS as an arm line. J5/J14 pin 6 pulled to 12 V through 10 kΩ (15 V max, Table 7), an ARM switch shorts it to RTN pin 5. Disarmed = both outputs low within 100 ns (Table 16), whatever PWM does. Order: 12 V, V_ISO, check, bus, arm, shot, disarm, bus off. | Order correct (sections 4, 5, 9). No arm; DIS only tested at 4.13 |
| S6 | **Channels: 17 signals wanted, 4 inputs.** 4 shunts, 4 V_DS, 8 V_GS, bus. One differential probe. LS V_GS by passive probe needs all SMA unplugged (M1), so V_GS is never seen with current. | V_GS at a stage comes from a different shot than the currents; a rare event appears in one and not the other. | Stacked shots with EXT sync (section 2). A second differential probe for LS V_GS with shunts live, or accept and say so. | Plans A, B, M1 are correct |
| S7 | **Gain check as drafted cannot reach its accuracy.** Procedure 6.4 feeds DC through the LS and reads shunts. A 100 mA bus supply cannot do it. At 20 A total each shunt gives 4.8 mV, about the DC offset error of a scope. No current reference independent of the shunts exists. | Gain errors (off-footprint land, ER N4; DC accuracy 1 %, PMK) show up as cell mismatch or a wrong current. | Low-voltage 40 A class supply. Read with a DMM across a 50 Ω terminator, 10 A per cell. Add a wideband current monitor (Pearson class or Rogowski) on the load lead: gives I(t) including the off-time on one channel. | Step present, T13 open |
| S8 | **Second turn-off is above the test point and unsimulated.** With 0.75 µs off and 0.3 µs pulse 2: 322 → 319 → **341 A, 85 A per cell (+6 %)** [hand: V_SD about 4.15 V]. With 0.5 µs pulse 2: 355 A. Deck `Vpk` windows only T1 and it ends 0.3 µs after pulse 2. First turn-on sees 80 V, not 75 V, also with no window. | The highest LS peak of the shot may come at turn-off 2, which nobody predicted. | Add both windows to the follow-up run. Keep pulse 2 as short as ringing allows. The scope view must include it. | Provisional 300 ns; H5 raised |
| S9 | **Discharge.** The bleed relies on R41 and the LED string being intact. AR N11 gives 44 s but ignores R39+R40+D9 in parallel (57.6 kΩ) and C rising from 134 µF to 480 µF as the bus falls. Fit model [hand]: 60 V in 2-8 s, 5 V in about 60 s (bounds 21-77 s). R41 alone: 5 V in about 100 s. | Someone trusts D9 going dark, which in a lit lab can happen well above 0 V (0.57 mA at 80 V, 60 µA at 10 V). Cracked 1206 parts leave the bank at 80 V for hours. | Discharge tool: 100 Ω, 10 W wirewound on insulated leads to J1/J2, or a push button. 0.8 A peak, bank below 5 V in under 0.2 s. Always verify with a meter on TP45/TP46. | Means open; wait + meter correct |
| S10 | **Accessories in no list.** SMA cables appear only in the draft, not the BOM. Also PWM split or two BNC-to-ribbon adapters, H-tie jumpers, EXT trigger cable, ring lugs, U.FL-to-BNC if wanted, wires or holders for pads, UFCS-Choke (560 g with cable: needs its own support on a 6.2 g shunt). | Lost days, or improvised long ground leads at the bench. | Add to the BOM lab section (section 1). | Partly |
| S11 | **MS is behind the plan.** Header says 75 V; 80 V pre-charge not mentioned. Gain 0.957 mV/A still absent (ER N3; only the draft has it). Row "Spring pads" says passive "where the return is DC−-referenced (LS side)", but KL and LSRC are not DC−: with one SMA on, that is rule 1. No sequence or shot-rate text. | Someone following MS, called binding by the draft, puts a passive probe on KL with shunts connected. | Update MS after the sim-analyst result. | Draft flags the M1 condition |
| S12 | **C_eff unverified** (no review read the TDK curves). At 80 V incremental C may be below 134 µF: 107 µF gives 73.7 V at 322 A. | A shot labelled 75 V is 73-76 V. Hand and SPICE agree with each other but not the bench. | Measure on the first ladder shots: C = Q / ΔV, Q = I t / 2 (0.66 mC gives 5 V). Adjust the pre-charge. Bus on TP45/TP46, passive 10x, ground on TP46. | Reads bus at end of pulse 1 |
| S13 | **Both board sides are in use.** Top: 4 shunts with SMA, HS V_DS pads, J21 with bar. Bottom: V_GS pads, MMCX, J1/J2, TP45-47. Standoffs 20 mm only suggested (AR N3). | Board lifted or flipped between shots, or a probe held by hand at 80 V. | A frame holding the board on edge or high on nylon, with cable clamps and a transparent cover. Earthed metal away from the SW bus (MS). | Mentions cover; no fixture |
| S14 | **"Add damping" has no parts.** MS remedy is higher R_G or a gate-source capacitor; no R_ON spares, no C_GS footprint. No FET spares or second board in the plan. | The stop rule fires at S3 and the test halts for weeks. | Buy 0603 R_ON 2.2 Ω and 3.3 Ω, spare EPC2361 and 2EDF7275K. Sim-check the values (T20). | T20 open |
| S15 | **People.** 80 V and 100 V peak are above the 60 V DC usually taken as safe to touch; silk says 75 V and nothing about discharge. FET or MLCC failure ejects fragments. KTH lab rules are not in the repository. | One person alone with hands near a live board. | Polycarbonate cover, safety glasses, second person or lab rule (T1), no touching with the bus above T11, one mains switch for all supplies. | Partly (0.1) |
| S16 | **T1-T21 open.** Stop numbers beyond −3.7 V and 100 V are empty, so the procedure cannot run. | Limits get set during the test, under pressure. | Section 5 gives proposals to accept or change. | Section 0.4 |

## Notes

| # | Note |
|---|---|
| N1 | **Thermal does not set the shot rate.** Per shot about 58 mJ goes into 4 HS FETs in reverse conduction: 15 mJ each over about 80 µs. Peak junction rise about 13 K [hand: 354 W falling to 0, Z_JB about 0.075 K/W at 100 µs, EPC Fig. 12]. Average at 0.2 Hz: 3 mW per FET x 44 K/W, nothing. This answers procedure hold H5 as far as a hand estimate can. The 1 kΩ resistor caps average power at 6.4 W even if the source runs away. |
| N2 | **A pulse too long is survivable.** Stuck-high PWM_L: LC peak 926 A at 18 µs, 232 A per FET against 697 A pulsed (EPC p. 1), shunts 1250 A at 100 µs. The bank falls to 0 V and the inductor energy then burns in the HS. Protection comes from the bank, not from any circuit. |
| N3 | **Shoot-through has no stop.** No desat and no overcurrent function in 2EDF7275K (0 hits in the datasheet; schematic: "No short-circuit protection"); Table 4 H,H gives both high. Loop rate 124 A/ns per cell, 700 A per FET in about 6 ns, bank drained in 4-9 µs (10.7-24 mC at 2800 A) [hand]. Energy 0.43 J at fixed C, up to 0.73 J with the bias fit: 54-92 mJ per FET, at about 28 kW each against about 8 kW for the 10 µs SOA line (Fig. 11). **Assume all eight FETs lost, but nothing further.** Shunts and scope survive (0.67 V on 50 Ω). Only the PWM_H tie, the DIS arm and the generator setup prevent it. |
| N4 | **Scope scale.** Turn-on peak is 131 A per cell (SIM), 125 mV, not 77 mV. 20 mV/div clips unless offset is used, and an overdriven input spoils the reading after it. |
| N5 | **V_DS cable.** 15 cm RG316 is 0.72 ns: quarter-wave at 347 MHz, low-impedance source and open end [hand]. It may add peaking with 200 MHz+ probes. Keep the cable fixed and include it in the S1 check. 14 pF is 1.5 % of C_oss, negligible. |
| N6 | **Shunt response** is fine for 2 ns edges: above 600 MHz, flat within about 0.5 dB to 300 MHz, then rising (+3 dB near 700 MHz, PMK chart), so ring amplitude above 300 MHz reads high. Insertion 120 pH x 40 A/ns = 4.8 V between LSRC and DC− during edges: a passive ground on KL with SMA on sees this as an earth-loop drive. |
| N7 | **RT1 is not a FET sensor.** Control side at the driver (27.0, 34.6), about 20 mm from the FETs, slow. Room reference only. Use an IR camera or thermocouple on the bank and via fields if at all (N1). |
| N8 | **Earth ties (T21).** No DC tie between RTN and DC− is needed. An earthed generator ties GNDI to earth and SMA shields tie DC− to earth, so both meet at mains earth. That is acceptable: barrier stress is under 100 V, and C_IO is 2 pF, 0.1 A per driver at 50 V/ns into the ribbon returns. Rule 1 lists only power and Kelvin nodes, so this breaks no rule. The MS check of INA/INB while switching stays. |
| N9 | **Shunts see only LS current,** including displacement current. HS sharing and the freewheel path are invisible, and the sum is zero in the off-time, so I(T2) must be read just after the edge or from the current monitor (S7). V x I at the shunt leaves out the own C_oss loop of the FET (about 3 µJ at 80 V, Fig. 6). The deck uses the same drain-current product, so compare like with like. |
| N10 | **Freewheel drop about 4.15 V** at 80 A (2.25 V at V_GS 0, Fig. 8, plus 1.9 V; EPC notes negative drive raises V_SD and recommends 0 V off). Decay about 4 A/µs at 1 µH, to zero in about 80 µs. |
| N11 | **Parked cables.** BOM buys 4 MMCX-BNC cables for one probe; the draft uses one at a time. If all four stay on, each BNC pin is live at 80 V, and a shell touching earthed metal joins LSRCx to earth. Fit one at a time with the bus discharged. |
| N12 | **M1 moves the earth.** With a passive probe on KL and SMA off, earth is at KL through a thin Kelvin track rather than DC−. CM current from SW (0.5 A per 10 pF at 50 V/ns) then returns through that track, which can shift the true V_GS by order 1 V [hand, track L of a few nH]. Compare with a differential probe on one FET if one is available. |
| N13 | **U1/U2 delay can be direct.** With the bus at 0 V and no power current, rule 1 has nothing to protect: two passive probes on Q3 and Q7 at once give the delay directly, without the subtraction across shots in step 4.12. Only with a meter-confirmed zero bus, and MS would have to say so. |

## 1. Equipment

Status: **have** = in BOM or a project document with a usable spec. **partly** = named without a spec. **missing** = nowhere in the documents.

| Item | Needed | Status |
|---|---|---|
| DC bus supply | ≥ 90 V, floating, 100 mA limit, OVP 85 V | partly (draft: no model) |
| Series resistor | 1 kΩ, 25 W, between supply and J1 | **missing** |
| HS gate supply | 7 V adjustable in 0.05 V steps, 30 mA, floats at 80 V, below 10 pF to earth | partly (B2) |
| LS gate supply | 7 V adjustable, 30 mA, floating, apart from HS | partly |
| 12 V supply | 12 V, 50 mA limit (2.9 mA per driver) | partly |
| Pulse source | per B3 | **missing** (not chosen) |
| ARM switch, DIS pull-up | S5 | **missing** |
| Control cables | 2 x 5 female IDC, H-tie pin 1-2 (J5, J14); BOM number is a male header (AR S10) | partly |
| PWM split | equal length, 2 outputs | **missing** |
| Load inductor | about 1 µH with leads, air core, 16 mm² | **missing** |
| LCR meter | 100 kHz, 1 µH range | **missing** |
| AC bar, M6 hardware | in BOM; M6 torque open; M4 screw still wrong in BOM (ER S2) | have |
| Oscilloscope | B6 | **missing** (no model anywhere) |
| 50 Ω feed-through x 4 | only if the scope has no 50 Ω input, D010031 | **missing** |
| SMA cables x 4 | SMA male to BNC, equal length, 50 Ω | partly (draft only) |
| Differential probe | B6 | partly (BOM "not chosen") |
| MMCX-BNC cables, 4 mm adapter | in BOM; confirm plug and rating | have |
| Second differential probe | S6 | **missing** |
| Isolated probe | B5, borrow | **missing** |
| Passive probe | 10x with spring tip, 300 V | partly |
| Current monitor on load lead | S7 | **missing** |
| Low-voltage high-current source | 40 A for the gain check, S7 | **missing** |
| Handheld battery meters x 2 | one on TP45/46, one across the 1 kΩ | partly |
| Discharge tool | 100 Ω 10 W, insulated leads | **missing** |
| Fixture, cover, glasses | S13, S15 | **missing** |
| IR camera or thermocouple | N7, optional | **missing** |
| Spare parts | R_ON, FET, driver | **missing** |
| UFCS-Choke | one, optional (ER N5) | partly |
| External bulk capacitor | not needed in the 1 µH plan | not needed |

## 2. Channel assignment against the rules

All four SMA shells are DC− and go to scope earth. So with any shunt on, **DC− is the earthed node**, and every earthed return must be DC−.

| Combination at the same time | Allowed? | Reason |
|---|---|---|
| RS1-RS4 on four 50 Ω channels | **Yes** | One return. Four shells at four points, 13-32 mV spread (ER N5, N7) |
| RS + differential probe on MMCX (shield = LSRCx, not earth) | **Yes** | Probe input floats, so no bypass. Up to 3 shunts + 1 V_DS on 4 channels |
| RS + passive on TP45, ground TP46 | **Yes** | Same node as the shells. Slow signal, lead length is fine |
| RS + passive on LS V_GS or V_DS pad (ground KL or LSRC) | **No** | Rule 1. Shunt bypassed via earth: 77 mV and 4.8 V spikes drive the earth loop. Not destructive, a current error of order 2 % [hand: 1 mΩ against about 50 mΩ] plus ground bounce, but not valid |
| Passive on KL1 and KL2 at once, bus up | **No** | Rule 1 (bus at 0 V: harmless, N13) |
| Passive on LS pad, all SMA off | Yes (M1) | One earthed return. No current in that shot |
| RS + differential on LS V_GS (U.FL with link, or wires to pad) | **Yes** | Common mode is only the 4.8 V shunt spike |
| One differential probe on V_DS and V_GS at once | **No** | One probe, one signal. Move it between shots, bus discharged |
| MMCX cable straight into scope | **Never** | Rule 3 |
| Anything earthed on KH, SW, HS pads | **Never** | Rule 2; bus shorted through R14 or the scope ground |
| Differential on HS V_GS or HS V_DS pads, bus up | **Not valid** | Rule 2 for the gate; about 4 V CM error (B5) |
| Battery meter on HS, bus at 0 V, static | Yes (M0) | |

**Concrete plan, 4 channels, one differential probe** (EXT sync from the pulse source, same settings and pre-charge):

| Shot set | Ch1 (50 Ω) | Ch2 | Ch3 | Ch4 | Gives |
|---|---|---|---|---|---|
| A | RS1 | RS2 (50 Ω) | RS3 (50 Ω) | RS4 (50 Ω) | Sharing, sum, slope |
| B1-B4 | RSk | Diff on the MMCX of cell k (1 MΩ or per manual) | Passive TP45 (1 MΩ, 10x) | spare RS (50 Ω) | V_DS, I of cell k, bus |
| C1-C4 | RSk | Diff on LS V_GS of cell k | Passive TP45 | spare | LS V_GS with current |
| M1 | Passive on LS pad, nothing else | | | | LS V_GS, if no diff path |

**Can V_GS be measured with one differential probe?** Low side: yes, one FET per shot, and it beats M1 because the shunts stay connected. It needs short wires on the spring pad, or a fitted link plus U.FL cable (not in BOM), and an HV probe on its lowest range has poor resolution for a 0.3 V margin; check its noise with the bus off first. High side: static levels yes (or the battery meter), dynamic no (B5).

## 3. Safety and failure modes

| Topic | Result | Source |
|---|---|---|
| Stored energy | 0.43 J at 80 V, fixed 134 µF; up to 0.73 J with the bias fit (real value between) | [hand]; ER S1: 0.377 J at 75 V |
| Inductor energy | 52 mJ at 322 A, 58 mJ at 341 A | [hand] |
| Shoot-through | No interlock, no desat, no overcurrent. Ends when the bank is empty, 4-9 µs. FETs assumed lost (N3) | 2EDF Table 4; schematic |
| What stops a fault | Only the empty bank, then supply limit + 1 kΩ. Nothing on the board reacts. DIS works only if something drives it; there is no sensing | Schematic note |
| Pulse too long | Not destructive at 1 µH (N2) | [hand], EPC p. 1 |
| Bleeder | R41 alone τ 13-48 s; with LED string 7.7-28 s (C from 134 to 480 µF). 5 V in about 60 s, plan 2 min | S9 |
| Gate supply order | 12 V, V_ISO, bus. Off: bus, V_ISO, 12 V. In the draft | Sections 4, 5, 9 |
| PWM high before gate supply | Output low until VDD passes 4.0-4.4 V plus 5 µs start-up, then it follows the input: LS on with no off-bias (S5). Input side: low until VDDI above 2.85 V | Tables 4, 9, 12, 16 |
| No V_ISO, bus up | 10 kΩ holds gate at Kelvin, 0 V, fine for a slow charge | ER "Floating inputs" |
| V_ISO as a fast step | −3.5 V transient at 7 V (ER). Scales with V_ISO: 8 V reaches −4 V. Ramp if possible, OVP 7.5 V | ER; [hand] |
| Repeated shots | Not thermal (N1). Floor about 1 s from recharge; proposal 5 s | [hand] |
| Reversed bus | HS and LS reverse conduction short the supply; 1 kΩ limits it to 80 mA | [hand] |
| FET gate failure | Bus reaches the driver output and its gate supply. The barrier protects the controller side (1500 V test, Table 17). The HS supply may be lost: one more reason for a cheap battery unit | [hand] |

## 4. Validity

| Risk | Size | Treatment |
|---|---|---|
| Probe bandwidth | Overshoot x 0.43 / 0.69 at 100 / 200 MHz | S1 |
| Shunt gain | 0.957 mV/A into 50 Ω, 4.3 % off if taken as 1 mV/A. DC accuracy 1 %, land off-footprint | S7 |
| Shunt at 1 MΩ by mistake | Wrong gain, ringing; looks like a bad cell | Label channels (draft does) |
| Shunt bandwidth | Above 600 MHz, not the limit | N6 |
| Deskew | 13 % per ns on E_on, 60 % per ns on E_off | S2 |
| V_DS port not Kelvin | +99 mV in conduction, some strip inductance in transients | ER S3; S3 |
| High side not seen | The peak that set R_ON, and the gate limit | B5 |
| Cell sharing | Expected 4 % static (ER N7), 1.5 % simulated. Instrument floor: 1 % gain, KL path under 1 %, shield effects. Spreads under about 3 % are not resolvable before gain calibration | S7 |
| Skew against SPICE | SPICE zero, bench up to 13 ns | S4 |
| Bus at turn-off | Hand 75.0 V, 73.7-75.8 V for C ±20 % | S12 |
| Cable loading | 15 pF on the measured cell | Plan A without cable (draft) |
| CM on shunts | Shield currents at four points; try the choke on one channel | ER N5 |
| Second turn-off current | +6 % over the point | S8 |
| Stale SPICE reference | Not the bench circuit | S3 |

## 5. Stages, expected values, stop numbers

The running simulation will replace the hand values at the full point. SIM numbers are the old 1 mF, 2.48 µH deck and serve only as order of magnitude.

| Stage (procedure section) | Expected, with source | Stop at, with source |
|---|---|---|
| Unpowered (1-3) | J1-J2 57.6-100 kΩ [hand]; gate-Kelvin about 10 kΩ (BOM) | Short; below 57.6 kΩ settled (draft) |
| 12 V (4) | 2.9 mA per driver, VDDI 3.3 V (ER); 3.0-3.5 V window (Table 7) | VDDI outside the window; over 50 mA [proposal T4] |
| V_ISO (4) | 13.4 mA per driver channel [hand: 12.7 + 0.7, Table 8]; V_GS,off −1.7 to −1.9 V (MS) | Over 60 mA per supply [proposal T5: 27 mA plus 4 x 4 mA I_GSS max]; V_GS,on ≥ 5.7 V [proposal T6: 0.3 V to +6 V]; V_ISO above 7.1 V (MS) |
| Gate pulses, no bus (4) | t_PD 31-44 ns (Table 16), plus filter | Skew above 3 ns [proposal T7 until swept; none in sources]; HS moves with PWM_H tied |
| Bus, no load (5) | 1.29 mA at 75 V, 1.37 mA at 80 V [hand, 2 V LED] | Over 0.6 mA above baseline [proposal T10: I_DSS max 4 x 0.15 mA at 80 V, EPC p. 1], or rising. T9 = 100 mA, T8 = 10 V steps of 30 s |
| Inductor (6) | 1.0 µH ±5 % with leads [proposal T12]; 20 V, 1 µs gives 20 A total, 5 A per cell | Slope off by over 10 %; any channel inverted (AR S4); L falls with current |
| Shunt gain (6) | 0.957 mV/A (PMK) | Off by over 3 % [proposal T13]: use measured gain |
| S1 (7) | 20 V, 4.1 µs: 80 A, 20 A per cell [hand] | Common limits. No stage above S1 until B5 is closed (draft H1) |
| S2 | 40 V: 161 A, 40 A per cell [hand] | Common limits |
| S3 | 60 V: 241 A, 60 A per cell [hand] | Common limits |
| Full point (8) | 80 V: 322 A, 80.5 A per cell, 77 mV, bus 75.0 V [hand]. Turn-on peak about 131 A per cell; E_on about 125 µJ, E_off about 20 µJ, sum of four; LS 86.7 V, HS 92.9 V (all SIM). **Pending the new run** | Common limits |

Stage currents assume a fixed 4.1 µs and C as at 80 V. A lower bus has more C, so slightly more current [hand]. This is my proposal for T14.

**Common limits, every stage:**

| Quantity | Stop at | Source |
|---|---|---|
| True V_DS | 100 V. **Reading limit:** 85.8 V with a 100 MHz probe, 92.3 V at 200 MHz, 98 V at 500 MHz (T15: 14 / 8 / 2 V) | EPC rating; [hand] first-order, 208 MHz, 75 V bus. Replace with the measured factor (S1). 120 V is a repetitive transient rating, but the MLCCs are 100 V (AR N8) |
| Extrapolation | Overshoot of the next stage (x current ratio) would pass the limit: do not take the step | [proposal] |
| V_GS minimum | −3.7 V | MS |
| V_GS bump | +0.3 V (T16 = 0.5 V below V_th,min 0.8 V); SIM −0.5 to −0.76 V | V_th,min from MS; margin [proposal] |
| V_GS maximum | +5.7 V, never +6 V | EPC p. 1; margin [proposal] |
| Cell sharing | ±10 % of mean at turn-off [proposal T17]; expect 4 % (ER N7), ±1.5 % (SIM) | No source for the limit |
| Bus at turn-off | Relabel the shot if off plan by over 1 V | ER S1; [proposal] |
| Board temperature | +10 K above room [proposal T18]; expected under 1 K in copper (ER) | A rise means a fault, not a limit |
| Shot interval | 5 s [proposal T19]; physical floor about 1 s | N1 |
| Touch | Below 5 V [proposal T11] | Lab rule decides (T1) |

**No number exists anywhere for:** U1/U2 skew limit, HS V_GS under the real supply capacitance, damping values (T20), M6 torque (T3), preheat (T2), lone-work rule (T1).

## Not checked

- SPICE not run. The 1 µH / 80 V result is not used. Numbers marked hand are lossless or first-order estimates.
- Real probes and scopes: none identified. The CMRR figure comes from a distributor listing for one probe, so read the table of the chosen probe.
- TDK C(V) curve not read. The bias fit C(V) = C0 / (1 + (V/48)²) is mine, set to 29 % at 75 V; the 0.73 J and the discharge times depend on it.
- LED brightness, supply capacitance to earth, gate-loop CM behaviour: estimates or unknown.
- Whether FETs survive shoot-through: an SOA graph reading, not a test.
- KTH lab rules, and equipment Enes has but has not documented: **missing** above means missing from the documents.
- `DPT_test_procedure.md` was read as a draft and may change after this report.

## Sources

Local: `reports/pcb-rules/DPT_measurement_setup.md` (12:16 version), `DPT_test_procedure.md` (draft), `independent-review-2026-11-04-electrical.md`, `-assembly.md`, `spb-bb-revb-dpt-review-2026-10-19.md`,
`PCB_rules_and_checklist.md`; `hardware/spb-bb-revb-dpt/fab/` BOM, pos, testpoints, schematic PDF; `pad_nets.json`; `simulation/bb_q3d/revb_q3d_spice.py`;
`reports/slides/data/q3d_spice_numbers.json` (committed 2026-10-23), `final_numbers.json`; `reports/design-loop/log.md`; `Datasheet/EPC2361_datasheet.pdf` (revised 2026-07-20) pp. 1-4;
`Datasheet/webfetch-1790845229554-qzkde0.pdf_datasheet.pdf` (2EDi Rev 3.0) Tables 4, 5, 7, 8, 9, 12, 13, 16, 17.

Web: [PMK UFCS datasheet Rev 02A](https://www.iwatsu.co.jp/wp-content/uploads/2026/01/UFCS_current-shunt-series_datasheet-Rev02A_J.pdf),
[PMK FireFly FF 1500A datasheet](https://www.iwatsu.co.jp/wp-content/uploads/2025/08/FireFly®-FF-1500A-Datasheet-Rev03.pdf),
[Tektronix THDP0200 listing](https://www.testequipmentdepot.com/tektronix-thdp0200-200-mhz-50x-500x-high-voltage-differential-probe-with-tekvpi-interface.html) (figures from the search summary; the page refused a direct fetch).

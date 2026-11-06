# DPT board (Rev B): bring-up and test procedure

Version 2026-11-05, written before the board was built. Section 8 holds SPICE model values: tune them on the bench. Board: `hardware/spb-bb-revb-dpt`. For one person on the bench with
no isolated probes. It runs from the incoming board to the full-power double pulse: low-side switching, high side held
off, load inductor from the AC bolt J21 to DC+.

**How to read a step.** Each row says what to connect or do, what to measure, the expected value with its source, and
when to stop. Stop means: bus off, discharge (section 9), find the cause, do not go on. Section 10 has all stop criteria,
section 11 is the one-page checklist.

**Numbers.** Every value has its source next to it. "Derived" means arithmetic on sourced values, with the sum shown.
"To be set by Enes" means no source gives the number; those items are collected in section 0.4 as T1, T2, and so on. "Proposal, Enes to
confirm" marks a suggestion from the readiness audit (TR section 5) that no design document backs. Settle that table before you start.

| Tag | Source |
|---|---|
| MS | `reports/pcb-rules/DPT_measurement_setup.md` (binding) |
| AR | `reports/pcb-rules/independent-review-2026-11-04-assembly.md` (S = should fix, N = note) |
| ER | `reports/pcb-rules/independent-review-2026-11-04-electrical.md` |
| JO | `reports/pcb-rules/DPT_JLC_order.md` |
| BOM | `hardware/spb-bb-revb-dpt/fab/spb-bb-revb-dpt-bom.csv` |
| TP | `hardware/spb-bb-revb-dpt/fab/testpoints.csv` |
| NET | `hardware/spb-bb-revb-dpt/pad_nets.json` (ER confirms that schematic and PCB nets match) |
| DECK | `simulation/bb_q3d/revb_q3d_spice.py` |
| SIM | `reports/slides/data/q3d_spice_numbers.json`, case `dpt` (committed results of DECK) |
| SP | `simulation/bb_spice/dpt_1uH_80V/results.json` (case B unless named), no bulk capacitor |
| RL | `simulation/bb_spice/dpt_1uH_80V/read_limits.json` |
| TR | `reports/pcb-rules/test-readiness-2026-11-05.md` |

Coordinates are board mm, origin bottom-left, x right, y up. `testpoints.csv` uses another origin (AR N2): board x = csv x + 44.75,
board y = 60.8 − csv y (derived from the origin (150, 100), y down, and the aux origin 105.25 / 160.8 in the `.kicad_pcb`).

## Holds: read these first

H1 and H4 are the main measurement gap of this test. They are not solved by this procedure. (H3 and H5 of the earlier draft are closed: see section 8.)

| Hold | Issue | Blocks |
|---|---|---|
| H1 | **The high-side gates cannot be measured while switching with the kit you have.** High-side V_GS is isolated only (MS port table, rule 2). In this test the high side is the held-off device, so the required record of the minimum V_GS of the held-off device (MS tolerance procedure) and the bump measurement cannot be made on Q1, Q2, Q5, Q6. A differential probe is no way round: about 4 V of common-mode error against a 0.3 V margin (TR B5). Enes decides: borrow an optically isolated probe for one session (first choice, TR B5), or record a decision to accept the risk at a reduced level. Allowing S1 at all is a judgement of this procedure, not a source: its HS gates go unrecorded. | Any switching above stage S1 of section 7 |
| H2 | The differential probe is "not chosen yet" (BOM). V_DS is not measured without it. See B6 below. | Section 7 |
| H4 | The high-side V_DS peak is not visible on the V_DS ports: they are low side only (MS). The highest peak of the shot is the high-side one, 95.9 V at the first turn-on (section 8), while the V_DS ports see 87.7 to 89.3 V. Spring pads TP38, TP40, TP42, TP44 exist, but their return is SW (TP), and rule 2 applies. TR B5 gives an unvalidated two-shot workaround for V_DS. Enes decides whether the gap is acceptable. | Section 8 |

**Must be solved first.** None of these needs a board change (TR). Each section repeats its own item.

| Item | What | Must be solved before |
|---|---|---|
| B6 | Scope and differential probe identified | Step 3.7 (scope); section 7 (probe) |
| B2 | HS gate supply chosen: live at bus potential on J3 and J12 | Step 4.3 |
| B3 | Pulse source meeting the requirements | Step 4.11 |
| TR S5 | DIS arm line built | Section 5 |
| B1 | Bus supply and 1 kΩ series resistor | Section 5 |
| B4 | Load inductor built | Section 6 |
| B5 | Same as H1 and H4 | Stage S2 and section 8 |

## 0. Before you start

### 0.1 Safety rules (binding, MS "Rules")

1. **One earthed return at a time.** All scope channels share protective earth. Two earthed channels on different returns (LSRC1 and LSRC2, or KL1 and DC−) short those nodes through the scope.
2. **High side isolated only.** KH1, KH2, SW and high-side V_GS move 0 to 100 V at 30 to 50 V/ns. No earthed probe or channel on them, ever. With no isolated probe, the only instrument allowed there is a handheld battery meter, static, with the DC bus at zero (it has no earth connection, so rule 2 is kept; sections 4 and 5 use it that way).
3. **V_DS MMCX: differential probe, or nothing.** Never an MMCX-to-BNC cable straight into the scope.
4. **Never 50 Ω on a V_DS port.** 75 V into 50 Ω is about 112 W. No feed-through in the path. Check the scope channel setting every time a cable moves.
5. **Do not float the scope.** Protective earth stays connected.
6. **Before powering:** ohmmeter check of every probe shield (section 3).
7. **Deskew** voltage and current channels with the real probes.

Additional rules for this board:

- Silk says 75 V DC; this test goes to 80 V. The board bank holds 0.377 J at 75 V (ER S1), 0.43 J at 80 V (TR). Discharge and check with a meter before touching (section 9).
- **Pre-charge never above 84 V, read at TP45-TP46.** The HS peak tracks the pre-charge 1:1 against the 100 V limit (SP). The supply display reads high by the 1 kΩ drop (TR B1).
- **J3, J12, the HS gate supply and KH are live at bus potential.** Once the inductor is fitted, SW sits at DC+ at rest: +80 V against earth all the time, not only on edges. An earth link on the HS supply puts 80 V across R14: 0.53 A, 43 W in a 0603 (TR B2). Do not touch a "7 V" supply with the bus up.
- **Shots at least 1 s apart, and read the bus before firing.** The current must reach zero first (79 µs, SP).
- Never have PWM_H and PWM_L high together with the bus up: the driver has no interlock, H,H gives both outputs high and shoots through the leg (ER N8). From step 4.14 on, PWM_H stays tied to RTN. Nothing on the board stops a shoot-through: assume all eight FETs lost (TR N3).
- Change probe connections only with the bus discharged.
- The copper at the bottom of the board is the switch node, not ground. Keep PWM cables and earthed metal (bench, brackets, probe bodies) away: 10 pF carries 0.5 A at 50 V/ns (MS setup notes).
- You work alone: fire single shots from a distance, polycarbonate cover on, safety glasses, one mains switch for all supplies (TR S15). Whether lab rules allow lone work at this voltage: T1.

### 0.2 Equipment

| Item | Requirement | Source | Status |
|---|---|---|---|
| Oscilloscope | Earthed. Minimum: 4 channels, 500 MHz or more, 50 Ω per channel (or PMK D010031 feed-through x 4), 2.5 GS/s or more with four active, EXT trigger (TR B6, proposal, Enes to confirm) | MS, TR B6 | **not identified (B6).** The channel plan below assumes 4 |
| Differential probe | Range above 100 V differential, inputs not earth-referenced, BNC output. 200 MHz or better, lowest range covering ±150 V, own power (TR B6, proposal, Enes to confirm) | BOM, MS, TR B6 | **not chosen (H2).** Its bandwidth sets the V_DS stop line (section 10) |
| 4 x V_DS cable | MMCX plug to BNC male, RG316, about 15 cm; confirm MMCX plug and voltage rating | BOM, MS | in BOM |
| BNC to 4 mm adapter | CT3889 for 4 mm sockets on the probe, PMK 4MM-BNC-F for 4 mm plugs on the probe | MS, BOM | follows the probe |
| 4 x SMA cable | Shunt to scope. Equal length; length to be set by Enes. Optional PMK UFCS-Choke | MS, ER N5 | not in BOM |
| Passive probe with spring tip | 10x, 300 V (TR); one probe for all pads. For KL, GNDI and DC− returns only | MS, TR | model to be set by Enes |
| 2 x handheld battery meter | One on TP45-TP46, one across the 1 kΩ (TR). Must resolve the 0.2 V wide V_GS,off window. Not earthed | MS, TR | yours |
| DC bus supply | At least 90 V, floating, limit 100 mA, OVP 85 V (TR B1, proposal, Enes to confirm) | MS bring-up 4, TR B1 | **not chosen (B1)** |
| Series resistor | 1 kΩ, 25 W wirewound, supply to J1, left in for all shots (TR B1, proposal, Enes to confirm) | TR B1 | **missing (B1)** |
| HS gate supply | Adjustable around 7 V in 0.05 V steps, 30 mA, floats at 80 V, below 10 pF to earth: battery-fed regulator or low-capacitance isolated DC/DC with post-regulator (TR B2, proposal, Enes to confirm) | MS gate settings, TR B2 | **not chosen (B2)** |
| LS gate supply | Adjustable around 7 V, 30 mA, floating, galvanically apart from the HS supply (TR) | TR B2 | model to be set by Enes |
| 12 V supply | J5 and J14 pin 8, 50 mA limit (TR) | BOM, TR | |
| Pulse source | Requirements at section 4 (B3). One source for J5 and J14, equal-length cables, delay trim between the outputs | MS gate settings, TR B3 | **not chosen (B3)** |
| Arm line | 10 kΩ pull-up to 12 V on DIS, ARM switch to RTN, for J5 and J14 (TR S5, proposal, Enes to confirm) | TR S5 | **missing** |
| Control cable | **Female** 2 x 5 IDC socket. The BOM number 61201021621 is a male header (AR S10) | AR S10 | buy a female part; mark pin 1 (AR N1) |
| Torque wrench, block | 1.2 N m; block for the top area x 33-56, y 74-85, relieved for the pin tips | MS bring-up 3 | |
| Preheater, iron | Convection or IR preheater, standoffs, narrow tip. Not a flat hot plate | AR S5, hand assembly | |
| Spare or bare board | To prove the shunt soldering first | AR S5 | |
| Screws | M4 sized to the real stack (step 2.1). M6 x 16 bolt, nut, 2 washers; AC bar 12 x 5 mm Cu | AR S8, BOM | **BOM still says M4 x 8** |
| Standoffs | M2.5 nylon. Plan about 20 mm height | BOM, AR N3 | |
| Load inductor, LCR meter | Section 6 (B4). LCR meter, 100 kHz, 1 µH range | ER S1, TR B4 | **missing (B4)** |
| Low-voltage high-current source | 40 A class, for the shunt gain check (TR S7, proposal, Enes to confirm) | TR S7 | **missing** |
| Fixture, cover | Frame holding the board with both sides reachable, cable clamps, transparent cover (TR S13) | TR S13 | **missing** |
| Spares | 0603 R_ON 2.2 Ω and 3.3 Ω, EPC2361, 2EDF7275K (TR S14, proposal, Enes to confirm) | TR S14 | **missing** |
| Discharge tool | 100 Ω, 10 W wirewound on insulated leads to J1/J2 (TR S9, proposal, Enes to confirm) | TR S9 | **missing** |

### 0.3 Where everything is

Cell map (NET, DECK):

| Cell | HS FET | LS FET | Driver | Shunt | V_DS MMCX | HS V_GS pad / return | LS V_GS pad / return |
|---|---|---|---|---|---|---|---|
| 1 | Q1 | Q3 | U1 | RS1 | J6 | TP15 / KH1 | TP17 / KL1 |
| 2 | Q2 | Q4 | U1 | RS2 | J9 | TP16 / KH1 | TP18 / KL1 |
| 3 | Q5 | Q7 | U2 | RS3 | J15 | TP33 / KH2 | TP35 / KL2 |
| 4 | Q6 | Q8 | U2 | RS4 | J18 | TP34 / KH2 | TP36 / KL2 |

All eight V_GS spring pads are on the bottom; the return is the oval next to the pad (TP).

Driver supplies (NET, TP; t = top side, b = bottom side):

| Channel | V_ISO input (1 +, 2 −) | VDD | Kelvin | VEE |
|---|---|---|---|---|
| U1 A, high side | J3 | TP7 (b) | TP9 (b) | TP8 (t) |
| U1 B, low side | J4 | TP11 (t) | TP13 (b) | TP12 (b) |
| U2 A, high side | J12 | TP25 (b) | TP27 (t) | TP26 (t) |
| U2 B, low side | J13 | TP29 (b) | TP31 (b) | TP30 (b) |

Control headers (BOM, NET): J5 / J14: 1 RTN, 2 PWM_H, 3 RTN, 4 PWM_L, 5 RTN, 6 DIS, 7 RTN, 8 12 V. J5: 9 RTN, 10 NTC. J14: 9, 10 not connected.
Logic test points: GNDI TP1 / TP19, 12 V TP2 / TP20, VDDI TP3 / TP21, INA TP4 / TP22, INB at C18 pad 2 / C51 pad 2 (TP).
Bus and switch node: DC+ TP45, DC− TP46, SW TP47, all bottom (TP).

Measurement setups. Every shot in this procedure uses exactly one of these:

| Setup | Instruments on the board | Earthed return | Used for |
|---|---|---|---|
| **M0** | Handheld battery meter only, scope off the board | none | All static readings, all high-side readings |
| **M1** | One passive probe on an LS spring pad or a logic node; **all SMA cables and every other probe unplugged** | KL1 or KL2, or GNDI (one at a time) | LS V_GS, PWM logic |
| **M2** | Shunts on 50 Ω channels; differential probe on one MMCX (1 MΩ or as the probe manual says); optional passive probe on TP45 with its ground on TP46 (same node as the shunt shields) | DC− | Current, V_DS, bus voltage |

M1 relies on the table note in MS: a passive probe only where the return is DC−-referenced and no other channel is tied elsewhere. The floating
bus supply is what keeps M1 legal; the shunt shields and KL must never be on the scope in the same shot, because that is the KL1-to-DC− case of rule 1.
M1 moves earth to KL through a thin Kelvin track, which can shift the true V_GS by order 1 V at high dV/dt (TR N12, hand estimate). A differential probe on LS V_GS with the shunts on avoids this, at poor resolution (TR section 2).

Scope channel plan for M2 on four channels:

- Plan A (sharing): Ch1-4 = RS1-RS4 at 50 Ω, no MMCX cable fitted.
- Plan B (per cell): Ch1 = shunt of that cell at 50 Ω, Ch2 = differential probe, Ch3 = passive on TP45, Ch4 free. Label the 50 Ω channels; do not reassign them.
- All plans: EXT sync from the pulse source, so shots stack across channels (TR section 2). Turn-on peak is about 125 mV, not 77 mV: set the scale for it (TR N4).

### 0.4 Values to set before starting

Proposals come from TR section 5, except T7 and T15, which are from the SPICE run. Rows marked open have no number in any document.

| ID | Value | Setting | Basis |
|---|---|---|---|
| T1 | Lone-work rule in the lab | **open:** to be set by Enes | KTH rules not in the repository (TR S15) |
| T2 | Preheat temperature and time | **open:** to be set by Enes | "Well below" 217 °C SAC305 solidus; no PMK limit found, ask PMK (AR S5) |
| T3 | M6 torque at J21 | **open:** to be set by Enes | none |
| T4 | Current limit, 12 V supply | 50 mA (proposal, Enes to confirm) | Draw 2.9 mA per driver (ER) |
| T5 | Current limit, each V_ISO supply | 60 mA (proposal, Enes to confirm) | 2 x 13.4 mA plus I_GSS maximum (TR) |
| T6 | Limit for static V_GS,on | 5.7 V, that is 0.3 V to +6 V (proposal, Enes to confirm) | Absolute +6 V (MS) |
| T7 | U1 to U2 skew at the gates | **Per stage (model values): 3 ns or less at 40 V, 1.5 ns at 60 V, 0.5 ns at 80 V** (see section 8) | SP: V_GS passes −4 V at 2 ns; threshold not resolved between 1 and 2 ns; based on an estimated 18 nH inter-cell path, not an extraction |
| T8 | Bus ramp | 10 V steps of 30 s (proposal, Enes to confirm) | "Slowly" (MS bring-up 4) |
| T9 | Bus supply current limit | 100 mA (proposal, Enes to confirm) | TR B1 |
| T10 | Leakage above the bleeder baseline | 0.6 mA (proposal, Enes to confirm) | I_DSS maximum 4 x 0.15 mA at 80 V (TR) |
| T11 | Safe-to-touch bus voltage | Below 5 V (proposal, Enes to confirm); the lab rule decides | TR |
| T12 | L measurement | 20 V, 1 µs gives 20 A total, 5 A per cell. Target 1.0 µH ±5 % with leads. Stop if the slope is off by over 10 % (proposal, Enes to confirm) | TR section 5 |
| T13 | Shunt gain check | 10 A per cell; off by over 3 %: use the measured gain (proposal, Enes to confirm) | TR S7, section 5 |
| T14 | Stage table of section 7 | 20, 40, 60, 80 V at fixed 4.1 µs (proposal, Enes to confirm) | TR section 5 |
| T15 | V_DS stop | Reading limits 98 V at 500 MHz, 93 V at 200 MHz, 87 V at 100 MHz (model value) | RL; first-order filter model. Replace with the measured probe factor (TR S1) |
| T16 | Bump limit | +0.3 V, that is 0.5 V below V_th,min 0.8 V (proposal, Enes to confirm) | TR section 5 |
| T17 | Current sharing limit | ±10 % of the mean at turn-off (proposal, Enes to confirm) | About 4 % expected (ER N7) |
| T18 | Board temperature limit | +10 K above room (proposal, Enes to confirm) | A rise means a fault (TR) |
| T19 | Time between shots | 5 s (proposal, Enes to confirm); never under 1 s (SP) | TR, SP |
| T20 | Damping values | **open:** to be set by Enes. Spares R_ON 2.2 and 3.3 Ω proposed, values not simulation-checked (TR S14) | MS names the remedy only |
| T21 | Tie between controller RTN and DC− | No DC tie needed: an earthed pulse source and the SMA shields meet at mains earth (proposal, Enes to confirm) | TR N8 |

## 1. Incoming inspection

Nothing powered. Setup M0. Record board number and manufacturer.

| Step | Do | Measure | Expected | Stop if |
|---|---|---|---|---|
| 1.1 | Read the delivered stack-up from the fab documents | L1-L2 and L3-L4 prepreg | 0.10 mm; 0.646 nH per cell assumes it (JO) | Thicker prepreg: rerun Q3D before quoting loop numbers (AR S2). Does not stop the bring-up |
| 1.2 | Magnifier, TP33 (GH_L2), bottom | Via at (62.17, 54.67), 0.57 mm off the pad centre (JO) | Filled and capped flat (MS bring-up 1) | Open or dimpled via |
| 1.3 | Same, TP1 (GNDI1), top | Via at (19.30, 33.80) on the pad edge (JO) | Filled and capped flat | Open or dimpled via |
| 1.4 | Same, 0805 rows at y 61.3, top | 24 DC− vias next to C1-C12, C34-C45 pad 2 (JO) | Filled and capped flat | Open via: solder wicks from the bypass capacitor (AR S3) |
| 1.5 | Compare the board with the assembly PDFs | U1 pin 1 (19.05, 39.65), U2 (66.55, 39.65), Q1 (13.85, 54.67), Q2 (28.15, 57.13), D1 cathode (18.0, 45.1), D3 cathode (9.7, 30.0) (AR "Not checked") | Match. U1/U2 have no pin-1 silk (AR S13): use the PDF and the pad gap | Rotated part |
| 1.6 | Check what must be absent | R16-R19, R35-R38, RS1-RS4 | Not fitted (JO). Paste on the empty lands is possible (AR N6) | 0 Ω links fitted: remove, they add U.FL stubs to the gates (AR S14) |
| 1.7 | Meter between J1, J2, J21, all three pairs. Bare board: no parts | Resistance | Open, all pairs. J1 and J2 pin pieces join only through the terminal pins (ER "Power nets"), so a single pin on a bare board may read open to a far-away point of its own net: not a fault | Any continuity between nets |
| 1.8 | Same on the assembled board, before shunts | J1-J2; J1-J21; J2-J21 | J1-J2 settles between 57.6 and 100 kΩ (step 3.1). J2-J21: open, the LS sources are not joined to DC− until the shunts are on (NET). J1-J21: no short | Short on any pair |
| 1.9 | Each shunt land pad 1 to TP47 (SW) | LSRCx to SW, four cells | No short | Short across a LS FET |
| 1.10 | RS1 pad 1 to RS2 pad 1, RS3 pad 1 to RS4 pad 1 | Resistance | Low, about 16 mΩ estimate: KL1 and KL2 link the pair through the packages (ER N6). Not a fault | |

## 2. Lab assembly

Follow this order. Terminals are torqued before the shunts because the shunts make the top side unusable (AR S9). The review proposes
the eleven low-mass loops first, while both sides are free (AR hand assembly); they are listed last here. Doing 2.13 before 2.1 is also fine.

| Step | Do | Measure | Expected | Stop if |
|---|---|---|---|---|
| 2.1 | Lay out the real stack at each terminal: lug(s), washer. J1 carries the bus lead **and** the inductor lead (DECK: inductor to DC+), so include both now and avoid torquing twice | Clamped thickness t | Screw length = t + at most 3.5 mm. M4 x 8 only if t ≥ 4.5 mm (AR S8). Typically M4 x 6 (ER S2). Thread is 4.0 mm blind | Screw bottoms: the joint feels tight with no contact pressure (ER S2) |
| 2.2 | Support the board with the block under J1/J2, top area x 33-56, y 74-85, relieved for the pin tips (about 1.4 mm proud, AR S7). Top parts must not touch the support | Look at C67, C68 (nearest MLCCs, 7.63 mm) | Board rests on the block only (MS bring-up 3) | Anything rests on the MLCCs |
| 2.3 | Fit J1 and J2 hardware, torque wrench, **hold the terminal** against the reaction torque. Point lugs away from TP45 and TP46 (bushing edge 5.48 / 5.33 mm from the axes; a Ø9 washer clears, a wide ring lug does not, AR N4) | Torque | 1.2 N m (MS bring-up 3, 74650174R p. 1) | Terminal moves or pins lift: a torque test can tear them out (AR S7) |
| 2.4 | Meter J1 to J2 | Resistance | As step 3.1 | Short: cracked MLCC (MS bring-up 4) |
| 2.5 | Prove the shunt sequence on the spare or bare board | Joint quality | Full wetting (AR S5) | No clean joint: do not touch the real board |
| 2.6 | Board on standoffs over the convection or IR preheater. No flat hot plate: REDCUBE 6.0 mm and MMCX 5 mm stand on the bottom (AR S5) | Board temperature | T2 | |
| 2.7 | In this preheat solder TP45 and TP46. They sit in solid planes and press-fit on their own, so a cold joint looks seated (AR S6) | Wetting on both sides | Solder through | Cold joint |
| 2.8 | Hold each shunt to the land and read its markings **before** the iron. **IN towards the FET, pad 1, LSRCx, y 49.0. SHLD to pad 2, DC−, y 46.4** (AR S4). No silk shows this | Direction | IN to LSRCx, SHLD to DC− (ER "Shunt polarity"). A reversed shunt puts the earthed SMA shield on LSRC, bypasses the shunt through earth, inverts the signal, and a meter cannot show it (1 mΩ both ways) | Doubt about the direction |
| 2.9 | Solder RS1-RS4 in the same setup, one at a time, SHLD side first, narrow tip entering at the land end (AR hand assembly) | | | Tip touches the FET area |
| 2.10 | Inspect each IN fillet against Q3, Q4, Q7, Q8. The land edge is 0.20 mm from the FET copper (AR S5). Meter SW (TP47) to the shunt, each cell | Resistance | No short. A bridge shorts SW to LSRC across the FET (AR S5) | Bridge or short |
| 2.11 | Check clearance | RS1 and RS4 overhang the left and right edge by 2.4 mm (MS bring-up 2). RS2 to RS3 bodies 0.7 mm (AR N7) | Fixture and probe holders clear | Collision |
| 2.12 | Cool down. Add strain relief on the SMA cables: 6.2 g, 27.4 mm part on a butt joint (AR N7) | | | |
| 2.13 | Fit the other eleven loops with a normal iron: TP7, TP8, TP11, TP12, TP13, TP25, TP26, TP27, TP29, TP30, TP47 (AR hand assembly) | Joints | Nearest foreign pad 1.56 mm (AR) | Bridge |
| 2.14 | 0 Ω links R16-R19, R35-R38 **only if needed**. The spring pads are the primary gate measurement (MS); links add stubs to the gates and U.FL is 30 V. Fit them on all four LS cells or none, to keep the cells comparable. High-side links are of no use without an isolated probe (H1) | | Default: not fitted | |
| 2.15 | Mount on the M2.5 nylon standoffs, about 20 mm (AR N3). Keep nylon: H1 and H2 are 0.22 mm from SW copper | | | |
| 2.16 | Mark pin 1 on both control cables: turned round, cable 12 V lands on header pin 3 (GNDI) (AR N1). Mark + on the four V_ISO plugs: headers are unkeyed (ER N8) | | | |

## 3. Unpowered checks

Setup M0, nothing powered, bus discharged.

| Step | Connect | Measure | Expected | Stop if |
|---|---|---|---|---|
| 3.1 | Meter on TP45, TP46 | DC-link resistance. The reading climbs while the bank charges from the meter; wait | Settles between 57.6 kΩ and 100 kΩ. R41 = 100 kΩ, in parallel with R39 + R40 + D9 = 136 kΩ when the meter voltage lights the LED (derived, BOM, NET) | Stays well below 57.6 kΩ, or short: cracked MLCC or bridge |
| 3.2 | Meter on each of the eight V_GS spring pads and its oval, both polarities | Gate to Kelvin | About 10 kΩ: pull-down R3, R6, R22, R25 (BOM). Paths through the driver may lower one polarity; compare the four pads of a side (no sourced value for that) | Short, open, or one pad clearly different |
| 3.3 | Meter J5 pin 10 to pin 9 | NTC RT1 | 10 kΩ nominal (BOM); read room temperature with it | Open or short |
| 3.4 | Meter on J3, J4, J12, J13 pins 1-2 and J5, J14 pins 8-7 | Supply inputs | No short | Short |
| 3.5 | Meter between SW (TP47) and TP45, and TP47 and TP46 | Baseline, both polarities | No short. Record the numbers (no value in the sources) | Short |
| 3.6 | Rule 6, board side. Meter from each SMA shell to J2, each MMCX shield to the shunt IN land of that cell | Resistance | About 0 Ω. With shunts fitted, LSRCx to DC− is 1 mΩ (BOM), and LSRC1 to LSRC2 reads the same way, so **the meter cannot prove these nodes are apart on the board** (see 3.7) | Open shield |
| 3.7 | **Solve B6 first: the scope must be identified.** Rule 6, instrument side. All cables and probes plugged into the scope, **unplugged from the board**. Meter between the board ends of every pair of returns, and each to scope earth | Resistance | SMA shields and passive grounds: 0 Ω to earth by design. Differential probe inputs and all supply outputs: not joined to earth or to each other (MS rule 6). The HS supply matters most: an earth link burns R14 (TR B2) | A differential input or a supply output joined to earth |
| 3.8 | Adapter on the differential probe cable | Which 4 mm plug is the shield | Shield = LSRCx = − input (MS) | |
| 3.9 | Scope setup | Input setting per channel | SMA channels 50 Ω (MS). Differential probe channel as the probe manual says, **no 50 Ω in the V_DS path** | Any 50 Ω in the V_DS path |

## 4. Low-voltage power-up, no DC bus

No bus supply connected. Check TP45-TP46 with the meter first: at or below T11. Setups M0 and M1.

**Must be solved before step 4.3 (B2):** the HS gate supply. It must float at bus potential with below 10 pF to earth; a bench channel has hundreds of pF to nF, and at 50 V/ns even 100 pF is 5 A of peak demand into the choke, ringing KH on the one gate nobody can observe (TR B2). The LS supply can be a floating bench channel, apart from the HS one.

**Must be solved before step 4.11 (B3):** the pulse source. Requirements (TR B3; items without a datasheet are proposals, Enes to confirm):

| Requirement | Value |
|---|---|
| High level at the board | above 2.35 V, up to 15 V operating, 17 V absolute maximum (2EDF Tables 5, 7, 13) |
| Low level | 0 V, never below −0.3 V: no bipolar output (Table 5) |
| Waveform | two pulses of different width, single shot, manual trigger, idle low |
| Timing | step 10 ns or better, jitter below 1 ns |
| Maximum pulse | hard limit about 6 µs, if the source can enforce it |
| Sync output | to the scope EXT input |
| Outputs | two, with ns delay trim, one for J5 and one for J14 (needed for T7) |
| Drive | generator set to High-Z load |

| Step | Connect | Measure | Expected | Stop if |
|---|---|---|---|---|
| 4.1 | Set the 12 V supply, limit T4 (50 mA), output off. Connect J5 and J14 (pin 8 +, RTN pin 7). Pulse source off, inputs left open | | Open inputs: 150 kΩ pull-downs keep outputs low (ER) | |
| 4.2 | 12 V on | TP2, TP20 to TP1, TP19; VDDI TP3, TP21 to GNDI | 12 V; VDDI 3.3 V; 2.9 mA per driver through R_VDDI 3 kΩ (ER "Input side") | Current limit reached, wrong VDDI |
| 4.3 | Set both V_ISO supplies to 7.0 V, limit T5 (60 mA), output off, then connect: HS to J3 and J12, LS to J4 and J13. **Check polarity at each plug** | Pin 1 + | Reversed plug takes VDD below the −0.3 V driver limit (ER N8) | Doubt on polarity |
| 4.4 | V_ISO on, PWM low. Ramp if the supply can: the transient scales with V_ISO (TR) | Supply current. Ignore a brief gate transient: capacitor divider gives −3.5 V, inside −4 V (ER "Power-up transient") | 13.4 mA per driver channel, so about 27 mA per supply (TR: 12.7 mA plus 0.7 mA, 2EDF Table 8) | Above T5 |
| 4.5 | M0: VDD to VEE on all four channels (table 0.3) | V_ISO at the board | 7.0 V; output supply limit: above 4.5 V (ER) | Far from setting |
| 4.6 | M0: VDD to Kelvin on all four channels | Zener voltage | 4.8 to 5.4 V at 5 mA; at 12.7 mA higher by rdif x 7.7 mA, rdif not found (MS, ER N1) | Above T6 |
| 4.7 | M0: PWM inputs low. Meter on all eight spring pads and ovals | Static V_GS,off | −(V_ISO − V_Z): −1.9 V nominal; −1.6 to −2.2 V at 7.0 V over the Zener range 4.8 to 5.4 V (derived, MS), moved by the 12.7 mA shift. Table below | Any pad positive or near 0 V, or not matching the Kelvin-to-VEE reading of its channel |
| 4.8 | Set V_ISO so that V_GS,off lies between **−1.7 and −1.9 V**. If one supply feeds both drivers, use the channel with the most negative level (MS procedure). Then repeat 4.7 | All eight pads | In the window. Going above 7.0 V is covered by the MS table only up to **7.1 V**; MS also says not to exceed 7 V without checking the EPC2361 minimum V_GS, and the check is the ringing estimate: off level minus 1.55 V must stay above −3.7 V | Needs more than 7.1 V: stop and decide. Static level more negative than −1.9 V: no switching. Least negative channel above −1.5 V: note it, bump reaches −0.06 V (MS) |
| 4.9 | **Bus at zero confirmed.** Static PWM_L1 and PWM_L2 high, 3.3 V, PWM_H low. M0 on Q3, Q4, Q7, Q8 pads. Then PWM_L low | Static V_GS,on, LS | 4.8 to 5.4 V plus the 12.7 mA shift (MS, ER N1). Margin = 6 V minus reading (MS: 0.6 V at best at 5 mA) | Above T6. Never at +6 V |
| 4.10 | PWM_L low, static PWM_H1 and PWM_H2 high. M0 on Q1, Q2, Q5, Q6 pads. Then PWM_H low. **Never both high** | Static V_GS,on, HS | As 4.9 | Above T6 |
| 4.11 | M1 on GNDI1, then GNDI2 (one return at a time). Real pulse source, real cable, shortest planned pulses (second pulse in section 8). Probe at J5 / J14 pin, then at INA, INB against the local GNDI | PWM logic | Filter 47 Ω, 100 pF: τ 4.7 ns, about 10 ns rise (MS); with a 50 Ω source τ is about 10 ns (TR B3). High level above V_INH max 2.35 V. Pulses well above the 18 ns typical driver minimum (MS, ER). U1 and U2 alike | Missing, double or short pulses |
| 4.12 | M1 on Q3 (return KL1), trigger from the pulse source sync. Measure sync to V_GS edge. Repeat on Q4, then move the return, Q7, Q8 (KL2). Do not put KL1 and KL2 on two channels (rule 1). **Trim the delay between the two outputs** and repeat | U1 to U2 skew on channel B, by subtracting the readings | As close to 0 as the source allows; **0.5 ns or less is required before any 80 V shot** (T7). Untrimmed it can be up to 13 ns: t_PD 31-44 ns between packages (TR S4). Channel A cannot be measured (H1) | Cannot reach 1 ns: no full-voltage shot |
| 4.13 | Fit the arm line on both headers: pin 6 to 12 V through 10 kΩ, ARM switch shorts it to RTN pin 5 (TR S5, proposal, Enes to confirm). Run LS pulses, then open the switch (disarm) | LS V_GS | Armed: follows PWM. Disarmed: both outputs low within 100 ns (TR S5, 2EDF Table 16), whatever PWM does | Outputs still switch when disarmed |
| 4.14 | PWM off. **Tie PWM_H1 to RTN at J5 (pin 2 to pin 1) and PWM_H2 at J14 (pin 2 to pin 1)** (ER N8). Run LS pulses, M0 on the HS pads | HS V_GS | Stays at V_GS,off | HS moves |
| 4.15 | Fill the table. Switch off V_ISO, then 12 V | | | |

| Pad | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 |
|---|---|---|---|---|---|---|---|---|
| V_GS,off at V_ISO 7.0 V | | | | | | | | |
| V_GS,off after setting | | | | | | | | |
| V_GS,on | | | | | | | | |
| Margin to +6 V | | | | | | | | |

HS V_ISO set: ____ V. LS V_ISO set: ____ V. U1 to U2 delay: ____ ns.

## 5. DC link first power-up

No inductor, J21 open. PWM_H tied to RTN, pulse source off, disarmed. 12 V and V_ISO on, so the gates sit at V_GS,off. Setup M0. Read the meter on TP45, TP46.

**Must be solved before this section (B1):** the bus source. A supply at 80 V with its limit set high stays on the bus after a FET fails short, and its output capacitor dumps into the fault before the limit acts (TR B1). Supply at least 90 V, floating, limit 100 mA, OVP 85 V, with **1 kΩ, 25 W in series between the supply and J1, left in for all shots** (proposal, Enes to confirm). The resistor decouples the supply from the pulse, holds a dead short to 80 mA and 6.4 W, recharges the bus in under 1 s (τ 0.13 s), and a meter across it reads 1 V per mA (TR B1).

**Must be solved before this section (TR S5):** the arm line of step 4.13. Order for the rest of the test: 12 V, V_ISO, check, bus, arm, shot, disarm, bus off.

| Step | Connect | Measure | Expected | Stop if |
|---|---|---|---|---|
| 5.1 | Bus supply at 0 V, limit T9 (100 mA), OVP 85 V, output off. Connect + through the 1 kΩ to J1, − to J2. Check polarity against the silk. Second meter across the 1 kΩ | Polarity | "75 V DC - CHECK POLARITY" (AR N11) | Doubt |
| 5.2 | Raise slowly, T8 (10 V steps of 30 s), up to the bus of section 8, **read on TP45-TP46, never the supply display**, never above 84 V | Voltage on TP45-TP46 and the 1 kΩ reading at each step | Tracks the set value less the 1 kΩ drop: 1.37 V at 80 V (TR B1). D9 lights (BOM) | Above 84 V; current limit reached; voltage does not follow |
| 5.3 | Baseline at each step | Meter across the 1 kΩ, 1 V per mA | 1.29 mA at 75 V, 1.37 mA at 80 V (TR, 2 V LED drop) | Above baseline plus T10 (0.6 mA) |
| 5.4 | **Hold at the top voltage and read the leakage once, before the first pulse** (MS bring-up 4). Log it | Current minus baseline | A cracked MLCC shows as leakage or a short (MS). Limit T10 | Above T10, or current drifting up |
| 5.5 | Bus to 0, discharge per section 9 | Time to reach T11 | Section 9 | Does not fall |

## 6. Load inductor

ER S1: neither the BOM nor MS names the inductor. L is whatever the bench gives, so measure it. **Measure L before any timed shot:** 1.2 µH with the same pulse gives only 269 A (SP case C_L1u2).

**Must be solved before this section (B4):** the inductor. Proposal, Enes to confirm (TR B4): air core, no saturation, flexible 16 mm² cable with 300 V insulation, 3 turns on a 90-100 mm former at 12 mm pitch (0.94-1.09 µH by Wheeler, about 1 m of cable), or 5 turns on 60 mm. Leads add about 1 nH/mm, and J21 and J1 are 71 mm apart on opposite sides: wind about 0.8 µH, then spread the turns to trim the total. Clamp to a non-metal board at least 100 mm from metal, with strain relief so J21 and J1 carry no weight.

| Step | Connect | Measure | Expected | Stop if |
|---|---|---|---|---|
| 6.1 | Build the inductor as above. Bus discharged | | About 1 µH with leads | |
| 6.2 | AC bar to J21: M6 x 16, nut, 2 washers (BOM), torque T3 (open). Other end to J1, DC+ (DECK: `Lload ACO BP`). LCR meter between J21 and J1 in the final position, 100 kHz (TR B4) | L; meter J1 to J2 | 1.0 µH ±5 % with leads (T12). J1 to J21 now reads near 0 Ω at DC: this is the inductor, not a fault. J1 to J2 still as step 3.1. A shorted coil acts as a short on the first shot (TR B4) | L far off target; J1 to J2 changed |
| 6.3 | Keep the inductor and its leads away from the PWM cables. Set up M2 Plan A | | | |
| 6.4 | Shunt gain check (ER N4). The 100 mA bus supply cannot do this (TR S7): disconnect it and the 1 kΩ, connect the 40 A class source to J1/J2, scope off the board. LS static on (armed, PWM_L high), raise in current limit to 10 A per cell. Read each shunt with a meter across a 50 Ω terminator. Then source to 0 **before** LS off, disarm, reconnect the bus chain | Sum of the shunt voltages / 0.957 mV/A against the source ammeter | Agree within 3 % (T13); otherwise use the measured gain. Gain 0.957 mV/A into 50 Ω (ER N3); 1 mV/A would read 4.3 % low. The IN land is off the PMK footprint (ER N4). Spreads under about 3 % are not resolvable before this (TR section 4) | A shunt reads inverted: reversed (step 2.8). A shunt reads nothing |
| 6.5 | Common-mode check (ER N5): repeat one pulse with and without the UFCS-Choke on one channel, if you have one | Difference | Shield currents on a 77 mV signal can look like mismatch | |
| 6.6 | Bus to 20 V (T12) on TP45-TP46. Arm, single LS pulse of 1 µs, disarm | Bus V (meter just before the shot), Σ I(t) = Σ shunts / 0.957 mV/A; slope ΔI/Δt on the straight part | 20 A total, 5 A per cell (T12). **L = V_bus × Δt / ΔI** (formula). All four signals same sign | Any channel inverted. Slope off by over 10 % (T12). Current does not ramp in a line |
| 6.7 | Repeat at a second current. Repeat again at each stage in section 7 | L | Same within T12. Air core: L does not fall with current | L falls |
| 6.8 | Log L, bus, ΔI, Δt. Hand L to section 8 | | | |

## 7. Staged double pulses

**Must be solved before this section (B6, H2):** scope and differential probe. On a scope with 1 MΩ-only inputs or below 500 MHz the shunts read with the wrong gain and edges are filtered, with no visible sign (TR B6).

**Before stage S1.** Section 8 settings read. PWM_H tied to RTN. V_ISO as set in 4.8. **Before S2:** H1 closed or a recorded decision. **Before Full:** skew 0.5 ns or less (T7), H4 decided.

**Every shot:** read the bus on TP45-TP46 (84 V maximum), wait at least T19 since the last shot (5 s, floor 1 s), arm, fire, disarm.

Fixed first pulse 4.1 µs at the low stages (T14, proposal, Enes to confirm); at another L, t1 = L × I / V (DECK uses the same relation). Off-time and second pulse as in section 8.

Raise one stage at a time. Do not take a step if the overshoot of the next stage (scaled by the current ratio) would pass a limit (TR section 5, proposal, Enes to confirm).

| Stage | Bus (V) | I at turn-off, total (A) | Per cell (A) | Shunt (mV) | t1 | Status |
|---|---|---|---|---|---|---|
| S1 | 20 | 80 (TR, hand) | 20 | 19.1 (derived) | 4.1 µs | proposal, Enes to confirm |
| S2 | 40 | 161 (TR, hand) | 40 | 38.5 (derived) | 4.1 µs | proposal, Enes to confirm |
| S3 | 60 | 241 (TR, hand) | 60 | 57.7 (derived) | 4.1 µs | proposal, Enes to confirm |
| Full | 80 at the board | 322.0 (SP) | 80.5 (ER) | 77.0 (derived; ER N5 "77 mV") | 4.146 µs (SP) | section 8 |

A lower bus has more capacitance, so slightly more current (TR). On the first shots measure C = Q / ΔV with Q = I t / 2 and adjust the pre-charge (TR S12).

**One-time deskew**

| Step | Do | Measure | Expected | Stop if |
|---|---|---|---|---|
| 7.1 | Deskew voltage and current channels with the real probes (rule 7). Method proposed by TR S2 (Enes to confirm): fast generator step through a T into a shunt channel and the probe gives the chain delays; check against the first turn-on at 20 V. Repeat after any probe or cable change | Channel delay | Recorded. About 13 % on E_on and 60 % on E_off per ns (TR S2) | E_on not valid without it. Do not publish E_off without a 500 MHz or better probe (TR S2) |
| 7.2 | Note the loading: RG316 adds about 15 pF across SW-LSRCx on the measured cell for 15 cm (MS); V_GS probe adds to the gate capacitance (MS) | | That cell behaves slightly differently, so sharing shots run without the cable | |

**Repeat 7.3 to 7.10 at every stage**

| Step | Setup | Do and record | Expected | Stop if |
|---|---|---|---|---|
| 7.3 | | Idle check. Bus at the stage value, meter across the 1 kΩ, as in step 5.3 | Baseline | Above baseline plus T10 |
| 7.4 | M2 Plan A | Single shot. Each cell current at turn-off of pulse 1 and just after turn-on of pulse 2 (shunts see LS current only and read zero in the off-time, TR N9). Sum and L check (6.7) | Outer cells lower than inner by about 4 % late in the pulse: not a fault (ER N7). KL path moves about 0.7 A, under 1 % (ER N6) | A channel inverted. Spread above T17 (±10 %) |
| 7.5 | M2 Plan B, per cell | Bus discharged, cable on J6, shot; repeat J9, J15, J18, one cable fitted at a time (TR N11). Use MMCX on all four for like-for-like data, not the spring pads (ER N2). Record V_DS peak at both LS turn-offs and ringing, cell current, and **V(DC+, DC−) at the end of pulse 1** in every test (ER S1) | **V_DS through the differential probe: switching transients only, LS only, not R_DS(on).** The port reads V_DS plus about 99 mV in conduction (ER S3). The peak reads low: compare like with like, see section 8 | Reading at T15 for your probe: 98 V at 500 MHz, 93 V at 200 MHz, 87 V at 100 MHz |
| 7.6 | M1 on KL1 or KL2 | **Unplug all SMA and the TP45 probe.** Bus discharged, move the probe, shot. Same probe on Q3, Q4, Q7, Q8. Record minimum V_GS, V_GS,on overshoot and off-state bump | At the full point: LS minimum −3.36 V, HS −3.43 V (SP). Tolerance excursion 1.55 V below the off level (MS) | Minimum within 0.3 V of −4 V, that is at or below −3.7 V: **stop and add damping (T20), not more negative bias** (MS). Bump above +0.3 V (T16). Any peak above T6 |
| 7.7 | | HS held-off V_GS, Q1, Q2, Q5, Q6: H1. Enter "not measured" unless Enes has closed H1 | | Do not go above S1 with this open |
| 7.8 | M1 on GNDI | Repeat 4.11 during switching (MS): INB on U1 and U2, and INA, which is tied low and must stay low: a pulse there can turn the high side on. If pickup appears, shorten the cable, twist pairs, single ground point (MS) | Same as 4.11; INA flat | Extra or missing pulses; any pulse on INA |
| 7.9 | M0 | Board around the via fields and source-to-shunt transitions (MS), IR camera or thermocouple if you have one. RT1 is a room reference only: 20 mm from the FETs, slow (TR N7) | Adiabatic rise under 1 K per pulse in the copper (ER) | Above T18 (+10 K) |
| 7.10 | | Compare with the previous stage | Everything scales with no new feature. Go on only if every row passed | Any item of section 10 |

## 8. Full point

**Status: SPICE model values, no bulk capacitor (SP case B). Tune them on the bench; they are not measurements.**

| Setting | Model value | Note |
|---|---|---|
| Bus pre-charge | **80 V at the board**, read on TP45-TP46 | Supply about 81.4 V because of the bleeder, through the 1 kΩ. **Never above 84 V** |
| L_load | **1 µH, measured in place** (section 6) | 1.2 µH with the same pulse gives only 269 A |
| First pulse | **4.146 µs** | Ends at 74.9 V, 322.0 A |
| Off-time | **0.75 µs** | Matches one 736 ns period of the 1.36 MHz row ring. Tune it, step 8.3 |
| Second pulse | **300 ns** | Ends at 339.5 A, above the 322 A test point |

Expected at the full point. Reading = die peak through a first-order probe filter (RL):

| Quantity | Model | Reads at 100 / 200 / 500 MHz | Measurable? |
|---|---|---|---|
| LS peak, first turn-off | 87.7 V | 84.2 / 85.5 / 87.1 V | Yes, MMCX |
| LS peak, second turn-off | 89.3 V; scatters 89 to 91.5 V, quote a range | 84.4 / 86.0 / 88.3 V | Yes, MMCX |
| HS peak, first turn-on | 95.9 V, from the 80 V bus | 86.2 / 90.7 / 94.6 V | **No (H4)** |
| HS peak, second turn-on | 90.9 V | 81.3 / 85.6 / 89.5 V | **No (H4)** |
| E_on, sum of four cells | 121 µJ. Bank ±20 %: 119 to 123 µJ (SP) | | Deskewed, with its error |
| E_off, sum of four cells | 20.6 µJ | | Only with a 500 MHz or better probe (TR S2) |
| Minimum V_GS | HS −3.43 V, LS −3.36 V (SP) | | LS only (H1) |
| Bus at first turn-off | 74.9 V. Bank ±20 %: 73.7 to 75.8 V (SP) | | Yes, TP45 |

**Stop lines from the same run**

- **Pre-charge never above 84 V** on TP45-TP46: the HS peak tracks it 1:1 against the 100 V limit. This headroom assumes zero skew: at 1 ns skew and 80 V the model already puts the HS first turn-on peak at about 100 V, with V_GS −3.72 V (SP case M0_skew1, 99.98 V raw). So do not use the margin up to 84 V unless the skew is near zero.
- **U1 to U2 skew at the gates, by stage (SPICE sweep 2026-11-06, `simulation/bb_spice/dpt_ron_skew/`):** 40 V / 100 A: 3 ns or less (limit not reached); 60 V / 200 A: 1.5 ns; 80 V / 322 A: 0.5 ns (V_GS -3.7 V crossing at 0.9-1.0 ns). Higher R_ON does **not** relax this: the limit comes from the LS turn-off, which does not pass through R_ON. Do not use R_ON 5 Ω at 80 V (unstable at 0.5 ns). R_ON 2 Ω gives 9.3 V V_DS margin at 80 V and 0.5 ns, against 2.2 V at 1.5 Ω, for 20 % more E_on. Check LS V_GS at the first low-voltage stage before relying on R_ON above 1.5 Ω: with an ideal D_OFF the model passes -3.7 V at R_ON 3 Ω. Model limits: estimated 18 nH inter-cell path, identical FETs, so a real spread acts like extra skew; treat these as upper bounds.
- **V_DS reading limits:** 98 V at 500 MHz, 93 V at 200 MHz, 87 V at 100 MHz. At 100 MHz this is a poor stop line, only 3 V above the normal reading.
- **Shots at least 1 s apart, bus read before firing.** The current must reach zero first (79 µs).

**End of burst.** After the last pulse 57.6 mJ of inductor energy goes into the HS FETs in reverse conduction: 12.85 mJ per FET, about 10 K junction rise (hand, 7 to 13 K). The current is at zero after 79 µs, and the bus does not rise (SP).

**About the committed SPICE results.** V_DS peak 92.9 V and E_on 125 µJ in SIM come from DECK, which has a 1 mF bulk capacitor (`Cbulk VS 0 1m`, behind 20 nH) and L_load 2.48 µH. **That capacitor does not exist on the bench** (ER S1). The 92.9 V was at 79.4 V rows and 316 A, not at 75 V / 322 A. Do not use these numbers as pass values.

| Step | Do | Record | Expected | Stop if |
|---|---|---|---|---|
| 8.1 | Confirm: H1 and H4 decided, skew 0.5 ns or less, every stage of section 7 passed, leakage at baseline, L measured in section 6 | | | Any open |
| 8.2 | Set the table values; correct t1 for the measured L. Check PWM_H tied to RTN, cover on, cable routing, bus on TP45-TP46 | | | Bus above 84 V |
| 8.3 | Tune the off-time at a lower stage first. The row is not probed directly: in the off-time the V_DS port reads the row voltage plus the 4.15 V freewheel drop (derived, SP) | Port voltage just before the second turn-on | Row 74.4 V at 0.75 µs, so about 78.6 V at the port. The row swings 70.9 to 79.7 V at the full point (SP). 0.5 µs: row 71.8 V, E_on −8 %. 1 µs: row 78.1 V, E_on +2 % (SP) | |
| 8.4 | Run 7.3 to 7.10 at the full point, single shots | Same as a stage. Bus at turn-off is the point that counts: off plan by over 1 V, relabel the shot (TR, proposal, Enes to confirm) | Tables above | As section 10 |
| 8.5 | Reduce E_on, E_off only from deskewed V_DS and cell current, naming the probe bandwidth and the integration window. Do not take R_DS(on) from these ports (MS, ER S3); use the datasheet or a separate four-wire measurement | | | |

## 9. After the test

| Step | Do | Measure | Expected | Stop if |
|---|---|---|---|---|
| 9.1 | Disarm. Pulse source off. Bus supply to 0 V, output off. Keep V_ISO and 12 V on until the bus is down, so the gates stay held off | | | |
| 9.2 | Discharge with the tool on J1/J2 (100 Ω, 10 W: below 5 V in under 0.2 s, 0.8 A peak, TR S9, proposal, Enes to confirm), or wait. Bleed alone: 5 V in about 60 s, plan 2 min (TR S9). AR N11's 44 s ignores the LED string and the capacitance rise at low bias | | D9 off is a sign, not proof: in a lit lab it can go dark well above 0 V (TR S9) | |
| 9.3 | M0 on TP45-TP46 | Bus voltage | At or below T11 (below 5 V) | Does not fall: R41 open. Use the discharge tool |
| 9.4 | V_ISO off, 12 V off. Unplug probes and cables | | | |
| 9.5 | Repeat 3.1 and 3.2 at the end of each test day | Same | Same as the first reading | Any change |
| 9.6 | Log the test | See below | | |

**Log every shot:** date, board number, stage, bus before pulse 1, V(DC+, DC−) at the end of pulse 1, L, t1, off-time, second pulse, I per cell at turn-off and at turn-on, V_DS peak and cell, probe and bandwidth, deskew values,
minimum V_GS and bump per LS FET, "not measured" for the HS FETs unless H1 is closed, V_ISO HS and LS, idle bus current, NTC reading, which cell had the MMCX cable on, whether a choke was on, scope file names. Loop inductance, where mentioned, is per cell.

## 10. Stop criteria

Stop means bus off, discharge, cause found before continuing.

| # | Criterion | Limit | Source |
|---|---|---|---|
| 1 | Any rule of 0.1 broken, or a probe on the wrong node | Any | MS rules |
| 2 | Open or dimpled via at TP33, TP1 or the y 61.3 rows | Any | MS bring-up 1 |
| 3 | Short between DC+, DC−, SW (before the inductor), or SW to LSRCx | Any | AR S5 |
| 4 | DC-link resistance | Below 57.6 kΩ after settling | Derived, BOM |
| 5 | Static V_GS,off | Outside −1.7 to −1.9 V at the governing channel: no switching | MS procedure |
| 6 | V_ISO needed for the window | Above 7.1 V | MS table |
| 7 | Static V_GS,on | Above 5.7 V (T6, proposal, Enes to confirm); never +6 V | MS, TR |
| 8 | Any V_GS, dynamic | Within 0.3 V of −4 V (at or below −3.7 V): add damping, not more bias | MS procedure |
| 9 | Bump on held-off gate | Above +0.3 V (T16, proposal, Enes to confirm) | MS, TR |
| 10 | Held-off HS gate not measured | No stage above S1 until H1 is closed or a decision is recorded | MS, H1 |
| 11 | **Pre-charge on TP45-TP46** | **Above 84 V: never** | SP |
| 12 | **U1 to U2 skew at the gates** | **Above 1 ns: no full-voltage shot** | SP (estimated 18 nH path) |
| 13 | V_DS peak reading | 98 V at 500 MHz, 93 V at 200 MHz, 87 V at 100 MHz probe; true limit 100 V | RL, EPC rating |
| 14 | Shot interval | Under 1 s, or bus not read before firing | SP |
| 15 | Leakage | Over 0.6 mA above baseline (T10, proposal, Enes to confirm), or rising | MS bring-up 4, TR |
| 16 | Shunt channel inverted | Any: reversed shunt or wrong cable | AR S4 |
| 17 | Current sharing | Over ±10 % of the mean (T17, proposal, Enes to confirm); about 4 % is normal | ER N7, TR |
| 18 | PWM | Extra, missing or short pulse; any pulse on INA | MS setup notes |
| 19 | PWM_H not tied to RTN with the bus up | Any | ER N8 |
| 20 | Supply current limit reached unexpectedly | Any | MS, ER N8 |
| 21 | L off target or falling with current | Slope off by over 10 % (T12, proposal, Enes to confirm) | Section 6, TR |
| 22 | Board temperature | Over +10 K above room (T18, proposal, Enes to confirm) | MS setup notes, TR |
| 23 | Unexpected waveform, smell, sound, D9 not as expected | Any | |

## 11. One-page checklist

**Before**
- [ ] T proposals confirmed, T1, T2, T3, T20 set; H1, H2, H4 decided
- [ ] Female IDC socket; M4 screw sized to the stack, not M4 x 8 by default
- [ ] B1 bus supply + 1 kΩ, B2 HS supply, B3 pulse source, B4 inductor, DIS arm line, B6 scope and probe in hand
- [ ] Bus and V_ISO supplies float; scope earthed

**Incoming (1)**
- [ ] Vias flat at TP33, TP1, y 61.3
- [ ] Rotation of U1, U2, Q1, Q2, D1, D3; R16-19, R35-38 absent
- [ ] No short J1, J2, J21; no SW to LSRCx short

**Assembly (2)**
- [ ] Block under J1/J2 (x 33-56, y 74-85), hold terminal, **1.2 N m**, lugs clear of TP45/46
- [ ] Shunt trial on the spare board
- [ ] Preheat on standoffs; TP45, TP46
- [ ] RS1-4: **IN to FET, SHLD to DC−**, SHLD side first; IN fillet checked
- [ ] Strain relief; 11 loops; links only if needed; nylon standoffs; pin-1 marks

**Unpowered (3)**
- [ ] TP45-46: 57.6 to 100 kΩ
- [ ] Eight V_GS pads about 10 kΩ
- [ ] Shields: board side, then instrument side unplugged from the board
- [ ] 50 Ω on SMA channels only

**Low voltage (4)**
- [ ] 12 V, VDDI 3.3 V; V_ISO 7.0 V, polarity checked
- [ ] Eight V_GS,off with meter; set to −1.7 to −1.9 V; V_ISO not above 7.1 V
- [ ] Eight V_GS,on, margin to +6 V, never H and L high together
- [ ] INA, INB at shortest pulse; U1 to U2 skew trimmed: **as low as possible; 3 ns at 40 V, 1.5 ns at 60 V, 0.5 ns at 80 V**
- [ ] Arm line fitted and tested
- [ ] **PWM_H tied to RTN on J5 and J14**

**DC link (5)**
- [ ] No inductor, disarmed. 1 kΩ in. Slow ramp, read TP45-46. 1.37 mA at 80 V
- [ ] Leakage read once, logged

**Inductor (6)**
- [ ] J21 to J1, torque T3; LCR in place, 1.0 µH ±5 %; shunt gain 0.957 mV/A checked
- [ ] J3, J12 and HS supply now live at bus potential
- [ ] L = V Δt / ΔI, two currents

**Stages (7), each stage**
- [ ] Each shot: bus on TP45-46, at most 84 V; at least 1 s since last shot; arm, fire, disarm
- [ ] Idle current; deskew valid
- [ ] Plan A: four currents, same sign, sum, L
- [ ] Plan B: V_DS each cell, **V(DC+, DC−) at end of pulse 1**; LS only, transients only, no 50 Ω; reading below 98 / 93 / 87 V at 500 / 200 / 100 MHz
- [ ] M1 (SMA unplugged): minimum V_GS above −3.7 V, bump, same probe
- [ ] HS gates: H1 status
- [ ] INB again, INA flat; temperature

**Full point (8)**
- [ ] H1, H4 decided; skew 0.5 ns or less; L measured, t1 corrected
- [ ] 80 V on TP45-46, 4.146 µs, 0.75 µs tuned, 300 ns
- [ ] Do not compare with 92.9 V or 125 µJ (1 mF deck)

**After (9)**
- [ ] Disarm; bus off first, gates still held; discharge tool; TP45-46 below 5 V; then V_ISO, 12 V off
- [ ] Repeat 3.1, 3.2; log everything

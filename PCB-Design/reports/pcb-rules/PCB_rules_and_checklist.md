# PCB rule set and design checklist: Rev B leg boards (DPT and load test)

Sources (all in `Application Notes/`):
- **[T]** B. Ben Hamed, *Design toolkit for PCB-based power electronic systems*, PhD thesis, INSA Lyon, 2025 (Ch. 1 §2–3, Ch. 5 §3).
- **[TI]** B. Genereaux, *PCB layout for switched-mode power supply*, TI High Voltage Seminar 2021 (`PCB-Design.pdf`).
- **[PAC]** Active-Semi, *PAC55XX PCB design and layout guide*.
- **[ADI]** Analog Devices, *Basic Linear Design*, Ch. 12 *Printed circuit board issues*.
- **[HS]** Sierra Circuits, *High-Speed PCB Design Guide* (EMC §5.4, vias §7.4, checklist §8.1).
- **[ST]** STMicroelectronics, *STPMIC2L PCB layout guidelines*.

The application notes barely give numbers for clearance and creepage ([PAC] and [TI] only point to IPC-2221 and UL/IEC). The numbers below therefore come from **IPC-2221B Table 6-1** and **IEC 60664-1 Table F.4**. The component data come from the 2EDF7275K datasheet (rev 3.0, Tables 17–19) and the EPC2361 and Murata MGN1 datasheets.

Board facts used below were measured with `scripts/domain_spacing.py` (KiCad DRC probe rules) and a scan of the copper under every choke.

---

## 1. Voltage domains of the leg board

| Domain | Nets | Potential |
|---|---|---|
| CTRL | J5/J14 connector, +12V, GNDI, PWM_H/L, DIS, driver input side | the controller's potential |
| HS | SW, KH, VDDA/VEEA, GH, OUTA, VINA (HS iso-supply input), U.FL H | 0…75 V against DC−, edges at 30–50 V/ns |
| LS | DC−, LSRC, KL, VDDB/VEEB, GL, OUTB, VINB, U.FL L/D, **NTC** | DC− |
| DCP | DC+, LED divider | +75 V |

These working voltages are fixed:
- HS ↔ LS ↔ DCP: 75 V DC, 90 V design peak, ≈100 V worst ringing.
- HS ↔ LS across the driver: limited by the 2EDF7275K channel-to-channel rating, 1.0 mm package creepage and 650 V DC test.

What is **not** fixed is **CTRL ↔ power**. It depends on where the controller is referenced:

| Case | CTRL ↔ power working voltage |
|---|---|
| Bench DPT / load test of one leg, controller GND tied to DC− (or to scope earth with the DC supply floating) | ≤ 100 V |
| Stacked inverter, one controller near earth driving all 16 levels | up to **1200 V DC** (top level), plus transients |
| Stacked inverter, a controller (or fibre/isolated PWM receiver and an isolated 12 V supply) local to each level | ≤ 100 V; the barrier then moves to that fibre/isolator |

**The 2EDF7275K has functional isolation only, with V_IOWM = 460 V** (datasheet Table 17; package creepage and clearance 3.4 mm, C_IO = 2 pF). It cannot be the barrier for the upper levels of a 1200 V stack driven from an earth-referenced controller. Before the system-level board, decide between:
- a per-level control reference (local controller or fibre PWM plus an isolated 12 V per level), or
- a reinforced driver: 2EDSx in WB DSO-16, which does not fit the current LGA footprint.

## 2. Proposed rule set

### 2a. Inside the power stage (HS / LS / DCP), functional insulation, ≤ 100 V

| Standard / case | Required | Board now |
|---|---|---|
| IEC 60664-1 Table F.4, printed wiring, PD2, 100 V | creepage ≥ 0.16 mm | 0.20 mm ✔ |
| IPC-2221B B1, internal layers, 51–100 V | ≥ 0.10 mm | 0.20 mm ✔ |
| IPC-2221B B4, external with permanent polymer coating (solder mask, tented vias), 51–100 V | ≥ 0.13 mm | 0.20 mm ✔ |
| IPC-2221B A6, external **uncoated** component leads/terminations, 51–100 V | ≥ 0.50 mm | 0.20 mm ✘ where pads of different nets face each other |
| IPC-2221B B2, external uncoated conductors, 51–100 V | ≥ 0.60 mm | ✘ |

Proposal (to be confirmed):
- **0.20 mm** between power-domain nets on all layers, with solder mask over the copper and all power vias **tented**, so that B4 / IEC PD2 apply.
- **0.50 mm** between *exposed* pads of different power nets where the footprint allows it (not inside the EPC2361 land pattern, which the device itself defines).
- Keep the 0.6 mm rule for the HV LED divider.
- Signal default 0.15 mm, only within one domain.

### 2b. Isolation barrier CTRL ↔ (HS, LS, DCP)

| Rule | Bench / per-level reference (≤ 100 V) | Match the 2EDF7275K (460 V) | 1200 V stack (needs another driver) |
|---|---|---|---|
| Outer layers (creepage) | 0.2 mm (functional) | **3.4 mm** (= package; IEC PD2 printed wiring at 500 V: 2.5 mm) | IEC PD2 printed wiring ≥ 5.0 mm at 1000 V and more above (material-group columns); IPC-2221B B2: 0.005 mm/V → 6.0 mm |
| Inner layers | 0.2 mm | **1.2 mm** (IPC B1: 0.0025 mm/V × 460 V) | 3.0 mm (IPC B1) |
| Through the dielectric (CTRL copper over power copper on adjacent layers) | allowed | not allowed: the 0.1 mm L1–L2 prepreg is not a defined insulation layer | not allowed |
| Barrier line | — | one straight line through the driver body; **no copper of either side crosses it on any layer** (pours, traces, vias) | same |

Recommendation: draw the barrier now for the 460 V case (3.4 mm / 1.2 mm). It costs little area and makes the board usable whenever the controller is not at DC−. The current boards meet none of the barrier rules (§3).

### 2c. Thermal interface (load board)
The top of the EPC2361 is internally connected to source. The four high-side tops therefore sit at **SW** potential and the low-side tops at DC−, all facing the heatsink (datasheet: *"TIM needs to provide electrical isolation to the heatsink"*). The gap pad must insulate the full heatsink-to-device voltage:
- ≤ 100 V if the heatsink is tied to DC− of the level;
- up to the level's potential to earth if the heatsink is earthed or touches a neighbour.

Write the chosen heatsink potential and the pad's dielectric rating into the BOM notes.

## 3. Measured spacing on the current boards

`scripts/domain_spacing.py`, minimum copper distance between domains (DPT board; the load board is the same within 0.05 mm):

| Pair | Min | Closest items | Verdict |
|---|---|---|---|
| CTRL ↔ LS | **0.20 mm** | KL1 / VDDB1 vias next to the GNDI1 pour (B.Cu); VDDB1 via 0.21 mm from the PWM_L1 trace | no barrier |
| CTRL ↔ HS | **0.76 mm** | SW via 0.76 mm from the +12V1 trace (F.Cu); SW vias 0.9 mm from the GNDI pours | no barrier |
| CTRL ↔ DCP | > 4 mm | — | ✔ |
| HS ↔ LS, HS ↔ DCP, LS ↔ DCP | 0.20 mm | EPC2361 pads, power vias next to inner planes | ✔ functional (§2a) |

Hundreds of CTRL-to-power pairs lie within 3.4 mm, because the GNDI corridor pours and the PWM/DIS/12 V traces run between the driver's output-side vias. The boards are fine for bench tests at 75 V with the controller referenced to DC−. They are **not** isolated designs.

## 4. Common-mode (CM) filtering: what is on the board

| Interface | CM filter now | Assessment |
|---|---|---|
| HS / LS isolated gate supplies (J3/J4, J12/J13) | ✔ WE-CNSW 744232601 per driver branch (L1, L2, L6, L7) | Right place. The CM current source is the supply module's isolation capacitance: MGN1 ≈ 2.5–4 pF at 30–50 V/ns gives ~0.1–0.2 A spikes. **But** a solid plane (KH/KL on In1, SW on In2 and B.Cu) runs 0.1 mm under each choke and under its input traces, and that capacitance bypasses the choke above ≈100 MHz [TI p. 23]. |
| 12 V control supply (J5/J14 pins 1, 2, 6) | ✔ L3, L8 (12 V + GND in one choke) | Correct pairing. GNDI plane under the choke (same remark). L8 also feeds the fan; the choke is rated 260 mA, so check the fan current. |
| PWM_H, PWM_L | ⚠ L4, L9 put **PWM_H and PWM_L in one choke**; their return current flows through the GND winding of L3 | CM blocking works, but each signal sees almost the full choke impedance (~µH) in series with 47 Ω / 100 pF → slower edges, ringing, extra delay. Fix: pair each signal with its own GND return (PWM_H+GND, PWM_L+GND, DIS+GND), or use a 4-line choke for the whole connector, or drop the signal chokes and use series R + local C (the driver barrier is only 2 pF). |
| DIS | ⚠ L5, L10 use **one winding only** (pins 3/4 open) | Acts as a series inductor, not a CM choke. Same fix. |
| DC+/DC− power input | ✘ none | Normal for a leg board. The DC terminals bolt to the level busbar, and a CM choke for 300 A does not belong on the leg. CM filtering of the inverter belongs at the battery input (system level). For the DPT bench: clip-on ferrite on the DC supply cable; keep the supply's earth/floating state defined. |
| AC output (M6 bolt) | ✘ none | Normal for a leg board (load inductor in DPT, motor winding in the inverter). Motor-side CM (bearing currents, winding-to-frame) is a system-level item, eased by the 75 V steps of the SPB. |
| NTC (J23) | ✘ none, **referenced to DC−** | This signal leaves the board from the power domain. If it goes to the controller it bridges DC− and CTRL. Measure it on the power side (isolated ADC, or route it through the driver side) or treat J23 as a DC−-referenced port; add an RC filter at the connector. |
| Fan (J15, block 2) | ✘ none (behind L8) | On the load board the fan sits on the heatsink, which couples to SW through the high-side tops (≈ several pF, §2c), while the fan is powered from the control side (GNDI2). That gives a CM path SW → heatsink → fan → GNDI → controller. Tie the heatsink to DC− with a short, low-inductance link (as [TI] recommends, *"ground the heatsink"*) and power the fan from the level side, or insulate the fan mounting. |
| U.FL probe points | n/a | U.FL H1–H4 are referenced to **KH = SW**. A coax shield on these swings at 50 V/ns: use isolated probing (optically isolated or isolated scope channel). LS points are referenced to KL/LSRC, which is fine with the scope referenced to DC−. |

## 5. Checklist distilled from the documents, with the status of the Rev B boards

| # | Check | Source | Rev B status |
|---|---|---|---|
| 1 | Power loop < 1 nH for WBG; turn-off overshoot ≤ 10 % of E (we accept 90 V = 20 %) | [T] §3.1.3 | 0.41 / 0.65 nH ✔; overshoot criterion is ours |
| 2 | Gate loop 1–2 nH for GaN | [T] §3.1.1 | 1.7 nH assumed in the models; extract from the routed gate star (Q3D) — **to do** |
| 3 | Kelvin source, gate return separate from the power path | [T] §3.1.2, [PAC] | ✔ |
| 4 | Gate resistors and pull-downs next to the FET | [PAC] | R_G at the FET ✔; 10 k pull-down at the star (≈ mm) ✔ |
| 5 | Symmetric gate tracks; the gate routing must not cut the power current path (current imbalance) | [T] Ch. 5 §3.3 | mirrored cells ✔; static sharing from the full-board DC Q3D — pending |
| 6 | Minimise switch-node copper area (C_AC → CM current) | [T] Ch. 5, [TI] | AC bus is full width on 4 layers: low R and L, large C to the busbar/heatsink. Quantify C_SW→heatsink and C_SW→busbar in Q3D — **to do** |
| 7 | Equal C_DC+ and C_DC− to the baseplate/heatsink (unequal values convert DM into CM) | [T] Ch. 5 | **to check** on the load board |
| 8 | Ground (tie) the heatsink | [TI] | **open** (§4 fan row) |
| 9 | EMI filters at input and output; no plane under CM chokes or EMI filters; choke input and output traces must not cross | [T] §3.1.4, [TI] | planes under all 10 chokes ✘; DC/AC filters at system level |
| 10 | Signals leaving the board: series R or ferrite bead; 45° corners | [PAC] | PWM 47 Ω ✔; NTC, fan unfiltered ✘ |
| 11 | Differential sense lines symmetric; filter capacitor at the receiver | [PAC], [ADI] | shunt sensing goes to U.FL (coax) ✔ |
| 12 | Star connection of power, driver and logic grounds; no slots in return planes; no traces over plane gaps | [PAC], [ADI], [ST], [HS] | GNDI per block ✔; check the inner-layer splits under PWM/DIS — **to check** |
| 13 | Decoupling at the IC pins, short and wide, vias right at the pads | [PAC], [ST], [ADI] | driver decoupling ✔ (0603 at the pins) |
| 14 | Current per via 1–3 A ([TI]); 8 mil (0.2 mm) via ≈ 0.8 A for 5 °C rise ([HS]) | [TI], [HS] | DC/AC terminals and power vias: count vias per path against the current — **to do** |
| 15 | Creepage/clearance per IPC-2221 / UL / IEC 60664 by insulation type | [TI], [PAC] | §2–3: power stage ✔, isolation barrier ✘ |
| 16 | Thermal: solid planes, thermal vias under hot parts, no splits in heat paths | [TI], [T] | load board heat goes to the top through the gap pad; PCB is secondary ✔ |
| 17 | Fab notes: IPC class, stack-up with copper and dielectric thickness, blind vias, mask colour, minimum annular ring, drill chart and tolerances, ≥ 3 fiducials, pin 1 / polarity, connector pin names on silk | [HS] §8.1 | silk and pin names ✔; **add a fab drawing** with the stack-up (0.1 mm L1–L2), blind L1–L2 vias (load), tented vias, IPC class 2, fiducials |

## 6. Implemented in Rev B (2026-10-16)

Enes decided: put clearance and creepage for **1200 V** on the boards (only one level is tested now, at full switching speed). The DPT board has no heatsink. The NTC is measured from the control side. Common-mode filtering goes on the board.

**Rule set.** `scripts/make_kicad_bb_revb.py` writes `<board>.kicad_dru` into both projects. KiCad's DRC checks it, with the voltage domains given as exact net-name lists:

| Rule | Value | Basis |
|---|---|---|
| Control ↔ power domains, outer layers | ≥ 4.0 mm | IPC-2221B B4/A6 at 1200 V with solder mask: 3.66 mm |
| Control ↔ power domains, inner layers | ≥ 3.0 mm | IPC-2221B B1: 0.0025 mm/V |
| Control ↔ power inside the 2EDF7275K courtyard | ≥ 3.0 mm (the package gives 3.35 mm) | component-defined |
| Between power domains (HS / LS / DC+) | ≥ 0.2 mm, tented vias | IEC 60664-1 PD2 / IPC B4, 75 V functional |
| Bare pads of different power nets, outer layers | ≥ 0.5 mm (EPC2361 land pattern and the shunt IN land excepted) | IPC-2221B A6 |
| Bare pad to the (masked) pour of another power domain, outer layers | ≥ 0.5 mm (top-side EPC2361 land pattern excepted); the pours pull back | same as above: a bare pad and its fillet face the pour edge |
| Power terminal pins J1 (DC+), J2 (DC−), J21 (AC) to another power domain, outer layers | ≥ 1.0 mm | large hand-soldered fillets on the bus rails, bank behind them |
| Inner-layer neighbours across the 0.1 mm prepreg (L1–L2, L3–L4) | ≥ 3.0 mm in-plane offset between control and power copper | by construction (keepouts), not checked by DRC |

**Layout.**
- **Control area per block:** right below the driver, |x_r| ≤ 6.75 mm, y 21.6–40.5 mm. All SMD on the top layer, plus a small GNDI plane on the bottom (|x_r| ≤ 6 mm) that joins the top pour.
- **Barrier keepouts** (no pour, tracks or vias) around the control area:
  - top and bottom layers: 4 mm;
  - L2: no copper within 3 mm;
  - under the chokes and the connector: no copper on any layer.
- **L3 under the control area:** clear. The gate-supply routes leave the driver sideways on L3 and run around the control area.
- **Gate-supply islands** moved to |x_r| = 10.9–16.0 mm; the AC columns on L1/L2 now start at |x_r| = 16.6 mm.
- **Driver output decoupling** moved to the bottom side.
- **AC bus and bolt** moved down 5.2 mm: the board is now **89.5 × 85.2 mm**.

**Common-mode filtering.**
- **Control connector:** a 2 × 5 SMT header where every signal has its own return pin: PWM_H, PWM_L, DIS, 12 V and NTC (block 1).
- **One WE-CNSW choke per signal/return pair:** 5 chokes on block 1 and 4 on block 2.
- **12 V:** a ferrite bead after the choke (Murata BLM18PG221SN1, 220 Ω at 100 MHz) and 4.7 µF.
- **Pull-downs and inputs:** 10 k pull-downs on PWM; the 47 Ω + 100 pF input filters at the driver stay.
- **No plane under any choke** on any layer. The isolated gate supplies keep their chokes and now also have no plane under them.

**Results.**
- **DRC:** 0 violations and 0 unconnected on both boards with the rule file active; schematic = PCB (0 problems).
- **Spacing measured** with `domain_spacing.py`:
  - control ↔ power on outer layers ≥ 4.0 mm, except the driver pins and their escape traces (3.35–3.6 mm, set by the package);
  - inner layers ≥ 3.35 mm.

**Bare pads and 0603 (follow-up, same day).** The 0.5 mm bare-pad rule moved bank capacitor row A up by 0.25 mm and the top bypass row 0.1 mm towards the bank (both previously 0.30 / 0.45 mm). All 0402 parts became 0603 for hand soldering; the V_DS port is treated separately (next paragraph). The driver input side was re-placed. The external 10 k PWM pull-downs and the 12 V 4.7 µF were dropped: INA, INB and DISABLE have internal 150 k pull-downs, and the 12 V only feeds VDDI through 3 k.

**Removed.**
- The DC−-referenced NTC header J23; the NTC is now RT1 in the control area of block 1.
- The 12 V LED.
- The fan header on block 2. On the load board the fan is supplied from the bench.

**Still limited.** The 2EDF7275K is functional isolation with V_IOWM = 460 V. The PCB is now laid out for 1200 V, but a stack test above ≈ 460 V between the controller and a level needs a reinforced driver (2EDS, WB DSO-16).

**To redo.**
- The Q3D loop of the DPT board, because the DC− copper next to the inner shunt ends was trimmed by the barrier.
- The lx and full-board DC models, because the AC bus moved.
- The 3D renders and the assembly STEP.

**Pad-to-pour and terminals (follow-up).** The 0.5 mm bare-pad rule only checked pad against pad. The DC− terminal pins therefore sat 0.2 mm from the top-side DC+ pour, and J1 likewise in the bottom DC− pour. Two rules were added on the outer layers:
- bare pad to the pour of another power domain: 0.5 mm;
- terminal pins J1, J2, J21 to another power domain: 1.0 mm.

The pours pull back automatically, on the bank capacitors C75–C82, the U.FL ports with their 0603 and 2512 resistors, and the gate resistors. The FET exception now uses `existsOnLayer('F.Cu') && insideFrontCourtyard('Qk')`. The earlier `insideCourtyard('Qk')` also excused the bottom-side U.FL parts under the FETs; this affected the pad-to-pad rule too.

Vias stay at 0.2 mm:
- All vias are tented, which puts them in IPC-2221B B4 (outer) and B1 (inner), both ~0.1–0.13 mm at 75 V.
- The hole wall to copper of another net is ≥ 0.30–0.35 mm.
- Opposite-polarity power via barrels are ≥ 1.55 mm apart, so CAF is not a concern at 75 V.
- Larger antipads would widen the slots that the 0.7–1.0 mm-pitch DC− via rows already cut into the foreign planes (1.0 mm antipads with the unused inner rings kept).

Both boards: DRC 0/0, schematic = PCB.

**Read-only review of 19 October 2026 (`spb-bb-revb-dpt-review-2026-10-19.md`), DPT board: dispositions.**
1. *V_DS U.FL underrated.* Hirose rates the U.FL-R-SMT-1 at 30 V. The four V_DS U.FL ports are replaced by Würth WR-MMCX 66012102111404 vertical SMT jacks (170 V rms working, 500 V rms withstanding).
   - Connections: centre = SW (LS drain), shield = LSRCx (device side of the shunt), on the bottom between the DC− via field and the next via rows.
   - Shield: reaches LSRC through the LSS via from the shunt IN land. Centre pin: a 0.4 mm stub between the shield pads into the switch-node pour.
   - Vias: the mirrored power-via pruning removes about 25 DC− vias per cell under the jacks (238 of 1274 power vias are pruned in total, 138 before).
   - Intended for a rated isolated probe with an MMCX tip, e.g. IsoVu TIVP + TIVPMX50X. The U.FL ports remain for V_GS only.
2. *Fresh DRC differs from the saved report.* The project file had no rules section, so a fresh load used KiCad's defaults (0.5 / 0.3 mm vias). The generator now writes the rules into `.kicad_pro`:
   - track 0.2 mm, clearance 0.2 mm, connection 0.2 mm, via 0.45 / 0.25 mm, annular ring 0.1 mm;
   - hole clearance 0.25 mm, hole to hole 0.25 mm, copper to edge 0.3 mm, mask web 0.1 mm;
   - Default netclass 0.2 mm clearance;
   - missing courtyard = error.

   A fresh load and DRC of a copy of the saved project gives 0 violations, 0 unconnected, 0 footprint errors. **The 0.45 / 0.25 mm gate-area vias and the 0.2 mm floor for 2 oz copper need the fab's confirmation.**
3. *Manufacturing safeguards.* The new limits exposed real issues, all fixed:
   - 0.1 mm necks in the inner planes between via antipads: unused inner annular rings removed on all vias (outer rings kept), and a 0.25 mm minimum fill width on the inner planes.
   - Test points without courtyards: courtyards added and checked.

   The library checks stay off on purpose: the generator saves its own modified footprints to `spb_fab.pretty`.
4. *"1200 V" rule is not an insulation design.* Agreed; see section 7 and the 460 V functional isolation of the 2EDF7275K. The driver exception is narrowed: inside the U1/U2 courtyard only pads and their pin-escape tracks get 3.0 mm, while pours and vias keep 4.0 / 3.0 mm.
5. *Measurement grounding.* See `DPT_measurement_setup.md`: port table, reference of every shield, connection rules and diagram.
6. *Documentation.*
   - The measurement slide describes the MMCX ports and the test points.
   - The mechanical BOM takes the AC bolt reference from the board.
   - The stale silk plots are archived in `plots/superseded-2026-10-15/`.
   - The generator writes `pad_nets.json` itself, and the schematic check runs against the saved board.

Open: rerun the Q3D loop model of the DPT board. About 100 DC− vias near the shunts are gone, and the inner planes changed. Not yet done for the load board.

## 7. Decisions needed (status 2026-10-16)

Items 1–6 were answered as described in §6. Item 1 is open for the stack only.

## 7a. Original decision list

1. **Controller reference in the stack**: per-level reference (keep the 2EDF7275K) or one earth-referenced controller (reinforced driver, new footprint)?
2. **Barrier rule for Rev B**: implement the 460 V barrier now (3.4 mm outer / 1.2 mm inner, no crossing), or keep the bench-only layout?
3. **Power-stage rule**: 0.2 mm with tented vias (IEC 60664-1 PD2 / IPC B4), or 0.5 mm between exposed pads (IPC A6)? Conformal coating on the load board?
4. **Signal chokes**: re-pair PWM/DIS with their returns, use a 4-line choke, or replace them with R/C filters? Void the planes under all chokes?
5. **Heatsink potential**: tie it to DC− (recommended) and power the fan from the level side?
6. **NTC**: measure it on the power side, or isolate it?

**V_DS port (follow-up, final).** The 4.99 kΩ 2512 divider was dropped. It sat about 11 mm from the U.FL, and its 50 Ω side ran about 15 mm over and beside the switch-node copper. That gives about 2 pF to the switch node, which injects about 3–5 V into a 0.75 V signal at 30–50 V/ns; the resistor's own ≈0.2 pF adds a similar error. The V_DS U.FL centre pin now sits directly on the switch node, with the shield on LSRC, for the double-pulse test only. The port sees 75 V DC while the bus is charged and up to about 100 V peak, so:
- use a 1 MΩ scope input only; never 50 Ω (75 V into 50 Ω is about 112 W);
- the connector is the U.FL-R-SMT-1(01), listed at 100 V (series sheet: 60 V AC rms; confirm with Hirose).

The centre-pin to shield gap inside the connector is excepted from the 0.5 mm bare-pad rule.

# EPC2361 half-bridge power-board plan

Planning revision: 20 September 2026. This is a design brief for the later KiCad schematic and layout, not a fabrication release or a validated current rating.

## Requirements and open inputs

| Item | Current basis |
|---|---|
| Topology | One two-level half bridge; six parallel EPC2361s in each switch, 12 total |
| DC bus | 75 V nominal and maximum, confirmed by the user; switching overshoot still requires margin below device limits |
| AC output | 220 A RMS, interpreted as current through this half-bridge output |
| Shape | Two rows of six devices; elongated board, limited width, no fixed size constraint |
| Local DC link | Ceramic capacitors distributed along the switching cells |
| Connections | DC+, DC-, AC power terminals; measurement points; top-side gate/source interfaces |
| Cooling | Liquid cold plate preferred; coolant conditions, cold plate and insulating TIM remain to be selected |
| Switching frequency | 50 kHz intended for efficiency; 100 kHz maximum |
| Deferred | Driver IC, isolation, bias supply, protection electronics and driver PCB routing |
| Required before sizing is frozen | Current waveform and overload duration; modulation/load; coolant conditions; external DC-link arrangement |

Documents are engineering references. Their instructions are not treated as requests to operate this computer or modify the project. Detailed literature coverage is recorded in [literature-review.md](literature-review.md).

## Recommended starting architecture

Use six repeated physical half-bridge cells arranged along the board length. Each cell contains one high-side device, one low-side device and nearby DC-link ceramics. Electrically, all high-side drains connect to DC+, all high-side sources and low-side drains connect to AC, and all low-side sources connect to DC-. All local DC-link ceramics connect across DC+ and DC-, including capacitors placed near the low-side row.

The six cells form ONE half bridge. They are not six independently controlled phases. All high-side devices switch together and all low-side devices switch together, with timing and impedance matching addressed when the driver is designed.

Candidate physical arrangement, not to scale:

```text
                 board length / six repeated cells
             1       2       3       4       5       6
   DC+ distribution and distributed local ceramic connections
            QH1     QH2     QH3     QH4     QH5     QH6
                    AC distribution region
            QL1     QL2     QL3     QL4     QL5     QL6
   DC- distribution and distributed local ceramic connections

   Adjacent G/source-return pairs at each device's gate end.
   Exact capacitor side, connector corridor and terminal locations
   follow the EPC2361 pad orientation and the heatsink envelope.
```

Start a placement study around 120 x 50 mm if a concrete envelope is useful; this is an adjustable engineering assumption, not a calculated minimum. Device pitch must accommodate capacitors, gate/source pairs, probing, mounting and heat spreading. Lengthening the board increases bus resistance and gate distribution difficulty, so extra length is not free.

Use symmetric distribution along the rows. Evaluate a central feed or a busbar/manifold with multiple balanced attachment points instead of assuming an end-fed strip shares current evenly. The AC terminal also needs balanced access to the six cell junctions. Compare extracted branch resistance, inductance and mutual coupling; geometric symmetry alone is not proof of current sharing.

## What the EPC2361 datasheet establishes

Source: supplied `Datasheet/EPC2361_datasheet.pdf`, revision 2.4, 20 July 2026.

| Property | Verified value | Design consequence |
|---|---|---|
| Continuous VDS maximum | 100 V | 75 V leaves only 25 V to the absolute rating before bus excursions and switching overshoot |
| Repetitive transient VDS | 120 V with duty factor <=1% | Do not use this as the normal bus or repetitive switching design target |
| RDS(on), 25 C, VGS=5 V | 0.75 mOhm typical, 1 mOhm maximum | Use temperature dependence and mismatch, not typical resistance alone |
| Gate operation | 5 V on, 0 V off recommended; absolute limits +6/-4 V | Gate-loop overshoot must be controlled; driver selection remains deferred |
| Gate charge at stated 50 V/50 A test point | 28 nC typical, 34 nC maximum | Six devices present 168/204 nC per bank at those conditions |
| Package | 3 x 5 mm, nominal height 0.65 mm | Requires the exact manufacturer footprint, mask and paste geometry |
| Top surface | Internally connected to source | Insulating TIM is required under a common heatsink; top is not a gate connection |
| Thermal resistance | RthetaJC(top)=0.2 K/W; RthetaJB=1.5 K/W, typical | These exclude TIM, spreading, heatsink and board-to-air effects |
| Pin assignment | 1 gate; 2/4/6 source; 3/5/7 drain | Kelvin return must be routed from the source pad nearest the gate |

Pages 1-2 give ratings and electrical data; page 5 gives cooling; page 6 gives layout; pages 10-13 define package, copper, mask and stencil. The exposed top must not be used as an electrical terminal. Use the solder-mask-defined land pattern and the recommended 100 um laser-cut stencil as the assembly starting point, subject to assembler review.

The 133 A headline continuous device rating is not a PCB or module rating. Multiplying it by six does not establish module capability.

## Current, loss and voltage budgets

For a sinusoidal 220 A RMS output, before PWM ripple and overload:

- Output peak = sqrt(2) x 220 = 311.1 A.
- Ideal instantaneous peak per conducting parallel device = 311.1/6 = 51.9 A.
- With equal current-squared sharing between high and low banks over a cycle, each physical device carries 220/(6 sqrt(2)) = 25.9 A RMS. Actual duty, modulation, ripple and imbalance must be included in the final model.
- Ideal combined channel conduction loss of the HALF BRIDGE is I_RMS^2 x RDS(on)/6: 6.05 W using typical 25 C resistance, or 8.07 W using maximum 25 C resistance. There is no extra factor of two because the banks conduct at different times.
- These figures exclude hot resistance, switching loss, dead-time reverse conduction, gate-drive loss, capacitors, copper, vias and contacts. They cannot size the heatsink by themselves.

Use a provisional 90 V peak VDS screening ceiling for initial studies, pending the agreed voltage margin. If the true maximum bus is 75 V, this leaves 15 V for dynamic overshoot. If 75 V is nominal and the bus rises, that budget shrinks. The final criterion must be based on worst-case measured VDS and the complete operating envelope.

An illustration of why shared inductance matters: commutating 311 A in 20 ns gives 15.6 A/ns. A common 1 nH segment then contributes about 15.6 V by L di/dt. A 15 V allowance corresponds to about 0.96 nH for that common segment alone. A local branch carries a smaller current step, but its inductance, mutual coupling and the common contribution must all be included. This is a sensitivity example, not an extracted board inductance or a chosen switching time.

For copper, a 100 mm long, 20 mm wide, 70 um thick strip has about 1.23 mOhm at 20 C and dissipates about 59.6 W at 220 A RMS. Actual distribution current is position-dependent, but this example shows why a long PCB plane cannot be accepted on width alone. Evaluate multiple copper layers and dedicated copper busbars, including via and contact losses.

## PCB and loop plan

Prefer the EPC2361 inner vertical power-loop arrangement: top-layer outgoing current and a return immediately beneath it on the first inner layer. Keep the dielectric thin subject to fabrication capability and voltage requirements. A roughly 0.1 mm top-to-first-inner spacing is an initial stackup inquiry, not a released specification.

Start by comparing a six-layer, 2 oz copper construction against a four-layer option with busbars. Six layers is a planning preference for distribution flexibility; it is not required by the transistor. The first inner layer must preserve the local power return and local source-reference geometry; do not automatically make every reference region a single DC- plane. High-side gate return belongs to AC/source, not DC-.

Use the remaining layers for parallel power distribution and thermal spreading with explicit net assignments after a cell is placed. Keep the construction mechanically balanced. EPC AN031 cautions that copper thicker than 2 oz creates fine-pitch etching difficulties. The reference paper's 4 oz outer layers are not automatically suitable for this package and fabricator.

Minimize common source inductance. Place each Kelvin takeoff next to the source pad nearest the gate and keep gate and power loops approximately perpendicular as shown on datasheet page 6. Use short via groups at current transitions without cutting slots into the paired return. Any via-in-pad needs a fabricator-approved filled/capped process; do not use open holes in solder lands.

Measure or extract local loops, shared distribution and branch imbalance. Neither copper thickness nor a formula for a parallel-plane segment proves a complete sub-nH switching loop.

## Ceramic capacitor shortlist and sizing

Initial candidates verified on manufacturer product pages, 19-20 September 2026:

| Candidate | Nominal specification | Role to evaluate |
|---|---|---|
| TDK C3225X7R2A225K230AB | 2.2 uF, 100 V, +/-10%, X7R, 1210; 2.3 mm nominal thickness | Main distributed bank candidate with tighter temperature characteristic |
| TDK CGA6M3X7S2A475K200AB | 4.7 uF, 100 V, +/-10%, X7S, 1210; 2.0 mm nominal thickness | Higher nominal density option, subject to retained capacitance and heating |
| TDK C2012X7S2A105K125AB | 1 uF, 100 V, +/-10%, X7S, 0805; 1.25 mm nominal thickness | Smaller local placements where they reduce connection inductance |

These are candidate parts, not an approved BOM or a claim that their nominal capacitance remains available at 75 V. The older 20%-tolerance C2012X7S2A105M125AB is marked NRND by TDK; use the current K-tolerance part as the comparison candidate. Automotive qualification does not imply soft termination.

Sources:

- [TDK 2.2 uF X7R](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3225X7R2A225K230AB)
- [TDK 4.7 uF X7S](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA6M3X7S2A475K200AB)
- [TDK 1 uF X7S](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012X7S2A105K125AB)
- [TDK NRND status of older M-tolerance part](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012X7S2A105M125AB)

For selection, obtain C(V,T,frequency), tolerance, ageing, impedance/ESR and ripple self-heating data at the actual conditions. Manufacturer product data was readable, but the attempted downloadable TDK characteristic sheet was denied by its server; numerical retained capacitance and ripple capability have not been verified. Compare higher voltage and soft-termination alternatives if the maximum bus, retained capacitance, board flex or reliability requirements justify them. A higher rated voltage alone does not guarantee better DC-bias retention.

Distribute matching capacitor groups among the six cells, connect both ends with short broad copper and local return vias, and keep them clear of mounting-force zones. Avoid automatically mixing decades of capacitance: check bank impedance and anti-resonance first. Count and pitch follow the required effective capacitance and RMS heating, not a photograph.

Separate the fast commutation requirement from PWM energy buffering. As a charge-only illustration, supplying the full 311 A for 50 ns with 3 V droop needs C_eff >= I dt/dV = 5.19 uF in total, before ESR/ESL. This is not the required finished bank: supplying PWM-period energy may need far more capacitance. Define the nearby external bulk DC link, connection inductance and current waveform. The local ceramics alone must not be assumed to support the entire 220 A PWM current for a switching period. Check resonance between low-ESR ceramics and supply/busbar inductance and provide damping where needed.

## Power terminals, measurement and driver interface

Use three logical power ports, DC+, DC- and AC. At this current, prefer bolted copper connections or manufacturer-rated high-current connectors supported mechanically by the enclosure/busbar. A power-port name does not imply one tiny solder contact. Evaluate multiple balanced attachment points, bolt/contact resistance, temperature rise and torque loads. Do not copy the paper's parallel 2.54 mm headers as a 220 A rating.

Keep DC+ and DC- feeds adjacent/overlapping with insulation to reduce supply loop inductance. Size their RMS and average currents from the modulation and external capacitor arrangement; AC RMS does not equal DC average current. Route the AC connection for equal cell access and keep switched copper no larger than needed for current and cooling.

Reserve a top-side gate and adjacent Kelvin-source pair for EACH device: GH1/SH1 through GH6/SH6 and GL1/SL1 through GL6/SL6. These are PCB contacts beside the package, not contacts to its exposed top. The source-return branches connect locally to their own device sources. Do not carry power current through the Kelvin return or join the source returns into a long shared power path.

Provide an individual gate-resistor footprint close to each gate, with optional gate-source bias resistor footprints. Values and any separate turn-on/turn-off paths will be determined with the driver. Preserve short paired connections, connector voltage clearance, matched branch impedance and protection against plugging the driver in backwards. The minimum logical interface is 12 gate/source pairs (24 contacts); physical grounds/shields or separate turn-off contacts may require more. Do not freeze a long common header or a high stacking height before gate-loop analysis.

Recommended probing provisions:

- Compact differential VDS pad pairs at representative high/low cells, with optional access across the row to compare edge and centre devices.
- Adjacent gate/source probe pads for all 12 devices where mechanically feasible.
- DC+/DC- pads at the local ceramic bank and AC/DC- pads near the low-side bank.
- Accessible low-frequency voltage test points near terminals, separate from high-bandwidth probing.
- Two temperature-sensor locations, one per device bank, and an optional third near the ceramic bank or hottest terminal. Specify the sensor later; an NTC reading is not junction temperature without calibration.
- Space for a nonintrusive output-current sensor outside the commutation loop. Avoid inserting a shunt into a shared source path just for convenience.

High-side VGS and floating-node measurements require an appropriate differential/isolated probe. Do not connect an earth-referenced scope ground to AC or a high-side source. Keep fast probe connections short; tall test loops and long ground leads distort GaN switching measurements.

Reserve symmetric optional RC-snubber sites where their local loop can remain short. Leave them unpopulated initially; select values from ringing measurements and loss calculations rather than copying another board.

## Cooling and mechanical integration

Preferred starting concept: an elongated top heatsink or cold plate over the two FET rows, with an electrically insulating, thermally conductive interface; mount the future driver board in a side corridor or use cutouts so it does not occupy that heat path. If the driver must cover the whole power board, reconsider the mechanical stack before routing. Bottom-only cooling is an alternative requiring a fresh thermal calculation, not an equivalent substitute.

Use a controlled heatsink gap, supported mounting points/backing, and specified TIM compression. Check capacitor height: the shortlisted 1210 parts stand much higher than the 0.65 mm FETs, so a flat heatsink must have a suitable contact region or machined relief. Do not simply increase the TIM thickness until it clears every capacitor, because that increases thermal resistance.

Evaluate junction-to-top, TIM, heat spreading and heatsink-to-air/coolant resistance along with the parallel PCB heat path. Calculate losses at hot RDS(on), actual switching frequency, current waveform, dead time and gate drive. Include neighbouring-device thermal coupling and airflow variation along the row. Size the cooling system only after those losses and ambient/coolant conditions are known.

Provide a deliberate heatsink/chassis bonding option for EMI evaluation. EPC recommends grounding the heatsink, but the system grounding scheme decides how; do not silently short chassis to DC-. Include switched-node capacitance to the heatsink in common-mode-current analysis. Insulating TIM remains required even if the heatsink floats.

## Proposed power-board content

| Item | Planned provision | Release status |
|---|---|---|
| EPC2361 | 12 devices, exact manufacturer pad/mask/paste geometry | Device selected |
| Local MLCC groups | Six matched distributed groups across DC+/DC- | Candidate parts above; quantity pending |
| External bulk link | Defined DC+/DC- busbar/interface | Capacitance and mounting pending system data |
| Gate components | 12 individual series-resistor sites, optional bias-resistor sites | Values pending driver work |
| Driver connection | 12 nearby G/Kelvin-source pairs on top | Connector and mechanical envelope pending |
| Power connections | Three rated logical ports with mechanically supported current paths | Terminal hardware pending |
| Probe points | VGS pairs, VDS pairs, DC-link and output pads | Probe geometry to be selected |
| Thermal sensing | Two bank locations plus optional third hotspot location | Sensor part and readout pending |
| Snubbers | Symmetric, short optional footprints | DNP until characterized |
| Cooling hardware | Insulating TIM, heatsink/cold plate, supported mounts | Size and hardware pending loss budget |

## Work sequence for the later KiCad agent

1. Resolve maximum bus, switching frequency, cooling and external DC-link data. Establish acceptable voltage margin and temperature rise.
2. Verify the EPC2361 symbol and footprint against datasheet pages 10-13, including pin numbering, copper, mask and paste; create project-local libraries if needed.
3. Place one complete high/low cell with capacitors, gate/source interface and heatsink keepouts. Review both power and gate return paths and assembly feasibility.
4. Replicate six cells into the two rows, then design the balanced busbar/terminal distribution. Compare the four- and six-layer options using resistance, inductance and fabrication constraints.
5. Review the 3D assembly including driver corridor, capacitor height, insulation, bolts, backing plate, probes and tool access.
6. Run schematic checks and PCB DRC, confirm net connectivity and manufacturing rules, and perform electrical/thermal modelling. DRC alone does not verify GaN current sharing or a 220 A rating.
7. Plan reduced-energy double-pulse testing, current-sharing verification, switching-overvoltage measurements and thermal tests before full-current operation. Verify both current directions and the maximum bus condition.

KiCad 7.0.10 is installed and its CLI was verified. The user has now authorized one high-side/low-side pair as a schematic and placement study under hardware/epc2361-cell. The six-cell module and manufacturing release remain subsequent work. Earlier conditional discussions above are retained as design reasoning; the confirmed bus and frequency in the requirements table supersede their open-input wording.

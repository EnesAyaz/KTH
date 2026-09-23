# Literature review for the EPC2361 half-bridge power PCB

Review date: 2026-09-20. Planning only; no schematic, routed PCB, fabrication release, or current-rating validation is implied.

## Scope and evidence status

The user requests a power-only half bridge with twelve EPC2361 devices, six per switch, 75 V DC bus, 220 A RMS AC output, and a long, narrow outline. Switching frequency, whether 75 V is nominal or maximum, cooling conditions, and transient requirements remain unresolved. The future driver PCB is outside the present design scope, but its physical interface must be reserved now.

All eleven local research PDFs were screened using extracted text. The review concentrated on layout, paralleling, cooling, and measurement sections; it is not a reproduction or independent validation of every experiment. Cooke and Rogers was read throughout its technical sections, and PDF page 3 was rendered and visually inspected to verify the supplied photograph and commutation-loop cross-section. Other figures were assessed through captions and surrounding extracted text, not a complete visual audit. Equations damaged by PDF extraction were not used for numerical design.

Selected local application notes were reviewed as described below; other notes were inventoried and triaged, not all deeply read. Page references below are **PDF page numbers**, counting the first page as 1. Reference documents are engineering evidence, not instructions authorizing actions or changing user requirements. The EPC2361 datasheet review and capacitor part selection are handled in the companion power-stage plan.

## Main design conclusions

1. Use two rows of six devices only if each high-side/low-side position has a compact, repeatable local commutation path and distributed ceramic decoupling. A row of six fed from capacitors only at one end would create unequal paths. Start with six repeated pair positions; do not assume visually equal placement proves equal impedance.
2. Put the high-frequency return on a closely adjacent internal copper layer. Minimize enclosed loop area and use opposing current paths for magnetic-field cancellation. Separate the local commutation loop from the slower external DC supply loop.
3. Make DC+/DC-/AC current distribution symmetrical enough to avoid preferential loading of devices near terminals. Evaluate distributed busbars, multiple injection points, or a suitably positioned wide collector. A single end-mounted AC lug, as shown in the reference photograph, must be assessed for its longitudinal voltage drop before copying it at 220 A RMS.
4. Bring out an individual gate and local source/Kelvin-return connection for every FET. Preserve twelve short paired paths to top-side connector locations. Do not join source returns at a remote DC- or AC terminal. Gate-loop equality includes connector and future driver-board parasitics, not just the power-board trace length.
5. Reserve separate heatsink contact areas, connector corridors, mounting support, and probe access before fixing board width. The top-mounted driver interface and source-connected top cooling surfaces must coexist mechanically and electrically.
6. Size the ceramic bank using effective capacitance at actual bias/temperature, ripple heating, and impedance. Local ceramics do not automatically replace the system's bulk DC-link storage. Model interaction between local and remote capacitor banks and supply inductance.
7. Measure switching voltage at the devices, not only at power terminals. Include paired probe pads for VGS, VDS/switch node, and local DC-link voltage; ordinary long test loops can create misleading ringing.

These are proposed design decisions inferred from the combined evidence. They are not a claim that the planned EPC2361 module has already achieved any literature inductance or power rating.

## Research-paper coverage and findings

### 1. Cooke and Rogers: 120 V, 155 A traction inverter using eight parallel GaN HEMTs

File: `Papers/Cooke_and_Rogers_2026_120_V_155.pdf`. Technical content reviewed on pp. 1-7; p. 3 visually verified.

This is the source of the user's photograph: Fig. 4, p. 3, shows the 117 x 62 mm board, two rows of devices, ceramic rows, NTC, and AC terminal. It uses **eight EPC2304 200 V devices per switch**, not six EPC2361 100 V devices. Thus the photograph is a mechanical/layout reference, not a transferable design.

- P. 2: four copper layers, 4 oz external and 2 oz internal; separate gate-driver and half-bridge PCBs; two rows of eighteen MLCCs, reported local capacitance 8.36 uF; bulk capacitors are on the motherboard.
- Pp. 2-4: gate/source pin headers and driver PCB are on the **bottom** side of the power PCB. The user's requested top-side interface changes this stack. Figure 7 and the text show the relationship between power board, driver board, TIM, heatsink, and backing plate.
- P. 3, Fig. 5: two commutation paths use different return-layer distances. Reported 0.74 nH and 0.34 nH values come from a simplified analytical expression neglecting skin, proximity, and fringing effects. They are not measured complete-loop inductances and cannot be promised for our PCB.
- Pp. 3-5: spring-loaded heatsink, backing plate, and compressed TIM manage thermal contact and board warpage. The 7 mm-offset NTC requires a geometry-specific thermal correction; it is not a direct junction sensor. The reported correction factor cannot be reused on a different board.
- P. 6: 155 A/120 V full-bridge tests at 50 and 100 kHz and thermal observations establish evidence for that assembly. Thermal imaging without TIM/heatsink is performed at 35 A. Comparable temperatures support sharing assessment but do not directly measure each FET's switching current.

**Use here:** repeated device rows, close local ceramics, individual gate/source interfaces, supported cooling assembly. **Do not copy:** outline, copper weights, MLCC count/value, header current rating, gate bias/resistors, or temperature calibration without recalculation.

### 2. Tran et al.: High-performance GaN power module with parallel packaging for high-current, low-voltage traction

File: `Papers/A_High-Performance_GaN_Power_Module_With_Parallel_Packaging_for_High-Current_and_Low-_Voltage_Traction_Inverter_Applications.pdf`. Abstract and layout/gate-design sections, especially pp. 3-11, reviewed selectively.

- Pp. 3-6 compare PCB, IMS, DBC, and hybrid structures. The proposed module uses separate distributed capacitor boards close to each high/low pair, connected with low-profile copper bars; shortening the vertical separation reduces commutation area.
- Pp. 7-10 show that matching quasi-common-source inductance and limiting power/gate mutual coupling matter even with nominal Kelvin connections. A separate driver board does not remove the need to design the two layouts together.
- P. 10 uses individual Kelvin gate/source connections to a stacked driver board. Gate voltage and resistor choices apply to its devices, not EPC2361.
- P. 11 evaluates power-path inductance including mutual terms. Adding conductor widths and self-inductances independently is an inadequate model of a closely coupled structure.

**Use here:** paired local decoupling, explicit gate-return geometry, and extraction of coupled paths. IMS/DBC architecture remains an alternative if FR4 thermal/current results are inadequate, not the default solely because the paper uses it.

### 3. Wattenberg et al.: Multi-kilowatt low-profile GaN inverter

File: `Papers/A_Multi-Kilowatt_Low-Profile_GaN_Inverter_for_Light_Electric_Vehicles_and_High-Power_Tools.pdf`. Abstract, layout/capacitor/cooling pp. 2-4 and results/conclusion pp. 6-7 reviewed.

- P. 3 presents a centrally fed, symmetric butterfly gate layout and comparison of all eight gate-path impedances. Equal geometric appearance is supplemented by electrical analysis.
- Pp. 3-4 distinguish capacitor RMS current, voltage ripple, and DC-bias loss. The implementation reports 580 uF nominal distributed MLCC capacitance with additional bulk-capacitor footprints. Its inverter sizing equations have topology and operating assumptions and should not be applied blindly to a standalone half bridge.
- P. 4: six-layer 70 um-copper board; component-height control leaves the device side available for cooling; source-connected tops require insulating TIM. The reported TIM compression and heatsink arrangement are specific to that assembly.
- P. 6: large temperature gradients can coexist with successful operation in a particular airflow test. Success does not establish equal device current or eliminate worst-device thermal checks.

**Use here:** gate-path impedance comparison, low-profile thermal keep-outs, and a capacitance/current/temperature assessment rather than selection by nominal microfarads alone.

### 4. Brothers and Beechner: Design recommendations from a commercial three-phase GaN module

File: `Papers/GaN_Module_Design_Recommendations_Based_on_the_Analysis_of_a_Commercial_3-Phase_GaN_Module.pdf`. Abstract and parasitic/layout/results discussion pp. 3-8 reviewed.

- Pp. 3-5 describe resonance between local capacitors, external decoupling, and module connections; adding capacitance alone does not remove harmful interconnect inductance.
- P. 6 contrasts lateral unequal paths and cascaded DC connections with distributed, flux-cancelling structures. Shared inductance creates cross-coupling and unequal stress.
- Pp. 7-8 demonstrate a redesigned high-current module, but some measured voltage peaks exceed its stated nominal device voltage rating. Such tests are evidence about parasitic effects, not acceptable operating limits for our module.
- The title/current rating is not a guarantee of hard-switching capability: the analyzed commercial module failed well below the aggregate die current rating in its test setup.

**Use here:** do not rate twelve devices by adding datasheet currents; qualify overshoot, supply-network resonance, and unequal loading explicitly. At 75 V with 100 V devices, voltage headroom is a central design constraint.

### 5. Lu and Chen: Paralleling GaN E-HEMTs in 10 kW-100 kW systems

File: `Papers/Paralleling_GaN_E-HEMTs_in_10kW100kW_systems.pdf`. Parasitic mechanisms pp. 3-6 and conclusion p. 8 reviewed.

- Pp. 3-4 show how quasi-common-source mismatch can perturb VGS despite Kelvin terminals; short, symmetric power and gate loops are required together.
- P. 6 advocates reducing commutation inductance instead of relying entirely on slow switching to suppress overshoot.
- P. 8 validates a four-parallel high-voltage prototype by pulse testing. Scaling language is not validation of a 100 kW continuous converter or our six-parallel low-voltage implementation.

**Use here:** individual local returns, matched branch inductance, and joint power/interface planning. Do not transfer its device-specific gate bias or gate-resistor values.

### 6. Palma, Barba, and Musumeci: Parallel connection experimental investigation

File: `Papers/Parallel_Connection_of_GaN_FETs_an_Experimental_Investigation_Approach.pdf`. Pp. 1-5 reviewed selectively, emphasizing pp. 2-5.

- Pp. 2-4 investigate parameter spread and deliberately unequal timing; a dedicated test board with independent drivers examines transient current redistribution.
- Pp. 4-5 report a four-parallel EPC2032 inverter example at 60 V and 150 A RMS with 720 uF DC-link capacitance; the described operating test is at 20 kHz.
- The paper distinguishes a device's pulse capability from actual parallel-operation currents. The worst branch during a transition can carry much more than total current divided by device count.

**Use here:** bound timing and parameter spread in simulation and validation. Neither the cited 720 uF nor a pulse-current allowance establishes our required capacitance or continuous current capability.

### 7. Musumeci et al.: Low-voltage electric-scooter inverter

File: `Papers/GaN-Based_Low-Voltage_Inverter_for_Electric_Scooter_Drive_System.pdf`. Abstract, pp. 2-3 parasitic discussion, and pp. 5-6 results/conclusion reviewed.

The two-parallel EPC2065 example examines threshold spread and source/drain/gate parasitics. P. 5 calls for symmetric power routes; p. 6 identifies threshold mismatch as a dynamic-sharing contributor. Several equations are corrupted in text extraction and were not used numerically.

**Use here:** static positive-temperature-coefficient sharing does not remove transient mismatch. Thermal headroom and parameter spread must supplement symmetry.

### 8. Rahman et al.: 650 V, 300 A module with integrated drivers

File: `Papers/Design_and_Evaluation_of_a_650_V_300_A_GaN-Based_Power_Module_with_Integrated_Drivers_and_Ultra-Low_Inductance_Layout.pdf`. Abstract, package description p. 2, and selected evaluation text reviewed; limited-depth screening.

The module combines a multilayer substrate, embedded capacitors, and close driver integration; the abstract reports an approximately 5.52 nH design result versus 9.1 nH baseline. Those numbers concern its geometry and extraction method. The title's 300 A module rating is not evidence of continuous operation at that current across all conditions.

**Use here:** integration and vertical spacing influence parasitics. This high-voltage package is less directly applicable than EPC's low-voltage layout guidance.

### 9. Satpathy et al.: Three-level traction-inverter considerations

File: `Papers/Design_Considerations_of_a_GaN-based_Three-Level_Traction_Inverter_for_Electric_Vehicles.pdf`. Abstract and pp. 3-5 reviewed selectively.

This is an 800 V-target ANPC design using 650 V devices; it is not a two-level low-voltage half bridge. Pp. 3-5 discuss stacked power/decoupling/driver boards, heatsink access, and close distributed gate resistors. P. 4 explicitly notes that provision for individual current probing adds power-loop inductance. The abstract distinguishes simulated delivering capability from the lower-power experimental demonstration.

**Use here:** reserve measurement access without adding major commutation-loop detours; assess driver/capacitor/heatsink geometry jointly. Do not reuse its gate bias, clearances, or topology-specific commutation analysis.

### 10. Novo et al.: Development and testing of GaN traction modules

File: `Papers/Development_and_testing_of_GaN_Power_Modules_for_EV_traction_inverters.pdf`. Abstract and selected packaging, thermal, and testing sections pp. 2-6 reviewed; limited-depth screening.

The work concerns VisIC D3GaN, including distinct direct-drive behavior, DBC/cold-plate integration, and module packaging. P. 2 emphasizes local decoupling and control-pin placement. Pp. 4-6 describe package/cooling construction and high-bandwidth isolated measurements.

**Use here:** co-design thermal and electrical interconnects; use appropriate device-referenced measurements. D3GaN driving conventions cannot be transferred to enhancement-mode EPC2361.

### 11. Zou et al.: Systematic efficiency-density co-optimization of a 100 kW inverter

File: `Papers/Systematic_Efficiency-Density_Co-Optimization_of_100_kW_GaN_Traction_Inverter_Methodology_and_Integration.pdf`. Abstract and selected co-design/integration sections, particularly pp. 8 and 10-12, plus conclusion p. 17 reviewed; not an independent audit of the full optimization.

- Pp. 10-11 use copper blocks for DC+/DC-/AC and a short integrated driver output path; the isolation daughterboard is distinct from the close output stage.
- Pp. 11-12 use liquid cooling and a separately designed film-capacitor link. These thermal/capacitor choices are tied to the optimization's losses and switching frequency.
- P. 12 uses stacked DC conductors and reports measured DC-link impedance. Its external-link inductance is distinct from a local semiconductor commutation-loop figure.

**Use here:** choose switching frequency, capacitance, and cooling together. A mechanical daughterboard interface should not force long gate-output paths merely because low-frequency isolation electronics can be farther away.

## Local application-note review

| File in Application Notes | Reviewed coverage | Applicable result and limit |
|---|---|---|
| AN020 Effectively Paralleling Enhancement Mode Gallium Nitride Transistors.pdf | Pp. 3-7 | First-inner-layer return and four distributed loops improve balance relative to one shared loop. Its approximately 0.4 nH/device-pair result and temperature improvement belong to the EPC2001 test hardware. Six repeated cells are our extrapolation. |
| Optimizing PCB Layout with eGaN FETs.pdf | Pp. 3-5 | Return-layer distance and field cancellation strongly affect loop inductance. Thin top-to-return dielectric matters more than simply reducing overall board thickness for the optimized layout. |
| AN031_PCB_Design_Guidelines_to_Maximize_Cooling_of_eGaN_FETs.pdf | Pp. 1-4 and 7 | Wide short copper paths, spreading area, and thermal vias improve cooling. P. 3 discusses fine-pitch limitations and a recommended 2 oz maximum in its context: do not blindly import the photograph's 4 oz stackup. Its PCB-only thermal improvements are not a heatsink rating. |
| Appnote_Thermal_Performance_of_eGaN_FETs.pdf | Pp. 1-4 | Thermal resistance depends on the defined boundary and board. Values for older wafer-level devices are not EPC2361 package thermal values. |
| AN029 Solder Stencil Design Guidelines for Reliable Assembly of PQFN GaN.pdf | Pp. 1-7 selectively | Pad/aperture geometry, paste transfer, and pad-dependent standoff can cause tilt. Relevant package class for EPC2361; use its actual datasheet stencil and assembly-house process, not the example device apertures. |
| Appnote_GaNassembly.pdf | Pp. 1-8 selectively | Correct footprint, solder volume, flatness, clean joints, and inspection matter. Much of this note is expressly LGA/BGA/WLCSP-focused, so it must not override the PQFN EPC2361 drawing. |
| AN023 Accurately Measuring High Speed GaN Transistors.pdf | Pp. 3-6, plus introductory bandwidth discussion | Nearby probe points and short spring-ground connections reduce measurement artifacts; non-ground-referenced fast signals need suitable isolated/differential measurement. |

Other notes were inventoried and their topics triaged. Loss calculation (AN030), device models, SOA, parasitic impact, optimal on-resistance, and dead-time optimization are relevant for the next quantitative pass. Converter examples may inform implementation details but their voltage, topology, and cooling differ. RF small-signal, resonant wireless-power, nanosecond pulse-driver, LLC, PFC, and USB supply notes are lower priority for this hard-switched low-voltage half-bridge plan. No claim is made that every application note has been deeply reviewed.

## Translation into the power-board plan

### Current distribution and terminals

At 220 A RMS sinusoidal phase current, the phase peak is approximately 311 A before ripple/overload. Ideal instantaneous peak current per conducting parallel device is about 51.9 A; this is not each transistor's RMS current or a qualified rating. Actual branch stress depends on PWM, direction, thermal state, and mismatch.

Use high-current bolted/press-fit terminals or busbar interfaces selected by contact resistance, temperature rise, conductor section, and mechanical load. The 32-pin power headers in Cooke's design are not an automatically suitable 220 A connector system. DC+ and DC- should enter as closely coupled conductors where practicable. AC collection should avoid a long narrow copper neck and excessive end-to-end voltage gradients. Compare a central take-off, multiple take-offs, or a longitudinal copper collector through current-density analysis.

### Gate interface and thermal stack

Reserve twelve individually identifiable G/Kelvin-S pairs, six referenced to the switch node and six to DC-. A Kelvin return is a connection near the relevant device source, not a separate package pin unless the datasheet provides one. Keep adjacent connector contacts paired with short local traces. Reserve per-device damping-resistor footprints if consistent with the later driver design, but leave component values undecided.

Top-side headers cannot occupy the same physical volume as a solid top cold plate. Propose connector corridors beside the rows, a shaped heatsink with access openings, or another explicitly drawn mechanical stack. Avoid raising the driver board far above the FETs without checking added gate-loop inductance. EPC2361 top-surface electrical potential and insulation requirements come from the actual datasheet, not the photograph.

Provide supported mounting holes, controlled TIM compression, and a backing/support structure where required. An NTC near each bank or at likely hot positions is useful for protection and trends, but junction-temperature inference needs calibration/modeling. Do not put large ceramic capacitors in high-board-strain clamp/terminal regions; assembly and mechanical compliance must be considered alongside low inductance.

### Capacitors and test facilities

Distribute local MLCCs across all six pair positions, with short broad pad connections and dense return vias into the adjacent plane. Determine the total effective capacitance from switching-frequency/ripple requirements, then check individual RMS current, ESR/ESL, bias loss, tolerances, temperature, and antiresonance with remote bulk capacitors. A mixture of values should be justified by an impedance result rather than assumed to be universally beneficial.

Provide device-local VGS probe pairs, short VDS/SW-reference access, local DC-link voltage pads, NTC connections, and separate terminal-voltage sensing. Position optional snubber footprints near the intended loop, default unpopulated until simulation/measurement establishes need and values. Avoid inserting a series current shunt into the fastest loop by default; individual-current instrumentation can materially change the circuit being characterized.

### Validation needed before a layout is accepted

Check the actual fabricator stackup and footprint rules; calculate DC copper/contact losses and worst-device conduction loss; extract representative near/middle/far branch impedances including mutual coupling; simulate switching with realistic gate-interface parasitics and tolerances; evaluate local/remote capacitor resonance; and solve the mechanical/thermal stack. Validate switching and sharing progressively at controlled operating points with appropriate probes before claiming 220 A RMS capability. These are design follow-up requirements, not completed tests.

At a 75 V bus, 100 V devices leave only 25 V to the continuous drain-voltage limit before any allowance for bus tolerance, regenerative rise, and design margin. No paper's high-current demonstration or transient excursion authorizes operating beyond the EPC2361 limits. Confirm the maximum bus and switching frequency before assigning a numerical allowable loop inductance or final capacitor bank.

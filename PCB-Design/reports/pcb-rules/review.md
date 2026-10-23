# PCB review — SPB Rev B DPT

Date: 23 October 2026  
Design: `hardware/spb-bb-revb-dpt`  
Scope: fabrication readiness, documented requirements, power-loop and gate-loop geometry, and measurement provisions.

**Disposition: suitable as a candidate for a 75 V DPT prototype, subject to fabricator acceptance of the via geometry and assembly-process confirmation. Hold the fabrication order until those conditions are closed.**

The updated layout addresses the principal geometric concerns from the previous review. No PCB, schematic, project, or fabrication files were changed during this review. Independent checks used temporary copies. This Markdown file records the review; it does not implement its recommendations.

## 1. Verification results

Reviewed PCB SHA-256:

```text
A32EB89D13BC16A3F6C0DA3EE90DB01BF29A6BC08179FD7B3B3479E578C392C0
```

| Check | Result |
|---|---|
| Fresh DRC with project and custom rules | Zero violations, zero unconnected pads, zero footprint errors |
| DRC after independently refilling copper zones | Zero violations, zero unconnected pads, zero footprint errors |
| Fresh schematic netlist compared with PCB component-pin connectivity | All 94 connected circuit nets match, excluding intentional PCB-only test pads; net names were not used as the sole matching criterion |
| Independent Gerber generation | All 11 Gerbers match the supplied files after excluding generation timestamps |
| Fabrication ZIP consistency | All 15 entries match their release-folder counterparts |
| Turn-on resistors | R7, R9, R26 and R28 are 1.5 Ω |
| PCB hash at completion | Unchanged |

The DRC result applies to the enabled checks. Library-footprint checks remain ignored; this is not an independent dimensional certification of custom footprints. The netlist comparison is not a full schematic ERC. Drill files were checked for ZIP consistency, not independently regenerated in this review.

## 2. Findings and recommended actions

### F1. Obtain manufacturing acceptance for the annular rings

**Priority: before ordering.**

The saved PCB contains:

| Via count | Pad diameter | Drill diameter | Nominal radial annular ring |
|---:|---:|---:|---:|
| 1,050 | 0.60 mm | 0.30 mm | 0.15 mm |
| 44 | 0.45 mm | 0.25 mm | 0.10 mm |

The project permits these dimensions, so a clean DRC does not establish acceptance by JLCPCB for the selected 2 oz process. The ordering document already identifies this as unresolved. JLC's published capability information also distinguishes manufacturing conditions; its general PTH guidance should not automatically be treated as a definitive rule for these filled vias.

**Recommended solution:** obtain written engineering acceptance covering both via sizes, 2 oz copper, finished-hole interpretation, and the filled/capped process. If the supplier rejects them, revise the layout to its approved dimensions and repeat clearance, plane-return and fabrication checks. Do not enlarge every via automatically: larger antipads can disrupt the power and gate return paths.

Source: [JLCPCB manufacturing capabilities](https://jlcpcb.com/capabilities/pcb-capabilities/).

### F2. Gate-voltage margin needs validation

**Priority: before full-power DPT.**

The project's documented simulation reaches approximately **−3.4 V VGS**, leaving **0.6 V** to the EPC2361's **−4 V** absolute limit. The nominal positive drive is **+5.1 V**, against a **+6 V** limit. These are margins to absolute limits, not validated operating margins.

The simulation values are taken from the existing project documentation; SPICE was not rerun in this review. Actual supply variation, Zener tolerance, temperature, ringing and probe loading can change the extrema.

**Recommended solution:** check the bias network across tolerances and temperature, then measure positive and negative gate extrema at the local spring pads during staged bring-up. Check both the driven device and the held-off device. Treat the specified 7 V isolated supply as a nominal setting, not proof of safe VGS. If margin is inadequate, reassess bias and damping together rather than increasing negative bias alone.

Source: [EPC2361 manufacturer datasheet](https://epc-co.com/epc/Portals/0/epc/documents/datasheets/EPC2361_datasheet.pdf).

### F3. Confirm the custom-footprint assembly process

**Priority: before assembly approval.**

The EPC2361 footprint uses graphical mask and paste apertures. This construction is intentional, but a DRC pass cannot validate stencil thickness, paste transfer, soldering process or placement orientation.

**Recommended solution:** have the assembler confirm the supplied stencil geometry against the EPC land/stencil recommendations, the stencil thickness, component orientation and filled/capped via-in-pad treatment. Review the custom driver, MMCX and shunt interfaces as part of the same assembly approval. Keep the laboratory-installed shunts and DNP measurement links excluded from automated assembly as specified.

### F4. Verify timing between the two drivers

**Priority: before switching qualification.**

Two drivers operate the four parallel cells. Matched PCB routing does not remove component propagation-delay differences or external PWM skew. An apparently symmetric layout can still exhibit unequal dynamic current sharing.

**Recommended solution:** use the specified common PWM source and equal-length control cables, then measure U1-to-U2 timing and individual shunt currents. Check turn-on and turn-off separately. Cable matching is useful but is not sufficient evidence of equal switching timing.

### F5. Align the solder-mask manufacturing requirement

**Priority: before ordering.**

The fabrication notes specify a **0.10 mm minimum mask web**, while the JLC ordering instructions discuss **0.20 mm**. This is a documentation inconsistency, not a demonstrated mask defect.

**Recommended solution:** agree on one supplier-approved requirement and verify the final CAM mask interpretation against it. Ensure any CAM changes retain the intended exposed pads and via covering.

## 3. Power-loop review

### Improvements verified

The previous local shunt-return discrepancy is resolved. In the same inspection window used previously—`abs(x - shunt_x) < 7.1 mm` and `112 < y < 117 mm`—all four shunt regions now contain **37 DC− vias**, instead of 37/41/37/41.

The local bypass placement, compact HS/LS arrangement, broad power copper and stitched return structure remain sensible. The connectivity and DRC checks found no new short or unconnected circuit pad in this structure.

### Remaining considerations

Equal via counts do not prove equal impedance. Current paths depend on copper shape, antipads, capacitor connections, shunts and terminal geometry. The confirmed local count is not the total effective current-carrying via count.

**Recommendation:** retain the present power layout for the first prototype if manufacturing acceptance is obtained, and validate per-cell current sharing and VDS overshoot during staged DPT. Preserve the specified stack-up and avoid unreviewed CAM changes to the via fields or return planes. No numerical power-loop inductance or current-density qualification is claimed here.

## 4. Gate-loop review

### Improvements verified

The gate resistors are closer to the device gates. The four block-1 post-resistor gate nets each contain **1.548 mm of top-layer track**. This is a geometric check of those branches, not the full electrical loop length.

The shared gate routes now use adjacent-layer Kelvin returns. This addresses the earlier separation between outgoing gate and return routing. Preserve the specified approximately **0.10 mm outer dielectric spacing**, because the benefit of that pairing depends on the manufactured stack-up.

### Remaining measurement branches

Gate-sense branches still attach copper to the gates even when the remote sense links are unpopulated. Their bottom-layer track lengths differ; the DNP links disconnect the remote connector section but do not remove the gate-side stubs.

**Recommendation:** keep the U.FL sense links DNP by default and use the local spring pads for initial gate measurements, as the current measurement plan specifies. Use probes with suitable loading and common-mode performance. Do not reopen the main gate layout solely to equalize unused measurement stubs without evidence that they materially affect the waveform.

The updated gate layout is a meaningful improvement. Its switching performance still requires measured VGS extrema, held-off gate behaviour and driver-to-driver timing.

## 5. Requirements and release status

| Requirement | Review status |
|---|---|
| Single-level 75 V DPT prototype | Reasonable candidate, subject to the conditions above |
| Clean enabled DRC and circuit connectivity | Verified |
| Fabrication Gerbers correspond to saved board | Verified |
| Local power-return symmetry concern | Previous local discrepancy resolved |
| Shorter gate branches and paired Kelvin return | Improved and checked in the saved routing |
| Controlled stack-up and via-in-pad treatment | Documented; supplier acceptance still required |
| Suitable measurement connections | Retain rated isolated probing and local spring-pad strategy; do not connect different source references through grounded instruments |
| Full-current switching performance | Requires staged hardware validation |
| 1200 V stack operation | Not qualified by this review; PCB spacing does not establish the complete isolation architecture |

## 6. Release recommendation

Keep the present layout as the candidate for the first prototype. Before placing the order, close the via-process acceptance, mask requirement and custom-footprint assembly review. During bring-up, prioritize gate-voltage margin, U1-to-U2 timing, per-cell current sharing and VDS overshoot.

This was a read-only geometric and consistency review. It did not rerun Q3D or SPICE, certify insulation compliance, or establish thermal/current capability for continuous operation. Existing simulation results are supporting project information, not independently reproduced results of this review.

## 7. Local documents considered

- [Previous fabrication review and subsequent design dispositions](PCB_review_for_fabrication_2026-10-19.md)
- [PCB rules and checklist](PCB_rules_and_checklist.md)
- [DPT measurement setup](DPT_measurement_setup.md)
- [DPT JLC ordering requirements](DPT_JLC_order.md)
- Current PCB, schematic, project rules, fabrication notes, BOM, Gerbers and fabrication ZIP under `hardware/spb-bb-revb-dpt`.

Temporary review evidence was generated under `C:/Users/enesa/AppData/Local/Temp/spb-review-20261023`.

## 8. Disposition (2026-10-23)

| Finding | Action | Status |
|---|---|---|
| F1 annular rings | JLC's capability page states separate rules. Vias: diameter ≥ hole + 0.10 mm (0.15 mm preferred), multilayer minimum 0.15 / 0.25 mm: the 0.60 / 0.30 and 0.45 / 0.25 mm vias meet it, and epoxy filled & capped via-in-pad is listed for 0.15–0.55 mm vias. Plated component holes: 0.254 mm ring at 2 oz: the AC-bolt stitching holes (0.40 / 0.80 mm, ring 0.20 mm) were enlarged to 0.40 / 0.92 mm (0.26 mm); a custom DRC rule now enforces 0.254 mm on every plated pad (checked to trigger on the old size). No via was enlarged. | Board changed; written CAM confirmation still requested through "confirm production file" |
| F2 gate-voltage margin | Tolerance table added to `DPT_measurement_setup.md`: with the BZX384-C5V1 range (4.8–5.4 V) and V_ISO 7.0 ± 0.1 V the static off level spans −1.5 to −2.3 V and the simulated ringing can reach −3.85 V. Bring-up procedure: set V_ISO per measured off level (−1.7 to −1.9 V), staged current, add damping rather than bias if the minimum comes within 0.3 V of −4 V. | Procedure documented; to be measured |
| F3 custom-footprint assembly | Assembler confirmation listed in `DPT_JLC_order.md` (EPC2361 stencil and thickness, filled/capped via-in-pad, orientation of LGA, MMCX, U.FL, REDCUBE); shunts and DNP links excluded from the JLC BOM / CPL | At ordering |
| F4 driver timing | One PWM source, equal cables, U1-to-U2 timing and per-cell shunt currents at turn-on and turn-off in the bring-up list | At bring-up |
| F5 mask requirement | One requirement: 0.20 mm minimum web (JLC 2 oz). Project rule changed from 0.10 to 0.20 mm (DRC clean); fab notes, JLC checklist and rules aligned. EPC2361 webs between different nets measured at 0.28 mm minimum. | Closed |

Gate-sense stubs (section 4): kept as recommended (U.FL links DNP, spring pads primary). Power layout (section 3): unchanged.

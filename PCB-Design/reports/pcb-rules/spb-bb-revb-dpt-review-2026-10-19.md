# SPB Rev B DPT PCB: read-only review and proposed solutions

Review date: 19 October 2026.

Design reviewed: `hardware/spb-bb-revb-dpt/spb-bb-revb-dpt.kicad_pcb`, its project settings, custom rules, schematic, BOM and supporting documents.

**No PCB, schematic, project-setting or fabrication files were changed.** Solutions below are proposals, not implemented changes. At the end of the review, hashes confirmed that all 62 original files in the target PCB folder remained unchanged.

## Summary

The board is a four-cell GaN half bridge for double-pulse testing, with four EPC2361 devices per switch, two 2EDF7275K drivers and individual low-side current shunts. Its intended local DC bus is 75 V; this must be distinguished from the possible common-mode voltage of a level in a 1200 V stack.

| Finding | Classification | Recommended disposition |
|---|---|---|
| Direct VDS U.FL ports exceed the manufacturer's stated connector voltage rating | Confirmed component-rating conflict | Resolve before operating these ports at the intended bus voltage |
| 36 small vias violate the current project limits, producing 72 DRC errors | Confirmed rule/layout mismatch | Agree manufacturing limits and make the saved rules and layout consistent |
| Several manufacturing safeguards are absent or disabled | Confirmed rule-coverage gaps | Establish explicit fabricator-approved constraints |
| Rules labelled 1200 V do not establish a complete 1200 V isolation barrier | Conditional system limitation and verification gap | Define controller reference and required insulation before stack use |
| Probe shields connect to different electrical references | Confirmed topology; risk depends on instruments and connections | Define and validate the complete measurement arrangement |
| Slides, older plots and mechanical BOM contain revision mismatches | Confirmed documentation inconsistencies | Regenerate and reconcile documentation from one frozen revision |

Positive results: fresh DRC reported **zero unconnected pads**, and an independent comparison of the actual routed PCB with the exported schematic found **no connectivity mismatches across the 94 connected PCB nets**. Seven custom spacing rules are present; all connected net names appear in their domain lists. These results do not establish switching performance, insulation compliance or thermal capability.

## 1. Direct VDS U.FL connectors are underrated

### Evidence and consequence

J8, J11, J17 and J20 have their centre contacts connected directly to `SW`, and their shields connected to `LSRC1` through `LSRC4`, respectively. They therefore see approximately the local drain-source voltage: up to the intended 75 V bus plus switching overshoot.

The BOM identifies `Hirose U.FL-R-SMT-1(01)` and includes the note "100 V listed, confirm". Hirose's manufacturer support page states a **30 V rated voltage** for U.FL-R-SMT-1. A test voltage used for insulation-resistance measurement or dielectric withstand must not be treated as a continuous operating-voltage rating.

Source: [Hirose: rated voltage of U.FL-R-SMT-1(01)](https://support.hirose.com/en/support/solutions/articles/68000029733-what-is-the-rated-voltage-of-u-fl-r-smt-1-01-).

### Proposed solution

Choose one measurement approach and qualify the entire path:

1. Replace the direct VDS interface with a connector and cable assembly explicitly rated for the maximum operating voltage, expected overshoot and intended environment. Preserve a short local drain/source pickup and verify its added inductance and capacitance.
2. Use a suitable differential or isolated probe with a manufacturer-approved local solder-in or probe-tip interface, rather than carrying full VDS through this U.FL interface.
3. If an attenuated coaxial interface is necessary, design and validate a compensated wideband divider at the pickup. Check resistor voltage/pulse ratings, parasitic capacitance, bandwidth, loading and termination. Do not simply restore the older divider without re-evaluating the coupling problems described in the project notes.

Changing the oscilloscope input to 1 Mohm does **not** fix an underrated connector. Leaving an underrated connector fitted but unplugged also leaves the voltage across its contacts.

### Concrete option: PCB-mounted MMCX socket and compatible isolated probe

A PCB MMCX socket is a small coaxial receptacle soldered onto the board. A matching probe-tip cable snaps into it, providing a secure, repeatable connection without a handheld tip or long ground lead. MMCX is a snap connection; if a threaded lock is required, investigate a suitably rated SMA interface supported by the selected probe system.

For each low-side VDS measurement, connect:

- **Centre contact:** the local FET drain (`SW`).
- **Outer contacts:** that FET's local source (`LSRC1`, `LSRC2`, `LSRC3` or `LSRC4`), on the device side of its shunt.

The outer contacts are the measurement return, **not an instruction to connect the source to earth**. Place the socket close to the device, with short, adjacent drain/source pickup paths and a minimal loop area. Keep the pickup out of the main power-current path and check probe access and mechanical clearance.

The intended measurement chain is:

```text
Local drain/source pickup
    -> voltage-rated PCB MMCX socket
    -> compatible attenuating sensor-tip cable
    -> isolated voltage-probe head
    -> supported oscilloscope
```

**Example probe accessory:** Tektronix **TIVPMX50X**, an MMCX sensor-tip cable for the **TIVP-series IsoVu** isolated measurement system. The cited datasheet lists 50x attenuation, a +/-250 V differential input range and approximately 2.3 pF input capacitance. Apply the manufacturer's frequency-dependent voltage limits and operating conditions. This is an example of the architecture, not a selected or approved component for this board.

Source: [Tektronix TIVP-series datasheet and sensor-tip cable specifications](https://download.tek.com/datasheet/TIVP-Datasheet-51W616552.pdf).

The TIVPMX50X requires the compatible IsoVu probe system and supported oscilloscope; it cannot be plugged directly into an ordinary oscilloscope input. Select the PCB socket only after confirming the probe accessory's mating requirements. **No exact PCB socket part number has been selected:** its connector, footprint clearance and mating assembly must be rated for the maximum VDS, including overshoot. An MMCX connector alone supplies neither attenuation nor isolation, and changing connector family alone does not guarantee less noise.

For comparison, the Tektronix **206-0663-xx** MMCX tip for the TPP1000 illustrates the same mechanical connection concept but is **not suitable for direct 75 V VDS**: its published accessory limits include 60 V DC and 42 V peak. Do not infer accessory suitability from the main probe's higher voltage rating.

Source: [Tektronix passive-probe accessory specifications](https://download.tek.com/datasheet/TPP1000-500-Passive-Probes-Datasheet-51W-26151-11.pdf).

Before implementing this option, confirm the available oscilloscope and probe models, select the complete rated interface, and verify loading, bandwidth and deskew. A plain MMCX-to-BNC cable to a grounded oscilloscope is not equivalent to the isolated-probe arrangement above.

### Verification required

- Obtain the exact connector and mating cable specifications, including working voltage.
- Check rating against the maximum credible VDS, not just the nominal bus voltage.
- Verify attenuation, bandwidth, step response and voltage/current channel deskew with the actual measurement chain.
- Update the BOM, schematic, port labels and test instructions together.

## 2. Fresh DRC disagrees with the saved clean report

### Evidence and consequence

The saved `drc_report.txt`, dated 17 October 2026, reports zero violations. A new KiCad 7 DRC run on a temporary copy of the current design found:

| Check | Current project minimum | Actual small vias | Count |
|---|---:|---:|---:|
| Through-hole drill | 0.30 mm | 0.25 mm | 36 errors |
| Via diameter | 0.50 mm | 0.45 mm | 36 errors |
| Total | | 36 affected vias | **72 errors** |

For example, the `GH_L1` via at absolute board coordinates **(120.8500 mm, 106.1300 mm)** produces both errors. The affected vias include gate, Kelvin-return and driver-supply nets. Their nominal annular ring is `(0.45 - 0.25) / 2 = 0.10 mm`, at the current minimum.

This establishes a mismatch between the board and its saved rules. It does not establish that 0.25/0.45 mm vias are inherently unmanufacturable. The reason the older report was clean was not conclusively established; it must not be used as evidence that the present saved project passes.

### Proposed solution

First obtain the fabricator's approved finished-drill, annular-ring, plating and registration requirements for the intended stack-up and copper weight. Then choose one of these approaches:

- If 0.25 mm drill / 0.45 mm diameter vias are approved, persist those limits in the project, or define narrowly scoped custom exceptions for the intended small vias. Keep stricter requirements elsewhere where appropriate.
- If they are not approved, enlarge the affected vias or redesign the affected connections to meet the approved process. Recheck clearance, gate-loop geometry and symmetry after enlargement.

Do not suppress the error severities to obtain a clean report. Ensure the generator, saved project settings and future editing session use the same limits.

### Verification required

Close and reopen the project, refill zones and rerun DRC with the custom rule file active. Confirm zero unresolved via errors and zero unconnected pads. Regenerate fabrication outputs if geometry changes. Retain the new report with the exact released revision.

## 3. Manufacturing constraints and checks need stronger coverage

### Evidence and consequence

The current project contains:

- `min_track_width = 0.0` and `min_connection = 0.0`.
- `min_clearance = 0.0`; the Default netclass still provides 0.20 mm clearance, and custom domain rules provide additional spacing. Thus clearance checking is not entirely absent.
- No positive minimum solder-mask web in the loaded settings.
- Ignored footprint-library issue/mismatch and missing-courtyard checks, among other ignored checks.

The inspected routed track segments are at least **0.20 mm** wide. The concern is that the rules do not adequately prevent later narrow tracks or copper necks. Track width alone also does not prove the current capacity of the high-current pours and their via transitions.

### Proposed solution

- Set a nonzero absolute manufacturing minimum track width, approved for 2 oz copper. Keep any special fine-pitch exceptions local and explicit.
- Set a meaningful minimum copper connection width to catch narrow necks. Derive power-path widths and via counts separately from current, copper thickness, temperature rise and pulse duty cycle.
- Establish a nonzero global clearance floor with explicitly justified footprint exceptions. Preserve the stronger domain rules.
- Set a fabricator-approved solder-mask web requirement and inspect the generated mask layers, particularly around the EPC2361 land patterns and via-in-pad areas.
- Review ignored checks individually. Enable useful checks and document intentional exceptions. For deliberately modified custom footprints, compare against a controlled project library rather than treating every library mismatch as an error to fix blindly.
- Define useful netclasses or equivalent custom constraints for control, gate-drive and power connections. A single Default netclass is not itself an error, but it provides limited protection against inappropriate future routing.

### Verification required

Run DRC using the agreed production constraints and inspect every new result. Obtain fabricator DFM feedback for the actual Gerbers, drill files, mask and via-in-pad process. Do not lower constraints solely to make DRC pass.

## 4. A rule named "1200 V barrier" is not a complete insulation design

### Evidence and consequence

The custom rules specify 4.0 mm control-to-power spacing on outer layers and 3.0 mm on inner layers. A later rule relaxes control-to-power spacing to 3.0 mm inside the U1/U2 courtyards.

U1/U2 are 2EDF7275K devices. Infineon specifies **functional isolation**, a **460 V RMS maximum isolation working voltage**, and approximately **3.4 mm package creepage and clearance**. Functional isolation must not be treated as basic or reinforced safety insulation.

Source: [Infineon 2EDF7275K datasheet, functional-isolation specifications](https://www.infineon.com/assets/row/public/documents/24/49/infineon-2edf7275k-datasheet-en.pdf).

The project checklist also states that the in-plane offset between opposite-domain copper across adjacent dielectric layers is achieved by construction and is **not checked by DRC**. Ordinary same-layer clearance checks do not establish dielectric insulation or surface creepage compliance. No insulation-compliance conclusion was made in this review.

### Proposed solution

Define the operating configuration first:

- **Single-level bench DPT:** document the controller, supply, instrument and earth references and the resulting maximum voltage across each barrier. Assess the board for those actual voltages.
- **Stack with control local to each level:** provide and qualify the required system isolation at the control/power interfaces, such as an appropriate isolated supply and optical control link. Include instruments and external cables in the insulation assessment.
- **Stack with one earth-referenced controller:** select an isolation architecture and components rated for the maximum level-to-controller working voltage and transients, with the required insulation classification. Wider PCB spacing alone cannot upgrade U1/U2.

Determine creepage, clearance and solid-insulation requirements from the applicable standard, working and impulse voltages, pollution degree, material group, altitude and coating qualification. Treat the current 4/3 mm values as design settings requiring justification, not proof of compliance. Narrow package exceptions to the intended objects where practical, rather than broadly permitting other copper inside a courtyard.

### Verification required

Inspect all copper layers, through-via barrels, mounting hardware, connectors and external assemblies. Check projected control/power overlap across dielectric layers and confirm the actual manufactured stack-up. Keep a separate insulation review for full-stack operation.

## 5. Measurement grounding can change or short the circuit

### Evidence and consequence

- High-side VGS U.FL shields connect to `KH1`/`KH2`, in the switching-node domain.
- Low-side VGS shields connect to `KL1`/`KL2`.
- VDS shields connect to individual `LSRC` nets on the device side of the current shunts.

Connecting those shields through an ordinary oscilloscope with shared channel grounds can join circuit nodes that must remain separate. Depending on the connections, this can short switching-node copper to another reference, connect individual source nodes together, or provide a parallel path around a shunt and corrupt its measurement.

The board already says **"VDS U.FL = 75 V: 1 MOHM SCOPE INPUT ONLY"**. This is useful loading guidance, but input impedance does not establish ground isolation. A 50 ohm termination directly across 75 V would dissipate approximately `75^2 / 50 = 112.5 W`.

### Proposed solution

- Prepare a connection diagram showing every probe tip, shield, termination and instrument-earth connection.
- Use suitably rated differential/isolated measurement equipment where references differ, including the high-side gate measurement.
- Check both differential and common-mode voltage ratings, bandwidth, CMRR at switching frequencies and probe capacitance.
- Preserve each shunt's intended current path; do not join source-side shields through common-ground channels.
- Specify attenuation, maximum input voltage and termination for each port. A 1 Mohm setting alone does not establish that a scope input can accept the voltage.
- Do not defeat protective earth to float a conventional oscilloscope.

### Verification required

With the DUT unpowered, check continuity between instrument shields and earth and compare it with the connection diagram. Validate waveform accuracy and deskew at reduced energy before using measurements for switching-loss calculations. Resolve the U.FL rating issue in Section 1 independently.

## 6. Documentation does not consistently describe the current PCB

### Evidence and consequence

- `reports/slides/spb_revb_design_flow.pptx`, slide 36, describes an older divided VDS interface into 50 ohms. The current board exposes direct VDS and specifies a 1 Mohm input.
- Older plots show the previous control-header arrangement; the current PCB has 2 x 5 headers.
- The mechanical BOM identifies the AC bolt as J22, while the current PCB identifies it as J21.
- The saved clean DRC report does not reproduce with the current project limits.

These mismatches can cause incorrect assembly or probing even where PCB connectivity is correct. The older plot discrepancy does not by itself prove that the newer fabrication Gerbers are stale; a full independent Gerber-to-board equivalence check was not performed.

### Proposed solution

Freeze one design revision, then regenerate the schematic/assembly plots, BOM, placement files, fabrication files and DRC report from that revision. Update the slides' measurement interface, header pinouts and connector references. Mark superseded plots clearly or move them into a revision-specific archive. Include the revision identifier and generation date in the release manifest.

### Verification required

Cross-check connector references and pinouts among PCB, schematic, assembly drawing, BOM and test instructions. Independently inspect the final Gerbers and drills. Confirm the exact files being ordered match the approved revision.

## Remaining power-electronics validation

The local application notes emphasize short commutation loops, separate Kelvin gate returns, controlled gate-loop inductance and local decoupling. The existing design uses these concepts, but the following remain validation tasks rather than confirmed layout errors:

- Extract or measure the routed gate-loop inductance; the project's checklist identifies the approximately 1.7 nH value as an assumption requiring extraction.
- Reconfirm commutation-loop and inter-pair inductance after the isolation-related copper changes. The checklist explicitly calls for redoing affected Q3D models; older numbers must not automatically be assigned to the current copper.
- Verify inter-driver delay mismatch and dynamic current sharing with a measurement arrangement that does not bypass the shunts.
- Confirm peak VDS and VGS, reverse-conduction behaviour and overshoot using the actual supplies, gate resistances and probe loading.
- Check power-pour bottlenecks, via current sharing and DPT pulse-energy/temperature limits. A connectivity pass does not establish these capacities.
- Quantify switch-node coupling and validate EMI filtering and signal return paths. This review did not establish EMC compliance.

Relevant local references include `Application Notes/PCB-Design.pdf`, `Application Notes/Optimizing PCB Layout with eGaN FETs.pdf`, `Application Notes/eGaN FET Drivers and Layout Considerations.pdf`, and `Application Notes/PAC55XX_PCB_Design_Layout_Guide.pdf`. The project-specific rationale and outstanding tasks are in `reports/pcb-rules/PCB_rules_and_checklist.md`.

## Suggested order of work

1. Resolve the direct VDS connector rating and define the complete probe/grounding arrangement.
2. Reconcile the via geometry with fabricator-approved saved project constraints and reproduce DRC after reopening.
3. Add the missing manufacturing safeguards and review the resulting findings.
4. Confirm the insulation architecture for the intended bench or stack configuration.
5. Revalidate affected parasitic models and switching limits.
6. Regenerate and reconcile the release documentation and fabrication package.

## Review limits and retained evidence

Checks performed: current PCB/project/custom-rule inspection, schematic netlist export and comparison against actual PCB pads, fresh KiCad 7 DRC on a temporary copy, current top-layer render inspection, selected local guideline and slide review, and manufacturer verification of connector and driver ratings.

The DRC result applies to the saved zone fills and current enabled checks. This was not a complete schematic ERC, independent zone-refill qualification, full Gerber comparison, mechanical collision study, current/thermal simulation, switching simulation or insulation certification.

The fresh DRC report was retained during the review at `C:/Users/enesa/AppData/Local/Temp/spb-readonly-review-20261019/fresh-drc.txt`. Temporary evidence can be removed by the operating system; the counts and representative affected geometry are recorded above for that reason.

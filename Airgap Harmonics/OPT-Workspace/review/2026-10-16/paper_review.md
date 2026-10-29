# Technical review and proposed revisions — 16 October 2026

Status: review only. No manuscript, figure, original simulation, or FEA data changed. Separate LTspice netlists and results accompany this document. Proposed wording below requires author approval.

## 1. Confirmed motor design and device interpretation

The generated design values specify Ns = 1 and Np = 6 per PV group. The design uses a high-voltage vertical multi-junction (VMJ) device, not a conventional single silicon junction. Six devices in parallel supply nominally 29 V and 0.78 A, or 22.6 W per channel. Two field coils in the channel have a combined resistance of 37.2 ohm and an estimated inductance of 7.63 H, giving L/R = 205 ms. Each coil has 550 turns, giving 429 A-turn per pole at 0.78 A.

Thus the selected device voltage is sufficient for the nominal steady-state winding design. Parallel connection adds current and power without multiplying voltage. This conclusion does not establish cold/hot voltage margin or any particular fast pole-change requirement.

The manufacturer reports 29 V and 3.3 A for its complete 5S1010.4-A555555 array at 10 W/cm2. The repository divides array current by 25 to infer a device current near 0.13 A. This is consistent with the high-voltage device concept, but the datasheet does not explicitly provide the individual-device equivalent-circuit parameters or certify the assumed reverse-voltage rating. Confirm array wiring or obtain individual-device data before calling all scaled parameters manufacturer-specified.

Source: https://www.mhgopower.com/downloads/Cell-Array_Datasheet_Rev_2.5_12-22-2021.pdf
The datasheet conditions include 975 nm illumination and water cooling; it also warns of temperature-dependent performance. The present electrical simulations use constant temperature. The paper's carrier thermal estimates do not establish that the quoted electrical performance is retained at the predicted carrier temperature.

## 2. Claim-to-evidence audit

| Claim | Evidence and assessment | Proposed action |
|---|---|---|
| Stationary illumination reverses field current without rotor active switches | Circuit principle and new motor-matched LTspice runs support this within the stated models. | Retain; describe two antiparallel groups and their internal series/parallel arrangement consistently. |
| The chosen PV voltage is sufficient | 29 V, 0.78 A, 37.2 ohm; new operating point 29.12 V, 0.783 A. | Retain nominal design claim. State Ns=1, Np=6 explicitly. |
| Shaded cells require bypass to preserve series-string current | Relevant to a general Ns>1 arrangement, not the selected Ns=1 example. | Separate general series-string protection from the motor's parallel-device shading behavior. |
| Diode–Zener branches govern commutation | Conditional on clamp voltage and PV forward conduction. New sweep shows substantial conduction at approximately 35.5/37 V but none at approximately 40 V. | Avoid claiming the external branches always carry commutation current. |
| Existing Fig. 5 quantitatively represents the protected motor circuit | It explicitly excludes external protection; old LTspice draft also has Ns=8 and tau=50 ms. | Replace its data with a motor-matched run after choosing the illustrative clamp. Retain Fig. 3 as a clearly labelled reference characteristic. |
| Co-design equations include arbitrary series/parallel combinations | Physical derivation is useful, but the notation starts with per-device MPP current and later treats it as group current. Np is absent. | Add Np explicitly throughout MPP matching, MMF, conductor sizing and optical-power relations. |
| FEA supports rated high-speed power | Existing machine maps and comparison support a numerical operating-envelope claim; no new FEA was run in this review. | Retain with model assumptions. Do not imply a simulated loaded pole-change transition. |
| Pole changing improves performance over a separate four-pole winding | Existing comparison shows lower low-speed current, but no top-speed current advantage; separate winding also reaches rated power. | Keep the fair comparison and qualify the particular benefit. A higher overload torque capability is not established merely by current headroom. |
| Torque-ripple improvement is quantitatively established | Manuscript reports mesh agreement within 1% for mean torque but six percentage points for ripple, for the 0.7 mm model. | Report ripple with appropriate precision. Extend mesh/angular-resolution checks to the baseline before strong quantitative claims. |
| Approximately 90% efficiency includes excitation | Source code includes electrical light-source input with 50% source efficiency; field copper is included within this input. | Define the system boundary. Optical coupling, inverter loss and cooling auxiliary power are not independently accounted for in the inspected expression. Do not double-count field copper. |
| Thermal feasibility is demonstrated | Analytical heat rejection is compared with estimated heat generation; temperature feedback into the PV model is absent. | Present as thermal sizing, not a verified operating temperature or hardware capability. |
| Air-gap enlargement improves performance | The stronger 0.7 mm case also changes MMF, winding turns and PV count. | Explain that its results combine a larger gap with redesigned excitation; retain the unchanged-excitation column to isolate the penalty. |
| Novelty relative to the closest publications is established | The introduction names the relevant approaches, but a full comparison requires reading the referenced papers. | Audit the specific novelty claims against the supplied reference PDFs before strengthening priority claims. No new literature priority claim is made here. |

## 3. Separate LTspice simulations

Each bipolar group contains six individually modelled parallel VMJ devices, with the two groups antiparallel at their terminals. Each device has its own generic series-opposed diode–Zener branch. Rf=37.2 ohm and Lf=7.63 H. Initial conditions come from the illuminated dc operating point. Switching occurs at 0.5 s with a 10 microsecond illumination transition; simulation ends at 2 s. The reversal-fine run halves maximum time step from 100 to 50 microseconds.

Parameters follow the repository's existing array fit scaled to one device: photocurrent 0.136 A, series resistance 16.75 ohm, shunt resistance 50 kohm, Voc 35.8 V and modified thermal voltage 1.3 V. The 150 V breakdown parameter is assumed, not a manufacturer rating. Generic diode models have no thermal or tolerance spread. All six branches are identical, so equal sharing is imposed by symmetry rather than demonstrated for real parts. This is a circuit-model check, not component qualification.

| Test | Result |
|---|---|
| Nominal protected operation | 29.12 V, 0.783 A; approximately 22.8 W field power |
| Reversal, approximately 35.5 V clamp | Zero crossing 123 ms; reaches -95% of initial current in 537 ms; peak absolute winding voltage 35.55 V |
| Same reversal without external branches | Zero crossing 119 ms; reaches -95% in 532 ms; peak absolute winding voltage 38.85 V |
| Protected de-excitation, both sources off | Current reaches 5% in 117 ms |
| One of six active parallel devices fully shaded | Final field current 0.673 A; terminal voltage 25.03 V; approximately 14% current reduction; shaded-device absorption approximately 13 mW under the assumed model |
| Reversal, approximately 37 V clamp | Peak voltage 36.98 V; zero crossing 120 ms; reaches -95% in 533 ms |
| Reversal, approximately 40 V clamp | PV junctions conduct first; external branch current negligible; peak voltage 38.85 V |
| Time-step check | Halving the maximum step leaves the reported three-significant-digit reversal results unchanged |

For the approximately 35.5 V case, one ideal identical protection branch reaches 4.94 W peak during reversal; the six branches in the initially illuminated group dissipate approximately 1.86 J over the simulated post-switch interval. These are combined diode–Zener branch values. They do not select a physical part or establish pulse ratings.

The approximately 35.5 V clamp inherited from the earlier draft is below the fitted open-circuit voltage of 35.8 V. It is nonconducting at the nominal matched operating point, but it is not a demonstrated no-conduction choice across the complete operating range. The approximately 37 V case illustrates a higher threshold, without allowing for device tolerances or temperature. Selecting a real clamp requires the normal maximum voltage, PV reverse rating, junction conduction characteristic and component tolerances.

Small differences in reversal time between these clamp choices are not the principal contribution. The meaningful change is voltage limitation and allocation of commutation energy between the external branch and the PV junctions.

The shading test concerns an entire external VMJ device. It does not resolve nonuniform illumination across the internal junctions of a VMJ device, nor does it demonstrate series-string shading protection for Ns>1. The LS3 channel was not simulated in this review.

## 4. Proposed mathematical corrections — not applied

Define Vmpp,c and Impp,c for one VMJ device, with Ns devices in series per branch and Np parallel branches in each group. For identical devices under uniform illumination:

- Vf = Ns Vmpp,c
- If = Np Impp,c
- Pf = Ns Np Pmpp,c
- Rf = Ns Vmpp,c / (Np Impp,c)
- Ac = Np Impp,c / Jf
- Nf = sigma Vf / (nc Jf lt)
- Ff = sigma Ns Np Pmpp,c / (nc Jf lt)
- Popt = Ns Np Pmpp,c / etaPV
- Agroup = Ns Np Acell, with the optical aperture/packing assumption stated when using Popt/Ee instead.

For equal sharing and inactive external branches, the junction-only commutation voltage becomes vf = -Ns Vd(if/Np). The existing expression for estimated decay time retains its form when Vd is evaluated at the per-device initial current. Clarify that turn independence of the stated time constant holds under the assumed fixed geometry, MMF and current density; excitation voltage and clamp behavior still determine the normalized transient.

## 5. Proposed text — not applied

### Introduction contribution sentence

This paper connects two rotor-mounted PV groups in antiparallel and selects the field-current direction through stationary-side illumination. Each group contains series- and parallel-connected PV devices selected to match the field winding, with passive diode–Zener branches providing voltage-dependent protection paths.

### Section II.A architecture clarification

The two bipolar PV groups are connected in antiparallel at terminals A and B. Each group contains Np parallel branches of Ns series-connected PV devices. Stationary sources LS1 and LS2 select the direction of current in the reversible field coils, while LS3 supplies the fixed-polarity channel. The general arrangement permits series voltage scaling; the design example uses Ns=1 because one VMJ device provides the required field voltage.

Keep the existing coil labels, connection polarities and mode mapping; this paragraph is a proposed clarification, not authorization to change them.

### Section II.C distinction between series and parallel shading

For Ns>1, nonuniform illumination can drive a shaded series-connected device into reverse bias. A bypass branch limits this voltage when its conduction threshold is reached. In the bipolar channel, a Zener diode is connected in series opposition with the bypass diode to prevent the inactive group from shorting the illuminated group. The branch also carries commutation current when the winding voltage reaches its threshold. For the Ns=1 design considered here, shading an external parallel device primarily reduces the available group current; series-string bypass action is not required to maintain continuity through the remaining devices.

Retain the existing citation for ordinary series-cell bypassing and the distinction between bipolar and unipolar protection. Do not describe a selected physical diode–Zener solution until ratings are known.

### Section IV.B selected connection

The selected VMJ device provides the nominal field voltage without external series connection. Six devices are therefore connected in parallel in each PV group to supply the required channel current. The field turns and conductor area follow from the voltage-matching and slot constraints. Shading one parallel device reduces the available photocurrent without forcing the current of the remaining devices through it.

Retain the existing reference to Table II, analytical MMF margin and irradiance result where needed; avoid repeating table values in the main prose.

### Section IV.D candidate simulation discussion

Circuit simulations use the selected parallel PV groups and the field resistance and inductance of the design example. Reversing illumination drives the field current through zero and establishes the opposite polarity. The diode–Zener branches limit the transient voltage when their threshold is below the competing PV-junction conduction voltage; otherwise, the PV junctions carry the commutation current. These results assume identical devices and constant temperature, and the protection threshold remains subject to device ratings and tolerances.

Numerical values and the Fig. 5 caption should be finalized only after the author chooses which documented clamp case to present. Do not combine new simulations with the old 552 ms result or label the generic circuit as validated hardware.

## 6. Changes proposed to figures and tables — not applied

1. Fig. 2: distinguish the general series/parallel architecture from the implemented Ns=1, Np=6 arrangement. For a machine-specific figure, show parallel devices, rather than a series chain that readers may interpret as the chosen design. This requires author approval before redrawing.
2. Fig. 3: retain as requested. Define whether its current axis is per-device or normalized group current; retain its reference-case qualification.
3. Fig. 5: propose motor-matched protected reversal and de-excitation data, with model assumptions stated. No figure was replaced during this review.
4. Table I: identify the tabulated device current as inferred from the array data if individual-device data remain unavailable.
5. Table II: its reverse-voltage and reversal-time entries currently refer to the old junction-only calculation. Replace or qualify both together with Fig. 5 after approval. Keep the nominal winding design values unchanged.
6. FEA tables: retain. The existing low-speed-current comparison and air-gap sensitivity are useful; qualify their comparison basis and avoid implying demonstrated dynamic pole changing.

## 7. Recommended next decisions

Approve the Ns/Np notation correction and the distinction between general series-string protection and the selected parallel-device design first. Then choose whether Fig. 2 should show the actual motor connection or remain general with an explicit implementation note. Before reporting a physically selected clamp, obtain individual VMJ reverse characteristics and confirm the array-to-device scaling. A prototype is not required to perform these numerical and documentation improvements.

Reproduction: run run_review.py with the installed LTspice executable, then analyse_review.py. The .cir files can also be opened directly in LTspice. results.json contains the extracted metrics; .raw and .log files preserve the solver outputs. No new COMSOL/FEA run was performed.

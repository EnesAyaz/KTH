> Historical single-example study. See DESIGN_SELECTION_METHOD.md for the current device, slot-budget and pole-ratio selection study.

# Three phase co design method

## Model boundary
This study addresses three-wire, three-phase winding groups with no external or inter-group neutral lead. A floating-wye phase basis is used numerically. Delta line/phase conversion is not modeled. All commanded phase sets satisfy iA+iB+iC=0. The earlier five-phase discussion has been moved out of the active paper.

No existing machine script is imported or modified. Run `run_three_phase_codesign.py` with the bundled Python; it uses local `vendor/` plotting dependencies and writes only Digest outputs. Run `../build_digest.py` afterward to rebuild the Word draft. The latter checks several manuscript numbers against the JSON so a parameter change cannot silently leave those numbers stale.

## Winding construction
Define pH=PH/2 and pL=PL/2, and integer r=pH/pL. Three phase-coil axes spaced by 120/pL mechanical degrees have low-mode phase angles 0,120,240 degrees. The high-mode angles are multiplied by r. Balanced positive or negative sequence is obtained when r is not divisible by 3. Ratios 2 and 4 are screened; the 12/4 ratio 3 is rejected for this construction. This is not an impossibility result for all three-phase windings.

For N equal-loaded cells, choose g=gcd(N,pL), Q=lcm(3N,3pL)=3NpL/g, c=pL/g coils per phase leg and s=Q/(3pL) slots between phase axes. There are pL repeating sectors. For q=0..s-1 and group r0=0..g-1, the cell index is j=qg+r0. Phase ph=0,1,2 uses coil indices b(3s)+q+ph*s for b=r0*c..(r0+1)*c-1. Each index appears once. Coil returns lie y slots later, modulo Q. This is a double-layer coil-position construction; coil sides sharing a slot are not joined electrically.

For N24, PH12/PL6: Q72, c1, s8, y8. Cell 1 has A coil 1→9, B 9→17, C 17→25; cell 2 starts at slots25,33,41. Low-mode phase progression is +120 degrees, high-mode progression is -120 degrees. Rotation direction must be preserved by the controller. A common mode-dependent angular offset aligns the rotor and stator d axes; CSV phase angles use the coil-start reference.

The script verifies unique coil coverage, balanced voltage/current phasors and coil-side Fourier amplitudes against the pitch factor |sin(πpy/Q)|. Pitch factors are both 0.866 for the selected example. This does not verify harmonic losses, manufacturing feasibility, force balance or all parasitic spatial orders. Q is minimal only under the stated exact-spacing construction and equal integer coils per leg.

## Cell count and voltage
N=2..40 is screened for six pole pairs: 8/4,12/6,16/8,20/10,16/4,12/4. Plotting shows selected N values for readability; the CSV retains the full sweep.

The illustrative device screen uses a 1200 V nominal and 1320 V maximum bus, factors of1.10 each for cell imbalance and overshoot, and voltage utilization ≤0.80. Required device rating ≥(1320/N)*1.10*1.10/0.80. Rating classes are illustrative and are not statements about available GaN devices. For N24 this scenario gives 66.55 V peak stress and a minimum rating of83.19 V, so a100 V class passes. N16 requires at least124.78 V under the same assumptions; a75 V nominal cell does not imply a75 V device rating.

12/6-pole Q values at N8,12,16,20,24 are72,36,144,180,72. Lower-slot alternatives may exist outside this construction. For example, N21 admits Q63, but its slot geometry and harmonic/manufacturing constraints are not ranked here. N24 is retained as a transparent even-slot candidate, not a global optimum. A full comparison must price devices, drivers, insulation, bus capacitors and winding complexity and use the established SPB loss model.

## Hybrid rotor and magnetic scaling
The 12-segment high-pole pattern is alternating +−. The six-pole pattern repeats ++−−. Segments1,4,5,8,9,12 retain their polarity and represent PM segments. Segments2,3,6,7,10,11 reverse and represent field-driven segments. The reference is the user's Conto/Bianchi ECCE2022 paper, especially Section VI and Figs18-22; our 12/6 extension is not their tested machine.

For rectangular pole-face fields of arc fraction0.70, the spatial Fourier amplitude is Bp/Bface=2 sin(pπ arc/M)/(πp) times the magnitude of the signed-pole phasor sum. This gives1.134465 for p6 and0.940828 for p3. Flux linkage scales with kp Bp/p, giving ψlow/ψhigh=1.658629 at equal pole-face magnitude and equal pitch factors. The low mode therefore needs1.659 times the high-mode back-iron flux capacity. A1.5 T low-mode yoke limit requires high-mode yoke loading≤0.904 T, absent nonlinear redistribution. This is a feasibility gate, not a freely available flux increase. Field return paths, PM sizing, excitation-circuit voltage, reversal dynamics and harmonic EMFs remain unverified.

## Conditional torque and power calculation
The curve example uses N24, a nominal1200 V bus, peak phase-voltage limit0.95 Vdc/(sqrt(3)N)=27.424 V, peak current376.308 A and phase resistance2 mΩ. The aggregate torque coefficient is(3N/2)p. All modes allow negative Id. The desired-order equations are:

Vd=R Id−ωe Lq Iq; Vq=R Iq+ωe(ψf+Ld Id)
T=(3N/2)p[ψf+(Ld−Lq)Id]Iq; ωe=pωm.

The matched 12-pole IPMSM and hybrid high-mode parameters are ψf=.026 Wb, Ld45µH and Lq90µH. Hybrid low mode uses ψf=.043124 Wb and Ld=Lq270µH. The latter is four times the mean high-mode inductance, with a round-mode approximation. These are analyst-selected linear parameters, not values extracted from the supplied prototype or validated on the KTH geometry. The hybrid endpoint fluxes are fixed; arbitrary continuous field reduction is not assumed for a rotor with fixed PM segments.

For each Id on a4001-point grid, the voltage-squared constraint is a quadratic in Iq. Its feasible interval is intersected with the current circle and Iq≥0. The best torque is capped at300 kW/ωm. Speeds are0..9000 rpm in50 rpm increments. Direct two-dimensional current-grid checks at selected points are lower bounds with gaps up to about1.96%; this is a numerical cross-check, not physical validation. Zero plotted torque denotes no positive-torque point found, not a safe mechanical operating condition.

The IPMSM field-weakening sensitivity holds ψf and saliency ratio2 while changing Ld so ψPM/(Ld Imax)=0.90 instead of1.54. It has a different peak torque and is not an optimized equal-volume comparison. It demonstrates that poor IPMSM field weakening must not be used as a universal baseline.

At150 kW the matched reference ends at4450 rpm, whereas the selectable12/6 model reaches the9000 rpm study ceiling. At300 kW both end at3300 rpm. Low mode produces155.85 kW at9000 rpm. The stronger-FW IPMSM reaches9000 rpm at300 kW. Low-mode inductances135,270,405µH give approximately300,156,104 kW at9000 rpm. An order-of-magnitude full-power target is Llow≈140µH or below under these assumptions; geometry, losses and saturation must prove whether it is achievable. Changing inductance in a sensitivity is not an implemented design change.

## Limits and next validation
The envelopes describe electromagnetic output. An assumed3 kW hybrid field loss is recorded but excluded from the plots; no shaft efficiency or equal DC-input-power benefit is claimed. Stator copper loss is recorded at operating points; core loss, field supply, thermal duty, inverter loss and mechanical loss are not deducted from the300 kW output ceiling.

Unused rotor spatial harmonics, saturation, PM demagnetization and actual modal saliency may eliminate the apparent gain. No cell-capacitor balancing, transition, excitation-reversal or mechanical stress simulation is included. The9000 rpm ceiling is an electrical study window, not a validated safe rotor speed. Next: field-analysis validation of the actual12/6 stator/rotor, particularly low-mode flux, reactance, yoke and parasitic EMFs, then equal-volume IPMSM optimization and transition/DC-cell energy checks. A simultaneous two-order overlap still has possible three-phase cross-power pulsation; removing it from the current paper's main contribution does not remove the physical constraint.

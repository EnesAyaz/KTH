# Design selection method and evidence

## Main question
Find a feasible intersection of discrete semiconductor voltage class, cell count N, independently connected coil count C, slot count Q, two pole counts PH/PL, balanced three-phase cell loading, pitch and rotor compatibility. Do not equate a higher cell count with a pole-changing control minimum.

Run `run_design_selection.py` with the bundled Python and task-local plotting dependencies. Then run the Digest `build_digest.py`. All outputs stay under Digest. No existing machine or review script is executed in place.

## Separate lower bounds
Each cell has3 inverter legs and no external/interconnected neutral. KCL removes one instantaneous current coordinate per group;3N phase branches give2N independent real current coordinates. Equal sinusoidal phase displacement in the current commands does not establish equal back-EMF or impedance. Both modes are checked for equal phase voltage magnitude, ±120-degree phase progression and equal modal gain across cells.

The voltage floor is ceil[Vbus,max × kimb × kov/(u Vrating)]. Current assumptions are1200 V nominal,1320 V maximum, kimb=1.10, kov=1.10, u=.80. Floors:100 V→20 cells;150 V→14;200 V→10;650 V→4. These are deliberately stated design margins, not a topology-invariant law. A100 V/16-cell75 V nominal design needs its actual maximum-link voltage, ripple and commutation overshoot verified; it is not automatically invalid simply because this stricter scenario requires20.

Under a standard double-layer Q-coil construction, at least one coil per leg gives3N≤Q. Under a standard single-layer Q/2-coil construction,6N≤Q. These are construction-specific capacity bounds. Splitting turns or conductor groups into additional circuits can increase C without more slots, but changes leads, insulation, phase grouping and manufacturing. The script explicitly implements double-layer Q-coil layouts only; its single-layer numbers are necessary capacity bounds, not validated single-layer designs.

## Fixed slot winding construction
Let g=gcd(pH,pL), a=pH/g and b=pL/g. A uniform phase-axis triple separated by120/g mechanical degrees has the required balanced phase sequence for both orders when a and b are not divisible by3. This includes2:1 and5:2. A3:1 ratio does not pass this family. A different distributed or multi-coil layout remains open; it must be demonstrated rather than declared impossible from this screen.

The tested Q values are18,24,...,96. N is1..32. Equal coils per phase leg requires integer c=Q/(3N). Uniform axis spacing requires integer s=Q/(3g). Primitive triples at positions q+3s*b+ph*s are grouped into cells. The code checks equal phase amplitudes,120-degree progression and equal gain across cells. Some groupings have unequal cell gain; they are rejected by the present equal-loaded family, not proven unusable with a balancing/current redesign.

Per-leg current phasors align with that leg's induced voltage in the desired order. Direct full-stator Fourier sums test both directions of the other selected order. If that other order cannot be suppressed, the candidate is rejected. No claim is made that all higher spatial harmonics disappear; detailed MMF/FEA, rotor interaction and losses still require verification.

For12/6 poles withQ36,N2,c6 and y4, calculated factors are kwH=.750 and kwL=.836516. Phase sums and other-mode rejection pass to numerical precision. The analogous one-cell layout cannot independently suppress the other selected spatial order. Thus two is the minimum demonstrated within this exact selection method. This is not a universal minimum for every single-winding harmonic, switched-winding or rotor-only pole-changing machine. Two600 V nominal stacked cells are also not a100 V-device implementation. Rotor excitation supply channels are separate hardware and are not counted in stator N.

## Discrete shortlist
For each rating and pole pair, filter all exact candidates by N≥Nvoltage and Q≤slot cap, then choose lowest N and Q. This shortlist rule is transparent but is not a loss or manufacturing optimization. Caps60,72,96 are evaluated. At Q≤60:
-100 V,8/4 poles: N20,Q60.
-100 V,12/6: no candidate in this family/even-slot set.
-150 V,12/6: N18,Q54.
-200 V,12/6: N12,Q36.
-650 V,12/6: N4,Q36 under the stated voltage margins; detailed device/paralleling and harmonic feasibility remain necessary.

Allowing Q≤72 adds the100 V,N24,Q72,12/6 candidate in the tested even-slot set. Odd-slot/fractional and other coil topologies can change the frontier. This is the correct explanation for the earlier24-cell example;24 is not a control minimum.

A48-slot benchmark-preserving choice can instead use150 V,N16,8/4 poles. The150 V voltage floor is14, but equal-branch winding compatibility at fixed Q48 raises it to16 in this family. Such differences are the purpose of joint device/winding selection.

## Pitch and ratio
For a common coil span y, kp=|sin(πpy/Q)|. The ratio screen plots minimum of both pitch factors against rho=y/(high-pole pitch). For2:1, the best minimum is .866 at rho=4/3. For5:2, the unrestricted continuous optimum is sin(4π/7)=.974928 at rho=20/7≈2.857. With rho≤1.5, its optimum is sin(2π/7)=.781831 at rho=10/7. A3:1 pitch-only curve can reach1 at rho3, but that does not cure the failed phase-triple balance condition. The1.5 limit is a stated short-span preference, not a universal physical limit. Slot discretization changes the attained values. No end-winding loss optimum is inferred from pitch alone.

The2:1 ratio also has a directly motivated synchronous hybrid-rotor route in the supplied paper. The5:2 stator match does not establish a5:2 hybrid rotor; pole grouping, PM/field return paths, flux density and unused harmonics would need a new design.

## Device evidence and limits
Primary manufacturer PDF copies are retained for EPC2361(100 V), EPC2305(150 V), EPC2304(200 V), IGLT65R025D2(650 V). Verified maximum on-resistances at25 C are1,3,5,30 mΩ. Test currents and package/current scales differ. The650 V comparator is Infineon IGLT65R025D2, rev1.1,2026-03-03, with30mΩ maximum on-resistance at25C. Gate drive, package and rated-current conditions differ from the low-voltage EPC parts. No traction current is assigned to a single FET without paralleling/thermal analysis.

At equal phase RMS current and equal devices per switch position, aggregate conduction scales as3N I²R/k. At voltage-floor N, the N*R indices are20,42,50,120 mΩ. This is a part-specific conduction index, not total loss or a fundamental voltage-class penalty. Gate charge, Qoss at actual cell voltage, temperature, current sharing, layout inductance, cost and device area must enter the existing established loss model before a sweet spot is claimed. More cells mean6N switch positions and3N leg channels before device paralleling.

## Production evidence and notation
Use total poles P and pole pairs p=P/2 consistently. Verified primary benchmarks:
-2017 Prius:48 slots and8 total poles,4 pairs (ORNL2017 presentation slide18).
-Nissan LEAF motor generations:48 slots and8 total poles,4 pairs (Nissan authors'2024 IEEJ paper Section4,p12).
-BMW i3:72 slots and12 total poles,6 pairs (DOE FY2016 report printed/PDFp200 and design tablep202).

These are a sample, not a market-share survey. They do not establish8/12/16 pole pairs as the most common EV choices. The script includes16,24 and32 total-pole sensitivity cases. Electrical frequency fe=p n/60 must be reported: at12000 rpm P8 gives800 Hz and P24 gives2400 Hz. Therefore absolute pole count matters even when the ratio is held constant. Sixty slots is a chosen compactness scenario, not an EV maximum.

## Torque and power diagnostic
The old illustrative envelope is retained as a subsequent verification gate, with a terminal-equivalent change from N24 to N12. Vm,Rs,Ld,Lq and flux linkage double; N halves; current is unchanged. Thus desired-order voltage equations scale by2, while aggregate torque and power stay invariant. This equivalence is algebraic, not magnetic identification of a36-slot physical motor. New12-cell values are Vpeak54.848 V,Ipeak376.308 A,Rs4 mΩ, high flux.052 Wb,Ld/Lq90/180µH; low flux.086249 Wb,Ld/Lq540/540µH. All modes allow negative Id and have a300 kW electromagnetic output ceiling.

The selected hybrid curve reaches9000 rpm at150 kW versus4450 rpm for the matched fixed reference, but both lose300 kW capability after3300 rpm. A stronger-FW IPMSM removes the advantage. Core/field/inverter loss, unused-harmonic EMFs, temperature, reversal/DC-cell dynamics and mechanical stress are omitted.9000 rpm is not a validated safe rotor speed. These curves cannot rank device classes or substitute for FEA.

## Next work
Prioritize a150–200 V versus100 V Pareto study, using both a48-slot8/4 baseline and a36-slot12/6 candidate rather than freezing one. Verify winding topology and lead count, identify actual high/low rotor flux and inductance maps, include device parallel area/thermal/cost and switching losses, then compare equal-volume optimized IPMSMs and drive cycles. Keep all new work inside Digest.


## Current 650-V and 17.5-mm revision

The active classes are100/150/200/650 V, with voltage floors20/14/10/4. The350-V example is historical and removed from the active digest. `evaluate_650V_cells.py` exports the two/three/four-cell voltage and winding screen and the four-cell winding connections. AtN=2/3/4, stress estimates are798.6/532.4/399.3V, compared with a chosen520-V allowance. Three cells are below the650-V continuous rating but miss the selected margin; four pass it. N4,Q36 has three series coils per phase leg and the same0.866 modal winding factors as N12,Q36.

The magnetic-model candidate now uses a17.5-mm stator yoke,132.5-mm stator outer radius, and unchanged rotor/excitation. See `check_yoke_17p5.py` and `results_saturation_screen/yoke_17p5mm_fine.json`. This no-load model does not determine actual torque-speed performance or converter loss.

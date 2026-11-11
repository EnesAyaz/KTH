# Feasibility and Co-Design of Pole-Changing Machines Fed by Stacked Polyphase Bridges

Working digest, 2026-11-09. Five-page content allocation, not final pagination. Anonymous review draft. Bracketed work items mark missing original results; this is not ready for submission.

## Page 1 - Motivation and research question

### Abstract (working)
High-voltage electric-vehicle architectures motivate modular traction converters using lower-voltage semiconductor devices. A stacked polyphase bridge (SPB) supplies separate machine winding groups from series-connected DC cells, offering control freedom that may also support electronic pole changing. However, a feasible winding pattern does not by itself guarantee balanced cell power or improved drive performance. This study formulates a joint screen of module phase number, winding layout, pole combination, cell energy storage and machine voltage constraints. Three-phase 4/2-pole and five-phase 6/2-pole designs are proposed for comparison, with matched-pole controls to distinguish phase-number and pole-ratio effects. Existing 8/4-pole project simulations identify a motivating trade-off: five-phase grouping suppresses the dominant ideal cross-power term, while machine voltage limits can still cause a substantial transition torque dip. The intended outcome is a design map identifying feasible combinations and their capacitor, converter and machine penalties. [Replace this prospective abstract after the proposed designs have been evaluated.]

### I. Introduction
Megawatt charging for heavy-duty electric vehicles strengthens interest in high-voltage electrical architectures. For a given power, higher voltage reduces DC current, although charging capability alone does not dictate the traction-link voltage. Conventional two-level traction inverters expose each switch to the full DC-link voltage, including an allowance for switching transients. The resulting voltage rating, switching energy, thermal limits and electromagnetic compatibility requirements constrain the practical switching frequency. These constraints also influence machine current ripple, harmonic loss and common-mode excitation.

Multilevel converters, including neutral-point-clamped and flying-capacitor implementations with three or more levels, offer smaller output-voltage steps and opportunities to use lower-voltage devices. Their common-mode performance depends on topology and modulation, while capacitor balancing and additional components introduce design and control requirements. Fault tolerance requires explicit provisions and cannot be inferred from either the multilevel label or component count.

SPB takes a different modular approach: series-connected DC cells supply separate polyphase winding groups. Lower cell voltages can permit low-voltage GaN devices, provided rating margins cover bus variation, imbalance and overshoot. The independently controlled groups also provide an opportunity for electronic pole changing without stator contactors. This opportunity requires co-design: the winding must produce both spatial orders, the rotor must support them, and the series cells must tolerate the resulting power distribution.

[Figure 1: SPB stack, isolated winding neutrals, cell energy storage and two pole-mode current patterns. Use an original schematic.]

## Page 2 - Prior work and the contribution

### II. Pole changing and the SPB-specific question
Pole-changing induction machines exploit the cage rotor's ability to adapt to the stator rotating field. Reconfigurable stator connections, separate windings and multiple-inverter excitation are established approaches. Consequently, the use of multiple inverter outputs alone is insufficient as a novelty claim.

Conto and Bianchi [R1] demonstrate that pole changing is also possible in purpose-designed synchronous machines. Their investigated families include wound-rotor and specialized hybrid configurations. Stator pole changes must be accompanied by a compatible rotor field or reluctance structure. Their work also highlights back-iron saturation and performance compromises in the lower-pole mode. It does not establish that a conventional fixed-pole PM rotor can achieve equivalent behaviour by changing stator commands alone.

The proposed contribution is a constrained design method for a series-stacked drive: (i) screen winding/pole compatibility under isolated-neutral excitation; (ii) derive cell cross-power and the corresponding storage requirement during multi-order operation; and (iii) compare feasible designs at matched machine, converter and duty constraints. The contribution is the engineering consequence for SPB co-design, rather than a claim that spatial orthogonality or electronic pole changing is new.

[Table I: A, B, C and negative-control D from the research plan. Add actual slot counts, winding factors, cell voltage ratings, leg counts and rotor configurations only after calculation.]

### III. Fair comparison
The requested three-phase 4/2-pole and five-phase 6/2-pole designs differ in both phase number and pole ratio. A five-phase 4/2-pole control is therefore needed before attributing a benefit to phase number. Compare against an optimized fixed-pole SPB and a three-phase SPB with additional cell capacitance. Fix the DC voltage range, torque-speed duty, active machine envelope, copper-temperature limit, current-density limit and allowed cell ripple. Account for rotor excitation power and hardware in synchronous designs.

## Page 3 - Method and design constraints

### IV. Winding and cell-energy feasibility
Let N denote the number of series DC modules, m the phases per module and p the pole-pair order. For the existing project's interleaved spaced construction with c=Q/(mN) coils per leg, a full-distribution-factor mode requires c to divide p, while m must not divide p/c. Constant single-mode cell power additionally requires m not to divide 2p/c. These conditions apply to this construction; other windings require direct evaluation.

For uniformly sampled phases theta_k=2*pi*k/m, the spatial sum

S_r = sum(k=0,...,m-1) exp(j*r*theta_k)

is zero unless m divides r. Cross products of signed spatial orders a and b can therefore survive the module phase sum when m divides a+b or a-b. Temporal frequency and sequence determine whether the surviving term produces ripple or a DC power mismatch. The 4/2-pole pair corresponds to orders 2 and 1 and admits a sum-order coupling in m=3. The 6/2-pole pair corresponds to orders 3 and 1; neither sum nor difference is divisible by 5. These are ideal coupling screens, not complete machine-performance predictions.

For cell j, with converter output power P_j and a consistent loss convention,

d(0.5*C_j*V_j^2)/dt = V_j*I_stack - P_j.

A sinusoidal imbalance of peak power P_hat at angular frequency Omega gives the small-ripple estimate

DeltaV_hat approximately P_hat/(Omega*C_j*V_j0).

For transitions, integrate the actual imbalance and enforce voltage limits directly. A low ripple frequency can demand substantial storage even when mean module powers match. Equal-frequency interactions and nonuniform groups require a separate average-power balance check. Saturation, asymmetry and controller limits must be assessed beyond the ideal phase-sum result.

[Figure 2: design-screen flow: winding -> rotor -> voltage/current/thermal -> cell energy -> loss/cost ranking.]

## Page 4 - Existing evidence and planned numerical comparison

### V. Motivating evidence from the existing 8/4-pole study
The existing project contains an independently formulated nonlinear magnetic-equivalent-circuit replay coupled to linearized DC-cell energy calculations. At 2100 rpm, with 16 cells on a 1200 V link and a 350 kW current-limit basis, its three-phase 8/4-pole overlap case gives a flat-road peak cell-power pulsation of 9.244 kW at 210 Hz. The corresponding single-frequency estimate is 12.5 mF per cell for +/-10% ripple about 75 V. A five-phase Q80 construction suppresses the dominant ideal interaction, leaving reported nonlinear residuals of 7 W on flat road and 39 W on a 2% grade.

These numbers are existing 8/4-pole model results, not results for the proposed 4/2- or 6/2-pole machines. The m=3 and m=5 constructions use Q48 and Q80 respectively, so the comparison does not yet establish a manufacturing or optimized-system advantage. The very large ripple predicted for undersized capacitors exceeds the validity of the linearized model and should be interpreted as a rejected operating point.

The same study provides an essential counterexample: the best tested five-phase overlapped schedule retains only 0.84 of requested torque on flat road and reaches approximately -0.15 on a 2% grade. Suppression of cell pulsation therefore does not imply a torque-continuous transition. Residual rotor flux and the shared machine voltage budget remain limiting.

[Table II: preserve the existing anchor's operating basis and source paths; separately report new A-C results after verification. Do not mix 300 kW and 350 kW current-limit cases.]

### VI. Required original results
For each candidate, report winding factors and harmonic spectrum, maximum voltage/current, yoke/tooth flux density, feasible torque-speed envelope, transition torque minimum and duration, cell ripple, required capacitance and converter/machine losses. Show Pareto trade-offs rather than a single unsupported winner. A synchronous design must additionally report excitation grouping, reversal voltage, field time constant, field loss and mode compatibility. [Insert completed calculations and selected-point FEA/cross-checks.]

## Page 5 - Interpretation, limitations and references

### VII. Design implications and conclusion (provisional)
SPB may reuse existing winding-group control freedom for pole changing, but this does not make pole changing free at system level. Winding utilization, rotor compatibility, cell-energy storage and voltage-constrained transitions determine whether the opportunity is useful. Phase number is a co-design variable: it can suppress particular ideal cross-power terms while increasing the number of converter legs and changing the feasible winding geometry.

A suitable conclusion will identify feasible operating regions and explicit rejection conditions. It should state whether additional capacitance in a three-phase design is preferable to a five-phase module for the specified duty, and whether the machine benefit survives converter and excitation penalties. A negative result for a particular synchronous rotor or pole pair is valuable if the constraints and comparison are fair. No drive-cycle energy saving, optimal pole pair or fault-tolerance advantage is claimed before those evaluations exist.

Limitations: no newly manufactured machine; existing evidence is model-based; the proposed cases have not yet been optimized or simulated; the existing nonlinear replay does not model all cage reactions to saturation-generated spatial orders; capacitor bias retention, thermal performance and balancing-loop dynamics require verification. Final submission must replace prospective statements and result slots with completed work.

### References to develop
[R1] C. Conto and N. Bianchi, "On the Possibility to Achieve a Pole Change in Synchronous Motors," IEEE ECCE, 2022. https://doi.org/10.1109/ECCE50734.2022.9947754

[R2] "Comparative Evaluation of Three-Phase Three-Level Flying Capacitor and Stacked Polyphase Bridge GaN Inverter Systems for Integrated Motor Drives," Electronics, vol. 13, no. 7, 1259, 2024. https://doi.org/10.3390/electronics13071259

[R3] "Dynamic multi-agent dc-bus reconfiguration in modular motor drives with a stacked polyphase bridge converter." https://doi.org/10.1049/elp2.12376

Add verified primary references on electronic pole changing, multiphase vector-space decomposition, and the specific selected synchronous rotor. The source register contains further motivation and submission links. Internal result files are traceability records, not a substitute for prior-art citations in the final manuscript.

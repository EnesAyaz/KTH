# Analyst assumptions

## T03 - torque-speed envelopes (IM / PMSM / WRSM, with and without SPB pole changing) {#t03}

Script: `02_analytics/torque_speed_envelope.py` -> `02_analytics/results/torque_speed_envelope.json`.
Quick-look: `02_analytics/scratch/torque_speed_envelope_quicklook.png`.
Status: first-pass analytical model. No FEA. Numbers are for comparing the machines and finding trends, not for design.

### Decisions used
- D01: IM, PMSM and WRSM. D02 (provisional): 40 t truck, 350 kW continuous, 1200 V DC link.
- No open decision blocks T03.

### Inverter (identical for all machines)
- 1200 V / 16 modules = 75 V per module. Each module is a three-phase bridge that feeds one coil group (3 coils) in star with an isolated neutral.
- Voltage limit: SVPWM linear range, V_ph,pk <= m_margin * V_mod / sqrt(3) with m_margin = 0.95, giving **29.09 V rms per coil**. Overmodulation and six-step are not used.
- Current limit: sized from 350 kW = 48 * V_rms * I_rms * PF_ref * eta_ref with PF_ref = 0.85 and eta_ref = 0.95, giving **I_max = 310.4 A rms (439 A peak) per module leg**. Inverter rating S = 48 * 29.09 * 310.4 = 433 kVA.
- The fixed SPB reference is 300 kW (2 x 150 kW blocks per leg). 350 kW needs about 17 % more current per leg or more parallel cells. This is flagged for the leader and is not resolved here.
- The current-limit sweep scales I_max by 0.3 to 2.0 at fixed V, with the machines unchanged.

### Vehicle
- From `../Drive Cycle/basic_vehicle_dynamics.m`: m = 40 t, r_wheel = 0.52 m, A = 10.5 m^2, Cd = 0.7, Crr = 0.01, rho = 1.225. Gear efficiency is 0.97 (my assumption).
- v_max = 90 km/h at n_max = 4500 rpm, which gives a single-speed gear ratio of 9.80.
- Cruise at 85 km/h is 4250 rpm and 352 Nm (155 kW at the wheel). Starting on a 12 % grade needs 2770 Nm at the motor.
- The drive-cycle .mat file is in OneDrive, outside the repo. It was not used in T03.

### Common stator (same outer size and copper for all machines)
- Q = 48 slots, R_gap = 165 mm, L_stk = 360 mm, R_out = 235 mm. Slots are 9 x 45 mm, yoke is 25 mm, g = 1.0 mm, k_c*k_sat = 1.3.
- 48 double-layer lap coils with N_c = 3 turns and pitch y = 7 slots. Fill factor 0.6, Cu at 120 C (2.40e-8 ohm m).
- R_coil = 2.16 mOhm. Copper mass 63 kg. J = 7.7 A/mm^2 at I_max (oil cooling assumed).
- Coil-to-module mapping: module j feeds coils j, j+16 and j+32 (120 deg mechanical apart). Coil k carries electrical angle alpha_k = p * 2*pi*k/Q.
  - This is the coil-group logic of Enes's 12-slot linearised 2-pole/4-pole patterns (`Field Excitation/6-phase Induction Machine/Phase-Pole.pptx`, slides 1-4), generalised to 48 coils and 16 modules.
  - Module currents sum to zero for every p not divisible by 3 (checked numerically).
- Machine frame: 48 identical coil-phases (m = 48). Per-coil rms phasor equivalent circuit.
  - Winding factor = pitch factor sin(p*y*pi/Q): 0.966 at 2p = 8 and 0.793 at 2p = 4. The distribution factor is 1 because each coil has its own phase.
  - MMF harmonics appear only at p ± jQ.
  - L_m = 2 m mu0 R L (N_c k_w)^2 / (pi g_eff p^2).
- Leakage per coil:
  - Slot leakage: lambda_self = 1.2. Mutual with the other coil side in the same slot: lambda_mut = 0.4 * cos(2*pi*p*y/Q).
  - End-winding leakage: lambda = 0.3.
  - Differential leakage from the numerical MMF spectrum: sigma_d = 0.020 (2p = 8) and 0.005 (2p = 4).
- Saturation by flux caps: airgap fundamental B <= 0.90 T (teeth), and stator yoke B_y = B*R/(p*h_y) <= 1.45 T.
  - The cap is 0.879 T at 2p = 8 and **0.439 T at 2p = 4**. The 2p = 4 cap is the main penalty of running 4-pole in an 8-pole-sized stator.
- Iron loss covers stator teeth and yoke at the fundamental only: P = 1.5 * m * (k_h f B^2 + k_e f^2 B^2).
  - Fit to M270-35A: k_h = 0.0212 W/(kg Hz T^2) and k_e = 5.6e-5 W/(kg Hz^2 T^2).
  - Masses: teeth 75 kg, yoke 96 kg. Tooth B = B_gap * slot pitch / tooth width.
  - Not included: rotor iron loss, PWM and slot harmonics, magnet eddy loss.
- Friction and windage: 0.5 kW*(n/4500) + 1.0 kW*(n/4500)^3, the same for all machines.
- AC copper effects are ignored.

### IM
- Copper cage with Q_r = 58, 150 mm^2 bars and 600 mm^2 rings at 150 C.
- Referral to the stator: R_r' = 4m(N_c k_w)^2/Q_r * (R_bar + R_ring/(2 sin^2(pi p/Q_r))). The ring share of R_r is 9 % at 2p = 8 and 29 % at 2p = 4. The rotor leakage uses the same transform, plus rotor differential leakage.
- The cage adapts to any p, so no rotor action is needed.
- Envelope: at each speed, maximise torque over (airgap flux <= cap, slip frequency) under the |V| and |I| limits.
- Efficiency points: minimum-loss flux, with slip solved in closed form for the required torque.

### PMSM (2p = 8, fixed; baseline)
- Saturated effective per-unit values on the SPB base (V = 29.09 V, I = 310.4 A, 2p = 8 at 1200 rpm): psi_pm = 0.70, L_d = 0.65, L_q = 1.30.
  - Characteristic current = 1.08 I_max.
  - psi_pm = 0.70 pu corresponds to B = 0.67 T fundamental.
- These are typical IPM traction values, not a design. The PMSM cruise efficiency and power factor depend strongly on psi_pm (high field-weakening current at cruise).
- Control: I_d <= 0, optimal over current angle (MTPA, then field weakening).

### WRSM (2p = 8, pole change to 2p = 4 by reversing rotor coil groups)
- Seed: Enes's PC-WFSM (P2, Ayaz/Tosun draft), `Airgap Harmonics/OPT-Workspace/config/draft_parameters.json`.
  - **DRAFT, unverified** (see `notes/open-questions.md` there): 10 kW, 4/2-pole, 100 Hz in both modes, eta 92.4 / 93.1 %.
  - Equal power at equal f_e implies T_low/T_high of about 0.5. The model gives 0.45 (baseline) and 0.34 (sensitivity).
- Rotor: 8 salient poles with pole arc ratio 0.7. Patterns follow `Field Excitation/FE_MMF.m` (P4).
  - 2p = 8: [1 -1 1 -1 1 -1 1 -1]. 2p = 4: [1 1 -1 -1 1 1 -1 -1].
  - Group A (coils 0, 3, 4, 7) keeps its polarity. Group B (coils 1, 2, 5, 6) is reversed.
- Numerical rotor-field FFT at equal B0:
  - 2p = 4 fundamental is 0.83x the 2p = 8 fundamental.
  - The 6th order (12-pole) is 0.60 of B0. It is zero-sequence inside every SPB module (coils 120 deg apart, 6 x 120 deg = 720 deg), so it drives no current through the isolated neutral.
  - The 10th order (0.14 of B0) is not zero-sequence. This is a simulator item.
- Rotor yoke: baseline margin = 2.0, i.e. the rotor yoke is sized for the ++-- pattern (which carries 2x the yoke flux), as in a purpose-built PC-WFSM (P2 seed).
  - In 2p = 4 the stator yoke cap (0.439 T) then limits I_f to 0.655 pu.
  - Sensitivity: margin = 1.0 (rotor yoke sized for 8 poles only), giving I_f <= 0.5 pu.
- Per-unit at 2p = 8 (saturated, typical salient-pole values): psi_f,max = 0.85, L_d = 1.10, L_q = 0.65. Field copper is 4 kW at full I_f (~1.1 % of 350 kW), scaled as I_f^2.
- 2p = 4 inductances: the magnetising part is scaled by k_w^2/p^2 (x2.70) and the leakage is recomputed.
  - This is the key assumption behind the WRSM result. The linear scaling may overstate L_d at 2p = 4 if that axis saturates. The simulator should check it against P2 FEA.
- Two control policies:
  - (i) I_d = 0, field weakening by I_f only (as in the brief).
  - (ii) Free I_d <= 0 together with I_f (the realistic controller).
- Bipolar excitation of group B is required. Generic rotating-rectifier brushless exciters are unipolar (Krupp2015rotary, Stella2024excitation).
  - Enes's own bipolar exciters exist at small scale and are treated as available: WPT, +/-2.88 A, 118 W, 99 % rectifier efficiency (P1); optical, 10 kW PC-WFSM (P2).
  - Scaling them to the ~4 kW truck field is open. The fallback is 3 slip rings plus a stationary H-bridge.

### Pole transition (order of magnitude)
- WRSM: tau_f = L_f/R_f = 2 W_f / P_f, which does not depend on the turn count.
  - W_f is the airgap energy at full field (68.5 J) times 1.3 for pole leakage, which gives tau_f = 45 ms.
  - P1 sequence (free-wheel to 5 %, 20 ms blanking, unforced build-up to 95 %): about 0.29 s, comparable to an AMT gear shift.
  - Forced reversal with 3x field voltage: about 0.05 s.
  - Saturation is ignored, which overestimates L_f.
  - Gradual option for the simulator: the P4 pattern [1 k -k -1 ...] with k swept from 1 to -1.
- IM: rotor time constant tau_r = 0.48 s (2p = 8) and 1.46 s (2p = 4).
  - Building the 2p = 4 flux at 2100 rpm with i_d forced to I_max takes about 85 ms.
  - The decaying 2p = 8 cage currents are spatially orthogonal to the new field.

### Metrics
- n_base = the highest speed with T >= 0.99 T_peak.
- Constant-power band = P >= 0.95 P(n_base). CPSR = n_end/n_base, evaluated up to 9000 rpm and flagged when capped.
- Crossover = the lowest speed above which the 2p = 4 envelope stays above the 2p = 8 envelope.
- Torque is electromagnetic. Efficiency covers the machine only: no inverter, no gearbox.
  - Inverter switching loss does not change with pole count (same f_sw). Conduction loss scales with the I_rms reported at each point.

### Literature anchors (T02, `01_literature/inputs_for_analyst.md`; "Sec." = secondary via Prakht2025review)
- Chen2025electromagnetic (Sec.): 40 t truck, WRSM vs IPMSM. High-speed eta 92.46 vs 87.61 %, cycle +4.11 %, PF 0.96 vs 0.45. The direction matches T03 at cruise (WRSM PF 0.95, PMSM 0.54).
- Prakht2025traction: an IM with CPSR 3.5 needs a 125 kVA inverter for 50 kW (2.5 kVA/kW). Compare with the T03 SPB IM with pole change at about 1.24 kVA/kW for CPSR of about 4.
- Bitsi2022design: WICSC IM shows no envelope extension for current limit <= 18 A of 22 A. T03 has I_max/I_mag(2p = 8) = 5.3, and the extension persists down to 0.3 I_max (see sweep).
- Prakht2025review: typical road-vehicle CPSR is 3-4.
- Mademlis2020performance and Dmitrievskii2023comparative (Sec.) are context only and not used numerically.

### Sanity checks (all in JSON `sanity_checks`)
- Winding factor, numerical MMF vs analytic: 0.96605 / 0.96593 (2p = 8) and 0.79335 / 0.79335 (2p = 4).
- Conventional 3-phase 48-slot, 8-pole, y = 5 winding: 0.9332 numerical vs 0.9330 textbook.
- 48-coil-phase IM vs the equivalent 3-phase machine (16 coils in series per phase): identical torque, voltage x16. This is the p = const reduction to the three-phase result.
- IM breakdown at 6000 rpm: 161.9 Nm envelope vs 165.9 Nm Thevenin/Kloss (2.4 %, flux and slip grid resolution).
- PMSM (R = 0): MTPA torque 3062.4 Nm matches the closed form, and the corner speed matches 1001.6 rpm.
- WRSM I_d = 0 (R = 0) high-speed power: m V^2/(2 omega L_q) = 66.68 kW vs 66.68 kW numerical.

## D02 final: 300 kW (rerun of T03 envelopes) {#t03-300kw}

- Run with `python 02_analytics/torque_speed_envelope.py --P_rated_kW 300`, or set env `SPB_P_RATED_KW=300` when importing.
  - Output: `results/torque_speed_envelope_300kW.json` and `scratch/torque_speed_envelope_quicklook_300kW.png`.
  - The default (350) run and `torque_speed_envelope.json` are unchanged (md5 checked), because the simulator is validating them.
- What changes at 300 kW. The voltage limit stays 29.09 V rms per coil.

  | Quantity | 350 kW | 300 kW |
  |---|---|---|
  | I_max (A rms per leg) | 310.4 | **266.1** (376 A peak) |
  | Inverter kVA | 433 | **372** |

  - 266 A per leg is the SPB reference 2 x 150 kW blocks per leg, so the earlier 17 % current shortfall flag is gone.
- What stays fixed and what scales:
  - IM: the stator design is unchanged (N_c = 3 is set by voltage, not current).
  - PMSM/WRSM: per-unit parameters stay on the SPB base, so the machines are re-matched to the inverter (L in H scales with 1/I_max and psi is unchanged).
- Start/grade requirement: 2770 Nm at the motor (12 % grade at G = 9.80) is a vehicle requirement and does not depend on power. It is **no longer met at G = 9.80** by any machine:

  | Machine (G = 9.80) | Peak torque (Nm) | Steepest start grade |
  |---|---|---|
  | IM with pole change | 2523 | **10.8 %** |
  | PMSM | 2625 | 11.3 % |
  | WRSM | 2513 | 10.8 % |

  - The grade is solved from c*cos(a) + sin(a) = F/(mg) with v = 0 and eta_gear = 0.97 (`max_start_grade_pct`).
  - Meeting 12 % needs G >= 10.9 for the IM (T03b: G = 10.875 gives 12.14 %) or about 10 % more current.
- Other 300 kW numbers: IM with pole change CPSR 4.55, crossover 2252 rpm, 305 kW at 4500 rpm. Cruise efficiencies (simple T03 loss model) are unchanged at the same current: IM 97.05 %, WRSM 97.23 %, PMSM 96.29 %.
- D04 (VECTO group 5 cycles in `data/vecto/`) replaces the `../Drive Cycle` constants from T07 on. T03, T03-300kW and T03b still use the `../Drive Cycle` vehicle constants (m = 40 t, r = 0.52 m, CdA = 7.35 m^2, Crr = 0.01).

## T03b - fair fixed-pole IM baselines and realistic IM losses (300 kW) {#t03b}

Script: `02_analytics/fair_baselines.py` -> `results/fair_baselines.json`. It imports the T03 module at 300 kW and does not write any T03 file.

### Same constraints for all three IMs
- R_out = 235 mm, L_stk = 360 mm, copper mass 62.9 kg, B_yoke <= 1.45 T, B_tooth <= 1.65 T, B_gap <= 0.90 T.
- Inverter: 29.09 V rms and 266.1 A rms per leg (372 kVA).
- Rotor surface speed <= 125 m/s (copper cage), which caps motor speed at 7.5-8.0k rpm.

### Fixed-pole designs
- Feeding: one coil-phase per SPB leg (k_d = 1, pitch 5/6). This is at least as good as a conventional 3-phase belt winding (k_d = 0.96), so the baseline is not handicapped.
- 2p = 4: Q = 48.
- **2p = 6 cannot be wound on 48 slots with 16 three-phase modules.** With p divisible by 3, a module's coils 120 deg mechanical apart fall in phase, and a balanced 3-phase 6-pole winding needs 9 | Q.
  - It is modelled with Q = 144: each leg drives 3 coils in series, 120 deg mechanical apart and in phase.
  - The resulting 3.3 mm slots are a practicality flag.
- Search variables:
  - bore R_gap = 120-190 mm;
  - yoke sized for B_design = 0.5-0.88 T;
  - slot depth = remainder; slot width from the fixed copper volume and the end-turn length (longer for low p);
  - effective series turns per leg N_leg = 1.5-9 (continuous; rounding is a stack/turn detail);
  - gear ratio G = 4-22.
- Slot permeance is scaled by (h/3b + 0.33)/2.0, which equals 1 for the T03 slot.
- The cage is scaled with the bore.
- Objective: maximise P at 90 km/h subject to the 12 % start torque (at the chosen G) and the tip-speed limit.
- Also reported:
  - the same machine at G = 9.80, with the inverter kVA it would need for the 12 % start;
  - a 2-speed gearbox (G_low just meets the start; G_high maximises P at 90 km/h);
  - the pole-changing IM with its gear chosen by the same rule.
- Check: the generic design code reproduces the T03 design (slot width 9.0 mm recovered, T_peak identical, P at 4500 rpm within 1 %).

### Realistic IM loss model (leader request; applied to every IM case)
- Stray load: IEC 60034-2-1 assumed allowance, P_LL,N = P1,N (0.025 - 0.005 log10(P2,N/1 kW)), giving 3.98 kW at 300 kW.
  - Scaled as (T/T_N)^2, with T_N = 300 kW / omega_base of the active mode's envelope.
  - Sensitivity at 2x, since inverter-fed machines often exceed the allowance.
- Rotor-bar skin effect: deep rectangular bar with h = 25 mm (scaled with bore), k_R(xi) applied to the bar part of R_r.
  - At slip frequency (1-3 Hz) k_R is about 1.00, i.e. negligible. At f_sw it is about 98.
- Rotor copper at the actual slip: included as 48 I_r^2 (R_bar k_R + R_ring).
- Magnetising-current copper: included through |I_s|. The magnetising share 48 I_m^2 R_s is reported (< 60 W at the part-load points).
  - At cruise speeds all IMs are already voltage-limited, so loss-optimal flux and rated flux coincide.
- SPB PWM ripple (upper-bound estimate):
  - f_sw = 100 kHz at 75 V (default in `../Analytical Loss Calculations - GaN/LOSS_MODELING.md`).
  - Ripple dI_pp = V_mod/(4 L_hf f_sw), with L_hf = 0.5 x total leakage, triangular rms.
  - Stator copper k_ac = 5; cage k_R(f_sw) on bars and x5 on rings.
  - Tooth eddy loss from the leakage ripple flux, with lamination skin correction (mu_r = 1000).
  - Result: 0.1-0.45 kW, dominated by tooth eddy loss. It is small because the per-module voltage is 75 V and f_sw = 100 kHz.
- Not included: gearbox loss dependence on ratio (eta_gear = 0.97 for all), inverter loss, rotor iron loss, thermal feedback.
  - The friction/windage law 0.5 kW (n/4500) + 1.0 kW (n/4500)^3 drives the fixed-pole cruise results (high motor speed), so efficiency excluding friction/windage is reported too.
- Part-load points are defined at the wheel and seen through each machine's own gear:
  - 85 km/h flat (VECTO long-haul mean target 83.4 km/h);
  - 60 km/h flat;
  - 85 km/h on 1 %;
  - 50 km/h on 3 %.
  - The requested "30-40 % of rated torque at cruise" is not reachable at 85 km/h within 300 kW. Flat 85 km/h is 14 % of the low-speed peak torque but 0.36 T_N of the PC IM's 4-pole mode. The 50 km/h, 3 % point gives 0.36-0.37 T_N for the fixed machines.
- Efficiency maps for T07: `efficiency_maps` in fair_baselines.json, 36 speeds x 26 torques on the motor side per IM case. They use the realistic loss model; for the PC IM the better mode is chosen per point.
  - `realistic_point()` and `efficiency_map()` can be called on the stored design dicts.

## T03d - drivetrain losses: gear/e-axle vs ratio and stages, motor friction + windage (300 kW) {#t03d}

Script: `02_analytics/drivetrain_losses.py` -> `results/drivetrain_losses.json`. Public vectorised functions for T07:
- `gear_topology()`
- `gear_motor_point(T_wheel, n_wheel, stages, drag_scale)`
- `mech_losses(n, T_motor, rotor)`
- `rotor_from_design()`

### Gear / e-axle
- Per-stage loss uses the VECTO generic transmission loss (stable @68a719e, `GenericTransmissionComponentData.cs` + `Constants.GenericLossMapSettings`; provenance in `data/vecto/README.md`):
  - T_loss,out = Td0/2 + Td0/2 · n/150 rpm + |T_out|(1/0.98 − 1), with Td0 = 52.5 + 15 i (Nm, output side).
  - These values appear to be 0.75x the regulation standard values. That is unverified; lit-scout should check Reg. (EU) 2017/2400 Annex VI/VII.
- Topologies (wheel side first):
  - **single**: hypoid axle (i_axle = 3.0, raised up to 4.5 if needed) + 1 helical stage (i <= 5).
  - **two_stage**: axle 3.0 + 2 equal helical stages.
  - **two_speed**: axle + 1 helical stage with two selectable pairs.
    - The unloaded pair adds its drag term.
    - At each point the gear with the lower total loss is used.
    - The axle ratio is raised so both pairs stay within i <= 5.
- Mesh efficiency is 0.98 per stage (VECTO generic) for hypoid and helical. Sensitivity: helical 0.99. Assumed; source needed.
- **Own assumption (flagged):**
  - VECTO's drag speed law is defined for axle output speeds. Every stage is therefore evaluated at wheel-equivalent speed, and its drag torque is scaled with the stage's rated output torque relative to the axle (T_ref = 27.1 kNm, the 12 % start).
  - In effect, each stage costs the drag power of an axle with the same torque-speed product.
  - Applying VECTO's law directly at intermediate-shaft speeds gives 20+ kW per stage, which is unphysical.
- Two drag variants:
  - **VECTO_generic** (scale 1.0): deliberately conservative. A generic i = 3 axle at 85 km/h loses 11.7 kW (eta = 92.8 %).
  - **certified_like** (drag x 0.3): own assumption. It stands in for certified axle data until lit-scout finds published heavy-duty axle or e-axle loss maps.
- Inverter loss is excluded. eta_drivetrain = wheel power / motor electrical input.

### Motor friction and windage (same model for every machine; replaces the T03 law 0.5 kW (n/4500) + 1.0 kW (n/4500)^3)
- Air-gap windage (Couette): C_M = 1.03 (d/R)^0.3 Re^-0.5 (Re < 1e4) and 0.065 (d/R)^0.3 Re^-0.2 (Re > 1e4); P = k C_M pi rho w^3 R^4 L.
  - Bilgen & Boulos 1973 as quoted by Saari 1998. Air at 60 C, k_rough = 1.0, gap = 1 mm.
- Rotor end faces: free-disc C_M = 3.87 Re^-0.5 (laminar) and 0.146 Re^-0.2 (turbulent); P = 0.5 C_M rho w^3 (R^5 - r_shaft^5) per face.
- Bearings (SKF): M = 0.5 mu F d with mu = 0.0015 and d = 70 mm. F = rotor weight + gear mesh force T/(r_pinion cos 20 deg), with r_pinion = 35 mm. Plus SKF no-load M0 = 1e-7 f0 (nu n)^(2/3) dm^3 for 2 bearings (f0 = 2, nu = 10 mm^2/s, dm = 100 mm).
- One radial shaft seal: P = 7.69e-6 d^2 n (SKF estimate, d = 70 mm).
- Result for R = 165 mm: 1.17 kW at 4500 rpm and 3.0 kW at 7500 rpm. The old T03 law gave 1.5 kW and 5.5 kW.
- **Calibration status:**
  - No measured traction-motor friction/windage value is available yet (lit-scout request).
  - Upper-bound check: VECTO generic ASM no-load loss (iron + mechanical) is 0.55 % / 1.95 % / 5.75 % of P_rated at 1.0 / 2.2 / 3.8 x base speed. The model's friction/windage is 6 % / 5 % / 5 % of those totals, consistent with friction/windage being a minor part of no-load loss.
  - Oil-spray churning in the end space is not modelled.
- Electromagnetic losses: IMs use the T03b realistic model, with the best mode chosen per point.
  - PMSM/WRSM use T03 at 300 kW plus the IEC stray allowance for parity.
  - PWM ripple loss is not modelled for PMSM/WRSM; for the IM it is 0.1-0.45 kW.
- The motor operating point is recomputed from wheel torque through the gear model. The T03/T03b constant eta_gear = 0.97 is no longer used in T03d.

## T08 - module count N x phase number m x slots Q x pole sets; gap-loop screens H01/H02/H04/H05 (300 kW) {#t08}

Script: `02_analytics/module_count_sweep.py`.
- Outputs:
  - `results/module_count_sweep.json` (master);
  - `results/screen_H01.json`, `screen_H02.json`, `screen_H04.json`, `screen_H05.json`;
  - `results/sensitivity_slot_leakage_2x.json`.
- Inputs that can be overridden (R01):
  - `--geometry <json>` (keys lam_slot_self, lam_slot_mut, lam_end, B_yoke_max_T, B_gap_max_T, g_m, kc_ksat);
  - `--slot_leakage_scale k`;
  - `--B_cap_scale k`.
  - Any override writes suffixed files and never touches the default screens.
- Not reconciled with the simulator yet; waiting for `reconcile_R01.md`.

### Winding / module feasibility (H01)
Stator and modules:
- Q coils, double layer. N modules in series on 1200 V, each an m-leg bridge (m = 3, 5, 6, 7, 9) with an isolated neutral.
- L = mN legs, and each leg drives c = Q/L coils in series. The wiring is fixed (coil polarity +/-1).
- Electronic mode p: coil k gets angle p 2 pi k / Q.

A mode is available with zero extra hardware iff, for the same wiring:
- (i) all leg phasors have equal magnitude (equal module power);
- (ii) the unit phasors of each module sum to zero (isolated neutral);
- (iii) for constant module power (no 2nd-harmonic power pulsation in the series DC stack), their squares also sum to zero.

Search space:
- Wirings: "spaced" (coils of a leg mN slots apart) or "contiguous" (adjacent coils, belt-like), with all sign patterns for c <= 4 and +/alternating for c > 4.
- Module partitions: interleaved {j + tN} or block {jm + t}. For m = 3 and L <= 72, also exact triple matching via signature classes.

Coverage:
- N = 2..24 (11 values), Q = 24..144 (multiples of mN), p <= min(8, Q/6), so 2p <= 16.
- Q = 36-96 is flagged practical (slot pitch 29-11 mm at the 330 mm bore).

Pitch and winding factor:
- Coil pitch per pair maximises k_p(p_hi)^2 + k_p(p_lo)^2.
- k_w = k_p * k_d, checked against the numerical MMF fundamental. sigma_diff comes from the same MMF.

Closed-form rule (spaced wiring, interleaved modules; derived):
- Mode p works with k_d = 1 iff c | p and m does not divide p/c.
- Constant module power additionally needs m not dividing 2p/c.
- Checked against the enumeration: 1221 agree, 0 disagree.

### Inverter per (N, m)
- V_module = 1200/N.
- Device class: smallest class in Enes's ICPE comparison CSV with V_module <= 0.75 V_class. Devices used: EPC2361 (100 V), EPC2304 (200 V), EPC2050 (350 V), IGT65R025D2 (650 V).
  - N = 2 (600 V) has no class with margin in that set (650 V at 0.92). This is flagged; SiC would be needed and is outside the data.
- m-leg voltage utilisation k_m = 1/(2 cos(pi/2m)) for odd m and 0.5 for even m, times 0.95 margin.
- The machine maps exactly onto the 48-leg T03 equivalent (same total VA, turns scaled). Per-leg current = I_eq x 48 VMAX / (L V_leg). For m = 3 this is 266.1 A for every N.
- Loss: Enes's `calculate()` from `epc2361_loss.py`, reused with per-class parameters swapped:
  - R_DS from the CSV (max/typ ratio as EPC2361);
  - Q_oss scaled to V_module as V^0.5;
  - **gate charges Q_g, Q_gd, Q_gs2, Q_gs(th) scaled with Q_oss (assumption, needs datasheets)**;
  - EPC2361's R_DS(T) curve and thermal model kept.
  - Paralleling: n_par = ceil(I_leg,max / I_dev,max), with I_dev,max = 40 A x sqrt(R_EPC2361 / R_dev), i.e. equal per-device conduction loss to Enes's default point. Leg loss = n_par x calculate(I_leg / n_par).
- Device area is not computed: package dimensions are not in the local data.
- "Start" = inverter loss at I_max. Cruise = loss at the cruise current from the T03b/T03d chain.

### Pole-changing IM per design
- T03 geometry: R = 165 mm, 25 mm yoke, same copper.
- Q, pitch, k_w and sigma_diff come from the winding.
- Turns are set so N_leg k_w in the high-pole mode equals T03 (same EMF per volt).
- T03b realistic losses, T03d friction/windage (gap-windage bug fixed: coefficients 0.515/0.0325), single-stage gear at G = 9.80.
- Gear model: the **EU 2017/2400** regulatory baseline (SR axle T_d0 = 70 + 20 i, eta 0.98; helical 0.986, EU2017regulation). certified_like is also reported.
- Fixed-pole baseline with the same N: T03b fixed 2p=4, either (a) at its free gear 17.3 with the same inverter, or (b) at G = 9.80 with the inverter scaled x1.74 for the 12 % start.

### H05 (cell parking)
- SPB modules are in series on the DC side, so parking k modules raises the rest to 1200/(N - k). That is allowed only up to 0.80 V_class.
- Active coil groups carry N/(N - k) more current for the same torque.
- Also screened: shedding parallel devices inside each switch position.
- H04 comparison is like-for-like:
  - Pairs 8/4 and 12/4 per m, N closest to 16, practical Q, constant module power.
  - Turns are set so N_leg k_w in the high-pole mode equals T03. Peak torque per converter kVA (= per ampere-turn) is therefore equal by construction for 8/4.
  - The m effect shows up through differential leakage, the extra 3:1 pairs and the pole-phase state count.
- Slot-leakage sensitivity (R01 pending, simulator has 2.0-2.3x our slot leakage):
  - Method: `--sens_leakage2x` reruns key designs with lam_slot_self and lam_slot_mut x2.
  - Output: `results/sensitivity_slot_leakage_2x.json`; flags are written into every screen and the master (`slot_leakage_2x_sensitivity`).
  - 2x slot leakage raises total stator leakage by +32-37 % (m = 3) and +56-60 % (m = 5).
  - Not sensitive: peak torque, start grade and the fixed-baseline kVA factor (all current-limited, 0 %); cruise efficiency (< 0.15 pt).
  - Sensitive (voltage/breakdown-limited): P at 90 km/h -6 % (m = 3) to -13 % (m = 5 12/4), crossover -7 to -10 %, CPSR -6 to -11 %.
- The T03d gap-windage bug fix (2x) and the EU2017 gear variant were applied to `drivetrain_losses.py` and its JSON was regenerated before T08 ran.

## H10 - series-stack cell power balance (gap-loop screen) {#h10}

Script: `02_analytics/screen_H10.py` -> `results/screen_H10.json`. The short summary is in the JSON field `summary_text`; no separate .md was written.

### Model
- Series stack: C dV_j/dt = I_dc - P_j/V_j.
  - Average imbalance gives drift dP/(V C).
  - Pulsation P~ at f gives ripple P~/(2 pi f V C).
- Module power for spatial orders a (voltage) and b (current), m legs, c coils per leg, interleaved modules:
  - The sum term (f_a + f_b) survives iff m | (a+b)/c.
  - The difference term survives iff m | (a-b)/c.
  - Amplitude is m V_a I_b. Checked in the time domain: m = 3 gives 3, m = 5/7 give 0, m = 6 gives 6.
  - With a = b at one frequency this reduces to the T08 condition (iii).
- Allowed ripple: +/-5 % of V_module (3.75 V at 75 V).

### Cell capacitance (source)
- Rev B load board BOM (`../PCB-Design/hardware/spb-bb-revb-load/fab/spb-bb-revb-load-bom.csv`): 40 x 1 uF + 20 x 22 uF, 100 V X7S, giving 480 uF nominal per board.
- Boards per module = 6 (3 legs x 2 parallel blocks): assumption from the SPB reference "2 x 150 kW blocks per leg".
- `PCB-Design/docs/capacitor-selection-p1.md` states that no DC-bias-retained value is verified, so the range used is:
  - 0.35 retention (worst case) -> 1.0 mF per module;
  - nominal -> 2.88 mF per module.
- No external bulk link is defined yet.

### Magnitudes used
- IM handover: simulator best schedule (`03_simulation/results/im_pole_transition.json`), steady states before/after, rms per coil, worst-case alignment, 2100 rpm.
- WRSM k-sweep: simulator I_rms_max. The non-loaded order's EMF is assumed to be 0.5 V_max at mid-sweep.
- WRSM steady space harmonics: simulator circulating-current table, with an assumed fundamental of 120 A.
- H03 injection: the other analyst's `screen_H03.json` (order 8, I_inj = 0.15 I_max), with P_field = 4 kW spread over 48 legs.
- Balancing knob: same-frequency order b with m | (p-b)/c. dP = m V I_b per module, with zero sum over modules. Copper loss uses R = 2.16 mOhm per leg.

## H11 / H11s - iteration 2 (crossfade correction, cost table, post-bypass, pulsation-constrained handover) {#h11}

Script: `02_analytics/screen_H11.py`.
- Output: `results/screen_H11.json`.
- It also writes an `iteration2_correction` block into `results/screen_H10.json`. Rerunning screen_H10.py drops that block; screen_H11.py reproduces it.

### Two-mode transition model
- Per mode: rotor-flux-oriented dynamics tau_r dpsi/dt = L_m i_d - psi.
- Parameters: T03 pole-changing IM at 300 kW (fair_baselines.json), tau_r = 0.48 s (2p8) and 1.46 s (2p4), I_max = 266 A.
- Current loops are first order with 1 ms. Linear magnetics: no saturation intermodulation (that is the simulator's MEC task).
- Constraints: peak-sum current |i8| + |i4| <= I_max; peak-sum voltage checked against 29.09 V.
- Cell pulsation: P_x = 3 (|v8||i4| + |v4||i8|) at f8 + f4 (210 Hz at 2100 rpm). Ripple = P_x / (2 pi f V C), V = 75 V.
- Cases: 2100 rpm; flat 248 Nm and 2 % grade 677 Nm (as in the simulator); C = 2.9 / 1.0 mF; ripple limit +/-10 % or +/-5 %.

### H11s schedule
1. Ramp the 2p8 torque current to 0 in 20 ms.
2. Demagnetise with i_d8 = -I_max until psi8 < 2 %. This is a single order, so there is no cross pulsation.
3. Build 2p4 flux with i_d4 up to the remaining current budget. The 2p4 current magnitude is limited online by 3 (v8 i4 + v4 i8) <= P_allow(f, C, limit).
4. Torque current starts once psi4 > 5 %.

### Crossfade
- Ideal x(1-x) envelope: factor 0.25, 2.12 kW.
- Naive current crossfade in the model: factor 1.39 (flat) / 1.50 (grade), because the flux lags the current. This is reported separately and labelled.

### Cost table (assumed, unverified prices; no web access in this run)
Unit prices assumed:
- EPC2361 6 EUR.
- Gate-driver channel 3 EUR; isolated supply channel 6 EUR.
- Current sensor 4 EUR per leg; PCB and assembly 15 EUR per leg; 60 g and 40 cm3 per leg.
- m = 5 winding extra: 300 EUR.

Capacitors (typical catalogue values, assumed):

| Type | C | Price | Ripple rating | ESR | Rth | Life |
|---|---|---|---|---|---|---|
| Al electrolytic 100 V | 1 mF (18 x 40 mm) | 2 EUR | 2.5 A at 120 Hz, x1.3 at 400 Hz | 45 mOhm | 15 K/W | 5000 h at 105 C |
| Hybrid polymer 100 V | 330 uF | 1.6 EUR | 1.2 A at low frequency | 60 mOhm | - | 10000 h at 125 C |
| MLCC 22 uF 100 V X7S | 0.35 retention | 0.8 EUR | - | - | - | - |

- Ambient 85 C; lifetime target 25,000 h. Life is Arrhenius x2 per 10 K below rating.
- m = 5 extras come from module_count_sweep.inverter_design (N = 16): 80 vs 48 legs and 800 vs 672 devices.

### Post-bypass
- One or two module DC ports are bypassed and their coil groups left unpowered (fixed wiring, so the remaining coils cannot be regrouped). MMF is computed numerically with each pair's own coil pitch.
- Cell voltage limit is 0.80 V_class.
- First-order argument for power balance: the remaining modules are unchanged and balanced. The hole fields are at the same frequency and reactive with respect to the main current, so they cause no average imbalance and no pulsation.

## E01-P - bench-test predictions for the pulsation law {#e01}

Script: `02_analytics/E01_predictions.py` -> `results/E01_predictions.json`.
- `pulsation_from_phasors()` takes measured complex peak FFT phasors per leg (pole voltage and current at f_a and f_b) and returns P and dV at f_a + f_b and |f_a - f_b|. No symmetry is assumed.
- Pole voltages relative to DC- are fine: zero-sequence cancels because the currents sum to zero.

Test conventions (assumed):
- I_a and I_b are PEAK amplitudes (as in the plan's reference expression).
- Signed orders: leg k lags k 2 pi a / m.
- Load: star RL per leg, isolated neutral, 1-2 Ohm and 2-5 mH.
- V_dc 48 / 75 / 100 V.
- C = 1 mF film nominal, with 0.5 / 2 / 4.7 mF parametric.

Ripple and current:
- Ripple assumes the source is decoupled at f: dV = P / (2 pi f V_dc C).
- Otherwise use |Z_C || Z_s|, or measure the capacitor current plus the source current against P / V_dc. This is a pitfall flagged to Enes.

Modulation limit (linear): V_pk sum <= V_dc / (2 cos(pi/2m)) for odd m, i.e. 0.577 V_dc for m = 3 and 0.526 V_dc for m = 5.

Sensitivities:
- Load imbalance: +/-5 % per-leg R and L (40 random draws plus an alternating worst case).
- Dead time: 100-1000 ns at f_sw = 20 kHz, V_sd = 1 V. A rejection fraction models how much of the dead-time error the current loop removes.
- Asymmetric dead time: +/-20 / 50 % per leg.
- Imperix PEB/B-Box specifics (dead time, f_sw, current-loop bandwidth) are not known here; Enes should replace them.

## R01 - adoption of the agreed geometry (data/machine_geometry.json) {#r01}

How to run: `SPB_GEOMETRY=data/machine_geometry.json` (or `--geometry` for torque_speed_envelope.py and module_count_sweep.py). The R01 values are applied once in `torque_speed_envelope.apply_agreed_geometry`, and every output gets the suffix `_R01`.

Values adopted:
- Slot leakage: the simulator's energy-method layered slot (liner 0.5, two layers, separator 1.0, top air 6.6, tip 1.5 mm over a 3 mm opening).
  - In my coil formula this gives lam_self = (top + bottom)/2 = 2.928 and lam_mut = 2.217, reproducing 39.5 / 28.5 uH exactly.
  - T03b candidate slots use the same layer stack, with layer height = (h_slot - 9.6 mm)/2.
- Air gap: g_eff = 1.076 mm (Carter only, no saturation factor).
- Flux caps:
  - B_yoke 1.45 T x stacking 0.95, applied as apparent density;
  - tooth tip 1.65 T x 0.95, i.e. an airgap equivalent of 0.914 T for the T03 slot.
  - Resulting caps are 50.8 / 41.7 mWb against the agreed 51.7 / 42.2 (-1.7 / -1.0 %).
- Rotor bar: lam_bar = 1.687.

Calibration (one factor each, from the T03 design, applied to every design):
- Differential leakage x1.149: the simulator's winding-function sum is about 15 % above my FFT sum, in both modes.
- Rotor leakage x1.025.
- After calibration the T03 design matches all agreed IM values within 0.3 %. fair_baselines re-refers the differential factor to its own finer MMF sum (x1.072).

Other R01 notes:
- H11s: the steady-state flux is now voltage-feasible including the R + j w sigma L drop (previously the 2 % grade case reached a 30.1 V peak-sum at R01 leakage).
- Not adopted: the WRSM/PMSM per-unit inputs (R01 WRSM reactances). See the WRSM/HESM note in `results/R01_deltas.json`.
- Iron masses with stacking factor and tapered teeth are not adopted (simulator: iron loss +/-5 %).

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

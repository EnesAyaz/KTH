# Analyst assumptions - T03c hybrid-excited synchronous machine (HESM) with SPB pole changing {#t03c}

- **Script:** `02_analytics/hesm_envelope.py` (add `--quick` for a coarse test run).
- **Output:** `results/hesm_envelope.json`; quick-look plot in `scratch/hesm_envelope_quicklook.png`.
- **Code reuse (read-only):** imports `torque_speed_envelope.py` at 300 kW and `fair_baselines.py`. It does not write any T03, T03b or T03d file.
- **Decisions used:**
  - D02: 300 kW.
  - D03: HESM as a fourth candidate.
  - D05: the module count N and the slot count Q are parameters. N = 16 is the reference.
- **No open decision blocks T03c.**

## Same basis as T03b
- **Inverter:** 29.09 V rms per coil, 266.1 A rms per leg, 372 kVA.
- **Stator:** the same 48-coil stator logic as T03, with R_out = 235 mm, L_stk = 360 mm and 62.9 kg of copper.
- **Vehicle:** the same vehicle as T03b, using the `../Drive Cycle` constants.
- **Gear rule:** the T03b rule (`fair_baselines.best_gear`): the highest P at 90 km/h, subject to the 12 % start and the 125 m/s tip speed (7234 rpm at R = 165 mm). The tip-speed limit is copied from the copper cage, and a wound salient rotor may be weaker.
  - Tie-break (new): the smallest G whose P at 90 km/h is within 0.5 % of the maximum. The synchronous machines have a flat P(G), so without it the chosen G jumps on grid noise.
  - In every feasible HESM case the rule ends at the start-torque bound, G = 10.8 (13.0 for the 38 mm yoke). The start grade is therefore 12.0 % for all cases.
- **Losses: the realistic T03b set, plus field and exciter loss:**
  - stator copper (DC, 120 C);
  - fundamental iron loss in teeth and yoke, using the design's own masses;
  - IEC 60034-2-1 stray-load allowance (3.98 kW at 300 kW), scaled (T/T_N)^2 with T_N = 300 kW / omega_base of the active mode;
  - SPB PWM ripple at 100 kHz (stator copper with k_ac = 5, plus tooth eddy loss), with L_hf = 0.5 x 2 L_sigma,s because there is no cage;
  - T03 friction/windage law (T03d will replace it in T07).
- **Field copper:** each rotor coil group (4 poles) carries at most 2 kW, i.e. half of the 4 kW WRSM field. The loss is 2 kW x i^2, where i is the coil current divided by its thermal-limit current.
- **Exciter:** one rectifier channel per group, using the P1 rectifier efficiency of 99 % at rated current and 87 % at 0.61/2.88 = 0.21 of rated.
  - It is fitted as P_loss = P_rated (k0 + k1 x) with k0 = 0.0058 and k1 = 0.0043. The fit is checked in `sanity_checks`.
  - The WPT link loss is excluded (rectifier only, as the brief specified).
- **PF:** circuit-consistent, PF = (T omega + P_cu,s) / (48 V I).
  - The simple-model sanity check uses the T03 definition instead.
- **Not included:**
  - rotor iron, pole-face and PM eddy losses (the T03b IMs also have no rotor iron loss, but their cage PWM loss was included);
  - PM temperature feedback;
  - inverter and gearbox losses;
  - demagnetisation checks.

## Rotor model (Conto2022hybrid generalised)
- **Poles and groups:** 8 salient poles, pole arc 0.7.
  - Group A = poles 0, 3, 4, 7 and keeps its polarity.
  - Group B = poles 1, 2, 5, 6 and is reversed. These are the T03 / P4 patterns.
- **Decomposition:** with pole amplitudes A and B (B > 0 meaning 8-pole polarity), the rotor field is A u_A + B u_B = (A+B)/2 P8 + (A-B)/2 P4.
  - 8-pole mode: A = B.
  - 4-pole mode: B = -A.
  - Off-balance states would leave a parasitic harmonic in the coils, so they are excluded from the envelopes and used only in the transition.
- **Amplitude unit:** amplitude 1 = the T03 WRSM rated field (B0 = 0.712 T pole face, psi = 0.85 pu in 8-pole mode).
- **PM share s** = the PM fraction of the rated 8-pole no-load flux.

  | s | PM | Field coils | Note |
  |---|---|---|---|
  | 0 | none | both groups | the T03 WRSM |
  | 0 < s < 0.5 | group A, m_A = 2s | both groups | |
  | 0.5 | group A, m_A = 1 | group B only | Conto rule: PM flux = field flux |
  | > 0.5 | group A m_A = 1, plus group B m_B = 2s - 1 (8-pole polarity) | group B, which must override its PM in 4-pole mode | |

- **PM sizing:** NdFeB at about 120 C, Br = 1.10 T, mu_r = 1.05, leakage factor 0.85. The thickness is h = B mu_r g_eff / (k Br - B). This gives 0.84 mm at s = 0.25 and 4.4 mm at s = 0.5. The PM mass is 0.8 kg (s = 0.25), 4.3 kg (s = 0.5) and 5.4 kg (s = 0.8).
- **The PM sits in the d-axis path of its poles (series magnetic circuit):**
  - A coil on a PM pole drives flux through g + h/mu_r. Its amplitude per unit coil MMF is therefore kappa = g/(g + h/mu_r).
  - The magnetising part of the armature L_d is scaled by the mean pole permeance, 0.5 (kappa_A + kappa_B): 0.81 at s = 0.25 and 0.62 at s = 0.5. This is applied in both modes.
  - L_q is unchanged.
- **Inductances:** as in T03. The magnetising part scales by L_m(p, mapping) / L_m(T03, 2p = 8), i.e. by k_w^2/p^2, and the leakage is recomputed for each stator and mapping.
- **Field ranges:**
  - Group A coil: unipolar (P2 uses a unipolar channel for the fixed group). Sensitivity `If_weakening_bipolarA` lets it buck the PM; demagnetisation risk is not checked.
  - Group B coil: bipolar.
  - Mode caps: 8-pole amplitude <= stator tooth/gap/yoke cap (1.087 on the T03 stator). 4-pole amplitude <= stator-yoke cap (0.655 on the T03 stator) and <= rotor-yoke margin (2.0, as in T03).
- **Control policies:**
  - `If_weakening` (WRSM-style): the field is free inside its range, with free I_d <= 0.
  - `fixed_field`: the field is at the maximum of each mode, and I_d does all the flux weakening.

## Stators (same R_out, L_stk and copper)
- **`T03_yoke25mm`:** the T03 stator. This is the reference, and s = 0 reproduces T03.
- **`yoke38mm_4pole_capable`:** a 38 mm yoke, so that the 4-pole mode can carry amplitude 1 (needed for the Conto rule, s = 0.5).
  - The slots become 32 mm deep and 12.8 mm wide (copper volume fixed, via `fair_baselines.make_design`).
  - The teeth narrow to 8.8 mm, so the tooth cap (1.65 T) limits the 8-pole amplitude to 0.83. This is the cost of a 4-pole-capable yoke inside the same frame.

## SPB vs Conto two-inverter supply (D05: N and Q are parameters)
- **Coil frame:** every leg drives c = Q/(3N) coils in series.
  - The per-module voltage 1200/N and the c coils cancel, so with N_c = 3 and the same copper the per-unit machine is the same for every N.
  - N enters only through:
    - the series grouping: k_d(p) for each pole mode, and the differential leakage;
    - the device voltage class (1200/N per module; T08);
    - the zero-sequence filtering of rotor harmonics in each module (T03: the 12-pole rotor harmonic is zero-sequence for N = 16).
- **Balanced modules:** every module is kept a balanced three-phase set (offset phi_j and sequence +/- chosen for each module). For Conto's feed this is "reverse inverter 2, swap B and C".
- **Winding factors (48 slots, y = 7):**
  - SPB N = 16: 0.966 (2p = 8) and 0.793 (2p = 4).
  - Conto feed (N = 2, odd/even pole pairs on the two inverters): 0.933 and 0.507, with sigma_diff = 0.18 in 4-pole mode (backward wave).
  - A generic SPB N = 2 block grouping is worse (0.69 / 0.38). Conto's belt grouping is the right N = 2 layout.
  - Numerical MMF (forward/backward split) agrees with the analytic value to 1e-4.
- **How the SPB generalises Conto:**
  - Conto = N = 2 with a fixed 0/180 deg shift between the two groups.
  - The SPB sets each coil's phase as p 2 pi k/Q, so any p not divisible by 3 is available, with k_d = 1 for N = 16.
  - It can carry both rotor-field harmonics (p = 4 and p = 2) at the same time during the rotor transition.
- **N = 2 result:** reported next to N = 16 for s = 0, 0.25 and 0.5.
  - Peak torque falls from 2513 to 2427 Nm and G rises from 10.8 to 11.2.
  - The 4-pole mode is weaker still (k_w 0.507).
  - The verdict does not change.

## Pole transition (field part)
- **Time constant:** tau_f of group B = 45 ms x kappa_B (T03 stored-energy estimate, saturation ignored).
  - Forced reversal with 3x field voltage: about 44-49 ms including 20 ms blanking.
  - P1 sequence (free-wheel, blanking, unforced build-up): 0.29 s.
- **Torque floor (lower bound):** during the reversal, group B sweeps from +c8 to -c4 while group A (PM and coil) keeps its polarity. The rotor then has both P8 and P4 components.
  - The floor puts all current and voltage into the better harmonic and subtracts the EMF of the unused harmonic from the voltage budget.
  - At 2000 rpm: minimum 19-21 % of the pre-shift torque, mean 49-53 %, for any s.
  - The torque gap is therefore not a full gap. **This comes from group A keeping its polarity, not from the PM: a WRSM that holds group A energised gets the same floor (s = 0: 19 % / 49 %).** The PM only removes the need to excite group A.

## Sanity checks (JSON `sanity_checks`)
- **s = 0 on the T03 stator against `torque_speed_envelope_300kW.json` (WRSM):**
  - Free I_d: T_peak, CPSR and P at 4500 rpm in 2p = 8 and 2p = 4.
  - I_d = 0: P at 4500 rpm.
  - Cruise efficiency and PF at G = 9.80 with the T03 loss set.
  - Maximum relative error: 6e-5.
- **Winding:** N = 16 numerical k_w equals the analytic value. This is the p = const reduction to T03.
- **Exciter fit:** reproduces 99 % and 87 %.

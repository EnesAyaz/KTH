# H07 review: hybrid-excited machine (PM + reversible field coils) makes SPB pole changing pay at truck scale

Gap-critic, gap-loop iteration 1, step 4, 2026-11-02.
Inputs: `01_literature/novelty_H07.md`; `02_analytics/results/hesm_envelope.json` (sweep, pole_transition, sanity_checks); `02_analytics/assumptions_hesm.md`; `03_simulation/validation.md` (flag 2, WRSM reactances; section 2).

## Verdict: **kill** (the HESM survives only as one rotor variant inside H09; the s = 0.25 PM-assist result is a side result, not pole changing). Weighted score **2.4 / 5**.

| Criterion | Score | Reason |
|---|---|---|
| Novelty (0.30) | 3 | HESM pole changing with field-coil reversal and a two-inverter half-phase stator is published at 0.5 kW (Conto2022hybrid; Bratke2022 with stator cage), and that two-inverter feed is an N = 2 SPB; truck scale and N = 16 are new, but "same idea, bigger" is weak novelty. |
| Value (0.30) | 1 | Negative: no crossover (2p=4 never beats 2p=8) for any PM share s = 0-0.8, either stator (25 mm or 38 mm yoke), any field policy, N = 16 or Conto N = 2; the best design (s = 0.25, 25 mm yoke, 97.38 % cruise, 338 kW at 90 km/h) runs fixed 8-pole, so pole changing adds exactly 0. |
| Feasibility (0.20) | 3 | Buildable for s <= 0.33 (0.84 mm NdFeB, 0.8 kg); s > 0.5 cannot reach 4-pole within copper, s >= 0.7 cannot reach 90 km/h, group-B PM override and group-A bucking have unchecked demagnetisation risk, and s = 0.25 already has an uncontrolled-generation EMF of 1.40 V_max at 90 km/h. |
| Enes fit (0.10) | 4 | Builds on P1/P2/P5 bipolar excitation (WPT/OPT, group A/B channels) and the SPB stator. |
| Paper fit (0.10) | 2 | A negative result; publishable at most as a paragraph ("why HESM does not rescue synchronous pole changing: yoke cap") in a larger paper. |

Weighted: 0.3 x 3 + 0.3 x 1 + 0.2 x 3 + 0.1 x 4 + 0.1 x 2 = **2.4**. Value at 1 alone blocks promotion.

## Strongest kill argument (the reviewer comment)
> "The 4-pole mode carries twice the flux per pole through the stator yoke, so in a stator sized for 8 poles the 4-pole flux is capped at 0.655 of rated (25 mm yoke). The PM must fit under that cap in the 4-pole mode, which limits the PM share to s <= 0.33, and below that share the machine is simply a PM-assisted WRSM that is best left in 8-pole mode. The authors' own sweep confirms there is no PM share, stator or control policy with any pole-changing benefit. The one case where 2p=4 is selected at cruise (38 mm yoke, s = 0.4: 96.35 % vs 95.24 % in fixed 8-pole) beats only its own handicapped baseline; the fixed-8-pole design on the standard stator reaches 97.38 %, a full point higher."

Supporting points:
1. **The negative result is robust to the model disagreement, in the direction that matters.** The R01 issues (WRSM L_d ~4x larger in the simulator, slot leakage 2.3x) change the size of the 2p=4 deficit (analyst 0.43-0.45 of 2p=8 torque; simulator config B 0.72-0.78 above 2100 rpm) but neither model finds a crossover at equal turns, and the binding limit (stator-yoke flux, 2x flux per pole at half the pole count) is first-principles geometry, not a fitted reactance. I score Value 1 rather than 2 for that reason: model error does not open a door here.
2. **Fair baseline check: passed, and it kills the claim.** Same stator, copper, inverter (372 kVA), gear rule (G = 10.8, 12 % start for all cases), loss set incl. field + exciter. The fixed-pole HESM with its own best s is the baseline, and it wins.
3. **The transition is no better than WRSM.** Torque floor 19-21 % min / 49-53 % mean during reversal for every s; it comes from group A keeping polarity, not from the PM (s = 0 gives the same 19 % / 49 %).
4. **Conto's own numbers point the same way.** Conto2022hybrid: 76 % / 67 % efficiency, 4-pole mode at k_w 0.62 (0.507 on our 48-slot stator); T03c N = 2 Conto feed at s = 0.5 reaches 93.6 % cruise with no I_f weakening, 3.8 pt below the best fixed HESM.

## What would save it
Only a change that lifts the yoke cap or the turns ratio, i.e. a different hypothesis:
- **Turns per mode (H09):** T04 shows halving the effective turns in 2p=4 flips the WRSM to 1.42x torque at 4500 rpm. The yoke cap still binds the 4-pole flux, so the HESM gain would come only from the turns change, and the PM then just reduces field loss. Add s = 0.25 as one rotor row in the H09 screen; if it does not beat the s = 0 WRSM row there, close H07 for good.
- A 4-pole-native stator (yoke sized for 4 poles, 8-pole as the weak mode) was effectively tried with the 38 mm yoke and loses 15 % of the power at 90 km/h (245 vs 288 kW at s = 0) and 0.45-0.5 pt of cruise efficiency because the teeth narrow; not worth repeating.

## Spin-off ideas
1. **Merge into H09** as a rotor variant (s = 0 WRSM vs s = 0.25 HESM under the SPB-native turns change), not as a separate hypothesis.
2. **Side result, not pole changing (park, as the leader already noted):** "SPB + PM-assisted WRSM with s ~ 0.25 gives WRSM-class cruise (97.38 % vs 96.94 % machine-only) with about half the field + exciter loss (516 W vs 1179 W at 85 km/h) and PF 0.98." Kill check before anyone spends time on it: the 1.40 V_max uncontrolled-generation EMF at 90 km/h must be shown safe for a 75 V GaN stack (field de-excitation alone does not remove the PM part), and the gain must survive R01 reactances and the missing PM/pole-face eddy loss.

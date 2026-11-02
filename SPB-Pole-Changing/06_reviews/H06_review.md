# H06 review: torque-gap-free pole transition through per-module control

Gap-critic, gap-loop iteration 1, step 4, 2026-11-02.
Inputs: `01_literature/novelty_H06.md`; `03_simulation/validation.md` (flags; section 3); `03_simulation/results/im_pole_transition.json`, `wrsm_pole_transition.json`, `wrsm_pole_transition_ksweep.json`; `02_analytics/assumptions_hesm.md` (transition floor); `board/prior_work.md` (P1, P4, P5).

## Verdict: **kill as stated; merge the synchronous-rotor restatement into H09** (as its transition chapter, gated by H10). Weighted score **2.0 / 5**.

| Criterion | Score | Reason |
|---|---|---|
| Novelty (0.30) | 2 | For the IM the claim is published by three groups with hardware: Libbos2025bumpless (TTE, bumpless, flux transition 200 ms, torque within ripple, 18-leg), Wu2025minimum (KTH, 10 % dip vs 133 % hard switch), Haq2024ripple; the synchronous-rotor version is not published by others, but its mechanism (gradual coil-group k-sweep [1 k -k -1]) is Enes's own P4 and the free-wheel sequence is P1, so the remaining step is incremental. |
| Value (0.30) | 1 | Our own IM result is **worse than the published state of the art** (flat road: min 80 % torque, < 90 % for 56 ms; 2 % grade: < 90 % for 0.5 s with a -62 Nm reversal, vs Wu2025minimum 10 % dip), and the synchronous transition that does look gap-free is the transition into a 4-pole mode that has **no value** for WRSM/HESM (T03, T03c, P5, T04 at equal turns). |
| Feasibility (0.20) | 2 | The gap-free WRSM result rests on config B (air gap x4, field MMF x4, never checked against the 4 kW field-copper budget), a quasi-static stator, no field-damping by stator currents and no solid-rotor eddy currents; with the realistic gap (config A) the 2p=4 mode cannot carry the 2 % grade load at all (294 Nm available vs 677 Nm needed). |
| Enes fit (0.10) | 4 | Direct continuation of P1 (bipolar WPT exciter, free-wheel sequence), P4 (k-sweep patterns) and P5 (677 ms reversal), on SPB hardware. |
| Paper fit (0.10) | 3 | "SPB dual-mode stator drive bridges the rotor field reversal" is a clean TTE/ECCE story, but only if the pole change it bridges is worth making. |

Weighted: 0.3 x 2 + 0.3 x 1 + 0.2 x 2 + 0.1 x 4 + 0.1 x 3 = **2.0**. Three criteria below 3.

## Strongest kill argument (the reviewer comment)
> "The transition is smooth, but why change poles at all? The authors' own steady-state analysis shows that the wound-rotor machine gains no torque, speed range or cruise efficiency in the 4-pole mode at equal turns (2p=4 delivers 0.43-0.78 of the 2p=8 torque at every speed, no crossover in either model). A torque-gap-free transition into a mode the machine should never enter is not a contribution. For the induction machine, where the pole change does pay, bumpless transitions are already demonstrated in hardware (Libbos et al., TTE 2025; Wu and Peretti, TEC 2025), and the proposed controller is worse than both (0.5 s below 90 % torque with a torque reversal on a 2 % grade)."

Supporting points, quantitative:
1. **IM: per-module control is not the differentiator, and our controller is behind.** The gap is set by the voltage budget while the residual 2p=8 rotor flux (tau_r ~ 0.5 s) still induces 18-35 V of the 41 V peak at 2100 rpm (validation.md section 3). Any multi-leg drive faces the same physics; Libbos/Wu solved it with droop / minimum-dip schedules. Our best of 27 schedules leaves a 256 Nm s torque deficit at 2 % grade. The 2.3x slot-leakage disagreement (flag 1) moves the voltage budget further against us: more leakage, more voltage per ampere during the hand-over, longer gap.
2. **WRSM: the gap-free result is a model artefact until three things are checked.**
   - Config B is a comparison device: x4 field MMF per pole (about 2.95 kA-turns). With unchanged field copper, field loss scales with MMF squared, i.e. about 16x the 4 kW budget (my estimate; the simulator states it did not check this). The forced 3x field voltage on top of that is not costed either.
   - Stator quasi-static, no field-circuit damping by the stator currents and no solid-rotor eddy currents: both slow the field reversal, and the 2 % grade margin is only about 8 % (620 of 677 Nm).
   - tau_f is inconsistent between models: analyst 45 ms (1.3 mm gap) vs simulator 0.17-0.21 s (gap consistent with the analyst's L_d). R01 must settle this before any transition time is quoted. P5 (40 kW design) already reports 677 ms to 95 %.
3. **Series stack (H10) is ignored.** The gap-free WRSM transition and the k-sweep run the 48 coils in two spatial modes at once (peak stator current 84 % of I_max). Whether every series-stacked module then carries the same average DC power is not checked; if not, the cell capacitors drift during exactly the 0.13-0.4 s that the transition lasts. This is the one place where SPB differs from the UIUC/KTH single-bus drives, and it is not analysed.
4. **HESM gives no help:** the T03c floor (19-21 % min, 49-53 % mean torque during reversal) comes from the fixed-polarity group A, not from the PM; a WRSM holding group A gets the same floor.

## What would save it
Value is the weakest score, and it cannot be raised inside H06: it depends entirely on whether the synchronous 4-pole mode becomes worth entering. T04 shows that it does when the low-pole mode gets about half the effective turns (WRSM 2p=4 at 1.42x the 2p=8 torque at 4500 rpm, crossover 4250 rpm). That is **H09**. If H09 survives, the transition analysis becomes its necessary second half ("the turns-and-poles change is gap-free on SPB with a bounded cell-voltage excursion"), and the synchronous-rotor restatement then scores roughly N 3 / V 3 / F 3. One concrete analysis to run then: the k-sweep with the H09 turns change, on the reconciled reactances (R01), with field damping and a per-module DC power trace (H10), at 2 % grade.

## Spin-off ideas
1. **H06s (merge into H09):** "On an SPB, a synchronous-rotor pole-and-turns change (rotor k-sweep [1 k -k -1] + stator driving both spatial modes) keeps torque >= 90 % on a 2 % grade with a field forcing ratio <= 3 and a field-copper budget the rotor can carry." Screening metric: min torque / time below 90 % vs forcing ratio, with R01 reactances and damping. Only meaningful if H09 shows a mode worth entering.
2. **Transition as an H10 test case (not a new hypothesis):** peak per-module DC-power imbalance and cell-capacitor excursion during the IM 8->4 hand-over and the WRSM k-sweep. If the excursion is large, SPB needs a transition schedule the single-bus literature does not; that would be the SPB-specific transition result.

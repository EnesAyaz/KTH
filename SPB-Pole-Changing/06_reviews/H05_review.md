# H05 review: pole changing lowers cruise voltage, so SPB parks cells (joint pole-and-cell scheduling)

Gap-critic, gap-loop iteration 1, step 4, 2026-11-02.
Inputs: `01_literature/novelty_H05.md`; `01_literature/gap_matrix.md` (stack / isolated-neutral / shared-bus columns); `02_analytics/results/screen_H05.json` (N16_m3_Q48_8/4, N8_m3_Q48_8/4); `02_analytics/results/screen_H02.json` (system loss for scale); `02_analytics/assumptions.md#t08` (H05 section); own quick search (below).

## Verdict: **kill** (confirmed). Weighted score **1.7 / 5**.

| Criterion | Score | Reason |
|---|---|---|
| Novelty (0.30) | 2 | lit-scout rated it "new", but online isolation/reactivation of one inverter in a stacked polyphase bridge converter is published (Verkroost et al., IET Electric Power Applications 2023: two extra unidirectional switches per inverter, reconfiguration in 100 ms without torque interruption, 4 kW modular axial-flux PMSM). Only the coupling to pole mode is unpublished, and that coupling has no effect (below). |
| Value (0.30) | 1 | Parking a series cell always raises loss: N = 16, +158 W at 85 km/h (2p4), +66 to +74 W at 60 km/h; up to +2 kW elsewhere in the sweep. The parallel-device shedding that does help (-28 W at 85 km/h, -92 to -102 W at 60 km/h) is under 0.7 % of the 14.7-23.7 kW system loss and does not depend on the pole mode. |
| Feasibility (0.20) | 2 | Needs DC bypass switches the SPB does not have; voltage headroom allows only k = 1 parked cell at N = 16 (80 V on a 100 V class at 0.80 derating) and k = 0 at N = 8. |
| Enes fit (0.10) | 3 | Uses SPB and the GaN loss model, but adds bypass hardware to his module. |
| Paper fit (0.10) | 1 | A negative result; at most a paragraph. |

Weighted: 0.3 x 2 + 0.3 x 1 + 0.2 x 2 + 0.1 x 3 + 0.1 x 1 = **1.7**.

## Strongest kill argument (the reviewer comment)
> "The premise confuses voltage need with cell need. In a series-stacked converter the DC link stays at 1200 V; a lower machine voltage only lowers the modulation index. Removing a cell does not reduce the motor current, it concentrates the same current on fewer coil groups (copper x N/(N-k)) and raises the remaining cells to 1200/(N-k), so conduction rises and the total switched voltage, hence switching loss, is unchanged. The authors' own screen shows parking always increases loss, and the bypass needed to park a cell online in a stacked polyphase bridge is already published (Verkroost et al., 2023)."

Supporting points:
1. **Physics, not tuning, kills it.** At cruise the SPB inverter loss is conduction-dominated and set by current; voltage reduction from pole changing appears as lower modulation index, not as idle cells. The screen's +158 W (85 km/h) splits into +117 W stator copper (N/(N-1) current concentration) and +41 W inverter; there is no regime in the sweep where parking wins, and the result is leakage-insensitive (limits set by device voltage rating).
2. **The joint (pole, cell) schedule has nothing to schedule.** At 60 km/h, 2p4 vs 2p8 changes inverter loss by 23 W (539 vs 562 W); device shedding gives the same ~100 W in either mode (437 W in 2p4 vs 469 W in 2p8 at 3 of 7 devices). The pole decision and the device decision are separable.
3. **Device shedding is not SPB- or pole-specific.** Shedding paralleled devices (or phase shedding in paralleled converters) at light load is a generic technique; at 85 km/h the optimum is 5 of 7 devices for -3.7 %, which is within the gate-charge scaling assumption of the loss model.

## What would save it
Nothing that keeps the cell-parking claim. The only defensible content is the **one-cell voltage headroom at N = 16** (1200/15 = 80 V within 0.80 x 100 V), which is a fault-tolerance property, not an efficiency one.

## Spin-off ideas
1. **Post-bypass operation of a pole-changing SPB (fold into H08 and the H01+H10 merge).** With a Verkroost-type bypass, N = 16 can lose one cell and keep running at 80 V per cell. But the bypassed cell removes one isolated coil group, and with N = 15, m = 3, Q = 48 the coils-per-leg c = Q/(mN) is no longer an integer, so the H01 rule no longer guarantees balanced modes. Which pole/phase patterns, with what k_w, torque derating and cell power balance, remain after one bypass? This is SPB-specific (series stack + isolated neutrals + pole patterns), quantifiable with the existing enumeration, and testable on Enes's hardware. It is a section of the merged H01/H10 paper or the core of H08, not a separate hypothesis.
2. (Side result, not pole changing) **GaN parallel-device shedding in SPB at light load**: -16 to -19 % inverter loss at 60 km/h. Worth one figure in an SPB hardware paper if the gate-charge scaling is confirmed with datasheets; do not carry it in the gap loop.

## Note for lit-scout
Add Verkroost2023 (IET EPA, dc-bus reconfiguration in SPB), Verkroost2024 (IET PE, consensus balancing in SPB) and Che2014 (IEEE TIE 61(1), series-connected machine-side converters, doi 10.1109/TIE.2013.2248338) to `refs.bib` and the gap matrix; they move H05 from "new" to "partly done" and bear directly on H10's novelty.

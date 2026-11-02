# novelty_H10.md  H10: series-stack power-balance constraint under pole/phase modes, transitions, unequal coil-group loading
Gap-loop, lit-scout, 2026-11-02, after importing the SPB lineage from Review-Paper-SPB/ref.bib. All keys below are in refs.bib with notes in papers/.

## Verdict
**Partly done. The balance mechanism is published; its application to mode changes is not found.** Stacked-bridge DC-split instability in motoring, balancing control, unequal power sharing between winding sets and the control that keeps the DC split stable under it are all published (Ghent, KTH, Levi). I found no paper that derives the per-cell power imbalance or the admissible mode set when the pole or phase mode changes, in a transition, or for an unequal coil-group pattern. The novelty is therefore narrowed to the mode-dependent (c, m, p) imbalance rule and the balancing headroom per mode, not the balancing itself.

## 1. Closest papers (Verkroost2024PowerDistribution read in full; others abstract level)
1. **Verkroost2024PowerDistribution** (TEC 2024, Ghent) is the closest. A 15-phase (five three-phase agents) axial-flux PMSM in an SPB; the agents may carry unequal torque (sharing coefficients), and a consensus controller keeps the total DC-bus voltage stably distributed even if agents are not identical; motoring only; 4 kW. Did not: change pole or phase mode, treat transitions, or give a rule for which sharing patterns the DC split tolerates beyond control stability.
2. **Zoric2017voltage** (ISIE 2017, Levi): 9-phase machine, three isolated neutrals, three cascaded VSIs; any imbalance in machine phases or inverters causes unequal power sharing and unequal DC voltages; balancing controller. Nearest hardware match to SPB, and it states the mechanism H10 depends on. Did not: pole or phase mode change.
3. **Zoric2018arbitrary / Subotic2019active** (Levi): power sharing among winding sets by imposing x-y fundamental currents with flux and average torque unchanged; sets do not share power as they share torque. Gives the actuation a mode scheduler could use to equalise cell power. Did not: apply it to series-stacked DC links or mode changes.
4. **Che2014SeriesConnected** (TIE 2014, Levi): asymmetrical six-phase IM, two series-connected converters, DC mid-point balancing with the extra multiphase degrees of freedom. Fixed 6-phase mode.
5. **Nikouie2017Stability, Ni2025SeriesDCLinkStability, Verkroost2024VoltageBalance, Jin2018Distributed, Wu2020ActiveBalancing, OpenEndWindingDrive**: stability of the DC split (unstable in motoring, stable in generating) and balancing controllers, all for a fixed mode and balanced or slightly unbalanced hardware.

## 2. Question-by-question
- **Cell power balance under a change of pole or phase mode?** Not found. Closest: Zoric2017voltage and Verkroost2024PowerDistribution (unequal loading at fixed mode).
- **Unequal coil-group loading?** Yes, published for a fixed mode (Verkroost2024PowerDistribution, Zoric2018arbitrary, Subotic2019active).

## 3. What a reviewer would cite against H10
Verkroost2024PowerDistribution for "unequal loading is controllable in an SPB", Zoric2017voltage for "unequal power sharing causes unequal voltages and a controller fixes it", Che2014SeriesConnected for "extra degrees of freedom rebalance a series stack".

## 4. New refs
None beyond the keys merged on 2026-11-02 (SPB lineage import plus Zoric2017voltage, Zoric2018arbitrary, Subotic2019active, Nikouie2016operation, Che2014SeriesConnected).

## 5. Coverage and caveats
Crossref searched for: series-connected DC link multiphase with pole-phase modulation; power sharing between winding sets; post-fault bypass in stacked bridges; variable pole with series converters. IEEE full texts of Zoric, Che and Subotic were not read (abstract level); the Ghent IET papers were not readable (Wiley blocked), the TEC paper was read in full. The "no paper on mode change" conclusion is unproven for non-indexed literature.

# novelty_H09.md  H09: SPB-native change of effective turns per pole mode (synchronous pole changing)
Gap-loop iteration 1, step 2. Author: lit-scout, 2026-11-02. Existing keys are in `refs.bib`; new keys are in the last section (not merged by me).

## Verdict
**Partly done.** Changing effective turns by winding reconfiguration is known and the two-inverter half-phase supply is published; changing turns by SPB cell-to-coil assignment or per-mode DC reallocation across the stack is not found.

## 1. Closest papers
1. **Conto2022hybrid**: two-inverter half-phase supply changes the pole count and the stator winding factor (0.96 to 0.62) with no contactor. Did not: choose turns as a design variable or use more than two modules.
2. **Boxriker2017effects**: coil-configuration switching (series/parallel), pole changing and phase number compared in a normalised plane, with the semiconductor cost counted; torque-speed area can double. Did: turns change by switching, with extra semiconductors. Did not: SPB.
3. **Osama1997modeling / Bitsi2022design**: coil-group reversal changes pole count and effective winding factor in IM. Did not: synchronous rotor.
4. **Conto2023pole**: Dahlander stator (star/delta) changes both poles and turns per phase for a synchronous machine; contactor-type.
5. Search hits not opened: reconfigurable-winding EV review (Bath) and patents on series/parallel winding sections with AC switches; mechanical or semiconductor switch count is the stated cost.

Flag (own reasoning): per-mode DC reallocation across stacked cells (unequal cell voltages) conflicts with the equal average DC current of the series string; unequal voltage is fine only with matching unequal power per cell, which is exactly what a different turns ratio per coil group would produce. This couples H09 to the cell-balancing problem.

## 2. Search coverage
## Synonyms searched (all hypotheses, this pass)
pole-phase modulation (PPM); variable pole-phase / variable phase-pole (VPP, VPPM); pole-amplitude modulation; electronic pole changing; Dahlander / pole-changing winding; multi-three-phase, dual three-phase, multi-star; independently controlled stator coils (WICSC); modular / segmented / fractional-slot multiphase drives; stator cage drive (ISCAD, TUM); cascaded H-bridge and modular multilevel converters for machines; series-stacked inverter for motors; open-end winding multilevel PPM; cell bypass / module deactivation / phase shedding; harmonic / brushless excitation via stator (third harmonic, sub-harmonic, PPM); fault-tolerant pole transition; hybrid-excited pole changing; reconfigurable windings. Engines: WebSearch (standard and one extended), Crossref and OpenAlex lookups. IEEE Xplore full texts not reachable (HTTP 418, not retried); MDPI direct download returned 403 and was not pursued. Most new papers are therefore abstract-level, flagged in each `papers/<key>.md`.

## Core-argument check (shared by all files)
Question: does any work use the multiple inverters of a modular / stacked / cascaded drive to also change poles or phases, and then argue the inverter count is paid for by another reason (low-voltage devices)?
Answer: **partly filled, not at SPB's operating point.** (a) UIUC (Libbos2020modular, Libbos2022inverter): many-leg GaN inverter plus variable-pole IM, but the legs sit on one DC bus and are counted as extra cost versus a 3-leg drive. (b) TUM ISCAD (Bachheibl2015control, Runde2019iscad, Runde2020dual): many individually fed bars, 48 V, 300 kW, pole switching as a virtual gearbox; low voltage is obtained by paralleling at 48 V (very high current), not by series stacking to 1.2 kV. (c) Keerthipati group (Umesh2016dual, Reddy2018multilevel): several 3-phase inverters whose phase-shifted outputs form multilevel voltage in PPM high-pole mode; full-voltage devices, motive is torque ripple and dc-link use. (d) Sarrazin2011cascaded: cascaded H-bridge EV drive, no pole changing. No source combines series-stacked low-voltage modules, isolated neutrals and pole changing at truck power.

## 3. Competitors
- **Bianchi / Padova (Conto)**; **Doppelbauer / KIT (Boxriker)**; **Peretti / KTH**; **Toliyat / TAMU** (synchronous PPM).

## New refs (to merge)
All DOIs resolved through Crossref (HTTP 200) on 2026-10-29. Notes for these keys are in `papers/<key>.md`.

```bibtex
@inproceedings{Boxriker2017effects,
  author = {Boxriker, Miriam and Kolb, Johannes and Doppelbauer, Martin},
  title = {{Effects of coil configuration switching, pole-changing and multi-phase windings on permanent magnet synchronous motors}},
  booktitle = {IECON 2017 - 43rd Annual Conference of the IEEE Industrial Electronics Society},
  year = {2017},
  doi = {10.1109/iecon.2017.8216325}
}

@article{Bukhari2020dual,
  author = {Bukhari, Syed Sabir Hussain and Sirewal, Ghulam Jawad and Chachar, Faheem Akhtar and Ro, Jong-Suk},
  title = {{Dual-Inverter-Controlled Brushless Operation of Wound Rotor Synchronous Machines Based on an Open-Winding Pattern}},
  journal = {Energies},
  year = {2020},
  doi = {10.3390/en13092205},
  volume = {13},
  number = {9},
  pages = {2205}
}
```

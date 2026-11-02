# novelty_H04.md  H04: PPM in a multiphase SPB (m = 5, 6, 7, 9) gives more states, better torque/A and part-load efficiency
Gap-loop iteration 1, step 2. Author: lit-scout, 2026-11-02. Existing keys are in `refs.bib`; new keys are in the last section (not merged by me).

## Verdict
**Done for induction machines** (claim as stated). Only the SPB-specific constraint set (isolated neutrals, series stack) is not covered.

## 1. Closest papers
1. **Libbos2020loss** (TTE): pole chosen by torque and speed gives average loss -1/3 and 2x torque per ampere at partial load, experimental, 18-leg. Did: the claim. Did not: stack.
2. **Chaubal2024continuously / Maheshwari2025modulation** (UIUC): continuous pole sharing (2+6 pole) for minimum loss; dc-bus utilisation +11.5 %, torque at maximum speed +49.5 %. Did: more states than discrete pole selection.
3. **Bitsi2022design** (WICSC IM): FEM maps of pole-phase changing; benefit mostly efficiency, depends on voltage and current limits. Did not: cycle.
4. **AbdelKhalik2019nine / Umesh2016dual / Reddy2020multilayer**: nine- and fifteen-phase PPM with CPSR above 4 and 1:3:5 ratios.
5. **Boxriker2016expanding**: optimum phase number for PMSM, +9.6 %.

Open item: which of m = 5, 6, 7, 9 is best has been explored mostly by analysis of one machine at a time; a systematic sweep under a fixed per-module voltage (75 V) is not published.

## 2. Search coverage
## Synonyms searched (all hypotheses, this pass)
pole-phase modulation (PPM); variable pole-phase / variable phase-pole (VPP, VPPM); pole-amplitude modulation; electronic pole changing; Dahlander / pole-changing winding; multi-three-phase, dual three-phase, multi-star; independently controlled stator coils (WICSC); modular / segmented / fractional-slot multiphase drives; stator cage drive (ISCAD, TUM); cascaded H-bridge and modular multilevel converters for machines; series-stacked inverter for motors; open-end winding multilevel PPM; cell bypass / module deactivation / phase shedding; harmonic / brushless excitation via stator (third harmonic, sub-harmonic, PPM); fault-tolerant pole transition; hybrid-excited pole changing; reconfigurable windings. Engines: WebSearch (standard and one extended), Crossref and OpenAlex lookups. IEEE Xplore full texts not reachable (HTTP 418, not retried); MDPI direct download returned 403 and was not pursued. Most new papers are therefore abstract-level, flagged in each `papers/<key>.md`.

## Core-argument check (shared by all files)
Question: does any work use the multiple inverters of a modular / stacked / cascaded drive to also change poles or phases, and then argue the inverter count is paid for by another reason (low-voltage devices)?
Answer: **partly filled, not at SPB's operating point.** (a) UIUC (Libbos2020modular, Libbos2022inverter): many-leg GaN inverter plus variable-pole IM, but the legs sit on one DC bus and are counted as extra cost versus a 3-leg drive. (b) TUM ISCAD (Bachheibl2015control, Runde2019iscad, Runde2020dual): many individually fed bars, 48 V, 300 kW, pole switching as a virtual gearbox; low voltage is obtained by paralleling at 48 V (very high current), not by series stacking to 1.2 kV. (c) Keerthipati group (Umesh2016dual, Reddy2018multilevel): several 3-phase inverters whose phase-shifted outputs form multilevel voltage in PPM high-pole mode; full-voltage devices, motive is torque ripple and dc-link use. (d) Sarrazin2011cascaded: cascaded H-bridge EV drive, no pole changing. No source combines series-stacked low-voltage modules, isolated neutrals and pole changing at truck power.

## 3. Competitors
- **Libbos / Krein / Banerjee (UIUC)**: published the claim experimentally.
- **Keerthipati group; Peretti / KTH; Levi / Liverpool (Levi2007multiphase, Levi2016advances; multiphase theory); Barrero / Duran (multiphase control, no pole-changing hit in this pass)**: all cover phase-number theory.

## New refs (to merge)
All DOIs resolved through Crossref (HTTP 200) on 2026-10-29. Notes for these keys are in `papers/<key>.md`.

```bibtex
@inproceedings{Chaubal2024continuously,
  author = {Chaubal, Soumil and Libbos, Elie and Mukherjee, Debranjan and Maheshwari, Anuj and Banerjee, Arijit and Krein, Philip T.},
  title = {{Continuously-Variable-Pole Induction Machine Drive for Electric Vehicles}},
  booktitle = {2024 IEEE Transportation Electrification Conference and Expo (ITEC)},
  year = {2024},
  doi = {10.1109/itec60657.2024.10598847}
}

@article{Maheshwari2025modulation,
  author = {Maheshwari, Anuj and Chaubal, Soumil and Libbos, Elie and Mukherjee, Debranjan and Mazumdar, Debojyoti and Bajaj, Parag and Banerjee, Arijit and Krein, Philip T.},
  title = {{Modulation Depth Maximization for High Phase Count Drives With Emphasis on Variable Pole Operation}},
  journal = {IEEE Transactions on Industry Applications},
  year = {2025},
  doi = {10.1109/tia.2025.3571361},
  volume = {61},
  number = {6},
  pages = {9295-9306}
}

@article{Umesh2016dual,
  author = {Umesh, B. S. and Sivakumar, K.},
  title = {{Dual-Inverter-Fed Pole-Phase Modulated Nine-Phase Induction Motor Drive With Improved Performance}},
  journal = {IEEE Transactions on Industrial Electronics},
  year = {2016},
  doi = {10.1109/tie.2016.2561268},
  volume = {63},
  number = {9},
  pages = {5376-5383}
}

@article{Reddy2020multilayer,
  author = {Reddy, B. Prathap and Keerthipati, Sivakumar},
  title = {{Multilayer Fractional Slot Pole-Phase Modulated Induction Motor Drives for Traction Applications}},
  journal = {IEEE Transactions on Industrial Electronics},
  year = {2020},
  doi = {10.1109/tie.2019.2958287},
  volume = {67},
  number = {11},
  pages = {9112-9119}
}

@inproceedings{Boxriker2016expanding,
  author = {Boxriker, Miriam and Kolb, Johannes and Doppelbauer, Martin},
  title = {{Expanding the operating range of permanent magnet synchronous motors by using the optimum number of phases}},
  booktitle = {2016 18th European Conference on Power Electronics and Applications (EPE'16 ECCE Europe)},
  year = {2016},
  doi = {10.1109/epe.2016.7695597}
}

@inproceedings{Libbos2019variable,
  author = {Libbos, Elie and Ku, Bonhyun and Agrawal, Shivang and Tungare, Samira and Banerjee, Arijit and Krein, Philip T.},
  title = {{Variable-Pole Induction Machine Drive for Electric Vehicles}},
  booktitle = {2019 IEEE International Electric Machines \&amp; Drives Conference (IEMDC)},
  year = {2019},
  doi = {10.1109/iemdc.2019.8785212}
}
```

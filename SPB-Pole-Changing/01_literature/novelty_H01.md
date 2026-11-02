# novelty_H01.md  H01: zero extra hardware, design rules for (N, m, Q, p1/p2)
Gap-loop iteration 1, step 2. Author: lit-scout, 2026-11-02. Existing keys are in `refs.bib`; new keys are in the last section (not merged by me).

## Verdict
**Partly done.** The general (inputs, slots, poles) theory exists; the series-stack-with-isolated-neutrals version and the design rules do not.

## 1. Closest papers
1. **Osama1997modeling** (Osama, Lipo): coil-group current reversal gives 4/2-pole electronic pole changing; VSD decouples the two pole models. Did not: treat the inverter legs as free, give a slot/phase/pole feasibility table, or consider a series DC stack.
2. **Magill2015dynamic** (Magill, Krein): dynamic PPM model for an arbitrary number of electrical inputs and pole configurations via VSD. Did not: constrain the inputs to isolated-neutral groups on a series stack; simulation only.
3. **Olson2024enabling / Wu2023pole** (Peretti, KTH): harmonic-plane decomposition for any coil-group count, WICSC 36 legs, one isolated neutral overall, loaded transition at 107 V DC. Did not: relate coil-group count to a voltage-stacking purpose; 15 kW lab machine.
4. **Reddy2020multilayer** (Reddy, Keerthipati): fractional-slot multilayer winding, 15 phases in 36 slots, 1:3:5 poles; the only paper found that makes slot count versus (m, p) the design variable. Did not: involve module count N, isolated neutrals, or low-voltage devices.
5. **Libbos2020modular** (Libbos et al.): sizing framework for a modular multiphase inverter driving a variable-pole IM. Did not: derive N from a DC voltage class; legs share one DC link.

Own analysis (not from a paper, to be checked by the critic): with k isolated neutrals an m-phase machine loses k zero-sequence-type current planes, so harmonics that need common-mode current across a module (as in Talebi2022asynchronously) are excluded, and the feasible (N, m, Q, p) set is a strict subset of the common-neutral PPM set. This filter is what a design-rule table would encode and no source tabulates it.

## 2. Search coverage
## Synonyms searched (all hypotheses, this pass)
pole-phase modulation (PPM); variable pole-phase / variable phase-pole (VPP, VPPM); pole-amplitude modulation; electronic pole changing; Dahlander / pole-changing winding; multi-three-phase, dual three-phase, multi-star; independently controlled stator coils (WICSC); modular / segmented / fractional-slot multiphase drives; stator cage drive (ISCAD, TUM); cascaded H-bridge and modular multilevel converters for machines; series-stacked inverter for motors; open-end winding multilevel PPM; cell bypass / module deactivation / phase shedding; harmonic / brushless excitation via stator (third harmonic, sub-harmonic, PPM); fault-tolerant pole transition; hybrid-excited pole changing; reconfigurable windings. Engines: WebSearch (standard and one extended), Crossref and OpenAlex lookups. IEEE Xplore full texts not reachable (HTTP 418, not retried); MDPI direct download returned 403 and was not pursued. Most new papers are therefore abstract-level, flagged in each `papers/<key>.md`.

## Core-argument check (shared by all files)
Question: does any work use the multiple inverters of a modular / stacked / cascaded drive to also change poles or phases, and then argue the inverter count is paid for by another reason (low-voltage devices)?
Answer: **partly filled, not at SPB's operating point.** (a) UIUC (Libbos2020modular, Libbos2022inverter): many-leg GaN inverter plus variable-pole IM, but the legs sit on one DC bus and are counted as extra cost versus a 3-leg drive. (b) TUM ISCAD (Bachheibl2015control, Runde2019iscad, Runde2020dual): many individually fed bars, 48 V, 300 kW, pole switching as a virtual gearbox; low voltage is obtained by paralleling at 48 V (very high current), not by series stacking to 1.2 kV. (c) Keerthipati group (Umesh2016dual, Reddy2018multilevel): several 3-phase inverters whose phase-shifted outputs form multilevel voltage in PPM high-pole mode; full-voltage devices, motive is torque ripple and dc-link use. (d) Sarrazin2011cascaded: cascaded H-bridge EV drive, no pole changing. No source combines series-stacked low-voltage modules, isolated neutrals and pole changing at truck power.

## 3. Competitors
- **Peretti / KTH (Wu, Olson, Haq, Raj, Lin, Tilahune)**: model-level, very close; 36-leg experiment with one shared neutral and a 107 V bus. Highest overlap on control theory; no stacking.
- **Libbos / Krein / Banerjee, UIUC**: closest on hardware philosophy (18-leg GaN); no stack.
- **Keerthipati group (India)**: closest on module grouping and slot constraints.
- **Gerling, TUM (ISCAD)**: closest on low-voltage many-module traction; parallel 48 V.

## New refs (to merge)
All DOIs resolved through Crossref (HTTP 200) on 2026-10-29. Notes for these keys are in `papers/<key>.md`.

```bibtex
@inproceedings{Magill2015dynamic,
  author = {Magill, Matthew P. and Krein, Philip T.},
  title = {{A dynamic pole-phase modulation induction machine model}},
  booktitle = {2015 IEEE International Electric Machines \&amp; Drives Conference (IEMDC)},
  year = {2015},
  doi = {10.1109/iemdc.2015.7409030}
}

@inproceedings{Libbos2020modular,
  author = {Libbos, Elie and Hao, Ruomu and Ku, Bonhyun and Banerjee, Arijit and Krein, Philip T.},
  title = {{Modular Multiphase Drives for Variable-Pole Induction Machines in Electric Vehicles}},
  booktitle = {2020 IEEE Applied Power Electronics Conference and Exposition (APEC)},
  year = {2020},
  doi = {10.1109/apec39645.2020.9124085}
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

@article{Reddy2018multilevel,
  author = {Reddy, B. Prathap and Keerthipati, Sivakumar},
  title = {{A Multilevel Inverter Configuration for an Open-End-Winding Pole-Phase-Modulated-Multiphase Induction Motor Drive Using Dual Inverter Principle}},
  journal = {IEEE Transactions on Industrial Electronics},
  year = {2018},
  doi = {10.1109/tie.2017.2750626},
  volume = {65},
  number = {4},
  pages = {3035-3044}
}

@article{Runde2019iscad,
  author = {Runde, S. and Baumgardt, A. and Moros, O. and Rubey, B. and Gerling, D.},
  title = {{ISCAD — Design, control and car integration of a 48 volt high performance drive}},
  journal = {CES Transactions on Electrical Machines and Systems},
  year = {2019},
  doi = {10.30941/cestems.2019.00017},
  volume = {3},
  number = {2},
  pages = {117-123}
}

@article{Bachheibl2015control,
  author = {Bachheibl, Florian and Dajaku, Gurakuq and Patzak, Adrian and Gerling, Dieter},
  title = {{Control Strategies and Functional Safety for the Intelligent Stator Cage Drive (ISCAD)}},
  journal = {World Electric Vehicle Journal},
  year = {2015},
  doi = {10.3390/wevj7020211},
  volume = {7},
  number = {2},
  pages = {211-219}
}
```

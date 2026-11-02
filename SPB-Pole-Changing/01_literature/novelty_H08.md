# novelty_H08.md  H08: fault tolerance by re-assigning remaining coil groups to another pole/phase pattern
Gap-loop iteration 1, step 2. Author: lit-scout, 2026-11-02. Existing keys are in `refs.bib`; new keys are in the last section (not merged by me).

## Verdict
**Partly done.** Fault-tolerant pole transition exists (open phase, IM); fault-driven choice of a new pole pattern and module (cell) faults in a series stack are not covered.

## 1. Closest papers
1. **Wu2024open / Wu2023openphase** (KTH): post-fault HPD controller during pole change on an 18-phase IM, minimum copper loss. Did not: choose a different pole/phase pattern as the remedy; whole-module loss; stack.
2. **Bachheibl2015control** (TUM ISCAD): many individually fed bars, better fail-safety claimed; functional-safety of current measurement. Did not: pole re-assignment numbers (abstract level).
3. **Reddy2018multilevel**: keeps a two-level supply under fault in a PPM multilevel drive.
4. **Sarrazin2011cascaded**: cascaded EV drive with better fault-mode operation.
5. Search hit (patent, not verified): reconfigurable multiphase machine re-configured into a fault-tolerant mode after a winding or converter fault.

Flag: a failed cell in a series stack must be shorted at its DC port or the stack breaks, so fault response has a DC-side constraint the open-phase literature ignores.

## 2. Search coverage
## Synonyms searched (all hypotheses, this pass)
pole-phase modulation (PPM); variable pole-phase / variable phase-pole (VPP, VPPM); pole-amplitude modulation; electronic pole changing; Dahlander / pole-changing winding; multi-three-phase, dual three-phase, multi-star; independently controlled stator coils (WICSC); modular / segmented / fractional-slot multiphase drives; stator cage drive (ISCAD, TUM); cascaded H-bridge and modular multilevel converters for machines; series-stacked inverter for motors; open-end winding multilevel PPM; cell bypass / module deactivation / phase shedding; harmonic / brushless excitation via stator (third harmonic, sub-harmonic, PPM); fault-tolerant pole transition; hybrid-excited pole changing; reconfigurable windings. Engines: WebSearch (standard and one extended), Crossref and OpenAlex lookups. IEEE Xplore full texts not reachable (HTTP 418, not retried); MDPI direct download returned 403 and was not pursued. Most new papers are therefore abstract-level, flagged in each `papers/<key>.md`.

## Core-argument check (shared by all files)
Question: does any work use the multiple inverters of a modular / stacked / cascaded drive to also change poles or phases, and then argue the inverter count is paid for by another reason (low-voltage devices)?
Answer: **partly filled, not at SPB's operating point.** (a) UIUC (Libbos2020modular, Libbos2022inverter): many-leg GaN inverter plus variable-pole IM, but the legs sit on one DC bus and are counted as extra cost versus a 3-leg drive. (b) TUM ISCAD (Bachheibl2015control, Runde2019iscad, Runde2020dual): many individually fed bars, 48 V, 300 kW, pole switching as a virtual gearbox; low voltage is obtained by paralleling at 48 V (very high current), not by series stacking to 1.2 kV. (c) Keerthipati group (Umesh2016dual, Reddy2018multilevel): several 3-phase inverters whose phase-shifted outputs form multilevel voltage in PPM high-pole mode; full-voltage devices, motive is torque ripple and dc-link use. (d) Sarrazin2011cascaded: cascaded H-bridge EV drive, no pole changing. No source combines series-stacked low-voltage modules, isolated neutrals and pole changing at truck power.

## 3. Competitors
- **Peretti / KTH (Wu)**: nearest and active.
- **Gerling / TUM**, **Barrero / Duran** and **Levi** (multiphase fault tolerance in general; no pole-changing paper surfaced).

## New refs (to merge)
All DOIs resolved through Crossref (HTTP 200) on 2026-10-29. Notes for these keys are in `papers/<key>.md`.

```bibtex
@inproceedings{Wu2023openphase,
  author = {Wu, Yixuan and Peretti, Luca},
  title = {{Pole Transition Under Open Phase Fault Conditions in a Variable Pole Machine}},
  booktitle = {IECON 2023- 49th Annual Conference of the IEEE Industrial Electronics Society},
  year = {2023},
  doi = {10.1109/iecon51785.2023.10312343}
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

@inproceedings{Sarrazin2011cascaded,
  author = {Sarrazin, B. and Rouger, N. and Ferrieux, J.P and Crebier, J.C},
  title = {{Cascaded Inverters for electric vehicles: Towards a better management of traction chain from the battery to the motor?}},
  booktitle = {2011 IEEE International Symposium on Industrial Electronics},
  year = {2011},
  doi = {10.1109/isie.2011.5984149}
}
```

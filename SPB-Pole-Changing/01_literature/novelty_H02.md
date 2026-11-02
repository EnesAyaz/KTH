# novelty_H02.md  H02: kVA reduction lets a pole-changing SPB use fewer/smaller cells (system cost and loss)
Gap-loop iteration 1, step 2. Author: lit-scout, 2026-11-02. Existing keys are in `refs.bib`; new keys are in the last section (not merged by me).

## Verdict
**Partly done.** Inverter-oversizing and loss benefits of pole changing are published for EV scale; the system-level cell-count co-design for a truck is new, and the benefit is fragile against fair baselines.

## 1. Closest papers
1. **Libbos2022inverter** (TPEL): 18-leg GaN variable-pole drive gives 2.2x torque at maximum speed over a fixed-pole 3-leg drive, which would need 1.5x oversizing; 50 % lower loss and 62 % less dc-link capacitance than 3-leg; up to 45 % lower machine-plus-drive loss at partial load. Did not: truck rating, drive cycle, gearing alternatives, count of modules as a variable.
2. **Raj2022design** (Peretti, KTH): VPPIM 37 kW covers the map that needs 56 kW fixed-pole. Did not: inverter kVA or cost; EV scale.
3. **Boxriker2017effects / Boxriker2016expanding** (KIT): PMSM winding switching, pole changing and phase number compared with a semiconductor-cost term; +9.6 % torque at optimum m. Did not: low-voltage stack or truck cycle.
4. **Libbos2020modular**: efficiency and sizing of a modular multiphase inverter for a VPIM. Did not: voltage stacking.
5. Internal: T03b/T03d (own) show the advantage shrinks against fixed-pole IMs with free gearing; Prakht2025traction cites 125 kVA for 50 kW IM at CPSR 3.5.



## 2. Search coverage
## Synonyms searched (all hypotheses, this pass)
pole-phase modulation (PPM); variable pole-phase / variable phase-pole (VPP, VPPM); pole-amplitude modulation; electronic pole changing; Dahlander / pole-changing winding; multi-three-phase, dual three-phase, multi-star; independently controlled stator coils (WICSC); modular / segmented / fractional-slot multiphase drives; stator cage drive (ISCAD, TUM); cascaded H-bridge and modular multilevel converters for machines; series-stacked inverter for motors; open-end winding multilevel PPM; cell bypass / module deactivation / phase shedding; harmonic / brushless excitation via stator (third harmonic, sub-harmonic, PPM); fault-tolerant pole transition; hybrid-excited pole changing; reconfigurable windings. Engines: WebSearch (standard and one extended), Crossref and OpenAlex lookups. IEEE Xplore full texts not reachable (HTTP 418, not retried); MDPI direct download returned 403 and was not pursued. Most new papers are therefore abstract-level, flagged in each `papers/<key>.md`.

## Core-argument check (shared by all files)
Question: does any work use the multiple inverters of a modular / stacked / cascaded drive to also change poles or phases, and then argue the inverter count is paid for by another reason (low-voltage devices)?
Answer: **partly filled, not at SPB's operating point.** (a) UIUC (Libbos2020modular, Libbos2022inverter): many-leg GaN inverter plus variable-pole IM, but the legs sit on one DC bus and are counted as extra cost versus a 3-leg drive. (b) TUM ISCAD (Bachheibl2015control, Runde2019iscad, Runde2020dual): many individually fed bars, 48 V, 300 kW, pole switching as a virtual gearbox; low voltage is obtained by paralleling at 48 V (very high current), not by series stacking to 1.2 kV. (c) Keerthipati group (Umesh2016dual, Reddy2018multilevel): several 3-phase inverters whose phase-shifted outputs form multilevel voltage in PPM high-pole mode; full-voltage devices, motive is torque ripple and dc-link use. (d) Sarrazin2011cascaded: cascaded H-bridge EV drive, no pole changing. No source combines series-stacked low-voltage modules, isolated neutrals and pole changing at truck power.

## 3. Competitors
- **Libbos / Krein / Banerjee (UIUC)**: already publish the inverter-sizing argument; SPB must differentiate by stacking and truck scale.
- **Peretti / KTH**: machine-size argument (Raj2022).
- **Doppelbauer / KIT**: PMSM-side system trade.

## New refs (to merge)
All DOIs resolved through Crossref (HTTP 200) on 2026-10-29. Notes for these keys are in `papers/<key>.md`.

```bibtex
@inproceedings{Libbos2020modular,
  author = {Libbos, Elie and Hao, Ruomu and Ku, Bonhyun and Banerjee, Arijit and Krein, Philip T.},
  title = {{Modular Multiphase Drives for Variable-Pole Induction Machines in Electric Vehicles}},
  booktitle = {2020 IEEE Applied Power Electronics Conference and Exposition (APEC)},
  year = {2020},
  doi = {10.1109/apec39645.2020.9124085}
}

@inproceedings{Boxriker2017effects,
  author = {Boxriker, Miriam and Kolb, Johannes and Doppelbauer, Martin},
  title = {{Effects of coil configuration switching, pole-changing and multi-phase windings on permanent magnet synchronous motors}},
  booktitle = {IECON 2017 - 43rd Annual Conference of the IEEE Industrial Electronics Society},
  year = {2017},
  doi = {10.1109/iecon.2017.8216325}
}

@inproceedings{Boxriker2016expanding,
  author = {Boxriker, Miriam and Kolb, Johannes and Doppelbauer, Martin},
  title = {{Expanding the operating range of permanent magnet synchronous motors by using the optimum number of phases}},
  booktitle = {2016 18th European Conference on Power Electronics and Applications (EPE'16 ECCE Europe)},
  year = {2016},
  doi = {10.1109/epe.2016.7695597}
}

@inproceedings{Sarrazin2011cascaded,
  author = {Sarrazin, B. and Rouger, N. and Ferrieux, J.P and Crebier, J.C},
  title = {{Cascaded Inverters for electric vehicles: Towards a better management of traction chain from the battery to the motor?}},
  booktitle = {2011 IEEE International Symposium on Industrial Electronics},
  year = {2011},
  doi = {10.1109/isie.2011.5984149}
}
```

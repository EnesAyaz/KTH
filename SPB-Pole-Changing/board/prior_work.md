# Enes's own prior work on pole changing (leader inventory, 2026-10-29)

All under `C:\Github\KTH\`. Own-work: build on it, cite it, don't re-derive it.

## P1. Bipolar field excitation via WPT for pole-changing EESMs (IEEE letter draft)
- `Field Excitation/manuscript.pdf` (+ `SourceFiles.zip`: main.tex, ref.bib, figures; `CoverLetter.pdf`).
- Ayaz, Nee, Norrga, Peretti — "Primary-Side Control of Bipolar Field Excitation System
  for Pole-Changing Electrically Excited Synchronous Machines". HEMIZERO project (Swedish Energy Agency P2022-00956).
- Method: dual-input dual-output series–series WPT; two coil sets each feed a diode rectifier,
  outputs anti-parallel on the field winding; self-driven MOSFET+diode switches (gate from a
  passive divider/zener network on the rectifier output) block the inactive path. Field polarity
  is chosen by which transmitter is energised; field current is regulated by detuning the WPT
  frequency (97 -> 105 kHz). No rotor-side active converter, no control signal across the gap.
- Prototype: 72 V input, 14.2 ohm / 600 uH emulated field, bipolar +/-2.88 A (118 W), rectifier efficiency 99 % (87 % at 0.61 A).
- Pole change sequence: free-wheel to zero (tau_f = L_f/R_f) + blanking -> short no-torque
  interval, scheduled like a gear shift (vehicle inertia rides through).
- Fig. 1: 2-pole vs 4-pole EESM rotor (L_F1..L_F4 coil groups, current directions) and the combined torque-speed envelope.
- Its stated future work: scale up to traction rotors; **stator-harmonic-based excitation instead of WPT** (see P3).

## P2. PC-WFSM with bipolar optical power transfer (IEEE Trans. Magn. draft)
- `Airgap Harmonics/OPT-Workspace/` (source/original-draft.pdf + .txt, paper/sections, config/draft_parameters.json, notes/open-questions.md).
- Ayaz, Tosun (Newcastle) — "Design of a Pole-Changing Wound Field Synchronous Machine With Bipolar Optical Power Transfer Excitation".
- Three stationary light sources: two bipolar channels for the rotor coil groups that flip polarity
  between pole modes, one channel for the fixed-polarity groups; inactive PV group is the return path.
- 2-D FEA of a **10 kW, 4-pole/2-pole** prototype: pole transformation, rotor MMF, airgap flux, EMF, torque, losses.
- Open issues listed in notes/open-questions.md (field resistance vs MPP matching, loss totals) — parameters are draft/unverified.

## P3. Stator-harmonic (airgap-harmonic) excitation — concurrent power transfer
- `Airgap Harmonics/airgap harmonics.pptx` ("Modulation Methodology for Concurrent Power Transfer for Field Excitation").
- `Field Excitation/6-phase Induction Machine/Phase-Pole.pptx`: 12-slot linearised 2-pole/4-pole
  rotor patterns (I+/I- per coil group), rotor harvesting coil, mutual inductances to the stator
  phases, induced superimposed voltage, controllable region under SPWM/SVPWM.
- `Airgap Harmonics/Past studies/` (VCPSM, Double-Tx, carrier-phase-shift Simulink, configurations).
- **Direct SPB link:** SPB modules with isolated neutrals can inject an excitation component per coil
  group (carrier-phase-shift / superimposed voltage) — the rotor exciter could come from the stator
  inverter itself, removing WPT/OPT hardware. Candidate core contribution of this project.

## P4. Rotor MMF transition patterns
- `Field Excitation/FE_MMF.m`, `gift_creating.m` (+ `pptrans_sweep_MMF.gif`, `pptrans_sweep_FFT.gif`):
  rotor coil-group patterns 4-pole [1 -1 1 -1 ...], 2-pole [1 1 -1 -1 ...], and a transition
  [1 k -k -1 ...] swept in k with spatial FFT — a gradual pole transition instead of a hard switch.

## Implications for the team
- lit-scout: "bipolar exciter is an open design item" is wrong — P1/P2 are own solutions; the open
  item is scaling to a traction rotor and integrating excitation into the SPB stator inverter (P3).
- analyst: WRSM pole-change transition = free-wheel + blanking (tau_f) or the gradual k-transition (P4); take the 10 kW 4/2-pole PC-WFSM (P2) as the scaling seed, flagged draft.
- simulator: P4 transition and P3 harmonic injection are simulation targets.

## P5. OPT-Bipolar-Field-Excitation repo (C:\Github\OPT-Bipolar-Field-Excitation, with Nail Tosun)
- Newer, fuller version of P2: IEEE Trans. Magn. drafts `IEEEtran/main.tex` (FEA) and `main_analytical.tex`;
  README.md holds the scope, rating table and open decisions. Machine moved to **40 kW, 4-pole/2-pole,
  10 000 / 20 000 r/min** (10 kW variant spends 6.3 % of power on excitation, which weakens the case).
- Analytical design: MMF/pole 762 A (4p) / 467 A (2p), field time constant 251 ms, **field reversal to 95 % in 677 ms**;
  2-pole field wave has a 3rd harmonic of 67 %; stator yoke carries 1.22x the 4-pole flux in 2-pole mode.
- **Its open decision #1 is "how the stator changes between four and two poles" — assumed, not designed.
  Load FEA is blocked on it. SPB electronic pole changing is exactly that missing piece.**
- `analysis/4_design_studies/` (COMSOL-map based, 10 kW, 0.5 mm gap): with Dahlander series/parallel switching
  the 2-pole mode gives more torque only from 19 000 to 20 000 r/min ("hybrid uses the 2-pole mode on 1.3 % of
  its continuous operating area"); `results/torque_speed_inverter_cases.png`: switched machine needs a larger
  inverter (15.6 vs 11.1 kVA) for about the same 20 krpm power; at quarter-load points 2-pole efficiency is lower
  than 4-pole (e.g. 83.4 vs 86.1 %). **Independent agreement with T03: for a WRSM that can weaken its field via I_f,
  pole changing adds little torque-speed range.** The value of WRSM pole changing must be argued elsewhere.
- Data usable by the simulator: `analysis/3_fea/maps/*.csv`, `paper_fea_numbers*.mat`, `torque_speed_switching.m`
  (dq per-unit model with k2, x2 scaling for the 2-pole mode — compare with the analyst's k_w^2/p^2).

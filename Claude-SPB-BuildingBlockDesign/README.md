# SPB Half-Bridge Building Block Design

Design toolkit for **one** half-bridge (two-level) building block of a stacked polyphase
bridge / modular multicell inverter, using EPC eGaN HEMTs. Given power, DC-link voltage,
power factor, and a full-load efficiency target, this estimates conduction and switching
loss over a fundamental cycle, sizes gate resistance (turn-on/turn-off) against a Vds
overshoot limit, estimates power-loop stray inductance, checks thermal feasibility, and
searches for the highest switching frequency achievable for a given number of parallel
devices per switch position.

## Status

Now running against the **real EPC2361** (data/devices/EPC2361.yaml, built from the
datasheet + thermal SPICE model + EPCGaNLibrary.lib you provided). The LTSpice
double-pulse pipeline has been validated against the real device model (see
`docs/derivations.md` for the pin-order and library-parsing issues that came up and how
they were fixed) and a full Rg x Id sweep is used to build an LTSpice-calibrated
switching-loss lookup (`outputs/EPC2361_dpt_sweep.csv`), which `scripts/run_design.py
--lookup-csv` uses for the actual fsw/Rg/N recommendation instead of the coarse analytical
fallback. `EXAMPLE_PLACEHOLDER.yaml` and `TEST_GENERIC_FET.yaml` remain as
non-EPC2361 references (the latter was used to smoke-test the LTSpice automation
mechanics before the real model was available).

## What's still worth double-checking

1. **Loop inductance**: `config/design_spec.yaml`'s layout geometry gives ~0.47nH via the
   analytical `parallel_plate` estimate -- at or below even the best published
   flux-canceling PCB layouts for this power class (see `docs/derivations.md`'s
   real-world-benchmarks section). Treat it as an optimistic lower bound until measured
   or field-solved on real hardware; consider re-running the Rg sweep at 1-2nH for a more
   conservative first hardware revision.
2. **Cooling architecture**: EPC2361's best thermal path (Rth_jc=0.2 C/W) is through the
   package TOP, which is at SOURCE potential -- for a half-bridge the high- and low-side
   devices' tops sit at different potentials, so a shared top-side heatsink needs an
   electrically isolating TIM. Confirm `r_th_interface_C_per_W` in the design spec
   reflects a real isolating TIM, not a generic (lower-Rth) non-isolating one.
3. **Even-current-sharing assumption**: the N-parallel search assumes perfectly even
   current sharing across parallel devices. Real boards see some dynamic imbalance from
   device-to-device Vth spread (see the parallel-GaN-FETs paper cited in
   `docs/derivations.md`) -- layout symmetry matters more than this model can check.

## Workflow

```
data/devices/<PART>.yaml          <- real datasheet numbers
data/ltspice_models/<PART>.lib    <- real EPC LTSpice model
        |
        v
python scripts/run_design.py config/design_spec.yaml        # coarse pass, analytical Rg/fsw
        |
        v
LTSpice double-pulse sweep (src/spb_bb/ltspice/runner.sweep_rg)
  -> outputs/<PART>_dpt_sweep.csv                             # accurate Eon/Eoff/overshoot(Rg, Id)
        |
        v
python scripts/run_design.py config/design_spec.yaml --lookup-csv outputs/<PART>_dpt_sweep.csv
        |
        v
outputs/design_report.md   # recommended N parallel, Rg, f_sw, loss & thermal breakdown
```

## Package layout

- `src/spb_bb/devices.py` -- device parameter model, loaded from `data/devices/*.yaml`.
- `src/spb_bb/modulation.py` -- SPWM/SVM current-stress model for one leg (see the
  docstring for the derivation of why synchronous GaN conduction loss is independent of
  modulation index and power factor, unlike the classical Si IGBT+diode case).
- `src/spb_bb/conduction_loss.py` -- Rds_on conduction + dead-time third-quadrant loss.
- `src/spb_bb/switching_loss.py` -- analytical (coarse) or LTSpice-lookup (accurate)
  switching energy, integrated over the fundamental cycle's current waveform.
- `src/spb_bb/loop_inductance.py` -- first-pass PCB power-loop inductance estimate.
- `src/spb_bb/thermal.py` -- steady-state Rth network, N-parallel Tj feasibility.
- `src/spb_bb/optimize.py` -- ties it together: min-Rg-for-overshoot, then max-fsw search,
  swept over parallel-device count.
- `src/spb_bb/ltspice/` -- double-pulse netlist generation, headless LTSpice runner
  (via `spicelib`), and Rg-sweep-to-lookup-table interpolation.
- `src/spb_bb/report.py` -- Markdown report generation.
- `scripts/run_design.py` -- CLI entry point.
- `.claude/agents/` -- four focused subagents: `loss-estimator`, `thermal-analyst`,
  `ltspice-runner`, `report-writer`.

## Setup

```bash
python -m pip install -r requirements.txt
python -m pytest tests/
```

LTSpice was found at `C:\Users\enesa\AppData\Local\Programs\ADI\LTspice\LTspice.exe` on
this machine; pass a different path via `ltspice_exe=` to `ltspice.runner.run_double_pulse`
if needed.

## Key modeling assumptions (read before trusting numbers)

- **Synchronous rectification**: both switches are actively gated (complementary, with
  dead time), so GaN's symmetric on-state channel resistance applies in both current
  directions when gated on. Only the dead-time gap falls back to third-quadrant
  (diode-like) conduction. If your actual gate drive scheme uses diode-emulation instead,
  swap in `modulation.casanellas_currents`.
- **Full-load, steady-state only**: the efficiency constraint and thermal check are both
  evaluated at rated power; no partial-load loss curve or transient thermal (Zth) model
  yet.
- **Switching loss**: `analytical` mode linearly scales a single datasheet/test reference
  point with Id, Vds and Rg -- adequate for a first pass, not for fine Rg optimization
  near an overshoot limit. Use `lookup` mode (real LTSpice double-pulse sweep) before
  finalizing Rg/f_sw.
- **Loop inductance**: analytical PCB geometry estimate, meant to bound the double-pulse
  sweep -- calibrate against a real board measurement once hardware exists.

## Reference papers (data/Papers/)

- Palma, Barba & Musumeci, "Parallel Connection of GaN FETs: an Experimental
  Investigation Approach," PCIM Europe 2024 -- parallel-device current sharing, directly
  informed the N-parallel modeling caveats above.
- Brothers & Beechner, "GaN Module Design Recommendations Based on the Analysis of a
  Commercial 3-Phase GaN Module," 2019 -- low-voltage GaN overshoot sensitivity and
  power-loop layout benchmarks, directly informed the loop-inductance caveat above.
- "A High-Performance GaN Power Module With Parallel Packaging for High-Current and
  Low-Voltage Traction Inverter Applications"
- "A Multi-Kilowatt Low-Profile GaN Inverter for Light Electric Vehicles and High-Power
  Tools"
- "GaN-Based Low-Voltage Inverter for Electric Scooter Drive System"
- Cooke & Rogers, "120 V..." (not yet reviewed in this session -- similar application
  class, worth checking for anything relevant to this design's 75V/5kW point)

The last three weren't read in depth this session (not yet needed for the numbers
produced so far) but match this design's application class closely enough to be worth a
look if you want more cross-checks.

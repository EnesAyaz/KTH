# EPC2361 parallel half-bridge design

Start with **data/inputs/design.json**, then press **Ctrl+Shift+B** to calculate and build **reports/generated/loss_report.pdf**.

The design unit is one half bridge: 4, 5 or 6 devices per switch position (8, 10 or 12 devices per half bridge). Three legs form the 75 V, 18.75 kW inverter. The objective is the **highest feasible switching frequency**, up to 100 kHz, with efficiency above 99.5% and junction temperature below 125 C.

## Workflow

1. **Characterize the device.** Existing single-device SPICE runs establish DC resistance versus temperature and switching-energy/voltage-stress trends. Read reports/generated/spice_characterization.pdf and split_gate_report.pdf. Their results are not a qualified parallel-bank lookup table.
2. **Develop the parallel bank.** Retain individual Ron/Roff, shared driver impedance, local capacitors, branch and common-source inductance. See results/layout_concepts and reports/cooke_rogers_inductance_review.md. Geometry estimates are assumptions until PCB extraction.
3. **Average over the sinusoidal fundamental.** The active model integrates upper/lower duty-weighted conduction, switching energy at instantaneous current, deadtime reverse conduction and gate power. It compares centered SVM (m=1.15) with a separate SPWM example (m=0.99). Linear SPWM cannot deliver the same fundamental voltage as SVM m=1.15 at the same DC link.
4. **Find frequency and cooling requirements.** results/design/highest_frequency.csv selects the highest passing frequency per configuration. sweep.csv includes all points and failure reasons. TIM and cold-plate limits are reported separately and referenced to one half bridge.

## Active folders

| Folder | Purpose |
|---|---|
| data/datasheets, data/spice, data/devices | Source PDFs, vendor model and device parameters |
| data/inputs | Design, characterization and geometry inputs |
| models | Half-bridge cycle integration and SPICE measurement/gate utilities |
| scripts | Runners, report builders and layout/geometry generators |
| results/design | Canonical design CSVs, summary and figures |
| results/double_pulse, spice_characterization, split_gate | Retained reproducible SPICE evidence and raw waveforms |
| results/layout_concepts, paper_review | Supporting layout illustrations and geometry estimates |
| reports/generated | Three useful PDFs: design, device characterization, split-gate study |
| reports/templates | Corresponding editable LaTeX templates |
| tests | Physics and numerical checks |
| archive/superseded-2026-09-09 | Reversible archive of superseded tutorials and duplicate models; excluded from VS Code search/Explorer |

## Main commands

    .\.venv\Scripts\python.exe scripts/run_sweep.py
    .\.venv\Scripts\python.exe scripts/create_report.py
    .\.venv\Scripts\python.exe -m unittest discover -s tests -v

Characterization commands (LTspice runs can take time):

    .\.venv\Scripts\python.exe scripts/run_double_pulse.py
    .\.venv\Scripts\python.exe scripts/check_double_pulse.py
    .\.venv\Scripts\python.exe scripts/build_spice_report.py --refresh
    .\.venv\Scripts\python.exe scripts/run_split_gate.py

Layout support:

    .\.venv\Scripts\python.exe scripts/create_layout_concepts.py
    .\.venv\Scripts\python.exe scripts/create_power_loop_concepts.py
    .\.venv\Scripts\python.exe scripts/estimate_loop_from_geometry.py

## Important modeling boundaries

- **Switching is still an analytical placeholder:** 5 ns on/off overlap and approximate Eoss. The sweep does not prove that a shared driver retains these timings for N=4/5/6. Existing single-device energies are intentionally not copied into a parallel-bank efficiency prediction.
- Switching energy must eventually cover the entire 0-to-peak per-device current range, with voltage, temperature, driver, parasitics and N matched. Average E(i) over angle; do not evaluate nonlinear energy only at average or RMS current. Total dissipative Eon/Eoff replaces the overlap/Coss model rather than being added to it.
- The power factor is 1 and carrier ripple is zero pending actual motor/output-inductance data. Power factor affects current. A fundamental frequency and transient thermal model are needed for junction-temperature ripple; present temperatures are steady mean estimates, not proof of an instantaneous 125 C ceiling.
- 99.5% permits 94.22 W total three-phase loss, or 31.41 W per balanced leg. Other losses are zero until characterized; apparent efficiency is an upper estimate. The CSV reports the remaining allowable mean switching pair energy per device.
- Hot resistance uses maximum 25 C Rds times a typical 125 C multiplier; it is a conservative-temperature screening assumption, not self-consistent electrothermal iteration or a guaranteed hot maximum.
- TIM uses thickness/conductivity/contact area plus optional contact resistance. The 0.5 mm, 17.8 W/mK, 15 mm2 example is **1.873 K/W per device**, not the old arbitrary 0.5 K/W. The full-package effective area and uniform plate temperature need verification. Use insulating TIM because device tops are connected to source.
- Plate resistance is **per half bridge**, shared by its 2N devices. If all three legs share a plate, recompute with the combined heat. Driver heat, PCB thermal paths and local coolant warming are excluded.
- Maximum allowable TIM and plate resistances are conditional alternatives, not simultaneously available maxima. Maximum TIM thickness is a mathematical bound, not a selected pad thickness.
- SVM m=1.15 is close to the linear boundary. With assumed 20 ns deadtime plus 10 ns useful pulse, centered PWM reaches only 67 kHz on the present grid. This is a timing screen, not a GaN frequency limit. Controller pulse suppression, lower m or verified shorter timing requires a corresponding model update.
- The 60 A/device peak-current screen and assumed 90 V voltage ceiling remain editable design assumptions. Actual overshoot, dynamic sharing and safe gate resistance require parallel-bank SPICE and measurement.

Superseded items and original relative paths are listed in results/design/cleanup_manifest.txt. Nothing from the archive is imported by the active workflow. The virtual environment and source characterization data were preserved.

Detailed engineering roadmap: [Design and validation plan](reports/DESIGN_PLAN.md).

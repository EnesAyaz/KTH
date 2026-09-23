# EPC2361 DPT simulation datasheet

Keep using Launch-DPT.cmd for the existing GUI. The GUI and original EPC library were not modified by this report task.

## Deliverables

- output/pdf/EPC2361_DPT_Report.pdf: 10-page datasheet-style simulation report.
- output/pdf/EPC2361_DPT_Report.tex: editable LaTeX source.
- figures/: individual graphs and setup diagram in PNG and vector PDF.
- results.csv and results.json: 30 case results with measured current, signed switching energies, voltage/gate extremes and limit flags.
- runs/: full settings, schematic, netlist, raw/log output, compressed plot data and result per case.
- convergence.json: reference 50 A nominal, 0.25 ns maximum-step comparison.
- provenance.json: selected setup and hashes of the unchanged GUI/library.
- qa.json: run/page counts and energy cross-check statistics.

## Cases selected from the user's examples

A: Rg_on=2 ohm, Rg_off=0.5 ohm, Llayout=1 nH.
B: Rg_on=2 ohm, Rg_off=0.5 ohm, Llayout=5 nH.
C: Rg_on=5 ohm, Rg_off=2 ohm, Llayout=1 nH.
D: Rg_on=5 ohm, Rg_off=0.5 ohm, Llayout=1 nH.
E: Rg_on=2 ohm, Rg_off=2.5 ohm, Llayout=1 nH.

Each uses nominal 0,10,20,30,40,50 A, 75 V supply, 100 deg C fixed device temperature, +5/-4 V gate drive. The external resistors are in addition to driver output resistance. Other parasitics and pulse settings are documented in the report. Plotted current is measured immediately before the event, not assumed equal to the nominal target. The 0 A point uses a separately identified 1 MH no-load approximation; it is not a conventional 75 V hard-switching event at zero current.

## Rebuild

From the parent DPT-GaN folder:

python datasheet_sweep.py
python build_datasheet.py

Or double-click Generate-Datasheet.cmd. Successful matching cases are cached. Use `python datasheet_sweep.py --force` to rerun the sweep. A rerun after changing the EPC model requires --force. Local Python needs NumPy and Matplotlib; the builder also needs pdflatex on PATH. These were available on this PC. No extra GUI dependencies were added.

To rerun the finer reference check without replacing the 30-case summary:

python -c "from datasheet_sweep import run_case,ROOT; import json; r=run_case(('reference_250ps_50A',50,2,.5,1,'250p'),force=True); (ROOT/'convergence.json').write_text(json.dumps(r,indent=2))"

Then run build_datasheet.py again. The internal --pilot option writes a pilot-only summary; rerun the normal sweep before rebuilding a report.

## Interpretation

This is simulation-only characterization, not a manufacturer datasheet or hardware qualification. Energy is signed DUT terminal Vds*Id integrated from 20 ns before to 100 ns after the command edge. Eoff comes from the first turn-off, Eon from the second turn-on. Different integration endpoints and ringing can change the energy. No absolute-value or monotonic corrections are applied. A 200 ns endpoint comparison and finer timestep check are included.

All 30 runs exhibited device-terminal Vgs below -4 V. Eighteen exceeded 100 V Vds and six exceeded 120 V. The requested -4 V rail is itself the negative gate rating and leaves no undershoot margin. Out-of-rating model results are retained and flagged, not presented as validated specifications.

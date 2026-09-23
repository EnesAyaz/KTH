# Completed 17 September 2026

The requested three-page report is complete and visually verified.
PDF: dut_gate_search/output/pdf/DUT_Gate_Resistance_Limits.pdf
Editable LaTeX: same directory, .tex extension.
Summary CSV: dut_gate_search/selected_settings.csv
All trials: dut_gate_search/trials.csv
Audit: dut_gate_search/qa.json

750 search/verification/neighbour runs; no unresolved runs. Nine calibration
runs and the additional failed-pair timestep checks are retained separately.
Eight of nine cases have a pair passing DUT Vds <100 V at 500, 250 and 125 ps.
At 5 nH / 45 A, all 576 nominal grid pairs (0.5..12 ohm per resistor,
0.5-ohm increments) exceed 100 V. Lowest nominal peak: 117.733 V at
12 ohm on / 0.5 ohm off; 125 ps recheck: 117.738 V.

The GUI is unchanged. These are DUT-voltage screening results, not whole-
half-bridge safety or tolerance qualification. Upper-device voltage excluded.
Use Generate-Gate-Limits-Report.cmd to reproduce from the saved cache.

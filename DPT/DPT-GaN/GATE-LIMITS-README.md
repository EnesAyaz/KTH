# DUT gate-resistance screening

The existing GUI is unchanged. This separate batch study uses 75 V DC link,
+5/-4 V gate command, and a 100 V peak DUT Vds ceiling. The upper transistor's
Vds is excluded from the selection criterion.

Run from this directory:

    python search_gate_limits.py
    python check_gate_search.py
    python build_gate_report.py

The search uses external resistors from 0.5 to 12 ohm in 0.5 ohm increments.
It minimizes Ron + Roff, breaking ties by lower Ron. A selected pair must
pass at 0.5 ns, 0.25 ns and 0.125 ns maximum timestep. This is a discrete resistor
objective, not a direct optimization of switching time or energy.

The nominal current is the first-turn-off setpoint. The second pulse is
1 us and raises the current further; the entire DPT is checked for peak Vds.
See the report table for actual first and second turn-off currents.

Results: dut_gate_search/summary.json and trials.csv.
Report: dut_gate_search/output/pdf/DUT_Gate_Resistance_Limits.pdf.
Editable LaTeX is alongside the PDF; vector figures are under figures/.
Per-run model, netlists, settings, raw waveforms and results are under runs/.

Pairs close to 100 V have little tolerance margin. Device, temperature,
bus-voltage and layout tolerances are not qualified. A DUT-voltage pass is
not a statement of whole-half-bridge safety. The -4 V gate command also
leaves no negative gate-voltage undershoot allowance.

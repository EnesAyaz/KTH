# E01 — Cell-power pulsation under two simultaneous spatial orders (H11 bench test)

Status: plan, 2026-11-02. Enes approved planning the test. Predictions: analyst (task E01-P). Run: Enes.

## Purpose
Test the H11 law on real hardware at low power. Show that:
- a single isolated-neutral 3-leg cell, driven with two current sets of different order and frequency, has DC-capacitor
  ripple at f_a ± f_b of the predicted amplitude;
- a 5-leg cell driven with the equivalent pair, chosen by the law, shows no such ripple, only switching ripple.

Pass: the measured 3-leg ripple amplitude is within ±20 % of the prediction at each test point, and the 5-leg ripple at
f_a ± f_b is below 10 % of the 3-leg value at equal currents.

## Why it is cheap
A stator is not needed. The law depends only on how the m leg currents of one cell combine. A star-connected
RL load with an isolated neutral reproduces a cell's coil group. The two "spatial orders" become two current sets with
different phase sequences (order mod m) and different frequencies.

## Phase A — lab inverter (low risk, do first)
- **Hardware:** Imperix PEB modules (PEB8024, as in the P1 setup) with a B-Box controller.
  - One DC source feeds a floating DC link with known C. Use a single film capacitor of measured value, so C is known
    (no MLCC DC-bias uncertainty).
  - 3 legs for the 3-leg cell, 5 legs for the 5-leg cell.
- **Load:** star RL per leg, isolated neutral; e.g. 2–5 mH and 1–2 Ω per leg. No machine.
- **Control:** per-leg current control, reference i_k = I_a cos(2π f_a t − k·2π a/m) + I_b cos(2π f_b t − k·2π b/m).
- **Points (3-leg):**
  - (a, b) = (1, −1) [positive + negative sequence], f_a = 50 Hz, f_b = **31 Hz** (30 Hz would alias a −2f_a + 6f_b
    order-10 product onto the 80 Hz bin), I_a = I_b = 5 A, 10 A. Use only the 66 "safe" points in
    `02_analytics/results/E01_predictions.json`: many 10 A points exceed linear modulation below 100 V, and at 1 mF the
    ripple reaches ±48 V.
  - (1, 1) at f_a ≠ f_b as a control case. The law predicts pulsation at |f_a − f_b| only.
- **Points (5-leg):** (a, b) = (1, 2): neither (a+b) nor (a−b) is divisible by 5, so the prediction is zero cross-pulsation.
  Same frequencies and currents as the 3-leg points.
- **Measure:** DC-link voltage (AC-coupled, high resolution) and source current; FFT at f_a ± f_b; leg currents for the
  actual I and phase.
- **Predicted ripple:** ΔV ≈ P_pulse / (2π f_pulse · V_dc · C) per the analyst's E01-P table, with P_pulse taken from the
  measured voltages and currents, not the references. `pulsation_from_phasors()` in `02_analytics/E01_predictions.py`
  takes the per-leg complex phasors straight from scope data.
- **Source:** a stiff lab supply absorbs part of the pulsating current. Decouple it (series choke or diode + R), or
  measure capacitor + source current and compare with P/V_dc.
- **Expected margins:** the 5-leg null survives ±5 % R/L imbalance (≤ 4.1 % residual) and asymmetric dead time (≤ 1.4 %),
  so the 10 % pass criterion is robust. Replace the assumed Imperix values (20 kHz, 100–1000 ns dead time, loop
  bandwidth) with the real ones.

## Phase B — Rev B GaN boards (after Rev B bring-up)
- **Hardware:** three Rev B half-bridge boards for a 3-leg cell, five for a 5-leg cell. Common 75 V local bus with the
  boards' own MLCC bank.
- **What it adds:** it measures the real retained MLCC capacitance at DC bias, which is the open assumption in H10/H11
  (1.0–2.9 mF per module). It also checks the ±5 / ±10 % ripple limits on the actual cell.
- **Constraints:** follow `PCB-Design/reports/pcb-rules/DPT_measurement_setup.md`. Bench use at 75 V, DC−-referenced
  controller, isolated probes on switch nodes, gate-level procedure first.

## Open items for Enes
- Imperix: are 5 PEB legs and a B-Box free? What DC-link capacitor value can be fitted and measured?
- Rev B: how many boards will be assembled, and when?
- Safety: Phase A at ≤ 100 V DC; Phase B at 75 V on the bench only, not inside a stack.

# H03 screen: rotor excitation by SPB space-harmonic injection

- **Files:** script `02_analytics/screen_H03.py`, numbers in `results/screen_H03.json`.
- **Machine:** T03c WRSM (s = 0) and HESM (s = 0.25) on the T03 stator, N = 16, 300 kW, G = 10.8.
- **Geometry:** stator, winding and R_coil come from `data/machine_geometry.json` (R01 shared geometry).
  - The WRSM air gap is still open in R01. The baseline uses the T03 g_eff = 1.3 mm, with a sensitivity over 1.08 to 3 mm.

**Verdict: partly feasible. The concept works without any extra stationary hardware, but it is not free.**
- **Main limiting factor:** the injected current competes with the torque current at start and just above base speed.
- **Why the current is large:** the only clean injection order on 48 coils is order 8. Its winding factor is 0.5 and its magnetising inductance is 43 uH, about 1/21 of the torque-order value. Delivering kW-level field power at standstill therefore needs about 12 % of the leg current.

## 1. Injection choice (what is SPB-specific)
- **Zero-sequence injection is not possible.** An isolated-neutral module carries no zero-sequence current, so orders divisible by 3 are blocked.
- **The SPB-specific freedom is an independent space order.** A conventional 3-phase 2p = 8 winding only makes orders 4, 20, 28 and 44, and all of them couple to the torque and the field winding. The SPB can drive any order not divisible by 3, at any frequency, on top of the torque current.
- **Only orders 8 and 16 are clean.** They make no average torque, do not couple to either field coil group (directly or through the 8-pole saliency), and make no order-1 pull.
- **Order 8 is chosen:** winding factor 0.50, coupling 0.73.
- **Rotor side:**
  - A polyphase order-8 harvesting winding, series-tuned at f_r0 = 8 f_m(90 km/h) = 661 Hz, feeding a diode rectifier.
  - The stator frequency follows f_i = |f_r0 - 8 f_m|. At standstill this is a transformer at 661 Hz, powered by the inverter. At 90 km/h it is a DC-excited brushless exciter, powered by the shaft, and needs no voltage headroom.

## 2-3. Power vs need, and cost

| | WRSM | HESM s = 0.25 |
|---|---|---|
| Field need: cruise / start / 3x forcing (kW) | 1.15 / 4.0 / 12 | 0.5 / 3.3 / 6 |
| Start grade: T03c -> injection, peak current rule (rms rule) | 12.0 -> **10.5 %** (11.9 %) | 12.0 -> 10.6 % (11.9 %) |
| Start injection: I/I_max, V/V_max, B_nu | 0.12, 0.19, 0.083 T | 0.11, 0.19, 0.083 T |
| Envelope at 1100-2000 rpm, peak (rms) rule | -13 to -17 % (-9 %) | -14 to -15 % (-7 %) |
| P at 90 km/h | -0.5 % | -4.7 % |
| Cruise 85 km/h efficiency: T03c (rectifier only) / P1 WPT / injection | 96.94 / 96.89 / 96.87 % | 97.38 / 97.36 / 97.34 % |
| 50 km/h on 3 % grade efficiency: T03c / WPT / injection | 96.82 / 96.75 / 96.48 % | 97.35 / 97.31 / 97.17 % |
| Injection chain efficiency at cruise | 90 % (123 W) | 88 % (69 W) |
| Maximum forcing power at 2000 rpm (15 % I) | 6.6 kW (2x forcing, not 3x) | 6.6 kW (enough) |

- **Assumptions behind the table:**
  - Peak-sum current is the conservative device limit; rms-sum is the thermal-only bound.
  - The injection current budget is capped at 15 % of I_max.
  - The rotor has a 3 % harvesting-winding loss.
  - The rectifier uses the P1 efficiency fit.
  - The P1 WPT link efficiency is assumed to be 94 %.
- **Module voltage at top speed:** still enough. f_i is about 0 at 90 km/h, so V_inj is 0.2 % of V_max. The voltage cost sits between base speed and about 3000 rpm (6 to 13 % of V_max).
- **Losses:** stator copper and iron from the injected wave are small (50 W at cruise, up to 220 W at start). The rectifier and harvesting winding add about 70 W at cruise.
- **Torque:** no average torque with the field. The exciter torque is at most 8 Nm (shaft power drawn), with about 2 Nm of rectifier ripple.
- **Forces (NVH risk):** at start the order-8 wave makes radial forces of orders 4 and 12 at about 661 Hz, at 21 % of the main force density. Order 4 is a soft stator mode. This needs FEA or simulator checks.
- **Tank-frequency trade-off:** raising f_r0 lowers the start current but costs top-speed power.
  - f_r0 = 3 kHz: start grade 11.3 %, but P at 90 km/h falls 24 %.
  - f_r0 = 661 Hz is the best compromise.
- **Air-gap sensitivity (R01 open):** g_eff = 2 / 3 mm raises the start injection current to 15 / 18 % of I_max.
- **Alternative order 5:** its magnetising inductance is 5.8x higher, so the start grade improves to 11.2 %. But the order-1 unbalanced magnetic pull with the 8-pole field is 6.5 kN at start and 1.1 kN at cruise, which rules it out.

## 4. Bipolar field for pole changing
- **Yes, in principle.** The SPB injection can act as the P1 bipolar exciter.
  - Two harvesting channels, each with its own rectifier, connect anti-parallel on group B. P1's self-driven blocking switches stay.
  - The polarity is set by which pattern the SPB injects. This replaces P1's choice of which transmitter is energised.
- **The channels need frequency separation.** Orders 8 and 16 are orthogonal, but order 16 is weak (coupling 0.47, 0.28 kW at standstill with 10 % voltage). The two orders also cross-couple through the 8-pole saliency.
  - The practical form is two or three tanks on order 8 at different rotor frequencies (selected by f_i), with group A on its own tank.
- **Reversal speed:** at 2000 rpm, 6.6 kW of forcing gives about 1.65x field voltage. The WRSM reversal then takes about 1.4 tau_f instead of 0.7 tau_f at 3x forcing.

## 5. Comparison

| | Injection (H03) | P1 WPT | Brushes |
|---|---|---|---|
| Stationary hardware | none | HF inverter, Tx coils, compensation | 3 slip rings, brushes, H-bridge |
| Rotor hardware | order-8 harvesting winding, tanks, rectifier, switches | Rx coils, compensation, rectifier, switches | none |
| Chain efficiency at cruise | 88-90 % (incl. stator extras) | about 93 % (99 % rectifier x 94 % link, assumed) | about 97 % (estimate) |
| Drive cost | start -1.5 grade points (peak rule); envelope -15 % at 1100-2000 rpm when the peak field is needed | none | none |
| Maintenance | none | none | brush wear |

## Open items for the gap-critic / simulator
- **Start penalty:** about 12 % of leg current at start. It disappears if the device limit is thermal (rms) rather than peak, so this needs a decision from the GaN SOA.
- **Order-4 radial force:** an NVH check at about 661 Hz is needed.
- **Harvesting-winding space:** the winding has to share the pole shoes with the field copper.
- **Saturation:** the incremental permeability for the small order-8 wave on a saturated main field is not modelled.
- **Novelty for lit-scout:** brushless WRSM "harmonic / sub-harmonic excitation" (Kwon / Ayub group; dual-inverter and open-winding zero-sequence injection) is the closest prior art. The SPB's isolated neutrals rule out the zero-sequence route but make independent space orders possible.

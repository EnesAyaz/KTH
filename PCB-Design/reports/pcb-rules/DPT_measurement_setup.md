# DPT board (Rev B): measurement ports, references and connection rules

Answers section 5 of `spb-bb-revb-dpt-review-2026-10-19.md`. Valid for the double-pulse test of one board on the bench: 75 V
local bus, up to about 100 V peak at the drains during the pulses, controller and bench supplies referenced to DC− of this
board. Not valid for a level inside a 1200 V stack (see section 4 of the review).

## Ports and what their returns are tied to

| Port | Signal | Return / shield | Max. voltage signal–return | Return potential vs DC− | Instrument |
|---|---|---|---|---|---|
| MMCX V_DS L1–L4 (bottom, next to each LS FET) | SW (LS drain) | LSRC1–4 (LS source, device side of the shunt) | 75 V DC + overshoot, ≤ 100 V peak | ≈ 0 V (shunt drop only), but **four different nodes** | rated isolated probe with an MMCX tip, e.g. Tektronix IsoVu TIVP + TIVPMX50X (±250 V, 50×) |
| U.FL V_GS H (bottom) | gate via 0 Ω | KH1 / KH2 (HS Kelvin = switch node) | +5.1 / −(V_ISO − 5.1) V | **0 … 100 V, 30–50 V/ns** | isolated probe only |
| U.FL V_GS L (bottom) | gate via 0 Ω | KL1 / KL2 (LS Kelvin) | +5.1 / −(V_ISO − 5.1) V | ≈ 0 V (LS source of that block) | isolated probe preferred; a ground-referenced channel only if no other channel is tied elsewhere (see below) |
| UFCS shunt RS1–RS4 (SMA cable) | shunt sense | DC− side of the shunt | mV | 0 V | scope channel, 50 Ω input per PMK |
| Spring pads V_GS / V_DS, test points | see `hardware/spb-bb-revb-dpt/fab/testpoints.csv` | as listed there | as for the matching port | as for the matching port | passive probe only where the return is DC−-referenced (LS side) and no other channel is tied elsewhere |

The U.FL connectors are rated 30 V (Hirose). They are used only for gate signals (≤ about 10 V between pin and shield).
Their 0 Ω links (R16–R19, R35–R38) are not fitted by default; the V_GS spring pads are the primary gate measurement.
The V_DS ports are MMCX (Würth WR-MMCX 66012102111404, 170 V rms working, 500 V rms withstanding).

## Gate-drive settings for the DPT (2026-10-23)

| Setting | Value | Why |
|---|---|---|
| Isolated gate supplies (HS and LS inputs) | **V_ISO = 7.0 V** | 5.1 V Zener: V_GS,on = +5.1 V, V_GS,off = −(7.0 − 5.1) = **−1.9 V** |
| R_ON (R7, R9, R26, R28) | **1.5 Ω** (R_G,on = 0.5 + 2 × 1.5 = 3.5 Ω per device) | SPICE with the Q3D copper (75 V, 322 A): HS V_DS peak 92.9 V; 1.0 Ω gives about 105 V |
| R_OFF (R8, R10, R27, R29) | 0 Ω jumper | turn-off through D_OFF; low hold-off impedance |
| PWM | one source for both control headers (J5, J14), equal-length cables | the four parallel high-side switches are driven by two drivers (U1, U2): source and cable skew shifts one pair against the other |

With −1.9 V off-bias, the simulated V_GS bump on the held-off FET peaks at −0.5 to −0.8 V (+1.2 to +1.4 V at 0 V off,
above the 1.1 V typical threshold). The simulated off-state ringing reaches about −3.4 V: do not set V_ISO above 7 V
without checking the EPC2361 minimum V_GS. At bring-up, measure on all eight V_GS spring pads: the on/off levels,
the bump on the held-off FET at the other FET's turn-on, and the delay between U1 and U2.

## Rules

1. **One ground-referenced return at a time.** All channels of a normal oscilloscope share protective earth. Two
   ground-referenced channels on different returns (for example LSRC1 and LSRC2, or KL1 and DC−) short these nodes
   through the scope. LSRCx to DC− through a scope ground bypasses the shunt and corrupts the current measurement.
2. **High side: isolated only.** KH1/KH2 move with the switch node (0 … 100 V at 30–50 V/ns). Never connect a
   ground-referenced probe or channel to a KH, SW or high-side V_GS port.
3. **V_DS MMCX: isolated probe or none.** A plain MMCX-to-BNC cable connects LSRCx to protective earth (rule 1) and
   puts up to 100 V on the scope input. An MMCX connector supplies no attenuation and no isolation.
4. **Never 50 Ω termination on a V_DS port.** 75 V into 50 Ω is about 112 W.
5. **Do not float the oscilloscope** (no protective-earth removal).
6. **Before powering:** with the DUT unpowered, check with an ohmmeter that each probe shield connects only to the
   node in the table above, and that no two of LSRC1–4, KL1/KL2, KH1/KH2, DC− are joined through the instruments.
7. **Deskew and loading:** deskew voltage and current channels (UFCS) with the actual probes; account for the probe
   input capacitance on V_DS (TIVPMX50X ≈ 2.3 pF) and on V_GS.

## Connection diagram (one cell, low side)

```text
           drain (SW) ──┬───────────── MMCX centre ──► IsoVu tip (isolated head) ──► scope
                        │
                   LS EPC2361
                        │
 Kelvin (KL) ── U.FL V_GS L shield            gate ── 0 Ω ── U.FL V_GS L centre ──► isolated probe
                        │
 source (LSRC) ─────────┴── MMCX shield (return of the isolated tip, NOT earth)
                        │
                     UFCS shunt ──► SMA ──► scope channel (earth-referenced, = DC−)
                        │
                       DC− ── bench supply return / controller GND reference
```

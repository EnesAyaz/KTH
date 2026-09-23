# Derivations and modeling notes

## Synchronous GaN conduction loss is independent of M and power factor

See the full derivation in the docstring of `src/spb_bb/modulation.py`. Summary: for
complementary (no-dead-time) synchronous switching, the top-switch duty `d_T(theta) = 0.5
+ 0.5*M*sin(theta)` has only a DC and 1st-harmonic component, while the leg current squared
`i(theta)^2` (with `i(theta) = I_pk*sin(theta-phi)`) has only a DC and 2nd-harmonic
component. Integrated over a full fundamental cycle, the cross term (which is where any
M/phi dependence would come from) vanishes exactly, leaving
`P_sync_per_switch = R_ds_on * I_pk^2 / 4`, independent of M and phi. This only holds
because a gated-on GaN channel conducts symmetrically in both current directions -- the
classical Casanellas (1994) result for Si IGBT + diode pairs *does* depend on M and phi,
because the IGBT and its antiparallel diode have genuinely different V-I curves, not
because of the duty-cycle skew itself.

## Double-pulse test: why the loop inductance sits between Cdc and node A, not in series
with the load inductor

Topology (`ltspice/double_pulse.py`):

```
Vdc/Cdc --Lloop-- A --XQH(D=A,S=SW)-- SW --Vsense_id-- XQL(D,S=0)-- 0
                   \--Lload-------------/
```

The commutation (fast, di/dt-limited) loop when QL switches is
`Cdc -> Lloop -> A -> QH -> SW -> QL -> 0 -> Cdc`. Lload sits between the *same* two nodes
(A, SW) as QH, in parallel with it -- but Lload is large (tens-hundreds of uH) and its
current is essentially constant over a single switching transition, so it behaves as a
current source during the fast commutation, not as part of the di/dt loop. Lloop, placed
between the bulk cap and node A, is therefore exactly the parasitic inductance that
determines Vds overshoot and switching-transition dynamics, matching standard GaN
clamped-inductive double-pulse test practice.

## Why QH's (or QL's) freewheel path works via the intrinsic body/third-quadrant diode

QH: drain=A, source=SW, body tied to source. When QL turns off, Lload's current (flowing
A->SW) has nowhere to go through QL, so it forces SW upward until it exceeds A by one
diode drop, forward-biasing QH's body/third-quadrant path (conducts when V(source=SW) >
V(drain=A)) and letting current recirculate A -> Lload -> SW -> [QH reverse] -> A. This is
exactly the Vds overshoot being characterized: `V(SW)` settles near `Vdc + V_f` during the
freewheel window, and the turn-on switching event (second pulse) is QL hard-commutating
that freewheeling current away from QH.

A real e-mode GaN part has no body diode as such; its third-quadrant conduction is the
channel itself operating with reversed current direction when Vgs=0 (data captured in the
device's `third_quadrant_conduction` YAML block / the vendor LTSpice model's own physics).
The double-pulse netlist relies on whatever reverse-conduction behavior the vendor's
LTSpice subckt implements -- verify it produces a plausible `V(SW)` clamp voltage before
trusting Eon/Eoff numbers from a new device model (see `.claude/agents/ltspice-runner.md`).
Confirmed against the real EPC2361 model (`EPCGaNLibrary.lib`): the `bswitch` behavioral
current source's `if(v(drain,source)>0, ..., ...)` branching implements forward and
third-quadrant conduction symmetrically using `v(gate,drain)` as the reverse-mode
overdrive term -- no separate diode element needed, matches real GaN physics.

## EPC's own subckt pin order (confirmed, not assumed)

`data/ltspice_models/EPCGaNLibrary.lib` defines `.subckt EPC2361 gatein drainin sourcein`
-- **G D S** order, not the "D G S" default this project started with. Confirmed
independently against `EPCGaN.asy`'s `PINATTR SpiceOrder` (1=gatein, 2=drainin,
3=sourcein). Every EPC GaN device in this library shares that symbol, so G-D-S is very
likely the pin order for other EPC parts too, but **check the actual `.subckt` line before
trusting a new device** -- set `ltspice_model.pin_order` in that device's YAML file
(`devices.py` / `double_pulse._pin_map` consume it).

Including the full ~7000-line `EPCGaNLibrary.lib` made LTSpice fail with a generic
`Unable to find definition of model "version"` error (likely from an unrelated device's
syntax elsewhere in the file, not EPC2361 itself). Extracting just the EPC2361 `.subckt`
block into its own `EPC2361.lib` fixed it -- also faster to simulate. Watch for a UTF-8
BOM when extracting a block with PowerShell (`Set-Content -Encoding utf8` adds one by
default); LTSpice's parser does not strip it and fails with a similarly unhelpful
"unknown subcircuit" error.

## Real-world benchmarks for power-loop inductance and parallel-device current sharing

From the reference papers under `data/Papers/`:

- **Palma, Barba & Musumeci, "Parallel Connection of GaN FETs: an Experimental
  Investigation Approach" (PCIM Europe 2024)**: a 4-parallel-EPC2302-per-switch inverter
  drove a 5 kW BLDC motor at 150 A_rms phase current, V_dc=60V, f_sw=20kHz -- essentially
  the same power class as this building block's own 75V/5kW/175A_rms design point. Confirms
  4-6 parallel EPC-class devices is a realistic, demonstrated N for this power range. Also:
  device-to-device V_GS(th) spread causes *dynamic* current-sharing imbalance during
  switching transients (the lower-Vth device turns on earlier / off later and sees a
  higher peak current) that this project's thermal/loss model does NOT capture -- it
  assumes perfectly even current sharing across the N parallel devices. Real designs
  mitigate this with layout symmetry and (ideally) per-position matched devices; treat the
  N-parallel search here as a first-pass sizing tool, not a guarantee of even sharing.

- **Brothers & Beechner, "GaN Module Design Recommendations..." (2019)**: directly
  demonstrates why low-voltage (<=100V) high-current GaN is unusually sensitive to Vds
  overshoot -- a commercial 100V/270A-per-phase module failed at just 36% of its rated
  current (292A) because 11-28nH of lateral (non-flux-canceled) power-loop inductance drove
  Vds past the die rating. Best-in-class published low-inductance layouts achieve:
  0.7nH (6-layer PCB, flux-canceling, [13] in that paper) up to 5.1-5.6nH (DBC substrate,
  [11]) between the DC bus and the paralleled dies. **This project's own
  `loop_inductance.py` parallel-plate estimate for the example
  `config/design_spec.yaml` layout (15mm x 8mm, 0.2mm dielectric) comes out to ~0.47nH --
  at or below even the best demonstrated real hardware.** Treat that as an optimistic
  lower bound that assumes a well-executed flux-canceling layout; a first hardware
  revision should probably budget for something closer to 1-2nH until measured, and the
  double-pulse Rg sweep should be re-run once a real board exists and loop inductance can
  be measured or field-solved.

  Also demonstrated: a well-designed 100V/360A-class GaN module (4 parallel GS61008 dies,
  6-layer PCB, Rg_on=10ohm/Rg_off=4ohm per die) hard-switched at 367A with only 85.5V Vds
  peak on a 48V bus -- a useful sanity reference for what "good" looks like at this voltage
  class.

## Gate-drive turn-on/off diode network

Two ideal diodes (`.model Dideal D(Ron=0.001 Roff=1e9 Vfwd=0 Vrev=1e9)`) route the gate
charge/discharge current through different resistors:

```
DRV --Don--Rg_on--> GL      ; Don: anode=DRV, conducts DRV->GL (charging) when DRV rises
GL --Doff--Rg_off--> DRV     ; Doff: anode=GL, conducts GL->DRV (discharging) when DRV falls
```

Both diodes must point "downhill" in the direction current needs to flow for their
respective transition -- get this backwards and the gate simply never discharges (this bit
the first smoke-test run: `Doff N_off GL` had it backwards and QL never turned off after
the first pulse, giving E_on = E_off = 0 and no Vds swing at all).

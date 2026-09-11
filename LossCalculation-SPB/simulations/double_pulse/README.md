# EPC2361 double-pulse workflow

The supplied archive contains a **transistor** SPICE model. The active Python
runner builds a half-bridge with one low-side DUT and one complementary device,
not a complete SPB module or a parallel bank.

1. Edit `data/inputs/double_pulse.json`.
2. Run `.\.venv\Scripts\python.exe scripts/run_double_pulse.py` from the project.
3. Run `.\.venv\Scripts\python.exe scripts/check_double_pulse.py` for nominal
   timestep and integration-window checks.
4. Run scripts/build_spice_report.py --refresh to regenerate the separate SPICE report.

Equivalent VS Code tasks are **Run LTspice double-pulse sweep** and
**Check double-pulse convergence**. Ctrl+Shift+B builds the separate half-bridge analytical design report; it does not import the single-device switching energies.

The runner finds the installed LTspice executable at its per-user ADI location;
set `LTSPICE_EXE` to override it. It uses hidden batch mode, preserving every
generated `.cir`, `.raw` and `.log` under `results/double_pulse/`. Open a generated
`test.cir` in LTspice to inspect/edit a specific case. `smoke.cir` is the initial
standalone example using the original, uninstrumented model.

## Circuit connections

- DC source: `dc` to ground.
- Load inductor: `dc` to switching node `sw`.
- Bus parasitics: `dc -> Lloop -> Rloop -> top`.
- Complementary transistor: drain=`top`, source=`sw`; gate is held off through
  its own resistance referenced directly to `sw`.
- DUT: drain connected to `sw` through a zero-volt current probe, source=`s`.
- Common-source inductance: `s` to ground. Driver return is ground, so this
  inductance is shared with the gate loop; an ideal Kelvin source is not assumed.
- DUT gate: 0/5 V driver through driver resistance, external Rg and gate-loop L.

The first gate pulse approximately builds `I = V*t/L`. The off interval
commutates current into the complementary device's reverse channel. The second
turn-on provides Eon, while the first turn-off provides Eoff at a similar load
current. Both **actual** edge currents are stored because `L*I/V` is approximate.
The first turn-on is not used for energy characterization.

## Files and measurements

`switching_table.csv` includes:

- Target and actual currents, bus voltage, external gate resistance and loop L.
- `eon_terminal_uj` and `eoff_terminal_uj`: signed package drain-terminal energy.
- `eon_channel_raw_uj` and `eoff_channel_raw_uj`: observed internal channel and
  drain/source resistance heat, excluding internal gate resistance/leakage.
- `eon_channel_excess_uj`: raw turn-on heat minus ordinary conduction over the
  measurement window. A separate 5 V DC sweep at the same temperature supplies
  the conduction reference; it is not inferred from a ringing waveform.
- `eoff_channel_excess_uj`: turn-off channel/access heat including turn-off delay.
- `channel_energy_pair_uj`: sum of the two excess values. Its two edge currents
  differ slightly and it excludes complementary-device reverse conduction.
- Raw maximum absolute derivatives and maximum slopes over a **1 ns** interval.
- DUT and complementary-device Vds peaks, Vgs extrema and voltage margins.

The nominal waveform plot shows both devices' voltage stress. The sensitivity
plot compares Rg and loop L at 75 V and target 40 A. All waveform cases remain
available, including cases violating voltage limits.

An extra observation source in `EPC2361_monitored.lib` exposes channel and
drain/source access-resistor power without feedback to electrical nodes. The
original supplied library and extracted original model remain unchanged.
The monitored output voltage is numerically watts; it is not a physical node.
The library's tiny convergence resistors and gate leakage are excluded from
this drain-source heat signal. Nonlinear charge elements exchange stored energy
and are not directly counted as dissipation.

## How to interpret the results

Terminal energy can differ from heat because it includes changing capacitance
energy. Do not add Eoss again to a switching-energy quantity that already
includes its dissipation. Do not add gate-drive power to this internal heat
signal unless intentionally building a total transistor/driver heat budget.

The energy convention uses a post-command window, initially 150 ns. Nominal
checks compare 100/150/200 ns windows and 0.2/0.1/0.05 ns maximum timesteps.
Checks passing do not prove that every grid corner or the real PCB is accurate.

Voltage screening uses **both** FETs, a 90 V design ceiling and a 100 V absolute
drain limit. Gate limits are -4/+6 V. The vendor model has no destructive
breakdown model and continues to simulate above ratings. Such results are
flagged failures, not acceptable switching points. No transient-rating credit
is used. Driver impedance and edge time are assumptions, not a modeled driver IC.

The 72-case default grid is 50/75 V, 20/40/60 A, Rg=0.5/1/2/4 ohms,
Lloop=0.5/2/5 nH, at 125 C. Common-source L=0.2 nH is additional to Lloop.
It deliberately explores potentially unacceptable corners.

The module calculation still uses the analytical model. Before replacing it
with an energy table, match real driver ON/OFF impedance, parallel-bank
parasitics, complementary gating/deadtime and temperature; extend the current
grid to cover the full phase waveform. Average the appropriate energies over
the electrical cycle, and remove any overlap/Coss terms already included.

Manufacturer context:
[EPC device models](https://epc-co.com/epc/design-support/device-models) and
[ADI LTspice quickstart](https://analogdevicesinc.github.io/ltspice-reference/ai_ref/LTSPICE-QUICKSTART.html).

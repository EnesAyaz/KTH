"""Generates a clamped-inductive double-pulse-test SPICE netlist for one DUT device,
switched against a second instance of the SAME device subckt held off (true synchronous
GaN topology: the "freewheel path" is the complementary device's third-quadrant
conduction, not an ideal diode, since e-mode GaN has no body diode).

Topology (see docs/derivations.md for the reasoning behind loop-inductance placement):

    VBUS --Cdc-- 0
    VBUS --Lloop-- A
    A --XQH(D=A,G=GH,S=SW)-- SW      ; high side, held off the whole test (Vgh=0)
    A --Lload-- SW                    ; big external test inductor, sets I_test
    SW --Vsense_id-- SWQL
    SWQL --XQL(D=SWQL,G=GL,S=0)-- 0   ; DUT, gate driven by the double-pulse waveform
    DRV --Don--Rg_on--> GL            ; turn-on path (Don: anode=DRV, conducts DRV->GL when DRV rises)
    GL --Doff--Rg_off--> DRV          ; turn-off path (Doff: anode=GL, conducts GL->DRV when DRV falls)

Vsense_id is a 0V ammeter so I(Vsense_id) is exactly the DUT drain current with a clean
sign convention, without depending on how the vendor subckt names its internal pins.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..devices import GaNDevice


@dataclass
class DoublePulseSpec:
    v_dc: float
    i_test: float           # target peak (2nd-pulse) current, A
    r_g_on: float
    r_g_off: float
    l_loop: float             # power-loop stray inductance, H
    l_load: float = 100e-6      # big external test inductor, H (current source during the pulse)
    c_dc: float = 100e-6
    c_dc_esr: float = 10e-3    # series damping resistance for Cdc, ohm. This is the ONLY
    # damping element in the Lloop<->Coss(high-side) resonant loop in this model -- raise
    # it to see how much of an observed ring is a lightly-damped physical resonance vs.
    # how much settles out once realistic parasitic resistance is added (see
    # docs/derivations.md's ringing-diagnosis note).
    v_gs_off: float = 0.0        # gate drive "off" rail, V (negative = negative gate bias,
    # e.g. -4V, a common real-driver technique for noise immunity against Miller-induced
    # parasitic turn-on -- NOT expected to change the on-time Lloop/Coss ringing, which
    # happens while Vgs is HIGH and the device is conducting, see docs/derivations.md).
    t_start_delay: float = 200e-9
    t_off_gap: float = 2e-6      # time both pulses are separated by (freewheel/settle time)
    pw2: float = 500e-9         # 2nd pulse width (only needs to capture the Eon transient)
    tr_tf_drive: float = 2e-9    # gate-drive source's own rise/fall (fast, not the DUT's actual switching speed)
    sim_tmax: float | None = None  # optional max internal timestep (s); leave None to let
    # LTSpice's adaptive (truncation-error-controlled) stepper choose -- it already takes
    # sub-ns steps during the fast edges on its own. Forcing a small Tmax over the WHOLE
    # simulation (including the multi-microsecond inductor-charging phase) blows up the
    # .raw file and runtime for no accuracy benefit; only set this if edges look under-resolved.
    sim_extra_time: float = 300e-9  # extra time after 2nd pulse's rising edge to capture full Eon transient


def _pin_map(device: GaNDevice, node_d: str, node_g: str, node_s: str) -> str:
    """Map (drain, gate, source) onto the subckt's own pin order string, e.g. 'D G S' or
    'G D S' (EPC's own GaN library subckts use 'G D S': `.subckt EPC2361 gatein drainin
    sourcein`, confirmed against both the .lib and the EPCGaN.asy symbol's SpiceOrder).
    Set device yaml's ltspice_model.pin_order to match a new device's own subckt line
    before trusting a sweep against it -- a wrong order simulates a nonsense circuit
    without necessarily erroring."""
    tokens = device.ltspice_pin_order.split()
    lookup = {"D": node_d, "G": node_g, "S": node_s}
    return " ".join(lookup.get(t, node_s) for t in tokens)


def _resolve_lib_path(lib_file: str) -> str:
    """LTSpice resolves a relative `.include` path against the NETLIST's own directory,
    not the project root -- device yaml files store project-relative paths (e.g.
    "data/ltspice_models/X.lib"), so make them absolute before writing the netlist."""
    p = Path(lib_file)
    if p.is_absolute():
        return str(p)
    project_root = Path(__file__).resolve().parents[3]
    return str((project_root / p).resolve())


def build_double_pulse_netlist(device: GaNDevice, spec: DoublePulseSpec, lib_override: str | None = None) -> str:
    lib_file = _resolve_lib_path(lib_override or device.ltspice_lib_file)
    subckt = device.ltspice_subckt

    pw1 = spec.i_test * spec.l_load / spec.v_dc  # time to ramp Lload to I_test at ~Vdc across it

    t0 = spec.t_start_delay
    t1_rise = t0
    t1_flat_end = t1_rise + pw1
    t1_fall_end = t1_flat_end + spec.tr_tf_drive
    t2_rise = t1_fall_end + spec.t_off_gap
    t2_flat_end = t2_rise + spec.pw2
    t_stop = t2_flat_end + spec.sim_extra_time

    vgs = device.v_gs_drive

    qh_pins = _pin_map(device, "A", "GH", "SW")
    ql_pins = _pin_map(device, "SWQL", "GL", "0")

    netlist = f"""* Auto-generated double-pulse test: {device.part_number}, Rg_on={spec.r_g_on}, Rg_off={spec.r_g_off}
.include {lib_file}

Vdc VBUS 0 DC {spec.v_dc}
Cdc VBUS VBUS_ESR {spec.c_dc}
Resr VBUS_ESR 0 {spec.c_dc_esr}
Lloop VBUS A {spec.l_loop}
Lload A SW {spec.l_load}

XQH {qh_pins} {subckt}
Vgh GH SW 0

Vsense_id SW SWQL 0
XQL {ql_pins} {subckt}

* Gate drive: PWL double pulse at the driver output, split into asymmetric on/off paths.
* Off-state rail is spec.v_gs_off (0V unless a negative bias is requested).
Vdrv DRV 0 PWL(0 {spec.v_gs_off}  {t1_rise:.6e} {spec.v_gs_off}  {t1_rise + spec.tr_tf_drive:.6e} {vgs}  {t1_flat_end:.6e} {vgs}  {t1_fall_end:.6e} {spec.v_gs_off}  {t2_rise:.6e} {spec.v_gs_off}  {t2_rise + spec.tr_tf_drive:.6e} {vgs}  {t2_flat_end:.6e} {vgs}  {t2_flat_end + spec.tr_tf_drive:.6e} {spec.v_gs_off})

.model Dideal D(Ron=0.001 Roff=1e9 Vfwd=0 Vrev=1e9)
Don DRV N_on Dideal
Rgon N_on GL {spec.r_g_on}
Rgoff DRV N_off {spec.r_g_off}
Doff GL N_off Dideal

.tran 0 {t_stop:.6e} 0{(' ' + format(spec.sim_tmax, '.6e')) if spec.sim_tmax else ''}
* Relaxed tolerances: the EPC behavioral (B-source, exp/log) model combined with a
* lightly-damped Lloop/Coss resonance at low Rg can make the default reltol=1e-3 Newton
* solver churn indefinitely ("Heightened Def Con" loop) or time out. This is a standard
* trick for fast GaN behavioral models, not a sign the result is inaccurate for our
* purposes (energy integrals are insensitive to this level of tolerance relaxation).
.options reltol=0.01 abstol=1e-9 vntol=1e-4 gmin=1e-11
.options numdgt=7

.save V(SW) V(A) V(GL) I(Vsense_id) I(Lload) I(Lloop)

.backanno
.end
"""
    meta = {
        "t1_rise": t1_rise,
        "t1_flat_end": t1_flat_end,
        "t1_fall_end": t1_fall_end,
        "t2_rise": t2_rise,
        "t2_flat_end": t2_flat_end,
        "t_stop": t_stop,
        "i_test": spec.i_test,
        "v_dc": spec.v_dc,
    }
    return netlist, meta

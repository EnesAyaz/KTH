"""Extended EPC2361 double-pulse characterization: two decoupled sweeps so Rg_on and
Rg_off can be optimized independently, each also spanning several power-loop inductance
values (per config/design_spec.yaml's layout.loop_inductance_sweep_nH literature-grounded
set).

Sweep 1 (turn-on): varies (Id, Rg_on, L_loop), Rg_off held at a fixed reference value.
  -> characterizes E_on(Id, Rg_on, L_loop).
Sweep 2 (turn-off): varies (Id, Rg_off, L_loop), Rg_on held at a fixed reference value.
  -> characterizes E_off(Id, Rg_off, L_loop) and V_ds overshoot(Id, Rg_off, L_loop).

This decoupling is valid because the double-pulse netlist's gate-drive network routes
turn-on and turn-off current through electrically separate resistor/diode paths
(ltspice/double_pulse.py) -- Rg_off has no effect on the turn-on edge and vice versa.
Reference Rg = 2 ohm (matches multiple literature designs: EPC's own datasheet test
condition, Infineon's butterfly-layout inverter).

Saves outputs/EPC2361_eon_sweep.csv and outputs/EPC2361_eoff_sweep.csv.
"""

import sys
import time
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from spb_bb.devices import load_device
from spb_bb.modulation import leg_peak_current_from_power
from spb_bb.ltspice.double_pulse import DoublePulseSpec
from spb_bb.ltspice.runner import run_double_pulse
from spb_bb.ltspice.lookup import save_sweep_csv

with open(PROJECT / "config" / "design_spec.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

device = load_device(str(PROJECT / "data" / "devices" / "EPC2361.yaml"))

v_dc = cfg["power"]["v_dc_V"]
i_pk = leg_peak_current_from_power(
    cfg["power"]["p_out_leg_W"], cfg["power"]["v_rms_fund_V"], cfg["power"]["power_factor"]
)
n_max = cfg["search"]["n_parallel_max"]
i_min = i_pk / n_max

i_test_list = [round(i_min + (i_pk - i_min) * f, 1) for f in (0.0, 0.4, 0.7, 1.0)]
rg_list = [0.5, 1.0, 2.0, 5.0, 10.0]
lloop_list_nH = cfg["search"]["loop_inductance_sweep_nH"]
rg_ref = 2.0

ltspice_exe = r"C:\Users\enesa\AppData\Local\Programs\ADI\LTspice\LTspice.exe"

print(f"I_pk={i_pk:.1f}A, I_test points: {i_test_list}")
print(f"Rg points: {rg_list}, Lloop points (nH): {lloop_list_nH}, Rg_ref={rg_ref}")
n_each = len(i_test_list) * len(rg_list) * len(lloop_list_nH)
print(f"Runs per sweep: {n_each}, total: {2 * n_each}")


def run_sweep(name, work_dir, vary_on: bool):
    rows = []
    failed = []
    t0 = time.time()
    for l_nh in lloop_list_nH:
        l_loop = l_nh * 1e-9
        for i_test in i_test_list:
            for rg in rg_list:
                rg_on = rg if vary_on else rg_ref
                rg_off = rg_ref if vary_on else rg
                spec = DoublePulseSpec(
                    v_dc=v_dc, i_test=i_test, r_g_on=rg_on, r_g_off=rg_off, l_loop=l_loop
                )
                try:
                    res = run_double_pulse(
                        device, spec, work_dir, ltspice_exe=ltspice_exe, keep_files=True
                    )
                except Exception as exc:  # noqa: BLE001
                    failed.append((l_nh, i_test, rg))
                    print(f"  [{name}] L={l_nh}nH I={i_test}A Rg={rg} -> FAILED: {str(exc)[:120]}", flush=True)
                    continue
                rows.append(
                    {
                        "l_loop_nH": l_nh,
                        "i_d": i_test,
                        "v_ds": v_dc,
                        "r_g_on": rg_on,
                        "r_g_off": rg_off,
                        "e_on": res.e_on,
                        "e_off": res.e_off,
                        "v_ds_overshoot": res.v_ds_overshoot,
                    }
                )
                print(
                    f"  [{name}] L={l_nh:>4.1f}nH I={i_test:>6.1f}A Rg={rg:>4.1f} -> "
                    f"Eon={res.e_on*1e6:6.3f}uJ Eoff={res.e_off*1e6:6.3f}uJ "
                    f"ovs={res.v_ds_overshoot:6.2f}V ({time.time()-t0:.0f}s)",
                    flush=True,
                )
    print(f"[{name}] done in {time.time()-t0:.0f}s, {len(rows)} rows, {len(failed)} failed")
    return rows


on_rows = run_sweep("Eon", str(PROJECT / "outputs" / "ltspice_epc2361_eon_sweep"), vary_on=True)
save_sweep_csv(on_rows, str(PROJECT / "outputs" / "EPC2361_eon_sweep.csv"))

off_rows = run_sweep("Eoff", str(PROJECT / "outputs" / "ltspice_epc2361_eoff_sweep"), vary_on=False)
save_sweep_csv(off_rows, str(PROJECT / "outputs" / "EPC2361_eoff_sweep.csv"))

print("All sweeps complete.")

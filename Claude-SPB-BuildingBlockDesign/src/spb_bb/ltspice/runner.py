"""Runs a generated double-pulse netlist through LTSpice (headless, via spicelib) and
extracts Eon, Eoff and Vds turn-off overshoot from the resulting .raw waveform.

Requires: `pip install spicelib`, and LTSpice installed locally. Point `ltspice_exe` at
the real executable if it's not auto-detected (this machine has it at
C:\\Users\\<you>\\AppData\\Local\\Programs\\ADI\\LTspice\\LTspice.exe).
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .double_pulse import DoublePulseSpec, build_double_pulse_netlist
from ..devices import GaNDevice


@dataclass
class DoublePulseResult:
    e_on: float
    e_off: float
    v_ds_overshoot: float
    v_ds_peak: float
    i_test_actual: float
    raw_path: str
    meta: dict


def run_double_pulse(
    device: GaNDevice,
    spec: DoublePulseSpec,
    work_dir: str,
    ltspice_exe: str | None = None,
    lib_override: str | None = None,
    keep_files: bool = True,
    edge_margin: float = 5e-9,
) -> DoublePulseResult:
    from spicelib import SimRunner
    from spicelib.simulators.ltspice_simulator import LTspice

    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)

    netlist_text, meta = build_double_pulse_netlist(device, spec, lib_override=lib_override)
    net_path = work / f"dpt_{device.part_number}_Ron{spec.r_g_on:g}_Roff{spec.r_g_off:g}.cir"
    net_path.write_text(netlist_text, encoding="utf-8")

    if ltspice_exe:
        LTspice.spice_exe = [ltspice_exe]

    runner = SimRunner(output_folder=str(work), simulator=LTspice)
    raw_path, log_path = runner.run_now(str(net_path))

    if raw_path is None:
        log_text = Path(log_path).read_text(errors="ignore") if log_path else "(no log)"
        raise RuntimeError(f"LTSpice run failed for {net_path.name}. Log:\n{log_text}")

    result = extract_switching_energy(str(raw_path), meta, edge_margin=edge_margin)
    result_full = DoublePulseResult(
        e_on=result["e_on"],
        e_off=result["e_off"],
        v_ds_overshoot=result["v_ds_overshoot"],
        v_ds_peak=result["v_ds_peak"],
        i_test_actual=result["i_test_actual"],
        raw_path=str(raw_path),
        meta=meta,
    )

    if not keep_files:
        shutil.rmtree(work, ignore_errors=True)

    return result_full


def read_raw_waveforms_full(raw_path: str) -> dict[str, np.ndarray]:
    """Reads every trace saved by the double-pulse netlist (see the `.save` line in
    double_pulse.py): DUT Vds (=V(SW), source grounded), Id (=I(Vsense_id)), DUT gate
    voltage Vgs (=V(GL), source grounded), node A voltage, and the two inductor branch
    currents. Shared by extract_switching_energy (which only needs t/v_sw/i_d) and the
    interactive GUI (gui.py, which plots Vgs too)."""
    from spicelib import RawRead

    raw = RawRead(raw_path)
    t = np.array(raw.get_trace("time").get_wave(), dtype=float)
    t = np.abs(t)  # LTSpice sometimes stores time with sign quirks in mixed-mode traces
    out = {"t": t}
    for name, key in [("V(sw)", "v_ds"), ("V(gl)", "v_gs"), ("V(a)", "v_a"),
                       ("I(Vsense_id)", "i_d"), ("I(Lload)", "i_lload"), ("I(Lloop)", "i_lloop")]:
        try:
            out[key] = np.array(raw.get_trace(name).get_wave(), dtype=float)
        except Exception:  # noqa: BLE001 -- trace may not exist for older netlists; skip it
            pass
    return out


def read_raw_waveforms(raw_path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Backwards-compatible 3-tuple (t, Vds, Id) view of read_raw_waveforms_full."""
    w = read_raw_waveforms_full(raw_path)
    return w["t"], w["v_ds"], w["i_d"]


def extract_switching_energy(raw_path: str, meta: dict, edge_margin: float = 5e-9) -> dict:
    """Numerically integrates V_ds(t) * I_d(t) over the turn-on and turn-off transitions.

    Window boundaries come from the netlist's own gate-drive timing (meta), widened by
    edge_margin on each side to make sure ringing settles inside the integration window.
    """
    t, v_sw, i_d = read_raw_waveforms(raw_path)

    def integrate_window(t_center_lo, t_center_hi):
        lo = t_center_lo - edge_margin
        hi = t_center_hi + edge_margin
        mask = (t >= lo) & (t <= hi)
        tt, vv, ii = t[mask], v_sw[mask], i_d[mask]
        if len(tt) < 2:
            return 0.0
        power = vv * ii
        trapezoid = getattr(np, "trapezoid", None) or np.trapz
        return float(trapezoid(power, tt))

    # The off-transition window must NOT be sized off t1_fall_end (that's just the ideal
    # gate-drive source's own edge, ~2ns, independent of Rg) -- a slow (high Rg_off) turn-
    # off can take tens of ns and was getting clipped, silently collapsing Eoff at high Rg.
    # Use most of the gap before the next pulse instead, same idea as Eon's pw2 window.
    off_window_end = min(meta["t1_flat_end"] + 0.6 * (meta["t2_rise"] - meta["t1_flat_end"]), meta["t2_rise"])
    e_off = integrate_window(meta["t1_flat_end"], off_window_end)
    e_on = integrate_window(meta["t2_rise"], meta["t2_flat_end"])

    steady_mask = (t >= meta["t1_flat_end"] - 20e-9) & (t <= meta["t1_flat_end"])
    v_ds_before_off = float(np.mean(v_sw[steady_mask])) if np.any(steady_mask) else 0.0
    off_window_mask = (t >= meta["t1_flat_end"]) & (t <= meta["t2_rise"])
    v_ds_peak = float(np.max(v_sw[off_window_mask])) if np.any(off_window_mask) else 0.0
    v_ds_overshoot = v_ds_peak - meta["v_dc"]

    i_before_on_mask = (t >= meta["t1_flat_end"] - 20e-9) & (t <= meta["t1_flat_end"])
    i_test_actual = float(np.mean(i_d[i_before_on_mask])) if np.any(i_before_on_mask) else meta["i_test"]

    return {
        "e_on": e_on,
        "e_off": e_off,
        "v_ds_peak": v_ds_peak,
        "v_ds_overshoot": v_ds_overshoot,
        "i_test_actual": i_test_actual,
    }


def sweep_rg(
    device: GaNDevice,
    v_dc: float,
    i_test_list: list[float],
    rg_on_list: list[float],
    rg_off_list: list[float],
    l_loop: float,
    work_dir: str,
    ltspice_exe: str | None = None,
    lib_override: str | None = None,
) -> list[dict]:
    """Full sweep, returns a flat list of rows suitable for pandas.DataFrame / CSV, which
    switching_loss.SwitchingLossModel's lookup mode can then interpolate over."""
    rows = []
    for i_test in i_test_list:
        for rg_on in rg_on_list:
            for rg_off in rg_off_list:
                spec = DoublePulseSpec(
                    v_dc=v_dc, i_test=i_test, r_g_on=rg_on, r_g_off=rg_off, l_loop=l_loop
                )
                res = run_double_pulse(
                    device, spec, work_dir, ltspice_exe=ltspice_exe, lib_override=lib_override
                )
                rows.append(
                    {
                        "i_d": i_test,
                        "v_ds": v_dc,
                        "r_g_on": rg_on,
                        "r_g_off": rg_off,
                        "e_on": res.e_on,
                        "e_off": res.e_off,
                        "v_ds_overshoot": res.v_ds_overshoot,
                    }
                )
    return rows

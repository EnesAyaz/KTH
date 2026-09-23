"""Builds interpolating lookup functions from the two decoupled LTSpice double-pulse
sweeps (scripts/run_epc2361_sweep_v2.py): one for E_on(Id, Rg_on, L_loop) with Rg_off
held at a reference value, one for E_off/overshoot(Id, Rg_off, L_loop) with Rg_on held
at a reference value. Turn-on and turn-off are electrically decoupled in the double-pulse
gate-drive network (separate diode/resistor paths, see ltspice/double_pulse.py), so this
is a valid reduction of the true 4D (Id, Rg_on, Rg_off, L_loop) space into two clean,
non-degenerate 3D interpolation problems -- and it matches exactly how the design
optimizer queries these models (Rg_on and Rg_off are optimized independently, see
optimize.find_min_rg_off_for_overshoot).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Callable

import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator


def load_sweep_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [{k: float(v) for k, v in row.items()} for row in reader]


def save_sweep_csv(rows: list[dict], path: str) -> None:
    if not rows:
        raise ValueError("no rows to save")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _make_3d_lookup(pts: np.ndarray, values: np.ndarray):
    lin = LinearNDInterpolator(pts, values)
    near = NearestNDInterpolator(pts, values)

    def lookup(q_pt: np.ndarray) -> float:
        v = lin(q_pt)[0]
        if np.isnan(v):
            v = near(q_pt)[0]
        return float(v)

    return lookup


def build_eon_interpolator(rows: list[dict]) -> Callable[[float, float, float], float]:
    """rows from EPC2361_eon_sweep.csv (Rg_off held fixed). Returns eon(i_d, l_loop_nH,
    r_g_on) -> e_on (J), linear over the 3D (i_d, r_g_on, l_loop_nH) point cloud with
    nearest-neighbor fallback outside the convex hull."""
    pts = np.array([[r["i_d"], r["r_g_on"], r["l_loop_nH"]] for r in rows])
    e_on = np.array([r["e_on"] for r in rows])
    lookup = _make_3d_lookup(pts, e_on)

    def eon(i_d: float, l_loop_nH: float, r_g_on: float) -> float:
        return lookup(np.array([[i_d, r_g_on, l_loop_nH]]))

    return eon


def build_eoff_interpolator(rows: list[dict]) -> Callable[[float, float, float], tuple[float, float]]:
    """rows from EPC2361_eoff_sweep.csv (Rg_on held fixed). Returns
    eoff(i_d, l_loop_nH, r_g_off) -> (e_off (J), v_ds_overshoot (V))."""
    pts = np.array([[r["i_d"], r["r_g_off"], r["l_loop_nH"]] for r in rows])
    e_off = np.array([r["e_off"] for r in rows])
    overshoot = np.array([r["v_ds_overshoot"] for r in rows])
    lookup_e = _make_3d_lookup(pts, e_off)
    lookup_o = _make_3d_lookup(pts, overshoot)

    def eoff(i_d: float, l_loop_nH: float, r_g_off: float) -> tuple[float, float]:
        q = np.array([[i_d, r_g_off, l_loop_nH]])
        return lookup_e(q), lookup_o(q)

    return eoff

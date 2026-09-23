"""Switching loss model: hard-switched two-level leg, one Eon + one Eoff event per switch
per switching period, at whatever instantaneous leg current exists at that instant.

Two data sources, same interface:

- "analytical": scales the single datasheet reference point (device.sw_ref) linearly with
  Id and Vds, and with Rg via a gate-charge-limited switching-time argument
  (E_sw ~ (Rg + Rg_internal), i.e. switching time -- and therefore the V-I overlap energy
  -- grows roughly proportionally with total gate resistance in the Miller-plateau-limited
  regime). This is a coarse first-pass model: good enough to bound the design space before
  double-pulse data exists, NOT accurate for large Rg excursions or non-linear Coss effects.
  Does not depend on L_loop and cannot predict overshoot.

- "lookup": two DECOUPLED interpolators built from the LTSpice double-pulse sweeps
  (ltspice/lookup.build_eon_interpolator / build_eoff_interpolator): E_on(Id, L_loop, Rg_on)
  with Rg_off held at a fixed reference during that sweep, and E_off/overshoot(Id, L_loop,
  Rg_off) with Rg_on held at a fixed reference. This is valid because turn-on and turn-off
  current flow through electrically separate gate resistor paths in the double-pulse
  netlist -- Rg_on has no effect on the turn-off edge and vice versa -- and it is exactly
  how the optimizer needs to query the data, since Rg_on and Rg_off are optimized
  independently (optimize.py). Both Eon and Eoff already include the Coss charge/discharge
  energy naturally captured by the V*I overlap integral in the simulation -- do not add a
  separate Coss loss term on top of either mode, that would double count.

Total switching power for the leg is obtained by numerically averaging Eon(theta)+Eoff(theta)
over the fundamental cycle (current magnitude at each switching instant), multiplied by f_sw,
then doubled for the two switch positions (top+bottom each incur one Eon+Eoff per period).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from .devices import GaNDevice
from .modulation import LegOperatingPoint


@dataclass
class SwitchingLossResult:
    e_on_avg: float
    e_off_avg: float
    p_switching_per_switch: float
    p_switching_leg: float
    i_used_for_avg: float


def _analytical_energy(device: GaNDevice, i_d: float, v_ds: float, r_g_on: float, r_g_off: float):
    ref = device.sw_ref
    i_d = max(i_d, 0.0)
    i_scale = i_d / ref.i_d_test if ref.i_d_test else 0.0
    v_scale = v_ds / ref.v_ds_test if ref.v_ds_test else 0.0

    rg_on_total = r_g_on + device.r_g_internal
    rg_off_total = r_g_off + device.r_g_internal
    rg_on_test_total = ref.r_g_on_test + device.r_g_internal
    rg_off_test_total = ref.r_g_off_test + device.r_g_internal

    e_on = ref.e_on_test * i_scale * v_scale * (rg_on_total / rg_on_test_total)
    e_off = ref.e_off_test * i_scale * v_scale * (rg_off_total / rg_off_test_total)
    return max(e_on, 0.0), max(e_off, 0.0)


class SwitchingLossModel:
    def __init__(
        self,
        device: GaNDevice,
        mode: str = "analytical",
        eon_lookup_fn: Optional[Callable[[float, float, float], float]] = None,
        eoff_lookup_fn: Optional[Callable[[float, float, float], tuple[float, float]]] = None,
    ):
        """eon_lookup_fn(i_d, l_loop_nH, r_g_on) -> e_on (J).
        eoff_lookup_fn(i_d, l_loop_nH, r_g_off) -> (e_off (J), v_ds_overshoot (V)).
        Both required when mode == "lookup" (build via ltspice.lookup.build_eon_interpolator
        / build_eoff_interpolator)."""
        self.device = device
        self.mode = mode
        self.eon_lookup_fn = eon_lookup_fn
        self.eoff_lookup_fn = eoff_lookup_fn
        if mode == "lookup" and (eon_lookup_fn is None or eoff_lookup_fn is None):
            raise ValueError("mode='lookup' requires both eon_lookup_fn and eoff_lookup_fn")

    def energies(
        self, i_d: float, v_ds: float, r_g_on: float, r_g_off: float, l_loop_nH: float = 0.0
    ) -> tuple[float, float]:
        if self.mode == "analytical":
            return _analytical_energy(self.device, i_d, v_ds, r_g_on, r_g_off)
        e_on = self.eon_lookup_fn(i_d, l_loop_nH, r_g_on)
        e_off, _overshoot = self.eoff_lookup_fn(i_d, l_loop_nH, r_g_off)
        return e_on, e_off

    def overshoot(self, i_d: float, r_g_off: float, l_loop_nH: float) -> float:
        if self.mode == "lookup":
            _e_off, overshoot = self.eoff_lookup_fn(i_d, l_loop_nH, r_g_off)
            return overshoot
        raise RuntimeError("Overshoot is only available from a 'lookup' (LTSpice-derived) model")

    def leg_loss(
        self,
        op: LegOperatingPoint,
        v_dc: float,
        r_g_on: float,
        r_g_off: float,
        l_loop_nH: float = 0.0,
        n_parallel: int = 1,
        n_theta: int = 720,
    ) -> SwitchingLossResult:
        theta = np.linspace(0.0, 2.0 * math.pi, n_theta, endpoint=False)
        i_leg = op.i_pk * np.sin(theta - op.power_factor_angle)
        i_switch = np.abs(i_leg) / n_parallel

        e_on_arr = np.empty(n_theta)
        e_off_arr = np.empty(n_theta)
        for k in range(n_theta):
            e_on_arr[k], e_off_arr[k] = self.energies(
                i_switch[k], v_dc, r_g_on, r_g_off, l_loop_nH=l_loop_nH
            )

        e_on_avg = float(np.mean(e_on_arr))
        e_off_avg = float(np.mean(e_off_arr))

        p_per_device = op.f_sw * (e_on_avg + e_off_avg)
        p_switching_per_switch = n_parallel * p_per_device

        return SwitchingLossResult(
            e_on_avg=e_on_avg,
            e_off_avg=e_off_avg,
            p_switching_per_switch=p_switching_per_switch,
            p_switching_leg=2.0 * p_switching_per_switch,
            i_used_for_avg=float(np.mean(i_switch)),
        )

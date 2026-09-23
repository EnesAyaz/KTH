"""Conduction loss for one half-bridge building block (two switches, N parallel devices each).

Two additive terms per switch position (top/bottom), see modulation.py for the derivation:
  1. Synchronous channel conduction: R_ds_on(Tj) * I_rms_switch_sync^2
  2. Dead-time third-quadrant conduction: V_sd(I) * I, averaged over the dead-time windows
     and weighted by how much of the fundamental cycle is spent in dead time
     (duty_dead = 2 * f_sw * t_dead, i.e. two dead-time events per switching period).
"""

from __future__ import annotations

from dataclasses import dataclass

from .devices import GaNDevice
from .modulation import CurrentStress, LegOperatingPoint, leg_current_stress


@dataclass
class ConductionLossResult:
    p_sync_per_switch: float
    p_deadtime_per_switch: float
    p_total_per_switch: float
    p_total_leg: float
    duty_dead: float
    i_rms_switch_sync: float
    i_dead_avg_abs: float


def conduction_loss(
    device: GaNDevice,
    op: LegOperatingPoint,
    t_j_c: float,
    n_parallel: int = 1,
) -> ConductionLossResult:
    stress: CurrentStress = leg_current_stress(op)

    # Devices in parallel share current equally; per-device current stress scales by 1/N,
    # power in each device scales by 1/N^2, but there are N devices, so total power per
    # switch position scales by 1/N (assuming perfect current sharing).
    r_ds_on = device.r_ds_on(t_j_c)
    i_rms_sync_per_device = stress.i_rms_switch_sync / n_parallel
    p_sync_per_switch = n_parallel * r_ds_on * i_rms_sync_per_device**2

    duty_dead = 2.0 * op.f_sw * op.t_dead
    if duty_dead > 1.0:
        raise ValueError(
            f"Dead time too large for this f_sw: 2*f_sw*t_dead = {duty_dead:.3f} > 1"
        )
    i_dead_per_device = stress.i_dead_avg_abs_per_switch / n_parallel
    v_sd = device.v_sd(i_dead_per_device)
    p_deadtime_per_switch = n_parallel * duty_dead * v_sd * i_dead_per_device

    p_total_per_switch = p_sync_per_switch + p_deadtime_per_switch

    return ConductionLossResult(
        p_sync_per_switch=p_sync_per_switch,
        p_deadtime_per_switch=p_deadtime_per_switch,
        p_total_per_switch=p_total_per_switch,
        p_total_leg=2.0 * p_total_per_switch,
        duty_dead=duty_dead,
        i_rms_switch_sync=stress.i_rms_switch_sync,
        i_dead_avg_abs=stress.i_dead_avg_abs_per_switch,
    )

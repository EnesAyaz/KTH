"""Steady-state thermal network: junction -> case/board -> TIM -> heatsink -> ambient.

Full-load design point uses steady-state (DC) thermal resistances only; if you later need
transient/duty-cycled thermal behavior, extend with Z_th(t) (Foster/Cauer) curves from the
datasheet instead of lumped Rth. Kept intentionally simple (single-node-per-device, shared
heatsink) since the goal here is parallel-device-count and Tj feasibility screening, not a
full 3D thermal simulation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ThermalStack:
    r_th_jc: float          # from device datasheet, C/W, per device
    r_th_interface: float     # TIM / case-to-sink, C/W, per device (user-supplied)
    r_th_sink_amb: float      # heatsink-to-ambient, C/W, TOTAL for the shared heatsink
    t_ambient_c: float


@dataclass
class ThermalResult:
    t_junction_c: float
    t_case_c: float
    t_sink_c: float
    p_per_device: float
    n_parallel: int
    margin_c: float


def solve_junction_temp(
    stack: ThermalStack,
    p_total_per_switch_position: float,
    n_parallel: int,
    t_j_max: float,
) -> ThermalResult:
    """p_total_per_switch_position: conduction+switching loss for ONE switch position
    (top or bottom) of the leg, i.e. already summed over all N parallel devices at that
    position. Devices assumed to share current (and therefore loss) equally and to sit on
    one common heatsink whose R_th,sink-amb is specified for the whole assembly.
    """
    p_per_device = p_total_per_switch_position / n_parallel
    p_total = p_total_per_switch_position

    t_sink = stack.t_ambient_c + p_total * stack.r_th_sink_amb
    t_case = t_sink + p_per_device * stack.r_th_interface
    t_junction = t_case + p_per_device * stack.r_th_jc

    return ThermalResult(
        t_junction_c=t_junction,
        t_case_c=t_case,
        t_sink_c=t_sink,
        p_per_device=p_per_device,
        n_parallel=n_parallel,
        margin_c=t_j_max - t_junction,
    )


def min_parallel_devices_for_tj(
    stack: ThermalStack,
    p_total_per_switch_position_fn,
    t_j_max: float,
    t_j_margin_c: float,
    n_max: int = 12,
) -> tuple[int, ThermalResult]:
    """Smallest N (1..n_max) that keeps Tj <= t_j_max - t_j_margin_c.

    p_total_per_switch_position_fn(n_parallel) -> total loss (W) for that switch position
    at that N (loss itself may depend weakly on N through Rds_on(Tj) self-heating feedback,
    so this takes a function rather than a fixed number).
    """
    for n in range(1, n_max + 1):
        p_total = p_total_per_switch_position_fn(n)
        result = solve_junction_temp(stack, p_total, n, t_j_max)
        if result.t_junction_c <= (t_j_max - t_j_margin_c):
            return n, result
    raise RuntimeError(
        f"No N up to {n_max} keeps Tj below {t_j_max - t_j_margin_c:.1f} C; "
        "improve cooling (R_th,sink-amb) or reduce loss."
    )

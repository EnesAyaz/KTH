"""Top-level design-point search: for a given power/voltage/PF/efficiency spec, find the
highest switching frequency that (a) keeps Vds turn-off overshoot within the allowed
fraction of Vdc, (b) keeps the full-load loss budget implied by the efficiency target,
and (c) keeps Tj at or below the design ceiling -- and report how many parallel devices
per switch position that requires.

Rg_on and Rg_off are optimized independently (see find_min_rg_off_for_overshoot /
_optimal_rg_on): turn-off resistance is set by the overshoot constraint, turn-on
resistance has no overshoot penalty in this model and is therefore minimized directly
(see optimal_rg_on's docstring for the real-world caveat this simplification ignores).

Monotonicity relied on by the bisections below (both hold for a hard-switched GaN
half-bridge, see docs/derivations.md and the LTSpice sweep data itself):
  - increasing Rg_off -> slower turn-off edge -> lower overshoot, higher Eoff
  - increasing f_sw -> more switching events/s -> more switching loss (conduction loss is
    f_sw-independent in this model, see modulation.py)
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from typing import Optional

from .conduction_loss import conduction_loss
from .devices import GaNDevice
from .modulation import LegOperatingPoint, leg_peak_current_from_power
from .switching_loss import SwitchingLossModel
from .thermal import ThermalStack, solve_junction_temp


@dataclass
class DesignSpec:
    p_out_leg: float          # W, real power this half-bridge building block delivers
    v_dc: float              # V, DC link voltage
    v_rms_fund: float          # V, fundamental RMS output (phase) voltage this leg produces
    power_factor: float
    modulation_index: float
    efficiency_target: float    # e.g. 0.99, evaluated at full load
    t_dead: float
    t_ambient_c: float
    r_th_interface: float       # TIM/case-to-sink per device, C/W
    r_th_sink_amb: float        # heatsink-to-ambient, TOTAL for the assembly, C/W
    l_loop_nH: float             # power-loop stray inductance the design targets, nH
    t_j_ceiling_c: float = 125.0  # design ceiling -- device's recommended max for full
    # utilization (not the 150C absolute max with a margin subtracted from it)
    v_overshoot_max_frac: float = 0.2   # e.g. 0.2 => Vds peak <= 1.2 * Vdc
    svm: bool = False
    power_factor_angle: float = field(init=False)

    def __post_init__(self):
        self.power_factor_angle = math.acos(self.power_factor)


@dataclass
class DesignPointResult:
    f_sw: float
    r_g_on: float
    r_g_off: float
    n_parallel: int
    l_loop_nH: float
    p_cond_leg: float
    p_sw_leg: float
    p_total_leg: float
    p_budget_leg: float
    t_junction_c: float
    t_j_ceiling_c: float
    margin_c: float
    v_ds_overshoot: Optional[float]
    feasible: bool


def loss_budget(spec: DesignSpec) -> float:
    """Total allowed loss (both switch positions) at full load for the stated efficiency."""
    eta = spec.efficiency_target
    return spec.p_out_leg * (1.0 - eta) / eta


def evaluate_point(
    device: GaNDevice,
    spec: DesignSpec,
    f_sw: float,
    r_g_on: float,
    r_g_off: float,
    n_parallel: int,
    sw_model: SwitchingLossModel,
    l_loop_nH: Optional[float] = None,
    t_j_guess_c: Optional[float] = None,
) -> DesignPointResult:
    l_loop_nH = spec.l_loop_nH if l_loop_nH is None else l_loop_nH
    i_pk = leg_peak_current_from_power(spec.p_out_leg, spec.v_rms_fund, spec.power_factor)
    op = LegOperatingPoint(
        i_pk=i_pk,
        modulation_index=spec.modulation_index,
        power_factor_angle=spec.power_factor_angle,
        f_sw=f_sw,
        f_fund=0.0,
        t_dead=spec.t_dead,
        svm=spec.svm,
    )

    t_j = t_j_guess_c if t_j_guess_c is not None else device.t_j_op_recommended

    # One Newton-ish fixed-point pass on Tj (Rds_on depends on Tj, Tj depends on loss):
    # three iterations converge to <1 C for typical GaN temp coefficients.
    stack = ThermalStack(
        r_th_jc=device.r_th_jc,
        r_th_interface=spec.r_th_interface,
        r_th_sink_amb=spec.r_th_sink_amb,
        t_ambient_c=spec.t_ambient_c,
    )

    for _ in range(3):
        cond = conduction_loss(device, op, t_j, n_parallel=n_parallel)
        sw = sw_model.leg_loss(op, spec.v_dc, r_g_on, r_g_off, l_loop_nH=l_loop_nH, n_parallel=n_parallel)
        p_switch_position = cond.p_total_per_switch + sw.p_switching_per_switch
        th = solve_junction_temp(stack, p_switch_position, n_parallel, device.t_j_max)
        t_j = th.t_junction_c

    p_cond_leg = cond.p_total_leg
    p_sw_leg = sw.p_switching_leg
    p_total_leg = p_cond_leg + p_sw_leg
    budget = loss_budget(spec)

    overshoot = None
    if sw_model.mode == "lookup":
        i_peak_per_device = i_pk / n_parallel
        overshoot = sw_model.overshoot(i_peak_per_device, r_g_off, l_loop_nH)

    feasible = (p_total_leg <= budget) and (th.t_junction_c <= spec.t_j_ceiling_c)
    if overshoot is not None:
        feasible = feasible and (overshoot <= spec.v_overshoot_max_frac * spec.v_dc)

    return DesignPointResult(
        f_sw=f_sw,
        r_g_on=r_g_on,
        r_g_off=r_g_off,
        n_parallel=n_parallel,
        l_loop_nH=l_loop_nH,
        p_cond_leg=p_cond_leg,
        p_sw_leg=p_sw_leg,
        p_total_leg=p_total_leg,
        p_budget_leg=budget,
        t_junction_c=th.t_junction_c,
        t_j_ceiling_c=spec.t_j_ceiling_c,
        margin_c=spec.t_j_ceiling_c - th.t_junction_c,
        v_ds_overshoot=overshoot,
        feasible=feasible,
    )


def find_min_rg_off_for_overshoot(
    device: GaNDevice,
    spec: DesignSpec,
    sw_model: SwitchingLossModel,
    n_parallel: int,
    rg_off_bounds: tuple[float, float] = (0.5, 15.0),
    l_loop_nH: Optional[float] = None,
    tol: float = 0.1,
) -> float:
    """Bisects for the smallest Rg_off that keeps peak-current turn-off overshoot within
    spec.v_overshoot_max_frac * Vdc. Requires a 'lookup' (LTSpice-derived) switching-loss
    model. Rg_on plays no role here -- overshoot is set by the turn-off edge only (see
    switching_loss.py / ltspice/double_pulse.py's decoupled gate-drive paths)."""
    if sw_model.mode != "lookup":
        raise RuntimeError(
            "Overshoot-constrained Rg search needs sw_model.mode == 'lookup' "
            "(run the LTSpice double-pulse sweep first, see scripts/run_epc2361_sweep_v2.py)."
        )
    l_loop_nH = spec.l_loop_nH if l_loop_nH is None else l_loop_nH
    i_pk = leg_peak_current_from_power(spec.p_out_leg, spec.v_rms_fund, spec.power_factor)
    i_peak_per_device = i_pk / n_parallel
    limit = spec.v_overshoot_max_frac * spec.v_dc

    lo, hi = rg_off_bounds
    if sw_model.overshoot(i_peak_per_device, hi, l_loop_nH) > limit:
        raise RuntimeError(
            f"Even Rg_off={hi} ohm exceeds the overshoot limit at Id={i_peak_per_device:.1f} A, "
            f"L_loop={l_loop_nH} nH; widen rg_off_bounds, reduce L_loop, or relax "
            "v_overshoot_max_frac."
        )
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if sw_model.overshoot(i_peak_per_device, mid, l_loop_nH) <= limit:
            hi = mid
        else:
            lo = mid
    return hi


def optimal_rg_on(rg_on_bounds: tuple[float, float] = (0.5, 15.0)) -> float:
    """Rg_on has no overshoot penalty in this model (overshoot is governed by the turn-off
    edge only), and E_on increases monotonically with Rg_on in every LTSpice sweep point
    collected (see outputs/EPC2361_eon_sweep.csv) -- so the loss-minimizing choice is
    always the search floor.

    Real designs sometimes deliberately use a LARGER Rg_on than Rg_off regardless (e.g.
    Cooke & Rogers 2025 use 15 ohm source / 2 ohm sink) to slow dv/dt at turn-on and
    reduce the risk of Miller-induced parasitic turn-on (crosstalk) of the complementary
    device -- a failure mode this toolkit does not model. Treat this function's output as
    a pure switching-loss optimum, not a complete gate-drive recommendation; a false-
    turn-on / crosstalk check against the actual gate-driver pull-down strength and PCB
    layout is still required before finalizing Rg_on on real hardware.
    """
    return rg_on_bounds[0]


def find_max_fsw(
    device: GaNDevice,
    spec: DesignSpec,
    r_g_on: float,
    r_g_off: float,
    n_parallel: int,
    sw_model: SwitchingLossModel,
    fsw_bounds: tuple[float, float] = (10e3, 5e6),
    l_loop_nH: Optional[float] = None,
    tol_hz: float = 1e3,
) -> DesignPointResult:
    """Bisects for the max f_sw meeting the loss-budget and Tj constraints (monotonic:
    more switching events per second only adds loss)."""
    lo, hi = fsw_bounds
    lo_result = evaluate_point(device, spec, lo, r_g_on, r_g_off, n_parallel, sw_model, l_loop_nH=l_loop_nH)
    if not lo_result.feasible:
        return lo_result  # infeasible even at the lowest fsw -- report why, don't pretend

    best = lo_result
    while hi - lo > tol_hz:
        mid = 0.5 * (lo + hi)
        res = evaluate_point(device, spec, mid, r_g_on, r_g_off, n_parallel, sw_model, l_loop_nH=l_loop_nH)
        if res.feasible:
            best = res
            lo = mid
        else:
            hi = mid
    return best


def design_sweep_over_n(
    device: GaNDevice,
    spec: DesignSpec,
    sw_model: SwitchingLossModel,
    n_range: range = range(1, 9),
    rg_on_bounds: tuple[float, float] = (0.5, 15.0),
    rg_off_bounds: tuple[float, float] = (0.5, 15.0),
    fsw_bounds: tuple[float, float] = (10e3, 5e6),
    l_loop_nH: Optional[float] = None,
) -> list[DesignPointResult]:
    """For each candidate parallel-device count N: Rg_on = search floor (optimal_rg_on),
    Rg_off = smallest value meeting the overshoot limit (find_min_rg_off_for_overshoot),
    then the max f_sw meeting the loss/thermal budget at that (Rg_on, Rg_off) -- giving a
    fsw-vs-N trade-off table to pick from. An N for which no Rg_off in rg_off_bounds meets
    the overshoot limit (too much current for too few devices) is skipped, not fatal --
    printed to stderr so the caller can see why that row is missing."""
    results = []
    rg_on = optimal_rg_on(rg_on_bounds)
    for n in n_range:
        if sw_model.mode == "lookup":
            try:
                rg_off = find_min_rg_off_for_overshoot(
                    device, spec, sw_model, n, rg_off_bounds=rg_off_bounds, l_loop_nH=l_loop_nH
                )
            except RuntimeError as exc:
                print(f"N={n}: skipped, no feasible Rg_off -- {exc}", file=sys.stderr)
                continue
        else:
            rg_off = rg_off_bounds[0]
        result = find_max_fsw(
            device, spec, rg_on, rg_off, n, sw_model, fsw_bounds=fsw_bounds, l_loop_nH=l_loop_nH
        )
        results.append(result)
    return results

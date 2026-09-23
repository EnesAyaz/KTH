"""Sanity checks for the loss models -- not a validation against real hardware/LTSpice,
just checks the formulas behave the way the physics says they should."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spb_bb.conduction_loss import conduction_loss
from spb_bb.devices import load_device
from spb_bb.loop_inductance import estimate_loop_inductance
from spb_bb.modulation import LegOperatingPoint, casanellas_currents, leg_current_stress
from spb_bb.switching_loss import SwitchingLossModel

DEVICE = load_device("EXAMPLE_PLACEHOLDER")


def test_conduction_loss_independent_of_m_and_pf():
    """Synchronous GaN conduction loss (excluding dead-time term) should not depend on M
    or power-factor angle -- see modulation.py derivation."""
    base = LegOperatingPoint(
        i_pk=40.0, modulation_index=0.9, power_factor_angle=0.0,
        f_sw=100e3, f_fund=50.0, t_dead=0.0,
    )
    shifted = LegOperatingPoint(
        i_pk=40.0, modulation_index=0.4, power_factor_angle=math.radians(30),
        f_sw=100e3, f_fund=50.0, t_dead=0.0,
    )
    r1 = conduction_loss(DEVICE, base, t_j_c=100.0)
    r2 = conduction_loss(DEVICE, shifted, t_j_c=100.0)
    assert math.isclose(r1.p_sync_per_switch, r2.p_sync_per_switch, rel_tol=1e-9)


def test_conduction_loss_scales_inversely_with_n_parallel():
    """The resistive (synchronous) term scales exactly as 1/N (I/N through N devices).
    The dead-time term does NOT scale as cleanly because V_sd = v_sd0 + r_sd*I has a
    current-independent offset v_sd0: total dead-time loss = duty*(v_sd0*I + r_sd*I^2/N),
    so only the r_sd*I^2 piece benefits from paralleling. Total loss per switch position
    is still strictly lower with more parallel devices, just not exactly halved."""
    op = LegOperatingPoint(
        i_pk=40.0, modulation_index=0.9, power_factor_angle=0.0,
        f_sw=100e3, f_fund=50.0, t_dead=20e-9,
    )
    r1 = conduction_loss(DEVICE, op, t_j_c=100.0, n_parallel=1)
    r2 = conduction_loss(DEVICE, op, t_j_c=100.0, n_parallel=2)
    assert r2.p_total_per_switch < r1.p_total_per_switch
    assert math.isclose(r2.p_sync_per_switch, r1.p_sync_per_switch / 2, rel_tol=1e-6)


def test_switching_loss_scales_with_fsw():
    op_lo = LegOperatingPoint(
        i_pk=40.0, modulation_index=0.9, power_factor_angle=0.0,
        f_sw=100e3, f_fund=50.0, t_dead=20e-9,
    )
    op_hi = LegOperatingPoint(
        i_pk=40.0, modulation_index=0.9, power_factor_angle=0.0,
        f_sw=200e3, f_fund=50.0, t_dead=20e-9,
    )
    model = SwitchingLossModel(DEVICE, mode="analytical")
    r_lo = model.leg_loss(op_lo, v_dc=400.0, r_g_on=5.0, r_g_off=5.0)
    r_hi = model.leg_loss(op_hi, v_dc=400.0, r_g_on=5.0, r_g_off=5.0)
    assert math.isclose(r_hi.p_switching_leg, 2 * r_lo.p_switching_leg, rel_tol=1e-6)


def test_switching_loss_increases_with_rg():
    op = LegOperatingPoint(
        i_pk=40.0, modulation_index=0.9, power_factor_angle=0.0,
        f_sw=100e3, f_fund=50.0, t_dead=20e-9,
    )
    model = SwitchingLossModel(DEVICE, mode="analytical")
    low_rg = model.leg_loss(op, v_dc=400.0, r_g_on=2.0, r_g_off=2.0)
    high_rg = model.leg_loss(op, v_dc=400.0, r_g_on=10.0, r_g_off=10.0)
    assert high_rg.p_switching_leg > low_rg.p_switching_leg


def test_loop_inductance_positive_and_reasonable():
    l_pp = estimate_loop_inductance("parallel_plate", l_mm=15, w_mm=8, h_or_s_mm=0.2)
    # busbar_pair models two separate conductors with comparable width/separation, not a
    # tightly-coupled plane pair (that's parallel_plate's regime) -- use a valid geometry.
    l_bb = estimate_loop_inductance("busbar_pair", l_mm=15, w_mm=5, h_or_s_mm=8)
    assert 0 < l_pp < 50e-9
    assert 0 < l_bb < 50e-9


def test_casanellas_matches_synchronous_average_at_unity_pf_high_m():
    stress = leg_current_stress(
        LegOperatingPoint(i_pk=40.0, modulation_index=1.0, power_factor_angle=0.0,
                           f_sw=100e3, f_fund=50.0, t_dead=0.0)
    )
    cas = casanellas_currents(40.0, m=1.0, phi=0.0)
    # Sanity: Casanellas switch+diode current should reconstruct roughly the full leg RMS
    combined_ms = cas["i_rms_switch"] ** 2 + cas["i_rms_diode"] ** 2
    assert math.isclose(combined_ms, stress.i_rms_leg**2 / 2, rel_tol=0.3)

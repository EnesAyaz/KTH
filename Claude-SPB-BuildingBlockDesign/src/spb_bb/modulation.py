"""Fundamental-cycle current-stress model for one half-bridge leg (SPWM or SVM).

This building block is one phase-leg of a multicell/modular polyphase bridge, driven by
naturally-sampled sinusoidal PWM (SPWM) or space-vector modulation (SVM), complementary
switching with a fixed dead time t_dead. GaN e-mode HEMTs behave as a *symmetric*
resistive channel (R_ds_on) in both current directions whenever they are actively gated
on (true synchronous rectification) -- unlike a Si IGBT + freewheel diode pair, whose
forward drops differ. Only during the dead-time gap (both gates off) does the leg fall
back to third-quadrant ("diode-like") conduction with the device's V_sd(I) curve.

Current reference for one leg (top-switch duty referenced to the leg midpoint):
    d_T(theta) = 0.5 + 0.5 * M * sin(theta)                (SPWM, linear region, M in [0,1])
    i(theta)   = I_pk * sin(theta - phi)                    (phi = current-vs-voltage angle,
                                                               cos(phi) = displacement power factor)

Synchronous (gated-on) conduction loss per switch, integrated over a full fundamental
cycle 2*pi, works out to be independent of M and phi:
    P_sync_per_switch = R_ds_on * I_pk^2 / 4 = R_ds_on * I_rms_leg^2 / 2
This is because d_T(theta) only contains a DC term and a 1st-harmonic term, while
i(theta)^2 only contains a DC term and a 2nd-harmonic term; the cross term integrates to
zero over 2*pi. (Verified by direct integration -- see docs/derivations.md.)

Dead-time third-quadrant conduction is added on top, split evenly between the two
switches by symmetry (i(theta) > 0 for exactly half the cycle, independent of phi).

For SVM (third-harmonic injection), d_T(theta) = 0.5 + 0.5*M*[sin(theta) + (1/6)*sin(3*theta)],
which keeps d_T in [0,1] for M up to 2/sqrt(3) ~= 1.1547 (the SVM hexagon boundary) instead
of SPWM's M <= 1. The injected 3rd-harmonic term is ALSO orthogonal to i(theta)^2's DC/2nd-
harmonic content over a full 2*pi cycle, so P_sync_per_switch = R_ds_on * I_pk^2 / 4 still
holds exactly for SVM too -- only the valid range of M changes. `max_valid_m(svm)` enforces
this bound; `leg_current_stress` does not itself need d_T(theta) since the closed form
above is independent of it.

Reference: F. Casanellas, "Losses in PWM inverters using IGBTs," IEE Proc. Electr. Power
Appl., 1994 (classical Si IGBT/diode form, kept here as `casanellas_currents` for
cross-checking against non-synchronous / diode-emulation operation).
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class LegOperatingPoint:
    i_pk: float          # peak fundamental leg (phase) current, A
    modulation_index: float  # M, 0..1 (linear region)
    power_factor_angle: float  # phi, rad (cos(phi) = displacement PF)
    f_sw: float           # switching frequency, Hz
    f_fund: float          # fundamental output frequency, Hz
    t_dead: float          # dead time, s
    svm: bool = False


@dataclass
class CurrentStress:
    i_rms_leg: float
    i_avg_abs_leg: float       # (2/pi) * I_pk, average of |i(theta)|
    i_rms_switch_sync: float    # RMS current a single switch's channel carries while gated on
    i_dead_avg_abs_per_switch: float  # average |current| during this switch's dead-time intervals


def max_valid_m(svm: bool) -> float:
    """Linear-modulation ceiling: 1.0 for SPWM, 2/sqrt(3) ~= 1.1547 for SVM/third-harmonic
    injection (the hexagon boundary) -- see module docstring."""
    return 2.0 / math.sqrt(3.0) if svm else 1.0


def leg_current_stress(op: LegOperatingPoint) -> CurrentStress:
    limit = max_valid_m(op.svm)
    if not (0.0 <= op.modulation_index <= limit):
        raise ValueError(
            f"modulation_index={op.modulation_index:.4f} exceeds the linear-region limit "
            f"({limit:.4f} for {'SVM' if op.svm else 'SPWM'}) -- this model doesn't cover "
            f"overmodulation."
        )
    i_rms_leg = op.i_pk / math.sqrt(2.0)
    i_avg_abs_leg = (2.0 / math.pi) * op.i_pk

    # Synchronous per-switch RMS current: half the leg's mean-square current is dissipated
    # in each switch (see module docstring), so effective RMS through one switch's channel:
    i_rms_switch_sync = op.i_pk / 2.0

    # Dead-time conduction current magnitude, averaged over the half-cycle the switch is
    # exposed to it: same (2/pi)*I_pk average-of-|sine| result restricted to a half cycle
    # by symmetry equals the full-cycle average of |i|.
    i_dead_avg_abs_per_switch = i_avg_abs_leg

    return CurrentStress(
        i_rms_leg=i_rms_leg,
        i_avg_abs_leg=i_avg_abs_leg,
        i_rms_switch_sync=i_rms_switch_sync,
        i_dead_avg_abs_per_switch=i_dead_avg_abs_per_switch,
    )


def casanellas_currents(i_pk: float, m: float, phi: float) -> dict:
    """Classical asymmetric switch/diode RMS & average currents (Casanellas 1994).

    Only valid for non-synchronous (diode-emulation) operation where the switch and its
    freewheel path have genuinely different V-I characteristics. Provided for
    cross-checking; the default GaN synchronous model above is `leg_current_stress`.
    """
    cos_phi = math.cos(phi)
    i_rms_t = i_pk * math.sqrt(max(1.0 / 8.0 + (m * cos_phi) / (3.0 * math.pi), 0.0))
    i_rms_d = i_pk * math.sqrt(max(1.0 / 8.0 - (m * cos_phi) / (3.0 * math.pi), 0.0))
    i_avg_t = i_pk / (2.0 * math.pi) + (m * i_pk * cos_phi) / 8.0
    i_avg_d = i_pk / (2.0 * math.pi) - (m * i_pk * cos_phi) / 8.0
    return {
        "i_rms_switch": i_rms_t,
        "i_rms_diode": i_rms_d,
        "i_avg_switch": i_avg_t,
        "i_avg_diode": i_avg_d,
    }


def leg_peak_current_from_power(p_out_leg: float, v_rms_fund: float, power_factor: float) -> float:
    """I_pk for this leg given the per-leg real power it delivers, fundamental RMS phase
    voltage and displacement power factor: P = V_rms * I_rms * PF, I_pk = sqrt(2) * I_rms.
    """
    i_rms = p_out_leg / (v_rms_fund * power_factor)
    return math.sqrt(2.0) * i_rms

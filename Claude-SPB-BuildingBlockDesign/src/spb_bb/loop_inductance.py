"""First-pass power-loop stray inductance estimate for the DC-link decoupling loop.

This feeds the LTSpice double-pulse test (as L_loop in series with the switch node) so
Eon/Eoff and Vds overshoot vs Rg are evaluated with realistic parasitics rather than an
ideal source. Two interchangeable models are provided; both are analytical first-pass
estimates standard in GaN layout practice (e.g. EPC AN014-style loop-area reasoning), NOT
a replacement for a field solver (Q3D/Clever/PEEC extraction) or a VNA/ringing
measurement on the real board -- treat this as a starting point to bound the double-pulse
sweep, then calibrate against measured overshoot once hardware exists.

1. `parallel_plate_loop_inductance`: decoupling-loop formula for two closely spaced planes
   (or a tight trace-over-plane pair) forming the commutation loop between the DC-link
   capacitor and the switch node:
       L = mu0 * h * l / w
   where h = dielectric thickness between the loop-forming copper (power/return),
         l = loop length (cap to device),
         w = trace/plane width carrying the loop current.
   Good when the loop is realized as overlapping copper pours (low-inductance layout).

2. `busbar_pair_inductance`: two parallel rectangular busbars/traces side by side or
   stacked with a gap, using the standard partial-inductance approximation for a pair of
   coplanar or stacked conductors of width w, thickness t, separation s, length l.
"""

from __future__ import annotations

import math

MU0 = 4.0 * math.pi * 1e-7


def parallel_plate_loop_inductance(h_m: float, l_m: float, w_m: float) -> float:
    """L = mu0 * h * l / w for an overlapping-plane (power/return) commutation loop."""
    if w_m <= 0:
        raise ValueError("width must be > 0")
    return MU0 * h_m * l_m / w_m


def busbar_pair_inductance(l_m: float, w_m: float, s_m: float, t_m: float = 0.0) -> float:
    """Partial-inductance estimate for two parallel go/return conductors of length l,
    width w, edge-to-edge separation s (stacked or coplanar), thickness t.

    Uses the common closed-form for a pair of parallel round-ish/flat conductors:
        L ~= (mu0 * l / pi) * [ln(2*s/w) + 0.25 + t/(3*s)]   (s >> t, s comparable to w)
    Falls back gracefully for the typical GaN power-loop regime (s, w both ~1-5 mm).
    """
    if s_m <= 0 or w_m <= 0 or l_m <= 0:
        raise ValueError("l, w, s must all be > 0")
    core = math.log(2.0 * s_m / w_m) + 0.25 + t_m / (3.0 * s_m)
    if core <= 0:
        raise ValueError(
            f"busbar_pair_inductance is only valid for separation s roughly > 0.4*w "
            f"(got s={s_m * 1e3:.2f} mm, w={w_m * 1e3:.2f} mm, which gives a non-physical "
            f"negative result). For tightly-coupled close-spaced planes/traces "
            f"(s << w), use parallel_plate_loop_inductance instead."
        )
    return (MU0 * l_m / math.pi) * core


def estimate_loop_inductance(
    method: str,
    l_mm: float,
    w_mm: float,
    h_or_s_mm: float,
    t_mm: float = 0.035,
) -> float:
    """Convenience wrapper taking mm inputs, returning L in H.

    method: "parallel_plate" (h_or_s_mm = dielectric thickness between planes) or
            "busbar_pair" (h_or_s_mm = edge separation between go/return conductors).
    """
    l_m, w_m, hs_m, t_m = l_mm * 1e-3, w_mm * 1e-3, h_or_s_mm * 1e-3, t_mm * 1e-3
    if method == "parallel_plate":
        return parallel_plate_loop_inductance(hs_m, l_m, w_m)
    if method == "busbar_pair":
        return busbar_pair_inductance(l_m, w_m, hs_m, t_m)
    raise ValueError(f"Unknown method: {method!r}, expected 'parallel_plate' or 'busbar_pair'")

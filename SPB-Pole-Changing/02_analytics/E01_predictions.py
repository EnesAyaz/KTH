"""E01-P - predictions for the bench test of the cell-power pulsation law (board/experiments/E01_cell_pulsation.md).

Run from repo root:  python 02_analytics/E01_predictions.py
Output: 02_analytics/results/E01_predictions.json

Plug in scope data:
    from E01_predictions import pulsation_from_phasors
    pulsation_from_phasors(V_a, I_a, V_b, I_b, V_dc, C, f_a, f_b, Z_source=None)
with V_a[k], I_a[k] = complex PEAK phasors of leg k pole voltage (any common reference, e.g. DC-) and leg current
at f_a (FFT bin), and V_b, I_b at f_b. No symmetry is assumed: per-leg products are summed.

Cell power  p(t) = sum_k v_k(t) i_k(t). With v_k = Re(V_ak e^{j w_a t} + V_bk e^{j w_b t}), i_k likewise:
  component at f_a + f_b:   P_sum  = | 1/2 sum_k (V_ak I_bk + V_bk I_ak) |
  component at |f_a - f_b|: P_diff = | 1/2 sum_k (V_ak conj(I_bk) + conj(V_bk) I_ak) |
For a symmetric cell with orders a, b (leg k lagging by k 2 pi a/m): P_sum = (m/2)|V_a I_b + V_b I_a| if m | (a+b), else 0;
P_diff = (m/2)|V_a conj(I_b) + conj(V_b) I_a| if m | (a-b), else 0. A zero-sequence voltage (neutral shift, pole-to-DC-
reference) adds v_0 sum_k i_k = 0, so pole voltages can be used directly.
DC-link ripple: the cell draws i_p = P/V_dc at f; if the source is decoupled (Z_s >> 1/(w C)), dV_pk = P / (2 pi f V_dc C);
in general dV_pk = (P/V_dc) |Z_C || Z_s|.
"""
from __future__ import annotations

import datetime as _dt
import itertools
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "02_analytics", "results", "E01_predictions.json")


# ----------------------------------------------------------------------------------
def pulsation_from_phasors(V_a, I_a, V_b, I_b, V_dc, C, f_a, f_b, Z_source=None):
    V_a, I_a, V_b, I_b = map(lambda x: np.asarray(x, complex), (V_a, I_a, V_b, I_b))
    P_sum = abs(0.5 * np.sum(V_a * I_b + V_b * I_a))
    P_diff = abs(0.5 * np.sum(V_a * np.conj(I_b) + np.conj(V_b) * I_a))
    out = {}
    for name, P, f in (("sum", P_sum, f_a + f_b), ("diff", P_diff, abs(f_a - f_b))):
        if f <= 0:
            out[name] = dict(P_W=P, f_Hz=f, note="f = 0: DC term (average power exchange), not a ripple")
            continue
        Zc = 1 / (1j * 2 * math.pi * f * C)
        Z = Zc if Z_source is None else Zc * Z_source / (Zc + Z_source)
        out[name] = dict(P_W=P, f_Hz=f, I_pulse_A=P / V_dc, dV_pk_V=P / V_dc * abs(Z), dV_pk_pct=100 * P / V_dc * abs(Z) / V_dc)
    return out


def symmetric_phasors(m, order, I_pk, f, R, L, phase=0.0, dR=None, dL=None):
    """Leg current phasors (peak) of one order and the load voltage phasors V_k = Z_k I_k."""
    k = np.arange(m)
    I = I_pk * np.exp(1j * (phase - k * 2 * math.pi * order / m))
    Rk = R * (1 + (dR if dR is not None else 0.0))
    Lk = L * (1 + (dL if dL is not None else 0.0))
    V = (Rk + 1j * 2 * math.pi * f * Lk) * I
    return V, I


def law(m, a, b):
    return dict(sum_term=(a + b) % m == 0, diff_term=(a - b) % m == 0,
                injectable=(a % m != 0 and b % m != 0))


def modulation_ok(m, V_pk_sum, V_dc):
    km = 1 / (2 * math.cos(math.pi / (2 * m))) if m % 2 else 0.5
    return bool(V_pk_sum <= km * V_dc), km * V_dc


# ----------------------------------------------------------------------------------
# Time-domain check with per-leg RL, dead time and imperfect current control
# ----------------------------------------------------------------------------------
def time_domain(m, a, b, I_pk, f_a, f_b, R, L, V_dc, dR=None, dL=None, t_dead=0.0, f_sw=20e3, rejection=1.0, V_sd=1.0,
                T=1.0, fs=100e3):
    """Returns amplitudes of cell power at f_a+f_b and |f_a-f_b| (W).
    Dead time: average pole-voltage error -V_dc t_d f_sw sign(i_k) per leg; a fraction (1 - rejection) of it is not
    compensated by the current loop and drives a current error through the leg impedance (its zero-sequence part
    only moves the neutral). Dead-time diode conduction loss V_sd 2 t_d f_sw |i_k| is added to the cell power."""
    t = np.arange(int(T * fs)) / fs
    k = np.arange(m)[:, None]
    Rk = R * (1 + (np.zeros(m) if dR is None else np.asarray(dR)))[:, None]
    Lk = L * (1 + (np.zeros(m) if dL is None else np.asarray(dL)))[:, None]
    i = I_pk * np.cos(2 * math.pi * f_a * t - k * 2 * math.pi * a / m) + I_pk * np.cos(2 * math.pi * f_b * t - k * 2 * math.pi * b / m)
    if np.any(np.asarray(t_dead) > 0) and rejection < 1.0:
        tdk = np.broadcast_to(np.asarray(t_dead, dtype=float).reshape(-1, 1) if np.ndim(t_dead) else np.full((m, 1), t_dead), (m, 1))
        e = -V_dc * tdk * f_sw * np.sign(i)
        e = e - e.mean(axis=0, keepdims=True)                     # zero-sequence part drives no current
        E = np.fft.rfft(e, axis=1)
        fr = np.fft.rfftfreq(t.size, 1 / fs)
        dI = (1 - rejection) * E / (Rk + 1j * 2 * math.pi * fr[None, :] * Lk)
        dI[:, 0] = 0
        di = np.fft.irfft(dI, n=t.size, axis=1)
        di -= di.mean(axis=0, keepdims=True)                       # isolated neutral: currents sum to zero
        i = i + di
    didt = np.gradient(i, 1 / fs, axis=1)
    v = Rk * i + Lk * didt
    p = np.sum(v * i, axis=0)
    if np.any(np.asarray(t_dead) > 0):
        tdk = np.asarray(t_dead, dtype=float).reshape(-1, 1) if np.ndim(t_dead) else t_dead
        p = p + np.sum(V_sd * 2 * tdk * f_sw * np.abs(i), axis=0)
    P = np.fft.rfft(p) / t.size * 2
    fr = np.fft.rfftfreq(t.size, 1 / fs)

    def amp(f):
        return float(np.abs(P[np.argmin(np.abs(fr - f))]))
    return dict(P_sum_W=amp(f_a + f_b), P_diff_W=amp(abs(f_a - f_b)), P_mean_W=float(p.mean()))


# ----------------------------------------------------------------------------------
def main():
    f_a, f_b = 50.0, 30.0
    loads = [(1.0, 2e-3), (1.0, 5e-3), (2.0, 2e-3), (2.0, 5e-3)]
    Vdcs = [48.0, 75.0, 100.0]
    C_nom = 1e-3
    C_list = [0.5e-3, 1e-3, 2e-3]
    points = [dict(cell="3-leg", m=3, a=1, b=-1, label="(1,-1) pos + neg sequence"),
              dict(cell="3-leg", m=3, a=1, b=1, label="(1,1) control: same order, f_a != f_b"),
              dict(cell="5-leg", m=5, a=1, b=2, label="(1,2) law: zero cross-pulsation"),
              dict(cell="5-leg", m=5, a=1, b=-1, label="(1,-1) m=5 control: should pulsate at f_a+f_b"),
              dict(cell="5-leg", m=5, a=1, b=1, label="(1,1) m=5 control: should pulsate at |f_a-f_b|")]
    table = []
    for pt in points:
        for I_pk in (5.0, 10.0):
            for R, L in loads:
                Va, Ia = symmetric_phasors(pt["m"], pt["a"], I_pk, f_a, R, L)
                Vb, Ib = symmetric_phasors(pt["m"], pt["b"], I_pk, f_b, R, L)
                Vpk_sum = abs(Va[0]) + abs(Vb[0])
                for Vdc in Vdcs:
                    ok, Vlim = modulation_ok(pt["m"], Vpk_sum, Vdc)
                    pr = pulsation_from_phasors(Va, Ia, Vb, Ib, Vdc, C_nom, f_a, f_b)
                    table.append(dict(cell=pt["cell"], m=pt["m"], a=pt["a"], b=pt["b"], label=pt["label"], I_pk_A=I_pk, R_ohm=R, L_mH=L * 1e3,
                                      V_dc_V=Vdc, C_mF=C_nom * 1e3, leg_V_pk_needed_V=Vpk_sum, leg_V_pk_limit_V=Vlim, modulation_feasible=ok,
                                      law=law(pt["m"], pt["a"], pt["b"]),
                                      P_avg_W=float(pt["m"] / 2 * R * 2 * I_pk ** 2),
                                      at_f_sum=pr["sum"], at_f_diff=pr["diff"],
                                      dV_pk_V_vs_C={f"{c * 1e3:g}mF": dict(sum=pr["sum"]["P_W"] / Vdc / (2 * math.pi * (f_a + f_b) * c),
                                                                          diff=pr["diff"]["P_W"] / Vdc / (2 * math.pi * abs(f_a - f_b) * c))
                                                    for c in C_list}))
    # time-domain cross-check (symmetric load) for one point per case
    td = {}
    for pt in points:
        r = time_domain(pt["m"], pt["a"], pt["b"], 10.0, f_a, f_b, 2.0, 5e-3, 100.0)
        Va, Ia = symmetric_phasors(pt["m"], pt["a"], 10.0, f_a, 2.0, 5e-3)
        Vb, Ib = symmetric_phasors(pt["m"], pt["b"], 10.0, f_b, 2.0, 5e-3)
        cf = pulsation_from_phasors(Va, Ia, Vb, Ib, 100.0, C_nom, f_a, f_b)
        td[f"m{pt['m']}_({pt['a']},{pt['b']})"] = dict(time_domain=r, closed_form_P_sum_W=cf["sum"]["P_W"], closed_form_P_diff_W=cf["diff"]["P_W"])

    # zero-pulsation pairs for m = 5
    pairs5 = []
    for a, b in itertools.product(range(-4, 5), repeat=2):
        if a == 0 or b == 0 or abs(a) > abs(b) or (abs(a) == abs(b) and a > b):
            continue
        lw = law(5, a, b)
        if lw["injectable"]:
            pairs5.append(dict(a=a, b=b, pulsation_free=not (lw["sum_term"] or lw["diff_term"]),
                               pulsates_at=("f_a+f_b" if lw["sum_term"] else "") + (" |f_a-f_b|" if lw["diff_term"] else "")))

    # sensitivities (m = 5, (1,2) vs m = 3, (1,-1); I = 10 A, R = 2, L = 5 mH, V_dc = 100 V)
    rng = np.random.default_rng(1)
    ref3 = time_domain(3, 1, -1, 10.0, f_a, f_b, 2.0, 5e-3, 100.0)["P_sum_W"]
    imb = []
    for trial in range(40):
        dR, dL = rng.uniform(-0.05, 0.05, 5), rng.uniform(-0.05, 0.05, 5)
        r = time_domain(5, 1, 2, 10.0, f_a, f_b, 2.0, 5e-3, 100.0, dR=dR, dL=dL)
        imb.append(max(r["P_sum_W"], r["P_diff_W"]))
    imb = np.array(imb)
    worst = time_domain(5, 1, 2, 10.0, f_a, f_b, 2.0, 5e-3, 100.0, dR=[0.05, -0.05, 0.05, -0.05, 0.05], dL=[0.05, -0.05, 0.05, -0.05, 0.05])
    dead = {}
    for td_ns in (100, 300, 1000):
        for rej in (0.0, 0.5, 0.9, 0.99):
            r5 = time_domain(5, 1, 2, 10.0, f_a, f_b, 2.0, 5e-3, 100.0, t_dead=td_ns * 1e-9, f_sw=20e3, rejection=rej)
            r3 = time_domain(3, 1, -1, 10.0, f_a, f_b, 2.0, 5e-3, 100.0, t_dead=td_ns * 1e-9, f_sw=20e3, rejection=rej)
            dead[f"td{td_ns}ns_rejection{rej}"] = dict(m5_12_P_sum_W=r5["P_sum_W"], m5_12_P_diff_W=r5["P_diff_W"],
                                                     m3_1m1_P_sum_W=r3["P_sum_W"],
                                                     m5_residual_over_m3=max(r5["P_sum_W"], r5["P_diff_W"]) / r3["P_sum_W"],
                                                     passes_10pct_criterion=bool(max(r5["P_sum_W"], r5["P_diff_W"]) < 0.1 * r3["P_sum_W"]))
    asym = {}
    for f_bb in (30.0, 31.0):
        r3 = time_domain(3, 1, -1, 10.0, f_a, f_bb, 2.0, 5e-3, 100.0)["P_sum_W"]
        for spread in (0.2, 0.5):
            tdl = 300e-9 * (1 + spread * np.array([1, -1, 0.5, -0.5, 0.0]))
            r5 = time_domain(5, 1, 2, 10.0, f_a, f_bb, 2.0, 5e-3, 100.0, t_dead=tdl, f_sw=20e3, rejection=0.0)
            asym[f"f_b{f_bb:g}Hz_spread{int(spread * 100)}pct"] = dict(m5_P_sum_W=r5["P_sum_W"], m5_P_diff_W=r5["P_diff_W"],
                                                                      residual_over_m3=max(r5["P_sum_W"], r5["P_diff_W"]) / r3,
                                                                      passes_10pct_criterion=bool(max(r5["P_sum_W"], r5["P_diff_W"]) < 0.1 * r3))
    sens = dict(
        dead_time_asymmetric=dict(cases=asym, note="per-leg dead time 300 ns x (1 + spread [1,-1,0.5,-0.5,0]), no current-loop rejection (worst)"),
        frequency_choice=dict(note="With f_a = 50, f_b = 30 Hz the combination -2 f_a + 6 f_b also equals f_a + f_b = 80 Hz, with order -2a + 6b = 10 "
                                   "(divisible by 5), so leg nonlinearities can alias onto the 80 Hz bin. Prefer incommensurate test frequencies, "
                                   "e.g. f_b = 31 Hz (sum 81 Hz, difference 19 Hz), and FFT windows that are integer multiples of 1/gcd."),
        reference_m3_P_sum_W=ref3,
        capacitance="dV_pk scales as 1/C (see dV_pk_V_vs_C per point): C = 0.5 / 1 / 2 mF -> x2 / x1 / x0.5",
        load_imbalance_pm5pct=dict(m5_12_residual_W_mean=float(imb.mean()), m5_12_residual_W_max=float(imb.max()),
                                   alternating_worst_W=max(worst["P_sum_W"], worst["P_diff_W"]),
                                   residual_over_m3=float(imb.max() / ref3),
                                   passes_10pct_criterion=bool(imb.max() < 0.1 * ref3),
                                   note="current-controlled legs: currents stay ideal, the leg voltages differ by Z_k -> residual cross power"),
        dead_time=dict(cases=dead, f_sw_Hz=20e3, V_sd_V=1.0,
                       note="rejection = fraction of the dead-time voltage error removed by the current loop (1 = ideal). The uncompensated "
                            "part creates current harmonics at combination frequencies; their cross power with the main voltages is the "
                            "main measurement risk for the m = 5 null. Diode-conduction loss pulsation is included but is small."),
        source_decoupling=dict(note="The pulsating current P/V_dc splits between C and the DC source. A stiff lab supply absorbs part of it and "
                                    "lowers dV. Either decouple the source (series L or R with |Z_s| >> 1/(2 pi f C): at 20 Hz, C = 1 mF -> "
                                    "1/(wC) = 8 Ohm) or measure both the capacitor current and the source current and compare their sum with P/V_dc. "
                                    "The pass criterion should use the current, not dV, if the source is not decoupled."))
    res = dict(meta=dict(script="02_analytics/E01_predictions.py", task="E01-P", date=_dt.date.today().isoformat(),
                         plan="board/experiments/E01_cell_pulsation.md",
                         conventions="I_a, I_b are PEAK leg-current amplitudes (as written in the plan's reference i_k = I_a cos(...)); "
                                     "phasors are peak; the RL load is per leg, star, isolated neutral; a, b are signed orders "
                                     "(leg k lags k 2 pi a / m)."),
               closed_form=dict(
                   general_measured_data="P_sum(f_a+f_b) = |1/2 sum_k (V_ak I_bk + V_bk I_ak)|, P_diff(|f_a-f_b|) = |1/2 sum_k (V_ak conj(I_bk) + conj(V_bk) I_ak)|; "
                                         "V, I = complex peak FFT phasors of leg pole voltage and leg current; function pulsation_from_phasors()",
                   symmetric="P_sum = (m/2)|V_a I_b + V_b I_a| if m | (a+b) else 0; P_diff = (m/2)|V_a conj(I_b) + conj(V_b) I_a| if m | (a-b) else 0; "
                             "for an RL load V = Z(f) I",
                   ripple="decoupled source: dV_pk = P/(2 pi f V_dc C); general: dV_pk = (P/V_dc)|Z_C || Z_source|",
                   upper_bound="P <= (m/2)(V_a I_b + V_b I_a) (aligned phasors)"),
               predictions=table, time_domain_check=td, m5_pairs=pairs5,
               m5_zero_pulsation_pairs=[(p["a"], p["b"]) for p in pairs5 if p["pulsation_free"]],
               m5_control_cases=[dict(a=1, b=-1, pulsates_at="f_a+f_b (a+b=0)"), dict(a=1, b=1, pulsates_at="|f_a-f_b| (a-b=0)"),
                                 dict(a=1, b=4, pulsates_at="f_a+f_b (a+b=5)")],
               sensitivity=sens)
    # recommended, safe and measurable points: modulation feasible, ripple <= 10 % V_dc at the chosen C, >= 0.5 V
    rec = []
    for r in table:
        if not r["modulation_feasible"]:
            continue
        P = max(r["at_f_sum"]["P_W"], r["at_f_diff"]["P_W"])
        if P < 1e-6:          # null cases: pair them with their controls; recommend the same load/current
            continue
        f = (f_a + f_b) if r["at_f_sum"]["P_W"] >= r["at_f_diff"]["P_W"] else abs(f_a - f_b)
        for cname, c in (("1mF", 1e-3), ("2mF", 2e-3), ("4.7mF", 4.7e-3)):
            dv = P / r["V_dc_V"] / (2 * math.pi * f * c)
            if 0.5 <= dv <= 0.10 * r["V_dc_V"]:
                rec.append(dict(cell=r["cell"], a=r["a"], b=r["b"], I_pk_A=r["I_pk_A"], R_ohm=r["R_ohm"], L_mH=r["L_mH"], V_dc_V=r["V_dc_V"],
                                C=cname, f_Hz=f, P_W=P, dV_pk_V=dv))
                break
    res["recommended_points"] = dict(
        rule="modulation feasible; predicted ripple between 0.5 V (measurable) and 10 % of V_dc (safe), smallest listed C that achieves it",
        points=rec,
        safety_note="At C = 1 mF the plan's 10 A points give up to +-48 V ripple at 100 V (difference term at 20 Hz). Use 5 A first, "
                    "or a larger film C, and prefer the 81/19 Hz frequency pair. The 5-leg null cases (1,2) use the same load and current as "
                    "their 5-leg controls (1,-1) and (1,1).")
    json.dump(res, open(OUT, "w"), indent=1)
    # console
    for r in table:
        if r["I_pk_A"] == 10.0 and r["R_ohm"] == 2.0 and r["L_mH"] == 5.0:
            print(f"{r['cell']} ({r['a']},{r['b']}) Vdc={r['V_dc_V']:.0f} mod_ok={r['modulation_feasible']} "
                  f"P_sum={r['at_f_sum']['P_W']:.1f}W dV={r['at_f_sum'].get('dV_pk_V', 0):.3f}V  P_diff={r['at_f_diff']['P_W']:.1f}W "
                  f"dV={r['at_f_diff'].get('dV_pk_V', 0):.3f}V")
    print(json.dumps(td, indent=0)[:1500])
    print("m5 zero pairs", res["m5_zero_pulsation_pairs"])
    print("imbalance", json.dumps(sens["load_imbalance_pm5pct"], indent=0))
    for k, v in asym.items():
        print("asym", k, round(v["residual_over_m3"], 4), v["passes_10pct_criterion"])
    for k, v in dead.items():
        print(k, round(v["m5_residual_over_m3"], 4), v["passes_10pct_criterion"])


if __name__ == "__main__":
    main()

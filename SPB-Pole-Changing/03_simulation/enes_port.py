"""Python port of OPT-Bipolar-Field-Excitation/analysis/4_design_studies/torque_speed_switching.m (read only source) and a sweep of x_q4."""
import math, json
import numpy as np


def enes_model(kw4=0.808, kw2=0.760, xq4=0.31, alpha=2 / 3, turns_halved=True, fmax=429 / 381):
    kd = alpha + math.sin(alpha * math.pi) / math.pi
    kq = alpha - math.sin(alpha * math.pi) / math.pi + 2 / (3 * math.pi) * math.cos(alpha * math.pi / 2)
    xd4 = xq4 * kd / kq
    c4 = 4 / math.pi * math.sin(alpha * math.pi / 2); c2 = 8 / math.pi * math.cos(math.pi / 4) * math.sin(alpha * math.pi / 4)
    k2 = (kw2 / kw4) * (c2 / c4)
    x2 = xq4 * (kw2 / kw4) ** 2 * (alpha / kq)
    if not turns_halved:
        k2, x2 = k2 * 2, x2 * 4
    F, B, I = np.meshgrid(np.linspace(0, fmax, 101), np.linspace(-10, 90, 101) * math.pi / 180, np.linspace(0.5, 2, 16), indexing="ij")
    id_, iq = -I * np.sin(B), I * np.cos(B)
    P4 = (F + xd4 * id_, xq4 * iq); P4T = P4[0] * iq - P4[1] * id_
    P2 = (k2 * F + x2 * id_, x2 * iq); P2T = (P2[0] * iq - P2[1] * id_) / 2
    T4max = P4T[I <= 1].max(); g = (P4T >= 0.999 * T4max) & (I <= 1)
    Vmax = np.hypot(P4[0][g], P4[1][g]).min()
    n = np.linspace(0.02, 3.0, 150)
    out = []
    for x in n:
        r = []
        for (psd, psq, T), w_ in (((P4[0], P4[1], P4T), x), ((P2[0], P2[1], P2T), x / 2)):
            ok = (I <= 1 + 1e-9) & (w_ * np.hypot(psd, psq) <= Vmax + 1e-9)
            r.append(T[ok].max() if ok.any() else np.nan)
        out.append(r)
    out = np.array(out)
    better = np.where(out[:, 1] > out[:, 0] + 1e-3)[0]
    return dict(xq4=xq4, turns_halved=turns_halved, x2_over_xq4=x2 / xq4, T2_over_T4_low=float(out[0, 1] / out[0, 0]),
                crossover_speed_over_n4_base=float(n[better[0]]) if len(better) else None,
                T2_over_T4_at_2x=float(np.interp(2.0, n, out[:, 1] / out[:, 0])), T2_over_T4_at_3x=float(out[-1, 1] / out[-1, 0]))


if __name__ == "__main__":
    res = [enes_model(xq4=x, turns_halved=h) for x in (0.31, 0.6, 0.9, 1.2) for h in (True, False)]
    for r in res:
        print(r)
    json.dump(dict(meta=dict(script="03_simulation/enes_port.py", task="T04 item 2", note="port of torque_speed_switching.m; x_q4 sweep"), cases=res),
              open("results/enes_kx_sweep.json", "w"), indent=1)

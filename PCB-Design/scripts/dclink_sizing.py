"""
DC-link sizing of one 75 V SPB level (three legs on a common bus), from the switching functions.

    C:\\Github\\KTH\\LossCalculation-SPB\\.venv\\Scripts\\python.exe scripts\\dclink_sizing.py
      -> reports/slides/data/dclink_sizing.json, reports/slides/revb_pptx/img/dclink_sizing.png

Model: SVPWM (min-max zero sequence, centred carrier), M = V_ph,pk / (V_dc/2) = 1.15, phase current
I_pk cos(wt - phi - k 120 deg), current constant within a switching period. DC-side current i_dc = sum s_k i_k;
the series stack supplies the average (it cannot carry the switching-frequency ripple through its inductance), so
the capacitor current is i_c = i_dc - <i_dc>. Per switching period the charge excursion dQ = max - min of the
integral of i_c gives the peak-to-peak ripple dV = dQ / C; the worst period over the line cycle sizes C.
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V_DC, M, PF, I_PK = 75.0, 1.15, 0.9, 322.0
PHI = np.arccos(PF)
N_PER = 2000                       # switching periods per line period evaluated
N_SUB = 400                        # samples within a switching period


def level(f_sw, m=M, phi=PHI, i_pk=I_PK):
    th = np.linspace(0, 2 * np.pi, N_PER, endpoint=False)
    ks = np.array([0, -2 * np.pi / 3, 2 * np.pi / 3])
    v = m * np.cos(th[:, None] + ks[None, :])                      # normalised to V_dc/2
    v0 = -(v.max(axis=1) + v.min(axis=1)) / 2                       # SVPWM zero sequence
    d = np.clip(0.5 * (1 + v + v0[:, None]), 0, 1)                  # duty of the upper switch
    i = i_pk * np.cos(th[:, None] + ks[None, :] - phi)
    t = (np.arange(N_SUB) + 0.5) / N_SUB                            # within one period (centred PWM)
    on = np.abs(t[None, None, :] - 0.5) < d[:, :, None] / 2         # upper switch on around the period centre
    idc = np.einsum("pk,pkt->pt", i, on.astype(float))              # (period, sample)
    i_avg = idc.mean()                                              # stack current (= P / V_dc)
    ic = idc - i_avg
    q = np.cumsum(ic - ic.mean(axis=1, keepdims=True), axis=1) / (N_SUB * f_sw)
    dq = q.max(axis=1) - q.min(axis=1)
    return dict(I_dc=float(i_avg), I_c_rms=float(np.sqrt((ic ** 2).mean())), dQ_max=float(dq.max()),
                dQ_mean=float(dq.mean()), th=th, dq=dq)


res = {}
for f in (50e3, 75e3, 100e3):
    r = level(f)
    res[int(f / 1e3)] = r
    print("f_sw %3d kHz: I_dc %.1f A, I_C,rms %.1f A, dQ_max %.2f uC -> C_eff for 1/2/3 %% ripple: %s uF" % (
        f / 1e3, r["I_dc"], r["I_c_rms"], r["dQ_max"] * 1e6,
        " / ".join("%.0f" % (r["dQ_max"] / (p / 100 * V_DC) * 1e6) for p in (1, 2, 3))))
# single leg alone (no sharing) for comparison: worst case D = 0.5, i = I_pk -> dQ = I_pk / (4 f) ... per period
for f in (50e3,):
    print("single leg, no sharing, 50 kHz: dQ_max = I_pk/(4 f) = %.2f uC" % (I_PK / (4 * f) * 1e6))

# MLCC counts per level and per leg board (three legs share the level)
RET_1210, RET_0805 = 0.30, 0.45            # X7S 100 V at 75 V DC bias (same values as the v3 deck)
C1210, C0805 = 10e-6, 1e-6
BYP_PER_LEG = 24 * C0805 * RET_0805        # 6 x 1 uF per cell, fixed by the loop inductance
I_RIPPLE_1210 = 2.0                        # A rms per 1210 part, conservative (self-heating ~10-15 K)
out = {"inputs": dict(V_dc=V_DC, M=M, cos_phi=PF, I_pk=I_PK, retention_1210=RET_1210,
                      retention_0805=RET_0805, ripple_A_per_1210=I_RIPPLE_1210), "cases": {}}
for fk, r in res.items():
    for p in (1, 2, 3):
        c_eff_level = r["dQ_max"] / (p / 100 * V_DC)
        c_eff_leg = c_eff_level / 3
        n_bank_v = max(0.0, (c_eff_leg - BYP_PER_LEG) / (C1210 * RET_1210))
        n_bank_i = r["I_c_rms"] / 3 / I_RIPPLE_1210
        n = int(np.ceil(max(n_bank_v, n_bank_i)))
        out["cases"]["%dkHz_%dpct" % (fk, p)] = dict(
            I_c_rms_level=r["I_c_rms"], C_eff_level_uF=c_eff_level * 1e6, C_eff_leg_uF=c_eff_leg * 1e6,
            n1210_voltage=n_bank_v, n1210_current=n_bank_i, n1210_per_leg=n,
            C_nominal_leg_uF=(n * C1210 + 24 * C0805) * 1e6)
        print("  %3d kHz, %d %% (%.2f V pp): C_eff %.0f uF per level, %.0f per leg -> %d x 10 uF 1210 per leg "
              "(voltage %.0f, current %.0f), nominal %.0f uF per leg" % (
                  fk, p, p / 100 * V_DC, c_eff_level * 1e6, c_eff_leg * 1e6, n, n_bank_v, n_bank_i,
                  (n * C1210 + 24 * C0805) * 1e6))
os.makedirs(os.path.join(ROOT, "reports", "slides", "data"), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, "reports", "slides", "data", "dclink_sizing.json"), "w"), indent=1)

fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.6), dpi=200)
r = res[50]
ax[0].plot(np.degrees(r["th"]), r["dq"] * 1e6, color="#1954A6")
ax[0].set_xlabel("line angle (deg)")
ax[0].set_ylabel("charge excursion per period (µC)")
ax[0].set_title("(a) one level, 50 kHz, SVPWM M = 1.15", fontsize=10)
ax[0].grid(alpha=0.3)
pct = np.linspace(0.5, 4, 50)
for fk, c in ((50, "#1954A6"), (75, "#3C8C50"), (100, "#C84632")):
    ax[1].plot(pct, [int(np.ceil(max((res[fk]["dQ_max"] / (p / 100 * V_DC) / 3 - BYP_PER_LEG) / (C1210 * RET_1210),
                                     res[fk]["I_c_rms"] / 3 / I_RIPPLE_1210))) for p in pct], color=c,
               label="%d kHz" % fk)
ax[1].axhline(75, color="gray", ls="--", lw=1)
ax[1].text(2.6, 77, "Rev B layout: 75", color="gray", fontsize=8)
ax[1].set_xlabel("allowed ripple ΔV_pp (% of 75 V)")
ax[1].set_ylabel("10 µF 1210 per leg board")
ax[1].set_title("(b) bank per leg (three legs share the level)", fontsize=10)
ax[1].legend()
ax[1].grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "reports", "slides", "revb_pptx", "img", "dclink_sizing.png"))

"""
Genuine nonlinear simulation of SPB dc-link (voltage-sharing)
stability, built directly from the state-space model of Nikouie,
Wallmark, Jin, Harnefors, Nee, "DC-Link Stability Analysis and
Controller Design for the Stacked Polyphase Bridges Converter," IEEE
Trans. Power Electronics, 2017 (already cited as Nikouie2017Stability):

    L_b di_b/dt = E_b - R_b*i_b - sum_k(v_k)          (1)
    C dv_k/dt   = i_b - P_k/v_k                        (2)-(3)

with constant-power submodule loads P_k. That paper proves this
open-loop system is UNSTABLE for msm>1 submodules in motoring mode
(msm-1 real positive eigenvalues, plus a resonant-mode oscillation) --
this script reproduces that instability directly by integrating the
exact nonlinear ODEs (not just quoting the linearized eigenvalues),
then shows the same system stabilized by their "controller
alternative I" balancing law:

    i_ref_d,k = id0 + g*id0*(v_k - vbar),  i_ref_q,k = iq0 + g*iq0*(v_k - vbar)

which (per their eq. 24) is equivalent, once linearized, to a
proportional correction on each cell's power command,
DeltaP_k = g'*(v_k - vbar), vbar = mean(v_k). Implemented here directly
on the nonlinear P_k for a concrete, non-linearized demonstration.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Nimbus Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 8,
    "axes.linewidth": 0.7,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "legend.frameon": False,
})

msm = 3            # number of submodules (matches this paper's N=3 convention)
Lb = 8e-6           # source inductance (H) -- real experimental value
Rb = 0.35           # source resistance (Ohm) -- real experimental value
C = 100e-6          # per-cell dc-link capacitance (F) -- real experimental value
v_star = 100.0      # nominal per-cell voltage (V)
Eb = msm * v_star   # battery voltage (V)
P_star = 1000.0     # nominal per-cell power (W)

# Stability check per eq. (33) of the reference: C_min = P*Lb/(v*^2 Rb)
C_min = P_star * Lb / (v_star ** 2 * Rb)
print(f"C = {C*1e6:.1f} uF, C_min for stability (eq. 33) = {C_min*1e6:.3f} uF "
      f"-> controller-alt-I stability condition {'holds' if C > C_min else 'FAILS'}")

# Balancing-controller gain (alternative I): g' > P*/v* required (eq. 36);
# use a gain comfortably above threshold for a clean, fast response.
g_prime = 3.0 * P_star / v_star

# Initial per-cell voltage imbalance (p.u. of v_star), matching the
# representative deviations used elsewhere in this paper's balancing figure.
dv0 = np.array([0.08, -0.05, 0.02]) * v_star

def rhs(ib, v, balancing_on):
    vbar = v.mean()
    if balancing_on:
        dP = g_prime * (v - vbar)
    else:
        dP = np.zeros_like(v)
    Pk = P_star + dP
    div = (Eb - Rb * ib - v.sum()) / Lb
    dvk = (ib - Pk / v) / C
    return div, dvk

def simulate(t_end, n_pts, balancing_on):
    t = np.linspace(0, t_end, n_pts)
    dt = t[1] - t[0]
    ib = np.zeros(n_pts)
    v = np.zeros((n_pts, msm))
    ib[0] = P_star * msm / Eb
    v[0, :] = v_star + dv0
    for n in range(n_pts - 1):
        ibn, vn = ib[n], v[n]
        k1i, k1v = rhs(ibn, vn, balancing_on)
        k2i, k2v = rhs(ibn + dt / 2 * k1i, vn + dt / 2 * k1v, balancing_on)
        k3i, k3v = rhs(ibn + dt / 2 * k2i, vn + dt / 2 * k2v, balancing_on)
        k4i, k4v = rhs(ibn + dt * k3i, vn + dt * k3v, balancing_on)
        ib[n + 1] = ibn + dt / 6 * (k1i + 2 * k2i + 2 * k3i + k4i)
        v[n + 1] = vn + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        if np.any(v[n + 1] <= 1.0) or np.any(v[n + 1] > 5 * v_star):
            # nonlinear blow-up (division by ~0 voltage): stop cleanly
            v[n + 2:] = np.nan
            ib[n + 2:] = np.nan
            break
    return t, v, ib

# Open loop: integrate long enough for the proven instability
# (eigenvalue ~ P*/(C v*^2), time constant ~1 ms here) to become
# visually dramatic rather than just a gentle drift.
t_ol, v_ol, _ = simulate(t_end=3e-3, n_pts=6000, balancing_on=False)
# Closed loop: same window, to show settling on a comparable timescale.
t_cl, v_cl, _ = simulate(t_end=3e-3, n_pts=6000, balancing_on=True)

fig, axes = plt.subplots(1, 2, figsize=(3.45, 2.3), sharey=True)

colors = ["#1f4e99", "#c0392b", "#1a7a4c"]
labels = [f"Cell {k+1}" for k in range(msm)]

ax = axes[0]
for k in range(msm):
    ax.plot(t_ol * 1e3, (v_ol[:, k] - v_star) / v_star, color=colors[k],
             linewidth=1.0, label=labels[k])
ax.axhline(0, color="gray", linewidth=0.5, alpha=0.6)
ax.set_title("Without balancing", fontsize=7.5)
ax.set_xlabel(r"$t$ (ms)")
ax.set_ylabel(r"$(v_k-v^\star)/v^\star$ (p.u.)")
ax.grid(True, linewidth=0.4, alpha=0.3)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax = axes[1]
for k in range(msm):
    ax.plot(t_cl * 1e3, (v_cl[:, k] - v_star) / v_star, color=colors[k],
             linewidth=1.0, label=labels[k])
ax.axhline(0, color="gray", linewidth=0.5, alpha=0.6)
ax.set_title("With balancing (controller I)", fontsize=7.5)
ax.set_xlabel(r"$t$ (ms)")
ax.grid(True, linewidth=0.4, alpha=0.3)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(loc="upper right", fontsize=6)

plt.tight_layout()
plt.savefig("fig_dclink_balancing.pdf", bbox_inches="tight")
print("saved")
print(f"open-loop final finite sample -> v = "
      f"{v_ol[~np.isnan(v_ol[:,0])][-1] if np.any(~np.isnan(v_ol[:,0])) else 'n/a'}")
print(f"closed-loop final v (V) = {v_cl[-1]}")

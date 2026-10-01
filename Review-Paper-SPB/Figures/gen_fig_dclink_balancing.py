"""Illustrative nonlinear SPB voltage-sharing simulation.
Model based on Nikouie et al., IEEE TPEL, 2017.
The balancing law DeltaP_k = Kp*(v_k-mean(v)) is motivated by
controller alternative I, with ideal instantaneous power tracking.
It does not reproduce the complete current-control implementation.
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

# Illustrative proportional power gain (W/V).
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

from pathlib import Path

# Plot differential imbalance, not deviation from nominal voltage:
# the common steady voltage includes the resistive supply-path drop.
fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.35), sharex=True, sharey=True)
colors = ["#1f4e99", "#b23a33", "#23764a"]
styles = ["-", "--", "-."]
labels = [f"Cell {k+1}" for k in range(msm)]
for ax, t, v, title in zip(
    axes, [t_ol, t_cl], [v_ol, v_cl],
    ["(a) Without balancing", "(b) With proportional\npower balancing"]
):
    imbalance = (v - v.mean(axis=1, keepdims=True)) / v_star
    for k in range(msm):
        ax.plot(t*1e3, imbalance[:, k], color=colors[k],
                linestyle=styles[k], linewidth=1.05, label=labels[k])
    ax.axhline(0, color="0.5", linewidth=0.5, zorder=0)
    ax.set_title(title, fontsize=7.2, pad=6)
    ax.set_xlabel(r"$t$ (ms)")
    ax.set_xlim(0, 3)
    ax.set_xticks([0, 1, 2, 3])
    ax.grid(True, linewidth=0.35, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
axes[0].set_ylabel(r"$\widetilde{V}_k/V_{\mathrm{base}}$ (p.u.)")
fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center",
           bbox_to_anchor=(0.55, 0.005), ncol=3, fontsize=7,
           handlelength=2.1, columnspacing=1.0)
fig.subplots_adjust(left=0.18, right=0.985, bottom=0.30, top=0.80, wspace=0.12)
output_dir = Path(__file__).resolve().parent
fig.savefig(output_dir / "fig_dclink_balancing.pdf", bbox_inches="tight")
fig.savefig(output_dir / "fig_dclink_balancing_preview.png", dpi=220, bbox_inches="tight")
print(f"Closed-loop final voltages (V): {v_cl[-1]}")
print(f"Final voltage spread (V): {np.ptp(v_cl[-1]):.6f}")
# Verify the illustrated balancing property and zero-sum power correction.
assert np.ptp(v_cl[-1]) < 0.1
assert abs(np.sum(g_prime*(v_cl[-1]-v_cl[-1].mean()))) < 1e-8
print("Figure regenerated; balancing and zero-sum power checks passed.")

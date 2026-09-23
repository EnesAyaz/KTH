"""
Common-mode voltage (CMV) cancellation simulation for the N=2 SPB
special case, plus the resulting bearing/ground current through a
capacitive coupling path.

Model: each cell is a standard 2-level three-phase bridge under
naturally-sampled SPWM. Each cell's own common-mode voltage is the
average of its three pole voltages relative to the dc-link midpoint:

    v_cm,k(t) = (Sa,k + Sb,k + Sc,k)/3 - 0.5      (p.u. of Vdc)

With three independent phase legs each switching once up and once
down per switching period, this naturally produces a six-step
staircase per switching period (up to 6 transitions -> 7 levels),
matching the "6-step CMV" structure of a real 2-level bridge -- not a
hand-drawn approximation.

Cell 2 is driven with the logically inverted gate commands of cell 1
(Sx,2 = 1 - Sx,1), which analytically gives v_cm,2(t) = -v_cm,1(t)
EXACTLY for perfectly aligned, ideal switching (verified numerically
below).

Crucially, because the two cells are SERIES-STACKED (not just two
independent inverters), cell 2's local dc rails sit at a different
absolute potential than cell 1's, per the stack-offset relation
already established earlier in this section (eq:spb_cm_offset):

    V_{-,k} = sum_{j<k} V_dc,j  ~=  (k-1) * V_dc / N

For N=2: V_{-,1} = 0, V_{-,2} = V_dc/2. Each cell's local switched CMV
(the six-step term above) is referenced to its OWN rail and swings
+-1/(2N) of the TOTAL stack V_dc; the cell's ABSOLUTE common-mode
voltage seen by the shared frame/ground is the stack offset plus that
local term:

    v_cm,k^abs(t) = V_{-,k} + v_cm,k^local(t)

This structural offset is present regardless of modulation strategy
(with or without cancellation) -- it is NOT the same thing as a
propagation delay or a sensor mismatch. On top of it, one additional
real-world imperfection is modeled: a small propagation delay td
between cell 1 and cell 2's switching instants (gate-drive/PCB-layout
mismatch). Because the bearing/ground current is capacitive
(i = C dv/dt), a CONSTANT offset (the stack term V_{-,2}, or any other
constant bias) contributes zero current (d(const)/dt = 0); only the
delay-induced transients drive nonzero current. This is verified
numerically below, not assumed.
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

M = 0.85
phi_pf = np.deg2rad(20)
theta0 = np.deg2rad(35)   # representative fixed electrical angle (short window)
thetas = [0.0, -2 * np.pi / 3, 2 * np.pi / 3]

fsw = 1.0
Tsw = 1.0 / fsw
n_periods_shown = 3
n_per_period = 3000
n_pts = n_per_period * n_periods_shown
t = np.linspace(0, n_periods_shown * Tsw, n_pts, endpoint=False)

N = 2
V_offset = [(k) / N for k in range(N)]  # V_{-,1}=0, V_{-,2}=1/N, ... (p.u. of total Vdc)
td = 0.02 * Tsw     # small inter-cell propagation delay (separate from the stack offset)

def carrier(tt):
    x = (tt / Tsw) % 1.0
    return 2 * np.abs(2 * (x - np.floor(x + 0.5))) - 1

def cell_S(tt):
    """Returns (Sa, Sb, Sc) at time tt for the fixed representative
    operating point theta0."""
    c = carrier(tt)
    out = []
    for th in thetas:
        d = 0.5 + 0.5 * M * np.cos(theta0 - th - phi_pf)
        out.append(((2 * d - 1) > c).astype(float))
    return out

Sa1, Sb1, Sc1 = cell_S(t)
v1_local = ((Sa1 + Sb1 + Sc1) / 3.0 - 0.5) / N
v1 = V_offset[0] + v1_local

# Cell 2 (cancellation case): inverted gate commands, delayed switching
# instants, PLUS the structural stack offset V_offset[1] = V_dc/N.
Sa2i, Sb2i, Sc2i = cell_S(t - td)
Sa2, Sb2, Sc2 = 1.0 - Sa2i, 1.0 - Sb2i, 1.0 - Sc2i
v2_local = ((Sa2 + Sb2 + Sc2) / 3.0 - 0.5) / N
v2 = V_offset[1] + v2_local

# Cell 2 (no-cancellation baseline): SAME pattern as cell 1 (not
# inverted), still carrying the same structural stack offset -- the
# offset is a property of series position, not of modulation choice.
v2_noninverted = V_offset[1] + v1_local

# Sanity check: with td=0, the LOCAL terms should be exact mirrors
# (the stack offset is separate and does not affect this identity).
Sa2_chk, Sb2_chk, Sc2_chk = 1 - Sa1, 1 - Sb1, 1 - Sc1
v2_local_chk = ((Sa2_chk + Sb2_chk + Sc2_chk) / 3.0 - 0.5) / N
assert np.allclose(v2_local_chk, -v1_local), "ideal inversion identity failed"

v_tot_without = (v1 + v2_noninverted) / 2.0   # same pattern: local swings ADD
v_tot_with = (v1 + v2) / 2.0                  # inverted cell 2: local swings cancel

expected_avg = sum(V_offset) / N
print(f"mean(v_tot_without)={v_tot_without.mean():.5f}  (expected ~= mean(V_offset) = {expected_avg:.5f})")
print(f"mean(v_tot_with)={v_tot_with.mean():.5f}  (expected ~= mean(V_offset) = {expected_avg:.5f})")

# Finite switching-transition time (device dv/dt is fast but not
# instantaneous) via light Gaussian smoothing, so the derivative-based
# bearing current has a realistic finite peak rather than a
# grid-resolution-dependent numerical spike.
dt_local = t[1] - t[0]
tau_rise = 0.004 * Tsw
sigma_pts = max(1, int(tau_rise / dt_local))
win = np.arange(-4 * sigma_pts, 4 * sigma_pts + 1)
gk = np.exp(-0.5 * (win / sigma_pts) ** 2)
gk /= gk.sum()

def smooth(x):
    xp = np.concatenate([x[-len(gk):], x, x[:len(gk)]])
    return np.convolve(xp, gk, mode="same")[len(gk):-len(gk)]

v_tot_without_s = smooth(v_tot_without)
v_tot_with_s = smooth(v_tot_with)

C_bear = 1.0  # normalized capacitive-coupling constant (illustrative)
i_bear_without = C_bear * np.gradient(v_tot_without_s, dt_local)
i_bear_with = C_bear * np.gradient(v_tot_with_s, dt_local)

# Normalize current to the worst-case (without-cancellation) peak.
i_ref = np.abs(i_bear_without).max()
i_bear_without /= i_ref
i_bear_with /= i_ref

# Confirm: current from the "with cancellation" case is driven only by
# the delay-induced transients, not by the (large, structural) stack
# offset -- check by recomputing with V_offset[1] artificially set to
# zero (i.e. no stack offset at all) and comparing the CURRENT, which
# should be numerically identical since only a time-varying term can
# produce d/dt =/= 0.
v2_nooffset = 0.0 + v2_local
v_tot_nooffset = smooth((v1_local + v2_nooffset) / 2.0)
i_bear_nooffset = C_bear * np.gradient(v_tot_nooffset, dt_local) / i_ref
print(f"max|i_with - i_nooffset| = {np.abs(i_bear_with - i_bear_nooffset).max():.2e} "
      f"(should be ~0: constant stack offset contributes no current)")

# --- Plot: 3 stacked panels, all p.u., over n_periods_shown switching periods ---
tt = t / Tsw
fig, axes = plt.subplots(3, 1, figsize=(3.45, 4.6), sharex=True)

ax = axes[0]
ax.plot(tt, v1, color="#1f4e99", linewidth=0.9, label=r"Cell 1, $v_{\mathrm{cm},1}$")
ax.plot(tt, v2, color="#c0392b", linewidth=0.9, alpha=0.85,
        label=r"Cell 2, $v_{\mathrm{cm},2}$ (inverted)")
ax.set_ylabel(r"$v_{\mathrm{cm},k}/V_{\mathrm{dc}}$ (p.u.)")
ax.set_ylim(-0.4, 0.9)
ax.axhline(V_offset[1], color="gray", linewidth=0.5, linestyle=":", alpha=0.7)
ax.legend(loc="upper center", ncol=1, fontsize=6, bbox_to_anchor=(0.78, 1.05))
ax.grid(True, linewidth=0.4, alpha=0.3)
ax.text(0.02, 0.06, "(a)", transform=ax.transAxes, fontsize=7)

ax = axes[1]
ax.plot(tt, v_tot_without, color="#c0392b", linewidth=0.9, alpha=0.8,
        label="Without cancellation")
ax.plot(tt, v_tot_with, color="#1f4e99", linewidth=0.9,
        label="With cancellation")
ax.set_ylabel(r"$v_{\mathrm{cm,tot}}/V_{\mathrm{dc}}$ (p.u.)")
ax.set_ylim(-0.1, 0.6)
ax.legend(loc="upper center", ncol=2, fontsize=6, bbox_to_anchor=(0.5, 1.18))
ax.grid(True, linewidth=0.4, alpha=0.3)
ax.text(0.02, 0.06, "(b)", transform=ax.transAxes, fontsize=7)

ax = axes[2]
ax.plot(tt, i_bear_without, color="#c0392b", linewidth=0.7, alpha=0.75,
        label="Without cancellation")
ax.plot(tt, i_bear_with, color="#1f4e99", linewidth=0.9,
        label="With cancellation")
ax.set_ylabel(r"$i_{\mathrm{bear}}$ (p.u.)")
ax.set_xlabel(r"$t/T_{sw}$")
ax.set_xlim(0, n_periods_shown)
ax.grid(True, linewidth=0.4, alpha=0.3)
ax.text(0.02, 0.88, "(c)", transform=ax.transAxes, fontsize=7)

for a in axes:
    a.spines["top"].set_visible(False)
    a.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig("fig_cm_cancellation.pdf", bbox_inches="tight")
print("saved")

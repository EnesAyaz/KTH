"""
Full state-space circuit simulation of the SPB series dc-link current,
with and without carrier interleaving between the N=3 submodules.

Circuit: N series-connected cells, each with its own local dc-link
capacitor C_k across its own three-phase 2-level bridge (drawing a
switched converter-side current i_conv,k(t) via naturally-sampled
SPWM). The N cells' capacitor voltages V_k are in series with the
battery, its internal/wire resistance R, and the shared bus/wire
inductance L. Because the stack is a single series loop, ONE current
i_dc(t) flows through the inductance, the battery, and (via each
cell's capacitor) into the series path -- it is NOT a sum of N
independent per-cell currents. Each cell's capacitor supplies exactly
the difference between the shared series current and that cell's own
converter draw:

    C_k dV_k/dt = i_dc(t) - i_conv,k(t),          k = 1..N
    L di_dc/dt  = V_batt - R*i_dc - sum_k V_k(t)

The carrier phase shift for interleaving is applied BETWEEN THE THREE
SUBMODULES (each cell's own carrier gets a different phase offset),
not between the a/b/c phase legs within one submodule (those keep
their fixed 120-degree reference separation, which is a separate,
unrelated three-phase structure). Solved here with explicit RK4.
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

N = 3                       # SPB cell (submodule) count
M = 0.85                    # modulation index
phi_pf = np.deg2rad(20)     # displacement power-factor angle
# Per-cell phase-current amplitude, solved so the steady-state average
# dc current is exactly 1 p.u.: at periodic steady state each
# capacitor's charge balance forces <i_dc> = <i_conv,k> = 0.75*M*Im*cos(phi)
# (standard averaged 3-phase SPWM result), independent of N, L, R, V_batt.
Im = 1.0 / (0.75 * M * np.cos(phi_pf))
f1 = 1.0                    # fundamental frequency (Hz) -- 1 period per unit graph
fsw = 100.0                 # switching frequency (Hz)
Tsw = 1.0 / fsw

# Series-loop circuit parameters (normalized, chosen for a stable,
# illustrative response -- not a specific hardware design point).
# Natural frequency of the series loop (L with N caps in series,
# C_eff = C_k/N) is placed well above f1 and well below fsw, with
# near-critical damping, so the loop settles within a fraction of a
# fundamental period instead of ringing.
C_k = 0.01                  # per-cell local dc-link capacitance (p.u.)
L_bus = 0.0085               # shared bus/wire inductance (p.u.)
R_bus = 2.5                 # series damping resistance (p.u.)
V_batt = 1.0 * N + R_bus * 1.0  # battery voltage, sized for ~1 p.u. avg i_dc
N_PERIODS = 6                # simulate several fundamental periods, keep the last
N_PER_SW = 40                 # time samples per switching period

thetas = [0.0, -2 * np.pi / 3, 2 * np.pi / 3]  # fixed a/b/c reference separation

def carrier(tt, phase_frac):
    x = ((tt - phase_frac * Tsw) / Tsw) % 1.0
    return 2 * np.abs(2 * (x - np.floor(x + 0.5))) - 1  # in [-1, 1]

def i_conv(tt, carrier_phase_frac):
    """This cell's own switched converter-side current at time tt,
    built from its own three phase legs (fixed 120-degree references)
    compared against a carrier whose PHASE (not the phase legs) is
    offset for inter-cell interleaving."""
    c = carrier(tt, carrier_phase_frac)
    total = 0.0
    for th in thetas:
        ia = Im * np.cos(2 * np.pi * f1 * tt - th)
        da = 0.5 + 0.5 * M * np.cos(2 * np.pi * f1 * tt - th - phi_pf)
        Sa = 1.0 if (2 * da - 1) > c else 0.0
        total += Sa * ia
    return total

def simulate(carrier_phases):
    """carrier_phases: list of N carrier phase fractions, one per cell.
    Simulates N_PERIODS fundamental periods and returns the full
    history (caller keeps only the last, settled period)."""
    n_per_sw = N_PER_SW
    n_pts = int(n_per_sw * fsw / f1 * N_PERIODS)
    dt = (N_PERIODS / f1) / n_pts
    t = np.zeros(n_pts)
    V = np.zeros((n_pts, N))
    idc = np.zeros(n_pts)
    V[0, :] = 1.0            # start at nominal per-cell voltage
    idc[0] = 1.0             # start at nominal dc current

    def rhs(tt, Vk, i_dc_val):
        dV = np.array([(i_dc_val - i_conv(tt, cp)) / C_k
                        for cp in carrier_phases])
        di = (V_batt - R_bus * i_dc_val - Vk.sum()) / L_bus
        return dV, di

    for n in range(n_pts - 1):
        tn = t[n]
        Vn, idn = V[n], idc[n]
        k1V, k1i = rhs(tn, Vn, idn)
        k2V, k2i = rhs(tn + dt / 2, Vn + dt / 2 * k1V, idn + dt / 2 * k1i)
        k3V, k3i = rhs(tn + dt / 2, Vn + dt / 2 * k2V, idn + dt / 2 * k2i)
        k4V, k4i = rhs(tn + dt, Vn + dt * k3V, idn + dt * k3i)
        V[n + 1] = Vn + dt / 6 * (k1V + 2 * k2V + 2 * k3V + k4V)
        idc[n + 1] = idn + dt / 6 * (k1i + 2 * k2i + 2 * k3i + k4i)
        t[n + 1] = tn + dt
    return t, idc

# Without interleaving: all N cells' carriers in phase.
t_full, idc_without_full = simulate([0.0] * N)
# With interleaving: carriers uniformly phase-shifted by 1/N of Tsw.
_, idc_with_full = simulate([k / N for k in range(N)])

# Discard the first N_PERIODS-1 fundamental periods as transient;
# keep only the final, settled period.
n_per_period = len(t_full) // N_PERIODS
idc_without = idc_without_full[-n_per_period:]
idc_with = idc_with_full[-n_per_period:]
t = t_full[-n_per_period:] - t_full[-n_per_period]

# The confirmed-periodic waveform has a 6*f1 envelope (six repeated
# lobes per fundamental period); roll the array so a local envelope
# MINIMUM sits at t=0 (=t=1), so each of the six lobes reads as a
# complete valley-to-valley hump instead of being cut at the window
# edge. This is a circular shift of an already-periodic signal, not a
# change to the underlying simulation.
win_env = 2 * N_PER_SW
roll_env = np.array([idc_without[i:i + win_env].max() - idc_without[i:i + win_env].min()
                      for i in range(len(idc_without) - win_env)])
shift = int(np.argmin(roll_env))
idc_without = np.roll(idc_without, -shift)
idc_with = np.roll(idc_with, -shift)

ss_without = idc_without
ss_with = idc_with

fig, ax1 = plt.subplots(figsize=(3.45, 2.5))

ax1.plot(t, idc_without, color="#c0392b", linewidth=0.35, alpha=0.85,
         label="Without interleaving")
ax1.plot(t, idc_with, color="#1f4e99", linewidth=0.35, alpha=0.9,
         label="With interleaving")
ax1.set_xlabel(r"$t$ (s), 1 fundamental period")
ax1.set_ylabel(r"$i_{\mathrm{dc}}$ (p.u.)")
ax1.set_xlim(0, 1)
ax1.set_ylim(0.88, 1.08)
ax1.grid(True, linewidth=0.4, alpha=0.3)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.legend(loc="upper center", ncol=2, fontsize=6.5,
           bbox_to_anchor=(0.5, 1.18), columnspacing=1.2)

dc_avg = ss_without.mean()
pp_without = ss_without.max() - ss_without.min()
pp_with = ss_with.max() - ss_with.min()
print(f"dc_avg_without={ss_without.mean():.4f}  dc_avg_with={ss_with.mean():.4f}")
print(f"pp_without={pp_without:.4f}  pp_with={pp_with:.4f}  ratio={pp_without/pp_with:.2f}")
print(f"min_without={ss_without.min():.4f}  min_with={ss_with.min():.4f}")

plt.tight_layout()
plt.savefig("fig_dclink_ripple.pdf", bbox_inches="tight")
print("saved")

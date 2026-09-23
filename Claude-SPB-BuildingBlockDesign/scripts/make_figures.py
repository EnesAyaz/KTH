"""Generates the figures for the paper-style report:
  fig_loss_vs_fsw.pdf    -- P_cond/P_sw/P_total vs f_sw at the recommended N
  fig_loss_vs_n.pdf      -- P_cond/P_sw/P_total and max f_sw vs N (parallel-device sweep)
  fig_eon_eoff_vs_rg.pdf -- Eon, Eoff vs Id for several Rg (fixed L_loop)
  fig_eon_eoff_vs_lloop.pdf -- Eon, Eoff, overshoot vs Id for several L_loop (fixed Rg)
Reads outputs/EPC2361_eon_sweep.csv and outputs/EPC2361_eoff_sweep.csv (run
scripts/run_epc2361_sweep_v2.py first) and config/design_spec.yaml.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
FIG_DIR = PROJECT / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

from spb_bb.devices import load_device
from spb_bb.optimize import DesignSpec, design_sweep_over_n, evaluate_point, optimal_rg_on, find_min_rg_off_for_overshoot
from spb_bb.switching_loss import SwitchingLossModel
from spb_bb.ltspice.lookup import build_eon_interpolator, build_eoff_interpolator, load_sweep_csv

plt.rcParams.update({
    "font.size": 10,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.figsize": (5.0, 3.4),
    "figure.dpi": 150,
})

with open(PROJECT / "config" / "design_spec.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

device = load_device(str(PROJECT / "data" / "devices" / "EPC2361.yaml"))

eon_rows = load_sweep_csv(str(PROJECT / "outputs" / "EPC2361_eon_sweep.csv"))
eoff_rows = load_sweep_csv(str(PROJECT / "outputs" / "EPC2361_eoff_sweep.csv"))
eon_fn = build_eon_interpolator(eon_rows)
eoff_fn = build_eoff_interpolator(eoff_rows)
sw_model = SwitchingLossModel(device, mode="lookup", eon_lookup_fn=eon_fn, eoff_lookup_fn=eoff_fn)

l_loop_nH_default = cfg["search"]["loop_inductance_sweep_nH"][1]  # the "typical" middle value

spec = DesignSpec(
    p_out_leg=cfg["power"]["p_out_leg_W"],
    v_dc=cfg["power"]["v_dc_V"],
    v_rms_fund=cfg["power"]["v_rms_fund_V"],
    power_factor=cfg["power"]["power_factor"],
    modulation_index=cfg["power"]["modulation_index"],
    efficiency_target=cfg["targets"]["efficiency_full_load"],
    t_dead=cfg["timing"]["dead_time_ns"] * 1e-9,
    t_ambient_c=cfg["thermal"]["t_ambient_C"],
    r_th_interface=cfg["thermal"]["r_th_interface_C_per_W"],
    r_th_sink_amb=cfg["thermal"]["r_th_sink_amb_C_per_W"],
    l_loop_nH=l_loop_nH_default,
    t_j_ceiling_c=cfg["targets"]["t_j_ceiling_C"],
    v_overshoot_max_frac=cfg["targets"]["v_overshoot_max_frac"],
    svm=(cfg["power"]["modulation_scheme"].upper() == "SVM"),
)

rg_on_bounds = (cfg["search"]["rg_on_min_ohm"], cfg["search"]["rg_on_max_ohm"])
rg_off_bounds = (cfg["search"]["rg_off_min_ohm"], cfg["search"]["rg_off_max_ohm"])
fsw_bounds = (cfg["search"]["fsw_min_Hz"], cfg["search"]["fsw_max_Hz"])
n_range = range(1, cfg["search"]["n_parallel_max"] + 1)

print("Running N-parallel design sweep for figures...")
n_results = design_sweep_over_n(
    device, spec, sw_model, n_range=n_range, rg_on_bounds=rg_on_bounds,
    rg_off_bounds=rg_off_bounds, fsw_bounds=fsw_bounds, l_loop_nH=l_loop_nH_default,
)
best = max(n_results, key=lambda r: r.f_sw)
print(f"Recommended: N={best.n_parallel}, Rg_on={best.r_g_on}, Rg_off={best.r_g_off}, fsw={best.f_sw/1e3:.1f}kHz")

# ---------------------------------------------------------------------------
# Figure 1: loss vs f_sw at the recommended N (Rg fixed at the recommended values)
# ---------------------------------------------------------------------------
fsw_grid = np.linspace(fsw_bounds[0], fsw_bounds[1], 40)
p_cond, p_sw, p_total = [], [], []
for fsw in fsw_grid:
    r = evaluate_point(
        device, spec, fsw, best.r_g_on, best.r_g_off, best.n_parallel, sw_model, l_loop_nH=l_loop_nH_default
    )
    p_cond.append(r.p_cond_leg)
    p_sw.append(r.p_sw_leg)
    p_total.append(r.p_total_leg)

fig, ax = plt.subplots()
ax.plot(fsw_grid / 1e3, p_cond, label="$P_{cond}$", color="tab:blue")
ax.plot(fsw_grid / 1e3, p_sw, label="$P_{sw}$", color="tab:orange")
ax.plot(fsw_grid / 1e3, p_total, label="$P_{total}$", color="tab:red", linewidth=2)
ax.axhline(best.p_budget_leg, color="black", linestyle="--", linewidth=1, label="Loss budget")
ax.axvline(best.f_sw / 1e3, color="gray", linestyle=":", linewidth=1)
ax.set_xlabel("Switching frequency $f_{sw}$ (kHz)")
ax.set_ylabel("Leg power loss (W)")
ax.set_title(f"Loss vs. $f_{{sw}}$ at N={best.n_parallel}, $R_g$=({best.r_g_on:.1f}/{best.r_g_off:.1f})$\\Omega$")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(FIG_DIR / "fig_loss_vs_fsw.pdf")
plt.close(fig)
print("Saved fig_loss_vs_fsw.pdf")

# ---------------------------------------------------------------------------
# Figure 2: loss and max f_sw vs N
# ---------------------------------------------------------------------------
ns = [r.n_parallel for r in n_results]
p_cond_n = [r.p_cond_leg for r in n_results]
p_sw_n = [r.p_sw_leg for r in n_results]
fsw_n = [r.f_sw / 1e3 for r in n_results]

fig, ax1 = plt.subplots()
width = 0.35
ax1.bar([n - width / 2 for n in ns], p_cond_n, width, label="$P_{cond}$", color="tab:blue")
ax1.bar([n - width / 2 for n in ns], p_sw_n, width, bottom=p_cond_n, label="$P_{sw}$", color="tab:orange")
ax1.axhline(n_results[0].p_budget_leg, color="black", linestyle="--", linewidth=1, label="Loss budget")
ax1.set_xlabel("Parallel devices per switch position, $N$")
ax1.set_ylabel("Leg power loss (W)")
ax1.set_xticks(ns)
ax2 = ax1.twinx()
ax2.plot([n + width / 2 for n in ns], fsw_n, "D-", color="tab:green", label="Max $f_{sw}$")
ax2.set_ylabel("Max feasible $f_{sw}$ (kHz)", color="tab:green")
ax2.tick_params(axis="y", labelcolor="tab:green")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper right")
ax1.set_title("Loss composition and max $f_{sw}$ vs. parallel-device count")
fig.tight_layout()
fig.savefig(FIG_DIR / "fig_loss_vs_n.pdf")
plt.close(fig)
print("Saved fig_loss_vs_n.pdf")

# ---------------------------------------------------------------------------
# Figure 3: Eon, Eoff vs Id for several Rg, at a fixed (middle) L_loop
# ---------------------------------------------------------------------------
rg_list = sorted(set(r["r_g_on"] for r in eon_rows))
i_grid = np.linspace(30, cfg["power"]["p_out_leg_W"] / cfg["power"]["v_rms_fund_V"] / cfg["power"]["power_factor"] * np.sqrt(2), 60)

fig, (axl, axr) = plt.subplots(1, 2, figsize=(9.0, 3.4), sharey=False)
colors = plt.cm.viridis(np.linspace(0, 0.9, len(rg_list)))
for rg, c in zip(rg_list, colors):
    eon_vals = [eon_fn(i, l_loop_nH_default, rg) * 1e6 for i in i_grid]
    axl.plot(i_grid, eon_vals, color=c, label=f"$R_g$={rg:g}$\\Omega$")
for rg, c in zip(rg_list, colors):
    eoff_vals = [eoff_fn(i, l_loop_nH_default, rg)[0] * 1e6 for i in i_grid]
    axr.plot(i_grid, eoff_vals, color=c, label=f"$R_g$={rg:g}$\\Omega$")
axl.set_xlabel("Device current $I_D$ (A)")
axl.set_ylabel("$E_{on}$ ($\\mu$J)")
axl.set_title(f"$E_{{on}}$ vs $I_D$, $L_{{loop}}$={l_loop_nH_default:g} nH")
axl.legend(fontsize=7)
axr.set_xlabel("Device current $I_D$ (A)")
axr.set_ylabel("$E_{off}$ ($\\mu$J)")
axr.set_title(f"$E_{{off}}$ vs $I_D$, $L_{{loop}}$={l_loop_nH_default:g} nH")
axr.legend(fontsize=7)
fig.tight_layout()
fig.savefig(FIG_DIR / "fig_eon_eoff_vs_rg.pdf")
plt.close(fig)
print("Saved fig_eon_eoff_vs_rg.pdf")

# ---------------------------------------------------------------------------
# Figure 4: Eon, Eoff, overshoot vs Id for several L_loop, at the reference Rg=2 ohm
# ---------------------------------------------------------------------------
lloop_list = sorted(set(r["l_loop_nH"] for r in eon_rows))
rg_ref = 2.0

fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.4))
colors = plt.cm.plasma(np.linspace(0, 0.8, len(lloop_list)))
for l_nh, c in zip(lloop_list, colors):
    eon_vals = [eon_fn(i, l_nh, rg_ref) * 1e6 for i in i_grid]
    axes[0].plot(i_grid, eon_vals, color=c, label=f"$L_{{loop}}$={l_nh:g}nH")
for l_nh, c in zip(lloop_list, colors):
    eoff_vals = [eoff_fn(i, l_nh, rg_ref)[0] * 1e6 for i in i_grid]
    axes[1].plot(i_grid, eoff_vals, color=c, label=f"$L_{{loop}}$={l_nh:g}nH")
for l_nh, c in zip(lloop_list, colors):
    ovs_vals = [eoff_fn(i, l_nh, rg_ref)[1] for i in i_grid]
    axes[2].plot(i_grid, ovs_vals, color=c, label=f"$L_{{loop}}$={l_nh:g}nH")
axes[2].axhline(spec.v_overshoot_max_frac * spec.v_dc, color="black", linestyle="--", linewidth=1, label="Limit")
axes[0].set_ylabel("$E_{on}$ ($\\mu$J)")
axes[1].set_ylabel("$E_{off}$ ($\\mu$J)")
axes[2].set_ylabel("$V_{DS}$ overshoot (V)")
for ax, title in zip(axes, [f"$E_{{on}}$, $R_g$={rg_ref:g}$\\Omega$", f"$E_{{off}}$, $R_g$={rg_ref:g}$\\Omega$", f"Overshoot, $R_g$={rg_ref:g}$\\Omega$"]):
    ax.set_xlabel("Device current $I_D$ (A)")
    ax.set_title(title)
    ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig(FIG_DIR / "fig_eon_eoff_vs_lloop.pdf")
plt.close(fig)
print("Saved fig_eon_eoff_vs_lloop.pdf")

print("All figures generated in", FIG_DIR)

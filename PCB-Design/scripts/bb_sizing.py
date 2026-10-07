"""
Building block (one phase leg, 2 x EPC2361 per switch): DC-link capacitor sizing, ripple
current, conduction / dead-time / gate / capacitor loss budget.

    python scripts/bb_sizing.py   -> reports/building-block/data/sizing.json + figures

Switching energies come from the LTspice study (simulation/bb_spice), and are merged in
scripts/bb_losses.py.
"""
import json
import math
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "reports", "building-block")
os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)

SPEC = dict(
    Vdc=75.0, I_rms=100.0, f_sw=50e3, f_sw_max=100e3, M_rated=1.0, pf_rated=1.0,
    eta=0.995, n_par=2,
    Rds_25_typ=0.75e-3, Rds_25_max=1.0e-3, Rds_factor_100C=1.48, Rds_factor_125C=1.64,  # datasheet fig. 9
    Qg_typ=28e-9, Qg_max=34e-9, Vdrv=5.0, Qoss_75=113e-9, Eoss_75=2.9e-6,             # datasheet figs. 6, 7
    Vsd0=1.95, Rsd=5e-3,          # reverse conduction per device (fig. 8, 25 C, VGS = 0): VSD ~ 1.95 V + 5 mOhm * I
    t_dead=10e-9,                 # dead time per edge
    ripple_target=0.04,           # DC-link HF voltage ripple, peak-peak (= +/-2 %), fraction of Vdc
)


def three_phase_dc_link(M, phi, fsw=50e3, f1=200.0, I_rms=100.0, svpwm=True, npts_per_sw=200):
    """Ideal 3-phase 2-level inverter with a common triangular carrier. Returns time, leg-A input
    current, total DC-link current."""
    n_sw = int(round(fsw / f1))
    t = np.arange(n_sw * npts_per_sw) / (fsw * npts_per_sw)
    th = 2 * np.pi * f1 * t
    refs = np.array([M * np.sin(th - k * 2 * np.pi / 3) for k in range(3)])
    if svpwm:  # min-max zero-sequence injection
        refs = refs - 0.5 * (refs.max(axis=0) + refs.min(axis=0))
    carrier = 2 * np.abs(2 * ((t * fsw) % 1.0) - 1) - 1          # triangle -1..1
    s = (refs > carrier).astype(float)
    i = np.array([math.sqrt(2) * I_rms * np.sin(th - k * 2 * np.pi / 3 - phi) for k in range(3)])
    legs = s * i
    return t, legs[0], legs.sum(axis=0)


def ripple(t, i_in, C, fsw):
    """HF capacitor current (minus switching-period average) and worst peak-peak voltage ripple."""
    n = int(round(len(t) * fsw * (t[1] - t[0])))
    per = len(t) // n
    x = i_in[: n * per].reshape(n, per)
    i_c = (x - x.mean(axis=1, keepdims=True)).ravel()
    dt = t[1] - t[0]
    v = np.cumsum(i_c) * dt / C
    v = v.reshape(n, per)
    return math.sqrt(np.mean(i_c ** 2)), float((v.max(axis=1) - v.min(axis=1)).max())


def main():
    S = SPEC
    res = {"spec": S}
    I_pk = math.sqrt(2) * S["I_rms"]
    P_rated = S["M_rated"] * S["Vdc"] / (2 * math.sqrt(2)) * S["I_rms"] * S["pf_rated"]
    P_loss_budget = P_rated * (1 / S["eta"] - 1)
    res.update(I_pk=I_pk, P_rated=P_rated, P_loss_budget=P_loss_budget)

    # ---- DC-link: sweep modulation index and power factor
    grid = []
    for M in (0.1, 0.3, 0.5, 0.6, 0.7, 0.9, 1.0, 1.15):
        for pf in (1.0, 0.8, 0.5, 0.0):
            phi = math.acos(pf)
            t, iA, idc = three_phase_dc_link(M, phi, fsw=S["f_sw"])
            Ileg, dV_leg = ripple(t, iA, 1e-6, S["f_sw"])       # leg alone, per 1 uF
            Itot, dV_tot = ripple(t, idc, 1e-6, S["f_sw"])      # three legs sharing one bank, per 1 uF
            grid.append(dict(M=M, pf=pf, I_leg_hf=Ileg, I_3ph_hf=Itot, dVpp_leg_1uF=dV_leg, dVpp_3ph_1uF=dV_tot))
    res["dc_link_grid"] = grid
    worst_leg = max(grid, key=lambda g: g["I_leg_hf"])
    worst_3ph = max(grid, key=lambda g: g["I_3ph_hf"])
    worst_dv_leg = max(g["dVpp_leg_1uF"] for g in grid)
    worst_dv_3ph = max(g["dVpp_3ph_1uF"] for g in grid)
    dV_allowed = S["ripple_target"] * S["Vdc"]
    C_leg_alone = worst_dv_leg * 1e-6 / dV_allowed               # leg supplies its own ripple
    C_3ph_total = worst_dv_3ph * 1e-6 / dV_allowed               # one shared bank
    res.update(I_leg_hf_worst=worst_leg, I_3ph_hf_worst=worst_3ph, dV_allowed=dV_allowed,
               C_eff_leg_alone_uF=C_leg_alone * 1e6, C_eff_3ph_total_uF=C_3ph_total * 1e6,
               C_eff_per_block_shared_uF=C_3ph_total * 1e6 / 3)
    # same at 100 kHz scales with 1/f
    res["C_eff_per_block_shared_uF_100k"] = res["C_eff_per_block_shared_uF"] / 2

    # ---- selected bank per block (EPC9186-style MLCC DC link)
    bank = dict(
        bulk_part="Murata GRM32EC72A106KE05L, 10 uF 100 V X7S 1210", bulk_n=24, bulk_C_eff_each=3.0e-6,
        bulk_note="C at 75 V assumed 30 % of nominal; verify with Murata SimSurfing",
        hf_part="TDK C2012X7S2A105K125AB, 1 uF 100 V X7S 0805", hf_n=12, hf_C_eff_each=0.45e-6,
        hf_note="6 per cell, next to QH; C at 75 V assumed 45 %",
        esr_bulk_each=3e-3, esr_hf_each=6e-3)
    C_eff_block = bank["bulk_n"] * bank["bulk_C_eff_each"] + bank["hf_n"] * bank["hf_C_eff_each"]
    esr_bank = 1 / (bank["bulk_n"] / bank["esr_bulk_each"] + bank["hf_n"] / bank["esr_hf_each"])
    bank.update(C_eff_block=C_eff_block, esr_bank=esr_bank,
                dVpp_shared_3ph=worst_dv_3ph * 1e-6 / (3 * C_eff_block),
                dVpp_leg_alone=worst_dv_leg * 1e-6 / C_eff_block)
    res["bank"] = bank

    # ---- loss budget (switching energy added later)
    Rsw = lambda f: S["Rds_25_typ"] * f / S["n_par"]
    res["P_cond_typ_100C"] = S["I_rms"] ** 2 * Rsw(S["Rds_factor_100C"])
    res["P_cond_max_100C"] = S["I_rms"] ** 2 * S["Rds_25_max"] * S["Rds_factor_100C"] / S["n_par"]
    res["P_cond_typ_25C"] = S["I_rms"] ** 2 * Rsw(1.0)
    # dead time: two edges per period, reverse conduction of the 2 parallel devices at |i|
    th = np.linspace(0, np.pi, 2001)
    i_abs = I_pk * np.sin(th)
    vsd = S["Vsd0"] + S["Rsd"] * i_abs / S["n_par"]
    res["P_dead_50k"] = 2 * S["f_sw"] * S["t_dead"] * np.mean(vsd * i_abs)
    res["P_gate_50k"] = 4 * S["Qg_typ"] * S["Vdrv"] * S["f_sw"]
    res["P_ldo_50k"] = (12 - 5) * (4 * S["Qg_typ"] * S["f_sw"] + 1.5e-3)
    res["P_cap_rated"] = None  # filled below with the leg HF current at the rated point
    rated = [g for g in grid if g["M"] == 1.0 and g["pf"] == 1.0][0]
    res["I_leg_hf_rated"] = rated["I_leg_hf"]
    res["P_cap_rated"] = rated["I_leg_hf"] ** 2 * esr_bank
    res["P_cap_worst"] = worst_leg["I_leg_hf"] ** 2 * esr_bank
    # per-device conduction (each switch position conducts ~ half the fundamental)
    res["I_dev_rms"] = S["I_rms"] / math.sqrt(2) / S["n_par"]
    res["P_cond_dev_100C"] = res["I_dev_rms"] ** 2 * S["Rds_25_typ"] * S["Rds_factor_100C"]

    # ---- bootstrap / driver supply
    Qbank = S["n_par"] * S["Qg_max"]
    res["boot"] = dict(Q_bank=Qbank, C_boot_min_100mV=Qbank / 0.1, C_boot_selected=1e-6,
                       droop_selected=Qbank / 1e-6, C_vcc_selected=10e-6,
                       I_gate_avg_100k=4 * S["Qg_max"] * 100e3)

    with open(os.path.join(OUT, "data", "sizing.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)

    # ---- figure: HF ripple current vs M
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    for pf, c in zip((1.0, 0.8, 0.5, 0.0), ("C0", "C1", "C2", "C3")):
        g = [x for x in grid if x["pf"] == pf]
        ax[0].plot([x["M"] for x in g], [x["I_leg_hf"] for x in g], "-o", color=c, ms=3, label="leg alone, cos phi=%.1f" % pf)
        ax[0].plot([x["M"] for x in g], [x["I_3ph_hf"] / 3 for x in g], "--", color=c, label="3 legs shared, per block")
        ax[1].plot([x["M"] for x in g], [x["dVpp_3ph_1uF"] / (3 * C_eff_block * 1e6) for x in g], "-o", color=c, ms=3,
                   label="cos phi=%.1f" % pf)
    ax[0].set_xlabel("modulation index M (SVPWM)")
    ax[0].set_ylabel("HF capacitor current [A rms]")
    ax[0].legend(fontsize=6, ncol=2)
    ax[1].axhline(dV_allowed, color="k", ls=":", lw=1)
    ax[1].set_xlabel("modulation index M (SVPWM)")
    ax[1].set_ylabel("DC-link ripple [V pk-pk]")
    ax[1].set_title("3 blocks sharing the bus, %.0f uF eff. per block, 50 kHz" % (C_eff_block * 1e6), fontsize=9)
    ax[1].legend(fontsize=7)
    for a in ax:
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "figures", "dc_link_ripple.pdf"))
    fig.savefig(os.path.join(OUT, "figures", "dc_link_ripple.png"), dpi=130)

    for k in ("P_rated", "P_loss_budget", "C_eff_leg_alone_uF", "C_eff_3ph_total_uF", "C_eff_per_block_shared_uF",
              "P_cond_typ_25C", "P_cond_typ_100C", "P_cond_max_100C", "P_dead_50k", "P_gate_50k", "P_ldo_50k",
              "I_leg_hf_rated", "P_cap_rated", "P_cap_worst", "I_dev_rms", "P_cond_dev_100C"):
        print("%-28s %10.3f" % (k, res[k]))
    print("worst leg HF current", worst_leg)
    print("worst 3ph HF current", worst_3ph)
    print("bank", {k: v for k, v in bank.items() if not isinstance(v, str)})


if __name__ == "__main__":
    main()

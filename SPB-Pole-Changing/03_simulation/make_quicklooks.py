import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import spb_core as c, sync_model as s

J = c.J
sp = np.array(J["speed_rpm"])
N = np.linspace(300, 8000, 24)
c.CAP_MODE["mode"] = "an_caps"
P4, P2 = c.im_params(4), c.im_params(2)
pm = s.Sync("PMSM", "2p8")
w8, w4 = s.Sync("WRSM", "2p8", tag="_gs4"), s.Sync("WRSM", "2p4", tag="_gs4")
fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
curves = {
    "IM": (J["machines"]["IM"], [("2p8", lambda n: c.im_envelope(P4, n)[0]), ("2p4", lambda n: c.im_envelope(P2, n)[0])]),
    "PMSM": (J["machines"]["PMSM"], [("2p8", lambda n: pm.envelope(n)[0])]),
    "WRSM (free I_d, I_f)": (J["machines"]["WRSM_freeId"], [("2p8", lambda n: w8.envelope(n)[0]), ("2p4", lambda n: w4.envelope(n)[0])]),
}
for a, (name, (an, sims)) in zip(ax, curves.items()):
    for key, f in sims:
        a.plot(sp, an[key]["torque_Nm"], "-", lw=1.5, label=f"analyst {key}")
        a.plot(N, [f(n) for n in N], "--", lw=1.5, label=f"simulation {key}")
    a.set_title(name); a.set_xlabel("speed (rpm)"); a.set_ylabel("torque (Nm)"); a.set_xlim(0, 8000); a.grid(alpha=.3); a.legend(fontsize=7)
fig.tight_layout(); fig.savefig("scratch/validation_envelopes.png", dpi=130)

# WRSM study
st = json.load(open("results/wrsm_pole_change_study.json"))
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for name, v in st["variants"].items():
    l, = ax[0].plot(v["speed_rpm"], v["T_2p4"], "-o", ms=3, label=f"2p4: {name}")
    ax[0].plot(v["speed_rpm"], v["T_2p8"], ":", color=l.get_color())
ax[0].set_xlabel("rpm"); ax[0].set_ylabel("torque (Nm)"); ax[0].legend(fontsize=7); ax[0].grid(alpha=.3); ax[0].set_title("WRSM: 2p4 (solid) vs 2p8 (dotted)")
sc = st["scaling"]["noload_curves"]
ax[1].plot(sc["If"], sc["psi_f_2p8_Wb"], label="psi_f 2p8"); ax[1].plot(sc["If"], sc["psi_f_2p4_Wb"], label="psi_f 2p4 (yoke saturates)")
ax[1].set_xlabel("I_f (pu)"); ax[1].set_ylabel("rms flux linkage per coil (Wb)"); ax[1].legend(); ax[1].grid(alpha=.3)
fig.tight_layout(); fig.savefig("scratch/wrsm_pole_change_study.png", dpi=130)

# IM transition
fig, ax = plt.subplots(2, 3, figsize=(14, 6.5))
for r, g in enumerate((0, 2)):
    d = np.load(f"scratch/im_transition_best_g{g}.npz")
    t = d["t"]
    ax[r, 0].plot(t, d["T4"], label="mode 2p8"); ax[r, 0].plot(t, d["T2"], label="mode 2p4"); ax[r, 0].plot(t, d["T4"] + d["T2"], "k", label="sum")
    ax[r, 0].plot(t, d["T_load"], "--", color="gray", label="road load"); ax[r, 0].set_ylabel("torque (Nm)"); ax[r, 0].legend(fontsize=7)
    ax[r, 1].plot(t, d["I_rms"] / c.IMAX); ax[r, 1].axhline(1, color="r", ls="--"); ax[r, 1].set_ylabel("I_rms / I_max (per coil)")
    ax[r, 2].plot(t, d["psi4"], label="psi_r 2p8"); ax[r, 2].plot(t, d["psi2"], label="psi_r 2p4"); ax[r, 2].set_ylabel("rotor flux (Wb rms-ish)"); ax[r, 2].legend(fontsize=7)
    ax[r, 0].set_title(f"IM 8->4 pole at 2100 rpm, grade {g} %")
    for a in ax[r]:
        a.set_xlabel("t (s)"); a.grid(alpha=.3)
fig.tight_layout(); fig.savefig("scratch/im_pole_transition.png", dpi=130)

# WRSM transition
if os.path.exists("scratch/wrsm_transition_series.npz"):
    z = np.load("scratch/wrsm_transition_series.npz")
    keys = sorted({k.split("__")[0] for k in z.files})
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    for k in keys:
        if not k.startswith("gs4"):
            continue
        ax[0].plot(z[k + "__t"], z[k + "__I_B"], label=k[4:])
        ax[1].plot(z[k + "__t"], z[k + "__T"], label=k[4:])
        ax[2].plot(z[k + "__t"], z[k + "__n"], label=k[4:])
    ax[0].set_ylabel("group-B field current (pu)"); ax[1].set_ylabel("torque (Nm)"); ax[2].set_ylabel("speed (rpm)")
    for a in ax:
        a.set_xlabel("t (s)"); a.grid(alpha=.3); a.legend(fontsize=6)
    fig.tight_layout(); fig.savefig("scratch/wrsm_pole_transition.png", dpi=130)
print("done")

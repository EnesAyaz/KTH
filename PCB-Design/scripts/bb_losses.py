"""
Building block: merge sizing, Q3D and LTspice results -> gate-resistor choice, loss breakdown,
efficiency vs switching frequency, figures and LaTeX macros for the report.

    python scripts/bb_losses.py
      reads  reports/building-block/data/sizing.json
             simulation/bb_q3d/results/summary.json
             simulation/bb_spice/BB_rg_sweep.log, BB_energy_sweep.log
      writes reports/building-block/data/results.json, reports/building-block/numbers.tex, figures
"""
import json
import math
import os
import re

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "reports", "building-block")
SP = os.path.join(ROOT, "simulation", "bb_spice")
FIG = os.path.join(REP, "figures")

LIMITS = dict(VDS_max=90.0, VGS_bump_max=1.0, VGS_min=-3.0)


def parse_log(path):
    """LTspice .log with .step -> {meas_name: [values per step]}, [step parameter dicts]."""
    raw = open(path, "rb").read()
    txt = raw.decode("utf-16-le") if b"\x00" in raw[:200] else raw.decode("latin-1")
    txt = txt.replace("\r\n", "\n")
    steps = [dict(re.findall(r"(\w+)=([\-\d.eE+]+)", m)) for m in re.findall(r"^\.step (.*)$", txt, re.M)]
    meas = {}
    for m in re.finditer(r"Measurement: (\w+)\n\s+step\t[^\n]*\n((?:\s+\d+\t[^\n]*\n)+)", txt):
        rows = [r.split("\t") for r in m.group(2).strip("\n").split("\n")]
        meas[m.group(1).lower()] = [float(r[1]) if r[1].strip() not in ("", "FAILED") else float("nan") for r in rows]
    return meas, [{k.lower(): float(v) for k, v in s.items()} for s in steps]


def copper_loss(rdc, S, M=1.0):
    """PCB copper loss at the rated point from the Q3D DC resistance matrix (two cells in parallel).
    AC path: full load current through the high- or low-side branch pair (duty d / 1-d).
    DC+ / DC- planes: switching-period average currents d*i and (1-d)*i (HF ripple stays in the local loop)."""
    names = rdc["names"]
    R = np.array(rdc["matrix"])
    ix = {n: k for k, n in enumerate(names)}

    def pair(a, b):
        return 0.25 * (R[ix[a], ix[a]] + R[ix[b], ix[b]] + 2 * R[ix[a], ix[b]])

    r_qhs, r_qld = pair("AC:QH_S_L", "AC:QH_S_R"), pair("AC:QL_D_L", "AC:QL_D_R")
    r_qhd, r_qls = pair("DCP:QH_D_L", "DCP:QH_D_R"), pair("DCN:QL_S_L", "DCN:QL_S_R")
    th = np.linspace(0, 2 * np.pi, 3601)
    refs = np.array([M * np.sin(th - k * 2 * np.pi / 3) for k in range(3)])
    m = refs[0] - 0.5 * (refs.max(axis=0) + refs.min(axis=0))      # SVPWM, leg A
    d = 0.5 * (1 + m)
    i = math.sqrt(2) * S["I_rms"] * np.sin(th)                       # cos phi = 1
    parts = dict(ac=float(np.mean(i ** 2 * (d * r_qhs + (1 - d) * r_qld))),
                 dcp=float(np.mean((d * i) ** 2) * r_qhd),
                 dcn=float(np.mean(((1 - d) * i) ** 2) * r_qls),
                 r_ac_mohm=1e3 * (r_qhs + r_qld) / 2, r_dcp_mohm=1e3 * r_qhd, r_dcn_mohm=1e3 * r_qls,
                 i_dcp_rms=float(math.sqrt(np.mean((d * i) ** 2))))
    return parts["ac"] + parts["dcp"] + parts["dcn"], parts


def main():
    sz = json.load(open(os.path.join(REP, "data", "sizing.json")))
    q3d = json.load(open(os.path.join(ROOT, "simulation", "bb_q3d", "results", "summary.json")))
    out = {"limits": LIMITS}

    # ---------------- gate-resistor study at 160 A ----------------
    m, st = parse_log(os.path.join(SP, "BB_rg_sweep.log"))
    rg = []
    for i, s in enumerate(st):
        rg.append(dict(RGON=s["rgon"], RGOFF=s["rgoff"], Eon=m["eon"][i], Eoff=m["eoff"][i],
                       VDSH=m["vdsh_pk"][i], VDSL=m["vdsl_pk"][i], VGSH=m["vgsh_bump"][i],
                       VGSLmin=m["vgsl_min"][i], VGSHmin=m["vgsh_min"][i], dvdt_on=m["dvdt_on"][i],
                       dvdt_off=m["dvdt_off"][i], IDpk=m["id_pk"][i]))
    for r in rg:
        r["ok"] = (max(r["VDSH"], r["VDSL"]) <= LIMITS["VDS_max"] and r["VGSH"] <= LIMITS["VGS_bump_max"]
                   and min(r["VGSLmin"], r["VGSHmin"]) >= LIMITS["VGS_min"])
    feas = [r for r in rg if r["ok"]]
    choice = min(feas, key=lambda r: r["Eon"] + r["Eoff"]) if feas else None
    out["rg_study"] = rg
    out["rg_choice"] = choice

    fig, ax = plt.subplots(1, 3, figsize=(13, 3.6))
    for rgoff, c in zip(sorted({r["RGOFF"] for r in rg}), ("C0", "C1", "C2")):
        sub = sorted([r for r in rg if r["RGOFF"] == rgoff], key=lambda r: r["RGON"])
        x = [r["RGON"] for r in sub]
        ax[0].plot(x, [r["VDSH"] for r in sub], "-o", color=c, ms=3, label="QH (QL turn-on), Rg_off=%g" % rgoff)
        ax[0].plot(x, [r["VDSL"] for r in sub], "--", color=c, label="QL turn-off, Rg_off=%g" % rgoff)
        ax[1].plot(x, [(r["Eon"] + r["Eoff"]) * 1e6 for r in sub], "-o", color=c, ms=3, label="Eon+Eoff, Rg_off=%g" % rgoff)
        ax[1].plot(x, [r["Eon"] * 1e6 for r in sub], ":", color=c)
        ax[2].plot(x, [r["VGSH"] for r in sub], "-o", color=c, ms=3, label="QH bump, Rg_off=%g" % rgoff)
    ax[0].axhline(LIMITS["VDS_max"], color="k", ls=":", lw=1)
    ax[2].axhline(LIMITS["VGS_bump_max"], color="k", ls=":", lw=1)
    ax[2].axhline(0.8, color="grey", ls=":", lw=1)
    ax[0].set_ylabel("peak VDS [V]")
    ax[1].set_ylabel("Eon+Eoff [uJ] (dotted: Eon)")
    ax[2].set_ylabel("off-state VGS bump on QH [V]")
    for a in ax:
        a.set_xlabel("Rg_on per FET [ohm]")
        a.grid(alpha=0.3)
        a.legend(fontsize=6)
    if choice:
        for a in ax:
            a.axvline(choice["RGON"], color="green", lw=0.8)
    fig.suptitle("Gate-resistor study, 75 V / 160 A, 2 x EPC2361 per switch, Q3D building-block parasitics", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "rg_study.pdf"))
    fig.savefig(os.path.join(FIG, "rg_study.png"), dpi=130)

    # ---------------- switching energy vs current (selected Rg) ----------------
    m, st = parse_log(os.path.join(SP, "BB_energy_sweep.log"))
    I = np.array([abs(v) for v in m["iload"]])
    Eon, Eoff = np.array(m["eon"]), np.array(m["eoff"])
    pon, poff = np.polyfit(I, Eon, 2), np.polyfit(I, Eoff, 2)
    out["energy"] = dict(I=I.tolist(), Eon=Eon.tolist(), Eoff=Eoff.tolist(), fit_on=pon.tolist(), fit_off=poff.tolist(),
                         VDSH=m["vdsh_pk"], VDSL=m["vdsl_pk"], dvdt_on=m["dvdt_on"], dvdt_off=m["dvdt_off"])

    # ---------------- losses vs fsw at the rated point ----------------
    S = sz["spec"]
    I_pk = sz["I_pk"]
    th = np.linspace(0, np.pi, 4001)
    i_abs = I_pk * np.sin(th)
    E_avg = float(np.mean(np.polyval(pon, i_abs) + np.polyval(poff, i_abs)))   # J per switching period
    rdc = q3d["BB_PL_Rdc"]
    # adopted stack-up: 2 oz inner layers (BB_PL_2oz); 1 oz kept for comparison
    P_cu_1oz, cu_1oz = copper_loss(q3d["BB_PL_Rdc"], S)
    P_cu, cu_parts = copper_loss(q3d["BB_PL_2oz_Rdc"], S) if "BB_PL_2oz_Rdc" in q3d else (P_cu_1oz, cu_1oz)
    out["copper"], out["copper_1oz"] = cu_parts, cu_1oz
    out["loop_2oz"] = q3d.get("BB_PL_2oz_loop")
    # switching-harmonic copper loss and MLCC ESR loss from the frequency-domain network with the Q3D sweep
    # (scripts/bb_copper_hf.py, SVM, M = 1, cos phi = 1); falls back to the ESR-only estimate without it
    hf_path = os.path.join(REP, "data", "copper_hf.json")
    hf = json.load(open(hf_path)) if os.path.exists(hf_path) else None
    if hf:
        fv = np.array([r["f"] for r in hf["vs_f"]])
        cu_hf_f = lambda f: float(np.interp(f, fv, [r["cu_hf"] for r in hf["vs_f"]]))  # noqa: E731
        cap_f = lambda f: float(np.interp(f, fv, [r["caps"] for r in hf["vs_f"]]))  # noqa: E731
        out["cu_hf_source"] = hf["source"]
        out["cu_hf_vs_M"] = hf["vs_M"]
    else:
        cu_hf_f = lambda f: 0.0  # noqa: E731
        cap_f = lambda f: sz["P_cap_rated"]  # noqa: E731
    fs = np.array([20e3, 30e3, 40e3, 50e3, 60e3, 80e3, 100e3])
    rows = []
    for f in fs:
        d = dict(f=f, cond=sz["P_cond_typ_100C"], sw=E_avg * f, dead=sz["P_dead_50k"] * f / 50e3,
                 gate=(sz["P_gate_50k"] + sz["P_ldo_50k"]) * f / 50e3, cap=cap_f(f), cu=P_cu, cu_hf=cu_hf_f(f))
        d["total"] = sum(v for k, v in d.items() if k != "f")
        d["eta"] = sz["P_rated"] / (sz["P_rated"] + d["total"])
        rows.append(d)
    out["loss_vs_f"] = rows
    r50 = [r for r in rows if r["f"] == 50e3][0]
    out["E_avg_uJ"] = E_avg * 1e6
    out["P_cu"] = P_cu
    out["P_cu_hf"] = r50["cu_hf"]
    out["P_cap_net"] = r50["cap"]
    worst = dict(r50)
    worst["cond"] = sz["P_cond_max_100C"]
    worst["total"] = sum(v for k, v in worst.items() if k not in ("f", "eta", "total"))
    worst["eta"] = sz["P_rated"] / (sz["P_rated"] + worst["total"])
    out["worst_50k_maxRds"] = worst
    f_max = max([r["f"] for r in rows if r["eta"] >= S["eta"]], default=0)
    out["f_max_for_eta"] = f_max
    # per-device temperature estimate (TIM 1.9 K/W per device + 0.2 K/W junction-case, heatsink at 60 C)
    P_dev = (r50["cond"] + r50["sw"] + r50["dead"]) / 4
    out["P_dev_50k"] = P_dev
    out["Tj_est"] = 60 + P_dev * (0.2 + 1.9)

    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    keys = [("cond", "conduction (typ, 100 C)"), ("sw", "switching (LTspice E(i))"), ("dead", "dead time"),
            ("cu", "PCB copper, load current (Q3D DC R)"), ("cu_hf", "PCB copper, switching harmonics (Q3D sweep)"),
            ("cap", "MLCC ESR"), ("gate", "gate drive + LDO")]
    bottom = np.zeros(len(rows))
    for k, lab in keys:
        v = np.array([r[k] for r in rows])
        ax[0].bar([r["f"] / 1e3 for r in rows], v, 7, bottom=bottom, label=lab)
        bottom += v
    ax[0].axhline(sz["P_loss_budget"], color="k", ls=":", lw=1)
    ax[0].text(21, sz["P_loss_budget"] + 0.2, "99.5 %% budget = %.1f W" % sz["P_loss_budget"], fontsize=8)
    ax[0].set_xlabel("switching frequency [kHz]")
    ax[0].set_ylabel("loss per phase leg [W]")
    ax[0].legend(fontsize=7)
    ax[1].plot(I, Eon * 1e6, "o-", label="Eon (switch position, 2 FETs)")
    ax[1].plot(I, Eoff * 1e6, "s-", label="Eoff")
    ii = np.linspace(0, I.max(), 100)
    ax[1].plot(ii, np.polyval(pon, ii) * 1e6, ":", color="C0")
    ax[1].plot(ii, np.polyval(poff, ii) * 1e6, ":", color="C1")
    ax[1].set_xlabel("switched current [A]")
    ax[1].set_ylabel("energy [uJ]")
    ax[1].legend(fontsize=8)
    for a in ax:
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "losses.pdf"))
    fig.savefig(os.path.join(FIG, "losses.png"), dpi=130)

    json.dump(out, open(os.path.join(REP, "data", "results.json"), "w"), indent=1, default=float)

    # ---------------- LaTeX macros ----------------
    loop = q3d["BB_PL_loop"]
    gl = q3d["BB_GL_loop"]
    mac = {
        "Prated": "%.2f" % (sz["P_rated"] / 1e3), "Pbudget": "%.1f" % sz["P_loss_budget"],
        "Ipk": "%.0f" % I_pk, "CreqBlock": "%.0f" % sz["C_eff_per_block_shared_uF"],
        "CreqTotal": "%.0f" % sz["C_eff_3ph_total_uF"], "CreqAlone": "%.0f" % sz["C_eff_leg_alone_uF"],
        "CeffBlock": "%.0f" % (sz["bank"]["C_eff_block"] * 1e6), "dVshared": "%.1f" % sz["bank"]["dVpp_shared_3ph"],
        "dValone": "%.1f" % sz["bank"]["dVpp_leg_alone"], "IlegHFworst": "%.0f" % sz["I_leg_hf_worst"]["I_leg_hf"],
        "IlegHFrated": "%.0f" % sz["I_leg_hf_rated"], "IthreeHF": "%.0f" % sz["I_3ph_hf_worst"]["I_3ph_hf"],
        "PcondTyp": "%.2f" % sz["P_cond_typ_100C"], "PcondMax": "%.2f" % sz["P_cond_max_100C"],
        "PcondCold": "%.2f" % sz["P_cond_typ_25C"], "Pdead": "%.2f" % sz["P_dead_50k"],
        "Pgate": "%.3f" % (sz["P_gate_50k"] + sz["P_ldo_50k"]), "Pcap": "%.2f" % r50["cap"],
        "PcuHf": "%.2f" % r50["cu_hf"], "PcuTot": "%.2f" % (P_cu + r50["cu_hf"]),
        "PcuHfLowM": "%.1f" % max([r["cu_hf"] for r in out.get("cu_hf_vs_M", [])] or [0.0]),
        "PcapOld": "%.2f" % sz["P_cap_rated"],
        "Pcu": "%.2f" % P_cu, "Psw": "%.2f" % r50["sw"], "Ptot": "%.2f" % r50["total"],
        "PcuOneOz": "%.2f" % P_cu_1oz, "PcuAC": "%.2f" % cu_parts["ac"], "PcuDCP": "%.2f" % cu_parts["dcp"],
        "PcuDCN": "%.2f" % cu_parts["dcn"], "RacPath": "%.3f" % cu_parts["r_ac_mohm"],
        "RdcpPath": "%.3f" % cu_parts["r_dcp_mohm"], "RdcnPath": "%.3f" % cu_parts["r_dcn_mohm"],
        "RdcpPathOneOz": "%.3f" % cu_1oz["r_dcp_mohm"], "RdcnPathOneOz": "%.3f" % cu_1oz["r_dcn_mohm"],
        "IdcpRms": "%.0f" % cu_parts["i_dcp_rms"],
        "LloopTwoOz": "%.3f" % q3d["BB_PL_2oz_loop"]["local_and_bank_esl"]["L_cell_L_nH"] if "BB_PL_2oz_loop" in q3d else "n/a",
        "Eta": "%.2f" % (100 * r50["eta"]), "EtaWorst": "%.2f" % (100 * worst["eta"]), "PtotWorst": "%.2f" % worst["total"],
        "Eavg": "%.1f" % (E_avg * 1e6), "Fmax": "%.0f" % (f_max / 1e3), "Pdev": "%.2f" % P_dev, "Tj": "%.0f" % out["Tj_est"],
        "Idev": "%.1f" % sz["I_dev_rms"],
        "LloopCu": "%.3f" % loop["local_and_bank_copper"]["L_cell_L_nH"],
        "LloopEsl": "%.3f" % loop["local_and_bank_esl"]["L_cell_L_nH"],
        "LloopLocalEsl": "%.3f" % loop["local_only_esl"]["L_cell_L_nH"],
        "LgateOne": "%.2f" % gl["L_gate_L_nH"], "LgateBoth": "%.2f" % gl["L_gate_both_driven_nH"],
        "RhiPath": "%.3f" % (rdc["R_high_path"] * 1e3), "RloPath": "%.3f" % (rdc["R_low_path"] * 1e3),
        "CbootSel": "1", "CbootMin": "%.0f" % (sz["boot"]["C_boot_min_100mV"] * 1e9),
        "BootDroop": "%.0f" % (sz["boot"]["droop_selected"] * 1e3),
    }
    if choice:
        mac.update(RgOn="%g" % choice["RGON"], RgOff="%g" % choice["RGOFF"], VdsH="%.1f" % choice["VDSH"],
                   VdsL="%.1f" % choice["VDSL"], VgsBump="%.2f" % choice["VGSH"], VgsMin="%.2f" % min(choice["VGSLmin"], choice["VGSHmin"]),
                   EonPk="%.1f" % (choice["Eon"] * 1e6), EoffPk="%.1f" % (choice["Eoff"] * 1e6),
                   DvdtOn="%.0f" % choice["dvdt_on"], DvdtOff="%.0f" % choice["dvdt_off"])
    with open(os.path.join(REP, "numbers.tex"), "w") as f:
        f.write("%% generated by scripts/bb_losses.py\n")
        for k, v in mac.items():
            f.write("\\newcommand{\\%s}{%s}\n" % (k, v))
    print(json.dumps({k: v for k, v in out.items() if k not in ("rg_study", "energy", "loss_vs_f")}, indent=1, default=float))
    print("feasible Rg pairs:", [(r["RGON"], r["RGOFF"]) for r in feas])


if __name__ == "__main__":
    main()

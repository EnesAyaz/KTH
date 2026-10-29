"""T03d - Gear/e-axle losses vs ratio and stage count, and motor friction + windage vs speed and rotor size.

Run from repo root:  python 02_analytics/drivetrain_losses.py
Output: 02_analytics/results/drivetrain_losses.json
Assumptions: 02_analytics/assumptions.md, section T03d.

Public, vectorised functions for T07 (speed-torque maps / cycle traces):
  gear_topology(G, kind)                      -> list of stages (wheel side first)
  gear_motor_point(T_wheel, n_wheel, stages)  -> T_motor, n_motor, P_gear_loss (+ per-stage breakdown)
  mech_losses(n_rpm, T_motor, rotor)          -> dict of bearing / seal / gap windage / end-disc windage (W)
  rotor_from_design(R_gap_m, L_stk_m)         -> rotor dict used by mech_losses
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ.setdefault("SPB_P_RATED_KW", "300")   # D02 final
import torque_speed_envelope as T3  # noqa: E402
import fair_baselines as FB         # noqa: E402

OUT_JSON = os.path.join(ROOT, "02_analytics", "results", "drivetrain_losses.json")
FB_JSON = os.path.join(ROOT, "02_analytics", "results", "fair_baselines.json")
T300_JSON = os.path.join(ROOT, "02_analytics", "results", "torque_speed_envelope_300kW.json")
RPM = T3.RPM

# ----------------------------------------------------------------------------------
# 1. Gear stages - VECTO generic transmission loss (GenericTransmissionComponentData.cs,
#    Constants.GenericLossMapSettings, code.europa.eu/vecto/vecto @ 68a719e):
#    T_loss,out = Td0/2 + Td0/2 * n_out/150 + |T_out| (1/eta - 1),  Td0 = 52.5 + 15 i  [Nm, output side]
# ----------------------------------------------------------------------------------
VECTO_GEN = dict(T0_Nm=52.5, T1_Nm=15.0, Td_n_rpm=150.0, eta_mesh=0.98,
                 source="VECTO stable @68a719e: VectoCore/Models/GenericModelData/GenericTransmissionComponentData.cs + Configuration/Constants.cs (GenericLossMapSettings)")
GEAR = dict(
    i_axle_nominal=3.0, i_axle_min=2.5, i_axle_max=4.5,  # hypoid axle ratio range (assumed, typical tractor axles)
    i_stage_max=5.0,                                      # max ratio per helical reduction stage (assumed)
    eta_mesh_hypoid=0.98,                                 # VECTO generic
    eta_mesh_helical=0.98,                                # VECTO generic (sensitivity: 0.99)
    T_ref_axle_out_Nm=FB.T_START_WHEEL,                   # drag scaling reference: axle rated output torque (12 % start)
    drag_scale_variants={"VECTO_generic": 1.0, "certified_like": 0.3, "EU2017": "EU2017"},
    two_speed_idle_pair_drag_factor=1.0,                  # idle (unloaded) gear pair: full drag term of that pair
)


def gear_topology(G, kind="single", G_alt=None, eta_helical=None):
    """Stages from wheel to motor. kind: 'single' (axle + 1 helical stage), 'two_stage' (axle + 2 helical),
    'two_speed' (axle + 1 helical stage with two selectable pairs; G = engaged ratio, G_alt = idle ratio).
    Returns None if the ratio cannot be built with the stage limits."""
    eh = GEAR["eta_mesh_helical"] if eta_helical is None else eta_helical
    ia = GEAR["i_axle_nominal"]
    if kind == "single":
        i1 = G / ia
        if i1 > GEAR["i_stage_max"]:
            ia = G / GEAR["i_stage_max"]
            if ia > GEAR["i_axle_max"]:
                return None
            i1 = GEAR["i_stage_max"]
        if i1 < 1.0:
            ia, i1 = max(G, GEAR["i_axle_min"]), 1.0
        return [dict(name="axle_hypoid", i=ia, eta=GEAR["eta_mesh_hypoid"]), dict(name="helical_1", i=i1, eta=eh)]
    if kind == "two_stage":
        r = math.sqrt(G / ia)
        if r > GEAR["i_stage_max"]:
            return None
        return [dict(name="axle_hypoid", i=ia, eta=GEAR["eta_mesh_hypoid"]), dict(name="helical_1", i=r, eta=eh),
                dict(name="helical_2", i=r, eta=eh)]
    if kind == "two_speed":
        if G_alt and max(G, G_alt) / ia > GEAR["i_stage_max"]:
            ia = min(max(G, G_alt) / GEAR["i_stage_max"], GEAR["i_axle_max"])
        i1, i_idle = G / ia, (G_alt / ia if G_alt else None)
        if i1 > GEAR["i_stage_max"] or (i_idle and i_idle > GEAR["i_stage_max"]):
            return None
        st = [dict(name="axle_hypoid", i=ia, eta=GEAR["eta_mesh_hypoid"]), dict(name="helical_1_engaged", i=i1, eta=eh)]
        if i_idle:
            st.append(dict(name="helical_1_idle_pair", i=i_idle, eta=1.0, idle=True))
        return st
    raise ValueError(kind)


def _stage_loss_out(T_out, n_out_rpm, i, eta, scale):
    Td0 = (VECTO_GEN["T0_Nm"] + VECTO_GEN["T1_Nm"] * i) * scale
    return Td0 / 2 + Td0 / 2 * np.abs(n_out_rpm) / VECTO_GEN["Td_n_rpm"] + np.abs(T_out) * (1 / eta - 1)


EU2017 = dict(axle_T0_Nm=70.0, axle_T1_Nm=20.0, axle_eta=0.98, helical_eta=0.986,
              source="Regulation (EU) 2017/2400 Annex VII (SR axle standard loss) and Annex VI App. 7 (certified mesh efficiency "
                     "0.986 external-external) - key EU2017regulation, 01_literature/inputs_for_analyst.md section 8.1",
              helical_drag="own assumption: helical-stage drag = axle-type T_d0(i) scaled by the stage's rated output torque, speed-independent like the EU axle term")


def gear_motor_point_eu(T_wheel, n_wheel_rpm, stages):
    """EU 2017/2400 regulatory baseline: T_loss,out = T_d0 + |T_out|(1/eta - 1), T_d0 = 70 + 20 i (speed-independent)."""
    T = np.asarray(T_wheel, dtype=float)
    n = np.asarray(n_wheel_rpm, dtype=float)
    P_total = np.zeros(np.broadcast(T, n).shape)
    T_cap = GEAR["T_ref_axle_out_Nm"]
    parts = {}
    for s in stages:
        if s.get("idle"):
            continue
        eta = EU2017["axle_eta"] if s["name"].startswith("axle") else EU2017["helical_eta"]
        Td0 = (EU2017["axle_T0_Nm"] + EU2017["axle_T1_Nm"] * s["i"]) * T_cap / GEAR["T_ref_axle_out_Nm"]
        Tl = Td0 * (np.abs(n) > 0) + np.abs(T) * (1 / eta - 1)
        P = Tl * np.abs(n) * RPM
        parts[s["name"]] = P
        P_total = P_total + P
        T = (T + Tl) / s["i"]
        n = n * s["i"]
        T_cap = T_cap / s["i"]
    engaged = [s for s in stages if not s.get("idle")]
    for s in stages:   # idle pair of a 2-speed: drag only; it turns with the engaged stage's output shaft
        if s.get("idle"):
            i_axle, i_eng = engaged[0]["i"], engaged[1]["i"]
            Td0 = (EU2017["axle_T0_Nm"] + EU2017["axle_T1_Nm"] * s["i"]) / i_axle     # scaled to that shaft's torque rating
            n_out = np.abs(np.asarray(n_wheel_rpm, dtype=float)) * i_axle
            P_i = Td0 * (n_out > 0) * n_out * RPM
            parts[s["name"]] = P_i
            P_total = P_total + P_i
            T = T + Td0 * (n_out > 0) / i_eng
    return dict(T_motor_Nm=T, n_motor_rpm=n, P_gear_loss_W=P_total, parts_W=parts)


def gear_motor_point(T_wheel, n_wheel_rpm, stages, drag_scale=1.0):
    if drag_scale == "EU2017":
        return gear_motor_point_eu(T_wheel, n_wheel_rpm, stages)
    """Propagate wheel torque/speed to the motor through the stages (vectorised).
    Drag torque of a stage is scaled with its rated output torque relative to the axle (T_cap/T_ref)."""
    T = np.asarray(T_wheel, dtype=float)
    n = np.asarray(n_wheel_rpm, dtype=float)
    n_wheel = np.abs(n)   # VECTO's drag speed law (n/150 rpm) is for axle output speeds: every stage is evaluated at
                          # wheel-equivalent speed, i.e. drag power = that of an axle with the same torque-speed product
    P_total = np.zeros(np.broadcast(T, n).shape)
    T_cap = GEAR["T_ref_axle_out_Nm"]
    parts = {}
    idle = [s for s in stages if s.get("idle")]
    for s in [s for s in stages if not s.get("idle")]:
        scale = drag_scale * T_cap / GEAR["T_ref_axle_out_Nm"]
        Tl = _stage_loss_out(T, n_wheel, s["i"], s["eta"], scale)
        P = Tl * n * RPM
        parts[s["name"]] = P
        P_total = P_total + P
        T = (T + Tl) / s["i"]           # same expression in traction and regen (loss always taken from the motor side)
        n = n * s["i"]
        T_cap = T_cap / s["i"]
        if s["name"].startswith("helical_1"):
            # idle pair of a 2-speed: its output gear turns with the stage output (wheel side of this stage)
            for sid in idle:
                n_out = n / s["i"]
                scale_i = drag_scale * (T_cap * s["i"]) / GEAR["T_ref_axle_out_Nm"]
                Td0 = (VECTO_GEN["T0_Nm"] + VECTO_GEN["T1_Nm"] * sid["i"]) * scale_i * GEAR["two_speed_idle_pair_drag_factor"]
                Tl_i = Td0 / 2 + Td0 / 2 * n_wheel / VECTO_GEN["Td_n_rpm"]
                P_i = Tl_i * n_out * RPM
                parts[sid["name"]] = P_i
                P_total = P_total + P_i
                T = T + Tl_i / s["i"]
    return dict(T_motor_Nm=T, n_motor_rpm=n, P_gear_loss_W=P_total, parts_W=parts)


# ----------------------------------------------------------------------------------
# 2. Motor friction and windage (physics, same model for every machine)
# ----------------------------------------------------------------------------------
MECH = dict(
    rho_air_kg_m3=1.06, mu_air_Pa_s=2.0e-5,       # air at ~60 C in the air gap
    gap_m=1.0e-3, k_rough=1.0,                     # smooth (closed slots / IPM / salient poles: k up to 1.4 - sensitivity)
    r_shaft_m=0.04,
    bearing_mu=0.0015,                             # SKF constant friction coefficient, deep-groove ball bearing
    bearing_bore_m=0.07, bearing_dm_m=0.10, n_bearings=2,
    bearing_f0=2.0, oil_visc_mm2_s=10.0,           # SKF M0 (no-load viscous) for oil-spray lubrication
    r_pinion_m=0.035, pressure_angle_deg=20.0,     # motor-side pinion; mesh force loads the motor bearings
    seal_d_mm=70.0, n_seals=1,                     # SKF radial shaft seal estimate P = 7.69e-6 d^2 n
    rho_rotor_kg_m3=7650.0, rotor_fill=0.85,
    sources=["Saari 1998 (TKK thesis) / Bilgen & Boulos 1973 J. Fluids Eng. - gap Couette friction coefficient",
             "Free rotating disc moment coefficient (laminar 3.87 Re^-0.5, turbulent 0.146 Re^-0.2), as quoted in Saari 1998",
             "SKF rolling bearing catalogue - friction model M = 0.5 mu F d and M0 = 1e-7 f0 (nu n)^(2/3) dm^3",
             "SKF industrial shaft seals - seal friction power estimate P = 7.69e-6 d^2 n",
             "NOT YET VERIFIED BY lit-scout: bib keys pending; calibration against a measured traction-motor mechanical loss pending"])


def rotor_from_design(R_gap_m, L_stk_m=T3.ST["L_stk_m"]):
    R = R_gap_m - MECH["gap_m"]
    m = MECH["rho_rotor_kg_m3"] * math.pi * R ** 2 * L_stk_m * MECH["rotor_fill"]
    return dict(R_m=R, L_m=L_stk_m, mass_kg=m)


def mech_losses(n_rpm, T_motor, rotor):
    n = np.abs(np.asarray(n_rpm, dtype=float))
    w = n * RPM
    rho, mu, d = MECH["rho_air_kg_m3"], MECH["mu_air_Pa_s"], MECH["gap_m"]
    R, L = rotor["R_m"], rotor["L_m"]
    # gap windage (Couette, Bilgen & Boulos as quoted by Saari)
    Re = np.maximum(rho * w * R * d / mu, 1e-9)
    # C_f = 0.515 / 0.0325 (Saari 1998 / Bilgen1973functional, P = k C_f pi rho w^3 r^4 l). Bug fix 2026-10-29:
    # the first T03d run used 1.03 / 0.065 (2x), i.e. gap windage was overstated by 2x.
    Cm = np.where(Re < 1e4, 0.515 * (d / R) ** 0.3 * Re ** -0.5, 0.0325 * (d / R) ** 0.3 * Re ** -0.2)
    P_gap = MECH["k_rough"] * Cm * math.pi * rho * w ** 3 * R ** 4 * L
    # rotor end faces (two free discs)
    Rer = np.maximum(rho * w * R ** 2 / mu, 1e-9)
    Cd = np.where(Rer < 3e5, 3.87 * Rer ** -0.5, 0.146 * Rer ** -0.2)
    P_ends = 2 * 0.5 * Cd * rho * w ** 3 * (R ** 5 - MECH["r_shaft_m"] ** 5)
    # bearings: load = rotor weight + gear mesh force (radial + tangential, from the motor torque)
    F_mesh = np.abs(np.asarray(T_motor, dtype=float)) / (MECH["r_pinion_m"] * math.cos(math.radians(MECH["pressure_angle_deg"])))
    F = rotor["mass_kg"] * 9.81 + F_mesh
    M_load = 0.5 * MECH["bearing_mu"] * F * MECH["bearing_bore_m"]                       # total over bearings (load split)
    M0 = MECH["n_bearings"] * 1e-7 * MECH["bearing_f0"] * (MECH["oil_visc_mm2_s"] * n) ** (2 / 3) * (MECH["bearing_dm_m"] * 1e3) ** 3 / 1e3
    P_bear = (M_load + M0) * w
    P_seal = MECH["n_seals"] * 7.69e-6 * MECH["seal_d_mm"] ** 2 * n
    tot = P_gap + P_ends + P_bear + P_seal
    return dict(P_windage_gap_W=P_gap, P_windage_ends_W=P_ends, P_bearings_W=P_bear, P_seal_W=P_seal, P_total_W=tot)


# ----------------------------------------------------------------------------------
# 3. Motor electromagnetic losses at an operating point (same models as T03 / T03b)
# ----------------------------------------------------------------------------------
def im_em_loss(designs, T_N, n, T):
    """Best mode, realistic IM model (T03b) minus its old friction/windage law."""
    best = None
    for mode, d in designs.items():
        r = FB.realistic_point(d, n, T, T_N[mode], n_psi=400)
        if r is None:
            continue
        fo = r["flux_optimised"]
        em = fo["P_loss_total_W"] - fo["P_mech_W"]
        if best is None or em < best["P_em_loss_W"]:
            best = dict(mode=mode, P_em_loss_W=em, PF=fo["PF"], I_rms_A=fo["I_rms_A"],
                        parts_W={k: fo[k] for k in ("P_cu_stator_W", "P_cu_rotor_W", "P_fe_W", "P_stray_IEC_W", "P_pwm_W")})
    return best


_SYNC = {}


def sync_em_loss(kind, n, T):
    """PMSM / WRSM (free I_d) from T03 at 300 kW, plus the IEC stray allowance for parity with the IM.
    PWM ripple loss is not modelled for these (IM estimate 0.1-0.45 kW)."""
    if kind not in _SYNC:
        par = T3.sync_params(kind, 4)
        env = T3.sync_envelope(par, T3.N_GRID, n_g=721 if kind == "PMSM" else 241)
        nb = T3.metrics(env)["n_base_rpm"]
        _SYNC[kind] = (par, T3.INV["P_rated_W"] / (nb * RPM))
    par, T_N = _SYNC[kind]
    r = T3.sync_min_loss(par, n, T)
    if r is None:
        return None
    stray = FB.iec_stray_allowance_W(T3.INV["P_rated_W"]) * (T / T_N) ** 2
    em = r["P_cu_stator_W"] + r["P_fe_W"] + r["P_field_W"] + stray
    return dict(mode="2p8", P_em_loss_W=em, PF=r["PF"], I_rms_A=r["I_rms_A"],
                parts_W=dict(P_cu_stator_W=r["P_cu_stator_W"], P_fe_W=r["P_fe_W"], P_field_W=r["P_field_W"], P_stray_IEC_W=stray))


# ----------------------------------------------------------------------------------
# 4. Cases and points
# ----------------------------------------------------------------------------------
POINTS = [("cruise_85kmh_flat", 85.0, 0.0), ("cruise_60kmh_flat", 60.0, 0.0),
          ("cruise_85kmh_1pct_grade", 85.0, 1.0), ("part_load_50kmh_3pct_grade", 50.0, 3.0)]


def wheel_point(v_kmh, grade):
    F, _, _ = T3.road_load(v_kmh, grade)
    r = T3.VEH["wheel_radius_m"]
    return F * r, v_kmh / 3.6 / r / RPM, F * v_kmh / 3.6


def build_cases():
    fb = json.load(open(FB_JSON))
    M = fb["machines"]
    cases = {}
    for k in ("fixed_2p4", "fixed_2p6"):
        d = M[k]["design"]
        G = M[k]["metrics"]["gear_ratio"]
        mode = f"2p{2 * d['p']}"
        base = dict(kind="IM", designs={mode: d}, T_N={mode: M[k]["realistic_losses"]["T_N_Nm"]},
                    rotor=rotor_from_design(d["R_gap_m"]))
        cases[f"{k}_G{G:.2f}_single"] = dict(base, G=G, topo=("single", None))
        cases[f"{k}_G{G:.2f}_two_stage"] = dict(base, G=G, topo=("two_stage", None))
        ts = M[k]["two_speed_gearbox"]
        cases[f"{k}_2speed_high_G{ts['G_high']:.2f}"] = dict(base, G=ts["G_high"], topo=("two_speed", ts["G_low"]),
                                                             note=f"2-speed; low gear {ts['G_low']:.2f} for the 12 % start")
    pc = M["pole_changing_2p8_4_T03"]
    TN = pc["realistic_losses"]["T_N_Nm"]
    base = dict(kind="IM", designs={"2p8": pc["design"]["2p8"], "2p4": pc["design"]["2p4"]}, T_N=TN,
                rotor=rotor_from_design(pc["design"]["2p8"]["R_gap_m"]))
    cases["pole_changing_G9.80_single"] = dict(base, G=FB.G_REF, topo=("single", None))
    Gpc = fb["summary"]["pole_changing_2p8_4_gear_optimised"]["gear_ratio"]
    cases[f"pole_changing_G{Gpc:.2f}_single"] = dict(base, G=Gpc, topo=("single", None))
    for kind in ("PMSM", "WRSM"):
        cases[f"{kind}_G9.80_single_300kW"] = dict(kind=kind, G=FB.G_REF, topo=("single", None),
                                                   rotor=rotor_from_design(T3.ST["R_gap_m"]))
    return cases


def evaluate(case, v, grade, drag_scale, eta_helical=None):
    """For a 2-speed case both gears are tried and the lower-loss feasible one is kept."""
    if case["topo"][0] == "two_speed" and case["topo"][1]:
        alt = dict(case, G=case["topo"][1], topo=("two_speed", case["G"]))
        cands = [r for r in (_evaluate(case, v, grade, drag_scale, eta_helical), _evaluate(alt, v, grade, drag_scale, eta_helical))
                 if r and r.get("feasible")]
        if not cands:
            return dict(feasible=False)
        best = max(cands, key=lambda r: r["eta_drivetrain_wheel_over_elec"])
        return best
    return _evaluate(case, v, grade, drag_scale, eta_helical)


def _evaluate(case, v, grade, drag_scale, eta_helical=None):
    Tw, nw, Pw = wheel_point(v, grade)
    st = gear_topology(case["G"], case["topo"][0], case["topo"][1], eta_helical)
    if st is None:
        return None
    g = gear_motor_point(Tw, nw, st, drag_scale)
    n, T = float(g["n_motor_rpm"]), float(g["T_motor_Nm"])
    em = im_em_loss(case["designs"], case["T_N"], n, T) if case["kind"] == "IM" else sync_em_loss(case["kind"], n, T)
    if em is None:
        return dict(feasible=False, n_motor_rpm=n, T_motor_Nm=T)
    mech = {k: float(v_) for k, v_ in mech_losses(n, T, case["rotor"]).items()}
    Pg = float(g["P_gear_loss_W"])
    P_shaft = T * n * RPM
    P_in = P_shaft + mech["P_total_W"] + em["P_em_loss_W"]
    return dict(feasible=True, gear_ratio_engaged=case["G"], n_motor_rpm=n, T_motor_Nm=T, wheel_power_W=Pw, mode=em["mode"], PF=em["PF"],
                I_rms_A=em["I_rms_A"], P_em_loss_W=em["P_em_loss_W"], em_parts_W=em["parts_W"],
                P_mech_W=mech["P_total_W"], mech_parts_W=mech, P_gear_W=Pg,
                gear_parts_W={k: float(v_) for k, v_ in g["parts_W"].items()}, stages=st,
                eta_motor_em_only=(P_shaft + mech["P_total_W"]) / P_in,
                eta_motor_incl_fw=P_shaft / P_in,
                eta_drivetrain_wheel_over_elec=Pw / P_in)


def main():
    cases = build_cases()
    res = dict(meta=dict(script="02_analytics/drivetrain_losses.py", task="T03d", date=_dt.date.today().isoformat(),
                         P_rated_W=T3.INV["P_rated_W"],
                         inputs=["02_analytics/results/fair_baselines.json (IM designs, T_N)",
                                 "02_analytics/torque_speed_envelope.py at 300 kW (PMSM, WRSM)",
                                 VECTO_GEN["source"]],
                         assumptions="02_analytics/assumptions.md#t03d",
                         vehicle_note="Vehicle constants still from ../Drive Cycle (T07 switches to VECTO group 5, D04).",
                         electrical_input_note="eta_drivetrain = wheel power / motor electrical input; inverter losses excluded"),
               gear_model=dict(VECTO_generic=VECTO_GEN, params=GEAR), mech_model=MECH, cases={}, ranking={})
    for cname, c in cases.items():
        out = {"G": c["G"], "topology": c["topo"][0], "two_speed_other_ratio": c["topo"][1], "note": c.get("note"),
               "rotor": c["rotor"]}
        for dv, ds in GEAR["drag_scale_variants"].items():
            out[dv] = {pn: evaluate(c, v, gr, ds) for pn, v, gr in POINTS}
        out["certified_like_eta_helical_0.99"] = {pn: evaluate(c, v, gr, 0.3, 0.99)
                                                  for pn, v, gr in POINTS}
        res["cases"][cname] = out

    # ranking at 85 km/h flat
    def rank(key, variant):
        rows = []
        for cname, c in res["cases"].items():
            r = c[variant]["cruise_85kmh_flat"]
            if r and r.get("feasible"):
                rows.append((cname, r[key]))
        rows.sort(key=lambda x: -x[1])
        return [dict(case=a, value=b) for a, b in rows]
    res["ranking"]["cruise_85kmh_flat"] = dict(
        motor_em_only=rank("eta_motor_em_only", "VECTO_generic"),
        motor_incl_new_friction_windage=rank("eta_motor_incl_fw", "VECTO_generic"),
        drivetrain_VECTO_generic_gear=rank("eta_drivetrain_wheel_over_elec", "VECTO_generic"),
        drivetrain_certified_like_gear=rank("eta_drivetrain_wheel_over_elec", "certified_like"),
        drivetrain_certified_like_helical_0p99=rank("eta_drivetrain_wheel_over_elec", "certified_like_eta_helical_0.99"),
        drivetrain_EU2017_regulatory=rank("eta_drivetrain_wheel_over_elec", "EU2017"))
    res["gear_model"]["EU2017"] = EU2017

    # sanity / plausibility checks
    Tw, nw, Pw = wheel_point(85.0, 0.0)
    ax = gear_motor_point(Tw, nw, [dict(name="axle_hypoid", i=3.0, eta=0.98)], 1.0)
    rot = rotor_from_design(0.165)
    vb = {}
    for n_rel, p0 in ((1.0, 0.0055), (2.2, 0.0195), (3.8, 0.0575)):   # VECTO generic ASM no-load P0 (interpolated T=0), x P_rated
        n_abs = n_rel * 1151.0
        vb[f"n_{n_rel}xbase"] = dict(speed_rpm=n_abs, model_fw_W=float(mech_losses(n_abs, 0.0, rot)["P_total_W"]),
                                     VECTO_generic_ASM_noload_total_W=p0 * T3.INV["P_rated_W"])
    res["sanity_checks"] = dict(
        VECTO_generic_axle_i3_at_85kmh=dict(wheel_torque_Nm=float(Tw), loss_W=float(ax["P_gear_loss_W"]),
                                            efficiency=float(Pw / (Pw + ax["P_gear_loss_W"])),
                                            note="generic (deliberately conservative) value; certified axles are better -> 'certified_like' variant"),
        fw_vs_VECTO_generic_ASM_noload_upper_bound=dict(points=vb, note="VECTO GenericBusData EfficiencyMap_ASM_normalized: Pel at T=+0.01 minus 0.01 n, "
                                                        "i.e. iron + mechanical no-load loss; friction/windage must stay below it"),
        old_T03_fw_law_W={str(n): float(T3.p_mech(n)) for n in (4500.0, 7500.0)},
        new_fw_R165_W={str(n): float(mech_losses(n, 350.0, rot)["P_total_W"]) for n in (4500.0, 7500.0)})
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(res, f, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.ndarray)) else str(o))
    print(json.dumps(res["sanity_checks"], indent=1, default=float))
    for k, v in res["ranking"]["cruise_85kmh_flat"].items():
        print(k)
        for r in v:
            print(f"   {r['value'] * 100:6.2f}  {r['case']}")
    for cname, c in res["cases"].items():
        r = c["VECTO_generic"]["cruise_85kmh_flat"]
        rc = c["certified_like"]["cruise_85kmh_flat"]
        if r and r.get("feasible"):
            print(f"{cname:38s} n={r['n_motor_rpm']:6.0f} T={r['T_motor_Nm']:6.0f} em={r['P_em_loss_W']:6.0f} fw={r['P_mech_W']:5.0f} "
                  f"gear(gen)={r['P_gear_W']:6.0f} gear(cert)={rc['P_gear_W']:6.0f} eta_dt gen {r['eta_drivetrain_wheel_over_elec']*100:.2f} cert {rc['eta_drivetrain_wheel_over_elec']*100:.2f}")
        else:
            print(cname, "infeasible", r)


if __name__ == "__main__":
    main()

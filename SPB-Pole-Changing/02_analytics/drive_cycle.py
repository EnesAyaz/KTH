"""T07 - Drive-cycle value screen for H02r on the agreed (R01) geometry.

Run from repo root:  python 02_analytics/drive_cycle.py
Output: 02_analytics/results/drive_cycle.json
Assumptions: 02_analytics/assumptions.md, section T07.

Pipeline
--------
1. VECTO distance-based cycles (data/vecto/LongHaul.vdri, RegionalDelivery.vdri) -> shared driver model (look-ahead
   braking, speed-dependent acceleration limit, stops) -> time traces. Every powertrain drives the same driver model
   inside its own wheel-force envelope; where it cannot follow, its trace slows down (time lost reported).
2. Wheel-side loss maps per powertrain and configuration (pole mode / gear): gear (EU2017 or certified-like) ->
   motor point -> machine losses (T03b realistic IM model or T03 PMSM + IEC stray) + friction/windage (T03d) +
   inverter (Enes's EPC2361 model, N = 16 SPB). Stray-load loss is stored separately (1x / 2x sensitivity).
3. Integrate battery energy (no auxiliaries), loss breakdown, pole changes / gear shifts with hysteresis, and the
   torque gaps (pole change 0.17 s per H11s; AMT shift 0.5 s, assumed).
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
os.environ.setdefault("SPB_P_RATED_KW", "300")
os.environ.setdefault("SPB_GEOMETRY", os.path.join("data", "machine_geometry.json"))
os.chdir(ROOT)
import torque_speed_envelope as T3   # noqa: E402
import fair_baselines as FB          # noqa: E402
import drivetrain_losses as DL       # noqa: E402
import module_count_sweep as MS      # noqa: E402

OUT = os.path.join(ROOT, "02_analytics", "results", "drive_cycle.json")
VECTO = os.path.join(ROOT, "data", "vecto")
RPM = T3.RPM
G_ACC = 9.81

# ----------------------------------------------------------------------------------
# Vehicle (VECTO group 5: 4x2 tractor + ST1 semitrailer)
# ----------------------------------------------------------------------------------
VEH = dict(tractor_curb_kg=8500.0, trailer_ST1_kg=7500.0, CdxA_m2=8.7, rho_air=1.188, Crr=0.0060, r_wheel_m=0.52,
           wheel_axle_inertia_factor=0.03,
           sources=dict(CdxA="SegmentTable.csv group 5 CdxA_Default 8.7 m2 (VECTO default when no certified air drag)",
                        trailer="Body_Trailers_Weights.csv ST1 curb 7500 kg",
                        payloads="SegmentTable.csv group 5: Long haul 2600/19300 kg, Regional delivery 2600/12900 kg (low/representative)",
                        assumed="tractor curb 8.5 t (BEV, assumed), Crr 0.006 (assumed, tyre-label class B/C), r 0.52 m (385/65 R22.5, "
                                "as in T03), wheels/axles inertia +3 %"))
LOADS = {"LongHaul_ref": ("LongHaul.vdri", 19300.0), "LongHaul_40t": ("LongHaul.vdri", 40000.0 - 8500.0 - 7500.0),
         "RegionalDelivery_ref": ("RegionalDelivery.vdri", 12900.0)}
DRIVER = dict(a_max_low=1.0, a_max_high=0.5, v_knee_ms=20.0, decel_ms2=0.8, dt_s=0.5, v_creep_ms=0.5,
              note="a_max falls linearly from 1.0 m/s2 (0 m/s) to 0.5 m/s2 at 20 m/s; look-ahead braking at 0.8 m/s2; "
                   "no coasting (VECTO's look-ahead coasting not modelled) - assumptions")
GAPS = dict(pole_change_s=0.17, amt_shift_s=0.5, hold_s=3.0, switch_margin=0.02,
            note="pole change 0.17 s (H11s R01); AMT shift 0.5 s assumed (lit-scout to source); mode/gear switches only if the other "
                 "one is >2 % (and >0.3 kW) better for >= 3 s, or if the current one cannot deliver the force")


def load_cycle(fname):
    rows = []
    with open(os.path.join(VECTO, fname)) as f:
        next(f)
        for line in f:
            p = line.strip().split(",")
            if len(p) < 4:
                continue
            rows.append([float(p[0]), float(p[1]), float(p[2]), float(p[3])])
    a = np.array(rows)
    return dict(s=a[:, 0], v_kmh=a[:, 1], grad_pct=a[:, 2], stop_s=a[:, 3])


# ----------------------------------------------------------------------------------
# Powertrains
# ----------------------------------------------------------------------------------
NW_GRID = np.linspace(0.0, 100.0 / 3.6 / VEH["r_wheel_m"] / RPM, 34)      # wheel rpm up to 100 km/h
X_GRID = np.linspace(-1.0, 1.0, 41)                                       # torque as a fraction of the envelope


class Config:
    """One operating configuration (pole mode or gear) of a powertrain: wheel-side envelope and loss map."""

    def __init__(self, name, G, topo, em_fn, env_motor, n_motor_max, inv, rotor, J_rotor, two_speed_other=None):
        self.name, self.G, self.topo, self.em_fn, self.inv = name, G, topo, em_fn, inv
        self.rotor, self.J = rotor, J_rotor
        self.n_motor_max = n_motor_max
        self.env_n, self.env_T = env_motor            # motor envelope (rpm, Nm)
        self.other = two_speed_other
        self.stages = {gv: DL.gear_topology(G, topo, two_speed_other) for gv in ("EU2017", "certified_like")}

    def wheel_envelope(self, nw, gv):
        """Max wheel torque at wheel speed nw (traction), through the gear model."""
        n_m = nw * self.G
        if n_m > self.n_motor_max:
            return 0.0
        Tm = float(np.interp(n_m, self.env_n, self.env_T))
        st = self.stages[gv]
        ds = DL.GEAR["drag_scale_variants"][gv]
        lo, hi = 0.0, Tm * self.G
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            if float(DL.gear_motor_point(mid, max(nw, 1e-3), st, ds)["T_motor_Nm"]) > Tm:
                hi = mid
            else:
                lo = mid
        return lo

    def build_map(self, gv):
        """Losses on (wheel rpm, x = T_wheel / T_env) for gear variant gv."""
        ds = DL.GEAR["drag_scale_variants"][gv]
        st = self.stages[gv]
        nN, nX = len(NW_GRID), len(X_GRID)
        keys = ("P_gear", "P_em_ex_stray", "P_stray", "P_fw", "P_inv")
        M = {k: np.full((nN, nX), np.nan) for k in keys}
        Tenv = np.array([self.wheel_envelope(nw, gv) for nw in NW_GRID])
        for i, nw in enumerate(NW_GRID):
            for j, x in enumerate(X_GRID):
                Tw = 0.995 * x * Tenv[i]
                nwe = max(nw, 0.5)                                   # creep: evaluate at 0.5 wheel rpm
                g = DL.gear_motor_point(Tw, nwe, st, ds)
                Tm, nm = float(g["T_motor_Nm"]), float(g["n_motor_rpm"])
                em = self.em_fn(nm, abs(Tm) if abs(Tm) > 1.0 else 1.0)
                if em is None:
                    continue
                M["P_gear"][i, j] = float(g["P_gear_loss_W"])
                M["P_em_ex_stray"][i, j] = em["P_em"] - em["P_stray"]
                M["P_stray"][i, j] = em["P_stray"]
                M["P_fw"][i, j] = float(DL.mech_losses(nm, Tm, self.rotor)["P_total_W"])
                P_inv = MS.inverter_loss(self.inv, em["I_rms"])[0] if self.inv else 0.0
                M["P_inv"][i, j] = P_inv if P_inv is not None else np.nan
            # fill rare NaNs along x by nearest valid
            for k in keys:
                row = M[k][i]
                ok = np.isfinite(row)
                if ok.any() and not ok.all():
                    M[k][i] = np.interp(X_GRID, X_GRID[ok], row[ok])
        return dict(Tenv=Tenv, maps=M)


def im_em_fn(design, T_N, I_scale=1.0):
    def fn(n, T):
        I0 = FB.IMAX0
        FB.IMAX0 = I0 * I_scale
        try:
            r = FB.realistic_point(design, n, T, T_N, n_psi=160)
        finally:
            FB.IMAX0 = I0
        if r is None:
            return None
        fo = r["flux_optimised"]
        return dict(P_em=fo["P_loss_total_W"] - fo["P_mech_W"], P_stray=fo["P_stray_IEC_W"], I_rms=fo["I_rms_A"])
    return fn


_PM = {}


def pmsm_em_fn():
    par = T3.sync_params("PMSM", 4)
    if "T_N" not in _PM:
        env = T3.sync_envelope(par, T3.N_GRID, n_g=721)
        _PM["env"] = env
        _PM["T_N"] = T3.INV["P_rated_W"] / (T3.metrics(env)["n_base_rpm"] * RPM)

    def fn(n, T):
        r = T3.sync_min_loss(par, n, T, n_g=361)
        if r is None:
            return None
        stray = FB.iec_stray_allowance_W(T3.INV["P_rated_W"]) * (T / _PM["T_N"]) ** 2
        return dict(P_em=r["P_cu_stator_W"] + r["P_fe_W"] + stray, P_stray=stray, I_rms=r["I_rms_A"])
    return fn, par


def build_powertrains():
    fb = json.load(open(FB.OUT_JSON))
    M = fb["machines"]
    inv16 = MS.inverter_design(16, 3)
    NG = FB.NG_FULL
    pts = {}

    def rotor_of(d):
        r = DL.rotor_from_design(d["R_gap_m"])
        J = 0.5 * r["mass_kg"] * r["R_m"] ** 2
        return r, J
    # (a) pole-changing IM, G = 11.35 (R01 gear-optimised)
    pc = M["pole_changing_2p8_4_T03"]
    Gpc = fb["summary"]["pole_changing_2p8_4_gear_optimised"]["gear_ratio"]
    rot, J = rotor_of(pc["design"]["2p8"])
    TN = pc["realistic_losses"]["T_N_Nm"]
    cfgs = []
    for mode in ("2p8", "2p4"):
        d = pc["design"][mode]
        env = FB.envelope(d, NG)
        cfgs.append(Config(f"PC_{mode}", Gpc, "single", im_em_fn(d, TN[mode]), (NG, env), d["n_tip_limit_rpm"], inv16, rot, J))
    pts["a_pole_changing_IM_G%.2f" % Gpc] = dict(configs=cfgs, kind="pole_change", note="R01 pole-changing IM, single stage")
    # (b) fixed IMs, own single stage
    for key in ("fixed_2p4", "fixed_2p6"):
        d = M[key]["design"]
        G = M[key]["metrics"]["gear_ratio"]
        rot, J = rotor_of(d)
        env = FB.envelope(d, NG)
        pts[f"b_{key}_G{G:.2f}"] = dict(configs=[Config(key, G, "single", im_em_fn(d, M[key]["realistic_losses"]["T_N_Nm"]), (NG, env),
                                                         d["n_tip_limit_rpm"], inv16, rot, J)], kind="fixed")
    # (c) fixed 2p=4, 2-speed
    d = M["fixed_2p4"]["design"]
    ts = M["fixed_2p4"]["two_speed_gearbox"]
    rot, J = rotor_of(d)
    env = FB.envelope(d, NG)
    TNf = M["fixed_2p4"]["realistic_losses"]["T_N_Nm"]
    pts["c_fixed_2p4_2speed_%.2f_%.2f" % (ts["G_low"], ts["G_high"])] = dict(configs=[
        Config("low", ts["G_low"], "two_speed", im_em_fn(d, TNf), (NG, env), d["n_tip_limit_rpm"], inv16, rot, J, two_speed_other=ts["G_high"]),
        Config("high", ts["G_high"], "two_speed", im_em_fn(d, TNf), (NG, env), d["n_tip_limit_rpm"], inv16, rot, J, two_speed_other=ts["G_low"])],
        kind="two_speed")
    # (d) fixed 2p=4 at G = 9.80 with the scaled inverter
    k = M["fixed_2p4"]["at_G_9p80"]["current_factor_needed_for_start"]
    inv_d = dict(inv16)
    inv_d["I_leg_rms_max_A"] *= k
    inv_d["devices_parallel"] = MS.n_parallel(inv_d["device"], inv_d["I_leg_rms_max_A"])[0]
    inv_d["devices_total"] = 2 * inv_d["legs"] * inv_d["devices_parallel"]
    env_d = FB.envelope(d, NG, I_max=FB.IMAX0 * k)
    pts["d_fixed_2p4_G9.80_inverter_x%.2f" % k] = dict(configs=[Config("fixed_2p4_bigInv", FB.G_REF, "single", im_em_fn(d, TNf, k), (NG, env_d),
                                                                       d["n_tip_limit_rpm"], inv_d, rot, J)], kind="fixed",
                                                        inverter_devices=inv_d["devices_total"])
    # (e) PMSM (typical per-unit reference, NOT R01-sized), single stage and 2-speed
    fn, par = pmsm_em_fn()
    rotp = DL.rotor_from_design(T3.ST["R_gap_m"])
    Jp = 0.5 * rotp["mass_kg"] * rotp["R_m"] ** 2
    envp = _PM["env"]
    n_max_p = FB.TIP_SPEED_MAX / T3.ST["R_gap_m"] / RPM
    pts["e_PMSM_ref_G10.50"] = dict(configs=[Config("PMSM", 10.5, "single", fn, (T3.N_GRID, envp), n_max_p, inv16, rotp, Jp)], kind="fixed",
                                    note="typical-parameter IPM reference (T03 per-unit), not sized on the R01 stator")
    pts["e_PMSM_ref_2speed_14.0_8.0"] = dict(configs=[
        Config("low", 14.0, "two_speed", fn, (T3.N_GRID, envp), n_max_p, inv16, rotp, Jp, two_speed_other=8.0),
        Config("high", 8.0, "two_speed", fn, (T3.N_GRID, envp), n_max_p, inv16, rotp, Jp, two_speed_other=14.0)], kind="two_speed",
        note="industry-style reference: PMSM + 2-speed AMT")
    return pts, inv16


# ----------------------------------------------------------------------------------
# Driver model and energy integration
# ----------------------------------------------------------------------------------
def road_force(v, grad_pct, m):
    a = math.atan(grad_pct / 100.0)
    return VEH["Crr"] * m * G_ACC * math.cos(a) + 0.5 * VEH["rho_air"] * VEH["CdxA_m2"] * v * v + m * G_ACC * math.sin(a)


def v_limit_profile(cyc):
    s, vt = cyc["s"], cyc["v_kmh"] / 3.6
    vt = vt.copy()
    vt[cyc["stop_s"] > 0] = 0.0
    vl = vt.copy()
    for i in range(len(s) - 2, -1, -1):
        vl[i] = min(vt[i], math.sqrt(vl[i + 1] ** 2 + 2 * DRIVER["decel_ms2"] * (s[i + 1] - s[i])))
    return vl


class Interp:
    def __init__(self, cfg, mp):
        self.cfg, self.mp = cfg, mp

    def wheel_Tmax(self, nw):
        return float(np.interp(nw, NW_GRID, self.mp["Tenv"]))

    def losses(self, nw, Tw):
        Te = self.wheel_Tmax(nw)
        if Te <= 0:
            return None
        x = Tw / Te
        if abs(x) > 1.0 + 1e-6:
            return None
        x = max(-1.0, min(1.0, x))
        out = {}
        i = np.searchsorted(NW_GRID, nw) - 1
        i = max(0, min(i, len(NW_GRID) - 2))
        j = np.searchsorted(X_GRID, x) - 1
        j = max(0, min(j, len(X_GRID) - 2))
        u = (nw - NW_GRID[i]) / (NW_GRID[i + 1] - NW_GRID[i])
        w = (x - X_GRID[j]) / (X_GRID[j + 1] - X_GRID[j])
        u, w = min(max(u, 0), 1), min(max(w, 0), 1)
        for k, A in self.mp["maps"].items():
            q = (1 - u) * (1 - w) * A[i, j] + u * (1 - w) * A[i + 1, j] + (1 - u) * w * A[i, j + 1] + u * w * A[i + 1, j + 1]
            out[k] = float(q)
        return out


def drive(cyc, vl, m, pt_maps, kind, J_eq_of, stray_k=1.0, gap_s=0.0, ideal=False):
    """Time-stepped driver. pt_maps: list of Interp (configs). Returns totals and counters."""
    dt = DRIVER["dt_s"]
    s_end = cyc["s"][-1]
    stops = {int(round(x)): t for x, t in zip(cyc["s"], cyc["stop_s"]) if t > 0}
    stop_pos = sorted(stops)
    s, v, t = 0.0, 0.0, 0.0
    cur = 0
    better_t = 0.0
    gap_left = 0.0
    E = dict(batt=0.0, wheel_pos=0.0, wheel_regen=0.0, friction_brake=0.0, P_gear=0.0, P_em_ex_stray=0.0, P_stray=0.0, P_fw=0.0, P_inv=0.0)
    n_switch = 0
    t_gap_total = 0.0
    next_stop_i = 0
    unfollowed_s = 0.0
    r = VEH["r_wheel_m"]
    while s < s_end - 1.0:
        idx = min(int(s), len(vl) - 1)
        # stop handling
        if next_stop_i < len(stop_pos) and s >= stop_pos[next_stop_i] - 0.5 and v < 0.6:
            t += stops[stop_pos[next_stop_i]]
            next_stop_i += 1
            v = 0.0
            s = max(s, stop_pos[next_stop_i - 1] + 0.01)
            continue
        v_target = vl[min(idx + 1, len(vl) - 1)]
        if next_stop_i < len(stop_pos):
            d_stop = stop_pos[next_stop_i] - s
            if d_stop > 0:
                v_target = min(v_target, math.sqrt(max(2 * DRIVER["decel_ms2"] * d_stop, 0)))
        grad = cyc["grad_pct"][idx]
        a_max = DRIVER["a_max_low"] - (DRIVER["a_max_low"] - DRIVER["a_max_high"]) * min(v / DRIVER["v_knee_ms"], 1.0)
        if v < v_target:
            a_des = min(a_max, (v_target - v) / dt)
        else:
            a_des = max(-DRIVER["decel_ms2"] * 1.5, (v_target - v) / dt)
        if v_target < 0.05 and v < DRIVER["v_creep_ms"] and (next_stop_i < len(stop_pos) and stop_pos[next_stop_i] - s > 0.5):
            a_des = max(a_des, 0.3)                       # creep to the stop line
        nw = max(v, 0.0) / r / RPM
        F_road = road_force(v, grad, m)
        # configuration choice and envelope
        if ideal:
            Fmax = min(60e3, 300e3 / max(v, 0.5))
            J_eq = 0.0
            m_eff = m * (1 + VEH["wheel_axle_inertia_factor"])
            F_req = m_eff * a_des + F_road
            F = min(F_req, Fmax)
            pw = None
        else:
            J_eq = J_eq_of(cur)
            m_eff = m * (1 + VEH["wheel_axle_inertia_factor"]) + J_eq / r ** 2
            F_req = m_eff * a_des + F_road
            Tw_req = F_req * r
            feas = [k for k, ip in enumerate(pt_maps) if ip.wheel_Tmax(nw) * 0.99 >= Tw_req or Tw_req <= 0]
            if len(pt_maps) > 1:
                def batt_cost(k):
                    ip = pt_maps[k]
                    Te = ip.wheel_Tmax(nw)
                    Tw = max(min(Tw_req, Te), -Te)
                    L = ip.losses(nw, Tw)
                    return np.inf if L is None else (L["P_gear"] + L["P_em_ex_stray"] + stray_k * L["P_stray"] + L["P_fw"] + L["P_inv"])
                costs = [batt_cost(k) for k in range(len(pt_maps))]
                if cur not in feas and feas:
                    new = min(feas, key=lambda k: costs[k])
                elif feas:
                    best = min(feas, key=lambda k: costs[k])
                    if best != cur and costs[best] < costs[cur] * (1 - GAPS["switch_margin"]) - 300:
                        better_t += dt
                    else:
                        better_t = 0.0
                    new = best if better_t >= GAPS["hold_s"] else cur
                else:
                    new = max(range(len(pt_maps)), key=lambda k: pt_maps[k].wheel_Tmax(nw))
                if new != cur:
                    n_switch += 1
                    gap_left = gap_s
                    t_gap_total += gap_s
                    cur = new
                    better_t = 0.0
            ip = pt_maps[cur]
            Te = ip.wheel_Tmax(nw)
            Fmax = Te / r
            if gap_left > 0:
                Fmax = 0.0
                gap_left -= dt
            F = min(F_req, Fmax)
            if F_req > Fmax + 1e-6:
                unfollowed_s += dt
            pw = ip
        a = (F - F_road) / m_eff
        v_new = max(0.0, v + a * dt)
        ds = 0.5 * (v + v_new) * dt
        # energy
        Pw = F * 0.5 * (v + v_new)
        if ideal:
            E["wheel_pos"] += max(Pw, 0) * dt
        else:
            Tw = F * r
            if Tw < 0:
                Tmin = -pw.wheel_Tmax(nw)
                Tw_el = max(Tw, Tmin)
                if Tw_el * (0.5 * (v + v_new)) < -300e3:
                    Tw_el = -300e3 / max(0.5 * (v + v_new), 0.1) * 1.0
                    Tw_el = max(Tw_el, Tmin)
                E["friction_brake"] += (Tw_el - Tw) / r * 0.5 * (v + v_new) * dt
                Tw = Tw_el
            Pw_el = Tw / r * 0.5 * (v + v_new)
            if v_new + v > 0.02:                       # motor spinning: no-load losses count even at zero torque
                L = pw.losses(nw, Tw)
                if L is None:
                    L = pw.losses(nw, math.copysign(pw.wheel_Tmax(nw), Tw))
                Ltot = 0.0
                for k_ in ("P_gear", "P_em_ex_stray", "P_fw", "P_inv"):
                    E[k_] += L[k_] * dt
                    Ltot += L[k_]
                E["P_stray"] += stray_k * L["P_stray"] * dt
                Ltot += stray_k * L["P_stray"]
            else:
                Ltot = 0.0
            E["batt"] += (Pw_el + Ltot) * dt
            if Pw_el > 0:
                E["wheel_pos"] += Pw_el * dt
            else:
                E["wheel_regen"] += -Pw_el * dt
        v, s, t = v_new, s + ds, t + dt
        if t > 5e5:
            break
    km = s_end / 1000.0
    out = dict(time_s=t, distance_km=km, avg_speed_kmh=km / (t / 3600.0), switches=n_switch, switches_per_100km=n_switch / km * 100,
               torque_gap_total_s=t_gap_total, time_not_following_s=unfollowed_s)
    if not ideal:
        f = 1 / 3.6e6 / km * 100       # J -> kWh/100 km
        out.update(E_batt_kWh_100km=E["batt"] * f, E_wheel_traction_kWh_100km=E["wheel_pos"] * f,
                   E_wheel_regen_kWh_100km=E["wheel_regen"] * f, E_friction_brake_kWh_100km=E["friction_brake"] * f,
                   loss_gear_kWh_100km=E["P_gear"] * f, loss_machine_kWh_100km=(E["P_em_ex_stray"] + E["P_stray"] + E["P_fw"]) * f,
                   loss_machine_stray_kWh_100km=E["P_stray"] * f, loss_fw_kWh_100km=E["P_fw"] * f, loss_inverter_kWh_100km=E["P_inv"] * f)
    else:
        out.update(E_wheel_traction_kWh_100km=E["wheel_pos"] / 3.6e6 / km * 100)
    return out


# ----------------------------------------------------------------------------------
def main():
    import time as _time
    t0 = _time.time()
    pts, inv16 = build_powertrains()
    maps = {}
    for pname, pt in pts.items():
        for cfg in pt["configs"]:
            for gv in ("EU2017", "certified_like"):
                maps[(pname, cfg.name, gv)] = Interp(cfg, cfg.build_map(gv))
        print(f"maps {pname}: {_time.time() - t0:.0f} s", flush=True)
    res = dict(meta=dict(script="02_analytics/drive_cycle.py", task="T07 (H02r value screen)", date=_dt.date.today().isoformat(),
                         geometry=T3.GEOMETRY_PATH, P_rated_W=T3.INV["P_rated_W"], inverter=dict(N=16, m=3, device=inv16["device"],
                                                                                                  devices=inv16["devices_total"]),
                         vehicle=VEH, driver=DRIVER, gaps=GAPS, loads={k: dict(cycle=v[0], payload_kg=v[1],
                                                                               mass_kg=VEH["tractor_curb_kg"] + VEH["trailer_ST1_kg"] + v[1])
                                                                       for k, v in LOADS.items()},
                         assumptions="02_analytics/assumptions.md#t07",
                         not_included=["auxiliaries", "battery internal loss", "DC-link/cable loss", "thermal derating",
                                       "VECTO look-ahead coasting", "saturation intermodulation during pole change"]),
               powertrains={k: dict(kind=v["kind"], note=v.get("note"), configs=[dict(name=c.name, G=c.G, topology=c.topo,
                                                                                        rotor_J_kgm2=c.J,
                                                                                        J_reflected_kg=c.J * c.G ** 2 / VEH["r_wheel_m"] ** 2)
                                                                                   for c in v["configs"]],
                                                    inverter_devices=v.get("inverter_devices", inv16["devices_total"]))
                            for k, v in pts.items()},
               cycles={})
    for lname, (cfile, payload) in LOADS.items():
        cyc = load_cycle(cfile)
        vl = v_limit_profile(cyc)
        m = VEH["tractor_curb_kg"] + VEH["trailer_ST1_kg"] + payload
        ref = drive(cyc, vl, m, None, None, None, ideal=True)
        rc = dict(reference_ideal_300kW=ref, powertrains={})
        for pname, pt in pts.items():
            cfgs = pt["configs"]
            gap = GAPS["pole_change_s"] if pt["kind"] == "pole_change" else (GAPS["amt_shift_s"] if pt["kind"] == "two_speed" else 0.0)
            rp = {}
            for gv in ("EU2017", "certified_like"):
                for sk in (1.0, 2.0):
                    ips = [maps[(pname, c.name, gv)] for c in cfgs]
                    r = drive(cyc, vl, m, ips, pt["kind"], lambda k, cfgs=cfgs: cfgs[k].J * cfgs[k].G ** 2, stray_k=sk, gap_s=gap)
                    r["time_lost_vs_reference_s"] = r["time_s"] - ref["time_s"]
                    rp[f"{gv}_stray{sk:g}x"] = r
            rc["powertrains"][pname] = rp
            b = rp["EU2017_stray1x"]
            print(f"{lname:22s} {pname:36s} E={b['E_batt_kWh_100km']:6.2f} kWh/100km inv={b['loss_inverter_kWh_100km']:.2f} "
                  f"mach={b['loss_machine_kWh_100km']:.2f} gear={b['loss_gear_kWh_100km']:.2f} t+={b['time_lost_vs_reference_s']:.0f}s "
                  f"sw/100km={b['switches_per_100km']:.1f} | cert {rp['certified_like_stray1x']['E_batt_kWh_100km']:.2f} "
                  f"stray2x {rp['EU2017_stray2x']['E_batt_kWh_100km']:.2f}  ({_time.time() - t0:.0f} s)", flush=True)
        # ranking per variant
        rk = {}
        for var in ("EU2017_stray1x", "certified_like_stray1x", "EU2017_stray2x", "certified_like_stray2x"):
            order = sorted(rc["powertrains"], key=lambda p: rc["powertrains"][p][var]["E_batt_kWh_100km"])
            rk[var] = [dict(powertrain=p, E_kWh_100km=rc["powertrains"][p][var]["E_batt_kWh_100km"],
                            time_lost_s=rc["powertrains"][p][var]["time_lost_vs_reference_s"]) for p in order]
        rc["ranking"] = rk
        res["cycles"][lname] = rc
    json.dump(res, open(OUT, "w"), indent=1, default=MS.fmt)
    print("done", _time.time() - t0)


if __name__ == "__main__":
    main()

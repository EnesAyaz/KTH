"""Independent coil-level model of the 48-coil / 16-module SPB stator (T04).

Method (does NOT reuse the analyst's equations):
  * 48 coil-phases, coil k has sides in slots k (+) and k+7 (-), N_c = 3 turns, module j = coils j, j+16, j+32.
  * Nonlinear magnetic-equivalent circuit (MEC): 48 tooth branches (gap + tooth iron, B-H table) joined by 48 yoke
    segments (B-H table), slot ampere-turns as sources, rotor = smooth (IM) or 8 salient poles with coil-group MMFs (WRSM).
  * Coil flux linkage = N_c * sum of the flux of the 7 enclosed teeth; slot leakage from the slot field energy of the
    two stacked coil sides (double layer); differential leakage and cage impedance from winding-function harmonic sums.
Shared INPUTS (not equations) are read from the analyst JSON: V/I limits, vehicle, stator dimensions, R_coil, g_eff.
"""
import json, math, os
import numpy as np
from scipy.interpolate import PchipInterpolator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AN_JSON = os.path.join(ROOT, "02_analytics", "results", "torque_speed_envelope.json")
MU0 = 4e-7 * math.pi
RPM = 2 * math.pi / 60
SQ2 = math.sqrt(2)
J = json.load(open(AN_JSON))
INV, VEH, STJ = J["inverter"], J["vehicle"], J["stator"]
VMAX, IMAX = INV["V_ph_rms_max_V"], INV["I_module_rms_max_A"]
M = 48
Q = 48
NC = 3
Y = 7
R = STJ["R_gap_m"]; LST = STJ["L_stk_m"]; GEFF = STJ["g_eff_m"]
TAU = 2 * math.pi / Q
KST = 0.95                                  # stacking factor (analyst has none)
SLOT_W, SLOT_H, YOKE_H = STJ["slot_w_m"], STJ["slot_h_m"], STJ["yoke_h_m"]
TOOTH_W = STJ["tooth_w_m"]
RS = STJ["R_coil_ohm"]                      # shared input
KG = MU0 * R * LST / GEFF                   # gap permeance per radian
RYM = R + SLOT_H + YOKE_H / 2
LY = 2 * math.pi * RYM / Q                  # yoke segment length
AY = KST * LST * YOKE_H
AT = KST * LST * TOOTH_W
M_TEETH, M_YOKE = STJ["m_teeth_kg"], STJ["m_yoke_kg"]

# ---- B-H curve (M270-35A-like, generic) -------------------------------------------------------------------
_B = np.array([0, .2, .4, .6, .8, 1.0, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.2, 2.5])
_H = np.array([0, 45, 70, 90, 115, 160, 260, 370, 600, 1000, 1850, 3700, 7500, 16000, 35000, 100000, 100000 + 0.3 / MU0])
_pch = PchipInterpolator(_B, _H)
BG = np.linspace(0, 2.5, 5001)
HG = _pch(BG)
DHG = np.maximum(_pch.derivative()(BG), 40.0)


def H_of_B(B):
    a = np.abs(B)
    return np.sign(B) * np.interp(a, BG, HG)


def dH_of_B(B):
    return np.interp(np.abs(B), BG, DHG)


def B_of_H(H):
    return np.sign(H) * np.interp(np.abs(H), HG, BG)

# ---- iron loss: P = c f^a B^2 [W/kg], anchored at M270-35A catalogue points (2.7 W/kg@1.5T/50Hz, 17.5@1.0T/400Hz)
_a_fe = math.log((17.5 / 1.0) / (2.7 / 2.25)) / math.log(8)
_c_fe = 2.7 / (2.25 * 50 ** _a_fe)


def p_iron(f, Bt, By, build=1.5):
    f = np.abs(f)
    return build * _c_fe * f ** _a_fe * (M_TEETH * Bt ** 2 + M_YOKE * By ** 2)


def p_mech(n_rpm):
    return 500.0 * (n_rpm / 4500) + 1000.0 * (n_rpm / 4500) ** 3   # shared input (analyst friction/windage law)

# ---- slot leakage from field energy of the two stacked coil sides ---------------------------------------------
H_WEDGE = 3e-3
H_LAYER = (SLOT_H - H_WEDGE) / 2


def slot_lambdas():
    h1 = h2 = H_LAYER; hw = H_WEDGE; w = SLOT_W
    laa = (h2 / 3 + hw) / w            # top coil side
    lbb = (h1 / 3 + h2 + hw) / w       # bottom coil side
    lab = (h2 / 2 + hw) / w            # mutual
    return laa, lbb, lab


L_END = MU0 * NC ** 2 * 2 * STJ["l_end_half_m"] * 0.3     # shared input (lambda_end = 0.3, l_end from analyst geometry)


def L_slot_mode(p):
    laa, lbb, lab = slot_lambdas()
    return MU0 * LST * NC ** 2 * (laa + lbb - 2 * lab * math.cos(Y * p * TAU))


def L_sigma_mode(p):
    return L_slot_mode(p) + L_END

# ---- winding-function harmonic sums (point conductors at slot centres) -------------------------------------------
def c2_stator(nu):
    """|c_nu|^2 of one coil winding function (N_c turns, sides y slots apart)."""
    nu = np.asarray(nu, float)
    return (NC / (math.pi * nu)) ** 2 * np.sin(nu * Y * TAU / 2) ** 2


def L_mode_total(p, jmax=200):
    j = np.arange(-jmax, jmax + 1)
    nu = p + Q * j
    return 2 * math.pi * M * KG * c2_stator(nu).sum()


def L_m_fund(p):
    return 2 * math.pi * M * KG * float(c2_stator(p))


def L_diff(p):
    return L_mode_total(p) - L_m_fund(p)


def kw(p):
    return abs(math.sin(p * Y * math.pi / Q))

# ---- the MEC -------------------------------------------------------------------------------------------------
TOOTH_ANG = np.arange(Q) * TAU            # tooth i centre angle
COIL_ANG = (np.arange(Q) + 4) * TAU       # coil k axis (middle of its 7 enclosed teeth)
H_T = SLOT_H


def rotor_smooth():
    return KG * TAU * np.ones(Q), np.zeros(Q)


def rotor_salient(theta, Fpole, arc=0.7, r_int=0.08):
    """8 salient poles; pole j centred at theta + j * 45 deg, arc*45 deg wide, MMF Fpole[j]."""
    npol = len(Fpole)
    pitch = 2 * math.pi / npol
    Pt = np.zeros(Q); PF = np.zeros(Q); cov = np.zeros(Q)
    for j in range(npol):
        c = theta + j * pitch
        d = np.angle(np.exp(1j * (TOOTH_ANG - c)))
        lo = np.maximum(d - TAU / 2, -arc * pitch / 2)
        hi = np.minimum(d + TAU / 2, arc * pitch / 2)
        ov = np.maximum(0, hi - lo)
        Pt += KG * ov; PF += KG * ov * Fpole[j]; cov += ov
    Pint = KG * r_int * np.maximum(TAU - cov, 0)
    Ptot = Pt + Pint
    return Ptot, PF / Ptot


def _tooth_solve(U, P, Feff):
    X = P * (np.abs(U) + np.abs(Feff)) + 1e-15
    lo, hi = -X, X
    for _ in range(55):
        mid = 0.5 * (lo + hi)
        f = mid / P + Feff + H_T * H_of_B(mid / AT) - U
        pos = f > 0
        hi = np.where(pos, mid, hi); lo = np.where(pos, lo, mid)
    phi = 0.5 * (lo + hi)
    G = 1.0 / (1.0 / P + H_T * dH_of_B(phi / AT) / AT)
    return phi, G


SIG = 1.0


def mec_solve(icoil, rotor, U0=None, tol=1e-10):
    """Return dict(phi[48 tooth fluxes], psi[48 air-gap coil flux linkages], Bt, By)."""
    P, Feff = rotor
    S = SIG * NC * (icoil - np.roll(icoil, Y))          # slot i source (coil i top, coil i-7 bottom)
    U = np.zeros(Q) if U0 is None else U0.copy()

    def resid(U):
        phi, G = _tooth_solve(U, P, Feff)
        x = U - np.roll(U, -1) + S
        Hs = x / LY
        Bq = B_of_H(Hs)
        Phi = Bq * AY
        c = AY / (LY * dH_of_B(Bq))
        r = np.roll(Phi, 1) - Phi - phi
        return r, phi, G, c, Phi

    for it in range(60):
        r, phi, G, c, Phi = resid(U)
        nr = np.linalg.norm(r)
        if nr < tol * (1e-6 + np.linalg.norm(phi)) or nr < 1e-14:
            break
        Jm = np.zeros((Q, Q))
        idx = np.arange(Q)
        Jm[idx, idx] = -(np.roll(c, 1) + c + G)
        Jm[idx, (idx - 1) % Q] += np.roll(c, 1)
        Jm[idx, (idx + 1) % Q] += c
        dU = np.linalg.solve(Jm - 1e-12 * np.eye(Q), -r)
        t = 1.0
        while t > 1e-3:
            rn = resid(U + t * dU)[0]
            if np.linalg.norm(rn) < nr * (1 - 1e-4 * t):
                break
            t *= 0.5
        U = U + t * dU
    r, phi, G, c, Phi = resid(U)
    cs = np.cumsum(np.concatenate([phi, phi]))
    psi = np.array([NC * (cs[k + Y] - cs[k]) for k in range(Q)])
    return dict(phi=phi, psi=psi, U=U, Bt=np.abs(phi) / AT, By=np.abs(Phi) / AY)


def dq_currents(p, theta_d, i_d, i_q):
    x = p * (COIL_ANG - theta_d)
    return i_d * np.cos(x) + i_q * np.sin(x)


def dq_flux(p, theta_d, psi):
    x = p * (COIL_ANG - theta_d)
    return 2 / M * np.sum(psi * np.cos(x)), 2 / M * np.sum(psi * np.sin(x))


def _fix_sign():
    global SIG
    i = np.zeros(Q); i[10] = 1.0
    for s in (1.0, -1.0):
        SIG = s
        r = mec_solve(i * 1e-2, rotor_smooth())
        if r["psi"][10] > 0:
            return
    raise RuntimeError("sign")


_fix_sign()

# ---- magnetising curve of the IM (smooth rotor, stator mode p, d-axis) ------------------------------------------
_MAG = {}


def mag_curve(p, imax_peak=700.0, n=60):
    """arrays (i_m_rms, psi_m_rms, Bt_pk, By_pk) from the MEC at a stator-mode-p amplitude sweep."""
    if p in _MAG:
        return _MAG[p]
    I = np.linspace(0, imax_peak, n)
    out = []
    U = None
    for a in I:
        r = mec_solve(dq_currents(p, 0.0, a, 0.0), rotor_smooth(), U)
        U = r["U"]
        pd, pq = dq_flux(p, 0.0, r["psi"])
        out.append((a / SQ2, pd / SQ2, r["Bt"].max(), r["By"].max()))
    o = np.array(out)
    _MAG[p] = (o[:, 0], o[:, 1], o[:, 2], o[:, 3])
    return _MAG[p]

# ---- IM electrical model ---------------------------------------------------------------------------------------
QR = 58
RHO_CAGE = 2.57e-8; BAR_A = 150e-6; BAR_L = 0.38; RING_A = 600e-6; RING_D = 0.27
LAM_BAR, LAM_RING = 1.5, 0.3         # rotor slot/ring permeance coefficients: shared assumption (rotor slot geometry undefined)


def im_params(p):
    beta = 2 * math.pi / QR
    cr2 = (1 / (math.pi * p)) ** 2 * math.sin(p * beta / 2) ** 2
    Lrr_m = 2 * math.pi * QR * KG * cr2
    Lm = L_m_fund(p)
    zeta = Lrr_m / Lm
    Rb = RHO_CAGE * BAR_L / BAR_A
    Rseg = RHO_CAGE * (math.pi * RING_D / QR) / RING_A
    s2 = math.sin(math.pi * p / QR) ** 2
    Rloop = 4 * Rb * s2 + 2 * Rseg
    Lsig_r = 4 * MU0 * BAR_L * LAM_BAR * s2 + 2 * MU0 * (math.pi * RING_D / QR) * LAM_RING
    i = np.arange(-60, 61); i = i[i != 0]
    nu = p + QR * i
    Ldiff_r = 2 * math.pi * QR * KG * np.sum((1 / (math.pi * nu)) ** 2 * np.sin(nu * beta / 2) ** 2)
    return dict(p=p, Lm=Lm, Lsig_s=L_sigma_mode(p) + L_diff(p), Rs=RS,
                Rr=Rloop / zeta, Lsig_r=(Lsig_r + Ldiff_r) / zeta, zeta=zeta, Ldiff_s=L_diff(p),
                Lslot=L_slot_mode(p), Lend=L_END)


def im_points(par, n_rpm, psi, wsl):
    p = par["p"]
    im_c, ps_c, Bt_c, By_c = mag_curve(p)
    im = np.interp(psi, ps_c, im_c)
    Bt = np.interp(psi, ps_c, Bt_c); By = np.interp(psi, ps_c, By_c)
    wm = p * n_rpm * RPM
    we = wm + wsl
    Ir = -1j * wsl * psi / (par["Rr"] + 1j * wsl * par["Lsig_r"])
    Is = im - Ir
    E = 1j * we * psi
    V = (par["Rs"] + 1j * we * par["Lsig_s"]) * Is + E
    Pag = M * np.real(E * np.conj(Is))
    T = Pag * p / we
    Pcus = M * par["Rs"] * np.abs(Is) ** 2
    Pcur = M * par["Rr"] * np.abs(Ir) ** 2
    Pfe = p_iron(we / (2 * math.pi), Bt, By)
    d = dict(T=T, V=np.abs(V), I=np.abs(Is), Pcus=Pcus, Pcur=Pcur, Pfe=Pfe, we=we, Bt=Bt, By=By, psi=psi, wsl=wsl)
    shp = np.broadcast(psi, wsl).shape
    return {k: np.array(np.broadcast_to(v, shp)) for k, v in d.items()}


CAP_MODE = {"mode": "mec"}      # "mec": soft MEC saturation only; "an_caps": also cap B_t,B_y at the analyst's flux limits


def psi_max(p):
    im_c, ps_c, Bt_c, By_c = mag_curve(p)
    if CAP_MODE["mode"] == "mec":
        return ps_c.max() * 0.99
    Bt_cap = STJ["B_gap_max_T"] * STJ["slot_pitch_m"] / TOOTH_W / KST
    By_cap = STJ["B_yoke_max_T"] / KST
    ok = (Bt_c <= Bt_cap) & (By_c <= By_cap)
    return float(ps_c[np.where(ok)[0].max()])


def im_grid(par, n_rpm, n_psi=140, n_sl=500):
    p = par["p"]
    psi = np.linspace(0.04 * psi_max(p), psi_max(p), n_psi)[:, None]
    wsl = np.linspace(1.0, 3000.0, n_sl)[None, :]
    return im_points(par, n_rpm, psi, wsl)


def im_envelope(par, n_rpm):
    g = im_grid(par, n_rpm)
    ok = (g["V"] <= VMAX) & (g["I"] <= IMAX)
    Tm = np.where(ok, g["T"], -1)
    j = np.unravel_index(np.argmax(Tm), Tm.shape)
    return float(Tm[j]), {k: float(v[j]) for k, v in g.items()}


def im_loss_point(par, n_rpm, T_req):
    g = im_grid(par, n_rpm, n_psi=200, n_sl=800)
    best = None
    for a in range(g["T"].shape[0]):
        T = g["T"][a]
        kpk = int(np.argmax(T))
        if T[kpk] < T_req:
            continue
        k = int(np.searchsorted(T[:kpk + 1], T_req))
        if k == 0:
            continue
        f = (T_req - T[k - 1]) / (T[k] - T[k - 1])
        val = {kk: (1 - f) * v[a, k - 1] + f * v[a, k] for kk, v in g.items()}
        if val["V"] > VMAX or val["I"] > IMAX:
            continue
        L = val["Pcus"] + val["Pcur"] + val["Pfe"]
        if best is None or L < best["L"]:
            best = dict(val, L=L)
    if best is None:
        return None
    Pm = p_mech(n_rpm)
    Pout = T_req * n_rpm * RPM - Pm
    tl = best["L"] + Pm
    best.update(eta=Pout / (Pout + tl), P_shaft_W=Pout, P_mech_W=Pm, f_e_Hz=best["we"] / 2 / math.pi,
                I_rms_A=best["I"], V_rms_V=best["V"], P_cu_stator_W=best["Pcus"], P_cu_rotor_W=best["Pcur"],
                P_fe_W=best["Pfe"], PF=(Pout + tl) / (M * best["V"] * best["I"]))
    return best

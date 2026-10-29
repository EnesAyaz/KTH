"""WRSM flux maps from the MEC (rotor = 8 salient poles with coil-group MMFs)."""
import math, numpy as np
import spb_core as c

NPOLE = 8
ARC = 0.7
F_MAX = 0.7122233430090569 * c.GEFF / c.MU0        # field MMF/pole at full I_f (shared input: analyst B0 at psi_f,max), ~737 A-turns
PAT = {"2p8": np.array([1, -1, 1, -1, 1, -1, 1, -1.0]), "2p4": np.array([1, 1, -1, -1, 1, 1, -1, -1.0])}
PMODE = {"2p8": 4, "2p4": 2}


def pattern_k(k):
    """FE_MMF.m transition pattern [1 k -k -1 1 k -k -1]; k=-1 -> 2p8, k=+1 -> 2p4."""
    return np.array([1, k, -k, -1, 1, k, -k, -1.0])


def dpos(mode, theta_d):
    """rotor angle placing the d-axis at theta_d: 2p8 d on pole 0 centre; 2p4 d between poles 0 and 1."""
    return theta_d - (0.0 if mode == "2p8" else math.pi / NPOLE)


GS = {'v': 1.0}


def solve_point(mode, id_, iq, If, U0=None, pat=None, rotor_kw=None):
    p = PMODE[mode] if pat is None or mode in PMODE else mode
    pattern = PAT[mode] if pat is None else pat
    th_d = 0.0
    rot = c.rotor_salient(dpos(mode, th_d), -If * F_MAX * pattern, arc=ARC, gs=GS['v'], **(rotor_kw or {}))
    r = c.mec_solve(c.dq_currents(p, th_d, id_, iq), rot, U0)
    pd, pq = c.dq_flux(p, th_d, r["psi"])
    Ls = c.L_sigma_mode(p) + c.L_diff(p)
    return pd + Ls * id_, pq + Ls * iq, r


if __name__ == "__main__":
    for mode in ("2p8", "2p4"):
        p = PMODE[mode]
        pd, pq, r = solve_point(mode, 0, 0, 1.0)
        print(mode, "psi_f(amp) at If=1:", pd, "rms", pd / c.SQ2, "pq", pq, "Bt", r["Bt"].max(), "By", r["By"].max())
        # linear inductances at small current and half field
        a = 5.0
        pd1, pq1, _ = solve_point(mode, -a, 0, 1.0); pd0, _, _ = solve_point(mode, 0, 0, 1.0)
        pd2, pq2, _ = solve_point(mode, 0, a, 1.0)
        print("   Ld~", (pd1 - pd0) / -a, "Lq~", pq2 / a, " (analyst Ld,Lq:", c.J["machine_parameters"]["WRSM"][mode]["L_d_H"], c.J["machine_parameters"]["WRSM"][mode]["L_q_H"], ")")
        # torque sign / virtual work check
        i = 20.0; d = 1e-4; IF = 0.1
        th = c.dq_currents(p, 0.0, 0.0, i)
        def psis(dth):
            rot = c.rotor_salient(dpos(mode, 0.0) + dth, -F_MAX * PAT[mode] * IF)
            return c.mec_solve(th, rot)["psi"]
        Tvw = np.sum(th * (psis(d) - psis(-d)) / (2 * d))   # rotor moves +dth => field moves +; torque on rotor = -(dW'/dtheta) wrt stator... sign test
        pdq, pqq, _ = solve_point(mode, 0, i, IF)
        Tdq = c.M / 2 * p * (pdq * i - pqq * 0)
        print("   T virtual-work", Tvw, " T dq", Tdq)

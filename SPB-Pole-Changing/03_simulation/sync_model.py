"""Synchronous machine operating-point solver on grids (PMSM from shared pu inputs, WRSM from MEC flux maps)."""
import math, numpy as np
from scipy.interpolate import RegularGridInterpolator
import spb_core as c

IA = c.SQ2 * c.IMAX
VA = c.SQ2 * c.VMAX
W_REF = 4 * 1200 * c.RPM
L_BASE = c.VMAX / (c.IMAX * W_REF)
PSI_BASE = c.VMAX / W_REF
P_FIELD_MAX = 4000.0


class Sync:
    def __init__(self, kind, mode="2p8", fmax=1.0, field_loss_scale=1.0, tag=""):
        self.kind, self.mode = kind, mode
        self.p = 4 if mode == "2p8" else 2
        self.fmax = fmax
        self.fls = field_loss_scale
        if kind == "WRSM":
            d = np.load(f"{c.ROOT}/03_simulation/scratch/wrsm_map_{mode}{tag}.npz")
            self.itp = RegularGridInterpolator((d["ID"], d["IQ"], d["IF"]), d["out"], bounds_error=False, fill_value=None)
        else:
            self.psi_pm = 0.70 * PSI_BASE * c.SQ2
            self.Ld, self.Lq = 0.65 * L_BASE, 1.30 * L_BASE

    def flux(self, id_, iq, If):
        if self.kind == "WRSM":
            pts = np.stack([id_, iq, If], axis=-1)
            o = self.itp(pts)
            return o[..., 0], o[..., 1], o[..., 2], o[..., 3]
        pd = self.psi_pm + self.Ld * id_
        pq = self.Lq * iq
        ps = np.hypot(pd, pq) / c.SQ2
        im_c, ps_c, Bt_c, By_c = c.mag_curve(4)
        return pd, pq, np.interp(ps, ps_c, Bt_c), np.interp(ps, ps_c, By_c)

    def eval(self, n_rpm, id_, iq, If):
        pd, pq, Bt, By = self.flux(id_, iq, If)
        we = self.p * n_rpm * c.RPM
        vd = c.RS * id_ - we * pq
        vq = c.RS * iq + we * pd
        V = np.hypot(vd, vq) / c.SQ2
        I = np.hypot(id_, iq) / c.SQ2
        T = c.M / 2 * self.p * (pd * iq - pq * id_)
        Pcu = c.M * c.RS * I ** 2
        Pfe = c.p_iron(we / 2 / math.pi, Bt, By)
        Pf = P_FIELD_MAX * self.fls * If ** 2 if self.kind == "WRSM" else 0 * If
        d = dict(T=T, V=V, I=I, Pcu=Pcu, Pfe=Pfe, Pf=Pf, we=we, Bt=Bt, By=By, id=id_, iq=iq, If=If, vd=vd, vq=vq, pd=pd, pq=pq)
        shp = np.broadcast(id_, iq, If).shape
        return {k: np.array(np.broadcast_to(v, shp)) for k, v in d.items()}

    def grid(self, nid=71, niq=76, nif=21):
        ID = np.linspace(-IA, 0.12 * IA, nid)
        IQ = np.linspace(0, IA, niq)
        IF = np.linspace(0, self.fmax, nif) if self.kind == "WRSM" else np.array([1.0])
        return np.meshgrid(ID, IQ, IF, indexing="ij")

    def envelope(self, n_rpm, **kw):
        a, b, f = self.grid(**kw)
        e = self.eval(n_rpm, a, b, f)
        ok = (e["V"] <= c.VMAX) & (e["I"] <= c.IMAX)
        Tm = np.where(ok, e["T"], -1)
        j = np.unravel_index(np.argmax(Tm), Tm.shape)
        return float(Tm[j]), {k: float(v[j]) for k, v in e.items()}

    def loss_point(self, n_rpm, T_req, **kw):
        a, b, f = self.grid(**kw)
        e = self.eval(n_rpm, a, b, f)
        T = e["T"]
        best = None
        # T vs iq at fixed (id, If): find first crossing of T_req on the rising branch
        nq = T.shape[1]
        ge = T >= T_req
        has = ge.any(axis=1)
        k = np.argmax(ge, axis=1)              # first iq index with T>=T_req
        ok = has & (k > 0)
        ii, ff = np.where(ok)
        kk = k[ii, ff]
        T0 = T[ii, kk - 1, ff]; T1 = T[ii, kk, ff]
        fr = (T_req - T0) / (T1 - T0)
        val = {n: (1 - fr) * v[ii, kk - 1, ff] + fr * v[ii, kk, ff] for n, v in e.items()}
        feas = (val["V"] <= c.VMAX) & (val["I"] <= c.IMAX)
        if not feas.any():
            return None
        Lt = val["Pcu"] + val["Pfe"] + val["Pf"]
        Lt = np.where(feas, Lt, np.inf)
        j = int(np.argmin(Lt))
        best = {n: float(v[j]) for n, v in val.items()}
        Pm = c.p_mech(n_rpm)
        Pout = T_req * n_rpm * c.RPM - Pm
        tot = Lt[j] + Pm
        # input incl. field supply power (field power is separate DC source; PF over stator VA only)
        best.update(eta=Pout / (Pout + tot), P_shaft_W=Pout, P_mech_W=Pm, I_rms_A=best["I"], V_rms_V=best["V"],
                    P_cu_stator_W=best["Pcu"], P_fe_W=best["Pfe"], P_field_W=best["Pf"],
                    PF=(Pout + best["Pcu"] + best["Pfe"] + Pm) / (c.M * best["V"] * best["I"]), P_cu_rotor_W=0.0)
        return best

"""
Gate-dip study (hold H6): off level x R_G x R_ON settings (Part A) and hypothetical gate-network edits (Part B) on the dpt_lx_skew deck.
Wraps ../dpt_lx_skew/run_lx_skew.py (not changed). Output only in this folder.

    python run_gate_dip.py run [regex] | post [regex]

Deck: Q3D BB_PL_LOOP_dpt_swv1 + SWNET (BB_PL_LX_dpt_swv1), 1 uH, board bank, 80 V pre-charge unless the case says otherwise, Bm on unless M0,
die gate probes on every FET (die V_GS = pin - 0.4 Ohm x gate current). Knobs, all text edits of the generated deck:
  voffH / voffL   off level of the HS hold source (VHOA/B) and of the LS PWL (VOFF), V_ISO - 5.1 V
  rg, ron         R_G per FET and the shared R_ON (R_G,on = rg + 2 ron)
  B: rk           resistor in every Kelvin leg (Lkb Rser), hypothetical
  B: roff         per-FET D_OFF + R_OFF from each gate (after R_G) to the driver, replacing the shared D_OFF/jumper, hypothetical
  B: cgs          capacitor gate pin to source pin on every FET, hypothetical
  B: tie          inductor (+0.5 mOhm) between the switch nodes of the two cells of a pair, hypothetical copper bridge
"""
import csv
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LX = os.path.join(HERE, "..", "dpt_lx_skew")
sys.path.insert(0, LX)
_argv, sys.argv = sys.argv, ["x", "none"]
import run_lx_skew as lx                          # noqa: E402
sys.argv = _argv

m, base = lx.m, lx.base
m.OUT = HERE
lx.HERE = HERE                                   # run_lx_skew.build reads the deck from its own HERE
base.SP = HERE
m.PAR = 6
CELLS = (1, 2, 3, 4)
TON80 = 4.1761e-6                                 # dpt_lx_skew trim at R_G,on 3.5 Ohm; +2.8 ns per Ohm of R_G,on (80_2 trim)


def tg(x):
    return ("%g" % x).replace(".", "p").replace("-", "m")


def mk(v=80, ron=1.5, rg=0.5, voffH=-1.9, voffL=-1.9, skew=0.0, bm=True, **what):
    rgon = rg + 2 * ron
    ton = TON80 + 2.8e-9 * (rgon - 3.5) if v == 80 else 2.56e-6
    c = m.case(v=float(v), ton=ton, skew=skew * 1e-9, lac=1.0, msign=1)
    c.update(rgon=rgon, ron=ron, rg=rg, stage=v, skew_ns=skew, bm=bm, rsel="dc", bmscale=1 if bm else 1e-6, die=True,
             voffH=voffH, voffL=voffL, what=what)
    return c


def name(v=80, ron=1.5, rg=0.5, voffH=-1.9, voffL=-1.9, skew=0.0, bm=True, **what):
    s = "%sV%d_Ron%s_Rg%s_off%s" % ("" if bm else "M0_", v, tg(ron), tg(rg), tg(voffH))
    if voffL != voffH:
        s += "_L%s" % tg(voffL)
    if skew:
        s += "_s%s" % tg(skew)
    for k in sorted(what):
        s += "_%s%s" % (k, tg(what[k]))
    return s


G = {}


def add(**kw):
    G[name(**kw)] = mk(**kw)


OFFS = (-1.9, -1.4, -0.9, -0.4)                   # V_ISO 7.0 / 6.5 / 6.0 / 5.5
RGS = (0.5, 1.0, 1.5, 2.2)
RONS = (1.0, 1.5, 2.2)
for off in OFFS:                                  # Part A: full off x R_G edge at R_ON 1.5 first, then the other R_ON
    for rg in RGS:
        add(voffH=off, voffL=off, rg=rg, ron=1.5)
for ron in (1.0, 2.2):
    for off in OFFS:
        for rg in RGS:
            add(voffH=off, voffL=off, rg=rg, ron=ron)
# Part B, hypothetical gate networks at the nominal setting (V_ISO 7, R_ON 1.5, R_G 0.5), 80 V, zero skew
for rk in (0.5, 1.0, 2.0):
    add(rk=rk)
for ro in (0.5, 1.0, 2.0):
    add(roff=ro)
for cg in (1.0, 2.2, 4.7):
    add(cgs=cg)
for lt in (2.0, 5.0):
    add(tie=lt)
EXTRA = os.path.join(HERE, "extra_cases.json")    # survivors, Zener and stage reruns are added here after the first pass
if os.path.exists(EXTRA):
    for kw in json.load(open(EXTRA)):
        add(**kw)
m.CASES = G
_b = lx.m.build                                   # run_lx_skew.build (SWNET, die probes, Bm scale)


def build(n):
    c = m.CASES[n]
    c.setdefault("tag", "BB_PL_LOOP_dpt_swv1")
    out = _b(n)
    p = os.path.join(HERE, out)
    txt = open(p).read()
    w = c["what"]
    txt, k = re.subn(r"VOFF=-1\.9", "VOFF=%g" % c["voffL"], txt)
    assert k == 1
    txt, k = re.subn(r"^(VHO[AB] ho[AB] KH[AB]) \{VOFF\}$", lambda q: "%s %g" % (q.group(1), c["voffH"]), txt, flags=re.M)
    assert k == 2, k
    if "rk" in w:
        txt, k = re.subn(r"^(Lkb[HL]\d \S+ \S+ \S+) Rser=10m$", lambda q: "%s Rser=%g" % (q.group(1), w["rk"] + 0.01), txt, flags=re.M)
        assert k == 8, k
    if "roff" in w:
        for s_, pair, cells in (("H", "A", (1, 2)), ("L", "A", (1, 2)), ("H", "B", (3, 4)), ("L", "B", (3, 4))):
            mo = re.search(r"^Lcoff%s%s st%s%so D%s%s (\S+) Rser=1m$" % (s_, pair, s_, pair, s_, pair), txt, flags=re.M)
            lco = mo.group(1)
            txt, k = re.subn(r"^(Doff%s%s|Lcoff%s%s) .*\n" % (s_, pair, s_, pair), "", txt, flags=re.M)
            assert k == 2, k
            add_ = "\n".join("Doffc%s%d gx%s%d do%s%d DID\nRoffc%s%d do%s%d db%s%d %g\nLoffc%s%d db%s%d D%s%s %s Rser=1m" % (
                s_, c_, s_, c_, s_, c_, s_, c_, s_, c_, s_, c_, w["roff"], s_, c_, s_, c_, s_, pair, lco) for c_ in cells)
            txt = txt.replace("\nRg%s%d " % (s_, cells[0]), "\n" + add_ + "\nRg%s%d " % (s_, cells[0]), 1)
    if "cgs" in w:
        add_ = "\n".join("Cgs%s%d g%s%d Q%s_S_%d %gn" % (s_, c_, s_, c_, s_, c_, w["cgs"]) for s_ in "HL" for c_ in CELLS)
        txt = txt.replace("\nXSW ", "\n" + add_ + "\nXSW ", 1)
    if "tie" in w:
        add_ = "Ltie12 QH_S_1 QH_S_2 %gn Rser=0.5m\nLtie34 QH_S_3 QH_S_4 %gn Rser=0.5m" % (w["tie"], w["tie"])
        txt = txt.replace("\nXSW ", "\n" + add_ + "\nXSW ", 1)
    sv = " ".join("I(Lkb%s%d) I(Rg%s%d) V(kk%s%d) V(st%s%s)" % (s_, i, s_, i, s_, i, s_, "A" if i < 3 else "B") for s_ in "HL" for i in CELLS)
    txt, k = re.subn(r"^\.save (.*)$", lambda q: ".save " + q.group(1) + " " + sv, txt, flags=re.M)
    assert k == 1
    open(p, "w").write(txt)
    return out


m.build = build


def metrics(n):
    c = m.CASES[n]
    r = m.post(n)                                 # E_on, E_off, di/dt, timing; sets MASK
    t, d = m.read_raw(os.path.join(HERE, n + ".raw"))
    w = m.W(t, d)
    T0 = 0.5e-6
    T1 = T0 + c["ton"]
    T2 = T1 + c["toff"]
    T3 = T2 + c["ton2"]
    TE = float(t[-1])
    vh = {i: w.vd("V(dH%d)" % i, "V(QH_S_%d)" % i) for i in CELLS}
    vl = {i: w.vd("V(dL%d)" % i, "V(QL_S_%d)" % i) for i in CELLS}
    m.MASK[:] = m.find_mask(t, np.max([np.abs(vh[i]) for i in CELLS] + [np.abs(vl[i]) for i in CELLS], axis=0))
    e = dict(stage_V=c["stage"], R_ON=c["ron"], R_G=c["rg"], off_HS=c["voffH"], off_LS=c["voffL"], skew_ns=c["skew_ns"], Bm=c["bm"],
             what=json.dumps(c["what"]), faults=json.dumps([[round(x * 1e9) for x in q] for q in m.MASK]), t_end_us=round(TE * 1e6, 3))
    for s_ in "HL":
        pin = {i: w.vd("V(g%s%d)" % (s_, i), "V(Q%s_S_%d)" % (s_, i)) for i in CELLS}
        die = {i: pin[i] - 0.4 * w("I(VG%s%d)" % (s_, i)) for i in CELLS}
        mins, below, bumps = [], [], []
        for i in CELLS:
            for x in (pin[i], die[i]):
                tu, xu = m.clean(t, x, 0, TE)
                mins.append(float(np.nanmin(xu)))
            tu, xu = m.clean(t, die[i], 0, TE)
            below.append(float((xu < -3.7).sum() * 0.1))
            # held-off bump: HS over the whole run; LS only in its off intervals (before T0, off-time, after pulse 2), edges excluded
            wins = [(0, TE)] if s_ == "H" else [(1e-9, T0 - 2e-9), (T1 + 60e-9, T2 - 2e-9), (T3 + 60e-9, TE)]
            for a, b in wins:
                for x in (pin[i], die[i]):
                    tu, xu = m.clean(t, x, a, b)
                    bumps.append(float(np.nanmax(xu)))
        e[s_ + "S_VGS_min"] = round(min(mins), 2)
        e[s_ + "S_ns_below_m3p7_die"] = round(max(below), 1)
        e[s_ + "S_bump_max"] = round(max(bumps), 2)
        e[s_ + "S_bump_margin_to_Vth0p8"] = round(0.8 - max(bumps), 2)
    e["HS_VDS_max"] = round(max(w.cmx(vh[i], 0, TE) for i in CELLS), 1)
    e["LS_VDS_max"] = round(max(w.cmx(vl[i], 0, TE) for i in CELLS), 1)
    for k in ("I_T1_peak", "I_T3_peak", "Eon", "Eon_250ns", "Eoff", "Eoff2", "didt_on", "didt_off", "dvdt_on", "dvdt_off", "ton_delay_ns", "imb_end1"
              if False else "ton_delay_ns"):
        if k in r:
            e[k] = round(float(r[k]), 2)
    il = {i: w("I(VIL%d)" % i) for i in CELLS}
    e["I_end1_cells"] = [round(float(il[i][w.win(T1 - 20e-9, T1)].mean()), 1) for i in CELLS]
    # coupling path at the first turn-off: anti-phase currents in the Kelvin legs and the R_G of the HS pair A, switch-node spread
    k = w.win(T1, T1 + 40e-9)
    e["cpl_SW2_minus_SW1_max_V"] = round(float(np.max(w("V(QH_S_2)")[k] - w("V(QH_S_1)")[k])), 2)
    for lab, key in (("Kelvin_leg", "I(LkbH%d)"), ("RG", "I(RgH%d)")):
        a1, a2 = w(key % 1)[k], w(key % 2)[k]
        e["cpl_%s_cell1_pk_A" % lab] = round(float(a1[np.argmax(np.abs(a1))]), 2)
        e["cpl_%s_cell2_pk_A" % lab] = round(float(a2[np.argmax(np.abs(a2))]), 2)
        e["cpl_%s_sum_pk_A" % lab] = round(float(np.max(np.abs(a1 + a2))), 2)
    e["cpl_kk2_minus_kk1_max_V"] = round(float(np.max(np.abs(w("V(kkH2)")[k] - w("V(kkH1)")[k]))), 2)
    e["cpl_star_minus_K_min_V"] = round(float(np.min(w("V(stHA)")[k] - w("V(kkH1)")[k])), 2)
    # pass/fail
    fails = []
    for s_ in "HL":
        if e[s_ + "S_VGS_min"] < -3.7:
            fails.append("%sS VGS %.2f" % (s_, e[s_ + "S_VGS_min"]))
        if e[s_ + "S_bump_max"] >= 0.3:
            fails.append("%sS bump %.2f" % (s_, e[s_ + "S_bump_max"]))
    for s_ in "HL":
        if e[s_ + "S_VDS_max"] >= 100:
            fails.append("%sS VDS %.1f" % (s_, e[s_ + "S_VDS_max"]))
    e["pass"] = not fails
    e["fails"] = "; ".join(fails)
    return e


KEYS = ["pass", "fails", "stage_V", "R_ON", "R_G", "off_HS", "off_LS", "skew_ns", "Bm", "what", "HS_VGS_min", "HS_ns_below_m3p7_die", "HS_bump_max",
        "HS_bump_margin_to_Vth0p8", "LS_VGS_min", "LS_ns_below_m3p7_die", "LS_bump_max", "LS_bump_margin_to_Vth0p8", "HS_VDS_max", "LS_VDS_max", "I_T1_peak",
        "I_T3_peak", "Eon", "Eon_250ns", "Eoff", "Eoff2", "didt_on", "didt_off", "dvdt_on", "dvdt_off", "ton_delay_ns", "I_end1_cells", "cpl_SW2_minus_SW1_max_V",
        "cpl_Kelvin_leg_cell1_pk_A", "cpl_Kelvin_leg_cell2_pk_A", "cpl_Kelvin_leg_sum_pk_A", "cpl_RG_cell1_pk_A", "cpl_RG_cell2_pk_A", "cpl_RG_sum_pk_A",
        "cpl_kk2_minus_kk1_max_V", "cpl_star_minus_K_min_V", "faults", "t_end_us"]


def main():
    mode = sys.argv[1]
    rx = re.compile(sys.argv[2]) if len(sys.argv) > 2 else None
    names = [n for n in m.CASES if not rx or rx.search(n)]
    if mode == "list":
        print(len(names), names)
    if mode == "build":
        for n in names:
            print(m.build(n))
    if mode == "run":
        def finished(n):
            p = os.path.join(HERE, n + ".log")
            if not os.path.exists(p):
                return False
            b = open(p, "rb").read()
            return "Total elapsed time".encode("utf-16-le") in b or b"Total elapsed time" in b
        todo = [n for n in names if not finished(n)]
        print(len(todo), "to run of", len(names), flush=True)
        m.run_all(todo)
    if mode == "post":
        p = os.path.join(HERE, "results.json")
        old = json.load(open(p)) if os.path.exists(p) else {}
        for n in names:
            if not os.path.exists(os.path.join(HERE, n + ".raw")):
                continue
            try:
                old[n] = metrics(n)
            except Exception as ex:
                old[n] = dict(failed=repr(ex)[:300])
                print("FAILED", n, old[n]["failed"], flush=True)
        json.dump(old, open(p, "w"), indent=1)
        with open(os.path.join(HERE, "results.csv"), "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["case"] + KEYS + ["failed"])
            for n in sorted(old):
                wr.writerow([n] + [old[n].get(k) for k in KEYS] + [old[n].get("failed")])
        print("posted", len(names), flush=True)


if __name__ == "__main__":
    main()

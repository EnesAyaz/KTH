"""
Simulation validation of the final leg boards: double-pulse test of the four-cell leg in LTspice with the copper
taken from the Q3D extraction of the routed boards (instead of the lumped loop of the design flow).

    python simulation/bb_q3d/revb_q3d_spice.py            -> simulation/bb_spice/REVB_Q3D_<board>.cir/.raw/.log
                                                            reports/slides/data/q3d_spice_numbers.json

Copper (AC R/L matrix at 100 MHz, every mutual inductance kept as a K statement):
  load : BB_PL_LX_load   cells + bypass pads + joined switch-node copper (no shunt)
  dpt  : BB_PL_LOOP_dpt  cells + bypass pads + shunt lands; the four switch nodes are joined outside the model
Components (same data as revb_post.py): bypass rows as C_eff / ESL / ESR per row, UFCS shunt 1 mOhm + 120 pH,
bank 20 x 22 uF (127 uF eff.) behind L_b, 75 V supply through 20 nH, load inductor at the ac bolt.
Gate drive: -1.9 V / +5 V (V_ISO 7 V, 5.1 V Zener), 4 / 8 A (0.85 / 0.35 Ohm), one driver channel per pair. Gate network of the board with the
inductances from the gate Q3D model (gate_post.py -> gate_summary_dpt.json, see gate_extracted()): R_ON 1.5 Ohm
shared, R_G 0.5 Ohm per FET (RGON = R_G + 2 R_ON = 3.5 Ohm per device), D_OFF + R_OFF 0, and the coupling of the
commutation loops into the gate loops. The case "dpt_lumpgate" keeps the earlier lumped gate drive of the design flow
(FLOW_lumped.inc): R_g,on 2 Ohm, R_g,off 0, gate loop 1.7 nH per device (1.2 nH out, 0.5 nH Kelvin return), one driver channel per
pair of cells (cells 1+2, 3+4), the same PWM for both pairs. Load current at turn-off 322 A (80.5 A per device).
The lumped reference (one device, LLOOP = the Q3D loop per cell, 80.5 A) is run from the same driver data.
"""
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "revb_post.py"), encoding="utf-8").read().split("summary = {}")[0]
__file__ = os.path.join(HERE, "revb_post.py")
exec(_src)                                       # load(), RES, ROOT, ESL_0805, C_0805, ESR_0805, C_1210, ...
__file__ = os.path.join(HERE, "revb_q3d_spice.py")

SP = os.path.join(ROOT, "simulation", "bb_spice")
LTS = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "ADI", "LTspice", "LTspice.exe")
IPK = 322.0                                      # A at turn-off (228 A_rms x sqrt2)
TON1 = 10.667e-6
LB = 2.0e-9                                      # bank behind the cell band (terminal row + bank copper), per board
MODELS = {"load": "BB_PL_LX_load", "dpt": "BB_PL_LOOP_dpt"}


def counts(board):
    geo = json.load(open(os.path.join(RES, "revb_loop_geometry_%s.json" % board)))
    return {t[1]: len(t[3]) for t in geo["terminals"]}


def subckt(tag):
    m = load(tag)
    L, br = m["Lac"], m["branches"]
    # DC resistance matrix: the 10 us current ramp divides by R; the 100 MHz R (skin effect) would distort it.
    # Branches sharing copper on the way to the net sink have large mutual resistances, which an R per branch
    # cannot represent, so the full matrix is applied with one behavioural source per branch, V_i = sum R_ij I_j.
    R = m.get("Rdc", m["Rac"])
    R = 0.5 * (R + R.T)
    terms = sorted({t for b in br for t in b})
    # symmetric, positive definite (Q3D matrices are, but guard against export rounding)
    L = 0.5 * (L + L.T)
    ev = np.linalg.eigvalsh(L)
    assert ev.min() > 0, "L matrix not positive definite"
    out = [".subckt %s %s" % (tag, " ".join(terms)),
           "* Q3D AC partial inductance (100 MHz, K for every mutual) and full DC resistance matrix,",
           "* branch = source terminal -> net sink"]
    for i, (a, b) in enumerate(br):
        out.append("L%d %s m%d %.9gn" % (i, a, i, L[i, i] * 1e9))
        out.append("B%d m%d %s V=%s" % (i, i, b, "+".join("%.6g*I(L%d)" % (R[i, j], j)
                                                        for j in range(len(br)) if abs(R[i, j]) > 1e-9)))
    nk = 0
    for i in range(len(br)):
        for j in range(i + 1, len(br)):
            k = L[i, j] / math.sqrt(L[i, i] * L[j, j])
            if abs(k) > 1e-5:
                nk += 1
                out.append("K%d_%d L%d L%d %.9f" % (i, j, i, j, max(min(k, 0.999999), -0.999999)))
    out.append(".ends %s" % tag)
    return "\n".join(out), terms, len(br), nk


GSUM = os.path.join(RES, "gate_summary_dpt.json")
GATE_OK = os.path.exists(GSUM)
R_ON_STAR = 1.5                                  # board: R_ON shared by the pair (R7 / R9), R_G per FET = RGON - 2 R_ON
R_G_FET = 0.5
RG_BOARD = R_G_FET + 2 * R_ON_STAR                   # 3.5 Ohm per device (R_ON 0.75 -> 1.5 after the gate Q3D and SPICE, 2026-10-23)
GATE_ESL = "esl0.4"                              # 1 uF 0603 output-side bypass taken as 0.4 nH (no published ESL)
L_R0603 = 0.4                                    # nH, body ESL of an 0603 resistor (R_G, R_ON, R_OFF jumper), typical
L_DOFF = 1.0                                     # nH, SOD-323F diode body (D_OFF), typical
V_OFF = -1.9                                     # V, gate off level: V_GS,off = -(V_ISO - 5.1 V) with V_ISO = 7 V


def gate_extracted(pair, cells, rgon):
    """Gate network of the board with the inductances from the gate Q3D model (gate_post.py, driver block 1 of the
    DPT board; block 2 is the same layout shifted: cell 3 <-> cell 1, cell 4 <-> cell 2). Driver output D<s><pair> ->
    R_ON + L_common,on -> star; star -> L_common,off -> D_OFF -> driver (turn-off); star -> R_G + L_branch -> gate;
    Kelvin branch (half the Kelvin pad-to-pad inductance) -> common Kelvin node K<s><pair> at the driver.
    The coupling of the commutation loops into each gate loop (LS switching, HS held off) is a source in the Kelvin
    return: v = M_own di_own/dt + M_other di_other/dt, with the LS drain currents of the two cells of the block."""
    gs = json.load(open(GSUM))
    sp, kp = gs["split_nH"][GATE_ESL], gs["kelvin_pair_nH"]
    cp = gs["coupling_pH"]["ls_switching_hs_held_off"]
    rg = R_G_FET                                 # 0.5 Ohm per FET; the sweep changes R_ON (shared by the pair)
    ron = (rgon - R_G_FET) / 2
    ref = {1: 1, 2: 2, 3: 1, 4: 2}               # block-1 cell each cell copies (block 2 = block 1 shifted, not mirrored)
    fet = {("H", 1): "Q1", ("H", 2): "Q2", ("L", 1): "Q3", ("L", 2): "Q4"}
    ln = ["* gate network %s: extracted (gate_summary_dpt.json, bypass ESL %s nH)" % (pair, GATE_ESL[3:])]
    for s, ch in (("H", "A"), ("L", "B")):
        qs = [fet[(s, ref[c])] for c in cells]
        lc_on = sum(sp[q]["common_on"] for q in qs) / 2
        lc_off = sum(sp[q]["common_off"] for q in qs) / 2
        lk = kp[ch] / 2
        st, d = "st%s%s" % (s, pair), "D%s%s" % (s, pair)
        # part bodies are not in the Q3D copper: R_ON in the on path, D_OFF + the R_OFF jumper in the off path
        ln += ["Ron%s%s %s %sx %g" % (s, pair, d, st, ron),
               "Lcon%s%s %sx %s %.4gn" % (s, pair, st, st, lc_on + L_R0603),
               "Doff%s%s %s %so DID" % (s, pair, st, st),
               "Lcoff%s%s %so %s %.4gn Rser=1m" % (s, pair, st, d, lc_off + L_DOFF + L_R0603)]
        for c in cells:
            q = fet[(s, ref[c])]
            other = [x for x in cells if x != c][0]
            src = ("QH_S_%d" if s == "H" else "QL_S_%d") % c
            # gate and Kelvin legs of a branch run as a coupled pair (same-layer neighbours since the fabrication-
            # review re-layout): the Kelvin leg carries half the Kelvin pad-to-pad inductance, and when that exceeds
            # the branch loop the gate leg gets the same inductance plus a coupling k so that L_g + L_k - 2M equals the
            # extracted branch loop (L_branch - L_k alone went negative, -0.6 nH LS, and stalled the solver); both legs
            # are passed from their first node around the loop (st -> g, source -> K), so the K value is negative
            br = sp[q]["branch"]
            if br > lk:
                lb, kgk = br - lk, 0.0
            else:
                lb, kgk = lk, (2 * lk - br) / (2 * lk)
            m_own = cp["cell%d_only" % ref[c]][q] * 1e-12
            m_oth = cp["cell%d_only" % ref[other]][q] * 1e-12
            ln += ["Rg%s%d %s gr%s%d %g" % (s, c, st, s, c, rg),
                   "Lrg%s%d gr%s%d gx%s%d %.4gn" % (s, c, s, c, s, c, L_R0603),          # R_G body
                   "Lgb%s%d gx%s%d g%s%d %.4gn" % (s, c, s, c, s, c, lb),
                   "Lkb%s%d %s kk%s%d %.4gn Rser=10m" % (s, c, src, s, c, lk),
                   ] + (["Kgk%s%d Lgb%s%d Lkb%s%d %.4f" % (s, c, s, c, s, c, -kgk)] if kgk > 0 else []) + [
                   "Bm%s%d K%s%s kk%s%d V=%.4g*ddt(I(VIL%d))+%.4g*ddt(I(VIL%d))" % (s, c, s, pair, s, c, m_own, c,
                                                                               m_oth, other)]
    return ln


def netlist(board, rgon=2, gate=True):
    tag = MODELS[board]
    sub, terms, nbr, nk = subckt(tag)
    nb = counts(board)
    shunt = "RSI_1" in terms
    ln = ["* Leg board '%s': double-pulse test with the Q3D copper %s (%d branches, %d couplings)" % (board, tag, nbr, nk),
          ".param VBUS=75 IPK=%g TON1=%g LLOAD={TON1*VBUS/IPK}" % (IPK, TON1),
          ".param RGON=%g RGOFF=0 RPU=0.85 RPD=0.35 VDRV=5 VOFF=%g LGO=1.2n LGK=0.5n" % (rgon, V_OFF),
          ".param TSTART=0.5u TOFF=1u TON2=0.5u",
          ".param T1={TSTART+TON1} T2={T1+TOFF} TEND={T2+TON2+0.3u}",
          ".include ../LMG1210-EPC2361/EPC2361.lib",
          ".model DID D(Ron=1m Roff=1G Vfwd=0)",
          sub,
          "XCU %s %s" % (" ".join(terms), tag),
          "* supply, bank (20 x 22 uF, %.0f uF eff.) behind L_b, load at the ac bolt" % (20 * C_1210 * 1e6),
          "V1 VS 0 {VBUS}", "Cbulk VS 0 1m Rser=20m", "Lbus VS BP 20n Rser=2m",
          "Cbank BP BN %.4gu Rser=%.4g" % (20 * C_1210 * 1e6, ESR_1210 / 20), "Rgnd BN 0 1u"]
    for c in range(1, 5):
        ln += ["Lbp%d BP CapP_%d %.4gn Rser=0.2m" % (c, c, 4 * LB * 1e9 / 2),
               "Lbn%d BN CapN_%d %.4gn Rser=0.2m" % (c, c, 4 * LB * 1e9 / 2)]
    for c in range(1, 5):
        for p, n, key in (("CapP_%d" % c, "CapN_%d" % c, "CapP_%d" % c), ("CapPb_%d" % c, "CapNb_%d" % c, "CapPb_%d" % c)):
            k = nb.get(key, 6 if key.startswith("CapP_") else 0)
            if k:
                ln.append("C%s %s %s %.4gu Rser=%.4g Lser=%.4gn" % (key, p, n, k * C_0805 * 1e6, ESR_0805 / k, ESL_0805 * 1e9 / k))
        if shunt:
            # LTspice resistors take no Lser (the line was reported as an error and the 120 pH ignored)
            ln += ["Rsh%d RSI_%d rsx%d %g" % (c, c, c, R_SHUNT), "Lsh%d rsx%d RSN_%d 0.12n" % (c, c, c)]
        ln.append("Lac%d QH_S_%d ACO 1n Rser=0.1m" % (c, c))
    ln.append("Lload ACO BP {LLOAD} Rser=2m Cpar=20p")
    # transistors with 0 V drain-current probes
    for c in range(1, 5):
        ln += ["VIH%d QH_D_%d dH%d 0" % (c, c, c), "XQH%d gH%d dH%d QH_S_%d EPC2361" % (c, c, c, c),
               "VIL%d QL_D_%d dL%d 0" % (c, c, c), "XQL%d gL%d dL%d QL_S_%d EPC2361" % (c, c, c, c)]
    pwm = ("PWL(0 {VOFF} {TSTART} {VOFF} {TSTART+1n} {VDRV} {T1} {VDRV} {T1+1n} {VOFF} {T2} {VOFF} {T2+1n} {VDRV} "
           "{T2+TON2} {VDRV} {T2+TON2+1n} {VOFF})")                  # off level V_OFF (negative bias), on +5 V
    for pair, cells in (("A", (1, 2)), ("B", (3, 4))):
        # low side: pulsed channel, star to both gates, Kelvin returns to both sources
        ln += ["VLO%s lo%s KL%s %s" % (pair, pair, pair, pwm),
               "Rpu%s lo%s lo%s1 {RPU}" % (pair, pair, pair), "Dpu%s lo%s1 DL%s DID" % (pair, pair, pair),
               "Dpd%s DL%s lo%s2 DID" % (pair, pair, pair), "Rpd%s lo%s2 lo%s {RPD}" % (pair, pair, pair),
               "VHO%s ho%s KH%s {VOFF}" % (pair, pair, pair), "Rph%s ho%s DH%s {RPD}" % (pair, pair, pair)]
        if gate:
            ln += gate_extracted(pair, cells, rgon)
            continue
        for c in cells:
            for s, d, g, src in (("L", "DL" + pair, "gL%d" % c, "QL_S_%d" % c), ("H", "DH" + pair, "gH%d" % c, "QH_S_%d" % c)):
                ln += ["Lg%s%d %s g%sx%d {LGO}" % (s, c, d, s, c),
                       "Ron%s%d g%sx%d g%s1_%d {RGON}" % (s, c, s, c, s, c), "Don%s%d g%s1_%d %s DID" % (s, c, s, c, g),
                       "Doff%s%d %s g%s2_%d DID" % (s, c, g, s, c), "Roff%s%d g%s2_%d g%sx%d {RGOFF+1m}" % (s, c, s, c, s, c),
                       "Lk%s%d %s K%s%s {LGK} Rser=10m" % (s, c, src, s, pair)]
    ln += [".options plotwinsize=0", ".tran 0 {TEND} 0 0.1n"]
    sv = ["I(Lload)"]
    for c in range(1, 5):
        sv += ["I(VIL%d)" % c, "I(VIH%d)" % c, "V(QL_D_%d)" % c, "V(QL_S_%d)" % c, "V(QH_D_%d)" % c, "V(QH_S_%d)" % c,
               "V(dL%d)" % c, "V(dH%d)" % c, "V(gL%d)" % c, "V(gH%d)" % c]
    ln.append(".save " + " ".join(sv))
    ln.append(".meas TRAN Iload FIND I(Lload) AT {T1}")
    for c in range(1, 5):
        vl, vh = "V(dL%d,QL_S_%d)" % (c, c), "V(dH%d,QH_S_%d)" % (c, c)
        ln += [".meas TRAN I%d FIND I(VIL%d) AT {T1}" % (c, c),
               ".meas TRAN Vpk%d MAX %s FROM {T1} TO {T1+150n}" % (c, vl),
               ".meas TRAN Eoff%d INTEG %s*I(VIL%d) FROM {T1} TO {T1+150n}" % (c, vl, c),
               ".meas TRAN Eon%d INTEG %s*I(VIL%d) FROM {T2} TO {T2+150n}" % (c, vl, c),
               ".meas TRAN Ionpk%d MAX I(VIL%d) FROM {T2} TO {T2+150n}" % (c, c),
               ".meas TRAN didton%d MAX D(I(VIL%d)) FROM {T2} TO {T2+150n}" % (c, c),
               ".meas TRAN didtoff%d MIN D(I(VIL%d)) FROM {T1} TO {T1+150n}" % (c, c),
               ".meas TRAN VHpk%d MAX %s FROM {T2} TO {T2+150n}" % (c, vh),
               ".meas TRAN bump%d MAX V(gH%d,QH_S_%d) FROM {T2} TO {T2+150n}" % (c, c, c)]
    ln.append(".end")
    name = "REVB_Q3D_%s%s%s.cir" % (board, "" if rgon == RG_BOARD else "_rg%g" % rgon, "" if gate else "_lumpgate")
    open(os.path.join(SP, name), "w").write("\n".join(ln) + "\n")
    return name


def lumped(loops):
    """reference: one device, lumped loop = Q3D loop per cell, same driver; FLOW_lumped.inc of the design flow"""
    name = "REVB_lumped_ref.cir"
    open(os.path.join(SP, name), "w").write(
        "* Lumped reference for the Q3D validation: one EPC2361 per switch at 80.5 A, LLOOP = Q3D loop per cell.\n"
        ".param VBUS=75 IPK=%g TON1=%g LLOAD={TON1*VBUS/IPK} RGON=2 RGOFF=0 RPU=0.85 RPD=0.35\n"
        ".step param LLOOP list %s\n"
        ".include FLOW_lumped.inc\n.end\n" % (IPK / 4, TON1, " ".join("%.4gn" % v for v in loops)))
    return name


def run(cir):
    print("running", cir, flush=True)
    subprocess.run([LTS, "-b", os.path.join(SP, cir)], cwd=SP, check=False, timeout=7200)


def meas(cir):
    raw = open(os.path.join(SP, cir.replace(".cir", ".log")), "rb").read()
    txt = raw.decode("utf-16-le") if raw[1:2] == b"\x00" else raw.decode("latin-1")
    out = {}
    for m in re.finditer(r"^(\w+):\s.*?=\s*([-+0-9.eE]+)", txt, re.M):
        out.setdefault(m.group(1).lower(), []).append(float(m.group(2)))
    for m in re.finditer(r"^(\w+)=([-+0-9.eE]+)", txt, re.M):      # PARAM-type lines
        out.setdefault(m.group(1).lower(), []).append(float(m.group(2)))
    # stepped measurements are printed as a table: "Measurement: name", header, "  <step>  <value> ..."
    name = None
    for line in txt.replace("\r", "").splitlines():
        if line.startswith("Measurement:"):
            name = line.split(":", 1)[1].strip().lower()
            out[name] = []
        elif name and line.strip():
            p = line.split()
            if p[0].isdigit() and len(p) > 1:
                out[name].append(float(p[1]))
        else:
            name = None
    return out


def main():
    fq = json.load(open(os.path.join(ROOT, "reports", "slides", "data", "final_numbers.json")))
    boards = [b for b in sys.argv[1:]] or ["load", "dpt"]
    res = {}
    # R_ON 1.5 Ohm (board) and 1.0 Ohm with the extracted gate network, plus the lumped design-flow gate at the board R_ON
    cases = [(b, rg, GATE_OK) for rg in (RG_BOARD, 2.5) for b in boards] +         ([("dpt", RG_BOARD, False)] if GATE_OK and "dpt" in boards else [])
    for b, rg, gt in cases:
        if not os.path.exists(os.path.join(RES, MODELS[b] + "_matrix.txt")):
            continue
        cir = netlist(b, rg, gt)
        run(cir)
        m = meas(cir)
        cells = []
        for c in range(1, 5):
            g = lambda k: m.get("%s%d" % (k, c), [None])[0]
            cells.append(dict(I_off=g("i"), Vpk=g("vpk"), Eoff_uJ=g("eoff") * 1e6, Eon_uJ=g("eon") * 1e6,
                              Ion_pk=g("ionpk"), didt_on=g("didton") / 1e9, didt_off=-g("didtoff") / 1e9,
                              VHpk=g("vhpk"), bump=g("bump")))
        lp = fq[b]["loop"]["mean_nH"]
        res[b + ("" if rg == RG_BOARD else "_rg%g" % rg) + ("" if gt else "_lumpgate")] = dict(loop_nH=lp, RGON=rg, gate="extracted" if gt else "lumped 1.7 nH", VHpk_max=max(c["VHpk"] for c in cells), Iload=m["iload"][0], cells=cells,
                      Eon_tot_uJ=sum(c["Eon_uJ"] for c in cells), Eoff_tot_uJ=sum(c["Eoff_uJ"] for c in cells),
                      Vpk_max=max(c["Vpk"] for c in cells),
                      share_off_pct=100 * (max(c["I_off"] for c in cells) / (sum(c["I_off"] for c in cells) / 4) - 1),
                      share_Eon_pct=100 * (max(c["Eon_uJ"] for c in cells) / (sum(c["Eon_uJ"] for c in cells) / 4) - 1),
                      share_Eoff_pct=100 * (max(c["Eoff_uJ"] for c in cells) / (sum(c["Eoff_uJ"] for c in cells) / 4) - 1))
    loops = [fq[b]["loop"]["mean_nH"] for b in ("load", "dpt")]
    if res:
        cir = lumped(loops)
        run(cir)
        m = meas(cir)
        res["lumped"] = dict(loop_nH=loops, Eon_uJ=[v * 1e6 for v in m["eon"]], Eoff_uJ=[v * 1e6 for v in m["eoff"]],
                             Vpk=m["vdsl_pk"], VHpk=m["vdsh_pk"], didt_on=[v / 1e9 for v in m["didt_on"]],
                             didt_off=[-v / 1e9 for v in m["didt_off"]], bump=m["vgsh_bump"])
    out = os.path.join(ROOT, "reports", "slides", "data", "q3d_spice_numbers.json")
    old = json.load(open(out)) if os.path.exists(out) else {}
    old.update(res)                                  # a run of one board keeps the other board's cases
    json.dump(old, open(out, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()

"""
LTspice runs for the decision-driven slides (reports/slides/spb_design_flow.tex), derived from the building-block
netlist simulation/bb_spice/BB_circuit.inc (Q3D copper, EPC2361 model, per-FET Rg_on / Rg_off, LT8418-like driver).

  FLOW_single     one EPC2361 per switch, one driver: only the left cell of the building block is populated, so the
                  device sees the same commutation loop (0.374 nH per cell) and the same gate loop as in the block.
                  Double pulse 10-300 A at 75 V -> Eon, Eoff, peak V_DS, dv/dt per device.
  FLOW_two        two complete building blocks (2 x EPC2361 per switch each) on one DC bus, AC terminals joined through
                  L_x/2 each; the low-side PWM of block 2 is delayed by DLY. Double pulse at 322 A (300 kW, M 1.15, pf 0.9, peak per
                  leg) -> current of each block before/after the edges, switching energy of each block.

    python scripts/design_flow_spice.py [single|two|parse]
      writes simulation/bb_spice/FLOW_*.cir / .inc, runs LTspice in batch mode, writes
      reports/slides/data/flow_spice.json
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP = os.path.join(ROOT, "simulation", "bb_spice")
OUTD = os.path.join(ROOT, "reports", "slides", "data")
LTS = os.path.join(os.environ["LOCALAPPDATA"], "Programs", "ADI", "LTspice", "LTspice.exe")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from bb_losses import parse_log  # noqa: E402

BODY = open(os.path.join(SP, "BB_circuit.inc")).read()
RIGHT = ("VIHR", "XQHR", "VILR", "XQLR", "Ronlr", "Donlr", "Dofflr", "Rofflr", "Ronhr", "Donhr", "Doffhr", "Roffhr")


def element_lines(txt):
    """Circuit part of BB_circuit.inc: everything before the analysis section."""
    return txt.split("* ---------------- analysis")[0]


# ------------------------------------------------------------------------------------------------ single device
def write_single():
    lines = []
    for ln in element_lines(BODY).splitlines():
        if ln.split() and ln.split()[0] in RIGHT:
            continue
        lines.append(ln)
    lines += ["* unused right-cell gate-star outputs and pads held by 1 G (cell not populated)",
              "Rnc1 GLR 0 1G", "Rnc2 GHR 0 1G", "Rnc3 QL_D_R 0 1G", "Rnc4 QH_D_R 0 1G",
              "* ---------------- analysis: one EPC2361 per switch ----------------",
              ".options plotwinsize=0",
              ".tran 0 {TEND} 0 0.1n",
              ".save V(QL_D_L) V(QL_S_L) V(QH_D_L) V(QH_S_L) V(gtLL) V(gtHL) I(VILL) I(VIHL) I(Lload)",
              ".meas TRAN Iload FIND I(VILL) AT {T1}",
              ".meas TRAN Eoff INTEG V(QL_D_L,QL_S_L)*I(VILL) FROM {T1} TO {T1+150n}",
              ".meas TRAN Eon INTEG V(QL_D_L,QL_S_L)*I(VILL) FROM {T2} TO {T2+150n}",
              ".meas TRAN VDSL_pk MAX V(QL_D_L,QL_S_L) FROM {T1} TO {T1+150n}",
              ".meas TRAN VDSH_pk MAX V(QH_D_L,QH_S_L) FROM {T2} TO {T2+150n}",
              ".meas TRAN VGSH_bump MAX V(gtHL,QH_S_L) FROM {T2} TO {T2+150n}",
              ".meas TRAN ID_pk MAX I(VILL) FROM {T2} TO {T2+150n}",
              ".meas TRAN t_on TRIG V(QL_D_L,QL_S_L) VAL={0.8*VBUS} FALL=1 TD={T2} TARG V(QL_D_L,QL_S_L) VAL={0.2*VBUS} FALL=1 TD={T2}",
              ".meas TRAN t_off TRIG V(QL_D_L,QL_S_L) VAL={0.2*VBUS} RISE=1 TD={T1} TARG V(QL_D_L,QL_S_L) VAL={0.8*VBUS} RISE=1 TD={T1}",
              ".meas TRAN dvdt_on PARAM 0.6*VBUS/t_on/1e9",
              ".meas TRAN dvdt_off PARAM 0.6*VBUS/t_off/1e9"]
    open(os.path.join(SP, "FLOW_single.inc"), "w").write("\n".join(lines) + "\n")
    open(os.path.join(SP, "FLOW_single.cir"), "w").write(
        "* One EPC2361 per switch with its own driver (left cell of the building block), Eon/Eoff vs current.\n"
        ".param VBUS=75 TON1=10.667u LLOAD={TON1*VBUS/IPK} RGON=2 RGOFF=0 RPU=0.6 RPD=0.2\n"
        ".step param IPK list 10 30 60 100 140 200 250 300\n"
        ".include FLOW_single.inc\n.end\n")
    return "FLOW_single.cir"


# ------------------------------------------------------------------------------------------------ lumped device
LUMPED = r"""* One EPC2361 per switch, first-cut lumped half bridge (no layout yet): the power loop is one inductance LLOOP
* (PCB copper + MLCC ESL), split between drain side and source side; L_CS in the low-side source is shared by the
* gate loop (Kelvin return at sK). Gate loop LG, per-device Rg_on / Rg_off, 4 A / 8 A driver (2EDF7275K typ.).
.include ../LMG1210-EPC2361/EPC2361.lib
.model DID D(Ron=1m Roff=1G Vfwd=0)
.param TSTART=0.5u TOFF=1u TON2=0.5u
.param T1={TSTART+TON1} T2={T1+TOFF} TEND={T2+TON2+0.3u}
.param VDRV=5 LG=1.7n LCS=0.03n CDC=10u RDC=1m

V1 VS 0 {VBUS}
Cbulk VS 0 1m Rser=20m
Lbus VS P 20n Rser=2m
Cdc P 0 {CDC} Rser={RDC}
Ld P P1 {LLOOP/2}
VIH P1 dH 0
XQH gH dH SW EPC2361
VIL SW dL 0
XQL gL dL sL EPC2361
Lcs sL sK {LCS}
Ls sK 0 {LLOOP/2-LCS}
Lload SW P {LLOAD} Rser=2m Cpar=20p

VLO lo sK PWL(0 0 {TSTART} 0 {TSTART+1n} {VDRV} {T1} {VDRV} {T1+1n} 0 {T2} 0 {T2+1n} {VDRV} {T2+TON2} {VDRV} {T2+TON2+1n} 0)
Rpul lo lo1 {RPU}
Dpul lo1 DOL DID
Dpdl DOL lo2 DID
Rpdl lo2 lo {RPD}
Lgl DOL gxl {LG}
Ronl gxl gl1 {RGON}
Donl gl1 gL DID
Doffl gL gl2 DID
Roffl gl2 gxl {RGOFF+1m}

VHO ho SW 0
Rpdh ho DOH {RPD}
Lgh DOH gxh {LG}
Ronh gxh gh1 {RGON}
Donh gh1 gH DID
Doffh gH gh2 DID
Roffh gh2 gxh {RGOFF+1m}

.options plotwinsize=0
.tran 0 {TEND} 0 0.1n
.save V(dL) V(sL) V(dH) V(SW) V(gL) V(gH) I(VIL) I(VIH) I(Lload)
.meas TRAN Iload FIND I(VIL) AT {T1}
.meas TRAN Eoff INTEG V(dL,sL)*I(VIL) FROM {T1} TO {T1+150n}
.meas TRAN Eon INTEG V(dL,sL)*I(VIL) FROM {T2} TO {T2+150n}
.meas TRAN VDSL_pk MAX V(dL,sL) FROM {T1} TO {T1+150n}
.meas TRAN VDSH_pk MAX V(dH,SW) FROM {T2} TO {T2+150n}
.meas TRAN VGSH_bump MAX V(gH,SW) FROM {T2} TO {T2+150n}
.meas TRAN didt_on MAX D(I(VIL)) FROM {T2} TO {T2+150n}
.meas TRAN didt_off MIN D(I(VIL)) FROM {T1} TO {T1+150n}
"""


def write_lumped():
    open(os.path.join(SP, "FLOW_lumped.inc"), "w").write(LUMPED)
    open(os.path.join(SP, "FLOW_lumped.cir"), "w").write(
        "* One EPC2361 per switch, lumped power loop LLOOP, Eon/Eoff and overshoot vs current per device.\n"
        ".param VBUS=75 TON1=10.667u LLOAD={TON1*VBUS/IPK} RGON=2 RGOFF=0 RPU=0.85 RPD=0.35\n"
        ".step param LLOOP list 0.3n 0.5n 0.8n\n"
        ".step param IPK list 10 40 80 120 160 200 250 330\n"
        ".include FLOW_lumped.inc\n.end\n")
    return "FLOW_lumped.cir"


# ------------------------------------------------------------------------------------------------ two blocks
def suffix_block(txt, k):
    """Flatten one copy of the building block: suffix element and node names with _k (ground 0 stays global)."""
    out = []
    for ln in element_lines(txt).splitlines():
        s = ln.strip()
        if not s or s[0] in "*." or s.startswith("+"):
            if s.startswith(".include") or s.startswith(".model") or s.startswith(".param"):
                if k == 1:
                    out.append(ln)
            continue
        tok = s.split()
        typ = tok[0][0].upper()
        if tok[0] in ("V1", "Cbulk", "Lbus", "Rret", "Lload"):
            continue                                     # DC bus and load are outside the blocks
        if typ == "X":
            nn = len(tok) - 2
        else:
            nn = 2
        new = [tok[0] + "_%d" % k]
        for t in tok[1:1 + nn]:
            new.append(t if t == "0" else t + "_%d" % k)
        rest = tok[1 + nn:]
        if typ == "V" and tok[0] == "VLO" and k == 2:
            # delay the low-side PWM of block 2 by DLY
            rest = [re.sub(r"\{([^}]*)\}", lambda m: "{%s+DLY}" % m.group(1) if m.group(1) != "VDRV" else m.group(0),
                           " ".join(rest))]
            rest = [rest[0].replace("PWL(0 0 ", "PWL(0 0 ")]
        new += rest
        out.append(" ".join(new))
    return out


def write_two():
    lines = ["* Two building blocks in parallel per leg (300 kW): shared DC bus, AC terminals joined through LX/2 each."]
    lines += suffix_block(BODY, 1) + suffix_block(BODY, 2)
    lines += ["* ---------------- shared DC bus and load ----------------",
              "V1 VS 0 {VBUS}", "Cbulk VS 0 1m Rser=20m", "Lbus VS DCB 20n Rser=2m",
              "Ld1 DCB T_DCP_1 {LXDC/2} Rser=0.1m", "Ld2 DCB T_DCP_2 {LXDC/2} Rser=0.1m",
              "Rret1 T_DCN_1 0 1u", "Rret2 T_DCN_2 0 1u",
              "La1 T_AC_1 ACO {LX/2} Rser={RX/2}", "La2 T_AC_2 ACO {LX/2} Rser={RX/2}",
              "Lload ACO DCB {LLOAD} Rser=2m Cpar=20p",
              "* ---------------- analysis ----------------",
              ".options plotwinsize=0",
              ".tran 0 {TEND} 0 0.1n",
              ".save I(La1) I(La2) I(Lload) V(T_AC_1) V(T_AC_2) V(QL_D_L_1) V(QL_S_L_1) V(QL_D_L_2) V(QL_S_L_2)"
              " I(VILL_1) I(VILR_1) I(VILL_2) I(VILR_2) V(QH_D_L_1) V(QH_S_L_1) V(QH_D_L_2) V(QH_S_L_2)"
              " V(QL_D_R_1) V(QL_S_R_1) V(QL_D_R_2) V(QL_S_R_2)",
              ".meas TRAN Iload FIND I(Lload) AT {T1}",
              ".meas TRAN I1_T1 FIND I(La1) AT {T1}",
              ".meas TRAN I2_T1 FIND I(La2) AT {T1}",
              ".meas TRAN I1_off FIND I(La1) AT {T1+200n}",
              ".meas TRAN I2_off FIND I(La2) AT {T1+200n}",
              ".meas TRAN I1_on FIND I(La1) AT {T2+200n}",
              ".meas TRAN I2_on FIND I(La2) AT {T2+200n}",
              ".meas TRAN I1_onpk MAX I(La1) FROM {T2} TO {T2+200n}",
              ".meas TRAN I2_onpk MAX I(La2) FROM {T2} TO {T2+200n}",
              ".meas TRAN Eoff1 INTEG V(QL_D_L_1,QL_S_L_1)*I(VILL_1)+V(QL_D_R_1,QL_S_R_1)*I(VILR_1) FROM {T1} TO {T1+160n}",
              ".meas TRAN Eoff2 INTEG V(QL_D_L_2,QL_S_L_2)*I(VILL_2)+V(QL_D_R_2,QL_S_R_2)*I(VILR_2) FROM {T1} TO {T1+160n}",
              ".meas TRAN Eon1 INTEG V(QL_D_L_1,QL_S_L_1)*I(VILL_1)+V(QL_D_R_1,QL_S_R_1)*I(VILR_1) FROM {T2} TO {T2+160n}",
              ".meas TRAN Eon2 INTEG V(QL_D_L_2,QL_S_L_2)*I(VILL_2)+V(QL_D_R_2,QL_S_R_2)*I(VILR_2) FROM {T2} TO {T2+160n}",
              ".meas TRAN VDSL1_pk MAX V(QL_D_L_1,QL_S_L_1) FROM {T1} TO {T1+160n}",
              ".meas TRAN VDSL2_pk MAX V(QL_D_L_2,QL_S_L_2) FROM {T1} TO {T1+160n}"]
    open(os.path.join(SP, "FLOW_two.inc"), "w").write("\n".join(lines) + "\n")
    open(os.path.join(SP, "FLOW_two.cir"), "w").write(
        "* Two building blocks in parallel, driver skew DLY on block 2, AC interconnect LX (RX), DC interconnect LXDC.\n"
        "* IPK=330 gives ~322 A at T1 (300 kW, M = 1.15, cos phi = 0.9: 228 A_rms per leg)\n"
        ".param VBUS=75 IPK=330 TON1=10.667u LLOAD={TON1*VBUS/IPK} RGON=2 RGOFF=0 RPU=0.6 RPD=0.2\n"
        ".param LXDC=5n RX=0.2m\n"
        ".step param LX list 5n 20n\n"
        ".step param DLY list 0 2n 5n\n"
        ".include FLOW_two.inc\n.end\n")
    return "FLOW_two.cir"


def run(cir):
    print("running", cir)
    subprocess.run([LTS, "-b", os.path.join(SP, cir)], cwd=SP, check=False, timeout=7200)


def parse():
    res = {}
    for tag in ("single", "lumped", "two"):
        log = os.path.join(SP, "FLOW_%s.log" % tag)
        if os.path.exists(log):
            m, st = parse_log(log)
            res[tag] = dict(meas=m, steps=st)
    os.makedirs(OUTD, exist_ok=True)
    json.dump(res, open(os.path.join(OUTD, "flow_spice.json"), "w"), indent=1)
    for tag, r in res.items():
        print(tag, {k: [round(v, 9 if abs(v) < 1e-3 else 2) for v in vals] for k, vals in r["meas"].items()})
        print(" steps", r["steps"])


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("single", "all"):
        run(write_single())
    if what in ("lumped", "all"):
        run(write_lumped())
    if what in ("two", "all"):
        run(write_two())
    parse()

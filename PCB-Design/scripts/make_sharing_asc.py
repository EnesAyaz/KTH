"""
Generate simulation/sharing/Sharing_2xEPC2361.asc: a basic, fully wired LTspice schematic
for current sharing between two parallel EPC2361s (low-side double-pulse test).

    python scripts/make_sharing_asc.py

Knobs (per branch k = 1, 2): LDk drain / power-loop inductance, LSk source inductance,
LGk gate-loop inductance, RGk gate resistance, DVTHk threshold offset; KELVIN = 1 returns the
driver at the die source (LS only in the power loop), KELVIN = 0 returns it after LS
(LS becomes common-source inductance). CASE steps through one-change-at-a-time scenarios.
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "simulation", "sharing")

PINS = {  # R0 pin offsets in SpiceOrder
    "res": [(16, 16), (16, 96)],
    "ind": [(16, 16), (16, 96)],
    "voltage": [(0, 16), (0, 96)],
    "EPC2361": [(0, 48), (96, 0), (96, 96)],
}

lines = ["Version 4", "SHEET 1 1600 1000"]
wires, flags, syms, texts = [], [], [], []


def place(sym, name, value, x, y, rot="R0", window=True, spiceline=None):
    """Place a symbol; returns absolute pin coordinates in SpiceOrder."""
    pins = []
    for px, py in PINS[sym]:
        pins.append((x + px, y + py) if rot == "R0" else (x - py, y + px))   # R90
    syms.append("SYMBOL %s %d %d %s" % (sym, x, y, rot))
    if window and sym in ("res", "ind"):
        if rot == "R90":
            syms.extend(["WINDOW 0 0 56 VBottom 2", "WINDOW 3 32 56 VTop 2"])
        else:
            syms.extend(["WINDOW 0 36 40 Left 2", "WINDOW 3 36 72 Left 2"])
    syms.append("SYMATTR InstName %s" % name)
    syms.append("SYMATTR Value %s" % value)
    if spiceline:
        syms.append("SYMATTR SpiceLine %s" % spiceline)
    return pins


def wire(*pts):
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        wires.append("WIRE %d %d %d %d" % (x1, y1, x2, y2))


def flag(p, net):
    flags.append("FLAG %d %d %s" % (p[0], p[1], net))


def text(x, y, s, size=2, directive=False):
    texts.append("TEXT %d %d Left %d %s%s" % (x, y, size, "!" if directive else ";", s))


# ---------------- bus, common loop, high side, load ----------------
v1 = place("voltage", "Vbus", "{VBUS}", 64, 160)
flag(v1[1], "0")
lloop = place("ind", "Lloop", "{LLOOP}", 272, 80, "R90", spiceline="Rser={RLOOP}")  # right (256,96), left (176,96)
wire(v1[0], (64, 96), lloop[1])
qh = place("EPC2361", "QH", "EPC2361", 256, 96)                 # gate (256,144) drain (352,96) source (352,192)
wire(lloop[0], qh[1])
flag(qh[1], "DH")
rgh = place("res", "Rgh", "1", 240, 128, window=False)          # (256,144) - (256,224): holds QH off
wire(rgh[1], (352, 224))
lload = place("ind", "Lload", "{LLOAD}", 448, 96)              # (464,112) - (464,192)
wire(qh[1], (464, 96), lload[0])
wire(lload[1], (464, 224), (352, 224))
wire(qh[2], (352, 224), (352, 288))
flag((352, 288), "SW")

# ---------------- two parallel low-side branches ----------------
BX = {1: 640, 2: 1120}
for k, bx in BX.items():
    wire((352 if k == 1 else BX[1], 288), (bx, 288))
    ld = place("ind", "LD%d" % k, "{LD%d}" % k, bx - 16, 288)        # (bx,304) - (bx,384)
    wire((bx, 288), ld[0])
    q = place("EPC2361", "QL%d" % k, "EPC2361", bx - 96, 384)       # gate (bx-96,432) drain (bx,384) source (bx,480)
    flag(q[1], "D%d" % k)
    flag(q[0], "G%d" % k)
    flag(q[2], "S%d" % k)
    ls = place("ind", "LS%d" % k, "{LS%d}" % k, bx - 16, 480)        # (bx,496) - (bx,576)
    wire(q[2], ls[0])
    flag(ls[1], "0")
    lg = place("ind", "LG%d" % k, "{LG%d}" % k, bx - 96, 416, "R90")  # (bx-112,432) - (bx-192,432)
    wire(lg[0], q[0])
    rg = place("res", "RG%d" % k, "{RG%d}" % k, bx - 192, 416, "R90")  # (bx-208,432) - (bx-288,432)
    wire(rg[0], lg[1])
    vth = place("voltage", "VTH%d" % k, "{-DVTH%d}" % k, bx - 272, 432, "R90")  # + (bx-288,432), - (bx-368,432)
    wire(vth[0], rg[1])
    flag(vth[1], "DRV")
    rk = place("res", "RK%d" % k, "{if(KELVIN,RKS,1G)}", bx + 48, 464)   # Kelvin return: (bx+64,480)-(bx+64,560)
    wire(q[2], (bx + 64, 480))
    flag(rk[1], "KRET")

# ---------------- gate driver ----------------
vg = place("voltage", "Vdrv", "PULSE(0 {VDRV} {TSTART} 1n 1n {TON1} {TON1+TOFF})", 96, 640)
flag(vg[0], "DRV")
flag(vg[1], "KRET")
rp = place("res", "Rp", "{if(KELVIN,1G,1m)}", 240, 720)         # non-Kelvin return to power ground
flag(rp[0], "KRET")
flag(rp[1], "0")

# ---------------- directives ----------------
D = [
    ".param VBUS=75 IPK=120 LLOAD=5u VDRV=5",
    ".param TSTART=0.5u TON1={LLOAD*IPK/VBUS} TOFF=1u TON2=0.5u",
    ".param T1={TSTART+TON1} T2={T1+TOFF}",
    "* baseline close to the Q3D board (~0.2 nH effective loop, 8 mohm at 100 MHz); case steps follow AN020 / the paralleling paper",
    ".param LLOOP=0.1n RLOOP=8m RKS=0.1",
    ".param LD1=0.15n LD2={if(CASE==1,0.45n,0.15n)}",
    ".param LG1=2n LG2={if(CASE==2,8n,2n)}",
    ".param LS1=0.05n LS2={if(CASE==4,0.25n,0.05n)}",
    ".param KELVIN={if(CASE==3|CASE==4,0,1)}",
    ".param RG1=2 RG2=2 DVTH1=0 DVTH2={if(CASE==5,0.3,0)}",
    ".step param CASE list 0 1 2 3 4 5",
    ".include ../LMG1210-EPC2361/EPC2361.lib",
    ".tran 0 {T2+TON2+0.5u} 0 0.1n",
    ".options plotwinsize=0",
    ".meas TRAN I1_off FIND I(LD1) AT {T1}",
    ".meas TRAN I2_off FIND I(LD2) AT {T1}",
    ".meas TRAN I1_pk MAX I(LD1) FROM {T2} TO {T2+100n}",
    ".meas TRAN I2_pk MAX I(LD2) FROM {T2} TO {T2+100n}",
    ".meas TRAN Eon1 INTEG V(D1,S1)*I(LD1) FROM {T2} TO {T2+100n}",
    ".meas TRAN Eon2 INTEG V(D2,S2)*I(LD2) FROM {T2} TO {T2+100n}",
    ".meas TRAN Eoff1 INTEG V(D1,S1)*I(LD1) FROM {T1} TO {T1+100n}",
    ".meas TRAN Eoff2 INTEG V(D2,S2)*I(LD2) FROM {T1} TO {T1+100n}",
    ".meas TRAN VDS_pk MAX V(D1) FROM {T1} TO {T1+100n}",
    ".meas TRAN VDSH_pk MAX V(DH,SW) FROM {T2} TO {T2+100n}",
    ".meas TRAN Idiff_on PARAM (I1_pk-I2_pk)/(I1_pk+I2_pk)",
    ".meas TRAN Ediff_on PARAM (Eon1-Eon2)/(Eon1+Eon2)",
]
ty = 640
for d in D:
    if d.startswith("*"):
        text(640, ty, d[1:].strip())
    else:
        text(640, ty, d, directive=True)
    ty += 24
text(16, 16, "Two parallel EPC2361: current sharing vs power-loop (LD), source / common-source (LS), "
             "gate-loop (LG) inductance and Vth mismatch", 3)
text(16, 48, "CASE 0 baseline | 1 LD2 +0.3 nH (power loop) | 2 LG2 2->8 nH (gate loop) | 3 no Kelvin (LS = CSI) | "
             "4 no Kelvin + LS2 +0.2 nH (CSI imbalance) | 5 Vth2 +0.3 V", 2)
text(16, 880, "Plot: I(LD1), I(LD2) drain currents | V(D1,S1) | V(G1,S1), V(G2,S2) | V(DH,SW). "
              "Low-side DPT: Vdrv pulses QL1+QL2 twice; QH is held off by Rgh.", 2)
text(16, 904, "KELVIN=1: driver returns at the die sources through RK1/RK2 (LS only in the power loop). "
              "KELVIN=0: driver returns at power ground through Rp (LS shared = common-source inductance).", 2)

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "Sharing_2xEPC2361.asc"), "w", newline="\n") as f:
    f.write("\n".join(lines + wires + flags + syms + texts) + "\n")
shutil.copy(os.path.join(ROOT, "simulation", "LMG1210-EPC2361", "EPC2361.asy"),
            os.path.join(OUT, "EPC2361.asy"))
print("wrote", os.path.join(OUT, "Sharing_2xEPC2361.asc"))

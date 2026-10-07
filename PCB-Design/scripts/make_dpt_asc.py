"""
Generate an LTspice schematic (.asc) + symbols from simulation/dpt/DPT_PL_A.cir.

    python scripts/make_dpt_asc.py

Every element of the netlist becomes a symbol (R, L, C, V, D, X) with a net-label
flag on each pin, grouped by the netlist's "* ---- section ----" comments; every
dot-directive becomes a SPICE directive on the sheet. The netlist stays the single
source of truth: edit DPT_PL_A.cir, then rerun this script.
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DPT = os.path.join(ROOT, "simulation", "dpt")
CIR = os.path.join(DPT, "DPT_PL_A.cir")

# symbol -> pin offsets (R0) in SpiceOrder, from the LTspice built-in / project symbols
PINS = {
    "res": [(16, 16), (16, 96)],
    "ind": [(16, 16), (16, 96)],
    "cap": [(16, 0), (16, 64)],
    "voltage": [(0, 16), (0, 96)],
    "diode": [(16, 0), (16, 64)],
    "EPC2361": [(0, 48), (96, 0), (96, 96)],
    "PL_A": [(0, 160), (0, 32), (224, 32), (224, 80), (224, 128), (224, 176)],
}
SYM = {"R": "res", "L": "ind", "C": "cap", "V": "voltage", "D": "diode"}

PL_A_ASY = """Version 4
SymbolType BLOCK
RECTANGLE Normal 0 0 224 208
TEXT 112 92 Center 2 PL_A
TEXT 112 116 Center 1 Q3D copper matrix
TEXT 8 32 Left 1 CapP
TEXT 8 160 Left 1 CapN
TEXT 216 32 Right 1 QH_D
TEXT 216 80 Right 1 QH_S
TEXT 216 128 Right 1 QL_D
TEXT 216 176 Right 1 QL_S
WINDOW 0 112 -16 Center 2
SYMATTR Prefix X
SYMATTR Value PL_A
SYMATTR Description Q3D PL_A copper partial R/L + K matrix (../q3d/results/PL_A.lib)
PIN 0 160 NONE 0
PINATTR PinName CapN
PINATTR SpiceOrder 1
PIN 0 32 NONE 0
PINATTR PinName CapP
PINATTR SpiceOrder 2
PIN 224 32 NONE 0
PINATTR PinName QH_D
PINATTR SpiceOrder 3
PIN 224 80 NONE 0
PINATTR PinName QH_S
PINATTR SpiceOrder 4
PIN 224 128 NONE 0
PINATTR PinName QL_D
PINATTR SpiceOrder 5
PIN 224 176 NONE 0
PINATTR PinName QL_S
PINATTR SpiceOrder 6
"""


def parse(path):
    sections, directives, notes = [], [], []
    current = ("misc", [])
    sections.append(current)
    for raw in open(path, encoding="ascii", errors="replace"):
        line = raw.rstrip("\n")
        s = line.strip()
        if not s:
            continue
        m = re.match(r"\*\s*-+\s*(.*?)\s*-+\s*$", s)
        if m:
            current = (m.group(1), [])
            sections.append(current)
        elif s.startswith("*"):
            notes.append(s)
        elif s.startswith("."):
            if s.lower() != ".end":
                directives.append(s)
        else:
            current[1].append(s.split())
    return [x for x in sections if x[1]], directives, notes


def element(tok):
    """-> (symbol, instname, nets, value, spiceline)"""
    name = tok[0]
    kind = name[0].upper()
    if kind == "X":
        model = tok[-1]
        return model, name, tok[1:-1], model, ""
    nets = tok[1:3]
    rest = tok[3:]
    if kind in "LC":
        value = rest[0]
        extra = " ".join(rest[1:])
        return SYM[kind], name, nets, value, extra
    return SYM[kind], name, nets, " ".join(rest), ""


def main():
    sections, directives, notes = parse(CIR)
    out = ["Version 4", "SHEET 1 3600 2600"]
    flags, syms, texts = [], [], []
    y0 = 96
    for title, elems in sections:
        texts.append("TEXT 48 %d Left 3 ;%s" % (y0 - 40, title))
        x, y = 64, y0 + 48
        row_h = 0
        for tok in elems:
            sym, name, nets, value, extra = element(tok)
            w = 352 if sym == "PL_A" else (224 if sym == "EPC2361" else 176)
            h = 256 if sym == "PL_A" else 176
            if x + w > 2150:          # directives start at x = 2240
                x, y = 64, y + row_h
                row_h = 0
            syms.append("SYMBOL %s %d %d R0" % (sym, x, y))
            if sym in ("res", "ind", "cap", "diode"):
                syms.append("WINDOW 0 36 32 Left 2")
                syms.append("WINDOW 3 36 64 Left 2")
            # LTspice prepends the X prefix to subcircuit instances itself
            inst = name[1:] if name[0].upper() == "X" else name
            syms.append("SYMATTR InstName %s" % inst)
            syms.append("SYMATTR Value %s" % value)
            if extra:
                syms.append("SYMATTR SpiceLine %s" % extra)
            for (px, py), net in zip(PINS[sym], nets):
                flags.append("FLAG %d %d %s" % (x + px, y + py, net))
            x += w
            row_h = max(row_h, h)
        y0 = y + row_h + 96
    # notes and directives on the right-hand side, one per line
    ty = 64
    for n in notes:
        texts.append("TEXT 2240 %d Left 2 ;%s" % (ty, n.lstrip("* ").replace("\\", "/")))
        ty += 32
    ty += 32
    for d in directives:
        texts.append("TEXT 2240 %d Left 2 !%s" % (ty, d))
        ty += 32
    # two different nets on one coordinate would silently short them
    seen = {}
    for fl in flags:
        _, fx, fy, net = fl.split()
        if seen.setdefault((fx, fy), net) != net:
            raise SystemExit("net clash at %s,%s: %s / %s" % (fx, fy, seen[(fx, fy)], net))
    out += flags + syms + texts
    with open(os.path.join(DPT, "DPT_PL_A.asc"), "w", encoding="ascii", errors="replace", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    with open(os.path.join(DPT, "PL_A.asy"), "w", newline="\n") as f:
        f.write(PL_A_ASY)
    shutil.copy(os.path.join(ROOT, "simulation", "LMG1210-EPC2361", "EPC2361.asy"), os.path.join(DPT, "EPC2361.asy"))
    print("wrote DPT_PL_A.asc, PL_A.asy, EPC2361.asy in", DPT)


if __name__ == "__main__":
    main()

"""
M1(c): geometry export for the L_x extraction of the committed DPT board with the DC side: the model region is extended down to the
DC terminal row (y = -25), the 2220 bank parts stay in as terminal groups (BankP_g / BankN_g, g = nearest cell or C for |x| <= 6) and
the DC terminals J1 / J2 (J_DCP, J_DCN) and the AC bolt (J_AC) are source terminals. Sinks as in the lx model (CapP_1, CapN_1, QH_S_1).
Runs simulation/bb_q3d/revb_export.py with in-memory edits only (the file on disk is not changed). Tag dpt_swv1dc -> BB_PL_LX_dpt_swv1dc.
"""
import os

P = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "bb_q3d", "revb_export.py"))
src = open(P, encoding="utf-8").read()
EDITS = (
    ('"lx": (-46.0, -4.6, 46.0, 61.2)', '"lx": (-46.0, -25.0, 46.0, 61.2)'),
    ('if CROP and not local and not BANK:', 'if CROP and not local and not BANK and REGION != "lx":'),
    ('(not CROP or (BANK and f.GetValue() != "AC"))', '(not CROP or (BANK and f.GetValue() != "AC") or REGION == "lx")'),
)
for a, b in EDITS:
    assert src.count(a) == 1, a
    src = src.replace(a, b)
__file__ = P
exec(compile(src, P, "exec"))

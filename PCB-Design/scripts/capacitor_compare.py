"""
DC-link capacitor comparison at 75 V DC bias, from manufacturer characteristic data (read 2026-10-14 from
product.tdk.com and pim.murata.com chart data), and the part count per leg board for a ripple target.

    C:\\Github\\KTH\\LossCalculation-SPB\\.venv\\Scripts\\python.exe scripts\\capacitor_compare.py
      -> reports/slides/data/capacitor_compare.json (uses dclink_sizing.json for the charge per period)
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SZ = json.load(open(os.path.join(ROOT, "reports", "slides", "data", "dclink_sizing.json")))
V = 75.0
DQ = {50: 859.61e-6, 75: 573.07e-6, 100: 429.81e-6}       # charge excursion per level (dclink_sizing.py)
I_LEG = 84.9 / 3                                          # ripple current per leg board (A rms)
# part, size, (L, W, T) mm, nominal F, effective F at 75 V, ESR at 50 kHz (Ohm), I for +10 K at 100 kHz (A), status
PARTS = [
    ("Murata GRM32EC72A106KE05", "1210", (3.2, 2.5, 2.5), 10e-6, 1.50e-6, None, None, "production (only 100 V 1210)"),
    ("TDK C3225X7S2A475K200AB", "1210", (3.2, 2.5, 2.0), 4.7e-6, 0.915e-6, 12.3e-3, 1.83, "production"),
    ("TDK C4532X7S2A475K230KB", "1812", (4.5, 3.2, 2.3), 4.7e-6, 1.10e-6, 13.1e-3, 1.81, "production"),
    ("TDK C5750X7S2A106K230KB", "2220", (5.7, 5.0, 2.3), 10e-6, 2.45e-6, 6.4e-3, 3.04, "production"),
    ("TDK C5750X7S2A156M250KB", "2220", (5.7, 5.0, 2.5), 15e-6, 3.80e-6, 3.6e-3, 3.6, "production"),
    ("TDK C5750X7S2A226M280KB", "2220", (5.7, 5.0, 2.8), 22e-6, 6.35e-6, 2.8e-3, 4.45, "production"),
]
BYPASS = dict(part="TDK C2012X7S2A105K125AB (0805 1 uF)", C_eff=0.178e-6, per_leg=24)
c_byp = BYPASS["C_eff"] * BYPASS["per_leg"]
out = dict(V=V, I_ripple_leg=I_LEG, bypass=dict(BYPASS, C_eff_leg=c_byp), parts=[])
print("bypass: 24 x %.2f uF eff = %.1f uF per leg (6 per cell = %.2f uF eff per cell)" % (
    BYPASS["C_eff"] * 1e6, c_byp * 1e6, 6 * BYPASS["C_eff"] * 1e6))
for name, size, (L, W, T), cn, ce, esr, i10, st in PARTS:
    row = dict(part=name, size=size, L=L, W=W, T=T, C_nom_uF=cn * 1e6, C_eff_uF=ce * 1e6, retention=ce / cn,
               ESR50k_mOhm=None if esr is None else esr * 1e3, I_10K_A=i10, status=st,
               uF_eff_per_mm2=ce * 1e6 / (L * W))
    for f in (50, 100):
        for pct in (2, 3):
            c_leg = DQ[f] / (pct / 100 * V) / 3
            n = math.ceil(max(0.0, c_leg - c_byp) / ce)
            row["n_%dkHz_%dpct" % (f, pct)] = n
            row["area_%dkHz_%dpct_mm2" % (f, pct)] = round(n * L * W)
            row["I_part_%dkHz_%dpct" % (f, pct)] = round(I_LEG / n, 2) if n else None
    out["parts"].append(row)
    print("%-26s %s  %4.1f uF -> %4.2f uF (%2.0f %%), %5.3f uF/mm2 | 50 kHz 3 %%: %3d parts %4d mm2, "
          "2 %%: %3d | 100 kHz 3 %%: %3d" % (name, size, cn * 1e6, ce * 1e6, 100 * ce / cn, ce * 1e6 / (L * W),
                                              row["n_50kHz_3pct"], row["area_50kHz_3pct_mm2"], row["n_50kHz_2pct"],
                                              row["n_100kHz_3pct"]))
json.dump(out, open(os.path.join(ROOT, "reports", "slides", "data", "capacitor_compare.json"), "w"), indent=1)

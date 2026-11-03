import json, os, sys, math
import numpy as np
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
def block(lines, title):
    for i, l in enumerate(lines):
        if l.strip() == title:
            names = lines[i + 1].split()
            return names, np.array([[float(v) for v in r.split()[1:]] for r in lines[i + 2:i + 2 + len(names)]])
    return None, None
w = 2 * math.pi * 100e6
out = {}
for tag in sys.argv[1:]:
    p = os.path.join(RES, "BB_PL_SWAC_%s_matrix.txt" % tag)
    if not os.path.exists(p):
        continue
    L = open(p).read().splitlines()
    n, Rdc = block(L, "DC Resistance Matrix"); _, Rac = block(L, "AC Resistance Matrix"); _, Lac = block(L, "AC Inductance Matrix")
    one = np.ones(len(n))
    r = {"terminals": n, "matrix": L[0].strip(),
         "Rdc_tied_mOhm": round(float(1 / (one @ np.linalg.inv(Rdc) @ one)) * 1e3, 4),
         "Rdc_diag_mOhm": [round(float(v) * 1e3, 4) for v in np.diag(Rdc)]}
    if Lac is not None:
        Z = Rac + 1j * w * Lac * 1e-9
        Zt = 1 / (one @ np.linalg.inv(Z) @ one)
        r.update({"Lac100MHz_tied_nH": round(float(Zt.imag / w * 1e9), 4), "Rac100MHz_tied_mOhm": round(float(Zt.real) * 1e3, 4),
                  "Lac_diag_nH": [round(float(v), 4) for v in np.diag(Lac)]})
    out[tag] = r
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(RES, "swac_summary.json"), "w"), indent=1)

import numpy as np, time, sys
import spb_core as c, wrsm_model as w
gs = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
w.GS["v"] = gs
tag = "" if gs == 1.0 else f"_gs{gs:g}"
ID = np.linspace(-450, 60, 12); IQ = np.linspace(0, 450, 10); IF = np.array([0, .2, .4, .6, .8, 1.0])
for mode in ("2p8", "2p4"):
    t = time.time()
    out = np.zeros((len(ID), len(IQ), len(IF), 4))
    for a, idv in enumerate(ID):
        for b, iqv in enumerate(IQ):
            U = None
            for f, ifv in enumerate(IF):
                pd, pq, r = w.solve_point(mode, idv, iqv, ifv, U)
                U = r["U"]
                out[a, b, f] = (pd, pq, r["Bt"].max(), r["By"].max())
    np.savez(f"scratch/wrsm_map_{mode}{tag}.npz", ID=ID, IQ=IQ, IF=IF, out=out)
    print(mode, time.time() - t, flush=True)

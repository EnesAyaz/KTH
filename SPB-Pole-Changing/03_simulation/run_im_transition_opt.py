"""Small parameter search over the handover schedule (minimise torque deficit, I_rms <= I_max) and final JSON."""
import json, itertools, datetime
import numpy as np
import run_im_transition as r
import spb_core as c

out = json.load(open("results/im_pole_transition.json"))
best = {}
allc = []
for grade in (0.0, 0.02):
    Tld = r.road_torque(2100.0, grade)
    cand = []
    for t_d, t_f4, t_f2 in itertools.product((0.02, 0.1, 0.25), (0.02, 0.06, 0.15), (0.03, 0.08, 0.15)):
        o = r.simulate(Tld, grade, t_end=1.3, dt=2e-4, t_d=t_d, t_f4=t_f4, t_f2=t_f2, label=f"search td={t_d} tf4={t_f4} tf2={t_f2}")
        if o is None:
            continue
        res, ser = o
        cand.append(res)
        allc.append(res)
    ok = [x for x in cand if x["I_rms_peak_over_Imax"] <= 1.005]
    b = min(ok, key=lambda x: x["torque_deficit_Nms"])
    best[f"grade_{grade*100:.0f}pct"] = b
    print(grade, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in b.items() if k not in ("ss_before", "ss_after")}, flush=True)
    res, ser = r.simulate(Tld, grade, t_end=1.3, dt=2e-4, **b["params"], label="best")
    np.savez(f"scratch/im_transition_best_g{grade*100:.0f}.npz", **{k: np.array(v) for k, v in ser.items()})
out["best_schedule"] = best
out["search_all"] = allc
out["meta"]["search"] = "grid t_d {0.02,0.1,0.25} x t_f4 {0.02,0.06,0.15} x t_f2 {0.03,0.08,0.15}; objective: min torque deficit with I_rms <= I_max"
json.dump(out, open("results/im_pole_transition.json", "w"), indent=1, default=float)

"""schedule search (dq model only): which overlapped handover keeps the torque >= 90 % of the request on flat road / 2 % grade"""
import os, json, itertools
import spb_core as c, run_im_transition as r
c.CAP_MODE["mode"] = "an_caps"
out = {}
for grade in (0.0, 0.02):
    T = r.road_torque(2100.0, grade)
    cand = []
    for td, tf4, tf2 in itertools.product((0.1, 0.25, 0.4, 0.6), (0.03, 0.06, 0.1, 0.15), (0.15, 0.3, 0.45, 0.6)):
        res, _ = r.simulate(T, grade, t_end=1.3, dt=2e-4, t_d=td, t_f4=tf4, t_f2=tf2)
        cand.append(dict(min_over_request=res["torque_min_Nm"] / res["T_req_Nm"], I_over_Imax=res["I_rms_peak_over_Imax"], gap90=res["torque_gap_below90pct_s"], params=dict(t_d=td, t_f4=tf4, t_f2=tf2)))
    cand.sort(key=lambda x: -x["min_over_request"])
    out[f"grade_{grade*100:.0f}pct"] = cand[:6]
    print(grade, [(round(x["min_over_request"], 3), x["params"]) for x in cand[:3]], flush=True)
json.dump(out, open(f"results/h10_schedule_search_Q{c.Q}.json", "w"), indent=1)

"""CLI entry point: python scripts/run_design.py config/design_spec.yaml [--lookup]

Runs the fsw-vs-N-parallel design sweep and writes a Markdown report to outputs/.
Uses the analytical switching-loss model unless --lookup is given, which loads
outputs/EPC2361_eon_sweep.csv and outputs/EPC2361_eoff_sweep.csv (the LTSpice-calibrated,
decoupled Rg_on/Rg_off sweep -- see scripts/run_epc2361_sweep_v2.py).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spb_bb.devices import load_device
from spb_bb.loop_inductance import estimate_loop_inductance
from spb_bb.optimize import DesignSpec, design_sweep_over_n
from spb_bb.report import format_design_report, save_report
from spb_bb.switching_loss import SwitchingLossModel
from spb_bb.ltspice.lookup import build_eon_interpolator, build_eoff_interpolator, load_sweep_csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="path to design_spec.yaml")
    parser.add_argument("--lookup", action="store_true", help="use the LTSpice-calibrated sweep data")
    parser.add_argument("--eon-csv", default="outputs/EPC2361_eon_sweep.csv")
    parser.add_argument("--eoff-csv", default="outputs/EPC2361_eoff_sweep.csv")
    parser.add_argument("--l-loop-nH", type=float, default=None, help="override the design L_loop (nH)")
    parser.add_argument("--out", default="outputs/design_report.md")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    device = load_device(cfg["device"])

    loop_l = estimate_loop_inductance(
        cfg["layout"]["loop_inductance_method"],
        cfg["layout"]["loop_length_mm"],
        cfg["layout"]["loop_width_mm"],
        cfg["layout"]["loop_h_or_s_mm"],
    )
    print(f"Estimated power-loop inductance: {loop_l * 1e9:.2f} nH")
    l_loop_nH = args.l_loop_nH if args.l_loop_nH is not None else loop_l * 1e9

    spec = DesignSpec(
        p_out_leg=cfg["power"]["p_out_leg_W"],
        v_dc=cfg["power"]["v_dc_V"],
        v_rms_fund=cfg["power"]["v_rms_fund_V"],
        power_factor=cfg["power"]["power_factor"],
        modulation_index=cfg["power"]["modulation_index"],
        efficiency_target=cfg["targets"]["efficiency_full_load"],
        t_dead=cfg["timing"]["dead_time_ns"] * 1e-9,
        t_ambient_c=cfg["thermal"]["t_ambient_C"],
        r_th_interface=cfg["thermal"]["r_th_interface_C_per_W"],
        r_th_sink_amb=cfg["thermal"]["r_th_sink_amb_C_per_W"],
        l_loop_nH=l_loop_nH,
        t_j_ceiling_c=cfg["targets"]["t_j_ceiling_C"],
        v_overshoot_max_frac=cfg["targets"]["v_overshoot_max_frac"],
        svm=(cfg["power"]["modulation_scheme"].upper() == "SVM"),
    )

    if args.lookup:
        eon_rows = load_sweep_csv(args.eon_csv)
        eoff_rows = load_sweep_csv(args.eoff_csv)
        sw_model = SwitchingLossModel(
            device,
            mode="lookup",
            eon_lookup_fn=build_eon_interpolator(eon_rows),
            eoff_lookup_fn=build_eoff_interpolator(eoff_rows),
        )
        print(f"Using LTSpice-calibrated lookup data at L_loop={l_loop_nH:.2f} nH")
    else:
        print(
            "WARNING: --lookup not given, using the coarse analytical switching-loss "
            "model. Overshoot-constrained Rg_off search is unavailable in this mode; "
            "run scripts/run_epc2361_sweep_v2.py for a real answer."
        )
        sw_model = SwitchingLossModel(device, mode="analytical")

    n_range = range(1, cfg["search"]["n_parallel_max"] + 1)
    rg_on_bounds = (cfg["search"]["rg_on_min_ohm"], cfg["search"]["rg_on_max_ohm"])
    rg_off_bounds = (cfg["search"]["rg_off_min_ohm"], cfg["search"]["rg_off_max_ohm"])
    fsw_bounds = (cfg["search"]["fsw_min_Hz"], cfg["search"]["fsw_max_Hz"])

    results = design_sweep_over_n(
        device,
        spec,
        sw_model,
        n_range=n_range,
        rg_on_bounds=rg_on_bounds,
        rg_off_bounds=rg_off_bounds,
        fsw_bounds=fsw_bounds,
        l_loop_nH=l_loop_nH,
    )

    report = format_design_report(device, spec, results)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    save_report(report, args.out)
    print(f"Report written to {args.out}")
    print(report)


if __name__ == "__main__":
    main()

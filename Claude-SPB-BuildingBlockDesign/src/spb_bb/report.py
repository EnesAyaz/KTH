"""Renders DesignPointResult / design_sweep_over_n output as a Markdown report."""

from __future__ import annotations

from datetime import datetime

from .devices import GaNDevice
from .optimize import DesignPointResult, DesignSpec


def format_design_report(
    device: GaNDevice,
    spec: DesignSpec,
    results: list[DesignPointResult],
    title: str = "Half-Bridge Building Block Design Report",
) -> str:
    lines = []
    lines.append(f"# {title}")
    lines.append(f"_Generated {datetime.now().isoformat(timespec='seconds')}_")
    lines.append("")
    lines.append("## Device")
    lines.append(f"- Part: **{device.part_number}** ({device.manufacturer})")
    lines.append(f"- V_ds,max: {device.v_ds_max:.0f} V, T_j,max: {device.t_j_max:.0f} C")
    lines.append(f"- R_ds_on @25C: {device.r_ds_on_25c * 1e3:.2f} mOhm")
    lines.append(f"- Source file: `{device.source_file}`")
    lines.append("")
    lines.append("## Design spec")
    lines.append(f"- P_out (this leg): {spec.p_out_leg:.1f} W")
    lines.append(f"- V_dc: {spec.v_dc:.1f} V, V_rms,fund: {spec.v_rms_fund:.1f} V")
    lines.append(f"- Power factor: {spec.power_factor:.3f}, Modulation index: {spec.modulation_index:.3f}")
    lines.append(f"- Efficiency target (full load): {spec.efficiency_target * 100:.2f} %")
    lines.append(f"- Dead time: {spec.t_dead * 1e9:.0f} ns")
    lines.append(f"- Max Vds overshoot: {spec.v_overshoot_max_frac * 100:.0f} % of Vdc")
    lines.append(f"- L_loop: {spec.l_loop_nH:.2f} nH")
    lines.append(f"- T_ambient: {spec.t_ambient_c:.1f} C, T_j ceiling: {spec.t_j_ceiling_c:.1f} C")
    lines.append("")
    lines.append("## f_sw vs. parallel-device-count trade-off")
    lines.append("")
    lines.append(
        "| N parallel | Rg_on (ohm) | Rg_off (ohm) | Max f_sw (kHz) | P_cond (W) | P_sw (W) | "
        "P_total (W) | Budget (W) | Tj (C) | Margin (C) | Vds overshoot (V) | Feasible |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        overshoot_str = f"{r.v_ds_overshoot:.1f}" if r.v_ds_overshoot is not None else "n/a"
        lines.append(
            f"| {r.n_parallel} | {r.r_g_on:.1f} | {r.r_g_off:.1f} | {r.f_sw / 1e3:.1f} | {r.p_cond_leg:.2f} | "
            f"{r.p_sw_leg:.2f} | {r.p_total_leg:.2f} | {r.p_budget_leg:.2f} | "
            f"{r.t_junction_c:.1f} | {r.margin_c:.1f} | {overshoot_str} | "
            f"{'yes' if r.feasible else 'NO'} |"
        )
    lines.append("")

    feasible_results = [r for r in results if r.feasible]
    if feasible_results:
        best = max(feasible_results, key=lambda r: r.f_sw)
        lines.append("## Recommended design point")
        lines.append(
            f"- **N = {best.n_parallel}** devices in parallel per switch position, "
            f"**Rg_on = {best.r_g_on:.1f} ohm**, **Rg_off = {best.r_g_off:.1f} ohm**, "
            f"**f_sw = {best.f_sw / 1e3:.1f} kHz**"
        )
        lines.append(
            f"- Loss: {best.p_total_leg:.2f} W of {best.p_budget_leg:.2f} W budget "
            f"({100 * best.p_total_leg / best.p_budget_leg:.0f} % used) "
            f"-- conduction {best.p_cond_leg:.2f} W / switching {best.p_sw_leg:.2f} W"
        )
        lines.append(f"- Tj = {best.t_junction_c:.1f} C ({best.margin_c:.1f} C margin to derated limit)")
        if best.v_ds_overshoot is not None:
            lines.append(f"- Vds overshoot: {best.v_ds_overshoot:.1f} V")
    else:
        lines.append("## No feasible design point found in the swept range.")
        lines.append(
            "Check: cooling (R_th,sink-amb), efficiency target realism, overshoot limit, "
            "or widen the Rg/f_sw/N search bounds."
        )

    lines.append("")
    lines.append("## Known limitations of this model")
    lines.append(
        "- Assumes perfectly even current sharing across the N parallel devices; real "
        "boards see some dynamic imbalance from device-to-device Vth spread."
    )
    lines.append(
        "- Steady-state, full-load thermal only -- no transient/duty-cycled Tj model."
    )
    lines.append(
        "- If any N below the max searched is missing from the table above, no Rg in "
        "the search bounds met the overshoot limit at that N's per-device current -- "
        "more parallel devices, lower loop inductance, or a relaxed overshoot limit are "
        "the ways out."
    )
    lines.append(
        "- If the recommended f_sw sits at (or just under) the search's fsw_max_Hz "
        "ceiling with large loss/thermal margin still unused, that row is likely "
        "search-bound-limited, not physically limited -- raise fsw_max_Hz and re-run to "
        "see how much higher it can actually go."
    )

    return "\n".join(lines)


def save_report(text: str, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

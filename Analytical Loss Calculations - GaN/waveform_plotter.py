"""Plot estimated EPC2361 half-bridge turn-on and turn-off waveforms.

The plotted transitions are analytical illustrations based on gate-charge
transition times and L*di/dt overshoot from epc2361_loss. They are not a
replacement for measured switching waveforms.
"""
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from epc2361_loss import LossInputs, calculate


FIELDS = [
    ("VBUS (V)", "vbus"),
    ("AC RMS current (A)", "ac_rms"),
    ("Switching frequency (Hz)", "fsw"),
    ("Waveform factor", "waveform_factor"),
    ("Modulation index (0..1)", "modulation_index"),
    ("Power factor (0..1)", "power_factor"),
    ("Gate voltage (V)", "vgs"),
    ("QG total (nC)", "qg_nc"),
    ("QGS(th) (nC, 0=QGS1)", "qgsth_nc"),
    ("QGD (nC)", "qgd_nc"),
    ("QGS2 (nC)", "qgs2_nc"),
    ("Internal RG (ohm)", "rg_internal"),
    ("Plot current (A, 0=AC peak)", "waveform_current_a"),
    ("RG on (ohm)", "rg_on"),
    ("RG off (ohm)", "rg_off"),
    ("Driver source R (ohm)", "driver_source_r"),
    ("Driver sink R (ohm)", "driver_sink_r"),
    ("Driver source limit (A)", "driver_source_a"),
    ("Driver sink limit (A)", "driver_sink_a"),
    ("Power-loop L / switch (nH)", "loop_inductance_nh"),
    ("VGS threshold (V)", "vgs_threshold"),
    ("VGS plateau (V)", "vgs_plateau"),
    ("COSS per device (nF)", "coss_nf"),
    ("QOSS at VBUS (nC)", "qoss_nc"),
    ("QOSS reference voltage (V)", "qoss_voltage"),
    ("EOSS at VBUS (uJ)", "eoss_uj"),
]


def _linear_step(time_s, duration_s):
    """Linear ramp matching the simplified EPC switching diagrams."""
    if duration_s <= 0:
        return (time_s >= 0).astype(float)
    return np.clip(time_s / duration_s, 0.0, 1.0)


def build_waveforms(inputs, result, samples=1200, include_ringing=False):
    """Return EPC-style piecewise turn-on/turn-off voltage, current, and VGS."""
    tgs1_on = result["threshold_time_on_ns"] * 1e-9
    tgs1_off = result["threshold_time_off_ns"] * 1e-9
    tpost_on = result["post_time_on_ns"] * 1e-9
    tpost_off = result["post_time_off_ns"] * 1e-9
    tcr = result["current_rise_time_ns"] * 1e-9
    tvf = result["voltage_fall_time_ns"] * 1e-9
    tvr = result["voltage_rise_time_ns"] * 1e-9
    tcf = result["current_fall_time_ns"] * 1e-9
    # During turn-off the gate first discharges from the drive voltage to the
    # Miller plateau. VDS then rises during the plateau, followed by current
    # fall and the final discharge below threshold.
    tpre_plateau_off = tpost_off
    peak = result["waveform_current_a"]
    overshoot = result["overshoot_voltage"]
    on_gate_time = tgs1_on + tcr + tvf + tpost_on
    off_gate_time = tpre_plateau_off + tvr + tcf + tgs1_off
    transition = max(on_gate_time, off_gate_time, 1e-12)
    span = transition * 1.6
    t = np.linspace(-span / 2.0, span / 2.0, samples)
    on_start = -on_gate_time / 2.0
    off_start = -off_gate_time / 2.0
    on_gate_start = on_start + tgs1_on
    on_current_start = on_gate_start
    on_voltage_start = on_current_start + tcr
    off_voltage_start = off_start + tpre_plateau_off
    off_current_start = off_voltage_start + tvr
    off_gate_end = off_current_start + tcf
    # Include every corner so integrating VDS*IDS reproduces analytic energies.
    t = np.unique(np.concatenate((t, [on_start, on_gate_start, on_voltage_start,
        on_voltage_start+tvf, on_voltage_start+tvf+tpost_on, off_start,
        off_voltage_start, off_current_start, off_gate_end, off_gate_end+tgs1_off])))
    on_current_step = _linear_step(t - on_current_start, tcr)
    on_voltage_step = _linear_step(t - on_voltage_start, tvf)
    off_voltage_step = _linear_step(t - off_voltage_start, tvr)
    off_current_step = _linear_step(t - off_current_start, tcf)
    vth = inputs.vgs_threshold
    vpl = inputs.vgs_plateau
    on_vgs = np.where(
        t < on_start,
        0.0,
        np.where(
            t < on_gate_start,
            vth * _linear_step(t - on_start, tgs1_on),
            np.where(
                t < on_voltage_start,
                vth + (vpl - vth) * np.clip(
                    (t - on_gate_start) / tcr, 0.0, 1.0
                ),
                np.where(
                    t < on_voltage_start + tvf,
                    vpl,
                    vpl + (inputs.vgs - vpl) * _linear_step(t - on_voltage_start - tvf, tpost_on),
                ),
            ),
        ),
    )
    off_vgs = np.where(
        t < off_start,
        inputs.vgs,
        np.where(
            t < off_voltage_start,
            inputs.vgs - (inputs.vgs - vpl) * _linear_step(t - off_start, tpre_plateau_off),
            np.where(
                t < off_current_start,
                vpl,
                np.where(
                    t < off_gate_end,
                    vpl - (vpl - vth) * np.clip(
                        (t - off_current_start) / tcf, 0.0, 1.0
                    ),
                    np.where(
                        t < off_gate_end + tgs1_off,
                        vth * (1.0 - _linear_step(t - off_gate_end, tgs1_off)),
                        0.0,
                    ),
                ),
            ),
        ),
    )
    on_voltage = inputs.vbus * (1.0 - on_voltage_step)
    on_current = peak * on_current_step
    off_voltage = inputs.vbus * off_voltage_step
    off_current = peak * (1.0 - off_current_step)

    if include_ringing and inputs.coss_nf > 0 and inputs.loop_inductance_nh > 0:
        c_total = 2.0 * inputs.devices_parallel * inputs.coss_nf * 1e-9
        ring_frequency = 1.0 / (2.0 * np.pi * np.sqrt(inputs.loop_inductance_nh * 1e-9 * c_total))
        damping = max(on_gate_time, off_gate_time)
        on_ring_time = np.maximum(t - on_voltage_start - tvf, 0.0)
        off_ring_time = np.maximum(t - off_current_start - tcf, 0.0)
        on_ring = result["overshoot_on_voltage"] * np.exp(-on_ring_time / damping)
        off_ring = result["overshoot_off_voltage"] * np.exp(-off_ring_time / damping)
        on_voltage += on_ring * np.sin(2.0 * np.pi * ring_frequency * on_ring_time)
        off_voltage += off_ring * np.sin(2.0 * np.pi * ring_frequency * off_ring_time)

    return t, on_voltage, on_current, on_vgs, off_voltage, off_current, off_vgs


def _parse_inputs(variables):
    values = {}
    for key, variable in variables.items():
        try:
            values[key] = float(variable.get())
        except ValueError as exc:
            raise ValueError(f"{key} must be numeric") from exc
    return LossInputs(**values)


def draw_waveforms(figure, axes, inputs, result=None, include_ringing=False):
    """Draw independently scaled schematic traces, matching AN030 Figures 2/3.

    Vertical positions are illustrative; physical levels and ns intervals are
    labeled explicitly. Power is the actual VDS*IDS overlap, independently scaled.
    """
    result = calculate(inputs) if result is None else result
    t, von, ion, gon, voff, ioff, goff = build_waveforms(
        inputs, result, include_ringing=include_ringing)
    tns = t * 1e9
    current = result["waveform_current_a"]
    colors = ("#ee2030", "#43a77c", "#0073b9")
    for ax, v, ids, gate, on in zip(axes, (von, voff), (ion, ioff), (gon, goff), (True, False)):
        total = result["gate_rise_time_ns" if on else "gate_fall_time_ns"]
        t0 = -total / 2
        if on:
            a = t0 + result["threshold_time_on_ns"]
            b = a + result["current_rise_time_ns"]
            c = b + result["voltage_fall_time_ns"]
            tail = result["post_time_on_ns"]
            labels = ("CR", "VF")
        else:
            a = t0 + result["post_time_off_ns"]
            b = a + result["voltage_rise_time_ns"]
            c = b + result["current_fall_time_ns"]
            tail = result["threshold_time_off_ns"]
            labels = ("VR", "CF")
        # Schematic spacing keeps the short switching intervals readable.
        # Physical durations remain explicitly labeled; arrays retain true time.
        physical_knots = [tns[0], t0, a, b, c, c+tail, tns[-1]]
        drawing_knots = [0, .45, 1.25, 2.15, 3.4, 4.05, 5]
        x = np.interp(tns, physical_knots, drawing_knots)
        ax.clear()
        ax.set_xlim(0, 5.8)
        ax.set_ylim(-0.19, 1.18)
        ax.axis("off")
        start, end = 0, 5
        ax.annotate("", (end * 1.12, 0), (start, 0),
                    arrowprops=dict(arrowstyle="-|>", lw=1.8, color="black"))
        ax.annotate("", (start, 1.1), (start, 0),
                    arrowprops=dict(arrowstyle="-|>", lw=1.8, color="black"))
        ax.text(end * 1.12, -.065, "t", fontsize=13)
        power = v * ids
        ax.fill_between(x, 0, power / (inputs.vbus * current), color="0.86", zorder=1)
        ax.plot(x, power / (inputs.vbus * current), color="black", lw=1.6)
        ax.plot(x, .72 * v / inputs.vbus, color=colors[0], lw=3)
        ax.plot(x, .57 * ids / current, color=colors[1], lw=3, linestyle=(0, (1, .5)))
        ax.plot(x, .31 * gate / inputs.vgs, color=colors[2], lw=3)
        for level in (.72, .57, .31 * inputs.vgs_threshold / inputs.vgs, .31 * inputs.vgs_plateau / inputs.vgs):
            ax.hlines(level, start, end, colors="0.3", linestyles="--", linewidth=.65, zorder=0)
        ax.text(start, .75, f"$V_{{BUS}}$ = {inputs.vbus:g} V", color=colors[0], fontsize=10)
        ax.text(start, .60, f"$I_L$ = {current:.1f} A", color=colors[1], fontsize=10)
        ax.text(end, .31, f"$V_{{DR}}$\n{inputs.vgs:g} V", color=colors[2], fontsize=9)
        ax.text(end, .31 * inputs.vgs_plateau / inputs.vgs, "$V_{PL}$", fontsize=9, va="bottom")
        ax.text(end, .31 * inputs.vgs_threshold / inputs.vgs, "$V_{th}$", fontsize=9, va="top")
        for edge in (1.25, 2.15, 3.4):
            ax.vlines(edge, 0, 1.04, colors="0.3", linestyles="--", linewidth=.7)
        for left, right, duration, label in ((1.25, 2.15, b-a, labels[0]), (2.15, 3.4, c-b, labels[1])):
            ax.annotate("", (right, -.055), (left, -.055), arrowprops=dict(arrowstyle="|-|", lw=.8))
            ax.text((left+right)/2, -.09, f"$t_{{{label}}}$\n{duration:.2f} ns", ha="center", va="top", fontsize=9)
        ax.annotate("$p_{ON}$" if on else "$p_{OFF}$", (2.15, .99),
                    (2.75, 1.08), fontsize=12,
                    arrowprops=dict(arrowstyle="->", color="black"))
        energy = result["eon_overlap_j" if on else "eoff_overlap_j"]
        ax.set_title(("Turn-on" if on else "Turn-off") + f"  |  overlap energy {energy*1e6:.2f} µJ", pad=16)
        direction = "on" if on else "off"
        dvdt = result[f"dvdt_{direction}_v_ns"] * (-1 if on else 1)
        didt = result[f"didt_{direction}_a_ns"] * (1 if on else -1)
        overshoot = result[f"overshoot_{direction}_voltage"]
        ax.text(.5, -.10,
                f"dVDS/dt = {dvdt:+.2f} V/ns   |   dIDS/dt = {didt:+.2f} A/ns\n"
                f"Estimated overshoot (L·|di/dt|) = {overshoot:.2f} V",
                transform=ax.transAxes, ha="center", va="top", fontsize=10,
                linespacing=1.6)

    for artist in list(figure.texts):
        if artist is not getattr(figure, "_suptitle", None):
            artist.remove()
    figure.suptitle("EPC2361 simplified switching waveforms", fontsize=15)
    figure.text(.5, .035, "Red: VDS   •   Green: IDS   •   Blue: VGS   •   Gray: p(t) = VDS × IDS\n"
                "Schematic time spacing and independent vertical scales; labeled durations are calculated.",
                ha="center", fontsize=9)
    figure.subplots_adjust(left=.07, right=.92, top=.82, bottom=.30, wspace=.3)
    return figure


def save_waveforms(path="output/switching_waveforms.png", inputs=None):
    """Render without starting the GUI (MPLBACKEND=Agg is supported)."""
    from pathlib import Path
    inputs = LossInputs() if inputs is None else inputs
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    draw_waveforms(fig, axes, inputs)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main():
    root = tk.Tk()
    root.title("EPC2361 Switching Waveform Estimator")
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)

    root.geometry("1450x850")
    control_container = ttk.Frame(root)
    control_container.grid(row=0, column=0, sticky="ns")
    control_canvas = tk.Canvas(control_container, width=350, highlightthickness=0)
    scrollbar = ttk.Scrollbar(control_container, orient="vertical", command=control_canvas.yview)
    control_canvas.configure(yscrollcommand=scrollbar.set)
    control_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    controls = ttk.Frame(control_canvas, padding=10)
    control_canvas.create_window((0, 0), window=controls, anchor="nw")
    controls.bind("<Configure>", lambda event: control_canvas.configure(scrollregion=control_canvas.bbox("all")))
    variables = {}
    defaults = LossInputs()
    for row, (label, key) in enumerate(FIELDS):
        ttk.Label(controls, text=label).grid(row=row, column=0, sticky="w", pady=2)
        variable = tk.StringVar(value=str(getattr(defaults, key)))
        variables[key] = variable
        ttk.Entry(controls, textvariable=variable, width=16).grid(
            row=row, column=1, sticky="ew", pady=2
        )

    figure, (ax_on, ax_off) = plt.subplots(1, 2, figsize=(12, 5))
    figure.tight_layout(pad=2.0)
    canvas = FigureCanvasTkAgg(figure, master=root)
    canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    ringing = tk.BooleanVar(value=False)
    ttk.Checkbutton(
        controls, text="Show calculated LC ringing", variable=ringing
    ).grid(row=len(FIELDS) + 2, column=0, columnspan=2, sticky="w")

    summary = tk.StringVar()
    ttk.Label(controls, textvariable=summary, justify="left").grid(
        row=len(FIELDS) + 1, column=0, columnspan=2, sticky="w", pady=8
    )

    def plot():
        try:
            inputs = _parse_inputs(variables)
            result = calculate(inputs)
            draw_waveforms(figure, (ax_on, ax_off), inputs, result,
                           include_ringing=ringing.get())
            canvas.draw()
            summary.set(
                f"One EPC2361 per switch position\n"
                f"Tj / RDS(on): {result['junction_temperature']:.2f} C / "
                f"{result['rds_on_mohm']:.4f} mOhm\n"
                f"Waveform current: {result['waveform_current_a']:.2f} A\n"
                f"Estimated stress: {result['stress_voltage']:.2f} V\n"
                f"Eon / Eoff (overlap): {result['eon_overlap_j'] * 1e6:.2f} / "
                f"{result['eoff_overlap_j'] * 1e6:.2f} uJ\n"
                f"Half-bridge loss: {result['total_loss']:.2f} W"
            )
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Invalid input", str(exc))

    ttk.Button(controls, text="Plot waveforms", command=plot).grid(
        row=len(FIELDS), column=0, columnspan=2, pady=8
    )
    plot()
    root.mainloop()


if __name__ == "__main__":
    main()

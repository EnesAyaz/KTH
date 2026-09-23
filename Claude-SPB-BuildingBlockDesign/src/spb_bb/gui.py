"""Interactive double-pulse test GUI: adjust every parameter in DoublePulseSpec (power-loop
inductance, gate resistances, load inductance, DC-link cap + its damping resistor, and all
pulse timing), run the real LTSpice double-pulse test against a device model, and view the
resulting Vgs/Vds/Id waveforms with Eon/Eoff computed the same way as
scripts/run_epc2361_sweep_v2.py (same netlist generator, same energy-integration code --
this GUI is a thin front end on ltspice/double_pulse.py and ltspice/runner.py, not a
separate implementation).
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from .devices import list_devices, load_device
from .ltspice.double_pulse import DoublePulseSpec
from .ltspice.runner import read_raw_waveforms_full, run_double_pulse

DEFAULT_LTSPICE_PATHS = [
    r"C:\Users\enesa\AppData\Local\Programs\ADI\LTspice\LTspice.exe",
    r"C:\Program Files\ADI\LTspice\LTspice.exe",
    r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe",
]


def _find_ltspice_default() -> str:
    for p in DEFAULT_LTSPICE_PATHS:
        if Path(p).exists():
            return p
    return ""


class LabeledEntry(ttk.Frame):
    """A label + entry pair on one row, with an optional unit suffix label."""

    def __init__(self, parent, label: str, default: str, unit: str = "", width: int = 10, tooltip: str = ""):
        super().__init__(parent)
        ttk.Label(self, text=label, width=20, anchor="w").pack(side="left")
        self.var = tk.StringVar(value=default)
        entry = ttk.Entry(self, textvariable=self.var, width=width)
        entry.pack(side="left")
        if unit:
            ttk.Label(self, text=unit, width=4).pack(side="left", padx=(4, 0))
        if tooltip:
            entry.bind("<Enter>", lambda e: None)  # placeholder; full tooltip not essential

    def get_float(self) -> float:
        return float(self.var.get())

    def get_float_or_none(self):
        s = self.var.get().strip()
        return float(s) if s else None


class ScrollableFrame(ttk.Frame):
    """A vertically-scrollable container (Tkinter has no built-in one)."""

    def __init__(self, parent, width=360):
        super().__init__(parent)
        canvas = tk.Canvas(self, width=width, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = ttk.Frame(canvas)
        self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)


class DoublePulseGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GaN Double-Pulse Test")
        self.geometry("1360x820")

        self.result_queue: queue.Queue = queue.Queue()
        self.running = False
        self.last_waveforms = None
        self.last_meta = None

        self._build_layout()
        self.after(100, self._poll_queue)

    # ------------------------------------------------------------------
    def _build_layout(self):
        root = ttk.Frame(self)
        root.pack(fill="both", expand=True, padx=8, pady=8)

        left_container = ScrollableFrame(root, width=380)
        left_container.pack(side="left", fill="y", padx=(0, 8))
        left = left_container.inner

        right = ttk.Frame(root)
        right.pack(side="left", fill="both", expand=True)

        self._build_inputs(left)
        self._build_plots(right)

    def _build_inputs(self, parent):
        dev_frame = ttk.LabelFrame(parent, text="Device")
        dev_frame.pack(fill="x", pady=4)
        devices = list_devices() or ["EPC2361"]
        self.device_var = tk.StringVar(value="EPC2361" if "EPC2361" in devices else devices[0])
        ttk.Label(dev_frame, text="Part:", width=16, anchor="w").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        combo = ttk.Combobox(dev_frame, textvariable=self.device_var, values=devices, state="readonly", width=18)
        combo.grid(row=0, column=1, sticky="w", padx=4, pady=4)
        combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_device_info())

        self.device_info_var = tk.StringVar(value="")
        ttk.Label(dev_frame, textvariable=self.device_info_var, justify="left", foreground="gray20",
                  font=("Consolas", 8)).grid(row=1, column=0, columnspan=2, sticky="w", padx=4, pady=(0, 4))
        self._refresh_device_info()

        bias_frame = ttk.LabelFrame(parent, text="Bias point")
        bias_frame.pack(fill="x", pady=4)
        self.v_dc = LabeledEntry(bias_frame, "Vdc", "75", "V")
        self.v_dc.pack(anchor="w", padx=4, pady=2)
        self.i_test = LabeledEntry(bias_frame, "Current reference", "155", "A")
        self.i_test.pack(anchor="w", padx=4, pady=2)
        self.v_gs_off = LabeledEntry(bias_frame, "Gate off-state bias", "0", "V")
        self.v_gs_off.pack(anchor="w", padx=4, pady=2)
        ttk.Label(
            bias_frame,
            text="(negative = real-driver-style negative bias,\ne.g. -4V; does NOT change on-time ringing,\nwhich happens while Vgs is already HIGH)",
            foreground="gray30", font=("", 8),
        ).pack(anchor="w", padx=4)
        ttk.Label(
            bias_frame,
            text="(pulse-1 width is derived from this,\nVdc, and L_load: t_pw1 = I*L/Vdc)",
            foreground="gray30", font=("", 8),
        ).pack(anchor="w", padx=4)

        circuit_frame = ttk.LabelFrame(parent, text="Circuit parameters")
        circuit_frame.pack(fill="x", pady=4)
        self.l_load = LabeledEntry(circuit_frame, "Load inductance", "100", "uH")
        self.l_load.pack(anchor="w", padx=4, pady=2)
        self.l_loop = LabeledEntry(circuit_frame, "Power loop L", "0.7", "nH")
        self.l_loop.pack(anchor="w", padx=4, pady=2)
        self.r_g_on = LabeledEntry(circuit_frame, "Rg on", "2.0", "ohm")
        self.r_g_on.pack(anchor="w", padx=4, pady=2)
        self.r_g_off = LabeledEntry(circuit_frame, "Rg off", "2.0", "ohm")
        self.r_g_off.pack(anchor="w", padx=4, pady=2)
        self.c_dc = LabeledEntry(circuit_frame, "DC-link bulk cap Cdc", "100", "uF")
        self.c_dc.pack(anchor="w", padx=4, pady=2)
        self.c_dc_esr = LabeledEntry(circuit_frame, "Cdc series ESR", "10", "mOhm")
        self.c_dc_esr.pack(anchor="w", padx=4, pady=2)
        ttk.Label(
            circuit_frame,
            text="Resr is the ONLY damping element in the\nLloop<->Coss ring -- raise it to test\nwhether ringing is lightly-damped resonance.",
            foreground="gray30", font=("", 8),
        ).pack(anchor="w", padx=4)

        timing_frame = ttk.LabelFrame(parent, text="Pulse timing")
        timing_frame.pack(fill="x", pady=4)
        self.t_start_delay = LabeledEntry(timing_frame, "Start delay", "200", "ns")
        self.t_start_delay.pack(anchor="w", padx=4, pady=2)
        self.t_off_gap = LabeledEntry(timing_frame, "Off gap (between pulses)", "2", "us")
        self.t_off_gap.pack(anchor="w", padx=4, pady=2)
        self.pw2 = LabeledEntry(timing_frame, "2nd pulse width", "500", "ns")
        self.pw2.pack(anchor="w", padx=4, pady=2)
        self.tr_tf_drive = LabeledEntry(timing_frame, "Drive edge speed", "2", "ns")
        self.tr_tf_drive.pack(anchor="w", padx=4, pady=2)
        self.sim_extra_time = LabeledEntry(timing_frame, "Extra time after 2nd pulse", "300", "ns")
        self.sim_extra_time.pack(anchor="w", padx=4, pady=2)
        self.sim_tmax = LabeledEntry(timing_frame, "Max timestep (blank=auto)", "", "ns")
        self.sim_tmax.pack(anchor="w", padx=4, pady=2)

        adv_frame = ttk.LabelFrame(parent, text="Energy-integration window")
        adv_frame.pack(fill="x", pady=4)
        self.edge_margin = LabeledEntry(adv_frame, "Edge margin", "5", "ns")
        self.edge_margin.pack(anchor="w", padx=4, pady=2)

        ltspice_frame = ttk.LabelFrame(parent, text="LTSpice")
        ltspice_frame.pack(fill="x", pady=4)
        self.ltspice_path = tk.StringVar(value=_find_ltspice_default())
        row = ttk.Frame(ltspice_frame)
        row.pack(fill="x", padx=4, pady=2)
        ttk.Entry(row, textvariable=self.ltspice_path, width=28).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="...", width=3, command=self._browse_ltspice).pack(side="left", padx=(4, 0))

        run_frame = ttk.Frame(parent)
        run_frame.pack(fill="x", pady=8)
        self.run_button = ttk.Button(run_frame, text="Run double-pulse test", command=self._on_run)
        self.run_button.pack(fill="x")
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(run_frame, textvariable=self.status_var, foreground="gray20", wraplength=340).pack(
            anchor="w", pady=(4, 0)
        )
        self.progress = ttk.Progressbar(run_frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=(4, 0))

        results_frame = ttk.LabelFrame(parent, text="Results")
        results_frame.pack(fill="x", pady=4)
        self.result_vars = {
            "e_on": tk.StringVar(value="-- uJ"),
            "e_off": tk.StringVar(value="-- uJ"),
            "v_ds_peak": tk.StringVar(value="-- V"),
            "v_ds_overshoot": tk.StringVar(value="-- V"),
            "i_test_actual": tk.StringVar(value="-- A"),
        }
        labels = {
            "e_on": "E_on:", "e_off": "E_off:", "v_ds_peak": "Vds peak:",
            "v_ds_overshoot": "Vds overshoot:", "i_test_actual": "I_test (actual):",
        }
        for i, key in enumerate(["e_on", "e_off", "v_ds_peak", "v_ds_overshoot", "i_test_actual"]):
            ttk.Label(results_frame, text=labels[key], width=16, anchor="w").grid(row=i, column=0, sticky="w", padx=4, pady=1)
            ttk.Label(results_frame, textvariable=self.result_vars[key], font=("", 10, "bold")).grid(
                row=i, column=1, sticky="w", padx=4, pady=1
            )

    def _refresh_device_info(self):
        try:
            dev = load_device(self.device_var.get())
        except Exception:
            self.device_info_var.set("(device not found)")
            return
        lines = [
            f"Rds_on(25C): {dev.r_ds_on_25c*1e3:.2f} mOhm   Rg_int: {dev.r_g_internal:.2f} ohm",
            f"Qgs/Qgd/Qg: {dev.q_gs*1e9:.1f}/{dev.q_gd*1e9:.1f}/{dev.q_g_total*1e9:.1f} nC",
            f"Coss@{dev.c_oss_ref_v:.0f}V: {dev.c_oss_ref*1e12:.0f} pF",
        ]
        if dev.c_iss_ref:
            lines.append(f"Ciss@{dev.c_oss_ref_v:.0f}V: {dev.c_iss_ref*1e12:.0f} pF (datasheet ref;"
                          " SPICE model uses nonlinear Cgs/Cgd, not this fixed value)")
        self.device_info_var.set("\n".join(lines))

    def _build_plots(self, parent):
        self.figure = Figure(figsize=(8.5, 7.5), dpi=100)
        self.ax_vgs = self.figure.add_subplot(311)
        self.ax_vds = self.figure.add_subplot(312, sharex=self.ax_vgs)
        self.ax_id = self.figure.add_subplot(313, sharex=self.ax_vgs)
        self.ax_vgs.set_ylabel("Vgs (V)")
        self.ax_vds.set_ylabel("Vds (V)")
        self.ax_id.set_ylabel("Id (A)")
        self.ax_id.set_xlabel("Time (ns)")
        for ax in (self.ax_vgs, self.ax_vds, self.ax_id):
            ax.grid(True, alpha=0.3)
        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()

        zoom_row = ttk.Frame(parent)
        zoom_row.pack(fill="x", pady=(4, 0))
        ttk.Label(zoom_row, text="Quick zoom:").pack(side="left", padx=(0, 6))
        ttk.Button(zoom_row, text="Full view", command=self._zoom_full).pack(side="left", padx=2)
        ttk.Button(zoom_row, text="Turn-on edge", command=self._zoom_turnon).pack(side="left", padx=2)
        ttk.Button(zoom_row, text="Turn-off edge", command=self._zoom_turnoff).pack(side="left", padx=2)
        ttk.Button(zoom_row, text="Steady conduction", command=self._zoom_conduction).pack(side="left", padx=2)

    # ------------------------------------------------------------------
    def _browse_ltspice(self):
        path = filedialog.askopenfilename(title="Locate LTspice.exe", filetypes=[("Executable", "*.exe")])
        if path:
            self.ltspice_path.set(path)

    def _on_run(self):
        if self.running:
            return
        try:
            spec = DoublePulseSpec(
                v_dc=self.v_dc.get_float(),
                i_test=self.i_test.get_float(),
                r_g_on=self.r_g_on.get_float(),
                r_g_off=self.r_g_off.get_float(),
                v_gs_off=self.v_gs_off.get_float(),
                l_loop=self.l_loop.get_float() * 1e-9,
                l_load=self.l_load.get_float() * 1e-6,
                c_dc=self.c_dc.get_float() * 1e-6,
                c_dc_esr=self.c_dc_esr.get_float() * 1e-3,
                t_start_delay=self.t_start_delay.get_float() * 1e-9,
                t_off_gap=self.t_off_gap.get_float() * 1e-6,
                pw2=self.pw2.get_float() * 1e-9,
                tr_tf_drive=self.tr_tf_drive.get_float() * 1e-9,
                sim_extra_time=self.sim_extra_time.get_float() * 1e-9,
                sim_tmax=(lambda v: v * 1e-9 if v is not None else None)(self.sim_tmax.get_float_or_none()),
            )
            edge_margin = self.edge_margin.get_float() * 1e-9
        except ValueError as exc:
            messagebox.showerror("Invalid input", f"Check your numeric fields: {exc}")
            return

        ltspice_exe = self.ltspice_path.get().strip() or None
        if ltspice_exe and not Path(ltspice_exe).exists():
            messagebox.showerror("LTSpice not found", f"No file at:\n{ltspice_exe}")
            return

        device_name = self.device_var.get()

        self.running = True
        self.run_button.state(["disabled"])
        self.status_var.set("Running LTSpice (this can take a few seconds to several minutes "
                             "for difficult convergence cases)...")
        self.progress.start(12)

        thread = threading.Thread(
            target=self._worker, args=(device_name, spec, ltspice_exe, edge_margin), daemon=True
        )
        thread.start()

    def _worker(self, device_name: str, spec: DoublePulseSpec, ltspice_exe: str | None, edge_margin: float):
        try:
            device = load_device(device_name)
            work_dir = str(Path(__file__).resolve().parents[2] / "outputs" / "dpt_gui_runs")
            result = run_double_pulse(
                device, spec, work_dir, ltspice_exe=ltspice_exe, keep_files=True, edge_margin=edge_margin
            )
            waveforms = read_raw_waveforms_full(result.raw_path)
            self.result_queue.put(("ok", result, waveforms))
        except Exception as exc:  # noqa: BLE001 -- surface any failure to the GUI, don't crash the thread silently
            self.result_queue.put(("error", str(exc)))

    def _poll_queue(self):
        try:
            item = self.result_queue.get_nowait()
        except queue.Empty:
            pass
        else:
            self.running = False
            self.run_button.state(["!disabled"])
            self.progress.stop()
            if item[0] == "ok":
                _, result, waveforms = item
                self._show_result(result, waveforms)
                self.status_var.set(f"Done. Raw file: {Path(result.raw_path).name}")
            else:
                self.status_var.set("Failed -- see error dialog.")
                messagebox.showerror("LTSpice run failed", item[1][:2000])
        self.after(100, self._poll_queue)

    def _show_result(self, result, waveforms):
        self.result_vars["e_on"].set(f"{result.e_on * 1e6:.3f} uJ")
        self.result_vars["e_off"].set(f"{result.e_off * 1e6:.3f} uJ")
        self.result_vars["v_ds_peak"].set(f"{result.v_ds_peak:.2f} V")
        self.result_vars["v_ds_overshoot"].set(f"{result.v_ds_overshoot:.2f} V")
        self.result_vars["i_test_actual"].set(f"{result.i_test_actual:.2f} A")

        self.last_waveforms = waveforms
        self.last_meta = result.meta

        t_ns = waveforms["t"] * 1e9
        self.ax_vgs.clear()
        self.ax_vds.clear()
        self.ax_id.clear()
        if "v_gs" in waveforms:
            self.ax_vgs.plot(t_ns, waveforms["v_gs"], color="tab:green", linewidth=0.8)
        self.ax_vds.plot(t_ns, waveforms["v_ds"], color="tab:blue", linewidth=0.8)
        self.ax_id.plot(t_ns, waveforms["i_d"], color="tab:orange", linewidth=0.8)

        meta = result.meta
        for ax in (self.ax_vgs, self.ax_vds, self.ax_id):
            ax.axvspan(meta["t1_flat_end"] * 1e9, meta.get("t2_rise", 0) * 1e9, color="red", alpha=0.06)
            ax.axvspan(meta["t2_rise"] * 1e9, meta["t2_flat_end"] * 1e9, color="green", alpha=0.08)
            ax.grid(True, alpha=0.3)
        self.ax_vgs.set_ylabel("Vgs (V)")
        self.ax_vds.set_ylabel("Vds (V)")
        self.ax_id.set_ylabel("Id (A)")
        self.ax_id.set_xlabel("Time (ns)")
        self.ax_vgs.set_title(
            f"Eon={result.e_on*1e6:.2f}uJ (green band)  Eoff={result.e_off*1e6:.2f}uJ (red band)  "
            f"overshoot={result.v_ds_overshoot:.1f}V"
        )
        self.figure.tight_layout()
        self._zoom_full()

    # --- quick-zoom helpers -------------------------------------------
    def _apply_xlim(self, t0_s, t1_s, margin_frac=0.15):
        span = t1_s - t0_s
        lo = (t0_s - margin_frac * span) * 1e9
        hi = (t1_s + margin_frac * span) * 1e9
        for ax in (self.ax_vgs, self.ax_vds, self.ax_id):
            ax.set_xlim(lo, hi)
            ax.relim()
            ax.autoscale(axis="y")
        self.canvas.draw()

    def _zoom_full(self):
        if not self.last_waveforms:
            return
        t = self.last_waveforms["t"]
        self._apply_xlim(t.min(), t.max(), margin_frac=0.02)

    def _zoom_turnon(self):
        if not self.last_meta:
            return
        m = self.last_meta
        self._apply_xlim(m["t2_rise"], m["t2_flat_end"], margin_frac=0.5)

    def _zoom_turnoff(self):
        if not self.last_meta:
            return
        m = self.last_meta
        self._apply_xlim(m["t1_flat_end"], m["t1_fall_end"], margin_frac=3.0)

    def _zoom_conduction(self):
        if not self.last_meta:
            return
        m = self.last_meta
        lo = m["t1_rise"] + 0.3 * (m["t1_flat_end"] - m["t1_rise"])
        hi = m["t1_rise"] + 0.7 * (m["t1_flat_end"] - m["t1_rise"])
        self._apply_xlim(lo, hi, margin_frac=0.1)


def main():
    app = DoublePulseGUI()
    app.mainloop()


if __name__ == "__main__":
    main()

"""Small Tkinter front end for epc2361_loss."""
import tkinter as tk
from tkinter import ttk, messagebox
from epc2361_loss import LossInputs, calculate

FIELDS = [
    ("VBUS (V)", "vbus"), ("AC RMS current (A)", "ac_rms"), ("Switching frequency (Hz)", "fsw"),
    ("Waveform factor", "waveform_factor"),
    ("Modulation / waveform", "modulation"), ("Modulation index (0..1)", "modulation_index"),
    ("Power factor (0..1)", "power_factor"), ("RDS(on), 25C (mOhm)", "rds25_mohm"),
    ("RDS(on) max (mOhm)", "rds_max_mohm"), ("Use max RDS (true/false)", "use_rds_max"),
    ("RDS mode (iterative/manual)", "rds_temperature_mode"),
    ("RDS scale (manual mode only)", "rds_temp_scale"),
    ("Gate voltage (V)", "vgs"), ("QG (nC)", "qg_nc"), ("QGD (nC)", "qgd_nc"), ("QGS2 (nC)", "qgs2_nc"),
    ("VGS threshold (V)", "vgs_threshold"), ("VGS plateau (V)", "vgs_plateau"),
    ("QG(th) (nC)", "qgsth_nc"), ("Internal RG (ohm)", "rg_internal"),
    ("RG on (ohm)", "rg_on"), ("RG off (ohm)", "rg_off"), ("Driver source R (ohm)", "driver_source_r"),
    ("Driver sink R (ohm)", "driver_sink_r"), ("Driver source limit (A)", "driver_source_a"),
    ("Driver sink limit (A)", "driver_sink_a"), ("Dead time (ns)", "dead_time_ns"),
    ("Effective dead time (ns)", "effective_dead_time_ns"), ("Power-loop L / switch (nH)", "loop_inductance_nh"),
    ("Case temperature (C)", "case_c"), ("Ambient temperature (C)", "ambient_c"),
    ("Rtheta JC (C/W)", "rtheta_jc_c_w"), ("Rtheta JA (C/W)", "rtheta_ja_c_w"),
    ("Thermal mode (case/ambient)", "thermal_mode"), ("Target junction (C)", "target_junction_c"),
    ("QOSS (nC)", "qoss_nc"), ("QOSS reference voltage (V)", "qoss_voltage"),
    ("EOSS at VBUS (uJ, reference)", "eoss_uj"), ("VSD (V)", "vsd"),
    ("Optional loop resistance (mOhm)", "optional_loop_r_mohm"),
    ("Hard switching (true/false)", "hard_switching"),
]

def main():
    root = tk.Tk(); root.title("EPC2361 Half-Bridge Loss Calculator")
    frame = ttk.Frame(root, padding=10); frame.grid()
    vars_ = {}
    for row, (label, key) in enumerate(FIELDS):
        column, display_row = 2 * (row // 22), row % 22
        ttk.Label(frame, text=label).grid(row=display_row, column=column, sticky="w")
        v = tk.StringVar(value=str(getattr(LossInputs(), key))); vars_[key] = v
        ttk.Entry(frame, textvariable=v, width=16).grid(row=display_row, column=column+1)
    output = tk.Text(frame, width=58, height=30); output.grid(row=0, column=4, rowspan=22, padx=15)
    def run():
        try:
            text_fields = {"modulation", "thermal_mode", "rds_temperature_mode"}
            bool_fields = {"hard_switching", "use_rds_max"}
            values = {}
            for k, v in vars_.items():
                raw = v.get().strip().lower()
                if k in text_fields: values[k] = raw
                elif k in bool_fields:
                    if raw not in ("true", "false"): raise ValueError(f"{k} must be true or false")
                    values[k] = raw == "true"
                else: values[k] = float(v.get())
            result = calculate(LossInputs(**values))
            output.delete("1.0", "end")
            output.insert("end", f"Junction temperature: {result['junction_temperature']:.3f} C\n"
                          f"Updated RDS(on): {result['rds_on_mohm']:.4f} mOhm\n"
                          f"Thermal iterations: {result['thermal_iterations']}\n\n")
            for k, v in result.items(): output.insert("end", f"{k:32} {v:12.5g}\n")
        except (ValueError, TypeError) as exc: messagebox.showerror("Invalid input", str(exc))
    ttk.Button(frame, text="Calculate", command=run).grid(row=23, column=0, columnspan=4, pady=8)
    root.mainloop()
if __name__ == "__main__": main()

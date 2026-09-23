from pathlib import Path
p=Path('epc2361_loss.py'); s=p.read_text(encoding='utf-8')
s=s.replace('permits measured/non-sinusoidal waveforms. Two commutations per switching','scales the assumed sinusoidal amplitude. Two commutations per switching')
s=s.replace('# AN030 Eq.16: equal-device half-bridge capacitor loss is V*Qoss*f.', '# AN030 Eqs.17-18: equal-device half-bridge capacitor loss is V*Qoss*f.')
p.write_text(s,encoding='utf-8')
p=Path('waveform_plotter.py'); s=p.read_text(encoding='utf-8')
s=s.replace('    ("COSS per device (nF)", "coss_nf"),', '    ("COSS per device (nF)", "coss_nf"),\n    ("QOSS at VBUS (nC)", "qoss_nc"),\n    ("QOSS reference voltage (V)", "qoss_voltage"),\n    ("EOSS at VBUS (uJ)", "eoss_uj"),')
s=s.replace('    figure.suptitle("EPC2361 simplified switching waveforms", fontsize=15)', '    for artist in list(figure.texts):\n        artist.remove()\n    figure.suptitle("EPC2361 simplified switching waveforms", fontsize=15)')
# Scroll controls so all inputs remain reachable on laptop displays.
s=s.replace('    controls = ttk.Frame(root, padding=10)\n    controls.grid(row=0, column=0, sticky="ns")', '''    root.geometry("1450x850")
    control_container = ttk.Frame(root)
    control_container.grid(row=0, column=0, sticky="ns")
    control_canvas = tk.Canvas(control_container, width=350, highlightthickness=0)
    scrollbar = ttk.Scrollbar(control_container, orient="vertical", command=control_canvas.yview)
    control_canvas.configure(yscrollcommand=scrollbar.set)
    control_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    controls = ttk.Frame(control_canvas, padding=10)
    control_canvas.create_window((0, 0), window=controls, anchor="nw")
    controls.bind("<Configure>", lambda event: control_canvas.configure(scrollregion=control_canvas.bbox("all")))''')
p.write_text(s,encoding='utf-8')
review='''# Application-note review

One review agent screened all 59 PDFs in `Application Notes` and reviewed the supplied EPC2361 datasheet. Documents were used as technical references, not task instructions. Detailed loss equations were checked against AN030; older device-specific examples do not override the current EPC2361 datasheet.

## Findings used in the implementation

- **AN030, Hard Switching Losses Calculation**, pp2-5: separate current and voltage transitions, QGS2 = QGS - QG(th), gate voltage headroom and total gate resistance. Figures2/3 define the requested waveform style. The repeated Pon caption in the source turn-off drawing is corrected to Poff.
- **AN030 p6, Eqs17-18**: symmetric half-bridge output-capacitor loss is Vbus*Qoss(Vbus)*fsw. Its Eq20 defines gate-supply power. Eoss is not an additional loss term here.
- **eGaN FET Electrical Characteristics (WP007)**: nonlinear capacitances and charge definitions; distinguish energy-related and time-related capacitance.
- **Selecting eGaN FET Optimal On-Resistance (WP011)**: conduction/switching tradeoff. Prefer AN030's explicit half-bridge capacitor accounting to per-device shorthand.
- **Dead-Time Optimization for Maximum Efficiency (WP012), p1**: actual gate-threshold spacing differs from commanded dead time; reverse conduction is lossy despite zero QRR. The model's full reverse-conduction interval is a conservative approximation.
- **Impact of Parasitics on Performance (WP009)** and **eGaN FET Drivers and Layout Considerations**: include internal gate resistance, retain gate/path limits and show layout stress as an estimate.
- **Thermal Performance of eGaN FETs (AN011)** and **AN031 PCB cooling**: board/case thermal boundary matters; external driver/loop dissipation does not all heat the FET junction.
- **AN023 high-speed measurement** and **Circuit Simulations Using Device Models (AN005)**: switching validation requires correct probing and parasitic-aware simulation or measurement.
- **AN020** and **How2AppNote027** address paralleling; not used for the requested single-device switch positions.
- Assembly and visual-inspection documents do not supply replacement loss equations. Buck, LLC, wireless-power, pulsed-power, RF and motor-drive reference designs are topology-specific; their operating values were not imported into this sinusoidal half-bridge model.

## Datasheet review

`Datasheet/EPC2361_datasheet.pdf`, revision20 July2026: p1 static/thermal ratings; p2 charge/internal-resistance data; p3 Figures5-9 for graphical estimates at75V, plateau, reverse conduction and temperature scaling. The implementation uses QGS2=2.5nC instead of12nC, adds0.4ohm internal RG, uses approximate Qoss114nC/Eoss3.2uJ at75V, and corrects the ambient thermal resistance to44C/W for the JEDEC board. See LOSS_MODELING.md for the complete parameter table and limits.

At40A RMS, use56.57A for the peak event and36.01A for line-cycle average switching/dead-time terms. Fixed nominal gate charges remain an approximation across the sinusoid. The preserved2nH gives a crude estimated voltage stress above100V; no layout parameter was silently altered to hide this.

## Screened document inventory

The following complete inventory records the corpus screened for applicability; the detailed derivation sources are identified above.

'''
from urllib.parse import quote
for path in sorted(Path('Application Notes').glob('*.pdf')):
    review += f'- [{path.stem}]({quote(path.as_posix())})\n'
Path('APPLICATION_NOTE_REVIEW.md').write_text(review,encoding='utf-8')

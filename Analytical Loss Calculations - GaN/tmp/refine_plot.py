from pathlib import Path
p=Path('waveform_plotter.py'); s=p.read_text()
s=s.replace('    on_current_step =', '''    # Include every corner so integrating VDS*IDS reproduces analytic energies.
    t = np.unique(np.concatenate((t, [on_start, on_gate_start, on_voltage_start,
        on_voltage_start+tvf, on_voltage_start+tvf+tpost_on, off_start,
        off_voltage_start, off_current_start, off_gate_end, off_gate_end+tgs1_off])))
    on_current_step =''')
s=s.replace('        ax.clear()\n        ax.set_xlim(tns[0], tns[-1] * 1.16)', '''        total = result["gate_rise_time_ns" if on else "gate_fall_time_ns"]
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
        ax.set_xlim(0, 5.8)''')
s=s.replace('        start, end = tns[0], tns[-1]','        start, end = 0, 5')
s=s.replace('fill_between(tns,','fill_between(x,').replace('ax.plot(tns,','ax.plot(x,')
a=s.index('        total = result[',s.index('ax.text(end, .31 * inputs.vgs_threshold'))
b=s.index('        energy = result[',a)
s=s[:a]+'''        for edge in (1.25, 2.15, 3.4):
            ax.vlines(edge, 0, 1.04, colors="0.3", linestyles="--", linewidth=.7)
        for left, right, duration, label in ((1.25, 2.15, b-a, labels[0]), (2.15, 3.4, c-b, labels[1])):
            ax.annotate("", (right, -.055), (left, -.055), arrowprops=dict(arrowstyle="|-|", lw=.8))
            ax.text((left+right)/2, -.09, f"$t_{{{label}}}$\\n{duration:.2f} ns", ha="center", va="top", fontsize=9)
        ax.annotate("$p_{ON}$" if on else "$p_{OFF}$", (2.15, .99),
                    (2.75, 1.08), fontsize=12,
                    arrowprops=dict(arrowstyle="->", color="black"))
'''+s[b:]
s=s.replace('Independent vertical scales; idealized gate-charge transitions, not measured waveforms.', 'Schematic time spacing and independent vertical scales; labeled durations are calculated.')
p.write_text(s,encoding='utf-8')

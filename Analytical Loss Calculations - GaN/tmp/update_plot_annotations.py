from pathlib import Path
p=Path('epc2361_loss.py'); s=p.read_text(encoding='utf-8').replace('modulation_index: float = 0.9','modulation_index: float = 1.0'); p.write_text(s,encoding='utf-8')
p=Path('waveform_plotter.py'); s=p.read_text(encoding='utf-8')
needle='        ax.set_title(("Turn-on" if on else "Turn-off") + f"  |  overlap energy {energy*1e6:.2f} µJ", pad=16)'
s=s.replace(needle,needle+'''
        direction = "on" if on else "off"
        dvdt = result[f"dvdt_{direction}_v_ns"] * (-1 if on else 1)
        didt = result[f"didt_{direction}_a_ns"] * (1 if on else -1)
        overshoot = result[f"overshoot_{direction}_voltage"]
        ax.text(.5, -.10,
                f"dVDS/dt = {dvdt:+.2f} V/ns   |   dIDS/dt = {didt:+.2f} A/ns\\n"
                f"Estimated overshoot (L·|di/dt|) = {overshoot:.2f} V",
                transform=ax.transAxes, ha="center", va="top", fontsize=10,
                linespacing=1.6)
''')
s=s.replace('bottom=.21, wspace=.3','bottom=.30, wspace=.3')
p.write_text(s,encoding='utf-8')
p=Path('LOSS_MODELING.md'); s=p.read_text(encoding='utf-8-sig').replace('modulation index 0.9','modulation index 1.0'); p.write_text(s,encoding='utf-8')
p=Path('README.md'); s=p.read_text(encoding='utf-8-sig').replace('100 kHz sinusoidal PWM.', '100 kHz sinusoidal PWM, modulation index 1.0.').replace('Each trace has its own vertical scale.', 'Signed dv/dt and di/dt plus the separate turn-on/off overshoot estimates appear below each panel. Each trace has its own vertical scale.'); p.write_text(s,encoding='utf-8')

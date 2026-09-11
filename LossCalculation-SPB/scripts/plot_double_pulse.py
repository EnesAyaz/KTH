"""Replot double-pulse sensitivity from the saved table without running LTspice."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'results/double_pulse'
    saved=json.loads((out/'summary.json').read_text())
    rows,c=saved['points'],saved['config']
    fig,axes=plt.subplots(2,2,figsize=(11,8))
    axes=axes.flatten()
    for inductance in c['power_loop_inductances_nh']:
        series=sorted([r for r in rows if r['bus_v']==75 and r['target_a']==40 and r['loop_nh']==inductance],key=lambda r:r['rg_external_ohm'])
        for ax,key in zip(axes,['channel_energy_pair_uj','vds_peak_v','max_dvdt_on_over_1ns','max_didt_on_over_1ns']):
            ax.plot([r['rg_external_ohm'] for r in series],[r[key] for r in series],marker='o',label=f'{inductance} nH')
            ax.set_xlabel('External gate resistance (ohm)');ax.grid(alpha=.25)
    for ax,label in zip(axes,['DUT excess channel energy pair (uJ)','Peak Vds across either FET (V)', 'Turn-on maximum 1 ns slope (V/ns)', 'Turn-on maximum 1 ns slope (A/ns)']):
        ax.set_ylabel(label)
    axes[1].axhline(c['design_vds_ceiling_v'],color='black',linestyle='--',label='Design ceiling')
    axes[1].axhline(c['absolute_vds_ceiling_v'],color='red',linestyle=':',label='Absolute rating')
    axes[0].legend();axes[1].legend(fontsize=8)
    fig.suptitle('Single-device DPT at 75 V, target 40 A: failed voltage cases remain visible')
    fig.tight_layout();fig.savefig(out/'sensitivity.pdf');fig.savefig(out/'sensitivity.png',dpi=150);plt.close(fig)


if __name__=='__main__':main()

"""Estimate scenarios, not extracted PCB inductance or a parallel SPICE solution."""
import csv, json, math, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from models.parallel_layout import equivalent_loop_nh


def main():
    c=json.loads((ROOT/'data/inputs/inverter_module.json').read_text())
    config=json.loads((ROOT/'data/inputs/parallel_layout.json').read_text())
    out=ROOT/'results/parallel_layout';out.mkdir(parents=True,exist_ok=True)
    rms=c['pout_w']/(3*c['modulation_index']*c['vin_v']/(2*math.sqrt(2))*c['power_factor'])
    peak=math.sqrt(2)*rms
    rows=[]
    for n in config['parallel_counts']:
        row=dict(parallel_per_position=n,total_devices=6*n,phase_rms_a=rms,
                 phase_peak_a=peak,ideal_device_peak_a=peak/n,
                 ideal_device_rms_a=rms/(math.sqrt(2)*n),
                 conduction_only_module_w=3*rms*rms*.001*c['rds_hot_multiplier']/n)
        for scenario in config['scenarios']:
            row[scenario['name']+'_effective_nh']=equivalent_loop_nh(scenario['shared_nh'],scenario['branch_nh'],scenario['coupling_k'],n)
        rows.append(row)
    with (out/'estimates.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'summary.json').write_text(json.dumps(dict(module_inputs=c,layout_inputs=config,estimates=rows),indent=2))
    fig,ax=plt.subplots(figsize=(7,4))
    for s in config['scenarios']:
        counts=list(range(1,7))
        ax.plot(counts,[equivalent_loop_nh(s['shared_nh'],s['branch_nh'],s['coupling_k'],n) for n in counts],marker='o',label=s['name'].replace('_',' '))
    ax.set(xlabel='Parallel devices per position',ylabel='Illustrative effective loop inductance (nH)',
           title='Assumed symmetric branches: shared inductance limits improvement')
    ax.legend();ax.grid(alpha=.25);fig.tight_layout()
    fig.savefig(out/'inductance_scenarios.pdf');fig.savefig(out/'inductance_scenarios.png',dpi=160)
    plt.close(fig)
    print(json.dumps(rows,indent=2))


if __name__=='__main__':main()

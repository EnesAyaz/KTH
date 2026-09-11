"""Parallel-plate copper estimate plus explicitly assumed lumped additions."""
from pathlib import Path
import json, csv, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def plate_nh(h_mm,l_mm,w_mm):
    if any(not math.isfinite(v) or v<=0 for v in (h_mm,l_mm,w_mm)):
        raise ValueError('Geometry must be finite and positive')
    return 1.2566370614359172*h_mm*l_mm/w_mm

def main():
    c=json.loads((ROOT/'data/inputs/paper_loop_geometry.json').read_text(encoding='utf-8-sig'))
    out=ROOT/'results/paper_review';out.mkdir(exist_ok=True)
    rows=[]
    for h in c['layer_separations_mm']:
        local=plate_nh(h,c['overlap_length_mm'],c['effective_branch_width_mm'])
        for n in c['parallel_counts']:
            branch=local+c['assumed_branch_extra_nh']
            estimate=c['assumed_shared_nh']+branch*(1+(n-1)*c['assumed_branch_coupling_k'])/n
            rows.append(dict(parallel_count=n,h_mm=h,local_copper_only_nh=local,ideal_uncoupled_bank_copper_only_nh=local/n,assumed_common_mode_total_nh=estimate))
    with (out/'geometry_estimates.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    fig,ax=plt.subplots(figsize=(8,5),layout='constrained')
    for h in c['layer_separations_mm']:
        r=[r for r in rows if r['h_mm']==h]
        ax.plot([v['parallel_count'] for v in r],[v['assumed_common_mode_total_nh'] for v in r],marker='o',label=f'Layer separation {h:g} mm')
    ax.set(xlabel='Parallel devices per switch position',ylabel='Assumed common-mode inductance (nH)',title='Geometry sensitivity — not extracted PCB inductance',xticks=c['parallel_counts'])
    ax.grid(alpha=.25);ax.legend()
    fig.supxlabel('10 mm overlap, 3 mm effective branch width; extra branch 0.5 nH, shared 0.3 nH, k = 0.2 assumed',fontsize=8)
    fig.savefig(out/'geometry_sensitivity.png',dpi=160)
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()

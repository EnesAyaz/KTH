"""Run the canonical 4/5/6 parallel half-bridge design study."""
from pathlib import Path
import sys,json,csv,argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from models.half_bridge import evaluate,validate

def write_csv(path,rows):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(config=ROOT/'data/inputs/design.json'):
 c=json.loads(Path(config).read_text(encoding='utf-8-sig'));d=json.loads((ROOT/'data/devices/epc2361.json').read_text());validate(c,d)
 out=ROOT/'results/design';out.mkdir(parents=True,exist_ok=True)
 freqs=np.arange(c['frequency_min_hz'],c['frequency_max_hz']+1,c['frequency_step_hz'])
 rows=[evaluate(c,d,m,f,n) for m in c['modulations'] for n in c['parallel_counts'] for f in freqs]
 write_csv(out/'sweep.csv',rows)
 best=[]
 for mode in c['modulations']:
  for n in c['parallel_counts']:
   passed=[r for r in rows if r['modulation']==mode['method'] and r['parallel_count']==n and r['passes_assumption_screen']]
   if passed:best.append(max(passed,key=lambda r:r['frequency_hz']))
 summary=dict(inputs=c,device=d,highest_frequency_per_configuration=best,points_at_100khz=[r for r in rows if r['frequency_hz']==100000],evidence_status='Screening only: parallel-bank SPICE characterization remains required')
 (out/'summary.json').write_text(json.dumps(summary,indent=2))
 if best:write_csv(out/'highest_frequency.csv',best)
 elif (out/'highest_frequency.csv').exists():(out/'highest_frequency.csv').unlink()
 fig,axs=plt.subplots(2,2,figsize=(11,8),layout='constrained')
 for mode in c['modulations']:
  for n in c['parallel_counts']:
   s=[r for r in rows if r['modulation']==mode['method'] and r['parallel_count']==n]
   for ax,key in zip(axs.flat,['efficiency_pct','junction_c','max_coldplate_k_w_per_halfbridge','allowed_mean_switching_pair_uj_per_device']):
    ax.plot([r['frequency_hz']/1000 for r in s],[r[key] for r in s],label=f"{mode['method']} N={n}",ls='-' if mode['method']=='SVM' else '--')
    ax.set_xlabel('Switching frequency (kHz)');ax.grid(alpha=.25)
 for ax,label in zip(axs.flat,['Three-phase efficiency estimate (%)','Junction estimate (C)','Max plate-to-water R per half bridge (K/W)','Allowed mean Eon+Eoff per device (uJ)']):ax.set_ylabel(label)
 axs[0,0].axhline(c['efficiency_target_pct'],color='black',ls=':');axs[0,0].legend(fontsize=8)
 axs[0,1].axhline(125,color='black',ls=':')
 fig.suptitle('Half-bridge design screening | losses averaged over a sinusoidal fundamental\nCurves include points failing current or minimum-pulse constraints; see CSV',fontsize=12)
 fig.savefig(out/'design.png',dpi=150);plt.close(fig)
 fig,axs=plt.subplots(2,1,figsize=(10,7),layout='constrained')
 for mode in c['modulations']:
  _,wave=evaluate(c,d,mode,100000,6,True)
  write_csv(out/f"cycle_{mode['method'].lower()}_n6_100khz.csv",[dict(zip(wave,vals)) for vals in zip(*wave.values())])
  axs[0].plot(wave['angle_deg'],wave['phase_current_a'],label=mode['method'])
  axs[1].plot(wave['angle_deg'],wave['high_device_carrier_average_w'],label=mode['method']+' upper')
  axs[1].plot(wave['angle_deg'],wave['low_device_carrier_average_w'],ls='--',label=mode['method']+' lower')
 for ax in axs:ax.set_xlabel('Fundamental electrical angle (deg)');ax.grid(alpha=.25);ax.legend()
 axs[0].set_ylabel('Phase current (A)');axs[1].set_ylabel('Per-device carrier-average loss (W)')
 fig.suptitle('Sinusoidal-cycle integration | N=6, 100 kHz diagnostic (not a qualified point)')
 fig.savefig(out/'fundamental_cycle.png',dpi=150);plt.close(fig)
 print(json.dumps(best,indent=2));return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=ROOT/'data/inputs/design.json');run(p.parse_args().config)

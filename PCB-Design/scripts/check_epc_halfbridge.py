from pathlib import Path
import json
r=Path.cwd()
namespace={'__file__':str(r/'scripts/check_lmg1210_modes.py')}
exec((r/'scripts/check_lmg1210_modes.py').read_text().split('results={}')[0],namespace)
p=r/'simulation/LMG1210-EPC2361/LMG1210_EPC2361_halfbridge'
log=namespace['decoded'](p.with_suffix('.log'))
if 'Total elapsed time:' not in log:
 print(log[-1800:]);raise SystemExit('Simulation not complete')
print(log[-2500:])
names,runs=namespace['raw'](p.with_suffix('.raw'))
ix={n:i for i,n in enumerate(names)}
rows=[v for v in runs[0] if v[0]>330e-6]
def series(a,b=None):return [v[ix[a]]-(v[ix[b]] if b else 0) for v in rows]
vals={n:series(a,b) for n,a,b in [('vgs_high','v(gh)','v(sw)'),('vgs_low','v(gl)',None),('bootstrap','v(hb)','v(sw)'),('switch_node','v(sw)',None),('load_current','i(lload)',None)]}
res={n:{'min':min(v),'max':max(v)} for n,v in vals.items()}
res['frequency_hz']=50000
res['both_gates_above_2p5V']=any(a>2.5 and b>2.5 for a,b in zip(vals['vgs_high'],vals['vgs_low']))
res['functional_pass']=min(vals['bootstrap'])>3.8 and max(vals['vgs_high'])>4 and max(vals['vgs_low'])>4 and max(vals['switch_node'])>70 and min(vals['switch_node'])<1 and not res['both_gates_above_2p5V']
(p.parent/'results.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
assert res['functional_pass']
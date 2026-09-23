"""Bounded GUI and loss regression checks; reuses the saved validation waveform."""
from pathlib import Path
import json,subprocess
import dpt_gui as d
from half_bridge_losses import analyze
BASE=Path(__file__).resolve().parent
f=BASE/'half_bridge_validation/losses/HalfBridge'
v=d.normalize_settings(json.loads(f.with_suffix('.json').read_text()))
rows,notes,data=analyze(f.with_suffix('.raw'),d.validate(v))
for name in ('Upper','Lower'):
 q=data[name]
 assert abs(sum(q[k] for k in ('on_W','off_W','conduction_W','deadtime_W','other_W'))-q['total_W'])<1e-8
 assert abs(q['on_W']-q['Eon_uJ']*1e-6*d.number(v['Fsw']))<1e-8
 assert all(q[k]>=-1e-6 for k in ('on_W','off_W','conduction_W','deadtime_W','other_W'))
for mode in (0,1):
 app=d.App(mode);app.withdraw();app.preview();assert d.validate(app.values())['Mode']==mode
 def widgets(w):
  yield w
  for child in w.winfo_children():yield from widgets(child)
 tabs=[w for w in widgets(app) if isinstance(w,d.ttk.Notebook)][0]
 labels=[tabs.tab(x,'text') for x in tabs.tabs()]
 assert ('Half-bridge PWM' in labels)==bool(mode)
 assert 'Conduction loss' not in labels
 app.reset();assert d.validate(app.values())['Mode']==mode;app.destroy()
b=f.with_suffix('.log').read_bytes();log=b.decode('utf-16-le' if b'\0' in b[:100] else 'utf-8',errors='replace')
r,n=d.result_summary(log,v,f.with_suffix('.raw'));assert len([x for x in r if 'Total channel' in x[0]])==2
assert not any('Unavailable; rerun' in x[1] for x in r)
d.export(v,f.with_suffix('.asc'))
subprocess.run([d.find_ltspice(),'-netlist',str(f.with_suffix('.asc'))],cwd=f.parent,check=True,timeout=30)
b=f.with_suffix('.net').read_bytes();net=b.decode('utf-16-le' if b'\0' in b[:100] else 'utf-8',errors='replace')
assert any(x.lower().startswith('xhs ') for x in net.splitlines())
assert any(x.lower().startswith('xdut ') for x in net.splitlines())
print('PASS: separate GUI modes, reset, loss partition closure, E*f conversion, result display and matching ASC/CIR device names.')
print(json.dumps(data,indent=2))

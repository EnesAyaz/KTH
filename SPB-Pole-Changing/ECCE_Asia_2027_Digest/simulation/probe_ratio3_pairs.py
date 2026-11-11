from pathlib import Path
import sys,itertools,json
import numpy as np
ROOT=Path(__file__).resolve().parent
Q=36;pH=6;pL=2
zH=np.exp(2j*np.pi*pH*np.arange(Q)/Q);zL=np.exp(2j*np.pi*pL*np.arange(Q)/Q)
def key(h,l):return tuple(round(float(v),8) for v in [h.real,h.imag,l.real,l.imag])
legs={};alllegs=[]
for a,b in itertools.combinations(range(Q),2):
 for sa,sb in [(1,1),(1,-1),(-1,1),(-1,-1)]:
  h=sa*zH[a]+sb*zH[b];l=sa*zL[a]+sb*zL[b]
  if abs(h)<1e-7 or abs(l)<1e-7:continue
  item={'slots':(a,b),'signs':(sa,sb),'h':h,'l':l,'mask':(1<<a)|(1<<b)}
  alllegs.append(item);legs.setdefault(key(h,l),[]).append(item)
rot=np.exp(2j*np.pi/3);cells={}
for leg in alllegs:
 for sh,sl in itertools.product([1,-1],repeat=2):
  bvals=legs.get(key(leg['h']*rot**sh,leg['l']*rot**sl),[])
  cvals=legs.get(key(leg['h']*rot**(2*sh),leg['l']*rot**(2*sl)),[])
  for b in bvals:
   if leg['mask']&b['mask']:continue
   for c in cvals:
    mask=leg['mask']|b['mask']|c['mask']
    if (leg['mask']|b['mask'])&c['mask']:continue
    # All cells in a cover should have equal induced-voltage magnitude.
    gain=(round(abs(leg['h']),7),round(abs(leg['l']),7))
    cells.setdefault(gain,{}).setdefault(mask,(leg,b,c))
print('gain groups',[(g,len(cs)) for g,cs in cells.items()])
solutions=[]
for gain,cs in sorted(cells.items(),key=lambda it:min(it[0]),reverse=True):
 byslot={k:[] for k in range(Q)}
 for mask,v in cs.items():
  for k in range(Q):
   if mask>>k&1:byslot[k].append(mask)
 target=(1<<Q)-1;tries=[0]
 def cover(used,path):
  tries[0]+=1
  if tries[0]>200000:return None
  if used==target:return path
  un=[k for k in range(Q) if not(used>>k&1)]
  options=min(([m for m in byslot[k] if not(m&used)] for k in un),key=len)
  for mask in options:
   result=cover(used|mask,path+[mask])
   if result:return result
  return None
 found=cover(0,[])
 if found:
  solution={'Q':Q,'N':6,'pH':pH,'pL':pL,'per_leg_phasor_gain_H_L':gain,'cells':[[{'slots':[s+1 for s in leg['slots']],'signs':leg['signs']} for leg in cs[mask]] for mask in found]}
  solutions.append(solution);break
(ROOT/'results_three_phase'/'ratio3_pair_leg_probe.json').write_text(json.dumps({'solutions':solutions,'gain_groups':[(str(k),len(v)) for k,v in cells.items()]},indent=2))
print(json.dumps(solutions,indent=2))

from pathlib import Path
import struct,re,json
p=Path('simulation/LMG1210-EPC2361/Parasitics_Check')
b=p.with_suffix('.log').read_bytes(); log=b.decode('utf-16le' if b'\0' in b[:100] else 'utf-8',errors='replace')
if 'Total elapsed time:' not in log:print('Run still in progress');raise SystemExit(2)
print(log[-2200:])
b=p.with_suffix('.raw').read_bytes();enc='utf-16le' if b'\0' in b[:100] else 'utf-8'
marker='Binary:\n'.encode(enc);k=b.find(marker)
if k<0:marker='Binary:\r\n'.encode(enc);k=b.find(marker)
assert k>0
head=b[:k].decode(enc);names=[m[1].lower() for m in re.finditer(r'^\s*\d+\s+(\S+)\s+\S+',head.rsplit('Variables:',1)[1],re.M)]
ix={n:j for j,n in enumerate(names)};fmt=struct.Struct('<d'+'f'*(len(names)-1))
queries={'VGS_H':('v(gh)','v(sw)'),'VGS_L':('v(gl)',None),'VDS_H':('v(dh)','v(sw)'),'VDS_L':('v(sw)',None),'VBOOT':('v(hb)','v(sw)'),'IG_H':('i(lgh)',None),'IG_L':('i(lgl)',None)}
out={n:[float('inf'),float('-inf')] for n in queries};both=0;count=0
for row in fmt.iter_unpack(memoryview(b)[k+len(marker):]):
 if row[0]<330e-6:continue
 count+=1
 for n,(a,c) in queries.items():
  v=row[ix[a]]-(row[ix[c]] if c else 0);out[n][0]=min(out[n][0],v);out[n][1]=max(out[n][1],v)
 both+=int(row[ix['v(gh)']]-row[ix['v(sw)']]>2.5 and row[ix['v(gl)']]>2.5)
res={'range_min_max':out,'samples_330us_to_400us':count,'both_gates_over_2p5V_samples':both,'simulation_completed':True}
p.with_name('Parasitics-results.json').write_text(json.dumps(res,indent=2))
print(json.dumps(res,indent=2))
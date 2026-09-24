"""Check saved LTspice binary traces for both driver-only mode tests."""
from pathlib import Path
import re, struct, json
root=Path(__file__).resolve().parents[1]/'simulation/LMG1210-modes'
def decoded(path):
    b=path.read_bytes()
    return b.decode('utf-16le' if b'\x00' in b[:100] else 'utf-8',errors='replace')
def raw(path):
    b=path.read_bytes();wide=b'\x00' in b[:100];enc='utf-16le' if wide else 'utf-8'
    marker='Binary:\n'.encode(enc);k=b.find(marker)
    if k<0:
        marker='Binary:\r\n'.encode(enc);k=b.find(marker)
    assert k>=0,'No binary data'
    header=b[:k].decode(enc);nv=int(re.search(r'No. Variables:\s*(\d+)',header)[1]);np=int(re.search(r'No. Points:\s*(\d+)',header)[1])
    names=[m[1].lower() for m in re.finditer(r'^\s*\d+\s+(\S+)\s+\S+',header.rsplit('Variables:',1)[1],re.M)]
    fmt=struct.Struct('<d'+'f'*(nv-1));data=b[k+len(marker):]
    assert len(data)==np*fmt.size,(len(data),np,fmt.size)
    offset=float(re.search(r'Offset:\s*(\S+)',header)[1]) if 'Offset:' in header else 0
    rows=[(r[0]+offset,*r[1:]) for r in fmt.iter_unpack(data)];runs=[];start=0
    for j in range(1,len(rows)):
        if rows[j][0]<rows[j-1][0]:runs.append(rows[start:j]);start=j
    runs.append(rows[start:]);return names,runs
def edges(t,v,rising):
    result=[]
    for j in range(1,len(t)):
        a,c=v[j-1]-2.5,v[j]-2.5
        if (a<0<=c) if rising else (a>0>=c):
            result.append(t[j-1]+(t[j]-t[j-1])*(-a)/(c-a))
    return result
results={}
for mode in ['IIM','PWM']:
    stem=root/f'LMG1210_{mode}_test'
    log=decoded(stem.with_suffix('.log'))
    assert 'Total elapsed time:' in log,mode+' still running or failed'
    names,runs=raw(stem.with_suffix('.raw'));assert len(runs)==2
    tests=[]
    for hz,rows in zip([50000,100000],runs):
        ix={n:j for j,n in enumerate(names)}
        rows=[r for r in rows if r[0]>300.5e-6]
        t=[r[0] for r in rows];ho=[r[ix['v(ho)']]-r[ix['v(hs)']] for r in rows];lo=[r[ix['v(lo)']] for r in rows]
        both_high=any(a>2.5 and c>2.5 for a,c in zip(ho,lo))
        dead=[]
        for a,c in [(ho,lo),(lo,ho)]:
            falls=edges(t,a,False)
            for rise in edges(t,c,True):
                prev=[f for f in falls if 0<rise-f<1/hz/4]
                if prev:dead.append((rise-max(prev))*1e9)
        vdd=rows[-1][ix['v(vdd)']]
        passed=(4.5<vdd<5.5 and 4.5<max(ho)<5.6 and 4.5<max(lo)<5.6 and min(ho)<.2 and min(lo)<.2 and not both_high and len(dead)>0)
        tests.append(dict(frequency_hz=hz,vdd_final_v=vdd,ho_range_v=[min(ho),max(ho)],lo_range_v=[min(lo),max(lo)],both_outputs_above_2p5V=both_high,dead_time_50percent_crossings_ns=[min(dead),max(dead)] if dead else [],functional_pass=passed))
    results[mode]=tests
(root/'mode-test-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
assert all(t['functional_pass'] for tests in results.values() for t in tests),'Functional test failed'

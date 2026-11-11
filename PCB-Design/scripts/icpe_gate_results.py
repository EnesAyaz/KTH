"""Measure saved LTspice waveforms, accounting for RAW time offsets and stepped runs."""
from pathlib import Path
import numpy as np,re,json

def read_raw(path):
    data=Path(path).read_bytes()
    enc='utf-16-le' if b'\0' in data[:100] else 'latin1'
    marker='Binary:\n'.encode(enc)
    k=data.index(marker)+len(marker)
    header=data[:k].decode(enc)
    nv=int(re.search(r'No. Variables:\s*(\d+)',header)[1])
    nn=int(re.search(r'No. Points:\s*(\d+)',header)[1])
    offset=float(re.search(r'Offset:\s*(\S+)',header)[1]) if 'Offset:' in header else 0
    names=re.findall(r'^\t\d+\t(\S+)\t',header,re.M)
    dt=np.dtype([('t','<f8')]+[(str(i),'<f4') for i in range(1,nv)])
    a=np.frombuffer(data,dt,count=nn,offset=k)
    times=np.abs(a['t'])+offset
    cuts=np.r_[0,np.flatnonzero(np.diff(times)<0)+1,nn]
    runs=[]
    for left,right in zip(cuts[:-1],cuts[1:]):
        runs.append({n.lower():(times[left:right] if j==0 else a[str(j)][left:right].astype(float)) for j,n in enumerate(names)})
    return runs

T1=11.167e-6
T2=12.167e-6

def window(z,y,start,end):
    t=z['time'];ok=(t>start)&(t<end)
    return np.r_[start,t[ok],end],np.r_[np.interp(start,t,y),y[ok],np.interp(end,t,y)]

def energy(z,v,i,t0):
    t,y=window(z,v*i,t0,t0+150e-9)
    return float(np.trapezoid(y,t))

def extrema(z,y,t0,tend,mode='max'):
    _,v=window(z,y,t0,tend)
    return float(np.max(v) if mode=='max' else np.min(v))

def single(path):
    from icpe_gate_loop_rerun import readlog
    txt=readlog(Path(path).with_suffix('.log'))
    steps=[float(v) for v in re.findall(r'^\.step ipk=([\d.eE+\-]+)',txt,re.M)]
    runs=read_raw(Path(path).with_suffix('.raw'))
    assert len(runs)==len(steps),(len(runs),len(steps),path)
    out=[]
    for ipk,z in zip(steps,runs):
        vl=z['v(dl)']-z['v(sl)'];vh=z['v(dh)']-z['v(sw)'];gl=z['v(gl)']-z['v(sl)'];gh=z['v(gh)']-z['v(sw)'];il=z['i(vil)']
        out.append(dict(ipk=ipk,iload=float(np.interp(T1,z['time'],il)),eon=energy(z,vl,il,T2),eoff=energy(z,vl,il,T1),vdsl_pk=extrema(z,vl,T1,T1+150e-9),vdsh_pk=extrema(z,vh,T2,T2+150e-9),vgsh_bump=extrema(z,gh,T2,T2+150e-9),vgsl_max=extrema(z,gl,T1-100e-9,z['time'][-1]),vgsl_min=extrema(z,gl,T1-100e-9,z['time'][-1], 'min'),vgsh_min=extrema(z,gh,T1-100e-9,z['time'][-1],'min')))
    Path(path).with_suffix('.json').write_text(json.dumps(out,indent=2))
    return out

def board(path):
    z=read_raw(Path(path).with_suffix('.raw'))[0]
    out={'iload':float(np.interp(T1,z['time'],z['i(lload)']))}
    for k in range(1,5):
        vl=z[f'v(dl{k})']-z[f'v(ql_s_{k})'];vh=z[f'v(dh{k})']-z[f'v(qh_s_{k})'];gl=z[f'v(gl{k})']-z[f'v(ql_s_{k})'];gh=z[f'v(gh{k})']-z[f'v(qh_s_{k})'];il=z[f'i(vil{k})']
        out.update({f'eon{k}':energy(z,vl,il,T2),f'eoff{k}':energy(z,vl,il,T1),f'vpk{k}':extrema(z,vl,T1,T1+150e-9),f'vhpk{k}':extrema(z,vh,T2,T2+150e-9),f'bump{k}':extrema(z,gh,T2,T2+150e-9),f'glmax{k}':extrema(z,gl,T1-100e-9,z['time'][-1]),f'glmin{k}':extrema(z,gl,T1-100e-9,z['time'][-1],'min'),f'ghmin{k}':extrema(z,gh,T1-100e-9,z['time'][-1],'min')})
    Path(path).with_suffix('.json').write_text(json.dumps(out,indent=2))
    return out

if __name__=='__main__':
    from icpe_gate_loop_rerun import RUN,readlog
    for p in RUN.glob('*.cir'):
        if not p.with_suffix('.log').exists():continue
        log=readlog(p.with_suffix('.log'))
        if 'Total elapsed time:' not in log:continue
        r=single(p) if p.stem.startswith('single') else board(p)
        print(p.stem,len(r))

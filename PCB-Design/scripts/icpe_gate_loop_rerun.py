"""Reproducible isolated LTspice sweeps for the ICPE manuscript gate-loop update."""
from pathlib import Path
import subprocess, re, json, time, sys
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'simulation/bb_spice/icpe_gate_loop_2026-11-02'
LTS=Path.home()/'AppData/Local/Programs/ADI/LTspice/LTspice.exe'
RUN.mkdir(exist_ok=True)

def readlog(path):
    raw=path.read_bytes()
    return raw.decode('utf-16-le') if b'\0' in raw[:200] else raw.decode('latin1')

def parse(path):
    txt=readlog(path).replace('\r\n','\n')
    steps=[{k.lower():float(v) for k,v in re.findall(r'(\w+)=([\-\d.eE+]+)',s)} for s in re.findall(r'^\.step (.*)$',txt,re.M)]
    meas={}
    for m in re.finditer(r'Measurement: (\w+)\n\s+step\t[^\n]*\n((?:\s+\d+\t[^\n]*\n)+)',txt):
        meas[m[1].lower()]=[float(r.split('\t')[1]) for r in m[2].strip('\n').split('\n')]
    if not steps or not meas:raise RuntimeError('Missing stepped measurements: '+str(path)+'\n'+txt[-1500:])
    return [{**s,**{k:vals[i] for k,vals in meas.items()}} for i,s in enumerate(steps)]

def prepare(lg,lp,roff=0,ron=2,dt=.1,bias=0,currents=None,suffix=''):
    name=f'single_g{lg:g}_p{lp:g}_on{ron:g}_off{roff:g}'+suffix
    body=(ROOT/'simulation/bb_spice/FLOW_lumped.inc').read_text()
    model=(ROOT/'simulation/LMG1210-EPC2361/EPC2361.lib').as_posix()
    body=body.replace('.include ../LMG1210-EPC2361/EPC2361.lib',f'.include "{model}"')
    body=re.sub(r'LG=\S+',f'LG={lg}n',body)
    if bias:
        body=body.replace('VHO ho SW 0',f'VHO ho SW {bias}')
        old='PWL(0 0 {TSTART} 0 {TSTART+1n} {VDRV} {T1} {VDRV} {T1+1n} 0 {T2} 0 {T2+1n} {VDRV} {T2+TON2} {VDRV} {T2+TON2+1n} 0)'
        new=f'PWL(0 {bias} {{TSTART}} {bias} {{TSTART+1n}} {{VDRV}} {{T1}} {{VDRV}} {{T1+1n}} {bias} {{T2}} {bias} {{T2+1n}} {{VDRV}} {{T2+TON2}} {{VDRV}} {{T2+TON2+1n}} {bias})'
        body=body.replace(old,new)
    body=body.replace('.tran 0 {TEND} 0 0.1n',f'.tran 0 {{TEND}} {{T1-200n}} {dt}n')
    # The saved RAW interval has a nonzero Offset. Use the common RAW postprocessor
    # rather than native .meas windows, which are not offset consistently by this release.
    body='\n'.join(ln for ln in body.splitlines() if not ln.lower().startswith('.meas'))+'\n'
    # Supplement the current grid near the candidate parallel-count operating points.
    ipk=4*300000/(3*1.15*1200*.9)
    currents=currents or sorted(set([1,10,20,40,60,80,100,120,160,200,250,330]+[round(ipk/n,6) for n in range(2,9)]))
    top=f'* ICPE single-cell gate-loop sweep, LG={lg} nH, Lpower={lp} nH\n.param VBUS=75 TON1=10.667u LLOAD={{TON1*VBUS/IPK}} RGON={ron} RGOFF={roff} RPU=0.85 RPD=0.35 LLOOP={lp}n\n.step param IPK list '+' '.join(map(str,currents))+'\n'
    path=RUN/(name+'.cir');path.write_text(top+body+'\n.end\n')
    return path

def run(path):
    start=time.time()
    result=subprocess.run([str(LTS),'-b','-Run',str(path)],cwd=RUN,capture_output=True,timeout=1200)
    log=path.with_suffix('.log')
    if result.returncode or not log.exists():raise RuntimeError(str(path)+repr(result))
    from icpe_gate_results import single
    rows=single(path)
    path.with_suffix('.json').write_text(json.dumps(rows,indent=2))
    print(path.stem,len(rows),'steps',round(time.time()-start,1),'s',flush=True)
    return rows

if __name__=='__main__':
    jobs=[prepare(g,l,1,3,.5,-1,[1,10,30,50,65,82,110,165],'_biasminus1') for g in [10,20] for l in [.5,1]]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(run,jobs))
    jobs=[prepare(g,.5,1,3,.1,-1,[80,82],'_biasminus1_fine') for g in [10,20]]
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,jobs))

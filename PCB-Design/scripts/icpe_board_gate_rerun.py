"""Rerun routed power networks with 10/20 nH lumped gate paths and the extracted DPT network."""
from pathlib import Path
import re,json,subprocess,time
from concurrent.futures import ThreadPoolExecutor
from icpe_gate_loop_rerun import ROOT,RUN,LTS,readlog

def prepare(board,lg,ron,bias=None,roff=None):
    tag=f'board_{board}_g{lg}_on{ron:g}'+('_revised_drive' if bias is not None else '')
    src={'load':'REVB_Q3D_load.cir','dpt':'REVB_Q3D_dpt_lumpgate.cir','extracted':'REVB_Q3D_dpt.cir'}[board]
    body=(ROOT/'simulation/bb_spice'/src).read_text()
    body=body.replace('.include ../LMG1210-EPC2361/EPC2361.lib',f'.include "{(ROOT/"simulation/LMG1210-EPC2361/EPC2361.lib").as_posix()}"')
    body=re.sub(r'RGON=\S+',f'RGON={ron}',body)
    if board=='extracted':
        # Extracted network uses one common resistor plus 0.5 ohm per gate.
        # Under equal pair currents the effective per-device value is 2*Rcommon+0.5.
        body=re.sub(r'^(Ron[HL][AB]\s+\S+\s+\S+) \S+$',rf'\g<1> {(ron-.5)/2:g}',body,flags=re.M)
    if roff is not None:body=re.sub(r'RGOFF=\S+',f'RGOFF={roff}',body)
    if bias is not None:
        body=re.sub(r'^(VHO\w+\s+\S+\s+\S+) 0$',rf'\g<1> {bias}',body,flags=re.M)
        old='PWL(0 0 {TSTART} 0 {TSTART+1n} {VDRV} {T1} {VDRV} {T1+1n} 0 {T2} 0 {T2+1n} {VDRV} {T2+TON2} {VDRV} {T2+TON2+1n} 0)'
        new=f'PWL(0 {bias} {{TSTART}} {bias} {{TSTART+1n}} {{VDRV}} {{T1}} {{VDRV}} {{T1+1n}} {bias} {{T2}} {bias} {{T2+1n}} {{VDRV}} {{T2+TON2}} {{VDRV}} {{T2+TON2+1n}} {bias})'
        body=body.replace(old,new)
    if board!='extracted':
        # Fixed split preserves the existing topology; the complete branch loop is LG.
        body=re.sub(r'LGO=\S+ LGK=\S+',f'LGO={lg*.7:g}n LGK={lg*.3:g}n',body)
    body=body.replace('.tran 0 {TEND} 0 0.1n','.tran 0 {TEND} {T1-200n} 0.1n')
    extra=''
    for k in range(1,5):
        for name,op,expr in [('glmax','MAX',f'V(gL{k},QL_S_{k})'),('glmin','MIN',f'V(gL{k},QL_S_{k})'),('ghmin','MIN',f'V(gH{k},QH_S_{k})')]:
            extra+=f'.meas TRAN {name}{k} {op} {expr} FROM {{T1-100n}} TO {{TEND}}\n'
    body=re.sub(r'^\.end\s*$',extra+'.end',body,flags=re.M)
    body='\n'.join(ln for ln in body.splitlines() if not ln.lower().startswith('.meas'))+'\n'
    path=RUN/(tag+'.cir');path.write_text(body);return path

def run(path):
    start=time.time();r=subprocess.run([str(LTS),'-b','-Run',str(path)],cwd=RUN,capture_output=True,timeout=1800)
    txt=readlog(path.with_suffix('.log'))
    if r.returncode or 'Total elapsed time' not in txt:raise RuntimeError(str(path)+' '+txt[-1000:])
    from icpe_gate_results import board
    vals=board(path)
    path.with_suffix('.json').write_text(json.dumps(vals,indent=2))
    print(path.stem,round(time.time()-start,1),'s',json.dumps({k:v for k,v in vals.items() if k in ['iload','vhpk1','eon1','bump1']}),flush=True)
    return vals

if __name__=='__main__':
    jobs=[prepare('load',g,r) for g in [10,20] for r in [2,3]]+[prepare('load',g,3,-1,1) for g in [10,20]]+[prepare('dpt',g,3.5) for g in [10,20]]+[prepare('extracted',0,r) for r in [2.5,3.5]]
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,jobs))

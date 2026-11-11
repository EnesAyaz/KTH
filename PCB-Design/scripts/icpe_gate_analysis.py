"""Fundamental-period loss and thermal calculation using the rerun switching maps."""
from pathlib import Path
import sys,json,math,csv
import numpy as np
from icpe_gate_loop_rerun import ROOT,RUN

Ipk=4*300000/(3*1.15*1200*.9)
Irms=Ipk/math.sqrt(2)
Rjh=.2+.4e-3/(5*15e-6)+2*.008/(200*.0128*.003)
temps=np.array([0,25,50,75,100,125,150])
factors=np.array([.84,1,1.16,1.33,1.49,1.65,1.8])
OUT=ROOT/'reports/paper/icpe/gate_loop_rerun_2026-11-02'
OUT.mkdir(exist_ok=True)

def maps(g,l):
    rows=json.loads((RUN/f'single_g{g}_p{l:g}_on3_off1_biasminus1.json').read_text())
    # Refined candidate-current checks replace the coarse samples near the decision.
    fine=RUN/f'single_g{g}_p{l:g}_on3_off1_biasminus1_fine.json'
    if fine.exists():
        refined=json.loads(fine.read_text())
        rows=[r for r in rows if r['ipk'] not in [a['ipk'] for a in refined]]+refined
        rows.sort(key=lambda r:r['iload'])
    return rows

def calculate(rows,n):
    x=np.array([r['iload'] for r in rows]);order=np.argsort(x);x=x[order]
    get=lambda k:np.array([r[k] for r in rows])[order]
    theta=np.linspace(0,np.pi,4001);i=Ipk*np.sin(theta)/n
    # Same semiconductor accounting as the established study, with updated energy maps.
    en=np.interp(i,x,get('eon'))+np.interp(i,x,get('eoff'))
    sw=n*50000*float(np.trapezoid(en,theta)/np.pi)+n*2.9e-6*50000
    ia=i*n
    dead=2*50000*10e-9*float(np.trapezoid(ia*(1.95+.005*ia/n),theta)/np.pi)
    gate=2*n*28e-9*6*50000
    tj=40
    valid=True
    for _ in range(300):
        if tj>150:valid=False;break
        cond=Irms**2*.00075*float(np.interp(tj,temps,factors))/n
        sem=cond+sw+dead
        updated=40+.65*sem+Rjh*sem/(2*n)
        if abs(updated-tj)<1e-7:tj=updated;break
        tj=updated
    # Device stress is the larger of low-side turn-off and high-side turn-on peaks.
    vls=float(np.interp(Ipk/n,x,get('vdsl_pk')))
    vhs=float(np.interp(Ipk/n,x,get('vdsh_pk')))
    return dict(n=n,ipeak=Ipk/n,cond=cond,sw=sw,dead=dead,gate=gate,tot=cond+sw+dead+gate,tj=tj,thermal_valid=valid,vls=vls,vhs=vhs,vpk=max(vls,vhs),bump=float(np.interp(Ipk/n,x,get('vgsh_bump'))))

def main():
    out={'assumptions':dict(Ipk=Ipk,Irms=Irms,Rjh=Rjh,Rsa=.65,Ta=40,Rgon=3,Rgoff=1,Voff=-1,Vg_on=5,f_sw=50000), 'single':{},'parallel':{},'boards':{}}
    for g in [10,20]:
        for l in [.5,1]:
            key=f'g{g}_p{l:g}';rows=maps(g,l);out['single'][key]=rows
            out['parallel'][key]=[calculate(rows,n) for n in range(2,9)]
    for path in RUN.glob('board*.json'):out['boards'][path.stem]=json.loads(path.read_text())
    (OUT/'results.json').write_text(json.dumps(out,indent=2))
    with (OUT/'parallel_count_results.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['gate_loop_nH','parallel_count','device_peak_A','leg_loss_W','junction_C','worst_Vds_0p5nH_V','worst_Vds_1nH_V','held_off_gate_0p5nH_V'])
        for g in [10,20]:
            for a,b in zip(out['parallel'][f'g{g}_p0.5'],out['parallel'][f'g{g}_p1']):
                w.writerow([g,a['n'],a['ipeak'],a['tot'],a['tj'] if a['thermal_valid'] else '>150',a['vpk'],b['vpk'],a['bump']])
    for g in [10,20]:
        print('GATE',g)
        for a,b in zip(out['parallel'][f'g{g}_p0.5'],out['parallel'][f'g{g}_p1']):print(a['n'],*(round(a[k],2) for k in ['tot','tj','vls','vhs','bump']),round(b['vpk'],2))

if __name__=='__main__':main()

from pathlib import Path
import subprocess, hashlib, json
P=Path(__file__).parent
EXE=r'C:/Users/enesa/AppData/Local/Programs/ADI/LTspice/LTspice.exe'
MAIN=Path(r'C:/Github/OPT-Bipolar-Field-Excitation/IEEEtran/main_18slot_p5.tex')
(P/'main_before.sha256').write_text(hashlib.sha256(MAIN.read_bytes()).hexdigest())
for case,protected,shade,off,step in [('reversal',True,False,False,'100u'),('reversal_fine',True,False,False,'50u'),('reference',False,False,False,'100u'),('deexcitation',True,False,True,'100u'),('shaded_one',True,True,False,'100u')]:
    lines=['Motor-matched bipolar OPT review: Ns=1, Np=6; generic device models',
    '* Existing 25-device array fit scaled to one VMJ device; NOT independently measured cell data.',
    '* Vbr=150 V assumed; Zener model generic; constant temperature and inductance.',
    '.param iph=0.136 voc=35.8 avt=1.3 rser=16.75 rsh=50k',
    '.param vth=1.380649e-23*300.15/1.602176634e-19',
    '.param is0=(iph-voc/rsh)/(exp(voc/avt)-1)',
    '.model CELL D(Is={is0} N={avt/vth} BV=150 IBV=40n NBV={2/vth})',
    '.model ZENER D(Is=1e-14 BV=35.0272 IBV=1m Rs=0.2)',
    '.model BLOCK D(Is=1u N=1.2 Rs=0.03 BV=1k)',
    'Rf a w 37.2','Lf w 0 7.63']
    for group,pos,neg in [('p','a','0'),('n','0','a')]:
        for k in range(1,7):
            name=f'{group}{k}'
            start=1 if group=='p' else 0
            end=(0 if off else (1 if group=='n' else 0))
            if shade: end=(0 if k==1 else 1) if group=='p' else 0
            lines += [f'I{name} {neg} j{name} PWL(0 {{{start}*iph}} .5 {{{start}*iph}} .50001 {{{end}*iph}})',f'Rs{name} j{name} {pos} {{rser}}',f'Rp{name} j{name} {neg} {{rsh}}',f'D{name} j{name} {neg} CELL']
            if protected: lines += [f'Db{name} {neg} z{name} BLOCK',f'Dz{name} {pos} z{name} ZENER']
    lines += ['.options plotwinsize=0 reltol=1e-5','.save V(a) I(Lf) V(jp1) I(Rsp1)']
    if protected: lines += ['.save I(Dbp1) I(Dbn1) V(zp1) V(zn1)']
    lines += [f'.tran 0 2 0 {step}', '.end']
    f=P/(case+'.cir');f.write_text('\n'.join(lines)+'\n')
    r=subprocess.run([EXE,'-b',str(f)],capture_output=True,timeout=120)
    print(case,'exit',r.returncode,'raw',(P/(case+'.raw')).exists(),flush=True)

for name,bv in [('reversal_clamp37',36.5),('reversal_clamp40',39.5)]:
    f=P/(name+'.cir')
    f.write_text((P/'reversal.cir').read_text().replace('BV=35.0272',f'BV={bv}'))
    r=subprocess.run([EXE,'-b',str(f)],capture_output=True,timeout=120)
    print(name,'exit',r.returncode,flush=True)

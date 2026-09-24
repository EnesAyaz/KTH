"""Readable native LTspice PWM and IIM driver-only tests."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'simulation/LMG1210-modes';out.mkdir(exist_ok=True)
old=root/'simulation/LMG1210-test'
for fn in ['test_voltage.asy','test_cap.asy']:shutil.copy2(old/fn,out/fn)
(out/'test_res.asy').write_text('Version 4\nSymbolType CELL\nRECTANGLE Normal -10 16 10 48\nLINE Normal 0 0 0 16\nLINE Normal 0 48 0 64\nWINDOW 0 18 16 Left 2\nWINDOW 3 18 48 Left 2\nSYMATTR Prefix R\nPIN 0 0 NONE 0\nPINATTR SpiceOrder 1\nPIN 0 64 NONE 0\nPINATTR SpiceOrder 2\n')
(out/'LMG1210_modes.lib').write_text('''* Local wrapper around TI model; VSS must be ground.
.include ../models/ti-lmg1210/LMG1210_LTspice.lib
.subckt LMG1210_TEST VIN VDD EN_HI PWM_LI VSS HB HS HO LO BST DHL DLH
XCORE HB HO PWM_LI HS HS HS HS 0 VSS VIN LO DHL DLH VDD VSS VSS EN_HI NC0 NC1 NC2 BST LMG1210
.ends LMG1210_TEST
''')
pins=[('VIN',0,32,1),('VDD',0,96,2),('EN_HI',0,160,3),('PWM_LI',0,224,4),('VSS',0,288,5),('DHL',0,352,11),('DLH',0,416,12),('HB',256,32,6),('HS',256,96,7),('HO',256,160,8),('LO',256,224,9),('BST',256,288,10)]
a=['Version 4','SymbolType CELL','RECTANGLE Normal 32 0 224 448','WINDOW 0 128 -32 Center 2','WINDOW 3 128 472 Center 2','SYMATTR Prefix X','SYMATTR Value LMG1210_TEST']
for name,x,y,n in pins:
    a.extend([f'LINE Normal {x} {y} {32 if x==0 else 224} {y}',f'PIN {x} {y} {"LEFT" if x==0 else "RIGHT"} 36',f'PINATTR PinName {name}',f'PINATTR SpiceOrder {n}'])
(out/'LMG1210_TEST.asy').write_text('\n'.join(a)+'\n')
for mode in ['IIM','PWM']:
    wires=[];flags=[];symbols=[];texts=[]
    def part(sym,ref,value,x,y,n1,n2):
        flags.extend([f'FLAG {x} {y} {n1}',f'FLAG {x} {y+64} {n2}'])
        symbols.extend([f'SYMBOL {sym} {x} {y} R0',f'SYMATTR InstName {ref}',f'SYMATTR Value {value}'])
    part('test_voltage','V12','PWL(0 0 1u 0 2u 12)',64,144,'VIN','0')
    part('test_cap','CVDD','1u',416,144,'VDD','0')
    part('test_voltage','VHB','5',64,656,'HB','HS')
    part('test_voltage','VHS','75',416,656,'HS','0')
    part('test_cap','CHO','1n',1152,320,'HO','HS')
    part('test_cap','CLO','1n',1376,416,'LO','0')
    if mode=='IIM':
        part('test_voltage','VHI','PULSE(0 3.3 {TS} 2n 2n {T/2-DT-2n} {T})',64,304,'HI','0')
        part('test_voltage','VLI','PULSE(0 3.3 {TS+T/2} 2n 2n {T/2-DT-2n} {T})',64,480,'LI','0')
        mapping={'EN_HI':'HI','PWM_LI':'LI','DHL':'VDD','DLH':'VDD','VSS':'0'}
        note='DLH = VDD selects IIM at startup. HI and LI independently control HO and LO. External dead time = 200 ns.'
    else:
        part('test_voltage','VEN','PWL(0 0 290u 0 291u 3.3)',64,304,'EN','0')
        part('test_voltage','VPWM','PULSE(0 3.3 {TS} 2n 2n {T/2-2n} {T})',64,480,'PWM','0')
        part('test_res','RDHL','100k',448,784,'DHL','0')
        part('test_res','RDLH','100k',672,784,'DLH','0')
        mapping={'EN_HI':'EN','PWM_LI':'PWM','VSS':'0'}
        note='PWM high requests HO; PWM low requests LO. EN low disables both. 100k dead-time resistors target about 7.2 ns.'
    symbols.extend(['SYMBOL LMG1210_TEST 768 176 R0','SYMATTR InstName U1'])
    for name,x,y,n in pins:
        x+=768;y+=176;end=x-64 if x==768 else x+64
        wires.append(f'WIRE {x} {y} {end} {y}');flags.append(f'FLAG {end} {y} {mapping.get(name,name)}')
    texts.extend([f'TEXT 64 32 Left 3 ;LMG1210 {mode} MODE - driver-only test',f'TEXT 64 72 Left 2 ;{note}',
                  'TEXT 64 112 Left 2 ;Ideal HB-HS = 5 V; HS = 75 V DC. Bootstrap recharge and dv/dt immunity are not tested.',
                  'TEXT 64 896 Left 2 !.include LMG1210_modes.lib',
                  'TEXT 64 928 Left 2 !.param TS=300u FSW=100k T=1/FSW DT=200n',
                  'TEXT 64 960 Left 2 !.step param FSW list 50k 100k',
                  'TEXT 64 992 Left 2 !.tran 0 360u 0 5n',
                  'TEXT 64 1024 Left 2 !.options plotwinsize=0 method=gear',
                  'TEXT 64 1056 Left 2 !.save V(VIN) V(VDD) V(HO) V(HS) V(LO) V(EN_HI) V(PWM_LI) V(HI) V(LI) V(EN) V(PWM)',
                  'TEXT 64 1088 Left 2 !.meas tran VDD_FINAL FIND V(VDD) AT=350u',
                  'TEXT 64 1120 Left 2 !.meas tran HO_HIGH FIND V(HO,HS) AT=302u',
                  'TEXT 64 1152 Left 2 !.meas tran LO_HIGH FIND V(LO) AT=317u',
                  'TEXT 64 1184 Left 2 !.meas tran HO_LOW FIND V(HO,HS) AT=317u',
                  'TEXT 64 1216 Left 2 !.meas tran LO_LOW FIND V(LO) AT=302u'])
    # Save only existing named nodes.
    texts=[t.replace('V(EN_HI) V(PWM_LI) ','').replace('V(EN) V(PWM)','') if mode=='IIM' else t.replace('V(EN_HI) V(PWM_LI) V(HI) V(LI) ','') for t in texts]
    (out/f'LMG1210_{mode}_test.asc').write_text('\n'.join(['Version 4','SHEET 1 1720 1350',*wires,*flags,*symbols,*texts])+'\n')
    inp=('hi','li') if mode=='IIM' else ('en','pwm')
    panes=[]
    for traces,lo,hi in [(list(inp),0,4),(['ho,hs','lo','vdd'],-1,6)]:
        spec=' '.join('{'+str(524290+j)+',0,"V('+n+')"}' for j,n in enumerate(traces))
        panes.append('   {\n      traces: '+str(len(traces))+' '+spec+"\n      X: ('u',0,0.0003,0.00001,0.00034)\n      Y[0]: (' ',0,"+str(lo)+',1,'+str(hi)+")\n      Y[1]: (' ',0,"+str(lo)+',1,'+str(hi)+")\n      Volts: (' ',0,0,0,"+str(lo)+',1,'+str(hi)+')\n      Log: 0 0 0\n   }')
    (out/f'LMG1210_{mode}_test.plt').write_text('[Transient Analysis]\n{\n   Npanes: 2\n'+'\n'.join(panes)+'\n}\n')
print(out)

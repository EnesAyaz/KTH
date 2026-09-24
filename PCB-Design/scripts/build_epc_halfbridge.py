from pathlib import Path
import shutil
r=Path.cwd();o=r/'simulation/LMG1210-EPC2361';o.mkdir(exist_ok=True)
src=r/'simulation/LMG1210-modes'
for n in ['LMG1210_TEST.asy','LMG1210_modes.lib','test_voltage.asy','test_res.asy','test_cap.asy']:
 shutil.copy2(src/n,o/n)
shutil.copy2(Path('C:/Github/KTH/LossCalculation-SPB/simulations/pwm_half_bridge/EPC2361.lib'),o/'EPC2361.lib')
def sym(n,p,draw,pins,val=''):
 a=['Version 4','SymbolType CELL',*draw,'WINDOW 0 110 16 Left 2','WINDOW 3 110 48 Left 2','SYMATTR Prefix '+p]
 if val:a+=['SYMATTR Value '+val]
 for x,y,k in pins:a += [f'PIN {x} {y} NONE 0',f'PINATTR SpiceOrder {k}']
 (o/(n+'.asy')).write_text('\n'.join(a)+'\n')
sym('EPC2361','X',['LINE Normal 0 48 48 48','LINE Normal 48 24 48 72','LINE Normal 64 24 64 72','LINE Normal 64 24 96 24','LINE Normal 96 0 96 24','LINE Normal 64 72 96 72','LINE Normal 96 72 96 96'],[(0,48,1),(96,0,2),(96,96,3)],'EPC2361')
sym('boot_diode','D',['LINE Normal 0 0 0 16','LINE Normal -12 16 12 16','LINE Normal -12 16 0 44','LINE Normal 12 16 0 44','LINE Normal -12 44 12 44','LINE Normal 0 44 0 64'],[(0,0,1),(0,64,2)])
sym('load_ind','L',['RECTANGLE Normal -10 16 10 48','LINE Normal 0 0 0 16','LINE Normal 0 48 0 64'],[(0,0,1),(0,64,2)])
w=[];f=[];s=[]
def part(n,ref,v,x,y,a,b):
 f.extend([f'FLAG {x} {y} {a}',f'FLAG {x} {y+64} {b}'])
 s.extend([f'SYMBOL {n} {x} {y} R0',f'SYMATTR InstName {ref}',f'SYMATTR Value {v}'])
part('test_voltage','VIN','PWL(0 0 1u 0 2u 12)',64,192,'VIN','0')
part('test_cap','CVDD','1u',352,192,'VDD','0')
part('test_voltage','VHI','PULSE(0 3.3 {TS+T/2} 2n 2n {T/2-202n} {T})',64,384,'HI','0')
part('test_voltage','VLI','PULSE(0 3.3 {TS} 2n 2n {T/2-202n} {T})',64,560,'LI','0')
pins=[('VIN',0,32),('VDD',0,96),('HI',0,160),('LI',0,224),('0',0,288),('VDD',0,352),('VDD',0,416),('HB',256,32),('SW',256,96),('HO',256,160),('LO',256,224),('BST',256,288)]
s+=['SYMBOL LMG1210_TEST 720 160 R0','SYMATTR InstName U1']
for n,x,y in pins:
 x+=720;y+=160;xx=x-32 if x==720 else x+32
 w.append(f'WIRE {x} {y} {xx} {y}');f.append(f'FLAG {xx} {y} {n}')
part('boot_diode','DBOOT','DBOOT',1120,192,'BST','HB')
part('test_cap','CBOOT','100n',1376,192,'HB','SW')
part('test_res','RGH','2',1120,384,'HO','GH')
part('test_res','RGL','2',1120,608,'LO','GL')
for ref,y,g,d,ss in [('QH',384,'GH','BUS','SW'),('QL',608,'GL','SW','0')]:
 s += [f'SYMBOL EPC2361 1392 {y} R0',f'SYMATTR InstName {ref}']
 f += [f'FLAG 1392 {y+48} {g}',f'FLAG 1488 {y} {d}',f'FLAG 1488 {y+96} {ss}']
w.append('WIRE 1488 480 1488 608')
part('test_voltage','VBUS','75',1760,160,'SUPPLY','0')
part('test_res','RBUS','10m',1760,304,'SUPPLY','BUS')
part('test_cap','CDC','10u',1984,304,'BUS','0')
part('load_ind','LLOAD','10u',1760,544,'SW','OUT')
part('test_res','RLOAD','2',1760,704,'OUT','0')
ds=['.include LMG1210_modes.lib','.include EPC2361.lib','.param TS=300u FSW=50k T=1/FSW','.model DBOOT D(Is=1n N=1.2 Rs=1 Cjo=2p Tt=1n Bv=150 Ibv=10u)','.tran 0 400u 0 5n','.options plotwinsize=0 method=gear','.save V(HI) V(LI) V(VDD) V(HB) V(SW) V(GH) V(GL) V(BUS) V(OUT) I(LLOAD) I(VBUS)',
'.meas tran VDD_END FIND V(VDD) AT=399u','.meas tran VBOOT_MIN MIN V(HB,SW) FROM=330u TO=400u','.meas tran VGH_MAX MAX V(GH,SW) FROM=330u TO=400u','.meas tran VGL_MAX MAX V(GL) FROM=330u TO=400u','.meas tran SW_MAX MAX V(SW) FROM=330u TO=400u','.meas tran ILOAD_AVG AVG I(LLOAD) FROM=380u TO=400u']
t=[f'TEXT 64 {832+j*32} Left 2 !{d}' for j,d in enumerate(ds)]
t+=['TEXT 64 32 Left 3 ;75 V HALF BRIDGE - LMG1210 IIM + one EPC2361 per arm','TEXT 64 80 Left 2 ;50 kHz, external 200 ns dead time; low side starts first for bootstrap charging.','TEXT 64 120 Left 2 ;Generic bootstrap diode, 2 ohm gate resistors, 10 uH / 2 ohm load. No extracted PCB parasitics.']
(o/'LMG1210_EPC2361_halfbridge.asc').write_text('\n'.join(['Version 4','SHEET 1 2300 1400',*w,*f,*s,*t])+'\n')
panes=[]
for ts,lo,hi in [(['V(hi)','V(li)'],0,4),(['V(gh,sw)','V(gl)','V(hb,sw)'],-1,6),(['V(sw)','V(out)'],-10,85),(['I(LLOAD)'],0,40)]:
 spec=' '.join('{'+str(524290+j)+',0,"'+n+'"}' for j,n in enumerate(ts))
 panes.append('   {\n      traces: '+str(len(ts))+' '+spec+"\n      X: ('u',0,0.0003,0.00002,0.0004)\n      Y[0]: (' ',0,"+str(lo)+',5,'+str(hi)+")\n      Y[1]: (' ',0,"+str(lo)+',5,'+str(hi)+')\n      Log: 0 0 0\n   }')
(o/'LMG1210_EPC2361_halfbridge.plt').write_text('[Transient Analysis]\n{\n   Npanes: 4\n'+'\n'.join(panes)+'\n}\n')
(o/'Open-HalfBridge.cmd').write_text('@echo off\ncd /d "%~dp0"\nstart "" "%LOCALAPPDATA%\\Programs\\ADI\\LTspice\\LTspice.exe" -alt -Run "%~dp0LMG1210_EPC2361_halfbridge.asc"\n')
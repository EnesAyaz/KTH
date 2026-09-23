from pathlib import Path
root=Path(r'C:/Github/KTH/PCB-Design/simulation')
out=root/'LMG1210-test';out.mkdir(exist_ok=True)
(root/'models/ti-lmg1210/LMG1210_LTspice.lib').read_text(encoding='cp1252')
# Local wrapper exposes the functional pins; independent-input mode is fixed.
(out/'LMG1210_IIM.lib').write_text('''* Local IIM wrapper, not a manufacturer symbol
.include ../models/ti-lmg1210/LMG1210_LTspice.lib
.subckt LMG1210_IIM VIN VDD HI LI VSS HB HS HO LO BST
XCORE HB HO LI HS HS HS HS 0 VSS VIN LO VDD VDD VDD VSS VSS HI NC0 NC1 NC2 BST LMG1210
.ends LMG1210_IIM
''')
pins=[('VIN',0,32,'LEFT',1),('VDD',0,96,'LEFT',2),('HI',0,160,'LEFT',3),('LI',0,224,'LEFT',4),('VSS',0,288,'LEFT',5),('HB',256,32,'RIGHT',6),('HS',256,96,'RIGHT',7),('HO',256,160,'RIGHT',8),('LO',256,224,'RIGHT',9),('BST',256,288,'RIGHT',10)]
a=['Version 4','SymbolType CELL','RECTANGLE Normal 32 0 224 320','WINDOW 0 128 -32 Center 2','WINDOW 3 128 344 Center 2','SYMATTR Prefix X','SYMATTR Value LMG1210_IIM']
for name,x,y,align,n in pins:
    a += [f'LINE Normal {x} {y} {32 if x==0 else 224} {y}',f'PIN {x} {y} {align} 36',f'PINATTR PinName {name}',f'PINATTR SpiceOrder {n}']
(out/'LMG1210_IIM.asy').write_text('\n'.join(a)+'\n')
for name,prefix,shape in [('test_voltage','V',['CIRCLE Normal -24 8 24 56','LINE Normal 0 0 0 8','LINE Normal 0 56 0 64','LINE Normal -6 23 6 23','LINE Normal 0 17 0 29','LINE Normal -6 43 6 43']),('test_cap','C',['LINE Normal 0 0 0 28','LINE Normal -18 28 18 28','LINE Normal -18 36 18 36','LINE Normal 0 36 0 64'])]:
    a=['Version 4','SymbolType CELL',*shape,'WINDOW 0 28 12 Left 2','WINDOW 3 28 48 Left 2',f'SYMATTR Prefix {prefix}','PIN 0 0 NONE 0','PINATTR PinName +','PINATTR SpiceOrder 1','PIN 0 64 NONE 0','PINATTR PinName -','PINATTR SpiceOrder 2']
    (out/(name+'.asy')).write_text('\n'.join(a)+'\n')
a=['Version 4','SHEET 1 1600 1100']
def component(symbol,ref,val,x,y,top,bottom):
    a.extend([f'FLAG {x} {y} {top}',f'FLAG {x} {y+64} {bottom}',f'SYMBOL {symbol} {x} {y} R0',f'SYMATTR InstName {ref}',f'SYMATTR Value {val}'])
component('test_voltage','V12','PWL(0 0 1u 0 2u 12)',80,120,'VIN','0')
component('test_voltage','VHI','PULSE(0 3.3 20u 2n 2n 4u 10u)',80,280,'HI','0')
component('test_voltage','VLI','PULSE(0 3.3 25u 2n 2n 4u 10u)',80,440,'LI','0')
component('test_voltage','VHB','5',80,600,'HB','HS')
component('test_voltage','VHS','{VHS_TEST}',320,600,'HS','0')
component('test_cap','CVDD','1u',400,120,'VDD','0')
component('test_cap','CHO','1n',1100,260,'HO','HS')
component('test_cap','CLO','1n',1300,420,'LO','0')
a.extend(['SYMBOL LMG1210_IIM 720 160 R0','SYMATTR InstName U1'])
for name,x,y,align,n in pins:
    x+=720;y+=160;end=x-48 if align=='LEFT' else x+48
    a.extend([f'WIRE {x} {y} {end} {y}',f'FLAG {end} {y} {"0" if name=="VSS" else name}'])
a.extend(['TEXT 64 32 Left 3 ;LMG1210 independent-input driver test - NO POWER FETS',
'TEXT 680 560 Left 2 ;IIM: DHL and DLH tied to VDD inside wrapper.\nHB uses an ideal floating 5 V supply for this first test.\nBST is unloaded; bootstrap operation is NOT tested here.'.replace('\n',r'\n'),
'TEXT 64 760 Left 2 !.include LMG1210_IIM.lib',
'TEXT 64 792 Left 2 !.param VHS_TEST=0',
'TEXT 64 824 Left 2 !.tran 0 65u 0 2n',
'TEXT 64 856 Left 2 !.options plotwinsize=0 method=gear',
'TEXT 64 888 Left 2 !.meas tran VDD_FINAL FIND V(VDD) AT=60u',
'TEXT 64 920 Left 2 !.meas tran HO_HIGH FIND V(HO,HS) AT=52u',
'TEXT 64 952 Left 2 !.meas tran LO_HIGH FIND V(LO) AT=57u',
'TEXT 64 984 Left 2 !.meas tran HO_LOW FIND V(HO,HS) AT=57u',
'TEXT 64 1016 Left 2 !.meas tran LO_LOW FIND V(LO) AT=52u'])
(out/'LMG1210_driver_test.asc').write_text('\n'.join(a)+'\n')
# Plot file prepared for LTspice's standard waveform viewer.
(out/'LMG1210_driver_test.plt').write_text('''[Transient Analysis]
{
   Npanes: 2
   {
      traces: 2 {524290,0,"V(hi)"} {524291,0,"V(li)"}
      X: ('u',0,4.8e-5,2e-6,6e-5)
      Y[0]: (' ',0,0,1,4)
      Y[1]: (' ',0,0,1,4)
      Volts: (' ',0,0,0,0,1,4)
      Log: 0 0 0
   }
   {
      traces: 3 {524292,0,"V(ho,hs)"} {524293,0,"V(lo)"} {524294,0,"V(vdd)"}
      X: ('u',0,4.8e-5,2e-6,6e-5)
      Y[0]: (' ',0,-1,1,6)
      Y[1]: (' ',0,-1,1,6)
      Volts: (' ',0,0,0,-1,1,6)
      Log: 0 0 0
   }
}
''')
print(out/'LMG1210_driver_test.asc')

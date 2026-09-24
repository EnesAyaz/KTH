from pathlib import Path
import re
r=Path.cwd();o=r/'simulation/LMG1210-EPC2361'
p=o/'HalfBridge.asc'
b=p.read_bytes(); a=b.decode('utf-8' if b'\xc2\xb5' in b else 'cp1252').replace('\xb5','u')
# Keep user values, sources and analysis duration. Remove old gate resistors only.
for ref in ['RGH','RGL']:
 a=re.sub(r'SYMBOL test_res [^\n]+\nSYMATTR InstName '+ref+r'\nSYMATTR Value [^\n]+\n','',a)
for line in ['FLAG 1120 384 HO','FLAG 1120 448 GH','FLAG 1120 608 LO','FLAG 1120 672 GL']:
 a=a.replace(line+'\n','')
a=a.replace('FLAG 1488 384 BUS','FLAG 1488 384 DH')
a=a.replace('FLAG 1760 224 0','FLAG 1760 224 PGND').replace('FLAG 1984 368 0','FLAG 1984 368 PGND')
a=a.replace('SHEET 1 2300 1400','SHEET 1 3400 2000')
a='\n'.join(l for l in a.splitlines() if not (l.startswith('TEXT') and ' ;' in l))+'\n'
w=[];f=[];s=[];t=[]
def part(sym,ref,val,x,y,n1,n2):
 f.extend([f'FLAG {x} {y} {n1}',f'FLAG {x} {y+64} {n2}'])
 s.extend([f'SYMBOL {sym} {x} {y} R0',f'SYMATTR InstName {ref}',f'SYMATTR Value {val}'])
for h,x in [('H',2240),('L',2800)]:
 out='HO' if h=='H' else 'LO';g='G'+h;k='KG'+h
 # Opposite directed diode branches: output -> gate ON, gate -> output OFF.
 part('test_res','RG'+h+'ON','{RGON}',x,224,out,'ON'+h)
 part('boot_diode','DG'+h+'ON','DGATE',x,368,'ON'+h,k)
 part('test_res','RG'+h+'OFF','{RGOFF}',x+256,224,k,'OFF'+h)
 part('boot_diode','DG'+h+'OFF','DGATE',x+256,368,'OFF'+h,out)
 part('load_ind','LG'+h,'{LGATE}',x,544,k,g)
 part('test_res','RGS'+h,'100k',x+256,544,g,'SW' if h=='H' else '0')
 t.append(f'TEXT {x} 144 Left 2 ;{h} GATE: ON output->gate / OFF gate->output')
part('load_ind','LPPLUS','{LPOWER/2}',2240,800,'BUS','DH')
part('load_ind','LPMINUS','{LPOWER/2}',2528,800,'0','PGND')
# Local capacitor ESL: move bottom plate to intermediary node.
a=a.replace('FLAG 1984 368 PGND','FLAG 1984 368 CAPRET')
part('load_ind','LCESL','{LCAP}',2816,800,'CAPRET','PGND')
ds=['.param RGON=2 RGOFF=0.5 LGATE=2n LPOWER=4n LCAP=0.5n',
'.model DGATE D(Is=1u N=1.05 Rs=0.05 Cjo=5p Tt=0 Bv=30)',
'.options plotwinsize=0 method=gear',
'.meas tran VGH_PK MAX V(GH,SW) FROM=800u TO=1m',
'.meas tran VGH_MIN MIN V(GH,SW) FROM=800u TO=1m',
'.meas tran VGL_PK MAX V(GL) FROM=800u TO=1m',
'.meas tran VGL_MIN MIN V(GL) FROM=800u TO=1m',
'.meas tran VDSH_PK MAX V(DH,SW) FROM=800u TO=1m',
'.meas tran VDSL_PK MAX V(SW) FROM=800u TO=1m',
'.meas tran VBOOT_MIN MIN V(HB,SW) FROM=800u TO=1m']
for j,d in enumerate(ds):t.append(f'TEXT 64 {1040+32*j} Left 2 !{d}')
t+=['TEXT 64 -128 Left 3 ;LMG1210 + EPC2361: gate/power parasitics and separate ON/OFF paths',
'TEXT 64 -80 Left 2 ;User HalfBridge.asc preserved: 100 uH load, 2 ohm, 50 kHz, 1 ms run.',
'TEXT 64 -32 Left 2 ;Illustrative inductances only. LGATE per gate loop; LPOWER total interconnect; LCAP additional capacitor ESL.',
'TEXT 64 16 Left 2 ;Ideal Kelvin source returns; common-source inductance and magnetic coupling are not modeled.',
'TEXT 2240 960 Left 2 ;Power commutation inductance = LPOWER + LCAP = 4.5 nH default.',
'TEXT 64 1424 Left 2 ;Optional: enable ONE sweep directive at a time below.',
'TEXT 64 1456 Left 2 ;.step param LGATE list 1n 2n 5n',
'TEXT 64 1488 Left 2 ;.step param LPOWER list 1n 4n 8n',
'TEXT 64 1520 Left 2 ;.step param RGOFF list 0.5 1 2']
# Wires/flags must precede all symbols in ASC.
lines=a.splitlines(); i=next(i for i,l in enumerate(lines) if l.startswith('SYMBOL'))
lines=lines[:i]+w+f+lines[i:]+s+t
(o/'HalfBridge_Parasitics.asc').write_text('\n'.join(lines)+'\n')
(o/'Open-Parasitics.cmd').write_text('@echo off\ncd /d "%~dp0"\nstart "" "%LOCALAPPDATA%\\Programs\\ADI\\LTspice\\LTspice.exe" -alt -Run "%~dp0HalfBridge_Parasitics.asc"\n')
plt=(o/'LMG1210_EPC2361_halfbridge.plt').read_text().replace('0.0003,0.00002,0.0004','0.0009,0.00002,0.001')
(o/'HalfBridge_Parasitics.plt').write_text(plt)
from pathlib import Path
import re
o=Path('simulation/LMG1210-EPC2361')
b=(o/'HalfBridge_Parasitics.asc').read_bytes()
try:a=b.decode('utf-8')
except UnicodeDecodeError:a=b.decode('cp1252')
a=a.replace('\xb5','u')
a=a.replace('PULSE(0 3.3 {TS+T/2} 2n 2n {T/2-202n} {T})','PULSE(0 3.3 {TS+(1-DUTY)*T} {TR} {TR} {DUTY*T-DEAD-TR} {T})')
a=a.replace('PULSE(0 3.3 {TS} 2n 2n {T/2-202n} {T})','PULSE(0 3.3 {TS} {TR} {TR} {(1-DUTY)*T-DEAD-TR} {T})')
a=a.replace('.param TS=300u FSW=50k T=1/FSW','.param FSW=50k DUTY=0.5 DEAD=200n TR=2n TS=300u T=1/FSW')
a=re.sub(r'!\.tran[^\n]*','!.tran 0 {TSTOP} 0 5n',a)
a='\n'.join(l for l in a.splitlines() if not re.search(r'!\.(meas|save|step)\b',l,re.I))+'\n'
a=a.replace('User HalfBridge.asc preserved: 100 uH load, 2 ohm, 50 kHz, 1 ms run.','Variable FSW and DUTY; low-side first for bootstrap. Edit parameters below.')
a+='TEXT 64 1152 Left 2 !.param TSTOP=1m\n'
a+='TEXT 64 1200 Left 2 ;DUTY = requested high-side fraction before dead-time subtraction (0 < DUTY < 1).\n'
a+='TEXT 64 1232 Left 2 ;Require min(DUTY,1-DUTY)/FSW > DEAD+TR. Bootstrap requires low-side charging time.\n'
a+='TEXT 64 1264 Left 2 ;No preset plots or automatic measurements. Click Run and select your own nodes/components.\n'
assert 'DUTY*T-DEAD-TR' in a and '(1-DUTY)*T-DEAD-TR' in a
assert a.count('SYMATTR InstName VHI')==1 and a.count('SYMATTR InstName VLI')==1
(o/'HalfBridge_Variable_PWM.asc').write_text(a)
(o/'Open-Variable-PWM.cmd').write_text('@echo off\ncd /d "%~dp0"\nstart "" "%LOCALAPPDATA%\\Programs\\ADI\\LTspice\\LTspice.exe" -alt "%~dp0HalfBridge_Variable_PWM.asc"\n')
(o/'Variable-PWM-README.md').write_text("""# Variable duty and frequency
Open HalfBridge_Variable_PWM.asc, or Open-Variable-PWM.cmd. The launcher opens the schematic with Alternate solver without automatically running it. Press Run yourself and select any node voltage or component current. No .plt, .save, .meas or active .step is supplied for this version. LTspice will still generate its normal RAW simulation data when you run; no traces are preselected.

Edit:
.param FSW=50k DUTY=0.5 DEAD=200n TR=2n TS=300u T=1/FSW
.param TSTOP=1m

FSW is frequency in Hz; 50k = 50 kHz, 100k = 100 kHz.
DUTY is requested high-side fraction BEFORE dead-time subtraction; 0.3 = 30%, 0.7 = 70%.
DEAD is the nominal input nonoverlap, not guaranteed output dead time.
TS delays switching for driver startup. The low-side starts first.
TSTOP sets simulation end time. Keep it beyond TS plus several periods.

Command timing each period:
LI starts at TS + n*T, with flat pulse width (1-DUTY)*T-DEAD-TR.
HI starts at TS + (1-DUTY)*T + n*T, with flat pulse width DUTY*T-DEAD-TR.
Both have TR rise/fall times.
At 50% input crossings the high interval fractions are approximately:
HI: DUTY - DEAD*FSW
LI: 1-DUTY - DEAD*FSW
For DUTY=0.5, FSW=50k and DEAD=200n this is 49% each, leaving two 200 ns nonoverlap intervals per period. Actual output voltage duty also depends on commutation and load.

Require min(DUTY,1-DUTY)/FSW > DEAD+TR so both pulse widths stay positive. Do not use DUTY=0 or 1. Satisfying this mathematical condition does not ensure enough bootstrap charging time: extreme duty or high frequency needs separate checking.

This version retains the user's existing parasitic circuit, 100 uH / 2 ohm load and RGON/RGOFF/LGATE/LPOWER/LCAP parameters. Existing model warnings and ringing limitations remain. The new timing expressions were checked structurally; no new transient run was started.
""")
print('Created variable PWM schematic and open-only launcher; no plot settings or simulation run.')
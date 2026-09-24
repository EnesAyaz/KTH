# Variable duty and frequency
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

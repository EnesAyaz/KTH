* Building block (one phase leg, 2 x EPC2361 per switch, driver in the middle): low-side double pulse.
* Shared circuit body; included by BB_DPT.cir, BB_rg_sweep.cir and BB_energy_sweep.cir.
* Copper: Q3D subcircuits BB_PL (power loop, 3 nets / 21 terminals) and BB_GL (gate star, used for LO and HO).
* Parameters expected from the top file: VBUS IPK LLOAD TON1 RGON RGOFF RPU RPD (+ defaults below)
* Note: LTspice evaluates .meas time windows once, not per .step, so a current sweep must keep TON1 fixed
* and step the load inductance (LLOAD = TON1*VBUS/IPK), see BB_energy_sweep.cir.

.include ../bb_q3d/results/BB_PL.lib
.include ../bb_q3d/results/BB_GL.lib
.include ../LMG1210-EPC2361/EPC2361.lib
.model DID D(Ron=1m Roff=1G Vfwd=0)

.param TSTART=0.5u TOFF=1u TON2=0.5u
.param T1={TSTART+TON1} T2={T1+TOFF} TEND={T2+TON2+0.3u}
* driver output resistances RPU / RPD come from the top file (LT8418: 0.6 / 0.2 ohm)
.param VDRV=5
* capacitors: local 6 x 1 uF 0805 per cell (45 % at 75 V), bank rows 8 x 10 uF 1210 (30 % at 75 V)
.param CLOC=2.7u RLOC=1m LLOC=0.08n CROW=24u RROW=0.375m LROW=0.0625n

* ---------------- copper (Q3D) ----------------
XPL CapB1N CapB1P CapB2N CapB2P CapB3N CapB3P CapNL CapNR CapPL CapPR QH_D_L QH_D_R QH_S_L QH_S_R QL_D_L QL_D_R QL_S_L QL_S_R T_AC T_DCN T_DCP BB_PL

* ---------------- capacitors ----------------
CL CapPL cl1 {CLOC} Rser={RLOC}
LL cl1 CapNL {LLOC}
CR CapPR cr1 {CLOC} Rser={RLOC}
LR cr1 CapNR {LLOC}
CB1 CapB1P cb1 {CROW} Rser={RROW}
LB1 cb1 CapB1N {LROW}
CB2 CapB2P cb2 {CROW} Rser={RROW}
LB2 cb2 CapB2N {LROW}
CB3 CapB3P cb3 {CROW} Rser={RROW}
LB3 cb3 CapB3N {LROW}

* ---------------- DC bus (lab supply + bulk + 20 nH busbar) and load ----------------
V1 VS 0 {VBUS}
Cbulk VS 0 1m Rser=20m
Lbus VS T_DCP 20n Rser=2m
Rret T_DCN 0 1u
Lload T_AC T_DCP {LLOAD} Rser=2m Cpar=20p

* ---------------- FETs (0 V sources measure drain currents) ----------------
VIHL QH_D_L dHL 0
XQHL gtHL dHL QH_S_L EPC2361
VIHR QH_D_R dHR 0
XQHR gtHR dHR QH_S_R EPC2361
VILL QL_D_L dLL 0
XQLL gtLL dLL QL_S_L EPC2361
VILR QL_D_R dLR 0
XQLR gtLR dLR QL_S_R EPC2361

* ---------------- low-side driver (pulsed) -> gate star (Q3D) -> per-FET Rg_on / Rg_off ----------------
VLO lo GNDL PWL(0 0 {TSTART} 0 {TSTART+1n} {VDRV} {T1} {VDRV} {T1+1n} 0 {T2} 0 {T2+1n} {VDRV} {T2+TON2} {VDRV} {T2+TON2+1n} 0)
Rpul lo lo1 {RPU}
Dpul lo1 DOL DID
Dpdl DOL lo2 DID
Rpdl lo2 lo {RPD}
XGL GNDL DOL GLL GLR QL_S_L QL_S_R BB_GL
Ronll GLL gll1 {RGON}
Donll gll1 gtLL DID
Doffll gtLL gll2 DID
Roffll gll2 GLL {RGOFF+1m}
Ronlr GLR glr1 {RGON}
Donlr glr1 gtLR DID
Dofflr gtLR glr2 DID
Rofflr glr2 GLR {RGOFF+1m}

* ---------------- high-side driver (held off through the pull-down) ----------------
VHO ho GNDH 0
Rpdh ho DOH {RPD}
XGH GNDH DOH GHL GHR QH_S_L QH_S_R BB_GL
Ronhl GHL ghl1 {RGON}
Donhl ghl1 gtHL DID
Doffhl gtHL ghl2 DID
Roffhl ghl2 GHL {RGOFF+1m}
Ronhr GHR ghr1 {RGON}
Donhr ghr1 gtHR DID
Doffhr gtHR ghr2 DID
Roffhr ghr2 GHR {RGOFF+1m}

* ---------------- analysis and measurements (sum of both FETs of the switch position) ----------------
.options plotwinsize=0
.tran 0 {TEND} 0 0.1n
* keep the raw file small: only the signals used by the measurements and the plots
.save V(QL_D_L) V(QL_S_L) V(QL_D_R) V(QL_S_R) V(QH_D_L) V(QH_S_L) V(QH_D_R) V(QH_S_R) V(gtLL) V(gtLR) V(gtHL) V(gtHR) V(T_AC) V(T_DCP) V(T_DCN) I(VILL) I(VILR) I(VIHL) I(VIHR) I(Lload)
.meas TRAN Iload FIND I(Lload) AT {T1}
.meas TRAN IL_L FIND I(VILL) AT {T1}
.meas TRAN IL_R FIND I(VILR) AT {T1}
.meas TRAN Eoff INTEG V(QL_D_L,QL_S_L)*I(VILL)+V(QL_D_R,QL_S_R)*I(VILR) FROM {T1} TO {T1+150n}
.meas TRAN Eon INTEG V(QL_D_L,QL_S_L)*I(VILL)+V(QL_D_R,QL_S_R)*I(VILR) FROM {T2} TO {T2+150n}
.meas TRAN VDSL_pk MAX V(QL_D_L,QL_S_L) FROM {T1} TO {T1+150n}
.meas TRAN VDSH_pk MAX V(QH_D_L,QH_S_L) FROM {T2} TO {T2+150n}
.meas TRAN VGSH_bump MAX V(gtHL,QH_S_L) FROM {T2} TO {T2+150n}
.meas TRAN VGSL_min MIN V(gtLL,QL_S_L) FROM {T1} TO {T1+150n}
.meas TRAN VGSH_min MIN V(gtHL,QH_S_L) FROM {T1} TO {T2+150n}
.meas TRAN ID_pk MAX I(VILL) FROM {T2} TO {T2+150n}
.meas TRAN t_on TRIG V(QL_D_L,QL_S_L) VAL={0.8*VBUS} FALL=1 TD={T2} TARG V(QL_D_L,QL_S_L) VAL={0.2*VBUS} FALL=1 TD={T2}
.meas TRAN t_off TRIG V(QL_D_L,QL_S_L) VAL={0.2*VBUS} RISE=1 TD={T1} TARG V(QL_D_L,QL_S_L) VAL={0.8*VBUS} RISE=1 TD={T1}
.meas TRAN dvdt_on PARAM 0.6*VBUS/t_on/1e9
.meas TRAN dvdt_off PARAM 0.6*VBUS/t_off/1e9
.meas TRAN share_on PARAM ID_pk

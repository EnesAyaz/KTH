* One EPC2361 per switch, first-cut lumped half bridge (no layout yet): the power loop is one inductance LLOOP
* (PCB copper + MLCC ESL), split between drain side and source side; L_CS in the low-side source is shared by the
* gate loop (Kelvin return at sK). Gate loop LG, per-device Rg_on / Rg_off, 4 A / 8 A driver (2EDF7275K typ.).
.include ../LMG1210-EPC2361/EPC2361.lib
.model DID D(Ron=1m Roff=1G Vfwd=0)
.param TSTART=0.5u TOFF=1u TON2=0.5u
.param T1={TSTART+TON1} T2={T1+TOFF} TEND={T2+TON2+0.3u}
.param VDRV=5 LG=1.7n LCS=0.03n CDC=10u RDC=1m

V1 VS 0 {VBUS}
Cbulk VS 0 1m Rser=20m
Lbus VS P 20n Rser=2m
Cdc P 0 {CDC} Rser={RDC}
Ld P P1 {LLOOP/2}
VIH P1 dH 0
XQH gH dH SW EPC2361
VIL SW dL 0
XQL gL dL sL EPC2361
Lcs sL sK {LCS}
Ls sK 0 {LLOOP/2-LCS}
Lload SW P {LLOAD} Rser=2m Cpar=20p

VLO lo sK PWL(0 0 {TSTART} 0 {TSTART+1n} {VDRV} {T1} {VDRV} {T1+1n} 0 {T2} 0 {T2+1n} {VDRV} {T2+TON2} {VDRV} {T2+TON2+1n} 0)
Rpul lo lo1 {RPU}
Dpul lo1 DOL DID
Dpdl DOL lo2 DID
Rpdl lo2 lo {RPD}
Lgl DOL gxl {LG}
Ronl gxl gl1 {RGON}
Donl gl1 gL DID
Doffl gL gl2 DID
Roffl gl2 gxl {RGOFF+1m}

VHO ho SW 0
Rpdh ho DOH {RPD}
Lgh DOH gxh {LG}
Ronh gxh gh1 {RGON}
Donh gh1 gH DID
Doffh gH gh2 DID
Roffh gh2 gxh {RGOFF+1m}

.options plotwinsize=0
.tran 0 {TEND} 0 0.1n
.save V(dL) V(sL) V(dH) V(SW) V(gL) V(gH) I(VIL) I(VIH) I(Lload)
.meas TRAN Iload FIND I(VIL) AT {T1}
.meas TRAN Eoff INTEG V(dL,sL)*I(VIL) FROM {T1} TO {T1+150n}
.meas TRAN Eon INTEG V(dL,sL)*I(VIL) FROM {T2} TO {T2+150n}
.meas TRAN VDSL_pk MAX V(dL,sL) FROM {T1} TO {T1+150n}
.meas TRAN VDSH_pk MAX V(dH,SW) FROM {T2} TO {T2+150n}
.meas TRAN VGSH_bump MAX V(gH,SW) FROM {T2} TO {T2+150n}
.meas TRAN didt_on MAX D(I(VIL)) FROM {T2} TO {T2+150n}
.meas TRAN didt_off MIN D(I(VIL)) FROM {T1} TO {T1+150n}

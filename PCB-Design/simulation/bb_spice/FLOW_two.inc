* Two building blocks in parallel per leg (300 kW): shared DC bus, AC terminals joined through LX/2 each.
.include ../bb_q3d/results/BB_PL.lib
.include ../bb_q3d/results/BB_GL.lib
.include ../LMG1210-EPC2361/EPC2361.lib
.model DID D(Ron=1m Roff=1G Vfwd=0)
.param TSTART=0.5u TOFF=1u TON2=0.5u
.param T1={TSTART+TON1} T2={T1+TOFF} TEND={T2+TON2+0.3u}
.param VDRV=5
.param CLOC=2.7u RLOC=1m LLOC=0.08n CROW=24u RROW=0.375m LROW=0.0625n
XPL_1 CapB1N_1 CapB1P_1 CapB2N_1 CapB2P_1 CapB3N_1 CapB3P_1 CapNL_1 CapNR_1 CapPL_1 CapPR_1 QH_D_L_1 QH_D_R_1 QH_S_L_1 QH_S_R_1 QL_D_L_1 QL_D_R_1 QL_S_L_1 QL_S_R_1 T_AC_1 T_DCN_1 T_DCP_1 BB_PL
CL_1 CapPL_1 cl1_1 {CLOC} Rser={RLOC}
LL_1 cl1_1 CapNL_1 {LLOC}
CR_1 CapPR_1 cr1_1 {CLOC} Rser={RLOC}
LR_1 cr1_1 CapNR_1 {LLOC}
CB1_1 CapB1P_1 cb1_1 {CROW} Rser={RROW}
LB1_1 cb1_1 CapB1N_1 {LROW}
CB2_1 CapB2P_1 cb2_1 {CROW} Rser={RROW}
LB2_1 cb2_1 CapB2N_1 {LROW}
CB3_1 CapB3P_1 cb3_1 {CROW} Rser={RROW}
LB3_1 cb3_1 CapB3N_1 {LROW}
VIHL_1 QH_D_L_1 dHL_1 0
XQHL_1 gtHL_1 dHL_1 QH_S_L_1 EPC2361
VIHR_1 QH_D_R_1 dHR_1 0
XQHR_1 gtHR_1 dHR_1 QH_S_R_1 EPC2361
VILL_1 QL_D_L_1 dLL_1 0
XQLL_1 gtLL_1 dLL_1 QL_S_L_1 EPC2361
VILR_1 QL_D_R_1 dLR_1 0
XQLR_1 gtLR_1 dLR_1 QL_S_R_1 EPC2361
VLO_1 lo_1 GNDL_1 PWL(0 0 {TSTART} 0 {TSTART+1n} {VDRV} {T1} {VDRV} {T1+1n} 0 {T2} 0 {T2+1n} {VDRV} {T2+TON2} {VDRV} {T2+TON2+1n} 0)
Rpul_1 lo_1 lo1_1 {RPU}
Dpul_1 lo1_1 DOL_1 DID
Dpdl_1 DOL_1 lo2_1 DID
Rpdl_1 lo2_1 lo_1 {RPD}
XGL_1 GNDL_1 DOL_1 GLL_1 GLR_1 QL_S_L_1 QL_S_R_1 BB_GL
Ronll_1 GLL_1 gll1_1 {RGON}
Donll_1 gll1_1 gtLL_1 DID
Doffll_1 gtLL_1 gll2_1 DID
Roffll_1 gll2_1 GLL_1 {RGOFF+1m}
Ronlr_1 GLR_1 glr1_1 {RGON}
Donlr_1 glr1_1 gtLR_1 DID
Dofflr_1 gtLR_1 glr2_1 DID
Rofflr_1 glr2_1 GLR_1 {RGOFF+1m}
VHO_1 ho_1 GNDH_1 0
Rpdh_1 ho_1 DOH_1 {RPD}
XGH_1 GNDH_1 DOH_1 GHL_1 GHR_1 QH_S_L_1 QH_S_R_1 BB_GL
Ronhl_1 GHL_1 ghl1_1 {RGON}
Donhl_1 ghl1_1 gtHL_1 DID
Doffhl_1 gtHL_1 ghl2_1 DID
Roffhl_1 ghl2_1 GHL_1 {RGOFF+1m}
Ronhr_1 GHR_1 ghr1_1 {RGON}
Donhr_1 ghr1_1 gtHR_1 DID
Doffhr_1 gtHR_1 ghr2_1 DID
Roffhr_1 ghr2_1 GHR_1 {RGOFF+1m}
XPL_2 CapB1N_2 CapB1P_2 CapB2N_2 CapB2P_2 CapB3N_2 CapB3P_2 CapNL_2 CapNR_2 CapPL_2 CapPR_2 QH_D_L_2 QH_D_R_2 QH_S_L_2 QH_S_R_2 QL_D_L_2 QL_D_R_2 QL_S_L_2 QL_S_R_2 T_AC_2 T_DCN_2 T_DCP_2 BB_PL
CL_2 CapPL_2 cl1_2 {CLOC} Rser={RLOC}
LL_2 cl1_2 CapNL_2 {LLOC}
CR_2 CapPR_2 cr1_2 {CLOC} Rser={RLOC}
LR_2 cr1_2 CapNR_2 {LLOC}
CB1_2 CapB1P_2 cb1_2 {CROW} Rser={RROW}
LB1_2 cb1_2 CapB1N_2 {LROW}
CB2_2 CapB2P_2 cb2_2 {CROW} Rser={RROW}
LB2_2 cb2_2 CapB2N_2 {LROW}
CB3_2 CapB3P_2 cb3_2 {CROW} Rser={RROW}
LB3_2 cb3_2 CapB3N_2 {LROW}
VIHL_2 QH_D_L_2 dHL_2 0
XQHL_2 gtHL_2 dHL_2 QH_S_L_2 EPC2361
VIHR_2 QH_D_R_2 dHR_2 0
XQHR_2 gtHR_2 dHR_2 QH_S_R_2 EPC2361
VILL_2 QL_D_L_2 dLL_2 0
XQLL_2 gtLL_2 dLL_2 QL_S_L_2 EPC2361
VILR_2 QL_D_R_2 dLR_2 0
XQLR_2 gtLR_2 dLR_2 QL_S_R_2 EPC2361
VLO_2 lo_2 GNDL_2 PWL(0 0 {TSTART+DLY} 0 {TSTART+1n+DLY} {VDRV} {T1+DLY} {VDRV} {T1+1n+DLY} 0 {T2+DLY} 0 {T2+1n+DLY} {VDRV} {T2+TON2+DLY} {VDRV} {T2+TON2+1n+DLY} 0)
Rpul_2 lo_2 lo1_2 {RPU}
Dpul_2 lo1_2 DOL_2 DID
Dpdl_2 DOL_2 lo2_2 DID
Rpdl_2 lo2_2 lo_2 {RPD}
XGL_2 GNDL_2 DOL_2 GLL_2 GLR_2 QL_S_L_2 QL_S_R_2 BB_GL
Ronll_2 GLL_2 gll1_2 {RGON}
Donll_2 gll1_2 gtLL_2 DID
Doffll_2 gtLL_2 gll2_2 DID
Roffll_2 gll2_2 GLL_2 {RGOFF+1m}
Ronlr_2 GLR_2 glr1_2 {RGON}
Donlr_2 glr1_2 gtLR_2 DID
Dofflr_2 gtLR_2 glr2_2 DID
Rofflr_2 glr2_2 GLR_2 {RGOFF+1m}
VHO_2 ho_2 GNDH_2 0
Rpdh_2 ho_2 DOH_2 {RPD}
XGH_2 GNDH_2 DOH_2 GHL_2 GHR_2 QH_S_L_2 QH_S_R_2 BB_GL
Ronhl_2 GHL_2 ghl1_2 {RGON}
Donhl_2 ghl1_2 gtHL_2 DID
Doffhl_2 gtHL_2 ghl2_2 DID
Roffhl_2 ghl2_2 GHL_2 {RGOFF+1m}
Ronhr_2 GHR_2 ghr1_2 {RGON}
Donhr_2 ghr1_2 gtHR_2 DID
Doffhr_2 gtHR_2 ghr2_2 DID
Roffhr_2 ghr2_2 GHR_2 {RGOFF+1m}
* ---------------- shared DC bus and load ----------------
V1 VS 0 {VBUS}
Cbulk VS 0 1m Rser=20m
Lbus VS DCB 20n Rser=2m
Ld1 DCB T_DCP_1 {LXDC/2} Rser=0.1m
Ld2 DCB T_DCP_2 {LXDC/2} Rser=0.1m
Rret1 T_DCN_1 0 1u
Rret2 T_DCN_2 0 1u
La1 T_AC_1 ACO {LX/2} Rser={RX/2}
La2 T_AC_2 ACO {LX/2} Rser={RX/2}
Lload ACO DCB {LLOAD} Rser=2m Cpar=20p
* ---------------- analysis ----------------
.options plotwinsize=0
.tran 0 {TEND} 0 0.1n
.save I(La1) I(La2) I(Lload) V(T_AC_1) V(T_AC_2) V(QL_D_L_1) V(QL_S_L_1) V(QL_D_L_2) V(QL_S_L_2) I(VILL_1) I(VILR_1) I(VILL_2) I(VILR_2) V(QH_D_L_1) V(QH_S_L_1) V(QH_D_L_2) V(QH_S_L_2) V(QL_D_R_1) V(QL_S_R_1) V(QL_D_R_2) V(QL_S_R_2)
.meas TRAN Iload FIND I(Lload) AT {T1}
.meas TRAN I1_T1 FIND I(La1) AT {T1}
.meas TRAN I2_T1 FIND I(La2) AT {T1}
.meas TRAN I1_off FIND I(La1) AT {T1+200n}
.meas TRAN I2_off FIND I(La2) AT {T1+200n}
.meas TRAN I1_on FIND I(La1) AT {T2+200n}
.meas TRAN I2_on FIND I(La2) AT {T2+200n}
.meas TRAN I1_onpk MAX I(La1) FROM {T2} TO {T2+200n}
.meas TRAN I2_onpk MAX I(La2) FROM {T2} TO {T2+200n}
.meas TRAN Eoff1 INTEG V(QL_D_L_1,QL_S_L_1)*I(VILL_1)+V(QL_D_R_1,QL_S_R_1)*I(VILR_1) FROM {T1} TO {T1+160n}
.meas TRAN Eoff2 INTEG V(QL_D_L_2,QL_S_L_2)*I(VILL_2)+V(QL_D_R_2,QL_S_R_2)*I(VILR_2) FROM {T1} TO {T1+160n}
.meas TRAN Eon1 INTEG V(QL_D_L_1,QL_S_L_1)*I(VILL_1)+V(QL_D_R_1,QL_S_R_1)*I(VILR_1) FROM {T2} TO {T2+160n}
.meas TRAN Eon2 INTEG V(QL_D_L_2,QL_S_L_2)*I(VILL_2)+V(QL_D_R_2,QL_S_R_2)*I(VILR_2) FROM {T2} TO {T2+160n}
.meas TRAN VDSL1_pk MAX V(QL_D_L_1,QL_S_L_1) FROM {T1} TO {T1+160n}
.meas TRAN VDSL2_pk MAX V(QL_D_L_2,QL_S_L_2) FROM {T1} TO {T1+160n}

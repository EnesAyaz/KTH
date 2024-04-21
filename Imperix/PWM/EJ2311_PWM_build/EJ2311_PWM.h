//
// Academic License - for use in teaching, academic research, and meeting
// course requirements at degree granting institutions only.  Not for
// government, commercial, or other organizational use.
//
// File: EJ2311_PWM.h
//
// Code generated for Simulink model 'EJ2311_PWM'.
// To be implemented on the B-Box RCP or the B-Board PRO.
//
// Model version                  : 16.3
// Simulink Coder version         : 23.2 (R2023b) 01-Aug-2023
// C/C++ source code generated on : Wed Feb 14 15:50:32 2024
//
#ifndef RTW_HEADER_EJ2311_PWM_h_
#define RTW_HEADER_EJ2311_PWM_h_
#include "rtwtypes.h"
#include "EJ2311_PWM_types.h"

extern "C"
{

#include "rtGetInf.h"

}

extern "C"
{

#include "rt_nonfinite.h"

}

// Macros for accessing real-time model data structure
#ifndef rtmGetErrorStatus
#define rtmGetErrorStatus(rtm)         ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
#define rtmSetErrorStatus(rtm, val)    ((rtm)->errorStatus = (val))
#endif

// Block signals (default storage)
struct B_EJ2311_PWM_T {
  real32_T ADC;                        // '<S25>/ADC'
  real32_T ADC_f;                      // '<S27>/ADC'
  real32_T ADC_d;                      // '<S29>/ADC'
  real32_T ADC_k;                      // '<S31>/ADC'
  real32_T SFunction;                  // '<S54>/S-Function'
  real32_T Saturation;                 // '<S33>/Saturation'
  real32_T SFunction_n;                // '<S56>/S-Function'
  real32_T SFunction_o;                // '<S60>/S-Function'
  real32_T SFunction_c;                // '<S58>/S-Function'
  real32_T SFunction_m;                // '<S66>/S-Function'
  real32_T SFunction_j;                // '<S62>/S-Function'
  real32_T SFunction_b;                // '<S68>/S-Function'
  real32_T SFunction_mp;               // '<S64>/S-Function'
};

// Block states (default storage) for system '<Root>'
struct DW_EJ2311_PWM_T {
  real_T SFunction_DSTATE;             // '<S46>/S-Function'
  real_T SFunction_DSTATE_n;           // '<S48>/S-Function'
  real_T SFunction_DSTATE_p;           // '<S50>/S-Function'
  real_T SFunction_DSTATE_k;           // '<S52>/S-Function'
  real_T SFunction_DSTATE_n5;          // '<S36>/S-Function'
  real_T SFunction_DSTATE_m;           // '<S54>/S-Function'
  real_T SFunction_DSTATE_i;           // '<S56>/S-Function'
  real_T SFunction_DSTATE_d;           // '<S60>/S-Function'
  real_T SFunction_DSTATE_f;           // '<S58>/S-Function'
  real_T SFunction_DSTATE_l;           // '<S66>/S-Function'
  real_T SFunction_DSTATE_ky;          // '<S62>/S-Function'
  real_T SFunction_DSTATE_n1;          // '<S68>/S-Function'
  real_T SFunction_DSTATE_j;           // '<S64>/S-Function'
};

// Parameters (default storage)
struct P_EJ2311_PWM_T_ {
  real32_T PWM_P2;                     // Expression: single(deadtime)
                                          //  Referenced by: '<S40>/PWM'

  real32_T PWM_P3;                     // Expression: single(duty)
                                          //  Referenced by: '<S40>/PWM'

  real32_T PWM_P4;                     // Expression: single(phase)
                                          //  Referenced by: '<S40>/PWM'

  real32_T PWM_P2_b;                   // Expression: single(deadtime)
                                          //  Referenced by: '<S42>/PWM'

  real32_T PWM_P3_e;                   // Expression: single(duty)
                                          //  Referenced by: '<S42>/PWM'

  real32_T PWM_P4_a;                   // Expression: single(phase)
                                          //  Referenced by: '<S42>/PWM'

  real32_T PWM_P2_e;                   // Expression: single(deadtime)
                                          //  Referenced by: '<S44>/PWM'

  real32_T PWM_P3_b;                   // Expression: single(duty)
                                          //  Referenced by: '<S44>/PWM'

  real32_T PWM_P4_h;                   // Expression: single(phase)
                                          //  Referenced by: '<S44>/PWM'

  real32_T SFunction_P6;               // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S46>/S-Function'

  real32_T SFunction_P12;              // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S46>/S-Function'

  real32_T SFunction_P6_c;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S48>/S-Function'

  real32_T SFunction_P12_d;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S48>/S-Function'

  real32_T SFunction_P6_k;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S50>/S-Function'

  real32_T SFunction_P12_c;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S50>/S-Function'

  real32_T SFunction_P6_cv;            // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S52>/S-Function'

  real32_T SFunction_P12_g;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S52>/S-Function'

  real32_T ADC_P2;                     // Expression: single(gain)
                                          //  Referenced by: '<S25>/ADC'

  real32_T ADC_P3;                     // Expression: single(offset)
                                          //  Referenced by: '<S25>/ADC'

  real32_T ADC_P2_a;                   // Expression: single(gain)
                                          //  Referenced by: '<S27>/ADC'

  real32_T ADC_P3_m;                   // Expression: single(offset)
                                          //  Referenced by: '<S27>/ADC'

  real32_T ADC_P2_d;                   // Expression: single(gain)
                                          //  Referenced by: '<S29>/ADC'

  real32_T ADC_P3_e;                   // Expression: single(offset)
                                          //  Referenced by: '<S29>/ADC'

  real32_T ADC_P2_g;                   // Expression: single(gain)
                                          //  Referenced by: '<S31>/ADC'

  real32_T ADC_P3_a;                   // Expression: single(offset)
                                          //  Referenced by: '<S31>/ADC'

  real32_T SFunction_P2;               // Expression: single(phase_vector)
                                          //  Referenced by: '<S36>/S-Function'

  real32_T SFunction_P3;               // Expression: single(interrupt_phase)
                                          //  Referenced by: '<S36>/S-Function'

  real32_T CLK1_P2;                    // Expression: single(frequency)
                                          //  Referenced by: '<S38>/CLK1'

  real32_T SFunction_P3_g;             // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S54>/S-Function'

  real32_T SFunction_P4;               // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S54>/S-Function'

  real32_T SFunction_P5;               // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S54>/S-Function'

  real32_T SFunction_P6_l;             // Expression: single(0)
                                          //  Referenced by: '<S54>/S-Function'

  real32_T SFunction_P7;               // Expression: single(0)
                                          //  Referenced by: '<S54>/S-Function'

  real32_T Saturation_UpperSat;       // Computed Parameter: Saturation_UpperSat
                                         //  Referenced by: '<S33>/Saturation'

  real32_T Saturation_LowerSat;       // Computed Parameter: Saturation_LowerSat
                                         //  Referenced by: '<S33>/Saturation'

  real32_T CLK1_P2_l;                  // Expression: single(frequency)
                                          //  Referenced by: '<S33>/CLK1'

  real32_T SFunction_P3_f;             // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S56>/S-Function'

  real32_T SFunction_P4_i;             // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S56>/S-Function'

  real32_T SFunction_P5_l;             // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S56>/S-Function'

  real32_T SFunction_P6_p;             // Expression: single(0)
                                          //  Referenced by: '<S56>/S-Function'

  real32_T SFunction_P7_b;             // Expression: single(0)
                                          //  Referenced by: '<S56>/S-Function'

  real32_T SFunction_P3_e;             // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S60>/S-Function'

  real32_T SFunction_P4_d;             // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S60>/S-Function'

  real32_T SFunction_P5_a;             // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S60>/S-Function'

  real32_T SFunction_P6_e;             // Expression: single(0)
                                          //  Referenced by: '<S60>/S-Function'

  real32_T SFunction_P7_j;             // Expression: single(0)
                                          //  Referenced by: '<S60>/S-Function'

  real32_T SFunction_P3_n;             // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S58>/S-Function'

  real32_T SFunction_P4_h;             // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S58>/S-Function'

  real32_T SFunction_P5_f;             // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S58>/S-Function'

  real32_T SFunction_P6_ps;            // Expression: single(0)
                                          //  Referenced by: '<S58>/S-Function'

  real32_T SFunction_P7_g;             // Expression: single(0)
                                          //  Referenced by: '<S58>/S-Function'

  real32_T SFunction_P3_ep;            // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S66>/S-Function'

  real32_T SFunction_P4_k;             // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S66>/S-Function'

  real32_T SFunction_P5_o;             // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S66>/S-Function'

  real32_T SFunction_P6_b;             // Expression: single(0)
                                          //  Referenced by: '<S66>/S-Function'

  real32_T SFunction_P7_m;             // Expression: single(0)
                                          //  Referenced by: '<S66>/S-Function'

  real32_T SFunction_P3_j;             // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S62>/S-Function'

  real32_T SFunction_P4_e;             // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S62>/S-Function'

  real32_T SFunction_P5_p;             // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S62>/S-Function'

  real32_T SFunction_P6_ek;            // Expression: single(0)
                                          //  Referenced by: '<S62>/S-Function'

  real32_T SFunction_P7_jk;            // Expression: single(0)
                                          //  Referenced by: '<S62>/S-Function'

  real32_T SFunction_P3_a;             // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S68>/S-Function'

  real32_T SFunction_P4_j;             // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S68>/S-Function'

  real32_T SFunction_P5_c;             // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S68>/S-Function'

  real32_T SFunction_P6_a;             // Expression: single(0)
                                          //  Referenced by: '<S68>/S-Function'

  real32_T SFunction_P7_c;             // Expression: single(0)
                                          //  Referenced by: '<S68>/S-Function'

  real32_T SFunction_P3_e5;            // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S64>/S-Function'

  real32_T SFunction_P4_kl;            // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S64>/S-Function'

  real32_T SFunction_P5_n;             // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S64>/S-Function'

  real32_T SFunction_P6_ew;            // Expression: single(0)
                                          //  Referenced by: '<S64>/S-Function'

  real32_T SFunction_P7_l;             // Expression: single(0)
                                          //  Referenced by: '<S64>/S-Function'

  uint32_T SFunction_P7_jt;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S46>/S-Function'

  uint32_T SFunction_P13;              // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S46>/S-Function'

  uint32_T SFunction_P7_gg;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S48>/S-Function'

  uint32_T SFunction_P13_a;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S48>/S-Function'

  uint32_T SFunction_P7_b4;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S50>/S-Function'

  uint32_T SFunction_P13_e;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S50>/S-Function'

  uint32_T SFunction_P7_o;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S52>/S-Function'

  uint32_T SFunction_P13_c;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S52>/S-Function'

  uint32_T SFunction_P10;              // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S54>/S-Function'

  uint32_T SFunction_P10_o;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S56>/S-Function'

  uint32_T SFunction_P10_a;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S60>/S-Function'

  uint32_T SFunction_P10_k;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S58>/S-Function'

  uint32_T SFunction_P10_d;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S66>/S-Function'

  uint32_T SFunction_P10_k1;           // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S62>/S-Function'

  uint32_T SFunction_P10_g;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S68>/S-Function'

  uint32_T SFunction_P10_p;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S64>/S-Function'

  int16_T PWM_P1;                      // Expression: int16(lane)
                                          //  Referenced by: '<S40>/PWM'

  int16_T PWM_P5;                      // Expression: int16(carrier)
                                          //  Referenced by: '<S40>/PWM'

  int16_T PWM_P6;                      // Expression: int16(rate)
                                          //  Referenced by: '<S40>/PWM'

  int16_T PWM_P7;                      // Expression: int16(outconf)
                                          //  Referenced by: '<S40>/PWM'

  int16_T PWM_P8;                      // Expression: int16(outmode)
                                          //  Referenced by: '<S40>/PWM'

  int16_T PWM_P9;                      // Expression: int16(nbBbx)
                                          //  Referenced by: '<S40>/PWM'

  int16_T PWM_P1_a;                    // Expression: int16(lane)
                                          //  Referenced by: '<S42>/PWM'

  int16_T PWM_P5_a;                    // Expression: int16(carrier)
                                          //  Referenced by: '<S42>/PWM'

  int16_T PWM_P6_o;                    // Expression: int16(rate)
                                          //  Referenced by: '<S42>/PWM'

  int16_T PWM_P7_e;                    // Expression: int16(outconf)
                                          //  Referenced by: '<S42>/PWM'

  int16_T PWM_P8_k;                    // Expression: int16(outmode)
                                          //  Referenced by: '<S42>/PWM'

  int16_T PWM_P9_j;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S42>/PWM'

  int16_T PWM_P1_k;                    // Expression: int16(lane)
                                          //  Referenced by: '<S44>/PWM'

  int16_T PWM_P5_o;                    // Expression: int16(carrier)
                                          //  Referenced by: '<S44>/PWM'

  int16_T PWM_P6_i;                    // Expression: int16(rate)
                                          //  Referenced by: '<S44>/PWM'

  int16_T PWM_P7_l;                    // Expression: int16(outconf)
                                          //  Referenced by: '<S44>/PWM'

  int16_T PWM_P8_o;                    // Expression: int16(outmode)
                                          //  Referenced by: '<S44>/PWM'

  int16_T PWM_P9_n;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S44>/PWM'

  int16_T SFunction_P2_e;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S46>/S-Function'

  int16_T SFunction_P3_d;              // Expression: int16(0)
                                          //  Referenced by: '<S46>/S-Function'

  int16_T SFunction_P2_b;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S48>/S-Function'

  int16_T SFunction_P3_ft;             // Expression: int16(0)
                                          //  Referenced by: '<S48>/S-Function'

  int16_T SFunction_P2_j;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S50>/S-Function'

  int16_T SFunction_P3_p;              // Expression: int16(0)
                                          //  Referenced by: '<S50>/S-Function'

  int16_T SFunction_P2_h;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S52>/S-Function'

  int16_T SFunction_P3_g3;             // Expression: int16(0)
                                          //  Referenced by: '<S52>/S-Function'

  int16_T ADC_P1;                      // Expression: int16(channel)
                                          //  Referenced by: '<S25>/ADC'

  int16_T ADC_P4;                      // Expression: int16(nbBbx)
                                          //  Referenced by: '<S25>/ADC'

  int16_T ADC_P6;                      // Expression: int16(outputwidth)
                                          //  Referenced by: '<S25>/ADC'

  int16_T ADC_P1_h;                    // Expression: int16(channel)
                                          //  Referenced by: '<S27>/ADC'

  int16_T ADC_P4_c;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S27>/ADC'

  int16_T ADC_P6_e;                    // Expression: int16(outputwidth)
                                          //  Referenced by: '<S27>/ADC'

  int16_T ADC_P1_m;                    // Expression: int16(channel)
                                          //  Referenced by: '<S29>/ADC'

  int16_T ADC_P4_l;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S29>/ADC'

  int16_T ADC_P6_m;                    // Expression: int16(outputwidth)
                                          //  Referenced by: '<S29>/ADC'

  int16_T ADC_P1_j;                    // Expression: int16(channel)
                                          //  Referenced by: '<S31>/ADC'

  int16_T ADC_P4_m;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S31>/ADC'

  int16_T ADC_P6_p;                    // Expression: int16(outputwidth)
                                          //  Referenced by: '<S31>/ADC'

  int16_T clk_id_Value;                // Computed Parameter: clk_id_Value
                                          //  Referenced by: '<S38>/clk_id'

  int16_T CLK1_P1;                     // Expression: int16(id)
                                          //  Referenced by: '<S38>/CLK1'

  int16_T clk_id_Value_a;              // Computed Parameter: clk_id_Value_a
                                          //  Referenced by: '<S33>/clk_id'

  int16_T SFunction_P2_l;              // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S54>/S-Function'

  int16_T CLK1_P1_h;                   // Expression: int16(id)
                                          //  Referenced by: '<S33>/CLK1'

  int16_T SFunction_P2_a;              // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S56>/S-Function'

  int16_T SFunction_P2_g;              // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S60>/S-Function'

  int16_T SFunction_P2_m;              // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S58>/S-Function'

  int16_T SFunction_P2_n;              // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S66>/S-Function'

  int16_T SFunction_P2_az;             // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S62>/S-Function'

  int16_T SFunction_P2_f;              // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S68>/S-Function'

  int16_T SFunction_P2_a5;             // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S64>/S-Function'

  uint16_T SFunction_P1[2];            // Computed Parameter: SFunction_P1
                                          //  Referenced by: '<S46>/S-Function'

  uint16_T SFunction_P5_ay;            // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S46>/S-Function'

  uint16_T SFunction_P8;               // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S46>/S-Function'

  uint16_T SFunction_P11;              // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S46>/S-Function'

  uint16_T SFunction_P14[5];           // Computed Parameter: SFunction_P14
                                          //  Referenced by: '<S46>/S-Function'

  uint16_T SFunction_P1_k[2];          // Computed Parameter: SFunction_P1_k
                                          //  Referenced by: '<S48>/S-Function'

  uint16_T SFunction_P5_lc;            // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S48>/S-Function'

  uint16_T SFunction_P8_d;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S48>/S-Function'

  uint16_T SFunction_P11_c;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S48>/S-Function'

  uint16_T SFunction_P14_m[5];         // Computed Parameter: SFunction_P14_m
                                          //  Referenced by: '<S48>/S-Function'

  uint16_T SFunction_P1_l[2];          // Computed Parameter: SFunction_P1_l
                                          //  Referenced by: '<S50>/S-Function'

  uint16_T SFunction_P5_e;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S50>/S-Function'

  uint16_T SFunction_P8_g;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S50>/S-Function'

  uint16_T SFunction_P11_f;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S50>/S-Function'

  uint16_T SFunction_P14_o[5];         // Computed Parameter: SFunction_P14_o
                                          //  Referenced by: '<S50>/S-Function'

  uint16_T SFunction_P1_lh[3];         // Computed Parameter: SFunction_P1_lh
                                          //  Referenced by: '<S52>/S-Function'

  uint16_T SFunction_P5_b;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S52>/S-Function'

  uint16_T SFunction_P8_f;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S52>/S-Function'

  uint16_T SFunction_P11_p;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S52>/S-Function'

  uint16_T SFunction_P14_l[5];         // Computed Parameter: SFunction_P14_l
                                          //  Referenced by: '<S52>/S-Function'

  uint16_T SFunction_P1_f;             // Expression: uint16(interrupt_pstsclr)
                                          //  Referenced by: '<S36>/S-Function'

  uint16_T SFunction_P4_io;          // Expression: uint16(private_adc_delay_ns)
                                        //  Referenced by: '<S36>/S-Function'

  uint16_T SFunction_P1_j[2];          // Computed Parameter: SFunction_P1_j
                                          //  Referenced by: '<S54>/S-Function'

  uint16_T SFunction_P9;               // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S54>/S-Function'

  uint16_T SFunction_P11_d;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S54>/S-Function'

  uint16_T SFunction_P14_j;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S54>/S-Function'

  uint16_T SFunction_P15;              // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S54>/S-Function'

  uint16_T SFunction_P1_b[2];          // Computed Parameter: SFunction_P1_b
                                          //  Referenced by: '<S56>/S-Function'

  uint16_T SFunction_P9_n;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S56>/S-Function'

  uint16_T SFunction_P11_m;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S56>/S-Function'

  uint16_T SFunction_P14_p;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S56>/S-Function'

  uint16_T SFunction_P15_p;            // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S56>/S-Function'

  uint16_T SFunction_P1_fu[3];         // Computed Parameter: SFunction_P1_fu
                                          //  Referenced by: '<S60>/S-Function'

  uint16_T SFunction_P9_d;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S60>/S-Function'

  uint16_T SFunction_P11_g;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S60>/S-Function'

  uint16_T SFunction_P14_pg;           // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S60>/S-Function'

  uint16_T SFunction_P15_g;            // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S60>/S-Function'

  uint16_T SFunction_P1_m[12];         // Computed Parameter: SFunction_P1_m
                                          //  Referenced by: '<S58>/S-Function'

  uint16_T SFunction_P9_l;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S58>/S-Function'

  uint16_T SFunction_P11_a;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S58>/S-Function'

  uint16_T SFunction_P14_e;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S58>/S-Function'

  uint16_T SFunction_P15_a;            // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S58>/S-Function'

  uint16_T SFunction_P1_bs[2];         // Computed Parameter: SFunction_P1_bs
                                          //  Referenced by: '<S66>/S-Function'

  uint16_T SFunction_P9_j;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S66>/S-Function'

  uint16_T SFunction_P11_b;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S66>/S-Function'

  uint16_T SFunction_P14_eq;           // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S66>/S-Function'

  uint16_T SFunction_P15_b;            // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S66>/S-Function'

  uint16_T SFunction_P1_ly[3];         // Computed Parameter: SFunction_P1_ly
                                          //  Referenced by: '<S62>/S-Function'

  uint16_T SFunction_P9_dm;            // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S62>/S-Function'

  uint16_T SFunction_P11_i;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S62>/S-Function'

  uint16_T SFunction_P14_pgt;          // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S62>/S-Function'

  uint16_T SFunction_P15_n;            // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S62>/S-Function'

  uint16_T SFunction_P1_kb[2];         // Computed Parameter: SFunction_P1_kb
                                          //  Referenced by: '<S68>/S-Function'

  uint16_T SFunction_P9_p;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S68>/S-Function'

  uint16_T SFunction_P11_k;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S68>/S-Function'

  uint16_T SFunction_P14_a;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S68>/S-Function'

  uint16_T SFunction_P15_m;            // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S68>/S-Function'

  uint16_T SFunction_P1_lo[3];         // Computed Parameter: SFunction_P1_lo
                                          //  Referenced by: '<S64>/S-Function'

  uint16_T SFunction_P9_a;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S64>/S-Function'

  uint16_T SFunction_P11_ck;           // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S64>/S-Function'

  uint16_T SFunction_P14_b;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S64>/S-Function'

  uint16_T SFunction_P15_ps;           // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S64>/S-Function'

  boolean_T PWM_P10;                   // Expression: boolean(dutyrealtime)
                                          //  Referenced by: '<S40>/PWM'

  boolean_T PWM_P11;                   // Expression: boolean(phaserealtime)
                                          //  Referenced by: '<S40>/PWM'

  boolean_T PWM_P12;                   // Expression: boolean(activaterealtime)
                                          //  Referenced by: '<S40>/PWM'

  boolean_T PWM_P10_o;                 // Expression: boolean(dutyrealtime)
                                          //  Referenced by: '<S42>/PWM'

  boolean_T PWM_P11_c;                 // Expression: boolean(phaserealtime)
                                          //  Referenced by: '<S42>/PWM'

  boolean_T PWM_P12_o;                 // Expression: boolean(activaterealtime)
                                          //  Referenced by: '<S42>/PWM'

  boolean_T PWM_P10_b;                 // Expression: boolean(dutyrealtime)
                                          //  Referenced by: '<S44>/PWM'

  boolean_T PWM_P11_j;                 // Expression: boolean(phaserealtime)
                                          //  Referenced by: '<S44>/PWM'

  boolean_T PWM_P12_j;                 // Expression: boolean(activaterealtime)
                                          //  Referenced by: '<S44>/PWM'

  boolean_T SFunction_P4_l;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S46>/S-Function'

  boolean_T SFunction_P9_am;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S46>/S-Function'

  boolean_T SFunction_P10_n;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S46>/S-Function'

  boolean_T SFunction_P15_e;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S46>/S-Function'

  boolean_T SFunction_P4_f;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S48>/S-Function'

  boolean_T SFunction_P9_m;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S48>/S-Function'

  boolean_T SFunction_P10_o5;          // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S48>/S-Function'

  boolean_T SFunction_P15_h;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S48>/S-Function'

  boolean_T SFunction_P4_iy;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S50>/S-Function'

  boolean_T SFunction_P9_nw;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S50>/S-Function'

  boolean_T SFunction_P10_j;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S50>/S-Function'

  boolean_T SFunction_P15_k;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S50>/S-Function'

  boolean_T SFunction_P4_m;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S52>/S-Function'

  boolean_T SFunction_P9_m0;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S52>/S-Function'

  boolean_T SFunction_P10_h;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S52>/S-Function'

  boolean_T SFunction_P15_l;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S52>/S-Function'

  boolean_T ADC_P5;                    // Expression: boolean(usehist)
                                          //  Referenced by: '<S25>/ADC'

  boolean_T ADC_P5_j;                  // Expression: boolean(usehist)
                                          //  Referenced by: '<S27>/ADC'

  boolean_T ADC_P5_f;                  // Expression: boolean(usehist)
                                          //  Referenced by: '<S29>/ADC'

  boolean_T ADC_P5_b;                  // Expression: boolean(usehist)
                                          //  Referenced by: '<S31>/ADC'

  boolean_T CLK1_P3;                   // Expression: boolean(var_freq)
                                          //  Referenced by: '<S38>/CLK1'

  boolean_T SFunction_P8_j;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S54>/S-Function'

  boolean_T SFunction_P12_p;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S54>/S-Function'

  boolean_T SFunction_P13_n;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S54>/S-Function'

  boolean_T SFunction_P16;             // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S54>/S-Function'

  boolean_T CLK1_P3_i;                 // Expression: boolean(var_freq)
                                          //  Referenced by: '<S33>/CLK1'

  boolean_T SFunction_P8_i;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S56>/S-Function'

  boolean_T SFunction_P12_a;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S56>/S-Function'

  boolean_T SFunction_P13_k;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S56>/S-Function'

  boolean_T SFunction_P16_j;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S56>/S-Function'

  boolean_T SFunction_P8_dw;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S60>/S-Function'

  boolean_T SFunction_P12_cs;          // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S60>/S-Function'

  boolean_T SFunction_P13_b;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S60>/S-Function'

  boolean_T SFunction_P16_e;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S60>/S-Function'

  boolean_T SFunction_P8_du;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S58>/S-Function'

  boolean_T SFunction_P12_ca;          // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S58>/S-Function'

  boolean_T SFunction_P13_o;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S58>/S-Function'

  boolean_T SFunction_P16_f;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S58>/S-Function'

  boolean_T SFunction_P8_m;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S66>/S-Function'

  boolean_T SFunction_P12_e;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S66>/S-Function'

  boolean_T SFunction_P13_i;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S66>/S-Function'

  boolean_T SFunction_P16_g;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S66>/S-Function'

  boolean_T SFunction_P8_d0;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S62>/S-Function'

  boolean_T SFunction_P12_cc;          // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S62>/S-Function'

  boolean_T SFunction_P13_ea;          // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S62>/S-Function'

  boolean_T SFunction_P16_l;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S62>/S-Function'

  boolean_T SFunction_P8_dd;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S68>/S-Function'

  boolean_T SFunction_P12_ac;          // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S68>/S-Function'

  boolean_T SFunction_P13_g;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S68>/S-Function'

  boolean_T SFunction_P16_c;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S68>/S-Function'

  boolean_T SFunction_P8_a;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S64>/S-Function'

  boolean_T SFunction_P12_h;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S64>/S-Function'

  boolean_T SFunction_P13_oo;          // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S64>/S-Function'

  boolean_T SFunction_P16_d;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S64>/S-Function'

};

// Real-time Model Data Structure
struct tag_RTM_EJ2311_PWM_T {
  const char_T * volatile errorStatus;
};

// Block parameters (default storage)
#ifdef __cplusplus

extern "C"
{

#endif

  extern P_EJ2311_PWM_T EJ2311_PWM_P;

#ifdef __cplusplus

}

#endif

// Block signals (default storage)
#ifdef __cplusplus

extern "C"
{

#endif

  extern struct B_EJ2311_PWM_T EJ2311_PWM_B;

#ifdef __cplusplus

}

#endif

// Block states (default storage)
extern struct DW_EJ2311_PWM_T EJ2311_PWM_DW;

#ifdef __cplusplus

extern "C"
{

#endif

  // Model entry point functions
  extern void EJ2311_PWM_initialize(void);
  extern void EJ2311_PWM_step(void);
  extern void EJ2311_PWM_terminate(void);

#ifdef __cplusplus

}

#endif

// Real-time Model object
#ifdef __cplusplus

extern "C"
{

#endif

  extern RT_MODEL_EJ2311_PWM_T *const EJ2311_PWM_M;

#ifdef __cplusplus

}

#endif

//-
//  These blocks were eliminated from the model due to optimizations:
//
//  Block '<S1>/DC bus voltage' : Unused code path elimination
//  Block '<S1>/Phase currents' : Unused code path elimination
//  Block '<S7>/Data Type Conversion1' : Eliminate redundant data type conversion
//  Block '<S9>/Data Type Conversion1' : Eliminate redundant data type conversion
//  Block '<S9>/Data Type Conversion2' : Eliminate redundant data type conversion
//  Block '<S9>/Data Type Conversion3' : Eliminate redundant data type conversion
//  Block '<S10>/Data Type Conversion1' : Eliminate redundant data type conversion
//  Block '<S10>/Data Type Conversion2' : Eliminate redundant data type conversion
//  Block '<S10>/Data Type Conversion3' : Eliminate redundant data type conversion
//  Block '<S11>/Data Type Conversion1' : Eliminate redundant data type conversion
//  Block '<S11>/Data Type Conversion2' : Eliminate redundant data type conversion
//  Block '<S11>/Data Type Conversion3' : Eliminate redundant data type conversion
//  Block '<S46>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S48>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S50>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S52>/Data Type Conversion' : Eliminate redundant data type conversion


//-
//  The generated code includes comments that allow you to trace directly
//  back to the appropriate location in the model.  The basic format
//  is <system>/block_name, where system is the system number (uniquely
//  assigned by Simulink) and block_name is the name of the block.
//
//  Use the MATLAB hilite_system command to trace the generated code back
//  to the model.  For example,
//
//  hilite_system('<S3>')    - opens system 3
//  hilite_system('<S3>/Kp') - opens and selects block Kp which resides in S3
//
//  Here is the system hierarchy for this model
//
//  '<Root>' : 'EJ2311_PWM'
//  '<S1>'   : 'EJ2311_PWM/Closed_loop_control'
//  '<S2>'   : 'EJ2311_PWM/Plant_Model'
//  '<S3>'   : 'EJ2311_PWM/Closed_loop_control/ADC'
//  '<S4>'   : 'EJ2311_PWM/Closed_loop_control/ADC1'
//  '<S5>'   : 'EJ2311_PWM/Closed_loop_control/ADC2'
//  '<S6>'   : 'EJ2311_PWM/Closed_loop_control/ADC3'
//  '<S7>'   : 'EJ2311_PWM/Closed_loop_control/CLK'
//  '<S8>'   : 'EJ2311_PWM/Closed_loop_control/Configuration'
//  '<S9>'   : 'EJ2311_PWM/Closed_loop_control/PWM_CB'
//  '<S10>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB1'
//  '<S11>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB2'
//  '<S12>'  : 'EJ2311_PWM/Closed_loop_control/Probe'
//  '<S13>'  : 'EJ2311_PWM/Closed_loop_control/Probe1'
//  '<S14>'  : 'EJ2311_PWM/Closed_loop_control/Probe2'
//  '<S15>'  : 'EJ2311_PWM/Closed_loop_control/Probe6'
//  '<S16>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter1'
//  '<S17>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter2'
//  '<S18>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter3'
//  '<S19>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter4'
//  '<S20>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter5'
//  '<S21>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter6'
//  '<S22>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter7'
//  '<S23>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter8'
//  '<S24>'  : 'EJ2311_PWM/Closed_loop_control/ADC/sub'
//  '<S25>'  : 'EJ2311_PWM/Closed_loop_control/ADC/sub/generation'
//  '<S26>'  : 'EJ2311_PWM/Closed_loop_control/ADC1/sub'
//  '<S27>'  : 'EJ2311_PWM/Closed_loop_control/ADC1/sub/generation'
//  '<S28>'  : 'EJ2311_PWM/Closed_loop_control/ADC2/sub'
//  '<S29>'  : 'EJ2311_PWM/Closed_loop_control/ADC2/sub/generation'
//  '<S30>'  : 'EJ2311_PWM/Closed_loop_control/ADC3/sub'
//  '<S31>'  : 'EJ2311_PWM/Closed_loop_control/ADC3/sub/generation'
//  '<S32>'  : 'EJ2311_PWM/Closed_loop_control/CLK/sub'
//  '<S33>'  : 'EJ2311_PWM/Closed_loop_control/CLK/sub/generation'
//  '<S34>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/Sampling clock'
//  '<S35>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/clk0'
//  '<S36>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/Sampling clock/generation'
//  '<S37>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/clk0/sub'
//  '<S38>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/clk0/sub/generation'
//  '<S39>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB/sub'
//  '<S40>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB/sub/generation'
//  '<S41>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB1/sub'
//  '<S42>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB1/sub/generation'
//  '<S43>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB2/sub'
//  '<S44>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB2/sub/generation'
//  '<S45>'  : 'EJ2311_PWM/Closed_loop_control/Probe/sub'
//  '<S46>'  : 'EJ2311_PWM/Closed_loop_control/Probe/sub/generation'
//  '<S47>'  : 'EJ2311_PWM/Closed_loop_control/Probe1/sub'
//  '<S48>'  : 'EJ2311_PWM/Closed_loop_control/Probe1/sub/generation'
//  '<S49>'  : 'EJ2311_PWM/Closed_loop_control/Probe2/sub'
//  '<S50>'  : 'EJ2311_PWM/Closed_loop_control/Probe2/sub/generation'
//  '<S51>'  : 'EJ2311_PWM/Closed_loop_control/Probe6/sub'
//  '<S52>'  : 'EJ2311_PWM/Closed_loop_control/Probe6/sub/generation'
//  '<S53>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter1/sub'
//  '<S54>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter1/sub/generation'
//  '<S55>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter2/sub'
//  '<S56>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter2/sub/generation'
//  '<S57>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter3/sub'
//  '<S58>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter3/sub/generation'
//  '<S59>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter4/sub'
//  '<S60>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter4/sub/generation'
//  '<S61>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter5/sub'
//  '<S62>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter5/sub/generation'
//  '<S63>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter6/sub'
//  '<S64>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter6/sub/generation'
//  '<S65>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter7/sub'
//  '<S66>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter7/sub/generation'
//  '<S67>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter8/sub'
//  '<S68>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter8/sub/generation'

#endif                                 // RTW_HEADER_EJ2311_PWM_h_

//
// End of automatically generated code
// Copyright imperix ltd. Switzerland 2021
// [EOF]
//

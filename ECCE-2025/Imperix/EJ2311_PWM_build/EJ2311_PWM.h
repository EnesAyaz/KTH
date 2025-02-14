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
// C/C++ source code generated on : Wed Feb 12 15:00:19 2025
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
  real32_T ADC;                        // '<S28>/ADC'
  real32_T ADC_f;                      // '<S30>/ADC'
  real32_T ADC_d;                      // '<S32>/ADC'
  real32_T ADC_k;                      // '<S34>/ADC'
  real32_T SFunction;                  // '<S73>/S-Function'
  real32_T Saturation;                 // '<S38>/Saturation'
  real32_T SFunction_o;                // '<S71>/S-Function'
  real32_T SFunction_d;                // '<S75>/S-Function'
  real32_T DataTypeConversion2;        // '<S10>/Data Type Conversion2'
  real32_T Dutycycles[3];              // '<S1>/Sum2'
  real32_T SFunction_c;                // '<S77>/S-Function'
  real32_T DataTypeConversion2_l;      // '<S11>/Data Type Conversion2'
  real32_T DataTypeConversion2_g;      // '<S12>/Data Type Conversion2'
  real32_T Vdc2[3];                    // '<S1>/Vdc//2'
};

// Block states (default storage) for system '<Root>'
struct DW_EJ2311_PWM_T {
  real_T SFunction_DSTATE;             // '<S51>/S-Function'
  real_T SFunction_DSTATE_n;           // '<S53>/S-Function'
  real_T SFunction_DSTATE_p;           // '<S55>/S-Function'
  real_T SFunction_DSTATE_k;           // '<S63>/S-Function'
  real_T SFunction_DSTATE_n5;          // '<S41>/S-Function'
  real_T SFunction_DSTATE_b;           // '<S57>/S-Function'
  real_T SFunction_DSTATE_pk;          // '<S59>/S-Function'
  real_T SFunction_DSTATE_h;           // '<S61>/S-Function'
  real_T SFunction_DSTATE_bo;          // '<S65>/S-Function'
  real_T SFunction_DSTATE_a;           // '<S67>/S-Function'
  real_T SFunction_DSTATE_c;           // '<S69>/S-Function'
  real_T Delay_DSTATE;                 // '<S7>/Delay'
  real_T SFunction_DSTATE_m;           // '<S73>/S-Function'
  real_T SFunction_DSTATE_hg;          // '<S71>/S-Function'
  real_T SFunction_DSTATE_kp;          // '<S75>/S-Function'
  real_T SFunction_DSTATE_f;           // '<S77>/S-Function'
};

// Parameters (default storage)
struct P_EJ2311_PWM_T_ {
  real_T Delay_InitialCondition;       // Expression: 0.0
                                          //  Referenced by: '<S7>/Delay'

  real_T WeightedSampleTime_WtEt; // Computed Parameter: WeightedSampleTime_WtEt
                                     //  Referenced by: '<S7>/Weighted Sample Time'

  real_T DataStoreMemory_InitialValue; // Expression: 0
                                          //  Referenced by: '<S7>/Data Store Memory'

  real_T phase_Value;                  // Expression: PHASE
                                          //  Referenced by: '<S10>/phase'

  real_T phase_Value_n;                // Expression: PHASE
                                          //  Referenced by: '<S11>/phase'

  real_T phase_Value_c;                // Expression: PHASE
                                          //  Referenced by: '<S12>/phase'

  real32_T PWM_P2;                     // Expression: single(deadtime)
                                          //  Referenced by: '<S45>/PWM'

  real32_T PWM_P3;                     // Expression: single(duty)
                                          //  Referenced by: '<S45>/PWM'

  real32_T PWM_P4;                     // Expression: single(phase)
                                          //  Referenced by: '<S45>/PWM'

  real32_T PWM_P2_b;                   // Expression: single(deadtime)
                                          //  Referenced by: '<S47>/PWM'

  real32_T PWM_P3_e;                   // Expression: single(duty)
                                          //  Referenced by: '<S47>/PWM'

  real32_T PWM_P4_a;                   // Expression: single(phase)
                                          //  Referenced by: '<S47>/PWM'

  real32_T PWM_P2_e;                   // Expression: single(deadtime)
                                          //  Referenced by: '<S49>/PWM'

  real32_T PWM_P3_b;                   // Expression: single(duty)
                                          //  Referenced by: '<S49>/PWM'

  real32_T PWM_P4_h;                   // Expression: single(phase)
                                          //  Referenced by: '<S49>/PWM'

  real32_T Gain2_Gain;                 // Computed Parameter: Gain2_Gain
                                          //  Referenced by: '<S1>/Gain2'

  real32_T Gain3_Gain;                 // Computed Parameter: Gain3_Gain
                                          //  Referenced by: '<S1>/Gain3'

  real32_T SFunction_P6;               // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S51>/S-Function'

  real32_T SFunction_P12;              // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S51>/S-Function'

  real32_T SFunction_P6_c;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S53>/S-Function'

  real32_T SFunction_P12_d;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S53>/S-Function'

  real32_T SFunction_P6_k;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S55>/S-Function'

  real32_T SFunction_P12_c;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S55>/S-Function'

  real32_T SFunction_P6_cv;            // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S63>/S-Function'

  real32_T SFunction_P12_g;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S63>/S-Function'

  real32_T ADC_P2;                     // Expression: single(gain)
                                          //  Referenced by: '<S28>/ADC'

  real32_T ADC_P3;                     // Expression: single(offset)
                                          //  Referenced by: '<S28>/ADC'

  real32_T ADC_P2_a;                   // Expression: single(gain)
                                          //  Referenced by: '<S30>/ADC'

  real32_T ADC_P3_m;                   // Expression: single(offset)
                                          //  Referenced by: '<S30>/ADC'

  real32_T ADC_P2_d;                   // Expression: single(gain)
                                          //  Referenced by: '<S32>/ADC'

  real32_T ADC_P3_e;                   // Expression: single(offset)
                                          //  Referenced by: '<S32>/ADC'

  real32_T ADC_P2_g;                   // Expression: single(gain)
                                          //  Referenced by: '<S34>/ADC'

  real32_T ADC_P3_a;                   // Expression: single(offset)
                                          //  Referenced by: '<S34>/ADC'

  real32_T SFunction_P2;               // Expression: single(phase_vector)
                                          //  Referenced by: '<S41>/S-Function'

  real32_T SFunction_P3;               // Expression: single(interrupt_phase)
                                          //  Referenced by: '<S41>/S-Function'

  real32_T CLK1_P2;                    // Expression: single(frequency)
                                          //  Referenced by: '<S43>/CLK1'

  real32_T SFunction_P6_p;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S57>/S-Function'

  real32_T SFunction_P12_n;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S57>/S-Function'

  real32_T SFunction_P6_cu;            // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S59>/S-Function'

  real32_T SFunction_P12_a;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S59>/S-Function'

  real32_T SFunction_P6_o;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S61>/S-Function'

  real32_T SFunction_P12_i;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S61>/S-Function'

  real32_T SFunction_P6_h;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S65>/S-Function'

  real32_T SFunction_P12_e;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S65>/S-Function'

  real32_T SFunction_P6_a;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S67>/S-Function'

  real32_T SFunction_P12_ew;           // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S67>/S-Function'

  real32_T SFunction_P6_n;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S69>/S-Function'

  real32_T SFunction_P12_l;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S69>/S-Function'

  real32_T Constant_Value;             // Computed Parameter: Constant_Value
                                          //  Referenced by: '<S7>/Constant'

  real32_T SFunction_P3_g;             // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S73>/S-Function'

  real32_T SFunction_P4;               // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S73>/S-Function'

  real32_T SFunction_P5;               // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S73>/S-Function'

  real32_T SFunction_P6_l;             // Expression: single(0)
                                          //  Referenced by: '<S73>/S-Function'

  real32_T SFunction_P7;               // Expression: single(0)
                                          //  Referenced by: '<S73>/S-Function'

  real32_T Gain1_Gain;                 // Computed Parameter: Gain1_Gain
                                          //  Referenced by: '<S1>/Gain1'

  real32_T Saturation_UpperSat;       // Computed Parameter: Saturation_UpperSat
                                         //  Referenced by: '<S38>/Saturation'

  real32_T Saturation_LowerSat;       // Computed Parameter: Saturation_LowerSat
                                         //  Referenced by: '<S38>/Saturation'

  real32_T CLK1_P2_l;                  // Expression: single(frequency)
                                          //  Referenced by: '<S38>/CLK1'

  real32_T Constant_Value_j;           // Computed Parameter: Constant_Value_j
                                          //  Referenced by: '<S1>/Constant'

  real32_T Constant1_Value;            // Computed Parameter: Constant1_Value
                                          //  Referenced by: '<S1>/Constant1'

  real32_T SFunction_P3_gc;            // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S71>/S-Function'

  real32_T SFunction_P4_p;             // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S71>/S-Function'

  real32_T SFunction_P5_e;             // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S71>/S-Function'

  real32_T SFunction_P6_g;             // Expression: single(0)
                                          //  Referenced by: '<S71>/S-Function'

  real32_T SFunction_P7_o;             // Expression: single(0)
                                          //  Referenced by: '<S71>/S-Function'

  real32_T SFunction_P3_l;             // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S75>/S-Function'

  real32_T SFunction_P4_pz;            // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S75>/S-Function'

  real32_T SFunction_P5_g;             // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S75>/S-Function'

  real32_T SFunction_P6_gd;            // Expression: single(0)
                                          //  Referenced by: '<S75>/S-Function'

  real32_T SFunction_P7_k;             // Expression: single(0)
                                          //  Referenced by: '<S75>/S-Function'

  real32_T Switch_Threshold;           // Computed Parameter: Switch_Threshold
                                          //  Referenced by: '<S1>/Switch'

  real32_T Gain_Gain;                  // Computed Parameter: Gain_Gain
                                          //  Referenced by: '<S1>/Gain'

  real32_T SFunction_P3_n;             // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S77>/S-Function'

  real32_T SFunction_P4_h;             // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S77>/S-Function'

  real32_T SFunction_P5_f;             // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S77>/S-Function'

  real32_T SFunction_P6_ps;            // Expression: single(0)
                                          //  Referenced by: '<S77>/S-Function'

  real32_T SFunction_P7_g;             // Expression: single(0)
                                          //  Referenced by: '<S77>/S-Function'

  real32_T Vdc2_Gain;                  // Computed Parameter: Vdc2_Gain
                                          //  Referenced by: '<S1>/Vdc//2'

  uint32_T SFunction_P7_j;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S51>/S-Function'

  uint32_T SFunction_P13;              // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S51>/S-Function'

  uint32_T SFunction_P7_gg;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S53>/S-Function'

  uint32_T SFunction_P13_a;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S53>/S-Function'

  uint32_T SFunction_P7_b;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S55>/S-Function'

  uint32_T SFunction_P13_e;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S55>/S-Function'

  uint32_T SFunction_P7_oo;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S63>/S-Function'

  uint32_T SFunction_P13_c;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S63>/S-Function'

  uint32_T SFunction_P7_a;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S57>/S-Function'

  uint32_T SFunction_P13_k;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S57>/S-Function'

  uint32_T SFunction_P7_a0;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S59>/S-Function'

  uint32_T SFunction_P13_k1;           // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S59>/S-Function'

  uint32_T SFunction_P7_e;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S61>/S-Function'

  uint32_T SFunction_P13_n;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S61>/S-Function'

  uint32_T SFunction_P7_b0;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S65>/S-Function'

  uint32_T SFunction_P13_o;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S65>/S-Function'

  uint32_T SFunction_P7_h;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S67>/S-Function'

  uint32_T SFunction_P13_cw;           // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S67>/S-Function'

  uint32_T SFunction_P7_n;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S69>/S-Function'

  uint32_T SFunction_P13_m;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S69>/S-Function'

  uint32_T SFunction_P10;              // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S73>/S-Function'

  uint32_T SFunction_P10_h;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S71>/S-Function'

  uint32_T SFunction_P10_d;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S75>/S-Function'

  uint32_T SFunction_P10_k;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S77>/S-Function'

  int16_T PWM_P1;                      // Expression: int16(lane)
                                          //  Referenced by: '<S45>/PWM'

  int16_T PWM_P5;                      // Expression: int16(carrier)
                                          //  Referenced by: '<S45>/PWM'

  int16_T PWM_P6;                      // Expression: int16(rate)
                                          //  Referenced by: '<S45>/PWM'

  int16_T PWM_P7;                      // Expression: int16(outconf)
                                          //  Referenced by: '<S45>/PWM'

  int16_T PWM_P8;                      // Expression: int16(outmode)
                                          //  Referenced by: '<S45>/PWM'

  int16_T PWM_P9;                      // Expression: int16(nbBbx)
                                          //  Referenced by: '<S45>/PWM'

  int16_T PWM_P1_a;                    // Expression: int16(lane)
                                          //  Referenced by: '<S47>/PWM'

  int16_T PWM_P5_a;                    // Expression: int16(carrier)
                                          //  Referenced by: '<S47>/PWM'

  int16_T PWM_P6_o;                    // Expression: int16(rate)
                                          //  Referenced by: '<S47>/PWM'

  int16_T PWM_P7_e;                    // Expression: int16(outconf)
                                          //  Referenced by: '<S47>/PWM'

  int16_T PWM_P8_k;                    // Expression: int16(outmode)
                                          //  Referenced by: '<S47>/PWM'

  int16_T PWM_P9_j;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S47>/PWM'

  int16_T PWM_P1_k;                    // Expression: int16(lane)
                                          //  Referenced by: '<S49>/PWM'

  int16_T PWM_P5_o;                    // Expression: int16(carrier)
                                          //  Referenced by: '<S49>/PWM'

  int16_T PWM_P6_i;                    // Expression: int16(rate)
                                          //  Referenced by: '<S49>/PWM'

  int16_T PWM_P7_l;                    // Expression: int16(outconf)
                                          //  Referenced by: '<S49>/PWM'

  int16_T PWM_P8_o;                    // Expression: int16(outmode)
                                          //  Referenced by: '<S49>/PWM'

  int16_T PWM_P9_n;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S49>/PWM'

  int16_T SFunction_P2_e;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S51>/S-Function'

  int16_T SFunction_P3_d;              // Expression: int16(0)
                                          //  Referenced by: '<S51>/S-Function'

  int16_T SFunction_P2_b;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S53>/S-Function'

  int16_T SFunction_P3_f;              // Expression: int16(0)
                                          //  Referenced by: '<S53>/S-Function'

  int16_T SFunction_P2_j;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S55>/S-Function'

  int16_T SFunction_P3_p;              // Expression: int16(0)
                                          //  Referenced by: '<S55>/S-Function'

  int16_T SFunction_P2_h;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S63>/S-Function'

  int16_T SFunction_P3_g3;             // Expression: int16(0)
                                          //  Referenced by: '<S63>/S-Function'

  int16_T ADC_P1;                      // Expression: int16(channel)
                                          //  Referenced by: '<S28>/ADC'

  int16_T ADC_P4;                      // Expression: int16(nbBbx)
                                          //  Referenced by: '<S28>/ADC'

  int16_T ADC_P6;                      // Expression: int16(outputwidth)
                                          //  Referenced by: '<S28>/ADC'

  int16_T ADC_P1_h;                    // Expression: int16(channel)
                                          //  Referenced by: '<S30>/ADC'

  int16_T ADC_P4_c;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S30>/ADC'

  int16_T ADC_P6_e;                    // Expression: int16(outputwidth)
                                          //  Referenced by: '<S30>/ADC'

  int16_T ADC_P1_m;                    // Expression: int16(channel)
                                          //  Referenced by: '<S32>/ADC'

  int16_T ADC_P4_l;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S32>/ADC'

  int16_T ADC_P6_m;                    // Expression: int16(outputwidth)
                                          //  Referenced by: '<S32>/ADC'

  int16_T ADC_P1_j;                    // Expression: int16(channel)
                                          //  Referenced by: '<S34>/ADC'

  int16_T ADC_P4_m;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S34>/ADC'

  int16_T ADC_P6_p;                    // Expression: int16(outputwidth)
                                          //  Referenced by: '<S34>/ADC'

  int16_T clk_id_Value;                // Computed Parameter: clk_id_Value
                                          //  Referenced by: '<S43>/clk_id'

  int16_T CLK1_P1;                     // Expression: int16(id)
                                          //  Referenced by: '<S43>/CLK1'

  int16_T SFunction_P2_l;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S57>/S-Function'

  int16_T SFunction_P3_e;              // Expression: int16(0)
                                          //  Referenced by: '<S57>/S-Function'

  int16_T SFunction_P2_bk;             // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S59>/S-Function'

  int16_T SFunction_P3_b;              // Expression: int16(0)
                                          //  Referenced by: '<S59>/S-Function'

  int16_T SFunction_P2_p;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S61>/S-Function'

  int16_T SFunction_P3_k;              // Expression: int16(0)
                                          //  Referenced by: '<S61>/S-Function'

  int16_T SFunction_P2_i;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S65>/S-Function'

  int16_T SFunction_P3_h;              // Expression: int16(0)
                                          //  Referenced by: '<S65>/S-Function'

  int16_T SFunction_P2_n;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S67>/S-Function'

  int16_T SFunction_P3_hu;             // Expression: int16(0)
                                          //  Referenced by: '<S67>/S-Function'

  int16_T SFunction_P2_a;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S69>/S-Function'

  int16_T SFunction_P3_j;              // Expression: int16(0)
                                          //  Referenced by: '<S69>/S-Function'

  int16_T clk_id_Value_a;              // Computed Parameter: clk_id_Value_a
                                          //  Referenced by: '<S38>/clk_id'

  int16_T SFunction_P2_lf;             // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S73>/S-Function'

  int16_T CLK1_P1_h;                   // Expression: int16(id)
                                          //  Referenced by: '<S38>/CLK1'

  int16_T SFunction_P2_m;              // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S71>/S-Function'

  int16_T SFunction_P2_k;              // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S75>/S-Function'

  int16_T SFunction_P2_m0;             // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S77>/S-Function'

  uint16_T SFunction_P1[2];            // Computed Parameter: SFunction_P1
                                          //  Referenced by: '<S51>/S-Function'

  uint16_T SFunction_P5_a;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S51>/S-Function'

  uint16_T SFunction_P8;               // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S51>/S-Function'

  uint16_T SFunction_P11;              // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S51>/S-Function'

  uint16_T SFunction_P14[5];           // Computed Parameter: SFunction_P14
                                          //  Referenced by: '<S51>/S-Function'

  uint16_T SFunction_P1_k[2];          // Computed Parameter: SFunction_P1_k
                                          //  Referenced by: '<S53>/S-Function'

  uint16_T SFunction_P5_l;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S53>/S-Function'

  uint16_T SFunction_P8_d;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S53>/S-Function'

  uint16_T SFunction_P11_c;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S53>/S-Function'

  uint16_T SFunction_P14_m[5];         // Computed Parameter: SFunction_P14_m
                                          //  Referenced by: '<S53>/S-Function'

  uint16_T SFunction_P1_l[2];          // Computed Parameter: SFunction_P1_l
                                          //  Referenced by: '<S55>/S-Function'

  uint16_T SFunction_P5_e4;            // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S55>/S-Function'

  uint16_T SFunction_P8_g;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S55>/S-Function'

  uint16_T SFunction_P11_f;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S55>/S-Function'

  uint16_T SFunction_P14_o[5];         // Computed Parameter: SFunction_P14_o
                                          //  Referenced by: '<S55>/S-Function'

  uint16_T SFunction_P1_lh[3];         // Computed Parameter: SFunction_P1_lh
                                          //  Referenced by: '<S63>/S-Function'

  uint16_T SFunction_P5_b;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S63>/S-Function'

  uint16_T SFunction_P8_f;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S63>/S-Function'

  uint16_T SFunction_P11_p;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S63>/S-Function'

  uint16_T SFunction_P14_l[5];         // Computed Parameter: SFunction_P14_l
                                          //  Referenced by: '<S63>/S-Function'

  uint16_T SFunction_P1_f;             // Expression: uint16(interrupt_pstsclr)
                                          //  Referenced by: '<S41>/S-Function'

  uint16_T SFunction_P4_i;           // Expression: uint16(private_adc_delay_ns)
                                        //  Referenced by: '<S41>/S-Function'

  uint16_T SFunction_P1_j[6];          // Computed Parameter: SFunction_P1_j
                                          //  Referenced by: '<S57>/S-Function'

  uint16_T SFunction_P5_gq;            // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S57>/S-Function'

  uint16_T SFunction_P8_dp;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S57>/S-Function'

  uint16_T SFunction_P11_pn;           // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S57>/S-Function'

  uint16_T SFunction_P14_a[5];         // Computed Parameter: SFunction_P14_a
                                          //  Referenced by: '<S57>/S-Function'

  uint16_T SFunction_P1_p[6];          // Computed Parameter: SFunction_P1_p
                                          //  Referenced by: '<S59>/S-Function'

  uint16_T SFunction_P5_i;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S59>/S-Function'

  uint16_T SFunction_P8_o;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S59>/S-Function'

  uint16_T SFunction_P11_fs;           // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S59>/S-Function'

  uint16_T SFunction_P14_e[5];         // Computed Parameter: SFunction_P14_e
                                          //  Referenced by: '<S59>/S-Function'

  uint16_T SFunction_P1_n[6];          // Computed Parameter: SFunction_P1_n
                                          //  Referenced by: '<S61>/S-Function'

  uint16_T SFunction_P5_o;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S61>/S-Function'

  uint16_T SFunction_P8_b;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S61>/S-Function'

  uint16_T SFunction_P11_e;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S61>/S-Function'

  uint16_T SFunction_P14_i[5];         // Computed Parameter: SFunction_P14_i
                                          //  Referenced by: '<S61>/S-Function'

  uint16_T SFunction_P1_py[3];         // Computed Parameter: SFunction_P1_py
                                          //  Referenced by: '<S65>/S-Function'

  uint16_T SFunction_P5_bl;            // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S65>/S-Function'

  uint16_T SFunction_P8_dh;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S65>/S-Function'

  uint16_T SFunction_P11_l;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S65>/S-Function'

  uint16_T SFunction_P14_n[5];         // Computed Parameter: SFunction_P14_n
                                          //  Referenced by: '<S65>/S-Function'

  uint16_T SFunction_P1_i[3];          // Computed Parameter: SFunction_P1_i
                                          //  Referenced by: '<S67>/S-Function'

  uint16_T SFunction_P5_fo;            // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S67>/S-Function'

  uint16_T SFunction_P8_h;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S67>/S-Function'

  uint16_T SFunction_P11_d;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S67>/S-Function'

  uint16_T SFunction_P14_mv[5];        // Computed Parameter: SFunction_P14_mv
                                          //  Referenced by: '<S67>/S-Function'

  uint16_T SFunction_P1_jd[3];         // Computed Parameter: SFunction_P1_jd
                                          //  Referenced by: '<S69>/S-Function'

  uint16_T SFunction_P5_ex;            // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S69>/S-Function'

  uint16_T SFunction_P8_dy;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S69>/S-Function'

  uint16_T SFunction_P11_a;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S69>/S-Function'

  uint16_T SFunction_P14_h[5];         // Computed Parameter: SFunction_P14_h
                                          //  Referenced by: '<S69>/S-Function'

  uint16_T SFunction_P1_jl;            // Computed Parameter: SFunction_P1_jl
                                          //  Referenced by: '<S73>/S-Function'

  uint16_T SFunction_P9;               // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S73>/S-Function'

  uint16_T SFunction_P11_d4;           // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S73>/S-Function'

  uint16_T SFunction_P14_j;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S73>/S-Function'

  uint16_T SFunction_P15;              // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S73>/S-Function'

  uint16_T SFunction_P1_fq;            // Computed Parameter: SFunction_P1_fq
                                          //  Referenced by: '<S71>/S-Function'

  uint16_T SFunction_P9_n;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S71>/S-Function'

  uint16_T SFunction_P11_k;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S71>/S-Function'

  uint16_T SFunction_P14_f;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S71>/S-Function'

  uint16_T SFunction_P15_p;            // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S71>/S-Function'

  uint16_T SFunction_P1_g[14];         // Computed Parameter: SFunction_P1_g
                                          //  Referenced by: '<S75>/S-Function'

  uint16_T SFunction_P9_p;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S75>/S-Function'

  uint16_T SFunction_P11_lo;           // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S75>/S-Function'

  uint16_T SFunction_P14_d;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S75>/S-Function'

  uint16_T SFunction_P15_o;            // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S75>/S-Function'

  uint16_T SFunction_P1_m[12];         // Computed Parameter: SFunction_P1_m
                                          //  Referenced by: '<S77>/S-Function'

  uint16_T SFunction_P9_l;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S77>/S-Function'

  uint16_T SFunction_P11_at;           // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S77>/S-Function'

  uint16_T SFunction_P14_ew;           // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S77>/S-Function'

  uint16_T SFunction_P15_a;            // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S77>/S-Function'

  boolean_T PWM_P10;                   // Expression: boolean(dutyrealtime)
                                          //  Referenced by: '<S45>/PWM'

  boolean_T PWM_P11;                   // Expression: boolean(phaserealtime)
                                          //  Referenced by: '<S45>/PWM'

  boolean_T PWM_P12;                   // Expression: boolean(activaterealtime)
                                          //  Referenced by: '<S45>/PWM'

  boolean_T PWM_P10_o;                 // Expression: boolean(dutyrealtime)
                                          //  Referenced by: '<S47>/PWM'

  boolean_T PWM_P11_c;                 // Expression: boolean(phaserealtime)
                                          //  Referenced by: '<S47>/PWM'

  boolean_T PWM_P12_o;                 // Expression: boolean(activaterealtime)
                                          //  Referenced by: '<S47>/PWM'

  boolean_T PWM_P10_b;                 // Expression: boolean(dutyrealtime)
                                          //  Referenced by: '<S49>/PWM'

  boolean_T PWM_P11_j;                 // Expression: boolean(phaserealtime)
                                          //  Referenced by: '<S49>/PWM'

  boolean_T PWM_P12_j;                 // Expression: boolean(activaterealtime)
                                          //  Referenced by: '<S49>/PWM'

  boolean_T SFunction_P4_l;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S51>/S-Function'

  boolean_T SFunction_P9_a;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S51>/S-Function'

  boolean_T SFunction_P10_n;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S51>/S-Function'

  boolean_T SFunction_P15_e;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S51>/S-Function'

  boolean_T SFunction_P4_f;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S53>/S-Function'

  boolean_T SFunction_P9_m;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S53>/S-Function'

  boolean_T SFunction_P10_o;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S53>/S-Function'

  boolean_T SFunction_P15_h;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S53>/S-Function'

  boolean_T SFunction_P4_iy;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S55>/S-Function'

  boolean_T SFunction_P9_nw;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S55>/S-Function'

  boolean_T SFunction_P10_j;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S55>/S-Function'

  boolean_T SFunction_P15_k;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S55>/S-Function'

  boolean_T SFunction_P4_m;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S63>/S-Function'

  boolean_T SFunction_P9_m0;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S63>/S-Function'

  boolean_T SFunction_P10_hu;          // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S63>/S-Function'

  boolean_T SFunction_P15_l;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S63>/S-Function'

  boolean_T ADC_P5;                    // Expression: boolean(usehist)
                                          //  Referenced by: '<S28>/ADC'

  boolean_T ADC_P5_j;                  // Expression: boolean(usehist)
                                          //  Referenced by: '<S30>/ADC'

  boolean_T ADC_P5_f;                  // Expression: boolean(usehist)
                                          //  Referenced by: '<S32>/ADC'

  boolean_T ADC_P5_b;                  // Expression: boolean(usehist)
                                          //  Referenced by: '<S34>/ADC'

  boolean_T CLK1_P3;                   // Expression: boolean(var_freq)
                                          //  Referenced by: '<S43>/CLK1'

  boolean_T SFunction_P4_k;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S57>/S-Function'

  boolean_T SFunction_P9_c;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S57>/S-Function'

  boolean_T SFunction_P10_p;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S57>/S-Function'

  boolean_T SFunction_P15_g;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S57>/S-Function'

  boolean_T SFunction_P4_pl;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S59>/S-Function'

  boolean_T SFunction_P9_i;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S59>/S-Function'

  boolean_T SFunction_P10_i;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S59>/S-Function'

  boolean_T SFunction_P15_j;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S59>/S-Function'

  boolean_T SFunction_P4_j;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S61>/S-Function'

  boolean_T SFunction_P9_b;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S61>/S-Function'

  boolean_T SFunction_P10_c;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S61>/S-Function'

  boolean_T SFunction_P15_jk;          // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S61>/S-Function'

  boolean_T SFunction_P4_n;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S65>/S-Function'

  boolean_T SFunction_P9_h;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S65>/S-Function'

  boolean_T SFunction_P10_f;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S65>/S-Function'

  boolean_T SFunction_P15_gg;          // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S65>/S-Function'

  boolean_T SFunction_P4_lb;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S67>/S-Function'

  boolean_T SFunction_P9_cz;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S67>/S-Function'

  boolean_T SFunction_P10_a;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S67>/S-Function'

  boolean_T SFunction_P15_px;          // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S67>/S-Function'

  boolean_T SFunction_P4_ku;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S69>/S-Function'

  boolean_T SFunction_P9_o;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S69>/S-Function'

  boolean_T SFunction_P10_c3;          // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S69>/S-Function'

  boolean_T SFunction_P15_ln;          // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S69>/S-Function'

  boolean_T SFunction_P8_j;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S73>/S-Function'

  boolean_T SFunction_P12_p;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S73>/S-Function'

  boolean_T SFunction_P13_nd;          // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S73>/S-Function'

  boolean_T SFunction_P16;             // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S73>/S-Function'

  boolean_T CLK1_P3_i;                 // Expression: boolean(var_freq)
                                          //  Referenced by: '<S38>/CLK1'

  boolean_T SFunction_P8_o5;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S71>/S-Function'

  boolean_T SFunction_P12_cu;          // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S71>/S-Function'

  boolean_T SFunction_P13_l;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S71>/S-Function'

  boolean_T SFunction_P16_i;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S71>/S-Function'

  boolean_T SFunction_P8_l;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S75>/S-Function'

  boolean_T SFunction_P12_b;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S75>/S-Function'

  boolean_T SFunction_P13_i;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S75>/S-Function'

  boolean_T SFunction_P16_e;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S75>/S-Function'

  boolean_T SFunction_P8_du;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S77>/S-Function'

  boolean_T SFunction_P12_ca;          // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S77>/S-Function'

  boolean_T SFunction_P13_od;          // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S77>/S-Function'

  boolean_T SFunction_P16_f;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S77>/S-Function'

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
//  Block '<S1>/Angle generator' : Unused code path elimination
//  Block '<S1>/DC bus voltage' : Unused code path elimination
//  Block '<S1>/Modulation and duty cycles' : Unused code path elimination
//  Block '<S1>/Phase currents' : Unused code path elimination
//  Block '<S1>/Reference phase voltage' : Unused code path elimination
//  Block '<S8>/Data Type Conversion1' : Eliminate redundant data type conversion
//  Block '<S10>/Data Type Conversion1' : Eliminate redundant data type conversion
//  Block '<S10>/Data Type Conversion3' : Eliminate redundant data type conversion
//  Block '<S11>/Data Type Conversion1' : Eliminate redundant data type conversion
//  Block '<S11>/Data Type Conversion3' : Eliminate redundant data type conversion
//  Block '<S12>/Data Type Conversion1' : Eliminate redundant data type conversion
//  Block '<S12>/Data Type Conversion3' : Eliminate redundant data type conversion
//  Block '<S51>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S53>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S55>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S57>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S59>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S61>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S63>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S65>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S67>/Data Type Conversion' : Eliminate redundant data type conversion
//  Block '<S69>/Data Type Conversion' : Eliminate redundant data type conversion


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
//  '<S7>'   : 'EJ2311_PWM/Closed_loop_control/Angle'
//  '<S8>'   : 'EJ2311_PWM/Closed_loop_control/CLK'
//  '<S9>'   : 'EJ2311_PWM/Closed_loop_control/Configuration'
//  '<S10>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB'
//  '<S11>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB1'
//  '<S12>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB2'
//  '<S13>'  : 'EJ2311_PWM/Closed_loop_control/Probe'
//  '<S14>'  : 'EJ2311_PWM/Closed_loop_control/Probe1'
//  '<S15>'  : 'EJ2311_PWM/Closed_loop_control/Probe2'
//  '<S16>'  : 'EJ2311_PWM/Closed_loop_control/Probe3'
//  '<S17>'  : 'EJ2311_PWM/Closed_loop_control/Probe4'
//  '<S18>'  : 'EJ2311_PWM/Closed_loop_control/Probe5'
//  '<S19>'  : 'EJ2311_PWM/Closed_loop_control/Probe6'
//  '<S20>'  : 'EJ2311_PWM/Closed_loop_control/Probe7'
//  '<S21>'  : 'EJ2311_PWM/Closed_loop_control/Probe8'
//  '<S22>'  : 'EJ2311_PWM/Closed_loop_control/Probe9'
//  '<S23>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter'
//  '<S24>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter1'
//  '<S25>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter2'
//  '<S26>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter3'
//  '<S27>'  : 'EJ2311_PWM/Closed_loop_control/ADC/sub'
//  '<S28>'  : 'EJ2311_PWM/Closed_loop_control/ADC/sub/generation'
//  '<S29>'  : 'EJ2311_PWM/Closed_loop_control/ADC1/sub'
//  '<S30>'  : 'EJ2311_PWM/Closed_loop_control/ADC1/sub/generation'
//  '<S31>'  : 'EJ2311_PWM/Closed_loop_control/ADC2/sub'
//  '<S32>'  : 'EJ2311_PWM/Closed_loop_control/ADC2/sub/generation'
//  '<S33>'  : 'EJ2311_PWM/Closed_loop_control/ADC3/sub'
//  '<S34>'  : 'EJ2311_PWM/Closed_loop_control/ADC3/sub/generation'
//  '<S35>'  : 'EJ2311_PWM/Closed_loop_control/Angle/If Action Subsystem'
//  '<S36>'  : 'EJ2311_PWM/Closed_loop_control/Angle/If Action Subsystem1'
//  '<S37>'  : 'EJ2311_PWM/Closed_loop_control/CLK/sub'
//  '<S38>'  : 'EJ2311_PWM/Closed_loop_control/CLK/sub/generation'
//  '<S39>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/Sampling clock'
//  '<S40>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/clk0'
//  '<S41>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/Sampling clock/generation'
//  '<S42>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/clk0/sub'
//  '<S43>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/clk0/sub/generation'
//  '<S44>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB/sub'
//  '<S45>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB/sub/generation'
//  '<S46>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB1/sub'
//  '<S47>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB1/sub/generation'
//  '<S48>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB2/sub'
//  '<S49>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB2/sub/generation'
//  '<S50>'  : 'EJ2311_PWM/Closed_loop_control/Probe/sub'
//  '<S51>'  : 'EJ2311_PWM/Closed_loop_control/Probe/sub/generation'
//  '<S52>'  : 'EJ2311_PWM/Closed_loop_control/Probe1/sub'
//  '<S53>'  : 'EJ2311_PWM/Closed_loop_control/Probe1/sub/generation'
//  '<S54>'  : 'EJ2311_PWM/Closed_loop_control/Probe2/sub'
//  '<S55>'  : 'EJ2311_PWM/Closed_loop_control/Probe2/sub/generation'
//  '<S56>'  : 'EJ2311_PWM/Closed_loop_control/Probe3/sub'
//  '<S57>'  : 'EJ2311_PWM/Closed_loop_control/Probe3/sub/generation'
//  '<S58>'  : 'EJ2311_PWM/Closed_loop_control/Probe4/sub'
//  '<S59>'  : 'EJ2311_PWM/Closed_loop_control/Probe4/sub/generation'
//  '<S60>'  : 'EJ2311_PWM/Closed_loop_control/Probe5/sub'
//  '<S61>'  : 'EJ2311_PWM/Closed_loop_control/Probe5/sub/generation'
//  '<S62>'  : 'EJ2311_PWM/Closed_loop_control/Probe6/sub'
//  '<S63>'  : 'EJ2311_PWM/Closed_loop_control/Probe6/sub/generation'
//  '<S64>'  : 'EJ2311_PWM/Closed_loop_control/Probe7/sub'
//  '<S65>'  : 'EJ2311_PWM/Closed_loop_control/Probe7/sub/generation'
//  '<S66>'  : 'EJ2311_PWM/Closed_loop_control/Probe8/sub'
//  '<S67>'  : 'EJ2311_PWM/Closed_loop_control/Probe8/sub/generation'
//  '<S68>'  : 'EJ2311_PWM/Closed_loop_control/Probe9/sub'
//  '<S69>'  : 'EJ2311_PWM/Closed_loop_control/Probe9/sub/generation'
//  '<S70>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter/sub'
//  '<S71>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter/sub/generation'
//  '<S72>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter1/sub'
//  '<S73>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter1/sub/generation'
//  '<S74>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter2/sub'
//  '<S75>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter2/sub/generation'
//  '<S76>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter3/sub'
//  '<S77>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter3/sub/generation'

#endif                                 // RTW_HEADER_EJ2311_PWM_h_

//
// End of automatically generated code
// Copyright imperix ltd. Switzerland 2021
// [EOF]
//

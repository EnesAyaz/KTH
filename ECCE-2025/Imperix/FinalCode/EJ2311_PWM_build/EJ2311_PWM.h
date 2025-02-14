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
// Model version                  : 16.7
// Simulink Coder version         : 23.2 (R2023b) 01-Aug-2023
// C/C++ source code generated on : Thu Feb 13 14:54:27 2025
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
  real32_T DataTypeConversion;         // '<S34>/Data Type Conversion'
  real32_T DataTypeConversion_g;       // '<S36>/Data Type Conversion'
  real32_T DataTypeConversion_p;       // '<S38>/Data Type Conversion'
  real32_T DataTypeConversion_m;       // '<S40>/Data Type Conversion'
  real32_T DataTypeConversion_b;       // '<S42>/Data Type Conversion'
  real32_T DataTypeConversion_i;       // '<S44>/Data Type Conversion'
  real32_T SFunction;                  // '<S46>/S-Function'
  real32_T Saturation;                 // '<S21>/Saturation'
  real32_T DataTypeConversion1;        // '<S7>/Data Type Conversion1'
  real32_T DataTypeConversion2;        // '<S7>/Data Type Conversion2'
  real32_T SFunction_c;                // '<S48>/S-Function'
  real32_T DataTypeConversion1_k;      // '<S8>/Data Type Conversion1'
  real32_T DataTypeConversion2_l;      // '<S8>/Data Type Conversion2'
  real32_T DataTypeConversion1_k0;     // '<S9>/Data Type Conversion1'
  real32_T DataTypeConversion2_g;      // '<S9>/Data Type Conversion2'
};

// Block states (default storage) for system '<Root>'
struct DW_EJ2311_PWM_T {
  real_T SFunction_DSTATE;             // '<S24>/S-Function'
  real_T SFunction_DSTATE_b;           // '<S34>/S-Function'
  real_T Delay_DSTATE;                 // '<S3>/Delay'
  real_T SFunction_DSTATE_p;           // '<S36>/S-Function'
  real_T SFunction_DSTATE_h;           // '<S38>/S-Function'
  real_T SFunction_DSTATE_bo;          // '<S40>/S-Function'
  real_T SFunction_DSTATE_a;           // '<S42>/S-Function'
  real_T SFunction_DSTATE_c;           // '<S44>/S-Function'
  real_T SFunction_DSTATE_m;           // '<S46>/S-Function'
  real_T SFunction_DSTATE_f;           // '<S48>/S-Function'
};

// Parameters (default storage)
struct P_EJ2311_PWM_T_ {
  real_T Constant2_Value;              // Expression: 0.2
                                          //  Referenced by: '<S1>/Constant2'

  real_T Delay_InitialCondition;       // Expression: 0.0
                                          //  Referenced by: '<S3>/Delay'

  real_T Vdc2_Gain;                    // Expression: 200/2
                                          //  Referenced by: '<S1>/Vdc//2'

  real_T Gain_Gain;                    // Expression: 0.5
                                          //  Referenced by: '<S1>/Gain'

  real_T Constant1_Value;              // Expression: 0.5
                                          //  Referenced by: '<S1>/Constant1'

  real_T WeightedSampleTime_WtEt; // Computed Parameter: WeightedSampleTime_WtEt
                                     //  Referenced by: '<S3>/Weighted Sample Time'

  real_T DataStoreMemory_InitialValue; // Expression: 0
                                          //  Referenced by: '<S3>/Data Store Memory'

  real_T Constant3_Value;              // Expression: 1
                                          //  Referenced by: '<S1>/Constant3'

  real_T ZeroPhaseShift_Value;         // Expression: 0
                                          //  Referenced by: '<S1>/Zero Phase Shift'

  real_T Switch1_Threshold;            // Expression: 0.5
                                          //  Referenced by: '<S1>/Switch1'

  real_T Switch2_Threshold;            // Expression: 0.5
                                          //  Referenced by: '<S1>/Switch2'

  real_T Switch3_Threshold;            // Expression: 0.5
                                          //  Referenced by: '<S1>/Switch3'

  real32_T PWM_P2;                     // Expression: single(deadtime)
                                          //  Referenced by: '<S28>/PWM'

  real32_T PWM_P3;                     // Expression: single(duty)
                                          //  Referenced by: '<S28>/PWM'

  real32_T PWM_P4;                     // Expression: single(phase)
                                          //  Referenced by: '<S28>/PWM'

  real32_T PWM_P2_b;                   // Expression: single(deadtime)
                                          //  Referenced by: '<S30>/PWM'

  real32_T PWM_P3_e;                   // Expression: single(duty)
                                          //  Referenced by: '<S30>/PWM'

  real32_T PWM_P4_a;                   // Expression: single(phase)
                                          //  Referenced by: '<S30>/PWM'

  real32_T PWM_P2_e;                   // Expression: single(deadtime)
                                          //  Referenced by: '<S32>/PWM'

  real32_T PWM_P3_b;                   // Expression: single(duty)
                                          //  Referenced by: '<S32>/PWM'

  real32_T PWM_P4_h;                   // Expression: single(phase)
                                          //  Referenced by: '<S32>/PWM'

  real32_T SFunction_P2;               // Expression: single(phase_vector)
                                          //  Referenced by: '<S24>/S-Function'

  real32_T SFunction_P3;               // Expression: single(interrupt_phase)
                                          //  Referenced by: '<S24>/S-Function'

  real32_T CLK1_P2;                    // Expression: single(frequency)
                                          //  Referenced by: '<S26>/CLK1'

  real32_T SFunction_P6;               // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S34>/S-Function'

  real32_T SFunction_P12;              // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S34>/S-Function'

  real32_T Constant_Value;             // Computed Parameter: Constant_Value
                                          //  Referenced by: '<S1>/Constant'

  real32_T SFunction_P6_c;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S36>/S-Function'

  real32_T SFunction_P12_a;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S36>/S-Function'

  real32_T SFunction_P6_o;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S38>/S-Function'

  real32_T SFunction_P12_i;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S38>/S-Function'

  real32_T SFunction_P6_h;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S40>/S-Function'

  real32_T SFunction_P12_e;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S40>/S-Function'

  real32_T SFunction_P6_a;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S42>/S-Function'

  real32_T SFunction_P12_ew;           // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S42>/S-Function'

  real32_T SFunction_P6_n;             // Expression: single(CAN_TX_FREQ)
                                          //  Referenced by: '<S44>/S-Function'

  real32_T SFunction_P12_l;            // Expression: single(ETH_TX_FREQ)
                                          //  Referenced by: '<S44>/S-Function'

  real32_T Constant_Value_c;           // Computed Parameter: Constant_Value_c
                                          //  Referenced by: '<S3>/Constant'

  real32_T SFunction_P3_g;             // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S46>/S-Function'

  real32_T SFunction_P4;               // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S46>/S-Function'

  real32_T SFunction_P5;               // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S46>/S-Function'

  real32_T SFunction_P6_l;             // Expression: single(0)
                                          //  Referenced by: '<S46>/S-Function'

  real32_T SFunction_P7;               // Expression: single(0)
                                          //  Referenced by: '<S46>/S-Function'

  real32_T Gain1_Gain;                 // Computed Parameter: Gain1_Gain
                                          //  Referenced by: '<S1>/Gain1'

  real32_T Saturation_UpperSat;       // Computed Parameter: Saturation_UpperSat
                                         //  Referenced by: '<S21>/Saturation'

  real32_T Saturation_LowerSat;       // Computed Parameter: Saturation_LowerSat
                                         //  Referenced by: '<S21>/Saturation'

  real32_T CLK1_P2_l;                  // Expression: single(frequency)
                                          //  Referenced by: '<S21>/CLK1'

  real32_T SFunction_P3_n;             // Expression: single(INITIALVAL)
                                          //  Referenced by: '<S48>/S-Function'

  real32_T SFunction_P4_h;             // Expression: single(VAL_MIN)
                                          //  Referenced by: '<S48>/S-Function'

  real32_T SFunction_P5_f;             // Expression: single(VAL_MAX)
                                          //  Referenced by: '<S48>/S-Function'

  real32_T SFunction_P6_p;             // Expression: single(0)
                                          //  Referenced by: '<S48>/S-Function'

  real32_T SFunction_P7_g;             // Expression: single(0)
                                          //  Referenced by: '<S48>/S-Function'

  uint32_T SFunction_P7_a;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S34>/S-Function'

  uint32_T SFunction_P13;              // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S34>/S-Function'

  uint32_T SFunction_P7_a0;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S36>/S-Function'

  uint32_T SFunction_P13_k;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S36>/S-Function'

  uint32_T SFunction_P7_e;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S38>/S-Function'

  uint32_T SFunction_P13_n;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S38>/S-Function'

  uint32_T SFunction_P7_b;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S40>/S-Function'

  uint32_T SFunction_P13_o;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S40>/S-Function'

  uint32_T SFunction_P7_h;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S42>/S-Function'

  uint32_T SFunction_P13_c;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S42>/S-Function'

  uint32_T SFunction_P7_n;             // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S44>/S-Function'

  uint32_T SFunction_P13_m;            // Expression: uint32(ETH_PORT)
                                          //  Referenced by: '<S44>/S-Function'

  uint32_T SFunction_P10;              // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S46>/S-Function'

  uint32_T SFunction_P10_k;            // Expression: uint32(CAN_BAUDRATE)
                                          //  Referenced by: '<S48>/S-Function'

  int16_T PWM_P1;                      // Expression: int16(lane)
                                          //  Referenced by: '<S28>/PWM'

  int16_T PWM_P5;                      // Expression: int16(carrier)
                                          //  Referenced by: '<S28>/PWM'

  int16_T PWM_P6;                      // Expression: int16(rate)
                                          //  Referenced by: '<S28>/PWM'

  int16_T PWM_P7;                      // Expression: int16(outconf)
                                          //  Referenced by: '<S28>/PWM'

  int16_T PWM_P8;                      // Expression: int16(outmode)
                                          //  Referenced by: '<S28>/PWM'

  int16_T PWM_P9;                      // Expression: int16(nbBbx)
                                          //  Referenced by: '<S28>/PWM'

  int16_T PWM_P1_a;                    // Expression: int16(lane)
                                          //  Referenced by: '<S30>/PWM'

  int16_T PWM_P5_a;                    // Expression: int16(carrier)
                                          //  Referenced by: '<S30>/PWM'

  int16_T PWM_P6_o;                    // Expression: int16(rate)
                                          //  Referenced by: '<S30>/PWM'

  int16_T PWM_P7_e;                    // Expression: int16(outconf)
                                          //  Referenced by: '<S30>/PWM'

  int16_T PWM_P8_k;                    // Expression: int16(outmode)
                                          //  Referenced by: '<S30>/PWM'

  int16_T PWM_P9_j;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S30>/PWM'

  int16_T PWM_P1_k;                    // Expression: int16(lane)
                                          //  Referenced by: '<S32>/PWM'

  int16_T PWM_P5_o;                    // Expression: int16(carrier)
                                          //  Referenced by: '<S32>/PWM'

  int16_T PWM_P6_i;                    // Expression: int16(rate)
                                          //  Referenced by: '<S32>/PWM'

  int16_T PWM_P7_l;                    // Expression: int16(outconf)
                                          //  Referenced by: '<S32>/PWM'

  int16_T PWM_P8_o;                    // Expression: int16(outmode)
                                          //  Referenced by: '<S32>/PWM'

  int16_T PWM_P9_n;                    // Expression: int16(nbBbx)
                                          //  Referenced by: '<S32>/PWM'

  int16_T clk_id_Value;                // Computed Parameter: clk_id_Value
                                          //  Referenced by: '<S26>/clk_id'

  int16_T CLK1_P1;                     // Expression: int16(id)
                                          //  Referenced by: '<S26>/CLK1'

  int16_T SFunction_P2_l;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S34>/S-Function'

  int16_T SFunction_P3_e;              // Expression: int16(0)
                                          //  Referenced by: '<S34>/S-Function'

  int16_T SFunction_P2_b;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S36>/S-Function'

  int16_T SFunction_P3_b;              // Expression: int16(0)
                                          //  Referenced by: '<S36>/S-Function'

  int16_T SFunction_P2_p;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S38>/S-Function'

  int16_T SFunction_P3_k;              // Expression: int16(0)
                                          //  Referenced by: '<S38>/S-Function'

  int16_T SFunction_P2_i;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S40>/S-Function'

  int16_T SFunction_P3_h;              // Expression: int16(0)
                                          //  Referenced by: '<S40>/S-Function'

  int16_T SFunction_P2_n;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S42>/S-Function'

  int16_T SFunction_P3_hu;             // Expression: int16(0)
                                          //  Referenced by: '<S42>/S-Function'

  int16_T SFunction_P2_a;              // Expression: int16(DATATYPE)
                                          //  Referenced by: '<S44>/S-Function'

  int16_T SFunction_P3_j;              // Expression: int16(0)
                                          //  Referenced by: '<S44>/S-Function'

  int16_T clk_id_Value_a;              // Computed Parameter: clk_id_Value_a
                                          //  Referenced by: '<S21>/clk_id'

  int16_T SFunction_P2_lf;             // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S46>/S-Function'

  int16_T CLK1_P1_h;                   // Expression: int16(id)
                                          //  Referenced by: '<S21>/CLK1'

  int16_T SFunction_P2_m;              // Expression: int16(DATA_TYPE)
                                          //  Referenced by: '<S48>/S-Function'

  uint16_T SFunction_P1;               // Expression: uint16(interrupt_pstsclr)
                                          //  Referenced by: '<S24>/S-Function'

  uint16_T SFunction_P4_i;           // Expression: uint16(private_adc_delay_ns)
                                        //  Referenced by: '<S24>/S-Function'

  uint16_T SFunction_P1_j[6];          // Computed Parameter: SFunction_P1_j
                                          //  Referenced by: '<S34>/S-Function'

  uint16_T SFunction_P5_g;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S34>/S-Function'

  uint16_T SFunction_P8;               // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S34>/S-Function'

  uint16_T SFunction_P11;              // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S34>/S-Function'

  uint16_T SFunction_P14[5];           // Computed Parameter: SFunction_P14
                                          //  Referenced by: '<S34>/S-Function'

  uint16_T SFunction_P1_p[6];          // Computed Parameter: SFunction_P1_p
                                          //  Referenced by: '<S36>/S-Function'

  uint16_T SFunction_P5_i;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S36>/S-Function'

  uint16_T SFunction_P8_o;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S36>/S-Function'

  uint16_T SFunction_P11_f;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S36>/S-Function'

  uint16_T SFunction_P14_e[5];         // Computed Parameter: SFunction_P14_e
                                          //  Referenced by: '<S36>/S-Function'

  uint16_T SFunction_P1_n[6];          // Computed Parameter: SFunction_P1_n
                                          //  Referenced by: '<S38>/S-Function'

  uint16_T SFunction_P5_o;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S38>/S-Function'

  uint16_T SFunction_P8_b;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S38>/S-Function'

  uint16_T SFunction_P11_e;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S38>/S-Function'

  uint16_T SFunction_P14_i[5];         // Computed Parameter: SFunction_P14_i
                                          //  Referenced by: '<S38>/S-Function'

  uint16_T SFunction_P1_py[3];         // Computed Parameter: SFunction_P1_py
                                          //  Referenced by: '<S40>/S-Function'

  uint16_T SFunction_P5_b;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S40>/S-Function'

  uint16_T SFunction_P8_d;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S40>/S-Function'

  uint16_T SFunction_P11_l;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S40>/S-Function'

  uint16_T SFunction_P14_n[5];         // Computed Parameter: SFunction_P14_n
                                          //  Referenced by: '<S40>/S-Function'

  uint16_T SFunction_P1_i[3];          // Computed Parameter: SFunction_P1_i
                                          //  Referenced by: '<S42>/S-Function'

  uint16_T SFunction_P5_fo;            // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S42>/S-Function'

  uint16_T SFunction_P8_h;             // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S42>/S-Function'

  uint16_T SFunction_P11_d;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S42>/S-Function'

  uint16_T SFunction_P14_m[5];         // Computed Parameter: SFunction_P14_m
                                          //  Referenced by: '<S42>/S-Function'

  uint16_T SFunction_P1_jd[3];         // Computed Parameter: SFunction_P1_jd
                                          //  Referenced by: '<S44>/S-Function'

  uint16_T SFunction_P5_e;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S44>/S-Function'

  uint16_T SFunction_P8_dy;            // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S44>/S-Function'

  uint16_T SFunction_P11_a;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S44>/S-Function'

  uint16_T SFunction_P14_h[5];         // Computed Parameter: SFunction_P14_h
                                          //  Referenced by: '<S44>/S-Function'

  uint16_T SFunction_P1_jl;            // Computed Parameter: SFunction_P1_jl
                                          //  Referenced by: '<S46>/S-Function'

  uint16_T SFunction_P9;               // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S46>/S-Function'

  uint16_T SFunction_P11_d4;           // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S46>/S-Function'

  uint16_T SFunction_P14_j;            // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S46>/S-Function'

  uint16_T SFunction_P15;              // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S46>/S-Function'

  uint16_T SFunction_P1_m[12];         // Computed Parameter: SFunction_P1_m
                                          //  Referenced by: '<S48>/S-Function'

  uint16_T SFunction_P9_l;             // Expression: uint16(CAN_MB_ID)
                                          //  Referenced by: '<S48>/S-Function'

  uint16_T SFunction_P11_at;           // Expression: uint16(CAN_ADDRESS)
                                          //  Referenced by: '<S48>/S-Function'

  uint16_T SFunction_P14_ew;           // Expression: uint16(ETH_MB_ID)
                                          //  Referenced by: '<S48>/S-Function'

  uint16_T SFunction_P15_a;            // Expression: uint16(ETH_PORT)
                                          //  Referenced by: '<S48>/S-Function'

  boolean_T PWM_P10;                   // Expression: boolean(dutyrealtime)
                                          //  Referenced by: '<S28>/PWM'

  boolean_T PWM_P11;                   // Expression: boolean(phaserealtime)
                                          //  Referenced by: '<S28>/PWM'

  boolean_T PWM_P12;                   // Expression: boolean(activaterealtime)
                                          //  Referenced by: '<S28>/PWM'

  boolean_T PWM_P10_o;                 // Expression: boolean(dutyrealtime)
                                          //  Referenced by: '<S30>/PWM'

  boolean_T PWM_P11_c;                 // Expression: boolean(phaserealtime)
                                          //  Referenced by: '<S30>/PWM'

  boolean_T PWM_P12_o;                 // Expression: boolean(activaterealtime)
                                          //  Referenced by: '<S30>/PWM'

  boolean_T PWM_P10_b;                 // Expression: boolean(dutyrealtime)
                                          //  Referenced by: '<S32>/PWM'

  boolean_T PWM_P11_j;                 // Expression: boolean(phaserealtime)
                                          //  Referenced by: '<S32>/PWM'

  boolean_T PWM_P12_j;                 // Expression: boolean(activaterealtime)
                                          //  Referenced by: '<S32>/PWM'

  boolean_T CLK1_P3;                   // Expression: boolean(var_freq)
                                          //  Referenced by: '<S26>/CLK1'

  boolean_T SFunction_P4_k;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S34>/S-Function'

  boolean_T SFunction_P9_c;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S34>/S-Function'

  boolean_T SFunction_P10_p;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S34>/S-Function'

  boolean_T SFunction_P15_g;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S34>/S-Function'

  boolean_T SFunction_P4_p;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S36>/S-Function'

  boolean_T SFunction_P9_i;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S36>/S-Function'

  boolean_T SFunction_P10_i;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S36>/S-Function'

  boolean_T SFunction_P15_j;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S36>/S-Function'

  boolean_T SFunction_P4_j;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S38>/S-Function'

  boolean_T SFunction_P9_b;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S38>/S-Function'

  boolean_T SFunction_P10_c;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S38>/S-Function'

  boolean_T SFunction_P15_jk;          // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S38>/S-Function'

  boolean_T SFunction_P4_n;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S40>/S-Function'

  boolean_T SFunction_P9_h;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S40>/S-Function'

  boolean_T SFunction_P10_f;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S40>/S-Function'

  boolean_T SFunction_P15_gg;          // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S40>/S-Function'

  boolean_T SFunction_P4_l;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S42>/S-Function'

  boolean_T SFunction_P9_cz;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S42>/S-Function'

  boolean_T SFunction_P10_a;           // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S42>/S-Function'

  boolean_T SFunction_P15_p;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S42>/S-Function'

  boolean_T SFunction_P4_ku;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S44>/S-Function'

  boolean_T SFunction_P9_o;            // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S44>/S-Function'

  boolean_T SFunction_P10_c3;          // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S44>/S-Function'

  boolean_T SFunction_P15_l;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S44>/S-Function'

  boolean_T SFunction_P8_j;            // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S46>/S-Function'

  boolean_T SFunction_P12_p;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S46>/S-Function'

  boolean_T SFunction_P13_nd;          // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S46>/S-Function'

  boolean_T SFunction_P16;             // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S46>/S-Function'

  boolean_T CLK1_P3_i;                 // Expression: boolean(var_freq)
                                          //  Referenced by: '<S21>/CLK1'

  boolean_T SFunction_P8_du;           // Expression: boolean(CAN_ENABLED)
                                          //  Referenced by: '<S48>/S-Function'

  boolean_T SFunction_P12_c;           // Expression: boolean(CAN_BIG_ENDIAN)
                                          //  Referenced by: '<S48>/S-Function'

  boolean_T SFunction_P13_od;          // Expression: boolean(ETH_ENABLED)
                                          //  Referenced by: '<S48>/S-Function'

  boolean_T SFunction_P16_f;           // Expression: boolean(ETH_BIG_ENDIAN)
                                          //  Referenced by: '<S48>/S-Function'

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
//  Block '<S1>/Modulation and duty cycles' : Unused code path elimination
//  Block '<S1>/Reference phase voltage' : Unused code path elimination
//  Block '<S1>/Scope' : Unused code path elimination
//  Block '<S1>/Scope1' : Unused code path elimination
//  Block '<S1>/Scope2' : Unused code path elimination
//  Block '<S4>/Data Type Conversion1' : Eliminate redundant data type conversion
//  Block '<S7>/Data Type Conversion3' : Eliminate redundant data type conversion
//  Block '<S8>/Data Type Conversion3' : Eliminate redundant data type conversion
//  Block '<S9>/Data Type Conversion3' : Eliminate redundant data type conversion


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
//  '<S3>'   : 'EJ2311_PWM/Closed_loop_control/Angle'
//  '<S4>'   : 'EJ2311_PWM/Closed_loop_control/CLK'
//  '<S5>'   : 'EJ2311_PWM/Closed_loop_control/Configuration'
//  '<S6>'   : 'EJ2311_PWM/Closed_loop_control/MATLAB Function'
//  '<S7>'   : 'EJ2311_PWM/Closed_loop_control/PWM_CB'
//  '<S8>'   : 'EJ2311_PWM/Closed_loop_control/PWM_CB1'
//  '<S9>'   : 'EJ2311_PWM/Closed_loop_control/PWM_CB2'
//  '<S10>'  : 'EJ2311_PWM/Closed_loop_control/Probe3'
//  '<S11>'  : 'EJ2311_PWM/Closed_loop_control/Probe4'
//  '<S12>'  : 'EJ2311_PWM/Closed_loop_control/Probe5'
//  '<S13>'  : 'EJ2311_PWM/Closed_loop_control/Probe7'
//  '<S14>'  : 'EJ2311_PWM/Closed_loop_control/Probe8'
//  '<S15>'  : 'EJ2311_PWM/Closed_loop_control/Probe9'
//  '<S16>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter1'
//  '<S17>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter3'
//  '<S18>'  : 'EJ2311_PWM/Closed_loop_control/Angle/If Action Subsystem'
//  '<S19>'  : 'EJ2311_PWM/Closed_loop_control/Angle/If Action Subsystem1'
//  '<S20>'  : 'EJ2311_PWM/Closed_loop_control/CLK/sub'
//  '<S21>'  : 'EJ2311_PWM/Closed_loop_control/CLK/sub/generation'
//  '<S22>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/Sampling clock'
//  '<S23>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/clk0'
//  '<S24>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/Sampling clock/generation'
//  '<S25>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/clk0/sub'
//  '<S26>'  : 'EJ2311_PWM/Closed_loop_control/Configuration/clk0/sub/generation'
//  '<S27>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB/sub'
//  '<S28>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB/sub/generation'
//  '<S29>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB1/sub'
//  '<S30>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB1/sub/generation'
//  '<S31>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB2/sub'
//  '<S32>'  : 'EJ2311_PWM/Closed_loop_control/PWM_CB2/sub/generation'
//  '<S33>'  : 'EJ2311_PWM/Closed_loop_control/Probe3/sub'
//  '<S34>'  : 'EJ2311_PWM/Closed_loop_control/Probe3/sub/generation'
//  '<S35>'  : 'EJ2311_PWM/Closed_loop_control/Probe4/sub'
//  '<S36>'  : 'EJ2311_PWM/Closed_loop_control/Probe4/sub/generation'
//  '<S37>'  : 'EJ2311_PWM/Closed_loop_control/Probe5/sub'
//  '<S38>'  : 'EJ2311_PWM/Closed_loop_control/Probe5/sub/generation'
//  '<S39>'  : 'EJ2311_PWM/Closed_loop_control/Probe7/sub'
//  '<S40>'  : 'EJ2311_PWM/Closed_loop_control/Probe7/sub/generation'
//  '<S41>'  : 'EJ2311_PWM/Closed_loop_control/Probe8/sub'
//  '<S42>'  : 'EJ2311_PWM/Closed_loop_control/Probe8/sub/generation'
//  '<S43>'  : 'EJ2311_PWM/Closed_loop_control/Probe9/sub'
//  '<S44>'  : 'EJ2311_PWM/Closed_loop_control/Probe9/sub/generation'
//  '<S45>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter1/sub'
//  '<S46>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter1/sub/generation'
//  '<S47>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter3/sub'
//  '<S48>'  : 'EJ2311_PWM/Closed_loop_control/Tunable parameter3/sub/generation'

#endif                                 // RTW_HEADER_EJ2311_PWM_h_

//
// End of automatically generated code
// Copyright imperix ltd. Switzerland 2021
// [EOF]
//

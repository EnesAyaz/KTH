//
// Academic License - for use in teaching, academic research, and meeting
// course requirements at degree granting institutions only.  Not for
// government, commercial, or other organizational use.
//
// File: EJ2311_PWM_data.cpp
//
// Code generated for Simulink model 'EJ2311_PWM'.
// To be implemented on the B-Box RCP or the B-Board PRO.
//
// Model version                  : 16.7
// Simulink Coder version         : 23.2 (R2023b) 01-Aug-2023
// C/C++ source code generated on : Thu Feb 13 14:54:27 2025
//
#include "EJ2311_PWM.h"

// Block parameters (default storage)
P_EJ2311_PWM_T EJ2311_PWM_P = {
  // Expression: 0.2
  //  Referenced by: '<S1>/Constant2'

  0.2,

  // Expression: 0.0
  //  Referenced by: '<S3>/Delay'

  0.0,

  // Expression: 200/2
  //  Referenced by: '<S1>/Vdc//2'

  100.0,

  // Expression: 0.5
  //  Referenced by: '<S1>/Gain'

  0.5,

  // Expression: 0.5
  //  Referenced by: '<S1>/Constant1'

  0.5,

  // Computed Parameter: WeightedSampleTime_WtEt
  //  Referenced by: '<S3>/Weighted Sample Time'

  0.015707963267948967,

  // Expression: 0
  //  Referenced by: '<S3>/Data Store Memory'

  0.0,

  // Expression: 1
  //  Referenced by: '<S1>/Constant3'

  1.0,

  // Expression: 0
  //  Referenced by: '<S1>/Zero Phase Shift'

  0.0,

  // Expression: 0.5
  //  Referenced by: '<S1>/Switch1'

  0.5,

  // Expression: 0.5
  //  Referenced by: '<S1>/Switch2'

  0.5,

  // Expression: 0.5
  //  Referenced by: '<S1>/Switch3'

  0.5,

  // Expression: single(deadtime)
  //  Referenced by: '<S28>/PWM'

  1.5E-7F,

  // Expression: single(duty)
  //  Referenced by: '<S28>/PWM'

  0.0F,

  // Expression: single(phase)
  //  Referenced by: '<S28>/PWM'

  0.0F,

  // Expression: single(deadtime)
  //  Referenced by: '<S30>/PWM'

  1.5E-7F,

  // Expression: single(duty)
  //  Referenced by: '<S30>/PWM'

  0.0F,

  // Expression: single(phase)
  //  Referenced by: '<S30>/PWM'

  0.0F,

  // Expression: single(deadtime)
  //  Referenced by: '<S32>/PWM'

  1.5E-7F,

  // Expression: single(duty)
  //  Referenced by: '<S32>/PWM'

  0.0F,

  // Expression: single(phase)
  //  Referenced by: '<S32>/PWM'

  0.0F,

  // Expression: single(phase_vector)
  //  Referenced by: '<S24>/S-Function'

  0.5F,

  // Expression: single(interrupt_phase)
  //  Referenced by: '<S24>/S-Function'

  0.5F,

  // Expression: single(frequency)
  //  Referenced by: '<S26>/CLK1'

  20000.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S34>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S34>/S-Function'

  10.0F,

  // Computed Parameter: Constant_Value
  //  Referenced by: '<S1>/Constant'

  2.09439516F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S36>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S36>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S38>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S38>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S40>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S40>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S42>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S42>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S44>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S44>/S-Function'

  10.0F,

  // Computed Parameter: Constant_Value_c
  //  Referenced by: '<S3>/Constant'

  6.28318548F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S46>/S-Function'

  9.0F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S46>/S-Function'

  3.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S46>/S-Function'

  91.0F,

  // Expression: single(0)
  //  Referenced by: '<S46>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S46>/S-Function'

  0.0F,

  // Computed Parameter: Gain1_Gain
  //  Referenced by: '<S1>/Gain1'

  50.0F,

  // Computed Parameter: Saturation_UpperSat
  //  Referenced by: '<S21>/Saturation'

  2000.0F,

  // Computed Parameter: Saturation_LowerSat
  //  Referenced by: '<S21>/Saturation'

  350.0F,

  // Expression: single(frequency)
  //  Referenced by: '<S21>/CLK1'

  1950.0F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S48>/S-Function'

  1.0F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S48>/S-Function'

  0.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S48>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S48>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S48>/S-Function'

  0.0F,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S34>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S34>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S36>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S36>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S38>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S38>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S40>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S40>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S42>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S42>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S44>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S44>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S46>/S-Function'

  1000000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S48>/S-Function'

  1000000U,

  // Expression: int16(lane)
  //  Referenced by: '<S28>/PWM'

  0,

  // Expression: int16(carrier)
  //  Referenced by: '<S28>/PWM'

  0,

  // Expression: int16(rate)
  //  Referenced by: '<S28>/PWM'

  1,

  // Expression: int16(outconf)
  //  Referenced by: '<S28>/PWM'

  2,

  // Expression: int16(outmode)
  //  Referenced by: '<S28>/PWM'

  0,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S28>/PWM'

  0,

  // Expression: int16(lane)
  //  Referenced by: '<S30>/PWM'

  2,

  // Expression: int16(carrier)
  //  Referenced by: '<S30>/PWM'

  0,

  // Expression: int16(rate)
  //  Referenced by: '<S30>/PWM'

  1,

  // Expression: int16(outconf)
  //  Referenced by: '<S30>/PWM'

  2,

  // Expression: int16(outmode)
  //  Referenced by: '<S30>/PWM'

  0,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S30>/PWM'

  0,

  // Expression: int16(lane)
  //  Referenced by: '<S32>/PWM'

  4,

  // Expression: int16(carrier)
  //  Referenced by: '<S32>/PWM'

  0,

  // Expression: int16(rate)
  //  Referenced by: '<S32>/PWM'

  1,

  // Expression: int16(outconf)
  //  Referenced by: '<S32>/PWM'

  2,

  // Expression: int16(outmode)
  //  Referenced by: '<S32>/PWM'

  0,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S32>/PWM'

  0,

  // Computed Parameter: clk_id_Value
  //  Referenced by: '<S26>/clk_id'

  0,

  // Expression: int16(id)
  //  Referenced by: '<S26>/CLK1'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S34>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S34>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S36>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S36>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S38>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S38>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S40>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S40>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S42>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S42>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S44>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S44>/S-Function'

  0,

  // Computed Parameter: clk_id_Value_a
  //  Referenced by: '<S21>/clk_id'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S46>/S-Function'

  1,

  // Expression: int16(id)
  //  Referenced by: '<S21>/CLK1'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S48>/S-Function'

  1,

  // Expression: uint16(interrupt_pstsclr)
  //  Referenced by: '<S24>/S-Function'

  0U,

  // Expression: uint16(private_adc_delay_ns)
  //  Referenced by: '<S24>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_j
  //  Referenced by: '<S34>/S-Function'

  { 86U, 97U, 95U, 114U, 101U, 102U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S34>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S34>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S34>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14
  //  Referenced by: '<S34>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_p
  //  Referenced by: '<S36>/S-Function'

  { 86U, 98U, 95U, 114U, 101U, 102U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S36>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S36>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S36>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_e
  //  Referenced by: '<S36>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_n
  //  Referenced by: '<S38>/S-Function'

  { 86U, 99U, 95U, 114U, 101U, 102U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S38>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S38>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S38>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_i
  //  Referenced by: '<S38>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_py
  //  Referenced by: '<S40>/S-Function'

  { 100U, 95U, 97U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S40>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S40>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S40>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_n
  //  Referenced by: '<S40>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_i
  //  Referenced by: '<S42>/S-Function'

  { 100U, 95U, 98U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S42>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S42>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S42>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_m
  //  Referenced by: '<S42>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_jd
  //  Referenced by: '<S44>/S-Function'

  { 100U, 95U, 99U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S44>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S44>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S44>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_h
  //  Referenced by: '<S44>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_jl
  //  Referenced by: '<S46>/S-Function'

  112U,

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S46>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S46>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S46>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S46>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_m
  //  Referenced by: '<S48>/S-Function'

  { 97U, 99U, 116U, 105U, 118U, 97U, 116U, 101U, 95U, 112U, 119U, 109U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S48>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S48>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S48>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S48>/S-Function'

  2000U,

  // Expression: boolean(dutyrealtime)
  //  Referenced by: '<S28>/PWM'

  true,

  // Expression: boolean(phaserealtime)
  //  Referenced by: '<S28>/PWM'

  true,

  // Expression: boolean(activaterealtime)
  //  Referenced by: '<S28>/PWM'

  true,

  // Expression: boolean(dutyrealtime)
  //  Referenced by: '<S30>/PWM'

  true,

  // Expression: boolean(phaserealtime)
  //  Referenced by: '<S30>/PWM'

  true,

  // Expression: boolean(activaterealtime)
  //  Referenced by: '<S30>/PWM'

  true,

  // Expression: boolean(dutyrealtime)
  //  Referenced by: '<S32>/PWM'

  true,

  // Expression: boolean(phaserealtime)
  //  Referenced by: '<S32>/PWM'

  true,

  // Expression: boolean(activaterealtime)
  //  Referenced by: '<S32>/PWM'

  true,

  // Expression: boolean(var_freq)
  //  Referenced by: '<S26>/CLK1'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S34>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S34>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S34>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S34>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S36>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S36>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S36>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S36>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S38>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S38>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S38>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S38>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S40>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S40>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S40>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S40>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S42>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S42>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S42>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S42>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S44>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S44>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S44>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S44>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S46>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S46>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S46>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S46>/S-Function'

  false,

  // Expression: boolean(var_freq)
  //  Referenced by: '<S21>/CLK1'

  true,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S48>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S48>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S48>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S48>/S-Function'

  false
};

//
// End of automatically generated code
// Copyright imperix ltd. Switzerland 2021
// [EOF]
//

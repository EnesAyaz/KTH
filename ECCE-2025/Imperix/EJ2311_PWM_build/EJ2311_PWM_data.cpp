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
// Model version                  : 16.3
// Simulink Coder version         : 23.2 (R2023b) 01-Aug-2023
// C/C++ source code generated on : Wed Feb 12 15:00:19 2025
//
#include "EJ2311_PWM.h"

// Block parameters (default storage)
P_EJ2311_PWM_T EJ2311_PWM_P = {
  // Expression: 0.0
  //  Referenced by: '<S7>/Delay'

  0.0,

  // Computed Parameter: WeightedSampleTime_WtEt
  //  Referenced by: '<S7>/Weighted Sample Time'

  0.015707963267948967,

  // Expression: 0
  //  Referenced by: '<S7>/Data Store Memory'

  0.0,

  // Expression: PHASE
  //  Referenced by: '<S10>/phase'

  0.0,

  // Expression: PHASE
  //  Referenced by: '<S11>/phase'

  0.0,

  // Expression: PHASE
  //  Referenced by: '<S12>/phase'

  0.0,

  // Expression: single(deadtime)
  //  Referenced by: '<S45>/PWM'

  1.5E-7F,

  // Expression: single(duty)
  //  Referenced by: '<S45>/PWM'

  0.0F,

  // Expression: single(phase)
  //  Referenced by: '<S45>/PWM'

  0.0F,

  // Expression: single(deadtime)
  //  Referenced by: '<S47>/PWM'

  1.5E-7F,

  // Expression: single(duty)
  //  Referenced by: '<S47>/PWM'

  0.0F,

  // Expression: single(phase)
  //  Referenced by: '<S47>/PWM'

  0.0F,

  // Expression: single(deadtime)
  //  Referenced by: '<S49>/PWM'

  1.5E-7F,

  // Expression: single(duty)
  //  Referenced by: '<S49>/PWM'

  0.0F,

  // Expression: single(phase)
  //  Referenced by: '<S49>/PWM'

  0.0F,

  // Computed Parameter: Gain2_Gain
  //  Referenced by: '<S1>/Gain2'

  3.0F,

  // Computed Parameter: Gain3_Gain
  //  Referenced by: '<S1>/Gain3'

  0.166666672F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S51>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S51>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S53>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S53>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S55>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S55>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S63>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S63>/S-Function'

  10.0F,

  // Expression: single(gain)
  //  Referenced by: '<S28>/ADC'

  0.0015259F,

  // Expression: single(offset)
  //  Referenced by: '<S28>/ADC'

  -0.045F,

  // Expression: single(gain)
  //  Referenced by: '<S30>/ADC'

  0.0015259F,

  // Expression: single(offset)
  //  Referenced by: '<S30>/ADC'

  -0.04F,

  // Expression: single(gain)
  //  Referenced by: '<S32>/ADC'

  0.0015259F,

  // Expression: single(offset)
  //  Referenced by: '<S32>/ADC'

  -0.052F,

  // Expression: single(gain)
  //  Referenced by: '<S34>/ADC'

  0.030579F,

  // Expression: single(offset)
  //  Referenced by: '<S34>/ADC'

  -0.35F,

  // Expression: single(phase_vector)
  //  Referenced by: '<S41>/S-Function'

  0.5F,

  // Expression: single(interrupt_phase)
  //  Referenced by: '<S41>/S-Function'

  0.5F,

  // Expression: single(frequency)
  //  Referenced by: '<S43>/CLK1'

  20000.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S57>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S57>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S59>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S59>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S61>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S61>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S65>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S65>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S67>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S67>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S69>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S69>/S-Function'

  10.0F,

  // Computed Parameter: Constant_Value
  //  Referenced by: '<S7>/Constant'

  6.28318548F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S73>/S-Function'

  9.0F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S73>/S-Function'

  3.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S73>/S-Function'

  91.0F,

  // Expression: single(0)
  //  Referenced by: '<S73>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S73>/S-Function'

  0.0F,

  // Computed Parameter: Gain1_Gain
  //  Referenced by: '<S1>/Gain1'

  50.0F,

  // Computed Parameter: Saturation_UpperSat
  //  Referenced by: '<S38>/Saturation'

  2000.0F,

  // Computed Parameter: Saturation_LowerSat
  //  Referenced by: '<S38>/Saturation'

  350.0F,

  // Expression: single(frequency)
  //  Referenced by: '<S38>/CLK1'

  1950.0F,

  // Computed Parameter: Constant_Value_j
  //  Referenced by: '<S1>/Constant'

  2.09439516F,

  // Computed Parameter: Constant1_Value
  //  Referenced by: '<S1>/Constant1'

  0.5F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S71>/S-Function'

  0.8F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S71>/S-Function'

  0.1F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S71>/S-Function'

  2.0F,

  // Expression: single(0)
  //  Referenced by: '<S71>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S71>/S-Function'

  0.0F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S75>/S-Function'

  0.0F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S75>/S-Function'

  0.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S75>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S75>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S75>/S-Function'

  0.0F,

  // Computed Parameter: Switch_Threshold
  //  Referenced by: '<S1>/Switch'

  0.5F,

  // Computed Parameter: Gain_Gain
  //  Referenced by: '<S1>/Gain'

  0.5F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S77>/S-Function'

  0.0F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S77>/S-Function'

  0.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S77>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S77>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S77>/S-Function'

  0.0F,

  // Computed Parameter: Vdc2_Gain
  //  Referenced by: '<S1>/Vdc//2'

  100.0F,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S51>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S51>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S53>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S53>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S55>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S55>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S63>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S63>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S57>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S57>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S59>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S59>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S61>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S61>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S65>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S65>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S67>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S67>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S69>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S69>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S73>/S-Function'

  1000000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S71>/S-Function'

  1000000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S75>/S-Function'

  1000000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S77>/S-Function'

  1000000U,

  // Expression: int16(lane)
  //  Referenced by: '<S45>/PWM'

  0,

  // Expression: int16(carrier)
  //  Referenced by: '<S45>/PWM'

  0,

  // Expression: int16(rate)
  //  Referenced by: '<S45>/PWM'

  1,

  // Expression: int16(outconf)
  //  Referenced by: '<S45>/PWM'

  2,

  // Expression: int16(outmode)
  //  Referenced by: '<S45>/PWM'

  0,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S45>/PWM'

  0,

  // Expression: int16(lane)
  //  Referenced by: '<S47>/PWM'

  2,

  // Expression: int16(carrier)
  //  Referenced by: '<S47>/PWM'

  0,

  // Expression: int16(rate)
  //  Referenced by: '<S47>/PWM'

  1,

  // Expression: int16(outconf)
  //  Referenced by: '<S47>/PWM'

  2,

  // Expression: int16(outmode)
  //  Referenced by: '<S47>/PWM'

  0,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S47>/PWM'

  0,

  // Expression: int16(lane)
  //  Referenced by: '<S49>/PWM'

  4,

  // Expression: int16(carrier)
  //  Referenced by: '<S49>/PWM'

  0,

  // Expression: int16(rate)
  //  Referenced by: '<S49>/PWM'

  1,

  // Expression: int16(outconf)
  //  Referenced by: '<S49>/PWM'

  2,

  // Expression: int16(outmode)
  //  Referenced by: '<S49>/PWM'

  0,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S49>/PWM'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S51>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S51>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S53>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S53>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S55>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S55>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S63>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S63>/S-Function'

  0,

  // Expression: int16(channel)
  //  Referenced by: '<S28>/ADC'

  0,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S28>/ADC'

  0,

  // Expression: int16(outputwidth)
  //  Referenced by: '<S28>/ADC'

  1,

  // Expression: int16(channel)
  //  Referenced by: '<S30>/ADC'

  1,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S30>/ADC'

  0,

  // Expression: int16(outputwidth)
  //  Referenced by: '<S30>/ADC'

  1,

  // Expression: int16(channel)
  //  Referenced by: '<S32>/ADC'

  2,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S32>/ADC'

  0,

  // Expression: int16(outputwidth)
  //  Referenced by: '<S32>/ADC'

  1,

  // Expression: int16(channel)
  //  Referenced by: '<S34>/ADC'

  3,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S34>/ADC'

  0,

  // Expression: int16(outputwidth)
  //  Referenced by: '<S34>/ADC'

  1,

  // Computed Parameter: clk_id_Value
  //  Referenced by: '<S43>/clk_id'

  0,

  // Expression: int16(id)
  //  Referenced by: '<S43>/CLK1'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S57>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S57>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S59>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S59>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S61>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S61>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S65>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S65>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S67>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S67>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S69>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S69>/S-Function'

  0,

  // Computed Parameter: clk_id_Value_a
  //  Referenced by: '<S38>/clk_id'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S73>/S-Function'

  1,

  // Expression: int16(id)
  //  Referenced by: '<S38>/CLK1'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S71>/S-Function'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S75>/S-Function'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S77>/S-Function'

  1,

  // Computed Parameter: SFunction_P1
  //  Referenced by: '<S51>/S-Function'

  { 73U, 97U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S51>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S51>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S51>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14
  //  Referenced by: '<S51>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_k
  //  Referenced by: '<S53>/S-Function'

  { 73U, 98U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S53>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S53>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S53>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_m
  //  Referenced by: '<S53>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_l
  //  Referenced by: '<S55>/S-Function'

  { 73U, 99U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S55>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S55>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S55>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_o
  //  Referenced by: '<S55>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_lh
  //  Referenced by: '<S63>/S-Function'

  { 86U, 100U, 99U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S63>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S63>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S63>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_l
  //  Referenced by: '<S63>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Expression: uint16(interrupt_pstsclr)
  //  Referenced by: '<S41>/S-Function'

  0U,

  // Expression: uint16(private_adc_delay_ns)
  //  Referenced by: '<S41>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_j
  //  Referenced by: '<S57>/S-Function'

  { 86U, 97U, 95U, 114U, 101U, 102U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S57>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S57>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S57>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_a
  //  Referenced by: '<S57>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_p
  //  Referenced by: '<S59>/S-Function'

  { 86U, 98U, 95U, 114U, 101U, 102U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S59>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S59>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S59>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_e
  //  Referenced by: '<S59>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_n
  //  Referenced by: '<S61>/S-Function'

  { 86U, 99U, 95U, 114U, 101U, 102U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S61>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S61>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S61>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_i
  //  Referenced by: '<S61>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_py
  //  Referenced by: '<S65>/S-Function'

  { 100U, 95U, 97U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S65>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S65>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S65>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_n
  //  Referenced by: '<S65>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_i
  //  Referenced by: '<S67>/S-Function'

  { 100U, 95U, 98U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S67>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S67>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S67>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_mv
  //  Referenced by: '<S67>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_jd
  //  Referenced by: '<S69>/S-Function'

  { 100U, 95U, 99U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S69>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S69>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S69>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_h
  //  Referenced by: '<S69>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_jl
  //  Referenced by: '<S73>/S-Function'

  112U,

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S73>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S73>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S73>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S73>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_fq
  //  Referenced by: '<S71>/S-Function'

  77U,

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S71>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S71>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S71>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S71>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_g
  //  Referenced by: '<S75>/S-Function'

  { 116U, 104U, 105U, 114U, 100U, 95U, 104U, 97U, 114U, 109U, 111U, 110U, 105U,
    99U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S75>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S75>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S75>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S75>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_m
  //  Referenced by: '<S77>/S-Function'

  { 97U, 99U, 116U, 105U, 118U, 97U, 116U, 101U, 95U, 112U, 119U, 109U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S77>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S77>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S77>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S77>/S-Function'

  2000U,

  // Expression: boolean(dutyrealtime)
  //  Referenced by: '<S45>/PWM'

  true,

  // Expression: boolean(phaserealtime)
  //  Referenced by: '<S45>/PWM'

  false,

  // Expression: boolean(activaterealtime)
  //  Referenced by: '<S45>/PWM'

  true,

  // Expression: boolean(dutyrealtime)
  //  Referenced by: '<S47>/PWM'

  true,

  // Expression: boolean(phaserealtime)
  //  Referenced by: '<S47>/PWM'

  false,

  // Expression: boolean(activaterealtime)
  //  Referenced by: '<S47>/PWM'

  true,

  // Expression: boolean(dutyrealtime)
  //  Referenced by: '<S49>/PWM'

  true,

  // Expression: boolean(phaserealtime)
  //  Referenced by: '<S49>/PWM'

  false,

  // Expression: boolean(activaterealtime)
  //  Referenced by: '<S49>/PWM'

  true,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S51>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S51>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S51>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S51>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S53>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S53>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S53>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S53>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S55>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S55>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S55>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S55>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S63>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S63>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S63>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S63>/S-Function'

  false,

  // Expression: boolean(usehist)
  //  Referenced by: '<S28>/ADC'

  false,

  // Expression: boolean(usehist)
  //  Referenced by: '<S30>/ADC'

  false,

  // Expression: boolean(usehist)
  //  Referenced by: '<S32>/ADC'

  false,

  // Expression: boolean(usehist)
  //  Referenced by: '<S34>/ADC'

  false,

  // Expression: boolean(var_freq)
  //  Referenced by: '<S43>/CLK1'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S57>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S57>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S57>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S57>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S59>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S59>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S59>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S59>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S61>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S61>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S61>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S61>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S65>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S65>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S65>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S65>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S67>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S67>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S67>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S67>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S69>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S69>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S69>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S69>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S73>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S73>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S73>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S73>/S-Function'

  false,

  // Expression: boolean(var_freq)
  //  Referenced by: '<S38>/CLK1'

  true,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S71>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S71>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S71>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S71>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S75>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S75>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S75>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S75>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S77>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S77>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S77>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S77>/S-Function'

  false
};

//
// End of automatically generated code
// Copyright imperix ltd. Switzerland 2021
// [EOF]
//

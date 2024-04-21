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
// C/C++ source code generated on : Wed Feb 14 15:50:32 2024
//
#include "EJ2311_PWM.h"

// Block parameters (default storage)
P_EJ2311_PWM_T EJ2311_PWM_P = {
  // Expression: single(deadtime)
  //  Referenced by: '<S40>/PWM'

  1.5E-7F,

  // Expression: single(duty)
  //  Referenced by: '<S40>/PWM'

  0.0F,

  // Expression: single(phase)
  //  Referenced by: '<S40>/PWM'

  0.0F,

  // Expression: single(deadtime)
  //  Referenced by: '<S42>/PWM'

  1.5E-7F,

  // Expression: single(duty)
  //  Referenced by: '<S42>/PWM'

  0.0F,

  // Expression: single(phase)
  //  Referenced by: '<S42>/PWM'

  0.0F,

  // Expression: single(deadtime)
  //  Referenced by: '<S44>/PWM'

  1.5E-7F,

  // Expression: single(duty)
  //  Referenced by: '<S44>/PWM'

  0.0F,

  // Expression: single(phase)
  //  Referenced by: '<S44>/PWM'

  0.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S46>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S46>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S48>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S48>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S50>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S50>/S-Function'

  10.0F,

  // Expression: single(CAN_TX_FREQ)
  //  Referenced by: '<S52>/S-Function'

  10.0F,

  // Expression: single(ETH_TX_FREQ)
  //  Referenced by: '<S52>/S-Function'

  10.0F,

  // Expression: single(gain)
  //  Referenced by: '<S25>/ADC'

  0.0015259F,

  // Expression: single(offset)
  //  Referenced by: '<S25>/ADC'

  -0.045F,

  // Expression: single(gain)
  //  Referenced by: '<S27>/ADC'

  0.0015259F,

  // Expression: single(offset)
  //  Referenced by: '<S27>/ADC'

  -0.04F,

  // Expression: single(gain)
  //  Referenced by: '<S29>/ADC'

  0.0015259F,

  // Expression: single(offset)
  //  Referenced by: '<S29>/ADC'

  -0.052F,

  // Expression: single(gain)
  //  Referenced by: '<S31>/ADC'

  0.030579F,

  // Expression: single(offset)
  //  Referenced by: '<S31>/ADC'

  -0.35F,

  // Expression: single(phase_vector)
  //  Referenced by: '<S36>/S-Function'

  0.5F,

  // Expression: single(interrupt_phase)
  //  Referenced by: '<S36>/S-Function'

  0.5F,

  // Expression: single(frequency)
  //  Referenced by: '<S38>/CLK1'

  20000.0F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S54>/S-Function'

  500.0F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S54>/S-Function'

  3.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S54>/S-Function'

  91.0F,

  // Expression: single(0)
  //  Referenced by: '<S54>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S54>/S-Function'

  0.0F,

  // Computed Parameter: Saturation_UpperSat
  //  Referenced by: '<S33>/Saturation'

  2000.0F,

  // Computed Parameter: Saturation_LowerSat
  //  Referenced by: '<S33>/Saturation'

  350.0F,

  // Expression: single(frequency)
  //  Referenced by: '<S33>/CLK1'

  1950.0F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S56>/S-Function'

  0.5F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S56>/S-Function'

  0.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S56>/S-Function'

  1.0F,

  // Expression: single(0)
  //  Referenced by: '<S56>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S56>/S-Function'

  0.0F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S60>/S-Function'

  0.0F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S60>/S-Function'

  0.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S60>/S-Function'

  1.0F,

  // Expression: single(0)
  //  Referenced by: '<S60>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S60>/S-Function'

  0.0F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S58>/S-Function'

  0.0F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S58>/S-Function'

  0.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S58>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S58>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S58>/S-Function'

  0.0F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S66>/S-Function'

  0.25F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S66>/S-Function'

  0.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S66>/S-Function'

  1.0F,

  // Expression: single(0)
  //  Referenced by: '<S66>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S66>/S-Function'

  0.0F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S62>/S-Function'

  0.0F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S62>/S-Function'

  0.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S62>/S-Function'

  1.0F,

  // Expression: single(0)
  //  Referenced by: '<S62>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S62>/S-Function'

  0.0F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S68>/S-Function'

  0.25F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S68>/S-Function'

  0.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S68>/S-Function'

  1.0F,

  // Expression: single(0)
  //  Referenced by: '<S68>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S68>/S-Function'

  0.0F,

  // Expression: single(INITIALVAL)
  //  Referenced by: '<S64>/S-Function'

  0.0F,

  // Expression: single(VAL_MIN)
  //  Referenced by: '<S64>/S-Function'

  0.0F,

  // Expression: single(VAL_MAX)
  //  Referenced by: '<S64>/S-Function'

  1.0F,

  // Expression: single(0)
  //  Referenced by: '<S64>/S-Function'

  0.0F,

  // Expression: single(0)
  //  Referenced by: '<S64>/S-Function'

  0.0F,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S46>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S46>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S48>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S48>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S50>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S50>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S52>/S-Function'

  1000000U,

  // Expression: uint32(ETH_PORT)
  //  Referenced by: '<S52>/S-Function'

  2000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S54>/S-Function'

  1000000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S56>/S-Function'

  1000000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S60>/S-Function'

  1000000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S58>/S-Function'

  1000000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S66>/S-Function'

  1000000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S62>/S-Function'

  1000000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S68>/S-Function'

  1000000U,

  // Expression: uint32(CAN_BAUDRATE)
  //  Referenced by: '<S64>/S-Function'

  1000000U,

  // Expression: int16(lane)
  //  Referenced by: '<S40>/PWM'

  0,

  // Expression: int16(carrier)
  //  Referenced by: '<S40>/PWM'

  0,

  // Expression: int16(rate)
  //  Referenced by: '<S40>/PWM'

  1,

  // Expression: int16(outconf)
  //  Referenced by: '<S40>/PWM'

  2,

  // Expression: int16(outmode)
  //  Referenced by: '<S40>/PWM'

  0,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S40>/PWM'

  0,

  // Expression: int16(lane)
  //  Referenced by: '<S42>/PWM'

  2,

  // Expression: int16(carrier)
  //  Referenced by: '<S42>/PWM'

  0,

  // Expression: int16(rate)
  //  Referenced by: '<S42>/PWM'

  1,

  // Expression: int16(outconf)
  //  Referenced by: '<S42>/PWM'

  2,

  // Expression: int16(outmode)
  //  Referenced by: '<S42>/PWM'

  0,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S42>/PWM'

  0,

  // Expression: int16(lane)
  //  Referenced by: '<S44>/PWM'

  4,

  // Expression: int16(carrier)
  //  Referenced by: '<S44>/PWM'

  0,

  // Expression: int16(rate)
  //  Referenced by: '<S44>/PWM'

  1,

  // Expression: int16(outconf)
  //  Referenced by: '<S44>/PWM'

  2,

  // Expression: int16(outmode)
  //  Referenced by: '<S44>/PWM'

  0,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S44>/PWM'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S46>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S46>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S48>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S48>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S50>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S50>/S-Function'

  0,

  // Expression: int16(DATATYPE)
  //  Referenced by: '<S52>/S-Function'

  1,

  // Expression: int16(0)
  //  Referenced by: '<S52>/S-Function'

  0,

  // Expression: int16(channel)
  //  Referenced by: '<S25>/ADC'

  0,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S25>/ADC'

  0,

  // Expression: int16(outputwidth)
  //  Referenced by: '<S25>/ADC'

  1,

  // Expression: int16(channel)
  //  Referenced by: '<S27>/ADC'

  1,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S27>/ADC'

  0,

  // Expression: int16(outputwidth)
  //  Referenced by: '<S27>/ADC'

  1,

  // Expression: int16(channel)
  //  Referenced by: '<S29>/ADC'

  2,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S29>/ADC'

  0,

  // Expression: int16(outputwidth)
  //  Referenced by: '<S29>/ADC'

  1,

  // Expression: int16(channel)
  //  Referenced by: '<S31>/ADC'

  3,

  // Expression: int16(nbBbx)
  //  Referenced by: '<S31>/ADC'

  0,

  // Expression: int16(outputwidth)
  //  Referenced by: '<S31>/ADC'

  1,

  // Computed Parameter: clk_id_Value
  //  Referenced by: '<S38>/clk_id'

  0,

  // Expression: int16(id)
  //  Referenced by: '<S38>/CLK1'

  0,

  // Computed Parameter: clk_id_Value_a
  //  Referenced by: '<S33>/clk_id'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S54>/S-Function'

  1,

  // Expression: int16(id)
  //  Referenced by: '<S33>/CLK1'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S56>/S-Function'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S60>/S-Function'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S58>/S-Function'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S66>/S-Function'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S62>/S-Function'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S68>/S-Function'

  1,

  // Expression: int16(DATA_TYPE)
  //  Referenced by: '<S64>/S-Function'

  1,

  // Computed Parameter: SFunction_P1
  //  Referenced by: '<S46>/S-Function'

  { 73U, 97U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S46>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S46>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S46>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14
  //  Referenced by: '<S46>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_k
  //  Referenced by: '<S48>/S-Function'

  { 73U, 98U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S48>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S48>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S48>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_m
  //  Referenced by: '<S48>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_l
  //  Referenced by: '<S50>/S-Function'

  { 73U, 99U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S50>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S50>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S50>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_o
  //  Referenced by: '<S50>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Computed Parameter: SFunction_P1_lh
  //  Referenced by: '<S52>/S-Function'

  { 86U, 100U, 99U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S52>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S52>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S52>/S-Function'

  1U,

  // Computed Parameter: SFunction_P14_l
  //  Referenced by: '<S52>/S-Function'

  { 101U, 109U, 112U, 116U, 121U },

  // Expression: uint16(interrupt_pstsclr)
  //  Referenced by: '<S36>/S-Function'

  0U,

  // Expression: uint16(private_adc_delay_ns)
  //  Referenced by: '<S36>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_j
  //  Referenced by: '<S54>/S-Function'

  { 102U, 115U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S54>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S54>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S54>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S54>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_b
  //  Referenced by: '<S56>/S-Function'

  { 100U, 65U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S56>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S56>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S56>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S56>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_fu
  //  Referenced by: '<S60>/S-Function'

  { 112U, 104U, 65U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S60>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S60>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S60>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S60>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_m
  //  Referenced by: '<S58>/S-Function'

  { 97U, 99U, 116U, 105U, 118U, 97U, 116U, 101U, 95U, 112U, 119U, 109U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S58>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S58>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S58>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S58>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_bs
  //  Referenced by: '<S66>/S-Function'

  { 100U, 66U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S66>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S66>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S66>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S66>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_ly
  //  Referenced by: '<S62>/S-Function'

  { 112U, 104U, 66U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S62>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S62>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S62>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S62>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_kb
  //  Referenced by: '<S68>/S-Function'

  { 100U, 67U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S68>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S68>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S68>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S68>/S-Function'

  2000U,

  // Computed Parameter: SFunction_P1_lo
  //  Referenced by: '<S64>/S-Function'

  { 112U, 104U, 67U },

  // Expression: uint16(CAN_MB_ID)
  //  Referenced by: '<S64>/S-Function'

  0U,

  // Expression: uint16(CAN_ADDRESS)
  //  Referenced by: '<S64>/S-Function'

  0U,

  // Expression: uint16(ETH_MB_ID)
  //  Referenced by: '<S64>/S-Function'

  1U,

  // Expression: uint16(ETH_PORT)
  //  Referenced by: '<S64>/S-Function'

  2000U,

  // Expression: boolean(dutyrealtime)
  //  Referenced by: '<S40>/PWM'

  true,

  // Expression: boolean(phaserealtime)
  //  Referenced by: '<S40>/PWM'

  true,

  // Expression: boolean(activaterealtime)
  //  Referenced by: '<S40>/PWM'

  true,

  // Expression: boolean(dutyrealtime)
  //  Referenced by: '<S42>/PWM'

  true,

  // Expression: boolean(phaserealtime)
  //  Referenced by: '<S42>/PWM'

  true,

  // Expression: boolean(activaterealtime)
  //  Referenced by: '<S42>/PWM'

  true,

  // Expression: boolean(dutyrealtime)
  //  Referenced by: '<S44>/PWM'

  true,

  // Expression: boolean(phaserealtime)
  //  Referenced by: '<S44>/PWM'

  true,

  // Expression: boolean(activaterealtime)
  //  Referenced by: '<S44>/PWM'

  true,

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

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S50>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S50>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S50>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S50>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S52>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S52>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S52>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S52>/S-Function'

  false,

  // Expression: boolean(usehist)
  //  Referenced by: '<S25>/ADC'

  false,

  // Expression: boolean(usehist)
  //  Referenced by: '<S27>/ADC'

  false,

  // Expression: boolean(usehist)
  //  Referenced by: '<S29>/ADC'

  false,

  // Expression: boolean(usehist)
  //  Referenced by: '<S31>/ADC'

  false,

  // Expression: boolean(var_freq)
  //  Referenced by: '<S38>/CLK1'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S54>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S54>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S54>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S54>/S-Function'

  false,

  // Expression: boolean(var_freq)
  //  Referenced by: '<S33>/CLK1'

  true,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S56>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S56>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S56>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S56>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S60>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S60>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S60>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S60>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S58>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S58>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S58>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S58>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S66>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S66>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S66>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S66>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S62>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S62>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S62>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S62>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S68>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S68>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S68>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S68>/S-Function'

  false,

  // Expression: boolean(CAN_ENABLED)
  //  Referenced by: '<S64>/S-Function'

  false,

  // Expression: boolean(CAN_BIG_ENDIAN)
  //  Referenced by: '<S64>/S-Function'

  false,

  // Expression: boolean(ETH_ENABLED)
  //  Referenced by: '<S64>/S-Function'

  false,

  // Expression: boolean(ETH_BIG_ENDIAN)
  //  Referenced by: '<S64>/S-Function'

  false
};

//
// End of automatically generated code
// Copyright imperix ltd. Switzerland 2021
// [EOF]
//

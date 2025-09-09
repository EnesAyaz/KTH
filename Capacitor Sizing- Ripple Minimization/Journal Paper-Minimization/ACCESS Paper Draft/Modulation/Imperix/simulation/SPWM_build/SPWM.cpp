//
// Academic License - for use in teaching, academic research, and meeting
// course requirements at degree granting institutions only.  Not for
// government, commercial, or other organizational use.
//
// File: SPWM.cpp
//
// Code generated for Simulink model 'SPWM'.
// To be implemented on the B-Box RCP or the B-Board PRO.
//
// Model version                  : 16.7
// Simulink Coder version         : 23.2 (R2023b) 01-Aug-2023
// C/C++ source code generated on : Tue Aug 12 17:33:52 2025
//
#include "SPWM.h"
#include <math.h>
#include "rtwtypes.h"
#include "SPWM_private.h"

extern "C"
{

#include "rt_nonfinite.h"

}

real32_T Ia;                           // Probe
real32_T Ib;                           // Probe
real32_T Ic;                           // Probe
real32_T Va_ref;                       // Probe
real32_T Vb_ref;                       // Probe
real32_T Vc_ref;                       // Probe
real32_T Vdc;                          // Probe
real32_T d_a;                          // Probe
real32_T d_b;                          // Probe
real32_T d_c;                          // Probe
int16_T* ix_raw_adc_ptr_0_0;
int16_T* ix_raw_adc_ptr_1_0;
int16_T* ix_raw_adc_ptr_2_0;
int16_T* ix_raw_adc_ptr_3_0;
real32_T p;                            // Tunable parameter
real32_T M;                            // Tunable parameter

// Block signals (default storage)
B_SPWM_T SPWM_B;

// Block states (default storage)
DW_SPWM_T SPWM_DW;

// Real-time model
RT_MODEL_SPWM_T SPWM_M_ = RT_MODEL_SPWM_T();
RT_MODEL_SPWM_T *const SPWM_M = &SPWM_M_;
uint32_T plook_u32ff_binx(real32_T u, const real32_T bp[], uint32_T maxIndex,
  real32_T *fraction)
{
  uint32_T bpIndex;

  // Prelookup - Index and Fraction
  // Index Search method: 'binary'
  // Extrapolation method: 'Linear'
  // Use previous index: 'off'
  // Use last breakpoint for index at or above upper limit: 'off'
  // Remove protection against out-of-range input in generated code: 'off'

  if (u <= bp[0U]) {
    bpIndex = 0U;
    *fraction = (u - bp[0U]) / (bp[1U] - bp[0U]);
  } else if (u < bp[maxIndex]) {
    bpIndex = binsearch_u32f(u, bp, maxIndex >> 1U, maxIndex);
    *fraction = (u - bp[bpIndex]) / (bp[bpIndex + 1U] - bp[bpIndex]);
  } else {
    bpIndex = maxIndex - 1U;
    *fraction = (u - bp[maxIndex - 1U]) / (bp[maxIndex] - bp[maxIndex - 1U]);
  }

  return bpIndex;
}

real32_T intrp4d_fu32fl_pw(const uint32_T bpIndex[], const real32_T frac[],
  const real32_T table[], const uint32_T stride[])
{
  real32_T yL_0d0;
  real32_T yL_1d;
  real32_T yL_2d;
  real32_T yL_3d;
  uint32_T offset_0d;
  uint32_T offset_1d;
  uint32_T offset_3d;

  // Column-major Interpolation 4-D
  // Interpolation method: 'Linear point-slope'
  // Use last breakpoint for index at or above upper limit: 'off'
  // Overflow mode: 'portable wrapping'

  offset_3d = ((bpIndex[3U] * stride[3U] + bpIndex[2U] * stride[2U]) + bpIndex
               [1U] * stride[1U]) + bpIndex[0U];
  yL_0d0 = table[offset_3d];
  yL_1d = (table[offset_3d + 1U] - yL_0d0) * frac[0U] + yL_0d0;
  offset_0d = offset_3d + stride[1U];
  yL_0d0 = table[offset_0d];
  yL_2d = (((table[offset_0d + 1U] - yL_0d0) * frac[0U] + yL_0d0) - yL_1d) *
    frac[1U] + yL_1d;
  offset_1d = offset_3d + stride[2U];
  yL_0d0 = table[offset_1d];
  yL_1d = (table[offset_1d + 1U] - yL_0d0) * frac[0U] + yL_0d0;
  offset_0d = offset_1d + stride[1U];
  yL_0d0 = table[offset_0d];
  yL_3d = (((((table[offset_0d + 1U] - yL_0d0) * frac[0U] + yL_0d0) - yL_1d) *
            frac[1U] + yL_1d) - yL_2d) * frac[2U] + yL_2d;
  offset_1d = offset_3d + stride[3U];
  yL_0d0 = table[offset_1d];
  yL_1d = (table[offset_1d + 1U] - yL_0d0) * frac[0U] + yL_0d0;
  offset_0d = offset_1d + stride[1U];
  yL_0d0 = table[offset_0d];
  yL_2d = (((table[offset_0d + 1U] - yL_0d0) * frac[0U] + yL_0d0) - yL_1d) *
    frac[1U] + yL_1d;
  offset_1d += stride[2U];
  yL_0d0 = table[offset_1d];
  yL_1d = (table[offset_1d + 1U] - yL_0d0) * frac[0U] + yL_0d0;
  offset_0d = offset_1d + stride[1U];
  yL_0d0 = table[offset_0d];
  return (((((((table[offset_0d + 1U] - yL_0d0) * frac[0U] + yL_0d0) - yL_1d) *
             frac[1U] + yL_1d) - yL_2d) * frac[2U] + yL_2d) - yL_3d) * frac[3U]
    + yL_3d;
}

uint32_T binsearch_u32f(real32_T u, const real32_T bp[], uint32_T startIndex,
  uint32_T maxIndex)
{
  uint32_T bpIdx;
  uint32_T bpIndex;
  uint32_T iRght;

  // Binary Search
  bpIdx = startIndex;
  bpIndex = 0U;
  iRght = maxIndex;
  while (iRght - bpIndex > 1U) {
    if (u < bp[bpIdx]) {
      iRght = bpIdx;
    } else {
      bpIndex = bpIdx;
    }

    bpIdx = (iRght + bpIndex) >> 1U;
  }

  return bpIndex;
}

// Model step function
void SPWM_step(void)
{
  real_T rtb_Delay;
  real32_T fractions[4];
  real32_T fractions_0[4];
  real32_T frac;
  real32_T rtb_Divide1;
  real32_T rtb_nDLookupTable1;
  uint32_T bpIndices[4];
  uint32_T bpIndices_0[4];

  // S-Function (PROBE): '<S49>/S-Function'
  Ia = SPWM_B.ADC;

  // S-Function (PROBE): '<S51>/S-Function'
  Ib = SPWM_B.ADC_f;

  // S-Function (PROBE): '<S53>/S-Function'
  Ic = SPWM_B.ADC_d;

  // S-Function (PROBE): '<S55>/S-Function'
  Va_ref = SPWM_B.Vdc2[0];

  // S-Function (PROBE): '<S57>/S-Function'
  Vb_ref = SPWM_B.Vdc2[1];

  // S-Function (PROBE): '<S59>/S-Function'
  Vc_ref = SPWM_B.Vdc2[2];

  // S-Function (PROBE): '<S61>/S-Function'
  Vdc = SPWM_B.ADC_k;

  // S-Function (PROBE): '<S63>/S-Function'
  d_a = SPWM_B.Dutycycles[0];

  // S-Function (PROBE): '<S65>/S-Function'
  d_b = SPWM_B.Dutycycles[1];

  // S-Function (PROBE): '<S67>/S-Function'
  d_c = SPWM_B.Dutycycles[2];

  // S-Function (ADC): '<S26>/ADC'
  SPWM_B.ADC = (float)(*ix_raw_adc_ptr_0_0) * 0.0015259F + -0.045F;

  // S-Function (ADC): '<S28>/ADC'
  SPWM_B.ADC_f = (float)(*ix_raw_adc_ptr_1_0) * 0.0015259F + -0.04F;

  // S-Function (ADC): '<S30>/ADC'
  SPWM_B.ADC_d = (float)(*ix_raw_adc_ptr_2_0) * 0.0015259F + -0.052F;

  // S-Function (ADC): '<S32>/ADC'
  SPWM_B.ADC_k = (float)(*ix_raw_adc_ptr_3_0) * 0.030579F + -0.35F;

  // Delay: '<S7>/Delay'
  rtb_Delay = SPWM_DW.Delay_DSTATE;

  // If: '<S7>/If' incorporates:
  //   Delay: '<S7>/Delay'

  if (SPWM_DW.Delay_DSTATE > 3.1415926535897931) {
    // DataStoreRead: '<S7>/Data Store Read' incorporates:
    //   Constant: '<S7>/Constant'
    //   SampleTimeMath: '<S7>/Weighted Sample Time'
    //   Sum: '<S7>/Add'
    //
    //  About '<S7>/Weighted Sample Time':
    //   y = u + K where K = ( w * Ts )

    SPWM_DW.Delay_DSTATE = (SPWM_DW.Delay_DSTATE +
      SPWM_P.WeightedSampleTime_WtEt) - SPWM_P.Constant_Value;
  } else {
    // DataStoreRead: '<S7>/Data Store Read' incorporates:
    //   SampleTimeMath: '<S7>/Weighted Sample Time'
    //
    //  About '<S7>/Weighted Sample Time':
    //   y = u + K where K = ( w * Ts )

    SPWM_DW.Delay_DSTATE += SPWM_P.WeightedSampleTime_WtEt;
  }

  // End of If: '<S7>/If'

  // S-Function (TUNABLE_PARAM): '<S71>/S-Function'
  SPWM_B.SFunction = p;

  // Gain: '<S1>/Gain1'
  SPWM_B.Saturation = SPWM_P.Gain1_Gain * SPWM_B.SFunction;

  // Saturate: '<S36>/Saturation'
  if (SPWM_B.Saturation > SPWM_P.Saturation_UpperSat) {
    // Gain: '<S1>/Gain1' incorporates:
    //   Saturate: '<S36>/Saturation'

    SPWM_B.Saturation = SPWM_P.Saturation_UpperSat;
  } else if (SPWM_B.Saturation < SPWM_P.Saturation_LowerSat) {
    // Gain: '<S1>/Gain1' incorporates:
    //   Saturate: '<S36>/Saturation'

    SPWM_B.Saturation = SPWM_P.Saturation_LowerSat;
  }

  // End of Saturate: '<S36>/Saturation'

  // S-Function (CLK): '<S36>/CLK1'
  Clock_SetFrequency((tClock) 1, SPWM_B.Saturation);

  // Sum: '<S1>/Sum4' incorporates:
  //   Abs: '<S1>/Abs'
  //   Abs: '<S1>/Abs1'
  //   Abs: '<S1>/Abs2'

  rtb_Divide1 = (static_cast<real32_T>(fabs(static_cast<real_T>(SPWM_B.ADC))) +
                 static_cast<real32_T>(fabs(static_cast<real_T>(SPWM_B.ADC_f))))
    + static_cast<real32_T>(fabs(static_cast<real_T>(SPWM_B.ADC_d)));

  // Product: '<S1>/Divide'
  rtb_nDLookupTable1 = SPWM_B.ADC_f / rtb_Divide1;

  // Product: '<S1>/Divide1'
  rtb_Divide1 = SPWM_B.ADC_d / rtb_Divide1;

  // S-Function (TUNABLE_PARAM): '<S69>/S-Function'
  SPWM_B.SFunction_o = M;

  // Product: '<S1>/Product' incorporates:
  //   Constant: '<S1>/Constant'
  //   DataTypeConversion: '<S7>/Data Type Conversion'
  //   Sum: '<S1>/Sum'
  //   Sum: '<S1>/Sum1'
  //   Trigonometry: '<S1>/Trigonometric Function'

  SPWM_B.Vdc2[0] = SPWM_B.SFunction_o * static_cast<real32_T>(sin
    (static_cast<real_T>(static_cast<real32_T>(rtb_Delay))));
  SPWM_B.Vdc2[1] = static_cast<real32_T>(sin(static_cast<real_T>
    (static_cast<real32_T>(rtb_Delay) - SPWM_P.Constant_Value_j))) *
    SPWM_B.SFunction_o;
  SPWM_B.Vdc2[2] = static_cast<real32_T>(sin(static_cast<real_T>
    (static_cast<real32_T>(rtb_Delay) + SPWM_P.Constant_Value_j))) *
    SPWM_B.SFunction_o;

  // Sum: '<S1>/Sum2' incorporates:
  //   Constant: '<S1>/Constant1'
  //   Gain: '<S1>/Gain'

  SPWM_B.Dutycycles[0] = SPWM_P.Gain_Gain * SPWM_B.Vdc2[0] +
    SPWM_P.Constant1_Value;
  SPWM_B.Dutycycles[1] = SPWM_P.Gain_Gain * SPWM_B.Vdc2[1] +
    SPWM_P.Constant1_Value;
  SPWM_B.Dutycycles[2] = SPWM_P.Gain_Gain * SPWM_B.Vdc2[2] +
    SPWM_P.Constant1_Value;

  // Lookup_n-D: '<S1>/n-D Lookup Table' incorporates:
  //   Lookup_n-D: '<S1>/n-D Lookup Table1'
  //   Product: '<S1>/Divide1'

  bpIndices[0U] = plook_u32ff_binx(SPWM_B.Dutycycles[1], SPWM_P.DB, 4U, &frac);
  fractions[0U] = frac;
  bpIndices[1U] = plook_u32ff_binx(SPWM_B.Dutycycles[2], SPWM_P.DC, 4U, &frac);
  fractions[1U] = frac;
  bpIndices[2U] = plook_u32ff_binx(rtb_nDLookupTable1, SPWM_P.Ib, 4U, &frac);
  fractions[2U] = frac;
  bpIndices[3U] = plook_u32ff_binx(rtb_Divide1, SPWM_P.Ic, 4U, &frac);
  fractions[3U] = frac;

  // Gain: '<S1>/Gain4' incorporates:
  //   Lookup_n-D: '<S1>/n-D Lookup Table'

  SPWM_B.Gain4 = SPWM_P.Gain4_Gain * intrp4d_fu32fl_pw(bpIndices, fractions,
    SPWM_P.theta_b_LUT, SPWM_P.nDLookupTable_dimSizes);

  // Lookup_n-D: '<S1>/n-D Lookup Table1' incorporates:
  //   Product: '<S1>/Divide1'

  bpIndices_0[0U] = plook_u32ff_binx(SPWM_B.Dutycycles[1], SPWM_P.DB, 4U, &frac);
  fractions_0[0U] = frac;
  bpIndices_0[1U] = plook_u32ff_binx(SPWM_B.Dutycycles[2], SPWM_P.DC, 4U, &frac);
  fractions_0[1U] = frac;
  bpIndices_0[2U] = plook_u32ff_binx(rtb_nDLookupTable1, SPWM_P.Ib, 4U, &frac);
  fractions_0[2U] = frac;
  bpIndices_0[3U] = plook_u32ff_binx(rtb_Divide1, SPWM_P.Ic, 4U, &frac);
  fractions_0[3U] = frac;

  // Gain: '<S1>/Gain5' incorporates:
  //   Lookup_n-D: '<S1>/n-D Lookup Table1'

  SPWM_B.Gain5 = SPWM_P.Gain5_Gain * intrp4d_fu32fl_pw(bpIndices_0, fractions_0,
    SPWM_P.theta_b_LUT, SPWM_P.nDLookupTable1_dimSizes);

  // DataTypeConversion: '<S10>/Data Type Conversion2' incorporates:
  //   Constant: '<S1>/Constant2'

  SPWM_B.DataTypeConversion2 = static_cast<real32_T>(SPWM_P.Constant2_Value);

  // DataTypeConversion: '<S10>/Data Type Conversion3' incorporates:
  //   Constant: '<S10>/enable'

  SPWM_B.DataTypeConversion3 = static_cast<real32_T>(SPWM_P.enable_Value);

  // Outputs for Atomic SubSystem: '<S42>/generation'
  // S-Function (CB_PWM): '<S43>/PWM' incorporates:
  //   Constant: '<S36>/clk_id'

  CbPwm_SetDutyCycle((tPwmOutput) 0, SPWM_B.Dutycycles[0], 0);
  CbPwm_SetPhase((tPwmOutput) 0, SPWM_B.DataTypeConversion2, 0);

  // End of Outputs for SubSystem: '<S42>/generation'

  // DataTypeConversion: '<S11>/Data Type Conversion3' incorporates:
  //   Constant: '<S11>/enable'

  SPWM_B.DataTypeConversion3_k = static_cast<real32_T>(SPWM_P.enable_Value_a);

  // Outputs for Atomic SubSystem: '<S44>/generation'
  // S-Function (CB_PWM): '<S45>/PWM' incorporates:
  //   Constant: '<S36>/clk_id'

  CbPwm_SetDutyCycle((tPwmOutput) 2, SPWM_B.Dutycycles[1], 0);
  CbPwm_SetPhase((tPwmOutput) 2, SPWM_B.Gain4, 0);

  // End of Outputs for SubSystem: '<S44>/generation'

  // DataTypeConversion: '<S12>/Data Type Conversion3' incorporates:
  //   Constant: '<S12>/enable'

  SPWM_B.DataTypeConversion3_l = static_cast<real32_T>(SPWM_P.enable_Value_o);

  // Outputs for Atomic SubSystem: '<S46>/generation'
  // S-Function (CB_PWM): '<S47>/PWM' incorporates:
  //   Constant: '<S36>/clk_id'

  CbPwm_SetDutyCycle((tPwmOutput) 4, SPWM_B.Dutycycles[2], 0);
  CbPwm_SetPhase((tPwmOutput) 4, SPWM_B.Gain5, 0);

  // End of Outputs for SubSystem: '<S46>/generation'

  // Gain: '<S1>/Vdc//2' incorporates:
  //   Product: '<S1>/Product'

  SPWM_B.Vdc2[0] *= SPWM_P.Vdc2_Gain;
  SPWM_B.Vdc2[1] *= SPWM_P.Vdc2_Gain;
  SPWM_B.Vdc2[2] *= SPWM_P.Vdc2_Gain;
}

// Model initialize function
void SPWM_initialize(void)
{
  // Registration code

  // initialize non-finites
  rt_InitInfAndNaN(sizeof(real_T));

  // non-finite (run-time) assignments
  SPWM_P.theta_b_LUT[0] = rtNaNF;
  SPWM_P.theta_b_LUT[1] = rtNaNF;
  SPWM_P.theta_b_LUT[2] = rtNaNF;
  SPWM_P.theta_b_LUT[5] = rtNaNF;
  SPWM_P.theta_b_LUT[6] = rtNaNF;
  SPWM_P.theta_b_LUT[10] = rtNaNF;
  SPWM_P.theta_b_LUT[14] = rtNaNF;
  SPWM_P.theta_b_LUT[18] = rtNaNF;
  SPWM_P.theta_b_LUT[19] = rtNaNF;
  SPWM_P.theta_b_LUT[22] = rtNaNF;
  SPWM_P.theta_b_LUT[23] = rtNaNF;
  SPWM_P.theta_b_LUT[24] = rtNaNF;
  SPWM_P.theta_b_LUT[25] = rtNaNF;
  SPWM_P.theta_b_LUT[26] = rtNaNF;
  SPWM_P.theta_b_LUT[27] = rtNaNF;
  SPWM_P.theta_b_LUT[30] = rtNaNF;
  SPWM_P.theta_b_LUT[31] = rtNaNF;
  SPWM_P.theta_b_LUT[35] = rtNaNF;
  SPWM_P.theta_b_LUT[39] = rtNaNF;
  SPWM_P.theta_b_LUT[43] = rtNaNF;
  SPWM_P.theta_b_LUT[44] = rtNaNF;
  SPWM_P.theta_b_LUT[47] = rtNaNF;
  SPWM_P.theta_b_LUT[48] = rtNaNF;
  SPWM_P.theta_b_LUT[49] = rtNaNF;
  SPWM_P.theta_b_LUT[50] = rtNaNF;
  SPWM_P.theta_b_LUT[51] = rtNaNF;
  SPWM_P.theta_b_LUT[52] = rtNaNF;
  SPWM_P.theta_b_LUT[55] = rtNaNF;
  SPWM_P.theta_b_LUT[56] = rtNaNF;
  SPWM_P.theta_b_LUT[60] = rtNaNF;
  SPWM_P.theta_b_LUT[64] = rtNaNF;
  SPWM_P.theta_b_LUT[68] = rtNaNF;
  SPWM_P.theta_b_LUT[69] = rtNaNF;
  SPWM_P.theta_b_LUT[72] = rtNaNF;
  SPWM_P.theta_b_LUT[73] = rtNaNF;
  SPWM_P.theta_b_LUT[74] = rtNaNF;
  SPWM_P.theta_b_LUT[75] = rtNaNF;
  SPWM_P.theta_b_LUT[76] = rtNaNF;
  SPWM_P.theta_b_LUT[77] = rtNaNF;
  SPWM_P.theta_b_LUT[80] = rtNaNF;
  SPWM_P.theta_b_LUT[81] = rtNaNF;
  SPWM_P.theta_b_LUT[85] = rtNaNF;
  SPWM_P.theta_b_LUT[89] = rtNaNF;
  SPWM_P.theta_b_LUT[93] = rtNaNF;
  SPWM_P.theta_b_LUT[94] = rtNaNF;
  SPWM_P.theta_b_LUT[97] = rtNaNF;
  SPWM_P.theta_b_LUT[98] = rtNaNF;
  SPWM_P.theta_b_LUT[99] = rtNaNF;
  SPWM_P.theta_b_LUT[100] = rtNaNF;
  SPWM_P.theta_b_LUT[101] = rtNaNF;
  SPWM_P.theta_b_LUT[102] = rtNaNF;
  SPWM_P.theta_b_LUT[105] = rtNaNF;
  SPWM_P.theta_b_LUT[106] = rtNaNF;
  SPWM_P.theta_b_LUT[110] = rtNaNF;
  SPWM_P.theta_b_LUT[114] = rtNaNF;
  SPWM_P.theta_b_LUT[118] = rtNaNF;
  SPWM_P.theta_b_LUT[119] = rtNaNF;
  SPWM_P.theta_b_LUT[122] = rtNaNF;
  SPWM_P.theta_b_LUT[123] = rtNaNF;
  SPWM_P.theta_b_LUT[124] = rtNaNF;
  SPWM_P.theta_b_LUT[125] = rtNaNF;
  SPWM_P.theta_b_LUT[126] = rtNaNF;
  SPWM_P.theta_b_LUT[127] = rtNaNF;
  SPWM_P.theta_b_LUT[130] = rtNaNF;
  SPWM_P.theta_b_LUT[131] = rtNaNF;
  SPWM_P.theta_b_LUT[135] = rtNaNF;
  SPWM_P.theta_b_LUT[139] = rtNaNF;
  SPWM_P.theta_b_LUT[143] = rtNaNF;
  SPWM_P.theta_b_LUT[144] = rtNaNF;
  SPWM_P.theta_b_LUT[147] = rtNaNF;
  SPWM_P.theta_b_LUT[148] = rtNaNF;
  SPWM_P.theta_b_LUT[149] = rtNaNF;
  SPWM_P.theta_b_LUT[150] = rtNaNF;
  SPWM_P.theta_b_LUT[151] = rtNaNF;
  SPWM_P.theta_b_LUT[152] = rtNaNF;
  SPWM_P.theta_b_LUT[155] = rtNaNF;
  SPWM_P.theta_b_LUT[156] = rtNaNF;
  SPWM_P.theta_b_LUT[160] = rtNaNF;
  SPWM_P.theta_b_LUT[164] = rtNaNF;
  SPWM_P.theta_b_LUT[168] = rtNaNF;
  SPWM_P.theta_b_LUT[169] = rtNaNF;
  SPWM_P.theta_b_LUT[172] = rtNaNF;
  SPWM_P.theta_b_LUT[173] = rtNaNF;
  SPWM_P.theta_b_LUT[174] = rtNaNF;
  SPWM_P.theta_b_LUT[175] = rtNaNF;
  SPWM_P.theta_b_LUT[176] = rtNaNF;
  SPWM_P.theta_b_LUT[177] = rtNaNF;
  SPWM_P.theta_b_LUT[180] = rtNaNF;
  SPWM_P.theta_b_LUT[181] = rtNaNF;
  SPWM_P.theta_b_LUT[185] = rtNaNF;
  SPWM_P.theta_b_LUT[189] = rtNaNF;
  SPWM_P.theta_b_LUT[193] = rtNaNF;
  SPWM_P.theta_b_LUT[194] = rtNaNF;
  SPWM_P.theta_b_LUT[197] = rtNaNF;
  SPWM_P.theta_b_LUT[198] = rtNaNF;
  SPWM_P.theta_b_LUT[199] = rtNaNF;
  SPWM_P.theta_b_LUT[200] = rtNaNF;
  SPWM_P.theta_b_LUT[201] = rtNaNF;
  SPWM_P.theta_b_LUT[202] = rtNaNF;
  SPWM_P.theta_b_LUT[205] = rtNaNF;
  SPWM_P.theta_b_LUT[206] = rtNaNF;
  SPWM_P.theta_b_LUT[210] = rtNaNF;
  SPWM_P.theta_b_LUT[214] = rtNaNF;
  SPWM_P.theta_b_LUT[218] = rtNaNF;
  SPWM_P.theta_b_LUT[219] = rtNaNF;
  SPWM_P.theta_b_LUT[222] = rtNaNF;
  SPWM_P.theta_b_LUT[223] = rtNaNF;
  SPWM_P.theta_b_LUT[224] = rtNaNF;
  SPWM_P.theta_b_LUT[225] = rtNaNF;
  SPWM_P.theta_b_LUT[226] = rtNaNF;
  SPWM_P.theta_b_LUT[227] = rtNaNF;
  SPWM_P.theta_b_LUT[230] = rtNaNF;
  SPWM_P.theta_b_LUT[231] = rtNaNF;
  SPWM_P.theta_b_LUT[235] = rtNaNF;
  SPWM_P.theta_b_LUT[239] = rtNaNF;
  SPWM_P.theta_b_LUT[243] = rtNaNF;
  SPWM_P.theta_b_LUT[244] = rtNaNF;
  SPWM_P.theta_b_LUT[247] = rtNaNF;
  SPWM_P.theta_b_LUT[248] = rtNaNF;
  SPWM_P.theta_b_LUT[249] = rtNaNF;
  SPWM_P.theta_b_LUT[250] = rtNaNF;
  SPWM_P.theta_b_LUT[251] = rtNaNF;
  SPWM_P.theta_b_LUT[252] = rtNaNF;
  SPWM_P.theta_b_LUT[255] = rtNaNF;
  SPWM_P.theta_b_LUT[256] = rtNaNF;
  SPWM_P.theta_b_LUT[260] = rtNaNF;
  SPWM_P.theta_b_LUT[264] = rtNaNF;
  SPWM_P.theta_b_LUT[268] = rtNaNF;
  SPWM_P.theta_b_LUT[269] = rtNaNF;
  SPWM_P.theta_b_LUT[272] = rtNaNF;
  SPWM_P.theta_b_LUT[273] = rtNaNF;
  SPWM_P.theta_b_LUT[274] = rtNaNF;
  SPWM_P.theta_b_LUT[275] = rtNaNF;
  SPWM_P.theta_b_LUT[276] = rtNaNF;
  SPWM_P.theta_b_LUT[277] = rtNaNF;
  SPWM_P.theta_b_LUT[280] = rtNaNF;
  SPWM_P.theta_b_LUT[281] = rtNaNF;
  SPWM_P.theta_b_LUT[285] = rtNaNF;
  SPWM_P.theta_b_LUT[289] = rtNaNF;
  SPWM_P.theta_b_LUT[293] = rtNaNF;
  SPWM_P.theta_b_LUT[294] = rtNaNF;
  SPWM_P.theta_b_LUT[297] = rtNaNF;
  SPWM_P.theta_b_LUT[298] = rtNaNF;
  SPWM_P.theta_b_LUT[299] = rtNaNF;
  SPWM_P.theta_b_LUT[300] = rtNaNF;
  SPWM_P.theta_b_LUT[301] = rtNaNF;
  SPWM_P.theta_b_LUT[302] = rtNaNF;
  SPWM_P.theta_b_LUT[305] = rtNaNF;
  SPWM_P.theta_b_LUT[306] = rtNaNF;
  SPWM_P.theta_b_LUT[310] = rtNaNF;
  SPWM_P.theta_b_LUT[314] = rtNaNF;
  SPWM_P.theta_b_LUT[318] = rtNaNF;
  SPWM_P.theta_b_LUT[319] = rtNaNF;
  SPWM_P.theta_b_LUT[322] = rtNaNF;
  SPWM_P.theta_b_LUT[323] = rtNaNF;
  SPWM_P.theta_b_LUT[324] = rtNaNF;
  SPWM_P.theta_b_LUT[325] = rtNaNF;
  SPWM_P.theta_b_LUT[326] = rtNaNF;
  SPWM_P.theta_b_LUT[327] = rtNaNF;
  SPWM_P.theta_b_LUT[330] = rtNaNF;
  SPWM_P.theta_b_LUT[331] = rtNaNF;
  SPWM_P.theta_b_LUT[335] = rtNaNF;
  SPWM_P.theta_b_LUT[339] = rtNaNF;
  SPWM_P.theta_b_LUT[343] = rtNaNF;
  SPWM_P.theta_b_LUT[344] = rtNaNF;
  SPWM_P.theta_b_LUT[347] = rtNaNF;
  SPWM_P.theta_b_LUT[348] = rtNaNF;
  SPWM_P.theta_b_LUT[349] = rtNaNF;
  SPWM_P.theta_b_LUT[350] = rtNaNF;
  SPWM_P.theta_b_LUT[351] = rtNaNF;
  SPWM_P.theta_b_LUT[352] = rtNaNF;
  SPWM_P.theta_b_LUT[355] = rtNaNF;
  SPWM_P.theta_b_LUT[356] = rtNaNF;
  SPWM_P.theta_b_LUT[360] = rtNaNF;
  SPWM_P.theta_b_LUT[364] = rtNaNF;
  SPWM_P.theta_b_LUT[368] = rtNaNF;
  SPWM_P.theta_b_LUT[369] = rtNaNF;
  SPWM_P.theta_b_LUT[372] = rtNaNF;
  SPWM_P.theta_b_LUT[373] = rtNaNF;
  SPWM_P.theta_b_LUT[374] = rtNaNF;
  SPWM_P.theta_b_LUT[375] = rtNaNF;
  SPWM_P.theta_b_LUT[376] = rtNaNF;
  SPWM_P.theta_b_LUT[377] = rtNaNF;
  SPWM_P.theta_b_LUT[380] = rtNaNF;
  SPWM_P.theta_b_LUT[381] = rtNaNF;
  SPWM_P.theta_b_LUT[385] = rtNaNF;
  SPWM_P.theta_b_LUT[389] = rtNaNF;
  SPWM_P.theta_b_LUT[393] = rtNaNF;
  SPWM_P.theta_b_LUT[394] = rtNaNF;
  SPWM_P.theta_b_LUT[397] = rtNaNF;
  SPWM_P.theta_b_LUT[398] = rtNaNF;
  SPWM_P.theta_b_LUT[399] = rtNaNF;
  SPWM_P.theta_b_LUT[400] = rtNaNF;
  SPWM_P.theta_b_LUT[401] = rtNaNF;
  SPWM_P.theta_b_LUT[402] = rtNaNF;
  SPWM_P.theta_b_LUT[405] = rtNaNF;
  SPWM_P.theta_b_LUT[406] = rtNaNF;
  SPWM_P.theta_b_LUT[410] = rtNaNF;
  SPWM_P.theta_b_LUT[414] = rtNaNF;
  SPWM_P.theta_b_LUT[418] = rtNaNF;
  SPWM_P.theta_b_LUT[419] = rtNaNF;
  SPWM_P.theta_b_LUT[422] = rtNaNF;
  SPWM_P.theta_b_LUT[423] = rtNaNF;
  SPWM_P.theta_b_LUT[424] = rtNaNF;
  SPWM_P.theta_b_LUT[425] = rtNaNF;
  SPWM_P.theta_b_LUT[426] = rtNaNF;
  SPWM_P.theta_b_LUT[427] = rtNaNF;
  SPWM_P.theta_b_LUT[430] = rtNaNF;
  SPWM_P.theta_b_LUT[431] = rtNaNF;
  SPWM_P.theta_b_LUT[435] = rtNaNF;
  SPWM_P.theta_b_LUT[439] = rtNaNF;
  SPWM_P.theta_b_LUT[443] = rtNaNF;
  SPWM_P.theta_b_LUT[444] = rtNaNF;
  SPWM_P.theta_b_LUT[447] = rtNaNF;
  SPWM_P.theta_b_LUT[448] = rtNaNF;
  SPWM_P.theta_b_LUT[449] = rtNaNF;
  SPWM_P.theta_b_LUT[450] = rtNaNF;
  SPWM_P.theta_b_LUT[451] = rtNaNF;
  SPWM_P.theta_b_LUT[452] = rtNaNF;
  SPWM_P.theta_b_LUT[455] = rtNaNF;
  SPWM_P.theta_b_LUT[456] = rtNaNF;
  SPWM_P.theta_b_LUT[460] = rtNaNF;
  SPWM_P.theta_b_LUT[464] = rtNaNF;
  SPWM_P.theta_b_LUT[468] = rtNaNF;
  SPWM_P.theta_b_LUT[469] = rtNaNF;
  SPWM_P.theta_b_LUT[472] = rtNaNF;
  SPWM_P.theta_b_LUT[473] = rtNaNF;
  SPWM_P.theta_b_LUT[474] = rtNaNF;
  SPWM_P.theta_b_LUT[475] = rtNaNF;
  SPWM_P.theta_b_LUT[476] = rtNaNF;
  SPWM_P.theta_b_LUT[477] = rtNaNF;
  SPWM_P.theta_b_LUT[480] = rtNaNF;
  SPWM_P.theta_b_LUT[481] = rtNaNF;
  SPWM_P.theta_b_LUT[485] = rtNaNF;
  SPWM_P.theta_b_LUT[489] = rtNaNF;
  SPWM_P.theta_b_LUT[493] = rtNaNF;
  SPWM_P.theta_b_LUT[494] = rtNaNF;
  SPWM_P.theta_b_LUT[497] = rtNaNF;
  SPWM_P.theta_b_LUT[498] = rtNaNF;
  SPWM_P.theta_b_LUT[499] = rtNaNF;
  SPWM_P.theta_b_LUT[500] = rtNaNF;
  SPWM_P.theta_b_LUT[501] = rtNaNF;
  SPWM_P.theta_b_LUT[502] = rtNaNF;
  SPWM_P.theta_b_LUT[505] = rtNaNF;
  SPWM_P.theta_b_LUT[506] = rtNaNF;
  SPWM_P.theta_b_LUT[510] = rtNaNF;
  SPWM_P.theta_b_LUT[514] = rtNaNF;
  SPWM_P.theta_b_LUT[518] = rtNaNF;
  SPWM_P.theta_b_LUT[519] = rtNaNF;
  SPWM_P.theta_b_LUT[522] = rtNaNF;
  SPWM_P.theta_b_LUT[523] = rtNaNF;
  SPWM_P.theta_b_LUT[524] = rtNaNF;
  SPWM_P.theta_b_LUT[525] = rtNaNF;
  SPWM_P.theta_b_LUT[526] = rtNaNF;
  SPWM_P.theta_b_LUT[527] = rtNaNF;
  SPWM_P.theta_b_LUT[530] = rtNaNF;
  SPWM_P.theta_b_LUT[531] = rtNaNF;
  SPWM_P.theta_b_LUT[535] = rtNaNF;
  SPWM_P.theta_b_LUT[539] = rtNaNF;
  SPWM_P.theta_b_LUT[543] = rtNaNF;
  SPWM_P.theta_b_LUT[544] = rtNaNF;
  SPWM_P.theta_b_LUT[547] = rtNaNF;
  SPWM_P.theta_b_LUT[548] = rtNaNF;
  SPWM_P.theta_b_LUT[549] = rtNaNF;
  SPWM_P.theta_b_LUT[550] = rtNaNF;
  SPWM_P.theta_b_LUT[551] = rtNaNF;
  SPWM_P.theta_b_LUT[552] = rtNaNF;
  SPWM_P.theta_b_LUT[555] = rtNaNF;
  SPWM_P.theta_b_LUT[556] = rtNaNF;
  SPWM_P.theta_b_LUT[560] = rtNaNF;
  SPWM_P.theta_b_LUT[564] = rtNaNF;
  SPWM_P.theta_b_LUT[568] = rtNaNF;
  SPWM_P.theta_b_LUT[569] = rtNaNF;
  SPWM_P.theta_b_LUT[572] = rtNaNF;
  SPWM_P.theta_b_LUT[573] = rtNaNF;
  SPWM_P.theta_b_LUT[574] = rtNaNF;
  SPWM_P.theta_b_LUT[575] = rtNaNF;
  SPWM_P.theta_b_LUT[576] = rtNaNF;
  SPWM_P.theta_b_LUT[577] = rtNaNF;
  SPWM_P.theta_b_LUT[580] = rtNaNF;
  SPWM_P.theta_b_LUT[581] = rtNaNF;
  SPWM_P.theta_b_LUT[585] = rtNaNF;
  SPWM_P.theta_b_LUT[589] = rtNaNF;
  SPWM_P.theta_b_LUT[593] = rtNaNF;
  SPWM_P.theta_b_LUT[594] = rtNaNF;
  SPWM_P.theta_b_LUT[597] = rtNaNF;
  SPWM_P.theta_b_LUT[598] = rtNaNF;
  SPWM_P.theta_b_LUT[599] = rtNaNF;
  SPWM_P.theta_b_LUT[600] = rtNaNF;
  SPWM_P.theta_b_LUT[601] = rtNaNF;
  SPWM_P.theta_b_LUT[602] = rtNaNF;
  SPWM_P.theta_b_LUT[605] = rtNaNF;
  SPWM_P.theta_b_LUT[606] = rtNaNF;
  SPWM_P.theta_b_LUT[610] = rtNaNF;
  SPWM_P.theta_b_LUT[614] = rtNaNF;
  SPWM_P.theta_b_LUT[618] = rtNaNF;
  SPWM_P.theta_b_LUT[619] = rtNaNF;
  SPWM_P.theta_b_LUT[622] = rtNaNF;
  SPWM_P.theta_b_LUT[623] = rtNaNF;
  SPWM_P.theta_b_LUT[624] = rtNaNF;

  // Start for S-Function (PROBE): '<S49>/S-Function'
  ConfigureProbe(&Ia, 0);

  // Start for S-Function (PROBE): '<S51>/S-Function'
  ConfigureProbe(&Ib, 0);

  // Start for S-Function (PROBE): '<S53>/S-Function'
  ConfigureProbe(&Ic, 0);

  // Start for S-Function (PROBE): '<S55>/S-Function'
  ConfigureProbe(&Va_ref, 0);

  // Start for S-Function (PROBE): '<S57>/S-Function'
  ConfigureProbe(&Vb_ref, 0);

  // Start for S-Function (PROBE): '<S59>/S-Function'
  ConfigureProbe(&Vc_ref, 0);

  // Start for S-Function (PROBE): '<S61>/S-Function'
  ConfigureProbe(&Vdc, 0);

  // Start for S-Function (PROBE): '<S63>/S-Function'
  ConfigureProbe(&d_a, 0);

  // Start for S-Function (PROBE): '<S65>/S-Function'
  ConfigureProbe(&d_b, 0);

  // Start for S-Function (PROBE): '<S67>/S-Function'
  ConfigureProbe(&d_c, 0);

  // Start for S-Function (ADC): '<S26>/ADC'
  Adc_ConfigureInput(0, 0.0015259F, -0.045F, 0);
  Adc_GetPointer(0, 0, &ix_raw_adc_ptr_0_0);

  // Start for S-Function (ADC): '<S28>/ADC'
  Adc_ConfigureInput(1, 0.0015259F, -0.04F, 0);
  Adc_GetPointer(1, 0, &ix_raw_adc_ptr_1_0);

  // Start for S-Function (ADC): '<S30>/ADC'
  Adc_ConfigureInput(2, 0.0015259F, -0.052F, 0);
  Adc_GetPointer(2, 0, &ix_raw_adc_ptr_2_0);

  // Start for S-Function (ADC): '<S32>/ADC'
  Adc_ConfigureInput(3, 0.030579F, -0.35F, 0);
  Adc_GetPointer(3, 0, &ix_raw_adc_ptr_3_0);

  // Start for S-Function (TUNABLE_PARAM): '<S71>/S-Function'
  p = 40.0F;                           // Tunable parameter initialization
  ConfigureTunable(&p, 0, 0, 3.0F, 300.0F);

  // Start for S-Function (CLK): '<S36>/CLK1'
  Clock_SetFrequency((tClock) 1, 1950.0F);
  Clock_ConfigureAsRealTimeTunable((tClock) 1);

  // Start for S-Function (IRQ): '<S39>/S-Function' incorporates:
  //   Constant: '<S41>/clk_id'

  ConfigureMainInterrupt(SimulinkInterrupt, (tClock) SPWM_P.clk_id_Value_o, 0.5F,
    0U);
  Adc_AddSamplingEvent((SPWM_P.SFunction_P2));
  ConfigureReadTriggerDelayInNs(2000U);

  // Start for S-Function (CLK): '<S41>/CLK1'
  Clock_SetFrequency((tClock) 0, 2000.0F);

  // Start for S-Function (TUNABLE_PARAM): '<S69>/S-Function'
  M = 0.8F;                            // Tunable parameter initialization
  ConfigureTunable(&M, 0, 0, 0.1F, 2.0F);

  // Start for Atomic SubSystem: '<S42>/generation'

  // Start for S-Function (CB_PWM): '<S43>/PWM' incorporates:
  //   Constant: '<S36>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 0, (tClock) SPWM_P.clk_id_Value, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 0, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 0, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 0, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 0, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 0, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 0, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 0, 0);

  // End of Start for SubSystem: '<S42>/generation'

  // Start for Atomic SubSystem: '<S44>/generation'

  // Start for S-Function (CB_PWM): '<S45>/PWM' incorporates:
  //   Constant: '<S36>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 2, (tClock) SPWM_P.clk_id_Value, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 2, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 2, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 2, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 2, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 2, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 2, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 2, 0);

  // End of Start for SubSystem: '<S44>/generation'

  // Start for Atomic SubSystem: '<S46>/generation'

  // Start for S-Function (CB_PWM): '<S47>/PWM' incorporates:
  //   Constant: '<S36>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 4, (tClock) SPWM_P.clk_id_Value, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 4, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 4, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 4, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 4, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 4, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 4, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 4, 0);

  // End of Start for SubSystem: '<S46>/generation'

  // InitializeConditions for Delay: '<S7>/Delay'
  SPWM_DW.Delay_DSTATE = SPWM_P.Delay_InitialCondition;
}

// Model terminate function
void SPWM_terminate(void)
{
  // (no terminate code required)
}

//
// End of automatically generated code
// Copyright imperix ltd. Switzerland 2021
// [EOF]
//

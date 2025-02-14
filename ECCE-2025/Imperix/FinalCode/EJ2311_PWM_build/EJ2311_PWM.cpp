//
// Academic License - for use in teaching, academic research, and meeting
// course requirements at degree granting institutions only.  Not for
// government, commercial, or other organizational use.
//
// File: EJ2311_PWM.cpp
//
// Code generated for Simulink model 'EJ2311_PWM'.
// To be implemented on the B-Box RCP or the B-Board PRO.
//
// Model version                  : 16.7
// Simulink Coder version         : 23.2 (R2023b) 01-Aug-2023
// C/C++ source code generated on : Thu Feb 13 14:54:27 2025
//
#include "EJ2311_PWM.h"
#include <math.h>
#include "rtwtypes.h"
#include "EJ2311_PWM_private.h"

extern "C"
{

#include "rt_nonfinite.h"

}

real32_T Va_ref;                       // Probe
real32_T Vb_ref;                       // Probe
real32_T Vc_ref;                       // Probe
real32_T d_a;                          // Probe
real32_T d_b;                          // Probe
real32_T d_c;                          // Probe
real32_T p;                            // Tunable parameter
real32_T activate_pwm;                 // Tunable parameter

// Block signals (default storage)
B_EJ2311_PWM_T EJ2311_PWM_B;

// Block states (default storage)
DW_EJ2311_PWM_T EJ2311_PWM_DW;

// Real-time model
RT_MODEL_EJ2311_PWM_T EJ2311_PWM_M_ = RT_MODEL_EJ2311_PWM_T();
RT_MODEL_EJ2311_PWM_T *const EJ2311_PWM_M = &EJ2311_PWM_M_;

// Model step function
void EJ2311_PWM_step(void)
{
  real_T rtb_Product_idx_0;
  real_T rtb_Product_idx_1;
  real_T rtb_Product_idx_2;
  real32_T SA_fs_mag;
  real32_T SB_fs_mag;
  real32_T SC_fs_mag;
  real32_T x_tmp;
  real32_T x_tmp_0;
  real32_T x_tmp_1;

  // S-Function (PROBE): '<S34>/S-Function'
  Va_ref = EJ2311_PWM_B.DataTypeConversion;

  // Product: '<S1>/Product' incorporates:
  //   Constant: '<S1>/Constant'
  //   Constant: '<S1>/Constant2'
  //   DataTypeConversion: '<S3>/Data Type Conversion'
  //   Delay: '<S3>/Delay'
  //   Sum: '<S1>/Sum'
  //   Sum: '<S1>/Sum1'
  //   Trigonometry: '<S1>/Trigonometric Function'

  rtb_Product_idx_0 = EJ2311_PWM_P.Constant2_Value * static_cast<real32_T>(sin(
    static_cast<real_T>(static_cast<real32_T>(EJ2311_PWM_DW.Delay_DSTATE))));
  rtb_Product_idx_1 = static_cast<real32_T>(sin(static_cast<real_T>(static_cast<
    real32_T>(EJ2311_PWM_DW.Delay_DSTATE) - EJ2311_PWM_P.Constant_Value))) *
    EJ2311_PWM_P.Constant2_Value;
  rtb_Product_idx_2 = static_cast<real32_T>(sin(static_cast<real_T>
    (static_cast<real32_T>(EJ2311_PWM_DW.Delay_DSTATE) +
     EJ2311_PWM_P.Constant_Value))) * EJ2311_PWM_P.Constant2_Value;

  // DataTypeConversion: '<S34>/Data Type Conversion' incorporates:
  //   Gain: '<S1>/Vdc//2'

  EJ2311_PWM_B.DataTypeConversion = static_cast<real32_T>(EJ2311_PWM_P.Vdc2_Gain
    * rtb_Product_idx_0);

  // S-Function (PROBE): '<S36>/S-Function'
  Vb_ref = EJ2311_PWM_B.DataTypeConversion_g;

  // DataTypeConversion: '<S36>/Data Type Conversion' incorporates:
  //   Gain: '<S1>/Vdc//2'

  EJ2311_PWM_B.DataTypeConversion_g = static_cast<real32_T>
    (EJ2311_PWM_P.Vdc2_Gain * rtb_Product_idx_1);

  // S-Function (PROBE): '<S38>/S-Function'
  Vc_ref = EJ2311_PWM_B.DataTypeConversion_p;

  // DataTypeConversion: '<S38>/Data Type Conversion' incorporates:
  //   Gain: '<S1>/Vdc//2'

  EJ2311_PWM_B.DataTypeConversion_p = static_cast<real32_T>
    (EJ2311_PWM_P.Vdc2_Gain * rtb_Product_idx_2);

  // S-Function (PROBE): '<S40>/S-Function'
  d_a = EJ2311_PWM_B.DataTypeConversion_m;

  // Sum: '<S1>/Sum2' incorporates:
  //   Constant: '<S1>/Constant1'
  //   Gain: '<S1>/Gain'

  rtb_Product_idx_0 = EJ2311_PWM_P.Gain_Gain * rtb_Product_idx_0 +
    EJ2311_PWM_P.Constant1_Value;
  rtb_Product_idx_1 = EJ2311_PWM_P.Gain_Gain * rtb_Product_idx_1 +
    EJ2311_PWM_P.Constant1_Value;
  rtb_Product_idx_2 = EJ2311_PWM_P.Gain_Gain * rtb_Product_idx_2 +
    EJ2311_PWM_P.Constant1_Value;

  // DataTypeConversion: '<S40>/Data Type Conversion'
  EJ2311_PWM_B.DataTypeConversion_m = static_cast<real32_T>(rtb_Product_idx_0);

  // S-Function (PROBE): '<S42>/S-Function'
  d_b = EJ2311_PWM_B.DataTypeConversion_b;

  // DataTypeConversion: '<S42>/Data Type Conversion'
  EJ2311_PWM_B.DataTypeConversion_b = static_cast<real32_T>(rtb_Product_idx_1);

  // S-Function (PROBE): '<S44>/S-Function'
  d_c = EJ2311_PWM_B.DataTypeConversion_i;

  // DataTypeConversion: '<S44>/Data Type Conversion'
  EJ2311_PWM_B.DataTypeConversion_i = static_cast<real32_T>(rtb_Product_idx_2);

  // If: '<S3>/If' incorporates:
  //   Delay: '<S3>/Delay'

  if (EJ2311_PWM_DW.Delay_DSTATE > 3.1415926535897931) {
    // DataStoreRead: '<S3>/Data Store Read' incorporates:
    //   Constant: '<S3>/Constant'
    //   SampleTimeMath: '<S3>/Weighted Sample Time'
    //   Sum: '<S3>/Add'
    //
    //  About '<S3>/Weighted Sample Time':
    //   y = u + K where K = ( w * Ts )

    EJ2311_PWM_DW.Delay_DSTATE = (EJ2311_PWM_DW.Delay_DSTATE +
      EJ2311_PWM_P.WeightedSampleTime_WtEt) - EJ2311_PWM_P.Constant_Value_c;
  } else {
    // DataStoreRead: '<S3>/Data Store Read' incorporates:
    //   SampleTimeMath: '<S3>/Weighted Sample Time'
    //
    //  About '<S3>/Weighted Sample Time':
    //   y = u + K where K = ( w * Ts )

    EJ2311_PWM_DW.Delay_DSTATE += EJ2311_PWM_P.WeightedSampleTime_WtEt;
  }

  // End of If: '<S3>/If'

  // S-Function (TUNABLE_PARAM): '<S46>/S-Function'
  EJ2311_PWM_B.SFunction = p;

  // Gain: '<S1>/Gain1'
  EJ2311_PWM_B.Saturation = EJ2311_PWM_P.Gain1_Gain * EJ2311_PWM_B.SFunction;

  // Saturate: '<S21>/Saturation'
  if (EJ2311_PWM_B.Saturation > EJ2311_PWM_P.Saturation_UpperSat) {
    // Gain: '<S1>/Gain1' incorporates:
    //   Saturate: '<S21>/Saturation'

    EJ2311_PWM_B.Saturation = EJ2311_PWM_P.Saturation_UpperSat;
  } else if (EJ2311_PWM_B.Saturation < EJ2311_PWM_P.Saturation_LowerSat) {
    // Gain: '<S1>/Gain1' incorporates:
    //   Saturate: '<S21>/Saturation'

    EJ2311_PWM_B.Saturation = EJ2311_PWM_P.Saturation_LowerSat;
  }

  // End of Saturate: '<S21>/Saturation'

  // S-Function (CLK): '<S21>/CLK1'
  Clock_SetFrequency((tClock) 1, EJ2311_PWM_B.Saturation);

  // MATLAB Function: '<S1>/MATLAB Function'
  // MATLAB Function 'Closed_loop_control/MATLAB Function': '<S6>:1'
  // '<S6>:1:4'
  // '<S6>:1:5'
  // '<S6>:1:6'
  // '<S6>:1:8'
  SA_fs_mag = static_cast<real32_T>(fabs(static_cast<real_T>
    (static_cast<real32_T>(sin(static_cast<real_T>(3.14159274F *
    static_cast<real32_T>(rtb_Product_idx_0)))) * 0.636619747F)));

  // '<S6>:1:9'
  SB_fs_mag = static_cast<real32_T>(fabs(static_cast<real_T>
    (static_cast<real32_T>(sin(static_cast<real_T>(3.14159274F *
    static_cast<real32_T>(rtb_Product_idx_1)))) * 0.636619747F)));

  // '<S6>:1:10'
  SC_fs_mag = static_cast<real32_T>(fabs(static_cast<real_T>
    (static_cast<real32_T>(sin(static_cast<real_T>(3.14159274F *
    static_cast<real32_T>(rtb_Product_idx_2)))) * 0.636619747F)));

  // '<S6>:1:12'
  if ((static_cast<real32_T>(fabs(static_cast<real_T>(SA_fs_mag - SB_fs_mag))) <=
       SC_fs_mag) && (SC_fs_mag <= SA_fs_mag + SB_fs_mag)) {
    // '<S6>:1:14'
    // '<S6>:1:17'
    // '<S6>:1:18'
    // '<S6>:1:20'
    x_tmp = SA_fs_mag * SA_fs_mag;
    x_tmp_0 = SC_fs_mag * SC_fs_mag;
    x_tmp_1 = SB_fs_mag * SB_fs_mag;
    SB_fs_mag = 180.0F - static_cast<real32_T>(acos(static_cast<real_T>(((x_tmp
      + x_tmp_1) - x_tmp_0) / (2.0F * SA_fs_mag * SB_fs_mag)))) * 57.2957802F;

    // '<S6>:1:21'
    SA_fs_mag = 360.0F - (180.0F - static_cast<real32_T>(acos(static_cast<real_T>
      (((x_tmp + x_tmp_0) - x_tmp_1) / (2.0F * SA_fs_mag * SC_fs_mag)))) *
                          57.2957802F);
  } else if ((SA_fs_mag >= SB_fs_mag) && (SA_fs_mag >= SC_fs_mag)) {
    // '<S6>:1:23'
    // '<S6>:1:24'
    SB_fs_mag = 180.0F;

    // '<S6>:1:25'
    SA_fs_mag = 180.0F;
  } else if ((SB_fs_mag >= SA_fs_mag) && (SB_fs_mag >= SC_fs_mag)) {
    // '<S6>:1:26'
    // '<S6>:1:27'
    SB_fs_mag = 180.0F;

    // '<S6>:1:28'
    SA_fs_mag = 180.0F;
  } else if ((SC_fs_mag >= SA_fs_mag) && (SC_fs_mag >= SB_fs_mag)) {
    // '<S6>:1:29'
    // '<S6>:1:30'
    SB_fs_mag = 0.0F;

    // '<S6>:1:31'
    SA_fs_mag = 180.0F;
  } else {
    // '<S6>:1:33'
    SB_fs_mag = 0.0F;

    // '<S6>:1:34'
    SA_fs_mag = 0.0F;
  }

  // DataTypeConversion: '<S7>/Data Type Conversion1' incorporates:
  //   DataTypeConversion: '<S40>/Data Type Conversion'

  // '<S6>:1:44'
  // '<S6>:1:45'
  EJ2311_PWM_B.DataTypeConversion1 = static_cast<real32_T>(rtb_Product_idx_0);

  // Switch: '<S1>/Switch1' incorporates:
  //   Constant: '<S1>/Constant3'

  if (EJ2311_PWM_P.Constant3_Value > EJ2311_PWM_P.Switch1_Threshold) {
    // DataTypeConversion: '<S7>/Data Type Conversion2' incorporates:
    //   MATLAB Function: '<S1>/MATLAB Function'

    EJ2311_PWM_B.DataTypeConversion2 = 0.0F;
  } else {
    // DataTypeConversion: '<S7>/Data Type Conversion2' incorporates:
    //   Constant: '<S1>/Zero Phase Shift'

    EJ2311_PWM_B.DataTypeConversion2 = static_cast<real32_T>
      (EJ2311_PWM_P.ZeroPhaseShift_Value);
  }

  // End of Switch: '<S1>/Switch1'

  // S-Function (TUNABLE_PARAM): '<S48>/S-Function'
  EJ2311_PWM_B.SFunction_c = activate_pwm;

  // Outputs for Atomic SubSystem: '<S27>/generation'
  // S-Function (CB_PWM): '<S28>/PWM' incorporates:
  //   Constant: '<S21>/clk_id'

  if (EJ2311_PWM_B.SFunction_c > 0.0) {
    CbPwm_Activate((tPwmOutput) 0, 0);
  } else {
    CbPwm_Deactivate((tPwmOutput) 0, 0);
  }

  CbPwm_SetDutyCycle((tPwmOutput) 0, EJ2311_PWM_B.DataTypeConversion1, 0);
  CbPwm_SetPhase((tPwmOutput) 0, EJ2311_PWM_B.DataTypeConversion2, 0);

  // End of Outputs for SubSystem: '<S27>/generation'

  // DataTypeConversion: '<S8>/Data Type Conversion1' incorporates:
  //   DataTypeConversion: '<S42>/Data Type Conversion'

  EJ2311_PWM_B.DataTypeConversion1_k = static_cast<real32_T>(rtb_Product_idx_1);

  // Switch: '<S1>/Switch2' incorporates:
  //   Constant: '<S1>/Constant3'

  if (EJ2311_PWM_P.Constant3_Value > EJ2311_PWM_P.Switch2_Threshold) {
    // DataTypeConversion: '<S8>/Data Type Conversion2' incorporates:
    //   MATLAB Function: '<S1>/MATLAB Function'

    EJ2311_PWM_B.DataTypeConversion2_l = SB_fs_mag / 360.0F;
  } else {
    // DataTypeConversion: '<S8>/Data Type Conversion2' incorporates:
    //   Constant: '<S1>/Zero Phase Shift'

    EJ2311_PWM_B.DataTypeConversion2_l = static_cast<real32_T>
      (EJ2311_PWM_P.ZeroPhaseShift_Value);
  }

  // End of Switch: '<S1>/Switch2'

  // Outputs for Atomic SubSystem: '<S29>/generation'
  // S-Function (CB_PWM): '<S30>/PWM' incorporates:
  //   Constant: '<S21>/clk_id'

  if (EJ2311_PWM_B.SFunction_c > 0.0) {
    CbPwm_Activate((tPwmOutput) 2, 0);
  } else {
    CbPwm_Deactivate((tPwmOutput) 2, 0);
  }

  CbPwm_SetDutyCycle((tPwmOutput) 2, EJ2311_PWM_B.DataTypeConversion1_k, 0);
  CbPwm_SetPhase((tPwmOutput) 2, EJ2311_PWM_B.DataTypeConversion2_l, 0);

  // End of Outputs for SubSystem: '<S29>/generation'

  // DataTypeConversion: '<S9>/Data Type Conversion1' incorporates:
  //   DataTypeConversion: '<S44>/Data Type Conversion'

  EJ2311_PWM_B.DataTypeConversion1_k0 = static_cast<real32_T>(rtb_Product_idx_2);

  // Switch: '<S1>/Switch3' incorporates:
  //   Constant: '<S1>/Constant3'

  if (EJ2311_PWM_P.Constant3_Value > EJ2311_PWM_P.Switch3_Threshold) {
    // DataTypeConversion: '<S9>/Data Type Conversion2' incorporates:
    //   MATLAB Function: '<S1>/MATLAB Function'

    EJ2311_PWM_B.DataTypeConversion2_g = SA_fs_mag / 360.0F;
  } else {
    // DataTypeConversion: '<S9>/Data Type Conversion2' incorporates:
    //   Constant: '<S1>/Zero Phase Shift'

    EJ2311_PWM_B.DataTypeConversion2_g = static_cast<real32_T>
      (EJ2311_PWM_P.ZeroPhaseShift_Value);
  }

  // End of Switch: '<S1>/Switch3'

  // Outputs for Atomic SubSystem: '<S31>/generation'
  // S-Function (CB_PWM): '<S32>/PWM' incorporates:
  //   Constant: '<S21>/clk_id'

  if (EJ2311_PWM_B.SFunction_c > 0.0) {
    CbPwm_Activate((tPwmOutput) 4, 0);
  } else {
    CbPwm_Deactivate((tPwmOutput) 4, 0);
  }

  CbPwm_SetDutyCycle((tPwmOutput) 4, EJ2311_PWM_B.DataTypeConversion1_k0, 0);
  CbPwm_SetPhase((tPwmOutput) 4, EJ2311_PWM_B.DataTypeConversion2_g, 0);

  // End of Outputs for SubSystem: '<S31>/generation'
}

// Model initialize function
void EJ2311_PWM_initialize(void)
{
  // Registration code

  // initialize non-finites
  rt_InitInfAndNaN(sizeof(real_T));

  // non-finite (run-time) assignments
  EJ2311_PWM_P.SFunction_P4_h = rtMinusInfF;
  EJ2311_PWM_P.SFunction_P5_f = rtInfF;

  // Start for S-Function (IRQ): '<S24>/S-Function' incorporates:
  //   Constant: '<S26>/clk_id'

  ConfigureMainInterrupt(SimulinkInterrupt, (tClock) EJ2311_PWM_P.clk_id_Value,
    0.5F, 0U);
  Adc_AddSamplingEvent((EJ2311_PWM_P.SFunction_P2));
  ConfigureReadTriggerDelayInNs(2000U);

  // Start for S-Function (CLK): '<S26>/CLK1'
  Clock_SetFrequency((tClock) 0, 20000.0F);

  // Start for S-Function (PROBE): '<S34>/S-Function'
  ConfigureProbe(&Va_ref, 0);

  // Start for S-Function (PROBE): '<S36>/S-Function'
  ConfigureProbe(&Vb_ref, 0);

  // Start for S-Function (PROBE): '<S38>/S-Function'
  ConfigureProbe(&Vc_ref, 0);

  // Start for S-Function (PROBE): '<S40>/S-Function'
  ConfigureProbe(&d_a, 0);

  // Start for S-Function (PROBE): '<S42>/S-Function'
  ConfigureProbe(&d_b, 0);

  // Start for S-Function (PROBE): '<S44>/S-Function'
  ConfigureProbe(&d_c, 0);

  // Start for S-Function (TUNABLE_PARAM): '<S46>/S-Function'
  p = 9.0F;                            // Tunable parameter initialization
  ConfigureTunable(&p, 0, 0, 3.0F, 91.0F);

  // Start for S-Function (CLK): '<S21>/CLK1'
  Clock_SetFrequency((tClock) 1, 1950.0F);
  Clock_ConfigureAsRealTimeTunable((tClock) 1);

  // Start for S-Function (TUNABLE_PARAM): '<S48>/S-Function'
  activate_pwm = 1.0F;                 // Tunable parameter initialization
  ConfigureTunable(&activate_pwm, 0, 0);

  // Start for Atomic SubSystem: '<S27>/generation'

  // Start for S-Function (CB_PWM): '<S28>/PWM' incorporates:
  //   Constant: '<S21>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 0, (tClock) EJ2311_PWM_P.clk_id_Value_a, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 0, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 0, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 0, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 0, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 0, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 0, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 0, 0);

  // End of Start for SubSystem: '<S27>/generation'

  // Start for Atomic SubSystem: '<S29>/generation'

  // Start for S-Function (CB_PWM): '<S30>/PWM' incorporates:
  //   Constant: '<S21>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 2, (tClock) EJ2311_PWM_P.clk_id_Value_a, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 2, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 2, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 2, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 2, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 2, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 2, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 2, 0);

  // End of Start for SubSystem: '<S29>/generation'

  // Start for Atomic SubSystem: '<S31>/generation'

  // Start for S-Function (CB_PWM): '<S32>/PWM' incorporates:
  //   Constant: '<S21>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 4, (tClock) EJ2311_PWM_P.clk_id_Value_a, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 4, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 4, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 4, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 4, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 4, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 4, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 4, 0);

  // End of Start for SubSystem: '<S31>/generation'

  // InitializeConditions for Delay: '<S3>/Delay'
  EJ2311_PWM_DW.Delay_DSTATE = EJ2311_PWM_P.Delay_InitialCondition;
}

// Model terminate function
void EJ2311_PWM_terminate(void)
{
  // (no terminate code required)
}

//
// End of automatically generated code
// Copyright imperix ltd. Switzerland 2021
// [EOF]
//

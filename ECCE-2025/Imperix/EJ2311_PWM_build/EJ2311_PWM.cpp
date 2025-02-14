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
// Model version                  : 16.3
// Simulink Coder version         : 23.2 (R2023b) 01-Aug-2023
// C/C++ source code generated on : Wed Feb 12 15:00:19 2025
//
#include "EJ2311_PWM.h"
#include <math.h>
#include "rtwtypes.h"
#include "EJ2311_PWM_private.h"

extern "C"
{

#include "rt_nonfinite.h"

}

real32_T Ia;                           // Probe
real32_T Ib;                           // Probe
real32_T Ic;                           // Probe
real32_T Vdc;                          // Probe
int16_T* ix_raw_adc_ptr_0_0;
int16_T* ix_raw_adc_ptr_1_0;
int16_T* ix_raw_adc_ptr_2_0;
int16_T* ix_raw_adc_ptr_3_0;
real32_T Va_ref;                       // Probe
real32_T Vb_ref;                       // Probe
real32_T Vc_ref;                       // Probe
real32_T d_a;                          // Probe
real32_T d_b;                          // Probe
real32_T d_c;                          // Probe
real32_T p;                            // Tunable parameter
real32_T M;                            // Tunable parameter
real32_T third_harmonic;               // Tunable parameter
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
  real_T rtb_Delay;
  real32_T rtb_Product1;

  // S-Function (PROBE): '<S51>/S-Function'
  Ia = EJ2311_PWM_B.ADC;

  // S-Function (PROBE): '<S53>/S-Function'
  Ib = EJ2311_PWM_B.ADC_f;

  // S-Function (PROBE): '<S55>/S-Function'
  Ic = EJ2311_PWM_B.ADC_d;

  // S-Function (PROBE): '<S63>/S-Function'
  Vdc = EJ2311_PWM_B.ADC_k;

  // S-Function (ADC): '<S28>/ADC'
  EJ2311_PWM_B.ADC = (float)(*ix_raw_adc_ptr_0_0) * 0.0015259F + -0.045F;

  // S-Function (ADC): '<S30>/ADC'
  EJ2311_PWM_B.ADC_f = (float)(*ix_raw_adc_ptr_1_0) * 0.0015259F + -0.04F;

  // S-Function (ADC): '<S32>/ADC'
  EJ2311_PWM_B.ADC_d = (float)(*ix_raw_adc_ptr_2_0) * 0.0015259F + -0.052F;

  // S-Function (ADC): '<S34>/ADC'
  EJ2311_PWM_B.ADC_k = (float)(*ix_raw_adc_ptr_3_0) * 0.030579F + -0.35F;

  // S-Function (PROBE): '<S57>/S-Function'
  Va_ref = EJ2311_PWM_B.Vdc2[0];

  // S-Function (PROBE): '<S59>/S-Function'
  Vb_ref = EJ2311_PWM_B.Vdc2[1];

  // S-Function (PROBE): '<S61>/S-Function'
  Vc_ref = EJ2311_PWM_B.Vdc2[2];

  // S-Function (PROBE): '<S65>/S-Function'
  d_a = EJ2311_PWM_B.Dutycycles[0];

  // S-Function (PROBE): '<S67>/S-Function'
  d_b = EJ2311_PWM_B.Dutycycles[1];

  // S-Function (PROBE): '<S69>/S-Function'
  d_c = EJ2311_PWM_B.Dutycycles[2];

  // Delay: '<S7>/Delay'
  rtb_Delay = EJ2311_PWM_DW.Delay_DSTATE;

  // If: '<S7>/If' incorporates:
  //   Delay: '<S7>/Delay'

  if (EJ2311_PWM_DW.Delay_DSTATE > 3.1415926535897931) {
    // DataStoreRead: '<S7>/Data Store Read' incorporates:
    //   Constant: '<S7>/Constant'
    //   SampleTimeMath: '<S7>/Weighted Sample Time'
    //   Sum: '<S7>/Add'
    //
    //  About '<S7>/Weighted Sample Time':
    //   y = u + K where K = ( w * Ts )

    EJ2311_PWM_DW.Delay_DSTATE = (EJ2311_PWM_DW.Delay_DSTATE +
      EJ2311_PWM_P.WeightedSampleTime_WtEt) - EJ2311_PWM_P.Constant_Value;
  } else {
    // DataStoreRead: '<S7>/Data Store Read' incorporates:
    //   SampleTimeMath: '<S7>/Weighted Sample Time'
    //
    //  About '<S7>/Weighted Sample Time':
    //   y = u + K where K = ( w * Ts )

    EJ2311_PWM_DW.Delay_DSTATE += EJ2311_PWM_P.WeightedSampleTime_WtEt;
  }

  // End of If: '<S7>/If'

  // S-Function (TUNABLE_PARAM): '<S73>/S-Function'
  EJ2311_PWM_B.SFunction = p;

  // Gain: '<S1>/Gain1'
  EJ2311_PWM_B.Saturation = EJ2311_PWM_P.Gain1_Gain * EJ2311_PWM_B.SFunction;

  // Saturate: '<S38>/Saturation'
  if (EJ2311_PWM_B.Saturation > EJ2311_PWM_P.Saturation_UpperSat) {
    // Gain: '<S1>/Gain1' incorporates:
    //   Saturate: '<S38>/Saturation'

    EJ2311_PWM_B.Saturation = EJ2311_PWM_P.Saturation_UpperSat;
  } else if (EJ2311_PWM_B.Saturation < EJ2311_PWM_P.Saturation_LowerSat) {
    // Gain: '<S1>/Gain1' incorporates:
    //   Saturate: '<S38>/Saturation'

    EJ2311_PWM_B.Saturation = EJ2311_PWM_P.Saturation_LowerSat;
  }

  // End of Saturate: '<S38>/Saturation'

  // S-Function (CLK): '<S38>/CLK1'
  Clock_SetFrequency((tClock) 1, EJ2311_PWM_B.Saturation);

  // S-Function (TUNABLE_PARAM): '<S71>/S-Function'
  EJ2311_PWM_B.SFunction_o = M;

  // S-Function (TUNABLE_PARAM): '<S75>/S-Function'
  EJ2311_PWM_B.SFunction_d = third_harmonic;

  // Switch: '<S1>/Switch' incorporates:
  //   Constant: '<S1>/Constant'
  //   DataTypeConversion: '<S7>/Data Type Conversion'
  //   Product: '<S1>/Product'
  //   Sum: '<S1>/Sum'
  //   Sum: '<S1>/Sum1'
  //   Sum: '<S1>/Sum3'
  //   Trigonometry: '<S1>/Trigonometric Function'

  if (EJ2311_PWM_B.SFunction_d > EJ2311_PWM_P.Switch_Threshold) {
    // Product: '<S1>/Product1' incorporates:
    //   DataTypeConversion: '<S7>/Data Type Conversion'
    //   Gain: '<S1>/Gain2'
    //   Gain: '<S1>/Gain3'
    //   Trigonometry: '<S1>/Trigonometric Function1'

    rtb_Product1 = EJ2311_PWM_P.Gain3_Gain * EJ2311_PWM_B.SFunction_o *
      static_cast<real32_T>(sin(static_cast<real_T>(EJ2311_PWM_P.Gain2_Gain *
      static_cast<real32_T>(rtb_Delay))));
    EJ2311_PWM_B.Vdc2[0] = EJ2311_PWM_B.SFunction_o * static_cast<real32_T>(sin(
      static_cast<real_T>(static_cast<real32_T>(rtb_Delay)))) + rtb_Product1;
    EJ2311_PWM_B.Vdc2[1] = static_cast<real32_T>(sin(static_cast<real_T>(
      static_cast<real32_T>(rtb_Delay) - EJ2311_PWM_P.Constant_Value_j))) *
      EJ2311_PWM_B.SFunction_o + rtb_Product1;
    EJ2311_PWM_B.Vdc2[2] = static_cast<real32_T>(sin(static_cast<real_T>(
      static_cast<real32_T>(rtb_Delay) + EJ2311_PWM_P.Constant_Value_j))) *
      EJ2311_PWM_B.SFunction_o + rtb_Product1;
  } else {
    EJ2311_PWM_B.Vdc2[0] = EJ2311_PWM_B.SFunction_o * static_cast<real32_T>(sin(
      static_cast<real_T>(static_cast<real32_T>(rtb_Delay))));
    EJ2311_PWM_B.Vdc2[1] = static_cast<real32_T>(sin(static_cast<real_T>(
      static_cast<real32_T>(rtb_Delay) - EJ2311_PWM_P.Constant_Value_j))) *
      EJ2311_PWM_B.SFunction_o;
    EJ2311_PWM_B.Vdc2[2] = static_cast<real32_T>(sin(static_cast<real_T>(
      static_cast<real32_T>(rtb_Delay) + EJ2311_PWM_P.Constant_Value_j))) *
      EJ2311_PWM_B.SFunction_o;
  }

  // End of Switch: '<S1>/Switch'

  // DataTypeConversion: '<S10>/Data Type Conversion2' incorporates:
  //   Constant: '<S10>/phase'

  EJ2311_PWM_B.DataTypeConversion2 = static_cast<real32_T>
    (EJ2311_PWM_P.phase_Value);

  // Sum: '<S1>/Sum2' incorporates:
  //   Constant: '<S1>/Constant1'
  //   Gain: '<S1>/Gain'

  EJ2311_PWM_B.Dutycycles[0] = EJ2311_PWM_P.Gain_Gain * EJ2311_PWM_B.Vdc2[0] +
    EJ2311_PWM_P.Constant1_Value;
  EJ2311_PWM_B.Dutycycles[1] = EJ2311_PWM_P.Gain_Gain * EJ2311_PWM_B.Vdc2[1] +
    EJ2311_PWM_P.Constant1_Value;
  EJ2311_PWM_B.Dutycycles[2] = EJ2311_PWM_P.Gain_Gain * EJ2311_PWM_B.Vdc2[2] +
    EJ2311_PWM_P.Constant1_Value;

  // S-Function (TUNABLE_PARAM): '<S77>/S-Function'
  EJ2311_PWM_B.SFunction_c = activate_pwm;

  // Outputs for Atomic SubSystem: '<S44>/generation'
  // S-Function (CB_PWM): '<S45>/PWM' incorporates:
  //   Constant: '<S38>/clk_id'

  if (EJ2311_PWM_B.SFunction_c > 0.0) {
    CbPwm_Activate((tPwmOutput) 0, 0);
  } else {
    CbPwm_Deactivate((tPwmOutput) 0, 0);
  }

  CbPwm_SetDutyCycle((tPwmOutput) 0, EJ2311_PWM_B.Dutycycles[0], 0);

  // End of Outputs for SubSystem: '<S44>/generation'

  // DataTypeConversion: '<S11>/Data Type Conversion2' incorporates:
  //   Constant: '<S11>/phase'

  EJ2311_PWM_B.DataTypeConversion2_l = static_cast<real32_T>
    (EJ2311_PWM_P.phase_Value_n);

  // Outputs for Atomic SubSystem: '<S46>/generation'
  // S-Function (CB_PWM): '<S47>/PWM' incorporates:
  //   Constant: '<S38>/clk_id'

  if (EJ2311_PWM_B.SFunction_c > 0.0) {
    CbPwm_Activate((tPwmOutput) 2, 0);
  } else {
    CbPwm_Deactivate((tPwmOutput) 2, 0);
  }

  CbPwm_SetDutyCycle((tPwmOutput) 2, EJ2311_PWM_B.Dutycycles[1], 0);

  // End of Outputs for SubSystem: '<S46>/generation'

  // DataTypeConversion: '<S12>/Data Type Conversion2' incorporates:
  //   Constant: '<S12>/phase'

  EJ2311_PWM_B.DataTypeConversion2_g = static_cast<real32_T>
    (EJ2311_PWM_P.phase_Value_c);

  // Outputs for Atomic SubSystem: '<S48>/generation'
  // S-Function (CB_PWM): '<S49>/PWM' incorporates:
  //   Constant: '<S38>/clk_id'

  if (EJ2311_PWM_B.SFunction_c > 0.0) {
    CbPwm_Activate((tPwmOutput) 4, 0);
  } else {
    CbPwm_Deactivate((tPwmOutput) 4, 0);
  }

  CbPwm_SetDutyCycle((tPwmOutput) 4, EJ2311_PWM_B.Dutycycles[2], 0);

  // End of Outputs for SubSystem: '<S48>/generation'

  // Gain: '<S1>/Vdc//2' incorporates:
  //   Switch: '<S1>/Switch'

  EJ2311_PWM_B.Vdc2[0] *= EJ2311_PWM_P.Vdc2_Gain;
  EJ2311_PWM_B.Vdc2[1] *= EJ2311_PWM_P.Vdc2_Gain;
  EJ2311_PWM_B.Vdc2[2] *= EJ2311_PWM_P.Vdc2_Gain;
}

// Model initialize function
void EJ2311_PWM_initialize(void)
{
  // Registration code

  // initialize non-finites
  rt_InitInfAndNaN(sizeof(real_T));

  // non-finite (run-time) assignments
  EJ2311_PWM_P.SFunction_P4_pz = rtMinusInfF;
  EJ2311_PWM_P.SFunction_P5_g = rtInfF;
  EJ2311_PWM_P.SFunction_P4_h = rtMinusInfF;
  EJ2311_PWM_P.SFunction_P5_f = rtInfF;

  // Start for S-Function (PROBE): '<S51>/S-Function'
  ConfigureProbe(&Ia, 0);

  // Start for S-Function (PROBE): '<S53>/S-Function'
  ConfigureProbe(&Ib, 0);

  // Start for S-Function (PROBE): '<S55>/S-Function'
  ConfigureProbe(&Ic, 0);

  // Start for S-Function (PROBE): '<S63>/S-Function'
  ConfigureProbe(&Vdc, 0);

  // Start for S-Function (ADC): '<S28>/ADC'
  Adc_ConfigureInput(0, 0.0015259F, -0.045F, 0);
  Adc_GetPointer(0, 0, &ix_raw_adc_ptr_0_0);

  // Start for S-Function (ADC): '<S30>/ADC'
  Adc_ConfigureInput(1, 0.0015259F, -0.04F, 0);
  Adc_GetPointer(1, 0, &ix_raw_adc_ptr_1_0);

  // Start for S-Function (ADC): '<S32>/ADC'
  Adc_ConfigureInput(2, 0.0015259F, -0.052F, 0);
  Adc_GetPointer(2, 0, &ix_raw_adc_ptr_2_0);

  // Start for S-Function (ADC): '<S34>/ADC'
  Adc_ConfigureInput(3, 0.030579F, -0.35F, 0);
  Adc_GetPointer(3, 0, &ix_raw_adc_ptr_3_0);

  // Start for S-Function (IRQ): '<S41>/S-Function' incorporates:
  //   Constant: '<S43>/clk_id'

  ConfigureMainInterrupt(SimulinkInterrupt, (tClock) EJ2311_PWM_P.clk_id_Value,
    0.5F, 0U);
  Adc_AddSamplingEvent((EJ2311_PWM_P.SFunction_P2));
  ConfigureReadTriggerDelayInNs(2000U);

  // Start for S-Function (CLK): '<S43>/CLK1'
  Clock_SetFrequency((tClock) 0, 20000.0F);

  // Start for S-Function (PROBE): '<S57>/S-Function'
  ConfigureProbe(&Va_ref, 0);

  // Start for S-Function (PROBE): '<S59>/S-Function'
  ConfigureProbe(&Vb_ref, 0);

  // Start for S-Function (PROBE): '<S61>/S-Function'
  ConfigureProbe(&Vc_ref, 0);

  // Start for S-Function (PROBE): '<S65>/S-Function'
  ConfigureProbe(&d_a, 0);

  // Start for S-Function (PROBE): '<S67>/S-Function'
  ConfigureProbe(&d_b, 0);

  // Start for S-Function (PROBE): '<S69>/S-Function'
  ConfigureProbe(&d_c, 0);

  // Start for S-Function (TUNABLE_PARAM): '<S73>/S-Function'
  p = 9.0F;                            // Tunable parameter initialization
  ConfigureTunable(&p, 0, 0, 3.0F, 91.0F);

  // Start for S-Function (CLK): '<S38>/CLK1'
  Clock_SetFrequency((tClock) 1, 1950.0F);
  Clock_ConfigureAsRealTimeTunable((tClock) 1);

  // Start for S-Function (TUNABLE_PARAM): '<S71>/S-Function'
  M = 0.8F;                            // Tunable parameter initialization
  ConfigureTunable(&M, 0, 0, 0.1F, 2.0F);

  // Start for S-Function (TUNABLE_PARAM): '<S75>/S-Function'
  third_harmonic = 0.0F;               // Tunable parameter initialization
  ConfigureTunable(&third_harmonic, 0, 0);

  // Start for S-Function (TUNABLE_PARAM): '<S77>/S-Function'
  activate_pwm = 0.0F;                 // Tunable parameter initialization
  ConfigureTunable(&activate_pwm, 0, 0);

  // Start for Atomic SubSystem: '<S44>/generation'

  // Start for S-Function (CB_PWM): '<S45>/PWM' incorporates:
  //   Constant: '<S38>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 0, (tClock) EJ2311_PWM_P.clk_id_Value_a, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 0, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 0, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 0, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 0, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 0, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 0, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 0, 0);

  // End of Start for SubSystem: '<S44>/generation'

  // Start for Atomic SubSystem: '<S46>/generation'

  // Start for S-Function (CB_PWM): '<S47>/PWM' incorporates:
  //   Constant: '<S38>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 2, (tClock) EJ2311_PWM_P.clk_id_Value_a, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 2, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 2, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 2, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 2, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 2, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 2, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 2, 0);

  // End of Start for SubSystem: '<S46>/generation'

  // Start for Atomic SubSystem: '<S48>/generation'

  // Start for S-Function (CB_PWM): '<S49>/PWM' incorporates:
  //   Constant: '<S38>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 4, (tClock) EJ2311_PWM_P.clk_id_Value_a, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 4, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 4, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 4, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 4, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 4, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 4, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 4, 0);

  // End of Start for SubSystem: '<S48>/generation'

  // InitializeConditions for Delay: '<S7>/Delay'
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

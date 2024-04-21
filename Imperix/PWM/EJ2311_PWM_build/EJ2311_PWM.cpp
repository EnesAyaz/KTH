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
// C/C++ source code generated on : Wed Feb 14 15:50:32 2024
//
#include "EJ2311_PWM.h"
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
real32_T fs;                           // Tunable parameter
real32_T dA;                           // Tunable parameter
real32_T phA;                          // Tunable parameter
real32_T activate_pwm;                 // Tunable parameter
real32_T dB;                           // Tunable parameter
real32_T phB;                          // Tunable parameter
real32_T dC;                           // Tunable parameter
real32_T phC;                          // Tunable parameter

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
  // S-Function (PROBE): '<S46>/S-Function'
  Ia = EJ2311_PWM_B.ADC;

  // S-Function (PROBE): '<S48>/S-Function'
  Ib = EJ2311_PWM_B.ADC_f;

  // S-Function (PROBE): '<S50>/S-Function'
  Ic = EJ2311_PWM_B.ADC_d;

  // S-Function (PROBE): '<S52>/S-Function'
  Vdc = EJ2311_PWM_B.ADC_k;

  // S-Function (ADC): '<S25>/ADC'
  EJ2311_PWM_B.ADC = (float)(*ix_raw_adc_ptr_0_0) * 0.0015259F + -0.045F;

  // S-Function (ADC): '<S27>/ADC'
  EJ2311_PWM_B.ADC_f = (float)(*ix_raw_adc_ptr_1_0) * 0.0015259F + -0.04F;

  // S-Function (ADC): '<S29>/ADC'
  EJ2311_PWM_B.ADC_d = (float)(*ix_raw_adc_ptr_2_0) * 0.0015259F + -0.052F;

  // S-Function (ADC): '<S31>/ADC'
  EJ2311_PWM_B.ADC_k = (float)(*ix_raw_adc_ptr_3_0) * 0.030579F + -0.35F;

  // S-Function (TUNABLE_PARAM): '<S54>/S-Function'
  EJ2311_PWM_B.SFunction = fs;

  // Saturate: '<S33>/Saturation'
  if (EJ2311_PWM_B.SFunction > EJ2311_PWM_P.Saturation_UpperSat) {
    // Saturate: '<S33>/Saturation'
    EJ2311_PWM_B.Saturation = EJ2311_PWM_P.Saturation_UpperSat;
  } else if (EJ2311_PWM_B.SFunction < EJ2311_PWM_P.Saturation_LowerSat) {
    // Saturate: '<S33>/Saturation'
    EJ2311_PWM_B.Saturation = EJ2311_PWM_P.Saturation_LowerSat;
  } else {
    // Saturate: '<S33>/Saturation'
    EJ2311_PWM_B.Saturation = EJ2311_PWM_B.SFunction;
  }

  // End of Saturate: '<S33>/Saturation'

  // S-Function (CLK): '<S33>/CLK1'
  Clock_SetFrequency((tClock) 1, EJ2311_PWM_B.Saturation);

  // S-Function (TUNABLE_PARAM): '<S56>/S-Function'
  EJ2311_PWM_B.SFunction_n = dA;

  // S-Function (TUNABLE_PARAM): '<S60>/S-Function'
  EJ2311_PWM_B.SFunction_o = phA;

  // S-Function (TUNABLE_PARAM): '<S58>/S-Function'
  EJ2311_PWM_B.SFunction_c = activate_pwm;

  // Outputs for Atomic SubSystem: '<S39>/generation'
  // S-Function (CB_PWM): '<S40>/PWM' incorporates:
  //   Constant: '<S33>/clk_id'

  if (EJ2311_PWM_B.SFunction_c > 0.0) {
    CbPwm_Activate((tPwmOutput) 0, 0);
  } else {
    CbPwm_Deactivate((tPwmOutput) 0, 0);
  }

  CbPwm_SetDutyCycle((tPwmOutput) 0, EJ2311_PWM_B.SFunction_n, 0);
  CbPwm_SetPhase((tPwmOutput) 0, EJ2311_PWM_B.SFunction_o, 0);

  // End of Outputs for SubSystem: '<S39>/generation'

  // S-Function (TUNABLE_PARAM): '<S66>/S-Function'
  EJ2311_PWM_B.SFunction_m = dB;

  // S-Function (TUNABLE_PARAM): '<S62>/S-Function'
  EJ2311_PWM_B.SFunction_j = phB;

  // Outputs for Atomic SubSystem: '<S41>/generation'
  // S-Function (CB_PWM): '<S42>/PWM' incorporates:
  //   Constant: '<S33>/clk_id'

  if (EJ2311_PWM_B.SFunction_c > 0.0) {
    CbPwm_Activate((tPwmOutput) 2, 0);
  } else {
    CbPwm_Deactivate((tPwmOutput) 2, 0);
  }

  CbPwm_SetDutyCycle((tPwmOutput) 2, EJ2311_PWM_B.SFunction_m, 0);
  CbPwm_SetPhase((tPwmOutput) 2, EJ2311_PWM_B.SFunction_j, 0);

  // End of Outputs for SubSystem: '<S41>/generation'

  // S-Function (TUNABLE_PARAM): '<S68>/S-Function'
  EJ2311_PWM_B.SFunction_b = dC;

  // S-Function (TUNABLE_PARAM): '<S64>/S-Function'
  EJ2311_PWM_B.SFunction_mp = phC;

  // Outputs for Atomic SubSystem: '<S43>/generation'
  // S-Function (CB_PWM): '<S44>/PWM' incorporates:
  //   Constant: '<S33>/clk_id'

  if (EJ2311_PWM_B.SFunction_c > 0.0) {
    CbPwm_Activate((tPwmOutput) 4, 0);
  } else {
    CbPwm_Deactivate((tPwmOutput) 4, 0);
  }

  CbPwm_SetDutyCycle((tPwmOutput) 4, EJ2311_PWM_B.SFunction_b, 0);
  CbPwm_SetPhase((tPwmOutput) 4, EJ2311_PWM_B.SFunction_mp, 0);

  // End of Outputs for SubSystem: '<S43>/generation'
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

  // Start for S-Function (PROBE): '<S46>/S-Function'
  ConfigureProbe(&Ia, 0);

  // Start for S-Function (PROBE): '<S48>/S-Function'
  ConfigureProbe(&Ib, 0);

  // Start for S-Function (PROBE): '<S50>/S-Function'
  ConfigureProbe(&Ic, 0);

  // Start for S-Function (PROBE): '<S52>/S-Function'
  ConfigureProbe(&Vdc, 0);

  // Start for S-Function (ADC): '<S25>/ADC'
  Adc_ConfigureInput(0, 0.0015259F, -0.045F, 0);
  Adc_GetPointer(0, 0, &ix_raw_adc_ptr_0_0);

  // Start for S-Function (ADC): '<S27>/ADC'
  Adc_ConfigureInput(1, 0.0015259F, -0.04F, 0);
  Adc_GetPointer(1, 0, &ix_raw_adc_ptr_1_0);

  // Start for S-Function (ADC): '<S29>/ADC'
  Adc_ConfigureInput(2, 0.0015259F, -0.052F, 0);
  Adc_GetPointer(2, 0, &ix_raw_adc_ptr_2_0);

  // Start for S-Function (ADC): '<S31>/ADC'
  Adc_ConfigureInput(3, 0.030579F, -0.35F, 0);
  Adc_GetPointer(3, 0, &ix_raw_adc_ptr_3_0);

  // Start for S-Function (IRQ): '<S36>/S-Function' incorporates:
  //   Constant: '<S38>/clk_id'

  ConfigureMainInterrupt(SimulinkInterrupt, (tClock) EJ2311_PWM_P.clk_id_Value,
    0.5F, 0U);
  Adc_AddSamplingEvent((EJ2311_PWM_P.SFunction_P2));
  ConfigureReadTriggerDelayInNs(2000U);

  // Start for S-Function (CLK): '<S38>/CLK1'
  Clock_SetFrequency((tClock) 0, 20000.0F);

  // Start for S-Function (TUNABLE_PARAM): '<S54>/S-Function'
  fs = 500.0F;                         // Tunable parameter initialization
  ConfigureTunable(&fs, 0, 0, 3.0F, 91.0F);

  // Start for S-Function (CLK): '<S33>/CLK1'
  Clock_SetFrequency((tClock) 1, 1950.0F);
  Clock_ConfigureAsRealTimeTunable((tClock) 1);

  // Start for S-Function (TUNABLE_PARAM): '<S56>/S-Function'
  dA = 0.5F;                           // Tunable parameter initialization
  ConfigureTunable(&dA, 0, 0, 0.0F, 1.0F);

  // Start for S-Function (TUNABLE_PARAM): '<S60>/S-Function'
  phA = 0.0F;                          // Tunable parameter initialization
  ConfigureTunable(&phA, 0, 0, 0.0F, 1.0F);

  // Start for S-Function (TUNABLE_PARAM): '<S58>/S-Function'
  activate_pwm = 0.0F;                 // Tunable parameter initialization
  ConfigureTunable(&activate_pwm, 0, 0);

  // Start for Atomic SubSystem: '<S39>/generation'

  // Start for S-Function (CB_PWM): '<S40>/PWM' incorporates:
  //   Constant: '<S33>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 0, (tClock) EJ2311_PWM_P.clk_id_Value_a, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 0, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 0, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 0, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 0, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 0, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 0, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 0, 0);

  // End of Start for SubSystem: '<S39>/generation'

  // Start for S-Function (TUNABLE_PARAM): '<S66>/S-Function'
  dB = 0.25F;                          // Tunable parameter initialization
  ConfigureTunable(&dB, 0, 0, 0.0F, 1.0F);

  // Start for S-Function (TUNABLE_PARAM): '<S62>/S-Function'
  phB = 0.0F;                          // Tunable parameter initialization
  ConfigureTunable(&phB, 0, 0, 0.0F, 1.0F);

  // Start for Atomic SubSystem: '<S41>/generation'

  // Start for S-Function (CB_PWM): '<S42>/PWM' incorporates:
  //   Constant: '<S33>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 2, (tClock) EJ2311_PWM_P.clk_id_Value_a, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 2, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 2, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 2, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 2, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 2, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 2, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 2, 0);

  // End of Start for SubSystem: '<S41>/generation'

  // Start for S-Function (TUNABLE_PARAM): '<S68>/S-Function'
  dC = 0.25F;                          // Tunable parameter initialization
  ConfigureTunable(&dC, 0, 0, 0.0F, 1.0F);

  // Start for S-Function (TUNABLE_PARAM): '<S64>/S-Function'
  phC = 0.0F;                          // Tunable parameter initialization
  ConfigureTunable(&phC, 0, 0, 0.0F, 1.0F);

  // Start for Atomic SubSystem: '<S43>/generation'

  // Start for S-Function (CB_PWM): '<S44>/PWM' incorporates:
  //   Constant: '<S33>/clk_id'

  CbPwm_ConfigureClock((tPwmOutput) 4, (tClock) EJ2311_PWM_P.clk_id_Value_a, 0);
  CbPwm_ConfigureOutputMode((tPwmOutput) 4, (tPwmOutMode) 0, 0);
  CbPwm_ConfigureCarrier((tPwmOutput) 4, (tPwmCarrier) 0, 0);
  CbPwm_ConfigureDeadTime((tPwmOutput) 4, 1.5E-7F, 0);
  CbPwm_ConfigureUpdateRate((tPwmOutput) 4, (tPwmRate) 1, 0);
  CbPwm_SetPhase((tPwmOutput) 4, 0.0F, 0);
  CbPwm_SetDutyCycle((tPwmOutput) 4, 0.0F, 0);
  CbPwm_Activate((tPwmOutput) 4, 0);

  // End of Start for SubSystem: '<S43>/generation'
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

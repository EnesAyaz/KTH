//
// Academic License - for use in teaching, academic research, and meeting
// course requirements at degree granting institutions only.  Not for
// government, commercial, or other organizational use.
//
// File: acg_main.cpp
//
// Code generated for Simulink model 'EJ2311_PWM'.
// To be implemented on the B-Box RCP or the B-Board PRO.
//
// Model version                  : 16.3
// Simulink Coder version         : 23.2 (R2023b) 01-Aug-2023
// C/C++ source code generated on : Wed Feb 14 15:50:32 2024
//
#include "User/user.h"
#include "extern_user.h"
#include "Core/core.h"
#include "EJ2311_PWM.h"

tUserSafe UserInit(void)
{
  EJ2311_PWM_initialize();
  return SAFE;
}

tUserSafe SimulinkInterrupt(void)
{
  EJ2311_PWM_step();
  return SAFE;
}

void UserError(tErrorSource source)
{
}

//
// End of automatically generated code
// Copyright imperix ltd. Switzerland 2021
// [EOF]
//

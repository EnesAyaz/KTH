//
// Academic License - for use in teaching, academic research, and meeting
// course requirements at degree granting institutions only.  Not for
// government, commercial, or other organizational use.
//
// File: EJ2311_PWM_private.h
//
// Code generated for Simulink model 'EJ2311_PWM'.
// To be implemented on the B-Box RCP or the B-Board PRO.
//
// Model version                  : 16.3
// Simulink Coder version         : 23.2 (R2023b) 01-Aug-2023
// C/C++ source code generated on : Wed Feb 14 15:50:32 2024
//
#ifndef RTW_HEADER_EJ2311_PWM_private_h_
#define RTW_HEADER_EJ2311_PWM_private_h_
#include "rtwtypes.h"
#include "EJ2311_PWM_types.h"

int Can_Write(unsigned int mailbox_id, void* data, int size);
int Eth_Write(unsigned int mailbox_id, void* data, int size);
void Adc_GetPointer(unsigned int input, unsigned int device, int16_T ** pointer);

#include "allIncludes.h"

tUserSafe SimulinkInterrupt(void);
void ConfigureReadTriggerDelayInNs(int);

#endif                                 // RTW_HEADER_EJ2311_PWM_private_h_

//
// End of automatically generated code
// Copyright imperix ltd. Switzerland 2021
// [EOF]
//

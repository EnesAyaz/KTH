//
// Academic License - for use in teaching, academic research, and meeting
// course requirements at degree granting institutions only.  Not for
// government, commercial, or other organizational use.
//
// File: SPWM_private.h
//
// Code generated for Simulink model 'SPWM'.
// To be implemented on the B-Box RCP or the B-Board PRO.
//
// Model version                  : 16.7
// Simulink Coder version         : 23.2 (R2023b) 01-Aug-2023
// C/C++ source code generated on : Tue Aug 12 17:33:52 2025
//
#ifndef RTW_HEADER_SPWM_private_h_
#define RTW_HEADER_SPWM_private_h_
#include "rtwtypes.h"
#include "SPWM_types.h"
#include "SPWM.h"

int Can_Write(unsigned int mailbox_id, void* data, int size);
int Eth_Write(unsigned int mailbox_id, void* data, int size);
void Adc_GetPointer(unsigned int input, unsigned int device, int16_T ** pointer);

#include "allIncludes.h"

tUserSafe SimulinkInterrupt(void);
void ConfigureReadTriggerDelayInNs(int);
extern uint32_T plook_u32ff_binx(real32_T u, const real32_T bp[], uint32_T
  maxIndex, real32_T *fraction);
extern real32_T intrp4d_fu32fl_pw(const uint32_T bpIndex[], const real32_T frac[],
  const real32_T table[], const uint32_T stride[]);
extern uint32_T binsearch_u32f(real32_T u, const real32_T bp[], uint32_T
  startIndex, uint32_T maxIndex);

#endif                                 // RTW_HEADER_SPWM_private_h_

//
// End of automatically generated code
// Copyright imperix ltd. Switzerland 2021
// [EOF]
//

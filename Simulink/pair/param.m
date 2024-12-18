%% Motor Parameters
f_motor=1000;
fsw=14e3;
ma=0.9;
%% Simulation parameters
SampleTime=1e-8;
Tfinal=10/f_motor;
mode=1;
%% DC SUPPLY
VDC=1070;
LSource= 1e-6;
RSource= 0.01;

%% 
ModuleAPhase=0;
ModuleBPhase=0;
ModuleCPhase=0;

%% Full-Bridge Parameters
C_DCA=150e-6;
C_DCB=150e-6;
C_DCC=150e-6;
% ESRA=1e-3;
% ESRB=1e-3;
% ESRC=1e-3;
%% Parasitics
% RA_parasitic=1e-3;
% LA_parasitic=1e-8;
% RB_parasitic=1e-3;
% LB_parasitic=1e-8;
% RC_parasitic=1e-3;
% LC_parasitic=1e-8;
% RAB_parasitic=1e-3;
% LAB_parasitic=1e-8;
% RBC_parasitic=1e-3;
% LBC_parasitic=1e-8;
% RA_mid_parasitic=1e-3;
% LA_mid_parasitic=1e-8;
% RB_mid_parasitic=1e-3;
% LB_mid_parasitic=1e-8;
% RC_mid_parasitic=1e-3;
% LC_mid_parasitic=1e-8;
%% MOTOR 
Rmotor=3;
Ld=100e-6; % H
Lq=200e-6; % H

% Kf=0.1157;
% J=0.001;
% Bm=0;
% Tf=1;
% w0=0;
%%  Load Torque


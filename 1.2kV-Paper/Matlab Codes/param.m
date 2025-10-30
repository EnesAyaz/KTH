%% ============================================
%  RUN PARAMETRIC PARETO STUDY
%  ============================================
clear; clc; close all;

% --- System definition ---
S = struct();

% --- Powertrain operating conditions ---
S.Pout       = 300e3;      % Output power [W]
S.ffund      = 500;        % Fundamental frequency [Hz]
S.Udc        = 800;        % DC-link voltage [V]  (change to 1200 for HV case)
S.ma         = 1.0;        % Modulation index
S.cosphi     = 1.0;        % Power factor
S.Ipk_scale  = 1.5;        % Scaling factor for peak current

% --- Sweep ranges ---
S.Fsw_vec    = 5e3:0.5e3:30e3;   % Switching frequency range [Hz]
S.Adie_vec   = 30:10:1000;       % Die area range [mm^2]

% --- Semiconductor loss model parameters ---
S.k_r        = 7.2e-3;     % Conduction constant
S.alpha_r    = 1.6;        % Conduction exponent
S.Ub_kV      = 1.2;        % Rated blocking voltage [kV] (1.2 kV or 1.7 kV)
S.k_c        = 1.6e4;      % Coss scaling constant
S.alpha_c    = -1;         % Coss exponent
S.dv_dt      = 10e3/1e-6;  % [V/s]
S.di_dt      = 10e3/1e-6;  % [A/s]

% --- Thermal parameters ---
S.DeltaT_allow = 75;        % Allowed junction-to-ambient rise [K]
S.r_jc_per_mm2 = 2.5;       % K·mm²/W (junction-to-case per mm²)
S.r_ch_module  = 0.025;     % K/W per cooling channel (estimated)

% --- Topology setup ---
S.topology.name       = '2L-3Ph';  % label for plots
S.topology.n_dies     = 6;         % number of dies sharing heat
S.topology.n_channels = 3;         % number of parallel cooling channels

% --- Cooling-to-volume mapping ---
S.alpha_cool = 0.02;        % [L·K/W] mapping coefficient (empirical)
S.cool_thickness_L = 0.0;   % Fixed offset volume [L]
S.V_fixed = 0.0;            % Optional fixed volume for other components [L]

% --- Capacitor requirement model ---
S.cap_model = @cap_model_simple;  % use built-in simple model (or replace)
S.Kc        = 4.0;         % scaling factor for ripple
S.dv_pp     = 12.5;        % allowed bus ripple voltage [Vpp]
S.cap_density = 80;        % F/L (film capacitor density estimate)

% --- Semiconductor packaging volume density ---
S.semi_vol_per_mm2 = 3e-4;  % L/mm² (effective including busbar etc.)

% --- Cooling surface area & packaging constants ---
S.cool_thickness_L = 0;    % constant offset in volume (header/manifold)

% --- Visual appearance (optional aesthetic controls) ---
S.colors.main  = [0.1 0.1 0.1];     % black
S.colors.front = [0.75 0.35 0.35];  % muted red for Pareto curve
S.ms = 24;
S.lw = 2;

% --- Run Pareto front optimizer ---
pareto_efficiency_volume();

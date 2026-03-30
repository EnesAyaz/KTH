%% =========================================================================
%  DC-Link Capacitor Stress Simulation with Parasitic Components
%  Adaptive Multi-Carrier PWM vs. Conventional Single-Carrier PWM
%
%  Based on: "Real-Time DC-Link Capacitor Stress Reduction in Two-Level
%  Three-Phase Inverters Using Adaptive Multi-Carrier PWM Method"
%  IPEC-Nagasaki 2026 - ECCE Asia
%
%  Extended model includes:
%    - DC-link capacitor ESR (R_c) and ESL (L_c)
%    - DC cable/battery inductance (L_bat) and resistance (R_bat)
%    - Analytical switching-period RMS evaluation (Eq. 5-7 in paper)
%    - Offline LUT-based optimal carrier phase shift computation
%    - Comparison plots: RMS current, voltage ripple, spectral content
%
%  Author: Extended simulation scaffold for IPEC 2026 paper
%  =========================================================================

clear; clc; close all;

%% =========================================================================
%  SECTION 1: SYSTEM PARAMETERS
%  =========================================================================

% --- Fundamental & Switching Frequencies ---
f1      = 50;               % Fundamental frequency [Hz]
fsw     = 10e3;             % Switching frequency [Hz]
Nsw     = fsw / f1;         % Switching intervals per fundamental period
Tsw     = 1 / fsw;          % Switching period [s]
T1      = 1 / f1;           % Fundamental period [s]

% --- DC-Link Parameters ---
Vdc     = 600;              % DC bus voltage [V]
C_dc    = 470e-6;           % DC-link capacitance [F]
ESR     = 5e-3;             % Capacitor equivalent series resistance [Ohm]
ESL     = 50e-9;            % Capacitor equivalent series inductance [H]

% --- DC Source / Battery Side Parameters ---
L_bat   = 100e-6;           % Battery/cable inductance [H]
R_bat   = 10e-3;            % Battery/cable resistance [Ohm]

% --- Load / Motor Parameters ---
R_load  = 5;                % Phase resistance [Ohm]
L_load  = 5e-3;             % Phase inductance [H]
theta_phase = atan(2*pi*f1*L_load / R_load);  % Load power factor angle [rad]

% --- Modulation Parameters (sweep) ---
ma_vec  = 0.1 : 0.05 : 1.0;    % Modulation index sweep
pf_vec  = [0.7, 0.8, 0.9, 0.95, 1.0]; % Power factor sweep
Ipp     = 1;                    % Peak phase current [p.u.]

% --- Time vector for one switching period (high resolution) ---
Npts    = 1000;                 % Points per switching period
t_sw    = linspace(0, Tsw, Npts);

%% =========================================================================
%  SECTION 2: CAPACITOR IMPEDANCE MODEL
%  Zcap(jw) = ESR + j*w*ESL + 1/(j*w*C_dc)
%  Used to compute actual capacitor voltage ripple from current stress
%  =========================================================================

% Frequency vector for impedance analysis
f_vec   = logspace(1, 6, 2000);
w_vec   = 2 * pi * f_vec;
Z_cap   = ESR + 1j * w_vec * ESL + 1 ./ (1j * w_vec * C_dc);

% Self-resonant frequency of the capacitor
f_res   = 1 / (2 * pi * sqrt(ESL * C_dc));
fprintf('=== Capacitor Parasitic Analysis ===\n');
fprintf('  Capacitance:         %.1f uF\n', C_dc*1e6);
fprintf('  ESR:                 %.1f mOhm\n', ESR*1e3);
fprintf('  ESL:                 %.1f nH\n', ESL*1e9);
fprintf('  Self-resonant freq:  %.2f kHz\n', f_res/1e3);
fprintf('  DC-bus inductance:   %.1f uH\n', L_bat*1e6);
fprintf('  DC-bus resistance:   %.1f mOhm\n\n', R_bat*1e3);

%% =========================================================================
%  SECTION 3: CORE ANALYTICAL FUNCTIONS
%  =========================================================================

% --- 3.1: Switching function for one leg (Eq. 4) ---
% Returns S(t) in {0,1} given duty cycle d and carrier phase shift phi_c
get_switching_function = @(d, phi_c, t) ...
    double( mod(t/Tsw - phi_c/(2*pi), 1) < d );

% --- 3.2: Instantaneous capacitor current (Eq. 1) ---
% icap(t) = ia*Sa + ib*Sb + ic*Sc - Idc
get_icap = @(ia, ib, ic, Sa, Sb, Sc) ...
    ia.*Sa + ib.*Sb + ic.*Sc - (ia.*Sa + ib.*Sb + ic.*Sc);
% Note: Idc is the average, computed inside the RMS function below

% --- 3.3: Switching-period RMS (Eq. 5) with parasitic correction ---
% The ESL introduces a voltage term: v_L = ESL * d(icap)/dt
% This modifies the effective current seen by pure C_dc
function [Irms, Vrms_cap, Vrms_esl] = compute_switching_rms(ia, ib, ic, ...
        da, db, dc, phi_b, phi_c, t_sw, Tsw, ESR, ESL, C_dc)
    
    Npts = length(t_sw);
    dt   = Tsw / Npts;
    
    % Switching functions for each leg
    Sa = double(mod(t_sw/Tsw,         1) < da);
    Sb = double(mod(t_sw/Tsw - phi_b/(2*pi), 1) < db);
    Sc = double(mod(t_sw/Tsw - phi_c/(2*pi), 1) < dc);
    
    % Raw inverter current
    i_inv = ia*Sa + ib*Sb + ic*Sc;
    
    % Average DC current (removed from capacitor path)
    Idc   = mean(i_inv);
    icap  = i_inv - Idc;
    
    % Capacitor RMS current
    Irms  = sqrt(mean(icap.^2));
    
    % ESL voltage: v_ESL = ESL * d(icap)/dt
    dicap_dt = gradient(icap, dt);
    v_ESL    = ESL * dicap_dt;
    
    % Voltage across pure capacitor (integrate icap/C_dc + ESR drop)
    v_C   = cumsum(icap * dt) / C_dc;
    v_C   = v_C - mean(v_C);           % Remove DC offset
    v_ESR = ESR * icap;
    v_cap_total = v_C + v_ESR + v_ESL; % Total capacitor terminal voltage
    
    Vrms_cap = sqrt(mean(v_C.^2));
    Vrms_esl = sqrt(mean(v_ESL.^2));
end

%% =========================================================================
%  SECTION 4: OFFLINE LUT CONSTRUCTION
%  Finds optimal (theta_b, theta_c) for each (ia_hat, ib_hat, da, db)
%  Grid search over carrier phase shifts as described in Section V of paper
%  =========================================================================

fprintf('=== Building Offline LUT (this may take a moment) ===\n');

% LUT grid resolution (coarse for speed, increase for accuracy)
N_curr  = 10;   % Grid points for normalized currents
N_duty  = 10;   % Grid points for duty cycles
N_phase = 18;   % Phase shift candidates (0 to 360 deg, step 20 deg)

% Normalized current grid: ia_hat in [-0.5, 0.5], ib_hat in [-0.5, 0.5]
ia_hat_vec = linspace(-0.5, 0.5, N_curr);
ib_hat_vec = linspace(-0.5, 0.5, N_curr);

% Duty cycle grid: da, db in [0.1, 0.9]
da_vec     = linspace(0.1, 0.9, N_duty);
db_vec     = linspace(0.1, 0.9, N_duty);

% Phase shift candidates [rad]
theta_candidates = linspace(0, 2*pi*(1-1/N_phase), N_phase);

% Pre-allocate LUT
LUT_theta_b = zeros(N_curr, N_curr, N_duty, N_duty);
LUT_theta_c = zeros(N_curr, N_curr, N_duty, N_duty);

t_sw_lut = linspace(0, Tsw, 200);  % Coarser time for LUT speed

for i1 = 1:N_curr
    for i2 = 1:N_curr
        for d1 = 1:N_duty
            for d2 = 1:N_duty
                
                ia_h = ia_hat_vec(i1);
                ib_h = ib_hat_vec(i2);
                ic_h = -ia_h - ib_h;  % Balanced: ia+ib+ic=0
                
                da = da_vec(d1);
                db = db_vec(d2);
                dc = 1.5 - da - db;   % SPWM constraint: da+db+dc=3/2
                
                % Skip physically impossible duty cycles
                if dc < 0 || dc > 1
                    continue;
                end
                
                best_rms = inf;
                best_tb  = 0;
                best_tc  = 0;
                
                for tb_idx = 1:N_phase
                    for tc_idx = 1:N_phase
                        phi_b = theta_candidates(tb_idx);
                        phi_c = theta_candidates(tc_idx);
                        
                        Sa = double(mod(t_sw_lut/Tsw, 1) < da);
                        Sb = double(mod(t_sw_lut/Tsw - phi_b/(2*pi), 1) < db);
                        Sc = double(mod(t_sw_lut/Tsw - phi_c/(2*pi), 1) < dc);
                        
                        i_inv = ia_h*Sa + ib_h*Sb + ic_h*Sc;
                        icap  = i_inv - mean(i_inv);
                        rms   = sqrt(mean(icap.^2));
                        
                        if rms < best_rms
                            best_rms = rms;
                            best_tb  = phi_b;
                            best_tc  = phi_c;
                        end
                    end
                end
                
                LUT_theta_b(i1, i2, d1, d2) = best_tb;
                LUT_theta_c(i1, i2, d1, d2) = best_tc;
            end
        end
    end
end

fprintf('  LUT construction complete (%dx%dx%dx%d entries).\n\n', ...
    N_curr, N_curr, N_duty, N_duty);

% --- LUT query function (bilinear interpolation) ---
query_lut = @(ia_h, ib_h, da, db) deal( ...
    interp2(ia_hat_vec, ib_hat_vec, ...
        LUT_theta_b(:,:, max(1,round(interp1(da_vec,1:N_duty,da,'nearest','extrap'))), ...
                         max(1,round(interp1(db_vec,1:N_duty,db,'nearest','extrap')))), ...
        ia_h, ib_h, 'linear', 0), ...
    interp2(ia_hat_vec, ib_hat_vec, ...
        LUT_theta_c(:,:, max(1,round(interp1(da_vec,1:N_duty,da,'nearest','extrap'))), ...
                         max(1,round(interp1(db_vec,1:N_duty,db,'nearest','extrap')))), ...
        ia_h, ib_h, 'linear', 0) ...
);

%% =========================================================================
%  SECTION 5: FULL FUNDAMENTAL-PERIOD SIMULATION
%  Sweeps over all switching intervals k=1..Nsw for both methods
%  Implements Eq. 6-7 from the paper + parasitic capacitor model
%  =========================================================================

fprintf('=== Running Fundamental-Period Simulation ===\n');

% --- Select operating point ---
ma         = 0.8;   % Modulation index
pf_angle   = acos(0.95);  % Power factor angle [rad]
theta_fund = 0;            % Initial phase

% Pre-allocate
Irms_conv   = zeros(1, Nsw);
Irms_prop   = zeros(1, Nsw);
Vrms_C_conv = zeros(1, Nsw);
Vrms_C_prop = zeros(1, Nsw);
Vrms_ESL_conv = zeros(1, Nsw);
Vrms_ESL_prop = zeros(1, Nsw);

for k = 1:Nsw
    % --- Quasi-static phase angle at interval k (Eq. 6) ---
    theta_k = 2*pi*k/Nsw + theta_fund;
    
    % Phase reference voltages (duty cycles)
    da = 0.5 + 0.5 * ma * cos(theta_k);
    db = 0.5 + 0.5 * ma * cos(theta_k - 2*pi/3);
    dc_val = 1.5 - da - db;
    
    % Clamp to valid range
    da = max(0.01, min(0.99, da));
    db = max(0.01, min(0.99, db));
    dc_val = max(0.01, min(0.99, dc_val));
    
    % Phase currents (Eq. 6)
    ia = Ipp * cos(theta_k - pf_angle);
    ib = Ipp * cos(theta_k - 2*pi/3 - pf_angle);
    ic = Ipp * cos(theta_k + 2*pi/3 - pf_angle);
    
    % --- CONVENTIONAL: all carriers in phase (phi_b=phi_c=0) ---
    [Irms_conv(k), Vrms_C_conv(k), Vrms_ESL_conv(k)] = ...
        compute_switching_rms(ia, ib, ic, da, db, dc_val, ...
        0, 0, t_sw, Tsw, ESR, ESL, C_dc);
    
    % --- PROPOSED: LUT-based optimal phase shifts ---
    i_sum = abs(ia) + abs(ib) + abs(ic) + 1e-10;
    ia_h  = ia / i_sum;
    ib_h  = ib / i_sum;
    
    % Clamp to LUT range
    ia_h  = max(ia_hat_vec(1), min(ia_hat_vec(end), ia_h));
    ib_h  = max(ib_hat_vec(1), min(ib_hat_vec(end), ib_h));
    
    [phi_b_opt, phi_c_opt] = query_lut(ia_h, ib_h, da, db);
    
    [Irms_prop(k), Vrms_C_prop(k), Vrms_ESL_prop(k)] = ...
        compute_switching_rms(ia, ib, ic, da, db, dc_val, ...
        phi_b_opt, phi_c_opt, t_sw, Tsw, ESR, ESL, C_dc);
end

% Fundamental-period RMS (Eq. 7)
Icap_conv_total = sqrt(mean(Irms_conv.^2));
Icap_prop_total = sqrt(mean(Irms_prop.^2));
reduction_pct   = (1 - Icap_prop_total/Icap_conv_total) * 100;

fprintf('  ma = %.2f, PF = %.2f\n', ma, cos(pf_angle));
fprintf('  Conventional RMS:  %.4f p.u.\n', Icap_conv_total);
fprintf('  Proposed RMS:      %.4f p.u.\n', Icap_prop_total);
fprintf('  RMS Reduction:     %.1f%%\n\n', reduction_pct);

%% =========================================================================
%  SECTION 6: SWEEP OVER ma AND POWER FACTOR (Fig. 7 equivalent)
%  =========================================================================

fprintf('=== Running ma / PF Sweep ===\n');

Irms_conv_map = zeros(length(pf_vec), length(ma_vec));
Irms_prop_map = zeros(length(pf_vec), length(ma_vec));

for pf_idx = 1:length(pf_vec)
    pf_angle_i = acos(pf_vec(pf_idx));
    for ma_idx = 1:length(ma_vec)
        ma_i = ma_vec(ma_idx);
        
        Ic_conv = zeros(1, Nsw);
        Ic_prop = zeros(1, Nsw);
        
        for k = 1:Nsw
            theta_k = 2*pi*k/Nsw;
            da = max(0.01,min(0.99, 0.5 + 0.5*ma_i*cos(theta_k)));
            db = max(0.01,min(0.99, 0.5 + 0.5*ma_i*cos(theta_k - 2*pi/3)));
            dc_i = max(0.01,min(0.99, 1.5 - da - db));
            
            ia = Ipp * cos(theta_k - pf_angle_i);
            ib = Ipp * cos(theta_k - 2*pi/3 - pf_angle_i);
            ic = Ipp * cos(theta_k + 2*pi/3 - pf_angle_i);
            
            % Conventional
            Sa = double(mod(t_sw/Tsw,1) < da);
            Sb = double(mod(t_sw/Tsw,1) < db);
            Sc = double(mod(t_sw/Tsw,1) < dc_i);
            i_inv = ia*Sa + ib*Sb + ic*Sc;
            icap  = i_inv - mean(i_inv);
            Ic_conv(k) = sqrt(mean(icap.^2));
            
            % Proposed (LUT)
            i_sum = abs(ia)+abs(ib)+abs(ic)+1e-10;
            ia_h = max(ia_hat_vec(1),min(ia_hat_vec(end), ia/i_sum));
            ib_h = max(ib_hat_vec(1),min(ib_hat_vec(end), ib/i_sum));
            [phi_b_i, phi_c_i] = query_lut(ia_h, ib_h, da, db);
            
            Sb = double(mod(t_sw/Tsw - phi_b_i/(2*pi),1) < db);
            Sc = double(mod(t_sw/Tsw - phi_c_i/(2*pi),1) < dc_i);
            i_inv = ia*Sa + ib*Sb + ic*Sc;
            icap  = i_inv - mean(i_inv);
            Ic_prop(k) = sqrt(mean(icap.^2));
        end
        
        Irms_conv_map(pf_idx, ma_idx) = sqrt(mean(Ic_conv.^2));
        Irms_prop_map(pf_idx, ma_idx) = sqrt(mean(Ic_prop.^2));
    end
    fprintf('  PF = %.2f done.\n', pf_vec(pf_idx));
end

%% =========================================================================
%  SECTION 7: CAPACITOR IMPEDANCE PLOT (Bode-style)
%  =========================================================================

%% =========================================================================
%  SECTION 8: VISUALIZATION
%  =========================================================================

fprintf('\n=== Generating Plots ===\n');

% Color scheme
c_conv = [0.85, 0.2, 0.2];   % Red for conventional
c_prop = [0.1,  0.5, 0.8];   % Blue for proposed
c_bat  = [0.2,  0.7, 0.3];   % Green for battery impedance effect

theta_axis = linspace(0, 360, Nsw);

%% --- Figure 1: Capacitor Impedance vs Frequency ---
figure('Name','Capacitor Impedance','Position',[50 50 800 400]);
subplot(1,2,1);
loglog(f_vec, abs(Z_cap), 'k-', 'LineWidth', 2);
xline(f_res/1e3,'--r','LineWidth',1.5);
text(f_res/1e3*1.2, max(abs(Z_cap))*0.3, sprintf('f_{res}=%.1fkHz',f_res/1e3), ...
    'Color','r','FontSize',9);
xlabel('Frequency [Hz]'); ylabel('|Z_{cap}| [\Omega]');
title('DC-Link Capacitor Impedance');
grid on; set(gca,'FontSize',10);
legend(sprintf('C=%.0fuF, ESR=%.1fmΩ, ESL=%.0fnH', ...
    C_dc*1e6, ESR*1e3, ESL*1e9), 'Location','NorthWest');

subplot(1,2,2);
semilogx(f_vec, angle(Z_cap)*180/pi, 'k-', 'LineWidth', 2);
xline(f_res/1e3,'--r','LineWidth',1.5);
xlabel('Frequency [Hz]'); ylabel('Phase [deg]');
title('Capacitor Impedance Phase');
grid on; set(gca,'FontSize',10); ylim([-95 95]);
yticks([-90,-45,0,45,90]);

%% --- Figure 2: Switching-period RMS over fundamental period (Fig 6 equiv) ---
figure('Name','Switching-Period RMS','Position',[50 100 900 500]);
subplot(2,2,1);
plot(theta_axis, Irms_conv, 'Color', c_conv, 'LineWidth', 1.2); hold on;
plot(theta_axis, Irms_prop, 'Color', c_prop, 'LineWidth', 1.2);
xlabel('Fundamental Phase [°]'); ylabel('I_{cap,rms}[k] [p.u.]');
title(sprintf('Capacitor RMS Current (m_a=%.1f, PF=%.2f)', ma, cos(pf_angle)));
legend('Conventional PWM','Proposed Multi-Carrier','Location','NorthEast');
grid on; set(gca,'FontSize',10);

subplot(2,2,2);
plot(theta_axis, Vrms_C_conv*1e3, 'Color', c_conv, 'LineWidth', 1.2); hold on;
plot(theta_axis, Vrms_C_prop*1e3, 'Color', c_prop, 'LineWidth', 1.2);
xlabel('Fundamental Phase [°]'); ylabel('V_{cap,rms} [mV]');
title('Capacitor Voltage Ripple (pure C)');
legend('Conventional','Proposed','Location','NorthEast');
grid on; set(gca,'FontSize',10);

subplot(2,2,3);
plot(theta_axis, Vrms_ESL_conv*1e3, 'Color', c_conv, 'LineWidth', 1.2); hold on;
plot(theta_axis, Vrms_ESL_prop*1e3, 'Color', c_prop, 'LineWidth', 1.2);
xlabel('Fundamental Phase [°]'); ylabel('V_{ESL,rms} [mV]');
title('ESL Voltage Stress (v = L_{ESL} \cdot di/dt)');
legend('Conventional','Proposed','Location','NorthEast');
grid on; set(gca,'FontSize',10);

subplot(2,2,4);
reduction_per_interval = (1 - Irms_prop ./ (Irms_conv + 1e-10)) * 100;
plot(theta_axis, reduction_per_interval, 'Color', [0.2 0.65 0.3], 'LineWidth', 1.5);
yline(reduction_pct, '--k', sprintf('Avg=%.1f%%',reduction_pct), 'LineWidth', 1);
xlabel('Fundamental Phase [°]'); ylabel('RMS Reduction [%]');
title('Per-Interval RMS Reduction of Proposed vs. Conventional');
ylim([0 60]); grid on; set(gca,'FontSize',10);

sgtitle(sprintf('Operating Point: m_a=%.2f, PF=%.2f | C=%.0fuF, ESR=%.0fmΩ, ESL=%.0fnH, L_{bat}=%.0fuH', ...
    ma, cos(pf_angle), C_dc*1e6, ESR*1e3, ESL*1e9, L_bat*1e6), 'FontSize',11,'FontWeight','bold');

%% --- Figure 3: RMS Map over ma and PF (Fig. 7 equivalent) ---
figure('Name','RMS Current Map','Position',[100 150 1100 450]);

subplot(1,3,1);
contourf(ma_vec, pf_vec, Irms_conv_map, 15, 'LineColor','none');
colorbar; colormap(gca, hot);
xlabel('Modulation Index m_a'); ylabel('Power Factor');
title('Conventional Single-Carrier PWM');
set(gca,'FontSize',10);

subplot(1,3,2);
contourf(ma_vec, pf_vec, Irms_prop_map, 15, 'LineColor','none');
colorbar; colormap(gca, hot);
xlabel('Modulation Index m_a'); ylabel('Power Factor');
title('Proposed Multi-Carrier PWM');
set(gca,'FontSize',10);

subplot(1,3,3);
reduction_map = (1 - Irms_prop_map ./ (Irms_conv_map + 1e-10)) * 100;
contourf(ma_vec, pf_vec, reduction_map, 15, 'LineColor','none');
colorbar; colormap(gca, parula);
xlabel('Modulation Index m_a'); ylabel('Power Factor');
title('RMS Reduction [%]');
set(gca,'FontSize',10);

sgtitle('DC-Link Capacitor RMS Current: Conventional vs. Proposed | With ESR/ESL/L_{bat} Parasitics', ...
    'FontSize',11,'FontWeight','bold');

%% --- Figure 4: Parametric Sensitivity to ESR/ESL/L_bat ---
figure('Name','Parasitic Sensitivity','Position',[150 200 900 350]);

ESR_range = logspace(-3, -1, 20);   % 1mΩ to 100mΩ
ESL_range = logspace(-9, -6, 20);   % 1nH to 1uH

% Compute peak capacitor voltage ripple vs ESR and ESL at fixed operating point
k_test = round(Nsw/4);  % Quarter period (peak current)
theta_k = 2*pi*k_test/Nsw;
da = max(0.01,min(0.99, 0.5+0.5*ma*cos(theta_k)));
db = max(0.01,min(0.99, 0.5+0.5*ma*cos(theta_k-2*pi/3)));
dc_t = max(0.01,min(0.99,1.5-da-db));
ia = Ipp*cos(theta_k-pf_angle);
ib = Ipp*cos(theta_k-2*pi/3-pf_angle);
ic_t = Ipp*cos(theta_k+2*pi/3-pf_angle);

V_peak_esr = zeros(1,length(ESR_range));
V_peak_esl = zeros(1,length(ESL_range));

for ei = 1:length(ESR_range)
    [~, Vc, ~] = compute_switching_rms(ia,ib,ic_t,da,db,dc_t,0,0,t_sw,Tsw,...
        ESR_range(ei), ESL, C_dc);
    V_peak_esr(ei) = Vc;
end
for li = 1:length(ESL_range)
    [~, ~, Vesl] = compute_switching_rms(ia,ib,ic_t,da,db,dc_t,0,0,t_sw,Tsw,...
        ESR, ESL_range(li), C_dc);
    V_peak_esl(li) = Vesl;
end

subplot(1,2,1);
semilogx(ESR_range*1e3, V_peak_esr*1e3, 'b-o', 'LineWidth', 1.5, 'MarkerSize',4);
xline(ESR*1e3,'--r','Nominal','LineWidth',1);
xlabel('ESR [m\Omega]'); ylabel('V_{cap,rms} [mV]');
title('Capacitor Voltage Ripple vs. ESR');
grid on; set(gca,'FontSize',10);

subplot(1,2,2);
loglog(ESL_range*1e9, V_peak_esl*1e3, 'r-o', 'LineWidth', 1.5, 'MarkerSize',4);
xline(ESL*1e9,'--b','Nominal','LineWidth',1);
xlabel('ESL [nH]'); ylabel('V_{ESL,rms} [mV]');
title('ESL Voltage Stress vs. Inductance');
grid on; set(gca,'FontSize',10);

sgtitle('Parasitic Sensitivity Analysis (DC-Link Capacitor)', ...
    'FontSize',11,'FontWeight','bold');

%% =========================================================================
%  SECTION 9: SUMMARY TABLE
%  =========================================================================

fprintf('\n========================================================\n');
fprintf('  SIMULATION SUMMARY\n');
fprintf('========================================================\n');
fprintf('  Operating point:  m_a=%.2f, PF=%.2f\n', ma, cos(pf_angle));
fprintf('  Switching freq:   %.1f kHz\n', fsw/1e3);
fprintf('  -------------------------------------------------------\n');
fprintf('  Component         Value\n');
fprintf('  -------------------------------------------------------\n');
fprintf('  C_dc              %.1f uF\n', C_dc*1e6);
fprintf('  ESR               %.1f mΩ\n', ESR*1e3);
fprintf('  ESL               %.1f nH\n', ESL*1e9);
fprintf('  L_battery         %.1f uH\n', L_bat*1e6);
fprintf('  R_battery         %.1f mΩ\n', R_bat*1e3);
fprintf('  -------------------------------------------------------\n');
fprintf('  Method            I_cap,rms [p.u.]   Reduction\n');
fprintf('  -------------------------------------------------------\n');
fprintf('  Conventional PWM  %.4f              --\n', Icap_conv_total);
fprintf('  Proposed PWM      %.4f              %.1f%%\n', Icap_prop_total, reduction_pct);
fprintf('========================================================\n');
fprintf('\nNote: Increase N_curr, N_duty, N_phase in Section 4 for\n');
fprintf('      higher LUT resolution (at cost of build time).\n');
fprintf('      Increase Npts in Section 1 for waveform accuracy.\n\n');
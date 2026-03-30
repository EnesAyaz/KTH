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

% --- Modulation Parameters (sweep) ---
ma_vec  = 0.1 : 0.05 : 1.0;           % Modulation index sweep
pf_vec  = [0.7, 0.8, 0.9, 0.95, 1.0]; % Power factor sweep
Ipp     = 1;                           % Peak phase current [p.u.]

% --- Time vector for one switching period ---
Npts    = 1000;
t_sw    = linspace(0, Tsw, Npts);

%% =========================================================================
%  SECTION 2: CAPACITOR IMPEDANCE MODEL
%  =========================================================================

f_freq  = logspace(1, 6, 2000);
w_vec   = 2 * pi * f_freq;
Z_cap   = ESR + 1j * w_vec * ESL + 1 ./ (1j * w_vec * C_dc);
f_res   = 1 / (2 * pi * sqrt(ESL * C_dc));

fprintf('=== Capacitor Parasitic Analysis ===\n');
fprintf('  Capacitance:         %.1f uF\n',    C_dc*1e6);
fprintf('  ESR:                 %.1f mOhm\n',  ESR*1e3);
fprintf('  ESL:                 %.1f nH\n',    ESL*1e9);
fprintf('  Self-resonant freq:  %.2f kHz\n',   f_res/1e3);
fprintf('  DC-bus inductance:   %.1f uH\n',    L_bat*1e6);
fprintf('  DC-bus resistance:   %.1f mOhm\n\n',R_bat*1e3);

%% =========================================================================
%  SECTION 3: OFFLINE LUT CONSTRUCTION
%  =========================================================================

fprintf('=== Building Offline LUT (this may take a moment) ===\n');

N_curr  = 10;
N_duty  = 10;
N_phase = 18;

ia_hat_vec       = linspace(-0.5, 0.5, N_curr);
ib_hat_vec       = linspace(-0.5, 0.5, N_curr);
da_vec           = linspace(0.1, 0.9, N_duty);
db_vec           = linspace(0.1, 0.9, N_duty);
theta_candidates = linspace(0, 2*pi*(1-1/N_phase), N_phase);

LUT_theta_b = zeros(N_curr, N_curr, N_duty, N_duty);
LUT_theta_c = zeros(N_curr, N_curr, N_duty, N_duty);

t_sw_lut = linspace(0, Tsw, 200);

for i1 = 1:N_curr
    for i2 = 1:N_curr
        for d1 = 1:N_duty
            for d2 = 1:N_duty

                ia_h = ia_hat_vec(i1);
                ib_h = ib_hat_vec(i2);
                ic_h = -ia_h - ib_h;

                da_lut = da_vec(d1);
                db_lut = db_vec(d2);
                dc_lut = 1.5 - da_lut - db_lut;

                if dc_lut < 0 || dc_lut > 1
                    continue;
                end

                best_rms = inf;
                best_tb  = 0;
                best_tc  = 0;

                for tb_idx = 1:N_phase
                    for tc_idx = 1:N_phase
                        phi_b_lut = theta_candidates(tb_idx);
                        phi_c_lut = theta_candidates(tc_idx);

                        Sa_l = double(mod(t_sw_lut/Tsw,                    1) < da_lut);
                        Sb_l = double(mod(t_sw_lut/Tsw - phi_b_lut/(2*pi), 1) < db_lut);
                        Sc_l = double(mod(t_sw_lut/Tsw - phi_c_lut/(2*pi), 1) < dc_lut);

                        i_inv_l = ia_h*Sa_l + ib_h*Sb_l + ic_h*Sc_l;
                        icap_l  = i_inv_l - mean(i_inv_l);
                        rms_l   = sqrt(mean(icap_l.^2));

                        if rms_l < best_rms
                            best_rms = rms_l;
                            best_tb  = phi_b_lut;
                            best_tc  = phi_c_lut;
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

%% =========================================================================
%  SECTION 4: FULL FUNDAMENTAL-PERIOD SIMULATION (single operating point)
%  =========================================================================

fprintf('=== Running Fundamental-Period Simulation ===\n');

ma        = 0.8;
pf_angle  = acos(0.95);

Irms_conv     = zeros(1, Nsw);
Irms_prop     = zeros(1, Nsw);
Vrms_C_conv   = zeros(1, Nsw);
Vrms_C_prop   = zeros(1, Nsw);
Vrms_ESL_conv = zeros(1, Nsw);
Vrms_ESL_prop = zeros(1, Nsw);

for k = 1:Nsw
    theta_k = 2*pi*k/Nsw;

    da = max(0.01, min(0.99, 0.5 + 0.5*ma*cos(theta_k)));
    db = max(0.01, min(0.99, 0.5 + 0.5*ma*cos(theta_k - 2*pi/3)));
    dc = max(0.01, min(0.99, 1.5 - da - db));

    ia = Ipp * cos(theta_k - pf_angle);
    ib = Ipp * cos(theta_k - 2*pi/3 - pf_angle);
    ic = Ipp * cos(theta_k + 2*pi/3 - pf_angle);

    % Conventional (phi_b = phi_c = 0)
    [Irms_conv(k), Vrms_C_conv(k), Vrms_ESL_conv(k)] = ...
        compute_switching_rms(ia, ib, ic, da, db, dc, 0, 0, ...
        t_sw, Tsw, ESR, ESL, C_dc);

    % Proposed: LUT query
    i_sum = abs(ia) + abs(ib) + abs(ic) + 1e-10;
    ia_h  = max(ia_hat_vec(1), min(ia_hat_vec(end), ia/i_sum));
    ib_h  = max(ib_hat_vec(1), min(ib_hat_vec(end), ib/i_sum));

    d1_idx = max(1, min(N_duty, round(interp1(da_vec, 1:N_duty, da, 'linear', 'extrap'))));
    d2_idx = max(1, min(N_duty, round(interp1(db_vec, 1:N_duty, db, 'linear', 'extrap'))));

    phi_b_opt = interp2(ia_hat_vec, ib_hat_vec, ...
        LUT_theta_b(:,:,d1_idx,d2_idx)', ia_h, ib_h, 'linear', 0);
    phi_c_opt = interp2(ia_hat_vec, ib_hat_vec, ...
        LUT_theta_c(:,:,d1_idx,d2_idx)', ia_h, ib_h, 'linear', 0);

    [Irms_prop(k), Vrms_C_prop(k), Vrms_ESL_prop(k)] = ...
        compute_switching_rms(ia, ib, ic, da, db, dc, phi_b_opt, phi_c_opt, ...
        t_sw, Tsw, ESR, ESL, C_dc);
end

Icap_conv_total = sqrt(mean(Irms_conv.^2));
Icap_prop_total = sqrt(mean(Irms_prop.^2));
reduction_pct   = (1 - Icap_prop_total / Icap_conv_total) * 100;

fprintf('  ma = %.2f, PF = %.2f\n', ma, cos(pf_angle));
fprintf('  Conventional RMS:  %.4f p.u.\n', Icap_conv_total);
fprintf('  Proposed RMS:      %.4f p.u.\n', Icap_prop_total);
fprintf('  RMS Reduction:     %.1f%%\n\n', reduction_pct);

%% =========================================================================
%  SECTION 5: SWEEP OVER ma AND POWER FACTOR
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
            da = max(0.01,min(0.99, 0.5+0.5*ma_i*cos(theta_k)));
            db = max(0.01,min(0.99, 0.5+0.5*ma_i*cos(theta_k-2*pi/3)));
            dc = max(0.01,min(0.99, 1.5-da-db));

            ia = Ipp * cos(theta_k - pf_angle_i);
            ib = Ipp * cos(theta_k - 2*pi/3 - pf_angle_i);
            ic = Ipp * cos(theta_k + 2*pi/3 - pf_angle_i);

            [Ic_conv(k), ~, ~] = compute_switching_rms(ia, ib, ic, da, db, dc, ...
                0, 0, t_sw, Tsw, ESR, ESL, C_dc);

            i_sum = abs(ia)+abs(ib)+abs(ic)+1e-10;
            ia_h  = max(ia_hat_vec(1), min(ia_hat_vec(end), ia/i_sum));
            ib_h  = max(ib_hat_vec(1), min(ib_hat_vec(end), ib/i_sum));

            d1_idx = max(1, min(N_duty, round(interp1(da_vec, 1:N_duty, da, 'linear', 'extrap'))));
            d2_idx = max(1, min(N_duty, round(interp1(db_vec, 1:N_duty, db, 'linear', 'extrap'))));

            phi_b_i = interp2(ia_hat_vec, ib_hat_vec, ...
                LUT_theta_b(:,:,d1_idx,d2_idx)', ia_h, ib_h, 'linear', 0);
            phi_c_i = interp2(ia_hat_vec, ib_hat_vec, ...
                LUT_theta_c(:,:,d1_idx,d2_idx)', ia_h, ib_h, 'linear', 0);

            [Ic_prop(k), ~, ~] = compute_switching_rms(ia, ib, ic, da, db, dc, ...
                phi_b_i, phi_c_i, t_sw, Tsw, ESR, ESL, C_dc);
        end

        Irms_conv_map(pf_idx, ma_idx) = sqrt(mean(Ic_conv.^2));
        Irms_prop_map(pf_idx, ma_idx) = sqrt(mean(Ic_prop.^2));
    end
    fprintf('  PF = %.2f done.\n', pf_vec(pf_idx));
end

%% =========================================================================
%  SECTION 6: VISUALIZATION
%  =========================================================================

fprintf('\n=== Generating Plots ===\n');

c_conv     = [0.85, 0.2, 0.2];
c_prop     = [0.1,  0.5, 0.8];
theta_axis = linspace(0, 360, Nsw);

% --- Figure 1: Capacitor Impedance ---
figure('Name','Capacitor Impedance','Position',[50 50 800 400]);
subplot(1,2,1);
loglog(f_freq, abs(Z_cap), 'k-', 'LineWidth', 2);
xline(f_res, '--r', 'LineWidth', 1.5);
text(f_res*1.2, max(abs(Z_cap))*0.3, sprintf('f_{res}=%.1fkHz',f_res/1e3), ...
    'Color','r','FontSize',9);
xlabel('Frequency [Hz]'); ylabel('|Z_{cap}| [\Omega]');
title('DC-Link Capacitor Impedance');
grid on; set(gca,'FontSize',10);
legend(sprintf('C=%.0fuF, ESR=%.1fmΩ, ESL=%.0fnH',C_dc*1e6,ESR*1e3,ESL*1e9), ...
    'Location','NorthWest');

subplot(1,2,2);
semilogx(f_freq, angle(Z_cap)*180/pi, 'k-', 'LineWidth', 2);
xline(f_res, '--r', 'LineWidth', 1.5);
xlabel('Frequency [Hz]'); ylabel('Phase [deg]');
title('Capacitor Impedance Phase');
grid on; set(gca,'FontSize',10); ylim([-95 95]);
yticks([-90 -45 0 45 90]);

% --- Figure 2: Switching-period RMS over fundamental period ---
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
title('ESL Voltage Stress  (v = L_{ESL} \cdot di/dt)');
legend('Conventional','Proposed','Location','NorthEast');
grid on; set(gca,'FontSize',10);

subplot(2,2,4);
reduction_per_interval = (1 - Irms_prop ./ (Irms_conv + 1e-10)) * 100;
plot(theta_axis, reduction_per_interval, 'Color', [0.2 0.65 0.3], 'LineWidth', 1.5);
yline(reduction_pct, '--k', sprintf('Avg=%.1f%%',reduction_pct), 'LineWidth', 1);
xlabel('Fundamental Phase [°]'); ylabel('RMS Reduction [%]');
title('Per-Interval RMS Reduction');
ylim([0 60]); grid on; set(gca,'FontSize',10);

sgtitle(sprintf('m_a=%.2f, PF=%.2f | C=%.0fuF, ESR=%.0fmΩ, ESL=%.0fnH, L_{bat}=%.0fuH', ...
    ma, cos(pf_angle), C_dc*1e6, ESR*1e3, ESL*1e9, L_bat*1e6), ...
    'FontSize',11,'FontWeight','bold');

% --- Figure 3: RMS Map (Fig. 7 equivalent) ---
figure('Name','RMS Current Map','Position',[100 150 1100 400]);

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

sgtitle('DC-Link RMS Current Map: Conventional vs. Proposed (with ESR/ESL/L_{bat})', ...
    'FontSize',11,'FontWeight','bold');

% --- Figure 4: Parasitic Sensitivity ---
figure('Name','Parasitic Sensitivity','Position',[150 200 900 350]);

ESR_range = logspace(-3, -1, 20);
ESL_range = logspace(-9, -6, 20);

k_test  = round(Nsw/4);
theta_k = 2*pi*k_test/Nsw;
da_s = max(0.01,min(0.99, 0.5+0.5*ma*cos(theta_k)));
db_s = max(0.01,min(0.99, 0.5+0.5*ma*cos(theta_k-2*pi/3)));
dc_s = max(0.01,min(0.99, 1.5-da_s-db_s));
ia_s = Ipp*cos(theta_k-pf_angle);
ib_s = Ipp*cos(theta_k-2*pi/3-pf_angle);
ic_s = Ipp*cos(theta_k+2*pi/3-pf_angle);

V_peak_esr = zeros(1,length(ESR_range));
V_peak_esl = zeros(1,length(ESL_range));

for ei = 1:length(ESR_range)
    [~, Vc, ~] = compute_switching_rms(ia_s,ib_s,ic_s,da_s,db_s,dc_s, ...
        0,0,t_sw,Tsw,ESR_range(ei),ESL,C_dc);
    V_peak_esr(ei) = Vc;
end
for li = 1:length(ESL_range)
    [~,~,Vesl] = compute_switching_rms(ia_s,ib_s,ic_s,da_s,db_s,dc_s, ...
        0,0,t_sw,Tsw,ESR,ESL_range(li),C_dc);
    V_peak_esl(li) = Vesl;
end

subplot(1,2,1);
semilogx(ESR_range*1e3, V_peak_esr*1e3, 'b-o', 'LineWidth', 1.5, 'MarkerSize', 4);
xline(ESR*1e3,'--r','Nominal','LineWidth',1);
xlabel('ESR [m\Omega]'); ylabel('V_{cap,rms} [mV]');
title('Capacitor Voltage Ripple vs. ESR');
grid on; set(gca,'FontSize',10);

subplot(1,2,2);
loglog(ESL_range*1e9, V_peak_esl*1e3, 'r-o', 'LineWidth', 1.5, 'MarkerSize', 4);
xline(ESL*1e9,'--b','Nominal','LineWidth',1);
xlabel('ESL [nH]'); ylabel('V_{ESL,rms} [mV]');
title('ESL Voltage Stress vs. Inductance');
grid on; set(gca,'FontSize',10);

sgtitle('Parasitic Sensitivity Analysis (DC-Link Capacitor)', ...
    'FontSize',11,'FontWeight','bold');

%% =========================================================================
%  SECTION 7: SUMMARY
%  =========================================================================

fprintf('\n========================================================\n');
fprintf('  SIMULATION SUMMARY\n');
fprintf('========================================================\n');
fprintf('  Operating point:  m_a=%.2f, PF=%.2f\n', ma, cos(pf_angle));
fprintf('  Switching freq:   %.1f kHz\n', fsw/1e3);
fprintf('  -------------------------------------------------------\n');
fprintf('  C_dc      %.1f uF\n',   C_dc*1e6);
fprintf('  ESR       %.1f mOhm\n', ESR*1e3);
fprintf('  ESL       %.1f nH\n',   ESL*1e9);
fprintf('  L_bat     %.1f uH\n',   L_bat*1e6);
fprintf('  R_bat     %.1f mOhm\n', R_bat*1e3);
fprintf('  -------------------------------------------------------\n');
fprintf('  Conventional RMS:  %.4f p.u.\n', Icap_conv_total);
fprintf('  Proposed RMS:      %.4f p.u.\n', Icap_prop_total);
fprintf('  RMS Reduction:     %.1f%%\n',    reduction_pct);
fprintf('========================================================\n');
fprintf('\nTip: Increase N_curr, N_duty, N_phase for finer LUT.\n');
fprintf('     Increase Npts for higher waveform resolution.\n\n');

%% =========================================================================
%  LOCAL FUNCTIONS  –  must appear at the END of a MATLAB script
%  =========================================================================

function [Irms, Vrms_cap, Vrms_esl] = compute_switching_rms(ia, ib, ic, ...
        da, db, dc, phi_b, phi_c, t_sw, Tsw, ESR, ESL, C_dc)
% COMPUTE_SWITCHING_RMS  Switching-period RMS + parasitic voltage terms
%
%   Implements Eq. 5 from paper, extended with ESR and ESL voltage terms.
%
%   Inputs:
%     ia, ib, ic   - quasi-static phase currents [p.u.]
%     da, db, dc   - duty cycles for legs A, B, C
%     phi_b, phi_c - carrier phase shifts for legs B and C [rad]
%     t_sw         - time vector for one switching period
%     Tsw          - switching period [s]
%     ESR          - capacitor series resistance [Ohm]
%     ESL          - capacitor series inductance [H]
%     C_dc         - capacitance [F]
%
%   Outputs:
%     Irms     - RMS capacitor current [p.u.]
%     Vrms_cap - RMS voltage across pure capacitance [V·p.u.]
%     Vrms_esl - RMS voltage across ESL [V·p.u.]

    dt = Tsw / length(t_sw);

    % Switching functions for each leg (Eq. 4)
    Sa = double(mod(t_sw/Tsw,                   1) < da);
    Sb = double(mod(t_sw/Tsw - phi_b/(2*pi),    1) < db);
    Sc = double(mod(t_sw/Tsw - phi_c/(2*pi),    1) < dc);

    % Capacitor current (Eq. 1): remove DC component
    i_inv = ia*Sa + ib*Sb + ic*Sc;
    icap  = i_inv - mean(i_inv);

    % RMS capacitor current
    Irms  = sqrt(mean(icap.^2));

    % Voltage across pure capacitance
    v_C  = cumsum(icap * dt) / C_dc;
    v_C  = v_C - mean(v_C);

    % ESL voltage: v_ESL = L * d(icap)/dt
    v_ESL = ESL * gradient(icap, dt);

    Vrms_cap = sqrt(mean(v_C.^2));
    Vrms_esl = sqrt(mean(v_ESL.^2));
end

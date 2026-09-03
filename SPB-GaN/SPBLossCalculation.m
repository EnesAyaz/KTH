%% SPB datasheet-based sizing and loss calculation
% This script calculates:
% 1) required number of SPB series modules, Ns
% 2) required number of parallel devices per switch, Np
% 3) conduction loss, switching loss, total loss
% 4) efficiency versus switching frequency

clear; clc; close all;

%% =========================
%  USER INPUTS
% ==========================

% System requirements
Vdc_total   = 1200;      % Total DC-link voltage [V]
Pout        = 300e3;     % Output mechanical/electrical power [W]
pf          = 1;      % Power factor [-]
M           = 1;      % Modulation index [-]
eta_guess   = 0.98;      % Initial efficiency guess for current estimation [-]

% Safety margins
voltage_margin = 1.2;    % Voltage safety margin, e.g. 1.5 means 50% margin
current_margin = 3;   % Current derating margin
post_fault_N_1 = true;   % true: check voltage after one series module is bypassed

%% EPC2304 datasheet parameters

% Device ratings
Vdev_rating = 200;       % [V] Continuous drain-source voltage
Idev_rating = 133;       % [A] Continuous drain current, TJ <= 125 C

% On-state resistance
Rds_25_mOhm = 3.3;         % [mOhm] max Rds(on), VGS = 5 V, ID = 30 A

% Temperature dependence
% From normalized Rds(on) figure: roughly 1.8x at 150 C compared with 25 C
alpha_Rds = 0.0064;      % [1/C] approximate: (1.8 - 1)/(150 - 25)

% Thermal parameters
Tj_max = 150;            % [C]
Rth_JC = 0.2;            % [C/W] junction-to-case
Rth_CH = 0.1;            % [C/W] assumed TIM/contact resistance
Rth_HA = 0.005;          % [C/W] assumed shared heatsink/coolant resistance

% Switching energy reference point
% Datasheet gives switching waveform condition:
% VIN = 160 V, IL = 25 A, RGon = 1 ohm, RGoff = 0 ohm
Vref_E = 160;            % [V]
Iref_E = 25;             % [A]

% EPC2304 datasheet does not directly give Eon/Eoff table values.
% Use these as first estimation values only.
Eon_mJ = 25e-3*0.4;           % [mJ] assumed initial value
Eoff_mJ = 10e-3*0.4;          % [mJ] assumed initial value
I_exp = 1.0;             % linear current scaling


% Thermal parameters
Tamb        = 65;        % Ambient/coolant temperature [C]

% Switching frequency sweep
fsw_min = 100e3;           % Minimum switching frequency [Hz]
fsw_max = 1000e3;         % Maximum switching frequency [Hz]
fsw_step = 50e3;          % Step [Hz]
fsw_vec = fsw_min:fsw_step:fsw_max;

%% =========================
%  CALCULATION
% ==========================

result = calculate_spb_loss( ...
    Vdc_total, Pout, pf, M, eta_guess, ...
    voltage_margin, current_margin, post_fault_N_1, ...
    Vdev_rating, Idev_rating, ...
    Rds_25_mOhm, alpha_Rds, ...
    Eon_mJ, Eoff_mJ, Vref_E, Iref_E, I_exp, ...
    Tamb, Tj_max, Rth_JC, Rth_CH, Rth_HA, fsw_vec);

%% =========================
%  PRINT NOMINAL RESULT
% ==========================

[~, idx_nom] = min(abs(fsw_vec - 20e3));   % show result close to 20 kHz

fprintf('\n===== SPB Sizing Result at %.1f kHz =====\n', fsw_vec(idx_nom)/1e3);
fprintf('Required series modules, Ns           = %d\n', result.Ns(idx_nom));
fprintf('Required parallel devices, Np         = %d\n', result.Np(idx_nom));
fprintf('Voltage per SPB module                = %.1f V\n', result.Vmodule(idx_nom));
fprintf('Estimated phase RMS current per module= %.1f A\n', result.Iphase_rms(idx_nom));
fprintf('Conduction loss                       = %.1f W\n', result.Pcond(idx_nom));
fprintf('Switching loss                        = %.1f W\n', result.Psw(idx_nom));
fprintf('Total semiconductor loss              = %.1f W\n', result.Ploss(idx_nom));
fprintf('Efficiency                            = %.3f %%\n', result.eta(idx_nom)*100);
fprintf('Estimated junction temperature         = %.1f C\n', result.Tj(idx_nom));
fprintf('Feasible                              = %s\n', string(result.feasible(idx_nom)));

%% =========================
%  TABLE
% ==========================

T = table( ...
    result.fsw(:)/1e3, ...
    result.Ns(:), ...
    result.Np(:), ...
    result.Vmodule(:), ...
    result.Iphase_rms(:), ...
    result.Pcond(:), ...
    result.Psw(:), ...
    result.Ploss(:), ...
    result.eta(:)*100, ...
    result.Tj(:), ...
    result.feasible(:), ...
    'VariableNames', {'fsw_kHz','Ns','Np','Vmodule_V','Iphase_rms_A', ...
    'Pcond_W','Psw_W','Ploss_W','Efficiency_percent','Tj_C','Feasible'});

disp(T);

%% =========================
%  PLOTS
% ==========================

figure;
plot(result.fsw/1e3, result.eta*100, 'LineWidth', 2);
grid on;
xlabel('Switching frequency [kHz]');
ylabel('Efficiency [%]');
title('SPB inverter efficiency vs switching frequency');

figure;
plot(result.fsw/1e3, result.Pcond, 'LineWidth', 2); hold on;
plot(result.fsw/1e3, result.Psw, 'LineWidth', 2);
plot(result.fsw/1e3, result.Ploss, 'LineWidth', 2);
grid on;
xlabel('Switching frequency [kHz]');
ylabel('Loss [W]');
title('SPB inverter loss breakdown vs switching frequency');
legend('Conduction loss','Switching loss','Total loss','Location','northwest');

figure;
plot(result.fsw/1e3, result.Tj, 'LineWidth', 2); hold on;
yline(Tj_max, '--', 'Tj max');
grid on;
xlabel('Switching frequency [kHz]');
ylabel('Estimated junction temperature [C]');
title('Estimated junction temperature vs switching frequency');

%% ============================================================
%  LOCAL FUNCTION
% ============================================================

function result = calculate_spb_loss( ...
    Vdc_total, Pout, pf, M, eta_guess, ...
    voltage_margin, current_margin, post_fault_N_1, ...
    Vdev_rating, Idev_rating, ...
    Rds_25_mOhm, alpha_Rds, ...
    Eon_mJ, Eoff_mJ, Vref_E, Iref_E, I_exp, ...
    Tamb, Tj_max, Rth_JC, Rth_CH, Rth_HA, fsw_vec)

    % Convert units
    Rds_25 = Rds_25_mOhm * 1e-3;      % [ohm]
    Eon = Eon_mJ * 1e-3;              % [J]
    Eoff = Eoff_mJ * 1e-3;            % [J]
    Esw_ref = Eon + Eoff;             % [J]

    n = length(fsw_vec);

    Ns = zeros(1,n);
    Np = zeros(1,n);
    Vmodule = zeros(1,n);
    Iphase_rms = zeros(1,n);
    Pcond = zeros(1,n);
    Psw = zeros(1,n);
    Ploss = zeros(1,n);
    eta = zeros(1,n);
    Tj = zeros(1,n);
    feasible = false(1,n);

    %% Required series module count from voltage rating

    if post_fault_N_1
        % After one module is bypassed:
        % Vdc_total/(Ns-1) * voltage_margin <= Vdev_rating
        Ns_req = ceil(Vdc_total * voltage_margin / Vdev_rating + 1);
    else
        % Normal operation:
        % Vdc_total/Ns * voltage_margin <= Vdev_rating
        Ns_req = ceil(Vdc_total * voltage_margin / Vdev_rating);
    end

    Ns_req = max(Ns_req, 1);

    %% Current estimation
    % Fundamental line-line RMS voltage for each module:
    % VLL_rms_module = sqrt(3)/(2*sqrt(2)) * M * Vmodule
    %
    % Power per module:
    % Pmodule = Pout / Ns
    %
    % Iphase_rms = Pmodule / (sqrt(3)*VLL_rms_module*pf*eta)
    %
    % Because Vmodule = Vdc_total/Ns, Ns approximately cancels out.

    for k = 1:n

        fsw = fsw_vec(k);

        Ns(k) = Ns_req;
        Vmodule(k) = Vdc_total / Ns(k);

        Pmodule = Pout / Ns(k);
        VLL_rms_module = sqrt(3)/(2*sqrt(2)) * M * Vmodule(k);

        Iphase_rms(k) = Pmodule / (sqrt(3) * VLL_rms_module * pf * eta_guess);

        %% Required parallel devices from current rating
        Np(k) = ceil(Iphase_rms(k) * current_margin / Idev_rating);
        Np(k) = max(Np(k), 1);

        %% Iterative thermal-loss calculation
        Tj_est = Tamb + 25;

        for iter = 1:10

            % Temperature-dependent Rds(on)
            Rds_T = Rds_25 * (1 + alpha_Rds * (Tj_est - 25));

            % Effective Rds per switch with Np devices in parallel
            Rds_eff = Rds_T / Np(k);

            % Total conduction loss:
            % For one 3-phase two-level bridge:
            % Pcond_module ≈ 3 * Irms^2 * Rds_eff
            Pcond_module = 3 * Iphase_rms(k)^2 * Rds_eff;

            % Total conduction loss for all SPB modules
            Pcond_temp = Ns(k) * Pcond_module;

            % Current per parallel device
            I_per_device = Iphase_rms(k) / Np(k);

            % Switching energy scaling
            Esw = Esw_ref ...
                * (Vmodule(k) / Vref_E) ...
                * (I_per_device / Iref_E)^I_exp;

            % Total switching loss:
            % six switches per 3-phase module
            Psw_module = 6 * Np(k) * Esw * fsw;
            Psw_temp = Ns(k) * Psw_module;

            Ploss_temp = Pcond_temp + Psw_temp;

            % Approximate per-device loss
            Pcond_per_device = Pcond_temp / (Ns(k) * 6 * Np(k));
            Psw_per_device   = Psw_temp   / (Ns(k) * 6 * Np(k));
            Pdevice = Pcond_per_device + Psw_per_device;

            % Junction temperature estimate
            Tcase_sink = Tamb + Ploss_temp * Rth_HA;
            Tj_new = Tcase_sink + Pdevice * (Rth_JC + Rth_CH);

            Tj_est = 0.5*Tj_est + 0.5*Tj_new;
        end

        Pcond(k) = Pcond_temp;
        Psw(k) = Psw_temp;
        Ploss(k) = Ploss_temp;
        eta(k) = Pout / (Pout + Ploss(k));
        Tj(k) = Tj_est;

        %% Feasibility checks

        if post_fault_N_1
            voltage_ok = (Vdc_total / (Ns(k)-1) * voltage_margin) <= Vdev_rating;
        else
            voltage_ok = (Vmodule(k) * voltage_margin) <= Vdev_rating;
        end

        current_ok = (Iphase_rms(k) * current_margin / Np(k)) <= Idev_rating;
        thermal_ok = Tj(k) <= Tj_max;

        feasible(k) = voltage_ok && current_ok && thermal_ok;
    end

    %% Store output

    result.fsw = fsw_vec;
    result.Ns = Ns;
    result.Np = Np;
    result.Vmodule = Vmodule;
    result.Iphase_rms = Iphase_rms;
    result.Pcond = Pcond;
    result.Psw = Psw;
    result.Ploss = Ploss;
    result.eta = eta;
    result.Tj = Tj;
    result.feasible = feasible;
end
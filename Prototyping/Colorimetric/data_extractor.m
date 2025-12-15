
%% ===================== RAW DATA ==========================
% Current values (A)
I_all = [
    100
    150
    200
     50
     50
    100
    150
    200
     50
    100
    150
    200
];
% Switching frequencies (kHz)
f_all_kHz = [
    19
    19
    19
    10
    19
    10
    10
    10
    15
    15
    15
    15
];
% Calorimetric steady-state TOTAL losses (W)
P_all = [
    3105.001034
    4948.411861
    7791.58566
     998.7043384
    1542.684099
    2030.243638
    2870.146249
    4404.48126
    1200.128389
    2395.111488
    3849.947385
    5944.016711
];

% Cold-plate outlet temperatures (°C)
T_cp_out = [
    41.20849888
    50.15549033
    67.66860358
    28.91730558
    32.44023337
    34.51436755
    40.7807326
    48.30766936
    31.27306127
    38.4723617
    45.83666894
    57.57382727
];
% Cold-plate inlet temperatures (°C)
T_cp_in = [
    28.55608022
    30.34059967
    35.77528507
    24.88209801
    26.28232305
    26.20002468
    28.93992376
    30.22947461
    26.41143851
    28.74525032
    29.96148137
    33.38701583
];
% Use average cold-plate temp for model
T_cp_all = (T_cp_out + T_cp_in) / 2;

% T_cp_all=T_cp_out;

freqs_to_remove = [10];
mask = ~ismember(f_all_kHz, freqs_to_remove);

% Make sure everything is column vectors
I_all      = I_all(mask);
f_all_kHz  = f_all_kHz(mask);
P_all      = P_all(mask);
T_cp_all   = T_cp_all(mask);


% Convert frequency kHz -> Hz
f_all = f_all_kHz * 1e3;


%% =============== FIXED DEVICE / SYSTEM PARAMETERS ================
% >>> Set these from datasheet as far as possible <<<

% Effective Rds(on) per leg at reference temperature
R0   = 2.6e-3;      % [Ohm]  <-- ADJUST FROM DATASHEET / DESIGN

% Temperature coefficient of Rds(on) [1/K]
alpha_R = 0.0115;  % [1/K]  <-- ADJUST
% alpha_R=0.0133; %%for 175 

% Reference temperature for R0
Tref = 25;        % [°C]

% DC-link voltage
Vdc  = 1200;      % [V]    <-- ADJUST if different

% Number of legs contributing to P_all (6-phase inverter)
Nlegs = 6;

% Pack constants
params.R0      = R0;
params.alpha_R = alpha_R;
params.Tref    = Tref;
params.Vdc     = Vdc;
params.Nlegs   = Nlegs;


%% ================== PARAMETER IDENTIFICATION ======================
% Identify: theta = [kappa1, alpha1, alpha2, Coss_eq]

% Initial guesses
kappa1_0 = 0.05;      % K/W
alpha1_0 = 1e-6;      % J/A
alpha2_0 = 1e-8;      % J/A^2
Coss_0   = 1.25e-9;   % F

theta0 = [kappa1_0, alpha1_0, alpha2_0, Coss_0];

% Bounds
lb = [0,   0,      0,      0];
ub = [1, Inf,   Inf,   Inf];

% Xdata = [I, f_sw, T_cp]
Xdata = [I_all, f_all, T_cp_all];

% Objective: model total loss
loss_model = @(theta, X) loss_model_fun(theta, X, params);

opts = optimoptions('lsqcurvefit', ...
    'Display','iter', ...
    'TolFun',1e-12, ...
    'TolX',1e-12);

[theta_opt, P_model, residual, exitflag, output] = lsqcurvefit( ...
    loss_model, theta0, Xdata, P_all, lb, ub, opts);

kappa1_opt = theta_opt(1);
alpha1_opt = theta_opt(2);
alpha2_opt = theta_opt(3);
Coss_opt   = theta_opt(4);

fprintf('\n=== Identified Parameters ===\n');
fprintf('kappa1   = %.4g K/W\n',   kappa1_opt);
fprintf('alpha1   = %.4g J/A\n',   alpha1_opt);
fprintf('alpha2   = %.4g J/A^2\n', alpha2_opt);
fprintf('Coss_eq  = %.4g F\n',     Coss_opt);

% Global RMSE
rmse = sqrt(mean((P_model - P_all).^2));
fprintf('Global RMSE between model and measurements: %.2f W\n', rmse);


%% ==== SEPARATE CONDUCTION & SWITCHING LOSSES + PER-POINT ERRORS ===
[P_cond_tot, P_sw_tot, Tj_all] = separate_losses(theta_opt, I_all, f_all, T_cp_all, params);

P_tot_sep = P_cond_tot + P_sw_tot;  % should be very close to P_model

% Per-point errors
err_abs = P_tot_sep - P_all;              % [W] (model - meas)
err_rel = 100 * err_abs ./ P_all;         % [%]

fprintf('\nPoint  I(A)  f(kHz)  P_meas  P_model  P_cond  P_sw    Tj(C)   err_abs  err_rel(%%)\n');
for k = 1:numel(I_all)
    fprintf('%3d   %3d   %7.1f  %7.1f  %7.1f  %7.1f  %7.1f  %8.1f  %8.2f\n', ...
        I_all(k), round(f_all_kHz(k)), ...
        P_all(k), P_tot_sep(k), ...
        P_cond_tot(k), P_sw_tot(k), ...
        Tj_all(k), err_abs(k), err_rel(k));
end

%% ===== TABLE WITH ERRORS (this is what you asked for) =============
results_loss = table( ...
    I_all, ...
    f_all_kHz, ...
    T_cp_all, ...
    P_all, ...
    P_tot_sep, ...
    P_cond_tot, ...
    P_sw_tot, ...
    Tj_all, ...
    err_abs, ...
    err_rel, ...
    'VariableNames', { ...
        'I_A', ...
        'f_sw_kHz', ...
        'T_cp_C', ...
        'P_meas_W', ...
        'P_model_W', ...
        'P_cond_W', ...
        'P_sw_W', ...
        'Tj_C', ...
        'Err_abs_W', ...
        'Err_rel_percent'});

disp(results_loss);

% If you want, save it to Excel:
% writetable(results_loss, 'loss_fit_results.xlsx');


%% ================== PLOTS (optional) ==============================
% 1) Measured vs modeled total loss
figure;
plot(P_all, P_tot_sep, 'o', 'LineWidth', 2); hold on; grid on;
plot([min(P_all) max(P_all)], [min(P_all) max(P_all)], 'k--');
xlabel('Measured total loss P_{meas} [W]');
ylabel('Modelled total loss P_{model} [W]');
title('Calorimetric vs Modelled Loss');
axis equal;

% 2) Conduction vs switching (3D scatter)
figure; hold on; grid on;
scatter3(I_all, f_all_kHz, P_cond_tot, 60, 'b', 'filled');
scatter3(I_all, f_all_kHz, P_sw_tot,  60, 'r', 'filled');
xlabel('Current [A]');
ylabel('f_{sw} [kHz]');
zlabel('Loss [W]');
legend('Conduction', 'Switching');
title('Separated Conduction and Switching Losses');

% 3) Surfaces (if you like)
I_vals = unique(I_all);
f_vals = unique(f_all_kHz);
[I_grid, F_grid] = meshgrid(I_vals, f_vals);
P_tot_grid  = NaN(size(I_grid));
P_cond_grid = NaN(size(I_grid));
P_sw_grid   = NaN(size(I_grid));

for i = 1:numel(I_vals)
    for j = 1:numel(f_vals)
        idx = (I_all == I_vals(i)) & (f_all_kHz == f_vals(j));
        if any(idx)
            P_tot_grid(j,i)  = P_tot_sep(idx);
            P_cond_grid(j,i) = P_cond_tot(idx);
            P_sw_grid(j,i)   = P_sw_tot(idx);
        end
    end
end

figure;
surf(I_grid, F_grid, P_tot_grid); shading interp; colorbar;
xlabel('Current [A]'); ylabel('f_{sw} [kHz]'); zlabel('P_{tot} [W]');
title('Total Loss Surface (Model)');

figure;
surf(I_grid, F_grid, P_cond_grid); shading interp; colorbar;
xlabel('Current [A]'); ylabel('f_{sw} [kHz]'); zlabel('P_{cond} [W]');
title('Conduction Loss Surface (Model)');

figure;
surf(I_grid, F_grid, P_sw_grid); shading interp; colorbar;
xlabel('Current [A]'); ylabel('f_{sw} [kHz]'); zlabel('P_{sw} [W]');
title('Switching Loss Surface (Model)');


%%

figure;
hold on; grid on;
freqs = unique(f_all_kHz);    % e.g. [7 15 19]

for k = 1:numel(freqs)
    f = freqs(k);
    idx = (f_all_kHz == f);

    I_tmp  = I_all(idx);
    P_sw_tmp = P_sw_tot(idx);

    % sort by current for nice line
    [I_sorted, order] = sort(I_tmp);
    P_sw_sorted = P_sw_tmp(order);

    plot(I_sorted, P_sw_sorted, '-o', 'LineWidth', 2, ...
        'DisplayName', sprintf('%d kHz', f));
end

xlabel('Current I_{RMS} [A]');
ylabel('Switching loss P_{sw,tot} [W]');
title('Switching Loss vs Current for Different Switching Frequencies');
legend('Location','northwest');


%% ============ I vs CONDUCTION LOSS for each f_sw ================
figure; hold on; grid on;

for k = 1:numel(freqs)
    f = freqs(k);
    idx = (f_all_kHz == f);

    I_tmp  = I_all(idx);
    P_cond_tmp = P_cond_tot(idx);

    [I_sorted, order] = sort(I_tmp);
    P_cond_sorted = P_cond_tmp(order);

    plot(I_sorted, P_cond_sorted, '-o', 'LineWidth', 2, ...
        'DisplayName', sprintf('%d kHz', f));
end

xlabel('Current I_{RMS} [A]');
ylabel('Conduction loss P_{cond,tot} [W]');
title('Conduction Loss vs Current for Different Switching Frequencies');
legend('Location','northwest');




%% ================== LOCAL FUNCTIONS ===============================
function P_tot_model = loss_model_fun(theta, X, params)
    % theta = [kappa1, alpha1, alpha2, Coss_eq]
    kappa1 = theta(1);
    alpha1 = theta(2);
    alpha2 = theta(3);
    Coss   = theta(4);

    I    = X(:,1);   % RMS current [A]
    f_sw = X(:,2);   % switching frequency [Hz]
    T_cp = X(:,3);   % cold-plate temp [°C]

    R0      = params.R0;
    alpha_R = params.alpha_R;
    Tref    = params.Tref;
    Vdc     = params.Vdc;
    Nlegs   = params.Nlegs;

    % First pass: assume Tj ≈ T_cp
    Tj = T_cp;
    Rds = R0 .* (1 + alpha_R .* (Tj - Tref));
    P_cond_leg = Rds .* (I.^2);
    P_sw_leg   = f_sw .* (alpha1 .* abs(I) + alpha2 .* (I.^2) + 0.5 .* Coss .* Vdc.^2);
    P_tot_model = Nlegs .* (P_cond_leg + P_sw_leg);

    % Second pass: update Tj with kappa1 * P_tot_model
    Tj = T_cp + kappa1 .* P_tot_model;
    Rds = R0 .* (1 + alpha_R .* (Tj - Tref));
    P_cond_leg = Rds .* (I.^2);
    P_sw_leg   = f_sw .* (alpha1 .* abs(I) + alpha2 .* (I.^2) + 0.5 .* Coss .* Vdc.^2);
    P_tot_model = Nlegs .* (P_cond_leg + P_sw_leg);
end

function [P_cond_tot, P_sw_tot, Tj] = separate_losses(theta, I, f_sw, T_cp, params)
    kappa1 = theta(1);
    alpha1 = theta(2);
    alpha2 = theta(3);
    Coss   = theta(4);

    R0      = params.R0;
    alpha_R = params.alpha_R;
    Tref    = params.Tref;
    Vdc     = params.Vdc;
    Nlegs   = params.Nlegs;

    % Initial Tj from T_cp
    Tj0 = T_cp;
    Rds0 = R0 .* (1 + alpha_R .* (Tj0 - Tref));
    P_cond_leg0 = Rds0 .* (I.^2);
    P_sw_leg0   = f_sw .* (alpha1 .* abs(I) + alpha2 .* (I.^2) + 0.5 .* Coss .* Vdc.^2);
    P_tot0      = Nlegs .* (P_cond_leg0 + P_sw_leg0);

    % Updated Tj with kappa1
    Tj = T_cp + kappa1 .* P_tot0;

    % Final conduction and switching losses
    Rds = R0 .* (1 + alpha_R .* (Tj - Tref));
    P_cond_leg = Rds .* (I.^2);
    P_sw_leg   = f_sw .* (alpha1 .* abs(I) + alpha2 .* (I.^2) + 0.5 .* Coss .* Vdc.^2);

    P_cond_tot = Nlegs .* P_cond_leg;
    P_sw_tot   = Nlegs .* P_sw_leg;
end

%%
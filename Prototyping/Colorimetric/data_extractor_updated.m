
%% SAVE RESULTS WITH AUTO-INCREMENTED FILENAME
outFolder = 'C:\Github\KTH\Prototyping\Colorimetric';
baseName  = 'steady_state_calo_roundedIF_';
ext       = '.xlsx';
n=3;
outFile = fullfile(outFolder, [baseName, num2str(n), ext]);

%% ========================================================================
%  PART 2: READ SUMMARY EXCEL, BUILD ARRAYS, AND PLOT
% ====================================================================== %%

% Use the file we just saved:
fname_summary = outFile;
Tsum = readtable(fname_summary);

% Column vectors
I_set   = Tsum.I_set_A;
f_sw    = Tsum.f_sw_kHz;
P_cal   = Tsum.P_cal_ss_W;
T_in_ss = Tsum.T_in_ss_degC;
T_out_ss= Tsum.T_out_ss_degC;

% === EXCLUDE specific switching frequencies ===
exclude_f = [];      % <-- change to whatever you want to skip
keep_idx = ~ismember(f_sw, exclude_f);

I_all   = I_set(keep_idx);
f_all_kHz  = f_sw(keep_idx);
P_all   = P_cal(keep_idx);
T_cp_in = T_in_ss(keep_idx);
T_cp_out= T_out_ss(keep_idx);

% Use average cold-plate temp for model
T_cp_all = (T_cp_out + T_cp_in) / 2;

% T_cp_all=T_cp_out;

% Convert frequency kHz -> Hz
f_all = f_all_kHz * 1e3;


%% =============== FIXED DEVICE / SYSTEM PARAMETERS ================
% >>> Set these from datasheet as far as possible <<<

% Effective Rds(on) per leg at reference temperature
R0 = 3.3e-3;      % [Ohm]  <-- ADJUST FROM DATASHEET / DESIGN

% Temperature coefficient of Rds(on) [1/K]
alpha_R = 0.0115;  % [1/K]  <-- ADJUST
%alpha_R=0.0133; %%for 175 


% Reference temperature for R0
Tref = 25;        % [°C]

% DC-link voltage
Vdc  = 1200;      % [V]    <-- ADJUST if different

% Number of legs contributing to P_all (6-phase inverter)
Nlegs = 6;
% P_all=P_all/Nlegs;
% Nlegs=1;

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
%%
%% --------------------------------------
%   BLUE GRADIENT COLORMAP (same style)
%% --------------------------------------
% blue colormap for η maps
nC = 256; stops = [1 1 1; 0.92 0.95 0.98; 0.75 0.84 0.93; 0.56 0.70 0.86; 0.36 0.54 0.75; 0.18 0.32 0.52];
xi = linspace(0,1,size(stops,1)); cmapBlue = interp1(xi, stops, linspace(0,1,nC));
eta_caxis   = [98.4 99.6];

figure('Color','w','Position',[160 90 940 480],'Renderer','painters');
t = tiledlayout(1,1,'Padding','compact','TileSpacing','compact');

font_axes = 20;
font_title = 20;
font_cb = 20;

nexttile;
contourf(I_grid, F_grid, 100*(3*I_grid*600/sqrt(2)-P_tot_grid/2)./(3*I_grid*600/sqrt(2)),4, 'LineStyle','none');   % 20 levels, no lines
colormap(gca, cmapBlue);
%caxis([]);     % <<< Set colorbar (and contour) range here
caxis(eta_caxis);
colorbar;

% --- Formatting ---
% title('Ef Map', 'FontSize', font_title, 'FontWeight','normal');
xlabel('Phase Current [A_{RMS}]', 'FontSize', font_axes, 'FontName','Times New Roman');
ylabel('Switching Frequency [kHz]', 'FontSize', font_axes, 'FontName','Times New Roman');

set(gca,'FontName','Times New Roman','FontSize',font_axes,...
        'Layer','top','TickDir','out','Box','on');

% Optional: control color range
%caxis([minValue  maxValue])
cb = colorbar('eastoutside');
ylabel(cb, 'Efficiency (%)', 'FontSize', font_cb, 'FontName','Times New Roman');
set(cb,'FontSize',font_cb);


%%
figure;
surf(I_grid, F_grid, P_cond_grid); shading interp; colorbar;
xlabel('Current [A]'); ylabel('f_{sw} [kHz]'); zlabel('P_{cond} [W]');
title('Conduction Loss Surface (Model)');
%%
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
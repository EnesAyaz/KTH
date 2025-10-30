%% ============================================
%  η(A_die, f_sw) COMPARISON with SCALING (no 1.2 kV datasheet)
%  Case A: Udc=1200 V, Ub=2.0 kV  (2 kV device)  ← calibrates per-area FoMs
%  Case B: Udc=800  V, Ub=1.2 kV  (1.2 kV device) ← reuses per-area FoMs
%  Constant dv/dt and di/dt for both cases
%  ============================================
clear; clc; close all;

%% ---------------- Base calibration on 2 kV device (Case A) ----------------
S_A.device.name   = 'Ref: 2 kV SiC (FF3MR20KM1H_S)';
S_A.Udc           = 1200;          % V (DC-link)
S_A.Ub_kV         = 2.0;           % kV (VDSS)
S_A.ffund         = 500;           % Hz
S_A.ma            = 1.0;           % modulation index
S_A.cosphi        = 1.0;           % power factor
S_A.Ipk_base      = 356;           % A
S_A.Ipk_scale     = 1.0;           % peak scaling (reference)
S_A.Pout          = 300e3;         % W

% Sweep ranges (same for both)
S_A.Fsw_vec       = 5e3:1e2:30e3;  % Hz
S_A.Adie_vec      = 30:5:1000;     % mm^2

% Conduction model (Rds(on) ∝ Ub^alpha_r / A_die), area-normalized
S_A.alpha_r       = 1.6;
S_A.Aref_mm2      = 300;           % assumption
S_A.Rds_on_25C    = 2.6e-3;        % Ω at 25°C (2 kV device, typ.)
S_A.k_r           = S_A.Rds_on_25C * S_A.Aref_mm2 / (S_A.Ub_kV^S_A.alpha_r);

% Junction temperature scaling (piecewise linear)
S_A.Tj_set_C      = 125;
R25=2.6e-3; R125=5.5e-3; R175=7.8e-3;
if S_A.Tj_set_C <= 125
    S_A.scale_temp = 1 + (S_A.Tj_set_C-25)/(125-25)*((R125/R25)-1);
else
    S_A.scale_temp = (R125/R25) + (S_A.Tj_set_C-125)/(175-125)*((R175/R25)-(R125/R25));
end

% ZCS switching model from EOSS @ 1200 V
S_A.Eoss_1200V    = 2030e-6;                               % J (typ.)
S_A.Coss_eq_ref   = S_A.Eoss_1200V / (S_A.Udc^2);          % F (@ 1200 V)
S_A.alpha_c       = 0;                                     % no Ub dependence
S_A.k_c           = S_A.Coss_eq_ref / (S_A.Aref_mm2*1e-12);% per-area F

% Constant edge rates (both cases)
S_A.dvdt_const    = 15e9;         % V/s  (~15 kV/us)
S_A.didt_const    = 3.0e9;        % A/s  (~3.0 kA/us)

% Plot styling
S_A.nLevels       = 10;
S_A.eta_caxis     = [96 100];

% Extra IL sweep figure settings
S_A.plotIL.A_sel   = 300;         % mm^2
S_A.plotIL.fsw_sel = 10e3;        % Hz

%% ---------------- Scaled 1.2 kV device at 800 V DC (Case B) ----------------
S_B = S_A;                        % copy all, then modify DC/blocking/current
S_B.device.name   = 'Scaled: 1.2 kV device @ Udc=800 V';
S_B.Udc           = 800;          % V (DC-link)
S_B.Ub_kV         = 1.2;          % kV (VDSS 1.2 kV)
S_B.Ipk_scale     = 1.5;          % ↑ current to keep Pout equal (1200/800=1.5)
S_B.Pout          = S_A.Pout;     % ensure same output power

% Reuse the SAME per-area FoMs (no 1.2 kV datasheet):
S_B.k_r = S_A.k_r;                % per-area conduction constant
S_B.k_c = S_A.k_c;                % per-area Coss_eq constant

%% ---------------- Compute maps for both scenarios ----------------
[eta_A, Ptot_A, P_on_A, P_zcs_A, P_ov_A] = eta_map_constdvdt(S_A);
[eta_B, Ptot_B, P_on_B, P_zcs_B, P_ov_B] = eta_map_constdvdt(S_B);

% Common grids
[X, Y] = meshgrid(S_A.Adie_vec, S_A.Fsw_vec/1e3);  % X: mm^2, Y: kHz

%% ---------------- FIG 1: Side-by-side efficiency maps ----------------
figure('Color','w','Position',[120 120 1100 480],'Renderer','painters');
tiledlayout(1,2,'Padding','compact','TileSpacing','compact');

nexttile(1);
contourf(X, Y, eta_A, S_A.nLevels, 'LineStyle','none'); hold on; box on;
title(sprintf('\\eta (U_{dc}=%.0f V, U_b=%.1f kV, I_{pk}\\times%.1f)', S_A.Udc, S_A.Ub_kV, S_A.Ipk_scale),'FontWeight','normal');
xlabel('Die area (mm^2)'); ylabel('f_{sw} (kHz)');
caxis(S_A.eta_caxis); colormap(nexttile(1), blueMutedMap()); colorbar;

nexttile(2);
contourf(X, Y, eta_B, S_A.nLevels, 'LineStyle','none'); hold on; box on;
title(sprintf('\\eta (U_{dc}=%.0f V, U_b=%.1f kV, I_{pk}\\times%.1f)', S_B.Udc, S_B.Ub_kV, S_B.Ipk_scale),'FontWeight','normal');
xlabel('Die area (mm^2)'); ylabel('f_{sw} (kHz)');
caxis(S_A.eta_caxis); colormap(nexttile(2), blueMutedMap()); colorbar;

%% ---------------- FIG 2: Δη map (B − A) ----------------
figure('Color','w','Position',[180 200 560 480],'Renderer','painters');
contourf(X, Y, eta_B - eta_A, 15, 'LineStyle','none'); box on;
title('\Delta\eta = \eta_{800V,1.2kV} - \eta_{1200V,2kV}','FontWeight','normal');
xlabel('Die area (mm^2)'); ylabel('f_{sw} (kHz)');
colormap(parula); cb=colorbar; ylabel(cb,'Δη (percentage points)');

%% ---------------- FIG 3: R_DS(on) vs A_die  &  E_sw vs A_die (overlay) ----------------
rds_A    = S_A.scale_temp * S_A.k_r * (S_A.Ub_kV^S_A.alpha_r) ./ S_A.Adie_vec; % Ω
rds_B    = S_B.scale_temp * S_B.k_r * (S_B.Ub_kV^S_B.alpha_r) ./ S_B.Adie_vec; % Ω

Coss_A   = S_A.k_c * ((S_A.Ub_kV*1e3)^S_A.alpha_c) .* S_A.Adie_vec * 1e-12;   % F
Coss_B   = S_B.k_c * ((S_B.Ub_kV*1e3)^S_B.alpha_c) .* S_B.Adie_vec * 1e-12;   % F
Esw_A_mJ = (Coss_A * S_A.Udc^2) * 1e3;                                         % mJ/event
Esw_B_mJ = (Coss_B * S_B.Udc^2) * 1e3;                                         % mJ/event

figure('Color','w','Position',[160 140 1040 420],'Renderer','painters');
tiledlayout(1,2,'Padding','compact','TileSpacing','compact');

nexttile(1);
plot(S_A.Adie_vec, rds_A, 'LineWidth',2.0, 'Color',[0.18 0.32 0.52]); hold on;
plot(S_B.Adie_vec, rds_B, 'LineWidth',2.0, 'Color',[0.36 0.54 0.75]); grid on; box on;
xlabel('Die area (mm^2)','FontSize',16); ylabel('R_{DS(on)} (\Omega)','FontSize',16);
title('R_{DS(on)} vs A_{die}','FontWeight','normal');
legend({sprintf('U_b=%.1f kV',S_A.Ub_kV), sprintf('U_b=%.1f kV',S_B.Ub_kV)}, ...
       'Location','northeast','Box','on','Color','w');

nexttile(2);
plot(S_A.Adie_vec, Esw_A_mJ, 'LineWidth',2.0, 'Color',[0.75 0.35 0.35]); hold on;
plot(S_B.Adie_vec, Esw_B_mJ, 'LineWidth',2.0, 'Color',[0.20 0.20 0.20]); grid on; box on;
xlabel('Die area (mm^2)','FontSize',16); ylabel('E_{sw} (mJ/event)','FontSize',16);
title('E_{sw} vs A_{die}','FontWeight','normal');
legend({sprintf('U_{dc}=%.0f V',S_A.Udc), sprintf('U_{dc}=%.0f V',S_B.Udc)}, ...
       'Location','northwest','Box','on','Color','w');

%% ---------------- FIG 4: Switching loss vs |I_L| (overlay A & B) ----------------
A_sel    = S_A.plotIL.A_sel;
fsw_sel  = S_A.plotIL.fsw_sel;
Ipk_A    = S_A.Ipk_base*S_A.Ipk_scale;
Ipk_B    = S_B.Ipk_base*S_B.Ipk_scale;
IL_max   = max(Ipk_A, Ipk_B);          % cover both cases on x-axis
IL_sweep = linspace(0, IL_max, 400);

% Case A (1200V/2kV)
EovA = (S_A.Udc.*IL_sweep.^2)/S_A.didt_const + (S_A.Udc.^2.*IL_sweep)/S_A.dvdt_const; % J/event
Coss_sel_A = S_A.k_c * ((S_A.Ub_kV*1e3)^S_A.alpha_c) * A_sel * 1e-12;  % F
Esw_sel_A  = Coss_sel_A * S_A.Udc^2;                                    % J/event
PzcsA_inv  = 3 * (fsw_sel * Esw_sel_A) * ones(size(IL_sweep));          % W
PovA_inv   = 3 * (fsw_sel * EovA);                                       % W
PswA_inv   = PzcsA_inv + PovA_inv;                                       % W

% Case B (800V/1.2kV)
EovB = (S_B.Udc.*IL_sweep.^2)/S_B.didt_const + (S_B.Udc.^2.*IL_sweep)/S_B.dvdt_const; % J/event
Coss_sel_B = S_B.k_c * ((S_B.Ub_kV*1e3)^S_B.alpha_c) * A_sel * 1e-12;  % F
Esw_sel_B  = Coss_sel_B * S_B.Udc^2;                                    % J/event
PzcsB_inv  = 3 * (fsw_sel * Esw_sel_B) * ones(size(IL_sweep));          % W
PovB_inv   = 3 * (fsw_sel * EovB);                                       % W
PswB_inv   = PzcsB_inv + PovB_inv;                                       % W

figure('Color','w','Position',[220 160 820 520],'Renderer','painters');
plot(IL_sweep, PzcsA_inv/1e3,  '-',  'LineWidth',2.0, 'Color',[0.75 0.35 0.35]); hold on;
plot(IL_sweep, PovA_inv/1e3,   '--', 'LineWidth',2.2, 'Color',[0.18 0.32 0.52]);
plot(IL_sweep, PswA_inv/1e3,   '-',  'LineWidth',2.4, 'Color',[0 0 0]);

plot(IL_sweep, PzcsB_inv/1e3,  '-',  'LineWidth',2.0, 'Color',[0.90 0.60 0.60]);
plot(IL_sweep, PovB_inv/1e3,   '--', 'LineWidth',2.2, 'Color',[0.45 0.65 0.85]);
plot(IL_sweep, PswB_inv/1e3,   '-',  'LineWidth',2.4, 'Color',[0.25 0.25 0.25]);

grid on; box on;
xlabel('|I_L| (A)','FontSize',16);
ylabel('Switching loss (kW)','FontSize',16);
title(sprintf('Switching loss vs |I_L| @ A_{die}=%d mm^2, f_{sw}=%.1f kHz', A_sel, fsw_sel/1e3), 'FontWeight','normal');
legend({ ...
  'A: ZCS (C_{oss})','A: Overlap (const)','A: Total', ...
  'B: ZCS (C_{oss})','B: Overlap (const)','B: Total'}, ...
  'Location','northwest','Box','on','Color','w');
set(gca,'FontName','Times New Roman','FontSize',13,'TickDir','out');

%% ---------------- Console sample point ----------------
ix = find(S_A.Adie_vec==300,1); iy = find(S_A.Fsw_vec==1e4,1);
if ~isempty(ix) && ~isempty(iy)
    fprintf('Sample (Adie=300 mm^2, fsw=10 kHz):\n');
    fprintf('  Case A η=%.3f %% | Case B η=%.3f %% | Δη=%.3f %%\n', ...
        eta_A(iy,ix), eta_B(iy,ix), eta_B(iy,ix)-eta_A(iy,ix));
end

%% ========================= Local functions (end of file) =========================
function [eta, Ptot, P_on_y, P_zcs_y, P_over_y] = eta_map_constdvdt(S)
% Exact same math/stepping style as your loop, with constant dv/dt & di/dt
I_peak   = S.Ipk_base * S.Ipk_scale;
theta_pf = acos(S.cosphi);
m_a      = S.ma;
ffund    = S.ffund;

Fsw_a    = S.Fsw_vec;
A_die_a  = S.Adie_vec;

k_r      = S.k_r;      alpha_r = S.alpha_r;
U_b      = S.Ub_kV;    Udc     = S.Udc;
Ub_volt  = U_b*1e3;    k_c     = S.k_c;  alpha_c = S.alpha_c;

P_on_y   = zeros(numel(Fsw_a), numel(A_die_a));
P_zcs_y  = zeros(numel(Fsw_a), numel(A_die_a));
P_over_y = zeros(numel(Fsw_a), numel(A_die_a));

dth_con_fixed = 1e-2;
for i_f = 1:numel(Fsw_a)
    fsw    = Fsw_a(i_f);
    dth_sw = ffund*2*pi/fsw;

    for i_a = 1:numel(A_die_a)
        A_die = A_die_a(i_a);

        % Conduction
        r_on = S.scale_temp * k_r * U_b^alpha_r / A_die;
        P_c  = 0;
        for theta = theta_pf : dth_con_fixed : (theta_pf + pi)
            IL      = I_peak * sin(theta - theta_pf);
            D_upper = (1 + m_a * sin(theta))/2;
            D_lower = (1 - m_a * sin(theta))/2;
            P_c     = P_c + (r_on*IL^2*D_upper*dth_con_fixed) + (r_on*IL^2*D_lower*dth_con_fixed);
        end
        P_cond = 2*P_c/(2*pi);

        % ZCS (Eoss/Coss_eq)
        C_oss = k_c * (Ub_volt^alpha_c) * A_die * 1e-12;
        Esw   = C_oss * Udc^2;
        Nsteps = numel(theta_pf : dth_sw : (theta_pf + pi));
        P_zcs  = ffund * 2 * Esw * Nsteps;

        % Overlap (constant dv/dt, di/dt)
        E_over = 0;
        for theta = theta_pf : dth_sw : (theta_pf + pi)
            ILabs   = abs(I_peak * sin(theta - theta_pf));
            E_over  = E_over + (Udc*ILabs.^2 / S.didt_const) + (Udc^2 * ILabs / S.dvdt_const);
        end
        P_over = ffund * 2 * E_over;

        P_on_y(i_f,i_a)   = P_cond;
        P_zcs_y(i_f,i_a)  = P_zcs;
        P_over_y(i_f,i_a) = P_over;
    end
end

Ptot = 3 * (P_on_y + P_zcs_y + P_over_y);
eta  = 100 * S.Pout ./ (S.Pout + Ptot);
end

function cmap = blueMutedMap()
nC = 256;
stops = [ ...
    1.00 1.00 1.00
    0.92 0.95 0.98
    0.75 0.84 0.93
    0.56 0.70 0.86
    0.36 0.54 0.75
    0.18 0.32 0.52 ];
xi = linspace(0,1,size(stops,1));
cmap = interp1(xi, stops, linspace(0,1,nC));
end

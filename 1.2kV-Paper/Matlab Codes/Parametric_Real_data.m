%% ============================================
%  PARAMETRIC η(A_die, f_sw) — 2 kV SiC (FF3MR20KM1H_S) + constant dv/dt, di/dt
%  ============================================
clear; clc; close all;

%% ---------- PARAMETERS (datasheet-calibrated & user choices) ----------
S.device.name   = 'Infineon FF3MR20KM1H_S (2 kV CoolSiC Trench MOSFET)';
S.Udc           = 1200;          % V  (DC-link)
S.Ub_kV         = 2.0;           % kV device blocking rating (VDSS = 2 kV)
S.ffund         = 500;           % Hz electrical fundamental
S.ma            = 1.0;           % modulation index
S.cosphi        = 1.0;           % power factor
S.Ipk_base      = 356;           % A
S.Ipk_scale     = 1;           % peak-current scaling
S.Pout          = 300e3;         % W

% Sweep ranges
S.Fsw_vec       = 5e3:1e2:30e3;  % Hz
S.Adie_vec      = 50:25:500;     % mm^2

% ------ Conduction model (Rds(on) ∝ Ub^alpha_r / Adie, area-normalized) ------
% Datasheet anchors (typical):
% Rds(on) @ 25°C ≈ 2.6 mΩ; @125°C ≈ 5.5 mΩ; @175°C ≈ 7.8 mΩ
S.alpha_r       = 1.6;           % exponent on Ub (kept from your model)
S.Aref_mm2      = 300;           % assumed equivalent total die area of the module (tune if known)
S.Rds_on_25C    = 2.6e-3;        % Ω at 25°C
S.k_r           = S.Rds_on_25C * S.Aref_mm2 / (S.Ub_kV^S.alpha_r);  % ensures r_on(Aref,25°C)=2.6mΩ

% Fixed junction temperature selection (piecewise-linear scaling)
S.Tj_set_C      = 125;           % << choose 100 or 125 (°C)
R25 = 2.6e-3; R125 = 5.5e-3; R175 = 7.8e-3; % Ω
% linear interpolation/extrapolation for scale_temp vs Tj
if S.Tj_set_C <= 125
    S.scale_temp = 1 + (S.Tj_set_C - 25)/(125-25) * ((R125/R25) - 1);
else
    S.scale_temp = (R125/R25) + (S.Tj_set_C - 125)/(175-125) * ((R175/R25)-(R125/R25));
end

% ------ ZCS switching (Eoss at 1200 V → Coss_eq reference) ------
% Datasheet: Eoss(1200 V, 25°C) ≈ 2030 µJ (typ)
S.Eoss_1200V    = 2030e-6;                   % J
S.Coss_eq_ref   = S.Eoss_1200V / (S.Udc^2);  % F (≈ 1.41 nF)
S.alpha_c       = 0;                         % no Ub dependence for Coss_eq (fit at 1200 V)
S.k_c           = S.Coss_eq_ref / (S.Aref_mm2*1e-12);  % scales linearly with die area

% ------ Constant dv/dt and di/dt (no |I|-dependence) ------
% Use typical datasheet-like values (you can tweak these)
S.dvdt_const    = 15e9;         % V/s  (≈ 15 kV/µs)
S.didt_const    = 10e9;        % A/s  (≈ 3.0 kA/µs)

% ------ Plot styling ------
S.nLevels       = 10;
S.eta_caxis     = [96 100];

% Extra figure (switching loss vs |I|) settings
S.plotIL.A_sel   = 300;         % mm^2 for the IL sweep plot
S.plotIL.fsw_sel = 10e3;        % Hz for the IL sweep plot

%% ---------- Derived constants ----------
I_peak   = S.Ipk_base * S.Ipk_scale;
theta_pf = acos(S.cosphi);
m_a      = S.ma;
ffund    = S.ffund;
Pout     = S.Pout;

Fsw_a    = S.Fsw_vec;
A_die_a  = S.Adie_vec;

k_r      = S.k_r;
alpha_r  = S.alpha_r;
U_b      = S.Ub_kV;                % kV for conduction model
Udc      = S.Udc;
Ub_volt  = U_b*1e3;                % V for Coss/Eoss model
k_c      = S.k_c;
alpha_c  = S.alpha_c;

%% ---------- Allocate (rows=f_sw, cols=A_die) ----------
P_on_y   = zeros(numel(Fsw_a), numel(A_die_a));   % conduction
P_zcs_y  = zeros(numel(Fsw_a), numel(A_die_a));   % zero-current switching (Eoss-based)
P_over_y = zeros(numel(Fsw_a), numel(A_die_a));   % overlap (constant dv/dt, di/dt)

%% ---------- Main loops (identical θ-stepping to your loop) ----------
dth_con_fixed = 1e-2;  % conduction theta step (fixed)

for i_f = 1:numel(Fsw_a)
    fsw    = Fsw_a(i_f);
    dth_sw = ffund*2*pi/fsw;                     % theta step for zcs/overlap

    for i_a = 1:numel(A_die_a)
        A_die = A_die_a(i_a);

        % --- Conduction (fixed step = 1e-2) ---
        r_on = S.scale_temp * k_r * U_b^alpha_r / A_die;  % Ω (U_b in kV by design)
        P_c  = 0;
        for theta = theta_pf : dth_con_fixed : (theta_pf + pi)
            IL      = I_peak * sin(theta - theta_pf);
            D_upper = (1 + m_a * sin(theta))/2;
            D_lower = (1 - m_a * sin(theta))/2;
            P_c     = P_c + (r_on*IL^2*D_upper*dth_con_fixed) + (r_on*IL^2*D_lower*dth_con_fixed);
        end
        P_cond = 2*P_c/(2*pi);                   % same scaling as your code

        % --- ZCS switching (Eoss/Coss_eq) ---
        C_oss = k_c * (Ub_volt^alpha_c) * A_die * 1e-12;  % F
        Esw   = C_oss * Udc^2;                             % J/event
        Nsteps = numel(theta_pf : dth_sw : (theta_pf + pi)); % exact ':' step count
        P_zcs  = ffund * 2 * Esw * Nsteps;                 % W

        % --- Overlap energy (constant dv/dt, di/dt) ---
        E_over = 0;
        for theta = theta_pf : dth_sw : (theta_pf + pi)
            ILabs   = abs(I_peak * sin(theta - theta_pf));
            E_over  = E_over + (Udc*ILabs.^2 / S.didt_const) + (Udc^2 * ILabs / S.dvdt_const);
        end
        P_over = ffund * 2 * E_over;

        % Store
        P_on_y(i_f, i_a)   = P_cond;
        P_zcs_y(i_f, i_a)  = P_zcs;
        P_over_y(i_f, i_a) = P_over;
    end
end

%% ---------- Total loss & Efficiency ----------
P_tot = 3 * (P_on_y + P_zcs_y + P_over_y);
eta   = 100 * S.Pout ./ (S.Pout + P_tot);

%% ---------- Figure 1: η(A_die, f_sw) ----------
[X,Y] = meshgrid(A_die_a, Fsw_a/1e3);   % X: die area [mm^2], Y: kHz
figure('Color','w','Position',[220 180 780 520],'Renderer','painters');
axes1 = axes('FontName','Times New Roman','FontSize',15,'LineWidth',1.1);
hold on; box on; grid off; set(gca,'Layer','top');
contourf(X, Y, eta, S.nLevels, 'LineStyle','none');

% single-hue muted blue colormap
nC = 256;
stops = [1 1 1; 0.92 0.95 0.98; 0.75 0.84 0.93; 0.56 0.70 0.86; 0.36 0.54 0.75; 0.18 0.32 0.52];
xi = linspace(0,1,size(stops,1)); cmap = interp1(xi, stops, linspace(0,1,nC)); colormap(cmap);

xlabel('Die area (mm^2)','FontSize',20);
ylabel('Switching frequency (kHz)','FontSize',20);
xlim([min(A_die_a) max(A_die_a)]);
ylim([min(Fsw_a)/1e3 max(Fsw_a)/1e3]);
c = colorbar('FontSize',14,'FontName','Times New Roman');
ylabel(c,'Efficiency (%)','FontSize',20);
caxis(S.eta_caxis); axis tight

%% ---------- Figure 2: R_DS(on) vs A_die & E_sw vs A_die ----------
rds_vec    = S.scale_temp * S.k_r * S.Ub_kV^S.alpha_r ./ A_die_a;         % Ω
Coss_vec   = S.k_c * ((S.Ub_kV*1e3)^S.alpha_c) .* A_die_a * 1e-12;       % F
Esw_vec_mJ = (Coss_vec * S.Udc^2) * 1e3;                                  % mJ/event

figure('Color','w','Position',[180 140 900 420],'Renderer','painters');
tiledlayout(1,2,'Padding','compact','TileSpacing','compact');

nexttile(1);
plot(A_die_a, rds_vec, 'LineWidth',2.0, 'Color',[0.18 0.32 0.52]); grid on; box on;
xlabel('Die area (mm^2)','FontSize',16); ylabel('R_{DS(on)} (\Omega)','FontSize',16);
title(sprintf('R_{DS(on)} vs A_{die}  (T_j=%d^\\circC)', S.Tj_set_C), 'FontWeight','normal');

nexttile(2);
plot(A_die_a, Esw_vec_mJ, 'LineWidth',2.0, 'Color',[0.36 0.54 0.75]); grid on; box on;
xlabel('Die area (mm^2)','FontSize',16); ylabel('E_{sw} (mJ/event)','FontSize',16);
title(sprintf('E_{sw} vs A_{die}  (U_{dc}=%g V)', S.Udc), 'FontWeight','normal');

%% ---------- Figure 3: Switching loss vs |I_L| (for A_sel & f_sw_sel) ----------
A_sel   = S.plotIL.A_sel;
fsw_sel = S.plotIL.fsw_sel;

IL_sweep = linspace(0, I_peak, 400);
Eover_ev = (Udc.*IL_sweep.^2)/S.didt_const + (Udc.^2.*IL_sweep)/S.dvdt_const; % J/event

Coss_sel = S.k_c * (Ub_volt^S.alpha_c) * A_sel * 1e-12;  % F
Esw_sel  = Coss_sel * Udc^2;                              % J/event

% Per-inverter switching power at fsw_sel:
Pzcs_inv  = 3 * (fsw_sel * Esw_sel) * ones(size(IL_sweep)); % W
Pover_inv = 3 * (fsw_sel * Eover_ev);                       % W
Psw_inv   = Pzcs_inv + Pover_inv;                           % W

figure('Color','w','Position',[220 160 720 480],'Renderer','painters');
plot(IL_sweep, Pzcs_inv/1e3,  '-', 'LineWidth',2.0, 'Color',[0.75 0.35 0.35]); hold on; % ZCS (red)
plot(IL_sweep, Pover_inv/1e3, '--', 'LineWidth',2.2, 'Color',[0.18 0.32 0.52]);        % Overlap (blue)
plot(IL_sweep, Psw_inv/1e3,   '-', 'LineWidth',2.4, 'Color',[0 0 0]);                   % Total (black)
grid on; box on;
xlabel('|I_L| (A)','FontSize',16);
ylabel('Switching loss (kW)','FontSize',16);
title(sprintf('Switching loss vs |I_L| @ A_{die}=%d mm^2, f_{sw}=%.1f kHz, T_j=%d^\\circC', ...
      A_sel, fsw_sel/1e3, S.Tj_set_C), 'FontWeight','normal');
legend({'ZCS (C_{oss})','Overlap (const dv/dt, di/dt)','Total (inverter)'}, ...
       'Location','northwest','Box','on','Color','w');
set(gca,'FontName','Times New Roman','FontSize',13,'TickDir','out');

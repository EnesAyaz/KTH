%% ============================================
%  PARAMETRIC η(A_die, f_sw) — EXACT MATCH TO YOUR LOOP + dv/dt(|I|)
%  ============================================
clear; clc; close all;

%% ---------- PARAMETERS (edit here) ----------
S.Pout        = 300e3;        % W
S.ffund       = 500;          % Hz
S.cosphi      = 1.0;          % power factor
S.ma          = 1.0;          % modulation index
S.Ipk_base    = 356;          % A (base peak current)
S.Ipk_scale   = 1;            % multiplier on I_peak

S.Fsw_vec     = 5e3:0.5e3:20e3; % Hz
S.Adie_vec    = 30:30:600;      % mm^2

S.k_r         = 7.2e-3*66;  % conduction constant
S.alpha_r     = 1.6;          % conduction exponent
S.Ub_kV       = 2;            % kV (for conduction model)

S.Udc         = 1200;         % V (dc-link)
S.k_c         = 1.6e4;        % Coss constant
S.alpha_c     = -1;           % Coss exponent (Ub in volts)

S.dv_dt       = 20e9;         % V/s fallback (used if dvdt_model='const')
S.di_dt       = 20e9;         % A/s placeholder for overlap term

S.scale_temp  = 1.0;          % temperature scaling for R_DS(on)

% --- dv/dt(|I|) control model ---
S.dvdt_model  = 'const';      % 'const' | 'linear_clamp' | 'inverse'
S.dvdt_min    = 3e9;                 % V/s slowest edge at high |I|
S.dvdt_max    = 15e9;                % V/s fastest edge at light |I|
S.dvdt_Iref   = 1*(S.Ipk_base*S.Ipk_scale); % A, where limitation kicks in
S.dvdt_k      = 1.0;                 % shape factor for 'inverse'

% Plot styling
S.nLevels     = 40;
S.eta_caxis   = [98 99.8];

% Extra-figure settings for "switching loss vs |I|"
S.plotIL.A_sel   = 300;   % mm^2 (choose die area for IL plot)
S.plotIL.fsw_sel = 14e3;  % Hz   (choose switching freq for IL plot)

% --- Deviation bands (relative, e.g., 0.10 = ±10%) ---
S.band.rds_rel  = 0.1;   % ±20% for R_DS(on) model spread
S.band.esw_rel  = 0.1;   % ±15% for Esw (Coss-based) spread
S.band.pzcs_rel = 0.1;   % ±15% for ZCS (Coss) power band in Fig. 3
S.band.psw_rel  = 0.1;   % ±15% for total switching loss vs |I|

%% ---------- Derived constants ----------
I_peak   = S.Ipk_base * S.Ipk_scale;
theta_pf = acos(S.cosphi);
m_a      = S.ma;
ffund    = S.ffund;

Fsw_a    = S.Fsw_vec;
A_die_a  = S.Adie_vec;

k_r      = S.k_r;
alpha_r  = S.alpha_r;
U_b      = S.Ub_kV;           % kV for conduction
Udc      = S.Udc;
Ub_volt  = U_b*1e3;           % V  for Coss
k_c      = S.k_c;
alpha_c  = S.alpha_c;

% --- dv/dt(I) mapping (anonymous function, same script; no local functions) ---
dvdt_of_I = @(Iabs) ...
    ( ...
      strcmpi(S.dvdt_model,'const')        .* (S.dv_dt*ones(size(Iabs))) + ...
      strcmpi(S.dvdt_model,'linear_clamp') .* ( ...
          max(S.dvdt_min, S.dvdt_max - (S.dvdt_max-S.dvdt_min).*min(1, Iabs./max(S.dvdt_Iref,eps))) ) + ...
      strcmpi(S.dvdt_model,'inverse')      .* ( ...
          max(S.dvdt_min, S.dvdt_max ./ (1 + S.dvdt_k.*Iabs./max(S.dvdt_Iref,eps))) ) ...
    );

%% ---------- Allocate (rows=f_sw, cols=A_die) ----------
P_on_y   = zeros(numel(Fsw_a), numel(A_die_a));   % conduction
P_zcs_y  = zeros(numel(Fsw_a), numel(A_die_a));   % zero-current switching
P_over_y = zeros(numel(Fsw_a), numel(A_die_a));   % overlap

%% ---------- Main loops (identical stepping to your loop) ----------
dth_con_fixed = 1e-2;  % conduction theta step (fixed)

for i_f = 1:numel(Fsw_a)
    fsw   = Fsw_a(i_f);
    dth_sw = ffund*2*pi/fsw;                     % theta step for zcs/overlap

    for i_a = 1:numel(A_die_a)
        A_die = A_die_a(i_a);

        % --- Conduction (fixed step = 1e-2) ---
        r_on = S.scale_temp * k_r * U_b^alpha_r / A_die;    % Ω (U_b in kV by design)
        P_c  = 0;
        for theta = theta_pf : dth_con_fixed : (theta_pf + pi)
            IL      = I_peak * sin(theta - theta_pf);
            D_upper = (1 + m_a * sin(theta))/2;
            D_lower = (1 - m_a * sin(theta))/2;
            P_c     = P_c + (r_on*IL^2*D_upper*dth_con_fixed) + (r_on*IL^2*D_lower*dth_con_fixed);
        end
        P_cond = 2*P_c/(2*pi);                   % same scaling as your code

        % --- ZCS switching loss (Coss) ---
        C_oss = k_c * (Ub_volt^alpha_c) * A_die * 1e-12;  % F
        Esw   = C_oss * Udc^2;                            % J per event
        % Count steps EXACTLY as ':' loop would
        Nsteps = numel(theta_pf : dth_sw : (theta_pf + pi));
        P_zcs  = ffund * 2 * Esw * Nsteps;                % W  (~ Esw*fsw)

        % --- Overlap (sum over the same discrete thetas), with dv/dt(|I|)
        E_over = 0;
        for theta = theta_pf : dth_sw : (theta_pf + pi)
            ILabs       = abs(I_peak * sin(theta - theta_pf));
            dvdt_theta  = dvdt_of_I(ILabs);               % V/s for this event
            E_over      = E_over + (Udc*ILabs.^2/S.di_dt) + (Udc^2.*ILabs./dvdt_theta);
        end
        P_over = ffund * 2 * E_over;

        % Store
        P_on_y(i_f, i_a)   = P_cond;
        P_zcs_y(i_f, i_a)  = P_zcs;
        P_over_y(i_f, i_a) = P_over;
    end
end

%% ---------- Total loss & Efficiency (kept as in your latest script) ----------
P_tot = 3 * (P_on_y + P_zcs_y + P_over_y);     % W
eta   = 100 * S.Pout ./ (S.Pout + P_tot);      % %

%% ---------- Figure 1: η(A_die, f_sw) ----------
[X,Y] = meshgrid(A_die_a, Fsw_a/1e3);          % X: die area [mm^2], Y: kHz
figure('Color','w','Position',[220 180 780 520],'Renderer','painters');
axes1 = axes('FontName','Times New Roman','FontSize',15,'LineWidth',1.1);
hold on; box on; grid off; set(gca,'Layer','top');
contourf(X, Y, eta, S.nLevels, 'LineStyle','none');

% Single-hue muted blue colormap
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

%% ---------- Figure 2: R_DS(on) vs A_die  &  E_sw vs A_die  + deviation bands ----------
rds_vec    = S.scale_temp * S.k_r * S.Ub_kV^S.alpha_r ./ A_die_a;            % Ω
Coss_vec   = S.k_c * ((S.Ub_kV*1e3)^S.alpha_c) .* A_die_a * 1e-12;          % F
Esw_vec_mJ = (Coss_vec * S.Udc^2) * 1e3;                                     % mJ/event

% Build bands
rds_low    = rds_vec .* (1 - S.band.rds_rel);
rds_high   = rds_vec .* (1 + S.band.rds_rel);

esw_low    = Esw_vec_mJ .* (1 - S.band.esw_rel);
esw_high   = Esw_vec_mJ .* (1 + S.band.esw_rel);

figure('Color','w','Position',[180 140 900 420],'Renderer','opengl');
tiledlayout(1,2,'Padding','compact','TileSpacing','compact');

% --- Left: Rds vs Adie with band
nexttile(1);
hold on; box on; grid on;
% shaded band
fill([A_die_a, fliplr(A_die_a)], [rds_low, fliplr(rds_high)], [0.18 0.32 0.52], ...
     'FaceAlpha', 0.15, 'EdgeColor','none');
% nominal line
plot(A_die_a, rds_vec, 'LineWidth',2.0, 'Color',[0.18 0.32 0.52]);
xlabel('Die area (mm^2)','FontSize',16); ylabel('R_{DS(on)} (\Omega)','FontSize',16);
title(sprintf('R_{DS(on)} vs A_{die}  (U_b=%.1f kV, scale\\_temp=%.2f)', S.Ub_kV, S.scale_temp), 'FontWeight','normal');
legend({sprintf('Model band (\\pm%.0f%%)',100*S.band.rds_rel), 'Nominal'}, ...
       'Location','northeast','Box','on','Color','w');

% --- Right: Esw vs Adie with band
nexttile(2);
hold on; box on; grid on;
fill([A_die_a, fliplr(A_die_a)], [esw_low, fliplr(esw_high)], [0.36 0.54 0.75], ...
     'FaceAlpha', 0.18, 'EdgeColor','none');
plot(A_die_a, Esw_vec_mJ, 'LineWidth',2.0, 'Color',[0.36 0.54 0.75]);
xlabel('Die area (mm^2)','FontSize',16); ylabel('E_{sw} (mJ/event)','FontSize',16);
title(sprintf('E_{sw} vs A_{die}  (U_{dc}=%g V, U_b=%.1f kV)', S.Udc, S.Ub_kV), 'FontWeight','normal');
legend({sprintf('Model band (\\pm%.0f%%)',100*S.band.esw_rel), 'Nominal'}, ...
       'Location','northwest','Box','on','Color','w');

%% ---------- Figure 3: Switching loss vs |I_L| (for one A_die & f_sw) + bands ----------
A_sel   = S.plotIL.A_sel;
fsw_sel = S.plotIL.fsw_sel;

% Per-event energies at a constant |I| = sweep
IL_sweep = linspace(0, I_peak, 400);
dvdt_ev  = dvdt_of_I(IL_sweep);                                % V/s per event
Eover_ev = (Udc.*IL_sweep.^2)./S.di_dt + (Udc.^2.*IL_sweep)./dvdt_ev;   % J/event
% ZCS energy (independent of IL) at this A_sel
Coss_sel = S.k_c * (Ub_volt^S.alpha_c) * A_sel * 1e-12;                 % F
Esw_sel  = Coss_sel * Udc^2;                                            % J/event

% Power per inverter (3 phases) at fsw_sel:
Pzcs_inv  = 3 * (fsw_sel * Esw_sel) * ones(size(IL_sweep));             % W
Pover_inv = 3 * (fsw_sel * Eover_ev);                                   % W
Psw_inv   = Pzcs_inv + Pover_inv;                                       % W

% --- Bands ---
% ZCS band (flat with |I|, set by Coss uncertainty etc.)
Pzcs_low  = Pzcs_inv .* (1 - S.band.pzcs_rel);
Pzcs_high = Pzcs_inv .* (1 + S.band.pzcs_rel);
% Total switching loss band
Psw_low   = Psw_inv   .* (1 - S.band.psw_rel);
Psw_high  = Psw_inv   .* (1 + S.band.psw_rel);

figure('Color','w','Position',[220 160 760 520],'Renderer','opengl');
hold on; box on; grid on;

% total band first (light gray)
fill([IL_sweep, fliplr(IL_sweep)], ([Psw_low,  fliplr(Psw_high)]/1e3), [0 0 0], ...
     'FaceAlpha',0.10, 'EdgeColor','none');

% ZCS band (light red)
fill([IL_sweep, fliplr(IL_sweep)], ([Pzcs_low, fliplr(Pzcs_high)]/1e3), [0.75 0.35 0.35], ...
     'FaceAlpha',0.10, 'EdgeColor','none');

% nominal component curves and total
plot(IL_sweep, Pzcs_inv/1e3,  '-',  'LineWidth',2.0, 'Color',[0.75 0.35 0.35]);  % ZCS (muted red)
plot(IL_sweep, Pover_inv/1e3, '--', 'LineWidth',2.2, 'Color',[0.18 0.32 0.52]);  % Overlap (deep blue)
plot(IL_sweep, Psw_inv/1e3,   '-',  'LineWidth',2.4, 'Color',[0 0 0]);           % Total (black)

xlabel('|I_L| (A)','FontSize',16);
ylabel('Switching loss (kW)','FontSize',16);
title(sprintf('Switching loss vs |I_L| @ A_{die}=%d mm^2, f_{sw}=%.1f kHz', A_sel, fsw_sel/1e3), 'FontWeight','normal');

legend({ ...
    sprintf('Total band (\\pm%.0f%%)', 100*S.band.psw_rel), ...
    sprintf('ZCS band (\\pm%.0f%%)',   100*S.band.pzcs_rel), ...
    'ZCS (C_{oss})','Overlap (dv/dt(|I|))','Total (inverter)'}, ...
    'Location','northwest','Box','on','Color','w');

set(gca,'FontName','Times New Roman','FontSize',13,'TickDir','out');

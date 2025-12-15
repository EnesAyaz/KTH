%% ============================================
%  PARAMETRIC η(A_die, f_sw): 800 V vs 1200 V Comparison
%  - Blue-shade efficiency maps (no Δη)
%  - Rds bands, Ezcs bands, and per-event E_total = Ezcs + Eover at a defined |I|
%  ============================================
clear; clc; close all;

%% ---------- BASE PARAMETERS (edit here) ----------
S.Pout        = 250e3;        % W
S.ffund       = 500;          % Hz
S.cosphi      = 1.0;
S.ma          = 1.0;
S.Ipk_base    = 282;          % A @ 1200 V
S.Fsw_vec     = 5e3:0.5e3:20e3; % Hz
S.Adie_vec    = 30:30:600;    % mm^2

% Conduction model
S.k_r         = 7.2e-3*63*1.6;
S.alpha_r     = 1.6;

% Coss / Ezcs model
S.k_c         = 1.6e4;
S.alpha_c     = -1;

% Overlap model params
S.dv_dt       = 10e9;         % V/s
S.di_dt       = 10e9;         % A/s

S.scale_temp  = 1.0;          % R_DS(on) temp scaling

% dv/dt(|I|) control model
S.dvdt_model  = 'const';      % 'const' | 'linear_clamp' | 'inverse'
S.dvdt_min    = 3e9;
S.dvdt_max    = 15e9;
S.dvdt_Iref   = S.Ipk_base;
S.dvdt_k      = 1.0;

% Plot styling
S.nLevels     = 40;
S.eta_caxis   = [98.2 99.8];

% "Switching loss vs |I|" demo point
S.plotIL.A_sel   = 300;       % mm^2
S.plotIL.fsw_sel = 10e3;      % Hz

% Deviation bands (relative)
S.band.rds_rel   = 0.10;
S.band.coss_rel  = 0.10;  % used for Coss (display only, if needed)
S.band.esw_rel   = 0.10;  % for Ezcs (since Ezcs = Coss*Udc^2)
S.band.eover_rel = 0.10;  % for per-event overlap energy uncertainty
S.band.evt_rel   = 0.10;  % optional extra slack on total per-event energy
S.band.pzcs_rel  = 0.10;  % for Pzcs bands in |I|-sweep figure
S.band.psw_rel   = 0.10;  % for total switching power band in |I|-sweep figure

% Reference current definition for per-event energy figure
S.event.Iref_mode = 'absolute';   % 'absolute' | 'per_case_rms' | 'per_case_peak'
S.event.Iref_abs  = 200;          % A, used if Iref_mode = 'absolute'

% --- Two cases ---
cases(1).name   = '800V-Udc (1.2kV device)';  cases(1).Udc = 800;  cases(1).Ub_kV = 1.2;  cases(1).Ipk_sc = 1200/800;
cases(2).name   = '1200V-Udc (2.0kV device)'; cases(2).Udc = 1200; cases(2).Ub_kV = 2.0;  cases(2).Ipk_sc = 1200/1200;

%% ---------- Helpers ----------
theta_pf = acos(S.cosphi);  m_a = S.ma;  ffund = S.ffund;
Fsw_a = S.Fsw_vec;  A_die_a = S.Adie_vec;

% blue colormap for η maps
nC = 256; stops = [1 1 1; 0.92 0.95 0.98; 0.75 0.84 0.93; 0.56 0.70 0.86; 0.36 0.54 0.75; 0.18 0.32 0.52];
xi = linspace(0,1,size(stops,1)); cmapBlue = interp1(xi, stops, linspace(0,1,nC));

dvdt_of_I = @(Iabs, Sloc) ( strcmpi(Sloc.dvdt_model,'const') .* (Sloc.dv_dt*ones(size(Iabs))) + ...
    strcmpi(Sloc.dvdt_model,'linear_clamp') .* (max(Sloc.dvdt_min, Sloc.dvdt_max - (Sloc.dvdt_max-Sloc.dvdt_min).*min(1, Iabs./max(Sloc.dvdt_Iref,eps)))) + ...
    strcmpi(Sloc.dvdt_model,'inverse')      .* (max(Sloc.dvdt_min, Sloc.dvdt_max ./ (1 + Sloc.dvdt_k.*Iabs./max(Sloc.dvdt_Iref,eps)))) );

%% ---------- Storage ----------
P_on = cell(1,2); P_zcs = cell(1,2); P_over = cell(1,2); eta = cell(1,2);
rds_curves = zeros(2,numel(A_die_a));
esw_curves = zeros(2,numel(A_die_a));  % Ezcs per event (mJ)
coss_curves = zeros(2,numel(A_die_a)); % only if you still want it

%% ---------- Main loops ----------
dth_con_fixed = 1e-2;

for k = 1:2
    Udc   = cases(k).Udc;    Ub_kV = cases(k).Ub_kV; Ub_V = Ub_kV*1e3;
    Ipk   = S.Ipk_base * cases(k).Ipk_sc;

    P_on_y = zeros(numel(Fsw_a), numel(A_die_a));
    P_zcs_y = zeros(numel(Fsw_a), numel(A_die_a));
    P_over_y= zeros(numel(Fsw_a), numel(A_die_a));

    for i_f = 1:numel(Fsw_a)
        fsw = Fsw_a(i_f);  dth_sw = ffund*2*pi/fsw;
        for i_a = 1:numel(A_die_a)
            A_die = A_die_a(i_a);

            % Conduction
            r_on =S.scale_temp * S.k_r * Ub_kV^S.alpha_r / A_die;
            P_c=0;
            for th = theta_pf:dth_con_fixed:(theta_pf+pi)
                IL = Ipk * sin(th - theta_pf);
                D_upper = (1 + m_a*sin(th))/2; D_lower = (1 - m_a*sin(th))/2;
                P_c = P_c + (r_on*IL^2*D_upper + r_on*IL^2*D_lower)*dth_con_fixed;
            end
            P_cond = 2*P_c/(2*pi);

            % Zero-current switching energy / power
            C_oss = S.k_c * (Ub_V^S.alpha_c) * A_die * 1e-12;  % F
            Ezcs  = C_oss * Udc^2;                              % J/event
            Nsteps = numel(theta_pf:dth_sw:(theta_pf+pi));
            Pzcs   = ffund * 2 * Ezcs * Nsteps;                 % W

            % Overlap losses
            Eover = 0;
            for th = theta_pf:dth_sw:(theta_pf+pi)
                ILabs = abs(Ipk * sin(th - theta_pf));
                dvdt_th = dvdt_of_I(ILabs, S);
                Eover = Eover + (Udc*ILabs.^2/S.di_dt) + (Udc^2.*ILabs./dvdt_th);
            end
            Pover = ffund * 2 * Eover;

            P_on_y(i_f,i_a)   = P_cond;
            P_zcs_y(i_f,i_a)  = Pzcs;
            P_over_y(i_f,i_a) = Pover;

            % 1D curves (per event)
            esw_curves(k,i_a)  = (C_oss * Udc^2) * 1e3; % mJ
            coss_curves(k,i_a) = C_oss;                 % F
        end
    end

    P_tot_y = 3*(P_on_y + P_zcs_y + P_over_y);
    eta_y   = 100*(S.Pout-P_tot_y)./S.Pout;

    P_on{k}=P_on_y; P_zcs{k}=P_zcs_y; P_over{k}=P_over_y; eta{k}=eta_y;
    rds_curves(k,:) = S.scale_temp * S.k_r * Ub_kV^S.alpha_r ./ A_die_a;
end

%% ---------- Figure A: η maps (blue) ----------
[X,Y] = meshgrid(A_die_a, Fsw_a/1e3);

figure('Color','w','Position',[160 90 940 480],'Renderer','painters');
t = tiledlayout(1,2,'Padding','compact','TileSpacing','compact');

% Common font sizes
font_axes = 20;
font_title = 20;
font_cb = 20;

% --- 800 V case ---
nexttile(1);
contourf(X, Y, eta{1}, S.nLevels, 'LineStyle', 'none');
%title('Efficiency \eta — 800 V U_{dc}', 'FontSize', font_title, 'FontWeight', 'normal');
title('800 V U_{dc}', 'FontSize', font_title, 'FontWeight', 'normal');
colormap(gca, cmapBlue);
caxis(S.eta_caxis);
box on; set(gca,'Layer','top','FontName','Times New Roman','FontSize',font_axes);

% --- 1200 V case ---
nexttile(2);
contourf(X, Y, eta{2}, S.nLevels, 'LineStyle', 'none');
%title('Efficiency \eta — 1200 V U_{dc}', 'FontSize', font_title, 'FontWeight', 'normal');
title('1200 V U_{dc}', 'FontSize', font_title, 'FontWeight', 'normal');
colormap(gca, cmapBlue);
caxis(S.eta_caxis);
box on; set(gca,'Layer','top','FontName','Times New Roman','FontSize',font_axes);

% Shared colorbar (create based on the second axes)
cb = colorbar('eastoutside');
ylabel(cb, 'Efficiency (%)', 'FontSize', font_cb, 'FontName','Times New Roman');
set(cb, 'FontSize', font_cb);

% Shared axis labels (global)
xlabel(t, 'Die area (mm^2)', 'FontSize', font_axes, 'FontName','Times New Roman');
ylabel(t, 'Switching frequency (kHz)', 'FontSize', font_axes, 'FontName','Times New Roman');



%% ---------- Figure B: R_DS(on) vs A_die (bands, compact legend) ----------
figure('Color','w','Position',[160 90 940 480],'Renderer','opengl'); 
hold on; grid on; box on;

for k = 1:2
    rds = rds_curves(k,:);
    rlo = 1e3*rds * (1 - 2*S.band.rds_rel);
    rhi = 1e3*rds * (1 + 2*S.band.rds_rel);
    c   = [0.18 0.32 0.52] + 0.25*(k-1);
    
    % shaded band (no legend)
    fill([A_die_a, fliplr(A_die_a)], [rlo, fliplr(rhi)], c, ...
         'FaceAlpha',0.12, 'EdgeColor','none', 'HandleVisibility','off');
    
    % nominal line (legend entry)
    plot(A_die_a, 1e3*rds, 'LineWidth',2.0, 'Color', c, ...
         'DisplayName', cases(k).name);
end

xlabel('Die area (mm^2)');
ylabel('R_{DS(on)} (m\Omega)');
%title('R_{DS(on)} vs A_{die}');
legend('Location','northeast','Box','on','Color','w','FontSize',20);  % smaller legend font
set(gca,'FontName','Times New Roman','FontSize',20,'TickDir','out');



%% ---------- Figure C: Zero-current switching energy E_zcs vs A_die (bands) ----------
figure('Color','w','Position',[220 120 680 480],'Renderer','opengl'); hold on; grid on; box on;
for k = 1:2
    ezcs = esw_curves(k,:);  % mJ/event
    elo  = ezcs*(1 - S.band.esw_rel);
    ehi  = ezcs*(1 + S.band.esw_rel);
    c    = [0.36 0.54 0.75] - 0.18*(k-1);
    fill([A_die_a, fliplr(A_die_a)], [elo, fliplr(ehi)], c, 'FaceAlpha',0.16, 'EdgeColor','none');
    plot(A_die_a, ezcs, 'LineWidth',2.0, 'Color', c);
end
xlabel('Die area (mm^2)'); ylabel('E_{zcs} (mJ/event)');
legend({sprintf('%s band (\\pm%.0f%%)',cases(1).name,100*S.band.esw_rel),cases(1).name, ...
        sprintf('%s band (\\pm%.0f%%)',cases(2).name,100*S.band.esw_rel),cases(2).name}, ...
        'Location','northwest','Box','on','Color','w');
title('Zero-Current Switching Energy E_{zcs} vs A_{die}');

%% ---------- Figure D: Per-event total energy at |I| = I_ref: E_evt = E_zcs + E_over ----------
% choose I_ref for each case
modeTag = S.event.Iref_mode;
figure('Color','w','Position',[220 120 680 480],'Renderer','opengl'); hold on; grid on; box on;

for k = 1:2
    Udc = cases(k).Udc; Ub_kV = cases(k).Ub_kV; Ub_V = Ub_kV*1e3; Ipk = S.Ipk_base*cases(k).Ipk_sc;
    switch lower(S.event.Iref_mode)
        case 'absolute',     Iref = S.event.Iref_abs;
        case 'per_case_rms', Iref = Ipk/sqrt(2);
        case 'per_case_peak',Iref = Ipk;
        otherwise,           Iref = S.event.Iref_abs;
    end
    % per-event components at |I| = Iref
    Coss_ref = S.k_c * (Ub_V^S.alpha_c) * A_die_a * 1e-12; % F
    Ezcs_ref = (Coss_ref * Udc^2) * 1e3;                    % mJ/event
    dvdt_ref = dvdt_of_I(Iref, S);
    Eover_ref= (Udc*Iref^2/S.di_dt + Udc^2*Iref/dvdt_ref) * 1e3;  % mJ/event (scalar)
    Eover_ref = Eover_ref*ones(size(A_die_a));  % flat vs A_die in this simple model
    Eevt      = Ezcs_ref + Eover_ref;           % mJ/event

    % conservative band: combine Ezcs and Eover bounds
    Ezcs_lo = Ezcs_ref*(1 - S.band.esw_rel);  Ezcs_hi = Ezcs_ref*(1 + S.band.esw_rel);
    Eov_lo  = Eover_ref*(1 - S.band.eover_rel); Eov_hi = Eover_ref*(1 + S.band.eover_rel);
    Eevt_lo = Ezcs_lo + Eov_lo;  Eevt_hi = Ezcs_hi + Eov_hi;

    c = [0.36 0.54 0.75] - 0.18*(k-1);
    fill([A_die_a, fliplr(A_die_a)], [Eevt_lo, fliplr(Eevt_hi)], c, 'FaceAlpha',0.14, 'EdgeColor','none');
    plot(A_die_a, Eevt, 'LineWidth',2.0, 'Color', c, 'DisplayName', sprintf('%s',cases(k).name));

    % add a thin line for Ezcs to show composition (optional)
    plot(A_die_a, Ezcs_ref, '--', 'Color', c, 'LineWidth',1.3, 'HandleVisibility','off');
    % annotate current used
    txt = sprintf('%s  (I_{ref} = %.0f A, %s)', cases(k).name, Iref, modeTag);
    plot(nan, nan, 's', 'MarkerSize', 6, 'MarkerEdgeColor', c, 'DisplayName', txt); % dummy for legend note
end
xlabel('Die area (mm^2)'); ylabel('E_{evt} = E_{zcs}+E_{over} (mJ/event)');
title(sprintf('Per-Event Total Energy at |I| = I_{ref} (%s mode)', modeTag));
legend('Location','northwest','Box','on','Color','w');

%% ---------- Figure E: Switching loss vs |I| @ A_sel & f_sw_sel (two panels, bands) ----------
A_sel = S.plotIL.A_sel; fsw_sel = S.plotIL.fsw_sel; ILfac = linspace(0,1,400);
figure('Color','w','Position',[180 90 1200 520],'Renderer','opengl');
tiledlayout(1,2,'Padding','compact','TileSpacing','compact');

for k = 1:2
    Udc = cases(k).Udc; Ub_kV = cases(k).Ub_kV; Ub_V = Ub_kV*1e3; Ipk = S.Ipk_base*cases(k).Ipk_sc;
    IL_sweep = ILfac*Ipk; dvdt_ev = dvdt_of_I(IL_sweep, S);
    Eover_ev = (Udc.*IL_sweep.^2)./S.di_dt + (Udc.^2.*IL_sweep)./dvdt_ev;  % J/event
    Coss_sel = S.k_c * (Ub_V^S.alpha_c) * A_sel * 1e-12; Ezcs_sel = Coss_sel*Udc^2; % J/event
    Pzcs_inv = 3*(fsw_sel*Ezcs_sel)*ones(size(IL_sweep));
    Pover_inv= 3*(fsw_sel*Eover_ev);
    Psw_inv  = Pzcs_inv + Pover_inv;

    Pzcs_low = Pzcs_inv*(1 - S.band.pzcs_rel); Pzcs_high = Pzcs_inv*(1 + S.band.pzcs_rel);
    Psw_low  = Psw_inv *(1 - S.band.psw_rel);  Psw_high  = Psw_inv *(1 + S.band.psw_rel);

    nexttile(k); hold on; grid on; box on;
    fill([IL_sweep, fliplr(IL_sweep)], ([Psw_low,  fliplr(Psw_high)]/1e3), [0 0 0], 'FaceAlpha',0.10,'EdgeColor','none');
    fill([IL_sweep, fliplr(IL_sweep)], ([Pzcs_low, fliplr(Pzcs_high)]/1e3), [0.75 0.35 0.35], 'FaceAlpha',0.10,'EdgeColor','none');
    plot(IL_sweep, Pzcs_inv/1e3, '-',  'LineWidth',2.0, 'Color',[0.75 0.35 0.35]);
    plot(IL_sweep, Pover_inv/1e3,'--', 'LineWidth',2.2, 'Color',[0.18 0.32 0.52]);
    plot(IL_sweep, Psw_inv/1e3,  '-',  'LineWidth',2.4, 'Color',[0 0 0]);
    xlabel('|I_L| (A)'); ylabel('Switching loss (kW)');
    title(sprintf('%s — A_{die}=%d mm^2, f_{sw}=%.1f kHz', cases(k).name, A_sel, fsw_sel/1e3));
    legend({sprintf('Total band (\\pm%.0f%%)',100*S.band.psw_rel), ...
            sprintf('ZCS band (\\pm%.0f%%)',  100*S.band.pzcs_rel), ...
            'ZCS (E_{zcs})','Overlap (dv/dt(|I|))','Total'}, 'Location','northwest','Box','on','Color','w');
end

%% ---------- Figure E (fixed): Total switching loss vs |I| for both cases ----------
A_sel   = S.plotIL.A_sel;
fsw_sel = S.plotIL.fsw_sel;

figure('Color','w','Position',[160 90 940 480],'Renderer','painters'); hold on; grid on; box on;

% colors
col800 = [0.36 0.54 0.75];
col1200= [0.18 0.32 0.52];

for k = 1:2
    Udc   = cases(k).Udc;
    Ub_kV = cases(k).Ub_kV;  Ub_V = Ub_kV*1e3;
    Ipk   = S.Ipk_base * cases(k).Ipk_sc;

    % individual current sweep limited to each Ipk
    IL = linspace(0, Ipk, 400);

    % model
    dvdt_ev  = dvdt_of_I(IL, S);
    Eover_ev = (Udc.*IL.^2)./S.di_dt + (Udc.^2.*IL)./dvdt_ev;     % J/event
    Coss_sel = S.k_c * (Ub_V^S.alpha_c) * A_sel * 1e-12;          % F
    Ezcs_sel = Coss_sel * Udc^2;                                   % J/event (constant)
    Ptot_inv = 3 * fsw_sel * (Ezcs_sel + Eover_ev);                % W total

    % ± band
    Plow  = Ptot_inv * (1 - S.band.psw_rel);
    Phigh = Ptot_inv * (1 + S.band.psw_rel);

    % color select
    if k==1, c=col800; else, c=col1200; end

    % shaded region
    fill([IL/sqrt(2), fliplr(IL/sqrt(2))], ([Plow, fliplr(Phigh)]/1e3), ...
         c, 'FaceAlpha',0.14, 'EdgeColor','none', 'HandleVisibility','off');

    % main curve
    plot(IL/sqrt(2), Ptot_inv/1e3, 'LineWidth',2.5, 'Color',c, ...
         'DisplayName',sprintf('%s',cases(k).name));
end

xlabel('Phase Current (A_{RMS})');
ylabel('Total switching loss (kW)');
% title(sprintf('Total Switching Loss vs |I|  (A_{die}=%d mm^2, f_{sw}=%.1f kHz)', A_sel, fsw_sel/1e3));
legend('Location','northwest','Box','on','Color','w');
set(gca,'FontName','Times New Roman','FontSize',20,'TickDir','out');
















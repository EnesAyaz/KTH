%% ============================================
%  PARAMETRIC PARETO: Efficiency vs Total Volume (single-file script)
%  - Includes separate plots for DC-link capacitance size and cooling size
%  - Fixed zero-current switching loss: P_zcs = Esw * f_sw
%  - Filters to show only points with efficiency >= 99.2%
%  ============================================
clear; clc; close all;
%% ---------------- System definition ----------------
S = struct();

% Powertrain operating conditions
S.Pout       = 300e3;      % Output power [W]
S.ffund      = 500;        % Fundamental frequency [Hz]
S.Udc        = 800;        % DC-link voltage [V]  (set 1200 for HV case)
S.ma         = 1.0;        % Modulation index
S.cosphi     = 1.0;        % Power factor
S.Ipk        = 356*1.5;        % Peak-current scaling factor

% Sweep ranges
S.Fsw_vec    = 10e3:1e3:30e3;   % Switching frequency range [Hz]
S.Adie_vec   = 50:25:400;       % Die area range [mm^2]

% Semiconductor loss model parameters
S.k_r        = 7.2*10e-3;     % Conduction constant
S.alpha_r    = 1.6;        % Conduction exponent
S.Ub_kV      = 1.2;        % Rated blocking voltage [kV] (e.g., 1.2 or 1.7)
S.k_c        = 1.6e4;      % Coss scaling constant
S.alpha_c    = -1;         % Coss exponent
S.dv_dt      = 10e3/1e-6;  % [V/s] placeholder
S.di_dt      = 10e3/1e-6;  % [A/s] placeholder

% Thermal parameters
S.DeltaT_allow = 75;        % Allowed junction-to-ambient rise [K]
S.r_jc_per_mm2 = 2.5;       % K·mm²/W (junction-to-case per mm²)
S.r_ch_module  = 0.025;     % K/W per cooling channel (estimated)

% Topology setup
S.topology.name       = '2L-3Ph';  % label for plots
S.topology.n_dies     = 6;         % number of dies sharing heat
S.topology.n_channels = 3;         % number of parallel cooling channels

% Cooling-to-volume mapping
S.alpha_cool       = 0.1;   % [L·K/W] mapping coefficient (empirical)
S.cool_thickness_L = 0.0;    % Fixed offset volume [L]
S.V_fixed          = 0.0;    % Optional fixed volume for other components [L]

% Capacitor requirement model
S.cap_model   = @cap_model_simple;  % simple model; swap with your lookup if desired
S.Kc          = 4.0;         % scaling factor for ripple (simple model)
S.dv_pp       = 12.5;        % allowed bus ripple voltage [Vpp] (alt. model)
S.cap_density = 200e-6;          % F/L (film capacitor density estimate)

% Semiconductor packaging volume density
S.semi_vol_per_mm2 = 6e-4;   % L/mm² (effective incl. package/busbar)

% Plot appearance
S.colors.front = [0.75 0.35 0.35];  % muted red for Pareto curve
S.eta_floor    = 99.2;              % Show only points with efficiency >= this (%)

%% ---------------- RUN GRID + PARETO ----------------
[Agrid, Fgrid] = meshgrid(S.Adie_vec, S.Fsw_vec);   % Agrid [mm^2], Fgrid [Hz]

% Efficiency & loss map from your model (vectorized)
[eta, Ploss] = map_efficiency(S, Agrid, Fgrid);

% Volumes (semiconductor, capacitor, cooling)
Vsemi = S.semi_vol_per_mm2 .* Agrid * S.topology.n_dies;   % L
Creq  = S.cap_model(S, Agrid, Fgrid);                      % F
Vcap  = Creq ./ S.cap_density;                             % L

% Thermal path → required r_ha → cooler volume
r_tot = S.DeltaT_allow ./ Ploss;                           % K/W
r_jc  = (S.r_jc_per_mm2 ./ Agrid) ./ S.topology.n_dies;    % K/W
r_ch  = (S.r_ch_module) ./ S.topology.n_channels;          % K/W
r_ha  = r_tot - r_jc - r_ch;                               % K/W
r_ha(r_ha <= 0) = NaN;                                     % infeasible

Vcool = S.alpha_cool ./ r_ha + S.cool_thickness_L;         % L

Vtot = Vsemi + Vcap + Vcool + S.V_fixed;                   % L

% Feasibility & efficiency mask
mask = isfinite(eta) & isfinite(Vtot) & eta >= S.eta_floor & ~isnan(r_ha);

% Flatten for Pareto
xV   = Vtot(mask);
yEff = eta(mask);
Ff   = Fgrid(mask);

% Pareto (min volume, max efficiency)
pareto_idx = pareto_front_2d([xV, -yEff]);
xVf = xV(pareto_idx);
yEfff = yEff(pareto_idx);
[xVf, order] = sort(xVf, 'ascend');
yEfff = yEfff(order);

%% ---------------- PLOT A — Pareto (η vs Volume) ----------------
figure('Color','w','Position',[200 160 900 520],'Renderer','painters');
tiledlayout(1,2,'Padding','compact','TileSpacing','compact');

% Scatter map + Pareto curve
nexttile(1);
scatter(xV, yEff, 18, Ff/1e3, 'filled'); hold on;
plot(xVf, yEfff, '-', 'Color', S.colors.front, 'LineWidth', 2);
xlabel('Total volume (L)','FontName','Times New Roman','FontSize',16);
ylabel('Efficiency (%)','FontName','Times New Roman','FontSize',16);
title(sprintf('Pareto: %s, U_{dc} = %g V', S.topology.name, S.Udc), 'FontWeight','normal');
grid on; box on;
cb = colorbar; ylabel(cb,'f_{sw} (kHz)');
set(gca,'TickDir','out','FontName','Times New Roman','FontSize',13);
ylim([S.eta_floor, 100]);   % start efficiency at 99.2%

% Highlight a few knee points
if ~isempty(xVf)
    knee = round(linspace(1, numel(xVf), min(5,numel(xVf))));
    plot(xVf(knee), yEfff(knee), 'o', 'Color', S.colors.front, ...
        'MarkerSize', 6, 'LineWidth',1.2, 'MarkerFaceColor','w');
end

% Volume breakdown at Pareto points
nexttile(2);
[Vsemi_p, Vcap_p, Vcool_p] = breakdown_at_points(xVf, yEfff, xV, yEff, Vsemi(mask), Vcap(mask), Vcool(mask));
if ~isempty(Vsemi_p)
    barh([Vsemi_p(:), Vcap_p(:), Vcool_p(:)], 'stacked'); 
    set(gca,'YDir','reverse','FontName','Times New Roman','FontSize',12);
    yticks(1:numel(xVf)); yticklabels(compose('Pt %d',1:numel(xVf)));
else
    barh(0,0); yticks([]); % graceful handling if no Pareto points
end
xlabel('Volume (L)'); 
legend({'Semiconductor','DC-link cap','Cooling'},'Location','southoutside','Orientation','horizontal','Box','off');
title('Volume breakdown (Pareto points)'); grid on; box on;

fprintf('Pareto front points (Volume [L], Efficiency [%%]):\n');
disp([xVf(:), yEfff(:)]);

%% ---------------- PLOT B — DC-LINK CAPACITANCE (µF) ----------------
Creq_uF = 1e6 * Creq;   % convert F → µF

figure('Color','w','Position',[120 120 780 520],'Renderer','painters');
axes1 = axes('FontName','Times New Roman','FontSize',15,'LineWidth',1.1);
hold(axes1,'on'); box on; set(axes1,'Layer','top');

% Filled contour (single-hue muted blue)
nLevels = 10;
contourf(Agrid, Fgrid/1e3, Creq_uF, nLevels, 'LineStyle','none');

% Muted blue colormap
nC = 256;
stops = [ ...
    1.00 1.00 1.00  % near-white
    0.92 0.95 0.98  % very light blue
    0.75 0.84 0.93  % light muted blue
    0.56 0.70 0.86  % mid muted blue
    0.36 0.54 0.75  % deep muted blue
    0.18 0.32 0.52  % darkest
];
xi = linspace(0,1,size(stops,1));
cmap_blue = interp1(xi, stops, linspace(0,1,nC));
colormap(cmap_blue);

xlabel('Die area (mm^2)','FontSize',18);
ylabel('Switching frequency (kHz)','FontSize',18);
title('DC-link capacitance requirement (µF)','FontWeight','normal');
cbC = colorbar; ylabel(cbC,'C_{req} (µF)','FontSize',16);
set(gca,'TickDir','out');

%% ---------------- PLOT C — COOLING SIZE (L) ----------------
figure('Color','w','Position',[940 120 780 520],'Renderer','painters');
axes2 = axes('FontName','Times New Roman','FontSize',15,'LineWidth',1.1);
hold(axes2,'on'); box on; set(axes2,'Layer','top');

% Filled contour (single-hue muted green)
nLevels = 10;
contourf(Agrid, Fgrid/1e3, Vcool, nLevels, 'LineStyle','none');

% Muted green colormap
stops_g = [ ...
    1.00 1.00 1.00  % near-white
    0.94 0.98 0.94  % very light green
    0.82 0.92 0.84  % light muted green
    0.67 0.84 0.71  % mid muted green
    0.45 0.65 0.45  % deep muted green
    0.25 0.45 0.28  % darkest
];
cmap_green = interp1(xi, stops_g, linspace(0,1,nC));
colormap(cmap_green);

xlabel('Die area (mm^2)','FontSize',18);
ylabel('Switching frequency (kHz)','FontSize',18);
title('Cooling volume (L) required (from r_{ha})','FontWeight','normal');
cbV = colorbar; ylabel(cbV,'V_{cool} (L)','FontSize',16);
set(gca,'TickDir','out');


%% === Efficiency field plot: η(A_die, f_sw) ===
% Assumes you already computed:
%   Agrid [mm^2], Fgrid [Hz], eta [%]

figure('Color','w','Position',[220 180 780 520],'Renderer','painters'); % vector-friendly
axes1 = axes('FontName','Times New Roman','FontSize',15,'LineWidth',1.1);
hold(axes1,'on'); box on; grid off; set(axes1,'Layer','top');

% Clamp/visualize only >= 99.2% if desired
eta_floor = 99.2;
eta_plot  = max(eta, eta_floor);

% Filled contour (no edge lines)
nLevels = 10;  % more levels = smoother gradient
contourf(Agrid, Fgrid/1e3, eta_plot, nLevels, 'LineStyle','none');

% Single-hue muted blue colormap
nC = 256;
stops = [ ...
    1.00 1.00 1.00  % near-white
    0.92 0.95 0.98  % very light blue
    0.75 0.84 0.93  % light muted blue
    0.56 0.70 0.86  % mid muted blue
    0.36 0.54 0.75  % deep muted blue
    0.18 0.32 0.52  % darkest
];
xi = linspace(0,1,size(stops,1));
cmap = interp1(xi, stops, linspace(0,1,nC));
colormap(cmap);

% Optional: thin isolines at key efficiencies
% isoVals = [99.2 99.4 99.6 99.7 99.75 99.8];
% [~, hIso] = contour(Agrid, Fgrid/1e3, eta, isoVals, ...
%     'LineColor',[0 0 0], 'LineWidth',0.75);
% leg = legend(hIso, string(isoVals) + " %", 'Location','northwest');
% set(leg,'Box','on','EdgeColor',[0.7 0.7 0.7],'Color','w','FontSize',12);

% Axes + labels
xlabel('Die area (mm^2)','FontSize',20);
ylabel('Switching frequency (kHz)','FontSize',20);
xlim([min(Agrid(:)) max(Agrid(:))]);
ylim([min(Fgrid(:))/1e3 max(Fgrid(:))/1e3]);
set(gca,'TickDir','out');

% Colorbar
c = colorbar('FontSize',14,'FontName','Times New Roman');
ylabel(c,'Efficiency (%)','FontSize',20);
caxis([eta_floor 100]);   % start at 99.2%

axis tight


%% ===== Local functions (must be at the end of the script) =====
function [eta, Ploss] = map_efficiency(S, Agrid, Fgrid)
% Loss composition: P_tot = 3*(2*P_on + P_zcs + P_over)
Ub    = S.Ub_kV*1e3;
k_r   = S.k_r;   alpha_r = S.alpha_r;
k_c   = S.k_c;   alpha_c = S.alpha_c;
Udc   = S.Udc;
ffund = S.ffund; %#ok<NASGU> (kept for clarity)

% Peak current (scaled as in your code)
Ipk =S.Ipk;

% Conduction term via numeric integration over theta (0..pi window shifted by pf angle)
nTheta   = 2000;
theta_pf = acos(S.cosphi);
theta    = linspace(theta_pf, theta_pf+pi, nTheta);
dth      = theta(2)-theta(1);

IL = Ipk * sin(theta - theta_pf);     % 1 x nTheta
Du = (1 + S.ma * sin(theta))/2;
Dl = (1 - S.ma * sin(theta))/2;

r_on = k_r .* (S.Ub_kV.^alpha_r) ./ Agrid;     % Ω

Pc_int = sum((IL.^2 .* (Du + Dl)) * dth, 2);   % integral scalar
P_on   = r_on .* Pc_int;                       % W per (Adie,Fsw)
P_on   = P_on / (2*pi) * 2;                    % match your 2*P_c/(2*pi)

% Zero-current switching energy (per event) and power
Coss = k_c .* (Ub.^alpha_c) .* Agrid * 1e-12;  % F
Esw  = Coss .* (Udc.^2);                       % J
P_zcs = Esw .* Fgrid;                          % *** Correct scaling: ∝ f_sw ***

% Overlap energy (placeholder term per your code)
dvdt = S.dv_dt; didt = S.di_dt;
ILabs = abs(IL);

% f(θ) as in your loop:
f_theta = Udc*(ILabs.^2)/didt + Udc^2*(ILabs)/dvdt;  % J per "event" proxy

% Average over the half-cycle (θ spanning length = π):
avg_f = (sum(f_theta, 2) * dth) / pi;   % scalar

% Power scales with switching events per second:
P_over = Fgrid .* avg_f;                % ∝ f_sw (matches your loop)

P_tot = 3 .* ( 2*P_on + P_zcs + P_over );
Ploss=P_tot;
eta   = 100 .* S.Pout ./ (S.Pout + P_tot);
end

function Creq = cap_model_simple(S, ~, Fgrid)
% Simple scaling: C ~ Kc * Ipk / (Udc * Fsw)
Ipk  = S.Ipk;
Creq = S.Kc .* Ipk ./ (S.Udc .* Fgrid);   % F
% If you prefer a strict ΔVpp constraint, swap to:
% Creq = Ipk ./ (S.dv_pp .* Fgrid);
end

function idx = pareto_front_2d(X)
% X(:,1): minimize (volume), X(:,2): minimize (-efficiency) -> maximize efficiency
n = size(X,1);
isND = true(n,1);
for i = 1:n
    if ~isND(i), continue; end
    dom = all(bsxfun(@le, X, X(i,:)), 2) & any(bsxfun(@lt, X, X(i,:)), 2);
    isND(dom) = false;
end
idx = find(isND);
end

function [Vsemi_p, Vcap_p, Vcool_p] = breakdown_at_points(xVf, yEf, xV, yE, Vsemi, Vcap, Vcool)
Vsemi_p = zeros(size(xVf));
Vcap_p  = zeros(size(xVf));
Vcool_p = zeros(size(xVf));
for k = 1:numel(xVf)
    d = hypot(xV - xVf(k), yE - yEf(k));
    [~,i] = min(d);
    Vsemi_p(k) = Vsemi(i);
    Vcap_p(k)  = Vcap(i);
    Vcool_p(k) = Vcool(i);
end
end
%%

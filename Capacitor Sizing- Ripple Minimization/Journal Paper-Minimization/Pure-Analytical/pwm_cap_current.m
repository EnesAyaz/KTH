%% ================================================================
%  Parametric PWM Capacitor Current Plotter
%  EJ2311 — Modulation of Power Converters, KTH
%
%  Each phase leg: switch signal S = 1 during [theta, theta+d] (mod 1)
%  DC current:     i_dc = ia*da + ib*db + ic*dc
%  Cap current:    i_cap = ia*Sa + ib*Sb + ic*Sc - i_dc
%
%  Usage: edit the PARAMETERS block below, then run.
%% ================================================================
clear; clc; close all;

%% ── PARAMETERS (edit here) ──────────────────────────────────────
% Duty cycles  (0 < d < 1)
ma=0.2;
theta=120;
da = (1+ma*sin(theta*pi/180))/2;
db = (1+ma*sin(theta*pi/180-2*pi/3))/2;
dc = (1+ma*sin(theta*pi/180+2*pi/3))/2;

% Phase currents  (p.u.)
pf=0.8;
ia = sin(theta*pi/180-acos(pf));
ib = sin(theta*pi/180-2*pi/3-acos(pf));
ic = sin(theta*pi/180+2*pi/3-acos(pf));


% Carrier phase shifts  (normalised, 0 … 1)
%   0   = conventional (all aligned)
%   Set theta_b / theta_c to shift leg B / C carrier
theta_a = da/2-1/2;
theta_b = db/2-1/2;   % try  da-dc  for optimal alignment
theta_c = dc/2-1/2-dc+da;   % try  da-dc  for optimal alignment
% 
% theta_a = 0;
% theta_b = 0;   % try  da-dc  for optimal alignment
% theta_c = 0;   % try  da-dc  for optimal alignment

% Resolution
N = 1000;       % number of time samples per switching period
%% ──────────────────────────────────────────────────────────────

tau = linspace(0, 1, N+1);   % normalised time [0,1]

%% Generate switching signals  (1 during ON interval, 0 otherwise)
Sa = make_pulse(da, theta_a-da/2+1/2, tau);
Sb = make_pulse(db, theta_b-db/2+1/2, tau);
Sc = make_pulse(dc, theta_c-dc/2+1/2, tau);

%% DC component and capacitor current
i_dc   = ia*da + ib*db + ic*dc;
%i_cap  = ia*Sa + ib*Sb + ic*Sc - i_dc;
i_cap  = ia*Sa + ib*Sb + ic*Sc ;

%% RMS
rms_val = sqrt(mean((i_cap).^2));

%% ── PLOT ────────────────────────────────────────────────────────
fig = figure('Color','white','Position',[100 80 1100 700]);

% ── Colour palette (KTH-ish) ─────────────────────────────────
col_a   = [0.00 0.28 0.57];    % dark blue
col_b   = [0.38 0.60 0.82];    % sky blue
col_c   = [0.85 0.53 0.10];    % amber
col_cap = [0.63 0.16 0.12];    % dark red

%% ---- Subplot 1: Switching signals --------------------------------
ax1 = subplot(2,1,1);
hold on; box on; grid on;

% Vertical offsets so all three signals are visible on one axes
offset_a = 2.2;
offset_b = 1.1;
offset_c = 0.0;

% Draw filled step plots
fill_step(tau, Sa + offset_a, col_a,  0.25, ax1);
fill_step(tau, Sb + offset_b, col_b,  0.25, ax1);
fill_step(tau, Sc + offset_c, col_c,  0.25, ax1);

% Draw the step lines on top
stairs(tau, Sa + offset_a, 'Color', col_a,  'LineWidth', 2.0);
stairs(tau, Sb + offset_b, 'Color', col_b,  'LineWidth', 2.0);
stairs(tau, Sc + offset_c, 'Color', col_c,  'LineWidth', 2.0);

% Y-axis tick labels
ax1.YTick      = [0.5, 0.5+offset_b, 0.5+offset_a];
ax1.YTickLabel = {'Sc','Sb','Sa'};
ax1.YLim       = [-0.15, offset_a + 1.15];
ax1.XLim       = [0, 1];

ylabel('Switch state', 'FontWeight','bold');
% title(sprintf(['Conventional PWM — \\theta_a=%.2f, \\theta_b=%.2f, \\theta_c=%.2f\n'...
%                'da=%.2f  db=%.2f  dc=%.2f'], ...
%                theta_a*360, theta_b*360, theta_c*360, da, db, dc), ...
%       'FontWeight','bold','FontSize',12);

title(sprintf(['PWM — \\theta_a=%.2f, \\theta_b=%.2f, \\theta_c=%.2f\n'...
               'da=%.2f  db=%.2f  dc=%.2f'], ...
               theta_a*360, theta_b*360, theta_c*360, da, db, dc), ...
      'FontWeight','bold','FontSize',12);

legend( sprintf('Sa   ia = %+.2f   da = %.2f', ia, da), ...
        sprintf('Sb   ib = %+.2f   db = %.2f', ib, db), ...
        sprintf('Sc   ic = %+.2f   dc = %.2f', ic, dc), ...
        'Location','northeast','FontSize',9);

ax1.FontSize = 11;
ax1.GridAlpha = 0.4;

%% ---- Subplot 2: Capacitor current --------------------------------
ax2 = subplot(2,1,2);
hold on; box on; grid on;

% Shaded fill
fill_step2(tau, i_cap, col_cap, 0.18, ax2);
stairs(tau, i_cap, 'Color', col_cap, 'LineWidth', 2.0);
yline(0, 'Color',[0.5 0.5 0.5], 'LineWidth', 0.8, 'LineStyle','--');

ylabel('i_{inv}  (p.u.)', 'FontWeight','bold');
xlabel('Normalised time  \tau', 'FontWeight','bold');
title(sprintf('Inverter Input Current   RMS = %.4f  p.u.', rms_val), ...
      'FontWeight','bold','FontSize',12);
ax2.XLim = [0, 1];
ax2.FontSize = 11;
ax2.GridAlpha = 0.4;

%% Link axes and tighten layout
linkaxes([ax1 ax2],'x');
set(fig,'PaperPositionMode','auto');

fprintf('\n=== Results ===\n');
fprintf('  i_dc  = %.4f p.u.\n', i_dc);
fprintf('  RMS   = %.4f p.u.\n', rms_val);
fprintf('  RMS²  = %.4f p.u.²\n', rms_val^2);

%% ================================================================
%  LOCAL FUNCTIONS
%% ================================================================

function S = make_pulse(d, theta, tau)
% Returns a PWM pulse: 1 during [theta, theta+d] (mod 1), else 0.
% Works correctly even when the pulse wraps around.
    theta = mod(theta, 1);
    t_on  = mod(tau - theta, 1);          % time since rising edge
    S     = double(t_on < d);
end

function fill_step(tau, sig, col, alpha_val, ax)
% Draws a filled step-plot polygon on axes ax.
    axes(ax); %#ok<LAXES>
    % Build staircase x,y vectors
    n   = numel(tau);
    xs  = reshape([tau(1:n-1); tau(2:n)], 1, []);
    ys  = reshape([sig(1:n-1); sig(1:n-1)], 1, []);
    % Close the polygon at y=0 (or the offset baseline)
    baseline = min(ys) - 0;          % close at the signal minimum
    xpoly = [xs, fliplr(xs)];
    ypoly = [ys, baseline*ones(1, numel(ys))];
    fill(xpoly, ypoly, col, 'FaceAlpha', alpha_val, ...
         'EdgeColor', 'none');
end

function fill_step2(tau, sig, col, alpha_val, ax)
% Draws a filled step-plot polygon on axes ax.
    axes(ax); %#ok<LAXES>
    % Build staircase x,y vectors
    n   = numel(tau);
    xs  = reshape([tau(1:n-1); tau(2:n)], 1, []);
    ys  = reshape([sig(1:n-1); sig(1:n-1)], 1, []);
    % Close the polygon at y=0 (or the offset baseline)
    baseline = 0;          % close at the signal minimum
    xpoly = [xs, fliplr(xs)];
    ypoly = [ys, baseline*ones(1, numel(ys))];
    fill(xpoly, ypoly, col, 'FaceAlpha', alpha_val, ...
         'EdgeColor', 'none');
end


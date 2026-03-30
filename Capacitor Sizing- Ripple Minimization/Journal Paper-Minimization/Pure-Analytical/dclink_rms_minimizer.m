%% DC-Link Capacitor RMS Current Minimizer — Analytical
% =========================================================
% For a single switching interval with given duty cycles and
% phase currents, finds optimal carrier phase shifts (theta_b,
% theta_c) that minimize capacitor RMS current analytically.
% No sweep, no LUT, no optimization toolbox required.
%
% Theory:
%   I_cap_rms^2 = ia^2*da*(1-da) + ib^2*db*(1-db) + ic^2*dc*(1-dc)
%               + 2*ia*ib*(lambda_ab - da*db)
%               + 2*ia*ic*(lambda_ac - da*dc)
%               + 2*ib*ic*(lambda_bc - db*dc)
%
%   lambda_xy = piecewise-linear overlap(dx, dy, delta_theta_xy)
%
%   Objective is piecewise-linear in (theta_b, theta_c).
%   Minimum is always at a breakpoint — evaluate ~60-80 candidates.
%
% Author : Based on analytical framework for IPEC 2026 paper
% Usage  : Run as-is, or call find_optimal_phase_shifts() directly

clear; clc; close all;

%% ── Operating point ─────────────────────────────────────────────────────────
ma          = 0.8;          % Modulation index
Iph         = 1.0;          % Peak phase current amplitude (p.u.)
pf          = 0.95;         % Power factor
theta_fund  = deg2rad(85);  % Fundamental phase angle for this interval (rad)

% Duty cycles from SPWM (da + db + dc = 1.5)
da = 0.5 + 0.5*ma*cos(theta_fund);
db = 0.5 + 0.5*ma*cos(theta_fund - 2*pi/3);
dc = 0.5 + 0.5*ma*cos(theta_fund - 4*pi/3);

% Phase currents (lagging by power factor angle), ia+ib+ic = 0
phi_pf = acos(pf);
ia = Iph * cos(theta_fund - phi_pf);
ib = Iph * cos(theta_fund - 2*pi/3 - phi_pf);
ic = Iph * cos(theta_fund - 4*pi/3 - phi_pf);

fprintf('============================================================\n');
fprintf('  DC-Link Capacitor RMS Minimizer — Analytical (MATLAB)\n');
fprintf('============================================================\n\n');
fprintf('  Operating point:\n');
fprintf('    ma=%.2f,  p.f.=%.2f,  theta_fund=%.1f deg\n', ...
        ma, pf, rad2deg(theta_fund));
fprintf('\n  Duty cycles:\n');
fprintf('    da=%.4f,  db=%.4f,  dc=%.4f  (sum=%.4f)\n', da, db, dc, da+db+dc);
fprintf('\n  Phase currents (p.u.):\n');
fprintf('    ia=%.4f,  ib=%.4f,  ic=%.4f  (sum=%.2e)\n', ia, ib, ic, ia+ib+ic);

%% ── Run analytical optimizer ─────────────────────────────────────────────────
[tb_opt, tc_opt, rms_opt, rms_conv, candidates] = ...
    find_optimal_phase_shifts(ia, ib, ic, da, db, dc);

fprintf('\n  Results:\n');
fprintf('    Conventional (tb=tc=0):  RMS = %.6f p.u.\n', rms_conv);
fprintf('    Optimal (analytical):    RMS = %.6f p.u.\n', rms_opt);
fprintf('    Optimal theta_b = %.4f  (%.2f deg)\n', tb_opt, tb_opt*360);
fprintf('    Optimal theta_c = %.4f  (%.2f deg)\n', tc_opt, tc_opt*360);
if rms_conv > 0
    reduction = 100*(rms_conv - rms_opt)/rms_conv;
else
    reduction = 0;
end
fprintf('    RMS reduction: %.2f%%\n', reduction);
fprintf('    Candidates evaluated: %d\n', size(candidates,1));

%% ── Cross-check with brute-force sweep ───────────────────────────────────────
fprintf('\n  Cross-check (brute-force sweep 500x500)...\n');
N = 500;
tb_s = linspace(0, 1, N+1); tb_s = tb_s(1:end-1);
tc_s = linspace(0, 1, N+1); tc_s = tc_s(1:end-1);
[TB, TC] = meshgrid(tb_s, tc_s);
RMS2_grid = arrayfun(@(tb,tc) cap_rms_squared(ia,ib,ic,da,db,dc,tb,tc), TB, TC);
[min_val, min_idx] = min(RMS2_grid(:));
rms_sweep = sqrt(max(min_val, 0));
fprintf('    Sweep minimum RMS = %.6f p.u.\n', rms_sweep);
if abs(rms_opt - rms_sweep) < 1e-4
    fprintf('    Analytical matches sweep: YES\n');
else
    fprintf('    Analytical matches sweep: NO  (diff=%.2e)\n', abs(rms_opt-rms_sweep));
end

%% ── Plots ────────────────────────────────────────────────────────────────────
N_wave = 10000;
tau = linspace(0, 1, N_wave+1); tau = tau(1:end-1);

% Reconstruct waveforms
[icap_conv, Sa_c, Sb_c, Sc_c] = reconstruct_waveforms(ia,ib,ic,da,db,dc,0,0,tau);
[icap_opt,  Sa_o, Sb_o, Sc_o] = reconstruct_waveforms(ia,ib,ic,da,db,dc,tb_opt,tc_opt,tau);

% Compute RMS from waveform (verification)
rms_conv_w = sqrt(mean(icap_conv.^2));
rms_opt_w  = sqrt(mean(icap_opt.^2));

fig = figure('Color',[0.051 0.067 0.090], 'Position',[100 50 1400 900]);

bg_col    = [0.051 0.067 0.090];
panel_col = [0.086 0.106 0.133];
grid_col  = [0.129 0.149 0.173];
text_col  = [0.545 0.580 0.616];
white_col = [0.902 0.929 0.953];
col_a = [0.969 0.506 0.400];
col_b = [0.475 0.753 1.000];
col_c = [0.337 0.827 0.392];
col_cap = [1.000 0.651 0.341];
col_conv = [0.545 0.580 0.616];

% ── Subplot 1: Switching signals conventional ─────────────────────────────
ax1 = subplot(3,3,[1 2]);
set(ax1,'Color',panel_col,'XColor',text_col,'YColor',text_col,...
        'GridColor',grid_col,'FontSize',8);
hold on; box on; grid on;
offset = 1.4;
plot(tau, Sa_c + 2*offset, 'Color',col_a, 'LineWidth',1.5);
plot(tau, Sb_c + 1*offset, 'Color',col_b, 'LineWidth',1.5);
plot(tau, Sc_c + 0*offset, 'Color',col_c, 'LineWidth',1.5);
xlim([0 1]); ylim([-0.2 3.2]);
yticks([0.5 0.5+offset 0.5+2*offset]);
yticklabels({'Sc','Sb','Sa'});
xlabel('Normalized time \tau', 'Color',text_col);
title(sprintf('Conventional PWM  (\\theta_b=\\theta_c=0)  —  RMS = %.4f p.u.', rms_conv), ...
      'Color',white_col,'FontSize',10);

% ── Subplot 2: Switching signals optimal ──────────────────────────────────
ax2 = subplot(3,3,[4 5]);
set(ax2,'Color',panel_col,'XColor',text_col,'YColor',text_col,...
        'GridColor',grid_col,'FontSize',8);
hold on; box on; grid on;
plot(tau, Sa_o + 2*offset, 'Color',col_a, 'LineWidth',1.5);
plot(tau, Sb_o + 1*offset, 'Color',col_b, 'LineWidth',1.5);
plot(tau, Sc_o + 0*offset, 'Color',col_c, 'LineWidth',1.5);
xlim([0 1]); ylim([-0.2 3.2]);
yticks([0.5 0.5+offset 0.5+2*offset]);
yticklabels({'Sc','Sb','Sa'});
xlabel('Normalized time \tau', 'Color',text_col);
title(sprintf('Optimal PWM  (\\theta_b=%.3f, \\theta_c=%.3f)  —  RMS = %.4f p.u.   [%.1f%% reduction]', ...
      tb_opt, tc_opt, rms_opt, reduction), 'Color',white_col,'FontSize',10);

% ── Subplot 3: Capacitor current comparison ───────────────────────────────
ax3 = subplot(3,3,[7 8]);
set(ax3,'Color',panel_col,'XColor',text_col,'YColor',text_col,...
        'GridColor',grid_col,'FontSize',8);
hold on; box on; grid on;
plot(tau, icap_conv, 'Color',conv_col_fill(col_conv, 0.6), 'LineWidth',1.2, ...
     'DisplayName', sprintf('Conventional  RMS=%.4f',rms_conv_w));
plot(tau, icap_opt,  'Color',col_cap, 'LineWidth',1.5, ...
     'DisplayName', sprintf('Optimal  RMS=%.4f',rms_opt_w));
yline(0,'--','Color',grid_col,'LineWidth',0.8);
xlim([0 1]);
xlabel('Normalized time \tau','Color',text_col);
ylabel('i_{cap} (p.u.)','Color',text_col);
title('DC-Link Capacitor Current','Color',white_col,'FontSize',10);
leg = legend('Location','northeast','FontSize',8);
set(leg,'Color',panel_col,'TextColor',white_col,'EdgeColor',grid_col);

% ── Subplot 4: RMS landscape heatmap ──────────────────────────────────────
ax4 = subplot(3,3,[3 6 9]);
set(ax4,'Color',panel_col,'XColor',text_col,'YColor',text_col,...
        'GridColor',grid_col,'FontSize',8);
hold on; box on;

RMS_map = sqrt(max(RMS2_grid, 0));
imagesc(tb_s, tc_s, RMS_map);
set(ax4,'YDir','normal');
colormap(ax4, flip(hot(256)));
cb = colorbar(ax4);
cb.Color = text_col;
ylabel(cb, 'I_{cap} RMS (p.u.)','Color',text_col,'FontSize',9);

% Candidate points
if ~isempty(candidates)
    plot(candidates(:,1), candidates(:,2), 'o', ...
         'Color',[0.2 0.2 0.2],'MarkerSize',3,'MarkerFaceColor',[0.2 0.2 0.2]);
end
% Optimal
plot(tb_opt, tc_opt, 'p', 'Color',col_c, 'MarkerSize',16, ...
     'MarkerFaceColor',col_c, 'DisplayName', ...
     sprintf('Optimal (%.3f, %.3f)',tb_opt,tc_opt));
% Conventional
plot(0, 0, 's', 'Color',col_b,'MarkerSize',10,'MarkerFaceColor',col_b, ...
     'DisplayName','Conventional');

xlabel('\theta_b (normalized)','Color',text_col);
ylabel('\theta_c (normalized)','Color',text_col);
title({'RMS Landscape';'(analytical breakpoints as dots)'},...
      'Color',white_col,'FontSize',10);
leg2 = legend('Location','northeast','FontSize',8);
set(leg2,'Color',panel_col,'TextColor',white_col,'EdgeColor',grid_col);
xlim([0 1]); ylim([0 1]);

% Main title
annotation(fig,'textbox',[0 0.96 1 0.04],'String', ...
    'DC-Link Capacitor RMS Minimizer — Analytical Solution', ...
    'Color',white_col,'FontSize',14,'FontWeight','bold', ...
    'HorizontalAlignment','center','EdgeColor','none', ...
    'BackgroundColor','none');

exportgraphics(fig, 'dclink_rms_result.png', ...
               'Resolution',150,'BackgroundColor',bg_col);
fprintf('\n  Plot saved.\n');
fprintf('============================================================\n');


%% ═══════════════════════════════════════════════════════════════════════════
%%  LOCAL FUNCTIONS
%% ═══════════════════════════════════════════════════════════════════════════

function ov = overlap(dx, dy, delta)
% OVERLAP  Exact piecewise-linear overlap between two pulses.
%   dx, dy  : pulse widths in [0,1]
%   delta   : relative phase offset (any real, taken mod 1)
%
%   Pulse x occupies [0, dx), pulse y occupies [delta, delta+dy) mod 1.
%   Returns the total overlap duration in [0, min(dx,dy)].

    delta = mod(delta, 1.0);
    % Forward overlap (no wrap)
    ov1 = max(0, min([dx, dy, dx + dy - delta]));
    % Wrap-around overlap
    ov2 = max(0, min([dx, dy, dx + dy - (1.0 - delta)]));
    ov  = ov1 + ov2;
end


function rms2 = cap_rms_squared(ia, ib, ic, da, db, dc, theta_b, theta_c)
% CAP_RMS_SQUARED  Exact closed-form capacitor RMS^2.
%   theta_a = 0 fixed; theta_b, theta_c in [0,1) normalized.

    % Fixed terms (no phase-shift dependence)
    F0 = ia^2*da*(1-da) + ib^2*db*(1-db) + ic^2*dc*(1-dc);

    % Pairwise overlaps
    lam_ab = overlap(da, db, theta_b);
    lam_ac = overlap(da, dc, theta_c);
    lam_bc = overlap(db, dc, theta_c - theta_b);

    % Cross terms
    cross = 2*ia*ib*(lam_ab - da*db) ...
          + 2*ia*ic*(lam_ac - da*dc) ...
          + 2*ib*ic*(lam_bc - db*dc);

    rms2 = F0 + cross;
end


function pts = breakpoints(dx, dy)
% BREAKPOINTS  Phase values where slope of overlap(dx,dy,delta) changes.
%   Returns unique values in [0,1).

    raw = [0, abs(dx-dy), dx+dy, 1-(dx+dy), 1-abs(dx-dy)];
    pts = unique(mod(raw, 1.0));
    pts = pts(pts >= 0 & pts < 1.0);
end


function [tb_opt, tc_opt, rms_opt, rms_conv, candidates] = ...
         find_optimal_phase_shifts(ia, ib, ic, da, db, dc)
% FIND_OPTIMAL_PHASE_SHIFTS  Analytical minimizer — no sweep, no LUT.
%
%   Evaluates I_cap_rms^2 at all breakpoint combinations of (theta_b, theta_c).
%   Since the objective is piecewise-linear, the global minimum is guaranteed
%   to be at one of these breakpoints.
%
%   Returns:
%     tb_opt, tc_opt  : optimal phase shifts (normalized [0,1))
%     rms_opt         : minimum capacitor RMS current
%     rms_conv        : conventional RMS (theta_b=theta_c=0)
%     candidates      : Nx3 array [theta_b, theta_c, rms] for all evaluated pts

    bp_ab = breakpoints(da, db);   % theta_b breakpoints from lambda_ab
    bp_ac = breakpoints(da, dc);   % theta_c breakpoints from lambda_ac
    bp_bc = breakpoints(db, dc);   % relative breakpoints from lambda_bc

    candidates = [];

    % For each theta_b candidate, add theta_c candidates:
    % direct from lambda_ac AND derived from lambda_bc (shifted by theta_b)
    for tb = bp_ab
        tc_set = unique([bp_ac, mod(tb + bp_bc, 1.0)]);
        for tc = tc_set
            rms2 = cap_rms_squared(ia, ib, ic, da, db, dc, tb, tc);
            candidates(end+1, :) = [tb, tc, sqrt(max(rms2, 0))]; %#ok<AGROW>
        end
    end

    % Also: for each theta_c candidate, derive theta_b from lambda_bc
    for tc = bp_ac
        tb_set = unique(mod(tc - bp_bc, 1.0));
        for tb = tb_set
            rms2 = cap_rms_squared(ia, ib, ic, da, db, dc, tb, tc);
            candidates(end+1, :) = [tb, tc, sqrt(max(rms2, 0))]; %#ok<AGROW>
        end
    end

    % Remove duplicates
    candidates = unique(candidates, 'rows');

    % Find minimum
    [rms_opt, idx] = min(candidates(:, 3));
    tb_opt = candidates(idx, 1);
    tc_opt = candidates(idx, 2);

    % Conventional (single carrier)
    rms_conv = sqrt(max(cap_rms_squared(ia, ib, ic, da, db, dc, 0, 0), 0));
end


function [icap, Sa, Sb, Sc] = reconstruct_waveforms(ia, ib, ic, da, db, dc, ...
                                                      theta_b, theta_c, tau)
% RECONSTRUCT_WAVEFORMS  Build i_cap(tau) waveform for visualization.

    Sa = pulse_wave(da, 0,        tau);
    Sb = pulse_wave(db, theta_b,  tau);
    Sc = pulse_wave(dc, theta_c,  tau);

    i_dc_avg = ia*da + ib*db + ic*dc;
    icap = ia*Sa + ib*Sb + ic*Sc - i_dc_avg;
end


function s = pulse_wave(d, theta, tau)
% PULSE_WAVE  Generate a 0/1 pulse of width d starting at theta (mod 1).

    start = mod(theta, 1.0);
    stop  = mod(theta + d, 1.0);
    if start < stop
        s = double(tau >= start & tau < stop);
    else
        s = double(tau >= start | tau < stop);
    end
end


function c = conv_col_fill(col, alpha)
% Blend color with background for transparency simulation
    bg = [0.051 0.067 0.090];
    c  = alpha*col + (1-alpha)*bg;
end

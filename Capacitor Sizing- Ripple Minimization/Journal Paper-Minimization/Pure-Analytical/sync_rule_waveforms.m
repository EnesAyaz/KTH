%% Adaptive Multi-Carrier PWM — Simple Synchronization Rule
% ============================================================
% For given duty cycles (da, db, dc) and phase currents (ia, ib, ic),
% applies the simple edge-alignment rule and plots the result.
%
% Rule:
%   1) Identify the lone-sign leg (positive or negative) → leg A
%   2) Align START of leg B carrier with START of leg A  → theta_b = 0
%   3) Align END   of leg C carrier with END   of leg A  → theta_c = da - dc
%
% Both phase shifts are just one subtraction each. No LUT, no sweep.

clear; clc; close all;

%% ── USER INPUTS ─────────────────────────────────────────────────────────────

da = 0.75;    % Duty cycle leg A
db = 0.55;    % Duty cycle leg B
dc = 0.20;    % Duty cycle leg C  (must satisfy da+db+dc = 1.5)

ia =  1.0;    % Phase current leg A (p.u.)
ib = -0.6;    % Phase current leg B (p.u.)
ic = -0.4;    % Phase current leg C (p.u.)  (must satisfy ia+ib+ic = 0)

%% ── VALIDATION ───────────────────────────────────────────────────────────────
assert(abs(da+db+dc - 1.5) < 1e-9, 'Duty cycles must sum to 1.5');
assert(abs(ia+ib+ic)       < 1e-9, 'Phase currents must sum to 0');

%% ── IDENTIFY LEGS AND APPLY RULE ─────────────────────────────────────────────
% The lone-sign leg is the one whose current sign differs from the other two.
% By convention we assign:
%   Leg A = lone-sign leg  (already given as ia,da above)
%   Leg B = same-bank leg 1  → START aligned with A
%   Leg C = same-bank leg 2  → END   aligned with A

% If ia is the lone positive:  theta_b = 0,  theta_c = da - dc
% If ia is the lone negative:  same rule applies (signs handle themselves)

theta_a = 0.0;
theta_b = 0.0;           % Rule ①: start of B = start of A
theta_c = da - dc;       % Rule ②: end of C = end of A  (start_c + dc = da)

fprintf('============================================================\n');
fprintf('  Synchronization Rule Results\n');
fprintf('============================================================\n\n');
fprintf('  Inputs:\n');
fprintf('    da=%.4f  db=%.4f  dc=%.4f  (sum=%.4f)\n', da,db,dc, da+db+dc);
fprintf('    ia=%.4f  ib=%.4f  ic=%.4f  (sum=%.2e)\n', ia,ib,ic, ia+ib+ic);
fprintf('\n  Applied phase shifts:\n');
fprintf('    theta_a = %.4f  (%.2f deg)  [reference]\n', theta_a, theta_a*360);
fprintf('    theta_b = %.4f  (%.2f deg)  [start aligned with A]\n', theta_b, theta_b*360);
fprintf('    theta_c = %.4f  (%.2f deg)  [end   aligned with A]\n', theta_c, theta_c*360);

%% ── WAVEFORM GENERATION ──────────────────────────────────────────────────────
N   = 100000;
tau = linspace(0, 1, N+1);
tau = tau(1:end-1);

Sa_opt  = make_pulse(da, theta_a, tau);
Sb_opt  = make_pulse(db, theta_b, tau);
Sc_opt  = make_pulse(dc, theta_c, tau);

Sa_conv = make_pulse(da, 0, tau);
Sb_conv = make_pulse(db, 0, tau);
Sc_conv = make_pulse(dc, 0, tau);

idc = ia*da + ib*db + ic*dc;

icap_opt  = ia*Sa_opt  + ib*Sb_opt  + ic*Sc_opt  - idc;
icap_conv = ia*Sa_conv + ib*Sb_conv + ic*Sc_conv - idc;

rms_opt  = sqrt(mean(icap_opt.^2));
rms_conv = sqrt(mean(icap_conv.^2));

if rms_conv > 0
    reduction = 100*(rms_conv - rms_opt)/rms_conv;
else
    reduction = 0;
end

fprintf('\n  RMS Results:\n');
fprintf('    Conventional RMS = %.6f p.u.\n', rms_conv);
fprintf('    Optimal RMS      = %.6f p.u.\n', rms_opt);
fprintf('    Reduction        = %.2f%%\n',     reduction);
fprintf('============================================================\n');

%% ── PLOT ─────────────────────────────────────────────────────────────────────
bg_col    = [0.051 0.067 0.090];
panel_col = [0.086 0.106 0.133];
grid_col  = [0.129 0.149 0.173];
text_col  = [0.545 0.580 0.616];
white_col = [0.902 0.929 0.953];
col_a     = [0.969 0.506 0.400];
col_b     = [0.475 0.753 1.000];
col_c     = [0.337 0.827 0.392];
col_cap   = [1.000 0.651 0.341];
col_conv  = [0.545 0.580 0.616];

fig = figure('Color', bg_col, 'Position', [80 50 1300 900]);

% ── Panel 1: Conventional switching signals ───────────────────────────────
ax1 = subplot(4,1,1);
hold on; box on;
offset = 1.35;
stairs(tau, Sa_conv + 2*offset, 'Color',col_a, 'LineWidth',2.0);
stairs(tau, Sb_conv + 1*offset, 'Color',col_b, 'LineWidth',2.0);
stairs(tau, Sc_conv + 0*offset, 'Color',col_c, 'LineWidth',2.0);
style_panel(ax1, panel_col, grid_col, text_col, white_col, ...
    sprintf('Conventional PWM  —  all carriers aligned  (\\theta_b = \\theta_c = 0)'));
ylim([-0.2 3.3]);
yticks([0.5  0.5+offset  0.5+2*offset]);
yticklabels({'Sc','Sb','Sa'});
add_labels(ax1, ia, ib, ic, da, db, dc, col_a, col_b, col_c, white_col, offset);

% ── Panel 2: Optimal switching signals ───────────────────────────────────
ax2 = subplot(4,1,2);
hold on; box on;
stairs(tau, Sa_opt + 2*offset, 'Color',col_a, 'LineWidth',2.0);
stairs(tau, Sb_opt + 1*offset, 'Color',col_b, 'LineWidth',2.0);
stairs(tau, Sc_opt + 0*offset, 'Color',col_c, 'LineWidth',2.0);
style_panel(ax2, panel_col, grid_col, text_col, white_col, ...
    sprintf('Optimal PWM  —  \\theta_b = 0 (start aligned),  \\theta_c = da-dc = %.4f (end aligned)', theta_c));
ylim([-0.2 3.3]);
yticks([0.5  0.5+offset  0.5+2*offset]);
yticklabels({'Sc','Sb','Sa'});
add_labels(ax2, ia, ib, ic, da, db, dc, col_a, col_b, col_c, white_col, offset);

% Edge markers
xline(ax2, theta_a,      '--', 'Color',[1 1 1 0.4], 'LineWidth',1.0);
xline(ax2, theta_a + da, '--', 'Color',[1 1 1 0.4], 'LineWidth',1.0);
text(ax2, theta_a + 0.01,      3.15, '① START', 'Color',white_col, 'FontSize',8);
text(ax2, theta_a + da + 0.01, 3.15, '② END',   'Color',white_col, 'FontSize',8);

% ── Panel 3: Capacitor current comparison ────────────────────────────────
ax3 = subplot(4,1,3);
hold on; box on;
stairs(tau, icap_conv, 'Color',col_conv, 'LineWidth',1.2, ...
       'DisplayName', sprintf('Conventional   RMS = %.4f p.u.', rms_conv));
stairs(tau, icap_opt,  'Color',col_cap,  'LineWidth',2.0, ...
       'DisplayName', sprintf('Optimal        RMS = %.4f p.u.   (%.1f%% reduction)', rms_opt, reduction));
yline(0, '--', 'Color',grid_col, 'LineWidth',0.8);
style_panel(ax3, panel_col, grid_col, text_col, white_col, ...
    'DC-Link Capacitor Current  i_{cap}(t)');
ylabel(ax3, 'i_{cap} (p.u.)', 'Color',text_col, 'FontSize',9);
leg = legend('Location','northeast','FontSize',9);
set(leg, 'Color',panel_col, 'TextColor',white_col, 'EdgeColor',grid_col);

% ── Panel 4: Rule diagram (timeline bar chart) ────────────────────────────
ax4 = subplot(4,1,4);
hold on; box on;
style_panel(ax4, panel_col, grid_col, text_col, white_col, ...
    'The Simple Rule — Edge Alignment Diagram');

y_a = 0.75;  y_b = 0.50;  y_c = 0.25;
h   = 0.14;

% ON regions (filled)
fill_pulse(ax4, theta_a,       da, y_a, h, col_a, 0.85);
fill_pulse(ax4, theta_b,       db, y_b, h, col_b, 0.85);
fill_pulse(ax4, theta_c,       dc, y_c, h, col_c, 0.85);

% OFF regions (dim)
fill_pulse(ax4, theta_a+da,    1-da, y_a, h, col_a, 0.12);
fill_pulse(ax4, theta_b+db,    1-db, y_b, h, col_b, 0.12);
fill_pulse(ax4, theta_c+dc,    1-dc, y_c, h, col_c, 0.12);

% Vertical dashed lines at START and END of A
xline(ax4, theta_a,      '--', 'Color',[1 1 1 0.5], 'LineWidth',1.2);
xline(ax4, theta_a + da, '--', 'Color',[1 1 1 0.5], 'LineWidth',1.2);

% Annotations
text(ax4, theta_a - 0.01, y_a, sprintf('Sa  ia=%+.2f  da=%.2f', ia, da), ...
     'Color',col_a, 'FontSize',9, 'HorizontalAlignment','right', 'FontWeight','bold');
text(ax4, theta_b - 0.01, y_b, sprintf('Sb  ib=%+.2f  db=%.2f', ib, db), ...
     'Color',col_b, 'FontSize',9, 'HorizontalAlignment','right', 'FontWeight','bold');
text(ax4, theta_c - 0.01, y_c, sprintf('Sc  ic=%+.2f  dc=%.2f', ic, dc), ...
     'Color',col_c, 'FontSize',9, 'HorizontalAlignment','right', 'FontWeight','bold');

% Rule callouts
text(ax4, theta_a + 0.01, 0.94, ...
     sprintf('① START:  \\theta_b = 0  (Sb starts with Sa)'), ...
     'Color',white_col, 'FontSize',9);
text(ax4, theta_a + da + 0.01, 0.94, ...
     sprintf('② END:  \\theta_c = da - dc = %.3f  (Sc ends with Sa)', theta_c), ...
     'Color',white_col, 'FontSize',9);

ylim([0.1 1.05]);
xlim([0 1]);
set(ax4, 'YTick', [], 'XTick', 0:0.1:1.0);
xlabel(ax4, 'Normalized time  \tau', 'Color',text_col, 'FontSize',9);

% Main figure title
annotation(fig, 'textbox', [0 0.965 1 0.035], ...
    'String', 'Adaptive Multi-Carrier PWM — Simple Synchronization Rule', ...
    'Color',white_col, 'FontSize',13, 'FontWeight','bold', ...
    'HorizontalAlignment','center', 'EdgeColor','none', 'BackgroundColor','none');

saveas(fig, 'sync_rule_waveforms.png');
fprintf('\n  Figure saved: sync_rule_waveforms.png\n');


%% ═══════════════════════════════════════════════════════════════════════════
%%  LOCAL FUNCTIONS
%% ═══════════════════════════════════════════════════════════════════════════

function s = make_pulse(d, theta, tau)
% MAKE_PULSE  Generate 0/1 switching function for given duty and phase.
    s_start = mod(theta, 1.0);
    s_end   = mod(theta + d, 1.0);
    if s_start < s_end
        s = double(tau >= s_start & tau < s_end);
    else
        s = double(tau >= s_start | tau < s_end);
    end
end

function style_panel(ax, panel_col, grid_col, text_col, white_col, ttl)
% STYLE_PANEL  Apply dark theme styling to an axes.
    set(ax, 'Color',panel_col, 'XColor',text_col, 'YColor',text_col, ...
            'GridColor',grid_col, 'FontSize',8, 'XGrid','on', 'YGrid','on', ...
            'GridAlpha',0.3);
    title(ax, ttl, 'Color',white_col, 'FontSize',10, 'FontWeight','bold');
    xlabel(ax, 'Normalized time  \tau', 'Color',text_col, 'FontSize',9);
    xlim(ax, [-0.01 1.01]);
end

function add_labels(ax, ia, ib, ic, da, db, dc, ca, cb, cc, cw, offset)
% ADD_LABELS  Add current/duty-cycle annotations to switching signal panels.
    text(ax, 0.99, 2*offset+0.5, sprintf('ia=%+.2f  da=%.2f', ia, da), ...
         'Color',ca, 'FontSize',8, 'HorizontalAlignment','right');
    text(ax, 0.99, 1*offset+0.5, sprintf('ib=%+.2f  db=%.2f', ib, db), ...
         'Color',cb, 'FontSize',8, 'HorizontalAlignment','right');
    text(ax, 0.99, 0*offset+0.5, sprintf('ic=%+.2f  dc=%.2f', ic, dc), ...
         'Color',cc, 'FontSize',8, 'HorizontalAlignment','right');
end

function fill_pulse(ax, x_start, width, y_center, height, color, alpha_val)
% FILL_PULSE  Draw a filled rectangle representing a pulse.
    x0 = mod(x_start, 1.0);
    x1 = x0 + width;
    if x1 <= 1.0
        patch(ax, [x0 x1 x1 x0], ...
              [y_center-height/2  y_center-height/2 ...
               y_center+height/2  y_center+height/2], ...
              color, 'FaceAlpha',alpha_val, 'EdgeColor','none');
    else
        % Wrap around
        patch(ax, [x0 1  1  x0], ...
              [y_center-height/2  y_center-height/2 ...
               y_center+height/2  y_center+height/2], ...
              color, 'FaceAlpha',alpha_val, 'EdgeColor','none');
        patch(ax, [0  x1-1  x1-1  0], ...
              [y_center-height/2  y_center-height/2 ...
               y_center+height/2  y_center+height/2], ...
              color, 'FaceAlpha',alpha_val, 'EdgeColor','none');
    end
end

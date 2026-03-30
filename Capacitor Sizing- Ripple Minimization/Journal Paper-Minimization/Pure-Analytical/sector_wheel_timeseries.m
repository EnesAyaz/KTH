%% ================================================================
%  Six Current-Sign Sectors  +  Time-Domain Phase Currents
%  EJ2311 — Modulation of Power Converters, KTH
%
%  Left panel : three-phase sinusoidal currents coloured by sector,
%               with sector boundaries marked and lone phase labelled.
%  Right panel: sector wheel (sign + lone phase + θ rule).
%% ================================================================
clear; clc; close all;

%% ── Colour palette (one colour per lone phase) ──────────────────
%   Same colours used on both the waveform and the wheel
COL = struct( ...
    'A', [0.20 0.45 0.75], ...   % blue   — lone A
    'B', [0.55 0.25 0.65], ...   % purple — lone B
    'C', [0.10 0.60 0.50]);      % teal   — lone C

ALPHA_FILL = 0.18;   % shading transparency on waveform plot

%% ── Time-domain parameters ──────────────────────────────────────
N    = 4000;
t    = linspace(0, 2*pi, N);     % one fundamental period [rad]

ia   =  cos(t);
ib   =  cos(t - 2*pi/3);
ic   =  cos(t - 4*pi/3);

%% ── Per-sample sector classification ───────────────────────────
%  Signs: +1 or -1  (zero treated as +1 to avoid edge ambiguity)
sa = sign(ia + 1e-12);
sb = sign(ib + 1e-12);
sc = sign(ic + 1e-12);

% Lone phase = the one whose sign differs from the other two
lone = zeros(1, N);   % 1=A, 2=B, 3=C
for k = 1:N
    if sa(k) ~= sb(k) && sa(k) ~= sc(k)
        lone(k) = 1;   % A is lone
    elseif sb(k) ~= sa(k) && sb(k) ~= sc(k)
        lone(k) = 2;   % B is lone
    else
        lone(k) = 3;   % C is lone
    end
end

%% ── Sector boundaries (zero-crossings of any phase) ─────────────
% A new sector begins whenever any phase changes sign.
sign_change = [false, diff(sa)~=0 | diff(sb)~=0 | diff(sc)~=0];
boundary_idx = find(sign_change);

%% ── Six sector definitions (for the wheel) ──────────────────────
sectors = {
%   sign label   lone
    '(+−−)',     'A';
    '(++−)',     'C';
    '(−+−)',     'B';
    '(−++)',     'A';
    '(−−+)',     'C';
    '(+−+)',     'B';
};
Ns = size(sectors,1);

%% ================================================================
%  FIGURE LAYOUT
%% ================================================================
fig = figure('Color','white','Position',[60 60 1400 640]);

%  Left: time-domain (wider), Right: sector wheel
ax_t = subplot('Position', [0.04 0.12 0.55 0.80]);   % time-domain
ax_w = subplot('Position', [0.63 0.08 0.36 0.86]);   % wheel

%% ================================================================
%  LEFT PANEL — Time-Domain Currents
%% ================================================================
axes(ax_t); hold on; box on; grid on;

%% Shade each sector region with the lone-phase colour
%  Build contiguous segment list first
seg_start = [1, boundary_idx];
seg_end   = [boundary_idx-1, N];

for s = 1:numel(seg_start)
    i1 = seg_start(s);
    i2 = seg_end(s);
    if i1 > i2, continue; end

    lp  = lone(i1);                          % lone phase index
    key = 'A'; if lp==2, key='B'; elseif lp==3, key='C'; end
    fc  = COL.(key);

    xpatch = [t(i1:i2), fliplr(t(i1:i2))];
    ypatch = [ones(1,i2-i1+1)*1.15, ones(1,i2-i1+1)*(-1.15)];
    fill(xpatch, ypatch, fc, ...
         'FaceAlpha', ALPHA_FILL, 'EdgeColor','none');
end

%% Phase current curves
plot(t, ia, 'Color', [0.08 0.28 0.65], 'LineWidth', 2.5, ...
     'DisplayName', 'i_a');
plot(t, ib, 'Color', [0.18 0.60 0.38], 'LineWidth', 2.5, ...
     'DisplayName', 'i_b');
plot(t, ic, 'Color', [0.75 0.22 0.17], 'LineWidth', 2.5, ...
     'DisplayName', 'i_c');

%% Sector boundary vertical lines
for k = boundary_idx
    xline(t(k), '--', 'Color',[0.5 0.5 0.5], 'LineWidth', 0.9, ...
          'Alpha', 0.7);
end

%% Zero line
yline(0, 'Color',[0.6 0.6 0.6], 'LineWidth', 0.8);

%% Sector labels: sign pattern + Lone=X
% Identify unique segments by lone phase AND sign pattern
prev_pattern = '';
for s = 1:numel(seg_start)
    i1  = seg_start(s);
    i2  = seg_end(s);
    if i1 > i2, continue; end

    lp  = lone(i1);
    key = 'A'; if lp==2, key='B'; elseif lp==3, key='C'; end
    fc  = COL.(key);

    % sign pattern string
    sp = sprintf('(%s%s%s)', pm(sa(i1)), pm(sb(i1)), pm(sc(i1)));

    t_mid = (t(i1) + t(i2)) / 2;
    cur_pattern = sprintf('%s_%d', sp, lp);
    if strcmp(cur_pattern, prev_pattern), continue; end   % skip duplicates
    prev_pattern = cur_pattern;

    % sign pattern + lone phase label
    text(t_mid,  1.08, sp, ...
         'HorizontalAlignment','center','FontSize', 9.5, ...
         'FontWeight','bold','Color', fc*0.7);
    text(t_mid,  0.92, sprintf('Lone=%s', key), ...
         'HorizontalAlignment','center','FontSize', 8.5, ...
         'Color', fc*0.7);

end

%% Axes formatting
xlim([0, 2*pi]);
ylim([-1.20, 1.20]);
xticks(0 : pi/3 : 2*pi);
xticklabels({'0','π/3','2π/3','π','4π/3','5π/3','2π'});
xlabel('\omega t  (rad)', 'FontSize', 12, 'FontWeight','bold');
ylabel('Current  (p.u.)', 'FontSize', 12, 'FontWeight','bold');
title('Three-Phase Currents with Current-Sign Sectors', ...
      'FontSize', 13, 'FontWeight','bold', 'Color',[0.05 0.10 0.30]);

% Phase legend + lone-phase colour patches
hL(1) = plot(NaN, NaN, 'Color',[0.08 0.28 0.65], 'LineWidth',2.5);
hL(2) = plot(NaN, NaN, 'Color',[0.18 0.60 0.38], 'LineWidth',2.5);
hL(3) = plot(NaN, NaN, 'Color',[0.75 0.22 0.17], 'LineWidth',2.5);
hL(4) = patch(NaN,NaN, COL.A, 'FaceAlpha',0.5,'EdgeColor','none');
hL(5) = patch(NaN,NaN, COL.B, 'FaceAlpha',0.5,'EdgeColor','none');
hL(6) = patch(NaN,NaN, COL.C, 'FaceAlpha',0.5,'EdgeColor','none');
legend(hL, {'i_a','i_b','i_c','Lone=A','Lone=B','Lone=C'}, ...
       'Location','southeast','FontSize',9,'NumColumns',3,'Box','off');

ax_t.FontSize = 11;

%% ================================================================
%  RIGHT PANEL — Sector Wheel
%% ================================================================
axes(ax_w); hold on; axis equal off;
ax_w.XLim = [-1.40 1.40];
ax_w.YLim = [-1.40 1.40];

R_out   = 1.00;
R_in    = 0.38;
R_label = 0.66;

th_fine = linspace(0, 2*pi, 3601);

% Sector centres: start at 90° (12-o'clock), go CCW, 60° each
ctr_deg = 90 - 30 - (0:Ns-1)*60;
half_deg = 30;

% ── Wedges ──────────────────────────────────────────────────────
for k = 1:Ns
    lk  = sectors{k,2};
    fc  = COL.(lk) * 0.45 + 0.55;   % lighten for wheel

    a1 = deg2rad(ctr_deg(k) + half_deg);
    a2 = deg2rad(ctr_deg(k) - half_deg);
    th_arc = linspace(a1, a2, 200);

    fill([0, R_out*cos(th_arc), 0], ...
         [0, R_out*sin(th_arc), 0], ...
         fc, 'EdgeColor',[0.5 0.5 0.6], 'LineWidth',1.1);
end

% ── Circles ─────────────────────────────────────────────────────
plot(R_out*cos(th_fine), R_out*sin(th_fine), ...
     'Color',[0.40 0.40 0.55], 'LineWidth',1.5);
plot(R_in*cos(th_fine),  R_in*sin(th_fine), ...
     '--','Color',[0.55 0.55 0.65],'LineWidth',0.9);

% ── Dividing lines ───────────────────────────────────────────────
for k = 1:Ns
    ang = deg2rad(ctr_deg(k) + half_deg);
    plot([0, R_out*cos(ang)],[0, R_out*sin(ang)], ...
         'Color',[0.50 0.50 0.60],'LineWidth',1.1);
end

% ── Sector labels ────────────────────────────────────────────────
for k = 1:Ns
    ac  = deg2rad(ctr_deg(k));
    lk  = sectors{k,2};
    tc  = COL.(lk) * 0.65;          % dark version for text

    xc = R_label*cos(ac);  yc = R_label*sin(ac);

    % sign pattern
    text(xc, yc+0.09, sectors{k,1}, ...
         'HorizontalAlignment','center','FontSize',11, ...
         'FontWeight','bold','Color',tc);
    % lone phase
    text(xc, yc-0.09, sprintf('Lone=%s', lk), ...
         'HorizontalAlignment','center','FontSize',9.5, ...
         'FontWeight','bold','Color',tc);


end

% ── Centre ───────────────────────────────────────────────────────
text(0,  0.07,'Sign', 'HorizontalAlignment','center', ...
     'FontSize',12,'FontWeight','bold','Color',[0.1 0.1 0.25]);
text(0, -0.09,'Sector','HorizontalAlignment','center', ...
     'FontSize',12,'FontWeight','bold','Color',[0.1 0.1 0.25]);

% ── Title ────────────────────────────────────────────────────────
title('Sign Sectors', 'FontSize',12,'FontWeight','bold', ...
      'Color',[0.05 0.10 0.30]);

% ── Legend ───────────────────────────────────────────────────────
h(1) = patch(NaN,NaN, COL.A*0.45+0.55, 'EdgeColor','none');
h(2) = patch(NaN,NaN, COL.B*0.45+0.55, 'EdgeColor','none');
h(3) = patch(NaN,NaN, COL.C*0.45+0.55, 'EdgeColor','none');
legend(h, {'Lone=A','Lone=B','Lone=C'}, ...
       'Location','southoutside','Orientation','horizontal', ...
       'FontSize',9,'Box','off');

set(fig,'PaperPositionMode','auto');

%% ================================================================
%  HELPER FUNCTIONS
%% ================================================================
function s = pm(v)
%PM  Return '+' or '−' depending on sign of v.
    if v >= 0, s = '+'; else, s = '−'; end
end

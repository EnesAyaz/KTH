%% ================================================================
%  Six Current-Sign Sectors — Phase Shift Wheel
%  EJ2311 — Modulation of Power Converters, KTH
%
%  Six sectors arranged as a pie chart, each showing:
%    • The current sign pattern  (+−−), etc.
%    • The lone phase name       Lone = A / B / C
%    • The phase-shift rule      θb = …, θc = …
%  Colour encodes which phase is the "lone" one.
%% ================================================================
clear; clc; close all;

%% ── Sector definitions (counter-clockwise from top-right) ──────
%  Each row: {sign label, lone phase, theta_b expression, theta_c expression}
sectors = {
    '(+−−)',  'A',  '\theta_b = 0',       '\theta_c = dA−dC';
    '(++−)',  'C',  '\theta_b = dC−dB',   '\theta_c = 0';
    '(−+−)',  'B',  '\theta_b = 0',       '\theta_c = dB−dC';   % (-+-)  lone B
    '(−++)',  'A',  '\theta_b = 0',       '\theta_c = dA−dC';
    '(−−+)',  'C',  '\theta_b = dC−dB',   '\theta_c = 0';
    '(+−+)',  'B',  '\theta_b = 0',       '\theta_c = dB−dC';
};


N_sectors = size(sectors, 1);

%% ── Colours per lone phase ─────────────────────────────────────
lone_color = containers.Map( ...
    {'A',         'B',         'C'}, ...
    {[0.68 0.78 0.90],  ...   % light blue  (lone A)
     [0.85 0.83 0.92],  ...   % light purple (lone B)
     [0.78 0.88 0.85]});      % light teal  (lone C)

%% ── Geometry ───────────────────────────────────────────────────
R_outer  = 1.00;   % outer radius
R_inner  = 0.38;   % inner dashed circle
R_text   = 0.68;   % radius for sign / lone label
R_rule   = 0.90;   % radius for θ rule labels  (just inside outer edge)

% Sectors are equal (60° each), first boundary at 90° (12-o'clock)
% so sector centres are at 90 − 30, 90 − 90, 90 − 150, …
sector_angles_deg = 90 - 30 - (0:N_sectors-1)*60;  % centres [deg]
half = 30;   % half-width of each sector [deg]

%% ── Figure ─────────────────────────────────────────────────────
fig = figure('Color','white','Position',[100 80 820 820]);
ax  = axes('Parent',fig);
hold(ax,'on'); axis(ax,'equal','off');
ax.XLim = [-1.35 1.35];
ax.YLim = [-1.35 1.35];

%% ── Draw sector wedges ─────────────────────────────────────────
th_fine = linspace(0, 2*pi, 3601);

for k = 1:N_sectors
    lone   = sectors{k,2};
    fc     = lone_color(lone);

    a1 = deg2rad(sector_angles_deg(k) + half);
    a2 = deg2rad(sector_angles_deg(k) - half);
    th_arc = linspace(a1, a2, 200);

    % Wedge polygon
    xw = [0, R_outer*cos(th_arc), 0];
    yw = [0, R_outer*sin(th_arc), 0];
    fill(xw, yw, fc, 'EdgeColor', [0.55 0.55 0.65], ...
         'LineWidth', 1.2, 'Parent', ax);
end

%% ── Outer circle boundary ──────────────────────────────────────
plot(R_outer*cos(th_fine), R_outer*sin(th_fine), ...
     'Color',[0.45 0.45 0.55], 'LineWidth', 1.5, 'Parent', ax);

%% ── Inner dashed circle ────────────────────────────────────────
plot(R_inner*cos(th_fine), R_inner*sin(th_fine), ...
     '--', 'Color',[0.55 0.55 0.65], 'LineWidth', 0.9, 'Parent', ax);

%% ── Sector dividing lines ──────────────────────────────────────
for k = 1:N_sectors
    ang = deg2rad(sector_angles_deg(k) + half);  % boundary angle
    plot([0, R_outer*cos(ang)], [0, R_outer*sin(ang)], ...
         'Color',[0.55 0.55 0.65], 'LineWidth', 1.2, 'Parent', ax);
end

%% ── Sector labels ──────────────────────────────────────────────
for k = 1:N_sectors
    ang_c = deg2rad(sector_angles_deg(k));   % centre angle of sector
    lone  = sectors{k,2};

    % ---- sign label (bold, dark blue) ----------------------------
    xc = R_text * cos(ang_c);
    yc = R_text * sin(ang_c);
    text(xc, yc + 0.07, sectors{k,1}, ...
         'HorizontalAlignment','center','VerticalAlignment','middle', ...
         'FontSize', 13, 'FontWeight','bold', ...
         'Color',[0.05 0.15 0.45], 'Parent', ax);

    % ---- "Lone = X" label ----------------------------------------
    text(xc, yc - 0.09, sprintf('Lone = %s', lone), ...
         'HorizontalAlignment','center','VerticalAlignment','middle', ...
         'FontSize', 11, 'FontWeight','bold', ...
         'Color',[0.05 0.15 0.45], 'Parent', ax);

    % ---- phase-shift rule (smaller, outside the inner circle) ---
    % Place between inner circle and outer edge, offset outward
    xr = R_rule * cos(ang_c);
    yr = R_rule * sin(ang_c);
    rule_str = sprintf('%s\n%s', sectors{k,3}, sectors{k,4});
    text(xr, yr, rule_str, ...
         'HorizontalAlignment','center','VerticalAlignment','middle', ...
         'FontSize', 7.5, 'Color',[0.25 0.25 0.45], ...
         'Parent', ax);
end

%% ── Centre label ───────────────────────────────────────────────
text(0, 0.06, 'Sign', ...
     'HorizontalAlignment','center','VerticalAlignment','middle', ...
     'FontSize', 13, 'FontWeight','bold', 'Color',[0.1 0.1 0.2], ...
     'Parent', ax);
text(0, -0.10, 'Sector', ...
     'HorizontalAlignment','center','VerticalAlignment','middle', ...
     'FontSize', 13, 'FontWeight','bold', 'Color',[0.1 0.1 0.2], ...
     'Parent', ax);

%% ── Title ──────────────────────────────────────────────────────
title('Six Current-Sign Sectors — Phase Shift Rule per Sector', ...
      'FontSize', 14, 'FontWeight','bold', 'Color',[0.05 0.10 0.30]);

%% ── Legend ─────────────────────────────────────────────────────
h(1) = patch(NaN, NaN, lone_color('A'), 'EdgeColor','none');
h(2) = patch(NaN, NaN, lone_color('B'), 'EdgeColor','none');
h(3) = patch(NaN, NaN, lone_color('C'), 'EdgeColor','none');
legend(h, {'Lone = A', 'Lone = B', 'Lone = C'}, ...
       'Location','southoutside','Orientation','horizontal', ...
       'FontSize', 11, 'Box','off');

set(fig, 'PaperPositionMode','auto');

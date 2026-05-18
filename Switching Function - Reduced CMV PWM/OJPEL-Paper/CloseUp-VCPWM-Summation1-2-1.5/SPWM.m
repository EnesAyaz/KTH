%% Publication-ready conventional CB-SPWM waveform figure
% Figure contents:
% (1) Reference and carrier signals
% (2) High-side PWM signals
% (3) Normalized CMV over one fundamental period
% (4) Close-up normalized CMV within one switching period
%
% No extra text inside subfigures.
% Suitable for IEEE-style paper figures.

clear; clc; close all;

%% ================= USER SETTINGS =================
ma         = 0.80;          % modulation index
mf         = 24;            % carrier-to-fundamental frequency ratio
Vdc        = 1;             % normalized dc-link voltage
Npts       = 60000;         % samples over one fundamental period

saveFigure = true;
fileName   = 'Fig_Conventional_CBSPWM_Updated';

% Figure size
figWidth   = 7.4;           % inches
figHeight  = 5.6;           % inches

% Fonts
fontName      = 'Times New Roman';
fontSizeAxis  = 12;
fontSizeLabel = 13;
fontSizeTitle = 13;

% Line widths
lineWidthAxis = 0.90;
lineWidthMain = 1.85;
lineWidthCarr = 1.15;
lineWidthCMV  = 1.65;
lineWidthPWM  = 1.65;
%% =================================================

%% ---------- Colors ----------
colA   = [0.08 0.20 0.65];
colB   = [0.55 0.10 0.70];
colC   = [0.00 0.55 0.20];
colCar = 1.5*[0.25 0.25 0.25];   % dark gray
colCMV = [0.05 0.05 0.05];   % black

%% ---------- Fundamental-period time base ----------
theta = linspace(0,2*pi,Npts);
xdeg  = rad2deg(theta);
tauF  = theta/(2*pi);

%% ---------- References ----------
uA = ma*sin(theta);
uB = ma*sin(theta - 2*pi/3);
uC = ma*sin(theta + 2*pi/3);

%% ---------- Common carrier ----------
carrier = triwave(mf*tauF);

%% ---------- PWM signals ----------
SA = double(uA >= carrier);
SB = double(uB >= carrier);
SC = double(uC >= carrier);

%% ---------- Phase-leg voltages and CMV ----------
VA = (2*SA - 1)*(Vdc/2);
VB = (2*SB - 1)*(Vdc/2);
VC = (2*SC - 1)*(Vdc/2);

VCM = (VA + VB + VC)/3;

%% ---------- Close-up selection: one switching period ----------
theta0_deg = 180;              % starting angle for close-up
Ts_norm    = 1/mf;             % normalized switching period
tau0       = theta0_deg/360;   % normalized fundamental time

idxClose = tauF >= tau0 & tauF <= tau0 + Ts_norm;

tauClose = (tauF(idxClose) - tau0)/Ts_norm;
VCMclose = VCM(idxClose);

%% ---------- PWM signals shifted vertically for plotting ----------
SA_plot = SA + 2.4;
SB_plot = SB + 1.2;
SC_plot = SC + 0.0;

%% ---------- Figure ----------
fig = figure('Color','w', ...
    'Units','inches', ...
    'Position',[0.4 0.4 figWidth figHeight], ...
    'PaperUnits','inches', ...
    'PaperPosition',[0 0 figWidth figHeight], ...
    'PaperSize',[figWidth figHeight]);

tlo = tiledlayout(2,2, ...
    'TileSpacing','compact', ...
    'Padding','compact');

%% ============================================================
% Reference and carrier signals
% ============================================================
ax1 = nexttile(1);
hold(ax1,'on'); box(ax1,'on');
formatAxis(ax1,fontName,fontSizeAxis,lineWidthAxis);
hideToolbar(ax1);

plot(xdeg, carrier, '-', 'Color', colCar, 'LineWidth', lineWidthCarr);
plot(xdeg, uA, '-', 'Color', colA, 'LineWidth', lineWidthMain);
plot(xdeg, uB, '-', 'Color', colB, 'LineWidth', lineWidthMain);
plot(xdeg, uC, '-', 'Color', colC, 'LineWidth', lineWidthMain);

xlim([0 360]);
ylim([-1.05 1.05]);

ylabel('Normalized voltage', ...
    'Interpreter','latex', ...
    'FontSize',fontSizeLabel);

set(ax1, ...
    'XTick',[0 180 360], ...
    'XTickLabel',{'0','180','360'}, ...
    'YTick',[-1 -ma 0 ma 1], ...
    'YTickLabel',{'$-1$','$-m_a$','0','$m_a$','$1$'}, ...
    'TickLabelInterpreter','latex');

xlabel('Fundamental phase ($^\circ$)', ...
    'Interpreter','latex', ...
    'FontSize',fontSizeLabel);

%% ============================================================
% High-side PWM signals
% ============================================================
ax2 = nexttile(2);
hold(ax2,'on'); box(ax2,'on');
formatAxis(ax2,fontName,fontSizeAxis,lineWidthAxis);
hideToolbar(ax2);

stairs(xdeg, SA_plot, 'Color', colA, 'LineWidth', lineWidthPWM);
stairs(xdeg, SB_plot, 'Color', colB, 'LineWidth', lineWidthPWM);
stairs(xdeg, SC_plot, 'Color', colC, 'LineWidth', lineWidthPWM);

xlim([0 360]);
ylim([-0.25 3.65]);

ylabel('PWM signal', ...
    'Interpreter','latex', ...
    'FontSize',fontSizeLabel);

set(ax2, ...
    'XTick',[0 180 360], ...
    'XTickLabel',{'0','180','360'}, ...
    'YTick',[0.5 1.7 2.9], ...
    'YTickLabel',{'$S_C$','$S_B$','$S_A$'}, ...
    'TickLabelInterpreter','latex');

xlabel('Fundamental phase ($^\circ$)', ...
    'Interpreter','latex', ...
    'FontSize',fontSizeLabel);

%% ============================================================
% Normalized CMV over one fundamental period
% ============================================================
ax3 = nexttile(3);
hold(ax3,'on'); box(ax3,'on');
formatAxis(ax3,fontName,fontSizeAxis,lineWidthAxis);
hideToolbar(ax3);

stairs(xdeg, VCM, 'Color', colCMV, 'LineWidth', lineWidthCMV);

xlim([0 360]);
ylim([-0.58*Vdc 0.58*Vdc]);

ylabel('Normalized voltage', ...
    'Interpreter','latex', ...
    'FontSize',fontSizeLabel);

set(ax3, ...
    'XTick',[0 180 360], ...
    'XTickLabel',{'0','180','360'}, ...
    'YTick',[-Vdc/2 -Vdc/6 0 Vdc/6 Vdc/2], ...
    'YTickLabel',{'$-\frac{V_{DC}}{2}$','$-\frac{V_{DC}}{6}$','0', ...
                  '$\frac{V_{DC}}{6}$','$\frac{V_{DC}}{2}$'}, ...
    'TickLabelInterpreter','latex');

xlabel('Fundamental phase ($^\circ$)', ...
    'Interpreter','latex', ...
    'FontSize',fontSizeLabel);

%% ============================================================
% Close-up CMV within one switching period
% ============================================================
ax4 = nexttile(4);
hold(ax4,'on'); box(ax4,'on');
formatAxis(ax4,fontName,fontSizeAxis,lineWidthAxis);
hideToolbar(ax4);

stairs(tauClose, VCMclose, 'Color', colCMV, 'LineWidth', lineWidthCMV);

xlim([0 1]);
ylim([-0.58*Vdc 0.58*Vdc]);

ylabel('Normalized voltage', ...
    'Interpreter','latex', ...
    'FontSize',fontSizeLabel);

set(ax4, ...
    'XTick',[0 1], ...
    'XTickLabel',{'0','$T_s$'}, ...
    'YTick',[-Vdc/2 -Vdc/6 0 Vdc/6 Vdc/2], ...
    'YTickLabel',{'$-\frac{V_{DC}}{2}$','$-\frac{V_{DC}}{6}$','0', ...
                  '$\frac{V_{DC}}{6}$','$\frac{V_{DC}}{2}$'}, ...
    'TickLabelInterpreter','latex');

xlabel('Time', ...
    'Interpreter','latex', ...
    'FontSize',fontSizeLabel);

%% ---------- Save ----------
if saveFigure
    exportgraphics(fig,[fileName '.pdf'],'ContentType','vector');
    exportgraphics(fig,[fileName '.png'],'Resolution',600);
    exportgraphics(fig,[fileName '.tif'],'Resolution',600);
end

%% ================================================================
% LOCAL FUNCTIONS
% ================================================================

function y = triwave(x)
    % Triangular carrier in [-1,1]
    x = mod(x,1);
    y = 1 - 4*abs(x - 0.5);
end

function formatAxis(ax,fontName,fontSizeAxis,lineWidthAxis)
    ax.FontName = fontName;
    ax.FontSize = fontSizeAxis;
    ax.LineWidth = lineWidthAxis;
    ax.TickDir = 'out';
    ax.Layer = 'top';
end

function hideToolbar(ax)
    try
        disableDefaultInteractivity(ax);
    catch
    end

    try
        ax.Toolbar.Visible = 'off';
    catch
    end
end
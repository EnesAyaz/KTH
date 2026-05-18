%% Publication-ready fundamental-period PWM figure
% Combined figure to replace old Fig.4 and Fig.5
%
% Rows:
%   1) Normalized reference signals
%   2) Carrier signals
%   3) CMV
%   4) Carrier phase shifts
%
% Columns:
%   1) Conventional SPWM
%   2) +1/3 dc injection
%   3) -1/3 dc injection
%   4) Third-harmonic square-wave injection
%   5) No injection, phase-shifted
%
% Notes:
% - No text inside subfigures
% - No grid lines
% - No helper lines
% - Modulation indices are used internally, but not written in the figure

clear; clc; close all;

%% ================= USER SETTINGS =================
Vdc        = 100;          % dc-link voltage
mf         = 20;           % carrier-to-fundamental frequency ratio
Npts       = 30000;        % samples over one fundamental period

saveFigure = true;         % true / false
fileName   = 'Fig_FundamentalPeriod_ModulationComparison';

% Figure size
figWidth   = 15.8;         % inches
figHeight  = 10.4;         % inches

% Fonts
fontName      = 'Times New Roman';
fontSizeAxis  = 14;
fontSizeLabel = 15;
fontSizeTitle = 15;

% Line widths
lineWidthAxis = 0.90;
lineWidthMain = 1.90;
lineWidthCarr = 1.05;
lineWidthCMV  = 1.55;
lineWidthPhi  = 1.70;
%% =================================================

%% ---------- Case definitions ----------
caseList = {'ConvSPWM','DCplus','DCminus','Square','NoInjPS'};
nCases   = numel(caseList);

% Modulation indices used internally.
% They are intentionally not written inside the figure.
maVec = [0.8, 0.6, 0.6, 0.7, 0.9];

%% ---------- Colors ----------
% Main colors: navy blue, dark purple, dark green
colA   = [0.08 0.20 0.65];
colB   = [0.55 0.10 0.70];
colC   = [0.00 0.55 0.20];
colCMV = [0.08 0.08 0.08];

% Slightly lighter carrier colors
carA = lightenColor(colA,0.35);
carB = lightenColor(colB,0.35);
carC = lightenColor(colC,0.35);

%% ---------- Figure ----------
fig = figure('Color','w', ...
    'Units','inches', ...
    'Position',[0.3 0.3 figWidth figHeight], ...
    'PaperUnits','inches', ...
    'PaperPosition',[0 0 figWidth figHeight], ...
    'PaperSize',[figWidth figHeight]);

tlo = tiledlayout(4,nCases, ...
    'TileSpacing','compact', ...
    'Padding','compact');

%% ---------- Main loop ----------
for k = 1:nCases

    mode = caseList{k};
    ma   = maVec(k);

    data = generateFundamentalCase(mode,ma,Vdc,mf,Npts);

    %% ============================================================
    % ROW 1: Normalized reference signals
    % ============================================================
    ax1 = nexttile(k);
    hold(ax1,'on');
    box(ax1,'on');
    formatAxis(ax1,fontName,fontSizeAxis,lineWidthAxis);
    hideToolbar(ax1);

    plot(data.xdeg, data.uA, '-', 'Color', colA, 'LineWidth', lineWidthMain);
    plot(data.xdeg, data.uB, '-', 'Color', colB, 'LineWidth', lineWidthMain);
    plot(data.xdeg, data.uC, '-', 'Color', colC, 'LineWidth', lineWidthMain);

    xlim([0 360]);
    ylim([-1.05 1.05]);

    if k == 1
        ylabel('Normalized voltage', ...
            'Interpreter','latex', ...
            'FontSize',fontSizeLabel);

        set(ax1, ...
            'YTick',[-1 -1/3 0 1/3 1], ...
            'YTickLabel',{'$-1$','$-\frac{1}{3}$','0','$\frac{1}{3}$','$1$'}, ...
            'TickLabelInterpreter','latex');
    else
        set(ax1, ...
            'YTick',[-1 -1/3 0 1/3 1], ...
            'YTickLabel',[], ...
            'TickLabelInterpreter','latex');
    end

    set(ax1, ...
        'XTick',[0 180 360], ...
        'XTickLabel',{'','',''});

    title(data.caseTitle, ...
        'Interpreter','latex', ...
        'FontSize',fontSizeTitle, ...
        'FontWeight','normal');

    %% ============================================================
    % ROW 2: Carrier signals
    % ============================================================
    ax2 = nexttile(nCases + k);
    hold(ax2,'on');
    box(ax2,'on');
    formatAxis(ax2,fontName,fontSizeAxis,lineWidthAxis);
    hideToolbar(ax2);

    plot(data.xdeg, data.cA, '-', 'Color', carA, 'LineWidth', lineWidthCarr);
    plot(data.xdeg, data.cB, '-', 'Color', carB, 'LineWidth', lineWidthCarr);
    plot(data.xdeg, data.cC, '-', 'Color', carC, 'LineWidth', lineWidthCarr);

    xlim([0 360]);
    ylim([-1.05 1.05]);

    if k == 1
        ylabel('Carrier signal', ...
            'Interpreter','latex', ...
            'FontSize',fontSizeLabel);

        set(ax2, ...
            'YTick',[-1 0 1], ...
            'YTickLabel',{'$-1$','0','$1$'}, ...
            'TickLabelInterpreter','latex');
    else
        set(ax2, ...
            'YTick',[-1 0 1], ...
            'YTickLabel',[], ...
            'TickLabelInterpreter','latex');
    end

    set(ax2, ...
        'XTick',[0 180 360], ...
        'XTickLabel',{'','',''});

    %% ============================================================
    % ROW 3: Common-mode voltage
    % ============================================================
    ax3 = nexttile(2*nCases + k);
    hold(ax3,'on');
    box(ax3,'on');
    formatAxis(ax3,fontName,fontSizeAxis,lineWidthAxis);
    hideToolbar(ax3);

    stairs(data.xdeg, data.VCM, ...
        'Color', colCMV, ...
        'LineWidth', lineWidthCMV);

    xlim([0 360]);
    ylim([-0.58*Vdc 0.58*Vdc]);

    if k == 1
        ylabel('$V_{\mathrm{CM}}$', ...
            'Interpreter','latex', ...
            'FontSize',fontSizeLabel);

        set(ax3, ...
            'YTick',[-Vdc/2 -Vdc/6 0 Vdc/6 Vdc/2], ...
            'YTickLabel',{'$-\frac{V_{DC}}{2}$','$-\frac{V_{DC}}{6}$','0', ...
                          '$\frac{V_{DC}}{6}$','$\frac{V_{DC}}{2}$'}, ...
            'TickLabelInterpreter','latex');
    else
        set(ax3, ...
            'YTick',[-Vdc/2 -Vdc/6 0 Vdc/6 Vdc/2], ...
            'YTickLabel',[], ...
            'TickLabelInterpreter','latex');
    end

    set(ax3, ...
        'XTick',[0 180 360], ...
        'XTickLabel',{'','',''});

    %% ============================================================
    % ROW 4: Carrier phase shifts
    % ============================================================
    ax4 = nexttile(3*nCases + k);
    hold(ax4,'on');
    box(ax4,'on');
    formatAxis(ax4,fontName,fontSizeAxis,lineWidthAxis);
    hideToolbar(ax4);

    plot(data.xdeg, data.phiA_deg, '-', 'Color', colA, 'LineWidth', lineWidthPhi);
    plot(data.xdeg, data.phiB_deg, '-', 'Color', colB, 'LineWidth', lineWidthPhi);
    plot(data.xdeg, data.phiC_deg, '-', 'Color', colC, 'LineWidth', lineWidthPhi);

    xlim([0 360]);
    ylim([-190 190]);

    if k == 1
        ylabel('Carrier phase shift ($^\circ$)', ...
            'Interpreter','latex', ...
            'FontSize',fontSizeLabel);

        set(ax4, ...
            'YTick',[-180 0 180], ...
            'YTickLabel',{'$-180$','0','$180$'}, ...
            'TickLabelInterpreter','latex');
    else
        set(ax4, ...
            'YTick',[-180 0 180], ...
            'YTickLabel',[], ...
            'TickLabelInterpreter','latex');
    end

    set(ax4, ...
        'XTick',[0 180 360], ...
        'XTickLabel',{'0','180','360'}, ...
        'TickLabelInterpreter','latex');

    xlabel('Fundamental phase ($^\circ$)', ...
        'Interpreter','latex', ...
        'FontSize',fontSizeLabel);
end

%% ---------- Save ----------
if saveFigure
    exportgraphics(fig,[fileName '.pdf'],'ContentType','vector');
    exportgraphics(fig,[fileName '.png'],'Resolution',600);
    exportgraphics(fig,[fileName '.tif'],'Resolution',600);
end

%% ================================================================
% LOCAL FUNCTIONS
% ================================================================

function data = generateFundamentalCase(mode,ma,Vdc,mf,Npts)

    % Fundamental electrical angle
    theta = linspace(0,2*pi,Npts);
    xdeg  = rad2deg(theta);

    % Base balanced references
    uA0 = ma*sin(theta);
    uB0 = ma*sin(theta - 2*pi/3);
    uC0 = ma*sin(theta + 2*pi/3);

    switch lower(mode)

        case 'convspwm'
            % Conventional SPWM:
            % no injection and no carrier phase shift
            uinj = zeros(size(theta));

            uA = uA0;
            uB = uB0;
            uC = uC0;

            DA = (1 + uA)/2;
            DB = (1 + uB)/2;
            DC = (1 + uC)/2;

            phiA = zeros(size(theta));
            phiB = zeros(size(theta));
            phiC = zeros(size(theta));

            caseTitle = 'Conv. SPWM';

        case 'dcplus'
            % +1/3 dc injection
            uinj = (1/3)*ones(size(theta));

            uA = uA0 + uinj;
            uB = uB0 + uinj;
            uC = uC0 + uinj;

            DA = (1 + uA)/2;
            DB = (1 + uB)/2;
            DC = (1 + uC)/2;

            phiA = zeros(size(theta));
            phiB = (DA + DB)*pi;
            phiC = (DA + 2*DB + DC)*pi;

            caseTitle = '$+1/3$ dc inj.';

        case 'dcminus'
            % -1/3 dc injection
            uinj = -(1/3)*ones(size(theta));

            uA = uA0 + uinj;
            uB = uB0 + uinj;
            uC = uC0 + uinj;

            DA = (1 + uA)/2;
            DB = (1 + uB)/2;
            DC = (1 + uC)/2;

            phiA = zeros(size(theta));
            phiB = (DA + DB)*pi;
            phiC = (DA + 2*DB + DC)*pi;

            caseTitle = '$-1/3$ dc inj.';

        case 'square'
            % Correct square-wave injection for this reference definition:
            %
            % uA = ma*sin(theta)
            % uB = ma*sin(theta - 2*pi/3)
            % uC = ma*sin(theta + 2*pi/3)
            %
            % To keep the references inside the linear range:
            % uinj = +(1/3) when sin(3theta) > 0
            % uinj = -(1/3) when sin(3theta) < 0
            %
            % This is equivalent to:
            % uinj = (1/3)*sgn(sin(3theta))

            uinj = (1/3)*sign(sin(3*theta));

            % Avoid zero-valued injection at exact transition samples
            uinj(uinj == 0) = 1/3;

            uA = uA0 + uinj;
            uB = uB0 + uinj;
            uC = uC0 + uinj;

            DA = (1 + uA)/2;
            DB = (1 + uB)/2;
            DC = (1 + uC)/2;

            phiA = zeros(size(theta));
            phiB = (DA + DB)*pi;
            phiC = (DA + 2*DB + DC)*pi;

            caseTitle = 'Square-wave inj.';

        case 'noinjps'
            % No injection, only adaptive carrier phase shift
            uinj = zeros(size(theta));

            uA = uA0;
            uB = uB0;
            uC = uC0;

            DA = (1 + uA)/2;
            DB = (1 + uB)/2;
            DC = (1 + uC)/2;

            phiA = zeros(size(theta));
            phiB = (DA + DB)*pi;
            phiC = (DA + 2*DB + DC)*pi;

            caseTitle = 'No inj., phase-shifted';

        otherwise
            error('Unknown mode.');
    end

    % Warn if references exceed linear range
    if any(abs([uA uB uC]) > 1 + 1e-12)
        warning(['Reference exceeds [-1,1] in mode ', mode, ...
            '. Reduce m_a or change settings.']);
    end

    % Normalized fundamental time
    tauF = theta/(2*pi);

    % Variable-phase carriers
    cA = triwaveFundamental(tauF,mf,phiA);
    cB = triwaveFundamental(tauF,mf,phiB);
    cC = triwaveFundamental(tauF,mf,phiC);

    % Switching states
    SA = double(uA >= cA);
    SB = double(uB >= cB);
    SC = double(uC >= cC);

    % Phase-leg voltages
    VA = (2*SA - 1)*(Vdc/2);
    VB = (2*SB - 1)*(Vdc/2);
    VC = (2*SC - 1)*(Vdc/2);

    % Common-mode voltage
    VCM = (VA + VB + VC)/3;

    % Wrapped phase shifts in degrees
    phiA_deg = wrapTo180_local(phiA);
    phiB_deg = wrapTo180_local(phiB);
    phiC_deg = wrapTo180_local(phiC);

    % Pack data
    data.xdeg = xdeg;

    data.uA = uA;
    data.uB = uB;
    data.uC = uC;
    data.uinj = uinj;

    data.DA = DA;
    data.DB = DB;
    data.DC = DC;

    data.cA = cA;
    data.cB = cB;
    data.cC = cC;

    data.VA = VA;
    data.VB = VB;
    data.VC = VC;
    data.VCM = VCM;

    data.phiA = phiA;
    data.phiB = phiB;
    data.phiC = phiC;

    data.phiA_deg = phiA_deg;
    data.phiB_deg = phiB_deg;
    data.phiC_deg = phiC_deg;

    data.caseTitle = caseTitle;
end

function y = triwaveFundamental(tauF,mf,phi)
    % Triangular carrier in [-1,1]
    % tauF : normalized fundamental time [0,1]
    % mf   : carrier-to-fundamental frequency ratio
    % phi  : carrier phase shift [rad], can be vector

    x = mod(mf*tauF + phi/(2*pi),1);
    y = 1 - 4*abs(x - 0.5);
end

function deg = wrapTo180_local(phi)
    % Wrap radians to [-180,180)
    deg = rad2deg(mod(phi + pi, 2*pi) - pi);
end

function c = lightenColor(c0,alpha)
    % alpha = 0 --> original color
    % alpha = 1 --> white
    c = c0 + alpha*(1-c0);
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
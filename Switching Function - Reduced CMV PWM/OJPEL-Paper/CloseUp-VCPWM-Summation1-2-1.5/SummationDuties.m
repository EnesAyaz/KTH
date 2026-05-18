%% Publication-ready close-up PWM figure
% Clean version:
% - No text inside subfigures
% - No helper y-lines
% - No grid lines
% - Phase-voltage row shows +/-VDC/2 levels on first column
% - Increased vertical spacing to avoid y-label clashes
% - Suitable for caption-based explanation

clear; clc; close all;

%% ================= USER SETTINGS =================
plotMode   = 'all4';      % 'Baseline', 'Dsum1', 'Dsum2', 'NoInjPS', 'all4'
ma         = 0.45;        % modulation index before injection
theta_deg  = 40;          % operating point angle in degrees
Vdc        = 100;         % dc-link voltage
Npts       = 4000;        % number of points in one switching period

saveFigure = true;        % true / false
fileName   = 'Fig_CloseUp_PWM_4Cases_Clean_Final';

% Figure size
figWidth  = 12.8;         % inches
figHeight = 8.2;          % inches

% Fonts
fontName      = 'Times New Roman';
fontSizeAxis  = 15;
fontSizeLabel = 15;
fontSizeTitle = 15;

% Line widths
lineWidthAxis = 0.90;
lineWidthMain = 2.10;
lineWidthCarr = 1.25;
lineWidthCMV  = 2.10;
%% =================================================

%% ---------- Case selection ----------
switch lower(plotMode)
    case 'baseline'
        caseList = {'Baseline'};
    case 'dsum1'
        caseList = {'Dsum1'};
    case 'dsum2'
        caseList = {'Dsum2'};
    case 'noinjps'
        caseList = {'NoInjPS'};
    case 'all4'
        caseList = {'Baseline','Dsum1','Dsum2','NoInjPS'};
    otherwise
        error('Unknown plotMode. Use: Baseline, Dsum1, Dsum2, NoInjPS, or all4.');
end

nCases = numel(caseList);

%% ---------- Colors ----------
% Navy blue, dark purple, dark green
colA   = 1.5*[0.05 0.15 0.45];   % navy blue
colB   = 1.5*[0.35 0.05 0.45];   % dark purple
colC   = 1.5*[0.00 0.35 0.15];   % dark green
colCMV = [0.05 0.05 0.05];   % black

% Lighter colors for carriers
carA = lightenColor(colA,0);
carB = lightenColor(colB,0);
carC = lightenColor(colC,0);

%% ---------- Figure ----------
fig = figure('Color','w', ...
    'Units','inches', ...
    'Position',[0.4 0.4 figWidth figHeight], ...
    'PaperUnits','inches', ...
    'PaperPosition',[0 0 figWidth figHeight], ...
    'PaperSize',[figWidth figHeight]);

tlo = tiledlayout(3,nCases, ...
    'TileSpacing','compact', ...
    'Padding','compact');

%% ---------- Main loop ----------
for k = 1:nCases

    mode = caseList{k};
    data = generateCase(mode,ma,theta_deg,Vdc,Npts);

    %% ============================================================
    % ROW 1: References and carriers
    % ============================================================
    ax1 = nexttile(k);
    hold(ax1,'on');
    box(ax1,'on');
    formatAxis(ax1,fontName,fontSizeAxis,lineWidthAxis);
    hideToolbar(ax1);

    % Carriers
    plot(data.tau, data.cA, '--', 'Color', carA, 'LineWidth', lineWidthCarr);
    plot(data.tau, data.cB, '--', 'Color', carB, 'LineWidth', lineWidthCarr);
    plot(data.tau, data.cC, '--', 'Color', carC, 'LineWidth', lineWidthCarr);

    % References
    plot(data.tau, data.uA*ones(size(data.tau)), '-', ...
        'Color', colA, 'LineWidth', lineWidthMain);
    plot(data.tau, data.uB*ones(size(data.tau)), '-', ...
        'Color', colB, 'LineWidth', lineWidthMain);
    plot(data.tau, data.uC*ones(size(data.tau)), '-', ...
        'Color', colC, 'LineWidth', lineWidthMain);

    xlim([0 1]);
    ylim([-1.08 1.08]);

    if k == 1
        ylabel('Normalized voltage', ...
            'Interpreter','latex', ...
            'FontSize',fontSizeLabel);
    end

    set(ax1, ...
        'XTick',[0 1], ...
        'XTickLabel',{'',''}, ...
        'YTick',[-1 0 1], ...
        'TickLabelInterpreter','latex');

    title(data.caseTitle, ...
        'Interpreter','latex', ...
        'FontSize',fontSizeTitle, ...
        'FontWeight','normal');

    if k ~= 1
        set(ax1,'YTickLabel',[]);
    end

    %% ============================================================
    % ROW 2: Phase voltages, shifted vertically
    % ============================================================
    ax2 = nexttile(nCases + k);
    hold(ax2,'on');
    box(ax2,'on');
    formatAxis(ax2,fontName,fontSizeAxis,lineWidthAxis);
    hideToolbar(ax2);

    % Larger spacing between stacked waveforms to avoid y-label clashes
    offsetA =  1.70*Vdc;
    offsetB =  0.00*Vdc;
    offsetC = -1.70*Vdc;

    VA_plot = data.VA + offsetA;
    VB_plot = data.VB + offsetB;
    VC_plot = data.VC + offsetC;

    stairs(data.tau, VA_plot, 'Color', colA, 'LineWidth', lineWidthMain);
    stairs(data.tau, VB_plot, 'Color', colB, 'LineWidth', lineWidthMain);
    stairs(data.tau, VC_plot, 'Color', colC, 'LineWidth', lineWidthMain);

    xlim([0 1]);
    ylim([-2.30*Vdc 2.30*Vdc]);

    if k == 1
        ylabel('Phase voltage', ...
            'Interpreter','latex', ...
            'FontSize',fontSizeLabel);

        % Tick positions must be increasing
        yticks_phase = [ ...
            offsetC - Vdc/2, offsetC + Vdc/2, ...
            offsetB - Vdc/2, offsetB + Vdc/2, ...
            offsetA - Vdc/2, offsetA + Vdc/2];

        yticklabels_phase = { ...
            '$-\frac{V_{DC}}{2}$', '$\frac{V_{DC}}{2}$', ...
            '$-\frac{V_{DC}}{2}$', '$\frac{V_{DC}}{2}$', ...
            '$-\frac{V_{DC}}{2}$', '$\frac{V_{DC}}{2}$'};

        set(ax2, ...
            'XTick',[0 1], ...
            'XTickLabel',{'',''}, ...
            'YTick',yticks_phase, ...
            'YTickLabel',yticklabels_phase, ...
            'TickLabelInterpreter','latex');
    else
        set(ax2, ...
            'XTick',[0 1], ...
            'XTickLabel',{'',''}, ...
            'YTick',[], ...
            'TickLabelInterpreter','latex');
    end

    %% ============================================================
    % ROW 3: Common-mode voltage
    % ============================================================
    ax3 = nexttile(2*nCases + k);
    hold(ax3,'on');
    box(ax3,'on');
    formatAxis(ax3,fontName,fontSizeAxis,lineWidthAxis);
    hideToolbar(ax3);

    stairs(data.tau, data.VCM, ...
        'Color', colCMV, ...
        'LineWidth', lineWidthCMV);

    xlim([0 1]);
    ylim([-0.58*Vdc 0.58*Vdc]);

    if k == 1
        ylabel('$V_{\mathrm{CM}}$', ...
            'Interpreter','latex', ...
            'FontSize',fontSizeLabel);

        set(ax3, ...
            'XTick',[0 1], ...
            'XTickLabel',{'0','$T_s$'}, ...
            'YTick',[-Vdc/2 -Vdc/6 0 Vdc/6 Vdc/2], ...
            'YTickLabel',{'$-\frac{V_{DC}}{2}$','$-\frac{V_{DC}}{6}$','0', ...
                          '$\frac{V_{DC}}{6}$','$\frac{V_{DC}}{2}$'}, ...
            'TickLabelInterpreter','latex');
    else
        set(ax3, ...
            'XTick',[0 1], ...
            'XTickLabel',{'0','$T_s$'}, ...
            'YTick',[-Vdc/2 -Vdc/6 0 Vdc/6 Vdc/2], ...
            'YTickLabel',[], ...
            'TickLabelInterpreter','latex');
    end

    xlabel('Time', ...
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

function data = generateCase(mode,ma,theta_deg,Vdc,Npts)

    theta = deg2rad(theta_deg);

    % Base balanced references
    uA0 = ma*sin(theta);
    uB0 = ma*sin(theta - 2*pi/3);
    uC0 = ma*sin(theta + 2*pi/3);

    switch lower(mode)

        case 'baseline'
            % Conventional SPWM: no injection, no carrier phase shift
            uinj = 0;

            uA = uA0;
            uB = uB0;
            uC = uC0;

            DA = (1+uA)/2;
            DB = (1+uB)/2;
            DC = (1+uC)/2;

            Dsum = DA + DB + DC;

            phiA = 0;
            phiB = 0;
            phiC = 0;

            caseTitle = 'Conv. SPWM';

        case 'dsum1'
            % Injection case with Dsum = 1
            uinj = -1/3;

            uA = uA0 + uinj;
            uB = uB0 + uinj;
            uC = uC0 + uinj;

            DA = (1+uA)/2;
            DB = (1+uB)/2;
            DC = (1+uC)/2;

            Dsum = DA + DB + DC;

            phiA = 0;
            phiB = (DA + DB)*pi;
            phiC = (DA + 2*DB + DC)*pi;

            caseTitle = '$D_{\Sigma}=1$';

        case 'dsum2'
            % Injection case with Dsum = 2
            uinj = +1/3;

            uA = uA0 + uinj;
            uB = uB0 + uinj;
            uC = uC0 + uinj;

            DA = (1+uA)/2;
            DB = (1+uB)/2;
            DC = (1+uC)/2;

            Dsum = DA + DB + DC;

            phiA = 0;
            phiB = (DA + DB)*pi;
            phiC = (DA + 2*DB + DC)*pi;

            caseTitle = '$D_{\Sigma}=2$';

        case 'noinjps'
            % No injection, but with adaptive carrier phase shift
            uinj = 0;

            uA = uA0;
            uB = uB0;
            uC = uC0;

            DA = (1+uA)/2;
            DB = (1+uB)/2;
            DC = (1+uC)/2;

            Dsum = DA + DB + DC;

            phiA = 0;
            phiB = (DA + DB)*pi;
            phiC = (DA + 2*DB + DC)*pi;

            caseTitle = 'No inj., phase-shifted';

        otherwise
            error('Unknown mode.');
    end

    if any(abs([uA uB uC]) > 1+1e-12)
        warning(['Reference exceeds [-1,1] in mode ', mode, ...
                 '. Reduce ma or change theta.']);
    end

    % Normalized time
    tau = linspace(0,1,Npts);

    % Phase-shifted carriers
    cA = triwave(tau,phiA);
    cB = triwave(tau,phiB);
    cC = triwave(tau,phiC);

    % Switching states
    SA = double(uA >= cA);
    SB = double(uB >= cB);
    SC = double(uC >= cC);

    % Phase voltages
    VA = (2*SA - 1)*(Vdc/2);
    VB = (2*SB - 1)*(Vdc/2);
    VC = (2*SC - 1)*(Vdc/2);

    % Common-mode voltage
    VCM = (VA + VB + VC)/3;

    % Pack data
    data.tau = tau;

    data.uA = uA;
    data.uB = uB;
    data.uC = uC;

    data.DA = DA;
    data.DB = DB;
    data.DC = DC;
    data.Dsum = Dsum;
    data.uinj = uinj;

    data.phiA = phiA;
    data.phiB = phiB;
    data.phiC = phiC;

    data.cA = cA;
    data.cB = cB;
    data.cC = cC;

    data.VA = VA;
    data.VB = VB;
    data.VC = VC;
    data.VCM = VCM;

    data.caseTitle = caseTitle;
end

function y = triwave(tau,phi)
    % Triangular carrier in [-1,1]
    x = mod(tau + phi/(2*pi),1);
    y = 1 - 4*abs(x - 0.5);
end

function c = lightenColor(c0,alpha)
    % alpha = 0: original color, alpha = 1: white
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
%% ========================================================================
% DATASHEET-BASED SEMICONDUCTOR LOSS COMPARISON
%
% System:
%   Vdc  = 1200 V
%   Pout = 100 kW
%   fsw  = 15 kHz
%
% Architectures:
%   1) Conventional 2L SiC
%      Wolfspeed CAB320M17XM3
%
%   2) 3-cell SPB
%      VisIC V08TC065A1X11, 650-V GaN
%
%   3) 15-cell SPB
%      EPC2361, 100-V GaN
%
% Figure:
%   Left axis  -> stacked semiconductor losses
%   Right axis -> active switching-position count = 6N
%
% IMPORTANT:
% The numerical values are first-order datasheet-based screening results.
% They are not experimentally measured complete-inverter losses.
% ========================================================================

clear;
clc;
close all;

%% ========================================================================
% COMMON SYSTEM PARAMETERS
% ========================================================================

Vdc  = 1200;              % DC-link voltage [V]
Pout = 100e3;             % Output power [W]
fsw  = 15e3;              % Switching frequency [Hz]

kv = 0.90;                % Fundamental voltage utilization
PF = 0.95;                % Power factor

%% Fundamental output voltage

VLL_rms = kv * Vdc / sqrt(2);

%% Phase current

Iph_rms = Pout / (sqrt(3) * VLL_rms * PF);

Iph_pk = sqrt(2) * Iph_rms;

%% Representative switching current

Isw_av = (2/pi) * Iph_pk;

fprintf('\n');
fprintf('========================================================\n');
fprintf('COMMON OPERATING POINT\n');
fprintf('========================================================\n');
fprintf('Vdc              = %.1f V\n',Vdc);
fprintf('Pout             = %.1f kW\n',Pout/1e3);
fprintf('VLL,rms          = %.1f V\n',VLL_rms);
fprintf('Iphase,rms       = %.2f A\n',Iph_rms);
fprintf('Iphase,peak      = %.2f A\n',Iph_pk);
fprintf('Average |I|      = %.2f A\n',Isw_av);
fprintf('Switching freq.  = %.1f kHz\n',fsw/1e3);
fprintf('========================================================\n\n');

%% ========================================================================
% ARCHITECTURE DEFINITIONS
% ========================================================================

architectureNames = { ...
    '2L SiC', ...
    '3-cell SPB', ...
    '15-cell SPB' ...
    };

deviceNames = { ...
    'CAB320M17XM3', ...
    'V08TC065A1X11', ...
    'EPC2361' ...
    };

Ncell = [ ...
     2, ...
     3, ...
    15 ...
    ];
Vcell = Vdc ./ Ncell;
%% Active switching positions

Nswitch = 6 .* Ncell;

% Therefore:
%
% 2L SiC       = 6 switch positions
% 3-cell SPB   = 18 switch positions
% 15-cell SPB  = 90 switch positions

%% ========================================================================
% VOLTAGE RATINGS
% ========================================================================

Vdevice = [ ...
    1700, ...
     650, ...
     100 ...
    ];

voltageUtilization = 100 .* Vcell ./ Vdevice;

%% ========================================================================
% DATASHEET-BASED SCREENING LOSS VALUES
%
% These are the values used for the comparison figure.
%
% ------------------------------------------------------------------------
% 2L SiC -- CAB320M17XM3
%
% Approximate screening:
%   Conduction loss ~ 0.12 kW
%   Switching loss  ~ 1.08 kW
%
% Switching energy is based on the Wolfspeed 1200-V switching-energy
% characteristic at approximately 72 A.
%
% ------------------------------------------------------------------------
% 3-cell SPB -- V08TC065A1X11
%
% Approximate screening:
%   Conduction loss ~ 0.76 kW
%   Switching loss  ~ 0.11 kW
%
% VisIC switching-energy curve is specified at VDS = 400 V.
%
% ------------------------------------------------------------------------
% 15-cell SPB -- EPC2361
%
% Approximate screening:
%   Conduction loss ~ 0.29 kW
%   Switching loss  ~ 0.025 kW
%
% Switching loss is estimated from Eoss and transition characteristics.
%
% ========================================================================

Pcond_W = [ ...
    120, ...
    759, ...
    290 ...
    ];

Psw_W = [ ...
    1080, ...
     110, ...
      25 ...
    ];

%% Optional gate/auxiliary semiconductor contribution

Pgate_W = [ ...
    2.0, ...
    0.8, ...
    0.5 ...
    ];

%% Total semiconductor loss

Ptotal_W = Pcond_W + Psw_W + Pgate_W;

%% Semiconductor-only efficiency

efficiency = 100 .* Pout ./ (Pout + Ptotal_W);

%% Convert losses to kW for plotting

Pcond_kW  = Pcond_W  / 1000;
Psw_kW    = Psw_W    / 1000;
Pgate_kW  = Pgate_W  / 1000;
Ptotal_kW = Ptotal_W / 1000;

%% ========================================================================
% PRINT RESULTS
% ========================================================================

fprintf('DATASHEET-BASED SCREENING RESULTS\n');
fprintf('========================================================\n');

for k = 1:length(architectureNames)

    fprintf('%s\n',architectureNames{k});
    fprintf('  Device                  : %s\n',deviceNames{k});
    fprintf('  Cell count              : %d\n',Ncell(k));
    fprintf('  Nominal cell voltage    : %.1f V\n',Vcell(k));
    fprintf('  Device voltage rating   : %.0f V\n',Vdevice(k));
    fprintf('  Voltage utilization     : %.1f %%\n', ...
        voltageUtilization(k));
    fprintf('  Active switch positions : %d\n',Nswitch(k));
    fprintf('  Conduction loss         : %.1f W\n',Pcond_W(k));
    fprintf('  Switching loss          : %.1f W\n',Psw_W(k));
    fprintf('  Gate/other loss         : %.1f W\n',Pgate_W(k));
    fprintf('  Total semiconductor loss: %.1f W\n',Ptotal_W(k));
    fprintf('  Semiconductor efficiency: %.3f %%\n\n',efficiency(k));

end

%% ========================================================================
% FIGURE SETTINGS
% ========================================================================

figureWidth  = 20;        % cm
figureHeight = 11.5;      % cm

fontName = 'Times New Roman';

axisFontSize   = 11;
labelFontSize  = 12;
legendFontSize = 10;
valueFontSize  = 10;

%% Colors

cCond = [0.20 0.45 0.72];       % conduction
cSw   = [0.88 0.48 0.12];       % switching
cGate = [0.55 0.55 0.55];       % gate/other

cCount = [0.45 0.18 0.52];      % active switch count

%% ========================================================================
% CREATE FIGURE
% ========================================================================

fig = figure( ...
    'Color','w', ...
    'Units','centimeters', ...
    'Position',[2 2 figureWidth figureHeight]);

ax = axes(fig);

hold(ax,'on');

%% ========================================================================
% LEFT AXIS -- STACKED SEMICONDUCTOR LOSSES
% ========================================================================

yyaxis left

lossMatrix = [ ...
    Pcond_kW(:), ...
    Psw_kW(:), ...
    Pgate_kW(:) ...
    ];

b = bar( ...
    1:3, ...
    lossMatrix, ...
    'stacked', ...
    'BarWidth',0.58);

b(1).FaceColor = cCond;
b(2).FaceColor = cSw;
b(3).FaceColor = cGate;

b(1).EdgeColor = 'none';
b(2).EdgeColor = 'none';
b(3).EdgeColor = 'none';

ylabel( ...
    'Semiconductor loss (kW)', ...
    'FontName',fontName, ...
    'FontSize',labelFontSize);

ylim([0 1.55]);

yticks(0:0.25:1.50);

ax.YColor = [0.10 0.10 0.10];

%% ========================================================================
% TOTAL LOSS LABEL ABOVE EACH BAR
% ========================================================================

for k = 1:3

    text( ...
        k, ...
        Ptotal_kW(k) + 0.045, ...
        sprintf('%.2f kW',Ptotal_kW(k)), ...
        'FontName',fontName, ...
        'FontSize',valueFontSize, ...
        'FontWeight','bold', ...
        'HorizontalAlignment','center', ...
        'VerticalAlignment','bottom', ...
        'Color',[0.10 0.10 0.10]);

end

%% ========================================================================
% EFFICIENCY LABEL
% ========================================================================

for k = 1:3

    text( ...
        k, ...
        0.055, ...
        sprintf('\\eta_{semi} = %.2f%%',efficiency(k)), ...
        'FontName',fontName, ...
        'FontSize',9.5, ...
        'HorizontalAlignment','center', ...
        'VerticalAlignment','bottom', ...
        'Color',[0.10 0.10 0.10], ...
        'Interpreter','tex');

end

%% ========================================================================
% RIGHT AXIS -- ACTIVE SWITCHING POSITIONS
% ========================================================================

yyaxis right

hCount = plot( ...
    1:3, ...
    Nswitch, ...
    '-d', ...
    'Color',cCount, ...
    'LineWidth',2.0, ...
    'MarkerSize',7.5, ...
    'MarkerFaceColor',cCount, ...
    'MarkerEdgeColor',cCount);

ylabel( ...
    'Active switching positions, 6N', ...
    'FontName',fontName, ...
    'FontSize',labelFontSize);

ylim([0 105]);

yticks(0:15:105);

ax.YColor = cCount;

%% ========================================================================
% SWITCH-COUNT LABELS
% ========================================================================

for k = 1:3

    text( ...
        k, ...
        Nswitch(k) + 5, ...
        sprintf('%d',Nswitch(k)), ...
        'FontName',fontName, ...
        'FontSize',valueFontSize, ...
        'FontWeight','bold', ...
        'Color',cCount, ...
        'HorizontalAlignment','center', ...
        'VerticalAlignment','bottom');

end

%% ========================================================================
% X AXIS
% ========================================================================

xlim([0.45 3.55]);

xticks(1:3);

xticklabels({ ...
    '2L SiC', ...
    '3-cell SPB', ...
    '15-cell SPB' ...
    });

xlabel( ...
    'Converter architecture', ...
    'FontName',fontName, ...
    'FontSize',labelFontSize);

%% ========================================================================
% DEVICE NAME LABELS BELOW ARCHITECTURE NAMES
%
% These labels are positioned manually in normalized figure coordinates
% so that the device name does not clutter the main x-axis.
% ========================================================================

annotation( ...
    fig, ...
    'textbox', ...
    [0.205 0.005 0.18 0.06], ...
    'String','CAB320M17XM3', ...
    'EdgeColor','none', ...
    'HorizontalAlignment','center', ...
    'FontName',fontName, ...
    'FontSize',9);

annotation( ...
    fig, ...
    'textbox', ...
    [0.420 0.005 0.22 0.06], ...
    'String','V08TC065A1X11', ...
    'EdgeColor','none', ...
    'HorizontalAlignment','center', ...
    'FontName',fontName, ...
    'FontSize',9);

annotation( ...
    fig, ...
    'textbox', ...
    [0.670 0.005 0.18 0.06], ...
    'String','EPC2361', ...
    'EdgeColor','none', ...
    'HorizontalAlignment','center', ...
    'FontName',fontName, ...
    'FontSize',9);

%% ========================================================================
% AXIS FORMATTING
% ========================================================================

ax.FontName = fontName;
ax.FontSize = axisFontSize;

ax.LineWidth = 1.0;

ax.TickDir = 'out';
ax.TickLength = [0.012 0.012];

ax.Box = 'on';

ax.XGrid = 'off';
ax.YGrid = 'on';

ax.GridColor = [0.84 0.84 0.84];
ax.GridAlpha = 0.45;

ax.Layer = 'top';

%% ========================================================================
% LEGEND
% ========================================================================

lgd = legend( ...
    [b(1) b(2) b(3) hCount], ...
    { ...
    'Conduction loss', ...
    'Switching loss', ...
    'Gate / other loss', ...
    'Active switching positions' ...
    }, ...
    'Location','northwest');

lgd.FontName = fontName;
lgd.FontSize = legendFontSize;
lgd.Box = 'off';

%% ========================================================================
% OPTIONAL OPERATING-POINT ANNOTATION
% ========================================================================

annotationText = { ...
    'V_{dc} = 1200 V', ...
    'P_{out} = 100 kW', ...
    'f_{sw} = 15 kHz' ...
    };

annotation( ...
    fig, ...
    'textbox', ...
    [0.705 0.72 0.16 0.13], ...
    'String',annotationText, ...
    'FontName',fontName, ...
    'FontSize',9.5, ...
    'Interpreter','tex', ...
    'EdgeColor',[0.70 0.70 0.70], ...
    'BackgroundColor','w', ...
    'FitBoxToText','on');

%% ========================================================================
% MANUAL EDITING
% ========================================================================

plotedit(fig,'on');

%% ========================================================================
% EXPORT
% ========================================================================

% Editable MATLAB figure
%
% savefig(fig, ...
%     'Loss_Comparison_100kW.fig');

% Vector PDF for IEEE manuscript
%
% exportgraphics( ...
%     fig, ...
%     'Loss_Comparison_100kW.pdf', ...
%     'ContentType','vector', ...
%     'BackgroundColor','white');

% High-resolution PNG
%
% exportgraphics( ...
%     fig, ...
%     'Loss_Comparison_100kW.png', ...
%     'Resolution',600, ...
%     'BackgroundColor','white');
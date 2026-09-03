%% ========================================================================
% RADAR PLOT: 400-V vs 800-V ELECTRIC VEHICLE SYSTEM
%
% 10 comparison categories
% No external MATLAB toolbox required.
%
% Suitable for an IEEE-style figure.
%
% IMPORTANT:
% The numerical scores below are normalized/illustrative scores.
% Replace them with your chosen/source-supported values if needed.
% ========================================================================

clear;
clc;
close all;

%% ========================================================================
% CATEGORIES
% ========================================================================

categories = { ...
    'Motor Power\nDensity', ...
    'Faster\nCharging', ...
    'BMS\nSimplicity', ...
    'Lower Switching\nLosses', ...
    'Lower Conduction\nLosses', ...
    'Lighter\nCables', ...
    'Lower\nEMI', ...
    'Lower \nInsulation Stress', ...
    'Lower Semiconductor \nVoltage', ...
    'Lower Capacitor\nVolume' ...
    };

%% ========================================================================
% DATA
%
% Radar scale:
% 0 = low
% 5 = high
%
% NOTE:
% For categories such as "Lower Conduction Losses", a higher value
% represents a benefit.
%
% For "Insulation stress proxy" and "Semiconductor voltage requirement",
% a higher value represents a larger design stress/requirement.
%
% ========================================================================

%% 400-V system

data400 = [ ...
    2.6, ...   % Motor Power Density
    2.3, ...   % Faster Charging
    4.1, ...   % BMS Simplicity
    3.7, ...   % Lower Switching Losses
    2.3, ...   % Lower Conduction Losses
    2.4, ...   % Lighter Cables
    4.2, ...   % Lower EMI
    4.0, ...   % Insulation stress proxy
    2.0, ...   % Semiconductor voltage requirement
    3.0  ...   % DC-link capacitor volume
    ];

%% 800-V system

data800 = [ ...
    4.3, ...   % Motor Power Density
    4.4, ...   % Faster Charging
    2.5, ...   % BMS Simplicity
    2.2, ...   % Lower Switching Losses
    4.1, ...   % Lower Conduction Losses
    4.5, ...   % Lighter Cables
    2.8, ...   % Lower EMI
    2.0, ...   % Insulation stress proxy
    4.0, ...   % Semiconductor voltage requirement
    3.6  ...   % DC-link capacitor volume
    ];

%% ========================================================================
% CHECK DATA
% ========================================================================

N = length(categories);

if length(data400) ~= N || length(data800) ~= N
    error('Number of data values must match number of categories.');
end

%% ========================================================================
% FIGURE SETTINGS
% ========================================================================

figureWidth  = 20;       % cm
figureHeight = 15;       % cm

fontName = 'Times New Roman';

labelFontSize  = 13;
legendFontSize = 12;

lineWidth  = 2.1;
markerSize = 7;

%% ========================================================================
% COLORS
% ========================================================================

% Muted journal-style colors

color400 = [1 0 0];      % soft orange
color800 = [0 0 1];      % muted blue

gridColor  = [0.82 0.82 0.82];
outerColor = [0.45 0.45 0.45];
textColor  = [0.10 0.10 0.10];

%% ========================================================================
% RADAR SETTINGS
% ========================================================================

rMax = 5;

radialLevels = 1:rMax;

% Start from top and proceed clockwise

theta = pi/2 - (0:N-1)*(2*pi/N);

% Close polygon

thetaClosed = [theta theta(1)];

%% ========================================================================
% CREATE FIGURE
% ========================================================================

fig = figure( ...
    'Color','w', ...
    'Units','centimeters', ...
    'Position',[2 2 figureWidth figureHeight]);

ax = axes(fig);

hold(ax,'on');

axis(ax,'equal');
axis(ax,'off');

%% ========================================================================
% DRAW RADIAL POLYGON GRID
% ========================================================================

for rr = radialLevels

    xGrid = rr*cos(thetaClosed);
    yGrid = rr*sin(thetaClosed);

    if rr == rMax

        plot( ...
            ax, ...
            xGrid, ...
            yGrid, ...
            '-', ...
            'Color',outerColor, ...
            'LineWidth',1.1);

    else

        plot( ...
            ax, ...
            xGrid, ...
            yGrid, ...
            '-', ...
            'Color',gridColor, ...
            'LineWidth',0.75);

    end

end

%% ========================================================================
% DRAW SPOKES
% ========================================================================

for k = 1:N

    plot( ...
        ax, ...
        [0 rMax*cos(theta(k))], ...
        [0 rMax*sin(theta(k))], ...
        '-', ...
        'Color',gridColor, ...
        'LineWidth',0.75);

end

%% ========================================================================
% CONVERT DATA TO CARTESIAN COORDINATES
% ========================================================================

data400Closed = [data400 data400(1)];
data800Closed = [data800 data800(1)];

x400 = data400Closed .* cos(thetaClosed);
y400 = data400Closed .* sin(thetaClosed);

x800 = data800Closed .* cos(thetaClosed);
y800 = data800Closed .* sin(thetaClosed);

%% ========================================================================
% OPTIONAL LIGHT FILLS
% ========================================================================

patch( ...
    ax, ...
    x400, ...
    y400, ...
    color400, ...
    'FaceAlpha',0.04, ...
    'EdgeColor','none', ...
    'HandleVisibility','off');

patch( ...
    ax, ...
    x800, ...
    y800, ...
    color800, ...
    'FaceAlpha',0.06, ...
    'EdgeColor','none', ...
    'HandleVisibility','off');

%% ========================================================================
% PLOT 400-V SYSTEM
% ========================================================================

h400 = plot( ...
    ax, ...
    x400, ...
    y400, ...
    '--', ...
    'Color',color400, ...
    'LineWidth',lineWidth, ...
    'Marker','s', ...
    'MarkerSize',markerSize, ...
    'MarkerFaceColor',color400, ...
    'MarkerEdgeColor',color400);

%% ========================================================================
% PLOT 800-V SYSTEM
% ========================================================================

h800 = plot( ...
    ax, ...
    x800, ...
    y800, ...
    '-', ...
    'Color',color800, ...
    'LineWidth',lineWidth, ...
    'Marker','o', ...
    'MarkerSize',markerSize, ...
    'MarkerFaceColor','w', ...
    'MarkerEdgeColor',color800);

%% ========================================================================
% CATEGORY LABELS
%
% All labels are centered.
% sprintf() converts \n into line breaks.
% ========================================================================

labelRadius = 5.75;

for k = 1:N

    xText = labelRadius*cos(theta(k));
    yText = labelRadius*sin(theta(k));

    labelString = sprintf(categories{k});

    text( ...
        ax, ...
        xText, ...
        yText, ...
        labelString, ...
        'FontName',fontName, ...
        'FontSize',labelFontSize, ...
        'Color',textColor, ...
        'HorizontalAlignment','center', ...
        'VerticalAlignment','middle', ...
        'Interpreter','tex');

end

%% ========================================================================
% LEGEND
% ========================================================================

lgd = legend( ...
    ax, ...
    [h400 h800], ...
    { ...
    'Low Voltage System', ...
    'High Voltage System' ...
    }, ...
    'Location','northeast', ...
    'Box','off');

lgd.FontName = fontName;
lgd.FontSize = legendFontSize;

%% ========================================================================
% AXIS LIMITS
%
% Extra space is included for multi-line labels.
% ========================================================================

xlim(ax,[-6.9 6.9]);
ylim(ax,[-6.7 6.7]);

%% ========================================================================
% ENABLE MANUAL EDITING
% ========================================================================

plotedit(fig,'on');

%% ========================================================================
% EXPORT
% ========================================================================

% Save editable MATLAB figure:
%
% savefig(fig,'400V_800V_Radar_10Categories.fig');

% Vector PDF for IEEE:
%
% exportgraphics( ...
%     fig, ...
%     '400V_800V_Radar_10Categories.pdf', ...
%     'ContentType','vector', ...
%     'BackgroundColor','white');

% High-resolution PNG:
%
% exportgraphics( ...
%     fig, ...
%     '400V_800V_Radar_10Categories.png', ...
%     'Resolution',600, ...
%     'BackgroundColor','white');
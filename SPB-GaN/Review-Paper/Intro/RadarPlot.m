%% ========================================================================
% PROFESSIONAL RADAR / SPIDER PLOT
% Comparison of 800-V baseline and 1.2-kV traction architecture
%
% Updated version:
%   - No numeric radial labels
%   - All category labels center-aligned
%   - Larger fonts
%   - Cleaner IEEE-style appearance
% ========================================================================

clear;
clc;
close all;

%% ========================================================================
% DATA
% ========================================================================

categories = { ...
    'Cable mass\n(current-density limited)', ...
    'Cable I^2R loss\n(same conductor)', ...
    'Charging current\n(same power)', ...
    'Insulation stress\nproxy', ...
    'Semiconductor voltage\nrequirement', ...
    'Charging power\n(same current limit)', ...
    'DC-link capacitor\nvolume' ...
    };

% 800-V baseline
data800 = [ ...
    1.00, ...
    1.00, ...
    1.00, ...
    1.00, ...
    1.00, ...
    1.00, ...
    1.00 ...
    ];

% 1.2-kV case
data1200 = [ ...
    0.667, ...
    0.444, ...
    0.667, ...
    1.500, ...
    1.500, ...
    1.500, ...
    0.800 ...
    ];

%% ========================================================================
% FIGURE SETTINGS
% ========================================================================

figureWidth  = 20;   % cm
figureHeight = 14;   % cm

fontName = 'Times New Roman';

labelFontSize  = 13;
legendFontSize = 12;

lineWidth  = 2.0;
markerSize = 7;

%% ========================================================================
% COLORS
% ========================================================================

color800  = [0.0000 0.4470 0.7410];
color1200 = [0.8500 0.3250 0.0980];

gridColor      = [0.82 0.82 0.82];
unityRingColor = [0.45 0.45 0.45];
spokeColor     = [0.84 0.84 0.84];
outerColor     = [0.25 0.25 0.25];
textColor      = [0.10 0.10 0.10];

%% ========================================================================
% RADIAL SETTINGS
% ========================================================================

rMax = 1.65;
radialLevels = [0.5 1.0 1.5];

%% ========================================================================
% GEOMETRY
% ========================================================================

N = length(categories);

% Start at top and go clockwise
theta = pi/2 - (0:N-1)*(2*pi/N);
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
% DRAW RADIAL GRID
% ========================================================================

for rr = radialLevels

    xGrid = rr*cos(thetaClosed);
    yGrid = rr*sin(thetaClosed);

    if abs(rr-1.0) < 1e-12
        plot(ax,xGrid,yGrid, ...
            '-', ...
            'Color',unityRingColor, ...
            'LineWidth',1.0);
    else
        plot(ax,xGrid,yGrid, ...
            '-', ...
            'Color',gridColor, ...
            'LineWidth',0.7);
    end
end

%% ========================================================================
% OUTER BOUNDARY
% ========================================================================

xOuter = rMax*cos(thetaClosed);
yOuter = rMax*sin(thetaClosed);

plot(ax,xOuter,yOuter, ...
    '-', ...
    'Color',outerColor, ...
    'LineWidth',1.1);

%% ========================================================================
% SPOKES
% ========================================================================

for k = 1:N
    plot(ax,[0 rMax*cos(theta(k))], ...
            [0 rMax*sin(theta(k))], ...
            '-', ...
            'Color',spokeColor, ...
            'LineWidth',0.7);
end

%% ========================================================================
% DATA COORDINATES
% ========================================================================

data800Closed  = [data800 data800(1)];
data1200Closed = [data1200 data1200(1)];

x800 = data800Closed .* cos(thetaClosed);
y800 = data800Closed .* sin(thetaClosed);

x1200 = data1200Closed .* cos(thetaClosed);
y1200 = data1200Closed .* sin(thetaClosed);

%% ========================================================================
% LIGHT FILLS
% ========================================================================

patch(ax,x800,y800,color800, ...
    'FaceAlpha',0.025, ...
    'EdgeColor','none', ...
    'HandleVisibility','off');

patch(ax,x1200,y1200,color1200, ...
    'FaceAlpha',0.040, ...
    'EdgeColor','none', ...
    'HandleVisibility','off');

%% ========================================================================
% PLOT CURVES
% ========================================================================

h800 = plot(ax,x800,y800, ...
    '-', ...
    'Color',color800, ...
    'LineWidth',lineWidth, ...
    'Marker','o', ...
    'MarkerSize',markerSize, ...
    'MarkerFaceColor','w', ...
    'MarkerEdgeColor',color800);

h1200 = plot(ax,x1200,y1200, ...
    '--', ...
    'Color',color1200, ...
    'LineWidth',lineWidth, ...
    'Marker','s', ...
    'MarkerSize',markerSize, ...
    'MarkerFaceColor',color1200, ...
    'MarkerEdgeColor',color1200);

%% ========================================================================
% CATEGORY LABELS
% All labels centered
% ========================================================================

labelRadius = 1.80;

for k = 1:N

    xText = labelRadius*cos(theta(k));
    yText = labelRadius*sin(theta(k));

    labelString = sprintf(categories{k});

    text(ax,xText,yText,labelString, ...
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

lgd = legend(ax,[h800 h1200], ...
    {'800 V baseline','1.2 kV case'}, ...
    'Location','northeast', ...
    'Box','off');

lgd.FontName = fontName;
lgd.FontSize = legendFontSize;

%% ========================================================================
% LIMITS
% ========================================================================

xlim(ax,[-2.05 2.05]);
ylim(ax,[-1.95 1.95]);

%% ========================================================================
% OPTIONAL MANUAL EDITING
% ========================================================================

plotedit(fig,'on');

%% ========================================================================
% EXPORT
% ========================================================================

% Save editable figure:
% savefig(fig,'HV_Traction_Motivation_Radar.fig');

% Export vector PDF:
% exportgraphics(fig,'HV_Traction_Motivation_Radar.pdf', ...
%     'ContentType','vector','BackgroundColor','white');

% Export PNG:
% exportgraphics(fig,'HV_Traction_Motivation_Radar.png', ...
%     'Resolution',600,'BackgroundColor','white');
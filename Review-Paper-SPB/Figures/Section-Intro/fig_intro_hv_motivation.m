% fig_intro_hv_motivation.m
%
% Conceptual radar/spider chart: qualitative system-level tradeoffs
% between a low-voltage and a high-voltage traction architecture.
% Reproduces Fig. 1 of the SPB review paper (previously drawn inline
% in TikZ in Sections/Section_I_Intro.tex).
%
% Values are illustrative/qualitative, not measured or simulated data.
%
% Run this script to regenerate fig_intro_hv_motivation.pdf in this
% same folder; the PDF is what main.tex embeds via \includegraphics.

clear; close all; clc;

% ---------------------------------------------------------------------
% Data (fraction of full axis radius, one value per axis, 0..1)
% ---------------------------------------------------------------------
categories = { ...
    sprintf('Motor Power\nDensity'), ...
    sprintf('Faster\nCharging'), ...
    sprintf('BMS\nSimplicity'), ...
    sprintf('Lower\nSwitching\nLosses'), ...
    sprintf('Lower\nConduction\nLosses'), ...
    sprintf('Lighter\nCables'), ...
    sprintf('Lower\nEMI'), ...
    sprintf('Lower\nInsulation\nStress'), ...
    sprintf('Lower\nSemiconductor\nVoltage'), ...
    sprintf('Lower\nCapacitor\nVolume')};

highV = [0.90 0.85 0.35 0.45 0.60 0.95 0.45 0.25 0.20 0.80];  % High Voltage System
lowV  = [0.45 0.40 0.85 0.80 0.35 0.30 0.75 0.80 0.65 0.35];  % Low Voltage System

nAx = numel(categories);
R = 1;                                  % outer axis radius
ringFrac = [0.2 0.4 0.6 0.8 1.0];       % grid ring radii (fraction of R)
labelR = 1.32*R;                        % label placement radius

% Axis i (1-indexed) sits at angle 90 - (i-1)*36 degrees, matching the
% original TikZ layout (i=0..9 there).
ang = deg2rad(90 - (0:nAx-1)*36);

% ---------------------------------------------------------------------
% Working-size scale factor
% ---------------------------------------------------------------------
% The figure is designed at a 9x9 cm "print" size with 8-8.5 pt text
% (that is how it looks once \includegraphics scales it down to the
% paper's single-column width). Editing anything by hand at 9 cm is
% painful, so figScale blows the whole design up uniformly -- figure
% window, fonts, markers, and line widths all scale together, so what
% you export still looks identical after LaTeX scales it back down.
% Just raise figScale for a bigger on-screen canvas; nothing else in
% this file needs to change.
figScale = 4;
baseFigCm = 9;
figSizeCm = baseFigCm*figScale;

fontAxis   = 8*figScale;     % axis-label font size (pt)
fontLegend = 8.5*figScale;   % legend text font size (pt)
markerSz   = 4.2*figScale;   % data-point marker size
lwData     = 1.4*figScale;   % data polygon line width
lwMarker   = 1.0*figScale;   % data marker edge line width
lwLegend   = 1.2*figScale;   % legend line/marker width
lwRingOut  = 1.2*figScale;   % outer grid ring line width
lwRingIn   = 0.5*figScale;   % inner grid ring line width
lwSpoke    = 0.4*figScale;   % radial spoke line width

% ---------------------------------------------------------------------
% Figure setup
% ---------------------------------------------------------------------
fig = figure('Color','w','Units','centimeters', ...
    'Position',[2 2 figSizeCm figSizeCm]);
% Classic MATLAB fix for "File > Save As > PDF" (or File > Print)
% cropping/rescaling the figure: without this, MATLAB prints onto a
% fixed-size page (Letter/A4 by default) using PaperPosition, which
% usually does not match what is on screen. With PaperPositionMode set
% to 'auto', printing/saving always captures exactly what the figure
% window currently shows, uncropped -- including anything you have
% dragged by hand in the plot editor.
set(fig,'PaperPositionMode','auto');
ax = axes(fig); hold(ax,'on'); axis(ax,'equal'); axis(ax,'off');

colBlue = [0.10 0.20 0.55];   % High Voltage System
colRed  = [0.65 0.06 0.06];   % Low Voltage System

% Grid rings (regular decagons); the outer ring (rf==1) drawn bolder
for rf = ringFrac
    xr = rf*R*cos(ang);
    yr = rf*R*sin(ang);
    if rf == 1
        ringColor = [0.35 0.35 0.35]; ringWidth = lwRingOut;
    else
        ringColor = [0.60 0.60 0.60]; ringWidth = lwRingIn;
    end
    plot(ax,[xr xr(1)],[yr yr(1)],'Color',ringColor,'LineWidth',ringWidth);
end

% Radial spokes
for k = 1:nAx
    plot(ax,[0 R*cos(ang(k))],[0 R*sin(ang(k))], ...
        'Color',[0.6 0.6 0.6],'LineWidth',lwSpoke);
end

% ---------------------------------------------------------------------
% Data polygons
% ---------------------------------------------------------------------
xH = highV.*R.*cos(ang);  yH = highV.*R.*sin(ang);
xL = lowV.*R.*cos(ang);   yL = lowV.*R.*sin(ang);

pH = fill(ax,[xH xH(1)],[yH yH(1)],colBlue,'FaceAlpha',0.22, ...
    'EdgeColor',colBlue,'LineWidth',lwData,'LineStyle','-');
plot(ax,[xH xH(1)],[yH yH(1)],'o','MarkerSize',markerSz, ...
    'MarkerEdgeColor',colBlue,'MarkerFaceColor','w','LineWidth',lwMarker);

pL = fill(ax,[xL xL(1)],[yL yL(1)],colRed,'FaceAlpha',0.20, ...
    'EdgeColor',colRed,'LineWidth',lwData,'LineStyle','--');
plot(ax,[xL xL(1)],[yL yL(1)],'s','MarkerSize',markerSz, ...
    'MarkerEdgeColor',colRed,'MarkerFaceColor',colRed,'LineWidth',lwMarker);

% ---------------------------------------------------------------------
% Axis labels, with per-axis anchor so text clears the grid and
% mirrored label pairs line up (matches the final TikZ layout)
% ---------------------------------------------------------------------
haList = {'center','center','center','center','center','center','center','center','center','center'};
vaList = {'bottom','bottom','middle','middle','top','top','top','middle','middle','bottom'};

% Label positions: hand-tuned (via the MATLAB plot editor, then pulled
% back in through File > Generate Code) to pull the label ring in
% tighter around the chart and minimize the figure's overall profile.
% Replaces the uniform labelR*cos/sin placement used earlier.
labelX = [ 0.00400273390504957,  0.927980421417954, 1.40349575599644, ...
           1.29942467446515,     0.819906605981612, -0.00800546781009892, ...
          -0.751860129595767,   -1.30743014227525,  -1.56760784610348, ...
          -0.927980421417954];
labelY = [ 1.05982229617177,  0.851754801702247, 0.311836818853739, ...
          -0.41190516647998, -0.823735664366898, -1.02780042493137, ...
          -0.835743866082047,-0.435921569910278,  0.339855956189086, ...
           0.735675518455805];

hText = gobjects(1,nAx);
for k = 1:nAx
    hText(k) = text(ax, labelX(k), labelY(k), categories{k}, ...
        'HorizontalAlignment',haList{k}, 'VerticalAlignment',vaList{k}, ...
        'FontSize',fontAxis, 'FontName','Times New Roman');
end

% ---------------------------------------------------------------------
% Legend (custom, upper right, line+marker style to match the figure)
% ---------------------------------------------------------------------
lx0 = 2*R; ly0 = 0.95*R; dy = 0.18*R; lw = 0.28*R;
plot(ax,[lx0 lx0+lw],[ly0 ly0],'--s','Color',colRed, ...
    'MarkerFaceColor',colRed,'MarkerEdgeColor',colRed,'MarkerSize',markerSz,'LineWidth',lwLegend);
hLeg1 = text(ax, lx0+lw+0.06*R, ly0, 'LV', ...
    'FontSize',fontLegend,'FontName','Times New Roman','VerticalAlignment','middle');
plot(ax,[lx0 lx0+lw],[ly0-dy ly0-dy],'-o','Color',colBlue, ...
    'MarkerFaceColor','w','MarkerEdgeColor',colBlue,'MarkerSize',markerSz,'LineWidth',lwLegend);
hLeg2 = text(ax, lx0+lw+0.06*R, ly0-dy, 'HV', ...
    'FontSize',fontLegend,'FontName','Times New Roman','VerticalAlignment','middle');

% ---------------------------------------------------------------------
% Tight bounding box + export
% ---------------------------------------------------------------------
% This recomputes xlim/ylim from whatever is CURRENTLY on the canvas
% (all label/legend text extents) and re-exports a tightly cropped PDF.
% It is a local function (not just inline code) so you can re-run it
% from the Command Window after manually dragging labels around in the
% plot -- e.g. after nudging something by hand, just type:
%
%   retightenAndExport(fig, ax, R, hText, hLeg1, hLeg2)
%
% without re-running this whole script (which would reset your edits
% and regenerate the data from scratch). It always saves to the same
% fig_intro_hv_motivation.pdf next to this script.
retightenAndExport(fig, ax, R, hText, hLeg1, hLeg2);


function retightenAndExport(fig, ax, R, hText, hLeg1, hLeg2)
allText = [hText, hLeg1, hLeg2];
xMin = -R; xMax = R; yMin = -R; yMax = R;
for h = allText
    e = h.Extent;   % [x y width height] in data units, live/current
    xMin = min(xMin, e(1));
    xMax = max(xMax, e(1)+e(3));
    yMin = min(yMin, e(2));
    yMax = max(yMax, e(2)+e(4));
end
pad = 0.04*R;
xlim(ax,[xMin-pad, xMax+pad]);
ylim(ax,[yMin-pad, yMax+pad]);

outFile = fullfile(fileparts(mfilename('fullpath')), ...
    'fig_intro_hv_motivation.pdf');
exportgraphics(fig, outFile, 'ContentType', 'vector', ...
    'BackgroundColor','white');
fprintf('Saved %s\n', outFile);
end

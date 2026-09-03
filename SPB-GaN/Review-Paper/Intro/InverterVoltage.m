%% ========================================================================
%  TRACTION VOLTAGE-POWER MAP
%
%  Data read directly from CSV / Excel
%
%  Panel (a): Published studies / demonstrators
%  Panel (b): Industrial / reference platforms
%  Panel (c): Production battery-electric vehicles
%
%  Required database columns:
%       Label
%       Year
%       Voltage_V
%       Power_kW
%       Category
%
%  Optional database column:
%       DisplayLabel
%
%  All labels are EDITABLE text-arrow annotations.
%
% ========================================================================

clear;
clc;
close all;

%% ========================================================================
% SELECT DATABASE FILE
% ========================================================================

[fileOnly,folderPath] = uigetfile( ...
    { ...
    '*.csv;*.xlsx;*.xls', 'CSV / Excel files'; ...
    '*.csv',              'CSV files (*.csv)'; ...
    '*.xlsx;*.xls',       'Excel files (*.xlsx, *.xls)' ...
    }, ...
    'Select Traction Power-Voltage Database');

if isequal(fileOnly,0)
    error('No database file was selected.');
end

fileName = fullfile(folderPath,fileOnly);

fprintf('\nSelected file:\n%s\n\n',fileName);

%% ========================================================================
% FIGURE SETTINGS
% ========================================================================

figW = 50;                  % cm
figH = 16;                  % cm

fontName = 'Times New Roman';

fontSize  = 12;             % axes and ticks
labelFont = 11.5;           % arrow labels
titleFont = 13;

markerSize = 82;

axisLineWidth  = 1.0;
gridLineWidth  = 0.8;
arrowLineWidth = 1.1;

%% Colors

cResearch = [0.000 0.447 0.741];    % blue
cIndustry = [0.850 0.325 0.098];    % orange
cVehicle  = [0.000 0.600 0.300];    % green

cGrid = [0.84 0.84 0.84];

%% Axis limits

xMin = 250;
xMax = 1300;

yMin = 0;
yMax = 900;

%% ========================================================================
% IMPORT DATABASE
% ========================================================================

[~,~,fileExtension] = fileparts(fileName);

switch lower(fileExtension)

    case '.csv'

        % ---------------------------------------------------------------
        % Automatically determine whether CSV uses ; or ,
        % Your current database uses semicolon.
        % ---------------------------------------------------------------

        fid = fopen(fileName,'r');

        if fid == -1
            error('Could not open selected CSV file.');
        end

        firstLine = fgetl(fid);
        fclose(fid);

        numberSemicolon = sum(firstLine == ';');
        numberComma     = sum(firstLine == ',');

        if numberSemicolon >= numberComma
            delimiter = ';';
        else
            delimiter = ',';
        end

        try

            T = readtable( ...
                fileName, ...
                'Delimiter',delimiter, ...
                'VariableNamingRule','preserve');

        catch

            % Compatibility with older MATLAB versions
            T = readtable( ...
                fileName, ...
                'Delimiter',delimiter);

        end

    case {'.xlsx','.xls'}

        try

            T = readtable( ...
                fileName, ...
                'VariableNamingRule','preserve');

        catch

            T = readtable(fileName);

        end

    otherwise

        error('Unsupported file type: %s',fileExtension);

end

%% ========================================================================
% CHECK REQUIRED COLUMNS
% ========================================================================

requiredColumns = { ...
    'Label', ...
    'Year', ...
    'Voltage_V', ...
    'Power_kW', ...
    'Category'};

for k = 1:length(requiredColumns)

    if ~ismember(requiredColumns{k},T.Properties.VariableNames)

        fprintf('\nColumns found:\n\n');
        disp(T.Properties.VariableNames');

        error( ...
            'Required column "%s" was not found.', ...
            requiredColumns{k});

    end

end

%% ========================================================================
% STANDARDIZE DATA TYPES
% ========================================================================

T.Label    = string(T.Label);
T.Category = string(T.Category);

if ~isnumeric(T.Year)
    T.Year = str2double(string(T.Year));
end

if ~isnumeric(T.Voltage_V)
    T.Voltage_V = str2double(string(T.Voltage_V));
end

if ~isnumeric(T.Power_kW)
    T.Power_kW = str2double(string(T.Power_kW));
end

%% Remove invalid rows

validRows = ...
    ~ismissing(T.Label) & ...
    ~ismissing(T.Category) & ...
    ~isnan(T.Year) & ...
    ~isnan(T.Voltage_V) & ...
    ~isnan(T.Power_kW);

T = T(validRows,:);

%% ========================================================================
% DISPLAY LABELS
%
% If "DisplayLabel" exists in the database, it is used.
% Otherwise MATLAB creates compact labels automatically.
% ========================================================================

T.PlotLabel = strings(height(T),1);

hasDisplayLabel = ...
    ismember('DisplayLabel',T.Properties.VariableNames);

for k = 1:height(T)

    useExcelLabel = false;

    if hasDisplayLabel

        candidate = string(T.DisplayLabel(k));

        if ~ismissing(candidate) && strlength(strtrim(candidate)) > 0
            T.PlotLabel(k) = candidate;
            useExcelLabel = true;
        end

    end

    if ~useExcelLabel

        T.PlotLabel(k) = createShortLabel( ...
            T.Label(k), ...
            T.Year(k));

    end

end

%% ========================================================================
% SPLIT DATA INTO THREE PANELS
% ========================================================================

category = lower(strtrim(T.Category));

idxResearch = ...
    category == "research" | ...
    contains(category,"published");

idxIndustry = ...
    contains(category,"industrial") | ...
    contains(category,"reference");

idxVehicle = ...
    contains(category,"production") | ...
    contains(category,"vehicle");

% Production vehicle should never appear in industry panel
idxIndustry = idxIndustry & ~idxVehicle;

% Any unknown category goes into research
idxUnknown = ...
    ~idxResearch & ...
    ~idxIndustry & ...
    ~idxVehicle;

idxResearch = idxResearch | idxUnknown;

R = T(idxResearch,:);
I = T(idxIndustry,:);
V = T(idxVehicle,:);

%% ========================================================================
% PRINT DATABASE SUMMARY
% ========================================================================

fprintf('====================================================\n');
fprintf('DATABASE SUMMARY\n');
fprintf('====================================================\n');

fprintf('Published / research:       %d\n',height(R));
fprintf('Industrial / reference:     %d\n',height(I));
fprintf('Production vehicles:        %d\n',height(V));
fprintf('Total:                      %d\n',height(T));

fprintf('====================================================\n\n');

%% ========================================================================
% SMALL HORIZONTAL JITTER
%
% Actual database voltage is NOT modified.
% Only graphical x-position is changed.
% ========================================================================

R.Xplot = applyJitter(R.Voltage_V,22);
I.Xplot = applyJitter(I.Voltage_V,24);
V.Xplot = applyJitter(V.Voltage_V,18);

%% ========================================================================
% HAND-TUNED INITIAL LABEL LOCATIONS
%
% These reproduce approximately the layout you manually created.
% They remain fully editable afterward.
% ========================================================================

[R.LabelX,R.LabelY] = getManualInitialPositions( ...
    R,1,xMin,xMax,yMin,yMax);

[I.LabelX,I.LabelY] = getManualInitialPositions( ...
    I,2,xMin,xMax,yMin,yMax);

[V.LabelX,V.LabelY] = getManualInitialPositions( ...
    V,3,xMin,xMax,yMin,yMax);

%% ========================================================================
% CREATE FIGURE
% ========================================================================

fig = figure( ...
    'Units','centimeters', ...
    'Position',[1 1 figW figH], ...
    'Color','w');

set(fig,'Renderer','painters');

tl = tiledlayout( ...
    fig, ...
    1,3, ...
    'TileSpacing','compact', ...
    'Padding','compact');

%% ========================================================================
% PANEL (a): PUBLISHED STUDIES
% ========================================================================

ax1 = nexttile(tl,1);

hold(ax1,'on');
box(ax1,'on');

addVoltageLines( ...
    ax1, ...
    [400 800 1000 1200], ...
    gridLineWidth);

scatter( ...
    ax1, ...
    R.Xplot, ...
    R.Power_kW, ...
    markerSize, ...
    'o', ...
    'MarkerFaceColor',cResearch, ...
    'MarkerEdgeColor',cResearch, ...
    'LineWidth',1.1);

xlim(ax1,[xMin xMax]);
ylim(ax1,[yMin yMax]);

xticks(ax1,[400 800 1000 1200]);
yticks(ax1,0:100:900);

xlabel( ...
    ax1, ...
    'DC-link voltage class (V)', ...
    'FontName',fontName, ...
    'FontSize',fontSize);

ylabel( ...
    ax1, ...
    'Reported power (kW)', ...
    'FontName',fontName, ...
    'FontSize',fontSize);

title( ...
    ax1, ...
    'Published studies / demonstrators', ...
    'FontName',fontName, ...
    'FontSize',titleFont, ...
    'FontWeight','normal');

text( ...
    ax1, ...
    0.02,0.95,'(a)', ...
    'Units','normalized', ...
    'FontName',fontName, ...
    'FontSize',13, ...
    'FontWeight','bold', ...
    'VerticalAlignment','top');

%% ========================================================================
% PANEL (b): INDUSTRIAL / REFERENCE
% ========================================================================

ax2 = nexttile(tl,2);

hold(ax2,'on');
box(ax2,'on');

addVoltageLines( ...
    ax2, ...
    [400 800 1000 1200], ...
    gridLineWidth);

scatter( ...
    ax2, ...
    I.Xplot, ...
    I.Power_kW, ...
    markerSize, ...
    '^', ...
    'MarkerFaceColor',cIndustry, ...
    'MarkerEdgeColor',cIndustry, ...
    'LineWidth',1.1);

xlim(ax2,[xMin xMax]);
ylim(ax2,[yMin yMax]);

xticks(ax2,[400 800 1000 1200]);
yticks(ax2,0:100:900);

xlabel( ...
    ax2, ...
    'DC-link voltage class (V)', ...
    'FontName',fontName, ...
    'FontSize',fontSize);

title( ...
    ax2, ...
    'Industrial / reference platforms', ...
    'FontName',fontName, ...
    'FontSize',titleFont, ...
    'FontWeight','normal');

text( ...
    ax2, ...
    0.02,0.95,'(b)', ...
    'Units','normalized', ...
    'FontName',fontName, ...
    'FontSize',13, ...
    'FontWeight','bold', ...
    'VerticalAlignment','top');

%% ========================================================================
% PANEL (c): PRODUCTION VEHICLES
% ========================================================================

ax3 = nexttile(tl,3);

hold(ax3,'on');
box(ax3,'on');

addVoltageLines( ...
    ax3, ...
    [400 800 900 1000 1200], ...
    gridLineWidth);

scatter( ...
    ax3, ...
    V.Xplot, ...
    V.Power_kW, ...
    markerSize, ...
    's', ...
    'MarkerFaceColor',cVehicle, ...
    'MarkerEdgeColor',cVehicle, ...
    'LineWidth',1.1);

xlim(ax3,[xMin xMax]);
ylim(ax3,[yMin yMax]);

xticks(ax3,[400 800 900 1000 1200]);
yticks(ax3,0:100:900);

xlabel( ...
    ax3, ...
    'Traction-system voltage class (V)', ...
    'FontName',fontName, ...
    'FontSize',fontSize);

title( ...
    ax3, ...
    'Production battery-electric vehicles', ...
    'FontName',fontName, ...
    'FontSize',titleFont, ...
    'FontWeight','normal');

text( ...
    ax3, ...
    0.02,0.95,'(c)', ...
    'Units','normalized', ...
    'FontName',fontName, ...
    'FontSize',13, ...
    'FontWeight','bold', ...
    'VerticalAlignment','top');

%% ========================================================================
% COMMON IEEE AXIS FORMATTING
% ========================================================================

for ax = [ax1 ax2 ax3]

    ax.FontName = fontName;
    ax.FontSize = fontSize;

    ax.LineWidth = axisLineWidth;

    ax.TickDir = 'out';
    ax.TickLength = [0.015 0.015];

    ax.Layer = 'top';

    ax.XGrid = 'off';
    ax.YGrid = 'on';

    ax.GridColor = cGrid;
    ax.GridAlpha = 0.35;

    ax.Box = 'on';

end

%% ========================================================================
% IMPORTANT:
% LET MATLAB FINISH TILE POSITIONS BEFORE ANNOTATIONS
% ========================================================================

drawnow;

%% ========================================================================
% ADD EDITABLE TEXT-ARROWS
% ========================================================================

% -------------------------------------------------------------------------
% Research
% -------------------------------------------------------------------------

for k = 1:height(R)

    addEditableTextArrow( ...
        fig, ...
        ax1, ...
        R.Xplot(k), ...
        R.Power_kW(k), ...
        R.LabelX(k), ...
        R.LabelY(k), ...
        R.PlotLabel(k), ...
        cResearch, ...
        fontName, ...
        labelFont, ...
        arrowLineWidth);

end

% -------------------------------------------------------------------------
% Industry
% -------------------------------------------------------------------------

for k = 1:height(I)

    addEditableTextArrow( ...
        fig, ...
        ax2, ...
        I.Xplot(k), ...
        I.Power_kW(k), ...
        I.LabelX(k), ...
        I.LabelY(k), ...
        I.PlotLabel(k), ...
        cIndustry, ...
        fontName, ...
        labelFont, ...
        arrowLineWidth);

end

% -------------------------------------------------------------------------
% Vehicles
% -------------------------------------------------------------------------

for k = 1:height(V)

    addEditableTextArrow( ...
        fig, ...
        ax3, ...
        V.Xplot(k), ...
        V.Power_kW(k), ...
        V.LabelX(k), ...
        V.LabelY(k), ...
        V.PlotLabel(k), ...
        cVehicle, ...
        fontName, ...
        labelFont, ...
        arrowLineWidth);

end

%% ========================================================================
% ENABLE MANUAL EDITING
% ========================================================================

plotedit(fig,'on');

fprintf('\n');
fprintf('Figure generated successfully.\n');
fprintf('Plot Edit mode is ON.\n');
fprintf('Click and drag each text-arrow manually if required.\n\n');

fprintf('IMPORTANT: after manual editing, save a MATLAB FIG file:\n\n');

fprintf([ ...
    "savefig(gcf,'TractionVoltagePowerMap_final.fig');\n\n"]);

fprintf('Then export vector PDF:\n\n');

fprintf([ ...
    "exportgraphics(gcf,'TractionVoltagePowerMap_final.pdf'," ...
    "'ContentType','vector','BackgroundColor','white');\n\n"]);

fprintf('And optional 600-dpi PNG:\n\n');

fprintf([ ...
    "exportgraphics(gcf,'TractionVoltagePowerMap_final.png'," ...
    "'Resolution',600,'BackgroundColor','white');\n\n"]);

%% ========================================================================
% FUNCTION: CREATE SHORT DISPLAY LABEL
% ========================================================================

function output = createShortLabel(label,year)

    label = string(label);

    shortYear = mod(year,100);

    yearText = sprintf("'%02d",shortYear);

    name = lower(strtrim(label));

    %% Research

    if contains(name,"bertel")
        base = "Bertel.";

    elseif name == "taha"
        base = "Taha";

    elseif name == "absar"
        base = "Absar";

    elseif contains(name,"ut austin")
        base = "UT Austin";

    elseif contains(name,"bristol")
        base = "Bristol";

    elseif contains(name,"visic")
        base = "VisIC/UT Austin";

    elseif contains(name,"polito")
        base = "PoliTo/NEV";

    elseif contains(name,"mcmaster")
        base = "McMaster ARC";

    elseif contains(name,"arkansas")
        base = "U. Arkansas";

    elseif contains(name,"ayaz")
        base = "Ayaz et al.";

    %% Industrial

    elseif contains(name,"nxp")
        base = "NXP ref.";

    elseif contains(name,"bosch")
        base = "Bosch Gen4";

    elseif contains(name,"zf")
        base = "ZF platform";

    elseif contains(name,"wolfspeed") || contains(name,"ti /")
        base = "TI/Wolfspeed";

    elseif contains(name,"infineon")
        base = "Infineon eCAV";

    elseif contains(name,"avl")
        base = "AVL PI850e";

    elseif contains(name,"motion")
        base = "Motion IPG5";

    elseif contains(name,"punch")
        base = "Punch IV5";

    elseif contains(name,"saykal")
        base = "Saykal";

    %% Vehicles

    elseif contains(name,"polestar")
        base = "Polestar 2 Perf.";

    elseif contains(name,"bmw")
        base = "BMW i4 M50";

    elseif contains(name,"mercedes") || contains(name,"eqs")
        base = "Mercedes EQS 580";

    elseif contains(name,"mustang") || contains(name,"mach")
        base = "Mustang Mach-E GT";

    elseif contains(name,"ioniq")
        base = "Hyundai IONIQ 5 N";

    elseif contains(name,"kia") || contains(name,"ev6")
        base = "Kia EV6 GT";

    elseif contains(name,"volvo") || contains(name,"ex90")
        base = "Volvo EX90 Perf.";

    elseif contains(name,"audi")
        base = "Audi RS e-tron GT Perf.";

    elseif contains(name,"porsche") || contains(name,"taycan")
        base = "Porsche Taycan Turbo S";

    elseif contains(name,"lucid")
        base = "Lucid Air Dream Perf.";

    else
        base = label;

    end

    output = base + yearText;

end

%% ========================================================================
% FUNCTION: HORIZONTAL JITTER
% ========================================================================

function xPlot = applyJitter(voltage,maxOffset)

    voltage = voltage(:);

    xPlot = voltage;

    classes = unique(voltage);

    for ii = 1:length(classes)

        idx = find(voltage == classes(ii));

        n = length(idx);

        if n > 1

            offsets = linspace( ...
                -maxOffset, ...
                 maxOffset, ...
                 n)';

            xPlot(idx) = voltage(idx) + offsets;

        end

    end

end

%% ========================================================================
% FUNCTION: HAND-TUNED INITIAL LABEL POSITIONS
%
% Actual voltage/power still come from CSV/Excel.
% These values only determine where each annotation initially appears.
% ========================================================================

function [xLabel,yLabel] = getManualInitialPositions( ...
    T,panelNumber,xMin,xMax,yMin,yMax)

    n = height(T);

    xLabel = zeros(n,1);
    yLabel = zeros(n,1);

    %% --------------------------------------------------------------------
    % Generic default for any future new data point
    % ---------------------------------------------------------------------

    for k = 1:n

        if mod(k,2) == 0
            dx = 120;
        else
            dx = -120;
        end

        xLabel(k) = T.Voltage_V(k) + dx;

        yLabel(k) = T.Power_kW(k) + 35;

    end

    %% ====================================================================
    % PANEL (a): RESEARCH
    % ====================================================================

    if panelNumber == 1

        for k = 1:n

            name = lower(strtrim(string(T.Label(k))));
            voltage = T.Voltage_V(k);

            if contains(name,"bertel")

                xLabel(k) = 300;
                yLabel(k) = 195;

            elseif name == "taha" && voltage < 600

                xLabel(k) = 450;
                yLabel(k) = 155;

            elseif name == "taha" && voltage > 600

                xLabel(k) = 650;
                yLabel(k) = 155;

            elseif name == "absar" && voltage < 600

                xLabel(k) = 455;
                yLabel(k) = 70;

            elseif name == "absar" && voltage > 600

                xLabel(k) = 650;
                yLabel(k) = 65;

            elseif contains(name,"visic")

                xLabel(k) = 900;
                yLabel(k) = 60;

            elseif contains(name,"ut austin")

                xLabel(k) = 900;
                yLabel(k) = 330;

            elseif contains(name,"bristol")

                xLabel(k) = 1110;
                yLabel(k) = 60;

            elseif contains(name,"polito")

                xLabel(k) = 650;
                yLabel(k) = 445;

            elseif contains(name,"mcmaster")

                xLabel(k) = 920;
                yLabel(k) = 135;

            elseif contains(name,"arkansas")

                xLabel(k) = 1040;
                yLabel(k) = 235;

            elseif contains(name,"ayaz")

                xLabel(k) = 1090;
                yLabel(k) = 300;

            end

        end

    end

    %% ====================================================================
    % PANEL (b): INDUSTRIAL
    % ====================================================================

    if panelNumber == 2

        for k = 1:n

            name = lower(strtrim(string(T.Label(k))));
            voltage = T.Voltage_V(k);

            if contains(name,"bosch") && voltage < 600

                xLabel(k) = 305;
                yLabel(k) = 300;

            elseif contains(name,"bosch") && voltage > 600

                xLabel(k) = 650;
                yLabel(k) = 390;

            elseif contains(name,"zf") && voltage < 600

                xLabel(k) = 490;
                yLabel(k) = 65;

            elseif contains(name,"zf") && voltage > 600

                xLabel(k) = 960;
                yLabel(k) = 190;

            elseif contains(name,"nxp")

                xLabel(k) = 925;
                yLabel(k) = 155;

            elseif contains(name,"wolfspeed") || contains(name,"ti /")

                xLabel(k) = 660;
                yLabel(k) = 340;

            elseif contains(name,"infineon")

                xLabel(k) = 970;
                yLabel(k) = 225;

            elseif contains(name,"avl")

                xLabel(k) = 650;
                yLabel(k) = 260;

            elseif contains(name,"motion")

                xLabel(k) = 910;
                yLabel(k) = 450;

            elseif contains(name,"punch")

                xLabel(k) = 900;
                yLabel(k) = 650;

            elseif contains(name,"saykal") && voltage < 600

                xLabel(k) = 520;
                yLabel(k) = 220;

            elseif contains(name,"saykal") && voltage > 600

                xLabel(k) = 940;
                yLabel(k) = 290;

            end

        end

    end

    %% ====================================================================
    % PANEL (c): VEHICLES
    % ====================================================================

    if panelNumber == 3

        for k = 1:n

            name = lower(strtrim(string(T.Label(k))));

            if contains(name,"polestar")

                xLabel(k) = 300;
                yLabel(k) = 300;

            elseif contains(name,"bmw")

                xLabel(k) = 300;
                yLabel(k) = 445;

            elseif contains(name,"mercedes") || contains(name,"eqs")

                xLabel(k) = 520;
                yLabel(k) = 405;

            elseif contains(name,"mustang") || contains(name,"mach")

                xLabel(k) = 520;
                yLabel(k) = 330;

            elseif contains(name,"ioniq")

                xLabel(k) = 650;
                yLabel(k) = 525;

            elseif contains(name,"kia") || contains(name,"ev6")

                xLabel(k) = 990;
                yLabel(k) = 465;

            elseif contains(name,"volvo") || contains(name,"ex90")

                xLabel(k) = 970;
                yLabel(k) = 550;

            elseif contains(name,"audi")

                xLabel(k) = 650;
                yLabel(k) = 650;

            elseif contains(name,"porsche") || contains(name,"taycan")

                xLabel(k) = 980;
                yLabel(k) = 750;

            elseif contains(name,"lucid")

                xLabel(k) = 1030;
                yLabel(k) = 850;

            end

        end

    end

    %% --------------------------------------------------------------------
    % Keep starting positions inside axis limits
    % ---------------------------------------------------------------------

    xLabel = max(xLabel,xMin + 20);
    xLabel = min(xLabel,xMax - 20);

    yLabel = max(yLabel,yMin + 20);
    yLabel = min(yLabel,yMax - 20);

end

%% ========================================================================
% FUNCTION: ADD REFERENCE VOLTAGE LINES
% ========================================================================

function addVoltageLines(ax,values,lineWidth)

    for vv = values

        xline( ...
            ax, ...
            vv, ...
            ':', ...
            'Color',[0.75 0.75 0.75], ...
            'LineWidth',lineWidth, ...
            'HandleVisibility','off');

    end

end

%% ========================================================================
% FUNCTION: DATA COORDINATES -> FIGURE NORMALIZED COORDINATES
% ========================================================================

function [xNorm,yNorm] = ...
    dataToFigureNormalized(fig,ax,xData,yData)

    drawnow;

    %% Axes position in pixels

    axPixels = getpixelposition(ax,true);

    %% Figure dimensions

    originalUnits = fig.Units;

    fig.Units = 'pixels';

    figPosition = fig.Position;

    fig.Units = originalUnits;

    figWidth  = figPosition(3);
    figHeight = figPosition(4);

    %% Axis limits

    xLimits = ax.XLim;
    yLimits = ax.YLim;

    %% Fractional position within axes

    xFraction = ...
        (xData - xLimits(1)) / ...
        (xLimits(2) - xLimits(1));

    yFraction = ...
        (yData - yLimits(1)) / ...
        (yLimits(2) - yLimits(1));

    %% Position relative to full figure

    xPixels = ...
        axPixels(1) + ...
        xFraction*axPixels(3);

    yPixels = ...
        axPixels(2) + ...
        yFraction*axPixels(4);

    xNorm = xPixels / figWidth;
    yNorm = yPixels / figHeight;

end

%% ========================================================================
% FUNCTION: CREATE EDITABLE TEXT ARROW
% ========================================================================

function h = addEditableTextArrow( ...
    fig, ...
    ax, ...
    xPoint, ...
    yPoint, ...
    xLabel, ...
    yLabel, ...
    labelText, ...
    categoryColor, ...
    fontName, ...
    fontSize, ...
    lineWidth)

    %% Data point coordinates

    [xPointNorm,yPointNorm] = ...
        dataToFigureNormalized( ...
        fig, ...
        ax, ...
        xPoint, ...
        yPoint);

    %% Label coordinates

    [xLabelNorm,yLabelNorm] = ...
        dataToFigureNormalized( ...
        fig, ...
        ax, ...
        xLabel, ...
        yLabel);

    %% Editable annotation

    h = annotation( ...
        fig, ...
        'textarrow', ...
        [xLabelNorm xPointNorm], ...
        [yLabelNorm yPointNorm], ...
        'String',char(labelText), ...
        'FontName',fontName, ...
        'FontSize',fontSize, ...
        'Color',categoryColor, ...
        'LineWidth',lineWidth, ...
        'HeadStyle','vback2', ...
        'HeadLength',4, ...
        'HeadWidth',4, ...
        'HorizontalAlignment','center', ...
        'VerticalAlignment','middle', ...
        'Interpreter','none');

end
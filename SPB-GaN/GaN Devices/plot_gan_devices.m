%% Plot off-the-shelf GaN devices: Coss vs. RDS(on)
% Color  = vendor / brand
% Marker = voltage class

clear; clc; close all;

%% User settings
excelFile = "GaN_device_database.xlsx";
sheetName = "GaN_Device_Table";

capVar = "Coss_pF";
rdsVar = "RDSon_max_mOhm";   % use max value for consistent comparison

%% Read Excel table
T = readtable(excelFile, ...
    "Sheet", sheetName, ...
    "VariableNamingRule", "preserve");

T.Properties.VariableNames = matlab.lang.makeValidName(T.Properties.VariableNames);

capVar = matlab.lang.makeValidName(capVar);
rdsVar = matlab.lang.makeValidName(rdsVar);

%% Remove rows with missing data
validRows = ~isnan(T.(capVar)) & ~isnan(T.(rdsVar));
T = T(validRows, :);

%% Sort table by voltage and then RDS(on)
T = sortrows(T, {'Voltage_V', char(rdsVar)}, {'ascend', 'ascend'});

%% Extract vendors and voltage classes
vendors = unique(string(T.Vendor), "stable");
voltageLevels = unique(T.Voltage_V, "stable");

%% Plot settings
markerList = {'o','s','^','d','v','>','<','p','h','x','+'};

if numel(voltageLevels) > numel(markerList)
    error("Not enough marker types for all voltage levels.");
end

colors = lines(numel(vendors));

%% Create large figure
fig = figure('Color','w', 'Position', [100 100 1400 850]);

% Main axes: leave space on the right for legends
ax = axes(fig, 'Position', [0.08 0.13 0.60 0.78]);
hold(ax, 'on');
grid(ax, 'on');
box(ax, 'on');

%% Plot each device
for i = 1:height(T)

    vendorIdx = find(vendors == string(T.Vendor(i)), 1);
    voltageIdx = find(voltageLevels == T.Voltage_V(i), 1);

    scatter(ax, T.(capVar)(i), T.(rdsVar)(i), 120, ...
        'Marker', markerList{voltageIdx}, ...
        'MarkerEdgeColor', colors(vendorIdx,:), ...
        'MarkerFaceColor', colors(vendorIdx,:), ...
        'LineWidth', 1.3);

    text(ax, T.(capVar)(i)*1.06, T.(rdsVar)(i)*1.06, string(T.Device(i)), ...
        'FontSize', 8, ...
        'Interpreter', 'none');
end

%% Axis settings
set(ax, 'XScale', 'log', 'YScale', 'log');
set(ax, 'FontSize', 12, 'LineWidth', 1.1);

xlabel(ax, 'Output capacitance, C_{oss} (pF)', ...
    'Interpreter', 'tex', ...
    'FontSize', 13);

ylabel(ax, 'On-state resistance, R_{DS(on),max} (m\Omega)', ...
    'Interpreter', 'tex', ...
    'FontSize', 13);

title(ax, 'Off-the-shelf GaN devices: C_{oss} vs. R_{DS(on)}', ...
    'Interpreter', 'tex', ...
    'FontSize', 14);

xlim(ax, [8 3000]);
ylim(ax, [0.5 600]);

%% Vendor legend: color meaning
vendorHandles = gobjects(numel(vendors),1);

for k = 1:numel(vendors)
    vendorHandles(k) = scatter(ax, nan, nan, 120, 'o', ...
        'MarkerEdgeColor', colors(k,:), ...
        'MarkerFaceColor', colors(k,:), ...
        'LineWidth', 1.3);
end

lgdVendor = legend(ax, vendorHandles, vendors, ...
    'Location', 'northeastoutside', ...
    'Interpreter', 'none');

title(lgdVendor, 'Vendor');

%% Manual voltage-class legend
axV = axes(fig, 'Position', [0.72 0.18 0.23 0.35]);
hold(axV, 'on');
axis(axV, 'off');

text(axV, 0.00, 1.05, 'Voltage class', ...
    'FontWeight', 'bold', ...
    'FontSize', 11, ...
    'Units', 'normalized');

for k = 1:numel(voltageLevels)

    y = 1.0 - 0.10*k;

    scatter(axV, 0.12, y, 120, ...
        'Marker', markerList{k}, ...
        'MarkerEdgeColor', 'k', ...
        'MarkerFaceColor', 'k', ...
        'LineWidth', 1.3);

    text(axV, 0.25, y, string(voltageLevels(k)) + " V", ...
        'FontSize', 10, ...
        'VerticalAlignment', 'middle');
end

xlim(axV, [0 1]);
ylim(axV, [0 1]);

%% Save figure
exportgraphics(fig, 'GaN_Coss_vs_RDSon_expanded.png', 'Resolution', 300);

disp("Plot saved as GaN_Coss_vs_RDSon_expanded.png");
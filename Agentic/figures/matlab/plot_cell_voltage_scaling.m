clear;
clc;
close all;

%% ========================================================
% PATHS
% =========================================================

scriptFolder = fileparts(mfilename('fullpath'));

projectFolder = fullfile( ...
    scriptFolder, ...
    '..', ...
    '..');

dataFile = fullfile( ...
    projectFolder, ...
    'data', ...
    'comparison.csv');

outputFolder = fullfile( ...
    projectFolder, ...
    'figures', ...
    'generated');

if ~exist(outputFolder, 'dir')
    mkdir(outputFolder);
end

%% ========================================================
% READ DATA
% =========================================================

T = readtable( ...
    dataFile, ...
    'VariableNamingRule', ...
    'preserve');

yColumn = 'voltage_v';

if ~ismember(yColumn, T.Properties.VariableNames)
    error('Missing column: %s', yColumn);
end

y = T.(yColumn);

valid = ~ismissing(y);

y = y(valid);

if numel(y) < 1
    error( ...
        'Not enough valid data points. Found %d.', ...
        numel(y));
end

%% ========================================================
% LABELS
% =========================================================

if ismember( ...
        'citation_key', ...
        T.Properties.VariableNames)

    labels = string( ...
        T.citation_key(valid));

else

    labels = string( ...
        1:numel(y));

end

%% ========================================================
% CREATE FIGURE
% =========================================================

figure;

bar(y);

xticks( ...
    1:numel(y));

xticklabels( ...
    labels);

xtickangle(45);

ylabel( ...
    'Voltage (V)', ...
    'Interpreter', ...
    'none');

title( ...
    'DC-Link Voltage and Series-Cell Voltage in the Stacked Converter', ...
    'Interpreter', ...
    'none');

grid on;
box on;

%% ========================================================
% EXPORT
% =========================================================

outputFile = fullfile( ...
    outputFolder, ...
    'fig_cell_voltage_scaling.pdf');

exportgraphics( ...
    gcf, ...
    outputFile, ...
    'ContentType', ...
    'vector');

fprintf( ...
    'Figure saved to: %s\n', ...
    outputFile);

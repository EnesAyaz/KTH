clear; clc; close all;
%% Set up the Import Options and import the data
opts = delimitedTextImportOptions("NumVariables", 4);

% Specify range and delimiter
opts.DataLines = [1, Inf];
opts.Delimiter = ",";

% Specify column names and types
opts.VariableNames = ["Time", "Va", "Vb", "Vc"];
opts.VariableTypes = ["double", "double", "double", "double"];

% Specify file level properties
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
opts.ConsecutiveDelimitersRule = "join";

% Import the data
tbl = readtable("C:\Users\enesa\OneDrive - KTH\Documents\Experimental Data\ECCE-2025\2025.02.12\SDS00023.csv", opts);

%% Convert to output type
Time = tbl.Time;
Va = tbl.Va;
Vb = tbl.Vb;
Vc = tbl.Vc;

%% Clear temporary variables
clear opts tbl

OnlyCMV
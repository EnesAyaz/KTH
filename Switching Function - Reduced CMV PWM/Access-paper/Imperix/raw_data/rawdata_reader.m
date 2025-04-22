opts = delimitedTextImportOptions("NumVariables", 5);

% Specify range and delimiter
opts.DataLines = [13, Inf];
opts.Delimiter = ",";

% Specify column names and types
opts.VariableNames = ["HorizontalUnits", "us", "VarName3", "VarName4", "VarName5"];
opts.VariableTypes = ["double", "double", "double", "double","double"];

% Specify file level properties
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
opts.ConsecutiveDelimitersRule = "join";

% Import the data

SDS00001 = readtable("C:\Github\KTH\Switching Function - Reduced CMV PWM\Access-paper\Imperix\raw_data\SDS00004.csv", opts);

%% Convert to output type
data_VABC = table2array(SDS00001);

%% Clear temporary variables
clear opts
%% SPB level optimization using only available discrete GaN voltage classes
% System: Vdc = 1200 V, Pout = 300 kW
%
% This script creates:
%   1) GaN device database: RDS(on) vs Coss
%   2) Device FOM graph: 1/sqrt(RDS(on)*Coss)
%   3) Discrete SPB levels vs selected best-FOM GaN device
%   4) Conduction loss vs discrete number of levels
%   5) Switching energy/loss vs discrete number of levels,
%      including Coss energy and dv/dt, di/dt overlap energy
%
% IMPORTANT:
% Only levels created by the available device voltage classes are evaluated.
% For Vdc = 1200 V and kSafety = 1.5:
%   cells = ceil(kSafety*Vdc / Vdevice_rating)
%   levels = cells + 1
%
% Therefore the x-axis contains only realizable/discrete points such as
% 4, 7, 10, 12, 13, 16, 19, etc., depending on the voltage classes in Excel.

clear; clc; close all;

%% ===================== USER INPUTS =====================
excelFile = "GaN_device_database_added_120_150_175V.xlsx";

if ~isfile(excelFile)
    excelFile = "GaN_device_database_expanded.xlsx";
end

if ~isfile(excelFile)
    excelFile = "GaN_device_database.xlsx";
end

sheetName = "GaN_Device_Table";

% System requirements
Vdc      = 1200;      % DC-link voltage [V]
Pout     = 300e3;     % total three-phase output power [W]
pf       = 0.90;      % power factor
modIndex = 0.90;      % modulation index
fsw      = 100e3;      % switching frequency per device [Hz]

% Design margin
kSafety = 1.2;        % Vdevice >= kSafety * Vdc / cells

% Parallel-device sweep
maxParallel = 10;     % allow enough paralleling for 300 kW case

% Switching transient assumptions
dvdt_V_per_ns = 100;   % voltage slew rate [V/ns]
didt_A_per_ns = 15;    % current slew rate [A/ns]

% Current used for switching overlap energy
% "averageAbs" is recommended for sinusoidal PWM screening.
% Other options: "rms", "peak"
switchCurrentMode = "averageAbs";

% Device selection mode:
% "bestFOM"      -> for each discrete level, choose feasible device with highest FOM
% "minTotalLoss" -> choose feasible device/parallel count with minimum Pcond+Psw
deviceSelectionMode = "bestFOM";

%% ===================== DERIVED OPERATING POINT =====================
Vphase_peak = modIndex * Vdc / 2;
Vphase_rms  = Vphase_peak / sqrt(2);
VLL_rms     = sqrt(3) * Vphase_rms;

Iphase_rms  = Pout / (sqrt(3) * VLL_rms * pf);
Iphase_peak = sqrt(2) * Iphase_rms;

switch switchCurrentMode
    case "averageAbs"
        Isw = 2/pi * Iphase_peak;     % average absolute sinusoidal current
    case "rms"
        Isw = Iphase_rms;
    case "peak"
        Isw = Iphase_peak;
    otherwise
        error("Unknown switchCurrentMode.");
end

dvdt = dvdt_V_per_ns * 1e9;   % [V/s]
didt = didt_A_per_ns * 1e9;   % [A/s]

fprintf('\nSystem inputs\n');
fprintf('Vdc = %.0f V, Pout = %.0f kW, pf = %.2f, modulation = %.2f\n', ...
    Vdc, Pout/1e3, pf, modIndex);
fprintf('VLL,rms = %.1f V, Iphase,rms = %.1f A, Iphase,peak = %.1f A\n', ...
    VLL_rms, Iphase_rms, Iphase_peak);
fprintf('Switching overlap current used = %.1f A (%s)\n', Isw, switchCurrentMode);
fprintf('dv/dt = %.1f V/ns, di/dt = %.1f A/ns\n\n', dvdt_V_per_ns, didt_A_per_ns);

%% ===================== READ DEVICE DATABASE =====================
T = readtable(excelFile, "Sheet", sheetName, "VariableNamingRule", "preserve");
T.Properties.VariableNames = matlab.lang.makeValidName(T.Properties.VariableNames);

% Remove accidental test rows
if ismember("Device", T.Properties.VariableNames)
    T = T(~contains(string(T.Device), ["Trial","Enes"], "IgnoreCase", true), :);
end

if ismember("Vendor", T.Properties.VariableNames)
    T = T(~contains(string(T.Vendor), ["Trial","Enes"], "IgnoreCase", true), :);
end

% Select RDS(on): maximum preferred; typical used only if maximum is missing
Rds_mOhm = NaN(height(T),1);

if ismember("RDSon_max_mOhm", T.Properties.VariableNames)
    Rds_mOhm = T.RDSon_max_mOhm;
end

if ismember("RDSon_typ_mOhm", T.Properties.VariableNames)
    idx = isnan(Rds_mOhm);
    Rds_mOhm(idx) = T.RDSon_typ_mOhm(idx);
end

% Select capacitance: Coss preferred; then Co(tr); then Co(er)
Coss_pF = NaN(height(T),1);

if ismember("Coss_pF", T.Properties.VariableNames)
    Coss_pF = T.Coss_pF;
end

if ismember("Co_tr_pF", T.Properties.VariableNames)
    idx = isnan(Coss_pF);
    Coss_pF(idx) = T.Co_tr_pF(idx);
end

if ismember("Co_er_pF", T.Properties.VariableNames)
    idx = isnan(Coss_pF);
    Coss_pF(idx) = T.Co_er_pF(idx);
end

% Current rating if available
Current_A = NaN(height(T),1);

if ismember("Current_A", T.Properties.VariableNames)
    Current_A = T.Current_A;
end

% Keep valid GaN rows
valid = ~isnan(T.Voltage_V) & ~isnan(Rds_mOhm) & ~isnan(Coss_pF);
T = T(valid,:);
Rds_mOhm = Rds_mOhm(valid);
Coss_pF = Coss_pF(valid);
Current_A = Current_A(valid);

% Device FOM
D_FOM = 1 ./ sqrt((Rds_mOhm*1e-3) .* (Coss_pF*1e-12));
D_FOM_norm = D_FOM ./ max(D_FOM);

T.RDSon_used_mOhm = Rds_mOhm;
T.Coss_used_pF = Coss_pF;
T.Current_used_A = Current_A;
T.D_FOM = D_FOM;
T.D_FOM_norm = D_FOM_norm;

%% ===================== DISCRETE LEVELS FROM AVAILABLE VOLTAGE CLASSES =====================
availableVoltageClasses = unique(T.Voltage_V);
availableVoltageClasses = sort(availableVoltageClasses(:));

% A voltage class creates a required number of SPB cells.
cellsFromVoltage = ceil(kSafety * Vdc ./ availableVoltageClasses);
levelsFromVoltage = cellsFromVoltage + 1;

% Unique discrete realizable levels only
discreteLevels = unique(levelsFromVoltage);
discreteLevels = sort(discreteLevels(:));

fprintf('Available device voltage classes in database:\n');
disp(availableVoltageClasses.');

fprintf('Discrete SPB levels evaluated only from available voltage classes:\n');
disp(discreteLevels.');

%% ===================== OPTIMIZATION OVER DISCRETE LEVELS =====================
nL = numel(discreteLevels);

Best = table();

for kk = 1:nL

    Levels = discreteLevels(kk);
    Cells = Levels - 1;

    Vcell = Vdc / Cells;
    Vreq = kSafety * Vcell;

    feasibleIdx = find(T.Voltage_V >= Vreq);

    if isempty(feasibleIdx)
        continue;
    end

    candidateRows = table();

    for a = 1:numel(feasibleIdx)

        ii = feasibleIdx(a);

        for nPar = 1:maxParallel

            % Current feasibility check, if current rating is known.
            % Use peak current as a conservative current-rating screen.
            currentOK = true;
            if ~isnan(T.Current_used_A(ii))
                currentOK = (T.Current_used_A(ii) * nPar >= Iphase_peak);
            end

            if ~currentOK
                continue;
            end

            % Parallel equivalent switch
            R_eq = (T.RDSon_used_mOhm(ii)*1e-3) / nPar;
            C_eq = (T.Coss_used_pF(ii)*1e-12) * nPar;

            % Conduction loss
            Pcond = 3 * Cells * Iphase_rms^2 * R_eq;

            % Coss energy per equivalent switch position per switching cycle
            E_coss = C_eq * Vcell^2;

            % dv/dt and di/dt overlap time
            t_v = Vcell / dvdt;
            t_i = Isw / didt;

            % First-order overlap energy.
            % This is equivalent to adding turn-on and turn-off linear overlap
            % using Eon+Eoff approx V*I*(t_v+t_i).
            E_overlap = Vcell * Isw * (t_v + t_i)/6;

            E_sw_total = E_coss + E_overlap;

            % Switching loss
            P_coss = 3 * Cells * fsw * E_coss;
            P_overlap = 3 * Cells * fsw * E_overlap;
            Psw = P_coss + P_overlap;

            Ptotal = Pcond + Psw;
            eta = 100 * Pout / (Pout + Ptotal);

            totalDevices = 6 * Cells * nPar;

            newRow = table( ...
                Levels, Cells, Vcell, Vreq, ...
                string(T.Device(ii)), string(T.Vendor(ii)), T.Voltage_V(ii), ...
                nPar, T.RDSon_used_mOhm(ii), T.Coss_used_pF(ii), ...
                T.D_FOM_norm(ii), ...
                E_coss*1e6, E_overlap*1e6, E_sw_total*1e6, ...
                Pcond, P_coss, P_overlap, Psw, Ptotal, eta, totalDevices, ...
                'VariableNames', {'Levels','Cells','Vcell_V','Required_Device_V', ...
                'Device','Vendor','Device_V','Parallel','RDSon_mOhm','Coss_pF', ...
                'D_FOM_norm','E_coss_uJ','E_overlap_uJ','E_total_sw_uJ', ...
                'Pcond_W','P_coss_W','P_overlap_W','Psw_W','Ptotal_W','Efficiency_pct','Total_Devices'} );

            candidateRows = [candidateRows; newRow]; %#ok<AGROW>
        end
    end

    if isempty(candidateRows)
        continue;
    end

    switch deviceSelectionMode
        case "bestFOM"
            % Pick the device with highest FOM first.
            % Then, among its parallel options, pick the minimum total loss.
            maxFom = max(candidateRows.D_FOM_norm);
            sub = candidateRows(candidateRows.D_FOM_norm == maxFom, :);
            [~, idx] = min(sub.Ptotal_W);
            selected = sub(idx,:);

        case "minTotalLoss"
            [~, idx] = min(candidateRows.Ptotal_W);
            selected = candidateRows(idx,:);

        otherwise
            error("Unknown deviceSelectionMode.");
    end

    Best = [Best; selected]; %#ok<AGROW>
end

%% ===================== SAVE RESULTS =====================
writetable(Best, "spb_1200V_300kW_discrete_levels_best_devices.csv");

fprintf('\nSelected devices for discrete levels:\n');
disp(Best(:, {'Levels','Cells','Required_Device_V','Device','Vendor','Device_V','Parallel','D_FOM_norm','Pcond_W','Psw_W','Ptotal_W','Efficiency_pct'}));

%% ===================== PLOTS =====================
fig = figure('Color','w', 'Position', [80 50 1500 900]);
tiledlayout(2,3, 'TileSpacing','compact', 'Padding','compact');

%% 1) RDS(on) vs Coss
nexttile;
scatter(T.Coss_used_pF, T.RDSon_used_mOhm, 65, T.Voltage_V, 'filled');
set(gca, 'XScale','log', 'YScale','log');
grid on; box on;
xlabel('C_{oss} used (pF)', 'Interpreter','tex');
ylabel('R_{DS(on)} used (m\Omega)', 'Interpreter','tex');
title('GaN devices: R_{DS(on)} vs. C_{oss}', 'Interpreter','tex');
cb = colorbar;
cb.Label.String = 'Device voltage rating (V)';

%% 2) FOM graph
nexttile;
scatter(T.Voltage_V, T.D_FOM_norm, 65, T.Voltage_V, 'filled');
grid on; box on;
xlabel('Device voltage rating (V)');
ylabel('Normalized D-FOM');
title('D-FOM = 1/sqrt(R_{DS(on)} C_{oss})', 'Interpreter','tex');
xticks(availableVoltageClasses);
xtickangle(45);

%% 3) Number of levels vs selected best-FOM device
nexttile;
scatter(Best.Levels, Best.Device_V, 90, Best.D_FOM_norm, 'filled');
grid on; box on;
xlabel('SPB voltage levels = cells + 1');
ylabel('Selected device rating (V)');
title('Discrete levels vs. selected best-FOM device');
xticks(Best.Levels);
yticks(availableVoltageClasses);
cb = colorbar;
cb.Label.String = 'Normalized D-FOM';

for k = 1:height(Best)
    labelText = string(Best.Device(k)) + ", " + string(Best.Parallel(k)) + "p";
    text(Best.Levels(k)+0.08, Best.Device_V(k), labelText, ...
        'FontSize', 8, 'Interpreter','none');
end

%% 4) Conduction loss vs levels
nexttile;
plot(Best.Levels, Best.Pcond_W/1000, '-o', 'LineWidth', 1.7, 'MarkerSize', 7);
grid on; box on;
xlabel('SPB voltage levels = cells + 1');
ylabel('Conduction loss (kW)');
title('Conduction loss vs. discrete levels');
xticks(Best.Levels);

%% 5) Switching energy vs levels
nexttile;
plot(Best.Levels, Best.E_coss_uJ, '-o', 'LineWidth', 1.7, 'MarkerSize', 7); hold on;
plot(Best.Levels, Best.E_overlap_uJ, '-s', 'LineWidth', 1.7, 'MarkerSize', 7);
plot(Best.Levels, Best.E_total_sw_uJ, '-^', 'LineWidth', 1.7, 'MarkerSize', 7);
grid on; box on;
xlabel('SPB voltage levels = cells + 1');
ylabel('Switching energy per equivalent switch cycle (\muJ)', 'Interpreter','tex');
title('Switching energy: C_{oss} + dv/dt, di/dt overlap', 'Interpreter','tex');
legend('E_{Coss}', 'E_{overlap}', 'E_{total}', 'Location','best', 'Interpreter','tex');
xticks(Best.Levels);

%% 6) Switching loss breakdown vs levels
nexttile;
bar(Best.Levels, [Best.P_coss_W, Best.P_overlap_W]/1000, 'stacked');
grid on; box on;
xlabel('SPB voltage levels = cells + 1');
ylabel('Switching loss (kW)');
title('Switching loss breakdown');
legend('C_{oss} loss', 'Overlap loss', 'Location','best', 'Interpreter','tex');
xticks(Best.Levels);

sgtitle(sprintf('SPB GaN level optimization: %.0f V DC, %.0f kW, fsw = %.0f kHz, dv/dt = %.0f V/ns, di/dt = %.1f A/ns', ...
    Vdc, Pout/1e3, fsw/1e3, dvdt_V_per_ns, didt_A_per_ns), ...
    'FontWeight','bold');

exportgraphics(fig, "SPB_1200V_300kW_discrete_levels_dvdt_didt.png", "Resolution", 300);

fprintf('\nSaved:\n');
fprintf('  spb_1200V_300kW_discrete_levels_best_devices.csv\n');
fprintf('  SPB_1200V_300kW_discrete_levels_dvdt_didt.png\n');

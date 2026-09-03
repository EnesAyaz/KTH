%% SPB level optimization for 1200 V / 300 kW
% Graph style updated to match the 4-panel summary figure.
% Includes 100 V devices in the database view.
%
% Important note:
% With kSafety = 1.5 and Vdc = 1200 V,
% required device rating per cell is:
%   Vreq = 1.5*1200/(Levels-1) = 1800/(Levels-1)
% Therefore 100 V devices become feasible only from:
%   Levels >= 19   (or Cells >= 18)
%
% If you only want to stop at 15 levels, set maxLevels = 15.
% In that case, the 100 V devices will still appear in the database plots,
% but they will not be feasible in the real-device optimization.

clear; clc; close all;

%% ================= USER INPUTS =================
excelFile = "GaN_device_database_added_120_150_175V.xlsx";
if ~isfile(excelFile)
    excelFile = "GaN_device_database_expanded.xlsx";
end
if ~isfile(excelFile)
    excelFile = "GaN_device_database.xlsx";
end
sheetName = "GaN_Device_Table";

Vdc      = 1200;     % total DC-link voltage [V]
Pout     = 300e3;    % total 3-phase output power [W]
pf       = 0.90;     % power factor
modIndex = 0.90;     % modulation index
fsw      = 20e3;     % per-device switching frequency [Hz]
kSafety  = 1.2;      % device voltage safety factor

maxLevels   = 20;    % use 20 so that 100 V feasibility becomes visible
maxParallel = 6;    % maximum number of paralleled devices per switch

% Practical penalty terms (simple screening only)
overhead_W_per_cell = 80;    % balancing/gate-drive/control overhead per cell [W]
componentPenalty_W  = 0.4;   % extra penalty per discrete device [W-eq]

% Ideal GaN D-FOM exponent from X-FOM paper:
% alpha_DFOM ~= -0.2  -> D-FOM ~ U_B^(-0.2)
alpha_DFOM_GaN = -0.2;

%% ================= DERIVED OPERATING POINT =================
Vphase_peak = modIndex * Vdc / 2;
Vphase_rms  = Vphase_peak / sqrt(2);
VLL_rms     = sqrt(3) * Vphase_rms;
Iphase_rms  = Pout / (sqrt(3) * VLL_rms * pf);
Iphase_peak = sqrt(2) * Iphase_rms;

fprintf('System: Vdc = %.0f V, Pout = %.0f kW, pf = %.2f, m = %.2f\n', ...
    Vdc, Pout/1e3, pf, modIndex);
fprintf('Estimated VLL,rms = %.1f V, Iphase,rms = %.1f A, Iphase,peak = %.1f A\n', ...
    VLL_rms, Iphase_rms, Iphase_peak);

%% ================= READ DATABASE =================
T = readtable(excelFile, 'Sheet', sheetName, 'VariableNamingRule', 'preserve');
T.Properties.VariableNames = matlab.lang.makeValidName(T.Properties.VariableNames);

% Remove accidental test rows
if ismember('Device', T.Properties.VariableNames)
    T = T(~contains(string(T.Device), ["Trial","Enes"], 'IgnoreCase', true), :);
end
if ismember('Vendor', T.Properties.VariableNames)
    T = T(~contains(string(T.Vendor), ["Trial","Enes"], 'IgnoreCase', true), :);
end

% Prefer max RDS(on), otherwise typ
Rds_mOhm = NaN(height(T),1);
if ismember('RDSon_max_mOhm', T.Properties.VariableNames)
    Rds_mOhm = T.RDSon_max_mOhm;
end
if ismember('RDSon_typ_mOhm', T.Properties.VariableNames)
    idx = isnan(Rds_mOhm);
    Rds_mOhm(idx) = T.RDSon_typ_mOhm(idx);
end

% Prefer Coss, then Co_tr, then Co_er
Coss_pF = NaN(height(T),1);
if ismember('Coss_pF', T.Properties.VariableNames)
    Coss_pF = T.Coss_pF;
end
if ismember('Co_tr_pF', T.Properties.VariableNames)
    idx = isnan(Coss_pF);
    Coss_pF(idx) = T.Co_tr_pF(idx);
end
if ismember('Co_er_pF', T.Properties.VariableNames)
    idx = isnan(Coss_pF);
    Coss_pF(idx) = T.Co_er_pF(idx);
end

% Prefer current column if available
Current_A = NaN(height(T),1);
if ismember('Current_A', T.Properties.VariableNames)
    Current_A = T.Current_A;
end

valid = ~isnan(T.Voltage_V) & ~isnan(Rds_mOhm) & ~isnan(Coss_pF);
T = T(valid,:);
Rds_mOhm = Rds_mOhm(valid);
Coss_pF  = Coss_pF(valid);
Current_A = Current_A(valid);

% Device FOM = 1/sqrt(RDS(on) * Coss)
D_FOM = 1 ./ sqrt((Rds_mOhm * 1e-3) .* (Coss_pF * 1e-12));
D_FOM_norm = D_FOM ./ max(D_FOM);

%% ================= LEVEL SWEEP =================
levelList = (2:maxLevels).';
numLevels = numel(levelList);
requiredVoltage = NaN(numLevels,1);
idealDFOMrel    = NaN(numLevels,1);
bestAvailDFOMpc = NaN(numLevels,1);   % best available normalized D-FOM / cell count
bestLoss_W      = NaN(numLevels,1);
bestScore_W     = NaN(numLevels,1);
bestEff_pct     = NaN(numLevels,1);
bestDevV        = NaN(numLevels,1);
bestParallel    = NaN(numLevels,1);
bestName        = strings(numLevels,1);

resultRows = [];

% Reference point for ideal scaling: the 2-level required device rating
Vref = kSafety * Vdc / (2-1);

for kk = 1:numLevels
    Levels = levelList(kk);
    Cells  = Levels - 1;

    Vcell = Vdc / Cells;
    Vreq  = kSafety * Vcell;
    requiredVoltage(kk) = Vreq;

    % Ideal GaN D-FOM scaling from X-FOM paper:
    % D-FOM(U) / D-FOM(Uref) = (Uref/U)^(-alpha_DFOM)
    idealDFOMrel(kk) = (Vref / Vreq)^(-alpha_DFOM_GaN);

    feasible = find(T.Voltage_V >= Vreq);
    if isempty(feasible)
        continue;
    end

    % Best available D-FOM per cell count (heuristic index)
    bestAvailDFOMpc(kk) = max(D_FOM_norm(feasible)) / Cells;

    % Real-device optimization
    localBestLoss  = inf;
    localBestScore = inf;
    localBestEff   = NaN;
    localBestDevV  = NaN;
    localBestPar   = NaN;
    localBestName  = "";

    for ii = feasible.'
        for nPar = 1:maxParallel

            % Current screening if current rating exists
            currentOK = true;
            if ~isnan(Current_A(ii))
                currentOK = (Current_A(ii) * nPar >= Iphase_peak);
            end
            if ~currentOK
                continue;
            end

            % Simplified equivalent per-switch values with paralleling
            R_eq = (Rds_mOhm(ii) * 1e-3) / nPar;
            C_eq = (Coss_pF(ii) * 1e-12) * nPar;

            % Simplified SPB semiconductor loss model
            Pcond = 3 * Cells * (Iphase_rms^2) * R_eq;
            Psw   = 3 * Cells * fsw * C_eq * (Vcell^2);
            Psemi = Pcond + Psw;
            eff   = 100 * Pout / (Pout + Psemi);

            totalDevices = 6 * Cells * nPar;
            score = Psemi + overhead_W_per_cell * Cells + componentPenalty_W * totalDevices;

            resultRows = [resultRows; ...
                Levels, Cells, Vreq, T.Voltage_V(ii), nPar, Rds_mOhm(ii), Coss_pF(ii), ...
                D_FOM_norm(ii), Pcond, Psw, Psemi, eff, score]; %#ok<AGROW>

            if Psemi < localBestLoss
                localBestLoss = Psemi;
                localBestEff  = eff;
                localBestDevV = T.Voltage_V(ii);
                localBestPar  = nPar;
                localBestName = string(T.Device(ii)) + " | " + string(T.Vendor(ii));
            end
            if score < localBestScore
                localBestScore = score;
            end
        end
    end

    if isfinite(localBestLoss)
        bestLoss_W(kk)   = localBestLoss;
        bestScore_W(kk)  = localBestScore;
        bestEff_pct(kk)  = localBestEff;
        bestDevV(kk)     = localBestDevV;
        bestParallel(kk) = localBestPar;
        bestName(kk)     = localBestName;
    end
end

%% ================= CONSOLE NOTES =================
first100 = find(requiredVoltage <= 100, 1, 'first');
if ~isempty(first100)
    fprintf('100 V devices first become feasible at Level = %d (Cells = %d).\n', ...
        levelList(first100), levelList(first100)-1);
else
    fprintf('100 V devices are NOT feasible in the chosen level sweep.\n');
end

idx15 = find(levelList == 15, 1);
if ~isempty(idx15)
    fprintf('At Level 15, required device rating = %.1f V.\n', requiredVoltage(idx15));
end

%% ================= SAVE TABLES =================
Summary = table(levelList, levelList-1, requiredVoltage, idealDFOMrel, bestAvailDFOMpc, ...
    bestLoss_W, bestScore_W, bestEff_pct, bestDevV, bestParallel, bestName, ...
    'VariableNames', {'Levels','Cells','Required_Device_V','Ideal_GaN_DFOM_Rel','Best_Available_DFOM_per_Cell', ...
    'Best_Loss_W','Best_Score_W','Best_Efficiency_pct','Best_Device_V','Best_Parallel','Best_Device'});

writetable(Summary, 'spb_1200V_300kW_graphstyle_summary.csv');

%% ================= PLOTTING =================
fig = figure('Color','w', 'Position', [100 80 1350 900]);
tiledlayout(2,2,'TileSpacing','compact','Padding','compact');

% -------- Top-left: device database scatter --------
nexttile;
scatter(Coss_pF, Rds_mOhm, 60, T.Voltage_V, 'filled');
set(gca, 'XScale', 'log', 'YScale', 'log', 'FontSize', 11);
grid on; box on;
xlabel('C_{oss} used (pF)', 'Interpreter', 'tex');
ylabel('R_{DS(on)} used (m\Omega)', 'Interpreter', 'tex');
title('GaN device database', 'FontWeight', 'bold');
cb = colorbar; cb.Label.String = 'Voltage rating (V)';

% -------- Top-right: FOM vs voltage --------
nexttile;
scatter(T.Voltage_V, D_FOM_norm, 55, T.Voltage_V, 'filled');
grid on; box on; set(gca, 'FontSize', 11);
xlabel('Device voltage rating (V)');
ylabel('Normalized D-FOM');
title('Device FOM = 1/sqrt(R_{DS(on)} C_{oss})', 'Interpreter', 'tex', 'FontWeight', 'bold');

% -------- Bottom-left: FOM scaling vs level number --------
nexttile;
yyaxis left;
plot(levelList, requiredVoltage, '-o', 'LineWidth', 1.6, 'MarkerSize', 6);
ylabel('Required device rating (V)');
ylim([0 max(requiredVoltage)*1.05]);

yyaxis right;
plot(levelList, idealDFOMrel, '--s', 'LineWidth', 1.6, 'MarkerSize', 6); hold on;
plot(levelList, bestAvailDFOMpc, ':^', 'LineWidth', 1.8, 'MarkerSize', 7);
ylabel('Normalized index');
grid on; box on;
xlabel('SPB voltage levels \approx cells + 1');
title('FOM scaling vs. level number', 'FontWeight', 'bold');
legend('Required rating', 'Ideal GaN D-FOM', 'D-FOM / cell count', 'Location', 'best');

% Mark level 15 and 19 for clarity
xline(15, '--', '15 levels', 'LabelOrientation', 'horizontal');
xline(19, '--', '100 V feasible', 'LabelOrientation', 'horizontal');

% -------- Bottom-right: real-device optimization --------
nexttile;
yyaxis left;
plot(levelList, bestLoss_W, '-o', 'LineWidth', 1.6, 'MarkerSize', 6); hold on;
plot(levelList, bestScore_W, '--s', 'LineWidth', 1.6, 'MarkerSize', 6);
ylabel('Estimated semiconductor loss / score (W)');

yyaxis right;
plot(levelList, bestEff_pct, '-^', 'LineWidth', 1.6, 'MarkerSize', 7);
ylabel('Efficiency (%)');
grid on; box on;
xlabel('SPB voltage levels \approx cells + 1');
title('Real-device optimization', 'FontWeight', 'bold');
legend('Best loss', 'Loss + overhead', 'Efficiency', 'Location', 'best');

sgtitle(sprintf('SPB optimization summary: V_{dc} = %.0f V, P = %.0f kW', Vdc, Pout/1e3), ...
    'FontWeight', 'bold');

exportgraphics(fig, 'SPB_1200V_300kW_graphstyle_with_100V.png', 'Resolution', 300);
fprintf('Saved: spb_1200V_300kW_graphstyle_summary.csv\n');
fprintf('Saved: SPB_1200V_300kW_graphstyle_with_100V.png\n');

%% ================= OPTIONAL SHORT TABLE =================
validBest = ~isnan(bestLoss_W);
ShortTable = Summary(validBest, {'Levels','Cells','Required_Device_V','Best_Device_V','Best_Parallel','Best_Loss_W','Best_Efficiency_pct','Best_Device'});
disp(ShortTable);

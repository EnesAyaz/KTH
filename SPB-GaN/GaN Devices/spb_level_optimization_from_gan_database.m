
%% SPB Level Number Optimization using FOM and Real GaN Devices
% Color/shape plots are optional. The key output is a table that selects
% the best available GaN device and parallel count for each number of SPB cells.
%
% Assumptions:
%   - m = number of series-stacked 2L three-phase cells/submodules.
%   - Approximate output voltage levels = m + 1.
%   - Each cell blocks Vdc/m; device rating must be >= kSafety*Vdc/m.
%   - Semiconductor loss model is a first-order comparative model:
%       Pcond = 3*m*Iphase_rms^2*(Rds_on/nParallel)
%       Psw   = 3*m*fsw*(Coss*nParallel)*(Vdc/m)^2
%   - Coss should ideally be replaced by Coss,Q at the actual cell voltage.
%     If the Excel table only has Coss, this script uses Coss as an approximation.
%
% Inputs:
%   GaN_device_database.xlsx with sheet GaN_Device_Table and columns:
%   Device, Vendor, Voltage_V, Current_A, RDSon_typ_mOhm, RDSon_max_mOhm, Coss_pF

clear; clc; close all;

%% User inputs
excelFile = "GaN_device_database.xlsx";
sheetName = "GaN_Device_Table";

Vdc = 1200;              % total DC-link voltage [V]
Pout = 30000;            % three-phase output power [W]
Iphase_peak = 320;       % nominal phase-current peak [A]
Iphase_rms = Iphase_peak/sqrt(2);
fsw = 100e3;            % device switching frequency [Hz]
kSafety = 1.5;          % voltage design factor, Vdevice >= kSafety*Vdc/m
maxCells = 10;          % number of series-stacked SPB cells to evaluate
maxParallel = 8;        % max parallel devices per switch position
overhead_W_per_cell = 1.5;  % simple implementation overhead for practical score [W/cell]

%% Read device table
T = readtable(excelFile, "Sheet", sheetName, "VariableNamingRule", "preserve");
T.Properties.VariableNames = matlab.lang.makeValidName(T.Properties.VariableNames);

% Robust resistance/capacitance choices
if ismember('RDSon_max_mOhm', T.Properties.VariableNames)
    Rds_mOhm = T.RDSon_max_mOhm;
else
    Rds_mOhm = NaN(height(T),1);
end
if ismember('RDSon_typ_mOhm', T.Properties.VariableNames)
    idx = isnan(Rds_mOhm);
    Rds_mOhm(idx) = T.RDSon_typ_mOhm(idx);
end

if ismember('Coss_pF', T.Properties.VariableNames)
    Coss_pF = T.Coss_pF;
else
    Coss_pF = NaN(height(T),1);
end
if ismember('Co_tr_pF', T.Properties.VariableNames)
    idx = isnan(Coss_pF);
    Coss_pF(idx) = T.Co_tr_pF(idx);
end
if ismember('Co_er_pF', T.Properties.VariableNames)
    idx = isnan(Coss_pF);
    Coss_pF(idx) = T.Co_er_pF(idx);
end

valid = ~isnan(T.Voltage_V) & ~isnan(Rds_mOhm) & ~isnan(Coss_pF);
T = T(valid,:);
Rds_mOhm = Rds_mOhm(valid);
Coss_pF = Coss_pF(valid);

% Remove any manual/test rows that are not real devices
if ismember('Vendor', T.Properties.VariableNames) && ismember('Device', T.Properties.VariableNames)
    testRows = contains(string(T.Vendor), {'Enes','Trial'}, 'IgnoreCase', true) | ...
               contains(string(T.Device), {'Enes','Trial'}, 'IgnoreCase', true);
    T = T(~testRows,:);
    Rds_mOhm = Rds_mOhm(~testRows);
    Coss_pF = Coss_pF(~testRows);
end

D_FOM = 1 ./ sqrt((Rds_mOhm*1e-3).*(Coss_pF*1e-12));
D_FOM_norm = D_FOM ./ max(D_FOM);

%% Brute-force real-device optimization
rows = [];
rowNames = {};
for m = 1:maxCells
    Vcell = Vdc/m;
    Vreq = kSafety*Vcell;

    for i = 1:height(T)
        if T.Voltage_V(i) < Vreq
            continue;
        end

        for nPar = 1:maxParallel
            currentOK = true;
            if ismember('Current_A', T.Properties.VariableNames) && ~isnan(T.Current_A(i))
                currentOK = (T.Current_A(i)*nPar >= Iphase_peak);
            end
            if ~currentOK
                continue;
            end

            R = (Rds_mOhm(i)*1e-3)/nPar;
            C = (Coss_pF(i)*1e-12)*nPar;
            Pcond = 3*m*(Iphase_rms^2)*R;
            Psw = 3*m*fsw*C*(Vcell^2);
            Psemi = Pcond + Psw;
            eff = 100*Pout/(Pout + Psemi);
            score = Psemi + overhead_W_per_cell*m;

            rows = [rows; m, m+1, Vcell, Vreq, T.Voltage_V(i), nPar, ...
                Rds_mOhm(i), Coss_pF(i), D_FOM_norm(i), Pcond, Psw, Psemi, eff, 6*m*nPar, 6*m, score]; %#ok<AGROW>
            rowNames{end+1,1} = string(T.Device(i)) + " | " + string(T.Vendor(i)); %#ok<SAGROW>
        end
    end
end

Opt = array2table(rows, 'VariableNames', {'Cells','Levels','Vcell_V','Required_Device_V','Device_V','Parallel','RDSon_mOhm','Coss_pF','D_FOM_norm','Pcond_W','Psw_W','Psemi_W','Efficiency_pct','Total_Switches','Gate_Drivers','Practical_Score_W'});
Opt.DeviceVendor = string(rowNames);
Opt = movevars(Opt, 'DeviceVendor', 'After', 'Levels');

%% Select best option for each number of cells
best = table();
bestScore = table();
for m = 1:maxCells
    sub = Opt(Opt.Cells == m,:);
    if isempty(sub)
        continue;
    end
    [~,idxLoss] = min(sub.Psemi_W);
    [~,idxScore] = min(sub.Practical_Score_W);
    best = [best; sub(idxLoss,:)]; %#ok<AGROW>
    bestScore = [bestScore; sub(idxScore,:)]; %#ok<AGROW>
end

fprintf('\nLoss-optimal real-device selection:\n');
disp(best(:, {'Cells','Levels','DeviceVendor','Required_Device_V','Device_V','Parallel','Psemi_W','Efficiency_pct','Total_Switches'}));

%% FOM-based ideal scaling intuition
m = (1:maxCells).';
levels = m + 1;
Vreq = kSafety*Vdc./m;
alpha_D_GaN = -0.2;       % from X-FOM paper: GaN D-FOM voltage scaling is relatively flat
Dideal = (Vreq/650).^alpha_D_GaN;
complexity = m;
FOM_per_complexity = Dideal./complexity;

%% Plots
figure('Color','w','Position',[100 100 1200 750]);
tiledlayout(2,2,'TileSpacing','compact','Padding','compact');

nexttile;
scatter(Coss_pF, Rds_mOhm, 60, T.Voltage_V, 'filled');
set(gca,'XScale','log','YScale','log'); grid on; box on;
xlabel('C_{oss} used (pF)'); ylabel('R_{DS(on)} used (m\Omega)');
title('GaN device database'); cb=colorbar; cb.Label.String='Voltage rating (V)';

nexttile;
scatter(T.Voltage_V, D_FOM_norm, 60, D_FOM_norm, 'filled');
set(gca,'XScale','log','YScale','log'); grid on; box on;
xlabel('Device voltage rating (V)'); ylabel('Normalized D-FOM');
title('Device FOM = 1/sqrt(R_{DS(on)} C_{oss})');

nexttile;
yyaxis left;
plot(levels, Vreq, 'o-', 'LineWidth', 1.5); ylabel('Required device rating (V)');
yyaxis right;
plot(levels, Dideal, 's--', levels, FOM_per_complexity, '^:', 'LineWidth', 1.5);
ylabel('Normalized index'); grid on; box on;
xlabel('SPB voltage levels \approx cells + 1');
title('FOM scaling vs. level number');
legend('Required rating','Ideal GaN D-FOM','D-FOM / cell count','Location','best');

nexttile;
yyaxis left;
plot(best.Levels, best.Psemi_W, 'o-', 'LineWidth', 1.5); hold on;
plot(bestScore.Levels, bestScore.Practical_Score_W, 's--', 'LineWidth', 1.5);
ylabel('Estimated semiconductor loss / score (W)');
yyaxis right;
plot(best.Levels, best.Efficiency_pct, '^-', 'LineWidth', 1.5);
ylabel('Efficiency (%)'); grid on; box on;
xlabel('SPB voltage levels \approx cells + 1');
title('Real-device optimization');
legend('Best loss','Loss + overhead','Efficiency','Location','best');

exportgraphics(gcf, 'SPB_FOM_real_device_optimization.png', 'Resolution', 300);
writetable(best, 'SPB_best_real_device_selection.csv');
writetable(Opt, 'SPB_all_candidate_results.csv');

%% SPB Level Number Optimization using FOM and Real GaN Devices
% Updated for Enes' system: Vdc = 1200 V, Pout = 300 kW.
%
% The script reads an Excel GaN device database and sweeps:
%   - number of series-stacked SPB cells m
%   - device choice from the database
%   - number of parallel devices per switch position
%
% Outputs:
%   spb_1200V_300kW_best_by_loss.csv
%   spb_1200V_300kW_best_by_practical_score.csv
%   SPB_1200V_300kW_optimization.png
%
% Model limitations:
%   - Coss is used as an approximation of Coss,Q if Coss,Q is unavailable.
%   - Eon/Eoff, dynamic RDS(on), thermal impedance, layout parasitics, DC-link ripple,
%     balancing dynamics, and machine harmonic losses are not yet included.

clear; clc; close all;

%% Input files
excelFile = "GaN_device_database_added_120_150_175V.xlsx";
if ~isfile(excelFile)
    excelFile = "GaN_device_database.xlsx";
end
sheetName = "GaN_Device_Table";

%% System inputs
Vdc = 1200;              % total DC-link voltage [V]
Pout = 300e3;            % three-phase output power [W]
pf = 0.90;               % assumed power factor
modIndex = 0.90;         % assumed fundamental modulation index
fsw = 20e3;              % device switching frequency [Hz]
kSafety = 1.5;           % Vdevice >= kSafety*Vdc/m
maxCells = 12;           % number of series-stacked SPB cells to evaluate
maxParallel = 8;        % maximum parallel devices per switch position
overhead_W_per_cell = 80;  % simple practical penalty [W/cell]
componentPenalty_W = 0.4;  % small penalty per discrete device [W-equivalent]

%% Derived current
Vphase_peak = modIndex*Vdc/2;
Vphase_rms = Vphase_peak/sqrt(2);
VLL_rms = sqrt(3)*Vphase_rms;
Iphase_rms = Pout/(sqrt(3)*VLL_rms*pf);
Iphase_peak = sqrt(2)*Iphase_rms;

fprintf('System: %.0f V DC, %.0f kW, pf = %.2f, modulation = %.2f\n', Vdc, Pout/1e3, pf, modIndex);
fprintf('Estimated VLL,rms = %.1f V, Iphase,rms = %.1f A, Iphase,peak = %.1f A\n', VLL_rms, Iphase_rms, Iphase_peak);

%% Read device table
T = readtable(excelFile, "Sheet", sheetName, "VariableNamingRule", "preserve");
T.Properties.VariableNames = matlab.lang.makeValidName(T.Properties.VariableNames);

% Remove test rows
if ismember('Device', T.Properties.VariableNames)
    T = T(~contains(string(T.Device), ["Trial","Enes"], 'IgnoreCase', true), :);
end
if ismember('Vendor', T.Properties.VariableNames)
    T = T(~contains(string(T.Vendor), ["Trial","Enes"], 'IgnoreCase', true), :);
end

% Select RDS(on): max preferred, typ if max is missing
Rds_mOhm = NaN(height(T),1);
if ismember('RDSon_max_mOhm', T.Properties.VariableNames)
    Rds_mOhm = T.RDSon_max_mOhm;
end
if ismember('RDSon_typ_mOhm', T.Properties.VariableNames)
    idx = isnan(Rds_mOhm);
    Rds_mOhm(idx) = T.RDSon_typ_mOhm(idx);
end

% Select Coss: Coss preferred, then Co_tr, then Co_er
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

valid = ~isnan(T.Voltage_V) & ~isnan(Rds_mOhm) & ~isnan(Coss_pF);
T = T(valid,:);
Rds_mOhm = Rds_mOhm(valid);
Coss_pF = Coss_pF(valid);

D_FOM = 1 ./ sqrt((Rds_mOhm*1e-3).*(Coss_pF*1e-12));
D_FOM_norm = D_FOM ./ max(D_FOM);

%% Sweep cells, devices, and parallel count
rows = [];
rowNames = strings(0,1);
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
            totalDevices = 6*m*nPar;
            score = Psemi + overhead_W_per_cell*m + componentPenalty_W*totalDevices;

            rows = [rows; m, m+1, Vcell, Vreq, T.Voltage_V(i), nPar, ...
                Rds_mOhm(i), Coss_pF(i), D_FOM_norm(i), Pcond, Psw, Psemi, eff, 6*m, totalDevices, score]; %#ok<AGROW>
            rowNames(end+1,1) = string(T.Device(i)) + " | " + string(T.Vendor(i)); %#ok<SAGROW>
        end
    end
end

Opt = array2table(rows, 'VariableNames', {'Cells','Levels','Vcell_V','Required_Device_V','Device_V','Parallel','RDSon_mOhm','Coss_pF','D_FOM_norm','Pcond_W','Psw_W','Psemi_W','Efficiency_pct','Gate_Drivers','Total_Devices','Practical_Score_W'});
Opt.DeviceVendor = rowNames;
Opt = movevars(Opt, 'DeviceVendor', 'After', 'Levels');

%% Select best option for each cell count
bestLoss = table();
bestScore = table();
for m = 1:maxCells
    sub = Opt(Opt.Cells == m,:);
    if isempty(sub)
        continue;
    end
    [~,idxLoss] = min(sub.Psemi_W);
    [~,idxScore] = min(sub.Practical_Score_W);
    bestLoss = [bestLoss; sub(idxLoss,:)]; %#ok<AGROW>
    bestScore = [bestScore; sub(idxScore,:)]; %#ok<AGROW>
end

disp('Loss-optimal real-device selection:');
disp(bestLoss(:, {'Cells','Levels','DeviceVendor','Required_Device_V','Device_V','Parallel','Psemi_W','Efficiency_pct','Total_Devices'}));

disp('Practical-score-optimal real-device selection:');
disp(bestScore(:, {'Cells','Levels','DeviceVendor','Required_Device_V','Device_V','Parallel','Practical_Score_W','Psemi_W','Efficiency_pct','Total_Devices'}));

writetable(Opt, 'spb_1200V_300kW_all_candidate_results.csv');
writetable(bestLoss, 'spb_1200V_300kW_best_by_loss.csv');
writetable(bestScore, 'spb_1200V_300kW_best_by_practical_score.csv');

%% Plots
figure('Color','w','Position',[100 100 1250 780]);
tiledlayout(2,2,'TileSpacing','compact','Padding','compact');

nexttile;
plot(bestLoss.Levels, bestLoss.Psemi_W/1000, 'o-', 'LineWidth', 1.5); hold on;
plot(bestScore.Levels, bestScore.Practical_Score_W/1000, 's--', 'LineWidth', 1.5);
grid on; box on;
xlabel('Approx. SPB voltage levels = cells + 1');
ylabel('Loss / score (kW)');
title('Real-device level optimization');
legend('Best semiconductor loss','Loss + practical penalty','Location','best');

nexttile;
bar(bestLoss.Levels, [bestLoss.Pcond_W bestLoss.Psw_W]/1000, 'stacked');
grid on; box on;
xlabel('Approx. SPB voltage levels = cells + 1');
ylabel('Semiconductor loss (kW)');
title('Loss breakdown');
legend('Conduction','Coss switching','Location','best');

nexttile;
plot(bestLoss.Levels, bestLoss.Required_Device_V, 'o-', 'LineWidth', 1.5); hold on;
yline(650,'--','650 V'); yline(350,'--','350 V'); yline(200,'--','200 V'); yline(150,'--','150 V');
grid on; box on;
xlabel('Approx. SPB voltage levels = cells + 1');
ylabel('Required device rating (V)');
title('Voltage requirement per cell');

nexttile;
scatter(T.Voltage_V, D_FOM_norm, 60, D_FOM_norm, 'filled');
set(gca,'XScale','log','YScale','log'); grid on; box on;
xlabel('Device voltage rating (V)');
ylabel('Normalized D-FOM');
title('Database device FOM');
cb = colorbar; cb.Label.String = 'D-FOM norm.';

exportgraphics(gcf, 'SPB_1200V_300kW_optimization.png', 'Resolution', 300);
fprintf('Saved CSV files and SPB_1200V_300kW_optimization.png\n');

%% SAVE RESULTS WITH AUTO-INCREMENTED FILENAME
outFolder = 'C:\Github\KTH\Prototyping\Colorimetric';
baseName  = 'steady_state_calo_roundedIF_';
ext       = '.xlsx';
n=3;
outFile = fullfile(outFolder, [baseName, num2str(n), ext]);

%% ========================================================================
%  PART 2: READ SUMMARY EXCEL, BUILD ARRAYS, AND PLOT
% ====================================================================== %%

% Use the file we just saved:
fname_summary = outFile;

Tsum = readtable(fname_summary);

% Column vectors

I_set   = Tsum.I_set_A;
f_sw    = Tsum.f_sw_kHz;
P_cal   = Tsum.P_cal_ss_W;
T_in_ss = Tsum.T_in_ss_degC;
T_out_ss= Tsum.T_out_ss_degC;

% === EXCLUDE specific switching frequencies ===
exclude_f = [10];      % <-- change to whatever you want to skip
keep_idx = ~ismember(f_sw, exclude_f);

I_set   = I_set(keep_idx);
f_sw    = f_sw(keep_idx);
P_cal   = P_cal(keep_idx);
T_in_ss = T_in_ss(keep_idx);
T_out_ss= T_out_ss(keep_idx);

% Unique sorted levels
I_vals = unique(I_set);
f_vals = unique(f_sw);

% Build matrix
P_mat = nan(numel(I_vals), numel(f_vals));
for n = 1:numel(P_cal)
    i_idx = find(I_vals == I_set(n));
    f_idx = find(f_vals == f_sw(n));
    P_mat(i_idx, f_idx) = P_cal(n);
end

%% Plot 1: P_cal vs Current for each frequency
figure; hold on; grid on;
for j = 1:numel(f_vals)
    plot(I_vals, P_mat(:,j), '-o', 'LineWidth', 2, ...
        'DisplayName', sprintf('%d kHz', f_vals(j)));
end
xlabel('Current [A]');
ylabel('Calorimetric loss P_{cal} [W]');
title('Calorimetric Power vs Current for Different Switching Frequencies');
legend('Location','northwest');

%% Plot 2: P_cal vs Frequency for each Current level
figure; hold on; grid on;
for i = 1:numel(I_vals)
    plot(f_vals, P_mat(i,:), '-o', 'LineWidth', 2, ...
        'DisplayName', sprintf('%d A', I_vals(i)));
end
xlabel('Switching Frequency [kHz]');
ylabel('Calorimetric Loss P_{cal} [W]');
title('Calorimetric Loss vs Switching Frequency for Different Currents');
legend('Location', 'northwest');

%% Plot 3: 3D surface P(I,f)
[I_grid, F_grid] = meshgrid(I_vals, f_vals);   % size: nF x nI
P_grid = P_mat.';                              % transpose to match

figure;
surf(I_grid, F_grid, P_grid);
shading interp;
colorbar;
xlabel('Current [A]');
ylabel('Switching Frequency [kHz]');
zlabel('Calorimetric Loss P_{cal} [W]');
title('Calorimetric Loss Surface');

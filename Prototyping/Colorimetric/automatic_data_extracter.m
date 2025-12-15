%% SETTINGS
baseFolder = 'C:\Users\enesa\KTH\Shahriar Sarmast Ghahfarokhi - Calorimetric results\8Dec';
filePattern = '*.xlsx';

fc  = 0.02;                  % low-pass cutoff [Hz]
rho = 1000;                  % kg/m^3, water
cp  = 4180;                  % J/(kg*K), water

% Discrete levels for rounding
I_levels   = [0 50 100 150 200];   % A
f_levels_k = [7 10 11 15 19];         % kHz

%% LIST FILES
files   = dir(fullfile(baseFolder, filePattern));
nFiles  = numel(files);

results = table('Size',[nFiles 6], ...
    'VariableTypes', {'string','double','double','double','double','double'}, ...
    'VariableNames', {'File','I_set_A','f_sw_kHz', ...
                      'P_cal_ss_W','T_in_ss_degC','T_out_ss_degC'});

%% LOOP OVER FILES
for k = 1:nFiles
    fname = files(k).name;
    fpath = fullfile(baseFolder, fname);
    fprintf('Processing %s\n', fname);

    %% Load data
    opts = detectImportOptions(fpath);
    opts = setvartype(opts, 1, 'datetime');
    opts = setvaropts(opts, 1, 'InputFormat', 'yyyy-MM-dd HH:mm:ss');
    T = readtable(fpath, opts);

    % Time
    time_dt = T{:,1};
    t  = seconds(time_dt - time_dt(1));
    dt = mean(diff(t));
    fs = 1/dt;

    % Numeric data: columns 2..10
    A = T{:, 2:10};

    P_loss_el   = A(:,1); %#ok<NASGU>
    T_in_raw    = A(:,2);
    T_out_raw   = A(:,3);
    flow_raw    = A(:,4);
    I_rms_vec   = A(:,5);  % RMS current
    V_dc        = A(:,6); %#ok<NASGU>
    dT_col_raw  = A(:,7); %#ok<NASGU>
    P_loss_tot  = A(:,8); %#ok<NASGU>
    f_sw_vec    = A(:,9);  % switching frequency

    %% Filtering
    Wn = fc/(fs/2);
    [b,a] = butter(2, Wn, 'low');

    T_in  = filtfilt(b,a,T_in_raw);
    T_out = filtfilt(b,a,T_out_raw);
    flow  = filtfilt(b,a,flow_raw);

    dT = T_out - T_in;

    %% Calorimetric loss
    m_dot = flow * 1e-3 / 60 * rho;     % [kg/s]
    P_cal = m_dot .* cp .* dT;          % [W]

    %% Steady state: last 10 %
    N = numel(t);
    idx_ss = max(1, round(0.9*N)) : N;

    P_cal_ss = mean(P_cal(idx_ss));          % filtered steady-state calorimetric loss
    T_in_ss  = mean(T_in(idx_ss));
    T_out_ss = mean(T_out(idx_ss));

    I_rms_ss   = mean(I_rms_vec(idx_ss));    % average RMS current
    f_sw_ss_Hz = mean(f_sw_vec(idx_ss));     % average switching frequency

    % Convert frequency to kHz if needed
    if f_sw_ss_Hz > 100          % assume this means Hz
        f_sw_ss_kHz = f_sw_ss_Hz / 1000;
    else                         % already in kHz
        f_sw_ss_kHz = f_sw_ss_Hz;
    end

    %% Quantize current and frequency to specified discrete levels
    [~, idxI] = min(abs(I_rms_ss   - I_levels));
    I_set     = I_levels(idxI);

    [~, idxF] = min(abs(f_sw_ss_kHz - f_levels_k));
    f_set_kHz = f_levels_k(idxF);

    %% Store in result table
    results(k,:) = {string(fname), I_set, f_set_kHz, ...
                    P_cal_ss, T_in_ss, T_out_ss};
end


%% Optional: sort rows
results = sortrows(results, {'I_set_A','f_sw_kHz'});

%% ==== AUTO-INCREMENT OUTPUT FILE NAME ====
outFolder = 'C:\Github\KTH\Prototyping\Colorimetric';
baseName  = 'steady_state_calo_roundedIF_';
ext       = '.xlsx';

existingFiles = dir(fullfile(outFolder, [baseName, '*.xlsx']));

if isempty(existingFiles)
    nextIndex = 1;
else
    nums = zeros(numel(existingFiles),1);
    for ii = 1:numel(existingFiles)
        nTok = regexp(existingFiles(ii).name, [baseName '(\d+)\.xlsx'], 'tokens','once');
        if ~isempty(nTok)
            nums(ii) = str2double(nTok{1});
        end
    end
    nextIndex = max(nums) + 1;
end

outFile = fullfile(outFolder, sprintf('%s%d%s', baseName, nextIndex, ext));

%% SAVE RESULTS
writetable(results, outFile);
fprintf('Saved rounded steady-state results to %s\n', outFile);


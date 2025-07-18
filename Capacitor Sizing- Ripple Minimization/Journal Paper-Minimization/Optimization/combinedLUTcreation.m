% === USER PARAMETERS ===
step_current = 0.1;   % For ib, ic
step_duty    = 0.1;   % For db, dc

% === DISCRETIZED LUT RANGES ===
ib_vals = -0.5 : step_current : 0.5;
ic_vals = -0.5 : step_current : 0.5;
db_vals =  0   : step_duty    : 1;
dc_vals =  0   : step_duty    : 1;

len_ib = length(ib_vals);
len_ic = length(ic_vals);
len_db = length(db_vals);
len_dc = length(dc_vals);

% === PREALLOCATE LUT ===
LUT_theta_b      = NaN(len_ib, len_ic, len_db, len_dc);
LUT_theta_c      = NaN(len_ib, len_ic, len_db, len_dc);
LUT_rms_opt      = NaN(len_ib, len_ic, len_db, len_dc);
LUT_rms_noshift  = NaN(len_ib, len_ic, len_db, len_dc);

% === GENERATE INPUTS BASED ON PHYSICAL MODEL ===
theta_vals = deg2rad(0:25:359);        % electrical angle [rad]
phi_vals   = deg2rad(-75:25:75);       % power factor angle [rad]
ma_vals    = 0:0.2:1.0;              % modulation index

% === PROGRESS TRACKING ===
total_cases = length(ma_vals) * length(phi_vals) * length(theta_vals);
completed_cases = 0;
tic;  % start timer

% === START GENERATION ===
for ma = ma_vals
    for phi = phi_vals
        for theta = theta_vals
            % Calculate phase angles
            theta_b = theta - 2*pi/3;
            theta_c = theta - 4*pi/3;

            % Duty cycles (SPWM)
            db = 0.5 + (ma/2)*sin(theta_b);
            dc = 0.5 + (ma/2)*sin(theta_c);

            % Phase currents
            ia = sin(theta);
            ib = sin(theta_b - phi);
            ic = sin(theta_c - phi);

            % Normalize currents (sum of abs to simulate constant load current)
            scale = abs(ia) + abs(ib) + abs(ic);
            ib = ib / scale;
            ic = ic / scale;

            % Quantize to grid indices
            [~, i_ib] = min(abs(ib_vals - ib));
            [~, i_ic] = min(abs(ic_vals - ic));
            [~, i_db] = min(abs(db_vals - db));
            [~, i_dc] = min(abs(dc_vals - dc));

            % Skip if already filled (optional: average multiple samples)
            if ~isnan(LUT_theta_b(i_ib, i_ic, i_db, i_dc))
                continue;
            end

            % Check valid da
            da = 3/2 - db - dc;
            if da < 0 || da > 1
                continue;
            end

            % Compute and store results
            rms_no = calculate_rms_no_shift(ib, ic, db, dc);
            [theta_b_opt, theta_c_opt, rms_opt] = optimize_interleaving_rms(ib, ic, db, dc);

            LUT_theta_b(i_ib, i_ic, i_db, i_dc)     = theta_b_opt;
            LUT_theta_c(i_ib, i_ic, i_db, i_dc)     = theta_c_opt;
            LUT_rms_opt(i_ib, i_ic, i_db, i_dc)     = rms_opt;
            LUT_rms_noshift(i_ib, i_ic, i_db, i_dc) = rms_no;

            % Progress tracking
            completed_cases = completed_cases + 1;
            if mod(completed_cases, 10) == 0
                elapsed = toc;
                avg_time = elapsed / completed_cases;
                remaining = avg_time * (total_cases - completed_cases);
                fprintf('[%d/%d] ma=%.2f, φ=%.1f°, θ=%.1f° → Remaining: %.1f min\n', ...
                    completed_cases, total_cases, ...
                    ma, rad2deg(phi), rad2deg(theta), remaining/60);
            end
        end
    end
end

% === SAVE TO FILE ===
save('LUT_PhysicalInputs_AdaptiveInterleaving.mat', ...
     'ib_vals','ic_vals','db_vals','dc_vals', ...
     'LUT_theta_b','LUT_theta_c','LUT_rms_opt','LUT_rms_noshift', ...
     'step_current','step_duty', '-v7.3');

fprintf('✅ LUT generation complete! Total time: %.1f minutes\n', toc/60);

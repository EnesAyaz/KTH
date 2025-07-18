% === PARAMETER SETTINGS ===
step_current = 0.1;   % Precision for ib, ic
step_duty    = 0.1;   % Precision for db, dc

% === DEFINE RANGES BASED ON PRECISION ===
ib_vals = -0.5 : step_current : 0.5;
ic_vals = -0.5 : step_current : 0.5;
db_vals =  0   : step_duty    : 1;
dc_vals =  0   : step_duty    : 1;

% === CALCULATE LENGTHS ===
len_ib = length(ib_vals);
len_ic = length(ic_vals);
len_db = length(db_vals);
len_dc = length(dc_vals);

% === PREALLOCATE LUTs ===
LUT_theta_b      = NaN(len_ib, len_ic, len_db, len_dc);
LUT_theta_c      = NaN(len_ib, len_ic, len_db, len_dc);
LUT_rms_opt      = NaN(len_ib, len_ic, len_db, len_dc);
LUT_rms_noshift  = NaN(len_ib, len_ic, len_db, len_dc);
% Start loop
for i_ib = 1:length(ib_vals)
    ib = ib_vals(i_ib);
    for i_ic = 1:length(ic_vals)
        ic = ic_vals(i_ic);
        for i_db = 1:length(db_vals)
            db = db_vals(i_db);
            for i_dc = 1:length(dc_vals)
                dc = dc_vals(i_dc);

                % Skip invalid da
                da = 3/2 - db - dc;
                if da < 0 || da > 1
                    continue;
                end
                % Compute RMS with no phase shift
                rms_noshift = calculate_rms_no_shift(ib, ic, db, dc);

                % Compute optimal angles and minimum RMS
                [theta_b, theta_c, rms_opt] = optimize_interleaving_rms(ib, ic, db, dc);

                % Store in LUTs
                LUT_theta_b(i_ib,i_ic,i_db,i_dc) = theta_b;
                LUT_theta_c(i_ib,i_ic,i_db,i_dc) = theta_c;
                LUT_rms_opt(i_ib,i_ic,i_db,i_dc) = rms_opt;
                LUT_rms_noshift(i_ib,i_ic,i_db,i_dc) = rms_noshift;
            end
        end
    end
end

% Save LUT
save('LUT_AdaptiveInterleaving.mat', ...
     'ib_vals','ic_vals','db_vals','dc_vals', ...
     'LUT_theta_b','LUT_theta_c','LUT_rms_opt','LUT_rms_noshift', '-v7.3');

function [theta_b_opt, theta_c_opt, min_rms] = optimize_interleaving_rms(ib, ic, db, dc)

    % Calculate ia and da based on balance assumption
    ia = -ib - ic;
    da = 3/2 - db - dc;

    % Check for valid duty cycle
    if da < 0 || da > 1
        error('Invalid da = 3/2 - db - dc. It must be within [0,1].');
    end

    % Simulation parameters
    fsw = 10e3;
    Ts = 1/fsw;
    N = 1000;
    t = linspace(0, Ts, N);

    % Reference triangular carrier for phase A
    carrier = sawtooth(2*pi*fsw*t, 0.5);  % symmetric triangle [-1,1]

    % Initialize results
    min_rms = Inf;
    theta_b_opt = 0;
    theta_c_opt = 0;

    % Search over all combinations of θ_b and θ_c
    for theta_b = 0:5:360
    for theta_c = 0:5:360

            % Convert angle to carrier time shift
            shift_b = mod(theta_b / 360, 1) * Ts;
            shift_c = mod(theta_c / 360, 1) * Ts;

            % Create phase-shifted carriers
            carrier_b = sawtooth(2*pi*fsw*(t - shift_b), 0.5);
            carrier_c = sawtooth(2*pi*fsw*(t - shift_c), 0.5);

            % Switching functions
            sa = 2*da-1 >= carrier;
            sb = 2*db-1 >= carrier_b;
            sc = 2*dc-1 >= carrier_c;

            % DC-link current: sum of absolute leg currents
            idc = sa.* ia + sb.* ib +sc .* ic-mean(sa.* ia + sb.* ib +sc .* ic);
            rms_val = sqrt(mean(idc.^2));

            if rms_val < min_rms
                min_rms = rms_val;
                theta_b_opt = theta_b;
                theta_c_opt = theta_c;
            end
        end
    end
end

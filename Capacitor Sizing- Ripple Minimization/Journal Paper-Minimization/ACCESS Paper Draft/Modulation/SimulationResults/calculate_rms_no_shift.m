function rms_val = calculate_rms_no_shift(ib, ic, db, dc)

    % Calculate ia and da assuming current and duty balance
    ia = -ib - ic;
    da = 3/2 - db - dc;

    % Check valid da
    if da < 0 || da > 1
        error('Invalid da = 1 - db - dc. It must be within [0,1].');
    end

    % Simulation parameters
    fsw = 10e3;
    Ts = 1/fsw;
    N = 1000;
    t = linspace(0, Ts, N);

    % Common (non-shifted) carrier
    carrier = sawtooth(2*pi*fsw*t, 0.5);  % centered triangular wave

    % Switching functions (no phase shifts)
    sa = 2*da-1 >= (carrier);
    sb = 2*db-1 >= (carrier);
    sc = 2*dc-1 >= (carrier);

    % DC-link current
    idc = sa.* ia + sb.* ib +sc .* ic-mean(sa.* ia + sb.* ib +sc .* ic);

    % RMS value
    rms_val = sqrt(mean(idc.^2));
end

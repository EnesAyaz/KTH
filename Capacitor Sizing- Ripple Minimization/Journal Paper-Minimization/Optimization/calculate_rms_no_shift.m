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
    sa = da >= (carrier + 0.5);
    sb = db >= (carrier + 0.5);
    sc = dc >= (carrier + 0.5);

    % DC-link current
    idc = abs(sa .* ia) + abs(sb .* ib) + abs(sc .* ic);

    % RMS value
    rms_val = sqrt(mean(idc.^2));
end

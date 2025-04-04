% System Parameters
Vdc = 1250;         % DC link voltage (V)
L = 500e-6;         % Inductance between inverters (H)
Imax = 360;         % Maximum current limit (A)
M2_max = 0.8;       % Maximum M2 allowed
delta_max = 90;     % Maximum phase shift allowed (degrees)

% EV Inverter Parameters
M1_range = linspace(0.1, 1.15, 50);  % Modulation index range
f_base = 50;                         % Base frequency (Hz)
f_max = 500;                         % Maximum frequency (Hz at M1=1.15)

% Initialize storage
optimal_M2 = nan(size(M1_range));
optimal_delta = nan(size(M1_range));
achieved_I = nan(size(M1_range));
achieved_freq = nan(size(M1_range));

for i = 1:length(M1_range)
    M1 = M1_range(i);
    
    % Calculate frequency (proportional to M1)
    freq = f_base + (f_max - f_base)*(M1/1.15);
    omega = 2*pi*freq;
    achieved_freq(i) = freq;
    
    % Grid search for M2 and delta that give Imax
    for M2 = linspace(0, M2_max, 100)
        for delta = linspace(0, delta_max, 100)
            % Calculate current magnitude
            I = (Vdc/2)*sqrt(M1^2 + M2^2 - 2*M1*M2*cosd(delta))/(omega*L);
            
            % Check if current matches Imax within 0.1% tolerance
            if abs(I - Imax) < Imax*0.001
                optimal_M2(i) = M2;
                optimal_delta(i) = delta;
                achieved_I(i) = I;
                break; % Take first solution found
            end
        end
        if ~isnan(optimal_M2(i)) % Solution found
            break;
        end
    end
end

%%
plot(optimal_delta)
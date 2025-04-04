Udc = 1250;
L = 100e-6;
omega = 2*pi*500;
I_max_limit = 360;

% Define ranges
M1_range = linspace(0, 1.15, 100);
M2_range = linspace(0, 1.15, 100);
delta_range = linspace(0, 180, 180); % Full range of possible delta values

% Initialize storage
optimal_M2 = zeros(size(M1_range));
optimal_delta = zeros(size(M1_range));

for i = 1:length(M1_range)
    M1 = M1_range(i);
    min_delta_found = inf; % Initialize with large value
    best_M2 = 0;
    
    % Search through M2 and delta combinations
    for M2 = M2_range
        for delta = delta_range
            % Calculate current
            I_max = (Udc/4)*sqrt(M1^2 + M2^2 - 2*M1*M2*cosd(delta))/(omega*L);
            
            % Check if current is within limit and delta is smaller than previous found
            if I_max <= I_max_limit && delta < min_delta_found
                min_delta_found = delta;
                best_M2 = M2;
            end
        end
    end
    
    % Store results if valid solution found
    if isfinite(min_delta_found)
        optimal_M2(i) = best_M2;
        optimal_delta(i) = min_delta_found;
    else
        optimal_M2(i) = NaN;
        optimal_delta(i) = NaN;
    end
end

% Plot results
figure;
subplot(2,1,1);
plot(M1_range, optimal_M2, 'LineWidth', 2);
xlabel('M1', 'FontSize', 12);
ylabel('Optimal M2', 'FontSize', 12);
title('Optimal M2 for Minimum Delta (I_{max} ≤ 360A)', 'FontSize', 12);
grid on;

subplot(2,1,2);
plot(M1_range, optimal_delta, 'LineWidth', 2);
xlabel('M1', 'FontSize', 12);
ylabel('Optimal Delta (degrees)', 'FontSize', 12);
title('Minimum Delta Values (I_{max} ≤ 360A)', 'FontSize', 12);
grid on;

% Create a table of results for M1 values that have solutions
valid_indices = ~isnan(optimal_delta);
results = table(M1_range(valid_indices)', optimal_M2(valid_indices)', optimal_delta(valid_indices)', ...
    'VariableNames', {'M1', 'Optimal_M2', 'Minimum_Delta'});
disp(results);
% System Parameters
Vdc = 1250;         % DC link voltage (V)
L = 200e-6;         % Inductance (H)
Imax = 360;         % Target current (A)
M2_max = 1.1;       % Maximum M2 allowed

% Operating Ranges
M1_range = linspace(0.1, 1.15, 50);  % EV inverter modulation index
M2_range = linspace(0.1, M2_max, 50); % Load inverter modulation index
f_base = 50;                         % Base frequency (Hz)
f_max = 500;                         % Max frequency (Hz at M1=1.15)

% Initialize delta matrix
delta_map = nan(length(M1_range), length(M2_range));
frequencies = zeros(length(M1_range), 1);
pf_map = nan(length(M1_range), length(M2_range));

for i = 1:length(M1_range)
    M1 = M1_range(i);
    
    % Calculate frequency (proportional to M1)
    frequencies(i) = f_base + (f_max - f_base)*(M1/1.15);
    omega = 2*pi*frequencies(i);
    
    for j = 1:length(M2_range)
        M2 = M2_range(j);
        
        % Solve for delta that gives exactly Imax
        % Rearrange current equation to solve for delta:
        cos_delta = (M1^2 + M2^2 - (2*omega*L*Imax/Vdc)^2)/(2*M1*M2);
        
        % Check if solution exists (|cos_delta| <= 1)
        if abs(cos_delta) <= 1
            delta_map(i,j) = acosd(cos_delta);

            % Calculate power factor for M1 (voltage source)
            V1_phasor = (Vdc/2)*M1;
            V2_phasor = (Vdc/2)*M2*exp(1i*deg2rad(acosd(cos_delta)));
            I_phasor = (V1_phasor - V2_phasor)/(1i*omega*L);
            
            % Power factor = cos(θ_v - θ_i)
            pf_map(i,j) = -cos(angle(V1_phasor) -angle(I_phasor));

        else
            delta_map(i,j) = nan; % No solution
            pf_map(i,j)=nan;
        end
    end
end

% Create meshgrid for plotting
[M1_grid, M2_grid] = meshgrid(M1_range, M2_range);
%%
% Plot delta surface
figure;
contourf(M1_grid, M2_grid, delta_map', 'EdgeColor', 'none');
xlabel('M1 (EV Modulation Index)');
ylabel('M2 (Load Modulation Index)');
% zlabel('Phase Shift \delta (degrees)');
title(sprintf('Phase Shift (δ) Required for %dA Current', Imax));
colorbar;
colormap jet;
hold on;
%%
% Highlight the M2=0.8 boundary
[M1_boundary, M2_boundary] = meshgrid(M1_range, M2_max);
delta_boundary = interp2(M1_grid, M2_grid, delta_map', M1_boundary, M2_boundary);
plot3(M1_boundary(:), M2_boundary(:), delta_boundary(:), 'r-', 'LineWidth', 2);

% Add text annotation
text(min(M1_range), M2_max, ...
    sprintf('White regions:\nNo solution exists\nfor %dA', Imax), ...
    'FontSize', 10, ...
    'BackgroundColor', 'none', ...
    'HorizontalAlignment', 'left', ...
    'VerticalAlignment', 'top');


% Plot 2D slices at specific M2 values
figure;
hold on;
colors = lines(5);
M2_slices = [0.2 0.4 0.6 0.8 1];
for k = 1:length(M2_slices)
    [~, idx] = min(abs(M2_range - M2_slices(k)));
    plot(M1_range, delta_map(:,idx), 'LineWidth', 2, 'Color', colors(k,:));
end
xlabel('M1 (EV Modulation Index)');
ylabel('Phase Shift \delta (degrees)');
title('Phase Shift vs M1 for Fixed M2 Values');
grid on;
legend(cellstr(num2str(M2_slices', 'M2=%.1f')), 'Location', 'best');
ylim([0 90]);

% Plot frequency profile (for reference)
figure;
plot(M1_range, frequencies, 'LineWidth', 2);
xlabel('M1 (EV Modulation Index)');
ylabel('Frequency (Hz)');
title('Operating Frequency vs M1');
grid on;

%%

%%
% Plot delta surface
figure;
contourf(M1_grid, M2_grid, pf_map', 'EdgeColor', 'none');
xlabel('M1 (EV Modulation Index)');
ylabel('M2 (Load Modulation Index)');
% zlabel('Phase Shift \delta (degrees)');
title(sprintf('Power Factor Required for %dA Current', Imax));
colorbar;
colormap jet;
hold on;
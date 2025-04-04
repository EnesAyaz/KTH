% System Parameters
Vdc = 1250;         % DC link voltage (V)
L = 500e-6;         % Inductance (H)
Imax = 360;         % Target current (A)
M2_max = 0.8;       % Maximum M2 allowed

% Operating Ranges
M1_range = linspace(0.1, 1.15, 50);  % EV inverter modulation index
M2_range = linspace(0.1, M2_max, 50); % Load inverter modulation index
f_base = 50;                         % Base frequency (Hz)
f_max = 500;                         % Max frequency (Hz at M1=1.15)

% Initialize matrices
delta_map = nan(length(M1_range), length(M2_range));
pf_map = nan(length(M1_range), length(M2_range));
frequencies = zeros(length(M1_range), 1);

for i = 1:length(M1_range)
    M1 = M1_range(i);
    
    % Calculate frequency (proportional to M1)
    frequencies(i) = f_base + (f_max - f_base)*(M1/1.15);
    omega = 2*pi*frequencies(i);
    
    for j = 1:length(M2_range)
        M2 = M2_range(j);
        
        % Solve for delta that gives exactly Imax
        cos_delta = (M1^2 + M2^2 - (2*omega*L*Imax/Vdc)^2)/(2*M1*M2);
        
        if abs(cos_delta) <= 1
            delta = acosd(cos_delta);
            delta_map(i,j) = delta;
            
            % Calculate power factor for M1 (voltage source)
            V1_phasor = (Vdc/2)*M1;
            V2_phasor = (Vdc/2)*M2*exp(1i*deg2rad(delta));
            I_phasor = (V1_phasor - V2_phasor)/(1i*omega*L);
            
            % Power factor = cos(θ_v - θ_i)
            pf_map(i,j) = cos(angle(V1_phasor) - angle(I_phasor));
        end
    end
end

% Create meshgrid for plotting
[M1_grid, M2_grid] = meshgrid(M1_range, M2_range);

%% Phase Shift Contour Plot
figure;
contourf(M1_grid, M2_grid, delta_map', 20, 'EdgeColor', 'none');
xlabel('M1 (EV Modulation Index)');
ylabel('M2 (Load Modulation Index)');
title('Phase Shift (\delta) Required for 360A Current');
colorbar;
colormap jet;
caxis([0 90]);
hold on;
contour(M1_grid, M2_grid, delta_map', [0:10:90], 'EdgeColor', 'k', 'ShowText', 'on');

%% Power Factor Contour Plot
figure;
contourf(M1_grid, M2_grid, pf_map', 20, 'EdgeColor', 'none');
xlabel('M1 (EV Modulation Index)');
ylabel('M2 (Load Modulation Index)');
title('Power Factor at M1 Voltage Source');
colorbar;
colormap jet;
caxis([0.8 1.0]);
hold on;
contour(M1_grid, M2_grid, pf_map', [0.8:0.02:1.0], 'EdgeColor', 'k', 'ShowText', 'on');

%% Power Factor vs M1 for Fixed M2 Values
figure;
hold on;
colors = lines(5);
M2_slices = [0.2 0.4 0.6 0.8];
for k = 1:length(M2_slices)
    [~, idx] = min(abs(M2_range - M2_slices(k)));
    plot(M1_range, pf_map(:,idx), 'LineWidth', 2, 'Color', colors(k,:));
end
xlabel('M1 (EV Modulation Index)');
ylabel('Power Factor');
title('Power Factor vs M1 for Fixed M2 Values');
grid on;
legend(cellstr(num2str(M2_slices', 'M2=%.1f')), 'Location', 'best');
ylim([0.8 1.01]);

%% Frequency Profile (for reference)
figure;
plot(M1_range, frequencies, 'LineWidth', 2);
xlabel('M1 (EV Modulation Index)');
ylabel('Frequency (Hz)');
title('Operating Frequency vs M1');
grid on;
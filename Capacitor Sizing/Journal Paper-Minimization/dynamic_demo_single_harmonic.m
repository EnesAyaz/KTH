% Example parameters
fs = 1e7;       % 10 MHz sampling
fsw = 10e3;        % 10 kHz switching


% Define phase shift resolution
n_points = 200; % Number of points for theta_b and theta_c
theta_b_values = linspace(0,180, n_points);
theta_c_values = linspace(0, 180, n_points);


theta_fund_x=[];
optimum_theta_b= [];
optimum_theta_c= [];


for theta_fund=0:12:360
% theta_fund = 0; % in degrees
theta_fund = theta_fund * pi / 180;
Ipp = 1;
pf = 1;
load_angle = acos(pf);

% Initialize RMS current matrix
I_rms_matrix = zeros(n_points, n_points);

for i = 1:1:n_points  
for j = 1:1:n_points  

shiftB = theta_b_values(i)*pi/180;     % in radians
shiftC = theta_b_values(j)*pi/180;      % in radians

% Generate carriers
[t, carrierA,carrierB,carrierC] = generate_triangular_carriers(fs, fsw, shiftB, shiftC);

% Fundamental currents (sinusoidal)
Ia = Ipp * cos(theta_fund - load_angle);
Ib = Ipp * cos(theta_fund - 2*pi/3 - load_angle);
Ic = Ipp * cos(theta_fund + 2*pi/3 - load_angle);

% Modulation index and duty cycles
ma = 0.8;
Va_ref = ma * cos(theta_fund);
Vb_ref = ma * cos(theta_fund - 2*pi/3);
Vc_ref = ma * cos(theta_fund + 2*pi/3);



Ica = Ia * (Va_ref > carrierA);
Icb = Ib * (Vb_ref > carrierB);
Icc = Ic * (Vc_ref > carrierC);
Ic_tot=Ica+Icb+Icc-mean(Ica+Icb+Icc);



if(0)
figure;
plot(t, carrierA, 'b', 'LineWidth', 1.5); hold on;
plot(t, carrierB, 'r', 'LineWidth', 1.5);
plot(t, carrierC, 'g', 'LineWidth', 1.5);
plot(t, Ic_tot);
yline( Va_ref, 'b--', 'LineWidth', 1.5); hold on;
yline(Vb_ref, 'r--', 'LineWidth', 1.5); hold on;
yline(Vc_ref, 'g--', 'LineWidth', 1.5); hold on;

hold off;
legend('Carrier 1 (0°)', sprintf('Carrier 2 (%.0f°)', rad2deg(shiftB)), ...
       sprintf('Carrier 3 (%.0f°)', rad2deg(shiftC)), 'Ic');
xlabel('Time (s)'); ylabel('Amplitude, Current (A)');
title('Phase-Shifted Triangular Carriers and Capacitor Current');
grid on;
xlim([0 1/fsw]);  % Show one complete period


figure;
plot(t, Ica, 'b', 'LineWidth', 1.5); hold on;
plot(t, Icb, 'r', 'LineWidth', 1.5);
plot(t, Icc, 'g', 'LineWidth', 1.5);
plot(t, Ic_tot);

hold off;
legend('Ica','Icb','Icc', 'Ic');
xlabel('Time (s)'); ylabel('Current (A)');
title('Phase-Shifted Triangular Carriers and Capacitor Current');
grid on;
xlim([0 1/fsw]);  % Show one complete period


figure;
plot(t, Ic_tot);
legend('Ic');
xlabel('Time (s)'); ylabel('Current (A)');
title('Phase-Shifted Triangular Carriers and Capacitor Current');
grid on;
xlim([0 1/fsw]);  % Show one complete period
end


% Calculate fundamental (first harmonic) component using DFT
N = length(Ic_tot);
Ic_fft = fft(Ic_tot)/N;       % Normalized FFT
harmonic_component = 2*abs(Ic_fft(2));  % First harmonic 2, second harmonic 3 (skip DC component at index 1)
Ic_RMS = harmonic_component/sqrt(2);    % Convert amplitude to RMS

I_rms_matrix(i, j) = Ic_RMS;

end
end

[min_value, linear_index] = min(I_rms_matrix(:));

% Convert linear index to row and column subscripts
[row_index, col_index] = ind2sub(size(I_rms_matrix), linear_index);

theta_fund_x=[theta_fund_x theta_fund]
optimum_theta_b= [optimum_theta_b theta_b_values(row_index)]
optimum_theta_c= [optimum_theta_c theta_c_values(col_index)]


if(1)
% Create contour plot
[Theta_b, Theta_c] = meshgrid(theta_b_values, theta_c_values);
figure;
contourf(Theta_b, Theta_c, I_rms_matrix, 20, 'LineColor', 'none'); % 20 contour levels
xlabel('\theta_b (rad)');
ylabel('\theta_c (rad)');
title('Total RMS Current vs. Phase Shifts \theta_b and \theta_c');
colorbar;
colormap(jet); % Use 'parula', 'hot', or other colormaps

% Optional: Overlay contour lines
hold on;
contour(Theta_b, Theta_c, I_rms_matrix, 10, 'LineColor', 'k', 'LineWidth', 0.5);
hold off;
end

end

%%
figure();
stairs(theta_fund_x, optimum_theta_b, 'LineWidth', 2, 'DisplayName', 'Optimum θ_b'); 
hold on;
stairs(theta_fund_x, optimum_theta_c, 'LineWidth', 2, 'DisplayName', 'Optimum θ_c');

% Add labels and title
xlabel('Fundamental Dimension (θ_{fund} x)', 'FontSize', 12);
ylabel('Optimum θ Values', 'FontSize', 12);
title('Comparison of Optimum θ_b and θ_c', 'FontSize', 14);

% Add legend
legend('Location', 'best');

% Add grid
grid on;

% Adjust axes if needed
xlim([min(theta_fund_x) max(theta_fund_x)]);
ylim([0 360])

% Improve overall appearance
set(gca, 'FontSize', 11);
box on;

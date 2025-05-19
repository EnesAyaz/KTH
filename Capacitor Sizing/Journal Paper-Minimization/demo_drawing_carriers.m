% Example parameters
fs = 1e7;       % 10 MHz sampling
fsw = 10e3;        % 10 kHz switching

theta_fund=30;
theta_fund = theta_fund * pi / 180;
Ipp = 100;
pf = 0.9;
load_angle = acos(pf);
ma = 0.8;



n_points = 360; % Number of points for theta_b and theta_c
theta_b_values = linspace(0,360, n_points);
theta_c_values = linspace(0, 360, n_points);


% Initialize RMS current matrix
I_rms_matrix = zeros(n_points, n_points);

theta_fund_x=[];
optimum_theta_b_tot= [];
optimum_theta_c_tot= [];
optimum_theta_b_first= [];
optimum_theta_c_first= [];
optimum_theta_b_second= [];
optimum_theta_c_second= [];

optimum_theta_RMS=[];
optimum_theta_RMS_first=[];
optimum_theta_RMS_second=[];

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

Iax=Ia./(abs(Ia)+abs(Ib)+abs(Ic));

Ibx=Ib./(abs(Ia)+abs(Ib)+abs(Ic));

Icx=Ic./(abs(Ia)+abs(Ib)+abs(Ic));

Ia=Iax;
Ib=Ibx;
Ic=Icx;

% Modulation index and duty cycles

Va_ref = ma * cos(theta_fund);
Vb_ref = ma * cos(theta_fund - 2*pi/3);
Vc_ref = ma * cos(theta_fund + 2*pi/3);

Ica = Ia * (Va_ref > carrierA);
Icb = Ib * (Vb_ref > carrierB);
Icc = Ic * (Vc_ref > carrierC);
Ic_total=Ica+Icb+Icc-mean(Ica+Icb+Icc);


if(0)
figure;
plot(t, carrierA, 'b', 'LineWidth', 1.5); hold on;
plot(t, carrierB, 'r', 'LineWidth', 1.5);
plot(t, carrierC, 'g', 'LineWidth', 1.5);
plot(t, Ic_total);
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
plot(t, Ic_total);

hold off;
legend('Ica','Icb','Icc', 'Ic');
xlabel('Time (s)'); ylabel('Current (A)');
title('Phase-Shifted Triangular Carriers and Capacitor Current');
grid on;
xlim([0 1/fsw]);  % Show one complete period


figure;
plot(t, Ic_total);
legend('Ic');
xlabel('Time (s)'); ylabel('Current (A)');
title('Phase-Shifted Triangular Carriers and Capacitor Current');
grid on;
xlim([0 1/fsw]);  % Show one complete period
end


Ic_RMS=rms(Ic_total);

% Calculate fundamental (first harmonic) component using DFT
N = length(Ic_total);
Ic_fft = fft(Ic_total)/N;       % Normalized FFT
harmonic_component = 2*abs(Ic_fft(2));  % First harmonic 2, second harmonic 3 (skip DC component at index 1)
Ic_RMS_first = harmonic_component/sqrt(2);    % Convert amplitude to RMS


% Calculate fundamental (first harmonic) component using DFT
N = length(Ic_total);
Ic_fft = fft(Ic_total)/N;       % Normalized FFT
harmonic_component = 2*abs(Ic_fft(3));  % First harmonic 2, second harmonic 3 (skip DC component at index 1)
Ic_RMS_second = harmonic_component/sqrt(2);    % Convert amplitude to RMS

I_rms_matrix(i, j) = Ic_RMS;
I_rms_matrix_first(i, j) = Ic_RMS_first;
I_rms_matrix_second(i, j) = Ic_RMS_second;


end
end

[min_value, linear_index] = min(I_rms_matrix(:));

% Convert linear index to row and column subscripts
[row_index, col_index] = ind2sub(size(I_rms_matrix), linear_index);

theta_fund_x=[theta_fund_x theta_fund];
optimum_theta_b_tot= [optimum_theta_b_tot theta_b_values(col_index)];
optimum_theta_c_tot= [optimum_theta_c_tot theta_c_values(row_index)];
optimum_theta_RMS=[optimum_theta_RMS, min_value];


[min_value, linear_index] = min(I_rms_matrix_first(:));

% Convert linear index to row and column subscripts
[row_index, col_index] = ind2sub(size(I_rms_matrix_first), linear_index);

optimum_theta_b_first= [optimum_theta_b_first theta_b_values(col_index)];
optimum_theta_c_first= [optimum_theta_c_first theta_c_values(row_index)];
optimum_theta_RMS_first=[optimum_theta_RMS_first min_value];


[min_value, linear_index] = min(I_rms_matrix_second(:));

% Convert linear index to row and column subscripts
[row_index, col_index] = ind2sub(size(I_rms_matrix_second), linear_index);

optimum_theta_b_second= [optimum_theta_b_second theta_b_values(col_index)];
optimum_theta_c_second= [optimum_theta_c_second theta_c_values(row_index)];
optimum_theta_RMS_second=[optimum_theta_RMS_second min_value ];

RMS_00= I_rms_matrix(1,1);
RMS_00_first= I_rms_matrix_first(1,1);
RMS_00_second= I_rms_matrix_second(1,1);

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


figure;
contourf(Theta_b, Theta_c, I_rms_matrix_first, 20, 'LineColor', 'none'); % 20 contour levels
xlabel('\theta_b (rad)');
ylabel('\theta_c (rad)');
title('First Harmonic RMS Current vs. Phase Shifts \theta_b and \theta_c');
colorbar;
colormap(jet); % Use 'parula', 'hot', or other colormaps

% Optional: Overlay contour lines
hold on;
contour(Theta_b, Theta_c, I_rms_matrix_first, 10, 'LineColor', 'k', 'LineWidth', 0.5);
hold off;


figure;
contourf(Theta_b, Theta_c, I_rms_matrix_second, 20, 'LineColor', 'none'); % 20 contour levels
xlabel('\theta_b (rad)');
ylabel('\theta_c (rad)');
title('Second Harmonic RMS Current vs. Phase Shifts \theta_b and \theta_c');
colorbar;
colormap(jet); % Use 'parula', 'hot', or other colormaps

% Optional: Overlay contour lines
hold on;
contour(Theta_b, Theta_c, I_rms_matrix_second, 10, 'LineColor', 'k', 'LineWidth', 0.5);
hold off;

end


[optimum_theta_b_tot , optimum_theta_c_tot, optimum_theta_RMS RMS_00; optimum_theta_b_first optimum_theta_c_first, optimum_theta_RMS_first  RMS_00_first; optimum_theta_b_second, optimum_theta_c_second, optimum_theta_RMS_second RMS_00_second]



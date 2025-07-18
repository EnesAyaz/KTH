theta_fund = 10; % in degrees
theta_fund = theta_fund * pi / 180;
Ipp = 1;
pf = 0.9;
load_angle = acos(pf);

% Fundamental currents (sinusoidal)
Ia = Ipp * cos(theta_fund - load_angle);
Ib = Ipp * cos(theta_fund - 2*pi/3 - load_angle);
Ic = Ipp * cos(theta_fund + 2*pi/3 - load_angle);

% Modulation index and duty cycles
ma = 0.8;
Va_ref = ma * cos(theta_fund);
Vb_ref = ma * cos(theta_fund - 2*pi/3);
Vc_ref = ma * cos(theta_fund + 2*pi/3);

da = (1 + Va_ref) / 2;
db = (1 + Vb_ref) / 2;
dc = (1 + Vc_ref) / 2;

% Define phase shift resolution
n_points = 200; % Number of points for theta_b and theta_c
theta_b_values = linspace(0, 2*pi, n_points);
theta_c_values = linspace(0, 2*pi, n_points);

% Initialize RMS current matrix
I_rms_matrix = zeros(n_points, n_points);

% Harmonic orders to consider
n_harmonics = 20; % Up to 20th harmonic

% Loop over all theta_b and theta_c combinations
for i = 1:n_points
    for j = 1:n_points
        theta_b = theta_b_values(i);
        theta_c = theta_c_values(j);
        
        % Initialize total current (sum of all harmonics)
        I_total_rms = 0;
        
        for n = 1:n_harmonics
            % Harmonic magnitudes (from PWM)
            Ia_n = Ia * sin(n * pi * da);
            Ib_n = Ib * sin(n * pi * db);
            Ic_n = Ic * sin(n * pi * dc);
            
            % Apply phase shifts (n*θ_b and n*θ_c)
            Ia_complex = Ia_n * exp(1i * 0); % Reference (0°)
            Ib_complex = Ib_n * exp(1i * n * theta_b); % Shifted by n*θ_b
            Ic_complex = Ic_n * exp(1i * n * theta_c); % Shifted by n*θ_c
            
            % Sum the harmonics (vector sum)
            I_total_n = Ia_complex + Ib_complex + Ic_complex;
            I_rms_n=abs(I_total_n)/sqrt(2);
            % Add squared magnitude to total RMS
            I_total_rms = sqrt(I_total_rms^2 + I_rms_n^2);
        end
        
        % Store RMS for this (θ_b, θ_c) combination
        I_rms_matrix(i, j) = I_total_rms;
    end
end

% (Previous code remains the same until I_rms_matrix is computed)

% Create contour plot
[Theta_b, Theta_c] = meshgrid(180*theta_b_values/pi, 180*theta_c_values/pi);
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

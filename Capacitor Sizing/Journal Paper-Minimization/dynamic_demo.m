% Example parameters
fs = 1e7;       % 10 MHz sampling
fsw = 10e3;        % 10 kHz switching

% Define phase shift resolution
n_points = 360; % Number of points for theta_b and theta_c
theta_b_values = linspace(0,360, n_points);
theta_c_values = linspace(0, 360, n_points);

theta_fund_x=[];
optimum_theta_b= [];
optimum_theta_c= [];
minimum_RMS= [];
RMS_00= [];

Iax=[];
Ibx=[];
Icx=[];

Va_ref_x=[];
Vb_ref_x=[];
Vc_ref_x=[];

for theta_fund=0:3:360
% theta_fund = 0; % in degrees
theta_fund = theta_fund * pi / 180;
Ipp = 100;
pf = 1;
load_angle = acos(pf);

% Initialize RMS current matrix
I_rms_matrix = zeros(n_points, n_points);

for i = 1:1:n_points  
for j = 1:1:n_points  

shiftB = theta_b_values(i)*pi/360;     % in radians
shiftC = theta_b_values(j)*pi/360;      % in radians

% Generate carriers
[t, carrierA,carrierB,carrierC] = generate_triangular_carriers(fs, fsw, shiftB, shiftC);

% Fundamental currents (sinusoidal)
Ia = Ipp * cos(theta_fund - load_angle);
Ib = Ipp * cos(theta_fund - 2*pi/3 - load_angle);
Ic= Ipp * cos(theta_fund + 2*pi/3 - load_angle);


% Modulation index and duty cycles
ma = 0.5;
Va_ref = ma * (cos(theta_fund)-cos(theta_fund*3)/6);
Vb_ref = ma * (cos(theta_fund - 2*pi/3)-cos(theta_fund*3)/6);
Vc_ref = ma * (cos(theta_fund + 2*pi/3)-cos(theta_fund*3)/6);
% 
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

Ic_RMS=rms(Ic_tot);

I_rms_matrix(i, j) = Ic_RMS;

end
end


[min_value, linear_index] = min(I_rms_matrix(:));

% Convert linear index to row and column subscripts
[row_index, col_index] = ind2sub(size(I_rms_matrix), linear_index);

theta_fund_x=[theta_fund_x theta_fund]
optimum_theta_b= [optimum_theta_b theta_b_values(row_index)]
optimum_theta_c= [optimum_theta_c theta_c_values(col_index)]
minimum_RMS= [ minimum_RMS min(I_rms_matrix(:))];
RMS_00= [ RMS_00 I_rms_matrix(1,1)];

Iax=[Iax Ia];
Ibx=[Ibx Ib];
Icx=[Icx Ic];

Va_ref_x=[Va_ref_x Va_ref];
Vb_ref_x=[Vb_ref_x Vb_ref];
Vc_ref_x=[Vc_ref_x Vc_ref];


if(0)
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
% yyaxis left
stairs(180*theta_fund_x/pi, optimum_theta_b, 'LineWidth', 2, 'DisplayName', 'Optimum θ_b'); 
hold on;
stairs(180*theta_fund_x/pi, optimum_theta_c, 'LineWidth', 2, 'DisplayName', 'Optimum θ_c');
hold on
ylim([0 360])
% ylabel('Optimum θ Values', 'FontSize', 12);
% yyaxis right
% stairs(theta_fund_x, minimum_RMS, 'LineWidth', 2, 'DisplayName', 'RMS');

% Add labels and title
xlabel('Fundamental Phase (θ_{fund})', 'FontSize', 12);
ylabel('Optimum θ Values', 'FontSize', 12);
title('Comparison of Optimum θ_b and θ_c', 'FontSize', 14);

% Add legend
legend('Location', 'best');

% Add grid
grid on;

% Adjust axes if needed
xlim([180*min(theta_fund_x)/pi  180*max(theta_fund_x)/pi]);


% Improve overall appearance
set(gca, 'FontSize', 11);
box on;
%%
%%
figure();

stairs(180*theta_fund_x/pi, minimum_RMS./max(RMS_00), 'LineWidth', 2, 'DisplayName', 'RMS-Optimized');
hold on 
stairs(180*theta_fund_x/pi, RMS_00./max(RMS_00), 'LineWidth', 2, 'DisplayName', 'RMS-Zero');

% Add labels and title
xlabel('Fundamental Phase (θ_{fund})', 'FontSize', 12);
ylabel('Normalized RMS Current', 'FontSize', 12);
% title('Comparison of Optimum θ_b and θ_c', 'FontSize', 14);

% Add legend
legend('Location', 'best');

% Add grid
grid on;

% Adjust axes if needed
xlim([180*min(theta_fund_x)/pi 180*max(theta_fund_x)/pi]);
ylim([ 0 1])


% Improve overall appearance
set(gca, 'FontSize', 11);
box on;
%%


figure();
stairs(180*theta_fund_x/pi, Iax, 'LineWidth', 2, 'DisplayName', 'PhA-Current'); 
hold on;
stairs(180*theta_fund_x/pi, Ibx, 'LineWidth', 2, 'DisplayName', 'PhB-Current');
hold on
stairs(180*theta_fund_x/pi, Icx, 'LineWidth', 2, 'DisplayName', 'PhC-Current');

% Add labels and title
xlabel('Fundamental Phase (θ_{fund})', 'FontSize', 12);
ylabel('Normalized Current (A)', 'FontSize', 12);
title('Phase Currents', 'FontSize', 14);

% Add legend
legend('Location', 'best');

% Add grid
grid on;

% Adjust axes if needed
xlim([180*min(theta_fund_x)/pi 180*max(theta_fund_x)/pi]);
% ylim([0 360])

% Improve overall appearance
set(gca, 'FontSize', 11);
box on;
%%
figure();
stairs(theta_fund_x, Va_ref_x, 'LineWidth', 2, 'DisplayName', 'PhA-Reference'); 
hold on;
stairs(theta_fund_x, Vb_ref_x, 'LineWidth', 2, 'DisplayName', 'PhB-Reference');
hold on
stairs(theta_fund_x, Vc_ref_x, 'LineWidth', 2, 'DisplayName', 'PhC-Reference');

% Add labels and title
xlabel('Fundamental Phase (θ_{fund})', 'FontSize', 12);
ylabel('Normalized Reference Voltage', 'FontSize', 12);
title('Phase Voltage', 'FontSize', 14);

% Add legend
legend('Location', 'best');

% Add grid
grid on;

% Adjust axes if needed
xlim([min(theta_fund_x) max(theta_fund_x)]);
% ylim([0 360])

% Improve overall appearance
set(gca, 'FontSize', 11);
box on;

%% Air-Core Inductor Design with Round Wire and Resistance Calculation
clear; close all; clc;

%% Design Specifications
L_required = 500e-6; % Required inductance (500 µH)
V_peak = 1200;       % Peak voltage (V)
I_peak = 350;        % Peak current (A)
f_fund = 500;        % Fundamental frequency (Hz)

%% Material Properties
mu0 = 4*pi*1e-7;    % Permeability of free space (H/m)
rho_Cu = 1.68e-8;   % Copper resistivity (Ω·m) at 20°C
J_max = 5e6;        % Current density (A/m²)
V_turn_max = 100;   % Maximum voltage per turn (V)
d_min = 1.2e-3;     % Minimum turn-to-turn spacing (m) for 1200V

%% Step 1: Determine Round Wire Size
A_Cu = I_peak / J_max;
wire_diameter = sqrt(4*A_Cu/pi);
fprintf('Minimum Copper Area: %.2f mm²\n', A_Cu*1e6);
fprintf('Equivalent Round Wire Diameter: %.2f mm\n', wire_diameter*1e3);

% Select standard AWG size (copper, solid)
AWG = [4, 2, 1, 1/0 4/0]; % Considering high current requirements
AWG_diam = [5.189, 6.544, 7.348, 8.252 12]*1e-3; % in meters

% AWG = [4/0]; % Considering high current requirements
% AWG_diam = [16]*1e-3; % in meters


AWG = [4]; % Considering high current requirements
AWG_diam = [3.5]*1e-3; % in meters

% AWG = [4, 2]; % Considering high current requirements
% AWG_diam = [5.189, 6.544]*1e-3; % in meters

AWG_area = pi*(AWG_diam/2).^2;

[~, idx] = min(abs(AWG_area - A_Cu));
selected_AWG = AWG(idx);
selected_diam = AWG_diam(idx);
selected_area = AWG_area(idx);
fprintf('Selected AWG: %s (%.2f mm diameter, %.2f mm² area)\n', ...
        num2str(selected_AWG), selected_diam*1e3, selected_area*1e6);

%% Step 2: Air-Core Inductor Design
% Wheeler's formula: L (µH) = (d² * n²) / (18d + 40l)
% where d is coil diameter (inches), n is turns, l is length (inches)

% Minimum turns based on voltage
n_min_voltage = ceil(V_peak / V_turn_max);

% Iterative design
target_L = L_required;
outer_diameter = 0.15; % Initial guess (m)
turn_spacing = max(d_min, V_peak/(n_min_voltage*1e6)); % Spacing based on voltage

best_error = inf;
for iter = 1:50
    % Try different turn counts
    for n_turns = max(5, n_min_voltage-5):n_min_voltage+20
        % Calculate length based on wire diameter and spacing
        length = n_turns * (selected_diam + turn_spacing);
        
        % Convert to inches for Wheeler's
        d_in = outer_diameter * 39.37;
        l_in = length * 39.37;
        
        % Calculate inductance
        L_calc = (d_in^2 * n_turns^2) / (18*d_in + 40*l_in) * 1e-6;
        
        % Track best design
        error = abs(L_calc - target_L)/target_L;
        if error < best_error
            best_error = error;
            best_design = struct('n_turns', n_turns, ...
                                'outer_diameter', outer_diameter, ...
                                'length', length, ...
                                'L_calc', L_calc, ...
                                'turn_spacing', turn_spacing);
        end
    end
    
    % Adjust diameter
    if best_design.L_calc < target_L
        outer_diameter = outer_diameter * 1.05;
    else
        outer_diameter = outer_diameter * 0.95;
    end
    
    if best_error < 0.01 % 1% tolerance
        break;
    end
end

%% Resistance Calculations
% 1. DC Resistance
mean_turn_length = pi * (best_design.outer_diameter - selected_diam);
total_wire_length = best_design.n_turns * mean_turn_length;
R_dc = rho_Cu * total_wire_length / selected_area;

% 2. AC Resistance (considering skin and proximity effects)
skin_depth = sqrt(rho_Cu/(pi*mu0*f_fund));
fprintf('\nSkin depth at %.1f kHz: %.2f mm\n', f_fund/1e3, skin_depth*1e3);

% Skin effect factor
if selected_diam > (2*skin_depth)
    xi = selected_diam/(2*skin_depth);
    F_skin = xi/2 * (besseli(0,xi)/besseli(1,xi) + 3/(4*xi^2));
else
    F_skin = 1; % Negligible skin effect
end

% Proximity effect factor (approximation)
wire_spacing = best_design.turn_spacing + selected_diam;
G_prox = 1 + (selected_diam/wire_spacing)^2 * (best_design.n_turns^2 - 1)/6;

R_ac = R_dc * F_skin * G_prox;

%% Display Results
fprintf('\n=== Final Design Parameters ===\n');
fprintf('Required Inductance: %.2f µH\n', L_required*1e6);
fprintf('Achieved Inductance: %.2f µH (%.1f%% error)\n', best_design.L_calc*1e6, best_error*100);
fprintf('Number of Turns: %d\n', best_design.n_turns);
fprintf('Outer Diameter: %.2f mm\n', best_design.outer_diameter*1e3);
fprintf('Coil Length: %.2f mm\n', best_design.length*1e3);
fprintf('Wire Diameter: %.2f mm (AWG %s)\n', selected_diam*1e3, num2str(selected_AWG));
fprintf('Turn-to-Turn Spacing: %.2f mm\n', best_design.turn_spacing*1e3);
fprintf('Voltage per Turn: %.2f V\n', V_peak/best_design.n_turns);

fprintf('\n=== Resistance Values ===\n');
fprintf('DC Resistance: %.4f mΩ\n', R_dc*1e3);
fprintf('AC Resistance at %.1f kHz: %.4f mΩ\n', f_fund/1e3, R_ac*1e3);
fprintf('   (Skin effect factor: %.3f)\n', F_skin);
fprintf('   (Proximity factor: %.3f)\n', G_prox);
fprintf('Total Wire Length: %.2f m\n', total_wire_length);

%% 3D Visualization
figure;
hold on;
theta = linspace(0, 2*pi, 100);
radius = best_design.outer_diameter/2 - selected_diam/2;

% Draw turns
for i = 1:best_design.n_turns
    z = -best_design.length/2 + (i-0.5)*(selected_diam + best_design.turn_spacing);
    plot3(radius*cos(theta), radius*sin(theta), z*ones(size(theta)), 'b', 'LineWidth',1.5);
end

% Add markers at start and end
plot3(radius*cos(0), radius*sin(0), -best_design.length/2, 'go', 'MarkerSize', 8, 'LineWidth',2);
plot3(radius*cos(0), radius*sin(0), best_design.length/2, 'ro', 'MarkerSize', 8, 'LineWidth',2);

view(3); axis equal; grid on;
title(sprintf('3D Round Wire Inductor\n%.2f µH, %d Turns, %.1fmm Wire', ...
    best_design.L_calc*1e6, best_design.n_turns, selected_diam*1e3));
xlabel('X (m)'); ylabel('Y (m)'); zlabel('Length (m)');
% legend('Turns', 'Start', 'End', 'Location','best');


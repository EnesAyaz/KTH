%% MOSFET Power Losses and Thermal Calculations

% MOSFET datasheet parameters
Rds_on_25C = 40e-3;     % On-state resistance at 25C [Ohm]
Vds = 1200;              % Maximum drain-source voltage rating [V]
Vgs_th_25C = 4;          % Gate threshold voltage at 25C [V]
alpha_Vgs = -2.2e-3;     % Temperature coefficient of Vgs_th [V/C]
Qg = 70e-9;              % Total gate charge [Coulombs]
Qgs = 15e-9;             % Gate-source charge [Coulombs]
Qgd = 25e-9;             % Gate-drain charge [Coulombs]
Ciss = 1200e-12;         % Input capacitance [Farads]
Coss = 200e-12;          % Output capacitance [Farads]
Crss = 40e-12;           % Reverse transfer capacitance [Farads]
td_on = 20e-9;           % Turn-on delay time [seconds]
tr = 45e-9;              % Rise time [seconds]
td_off = 50e-9;          % Turn-off delay time [seconds]
tf = 30e-9;              % Fall time [seconds]
Rth_jc = 0.07;           % Thermal resistance junction-to-case [C/W]
Rth_ca = 0.5;           % Thermal resistance junction-to-case [C/W]

% Operating conditions
I = 30;                  % RMS current [A]
fsw = 30e3;             % Switching frequency [Hz]
Qrr = 5e-9;              % Reverse recovery charge [Coulombs]
trr = 30e-9;             % Reverse recovery time [seconds]
Vgs_25C = 15;            % Gate-source voltage at 25C [V]
Vds_max = 1200;          % Maximum drain-source voltage [V]
T_amb = 25;              % Ambient temperature [Celsius]
T_j_max = 175;           % Maximum junction temperature [Celsius]
T_j_init = T_amb + 10;   % Initial guess for junction temperature [Celsius]
tol = 0.01;              % Tolerance for iterative method

% Temperature-dependent parameters
T_ref = 25;                      % Reference temperature [Celsius]
Rds_on = Rds_on_25C * (1 + 0.0045*(T_amb - T_ref)); % On-state resistance [Ohm]
Vgs_th = Vgs_th_25C + alpha_Vgs*(T_amb - T_ref);   % Gate threshold voltage [V]

% Iterative method to find steady-state thermal condition
T_j = T_j_init;
T_j_old = T_j_init - 1;
while abs(T_j - T_j_old) > tol
    T_j_old = T_j;
    
    % Calculate MOSFET power losses
    P_on = I^2 * Rds_on;
    P_switch = (Ciss + Coss + Crss) * Vds^2 * fsw ...
               + (Qg - Qgs) * Vgs_th * fsw ...
               + (Qgd + Qgs) * Vds * fsw ...
               + (td_on + tr) * I * Vds / 2 ...
               + (td_off + tf) * I * Vds / 2;
           
    P_rr = (Qrr * Vds_max) / trr;
    P_diode = P_rr / 2; % assuming symmetric diodes

    % Calculate MOSFET junction temperature
    P_tot = P_on + P_switch + P_diode;
    T_j = T_amb + P_tot * (Rth_jc+Rth_ca);

    % Update temperature-dependent parameters
    Rds_on = Rds_on_25C * (1 + 0.0045*(T_j - T_ref));
    Vgs_th = Vgs_th_25C + alpha_Vgs*(T_j - T_ref);
    
end


% Display results
fprintf('On-state power dissipation: %f W\n', P_on)
fprintf('Switching power dissipation: %f W\n', P_switch)
fprintf('Reverse recovery power dissipation: %f W\n', P_diode)
fprintf('Total power dissipation: %f W\n', P_tot)
fprintf('Steady-state junction temperature: %f C\n', T_j)



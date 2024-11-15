% Define component values
% Inductances between input nodes and capacitor nodes
LphAcap1Pos = 1e-6; % Example values in Henries
LphAcap2Pos = 1e-6;
LphAcap3Pos = 1e-6;
LphAcap4Pos = 1e-6;

LphAcap1Neg = 1e-6;
LphAcap2Neg = 1e-6;
LphAcap3Neg = 1e-6;
LphAcap4Neg = 1e-6;

% Mutual inductances between corresponding positive and negative branches
MphAcap1 = 0.5e-6;
MphAcap2 = 0.5e-6;
MphAcap3 = 0.5e-6;
MphAcap4 = 0.5e-6;

% Capacitances and ESLs
Ccap1 = 1e-6; ESLcap1 = 1e-9;
Ccap2 = 1e-6; ESLcap2 = 1e-9;
Ccap3 = 1e-6; ESLcap3 = 1e-9;
Ccap4 = 1e-6; ESLcap4 = 1e-9;

% Frequency range
frequencies = logspace(1, 6, 1000); % From 10 Hz to 1 MHz
omega = 2 * pi * frequencies; % Angular frequencies

% Initialize response array
current_response = zeros(size(frequencies));

% Define node indices for reference
% 1: phAPos, 2: phANeg, 3: Cap1Pos, 4: Cap1Neg, ..., 10: Cap4Neg
num_nodes = 10;
Y = zeros(num_nodes, num_nodes);

% Sweep through frequencies
for k = 1:length(omega)
    w = omega(k);
    
    % Reset admittance matrix
    Y = zeros(num_nodes, num_nodes);
    
    % Inductive admittance with mutual inductances
    % Y(1,3): phAPos to Cap1Pos, Y(2,4): phANeg to Cap1Neg (with mutual MphAcap1)
    Y(1, 3) = 1/(1i * w * LphAcap1Pos); Y(3, 1) = Y(1, 3);
    Y(2, 4) = 1/(1i * w * LphAcap1Neg); Y(4, 2) = Y(2, 4);
    Y(3, 4) = -1/(1i * w * MphAcap1); Y(4, 3) = Y(3, 4); % Mutual inductance

    % Y(1,5): phAPos to Cap2Pos, Y(2,6): phANeg to Cap2Neg (with mutual MphAcap2)
    Y(1, 5) = 1/(1i * w * LphAcap2Pos); Y(5, 1) = Y(1, 5);
    Y(2, 6) = 1/(1i * w * LphAcap2Neg); Y(6, 2) = Y(2, 6);
    Y(5, 6) = -1/(1i * w * MphAcap2); Y(6, 5) = Y(5, 6);

    % Y(1,7): phAPos to Cap3Pos, Y(2,8): phANeg to Cap3Neg (with mutual MphAcap3)
    Y(1, 7) = 1/(1i * w * LphAcap3Pos); Y(7, 1) = Y(1, 7);
    Y(2, 8) = 1/(1i * w * LphAcap3Neg); Y(8, 2) = Y(2, 8);
    Y(7, 8) = -1/(1i * w * MphAcap3); Y(8, 7) = Y(7, 8);

    % Y(1,9): phAPos to Cap4Pos, Y(2,10): phANeg to Cap4Neg (with mutual MphAcap4)
    Y(1, 9) = 1/(1i * w * LphAcap4Pos); Y(9, 1) = Y(1, 9);
    Y(2, 10) = 1/(1i * w * LphAcap4Neg); Y(10, 2) = Y(2, 10);
    Y(9, 10) = -1/(1i * w * MphAcap4); Y(10, 9) = Y(9, 10);

    % Capacitances and ESLs
    Y(3, 3) = Y(3, 3) + 1i * w * ESLcap1 + 1/(1i * w * Ccap1);
    Y(4, 4) = Y(4, 4) + 1i * w * ESLcap1 + 1/(1i * w * Ccap1);
    
    % Input current source at phAPos and phANeg
    I = zeros(num_nodes, 1);
    I(1) = 1; % Current source of 1 A
    
    % Solve for node voltages
    V = Y \ I;
    
    % Compute the current response through Cap1 (from Cap1Pos to Cap1Neg)
    Vcap1Pos = V(3);
    Vcap1Neg = V(4);
    current_response(k) = (Vcap1Pos - Vcap1Neg) * (1i * w * Ccap1);
end

% Plotting the frequency response
figure;
subplot(2, 1, 1);
loglog(frequencies, abs(current_response));
xlabel('Frequency (Hz)');
ylabel('Magnitude of Current Response (A)');
title('Frequency Response with Mutual Inductance between phAPos-phANeg branches');
grid on;

subplot(2, 1, 2);
semilogx(frequencies, angle(current_response) * (180/pi));
xlabel('Frequency (Hz)');
ylabel('Phase of Current Response (Degrees)');
grid on;


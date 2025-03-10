% MATLAB Script for 3-Level SVM (NTSVPWM)
% Based on the paper: "A Simple Carrier-Based Implementation for a General 3-level Inverter Using Nearest Three Space Vector PWM Approach"

% Parameters
Vdc = 400;          % DC-link voltage
M = 1.0;            % Modulation index (can be up to 1.0)
fout = 50;          % Output frequency (Hz)
fs = 10e3;          % Sampling frequency (Hz)
Ts = 1/fs;          % Sampling period
t = 0:Ts:1/fout;    % Time vector for one period

% Modulation signals (3-phase)
theta = 2*pi*fout*t; % Electrical angle
mA = M * cos(theta); % Phase A modulation signal
mB = M * cos(theta - 2*pi/3); % Phase B modulation signal
mC = M * cos(theta - 4*pi/3); % Phase C modulation signal

% Initialize new reference signals
mA_new = zeros(size(t)); % New reference for phase A
mB_new = zeros(size(t)); % New reference for phase B
mC_new = zeros(size(t)); % New reference for phase C

% Common-mode signal calculation
for i = 1:length(t)
    % Find max, mid, and min values of mA, mB, mC
    max_val = max([mA(i), mB(i), mC(i)]);
    min_val = min([mA(i), mB(i), mC(i)]);
    mid_val = mA(i) + mB(i) + mC(i) - max_val - min_val;
    
    % Calculate common-mode signal (m_cm)
    if (max_val - min_val) < 0.5
        m_cm = min_val / 2;
    elseif (mid_val - min_val) < 0.5
        m_cm = (max_val - 0.5) / 2;
    else
        m_cm = mid_val / 2;
    end
    
    % Calculate new reference signals
    mA_new(i) = mA(i) + m_cm;
    mB_new(i) = mB(i) + m_cm;
    mC_new(i) = mC(i) + m_cm;
end

% Plotting the results
figure;
subplot(2,1,1);
plot(t, mA, 'r', t, mB, 'g', t, mC, 'b');
title('Original Modulation Signals');
legend('mA', 'mB', 'mC');
xlabel('Time (s)');
ylabel('Amplitude');

subplot(2,1,2);
plot(t, mA_new, 'r', t, mB_new, 'g', t, mC_new, 'b');
title('New Reference Signals with Common-Mode Component');
legend('mA\_new', 'mB\_new', 'mC\_new');
xlabel('Time (s)');
ylabel('Amplitude');
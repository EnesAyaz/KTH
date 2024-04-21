load('\\ug.kth.se\dfs\home\e\n\enesa\appdata\xp.V2\Desktop\OneDrive_1_3-28-2024\measuredData.mat');
%%
time=Data.Time;
U_RS=Data.U_R1_S1;
U_TS=-Data.U_S1_T1;
I_R=Data.I_R1;
I_T=Data.I_T1;


% Define the time vector
T = time(end)-time(1); % Period of the signal
Fs=1/(time(2)-time(1)); % Sampling frequency   
t = time; % Time vector

% Define the time domain signal x(t)
% Example: square wave
x = square(2*pi*5*t); % Square wave with frequency 5 Hz

% Calculate the Fourier series coefficients
N = 1000; % Number of coefficients to calculate
a = zeros(1,N);
b = zeros(1,N);

for n = 1:N
    % Calculate coefficients a_n and b_n using numerical integration
    a(n) = (2/T) * trapz(t, x.*cos(2*pi*n*t/T));
    b(n) = (2/T) * trapz(t, x.*sin(2*pi*n*t/T));
end

% Calculate the DC term (a0) separately
a0 = (2/T) * trapz(t, x);

% Compute the Fourier series approximation
f = @(t) a0/2; % Initialize with DC term

for n = 1:N
    f = @(t) f(t) + a(n)*cos(2*pi*n*t/T) + b(n)*sin(2*pi*n*t/T);
end

% Plot original signal and Fourier series approximation
figure;
subplot(2,1,1);
plot(t, x);
title('Original Signal');
xlabel('Time (s)');
ylabel('Amplitude');

subplot(2,1,2);
plot(t, f(t));
title('Fourier Series Approximation');
xlabel('Time (s)');
ylabel('Amplitude');


% Sample time and frequency
Fs = 1000; % Sampling frequency (Hz)
T = 1/Fs; % Sampling period
L = 1000; % Length of signal
t = (0:L-1)*T; % Time vector

% Define input voltages for phases A, B, and C (time-domain waveforms)
Va = sin(2*pi*50*t); % Example waveform for Va
Vb = sin(2*pi*50*t - 2*pi/3); % Example waveform for Vb (shifted by 120 degrees)
Vc = sin(2*pi*50*t + 2*pi/3); % Example waveform for Vc (shifted by -120 degrees)

a=(-1+1i*sqrt(3))/2;

A= [1 1 1 ; 1 a a^2 ; 1 a^2 a]/3;

U_RST=[Va; Vb; Vc];

V= A*U_RST;
%%
V0= V(1,:);
Vp= V(2,:);
Vn= V(3,:);
%%

plot(t,V0)
hold on;
plot(t,real(Vp))
hold on;
% plot(t,imag(conj(Vp)))
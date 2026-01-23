% Parameters
fs  = 200e3;          % sampling frequency
T   = 0.05;           % simulation time
t   = (0:1/fs:T-1/fs)';

f1 = 200;  D1 = 0.2; ph1 = deg2rad(0);   % wave 1
f2 = 1400;  D2 = 0.2; ph2 = deg2rad(0);  % wave 2

fd = 2800;            % dither frequency for replacing level-1
Dd = 0.5;             % must be 0.5 for average=1

% Helper: 0/1 square with duty and phase
sq01 = @(f,D,ph) double(mod(t + ph/(2*pi*f), 1/f) < D/f);

x1 = sq01(f1,D1,ph1);
x2 = sq01(f2,D2,ph2);

s  = x1 + x2;                 % {0,1,2}
c  = sq01(fd,Dd,0);           % {0,1} 50% duty carrier
y  = zeros(size(s));          % final {0,2}

y(s==0) = 0;
y(s==2) = 2;
y(s==1) = 2*c(s==1);
y=y/2;

% Plot
figure; 
subplot(4,1,1); stairs(t,x1,'LineWidth',1); ylim([-0.2 1.2]); title('x1 (0/1)');
subplot(4,1,2); stairs(t,x2,'LineWidth',1); ylim([-0.2 1.2]); title('x2 (0/1)');
subplot(4,1,3); stairs(t,s ,'LineWidth',1); ylim([-0.2 2.2]); title('s = x1+x2 (0/1/2)');
subplot(4,1,4); stairs(t,y ,'LineWidth',1); ylim([-0.2 2.2]); title('y (only 0/2, dithered when s=1)');

% Quick check: average during s==1 region (global, not windowed)
if any(s==1)
    fprintf('Mean(y | s==1) = %.4f (target ~1)\n', mean(y(s==1)));
end

%%

%% FFT magnitude of y (linear scale)
N  = length(y);
df = fs/N;

% Window to reduce leakage
w   = hann(N);
Wcg = sum(w)/N;

% FFT → single-sided magnitude
Y  = fft(y .* w, N);
P2 = abs(Y) / (N*Wcg);
P1 = P2(1:floor(N/2)+1);
P1(2:end-1) = 2*P1(2:end-1);

% Frequency axis
f = (0:floor(N/2))' * df;

% Plot (set fmax as needed)
fmax = 50e3;
idx  = f <= fmax;

figure;
plot(f(idx), P1(idx), 'LineWidth', 1);
grid on;
xlabel('Frequency (Hz)');
ylabel('Magnitude |Y(f)|');
title('FFT magnitude of y (linear scale)');
xlim([0 5e3])


% Parameters
N = 360*10;                 % Number of samples in one carrier period
DA = 0.2; 
DB = 0.6; 
DC = 0.7;   % Duty cycles

phase_x=(DC-0.6)*pi;
% Phase shifts in radians (0 to 2*pi)
phiA = phase_x-(DA)*pi;            
phiB = phase_x-(DB+2*DA)*pi;          % 60° phase shift
phiC = phase_x+DC*pi;        % 120° phase shift

% Time vector for one period
x = linspace(0, 2*pi, N);

% Triangular carriers with phase shift
carrierA = sawtooth(x + phiA, 0.5);   % -1..1 triangle
carrierB = sawtooth(x + phiB, 0.5);
carrierC = sawtooth(x + phiC, 0.5);

% Scale to 0..1
carrierA = (carrierA+1)/2;
carrierB = (carrierB+1)/2;
carrierC = (carrierC+1)/2;

% Generate PWM (compare duty ratio with carrier)
pwmA = double(DA > carrierA);
pwmB = double(DB > carrierB);
pwmC = double(DC > carrierC);

% Plot
figure;
subplot(4,1,1); plot(x*180/pi, pwmA, 'b'); ylim([-0.2 1.2]); xlim([0 360]); title('PWM A'); grid on;
subplot(4,1,2); plot(x*180/pi, pwmB, 'r'); ylim([-0.2 1.2]); xlim([0 360]);title('PWM B'); grid on;
subplot(4,1,3); plot(x*180/pi, pwmC, 'k'); ylim([-0.2 1.2]); xlim([0 360]);title('PWM C'); grid on;
subplot(4,1,4); plot(x*180/pi, (pwmA+pwmB+pwmC)/2, 'k'); ylim([-0.2 1.2]); xlim([0 360]); title('PWM C'); grid on;
xlabel('Angle (rad)');

%%


% Parameters
N = 1000;                 % Number of samples in one carrier period
DA = 0.5; 
DB = 0.4; 
DC = 0.6;   % Duty cycles

% Phase shifts in radians (0 to 2*pi)
phiA = -(DA)*pi;            
phiB = -(DB+2*DA)*pi;      
phiC = DC*pi;        % 120° phase shift

% Time vector for one period
x = linspace(0, 2*pi, N);

% Triangular carriers with phase shift
carrierA = sawtooth(x + phiA, 0.5);   % -1..1 triangle
carrierB = sawtooth(x + phiB, 0.5);
carrierC = sawtooth(x + phiC, 0.5);

% Scale to 0..1
carrierA = (carrierA+1)/2;
carrierB = (carrierB+1)/2;
carrierC = (carrierC+1)/2;

% Generate PWM (compare duty ratio with carrier)
pwmA = double(DA > carrierA);
pwmB = double(DB > carrierB);
pwmC = double(DC > carrierC);

% Plot
figure;
subplot(4,1,1); plot(x*180/pi, pwmA, 'b'); ylim([-0.2 1.2]); xlim([0 360]); title('PWM A'); grid on;
subplot(4,1,2); plot(x*180/pi, pwmB, 'r'); ylim([-0.2 1.2]); xlim([0 360]);title('PWM B'); grid on;
subplot(4,1,3); plot(x*180/pi, pwmC, 'k'); ylim([-0.2 1.2]); xlim([0 360]);title('PWM C'); grid on;
subplot(4,1,4); plot(x*180/pi, (pwmA+pwmB+pwmC)/2, 'k'); ylim([-0.2 1.2]); xlim([0 360]); title('PWM C'); grid on;
xlabel('Angle (rad)');


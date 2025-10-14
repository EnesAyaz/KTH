% Parameters
N = 360*10;                 % Number of samples in one carrier period

theta = 100;                  % degrees
theta = theta*pi/180;       % radians
ma = 0.8;

% Duty ratios (single-period constants)
DA = (ma*sin(theta)            + 1)/2; 
DB = (ma*sin(theta - 2*pi/3)   + 1)/2;  
DC = (ma*sin(theta + 2*pi/3)   + 1)/2;  

% ---- Order-agnostic phase definition ----
% Sort duties and remember which leg each belongs to
D = [DA, DB, DC];
[Ds, idxAsc] = sort(D, 'ascend');   % Ds = [Dmin, Dmid, Dmax]
Dmin = Ds(1); Dmid = Ds(2); Dmax = Ds(3);

% Your original structure generalized by "roles":
%   role_min  -> was A-formula
%   role_mid  -> was B-formula (uses Dmid and Dmin)
%   role_max  -> was C-formula
phase_x = (0.75-Dmax)*2*pi;
% phase_x=0;

phi_role_min = phase_x - (Dmin)*pi;             % like phiA
phi_role_mid = phase_x - (Dmid + 2*Dmin)*pi;    % like phiB
phi_role_max = phase_x + (Dmax)*pi;             % like phiC

% Map role phases back to legs A/B/C
phi_all = zeros(1,3);
phi_all(idxAsc(1)) = phi_role_min;   % leg with smallest D gets "A-role" phase
phi_all(idxAsc(2)) = phi_role_mid;   % leg with middle   D gets "B-role" phase
phi_all(idxAsc(3)) = phi_role_max;   % leg with largest  D gets "C-role" phase

% Wrap phases into [0, 2*pi) to be safe
phi_all = mod(phi_all, 2*pi);
phiA = phi_all(1); phiB = phi_all(2); phiC = phi_all(3);

% Time vector for one carrier period
x = linspace(0, 2*pi, N);

% Triangular carriers with phase shift (range -1..1), then scale to 0..1
carrierA = (sawtooth(x + phiA, 0.5) + 1)/2;
carrierB = (sawtooth(x + phiB, 0.5) + 1)/2;
carrierC = (sawtooth(x + phiC, 0.5) + 1)/2;

% Generate PWM (compare duty ratio with carrier)
pwmA = double(DA > carrierA);
pwmB = double(DB > carrierB);
pwmC = double(DC > carrierC);

% Plots
figure;
subplot(4,1,1); plot(x*180/pi, pwmA, 'b'); ylim([-0.2 1.2]); xlim([0 360]); title('PWM A'); grid on;
subplot(4,1,2); plot(x*180/pi, pwmB, 'r'); ylim([-0.2 1.2]); xlim([0 360]); title('PWM B'); grid on;
subplot(4,1,3); plot(x*180/pi, pwmC, 'k'); ylim([-0.2 1.2]); xlim([0 360]); title('PWM C'); grid on;
subplot(4,1,4); plot(x*180/pi, (pwmA+pwmB+pwmC)/3, 'k'); ylim([-0.2 1.2]); xlim([0 360]); title('(pwmA+pwmB+pwmC)/3'); grid on;
xlabel('Angle (deg)');

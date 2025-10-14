% Parameters
N = 360*10;                 % Samples per carrier period
theta_deg = 100;            % degrees
theta = theta_deg*pi/180;   % radians
ma = 0.8;                   % modulation index for single-period test

% Single-period leg "targets" in [-1,1] (like average leg refs)
rA = ma*sin(theta);
rB = ma*sin(theta - 2*pi/3);
rC = ma*sin(theta + 2*pi/3);

% If you want to keep the exact same duty-based role logic:
DA = (rA + 1)/2;  DB = (rB + 1)/2;  DC = (rC + 1)/2;

% ---- Order-agnostic role assignment (same as your code) ----
D  = [DA, DB, DC];
[Ds, idxAsc] = sort(D, 'ascend');   % Ds = [Dmin, Dmid, Dmax]
Dmin = Ds(1); Dmid = Ds(2); Dmax = Ds(3);

% Role phases (your structure)
phase_x = (0.75 - Dmax)*2*pi;   % you can tune this pivot if needed
phi_role_min = phase_x - (Dmin)*pi;            % like phiA
phi_role_mid = phase_x - (Dmid + 2*Dmin)*pi;   % like phiB
phi_role_max = phase_x + (Dmax)*pi;            % like phiC

% Map role phases back to legs A/B/C
phi_all = zeros(1,3);
phi_all(idxAsc(1)) = phi_role_min;
phi_all(idxAsc(2)) = phi_role_mid;
phi_all(idxAsc(3)) = phi_role_max;
phi_all = mod(phi_all, 2*pi);
phiA = phi_all(1); phiB = phi_all(2); phiC = phi_all(3);

% Time vector for one carrier period
x = linspace(0, 2*pi, N);

% 3-level carrier scheme (mirrored thresholds):
% c_i in [-1,1]; thresholds are +c_i (upper) and -c_i (lower)
cA = sawtooth(x + phiA, 0.5);   % -1..1 triangle
cB = sawtooth(x + phiB, 0.5);
cC = sawtooth(x + phiC, 0.5);

% Vectorize references for comparison
rA_vec = rA * ones(size(x));
rB_vec = rB * ones(size(x));
rC_vec = rC * ones(size(x));

% 3-level decision (per sample):
% +1 if r >= +c, -1 if r <= -c, else 0
vA =  (rA_vec >=  cA) - (rA_vec <= -cA);
vB =  (rB_vec >=  cB) - (rB_vec <= -cB);
vC =  (rC_vec >=  cC) - (rC_vec <= -cC);

% Plots
figure;
subplot(5,1,1); plot(x*180/pi, vA, 'b'); ylim([-1.2 1.2]); xlim([0 360]);
title('3L PWM Leg A (v_A \in \{-1,0,1\})'); grid on;

subplot(5,1,2); plot(x*180/pi, vB, 'r'); ylim([-1.2 1.2]); xlim([0 360]);
title('3L PWM Leg B'); grid on;

subplot(5,1,3); plot(x*180/pi, vC, 'k'); ylim([-1.2 1.2]); xlim([0 360]);
title('3L PWM Leg C'); grid on;

subplot(5,1,4); plot(x*180/pi, (vA+vB+vC)/3, 'm'); ylim([-1.2 1.2]); xlim([0 360]);
title('(v_A + v_B + v_C)/3'); grid on;

subplot(5,1,5); plot(x*180/pi, [cA; cB; cC]'); xlim([0 360]);
title('Mirrored 3L carriers (per-leg phase-shifted)'); grid on; ylabel('c_i');
xlabel('Angle (deg)');

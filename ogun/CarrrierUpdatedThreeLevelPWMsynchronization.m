% -------- Parameter
N = 360*10;
theta_deg = 200;  
theta = theta_deg*pi/180;
ma = 0.8;

% leg references in [-1,1]  (single-period constants for this test)
rA = ma*sin(theta);
rB = ma*sin(theta - 2*pi/3);
rC = ma*sin(theta + 2*pi/3);

%Duties
if rA>0
DA = rA;
else
DA = rA+1;  
end

if rB>0
DB = rB;
else
DB = rB+1;  
end

if rC>0
DC = rC;
else
DC = rC+1;  
end

% -------- Order role phases (your logic) --------
D  = [DA, DB, DC];
[Ds, idxAsc] = sort(D, 'ascend');
Dmin = Ds(1); Dmid = Ds(2); Dmax = Ds(3);


phi_role_min = -(Dmin)*pi;
phi_role_mid = -(2*Dmin+Dmid)*pi;
phi_role_max = -(2*Dmin+2*Dmid+Dmax)*pi;


phi_all = zeros(1,3);
phi_all(idxAsc(1)) = phi_role_min;
phi_all(idxAsc(2)) = phi_role_mid;
phi_all(idxAsc(3)) = phi_role_max;
phi_all = mod(phi_all, 2*pi);
phiA = phi_all(1); phiB = phi_all(2); phiC = phi_all(3);

phi_all = zeros(1,3);
phi_all(idxAsc(1)) = phi_role_min;
phi_all(idxAsc(2)) = phi_role_mid;
phi_all(idxAsc(3)) = phi_role_max;
phi_all = mod(phi_all, 2*pi);
phiA = phi_all(1); phiB = phi_all(2); phiC = phi_all(3);

% -------- Time base --------
x = linspace(0, 2*pi, N);

% -------- Choose carrier disposition type --------
use_POD = false;     % true -> Phase-Opposition (lower = -upper), false -> Phase-Dispositon (in-phase)

% -------- Build explicit upper/lower carriers per leg (like your figure) --------
tri01 = @(phi) (sawtooth(x + phi, 0.5) + 1)/2;   % 0..1 triangular, period 2π

% Upper carriers (0..1)
cuA = tri01(phiA);
cuB = tri01(phiB);
cuC = tri01(phiC);

% Lower carriers (-1..0)
if use_POD
    % Phase-Opposition Disposition: 180° time shift
    clA = tri01(mod(phiA + pi, 2*pi)) - 1;   % -> [-1,0]
    clB = tri01(mod(phiB + pi, 2*pi)) - 1;
    clC = tri01(mod(phiC + pi, 2*pi)) - 1;
else
    % Phase-Disposition: same phase
    clA = tri01(phiA) - 1;   % -> [-1,0]
    clB = tri01(phiB) - 1;
    clC = tri01(phiC) - 1;
end

% -------- Vectorize refs --------
rA_vec = rA * ones(size(x));
rB_vec = rB * ones(size(x));
rC_vec = rC * ones(size(x));

% -------- 3-level decision using explicit upper/lower carriers --------
% State v ∈ {-1,0,+1}
if rA_vec>0
vA =  (rA_vec >= cuA);
else
vA = -(rA_vec <= clA);
end

if rB_vec>0
vB =  (rB_vec >= cuB);
else
vB =  - (rB_vec <= clB);
end

if rC_vec>0
vC =  (rC_vec >= cuC);
else
vC = - (rC_vec <= clC);
end

% -------- Plots (incl. the upper/lower carriers you wanted) --------
figure;
subplot(5,1,1); plot(x*180/pi, vA,'Linewidth',2); ylim([-1.2 1.2]); xlim([0 360]); title('Leg A state v_A ∈ {-1,0,1}'); grid on
subplot(5,1,2); plot(x*180/pi, vB,'Linewidth',2); ylim([-1.2 1.2]); xlim([0 360]); title('Leg B state'); grid on
subplot(5,1,3); plot(x*180/pi, vC,'Linewidth',2); ylim([-1.2 1.2]); xlim([0 360]); title('Leg C state'); grid on
subplot(5,1,4); plot(x*180/pi, (vA+vB+vC)/3,'Linewidth',2); ylim([-1.2 1.2]); xlim([0 360]); title('(v_A+v_B+v_C)/3'); grid on
subplot(5,1,5); 
plot(x*180/pi, cuA, '-', x*180/pi, clA, '-','Linewidth',2); xlim([0 360]); 
legend('Upper carrier (A)','Lower carrier (A)'); title('Carriers per leg (A)'); grid on; xlabel('Angle (deg)')

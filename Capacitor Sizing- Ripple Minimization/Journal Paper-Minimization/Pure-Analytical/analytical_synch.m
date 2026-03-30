ma      = 0.8;      % Modulation index
Iph     = 0.8;      % Peak phase current (p.u.)
pf      = 1;     % Power factor (lagging)
Nsw     = 200;      % Switching intervals per fundamental period (resolution)

phi_pf  = acos(pf); % Power factor angle (rad)

thetax   = linspace(0, 2*pi, Nsw+1);
thetax   = thetax(1:end-1);   % Nsw points, one per switching interval
theta=thetax(200);

% Duty cycles (SPWM, da+db+dc = 1.5 always)
da_vec  = 0.5 + 0.5*ma*cos(theta);
db_vec  = 0.5 + 0.5*ma*cos(theta - 2*pi/3);
dc_vec  = 0.5 + 0.5*ma*cos(theta - 4*pi/3);

% Phase currents (lagging by phi_pf)
ia_vec  = Iph * cos(theta           - phi_pf);
ib_vec  = Iph * cos(theta - 2*pi/3 - phi_pf);
ic_vec  = Iph * cos(theta - 4*pi/3 - phi_pf);

A=[ da_vec, db_vec, dc_vec, ia_vec, ib_vec, ic_vec]


da= da_vec;
db= db_vec;
dc= dc_vec;


ia=ia_vec ; 
ib= ib_vec ;
ic=ic_vec;  

% Sector-based carrier phase shift selection
% Signs of (ia, ib, ic) determine which leg is lone-sign.
% One leg is always lone (opposite sign to the other two).
% theta_a is always the reference shifted leg (not necessarily 0).
%
% Rule:
%   Lone leg  → its carrier is the reference (internal phase = 0)
%   Bank leg 1 → START aligned with lone  → phase shift = 0 relative to lone
%   Bank leg 2 → END   aligned with lone  → phase shift = d_lone - d_bank2
%
% Expressed as absolute (theta_a, theta_b, theta_c) where we always
% keep one of them at 0 and shift the others accordingly.

sa = sign(ia);
sb = sign(ib);
sc = sign(ic);

if sa ~= sb && sa ~= sc          % (+--) or (-++) : lone = a
    % a is lone, bank = {b, c}
    % a is reference → theta_a = 0
    % b START aligned with a → theta_b = 0
    % c END   aligned with a → theta_c = da - dc
    theta_a = 0;
    theta_b = 0;
    theta_c = da - dc;

elseif sb ~= sa && sb ~= sc      % (-+-) or (+-+) : lone = b
    % b is lone, bank = {a, c}
    % b is reference → theta_b = 0
    % a START aligned with b → theta_a = 0
    % c END   aligned with b → theta_c = db - dc
    theta_a = 0;
    theta_b = 0;
    theta_c = db - dc;

else                             % (++-) or (--+) : lone = c
    % c is lone, bank = {a, b}
    % c is reference → theta_c = 0
    % a START aligned with c → theta_a = 0  (a is fixed reference)
    % b END   aligned with c → theta_b = dc - db
    theta_a = 0;
    theta_b = dc - db;
    theta_c = 0;

end

N   = 100000;
tau = linspace(0, 1, N+1);
tau = tau(1:end-1);

Sa_opt  = make_pulse(da, theta_a, tau);
Sb_opt  = make_pulse(db, theta_b, tau);
Sc_opt  = make_pulse(dc, theta_c, tau);



Sa_conv = make_pulse(da, 0, tau);
Sb_conv = make_pulse(db, 0, tau);
Sc_conv = make_pulse(dc, 0, tau);


icap_opt  = ia*Sa_opt  + ib*Sb_opt  + ic*Sc_opt  - mean(ia*Sa_opt  + ib*Sb_opt  + ic*Sc_opt) ;
icap_conv = ia*Sa_conv + ib*Sb_conv + ic*Sc_conv -mean(ia*Sa_conv + ib*Sb_conv + ic*Sc_conv);

figure;
plot(ia*Sa_opt) 
hold on 
plot(ib*Sb_opt) 
hold on 
plot(ic*Sc_opt) 
hold on 
hold on 
legend('Sa','Sb','Sc')

figure;
plot(icap_opt) 
hold on 
plot(icap_conv) 
hold on 
legend('Icap_opt','Icap_conv')


rms_opt  = sqrt(mean(icap_opt.^2));
rms_conv = sqrt(mean(icap_conv.^2));


reduction = 100*(rms_conv - rms_opt)/rms_conv;


fprintf('\n  RMS Results:\n');
fprintf('    Conventional RMS = %.6f p.u.\n', rms_conv);
fprintf('    Optimal RMS      = %.6f p.u.\n', rms_opt);
fprintf('    Reduction        = %.2f%%\n',     reduction);
fprintf('============================================================\n');



function s = make_pulse(d, theta, tau)
% MAKE_PULSE  Generate 0/1 switching function for given duty and phase.
    s_start = mod(theta, 1.0);
    s_end   = mod(theta + d, 1.0);
    if s_start < s_end
        s = double(tau >= s_start & tau < s_end);
    else
        s = double(tau >= s_start | tau < s_end);
    end
end


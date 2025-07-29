theta_f=45*pi/180;

ma=0.8;
VrefA = ma*cos(theta_f);
VrefB = ma*cos(theta_f-2*pi/3);
VrefC = ma*cos(theta_f+2*pi/3);

mc=0.8;
pf=0.9;
IphA = mc*cos(theta_f-acos(pf));
IphB = mc*cos(theta_f-2*pi/3-acos(pf));
IphC = mc*cos(theta_f+2*pi/3-acos(pf));


da=(1+VrefA)/2; 
db=(1+VrefB)/2; 
dc=(1+VrefC)/2; 




[theta_b_opt, theta_c_opt, min_rms] = optimize_interleaving_rms(IphB, IphC, db, dc)
rms_val = calculate_rms_no_shift(IphB, IphC, db, dc)


% Simulation parameters

N = 1000;
Ts = linspace(0, 1, N);

% Reference triangular carrier for phase A
carrier = sawtooth(2*pi*Ts, 0.5);  % symmetric triangle [-1,1]
shift_b = mod(theta_b_opt / 360, 1);
shift_c = mod(theta_c_opt / 360, 1);

% Create phase-shifted carriers
if 0
carrier_b = sawtooth(2*pi*(Ts - shift_b), 0.5);
carrier_c = sawtooth(2*pi*(Ts - shift_c), 0.5);
else
carrier_b = carrier;
carrier_c = carrier;
end


figure()
plot(Ts,carrier)
hold on
plot(Ts,carrier_b)
hold on 
plot(Ts,carrier_c)


SA= double(VrefA>carrier);
SB= double(VrefB>carrier_b);
SC= double(VrefC>carrier_c);

%%
figure()
plot(Ts,SA+1.5)
hold on
plot(Ts,SB)
hold on 
plot(Ts,SC-1.5)
%%

figure()
plot(Ts,SA*IphA)
hold on
plot(Ts,SB*IphB)
hold on 
plot(Ts,SC*IphC)
%%
figure()
plot(Ts,SA*IphA+SB*IphB+SC*IphC)
hold on


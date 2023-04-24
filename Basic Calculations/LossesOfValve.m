% This code calculates MOSFET power losses and thermal calculations 
% for a three-phase inverter system. 
% It first defines MOSFET datasheet parameters, system parameters, and ratings. 
% It then calculates the required number of chips based on the peak current limit, 
% and applies a safety margin, and calculates the thermal resistance of the valve.
% 
% The code then calculates the switching times of the MOSFETs
% based on the input capacitance, gate resistance, gate-source voltage,
% and threshold voltage.
% The reverse recovery losses are also calculated based on the reverse recovery charge,
% reverse recovery time, and diode forward voltage drop.
% 
% The code then initializes the junction temperature and calculates
% the conduction losses of each switch, as well as the total conduction
% loss of all switches. 
% The total switching loss and reverse recovery loss are then calculated, 
% and the efficiency of the system is calculated based on the total power and losses. 
% Finally, the junction temperature is calculated based on the 
% thermal resistance of the valve and the total power losses,
% and the loop continues until the junction temperature stabilizes.


%% MOSFET Power Losses and Thermal Calculations

% MOSFET datasheet parameters
Rds_on_25C = 37e-3;     % On-state resistance at 25C [Ohm]
Rds_on_175C = 84e-3;     % On-state resistance at 175C [Ohm]
I_soa=135; % chip SOA current limit (A);
cm= 0.4;  % current margin
rth_jc= 0.24;  % thermal resistance of j-c (K/W)
rth_ca= 1;  % thermal resistance of j-c (K/W)
Ta=40;  % cooling medium temperature (^o C)
Ipk=I_soa*(1-cm); % Chip peak current limit (A)
Vgs = 20; % gate-source voltage (volts)
Ciss = 3580e-12; % input capacitance (farads)
Coss = 180e-12; % output capacitance (farads)
Crss= 14e-12;   % Reverse transfer capacitance (farad)
Rg=5; % gate resistance (Ohm)
Vgs_th= 2.5; % Thrashold voltage (V)

% System parameters
Udnom= 1200 ;  % DC link voltage pole-pole (V);
ma=1.07;    % max modulation index

% Ratings
P= 600e3; % total power (W)
Ua= (Udnom/2)*ma/sqrt(2); % AC phase voltage (Vrms);
Ia = P/Ua/3;   % AC phase current (Arms)
Iap= Ia*sqrt(2);  % AC phase peak current (Apk)
fsw=20e3;


% Finding valve parameters
Nchip1= Iap/Ipk; % required no of chips
sm=1.3; % safe margin of  current limit
Nchip=round(Nchip1*sm); %% actual no of chips
Rth_jc_valve=rth_jc/Nchip;
Rth_ja_valve= Rth_jc_valve+ rth_ca/Nchip;


% Calculate the switching time assuming linear waveforms
Qoss = Udnom * Coss*Nchip; % output charge
Qiss = Vgs * Ciss*Nchip; % input charge
td_on = abs(Rg * Ciss * log((Vgs - Vth)/Vgs)); % turn-on delay time
tr = Qoss/Ia; % turn-on rise time
td_off =abs( Rg * Coss * log(Udnom/(Udnom - Vgs))); % turn-off delay time
tf = Qiss/Ia; % turn-off fall time

% Reverse recovery parameters (datasheets)
Vfwd = 4; % diode forward voltage drop (V)
Qrr= 1666e-6 ;  %Reverse Recovery Charge (C)
trr= 25e-9;     %Reverse Recovery Time (s)

% Paramater initalization
Tj_init=Ta; % initial junction temp 
rdson_Tj= Rds_on_25C+ ((Rds_on_175C-Rds_on_25C)/(175-25))*Tj_init;
Rds_on=rdson_Tj/Nchip;

while 1

Pl_v=(Ia^2*Rds_on)/2; % conduction loss of one switch (W)
Pl_tot_con=Pl_v*6; % total conduction loss(W)


P_switch = (Ciss + Coss + Crss) * Udnom^2 * fsw ...
               + (td_on + tr) * Ia * Udnom / 2* fsw ...
               + (td_off + tf) * Ia * Udnom / 2* fsw; % switching loss of one switch

Irr = Qrr/trr; % reverse recovery current
P_diode = Vfwd*Irr/fsw; % reverse recovery power of one diode
 
Pl_tot= Pl_tot_con+P_switch*6+ P_diode*6; % rotal losses
eta=1-Pl_tot/P;% efficiency

Tj= Ta+ Pl_tot/6*Rth_ja_valve; % junction temperature of one valve

rdson_Tj= Rds_on_25C+ ((Rds_on_175C-Rds_on_25C)/(175-25))*Tj; % updating rds concerning Tj
Rds_on=rdson_Tj/Nchip; % rds of one valve

if (Tj-Tj_init)<0.01
    break
end

Tj_init=Tj; % previous junction temperature

end

[Tj,eta]




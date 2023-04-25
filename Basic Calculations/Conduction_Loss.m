run('CPM2_1700_0045A.m')
run('CPM2_1200_0025A.m')
run('system_parameters.m')
%% MOSFET Power Losses and Thermal Calculations

% MOSFET datasheet parameters
Rds_on_25C = Switch.Rds_on_25C;     % On-state resistance at 25C [Ohm]
Rds_on_175C = Switch.Rds_on_175C;     % On-state resistance at 175C [Ohm]
I_soa=Switch.I_soa; % chip SOA current limit (A);
cm= Switch.cm;  % current margin
rth_jc= Switch.rth_jc;  % thermal resistance of j-c (K/W)
Ipk=Switch.Ipk;   % Chip peak current limit (A)

%% System Parameters and Ratings
Ta=system.Ta;  % cooling medium temperature (^o C)
Udnom= system.Udnom ;  % DC link voltage pole-pole (V);
ma=system.ma;    % max modulation index
P= system.P; % total power (W)
Ua= system.Ua; % AC phase voltage (Vrms);
Ia = system.Ia;   % AC phase current (Arms)
Iap= system.Iap;  % AC phase peak current (Apk)

%% Finding valve parameters
Nchip1= Iap/Ipk; % required no of chips
sm=1.3; % safe margin of  current limit
Nchip=round(Nchip1*sm); %% actual no of chips
Rth_jc_valve=rth_jc/Nchip;

%% Initial paramaters
Tj_init=Ta; % initial junction temp 
rdson_Tj= Rds_on_25C+ ((Rds_on_175C-Rds_on_25C)/(175-25))*Tj_init;
Rds_on=rdson_Tj/Nchip;
%% İterative solution
while 1

Pl_v=(Ia^2*Rds_on)/2; % conduction loss of one switch (W)
Pl_tot=Pl_v*6; % total conduction loss(W)
eta=1-Pl_tot/P;% efficiency

Tj= Ta+ Pl_v*Rth_jc_valve; % updated junction temperature

rdson_Tj= Rds_on_25C+ ((Rds_on_175C-Rds_on_25C)/(175-25))*Tj; % updated on-state chip resistance
Rds_on=rdson_Tj/Nchip; % updated on-state resistance of the valve

if (Tj-Tj_init)<0.01
    break
end

Tj_init=Tj; % updated previous junction temperature

end
%%

[Tj,eta,rdson_Tj,Pl_v]




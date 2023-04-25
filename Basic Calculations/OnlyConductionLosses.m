%% MOSFET Power Losses and Thermal Calculations

% MOSFET datasheet parameters
Rds_on_25C = 37e-3;     % On-state resistance at 25C [Ohm]
Rds_on_175C = 84e-3;     % On-state resistance at 175C [Ohm]
I_soa=135; % chip SOA current limit (A);
cm= 0.4;  % current margin
rth_jc= 0.24;  % thermal resistance of j-c (K/W)
Ta=40;  % cooling medium temperature (^o C)
Ipk=I_soa*(1-cm); % Chip peak current limit (A)

Rds_on_25C = 25e-3;     % On-state resistance at 25C [Ohm]
Rds_on_175C = 43e-3;     % On-state resistance at 175C [Ohm]
I_soa=200; % chip SOA current limit (A);
cm= 0.4;  % current margin
rth_jc= 0.35;  % thermal resistance of j-c (K/W)
Ta=40;  % cooling medium temperature (^o C)
Ipk=I_soa*(1-cm); % Chip peak current limit (A)

% System parameters
Udnom= 1200 ;  % DC link voltage pole-pole (V);
ma=1.07;    % max modulation index

% Ratings
P= 600e3; % total power (W)
Ua= (Udnom/2)*ma/sqrt(2); % AC phase voltage (Vrms);
Ia = P/Ua/3;   % AC phase current (Arms)
Iap= Ia*sqrt(2);  % AC phase peak current (Apk)

% Finding valve parameters
Nchip1= Iap/Ipk; % required no of chips
sm=1.3; % safe margin of  current limit
Nchip=round(Nchip1*sm); %% actual no of chips
Nchip=10; %% actual no of chips
Rth_jc_valve=rth_jc/Nchip;

% Initial paramaters
Tj_init=Ta; % initial junction temp 
rdson_Tj= Rds_on_25C+ ((Rds_on_175C-Rds_on_25C)/(175-25))*Tj_init;
Rds_on=rdson_Tj/Nchip;

while 1

Pl_v=(Ia^2*Rds_on)/2; % conduction loss of one switch (W)
Pl_tot=Pl_v*6; % total conduction loss(W)
eta=1-Pl_tot/P;% efficiency

Tj= Ta+ Pl_v*Rth_jc_valve;

rdson_Tj= Rds_on_25C+ ((Rds_on_175C-Rds_on_25C)/(175-25))*Tj;
Rds_on=rdson_Tj/Nchip;

if (Tj-Tj_init)<0.01
    break
end

Tj_init=Tj;

end


[Tj,eta]




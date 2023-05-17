% Define a struct with some parameters and values
Switch.Rds_on_25C = 25e-3;     % On-state resistance at 25C [Ohm]
Switch.Rds_on_175C = 43e-3;    % On-state resistance at 175C [Ohm]
Switch.I_soa = 200;            % chip SOA current limit (A);
Switch.rth_jc = 0.35;           % thermal resistance of j-c (K/W)
Switch.cm= 0.4;  % current margin
Switch.Ipk=Switch.I_soa*(1-Switch.cm); % Chip peak current limit (A)

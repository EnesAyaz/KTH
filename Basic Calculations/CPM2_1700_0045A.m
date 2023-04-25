% Define a struct with some parameters and values
Switch.Rds_on_25C = 37e-3;     % On-state resistance at 25C [Ohm]
Switch.Rds_on_175C = 84e-3;    % On-state resistance at 175C [Ohm]
Switch.I_soa = 135;            % chip SOA current limit (A);
Switch.rth_jc = 0.24;           % thermal resistance of j-c (K/W)
Switch.cm= 0.4;  % current margin
Switch.Ipk=Switch.I_soa*(1-Switch.cm); % Chip peak current limit (A)

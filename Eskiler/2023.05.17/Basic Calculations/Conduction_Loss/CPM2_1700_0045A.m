% This code defines a struct called Switch with five fields: 
% Rds_on_25C, Rds_on_175C, I_soa, rth_jc, and cm.
% 
% The Rds_on_25C and Rds_on_175C fields represent
% the on-state resistance of a switch at 25°C and 175°C, 
% respectively, and are specified in units of ohms.
% 
% The I_soa field represents the current limit for the switch, 
% specified in amperes.
% 
% The rth_jc field represents the thermal resistance of the switch
% from junction to case, specified in units of kelvin per watt.
% 
% The cm field represents the current margin for the switch, 
% specified as a fraction of the current limit.
% For example, a cm value of 0.4 means that 
% the switch is designed to operate at a current 
% of 60 percent of its maximum rated current (i.e., 1 - cm = 0.6).
% 
% Finally, the Ipk field calculates the peak currentlimit of the switch,
% which is the maximum current the switch can handle before failing,
% taking into account the current margin specified in the cm field.
% 
% Overall, this struct is a representation of a switch device 
% and its specifications, and can be used in further calculations
% or simulations related to switch operation.

% Define a struct with some parameters and values
Switch.Rds_on_25C = 37e-3;     % On-state resistance at 25C [Ohm]
Switch.Rds_on_175C = 84e-3;    % On-state resistance at 175C [Ohm]
Switch.I_soa = 135;            % chip SOA current limit (A);
Switch.rth_jc = 0.24;           % thermal resistance of j-c (K/W)
Switch.cm= 0.4;  % current margin
Switch.Ipk=Switch.I_soa*(1-Switch.cm); % Chip peak current limit (A)

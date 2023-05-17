% This code defines a struct called system with six fields:
% Ta, Udnom, ma, P, Ua, and Ia.
% 
% The Ta field represents the temperature of the cooling medium, 
% specified in degrees Celsius.
% 
% The Udnom field represents the nominal DC link voltage of the system,
% specified in volts.
% 
% The ma field represents the maximum modulation index of the system,
% which is a measure of the extent to which 
% the amplitude of the AC waveform can be varied. 
% This value is dimensionless.
% 
% The P field represents the total power of the system, specified in watts.
% 
% The Ua field calculates the AC phase voltage of the system, 
% which is the effective (RMS) value of the AC waveform at the output of the inverter.
% This value is calculated using the formula Ua = (Udnom/2)*ma/sqrt(2).
% 
% The Ia field calculates the AC phase current of the system, 
% which is the effective (RMS) value of the current flowing through each phase of the AC output.
% This value is calculated using the formula Ia = P/Ua/3,
% where 3 is the number of phases in the system.
% 
% Finally, the Iap field calculates the peak AC phase current of the system,
% which is the maximum current that each phase of the AC output can handle before failing.
% This value is calculated using the formula Iap = Ia*sqrt(2).
% 
% Overall, this struct is a representation of a power electronic system and its ratings,
% and can be used in further calculations or simulations related to the operation 
% and performance of the system.



system.Ta=40;  % cooling medium temperature (^o C)
system.Udnom= 1200 ;  % DC link voltage pole-pole (V);
system.ma=1.07;    % max modulation index
system.P= 600e3; % total power (W)
system.Ua= (system.Udnom/2)*system.ma/sqrt(2); % AC phase voltage (Vrms);
system.Ia = system.P/system.Ua/3;   % AC phase current (Arms)
system.Iap= system.Ia*sqrt(2);  % AC phase peak current (Apk)
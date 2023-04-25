% Ratings
system.Ta=40;  % cooling medium temperature (^o C)
system.Udnom= 1200 ;  % DC link voltage pole-pole (V);
system.ma=1.07;    % max modulation index
system.P= 600e3; % total power (W)
system.Ua= (system.Udnom/2)*system.ma/sqrt(2); % AC phase voltage (Vrms);
system.Ia = system.P/system.Ua/3;   % AC phase current (Arms)
system.Iap= system.Ia*sqrt(2);  % AC phase peak current (Apk)
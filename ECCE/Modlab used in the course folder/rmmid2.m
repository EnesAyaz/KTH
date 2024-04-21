function sout = rmmid2(sin)
%Conversion phase potentials -> phase-to-load-midpoint voltages
%
% sout = rmmid2(sin)
%
% Conversion from phase potentials to phase-to-midpoint voltages in a
% three-phase system
%
sm = (1/3)*sum(sin);        % Load midpoint voltage
%
sout = sin - [sm ; sm ; sm];               % Voltage across load filter + load
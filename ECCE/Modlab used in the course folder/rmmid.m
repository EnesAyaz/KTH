function [v1, v2, v3] = rmmid[vp1, vp2, vp3]
%Conversion phase potentials -> phase-to-load-midpoint voltages
%
% [v1, v2, v3] = rmmid[vp1, vp2, vp3]
%
% Conversion from phase potentials to phase-to-midpoint voltages in a
% three-phase system
%
vm = (vp1 + vp2 + vp3)/3;        % Load midpoint voltage
%
v1 = vp1-vM;                % Voltage across line inductance
v2 = vp2-vM;
v3 = vp3-vM;
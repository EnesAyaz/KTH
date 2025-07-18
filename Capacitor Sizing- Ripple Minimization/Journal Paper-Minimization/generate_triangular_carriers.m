function [t, carrierA,carrierB,carrierC] = generate_triangular_carriers(fs, fsw, var_shiftB, var_shiftC)
% GENERATE_TRIANGULAR_CARRIERS Generate phase-shifted triangular carriers
% Inputs:
%   fs - Sampling frequency (Hz)
%   fsw - Switching frequency (Hz)
%   var_shiftB - Phase shift for carrier 2 (radians)
%   var_shiftC - Phase shift for carrier 3 (radians)
% Outputs:
% t - Time vector
% carrierA; % constant phase shift
% carrierB; % var_shiftB
% carrierC % var_shiftC

duration = 1/fsw;    % One switching period
t = 0:1/fs:duration; % Time vector

% Generate all three carriers
carrierA = sawtooth(2*pi*fsw*t, 0.5);               % Reference
carrierB = sawtooth(2*pi*fsw*t + var_shiftB, 0.5);   % Variable shift B
carrierC = sawtooth(2*pi*fsw*t + var_shiftC, 0.5);   % Variable shift C

end






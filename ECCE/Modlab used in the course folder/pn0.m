function sfout = pn0(sfin);
% abc -> pn0 conversion
%
% Extracts the positive, negative and the zero sequence from a set of three-phase
% phasors.
%
cmat=1/3*[1 exp(-j*2*pi/3) exp(j*2*pi/3) ; 1 exp(j*2*pi/3) exp(-j*2*pi/3) ; 1 1 1];
%
sfout=cmat*sfin;
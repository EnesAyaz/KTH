function sfout = abc2alfabeta(sfin);
% abc -> alfabeta conversion
%
% Converts from three-phase quantities to space vector
%
K=2/3;
%
cmat=[1 exp(j*2*pi/3) exp(-j*2*pi/3)];
%
sfout=K*cmat*sfin;
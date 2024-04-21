function [y]=itr_rms(s,theta0, fi, npoints);
%
% Computes the ratio of the transformer rms current to the phase rms
% current
% Verified against Simplorer 050307
%
% s is a vector of size 3 x npoints. s assumes the values 0 and 2.
% theta0:  phase angle shift of reference (and current)
% fi load angle
%
ktot=0.5*(s-1);
%
w0t=2*pi*(0:npoints-1)/npoints + theta0;
%
i1=cos(w0t-fi);
i2=cos(w0t-2*pi/3-fi);
i3=cos(w0t-4*pi/3-fi);
%
itrmod=ktot(1,:).*i1 + ktot(2,:).*i2 + ktot(3,:).*i3;
%
% Root mean square calculation
itr_rms=sqrt(mean(itrmod.^2));
%
y=sqrt(2)*itr_rms;              % ratio of xfmr rms current to phase rms current

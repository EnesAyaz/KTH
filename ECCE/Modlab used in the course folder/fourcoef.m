function C=fourcoef(s,n);
%
% Numerical calculation of Fourier coefficient by evaluation of the Fourier
% integral
%
%global xv s;
noofpoints=length(s);
xv=2*pi*(0:noofpoints-1)/noofpoints;
C=1/(2*pi)*quad( @ignd,0,2*pi,1e-6,[],n,xv,s);
%
function y= ignd(x,n,xv,s);
%global xv s;
s1 = interp1(xv,s,x,'linear','extrap');
y=s1.*exp(-j*n*x);
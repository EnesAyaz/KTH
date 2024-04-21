% Notch modulation
%
alpha1=0; %pi/2-0.1;
%
N=2^12;
%
wt=2*pi*(0:N-1)/N;
wt1=wt(1:2^10);
%
s=2*(wt1<alpha1)-1;
s=[s s(end:-1:1)];
s=[s -s];
%
Sf=fourser(s,12);
%
h=1:11;
%
Sfana=(4/pi)./h.*(1-2*cos(h*alpha1));
Sfana(2:2:11)=0;
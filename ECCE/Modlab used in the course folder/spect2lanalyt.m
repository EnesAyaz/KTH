function V = spect2lanalyt(p,M,nharm,meth,theta0,thetac)
% spect2lanalyt.m
%
% Analytic computation of harmonic spectra of 2-level unconstrained modulation with
% natural sampling. The file returns the corresponding Fourier
% coefficients. 
%
% V = spect2lanalyt(p,M,nharm,meth,theta0,thetac)
%
% p: pulse number
% M: Modulation index
% nharm: number of harmonics to compute
% meth: modulation method
%       meth='tria' -> triangular carrier
%       meth='sawp' -> sawtooth carrier with rising slope
% theta0: phase of fundamental
% thetac: phase of carrier
%
mmax=round(nharm/p)+2;
%
V=zeros(1,nharm);

V(1)=0; % Assume bipolar signal
V(2)=M/2*exp(j*theta0);

for k=1:nharm-1,
    loop=1;
    m=1;
    Vc=0;
    while loop,
        n=k-p*m;
        nm=k+p*m;   % DEBUG
        Vc=harm(m,n,M,meth)*exp(j*(theta0*n+thetac*m));%  + harm(-m,nm,M,meth); % DEBUG
        V(k+1)=V(k+1)+Vc;
        m=m+1;
        if abs(Vc)<0.0001 & m>mmax,
            loop=0;
        end;        
    end;
end;

function V = harm(m,n,M,meth)
if meth=='sawp'
    
    if n==0,
        V=j/m/pi*(besselj(0,m*M*pi)-cos(m*pi));
    else
        V=1/m/pi*besselj(n,m*M*pi)*(sin(n*pi/2)+j*cos(n*pi/2));
    end;
    
elseif meth=='tria'
    
    if n==0,
        V=2/m/pi*besselj(0,m*M*pi/2)*sin(m*pi/2);
    else
        V=2/m/pi*besselj(n,m*M*pi/2)*sin((m+n)*pi/2);
    end;
else
    error(['Method ' meth ' not implemented'])
end;
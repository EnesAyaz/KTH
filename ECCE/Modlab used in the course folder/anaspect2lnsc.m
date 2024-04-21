function V = anaspect2lnsc(M, p, theta0, thetac, phi, nharm);
%
% Analytically computes the spectrum of 2-level  naturally sampled 
% constrained modulation
%
% Staffan Norrga 2004-2005
%
% V = anaspect2lnsc(M, p, theta0, thetac, phi, nharm);
%
% M: Modulation index
% p:pulse number
% theta0: reference phase displacement
% thetac: carrier phase displacement
% phi: load angle
% nharm: number of harmonics

    offs=1;  % index minus harmonic order
    
    V=zeros(1,nharm);
    V(offs+0)=0.5;      % DC component
    V(offs+1)=M*exp(j*theta0);
    for k=1:1:nharm-offs,
        m=1;
        mloop=1;
        while mloop,
            nmp=k-m*p; % Contribution from sideband around m*p
            nmm=k+m*p; % Contribution from sideband around -m*p            
            Vcmp=sband1plja(nmp,m,M,phi,theta0,thetac); % sideband at w0(m+nmp)
            Vcmm=sband1plja(nmm,-m,M,phi,theta0,thetac); % sideband at w0(-m+nmm)
            % Vcmm=0;
            Vc=2*(Vcmp+Vcmm);   % '2': Fourier coeff->magnitude of harmonic
            V(k + offs)=V(k + offs)+Vc;
            mloop= ~(m >19);% mloop= ~(( abs(Vc)<=0.001*abs(V(k)) & m>4 ) | m >20); %
            m=m+1;
        end;
        % k
        % m
    end;
 
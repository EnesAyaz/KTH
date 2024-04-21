function V = anaspect1ph3lnsc(M, p, theta0, thetac, phi, nharm);
%
% Analytically computes the spectrum of 3-level single phase naturally sampled 
% constrained modulation
%
% Staffan Norrga 2004-2005
%
% V = anaspect1ph3lnsc(M, p, theta0, thetac, phi, nharm);
%
% M: Modulation index
% p:pulse number
% theta0: reference phase displacement
% thetac: carrier phase displacement
% phi: load angle
% nharm: number of harmonics

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % THIS PART IS NUMERICALLY VERIFIED AND SHOULD NOT BE CHANGED     

    offs=1;  % index minus harmonic order
    
    V=zeros(1,nharm);
    V(offs+0)=0.0  % DC component
    V(offs+1)=2*M*exp(j*(theta0)); % fundamental
    %
    % Iterate to get sideband contributions
    %
    for k=1:2:nharm-offs,
        m=1;
        mloop=1;
        while mloop,
            nmp=k-m*p;
            nmm=k+m*p;
            Vcmp=sband1pja(nmp,m,M,phi, theta0,thetac);  % Contribution from sideband around m*p
            Vcmm=sband1pja(nmm,-m,M,phi, theta0,thetac); % Contribution from sideband around -m*p
            % Vcmm=0;
            Vc=2*(Vcmp+Vcmm);
            V(k+offs)=V(k+offs)+Vc;
            mloop= ~(m>14); % mloop= ~(( abs(Vc)<0.01*abs(V(k)) & m>6 ) | m >20);
            m=m+1;
        end;
        %k
        %m
    end;
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

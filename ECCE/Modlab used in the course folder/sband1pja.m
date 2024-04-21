function [y, varargout]=sband1pja(n,m,M,phi, theta0,thetac, varargin);
% sband1pja: Calculation of sideband harmonics using the Jacobi-Anger expansion
% Single-phase three level modulation
%
% [y, varargout]=sband1pja(n,m,M,phi, theta0,thetac, varargin);
% 
% y: harmonic fourier component
% n: baseband index 
% m: sideband index
% M: Modulation index
% phi: load angle
% theta0: reference phase displacement
% thetac: carrier phase displacement
% method (optional): calculation method


if nargin >6,
    if isempty(varargin{1}),
        meth='ucfc';
    else
        meth=varargin{1};
    end;
else 
    meth='ucfc';
end;

if rem(n,2)==0,  % Even sideband?
    y=0;
else             % No, odd sideband!
    
    if meth=='orig' | meth=='both',
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % THIS PART IS NUMERICALLY VERIFIED AND SHOULD NOT BE CHANGED     
        
        xi=2*pi*m*M;
        sum1=0;
        k=2;
        loop=1;
        while loop,
            delta=besselj(k,xi)*(n*cos(k*phi) - k*j*sin(k*phi))/(n^2-k^2);
            sum1 = sum1+delta;
            if (k > 2*abs(n)) & abs(delta)<0.001*abs(sum1),
                loop=0;
            end
            k=k+2;
        end
        % k
        itgrl = 2*j^(n-1)*exp(j*n*phi)*(besselj(0,xi)/n + 2*sum1) - j^n*pi*besselj(n,xi);
        
        y=-2/(j*m*pi^2)*(-1)^m*( j^n*itgrl + 2*exp(j*n*phi)/j/n ); % Original
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        y=y*exp(-j*(theta0*n+thetac*m));
        
    end;
    
    
    
    if meth=='ucfc' | meth=='both',
        
        % 'ucfc' gives unconjugated complex Fourier coefficients
        % Verified against orig    
        xi=2*pi*m*M;
        sum1=0;
        k=2;
        loop=1;
        while loop,
            delta=besselj(k,xi)*(k*j*sin(k*phi) + n*cos(k*phi))/(n^2-k^2);
            sum1 = sum1+delta;
            if (k > 2*abs(n)) & abs(delta)<0.001*abs(sum1),
                loop=0;
            end
            k=k+2;
        end
        % k
        fact=  2/m/pi^2*(-1)^m*j^n;
        term1= exp(-j*n*phi)/n;
        term2= -exp(-j*n*phi)*besselj(0,xi)/n;
        term3= -2*exp(-j*n*phi)*sum1;
        term4= -j*pi*besselj(n,xi)/2;
        
        y= fact*(term1+term2+term3+term4);
        
        y= y*exp(j*(theta0*n+thetac*m));
        
        if nargout > 1   
            
            % terms requested
            varargout{1}=[term1 term2 term3 term4];
        end;
        
        %diff2= y*j^(-n) - 2*conj(ytest2)
        
    end; % End of method ucfc
    
    if meth=='hghn',
        
        % hghn gives unconjugated complex Fourier coefficients
        % approximated at high values of abs(n)
        
        xi=2*pi*m*M;
        % k
        fact=  2/m/n/pi^2*(-1)^m*j^n*exp(-j*n*phi);
        
        y= fact*(1-cos(xi*sin(phi)));
        
        y= y*exp(j*(theta0*n+thetac*m));
        
        %diff2= y*j^(-n) - 2*conj(ytest2)
        
    end; % End of method hghn
    
end; % End of odd sideband calc

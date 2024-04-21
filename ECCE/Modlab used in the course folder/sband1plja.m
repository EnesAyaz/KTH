function [y, varargout]=sband1plja(n,m,M,phi,theta0,thetac, varargin);
%
% Calculation of sideband harmonics for a single phase leg with constrained modulation using the Jacobi-Anger expansion
%
% [y, varargout]=sband1plja(n,m,M,phi,theta0,thetac, varargin);
% 
% y: harmonic fourier component
% n: baseband index 
% m: sideband index
% M: Modulation index
% phi: load angle
% theta0: reference phase displacement
% thetac: carrier phase displacement
% method (optional): calculation method
%
if nargin >6,
    if isempty(varargin{1}),
        meth='ucfc';
    else
        meth=varargin{1};
    end;
else 
    meth='ucfc';   % 'ucfc'= unconjugated Fourier coefficients
end;


if meth=='orig' | meth=='both',
    
    if rem(n,2)==0,  % Even sideband?
        y=0;
    else             % No, odd sideband!
        
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % THIS PART IS NUMERICALLY VERIFIED AND SHOULD NOT BE CHANGED    
        xi=pi*m*M;
        sum1=0;
        k=2;
        loop=1;
        while loop,
            if n~=k,
                delta=besselj(k,xi)*(j*n*cos(k*phi) + k*sin(k*phi))/(n^2-k^2);
            else
                delta=0;
            end
            sum1 = sum1+delta;
            if ((k > 2*abs(n)) & abs(delta)<0.001*abs(sum1)) | k>4*abs(n),
                loop=0;
            end
            k=k+2;
        end
        k;
        
        itgr01 = 2*j^(n+1)*besselj(0,xi)*exp(j*n*phi)/n +...
            4*exp(j*n*phi)*j^n*sum1+...
            j^n*pi*besselj(n,xi);
        
        y= (-2/(m*pi^2)*(...
            j*itgr01+...
            2*exp(j*n*phi)*j^n*(-1)^m/n ));
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        y=y*exp(-j*(theta0*n+thetac*m));
    end; % End of calc for odd sideband
end; % End of method 'orig'


if meth=='ucfc' | meth=='both',
    % ucfc gives unconjugated complex Fourier coefficients
    % Verified against orig!
    if rem(n,2)==0,   % Even sideband?
        y=0;
    else              % No, odd sideband!
        xi=pi*m*M;
        sum1=0;
        k=2;
        loop=1;
        while loop,
            if n~=k,
                delta=besselj(k,xi)*(j*k*sin(k*phi) + n*cos(k*phi))/(n^2-k^2);
            else
                delta=0;
            end
            sum1 = sum1+delta;
            if ((k > 2*abs(n)) & abs(delta)<0.001*abs(sum1)) | k>4*abs(n),
                loop=0;
            end
            k=k+2;
        end
        fact=2/m/pi^2*j^n; % '2' comes from (1-(-1)^n) in the original expression
        term1=(-1)^m/n*exp(-j*n*phi);
        term2=-besselj(0,xi)*exp(-j*n*phi)/n;
        term3=-2*exp(-j*n*phi)*sum1;
        term4=-j*pi*besselj(n,xi)/2;
        y= fact*(term1+term2+term3+term4);
        
        % sumtest1=term1+term2+term3
        
        y=y*exp(j*(theta0*n+thetac*m));
        
        if nargout > 1   
            % terms requested
            varargout{1}=[term1 term2 term3 term4];
        end;
        
    end;  % End of calc for odd sideband
end; % End of method 'ucfc'


if meth=='hnfc'
    % 'hnfc' gives unconjugated complex Fourier coefficients
    % Approximation valid at high values of n
    if rem(n,2)==0,   % Even sideband?
        y=0;
    else              % No, odd sideband!
        xi=pi*m*M;
        fact=2/m/n/pi^2*j^n*exp(-j*n*phi);
        y= fact*( (-1)^m - cos(xi*sin(phi)) );
        
        y=y*exp(j*(theta0*n+thetac*m));
        
    end;  % End of calc for odd sideband
end; % End of method 'hnfc'

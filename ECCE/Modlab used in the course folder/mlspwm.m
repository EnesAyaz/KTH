function [stot, varargout]=mlspwm(ma, p, nlev, theta0, npts, type, opt, varargin)
% mlswpm : produces sampled version of multilevel carrier-based modulation pattern during  exactly fundamental one cycle
%
% [stot {, wt} {, ref} {, carr} {, slev}]=mlspwm(ma, p, nlev, theta0, npts,type, refinj,theta_c, scale);
%
% ma        modulation index
% p         pulse number
% nlev      number of levels
% theta0    fundamental phase displacement
% npts      number of samples 
% type      type of modulation
%               = 'pcs' -> Phase shifted carriers
%               = 'pc2' -> M2LC phase shifted carriers
%               = 'sc1' -> Stacked carriers with equal phase 'PD'
%               = 'sc2' -> Stacked carriers with alternative phase opposition 'APOD'
%               = 'sc3' -> Stacked carriers with phase opposition 'POD'
% opt       reference injection
%               = 'none' -> pure cosine reference
%               = '3rd1' -> one 6th third harmonic
%
wt=2*pi*(0:npts-1)/npts;

ncarr=nlev-1;          % Number of carriers

udlev=1/ncarr;         % Normalised DC-band for one level


if nargin > 7
    theta_c = varargin{1};
else
    theta_c = 0;
end;

if nargin > 8
   scale = varargin{2};
else
    if strcmp(type,'pcs') | type == 'pc2'
       scale = 1;
    else 
       scale = ncarr/2;
    end;
end;

if nargin > 9
   offset = varargin{3};
   % offset = 0 -> symmetric interval 
   % offset = 1 interval between 1 and Nlev-1
else
   offset = 0;
end;

if nargin > 10
    % Determine variation of carrier frequency
      carrmod = varargin{4};
      if nargin ~=12,
          error('wrong number of arguments');
      else
          carrfreqphase = varargin{5};
          carrfreqmag = varargin{6};          
          carrfreqmod = 1 + carrfreqmag*cos(2*wt + carrfreqphase);        
      end;
else
    carrfreqmod = 1;
end;

switch opt
    case 'none'
        ref = scale*(ma*cos(wt+theta0)+offset); % Reference waveform
    case '3rd1'
        ref = scale*(ma*(cos(wt+theta0) - (1/6)*cos(3*(wt+theta0)))+offset); % Reference waveform 1/6th 3rd harmonic
end;

switch type
    case 'pcs'
        % Phase shifted carriers
        carr=zeros(ncarr,npts);  % Allocate memory
        wtcarr =mod(p*wt,2*pi).*carrfreqmod;
        for k = 1:ncarr,
            carrshft=2*pi*(k-1)/(ncarr)+theta_c;
            carr(k,:)=sawtooth(wtcarr + carrshft,0.5);  % Carrier k
            s(k,:) = scale*udlev*(2*(ref > carr(k,:))-1+offset);
        end;
    case 'pc2'
        % Phase shifted carriers for M2LC
        if ~rem(nlev,2),
            error('Phase shifted carriers for M2LC only works for an odd number of levels');
        end;
        carr=zeros(ncarr,npts);                     % Allocate memory
        wtcarr =mod(p*wt,2*pi).*carrfreqmod;
        ncell=ncarr/2;                              % No of cells per phase branch
        for k = 1:ncell,
            carrshft1 = 2*pi*(k-1)/ncell;
            carrshft2 = 2*pi*(k-0.5)/ncell;
            carr(k,:)       = scale*sawtooth(wtcarr + carrshft1,0.5);  % Carrier k
            carr(k+ncell,:) = scale*sawtooth(wtcarr + carrshft2,0.5);  % Carrier k
            s(k,:) =        scale*udlev*(2*(ref > carr(k,:))-1+offset);
            s(k+ncell,:) = -scale*udlev*(2*(-ref > carr(k+ncell,:))-1+offset);
        end;
    case 'sc1'
        % Stacked carriers with equal phase 'PD'
        peff=round(ncarr)*p; % Effective pulse number
        wtcarr =mod(peff*wt,2*pi).*carrfreqmod;
        carr=zeros(ncarr,npts);  % Allocate memory
        for k = 1:(ncarr),
            carrshft=0;
            carr(k,:)=scale*(-1 + offset + udlev*(2*k - 1 + sawtooth(wtcarr + carrshft,0.5)));  % Carrier k
            s(k,:) = scale*udlev*(2*(ref > carr(k,:))-1 + offset);
        end;
    case 'sc2'
        % Stacked carriers with alternative phase opposition 'APOD'
        if ~rem(nlev,2),
            error('APOD only works for an odd number of levels');
        end;
        peff=round(ncarr*p); % Effective pulse number
        carr=zeros(ncarr,npts);  % Allocate memory
        for k = 1:ncarr,
            carrshft=(k-1)*pi;
            carr(k,:)=scale*(-1+offset + udlev*(2*k - 1 + sawtooth(peff*wt.*carrfreqmod + carrshft,0.5)));  % Carrier k
            s(k,:) = scale*udlev*(2*(ref > carr(k,:))-1+offset);
        end;
    case 'sc3'
        % Stacked carriers with phase opposition 'POD'
        if ~rem(nlev,2),
            error('POD only works for an odd number of levels');
        end;
        peff=round(ncarr*p); % Effective pulse number
        carr=zeros(ncarr,npts);  % Allocate memory
        for k = 1:ncarr,
            carrshft=(k>round(ncarr/2))*pi;     % Shift carriers above zero
            carr(k,:)=scale*(-1+offset + udlev*(2*k - 1 + sawtooth(peff*wt.*carrfreqmod + carrshft,0.5)));  % Carrier k
            s(k,:) = scale*udlev*(2*(ref > carr(k,:))-1+offset);
        end;        
        
end;



stot=sum(s,1);

if nargout>1,
    varargout{1}=wt;
    if nargout>2
           varargout{2}=ref;
           if nargout>3
                varargout{3}=carr;                
                if nargout>4
                    varargout{4}=s;
                end;                
           end;
           
    end;
end;

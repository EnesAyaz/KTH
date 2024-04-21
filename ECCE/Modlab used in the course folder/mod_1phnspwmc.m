function [s, varargout] = mod_1phnspwmc(M, pn, theta0, fi, npoints, varargin);
% mod_1phnspwmc: Three-level single phase constrained naturally sampled PWM modulation
%
% s=mod_1phnspwmc(M, pn, theta0, fi, npoints[,start,end,M0,thetac]);
%
% s: pwm pattern during fundamental cycle
% M: modulation index = Uout/(UD) (interval: [0,1] M=1 corresponds to a
% fundamental voltage of 2 p. u. i. e. 1 p.u.=Ud where UD=2Ud)
% pn: pulse number 1, 2,...
% npoints: number of points during fundamental cycle
% fi: load angle (interval [-pi, pi])
%
% Staffan Norrga 2004
%
if nargin >5,
    if not(isempty(varargin{1})),
        wtstart=varargin{1};
    else
        wtstart=0;
    end;
else 
    wtstart=0;
end;

if nargin >6,
    if not(isempty(varargin{2})),
        wtend=varargin{2};
    else
        wtend=2*pi;
    end;
else 
    wtend=2*pi;
end;

if nargin >7,
    if not(isempty(varargin{3})),
        M0=varargin{3};
    else
        M0=0;
    end;
else 
    M0=0;
end;
%
if nargin >8,
    if not(isempty(varargin{4})),
        thetac=varargin{4};
    else
        thetac=0;
    end;
else 
    thetac=0;
end;

if nargin >9,
    if isempty(varargin{5}),
        opt='ns';
    else
        opt=varargin{5};
    end;
else 
        opt='ns';
end;

%
wt=wtstart+ (wtend-wtstart)*(0:(npoints-1))/(npoints-1);
%
wt=2*pi*(0:(npoints-1))/npoints;
%
% Generate reference waveform
%
if opt == 'ns',
uref=2*M*cos(wt+theta0);
elseif opt=='rs'
uref= regsamp(2*M, pn, theta0, npoints);   
end;
%
iph=0.5*cos(wt-fi+theta0);
%
sawt1=sawtooth(wt*pn-pi+thetac);
sawt2=sawtooth(wt*pn-pi+thetac,0);
%
swcarrp= ((sawt1+1).*(iph<0) + (sawt2+1).*(iph>0)); % Positive carrier
swcarrn= ((sawt2-1).*(iph>0) + (sawt1-1).*(iph<0)); % Negative carrier
%
pwmp=2*(uref>swcarrp);
pwmn=2*(uref<swcarrn);

s=pwmp-pwmn; % PWM resulting from zero-voltage intervals by direct converter

if nargout > 1
    % carrier array requested
    varargout{1}=wt;
end;

if nargout > 2    
    % carrier array requested
    varargout{2}=swcarrp;
    varargout{3}=swcarrn;
end;

if nargout > 4
    % reference array requested
    varargout{4}=uref;
end;

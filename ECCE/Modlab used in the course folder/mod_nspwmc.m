function [s,varargout] = mod_nspwmc(M, pn, theta0, fi, npoints, varargin);
% mod_nspwmc: Two-level constrained naturally sampled PWM modulation of
% a single phase leg
%
%              1  2      3     4     5      6    7   8   9      10
% s=mod_nspwmc(M, pn, theta0, fi, npoints,start,end,M0,thetac, opt);
%                                           1    2   3   4      5
%
% s: pwm pattern during fundamental cycle
% M: modulation index = Up/(UD/2) ( interval: [0,1]) M=1 corresponds to a
% fundamental voltage of 1 p. u. Ud=UD/2
% pn: pulse number 1, 2,...
% npoints: number of points during fundamental cycle
% fi: load angle (interval [-pi, pi])
%
% Staffan Norrga 2004
%
%
if nargin >5,
    if isempty(varargin{1}),
        wtstart=0;
    else
        wtstart=varargin{1};
    end;
else 
    wtstart=0;
end;

if nargin >6,
    if isempty(varargin{2}),
        wtend=2*pi;
    else
        wtend=varargin{2};
    end;
else 
    wtend=2*pi;
end;

if nargin >7,
    if isempty(varargin{3}),
        M0=0;      
    else
        M0=varargin{3};         
    end;
else 
    M0=0;
end;

if nargin >8,
    if isempty(varargin{4}),
        thetac=0;
    else
        thetac=varargin{4};
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
% Generate reference waveform
%
if opt == 'ns',
uref=M0+M*cos(wt+theta0);
elseif opt=='rs'
uref= regsamp(M, pn, theta0, npoints);   
end;
%
iph=0.5*cos(wt-fi+theta0);
%
sawt1=sawtooth(wt*pn-pi+thetac);   % Rising sawtooth -> trailing edge modulated
sawt2=sawtooth(wt*pn-pi+thetac,0); % Falling sawtooth-> leading edge modulated
%
swcarr= sawt1.*(iph<0) + sawt2.*(iph>0); % Carrier
%
s=2*(uref>swcarr)-1;


if nargout > 1   
    
    % carrier array requested
    varargout{1}=wt;
end;

if nargout > 2    
    % carrier array requested
    varargout{2}=swcarr;
end;

if nargout > 3
    % reference array requested
    varargout{3}=uref;
end;
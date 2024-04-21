function [s, varargout] = mod_nspwm(M, pn, theta0, npoints, meth, varargin);
%
% mod_nspwm: Two-level naturally sampled PWM modulation of
% a single phase leg
%
% [s,[wt],[carr],[ref]]=mod_nspwm(M, pn, theta0, npoints, meth,start,end,M0);
%
% Outputs:
% s: pwm pattern during fundamental cycle
% wt: phase angle vector corresponding to s
% carr: carrier
% ref:reference curve
%
% Inputs
% M: modulation index = Up/(UD/2) ( interval: [0,1]
% pn: pulse number 1, 2,...
% npoints: number of points during fundamental cycle
% meth: type of carrier
%       meth='sawp' : sawtooth carrier with positive slope
%       meth='tria' : triangular carrier
% start: (optional) reference angle to start with (default=0)
% end:  (optional) reference angle to endwith with (default=2pi)
% M0: (optional) DC reference (default =0)
%
% Staffan Norrga 2004
%
if nargin >5,
    wtstart=varargin{1};
else 
    wtstart=0;
end;

if nargin >6,
    wtend=varargin{2};
else 
    wtend=2*pi;
end;

if nargin >7,
    M0=varargin{3};
else 
    M0=0;
end;

if nargin >8,
    if isempty(varargin{4}),
        opt='ns';
    else
        opt=varargin{4};
    end;
else 
        opt='ns';
end;
%
if meth=='sawp'
    slope=1;
    thetac1=-pi;
elseif meth=='tria'
    slope=0.5;
    thetac1=0;
else
    slope=1;
    thetac1=-pi;
end;
%
wt=wtstart+ (wtend-wtstart)*(0:(npoints-1))/(npoints-1);
%
if opt == 'ns',
uref=M0+M*cos(wt+theta0);
elseif opt=='rs'
uref= regsamp(M, pn, theta0, npoints);   
end;
%
carr=sawtooth(wt*pn+thetac1,slope);   % Rising sawtooth -> trailing edge modulated
%
% The function sawtooth behaves like a -cos() function, sawtooth(0)=-1
%
s=2*(uref>carr)-1;

if nargout > 1   
    
    % angle array requested
    varargout{1}=wt;
end;

if nargout > 2    
    % carrier array requested
    varargout{2}=carr;
end;

if nargout > 3
    % reference array requested
    varargout{3}=uref;
end;
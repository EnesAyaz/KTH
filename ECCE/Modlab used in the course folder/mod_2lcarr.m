function [s, varargout] = mod_2lcarr(ma, pn, npoints, varargin);
%
% mod_2lcarr: Two-level carrier-based PWM modulation of a single phase leg
%
% Creates sampled PWM waveform during one cycle
%
% [s,[wt],[carr],[ref]]=mod_2lcarr(ma, pn,  npoints {, carrtype} {, smp} {, cmode} {, theta0} {, thetac} {, start} {, end} {, ma0});
%
% Outputs:
% s: switching waveform during a fundamental cycle
% wt: phase angle vector corresponding to s
% carr: carrier
% ref: reference curve
%
% Inputs
% 1. ma:       modulation index = U1/(UD/2) ( interval: [0,1])
% 2. pn:       pulse number 1, 2,...
% 3. npoints:  number of sampling points during fundamental cycle
% 4. carrtype: (optional) type of carrier
%           'sawp' : sawtooth carrier with positive slope
%           'tria' : triangular carrier (default)
% 5. smp:      (optional) reference sampling mode
%           'ns' : natural sampling (default)
%           'rs' : regular symmetric sampling
%           'ra' : regular asymmetric sampling
% 6. cmode:    (optional) reference common-mode component for three-phase systems
%           'none' : No common mode (default)
%           'tri4' : One fourth third harmonic
%           'tri6' : One sixth third harmonic
% 7. theta0:   (optional) reference phase offset
% 8. thetac:   (optional) carrier phase offset
% 9. start:    (optional) reference angle to start with (default=0)
% 10. end:     (optional) reference angle to end with (default=2pi)
% 11. ma0:     (optional) DC reference (default =0)
%
% Staffan Norrga 2004,2007
%
%
antfarg=3;  % No of fixed arguments
%
vargno=1;   % carrtype
if nargin >= antfarg+vargno,
    if isempty(varargin{vargno}),
        carrtype='tria';
    else
        carrtype=varargin{vargno};
    end;
else 
    carrtype='tria';
end;

vargno=2;   % smp
if nargin >= antfarg+vargno,
    if isempty(varargin{vargno}),
        smp='ns';
    else
        smp=varargin{vargno};
    end;
else 
    smp='ns';
end;

vargno=3;  % cmode
if nargin >= antfarg+vargno,
    if isempty(varargin{vargno}),
        cmode = 'none';
    else
        cmode=varargin{vargno};
    end;
else 
    cmode= 'none';
end;

vargno=4;   % theta0
if nargin >= antfarg+vargno,
    if isempty(varargin{vargno}),
        theta0=0;
    else
        theta0=varargin{vargno};
    end;
else 
    theta0=0;
end;

vargno=5;   % thetac
if nargin >= antfarg+vargno,
    if isempty(varargin{vargno}),
        thetac=0;
    else
        thetac=varargin{vargno};
    end;
else 
    thetac=0;
end;

vargno=6;   % wtstart
if nargin >= antfarg+vargno,
    if isempty(varargin{vargno}),
        wtstart = 0;
    else
        wtstart=varargin{vargno};
    end;
else 
    wtstart= 0;
end;

vargno=7;   % wtend
if nargin >= antfarg+vargno,
    if isempty(varargin{vargno}),
        wtend=2*pi;
    else
        wtend=varargin{vargno};
    end;
else 
    wtend=2*pi;
end;

vargno=8;   % ma0
if nargin >= antfarg+vargno,
    if isempty(varargin{vargno}),
        ma0=0;
    else
        ma0=varargin{vargno};
    end;
else 
    ma0=0;
end;

if nargin > antfarg+vargno,
    error('Too many arguments');
end;
%
if carrtype=='sawp'
    slope=1;
    thetac1=-pi+thetac;
elseif carrtype=='tria'
    slope=0.5;
    thetac1=thetac;
else
    error(['Unknown carrier type' carrtype]);
end;
%
wt=wtstart+ (wtend-wtstart)*(0:(npoints-1))/(npoints-1);
%
switch cmode
    case 'none'
        gamma3=0;
    case 'tri4'
        gamma3=-1/4;
    case 'tri6'
        gamma3=-1/6;
    otherwise
        error(['Unknown common mode option: ' cmode']);
end;
%
if smp == 'ns',     % Natural
    uref=ma0+ma*(cos(wt+theta0) + gamma3*cos(3*(wt+theta0))) ;
elseif smp=='rs'    % Regular symmetric    
    if thetac~=0,
        error('No carrier phase shift allowed with regular sampling');
    end;
    uref= regsamp(ma, pn, theta0, npoints, gamma3);
elseif smp=='ra'    % Regular asymmetric
    if thetac~=0,
        error('No carrier phase shift allowed with regular sampling');
    end;
    if carrtype~='tria',
        error('Asymmetric regular sampling only allowed for triangular carrier');
    end;    
    uref= regsamp(ma, 2*pn, theta0, npoints, gamma3);
else
    error(['Unknown reference sampling type: ' smp]);
end;
%
carr=sawtooth(wt*pn+thetac1,slope);
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
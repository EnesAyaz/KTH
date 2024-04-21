function s = regsamp(M, pn, theta0, npoints, varargin);
% regsamp: Generates regularly sampled cosine waveform
%
% s=mod_pwm(M, pn, theta0,npoints,[gamma3]);
%
% s: pwm pattern during fundamental cycle
% M: modulation index = Uout/(Ud) ( interval: [0,1])
% pn: pulse number 1, 2,...
% npoints
% gamma3: (optional), third harmonic injection as a fraction 
%         of fundamental
%
% Staffan Norrga 2005-2007
%
if nargin > 4,
    gamma3=varargin{1};
else
    gamma3=0;
end;
%
w0t=2*pi*(0:npoints-1)/npoints;
%
s=[];
ptsprsmp=npoints/pn;                        % Time points per commutation cycle, not neccessarily integer
lastpoint=0;
for smpctr=1:pn,                            % Commutation cycle number
    firstpoint=lastpoint+1;                 % First point in commutation cycle
    w0tf=w0t(firstpoint);
    lastpoint=round(smpctr*ptsprsmp);       % Last point in commutation cycle
    ptsinsmp=lastpoint-firstpoint+1;        % Number of points in current commutation cycle (integer)
    uref = M*(cos(w0tf + theta0) + gamma3*cos(3*(w0tf + theta0)));
    sinsmp=[uref*ones(1,ptsinsmp)];
    s = [s sinsmp];
end;
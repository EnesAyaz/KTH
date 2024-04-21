function s = regsamp(M, pn, theta0, npoints);
% regsamp: Generates regularly sampled cosine waveform
%
% s=mod_pwm(M, pn, theta0,npoints);
%
% s: pwm pattern during fundamental cycle
% M: modulation index = Uout/(Ud) ( interval: [0,1])
% pn: pulse number 1, 2,...
% npoints
%
% Staffan Norrga 2005
%
%
w0t=2*pi*(0:npoints-1)/npoints;
%
s=[];
ptsprsmp=npoints/pn;                        % Time points per commutation cycle, not neccessarily integer
ptshift=ptsprsmp*mod(1+thetac/2/pi,1);
lastpoint=ptshift;
% First, possibly incomplete sample
for smpctr=1:pn,                            % Commutation cycle number
    firstpoint=lastpoint+1;                 % First point in commutation cycle
    w0tf=w0t(firstpoint-theta0);
    lastpoint=round(smpctr*ptsprsmp);       % Last point in commutation cycle
    ptsinsmp=lastpoint-firstpoint+1;        % Number of points in current commutation cycle (integer)
    uref = M*cos(w0tf + theta0);
    sinsmp=[uref*ones(1,ptsinsmp)];
    s = [s sinsmp];
end;
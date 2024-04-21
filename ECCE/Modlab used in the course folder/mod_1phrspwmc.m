function s = mod_1phrspwmc(M, pn, theta0, fi, npoints, opt,varargin);
% mod_1phrspwmc: Three-level single-phase constrained regularly sampled PWM modulation
% Regular sampling of voltage AND CURRENT!
% s=mod_pwm(M, pn, theta0, fi, npoints, opt,dc);
%
% s: pwm pattern during fundamental cycle
% M: modulation index = Uout/(Ud) ( interval: [0,1])
% pn: pulse number 1, 2,...
% npoints: number of points during fundamental cycle
% fi: load angle (interval [-pi, pi])
% opt: 
%   opt = 0 :
%   opt = 1 :
%   opt = 2 :
%   opt = 3 :
% dc: (optional) the reference curves are constant when =1
%
% Staffan Norrga 2005
%
if nargin>6
    if varargin{1}==1
        argfact=0;
    else
        argfact=1;
    end
else
    argfact=1;
end
%
w0t=argfact*2*pi*(0:npoints-1)/npoints;
%
s=[];
ptsprsmp=npoints/pn;                        % Time points per commutation cycle, not neccessarily integer
lastpoint=0;
for smpctr=1:pn,                            % Commutation cycle number
    firstpoint=lastpoint+1;                 % First point in commutation cycle
    w0tf=w0t(firstpoint);
    lastpoint=round(smpctr*ptsprsmp);       % Last point in commutation cycle
    ptsinsmp=lastpoint-firstpoint+1;        % Number of points in current commutation cycle (integer)
    uref = M*cos(w0tf + theta0);
    sgn_uref = sign(uref);
    if sgn_uref==0,
        sgn_uref=-sign(sin(w0tf + theta0));
    end;
    
    
    switch opt
        case 0,
            urefzs = 0;
        case 1,
            urefzs = 0;
        case 2,
            urefzs = 0;
        case 3,
            urefzs = 0;
        case 4,
            urefzs = 0;
    end;
    
    sgn_i = sign(cos(w0tf-fi + theta0));
    if sgn_i==0,
        sgn_i=-sign(sin(w0tf-fi + theta0));
    end;
    
    nd = round(ptsinsmp*abs(uref));
    nz = ptsinsmp-nd;
    poflo = sgn_i*sgn_uref;
    if poflo > 0;
        n1 = nz;
        n2 = nd;
        u1 = 0;
        u2 = 2*sgn_uref;
    else
        n1 = nd;
        n2 = nz;
        u1 = 2*sgn_uref;
        u2 = 0;
    end;
    
    sinsmp=[u1*ones(1,n1) u2*ones(1,n2)];
    
    s = [s sinsmp];

    % Vavg=(n(1)*V1 + n(2)*V2 + n(3)*V3)/ptsinsmp;
    % SVavg=(2/3)*(Vavg(1) + Vavg(2)*exp(j*2*pi/3) + Vavg(3)*exp(-j*2*pi/3));
    % smpctr
    % uref
    % Mag=abs(SVavg)
    % Argu=angle(SVavg)/pi
end;
function s = mod_pwmc(M, pn, theta0, fi, npoints, opt,varargin);
% MOD_PWMC: Two-level three-phase constrained regularly sampled PWM modulation
%
% s=mod_pwm(M, pn, theta0, fi, npoints, opt,dc);
%
% s: pwm pattern during fundamental cycle
% M: modulation index = Up/(Ud/2) ( interval: [0,2/sqrt(3)] = [0, 1.155] )
% pn: pulse number 1, 2,...
% npoints: number of points during fundamental cycle
% fi: load angle (interval [-pi, pi])
% opt: 
%   opt = 0 : No third harmonic
%   opt = 1 : Discontinous modulation. The added zero-sequence ensures that the reference with the
%   highest magnitude is clamped to the closest DC rail.
%   opt = 2 : 1/6 third harmonic added
%   opt = 3 : 1/4 third harmonic added
%   dc: (optional) the reference curves are constant when =1
%
% Staffan Norrga 2004
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
w0t=argfact*2*pi*(0:npoints-1)/npoints + theta0;
a=exp(j*2*pi/3);
%
s=[];
ptsprsmp=npoints/pn;                        % Time points per commutation cycle, not neccessarily integer
lastpoint=0;
for smpctr=1:pn,                            % Commutation cycle number
    firstpoint=lastpoint+1;                 % First point in commutation cycle
    w0tf1=w0t(firstpoint);
    w0tf2=w0t(firstpoint)-2*pi/3;
    w0tf3=w0t(firstpoint)-4*pi/3;
    lastpoint=round(smpctr*ptsprsmp);       % Last point in commutation cycle
    ptsinsmp=lastpoint-firstpoint+1;        % Number of points in current commutation cycle (integer)
    uref1 = M*cos(w0tf1);
    uref2 = M*cos(w0tf2);
    uref3 = M*cos(w0tf3);
    
    switch opt
        case 0,
            urefzs = 0;
        case 1,
            urefzs = refdmax0(uref1,uref2,uref3);
        case 2,
            urefzs = (1/6)*M*(cos(3*w0tf1));
        case 3,
            urefzs = (1/4)*M*(cos(3*w0tf1));
        case 4,
            urefzs = refdmid(uref1,uref2,uref3);
    end;
    
    uref1c = uref1 + urefzs;
    uref2c = uref2 + urefzs;
    uref3c = uref3 + urefzs;

    sgn_i1 = sign(cos(w0tf1-fi));
    if sgn_i1==0,
        sgn_i1=-sign(sin(w0tf1-fi));
    end;
    
    sgn_i2 = sign(cos(w0tf2-fi));
    if sgn_i2==0,
        sgn_i2=-sign(sin(w0tf2-fi));
    end;
    
    sgn_i3 = sign(cos(w0tf3-fi));
    if sgn_i3==0,
        sgn_i3=-sign(sin(w0tf3-fi));
    end;

    n11 = round(ptsinsmp*0.5*(1 - sgn_i1*uref1c));
    n12 = ptsinsmp-n11;
    u11 = sgn_i1<0;
    u12 = not(u11);
    
    n21 = round(ptsinsmp*0.5*(1 - sgn_i2*uref2c));
    n22 = ptsinsmp-n21;
    u21 = sgn_i2<0;
    u22 = not(u21);
    
    n31 = round(ptsinsmp*0.5*(1 - sgn_i3*uref3c));
    n32 = ptsinsmp-n31;
    u31 = sgn_i3<0;
    u32 = not(u31);
    
    sinsmp=2*[u11*ones(1,n11) u12*ones(1,n12) ;...
            u21*ones(1,n21) u22*ones(1,n22) ;...
            u31*ones(1,n31) u32*ones(1,n32)];
    
    s = [s sinsmp];

    % Vavg=(n(1)*V1 + n(2)*V2 + n(3)*V3)/ptsinsmp;
    % SVavg=(2/3)*(Vavg(1) + Vavg(2)*exp(j*2*pi/3) + Vavg(3)*exp(-j*2*pi/3));
    % smpctr
    % uref
    % Mag=abs(SVavg)
    % Argu=angle(SVavg)/pi
end;
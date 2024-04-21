function [s, varargout] = mod_svmc(M, pn, theta0, fi, npoints,varargin);
%Two-level constrained SVM modulation. Malesani applied to MIRPACS
%converters. The adaptation essentially consists in a reversal of the
%vector sequence in dq-coordinates.
%
% s=mod_svmc(M, pn, theta0, fi, npoints,dc,meth);
%
% s: pwm pattern during fundamental cycle
% M: modulation index = Up/(Ud/2) ( interval: [0,2/sqrt(3)] = [0, 1.155] )
% pn: pulse number 1, 2,...
% theta0: initial phase angle of reference vector
% fi: load angle
% npoints: number of sampling points during fundamental cycle
% dc: (optional) the reference curves are constant when =1
% meth (optional) MIRPACS 1 variant if = 'mirp'
%                 MIRPACS 3 variant if = 'mrp3'
%                 MIRPACS 4 variant if = 'mrp4'
%                 QRDCL variant if = 'qrdc' 
% Staffan Norrga 2004
%
if nargin>5
    if varargin{1}==1
        argfact=0;
    else
        argfact=1;
    end
else
    argfact=1;
end

if nargin>6
   meth= varargin{2};
else
    meth= 'mirp';
end;   

if nargout > 1
    
    % vector array requested
end

%
w0t=argfact*2*pi*(0:npoints-1)/npoints;
%
if meth=='mirp'
dummy =svmc(0,0,1);      % Initialise SVM generator
elseif meth=='qrdc'
dummy =svmc_qrdcl(0,0,1);      % Initialise SVM generator
elseif meth=='mrp3'
dummy =svmc_mirp3(0,0,1);      % Initialise SVM generator
elseif meth=='mrp4'
dummy =svmc_mirp4(0,0,1);      % Initialise SVM generator
end;
%
%
Vbase = [0 0 0;  %  0
         1 0 0;  %  1
         1 1 0;  %  2
         0 1 0;  %  3
         0 1 1;  %  4
         0 0 1;  %  5
         1 0 1;  %  6
         1 1 1]; %  7
%
s=[];
ptsprsmp=npoints/pn;                        % Time points per commutation cycle, not neccessarily integer
lastpoint=0;
for smpctr=1:pn,                            % Commutation cycle number
    firstpoint=lastpoint+1;                 % First point in commutation cycle
    lastpoint=round(smpctr*ptsprsmp);       % Last point in commutation cycle
    ptsinsmp=lastpoint-firstpoint+1;        % Number of points in current commutation cycle (integer)
    uref=M*exp( j*(w0t(firstpoint)+theta0) );          % Sampled reference vector at beginning of commutation cycle
%
    if meth=='mirp'
        [d, vectseq]=svmc(uref,fi,2);
    elseif meth=='qrdc'
        [d, vectseq]=svmc_qrdcl(uref,fi,2);
    elseif meth=='mrp3'
        [d, vectseq]=svmc_mirp3(uref,fi,2);
    elseif meth=='mrp4'
        [d, vectseq]=svmc_mirp4(uref,fi,2);
    end;

    % disp((w0t(firstpoint)+theta0)/pi);
    % disp(vectseq);
    n=stuff(d,ptsinsmp);                    % # of timesteps during the three vectors
    V1 = Vbase(vectseq(1)+1,:)';
    V2 = Vbase(vectseq(2)+1,:)';
    V3 = Vbase(vectseq(3)+1,:)';
    si=2*[repmat(V1,1,n(1)) repmat(V2,1,n(2)) repmat(V3,1,n(3))];  % Switching functions in current interval
    s=[s si];
 
    
%    Vavg=(n(1)*V1 + n(2)*V2 + n(3)*V3)/ptsinsmp;
%    SVavg=(2/3)*(Vavg(1) + Vavg(2)*exp(j*2*pi/3) + Vavg(3)*exp(-j*2*pi/3));
%     smpctr
%     uref
%     Mag=abs(SVavg)
%     Argu=angle(SVavg)/pi
end;






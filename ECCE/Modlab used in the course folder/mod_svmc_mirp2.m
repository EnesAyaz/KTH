function [s, varargout] = mod_svmc_mirp2(M, pn, theta0, fi, npoints,varargin);
%VERSION 2 Two-level constrained SVM modulation. Malesani applied to MIRPACS
%converters. The adaptation essentially consists in a reversal of the
%vector sequence in dq-coordinates.
%
% Version 2 can use 4-vector sequences.
%
% s=mod_svmc_mirp2(M, pn, theta0, fi, npoints,dc);
%
% s: pwm pattern during fundamental cycle
% M: modulation index = Up/(Ud/2) ( interval: [0,2/sqrt(3)] = [0, 1.155] )
% pn: pulse number 1, 2,...
% theta0: initial phase angle of reference vector
% fi: load angle
% npoints: number of sampling points during fundamental cycle
% dc: (optional) the reference curves are constant when =1
%
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

if nargout > 1
    
    % vector array requested
end
%
w0t=argfact*2*pi*(0:npoints-1)/npoints;
%
dummy =svmc_mirp2(0,0,1);      % Initialise SVM generator
%
%
Vbase = [0 0 0;  %  0
         1 0 0;  %  1
         1 1 0;  %  2
         0 1 0;  %  3
         0 1 1;  %  4
         0 0 1;  %  5
         1 0 1;  %  6
         1 1 1;  %  7
         0 0 0]; %  8  % NOT USED!
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
    [d, vectseq]=svmc_mirp2(uref,fi,2);

    % disp((w0t(firstpoint)+theta0)/pi);
    % disp(vectseq);
    n=stuff4(d,ptsinsmp);                    % # of timesteps during the three vectors
    V1 = 2*Vbase(vectseq(1)+1,:)';
    V2 = 2*Vbase(vectseq(2)+1,:)';
    V3 = 2*Vbase(vectseq(3)+1,:)';
    V4 = 2*Vbase(vectseq(4)+1,:)';
    s=[s repmat(V1,1,n(1)) repmat(V2,1,n(2)) repmat(V3,1,n(3)) repmat(V4,1,n(4))];
 
%    Vavg=(n(1)*V1 + n(2)*V2 + n(3)*V3)/ptsinsmp;
%    SVavg=(2/3)*(Vavg(1) + Vavg(2)*exp(j*2*pi/3) + Vavg(3)*exp(-j*2*pi/3));
%    smpctr
%     uref
%     Mag=abs(SVavg)
%     Argu=angle(SVavg)/pi
end;
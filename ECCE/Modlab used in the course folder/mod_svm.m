function s = mod_svm(M, pn, theta0, npoints,varargin);
%Two-level SVM modulation
%
% [s]=mod_svm(M, pn, theta0, npoints,dc);
%
% s: switching waveform during a fundamental cycle
% M: modulation index = Up/(Ud/2) ( interval: [0,2/sqrt(3)] = [0, 1.155] )
% pn: pulse number 1, 2,...
% theta0: initial phase angle of reference vector
% npoints: number of points
% dc: (optional) the reference curves are constant when =1
%
% Staffan Norrga 2004
%
if nargin>4
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
%
dummy =svm(0,1);      % Initialise SVM generator
Vbase = [1 0 0;  %  1
         1 1 0;  %  2
         0 1 0;  %  3
         0 1 1;  %  4
         0 0 1;  %  5
         1 0 1]; %  6
Vz    = [0 0 0;  % state 0
         1 1 1]; % state 7
%
zerovect=[0 0 0];                                 % zerovect=0 -> state 0 (000), zerovect=1 -> state 7 (111). 
s=[];
ptsprsmp=npoints/(2*pn);                        % Time points per commutation cycle, not neccessarily integer
lastpoint=0;
for smpctr=1:(2*pn),                            % Commutation cycle number
    firstpoint=lastpoint+1;                 % First point in commutation cycle
    lastpoint=round(smpctr*ptsprsmp);          % Last point in commutation cycle
    ptsinsmp=lastpoint-firstpoint+1;           % Number of points in current commutation cycle (integer)
    Uref=M*exp(j*( w0t(firstpoint)+theta0 ));      % Sampled reference vector at beginning of commutation cycle
    [d0, d1, d2, sect]=svm(Uref,2);
    oddsect=rem(sect,2);
    if (~zerovect & oddsect) | (zerovect & ~oddsect), 
        % Vectors run through in positive sequence
        % (odd numbered sector AND starting from state 0) OR 
        % (even numbered sector AND starting from state 7)
        n1=round(d1*ptsprsmp);             % # of timesteps during first active vector
        n2=round(d2*ptsprsmp);             % # of timesteps during second active vector
        n0=ptsinsmp-n1-n2;                 % total # of timesteps during zero vectors
        n01=floor(n0/2);
        n02=ceil(n0/2);
        Vz1=zerovect';
        Va1=Vbase(sect,:)';
        Va2=Vbase(mod(sect,6)+1,:)';
        zerovect=not(zerovect);
        Vz2=zerovect';
    else
        % Vectors run through in negative sequence
        n1=round(d2*ptsprsmp);             % # of timesteps during first active vector
        n2=round(d1*ptsprsmp);             % # of timesteps during second active vector
        n0=ptsinsmp-n1-n2;                 % total # of timesteps during zero vectors
        n01=ceil(n0/2);
        n02=floor(n0/2);
        Vz1=zerovect';
        Va1=Vbase(mod(sect,6)+1,:)';
        Va2=Vbase(sect,:)';
        zerovect=not(zerovect);        
        Vz2=zerovect';        
    end;
    
    s=[s 2*[repmat(Vz1,1,n01) repmat(Va1,1,n1) repmat(Va2,1,n2) repmat(Vz2,1,n02)]];
        
end;    

s=s-1; % Remove DC offset
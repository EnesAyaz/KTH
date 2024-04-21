function [d0, d1, d2, sect]=svm(Uref,opt);
%Two-level SVM modulator
%
% [d0,d1,d2, sect]=svm(Uref,opt);
%
% 
%
% munlock
% mlock;
persistent cmat initd;
%
%
if opt==1,
    %
    % Compute transformation matrices for each sector
    % cmat converts from cartesian (alpha,beta) coordinates to coordinates
    % of the two adjacent base vectors of each sector (d1,d2)
    %
    K=2/3;
    gamma_v =pi/3*(0:6);
    Vb_a= 2*K*cos(gamma_v);
    Vb_b= 2*K*sin(gamma_v);
    for rakn=1:6,
        cmat(:,:,rakn)=inv([Vb_a(rakn) Vb_a(rakn+1) ; Vb_b(rakn) Vb_b(rakn+1) ]);
    end;
    d0=[];
    d1=[];
    d2=[];    
    sect=[];
    initd=1;
elseif opt==2,
    if initd~=1,
        error('Function not initialised')
    end;
    %
    % Determine sector
    %
    gamma=angle(Uref);
    uref_alpha=real(Uref);
    uref_beta= imag(Uref);
    
        %if gamma >= 0;    
        %    sect=floor(gamma/(pi/3))+1;
        %else
        %     sect=floor(gamma/(pi/3)+6)+1;
        % end;
    sect=mod(floor(gamma/(pi/3)),6)+1;
    
    %
    % Determine duty cycles
    %
    d = cmat(:,:,sect)*[uref_alpha ; uref_beta];
    d1 = d(1);
    d2 = d(2);
    d0 = 1 - d1 - d2;
    if d0<0,
        disp('Warning: overmodulation');
    end;
        %
end;
    %
function [d, vectseq,subsect_uref_dq]=svmc_mirp2(uref,fi,opt);
%Two-level constrained SVM modulator, version for MIRPACS converters with
%distributed capacitive snubbers
% - Three-vector sequences in sectors A, D, E and H
% - Four-vector sequences in sectors B, C, F and G
%
% [d, vectseq]=svmc_mirp2(Uref, fi, opt);
%
% The base vectors are nomalised to have the magnitude 4/3.
%
% Staffan Norrga 2004
%
%
% munlock
% mlock;
persistent dmat1 initd dq2ab implseq;
%
%
if opt==1,
    %
    K=2/3;
    gamma_v = pi/3*(0:5);    
    % Base vectors of hexagon (index shifted)
    Vb_a= [0 2*K*cos(gamma_v) 0];
    Vb_b= [0 2*K*sin(gamma_v) 0];
    
    % Conversion table dq_i -> ab
    %
    % Vb_dq_i-> 0 1 2 3 4 5 6 7(8)  % cursect
    dq2ab =    [0 1 2 3 4 5 6 7 0;  %    1
                7 2 3 4 5 6 1 0 0;  %    2
                0 3 4 5 6 1 2 7 0;  %    3
                7 4 5 6 1 2 3 0 0;  %    4
                0 5 6 1 2 3 4 7 0;  %    5
                7 6 1 2 3 4 5 0 0]; %    6
    
    % Table of used vector sequences FOR COMPUTATION OF DUTY CYCLE MATRIX
    % ONLY
    %
    %                  Ref voltage sector 
    %                           |
    %Vect# ->   1 2 3           v
    optseq =   [7 2 1 ;  %     1 A
                3 2 0 ;  %     2 B-C
                4 3 0 ;  %     3 D
                4 5 0 ;  %     4 E
                5 6 0 ;  %     5 F-G
                7 6 1 ]; %     6 H            
    % Compute matrices for duty cycle calculation for each sector.
    % dmat converts from cartesian dq-coordinates to coordinates
    % of the three base vectors of each sector (d1, d2, d3)
    for rakn=1:6,        
        dmat0(:,:,rakn) = inv([Vb_a( optseq(rakn,:)+1 ) ; Vb_b( optseq(rakn,:)+1 ) ; 1 1 1 ]);
    end;
 
    % Conversion matrix -> 4-vector sequences
    % Sectors A, D ,E and H
    for rakn=[1 3 4 6],
    dmat1(:,:,rakn) = [1   0   0 ;...
                       0   1   0 ;...
                       0   0   1 ;...
                       0   0   0] * dmat0(:,:,rakn);
    end;
    
    for rakn=[2 5],
    dmat1(:,:,rakn) = [0   0  0.5 ;...
                       1   0   0  ;...
                       0   1   0  ;...
                       0   0  0.5] * dmat0(:,:,rakn);
    end;
    
   
    % Table of used vector sequences
    %
    %                     Ref voltage sector 
    %                             |
    %Vect# ->   1 2 3 4           v
       implseq=[7 2 1 8;  %     1 A
                4 3 2 1 ; %     2 B-C
                4 3 0 8 ; %     3 D
                4 5 0 8 ; %     4 E
                4 5 6 1 ; %     5 F-G
                7 6 1 8]; %     6 H            

    d=[];
    vectseq=[];
    initd=1;
elseif opt==2,
    if initd~=1,
        error('Function not initialised')
    end;
    %
    gamma_uref=angle(uref);
    %
    gamma_i=gamma_uref-fi;
    sect_i=mod(floor(gamma_i/(pi/3)+0.5),6)+1;    % Determine current sector (1-6)
    theta_i=(sect_i-1)*pi/3;
        %
    uref_dq=uref*exp(-j*theta_i);                 % Convert voltage vector to dq-coordinates
    %
    % Determine vector sequence 
    %
    gamma_uref_dq=angle(uref_dq);
    mainsect_uref_dq=mod(floor(gamma_uref_dq/(pi/3)),6)+1;
    uref_d=real(uref_dq);
    uref_q=imag(uref_dq);

    %subsect_uref_dq
    %abs(uref_dq)
    %angle(uref_dq)    
    vectseq = dq2ab( sect_i , implseq(mainsect_uref_dq,:)+1 );   % Actual vector sequence
    d=dmat1(:,:,mainsect_uref_dq)*[uref_d ; uref_q ; 1];       % Determine duty cycles
    %
    end;
    %
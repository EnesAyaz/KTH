function [d, vectseq,subsect_uref_dq]=svmc(uref,fi,opt);
%Two-level constrained SVM modulator
%
% [d, vectseq]=svmc(Uref,fi, opt);
%
% The base vectors are nomalised to have the magnitude 4/3.
%
% Staffan Norrga 2004


% munlock
% mlock;
persistent dmat initd dq2ab optseq;
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
    % Vb_dq_i-> 0 1 2 3 4 5 6 7   % cursect
    dq2ab =    [0 1 2 3 4 5 6 7 ; %    1
                7 2 3 4 5 6 1 0 ; %    2
                0 3 4 5 6 1 2 7 ; %    3
                7 4 5 6 1 2 3 0 ; %    4
                0 5 6 1 2 3 4 7 ; %    5
                7 6 1 2 3 4 5 0]; %    6
    
    % Table of optimal vector sequences
    %
    %                  Ref voltage sector 
    %                           |
    %Vect# ->   1 2 3           v
    optseq =   [7 2 1 ;  %     1 A
                4 7 2 ;  %     2 B1
                4 3 2 ;  %     3 B2
                3 0 1 ;  %     4 C1
                3 2 1 ;  %     5 C2
                4 3 0 ;  %     6 D
                4 5 0 ;  %     7 E
                5 0 1 ;  %     8 F1
                5 6 1 ;  %     9 F2
                4 7 6 ;  %    10 G1
                4 5 6 ;  %    11 G2
                7 6 1 ]; %    12 H
            
    % Compute matrices for duty cycle calculation for each sector.
    % dmat converts from cartesian dq-coordinates to coordinates
    % of the three base vectors of each sector (d1, d2, d3)
    
    for rakn=1:12,        
        dmat(:,:,rakn) = inv([Vb_a( optseq(rakn,:)+1 ) ; Vb_b( optseq(rakn,:)+1 ) ; 1 1 1 ]);
    end;
    
    d=[];
    vectseq=[];
    initd=1;
elseif opt==2,
    if initd~=1,
        error('Function not initialised')
    end;
    %
    % Uref_m=abs(uref)
    gamma_uref=angle(uref);
    % sect_uref=mod(floor(gamma_u/(pi/3)),6)+1    % Determine voltage sector (1-6)
    %
    gamma_i=gamma_uref-fi;
    sect_i=mod(floor(gamma_i/(pi/3)+0.5),6)+1;    % Determine current sector (1-6)
    theta_i=(sect_i-1)*pi/3;
    
    %   oddfirst=rem(sect_i,2);
    %
    uref_dq=uref*exp(-j*theta_i);                 % Convert voltage vector to dq-coordinates
    %
    % Determine vector sequence 
    %
    %   sect_u_norm=mod(sect_u-sect_i,6)+1;         % Determine normalised voltage sector
    
    gamma_uref_dq=angle(uref_dq);
    mainsect_uref_dq=mod(floor(gamma_uref_dq/(pi/3)),6)+1;
    uref_d=real(uref_dq);
    uref_q=imag(uref_dq);
    inner=sqrt(3)*abs(uref_q)-abs(uref_d)-4/3 < 0;  % Determine whether the reference vector falls in the inner or outer sectors
    dpos=(uref_d >= 0);
    switch mainsect_uref_dq    
        case 1,  % Sect A
            subsect_uref_dq=1;
        case 2,  % Sect B or C            
            if dpos,
                if inner % Sect B1
                    subsect_uref_dq=2;
                else     % Sect B2
                    subsect_uref_dq=3;
                end;
            else
                if inner % Sect C1
                    subsect_uref_dq=4;                   
                else     % Sect C2   
                    subsect_uref_dq=5;
                end;                
            end;            
        case 3, % Sect D
            subsect_uref_dq=6;
        case 4, % Sect E
            subsect_uref_dq=7;
        case 5, % Sect F or G
            if dpos,
                if inner % Sect G1
                    subsect_uref_dq=10;
                else     % Sect G2
                    subsect_uref_dq=11;
                end;
            else
                if inner % Sect F1
                    subsect_uref_dq=8;
                else     % Sect F2   
                    subsect_uref_dq=9;
                end;                
            end;                        
        case 6, % Sect G
            subsect_uref_dq=12;
    end;
    %subsect_uref_dq
    %abs(uref_dq)
    %angle(uref_dq)    
    vectseq = dq2ab( sect_i , optseq(subsect_uref_dq,:)+1 );   % Actual vector sequence
    d=dmat(:,:,subsect_uref_dq)*[uref_d ; uref_q ; 1];       % Determine duty cycles
    %
    end;
    %
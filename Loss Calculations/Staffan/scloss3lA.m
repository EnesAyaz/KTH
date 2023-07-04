function SCLOSS = scloss(Ip,Up,f0,PC,OP,SCPAR)
% mebtu b. beza
% 3 level ANPC VSC Semiconductor losses
% Switching patterns used the 3-Ix type where the nuetral state is chosen 
% to alternate between (N1 and N2) each second time
% original or modified pattern to remove voltage spices give the same loss
% if the blanking time is ignored so the original pattern is used here

% Ip current in the time domain [OP,t]
% Up Phase voltage [OP,t]
% Ud DC Voltage [OP]
% Ta = ambient temperature [OP]
% SC semiconductor parameters
% .SW = switch loss parameters
% .swscale = scaling of switch active area [PAR]
% .DIPAR = diode  loss parameters
% .discale = scaling of diode active area [PAR]
% PC.SCTHERM.model 
%       = 1 No thermal model, assume Tj=Ta in power loss calc;
%       = 2 Use thermal model and iterate to find proper T_j
%
if PC.SC.seriesautoselct, %  Calculate number of series devices in the converter leg
   N = round(max(OP.Ud)/(PC.SC.seriesmargin/100*SCPAR.SW.BV)); %num. of igbts
   if isempty(PC.SC.diodefile)
      Nd = N*SCPAR.DI.NPKG/SCPAR.SW.NPKG; % no of diodes 
   else
      Nd = round(max(OP.Ud)/(PC.SC.seriesmargin/100*SCPAR.DI.BV)); %num. of diodes
   end
else
   N=PC.SC.Nseries;   %no of igbts
   if isempty(PC.SC.diodefile)
      Nd = N*SCPAR.DI.NPKG/SCPAR.SW.NPKG; % no of diodes 
   else
      Nd = round(max(OP.Ud)/(PC.SC.seriesmargin/100*SCPAR.DI.BV)); %num. of diodes
   end
 end;
%
if PC.SC.SC3L.seriesautoselct, %  Calculate number of upper clamping valves
   Nc = round(max(OP.Ud)/(PC.SC.SC3L.seriesmargin/100*SCPAR.SC3L.SW.BV)); %num. of igbts
   if isempty(PC.SC.SC3L.diodefile)
      Ndc = Nc*SCPAR.SC3L.DI.NPKG/SCPAR.SC3L.SW.NPKG; % no of upper clamping diodes 
   else
      Ndc = round(max(OP.Ud)/(PC.SC.SC3L.seriesmargin/100*SCPAR.SC3L.DI.BV)); 
   end
else
   Nc=PC.SC.SC3L.Nseries;   %no of igbts
   if isempty(PC.SC.SC3L.diodefile)
      Ndc = Nc*SCPAR.SC3L.DI.NPKG/SCPAR.SC3L.SW.NPKG; % no of diodes 
   else
      Ndc = round(max(OP.Ud)/(PC.SC.SC3L.seriesmargin/100*SCPAR.SC3L.DI.BV)); %num. of diodes
   end
end
                                  
T0=1/f0;    % Fundamental cycle time
thiterate = PC.SCTHERM.model > 1;   % Iterate to find proper junction temperatures?
if thiterate, PC.SCTHERM.Tjtol=0.5; end; %tolerance in temperature;
npts=length(Up);    % No of time points

%6 groups of semiconductors exist here with different loss Characteristics 
%IGBTs and diodes in the main valve(T1/T4...D1/D4),in the auxiliary
%valve(T2/T3...D2/3) and clamping branch(T5/T6......D5/D6)

% Reserve space
SCLOSS.SW1.Tj =   plstruc('Switch junction temperature',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.SW1.Pc =   plstruc('Switch conduction losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW1.Pton = plstruc('Switch turn on losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW1.Ptof = plstruc('Switch turn off losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW1.Ptot = plstruc('Switch total losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW2.Tj =   plstruc('Switch junction temperature',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.SW2.Pc =   plstruc('Switch conduction losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW2.Pton = plstruc('Switch turn on losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW2.Ptof = plstruc('Switch turn off losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW2.Ptot = plstruc('Switch total losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW5.Tj =   plstruc('Switch junction temperature',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.SW5.Pc =   plstruc('Switch conduction losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW5.Pton = plstruc('Switch turn on losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW5.Ptof = plstruc('Switch turn off losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW5.Ptot = plstruc('Switch total losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.DI1.Tj =   plstruc('Diode junction temperature',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.DI1.Pc =   plstruc('Diode conduction losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.DI1.Ptof = plstruc('Diode turn off losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.DI1.Ptot = plstruc('Diode total losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.DI2.Tj =   plstruc('Diode junction temperature',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.DI2.Pc =   plstruc('Diode conduction losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.DI2.Ptof = plstruc('Diode turn off losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.DI2.Ptot = plstruc('Diode total losses',zeros(PC.npar,PC.nop),'W',1);     
SCLOSS.DI5.Tj =   plstruc('Diode junction temperature',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.DI5.Pc =   plstruc('Diode conduction losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.DI5.Ptof = plstruc('Diode turn off losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.DI5.Ptot = plstruc('Diode total losses',zeros(PC.npar,PC.nop),'W',1);    
SCLOSS.Ptot=     plstruc('Total semiconductor losses',zeros(PC.npar,PC.nop),'W',1); 

for kpar = 1:PC.npar
    for kop = 1:PC.nop
        Ipk = Ip.data(kop+(kpar-1)*PC.nop,:);
        Upk = Up(kop+(kpar-1)*PC.nop,:);
        
        Ugp = zeros(size(Upk));
        Ugm = zeros(size(Upk));
        Ugn = zeros(size(Upk));
               
        % generating pulse signals
        Ugp =  (Upk > 0);       %plus voltage
        Ugm =  (Upk < 0);       %minus voltage
        Ugn = ~abs(abs(Upk));   %zero voltage
        k = 1;
        Ugn2 = zeros(size(Ugn));
        Ugn1 = zeros(size(Ugn));
        Ugn1(1) = Ugn(1);
        for n=2:length(Ugn)
         if (Ugn(n)-Ugn(n-1) > 0)
             k = -1*k;
         end
        Ugn1(n) = k*Ugn(n);
        end
        Ugn1 = Ugn1 & (Ugn1 > 0);  % N1 mode 
        Ugn2 = Ugn - Ugn1;         % N2 mode
        sw16 = Ugn2 | Ugp;         %pulse controlling switch 1 and 6            
        sw45 = Ugm | Ugn1;         %pulse controlling switch 4 and 5
        sw2 = Ugp | Ugn1;          %pulse controlling switch 2
        sw3 = Ugm | Ugn2;          %pulse controlling switch 3
                       
        Isw1 = (Ugp & (Ipk>0)).*Ipk; 
        Idi1 = abs((Ugp & (Ipk<0)).*Ipk);
        Isw5 = abs((Ugn1 & (Ipk<0)).*Ipk);
        Idi5 = (Ugn1 & (Ipk>0)).*Ipk;
        Isw2 = Isw1 + Idi5;
        Idi2 = Idi1 + Isw5;
        
        
        comm_s1 = sw16 - [sw16(end) sw16(1:end-1)];   %same signals for diode current commutation also
        comm_s2 = sw2 - [sw2(end) sw2(1:end-1)];
        comm_s5 = sw45 - [sw45(end) sw45(1:end-1)];
                
        s1_on=find(comm_s1 > eps);
        s2_on=find(comm_s2 > eps);
        s5_on=find(comm_s5 > eps);
        s1_off=find(comm_s1 < -eps);
        s2_off=find(comm_s2 < -eps);
        s5_off=find(comm_s5 < -eps);
        is1_on = abs(Isw1(s1_on));             % Current at commutations to SW
        is2_on = abs(Isw2(s2_on));
        is5_on = abs(Isw5(s5_on));
        is1_off = abs(Isw1(s1_off-1));           % Current at commutations from SW, index-1 is to take the current just before turn off
        is2_off = abs(Isw2(s2_off-1));
        is5_off = abs(Isw5(s5_off-1));
        id1_off = abs(Idi1(s1_off-1));           % Current at commutations from di
        id2_off = abs(Idi2(s2_off-1));
        id5_off = abs(Idi5(s5_off-1));
        
        Tjdi1 = OP.Ta(kop);        % Inital value for iteration
        Tjdi2 = OP.Ta(kop);             
        Tjdi5 = OP.Ta(kop); 
        Tjsw1 = OP.Ta(kop);
        Tjsw2 = OP.Ta(kop);  
        Tjsw5 = OP.Ta(kop);
        % Inital value for iteration
        niter=0;
        go=1;
        
        if kop==2, Up_pnom = Upk; Ip_pnom = Ipk/max(Ipk); end;
        % Iterate to find junction temps
        % if SCPAR.SW.Tdep || % No temperature dependence SC losses gIpken at one temperature only
        while go,
            niter=niter+1;
            if(niter) > PC.SCTHERM.maxiter,
                error('Max no of iterations exceeded in thermal calculation');
            end;
            Pcsw1 = Isw1*Von(SCPAR.SW.ON,Tjsw1,Isw1/SCPAR.igbtareascale(kpar))/npts;     
            Pcsw2 = Isw2*Von(SCPAR.SW.ON,Tjsw2,Isw2/SCPAR.igbtareascale(kpar))/npts; 
            Pcsw5 = Isw5*Von(SCPAR.SC3L.SW.ON,Tjsw5,Isw5/SCPAR.SC3L.igbtareascale(kpar))/npts;
            Pcdi1 = Idi1*Von(SCPAR.DI.ON,Tjdi1,Idi1/SCPAR.diodeareascale(kpar))/npts;  
            Pcdi2 = Idi2*Von(SCPAR.DI.ON,Tjdi2,Idi2/SCPAR.diodeareascale(kpar))/npts;     
            Pcdi5 = Idi5*Von(SCPAR.SC3L.DI.ON,Tjdi5,Idi5/SCPAR.SC3L.diodeareascale(kpar))/npts/2;        
            Ptonsw1 = SCPAR.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SW.TON , Tjsw1 , OP.Ud(kop)/N , is1_on/SCPAR.igbtareascale(kpar))) / T0 ;
            Ptonsw2 = SCPAR.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SW.TON , Tjsw2 , OP.Ud(kop)/N , is2_on/SCPAR.igbtareascale(kpar))) / T0 ;
            Ptonsw5 = SCPAR.SC3L.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SC3L.SW.TON , Tjsw5 , OP.Ud(kop)/Nc , is5_on/SCPAR.SC3L.igbtareascale(kpar))) / T0 ;
            Ptofsw1 = SCPAR.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SW.TOF , Tjsw1 , OP.Ud(kop)/N , is1_off/SCPAR.igbtareascale(kpar))) / T0 ;
            Ptofsw2 = SCPAR.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SW.TOF , Tjsw2 , OP.Ud(kop)/N , is2_off/SCPAR.igbtareascale(kpar))) / T0 ;
            Ptofsw5 = SCPAR.SC3L.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SC3L.SW.TOF , Tjsw5 , OP.Ud(kop)/Nc , is5_off/SCPAR.SC3L.igbtareascale(kpar))) / T0 ;
            Ptofdi1 = SCPAR.diodeareascale(kpar)*sum(swloss_calc(SCPAR.DI.TOF , Tjdi1 , OP.Ud(kop)/Nd , id1_off/SCPAR.diodeareascale(kpar))) / T0 ; 
            Ptofdi2 = SCPAR.diodeareascale(kpar)*sum(swloss_calc(SCPAR.DI.TOF , Tjdi2 , OP.Ud(kop)/Nd , id2_off/SCPAR.diodeareascale(kpar))) / T0 ;   
            Ptofdi5 = SCPAR.SC3L.diodeareascale(kpar)*sum(swloss_calc(SCPAR.SC3L.DI.TOF , Tjdi5 ,OP.Ud(kop)/Ndc , id5_off/SCPAR.SC3L.diodeareascale(kpar))) / T0 ;
            
            Ptotsw1 = Pcsw1 + Ptonsw1 + Ptofsw1;
            Ptotsw2 = Pcsw2 + Ptonsw2 + Ptofsw2;
            Ptotsw5 = Pcsw5 + Ptonsw5 + Ptofsw5;
            Ptotdi1 = Pcdi1 + Ptofdi1;   
            Ptotdi2 = Pcdi2 + Ptofdi2;
            Ptotdi5 = Pcdi5 + Ptofdi5;
            if isempty(PC.SC.diodefile)  %diode and igbts on the same submodule 
                                         %for a submodule with any no of diode and igbt, and any area of diode and igbt silicon area            
            %Ptot_eq1 = (SCPAR.SW.NPKG*Ptotsw1 + SCPAR.DI.NPKG*Ptotdi1)/(SCPAR.DI.NPKG*PC.SC.igbtareascale(kpar) + SCPAR.SW.NPKG*PC.SC.diodeareascale(kpar)); 
            %Ptot_eq2 = (SCPAR.SW.NPKG*Ptotsw2 + SCPAR.DI.NPKG*Ptotdi2)/(SCPAR.DI.NPKG*PC.SC.igbtareascale(kpar) + SCPAR.SW.NPKG*PC.SC.diodeareascale(kpar)); 
            Ptot_eq1 = Ptotsw1 + Ptotdi1;
            Ptot_eq2 = Ptotsw2 + Ptotdi2;
            %in the theramal calculation Rthha should be Rthva.....virtual to ambiant.             
            Tjsw1_next = sctherm(SCPAR.HSSW,SCPAR.SW.TH,SCPAR.igbtareascale(kpar),PC.SC.igbtpackincr,PC.SC.igbtcoolincr, OP.Ta(kop),Ptotsw1,Ptot_eq1);
            Tjsw2_next = sctherm(SCPAR.HSSW,SCPAR.SW.TH,SCPAR.igbtareascale(kpar),PC.SC.igbtpackincr,PC.SC.igbtcoolincr, OP.Ta(kop),Ptotsw2,Ptot_eq2);
            Tjdi1_next = sctherm(SCPAR.HSDI,SCPAR.DI.TH,SCPAR.diodeareascale(kpar),PC.SC.diodepackincr,PC.SC.diodecoolincr,OP.Ta(kop),Ptotdi1,Ptot_eq1);
            Tjdi2_next = sctherm(SCPAR.HSDI,SCPAR.DI.TH,SCPAR.diodeareascale(kpar),PC.SC.diodepackincr,PC.SC.diodecoolincr,OP.Ta(kop),Ptotdi2,Ptot_eq2);
            else
            Tjsw1_next = sctherm(SCPAR.HSSW,SCPAR.SW.TH,SCPAR.igbtareascale(kpar),PC.SC.igbtpackincr,PC.SC.igbtcoolincr, OP.Ta(kop),Ptotsw1);
            Tjsw2_next = sctherm(SCPAR.HSSW,SCPAR.SW.TH,SCPAR.igbtareascale(kpar),PC.SC.igbtpackincr,PC.SC.igbtcoolincr, OP.Ta(kop),Ptotsw2);
            Tjdi1_next = sctherm(SCPAR.HSDI,SCPAR.DI.TH,SCPAR.diodeareascale(kpar),PC.SC.diodepackincr,PC.SC.diodecoolincr,OP.Ta(kop),Ptotdi1);
            Tjdi2_next = sctherm(SCPAR.HSDI,SCPAR.DI.TH,SCPAR.diodeareascale(kpar),PC.SC.diodepackincr,PC.SC.diodecoolincr,OP.Ta(kop),Ptotdi2);
            end
            
            if isempty(PC.SC.SC3L.diodefile)  %diode and igbts on the same submodule 
                                              %for a submodule with any no of diode and igbt, and any area of diode and igbt silicon area            
            %Ptot_eq5 = (SCPAR.SC3L.SW.NPKG*Ptotsw5 + SCPAR.SC3L.DI.NPKG*Ptotdi5)/(SCPAR.SC3L.DI.NPKG*PC.SC.SC3L.igbtareascale(kpar) + SCPAR.SC3L.SW.NPKG*PC.SC.SC3L.diodeareascale(kpar)); 
            Ptot_eq5 = Ptotsw5 + Ptotdi5;
            %in the theramal calculation Rthha should be gIpken per cm2 area. 
            Tjsw5_next = sctherm(SCPAR.SC3L.HSSW,SCPAR.SC3L.SW.TH,SCPAR.SC3L.igbtareascale(kpar),PC.SC.SC3L.igbtpackincr,PC.SC.SC3L.igbtcoolincr, OP.Ta(kop),Ptotsw5,Ptot_eq5);
            Tjdi5_next = sctherm(SCPAR.SC3L.HSDI,SCPAR.SC3L.DI.TH,SCPAR.SC3L.diodeareascale(kpar),PC.SC.SC3L.diodepackincr,PC.SC.SC3L.diodecoolincr,OP.Ta(kop),Ptotdi5,Ptot_eq5);
            else
            Tjsw5_next = sctherm(SCPAR.SC3L.HSSW,SCPAR.SC3L.SW.TH,SCPAR.SC3L.igbtareascale(kpar),PC.SC.SC3L.igbtpackincr,PC.SC.SC3L.igbtcoolincr, OP.Ta(kop),Ptotsw5);
            Tjdi5_next = sctherm(SCPAR.SC3L.HSDI,SCPAR.SC3L.DI.TH,SCPAR.SC3L.diodeareascale(kpar),PC.SC.SC3L.diodepackincr,PC.SC.SC3L.diodecoolincr,OP.Ta(kop),Ptotdi5);    
            end
            
            temp = max(abs([Tjsw1_next-Tjsw1 Tjsw2_next-Tjsw2 Tjsw5_next-Tjsw5  Tjdi1_next-Tjdi1 Tjdi2_next-Tjdi2 Tjdi5_next-Tjdi5]));
            go = thiterate && (temp > PC.SCTHERM.Tjtol);
            
            Tjsw1 = Tjsw1_next;
            Tjsw2 = Tjsw2_next;
            Tjsw5 = Tjsw5_next;
            Tjdi1 = Tjdi1_next; 
            Tjdi2 = Tjdi2_next;
            Tjdi5 = Tjdi5_next;
        end;        
        SCLOSS.SW1.Tj.data(kpar,kop) =   Tjsw1;
        SCLOSS.SW1.Pc.data(kpar,kop) =   Pcsw1;
        SCLOSS.SW1.Pton.data(kpar,kop) = Ptonsw1;
        SCLOSS.SW1.Ptof.data(kpar,kop) = Ptofsw1;
        SCLOSS.SW1.Ptot.data(kpar,kop) = Ptotsw1;
        SCLOSS.SW2.Tj.data(kpar,kop) =   Tjsw2;
        SCLOSS.SW2.Pc.data(kpar,kop) =   Pcsw2;
        SCLOSS.SW2.Pton.data(kpar,kop) = Ptonsw2;
        SCLOSS.SW2.Ptof.data(kpar,kop) = Ptofsw2;
        SCLOSS.SW2.Ptot.data(kpar,kop) = Ptotsw2;
        SCLOSS.SW5.Tj.data(kpar,kop) =   Tjsw5;
        SCLOSS.SW5.Pc.data(kpar,kop) =   Pcsw5;
        SCLOSS.SW5.Pton.data(kpar,kop) = Ptonsw5;
        SCLOSS.SW5.Ptof.data(kpar,kop) = Ptofsw5;
        SCLOSS.SW5.Ptot.data(kpar,kop) = Ptotsw5;
        SCLOSS.DI1.Tj.data(kpar,kop) =   Tjdi1;
        SCLOSS.DI1.Pc.data(kpar,kop) =   Pcdi1;
        SCLOSS.DI1.Ptof.data(kpar,kop) = Ptofdi1;
        SCLOSS.DI1.Ptot.data(kpar,kop) = Ptotdi1;  
        SCLOSS.DI2.Tj.data(kpar,kop) =   Tjdi2;
        SCLOSS.DI2.Pc.data(kpar,kop) =   Pcdi2;
        SCLOSS.DI2.Ptof.data(kpar,kop) = Ptofdi2;
        SCLOSS.DI2.Ptot.data(kpar,kop) = Ptotdi2; 
        SCLOSS.DI5.Tj.data(kpar,kop) =   Tjdi5;
        SCLOSS.DI5.Pc.data(kpar,kop) =   Pcdi5;
        SCLOSS.DI5.Ptof.data(kpar,kop) = Ptofdi5;
        SCLOSS.DI5.Ptot.data(kpar,kop) = Ptotdi5;   
        SCLOSS.Ptot.data(kpar,kop) =   6*N*(Ptotsw1 + Ptotsw2 + Nc/N*Ptotsw5 + Nd/N*Ptotdi1 + Nd/N*Ptotdi2 + Ndc/N*Ptotdi5);  %total loss for all SC for all phase legs
    end;
end;

SCLOSS.N=N;  % no of igbts per valve
SCLOSS.Nd=Nd;  % no of diodes per valve
SCLOSS.Nc=Nc; % no of half the clamping igbts per leg
SCLOSS.Ncd=Ndc; %no of half the clamping diodes per leg
SCLOSS.Ip=Ip;
SCLOSS.wt=2*pi*(0:npts-1)'/npts;
SCLOSS.cases=1:length(OP.Ud);
SCLOSS.op_pt= angle(OP.Pac)+ j*sign(OP.Qac);  %operating point 
SCLOSS.pf=cos(SCLOSS.op_pt);   %power factor of oper. pts
SCLOSS.pnom.Up = Up_pnom;SCLOSS.pnom.Ip = Ip_pnom;



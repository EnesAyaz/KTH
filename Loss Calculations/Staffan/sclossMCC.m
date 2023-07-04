function SCLOSS = sclossMCC(Ip,s,f0,PC,OP,SCPAR)
% modified 23 march 2009
% Adil M.Elhaj
% Ip current in the time domain [OP,t]
% Up Phase voltage [OP,t]
% Ud DC Voltage [OP]
% Ta = ambient temperature [OP]
% SC semiconductor parameters
% .Thy = thyristor loss parameters
% .SW = switch loss parameters
% .swscale = scaling of switch active area [PAR]
% .DIPAR = diode  loss parameters
% .discale = scaling of diode active area [PAR]
% PC.SCTHERM.model
%       = 1 No thermal model, assume Tj=Ta in power loss calc;
%       = 2 Use thermal model and iterate to find proper T_j
%       
         if PC.SC.seriesautoselct, %  Calculate number of series devices
            N = ceil(2*max(OP.Ud)/(PC.SC.seriesmargin/100*SCPAR.SW.BV)); %num. of igbts
            if isempty(PC.SC.diodefile)
               Nd = N*SCPAR.DI.NPKG/SCPAR.SW.NPKG; % no of diodes 
            else
               Nd = ceil(2*max(OP.Ud)/(PC.SC.seriesmargin/100*SCPAR.DI.BV)); %num. of diodes
            end
        else
            N=PC.SC.Nseries;    %no of igbts 
            if isempty(PC.SC.diodefile)
               Nd = N*SCPAR.DI.NPKG/SCPAR.SW.NPKG; % no of diodes 
            else
               Nd = round(2*max(OP.Ud)/(PC.SC.seriesmargin/100*SCPAR.DI.BV)); %num. of diodes
            end
        end;
        
        %will be changed latter when GUI is defined
        thy = SCPAR.thy;
        N_thy=ceil(OP.Ntr*OP.Ud/(thy.VSSOA));   % no of  seriesly connected thyristors per valve 
        
        T0=1/f0;    % Fundamental cycle time
        thiterate = PC.SCTHERM.model > 1;   % Iterate to find proper junction temperatures?
        if thiterate, PC.SCTHERM.Tjtol=0.5; end; %tolerance in temperature;
        npts=length(s(1,:));    % No of time points

        % Reserve space
        SCLOSS.SW.Tj =   plstruc('Switch junction temperature',zeros(PC.npar,PC.nop),'C',1);
        SCLOSS.SW.Pc =   plstruc('Switch conduction losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.SW.Pton = plstruc('Switch turn on losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.SW.Ptof = plstruc('Switch turn off losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.SW.Ptot = plstruc('Switch total losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.DI.Tj =   plstruc('Diode junction temperature',zeros(PC.npar,PC.nop),'C',1);
        SCLOSS.DI.Pc =   plstruc('Diode conduction losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.DI.Pton = plstruc('Switch turn on losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.DI.Ptof = plstruc('Diode turn off losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.DI.Ptot = plstruc('Diode total losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.vsc.Ptot = plstruc('vsc total losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.thy.Pc =   plstruc('thyristor conduction losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.thy.Psw = plstruc('thyristor switching  losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.thy.Ptot = plstruc('thyristor total losses',zeros(PC.npar,PC.nop),'W',1);
        SCLOSS.Ptot =    plstruc('Total semiconductor losses',zeros(PC.npar,PC.nop),'W',1);

        samples = length(Ip);
        dt = 1/f0/samples;
        t=[0:dt:1/f0-dt];
        %generation of voltage and current waveforms
        Vtr = square(2*pi*OP.mf*t)*OP.Ud;           %VSC output voltage
        
        
       % Ideal reactor currents
      Ia = Ip;
      Ib = timeshift(Ia, -2*pi/3);  
      Ic = timeshift(Ia, 2*pi/3);
      % real cycloconverter phase voltages 
            
      Vacyc = OP.Ntr*OP.Ud/2*(s(1,:)- 1);
      Vbcyc = OP.Ntr*OP.Ud/2*(s(2,:)- 1);
      Vccyc = OP.Ntr*OP.Ud/2*(s(3,:)- 1);

      %Thyristor, Igbt and diode currents
      %Current of one valve of cycloconverter 
      Ithy = zeros(size(Ia));
      Ithy = Ia.*((Ia>=0) & (sign(Vacyc)~=sign(Vtr)));
      
      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
      % Generation of the transformer current from ideal reactor currents.
      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

      Ntr = OP.Ntr;
      Itr(1:samples)=0;
  
  for i=1:samples
  if sign(Vacyc(i)) == sign(Vtr(i)) & sign(Vbcyc(i)) == sign(-Vtr(i)) & sign(Vccyc(i)) == sign(-Vtr(i))      
     Itr(i) =  Itr(i)+Ia(i)*Ntr;
  elseif sign(Vacyc(i)) == sign(-Vtr(i)) & sign(Vbcyc(i)) == sign(Vtr(i)) & sign(Vccyc(i)) == sign(-Vtr(i))
      Itr(i) =Itr(i)+Ib(i)*Ntr;
  elseif sign(Vacyc(i)) == sign(-Vtr(i)) & sign(Vbcyc(i)) == sign(-Vtr(i)) & sign(Vccyc(i)) == sign(Vtr(i))
      Itr(i) = Itr(i)+Ic(i)*Ntr;
  elseif sign(Vacyc(i)) == sign(Vtr(i)) & sign(Vbcyc(i)) == sign(Vtr(i)) & sign(Vccyc(i)) == sign(-Vtr(i))
      Itr(i) = Itr(i)+(Ia(i)+Ib(i))*Ntr;
  elseif sign(Vacyc(i)) == sign(Vtr(i)) & sign(Vbcyc(i)) == sign(-Vtr(i)) & sign(Vccyc(i)) == sign(Vtr(i))
      Itr(i) = Itr(i)+(Ia(i)+Ic(i))*Ntr;
  elseif sign(Vacyc(i)) == sign(-Vtr(i)) & sign(Vbcyc(i)) == sign(Vtr(i)) & sign(Vccyc(i)) == sign(Vtr(i))
      Itr(i) = Itr(i)+(Ib(i)+Ic(i))*Ntr;
  else
      Itr(i)=0;
  end
  end
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
   %calculation of diode  currents 
   %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    ID2 = Itr.*((Itr>=0) & (Vtr<=0));
    Is1 = Itr.*((Itr>=0) & (Vtr>0));
    
    Tjdi = OP.Ta;             % Inital value for iteration
    Tjsw = OP.Ta;             % Inital value for iteration
    Tjthy = OP.Ta;            % Inital value for iteration
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %loss calculation for cycloconverter, thyristors 
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    thy = SCPAR.thy;
    A=thy.von.A;
    B=thy.von.B;      % (von coefficients)
    C=thy.von.C;
    D=thy.von.D;
    von_thy=(thy.Vt+thy.rt.*Ithy); %Thyristor on-staet voltage drop
    %von_thy=A+B.*Ithy/1000+C.*log(1+Ithy/1000)+D.*sqrt(Ithy/1000);%Thyristor on-staet voltage drop
                                                                  %(exact equation from data sheet,Proton Eletrotex)
    %von_thy=A+C.*Ithy+B.*log(1e-18+Ithy)+D.*sqrt(Ithy);%Thyristor on-staet voltage drop
                                                                  %(exact equation from data sheet ,Westcode)                                                              
    Ethy_on=(von_thy.*Ithy).*[diff(t) 0];             %Instataneous on-state energy/thyristor
    Pcond_cc= sum(Ethy_on)./(t(:,size(t,2))-t(:,1));  %  on-state loss in W for one thyristor

    %Switching losses
    Esw_approx=thy.Esw_fit;                                      
    Thy_sw = 0;
    for i=2:samples
    if (sign(Vacyc(i-1)) ~= sign(Vacyc(i)) && sign(Vtr(i-1)) == sign(Vtr(i)))
    Thy_sw=Thy_sw+2*(Esw_approx(1)*(abs(Ia(i))).^4+Esw_approx(2)*(abs(Ia(i))).^3+Esw_approx(3)*(abs(Ia(i))).^2+Esw_approx(4)*(abs(Ia(i)))+Esw_approx(5))/4*f0;%Turn-off losses=Turn-on losses (Assumption)
    end
    end
    Thy_switching=Thy_sw;               % switching losse in W for one thyristor
    Thy_loss=(Pcond_cc+Thy_switching);  %one thyristor losses
    
    %Thermal calculation
    Ta=Tjthy;
    Tj_thy=Ta+(thy.TH.Rthjc+thy.TH.Rthcs+0.5*thy.TH.Rthcs)*Thy_loss; %Thyristor junction temperature
    T=Tj_thy;
%Thyristor juction temperature, cycloconverter total losses
    SCLOSS.thy.Tj.data = Tj_thy;
    SCLOSS.thy.Pc.data = 12*N_thy*Pcond_cc;
    SCLOSS.thy.Psw.data = 12*N_thy*Thy_switching;
    SCLOSS.thy.Ptot.data = 12*N_thy*Thy_loss;
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Loss and thermal calculations
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

von_igbt=interp1(SCPAR.SW.ON.I , SCPAR.SW.ON.V , Is1,[],'extrap'); %IGBT on-staet voltage drop
von_di=interp1(SCPAR.DI.ON.I , SCPAR.DI.ON.V , ID2,[],'extrap');   %Diode onstate voltage drop

%On-state losses
%IGBT on-state losses
Eigbt_on=von_igbt.*Is1.*[diff(t) 0];              %Instataneous IGBT on-state energy
Pcond_igbt=sum(Eigbt_on)./(t(:,size(t,2))-t(:,1));%one IGBT losses (onstate)
%Diode on-state losses
Ed_on= von_di.*ID2.*[diff(t) 0];               %Instataneous diode on-state energy
Pcond_di=sum(Ed_on)./(t(:,size(t,2))-t(:,1));   %onstate losses/diode


%IGBT switching losses  
offTx=Is1.*-[diff(sign(Is1)) 0];                 %IGBT current vector at turn-off instances
Eoff_igbt=(2*OP.Ud/N)/(SCPAR.SW.TOF.U)*interp1(SCPAR.SW.TOF.I,SCPAR.SW.TOF.E,offTx,'linear','extrap');                      %Instantaneous turn-off energy vestor using interpolation
Pigbt_off=sum(Eoff_igbt)./(t(:,size(t,2))-t(:,1)); %Turn-off losses/IGBT

% Eon_IGBT=0;                                  %ZCS and ZVS turn-on
Pigbt_on=0; 
Ploss_igbt=(Pcond_igbt+Pigbt_off+ Pigbt_on);    %Total losses/IGBT in W
 
%Diode switching losses
offDi=ID2.*-[diff(sign(ID2)) 0];                %Diode current vector at turn-off instances               
Eoff_Di=(2*OP.Ud/N)/(SCPAR.DI.TOF.U)*interp1(SCPAR.DI.TOF.I,SCPAR.DI.TOF.E,offDi,'linear','extrap');                      %Instantaneous turn-off energy vestor using interpolation
PDi_off= sum(Eoff_Di)./(t(:,size(t,2))-t(:,1)); %Turn-off losses/diode


onDi=ID2.*[0 diff(sign(ID2))];                 %Diode current vector at turn-on instances      
Eon_Di=(2*OP.Ud/Nd)/(SCPAR.DI.TOF.U)*interp1(SCPAR.DI.TON.I,SCPAR.DI.TON.E,onDi,'linear','extrap');
PDi_on=sum(Eon_Di)./(t(:,size(t,2))-t(:,1));        %Turn-on losses/diode
Ploss_Di=(Pcond_di+PDi_off+PDi_on);                 %Total losses/diode in W

%Total losses
Pcond_vsc= 2*N*(Pcond_igbt+Nd/N*Pcond_di);       % Total VSC on-state loss in W
Psw_vsc=2*N*(PDi_off+PDi_on+Pigbt_off+Pigbt_on);  %Total VSC switching losses in W
Ploss_vsc=Pcond_vsc+ Psw_vsc;

%Thermal Calculation for a module having same no of diode and igbt on the same heat sink
Ta=OP.Ta;
Tj_Di=Ta+Ploss_Di*(SCPAR.DI.TH.Rthjc+SCPAR.DI.TH.Rthch)+SCPAR.HSSW.Rthha*0.5*(Ploss_Di+Ploss_igbt);
Tj_igbt=Ta+Ploss_igbt*(SCPAR.SW.TH.Rthjc+SCPAR.SW.TH.Rthch)+SCPAR.HSDI.Rthha*0.5*(Ploss_Di+Ploss_igbt);

SCLOSS.SW.Tj.data = Tj_igbt;
SCLOSS.SW.Pc.data = 2*N*Pcond_igbt;
SCLOSS.SW.Pton.data = 0;
SCLOSS.SW.Ptof.data = 2*N*Pigbt_off;
SCLOSS.SW.Ptot.data = 2*N*(Pcond_igbt+Pigbt_off+Pigbt_on);
SCLOSS.DI.Tj.data =   Tj_Di;
SCLOSS.DI.Pc.data =   2*Nd*Pcond_di;
SCLOSS.DI.Ptof.data = 2*Nd*PDi_off;
SCLOSS.DI.Pton.data = 2*Nd*PDi_on;
SCLOSS.DI.Ptot.data = 2*Nd*(Pcond_di+PDi_off+PDi_on);
SCLOSS.vsc.Ptot.data = Pcond_vsc+ Psw_vsc;  %total vsc loss in W
SCLOSS.Ptot.data = SCLOSS.vsc.Ptot.data + SCLOSS.thy.Ptot.data;   %total loss for all SC for all phase legs
SCLOSS.N = N;
SCLOSS.Nd = Nd;
SCLOSS.N_thy=N_thy;
            
%save(['C:\mebtu\PELAB\VSC\code\case_definition\' 'lossmcc'],'SCLOSS');
[SCLOSS.SW.Pc.data SCLOSS.SW.Ptof.data SCLOSS.SW.Ptot.data;SCLOSS.DI.Pc.data SCLOSS.DI.Ptof.data+SCLOSS.DI.Pton.data SCLOSS.DI.Ptot.data;SCLOSS.thy.Pc.data SCLOSS.thy.Psw.data SCLOSS.thy.Ptot.data]   
SCLOSS.Ptot.data   
    
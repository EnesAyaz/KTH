function SCLOSS = sclossMMC(Ip,Up,f0,PC,OP,SCPAR)
%
% Semiconductor loss calculation for modular mutilevel converter
% 
% 
% Ip current in the time domain [OP,t]
% Up Phase switching function for each cell [OP,cell#,t]
% Ud DC Voltage [OP]
% Ta = ambient temperature [OP]
% SCPAR semiconductor parameters         
%     .Nseries                      Number of cells per arm
%     .seriesmargin                 Voltage margin in number of cells
%     .seriesautoselct 0            Automatic choice of the number of cells?
%     .SCCASC                       Cell data
%         .BP,.IS                   Valve data for bypass and insertion valves respectively      
%               igbtfile            Switch parameter file data
%               diodefile           Diode parameter file data
%               igbthsfile          Switch heat sink parameter file data
%               diodehsfile         Diode parameter file data
%               igbtareascale
%               diodeareascale
%               igbtcoolerspeed
%               diodecoolerspeed 
%               igbtpackincr
%               diodepackincr
%               igbtcoolincr
%               diodecoolincr
%               Nseries
%               seriesmargin
%               seriesautoselct%
% PC.SCTHERM.model
%       = 1 No thermal model, assume Tj=Ta in power loss calc;
%       = 2 Use thermal model and iterate to find proper T_j
%
T0=1/f0;                                    % Fundamental cycle time
thiterate = PC.SCTHERM.model > 1;           % Iterate to find proper junction temperatures?
if thiterate, PC.SCTHERM.Tjtol=0.5; end;    % Tolerance in temperature;
npts=length(Ip);     % No of time points

%% LOAD SEMICONDUCTOR AND VALVE DATA

paths=load('pelabpaths');
pelabroot=paths.pelabroot;

% Bypass valve
SCPAR.SCCASC.BP.SW=load(findfile(SCPAR.SCCASC.BP.igbtfile,pelabroot,paths.semicond));
if all(isfield(SCPAR.SCCASC.BP.SW, {'SW','DI'})) %&& isempty(SCPAR.SCCASC.diodefile), 
    % Combo file 
    SCPAR.SCCASC.BP.DI=SCPAR.SCCASC.BP.SW.DI;   %diode data on switch file 
    SCPAR.SCCASC.BP.SW=SCPAR.SCCASC.BP.SW.SW;
elseif ~isempty(PC.SCPAR.SCCASC.BP.diodefile) %this can be modified to allow file input for clamping diodes in 3l NPC
    SCPAR.SCCASC.BP.DI=load(findfile(SCPAR.SCCASC.BP.diodefile,pelabroot,paths.semicond));
    SCPAR.SCCASC.BP.DI=SCPAR.SCCASC.BP.DI.DI;   %diode data on separate file   
    SCPAR.SCCASC.BP.SW=SCPAR.SCCASC.BP.SW.SW;
else
    error('Insufficient semiconductor data');
end;
SCPAR.SCCASC.BP.HSSW=load(findfile(SCPAR.SCCASC.BP.igbthsfile,pelabroot,paths.semicond));
SCPAR.SCCASC.BP.HSDI=load(findfile(SCPAR.SCCASC.BP.diodehsfile,pelabroot,paths.semicond));
%  Calculate number of series devices in the cell valves
if SCPAR.SCCASC.BP.seriesautoselct,                 
    SCPAR.SCCASC.BP.Nseries = round(SCPAR.SCCASC.BP.seriesmargin * 4*max(OP.Ud)/SCPAR.SCCASC.BP.SW.BV/PC.Ncells); 
end;


% Insertion valve
SCPAR.SCCASC.IS.SW=load(findfile(SCPAR.SCCASC.IS.igbtfile,pelabroot,paths.semicond));
if all(isfield(SCPAR.SCCASC.IS.SW, {'SW','DI'})) %&& isempty(SCPAR.SCCASC.diodefile), 
    % Combo file 
    SCPAR.SCCASC.IS.DI=SCPAR.SCCASC.IS.SW.DI;   %diode data on switch file 
    SCPAR.SCCASC.IS.SW=SCPAR.SCCASC.IS.SW.SW;
elseif ~isempty(PC.SCPAR.SCCASC.IS.diodefile) %this can be modified to allow file input for clamping diodes in 3l NPC
    SCPAR.SCCASC.IS.DI=load(findfile(SCPAR.SCCASC.IS.diodefile,pelabroot,paths.semicond));
    SCPAR.SCCASC.IS.DI=SCPAR.SCCASC.IS.DI.DI;   %diode data on separate file   
    SCPAR.SCCASC.IS.SW=SCPAR.SCCASC.IS.SW.SW;
else
    error('Insufficient semiconductor data');
end;
SCPAR.SCCASC.IS.HSSW=load(findfile(SCPAR.SCCASC.IS.igbthsfile,pelabroot,paths.semicond));
SCPAR.SCCASC.IS.HSDI=load(findfile(SCPAR.SCCASC.IS.diodehsfile,pelabroot,paths.semicond));
%  Calculate number of series devices in the cell valves
if SCPAR.SCCASC.IS.seriesautoselct,                 
    SCPAR.SCCASC.IS.Nseries = round(SCPAR.SCCASC.IS.seriesmargin * 4*max(OP.Ud)/SCPAR.SCCASC.IS.SW.BV/PC.Ncells); 
end;

% Reserve space for outputs
SCLOSS.BP.SW.Tj =   plstruc('Switch junction temperature, insertion valve',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.BP.SW.Pc =   plstruc('Switch conduction losses, insertion valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.BP.SW.Pton = plstruc('Switch turn on losses, insertion valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.BP.SW.Ptof = plstruc('Switch turn off losses, insertion valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.BP.SW.Ptot = plstruc('Switch total losses, insertion valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.BP.DI.Tj =   plstruc('Diode junction temperature, insertion valve',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.BP.DI.Pc =   plstruc('Diode conduction losses, insertion valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.BP.DI.Ptof = plstruc('Diode turn off lossese, insertion valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.BP.DI.Ptot = plstruc('Diode total losses, insertion valve',zeros(PC.npar,PC.nop),'W',1);

SCLOSS.IS.SW.Tj =   plstruc('Switch junction temperature, bypass valve',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.IS.SW.Pc =   plstruc('Switch conduction losses, bypass valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.IS.SW.Pton = plstruc('Switch turn on losses, bypass valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.IS.SW.Ptof = plstruc('Switch turn off losses, bypass valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.IS.SW.Ptot = plstruc('Switch total losses, bypass valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.IS.DI.Tj =   plstruc('Diode junction temperature, bypass valve',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.IS.DI.Pc =   plstruc('Diode conduction losses, bypass valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.IS.DI.Ptof = plstruc('Diode turn off lossese, bypass valve',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.IS.DI.Ptot = plstruc('Diode total losses, bypass valve',zeros(PC.npar,PC.nop),'W',1);

SCLOSS.Ptot=     plstruc('Total semiconductor losses in the converter, bypass valve',zeros(PC.nop),'W',1);

%% CALCULATION PART

% CODE FOR THE (Ncells+1) level MMC case
for kpar = 1:PC.npar
     for kop = 1:PC.nop
         Ipk = Ip.data(kop+(kpar-1)*PC.nop,:);
         Upk = Up(kop+(kpar-1)*PC.nop,:,:);
         Iarm = abs((Ipk/2)+(Id/3));
         for k = 1:PC.Ncells
             IS.sw(k,:) = (Ipk<0&Up(k,:)>0);
             IS.di(k,:) = (Ipk>=0&Up(k,:)>0);
             BP.sw(k,:) = (Ipk>=0&Up(k,:)==0);
             BP.di(k,:) = (Ipk<0&Up(k,:)==0);
             I.IS.sw(k,:) = Iarm.*IS.sw(k,:);
             I.IS.di(k,:) = Iarm.*IS.di(k,:);
             I.BP.sw(k,:) = Iarm.*BP.sw(k,:);
             I.BP.di(k,:) = Iarm.*BP.di(k,:);
             
             comm_IS.s(k,:) =  IS.sw(k,:) - [IS.sw(k,:,end) IS.sw(k,:,1:end-1)];
             comm_IS.d(k,:) =  IS.di(k,:) - [IS.di(k,:,end) IS.di(k,:,1:end-1)];
             comm_BP.s(k,:) =  BP.sw(k,:) - [BP.sw(k,:,end) BP.sw(k,:,1:end-1)];
             comm_BP.D(k,:) =  BP.di(k,:) - [BP.di(k,:,end) BP.di(k,:,1:end-1)];
             
             IS.s_on(k,:)=find(comm_IS.s(k,:) > eps);
             BP.s_on(k,:)=find(comm_BP.s(k,:) > eps);
             IS.s_off(k,:)=find(comm_IS.s(k,:) < -eps);
             BP.s_off(k,:)=find(comm_BP.s(k,:) < -eps);
             IS.d_off(k,:)=find(comm_IS.d(k,:) < -eps);
             BP.d_off(k,:)=find(comm_BP.d(k,:) < -eps);
             I.IS.s_on(k,:) = abs(Iarm(IS.s_on(k,:)));
             I.BP.s_on(k,:) = abs(Iarm(BP.s_on(k,:)));
             I.IS.s_off(k,:) = abs(Iarm(IS.s_off(k,:)));
             I.BP.s_off(k,:) = abs(Iarm(BP.s_off(k,:)));
             I.IS.d_off(k,:) = abs(Iarm(IS.d_off(k,:)));
             I.BP.d_off(k,:) = abs(Iarm(BP.d_off(k,:)));
             
             TjIS.d(k) = OP.Ta(kop);
             TjBP.d(k) = OP.Ta(kop);
             TjIS.s(k) = OP.Ta(kop);
             TjBP.s(k) = OP.Ta(kop);
             
             % Inital value for iteration
             niter=0;
             go=1;
         end;
         
         if kop==2, Up_pnom = Upk; Ip_pnom = Ipk/max(Ipk); end;
         % Iterate to find junction temps
         % if SCPAR.SW.Tdep || % No temperature dependence SC losses given at one temperature only
         while go,
             niter=niter+1;
             if(niter) > PC.SCTHERM.maxiter,
                 error('Max no of iterations exceeded in thermal calculation');
             end;         

             for k = 1:PC.Ncells
                 PcIS.sw(k) = I.IS.sw(k,:)*Von(SCPAR.SW.ON,TjIS.s(k),IIS.sw(k)/SCPAR.igbtareascale(kpar))/npts;     % Unlike the 2-level, it should not be divided by 2 as both arms are conducting simultaneously
                 PcIS.di(k) = I.IS.di(k,:)*Von(SCPAR.DI.ON,TjIS.d(k),IIS.di(k)/SCPAR.igbtareascale(kpar))/npts;
                 PcBP.sw(k) = I.BP.sw(k,:)*Von(SCPAR.SW.ON,TjBP.s(k),IBP.sw(k)/SCPAR.igbtareascale(kpar))/npts;     
                 PcBP.di(k) = I.BP.di(k,:)*Von(SCPAR.DI.ON,TjBP.d(k),IBP.di(k)/SCPAR.igbtareascale(kpar))/npts;
                 PtonIS.sw(k) = SCPAR.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SW.TON , TjIS.s(k) , OP.Ud(kop)/N , iIS.s_on(k)/SCPAR.igbtareascale(kpar))) / T0 / 2;
                 PtonBP.sw(k) = SCPAR.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SW.TON , TjBP.s(k) , OP.Ud(kop)/N , iBP.s_on(k)/SCPAR.igbtareascale(kpar))) / T0 / 2;
                 PtofIS.sw(k) = SCPAR.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SW.TOF , TjIS.s(k) , OP.Ud(kop)/N , iIS.s_off(k)/SCPAR.igbtareascale(kpar))) / T0 / 2;
                 PtofBP.sw(k) = SCPAR.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SW.TOF , TjBP.s(k) , OP.Ud(kop)/N , iBP.s_off(k)/SCPAR.igbtareascale(kpar))) / T0 / 2;
                 PtofIS.di(k) = SCPAR.diodeareascale(kpar)*sum(swloss_calc(SCPAR.DI.TOF , TjIS.d(k) , OP.Ud(kop)/Nd , iIS.d_off(k)/SCPAR.diodeareascale(kpar))) / T0 / 2;
                 PtofBP.di(k) = SCPAR.diodeareascale(kpar)*sum(swloss_calc(SCPAR.DI.TOF , TjBP.d(k) , OP.Ud(kop)/Nd , iBP.d_off(k)/SCPAR.diodeareascale(kpar))) / T0 / 2;
                
                 PtotIS.sw(k) = PcIS.sw(k) + PtonIS.sw(k) + PtofIS.sw(k);
                 PtotBP.sw(k) = PcBP.sw(k) + PtonBP.sw(k) + PtofBP.sw(k);
                 PtotIS.di(k) = PcIS.di(k) + PtofIS.di(k);
                 PtotBP.di(k) = PcBP.di(k) + PtofBP.di(k);
                 
                 if isempty(PC.SC.diodefile)  %diode and igbts on the same submodule 
                                         %for a submodule with any no of diode and igbt, and any area of diode and igbt silicon area            
                 %Ptot_eq1 = (SCPAR.SW.NPKG*Ptotsw1 + SCPAR.DI.NPKG*Ptotdi1)/(SCPAR.DI.NPKG*PC.SC.igbtareascale(kpar) + SCPAR.SW.NPKG*PC.SC.diodeareascale(kpar)); 
                 %Ptot_eq2 = (SCPAR.SW.NPKG*Ptotsw2 + SCPAR.DI.NPKG*Ptotdi2)/(SCPAR.DI.NPKG*PC.SC.igbtareascale(kpar) + SCPAR.SW.NPKG*PC.SC.diodeareascale(kpar)); 
                 PtotIS_eq1(k) = PtotIS.sw(k) + PtotIS.di(k);
                 PtotBP_eq2(k) = PtotBP.sw(k) + PtotBP.di(k);
                 %in the theramal calculation Rthha represents Rthva....virtual to ambiant             
                 TjIS.s_next(k) = sctherm(SCPAR.HSSW,SCPAR.SW.TH,SCPAR.igbtareascale(kpar),PC.SC.igbtpackincr,PC.SC.igbtcoolincr, OP.Ta(kop),PtotIS.sw(k),PtotIS_eq1(k));
                 TjBP.s_next(k) = sctherm(SCPAR.HSSW,SCPAR.SW.TH,SCPAR.igbtareascale(kpar),PC.SC.igbtpackincr,PC.SC.igbtcoolincr, OP.Ta(kop),PtotBP.sw(k),PtotBP_eq2(k));
                 TjIS.d_next(k) = sctherm(SCPAR.HSDI,SCPAR.DI.TH,SCPAR.diodeareascale(kpar),PC.SC.diodepackincr,PC.SC.diodecoolincr,OP.Ta(kop),PtotIS.di(k),PtotIS_eq1(k));
                 TjIS.d_next(k) = sctherm(SCPAR.HSDI,SCPAR.DI.TH,SCPAR.diodeareascale(kpar),PC.SC.diodepackincr,PC.SC.diodecoolincr,OP.Ta(kop),PtotBP.di(k),PtotBP_eq2(k));
                 else
                 TjIS.s_next(k) = sctherm(SCPAR.HSSW,SCPAR.SW.TH,SCPAR.igbtareascale(kpar),PC.SC.igbtpackincr,PC.SC.igbtcoolincr, OP.Ta(kop),PtotIS.sw(k));
                 TjBP.s_next(k) = sctherm(SCPAR.HSSW,SCPAR.SW.TH,SCPAR.igbtareascale(kpar),PC.SC.igbtpackincr,PC.SC.igbtcoolincr, OP.Ta(kop),PtotBP.sw(k));
                 TjIS.d_next(k) = sctherm(SCPAR.HSDI,SCPAR.DI.TH,SCPAR.diodeareascale(kpar),PC.SC.diodepackincr,PC.SC.diodecoolincr,OP.Ta(kop),PtotIS.di(k));
                 TjIS.d_next(k) = sctherm(SCPAR.HSDI,SCPAR.DI.TH,SCPAR.diodeareascale(kpar),PC.SC.diodepackincr,PC.SC.diodecoolincr,OP.Ta(kop),PtotBP.di(k));
                 end
                 temp = max(abs([TjIS.s_next(k)-TjIS.s(k) TjBP.s_next(k)-TjBP.s(k) TjIS.d_next(k)-TjIS.d(k) TjBP.d_next(k)-TjBP.d(k)]));
                 go = thiterate && (temp > PC.SCTHERM.Tjtol);
                 
                 TjIS.s(k) = TjIS.s_next(k);
                 TjBP.s(k) = TjBP.s_next(k);
                 TjIS.d(k) = TjIS.d_next(k);
                 TjBP.d(k) = TjBP.d_next(k);
             end
         end
         
        SCLOSS.IS.SW.Tj.data(kpar,kop) = sum(TjIS.s);
        SCLOSS.IS.SW.Pc.data(kpar,kop) = sum(PcIS.sw);
        SCLOSS.IS.SW.Pton.data(kpar,kop) = sum(PtonIS.sw);
        SCLOSS.IS.SW.Ptof.data(kpar,kop) = sum(PtofIS.sw);
        SCLOSS.IS.SW.Ptot.data(kpar,kop) = sum(PtotIS.sw);
        SCLOSS.IS.DI.Tj.data(kpar,kop) = sum(TjIS.d);
        SCLOSS.IS.DI.Pc.data(kpar,kop) = sum(PcIS.di);
        SCLOSS.IS.DI.Ptof.data(kpar,kop) = sum(PtofIS.di);
        SCLOSS.IS.DI.Ptot.data(kpar,kop) = sum(PtotIS.di);
        
        SCLOSS.BP.SW.Tj.data(kpar,kop) = sum(TjBP.s);
        SCLOSS.BP.SW.Pc.data(kpar,kop) = sum(PcBP.sw);
        SCLOSS.BP.SW.Pton.data(kpar,kop) = sum(PtonBP.sw);
        SCLOSS.BP.SW.Ptof.data(kpar,kop) = sum(PtofBP.sw);
        SCLOSS.BP.SW.Ptot.data(kpar,kop) = sum(PtotBP.sw);
        SCLOSS.BP.DI.Tj.data(kpar,kop) = sum(TjBP.d);
        SCLOSS.BP.DI.Pc.data(kpar,kop) = sum(PcBP.di);
        SCLOSS.BP.DI.Ptof.data(kpar,kop) = sum(PtofBP.di);
        SCLOSS.BP.DI.Ptot.data(kpar,kop) = sum(PtotBP.di);
        
        SCLOSS.Ptot.data(kpar,kop) =   6*Nseries*(sum(PtotIS.sw) + sum(PtotBP.sw) + Ndseries/Nseries*PtotIS.di + Ndseries/Nseries*PtotBP.di);  %total loss for all SC for all phase legs
     
     end
end

 SCLOSS.N =N;     % no of igbts per valve
 SCLOSS.Nd =Nd;     % no of diodes per valve
 SCLOSS.Ip=Ip;
 SCLOSS.wt=2*pi*(0:npts-1)'/npts;
 SCLOSS.cases=1:length(OP.Ud);
 SCLOSS.op_pt= angle(OP.Pac)+ 1i*sign(OP.Qac);  %operating point
 SCLOSS.pf=cos(SCLOSS.op_pt);   %power factor of oper. pts
 SCLOSS.pnom.Up = Up_pnom;SCLOSS.pnom.Ip = Ip_pnom;

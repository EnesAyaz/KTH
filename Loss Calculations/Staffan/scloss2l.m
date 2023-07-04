function SCLOSS = scloss2l(Ip,Up,f0,PC,OP,SCPAR)
% modified 2010-08-19
% Staffan Norrga
% 2 level VSC Semiconductor losses

% Ip current in the time domain [OP,t]
% Up Phase voltage [OP,t]
% Ud DC Voltage [OP]
% Ta = ambient temperature [OP]
% SC semiconductor parameters
% .SW = switch loss parameters
% .swscale = scaling of switch active area [PAR]
% .DI = diode  loss parameters
% .discale = scaling of diode active area [PAR]
% PC.SCTHERM.model
%       = 1 No thermal model, assume Tj=Ta in power loss calc;
%       = 2 Use thermal model and iterate to find proper T_j
%
if PC.SC.seriesautoselct, %  Calculate number of series devices
    N = round(PC.SC.seriesmargin * 2*max(OP.Ud)/SCPAR.SW.BV); 
else
    N=PC.SC.Nseries;
end;

Nd = N*SCPAR.DI.NPKG/SCPAR.SW.NPKG; % no of diodes

T0=1/f0;    % Fundamental cycle time
thiterate = PC.SCTHERM.model > 1;   % Iterate to find proper junction temperatures?
if thiterate, PC.SCTHERM.Tjtol=0.5; end; %tolerance in temperature;
npts=length(Up);    % No of time points

% Reserve space
SCLOSS.SW.Tj =   plstruc('Switch junction temperature',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.SW.Pc =   plstruc('Switch conduction losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW.Pton = plstruc('Switch turn on losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW.Ptof = plstruc('Switch turn off losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.SW.Ptot = plstruc('Switch total losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.DI.Tj =   plstruc('Diode junction temperature',zeros(PC.npar,PC.nop),'C',1);
SCLOSS.DI.Pc =   plstruc('Diode conduction losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.DI.Ptof = plstruc('Diode turn off losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.DI.Ptot = plstruc('Diode total losses',zeros(PC.npar,PC.nop),'W',1);
SCLOSS.Ptot=     plstruc('Total semiconductor losses',zeros(PC.npar,PC.nop),'W',1);

for kpar = 1:PC.npar
    for kop = 1:PC.nop
        Ipk = Ip.data(kop+(kpar-1)*PC.nop,:);
        Upk = Up(kop+(kpar-1)*PC.nop,:);
        
        sw = (Ipk>=0&Upk>0) | (Ipk<0&Upk<=0);   % =1 when current passes through switch
        di = ~sw;                               % =1 when current passes through diode
        Isw = abs(Ipk.*sw);
        Idi = abs(Ipk.*di);
        
        comm = sw - [sw(end) sw(1:end-1)];   % Nonzero at commutations (NOTE includes natural as well as forced commutations)
        
        s2d=find(comm < -eps);
        d2s=find(comm > eps);
        is2d = abs(Ipk(s2d));            % Current at commutations switch to diode
        id2s = abs(Ipk(d2s));            % Current at commutations diode to switch
        
        Tjdi = OP.Ta(kop);             % Inital value for iteration
        Tjsw = OP.Ta(kop);             % Inital value for iteration
        niter=0;
        go=1;
        
        if kop==2, Up_pnom = Upk; Ip_pnom = Ipk/max(Ipk); end;
        % Iterate to find junction temps
        % if SCPAR.SW.Tdep || % No temperature dependence SC losses given at one temperature only
        while go,
            niter=niter+1;
            if(niter) > PC.SCTHERM.maxiter,
                error('Max no of iterations exceeded in thermal calculation');
            end;
            Pcsw = Isw*Von(SCPAR.SW.ON,Tjsw,Isw/SCPAR.igbtareascale(kpar))/npts/2;     % '/2' -> Loss in one of two devices in a phase leg
            Pcdi = Idi*Von(SCPAR.DI.ON,Tjdi,Idi/SCPAR.diodeareascale(kpar))/npts/2;
            Ptonsw = SCPAR.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SW.TON , Tjsw , 2*OP.Ud(kop)/N , id2s/SCPAR.igbtareascale(kpar))) / T0 / 2;
            Ptofsw = SCPAR.igbtareascale(kpar)*sum(swloss_calc(SCPAR.SW.TOF , Tjsw , 2*OP.Ud(kop)/N , is2d/SCPAR.igbtareascale(kpar))) / T0 / 2;
            Ptofdi = SCPAR.diodeareascale(kpar)*sum(swloss_calc(SCPAR.DI.TOF , Tjdi ,2*OP.Ud(kop)/Nd , id2s/SCPAR.diodeareascale(kpar))) / T0 / 2;
            
            Ptotsw = Pcsw + Ptonsw + Ptofsw;
            Ptotdi = Pcdi + Ptofdi;
            
            if isempty(PC.SC.diodefile)  % diode and igbts in the same package
                %Ptot_eq = (SCPAR.SW.NPKG*Ptotsw + SCPAR.DI.NPKG*Ptotdi)/(SCPAR.DI.NPKG*PC.SC.igbtareascale(kpar) + SCPAR.SW.NPKG*PC.SC.diodeareascale(kpar));
                Ptot_eq = Ptotsw + Ptotdi;
                %Rthha represents Rthva...virtual to ambiant
                Tjsw_next = sctherm(SCPAR.HSSW,SCPAR.SW.TH,SCPAR.igbtareascale(kpar),PC.SC.igbtpackincr,PC.SC.igbtcoolincr, OP.Ta(kop),Ptotsw,Ptot_eq);
                Tjdi_next = sctherm(SCPAR.HSDI,SCPAR.DI.TH,SCPAR.diodeareascale(kpar),PC.SC.diodepackincr,PC.SC.diodecoolincr,OP.Ta(kop),Ptotdi,Ptot_eq);
            else % separate IGBT and diode packages
                Tjsw_next = sctherm(SCPAR.HSSW,SCPAR.SW.TH,SCPAR.igbtareascale(kpar),PC.SC.igbtpackincr,PC.SC.igbtcoolincr, OP.Ta(kop),Ptotsw);
                Tjdi_next = sctherm(SCPAR.HSDI,SCPAR.DI.TH,SCPAR.diodeareascale(kpar),PC.SC.diodepackincr,PC.SC.diodecoolincr,OP.Ta(kop),Ptotdi);
            end
            
            temp = max([abs(Tjsw_next - Tjsw) abs(Tjdi_next - Tjdi)]);
            go = thiterate && (temp > PC.SCTHERM.Tjtol);
            
            Tjsw = Tjsw_next;
            Tjdi = Tjdi_next;
        end;
        SCLOSS.SW.Tj.data(kpar,kop) = Tjsw;
        SCLOSS.SW.Pc.data(kpar,kop) = Pcsw;
        SCLOSS.SW.Pton.data(kpar,kop) = Ptonsw;
        SCLOSS.SW.Ptof.data(kpar,kop) = Ptofsw;
        SCLOSS.SW.Ptot.data(kpar,kop) = Ptotsw;
        SCLOSS.DI.Tj.data(kpar,kop) =   Tjdi;
        SCLOSS.DI.Pc.data(kpar,kop) =   Pcdi;
        SCLOSS.DI.Ptof.data(kpar,kop) = Ptofdi;
        SCLOSS.DI.Ptot.data(kpar,kop) = Ptotdi;
        SCLOSS.Ptot.data(kpar,kop) =   6*N*(Ptotsw + Nd/N*Ptotdi);  %total loss for all SC for all phase legs
    end;
end;
SCLOSS.N =N;     % no of igbts per valve
SCLOSS.Nd =Nd;     % no of diodes per valve
SCLOSS.Ip=Ip;
SCLOSS.wt=2*pi*(0:npts-1)'/npts;
SCLOSS.cases=1:length(OP.Ud);
SCLOSS.op_pt= angle(OP.Pac)+ 1i*sign(OP.Qac);  %operating point
SCLOSS.pf=cos(SCLOSS.op_pt);   %power factor of oper. pts
SCLOSS.pnom.Up = Up_pnom;SCLOSS.pnom.Ip = Ip_pnom;

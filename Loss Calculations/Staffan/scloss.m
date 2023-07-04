function SCLOSS = scloss(Ip,Up,f0,PC,OP,SCPAR)
%
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
% modified 10 march 2009
% mebtu b. beza
% Semiconductor losses calculation

switch PC.TOPOLOGY,
    case 1 %case for 2l........
        SCLOSS = scloss2l(Ip,Up,f0,PC,OP,SCPAR);
    case 2,  %case for 3l NPC
        SCLOSS = scloss3l(Ip,Up,f0,PC,OP,SCPAR);
    case 3,             % 3l ANPC case
        SCLOSS = scloss3lA(Ip,Up,f0,PC,OP,SCPAR);
    case 4,             % MCC case
        SCLOSS = sclossMCC(Ip,Up,f0,PC,OP,SCPAR);
    case 5,             % MCC case
        SCLOSS = sclossMMC(Ip,Up,f0,PC,OP,SCPAR);
    otherwise
        error('This configuration not implemented in loss calculation');
end



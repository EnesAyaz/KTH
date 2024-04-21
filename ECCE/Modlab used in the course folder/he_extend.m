function [mavect, angvect]=he_extend(hctrl,mastart,start_angles, mainc,ma_min,ma_max, varargin)
%
% Extend a harmonic elimination solution set to as large range of
% modulation indices as possible
%
%
p=2*length(start_angles)+1;
%
if nargin>6
    if varargin{1}=='up'
        up=1;
        dn=0;
    elseif varargin{1}=='dn'
        up=0;
        dn=1;
    else
        up=1;
        dn=1;
    end;
else
    up=1;
    dn=1;
end;

downsol_angles=[];
downsol_ma=[];
upsol_angles=[];
upsol_ma=[];


% try downwards
if dn,
    init_angles=start_angles;
    ma=mastart-mainc;
    k2=0;
    ok=1;
    while ok & ma>=ma_min
        [alpha, residual] = harmelim(hctrl, p , ma, init_angles);
        conv_err=sqrt(sum(residual.^2))>0.01;
        seq_err= any( ([alpha pi/2] - [0 alpha])<=eps);
        if ~seq_err & ~conv_err
            k2=k2+1;
            init_angles=alpha;
            downsol_angles(k2,:)=alpha;
            downsol_ma(k2)=ma;
            ma=ma-mainc;
        else
            ok=0;
        end;
    end;

    if k2>0 % revert order
        downsol_angles=downsol_angles(k2:-1:1,:);
        downsol_ma=downsol_ma(k2:-1:1);
    end;
end;

% try upwards
if up
    init_angles=start_angles;
    ma=mastart+mainc;
    k2=0;
    ok=1;
    while ok & ma<=0.91*4/pi,
        [alpha, residual] = harmelim(hctrl, p , ma, init_angles);
        conv_err=sqrt(sum(residual.^2))>0.01;
        seq_err= any( ([alpha pi/2] - [0 alpha])<=eps);
        if ~seq_err & ~conv_err
            k2=k2+1;
            init_angles=alpha;
            upsol_angles(k2,:)=alpha;
            upsol_ma(k2)=ma;
            ma=ma+mainc;
        else
            ok=0;
        end;
    end;
end;
angvect = [downsol_angles ; start_angles ; upsol_angles];
mavect = [downsol_ma mastart upsol_ma];

% end of opwm_extend function

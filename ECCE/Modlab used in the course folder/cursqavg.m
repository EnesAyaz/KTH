function cursqavg= cursqavg(sll,p);
%cursqavg(sll,p) Computes the average of the square of the normalised ripple current
% during a fundamental cycle (cf. Skudelny)
%
% cursqavg= cursqavg(sll,p);
%
% sll: normalised line-line voltage
% p: pulse number
%
N=length(sll);
Nint=round(N/p)-1;       % No of samples in a carrier interval

Nbegin=1;
cursqavg_ack=0;
for rakn=1:p,
    Nend=min(N,Nbegin + Nint);
    slli=sll(Nbegin:Nend);
    cursqavg_ack=cursqavg_ack + cursqavgi(slli);
    Nbegin=Nend+1;
end;

cursqavg=cursqavg_ack/p;


function cursqavgi= cursqavgi(slli)

% Computes the average of the square of the ripple current
% during a switching interval

N=length(slli);
sllr=slli-mean(slli);    % Remove average

intg=0;
for rakn=1:N,              % Integrate to get current
    cur(rakn) = intg;
    intg = intg + sllr(rakn)/N;
end;

cursq=cur.^2;              % Square of the dimensionless current
cursqavgi=mean(cursq);      % Average of the square of the current
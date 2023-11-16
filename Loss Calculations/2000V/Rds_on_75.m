load('RdsTj_89A.mat')

%%

plot(RdsTj.Tj, RdsTj.Rds)
hold on


rds_T=[25:5:175];
figure
rds_inter = interp1(RdsTj.Tj,RdsTj.Rds,rds_T);


plot(RdsTj.Tj,RdsTj.Rds,'o',rds_T,rds_inter,':x');
% xlim([0 2*pi]);
title('(Default) Linear Interpolation');

close all
clear Rds_Tj







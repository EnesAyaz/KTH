I=Id;
fs=1/(time(2)-time(1));
flp=100e6;
[I_lp, lp]= lowpass(I,flp,fs);
ws=1;
I_mf= medfilt1(I_lp,ws);
 I_mf=circshift(I_mf,200)
% I_mf=I_lp;
%%
% plot(time,I)
% hold on;
% plot(time,I_lp)
% hold on;
V=Vds;
fs=1/(time(2)-time(1));
flp=100e6;
[V_lp, lp]= lowpass(V,flp,fs);
ws=1;
V_mf= medfilt1(V_lp,ws);
% 
% V_mf=V_lp;

 % V_mf=circshift(V_mf,22)
%%
figure()
plot(time,V_mf);
hold on
plot(time,I_mf);
hold on
xlim([1.1e-5 1.2e-5])
 % xlim([2.15e-5 2.25e-5])
%%
% %%
% x=50
% differences =V_mf(x+1:end) -V_mf(1:end-x);
% % ws=100;
% % differences= medfilt1(differences,ws);
% plot(time(x+1:end),differences);
% hold on
% plot(time,V_mf);
% 
% 
% tspan=40e-6;
% t1=10e-6;
% toff_tspan= [(tspan/20)+t1-1e-6 (tspan/40)+t1+1e-6 ]
% 
% xlim(toff_tspan)
% 
% figure();
% plot(time,V_mf.*I_mf);
% xlim([2e-5 2.4e-5])



load('\\ug.kth.se\dfs\home\e\n\enesa\appdata\xp.V2\Desktop\OneDrive_1_3-28-2024\measuredData.mat');
%%
time=Data.Time;
U_RS=Data.U_R1_S1;
U_TR=Data.U_T1_R1;
U_ST= Data.U_S1_T1;

I_R=Data.I_R1;
I_S= Data.I_S1;
I_T= Data.I_T1;
%%
U_R= (U_RS-U_TR)/3;
U_T=  (U_TR-U_ST)/3;
U_S=  (U_ST-U_RS)/3;


n=3;
t_sample= time(2)-time(1);
T_fundamental=1/300;
time_end=round(T_fundamental*n/t_sample);

U_R=U_R(1:time_end);
I_R=I_R(1:time_end);
U_T=U_T(1:time_end);
I_T=I_T(1:time_end);
U_S=U_S(1:time_end);
I_S=I_S(1:time_end);

time=linspace(0,T_fundamental*n,length(I_R));

P=U_R.*I_R+U_S.*I_S+U_T.*I_T;
%%
close all
figure(1)
plot(time,P)
hold on;


%%
L = length(P);  % Length of signal

P_mag=fft(P);
P_mag=abs(P_mag/L);
P_mag=P_mag(1:L/2+1);
P_mag(2:end-1)=2*P_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));

P_angle=fft(P);
P_angle=angle(P_angle);
P_angle=P_angle(1:L/2+1);

P_x=real(P_mag.*exp(1i*P_angle));


figure(2)
stem(f/1e3,P_x,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[0 0 0]);
hold on;
%xlim([8 12])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_RS(f)|")
hold on


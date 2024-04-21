load('\\ug.kth.se\dfs\home\e\n\enesa\appdata\xp.V2\Desktop\OneDrive_1_3-28-2024\measuredData.mat');
%%
control_1=1;
if control_1==1
figure1 = figure;
axes1 = axes('Parent',figure1);
hold(axes1,'on');


% Create multiple line objects using matrix input to plot
plot1=plot(Data.Time-Data.Time(1), Data.U_R1_S1);
plot2=plot(Data.Time-Data.Time(1), Data.I_R1);
set(plot1,'DisplayName','V_{RS}','Color',[0 0 1]);
set(plot2,'DisplayName','I_{R}','Color',[1 0 0]);
xlim([0,0.4194])

% Create ylabel
ylabel({'Voltage (V)','Current (A)'});

% Create xlabel
xlabel({'Time (s)'});

box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.723809525459295 0.7162698453854 0.1464285697788 0.148809519693965]);
end


%%
time=Data.Time;
U_RS=Data.U_R1_S1;
U_TS=-Data.U_S1_T1;
I_R=Data.I_R1;
I_T=Data.I_T1;

%%
L = length(U_RS);  % Length of signal

U_RS_mag=fft(U_RS);
U_RS_mag=abs(U_RS_mag/L);
U_RS_mag=U_RS_mag(1:L/2+1);
U_RS_mag(2:end-1)=2*U_RS_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));

%%
% control_2=0;
% if control_2==1
% plot(f/1e3,U_RS_mag,"LineWidth",3);
% xlim([0 40])
% title("Single-Sided Amplitude Spectrum of X(t)")
% xlabel("f (kHz)")
% ylabel("|U_RS(f)|")
% end
%%
U_RS_angle=fft(U_RS);
U_RS_angle=angle(U_RS_angle);
U_RS_angle=U_RS_angle(1:L/2+1);
%%
% control_2=0;
% if control_2==1
% stem(f/1e3,U_RS_angle,"LineWidth",3);
% xlim([0 40])
% title("Single-Sided Amplitude Spectrum of X(t)")
% xlabel("f (kHz)")
% ylabel("|U_RS(f)|")
% end
%%
threshold=max(abs(U_RS_mag)/100);
U_RS_angle(abs(U_RS_mag)<threshold)=0; 
U_RS_mag(abs(U_RS_mag)<threshold)=0;
%%
control_2=1;
if control_2==1
stem(f/1e3,U_RS_mag,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_RS(f)|")
hold on
end
%%
control_2=0;
if control_2==1
stem(f/1e3,U_RS_angle,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_RS(f)|")
hold on
end
%%
L = length(I_R);  % Length of signal

I_R_mag=fft(I_R);
I_R_mag=abs(I_R_mag/L);
I_R_mag=I_R_mag(1:L/2+1);
I_R_mag(2:end-1)=2*I_R_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));

% %%
% control_2=0;
% if control_2==1
% plot(f/1e3,I_R_mag,"LineWidth",3);
% xlim([0 40])
% title("Single-Sided Amplitude Spectrum of X(t)")
% xlabel("f (kHz)")
% ylabel("|I_R(f)|")
% end
%%
I_R_angle=fft(I_R);
I_R_angle=angle(I_R_angle);
I_R_angle=I_R_angle(1:L/2+1);
%%
% control_2=0;
% if control_2==1
% stem(f/1e3,I_R_angle,"LineWidth",3);
% xlim([0 40])
% title("Single-Sided Amplitude Spectrum of X(t)")
% xlabel("f (kHz)")
% ylabel("|I_R(f)|")
% end
%%
threshold=max(abs(I_R_mag)/100);
I_R_angle(abs(I_R_mag)<threshold)=0; 
I_R_mag(abs(I_R_mag)<threshold)=0;
%%
control_2=1;
if control_2==1
stem(f/1e3,I_R_mag,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|I_R(f)|")
hold on
end
%%
control_2=0;
if control_2==1
stem(f/1e3,I_R_angle,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|I_R(f)|")
end
%%


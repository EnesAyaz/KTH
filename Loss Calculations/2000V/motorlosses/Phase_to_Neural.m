load('\\ug.kth.se\dfs\home\e\n\enesa\appdata\xp.V2\Desktop\OneDrive_1_3-28-2024\measuredData.mat');
%%
time=Data.Time;
U_RS=Data.U_R1_S1;
U_TR=Data.U_T1_R1;

U_R= (U_RS-U_TR)/3;
I_R=Data.I_R1;

n=3;
t_sample= time(2)-time(1);
T_fundamental=1/300;
time_end=round(T_fundamental*n/t_sample);

U_R=U_R(1:time_end);
I_R=I_R(1:time_end);
time=linspace(0,T_fundamental*n,length(I_R));
%%
L = length(U_R);  % Length of signal

U_R_mag=fft(U_R);
U_R_mag=abs(U_R_mag/L);
U_R_mag=U_R_mag(1:L/2+1);
U_R_mag(2:end-1)=2*U_R_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));

U_R_angle=fft(U_R);
U_R_angle=angle(U_R_angle);
U_R_angle=U_R_angle(1:L/2+1);
%%

L = length(I_R);  % Length of signal

I_R_mag=fft(I_R);
I_R_mag=abs(I_R_mag/L);
I_R_mag=I_R_mag(1:L/2+1);
I_R_mag(2:end-1)=2*I_R_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));

I_R_angle=fft(I_R);
I_R_angle=angle(I_R_angle);
I_R_angle=I_R_angle(1:L/2+1);
%%
% threshold=max(abs(U_R_mag)/100);
% U_R_angle(abs(U_R_mag)<threshold)=0; % determines the low-amplitude threshold
% U_R_mag(abs(U_R_mag)<threshold)=0;
% I_R_angle(abs(U_R_mag)<threshold)=0; % determines the low-amplitude threshold
% I_R_mag(abs(U_R_mag)<threshold)=0;
% f(abs(U_R_mag)<threshold)=0;
% f=f';


P=((U_R_mag.*I_R_mag)/2).*cos(U_R_angle-I_R_angle);
P=P';

Ph=(sum(P)-P(n+1))*3
%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create stem
stem(f/1e3,3*P,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[0 0 0]);

% Create ylabel
ylabel('|P(f)|','FontName','Times New Roman');

% Create xlabel
xlabel('f (kHz)','FontName','Times New Roman');

% Create title
% title('Single-Sided Amplitude Spectrum of P(t)');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[1 40]);
% ylim([-500 500])
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'XGrid','on',...
    'XMinorGrid','on','YGrid','on','YMinorGrid','on');

%%
close all
figure(1)
stem(f/1e3,U_R_angle*180/pi,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[0 0 0]);
hold on;
% stem(f/1e3,I_R_angle*180/pi,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[1 0 0],'LineStyle','--');
xlim([0 24])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_RS(f)|")
hold on

%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create stem
stem(f/1e3,U_R_mag,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[0 0 0]);

% Create ylabel
ylabel('|V_R(f)|','FontName','Times New Roman');

% Create xlabel
xlabel('f (kHz)','FontName','Times New Roman');

% Create title
title('Single-Sided Amplitude Spectrum of V_R(t)');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 40]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'XGrid','on',...
    'XMinorGrid','on','YGrid','on','YMinorGrid','on');
%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create stem
stem(f/1e3,I_R_mag,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[0 0 0]);

% Create ylabel
ylabel('|I_R(f)|','FontName','Times New Roman');

% Create xlabel
xlabel('f (kHz)','FontName','Times New Roman');

% Create title
title('Single-Sided Amplitude Spectrum of I_R(t)');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 40]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'XGrid','on',...
    'XMinorGrid','on','YGrid','on','YMinorGrid','on');
%%
figure1=figure();
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create stem
stem(f/1e3,U_R_mag,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[0 0 0]);

% Create ylabel
ylabel('|V_R(f)|','FontName','Times New Roman');

% Create xlabel
xlabel('f (kHz)','FontName','Times New Roman');

% Create title
title('Single-Sided Amplitude Spectrum of V_R(t)');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 40]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'XGrid','on',...
    'XMinorGrid','on','YGrid','on','YMinorGrid','on');


%%
figure(2)
stem(f/1e3,U_R_mag,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[0 0 0]);
hold on;
stem(f/1e3,I_R_mag,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[1 0 0],'LineStyle','--');
xlim([8 12])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_R(f)|")
hold on

%%
Angle_difference= (U_R_angle-I_R_angle);
for i=1:length(Angle_difference)
if Angle_difference(i)<0
Angle_difference(i)=Angle_difference(i)+2*pi;
end
end
%%

figure(3)
stem(f/1e3,Angle_difference*180/pi,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[0 0 1]);
xlim([8 13])
yline(90)
title("Phase Differences between Current and Voltage")
xlabel("f (kHz)")
ylabel("Angle (^o)")
hold on
%%
figure3 = figure;

% Create axes
axes1 = axes('Parent',figure3);
hold(axes1,'on');

% Create multiple stem objects using matrix input to stem
stem(f/1e3,Angle_difference*180/pi,'MarkerSize',1,'Marker','none','LineWidth',2,...
    'Color',[0 0 1],...
    'Parent',axes1);

% Create yline
yline(90,'Parent',axes1,'LineStyle','--','LineWidth',2);

% Create ylabel
ylabel('Angle (^o)','FontName','Times New Roman');

% Create xlabel
xlabel('f (kHz)','FontName','Times New Roman');

% Create title
title('Phase Differences between Current and Voltage');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[8 13]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% Create textarrow
annotation(figure3,'textarrow',[0.257142857142857 0.208928571428571],...
    [0.818047619047619 0.730952380952381],'String',{'90^o'},'FontSize',15,...
    'FontName','Times New Roman');






%%
fo=-156.2;
fsw_m_4fo=92.9;
fsw_m_2fo=-40.7;
% fsw_m_fo=-20.1;
% fsw_p_fo=-153.6;
fsw_p_2fo=55.5;
fsw_p_4fo=-77.2;


a=fsw_m_4fo+fsw_p_4fo;
b=fsw_m_2fo+fsw_p_2fo;

b-2*fo-360
b+2*fo+360
% a-4*fo-360-360
% fsw_m_fo+fsw_p_fo

a-4*fo-360-360;
a+4*fo+360+360;





load('\\ug.kth.se\dfs\home\e\n\enesa\appdata\xp.V2\Desktop\OneDrive_1_3-28-2024\measuredData.mat');
%%
time=Data.Time;
U_RS=Data.U_R1_S1;
U_TS=-Data.U_S1_T1;
U_TR=Data.U_T1_R1;
I_R=Data.I_R1;
I_T=Data.I_T1;

n=3;
t_sample= time(2)-time(1);
T_fundamental=1/300;
time_end=round(T_fundamental*n/t_sample);

U_RS=U_RS(1:time_end);
U_TS=U_TS(1:time_end);
I_R=I_R(1:time_end);
I_T=I_T(1:time_end);
time=linspace(0,T_fundamental*n,length(I_T));

%%
L = length(U_RS);  % Length of signal

U_RS_mag=fft(U_RS);
U_RS_mag=abs(U_RS_mag/L);
U_RS_mag=U_RS_mag(1:L/2+1);
U_RS_mag(2:end-1)=2*U_RS_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));

U_RS_angle=fft(U_RS);
U_RS_angle=angle(U_RS_angle);
U_RS_angle=U_RS_angle(1:L/2+1);
%%
control_2=0;
if control_2==1

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create stem
stem(f/1e3,U_RS_mag,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[0 0 0]);

% Create ylabel
ylabel('|U_RS(f)|','FontName','Times New Roman');

% Create xlabel
xlabel('f (kHz)','FontName','Times New Roman');

% Create title
% title('Single-Sided Amplitude Spectrum of X(t)');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 45]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);

end
%%
%%
% threshold=max(abs(U_RS_mag)/100);
% U_RS_angle(abs(U_RS_mag)<threshold)=0; 
% U_RS_mag(abs(U_RS_mag)<threshold)=0;

%%
L = length(U_TS);  % Length of signal

U_TS_mag=fft(U_TS);
U_TS_mag=abs(U_TS_mag/L);
U_TS_mag=U_TS_mag(1:L/2+1);
U_TS_mag(2:end-1)=2*U_TS_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));

U_TS_angle=fft(U_TS);
U_TS_angle=angle(U_TS_angle);
U_TS_angle=U_TS_angle(1:L/2+1);

% threshold=max(abs(U_TS_mag)/100);
% U_TS_angle(abs(U_TS_mag)<threshold)=0; 
% U_TS_mag(abs(U_TS_mag)<threshold)=0;

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

% threshold=max(abs(I_R_mag)/10000);
% I_R_angle(abs(I_R_mag)<threshold)=0; 
% I_R_mag(abs(I_R_mag)<threshold)=0;
%%
control_2=0;
if control_2==1

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create stem
stem(f/1e3,I_R_mag,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[0 0 0]);

% Create ylabel
ylabel('|I_R(f)|','FontName','Times New Roman');

% Create xlabel
xlabel('f (kHz)','FontName','Times New Roman');

% Create title
% title('Single-Sided Amplitude Spectrum of X(t)');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 45]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);

end


%%
L = length(I_T);  % Length of signal

I_T_mag=fft(I_T);
I_T_mag=abs(I_T_mag/L);
I_T_mag=I_T_mag(1:L/2+1);
I_T_mag(2:end-1)=2*I_T_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));

I_T_angle=fft(I_T);
I_T_angle=angle(I_T_angle);
I_T_angle=I_T_angle(1:L/2+1);

% threshold=max(abs(I_T_mag)/10000);
% I_T_angle(abs(I_T_mag)<threshold)=0; 
% I_T_mag(abs(I_T_mag)<threshold)=0;
%%
control_2=0;
if control_2==1
stem(f/1e3,U_RS_mag,"LineWidth",3);
hold on;
stem(f/1e3,I_R_mag,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_RS(f)|")
hold on
end
%%

U_RS_h= U_RS_mag.*exp(1i*U_RS_angle);
U_TS_h= U_TS_mag.*exp(1i*U_TS_angle);
I_R_h= I_R_mag.*exp(1i*I_R_angle);
I_T_h= I_T_mag.*exp(1i*I_T_angle);
% 
% I_R_angle= I_R_angle;
% I_T_angle= I_T_angle+0.275;

P=((U_RS_mag.*I_R_mag)/2).*cos(U_RS_angle-I_R_angle)+ ((U_TS_mag.*I_T_mag)/2).*cos(U_TS_angle-I_T_angle);

% P= real(U_RS_h.*conj(I_R_h) + U_TS_h.*conj(I_T_h))/2;
%%
control_2=1;
if control_2==1

figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create stem
stem(f/1e3,P,'MarkerSize',1,'Marker','none','LineWidth',2,'Color',[0 0 0]);

% Create ylabel
ylabel('|P_R(f)|','FontName','Times New Roman');

% Create xlabel
xlabel('f (kHz)','FontName','Times New Roman');

% Create title
% title('Single-Sided Amplitude Spectrum of X(t)');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 45]);
ylim([-1000 1000])
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% set(axes1,'FontName','Times New Roman','FontSize',15,'YScale', 'log');


end
%%
Ph=(sum(P)-P(n+1))


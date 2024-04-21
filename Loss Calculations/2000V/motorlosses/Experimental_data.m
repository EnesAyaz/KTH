load('\\ug.kth.se\dfs\home\e\n\enesa\appdata\xp.V2\Desktop\OneDrive_1_3-28-2024\measuredData.mat');
%%
%%
plot(Data.Time, Data.U_R1_S1)
hold on;
plot(Data.Time, Data.I_R1)

%%
time=Data.Time;
U_RS=Data.U_R1_S1;
U_ST=Data.U_S1_T1;
U_TR=Data.U_T1_R1;
I_R=Data.I_R1;

%%
L = length(U_RS);  % Length of signal

U_RS_mag=fft(U_RS);
U_RS_mag=abs(U_RS_mag/L);
U_RS_mag=U_RS_mag(1:L/2+1);
U_RS_mag(2:end-1)=2*U_RS_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));
plot(f/1e3,U_RS_mag,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_RS(f)|")

U_RS_angle=fft(U_RS);
U_RS_angle=angle(U_RS_angle);
U_RS_angle=U_RS_angle(1:L/2+1);
stem(f/1e3,U_RS_angle,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_RS(f)|")

threshold=max(abs(U_RS_mag)/100);
U_RS_angle(abs(U_RS_mag)<threshold)=0; 
U_RS_mag(abs(U_RS_mag)<threshold)=0;
%%
plot(f/1e3,U_RS_mag,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_RS(f)|")
%%
stem(f/1e3,U_RS_angle,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_RS(f)|")

%%



L = length(U_ST);  % Length of signal

U_ST_mag=fft(U_ST);
U_ST_mag=abs(U_ST_mag/L);
U_ST_mag=U_ST_mag(1:L/2+1);
U_ST_mag(2:end-1)=2*U_ST_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));
plot(f/1e3,U_ST_mag,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_ST(f)|")

U_ST_angle=fft(U_ST);
U_ST_angle=angle(U_ST_angle);
U_ST_angle=U_ST_angle(1:L/2+1);
stem(f/1e3,U_ST_angle,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_ST(f)|")

threshold=max(abs(U_ST_mag)/100);
U_ST_angle(abs(U_ST_mag)<threshold)=0; 
U_ST_mag(abs(U_ST_mag)<threshold)=0;

plot(f/1e3,U_ST_mag,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_ST(f)|")

stem(f/1e3,U_ST_angle,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_ST(f)|")


%%

L = length(U_TR);  % Length of signal

U_TR_mag=fft(U_TR);
U_TR_mag=abs(U_TR_mag/L);
U_TR_mag=U_TR_mag(1:L/2+1);
U_TR_mag(2:end-1)=2*U_TR_mag(2:end-1);

Fs=1/(time(2)-time(1)); % Sampling frequency   
f = Fs/L*(0:(L/2));
plot(f/1e3,U_TR_mag,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_TR(f)|")

U_TR_angle=fft(U_TR);
U_TR_angle=angle(U_TR_angle);
U_TR_angle=U_TR_angle(1:L/2+1);
stem(f/1e3,U_TR_angle,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_TR(f)|")

threshold=max(abs(U_TR_mag)/100);
U_TR_angle(abs(U_TR_mag)<threshold)=0; 
U_TR_mag(abs(U_TR_mag)<threshold)=0;

plot(f/1e3,U_TR_mag,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_TR(f)|")

stem(f/1e3,U_TR_angle,"LineWidth",3);
xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_TR(f)|")

%%
stem(f/1e3,U_RS_angle*180/pi,"LineWidth",3);
hold on 
stem(f/1e3,U_ST_angle*180/pi,"LineWidth",3);
hold on 
stem(f/1e3,U_TR_angle*180/pi,"LineWidth",3);
hold on 

xlim([0 40])
title("Single-Sided Amplitude Spectrum of X(t)")
xlabel("f (kHz)")
ylabel("|U_TR(f)|")




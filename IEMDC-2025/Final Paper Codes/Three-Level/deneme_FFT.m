load('C:\Github\KTH\IEMDC-2025\Final Paper Codes\Three-Level\Waweforms\F\current_waveform1.mat')
figure()
plot(data.time,data.i_q_time)
hold on
plot(data.time,data.i_d_time)

% 
% data.i_d_time(end)-data.i_d_time(1)
% 
% data.i_q_time(end)-data.i_q_time(1)


theta= linspace(0,2*pi,length(data.time));

ialpha = data.i_d_time .* cos(theta) - data.i_q_time .* sin(theta);
ibeta = data.i_d_time .* sin(theta) + data.i_q_time .* cos(theta);
% Inverse Clarke Transformation: alpha-beta to abc
i_a = ialpha;
i_b = -0.5 * ialpha + (sqrt(3) / 2) * ibeta;
i_c = -0.5 * ialpha - (sqrt(3) / 2) * ibeta;


figure2= figure('Name','Time domain phase-A Current');
axes1 = axes('Parent',figure2);

plot(data.time*1e3,i_a,"LineWidth",2) 

xlabel("Time(ms)")
ylabel("Current (A)")
set(axes1,'FontName','Times New Roman','FontSize',15);



%%
sample_time=data.time(2)-data.time(1);
Fs=1/sample_time;
Y = fft(i_a);
L=length(data.time);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);
f = Fs/L*(0:(L/2));
%%

figure1= figure('Name','FFT for phase-A');
subplot(4,1,1)
plot(f/data.fundamentalfrequency,P1,"LineWidth",2) 
% title("Single-Sided Amplitude Spectrum of Phase Curremt")
xlabel("Harmonic Number")
% ylabel("Magnitude of Phase Current (A)")
xlim([2 12])
% ylim([0 20])

subplot(4,1,2)
plot(f/data.fundamentalfrequency,P1,"LineWidth",2) 
% title("Single-Sided Amplitude Spectrum of Phase Curremt")
xlabel("Harmonic Number")
% ylabel("Magnitude of Phase Current (A)")
xlim([2*data.fsw/data.fundamentalfrequency-7 2*data.fsw/data.fundamentalfrequency+7 ])

subplot(4,1,3)
plot(f/data.fundamentalfrequency,P1,"LineWidth",2) 
% title("Single-Sided Amplitude Spectrum of Phase Curremt")
xlabel("Harmonic Number")
% ylabel("Magnitude of Phase Current (A)")
xlim([4*data.fsw/data.fundamentalfrequency-7 4*data.fsw/data.fundamentalfrequency+7 ])

subplot(4,1,4)
plot(f/data.fundamentalfrequency,P1,"LineWidth",2) 
% title("Single-Sided Amplitude Spectrum of Phase Curremt")
xlabel("Harmonic Number")
% ylabel("Magnitude of Phase Current (A)")
xlim([2 5*data.fsw/data.fundamentalfrequency+7 ])

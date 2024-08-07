Ld=50e-6; % H
Lq=100e-6; % H

f_fund= 500; 
theta=0;

harmonic_number_1= 21;
V1_mag= 5;
V1_phase= 0;

harmonic_number_1= 23;
V2_mag= 5;
V2_phase= 0;

t_period= 4/f_fund;

sample_time=1e-6;
time=0:sample_time:t_period;

 V1= V1_mag*sin(2*pi*harmonic_number_1*f_fund*time-V1_phase);
 V2= V2_mag*sin(2*pi*harmonic_number_2*f_fund*time-V2_phase);
 L= ((Ld+Lq)/2)+ ((-Ld+Lq)/2)*sin(2*2*pi*f_fund*time-theta); % double fundamental

plot(time,V1);
hold on
plot(time,V2);
hold on
plot(time, L*1e5);


%%
V1_integ2= -1*V1_mag*cos(2*pi*harmonic_number_1*f_fund*time-V1_phase)/2/pi/harmonic_number_1/f_fund;
V2_integ2= -1*V2_mag*cos(2*pi*harmonic_number_2*f_fund*time-V2_phase)/2/pi/harmonic_number_2/f_fund;
%%
I1= V1_integ2./L;
plot(time,I1)
hold on;
I2= V2_integ2./L;
plot(time,I2)

%%

P1=V1.*I1;
P2=V2.*I2;

plot(time,P1)
hold on;
plot(time,P2)

mean(P1)
mean(P2)

%%
Fs=1/sample_time ; % Sampling frequency          
T = 1/Fs;             % Sampling period       
L = length(I1);             % Length of signal
t = (0:L-1)*T;        % Time vector

Y = fft(I1);
P3 = abs(Y/L);
P1 = P3(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

P3 = angle(Y/L);
P1_angle = P3(1:L/2+1);
P1_angle(2:end-1) = P1_angle(2:end-1);

f = Fs/L*(0:(L/2));

Y = fft(I2);
P3 = abs(Y/L);
P2 = P3(1:L/2+1);
P2(2:end-1) = 2*P2(2:end-1);

P3 = angle(Y/L);
P2_angle = P3(1:L/2+1);
P2_angle(2:end-1) = P2_angle(2:end-1);

figure(1)
stem(f,P1,"LineWidth",1) 
hold on
stem(f,P2,"LineWidth",1) ;

xlim( [4000, 16000 ] )

figure(2)
% stem(f,180*P1_angle/pi,"LineWidth",1) 
hold on
stem(f,180*P2_angle/pi,"LineWidth",1) ;

xlim( [4000, 16000 ] )

%%
Fs=1/sample_time ; % Sampling frequency          
T = 1/Fs;             % Sampling period       
L = length(I1);             % Length of signal
t = (0:L-1)*T;        % Time vector

Y = fft(I1+I2);
P3 = abs(Y/L);
P1 = P3(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

P3 = angle(Y/L);
P1_angle = P3(1:L/2+1);
P1_angle(2:end-1) = P1_angle(2:end-1);

f = Fs/L*(0:(L/2));


figure(3)
stem(f,P1,"LineWidth",1) 
hold on 
xlim( [4000, 16000 ] )

figure(4)

stem(f,180*P1_angle/pi,"LineWidth",1) ;

xlim( [4000, 16000 ] )



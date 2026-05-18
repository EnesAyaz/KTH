ma=0.3;
theta=linspace(0,2*pi,13);

% theta=pi/180*[0 45 90 135 180 225 270 315]

phA=ma*cos(theta);
phB=ma*cos(theta-2*pi/3);
phC=ma*cos(theta+2*pi/3);
% common_mode= -sign(ma*cos(3*theta))/3;
 % common_mode= 1/3;
common_mode= 0;
% common_mode= -1/3;

figure();
plot(theta,phA) 
hold on
plot(theta,phB) 
hold on
plot(theta,phC) 
hold on
plot(theta,common_mode) 

duty_ratios_phA= (1+phA+common_mode)/2;
duty_ratios_phB= (1+phB+common_mode)/2;
duty_ratios_phC= (1+phC+common_mode)/2;


figure();
stem(theta,duty_ratios_phA) 
hold on
stem(theta,duty_ratios_phB) 
hold on
stem(theta,duty_ratios_phC) 
hold on
stem(theta,duty_ratios_phA+duty_ratios_phB+duty_ratios_phC) 
hold on

PhiA = 0*duty_ratios_phA; % Explicitly set to single

PhiB=360*mod((duty_ratios_phA+duty_ratios_phB)/2,1);

PhiC =360*mod((duty_ratios_phA+2*duty_ratios_phB+duty_ratios_phC)/2,1);

duty_without_phA=(1+phA)/2;
duty_without_phB=(1+phB)/2;
duty_without_phC=(1+phC)/2;

theta*180/pi
[duty_without_phA;duty_without_phB;duty_without_phC; duty_without_phA+duty_without_phB+duty_without_phC ]
[ duty_ratios_phA;duty_ratios_phB;duty_ratios_phC; duty_ratios_phA+duty_ratios_phB+duty_ratios_phC]
[PhiA;  PhiB ; PhiC]

close all

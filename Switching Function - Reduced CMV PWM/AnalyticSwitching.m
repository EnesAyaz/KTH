

fo=1e3;
fs=40e3;
ma=0.5;

time= 0:1/fs/1000:2/fo;

DA= (1+ma*sin(2*pi*fo.*time))/2;
DB= (1+ma*sin(2*pi*fo.*time-2*pi/3))/2;
DC= (1+ma*sin(2*pi*fo.*time+2*pi/3))/2;

% figure();
% plot(time,DA)
% hold on;
% plot(time,DB)
% hold on;
% plot(time,DC)
% hold on;

PhiB=2*pi/3;
PhiC=-2*pi/3;

PhiB=0;
PhiC=0;

SA_fs= (2/pi).*sin(pi.*DA).*cos(2*pi*fs.*time);
SB_fs= (2/pi).*sin(pi.*DB).*cos(2*pi*fs.*time-PhiB);
SC_fs= (2/pi).*sin(pi.*DC).*cos(2*pi*fs.*time-PhiC);

figure();
% plot(time,SA_fs)
% hold on;
% plot(time,SB_fs)
% hold on;
% plot(time,SC_fs)
% hold on;
plot(time, (SA_fs+SB_fs+SC_fs)/3)
hold on;



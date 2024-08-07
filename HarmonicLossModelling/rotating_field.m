number_of_theta=1000;
theta= linspace(0,2*pi, number_of_theta);

Ax=[];
ABx=[];
timex=[];
for a=0:0.1:1
time=a*1.0000e-04;
freq=10e3;
omega=2*pi*freq;

A= 1*sin(-theta+omega*time);
B= 1*sin(theta+omega*time-pi/2);
AB=A+B;

figure(1)
% plot(theta,A);
% hold on;
% plot(theta,B);
% hold on;
plot(theta,A+B);
hold on;

Ax=[Ax, rms(A)];
ABx=[ABx rms(AB) ] ;

timex=[timex time];

end
%%
plot( timex, ABx)
hold on;
plot( timex, Ax)

% sum(ABx)
% sum(Ax)


theta= linspace(0,2*pi,1000);
id=500;
iq=0;

third_harmonic=500*cos(3*theta)/6;

id= third_harmonic;
iq=third_harmonic;

ialpha = id .* cos(theta) - iq .* sin(theta);
ibeta = id.* sin(theta) + iq .* cos(theta);
% Inverse Clarke Transformation: alpha-beta to abc
i_a = ialpha;
i_b = -0.5 * ialpha + (sqrt(3) / 2) * ibeta;
i_c = -0.5 * ialpha - (sqrt(3) / 2) * ibeta;


figure2= figure('Name','Time domain phase-A Current');
axes1 = axes('Parent',figure2);

plot(theta,i_a,"LineWidth",2) 
hold on

% plot(theta,i_b,"LineWidth",2) 

% plot(theta,i_c,"LineWidth",2) 
hold on

% plot(theta,third_harmonic,"LineWidth",2) 

xlabel("Time(ms)")
ylabel("Current (A)")
set(axes1,'FontName','Times New Roman','FontSize',15);

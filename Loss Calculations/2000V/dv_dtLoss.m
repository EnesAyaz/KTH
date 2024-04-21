%Turning on
di_dt_on= 10e9; % A/s
dv_dt_on= 25e9; % V/s
di_dt_off= 42.5e9; % A/s
dv_dt_off= 42.5e9; % V/s


IL=200;
Udc=600;
Eon= ((Udc*IL.^2/di_dt_on)+(Udc^2.*IL/dv_dt_on));

Eon*1e3

IL=200;
Udc=600;
Eoff= ((Udc*IL.^2/di_dt_off)+(Udc^2.*IL/dv_dt_off));

Eoff*1e3


%%
I=200; % A
Vdc=600;






di_dt= di_dt_on;
dv_dt= dv_dt_on;

dt= I/di_dt;

I_max=I;
V_max= Vdc;
V_min= Vdc-dv_dt*dt;

a=(V_max*I_max);
b=(V_max-V_min)*I_max;

Eon_1= (a/2)*(dt)-(b/3)*(dt);


V_max=V_min;
I_max=I;

dt=V_max/dv_dt;

a=V_max*I_max;
b= V_max*I_max;

Eon_2= a*dt- (b/2)*dt

(Eon_1+Eon_2)*1e3;

Eon= (Eon_1+Eon_2)


% t=linspace(0,dt,1000); 
% 
% V=V_max- ((V_max)/dt)*t;
% 
% I= (I_max)*ones(size(t));
% 
% plot(t,V); 
% hold on; 
% plot(t,I)
% hold on
% 
% P= V.*I
% plot(t,P)
% plot(t,P*dt/1000)
% 
% sum(P*dt/1000)

%% Turning off
% I=300; % A
% Vdc=1250;


di_dt= di_dt_off; % A/s
dv_dt= dv_dt_off; % V/s

V_max=Vdc;
I_max=I;

dt=V_max/dv_dt;

a=V_max*I_max;

Eoff_1= (a/2)*dt;


V_max=Vdc;
I_max=I;

dt=I_max/di_dt;

a=V_max*I_max;

Eoff_2= (a/2)*dt;

Eoff=Eoff_1+Eoff_2;



%%
% t=linspace(0,dt,1000); 
% 
% % V= ((V_max)/dt)*t;
% % 
% % I= (I_max)*ones(size(t));
% 
% I= ((I_max)/dt)*t;
% 
% V= (V_max)*ones(size(t));
% 
% plot(t,V); 
% hold on; 
% plot(t,I)
% hold on
% %
% P= V.*I
% plot(t,P)
% plot(t,P*dt/1000)
% % 
% sum(P*dt/1000)
E=(Eon+Eoff);

[Eon*1e3 Eoff*1e3 E*1e3]






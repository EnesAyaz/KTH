theta=linspace(0,2*pi,100)
Ia=10*sin(theta);
Ib=10*sin(theta-2*pi/3);
Ic=10*sin(theta+2*pi/3)

ma=0.6;
phi=0
Da_x=(1+ma*sin(theta+phi))/2;
Db_x=(1+ma*sin(theta-2*pi/3+phi))/2;
Dc_x=(1+ma*sin(theta+2*pi/3+phi))/2;


Iax=Ia./(abs(Ia)+abs(Ib)+abs(Ic));

Ibx=Ib./(abs(Ia)+abs(Ib)+abs(Ic));

Icx=Ic./(abs(Ia)+abs(Ib)+abs(Ic));
%%
figure()
plot(Db_x)
hold on
plot(Dc_x)
hold on
plot(Ibx)
hold on
plot(Icx)
hold on
% plot(Iax+Ibx+Icx)
legend('Db','Dc','Ib','Ic')

theta=linspace(0,2*pi,100)
Ia=10*sin(theta);
Ib=10*sin(theta-2*pi/3);
Ic=10*sin(theta+2*pi/3)


Iax=Ia./(abs(Ia)+abs(Ib)+abs(Ic));

Ibx=Ib./(abs(Ia)+abs(Ib)+abs(Ic));

Icx=Ic./(abs(Ia)+abs(Ib)+abs(Ic));

figure()
plot(Iax)
hold on
plot(Ibx)
hold on
plot(Icx)
hold on
plot(Iax+Ibx+Icx)

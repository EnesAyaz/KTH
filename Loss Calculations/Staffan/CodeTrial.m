f0=50;
time=0:1e-6:1/f0;
Ip1=320*sin(2*pi*f0*time);
Ip=[Ip1', time'];

Up1=800*sin(2*pi*f0*time);

Up=[Up1', time'];




%%
scloss2l(Ip,Up,f0,PC,OP,SCPAR)
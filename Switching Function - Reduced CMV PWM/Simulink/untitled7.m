len=1200;
phi= linspace(0,2*pi,len)
ma=1;

a= ma*cos(phi) 
b= ma*cos(phi-2*pi/3) 
c= ma*cos(phi+2*pi/3)

xax=[];
xbx=[];
xcx=[];

for i=1:1:200
    xa= (1/4)- a(i)-c(i);
    xax=[xax xa];
    xcx=[xcx -xa];
    xbx=[xbx 0];
end

for i=201:1:400
    xb= (1/4)- b(i)-c(i);
     xax=[xax 0];
    xcx=[xcx -xb];
    xbx=[xbx xb];
end

for i=401:1:600
    xa= (1/4)- a(i)-b(i);
    xax=[xax xa];
    xcx=[xcx 0];
    xbx=[xbx -xa];
end


for i=601:1:800
    xc= (1/4)- a(i)-c(i);
    xax=[xax xc];
    xcx=[xcx -xc];
    xbx=[xbx 0];
end

for i=801:1:1000
    xc= (1/4)- b(i)-c(i);
     xax=[xax 0];
    xcx=[xcx -xc];
    xbx=[xbx xc];
end

for i=1001:1:1200
    xb= (1/4)- a(i)-b(i);
    xax=[xax xb];
    xcx=[xcx 0];
    xbx=[xbx -xb];
end


%% 

plot(xcx)
hold on
plot(c)




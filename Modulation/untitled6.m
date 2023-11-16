len=1200;
phi= linspace(0,2*pi,len)

ma=1;

% a= ma*sin(phi) +linspace(0,ma,100)
a_i= ma*cos(phi) ;
b_i= ma*cos(phi-2*pi/3) ;
c_i= ma*cos(phi+2*pi/3);

a= (1+a_i)/2;
b= (1+b_i)/2;
c= (1+c_i)/2;


for i=1:1:len

 max_abc=   max([a(i),b(i),c(i)]);
 min_abc = min([a(i),b(i),c(i)]);
 med= a(i)+b(i)+c(i)-max_abc-min_abc; 




end
%%
subplot(2,1,1)
plot(a+b,'r')
hold on; 
plot(b+c,'b')
hold on; 
plot(c+a,'g')
yline(5/4)

subplot(2,1,2)
plot(a,'r')
hold on; 
plot(b,'b')
hold on; 
plot(c,'g')

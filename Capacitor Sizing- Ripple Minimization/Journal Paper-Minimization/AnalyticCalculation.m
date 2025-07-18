mf=41;
wt=linspace(0,2*pi,mf);
theta=0;
ma=0.5;

Isw_A= abs(cos(wt-theta).*sin(pi*(ma*cos(wt)+1)/2));
Isw_B= abs(cos(wt-2*pi/3-theta).*sin(pi*(ma*cos(wt-2*pi/3)+1)/2));
Isw_C= abs(cos(wt+2*pi/3-theta).*sin(pi*(ma*cos(wt+2*pi/3)+1)/2));

%%
stairs(wt,Isw_A)
hold on;
stairs(wt,Isw_B)
hold on;
stairs(wt,Isw_C)
%%

stairs(mf*wt/2/pi,Isw_A-Isw_B,'r')
hold on;
stairs(mf*wt/2/pi,Isw_C,'b')
hold on;
stairs(mf*wt/2/pi,Isw_A+Isw_B,'--r')
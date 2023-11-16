theta= linspace(0,4*pi,1000);
ma3=1;


phase_3=pi/4; 
VA_3= ma3*sin(3*theta-phase_3); 


ma9=ma3;
phase_9=pi/2; 
VA_9= ma9*sin(9*theta-phase_9); 


VA3=VA_3+VA_9;

% plot(theta, VA_1)
% hold on; 
% plot(theta, VA_3)
% hold on; 
hold off
% plot(theta, VA)
hold on 
plot(theta*180/pi, VA3)
disp(max(VA))


x= sin(theta-pi/4)+ sin(theta+pi/4); 
%%
plot(x)
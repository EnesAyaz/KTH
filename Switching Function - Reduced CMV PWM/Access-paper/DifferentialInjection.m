start=0;
stop=2*pi;

phase_fundamental= linspace(start,stop,1000)

phaseA= cos(phase_fundamental);
phaseB= cos(phase_fundamental-2*pi/3);
phaseC= cos(phase_fundamental-4*pi/3);

figure();
plot(phase_fundamental*180/pi,phaseA, Color=[1 0 0])
hold on 
plot(phase_fundamental*180/pi,phaseB, Color=[0 1 0])
hold on 
plot(phase_fundamental*180/pi,phaseC, Color=[0 0 1])
hold on 



A_inject=0*ones(size(phaseA));
A_inject(phaseA<0)=0.5;


B_inject=0*ones(size(phaseB));
B_inject(phaseB<0)=0.5;

C_inject=0*ones(size(phaseC));
C_inject(phaseC<0)=0.5;

figure()
plot(phase_fundamental*180/pi,phaseA+A_inject, Color=[1 0 0])
hold on 
plot(phase_fundamental*180/pi,phaseB+B_inject, Color=[0 1 0])
hold on 
plot(phase_fundamental*180/pi,phaseC+C_inject, Color=[0 0 1])
hold on 



figure()
plot(phase_fundamental*180/pi,A_inject, Color=[1 0 0])
hold on 
% plot(phase_fundamental*180/pi,B_inject, Color=[0 1 0])
% hold on 
% plot(phase_fundamental*180/pi,C_inject, Color=[0 0 1])
hold on 







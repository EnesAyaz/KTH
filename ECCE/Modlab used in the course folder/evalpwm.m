function evalpwm(s);
%EVALPWM: Extracts certain parameters from a 3-phase pwm pattern
%
a=exp(j*2*pi/3);
%
sf(1,:)=fourser(s(1,:),10);
sf(2,:)=fourser(s(2,:),10);
sf(3,:)=fourser(s(3,:),10);
%
s1= sf(1,2);
s2= sf(2,2);
s3= sf(3,2);

sp=1/3*(s1 + s2*a + s3*a^2);
sm=1/3*(s1 + s2*a^2 + s3*a);
s0=1/3*(s1 + s2 + s3);
negshare=100*abs(sm/sp);
zeroshare=100*abs(s0/sp);

s12= sf(1,2)-sf(2,2);
s23= sf(2,2)-sf(3,2);
s31= sf(3,2)-sf(1,2);

disp( ['s1: ' num2str( abs(s1) ) ]);
disp( ['s2: ' num2str( abs(s2) ) ]);
disp( ['s3: ' num2str( abs(s3) ) ]);
disp( ['Neg sequence: ' num2str( negshare ) ' %']);
disp( ['Zero sequence: ' num2str( zeroshare ) ' %']);
disp( ['s12: ' num2str( abs(s12) ) ]);
disp( ['s23: ' num2str( abs(s23) ) ]);
disp( ['s31: ' num2str( abs(s31) ) ]);
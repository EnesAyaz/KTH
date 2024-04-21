function pwmplot(s)
%Plots phase and line-to-line switching functions for 3-phase system
%
axis1=[0 2*pi -0.1 1.1];
axis2=[0 2*pi -1.1 1.1];

noofpts=length(s);
wt=2*pi*(0:noofpts-1)/noofpts;
figure

subplot(6,1,1)
plot(wt,s(1,:));
axis(axis1);
xlabel('s1');
%
subplot(6,1,2)
plot(wt,s(2,:));
axis(axis1);
xlabel('s2');
%
subplot(6,1,3)
plot(wt,s(3,:));
axis(axis1);
xlabel('s3');
%
subplot(6,1,4)
plot(wt,s(1,:)-s(2,:));
axis(axis2);
xlabel('s12');
%
subplot(6,1,5)
plot(wt,s(2,:)-s(3,:));
axis(axis2);
xlabel('s23');
%
subplot(6,1,6)
plot(wt,s(3,:)-s(1,:));
axis(axis2);
xlabel('s31');
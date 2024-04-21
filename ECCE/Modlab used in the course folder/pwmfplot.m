function pwmfplot(s,nharm)
%Plots switching functions for 3-phase system the frequency domain

sf(1,:)=fourser(s(1,:),nharm);
sf(2,:)=fourser(s(2,:),nharm);
sf(3,:)=fourser(s(3,:),nharm);
%
order=0:nharm-1;
%
%axis1=[0 2*pi -0.1 1.1];
%axis2=[0 2*pi -1.1 1.1];
%
figure
%
subplot(6,1,1)
bar(order,abs(sf(1,:)));
%axis(axis1);
xlabel('s1');
%
subplot(6,1,2)
bar(order,abs(sf(2,:)));
%axis(axis1);
xlabel('s2');
%
subplot(6,1,3)
bar(order,abs(sf(3,:)));
%axis(axis1);
xlabel('s3');
%
subplot(6,1,4)
bar(order,abs(sf(1,:)-sf(2,:)));
%axis(axis2);
xlabel('s12');
%
subplot(6,1,5)
bar(order,abs(sf(2,:)-sf(3,:)));
%axis(axis2);
xlabel('s23');
%
subplot(6,1,6)
bar(order,abs(sf(3,:)-sf(1,:)));
%axis(axis2);
xlabel('s31');

%X=[x;x];
%x=2*pi*(0:9)/10;
%Y=[-1.1*ones(1,10); 1.1*ones(1,10)];
%L=line(X,Y,'LineWidth',0.25,'Color',[0 0 0])

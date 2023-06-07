fo=1e3;
fs=40e3;
ma=0;

DA_tot=[];
DB_tot=[];
DC_tot=[];
SA_fs_tot= [];
SB_fs_tot= [];
SC_fs_tot= [];

PhiB_tot=[];
PhiC_tot=[];

time_tot= 0:1/fs/1000:1/fo;
i=0;

PhiB=0;
PhiC=0;
SA_fs_mag_x=[];
SB_fs_mag_x=[];
SC_fs_mag_x=[];

for time=time_tot
 
DA= (1+ma*sin(2*pi*fo.*time))/2;
DB= (1+ma*sin(2*pi*fo.*time-2*pi/3))/2;
DC= (1+ma*sin(2*pi*fo.*time+2*pi/3))/2;


if i ==  0
SA_fs_mag= abs((2/pi).*sin(pi.*DA));
SB_fs_mag= abs((2/pi).*sin(pi.*DB));
SC_fs_mag= abs((2/pi).*sin(pi.*DC));

SA_fs_mag_x=[SA_fs_mag_x SA_fs_mag];
SB_fs_mag_x=[SB_fs_mag_x SB_fs_mag];
SC_fs_mag_x=[SC_fs_mag_x SC_fs_mag];

if abs(SA_fs_mag-SB_fs_mag) < SC_fs_mag && SC_fs_mag < (SA_fs_mag+SB_fs_mag)
    
cos_x= (-SC_fs_mag^2+SA_fs_mag^2+SB_fs_mag^2)/(2*SA_fs_mag*SB_fs_mag);
x=acos(cos_x);
PhiB=pi-x;

sin_y=SB_fs_mag*sin(x)/SC_fs_mag;
y=asin(sin_y);
PhiC=y-pi;

elseif SA_fs_mag> SB_fs_mag && SA_fs_mag> SB_fs_mag 
PhiB=pi;
PhiC=pi;
elseif SB_fs_mag> SA_fs_mag && SB_fs_mag> SC_fs_mag 
PhiB=pi;
PhiC=0;
elseif  SC_fs_mag> SA_fs_mag && SC_fs_mag> SB_fs_mag 
PhiB=0;
PhiC=pi;
else 
PhiB=pi/3;
PhiC=pi/3;   
end
i=0;
else 
i=i+1
end


SA_fs= (2/pi).*sin(pi.*DA).*cos(2*pi*fs.*time);
SB_fs= (2/pi).*sin(pi.*DB).*cos(2*pi*fs.*time-PhiB);
SC_fs= (2/pi).*sin(pi.*DC).*cos(2*pi*fs.*time-PhiC);

PhiB_tot=[PhiB_tot PhiB];
PhiC_tot=[PhiC_tot PhiC];


DA_tot=[DA_tot DA];
DB_tot=[DB_tot DB];
DC_tot=[DC_tot DC];

SA_fs_tot= [SA_fs_tot SA_fs];
SB_fs_tot= [SB_fs_tot SB_fs];
SC_fs_tot= [SC_fs_tot SC_fs];

end
%%
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

plot(time_tot*fo*360,SA_fs_mag_x,'DisplayName','leg-A','color', [0.8 0 0]);
hold on;
plot(time_tot*fo*360,SB_fs_mag_x,'DisplayName','leg-B','color', [0 0 0.8]);
hold on;
plot(time_tot*fo*360,SC_fs_mag_x,'DisplayName','leg-C','color', [0 0.8 0]);
hold on;

xlim([0 360])
ylim([0 1])

ylabel({'|S|'});

% Create xlabel
xlabel({'Fundamental Phase'});

% Uncomment the following line to preserve the X-limits of the axes
% xlim(axes1,[0 360]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties

legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.70595238334721 0.717460322356413 0.169642854801246 0.17619047129438]);

set(axes1,'FontSize',15,'XTick',[0 100 200 300 360]);


%%
figure();
plot(time_tot,SA_fs_tot)
hold on;
plot(time_tot,SB_fs_tot)
hold on;
plot(time_tot,SC_fs_tot)
hold on;
%%
figure();
plot(time_tot, (SA_fs_tot+SB_fs_tot+SC_fs_tot)/3)
hold on;
% plot(time_tot, (SA_fs_tot-SB_fs_tot)/sqrt(3))
hold on;

%%

figure();
% plot(time,SA_fs)
% hold on;
% plot(time,SB_fs)
% hold on;
% plot(time,SC_fs)
% hold on;
plot(time_tot*fo*360, PhiB_tot*180/pi,'r')
hold on;
plot(time_tot*fo*360, PhiC_tot*180/pi,'b')
hold on;
% plot(time_tot*fo*360, (PhiB_tot+PhiC_tot)*180/pi,'b')
hold on;
ylim([-200 200])






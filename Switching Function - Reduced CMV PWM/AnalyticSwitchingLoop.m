fo=1e3;
fs=40e3;
ma=0.5;

DA_tot=[];
DB_tot=[];
DC_tot=[];
SA_fs_tot= [];
SB_fs_tot= [];
SC_fs_tot= [];

PhiB_tot=[];
PhiC_tot=[];


time_tot= 0:1/fs/1000:2/fo;
i=0;

PhiB=0;
PhiC=0;

for time=time_tot
 
DA= (1+ma*sin(2*pi*fo.*time))/2;
DB= (1+ma*sin(2*pi*fo.*time-2*pi/3))/2;
DC= (1+ma*sin(2*pi*fo.*time+2*pi/3))/2;


if i ==  1000
SA_fs_mag= abs((2/pi).*sin(pi.*DA));
SB_fs_mag= abs((2/pi).*sin(pi.*DB));
SC_fs_mag= abs((2/pi).*sin(pi.*DC));
if SA_fs_mag-SB_fs_mag < SC_fs_mag< SA_fs_mag-SB_fs_mag
PhiB=0;
PhiC=0;
elseif SA_fs_mag> SB_fs_mag && SA_fs_mag> SB_fs_mag 
PhiB=pi;
PhiC=pi;
elseif SB_fs_mag> SA_fs_mag && SB_fs_mag> SC_fs_mag 
PhiB=pi;
PhiC=0;
else 
PhiB=0;
PhiC=pi;
end
i=0;
else 
i=i+1;
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
figure();
% plot(time,SA_fs)
% hold on;
% plot(time,SB_fs)
% hold on;
% plot(time,SC_fs)
% hold on;
plot(time_tot, (SA_fs_tot+SB_fs_tot+SC_fs_tot)/3)
hold on;

%%

figure();
% plot(time,SA_fs)
% hold on;
% plot(time,SB_fs)
% hold on;
% plot(time,SC_fs)
% hold on;
% plot(time_tot, PhiB_tot)
hold on;
plot(time_tot, PhiC_tot)
hold on;





fo=1e3;
fs=40e3;
ma=0.25;

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

% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create multiple line objects using matrix input to plot
plot1 = plot(time_tot*fo*360,SA_fs_mag_x,'Parent',axes1);
plot2 = plot(time_tot*fo*360,SB_fs_mag_x,'Parent',axes1);
plot3 = plot(time_tot*fo*360,SC_fs_mag_x,'Parent',axes1);

set(plot1,'DisplayName','Phase-A','Color',[0 0 1]);
set(plot2,'DisplayName','Phase-B','Color',[1 0 1]);
set(plot3,'DisplayName','Phase-C','Color',[0 1 0]);

% Create ylabel
ylabel({'Normalized Voltage'},'FontName','Times New Roman');

% Create xlabel
xlabel({'Fundamental Phase'},'FontName','Times New Roman');

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 360]);
% Uncomment the following line to preserve the Y-limits of the axes
ylim(axes1,[0 1]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',20,'XTick',...
    [0 100 200 300 360]);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.388095241501216 0.696031751353592 0.237499995636089 0.204761899014313],...
    'EdgeColor','none',...
    'Color','none');

% % Create textbox
% annotation(figure1,'textbox',...
%     [0.418857142857141 0.390476190476193 0.156142857142858 0.1],...
%     'String',{'ma=1'},...
%     'FontSize',20,...
%     'FontName','Times New Roman',...
%     'FitBoxToText','off',...
%     'EdgeColor','none');


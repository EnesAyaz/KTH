clear; 
clc;
 close all

file_folder="C:\Users\enesa\KTH\Shahriar Sarmast Ghahfarokhi - topology\DPT_Results\" ;
file_extension=strcat(file_folder,'*.xlsx');
files=dir(file_extension);

i=5;
file_name=files(i).name;
% file_name= "Test-Oct-31-23 Time 16 11 32--V 500-t1 4-t2 10-t3 4-td 10-tdead 200ns.xlsx";

file_path=strcat(file_folder, file_name);

[Ch1, Ch2, Ch3] = importfile(file_path, "sheet1", [2, Inf]);
%%
newStr = split(file_name,'-');
%%
V=newStr(6);
V=split(V);
V=string(V);
tit= strcat('V_{dc}=',V(2),'V');
V=str2num(V(2));

t1=newStr(7);
t1=split(t1);
t1=string(t1);
tit= strcat(tit, '{  } ','t_1=',t1(2), '\mus');
t1=str2num(t1(2));

t2=newStr(8);
t2=split(t2);
t2=string(t2);
tit= strcat(tit, '{  } ','t_2=',t2(2), '\mus');
t2=str2num(t2(2));

t3=newStr(8);
t3=split(t3);
t3=string(t3);
tit= strcat(tit, '{  } ','t_3=',t3(2), '\mus');
t3=str2num(t3(2));

td=newStr(9);
td=split(td);
td=string(td);
td=str2num(td(2));

[V t1 t2 t3 td];

tspan= (t1+t2+t3+td)*1e-6;
%%
Vgs=Ch1;
Vds= Ch2;
Id=Ch3;
time= linspace(0, tspan, length(Vds));

%%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
colororder([0 0.447 0.741]);
% Activate the left side of the axes
yyaxis(axes1,'left');
% Create multiple line objects using matrix input to plot
plot1 = plot(time*1e6,10*Vgs,'LineStyle','-','LineWidth',1);
plot2 =  plot(time*1e6,Vds,'LineStyle','-','LineWidth',1);

set(plot1,'DisplayName','10 xV_{GS}','Color',[1 0 0]);
set(plot2,'DisplayName','V_{DS}','Color',[0 0 1]);

% Create ylabel
ylabel({'Voltage (V)'});

% Set the remaining axes properties
set(axes1,'YColor',[0 0 1]);
% Activate the right side of the axes
yyaxis(axes1,'right');
% Create plot
plot(time*1e6,Id,'DisplayName','I_{D}','LineWidth',1,'Color',[0 0 0]);

% Create ylabel
ylabel({'Current (A)'});

% Set the remaining axes properties
set(axes1,'YColor',[0 0 0]);
% Create xlabel
xlabel({'Time (\mus)'});

title(tit)


box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.658630955121701 0.44603175135359 0.205357139451163 0.219047612874281]);

clearvars -except Vgs Vds Id time

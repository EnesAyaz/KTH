r=0.5;

NumberofDie= 0:0.1:4;

rds= r./NumberofDie;



Psw= (1/6+NumberofDie/3)*0.5;


% 
% plot(NumberofDie,rds)
% hold on
% plot(NumberofDie,Psw)
% hold on;
% plot(NumberofDie,Psw+rds)
% 
% ylim([0 3])
% xlim([0 4])
% xticks([0 1 2 3 4])

X1=NumberofDie;
YMatrix1=[rds;Psw; (Psw+rds)];

% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create multiple line objects using matrix input to plot
plot1 = plot(X1,YMatrix1,'LineWidth',1,'Color',[0 0 0],'Parent',axes1);
set(plot1(1),'DisplayName','Conduction losses','LineStyle','--');
set(plot1(2),'DisplayName','Switching losses','LineStyle','-.');
set(plot1(3),'DisplayName','Total losses');

% Create ylabel
ylabel({'P_{semi}/ P_{semi,opt} (p.u.)'});

% Create xlabel
xlabel({'A_{die} / A_{die,opt} (p.u.)'});

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 4]);
% Uncomment the following line to preserve the Y-limits of the axes
ylim(axes1,[0 3]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',1,...
    'GridColor',[0.466666666666667 0.674509803921569 0.188235294117647],...
    'MinorGridAlpha',1,'MinorGridColor',...
    [0.466666666666667 0.674509803921569 0.188235294117647],'XGrid','on',...
    'XMinorGrid','on','XTick',[0 1 2 3 4],'YGrid','on','YMinorGrid','on');
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.463988101863789 0.712698417168762 0.326785707260881 0.161904757434413]);

% Create textbox
annotation(figure1,'textbox',...
    [0.356357142857143 0.528571428571429 0.209714285714286 0.0666666666666668],...
    'String',{'Optimized point'},...
    'FitBoxToText','off');

% Create arrow
annotation(figure1,'arrow',[0.425 0.328571428571427],...
    [0.516666666666667 0.423809523809527]);

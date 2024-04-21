r=0.5/2*(3/2);

NumberofDie= 0:0.1:4;
rds= r./NumberofDie;



Psw= (NumberofDie)/4*(3/2);

Pover= ones(size(NumberofDie))/4;


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
YMatrix1=[rds;Psw; Pover; (Psw+rds+Pover),];

% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create multiple line objects using matrix input to plot
plot1 = plot(X1,YMatrix1,'LineWidth',2,'Color',[0 0 0],'Parent',axes1);
set(plot1(1),'DisplayName','Conduction losses','LineStyle','--');
set(plot1(2),'DisplayName','Zero Current Switching losses','LineStyle','-.');
set(plot1(3),'DisplayName','Overlapping Losses','LineStyle',':');
set(plot1(4),'DisplayName','Total losses','LineStyle','-');
% Create ylabel
ylabel({'P_{semi}/ P_{semi,opt} (p.u.)'},'FontName','Times New Roman');

% Create xlabel
xlabel({'A_{die} / A_{die,opt} (p.u.)'},'FontName','Times New Roman');

% Uncomment the following line to preserve the X-limits of the axes
 xlim(axes1,[0 4]);
% Uncomment the following line to preserve the Y-limits of the axes
ylim(axes1,[0 3]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',1,...
    'GridColor',[0.909803921568627 0.780392156862745 0.780392156862745],...
    'MinorGridAlpha',1,'MinorGridColor',...
    [0.909803921568627 0.780392156862745 0.780392156862745],'XGrid','on',...
    'XMinorGrid','on','XTick',[0 1 2 3 4],'YGrid','on','YMinorGrid','on');
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.463988101863789 0.687103179818582 0.326785707260881 0.213095232134774]);

% Create arrow
annotation(figure1,'arrow',[0.425 0.328571428571427],...
    [0.516666666666667 0.423809523809527]);

% Create textbox
annotation(figure1,'textbox',...
    [0.302785714285714 0.528571428571429 0.284714285714286 0.0666666666666668],...
    'String',{'Optimized point'},...
    'FontSize',15,...
    'FontName','Times New Roman',...
    'FitBoxToText','off',...
    'EdgeColor','none');


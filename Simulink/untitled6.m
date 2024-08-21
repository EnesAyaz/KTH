theta=linspace(0,360,100)


Rmotor=3;
Ld=0.5; % H
Lq=1; % H

L=(Ld+Lq)/2 + (cosd(theta)*(Ld-Lq)/2);


% plot(theta,L)
% yline([0.75])
% ylim([0 1])
% xlim([0 360])


figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create plot
plot(theta,L,'DisplayName','Inductance','LineWidth',2,'Color',[0 0 1]);

% Create yline
yline(0.75,'DisplayName','Mean Inductance','Parent',axes1,'Color',[1 0 0],...
    'LineWidth',2);

% Create ylabel
ylabel({'Inductance (p.u)'});

% Create xlabel
xlabel({'Electrical angle'});

% Uncomment the following line to preserve the X-limits of the axes
xlim(axes1,[0 360]);
% Uncomment the following line to preserve the Y-limits of the axes
% ylim(axes1,[0 1]);
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.397916670684658 0.316269843753368 0.31428570763341 0.110714282734054]);


% Create textarrow
annotation(figure1,'textarrow',[0.489285714285714 0.517857142857143],...
    [0.837095238095239 0.911904761904763],'String',{'Lq'},'FontSize',15,...
    'FontName','Times New Roman');

% Create textarrow
annotation(figure1,'textarrow',[0.175 0.142857142857143],...
    [0.276190476190476 0.173809523809524],'String',{'Ld'},'FontSize',15,...
    'FontName','Times New Roman');

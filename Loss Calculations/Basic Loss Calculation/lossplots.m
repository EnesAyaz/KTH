frequency= 5;

switching_loss_25= 164  ;
switching_loss_125= 176;
conduction_loss_25= 233*2;
conduction_loss_125= 388*2;

k= 1:1:6; 
frequency_k= k*frequency;
switching_loss_25_k=k*switching_loss_25;
switching_loss_125_k=k*switching_loss_125;

conduction_loss_25_k=conduction_loss_25*ones(size(k));
conduction_loss_125_k=conduction_loss_125*ones(size(k));


%%
figure1 = figure;
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create multiple line objects using matrix input to plot
plot1 = plot(frequency_k,switching_loss_25_k,'LineWidth',2);
plot2 = plot(frequency_k,switching_loss_125_k,'LineWidth',2);

set(plot1,'DisplayName','25 C^o','MarkerSize',10,'Marker','o',...
    'Color',[0 0 1]);
set(plot2,'DisplayName','125 C^o','MarkerSize',12,'Marker','x',...
    'Color',[1 0 0]);
% Create ylabel
ylabel({'Loss (W)'});
% Create xlabel
xlabel({'Frequency (kHz)'},'FontName','Times New Roman');
% Create title
title({'Switching Loss'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);
% Create legend
ylim([0 3000])
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.338988097659533 0.706746035152013 0.183928568661212 0.139285710453987],...
    'EdgeColor','none');

%%

%%
figure1 = figure;
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create multiple line objects using matrix input to plot
plot1 = plot(frequency_k,conduction_loss_25_k,'LineWidth',2);
plot2 = plot(frequency_k,conduction_loss_125_k,'LineWidth',2);

set(plot1,'DisplayName','25 C^o','MarkerSize',10,'Marker','o',...
    'Color',[0 0 1]);
set(plot2,'DisplayName','125 C^o','MarkerSize',12,'Marker','x',...
    'Color',[1 0 0]);
% Create ylabel
ylabel({'Loss (W)'});
% Create xlabel
xlabel({'Frequency (kHz)'},'FontName','Times New Roman');
% Create title
title({'Conduction Loss'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);

ylim([0 3000])
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.338988097659533 0.706746035152013 0.183928568661212 0.139285710453987],...
    'EdgeColor','none');

%%

%%
figure1 = figure;
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create multiple line objects using matrix input to plot
plot1 = plot(frequency_k,(conduction_loss_25_k+switching_loss_25_k),'LineWidth',2);
plot2 = plot(frequency_k,(conduction_loss_125_k+switching_loss_125_k),'LineWidth',2);
plot3= yline(1500,'LineWidth',2);

set(plot1,'DisplayName','25 C^o','MarkerSize',10,'Marker','o',...
    'Color',[0 0 1]);
set(plot2,'DisplayName','125 C^o','MarkerSize',12,'Marker','x',...
    'Color',[1 0 0]);
set(plot3,'DisplayName','Loss Limitation', 'Color',[0 0 0]);
% Create ylabel
ylabel({'Loss (W)'});
% Create xlabel
xlabel({'Frequency (kHz)'},'FontName','Times New Roman');
% Create title
title({'Total Loss'});
box(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15);


ylim([0 3000])
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.338988097659533 0.706746035152013 0.183928568661212 0.139285710453987],...
    'EdgeColor','none');


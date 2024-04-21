figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

addpath('C:\Github\KTH\ECCE\Modlab used in the course folder')

M=0:00.1:1;
p=22;    %Max three pulse numbers

nharms=p*5;

for j=1:length(p)
    for i=1:length(M)
        Vpanatri_a=2*spect2lanalyt(p(j),M(i),nharms(j),'tria',0,0); 
        Vpanatri_b=2*spect2lanalyt(p(j),M(i),nharms(j),'tria',2*pi/3,0); 
        Vpanatri= Vpanatri_a(1:end)- Vpanatri_b(1:end);
        n=2:length(Vpanatri)-1;
        WTHD0_Vpanatri(j,i)=100*sqrt(sum((1./(n.^2)).*abs(Vpanatri(3:end)).^2));
    end
    plot1= plot(M,WTHD0_Vpanatri(j,:)./1.7321,'LineWidth',2,'Parent',axes1) ;
    hold on;
end

%%

addpath('C:\Github\KTH\ECCE\Modlab used in the course folder')

M=0:00.1:1;
p=24;    %Max three pulse numbers

nharms=p*5;

for j=1:length(p)
    for i=1:length(M)
        Vpanatri_a=2*spect2lanalyt(p(j),M(i),nharms(j),'tria',0,0); 
        Vpanatri_b=2*spect2lanalyt(p(j),M(i),nharms(j),'tria',pi/3,0); 
        Vpanatri= Vpanatri_a(1:end)- Vpanatri_b(1:end);
        n=2:length(Vpanatri)-1;
        WTHD0_Vpanatri(j,i)=100*sqrt(sum((1./(n.^2)).*abs(Vpanatri(3:end)).^2));
    end
     plot2= plot(M,WTHD0_Vpanatri(j,:)./1.7321,'LineWidth',2,'Parent',axes1) ;
    hold on;
end
%%
% V = anaspect1ph3lnsc(M, p, theta0, thetac, phi, nharm);
addpath('C:\Github\KTH\ECCE\Modlab used in the course folder')

M=0:00.1:1;
p=50;    %Max three pulse numbers

nharms=p*5;

for j=1:length(p)
    for i=1:length(M)
        ma=M(i);   % Modulation index
        px = p(j) % Pulse number
        nlev=3;
        theta0=0;
        npts = 10000; % Number of timepoints
        type='sc1'; % carrier type 
        opt='none'; % reference common-mode injection
        thetac=0; % carrier phase offset
        %scale=0;
        %offset=0;
        %carrmod=0;
        [vp_a,wt,ref,carr] = mlspwm(ma, px ,nlev, theta0, npts,type,opt);  % Numerical waveforms during one cycle
        theta0=2*pi/3; % reference phase offset
        [vp_b,wt,ref,carr] = mlspwm(ma, px ,nlev, theta0, npts,type,opt);  % Numerical waveforms during one cycle
        Vpanatri_a= fourser(vp_a,nharms(j));
        Vpanatri_b= fourser(vp_b,nharms(j));
        Vpanatri= Vpanatri_a- Vpanatri_b;
        n=2:length(Vpanatri)-1;
        WTHD0_Vpanatri(j,i)=100*sqrt(sum((1./(n.^2)).*abs(Vpanatri(3:end)).^2));
    end
     plot3= plot(M,WTHD0_Vpanatri(j,:)./1.7321,'LineWidth',2,'Parent',axes1) ;
    hold on;
end

set(plot1,'DisplayName','2L-3Ph at f_{sw}= 11kHz',...
    'Color',[0.32156862745098 0.32156862745098 0.949019607843137]);
set(plot2,'DisplayName','2L-6Ph at f_{sw}= 12kHz',...
    'Color',[0.32156862745098 0.949019607843137 0.32156862745098]);
set(plot3,'DisplayName','3L-NPC at f_{sw}= 25kHz',...
    'Color',[0.32156862745098 0.949019607843137 0.949019607843137]);

% Create ylabel
ylabel('WTHD0 (%)','FontName','Times New Roman');

% Create xlabel
xlabel('Modulation index ','FontName','Times New Roman');

hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0.25,...
    'GridColor',[0.949019607843137 0.32156862745098 0.32156862745098],...
    'MinorGridColor',[0.949019607843137 0.32156862745098 0.32156862745098],...
    'XGrid','on','XMinorGrid','on','YGrid','on','YMinorGrid','on');
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.160416672174774 0.662698418020257 0.391071419630732 0.219047612874281],...
    'EdgeColor','none',...
    'Color','none');


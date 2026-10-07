% Fig. 9: analytical periodic steady state of ideal natural SPWM.
% No ODE time stepping, startup transient, dead time, or parasitic ringing.
% Exact sinusoidal-current integrals between PWM crossing times; crossings
% are located by bisection. Fourier coefficients use the two-sided convention.
% Normalized illustrative circuit: N=3, L=.0085, C=.01, R=2.5;
% f1=1 Hz, fsw=100 Hz, M=.85, power-factor angle=20 degrees.
outdir=fileparts(mfilename('fullpath'));
addpath(fullfile(outdir,'..','Style'));st=pes_style();
N=3;M=.85;f1=1;fsw=100;phi=20*pi/180;
Im=1/(.75*M*cos(phi));L=.0085;C=.01;R=2.5;
H=8000;ns=65536;h=(0:H)';w=2*pi*f1*h;
cellCoeffs=zeros(H+1,N);
for k=1:N
    cellCoeffs(:,k)=pwmCoefficients((k-1)/N,H,M,phi,Im,fsw/f1);
end
den=N-w.^2*L*C+1i*w*C*R;
coeffs=[N*cellCoeffs(:,1)./den,sum(cellCoeffs,2)./den];
y=zeros(ns,2);ylow=y;
for k=1:2
    y(:,k)=reconstruct(coeffs(:,k),ns);
    ylow(:,k)=reconstruct(coeffs(1:H/2+1,k),ns);
end
t=(0:ns-1)'/(ns*f1);
rippleRms=sqrt(2*sum(abs(coeffs(2:end,:)).^2,1));
convergence=max(abs(y-ylow),[],1);
assert(max(abs(coeffs(1,:)-1))<1e-9,'Incorrect dc normalization.');
assert(max(convergence)<2e-5,'Increase harmonic cutoff.');
assert(max(abs(std(y,1,1)-rippleRms))<1e-10,'Parseval check failed.');
fprintf('Ripple RMS [without, with]: %.9g %.9g p.u.\n',rippleRms);
fprintf('4000-to-8000 harmonic max change: %.9g %.9g p.u.\n',convergence);
fprintf('Peak-to-peak ripple: %.9g %.9g p.u.\n',max(y)-min(y));
data=table(t,y(:,1),y(:,2),'VariableNames', ...
    {'t_seconds','without_interleaving','with_interleaving'});
writetable(data,fullfile(outdir,'dclink_ripple_data.csv'));
fig=figure('Visible','off','Color','w','Units','centimeters', ...
    'Position',[2 2 8.8 4.6],'Renderer','painters');
ax=axes(fig,'Position',[.21 .24 .73 .49]);hold(ax,'on');
plot(ax,t*fsw,y(:,1),'Color',st.red,'LineWidth',.65, ...
    'DisplayName','Without interleaving');
plot(ax,t*fsw,y(:,2),'--','Color',st.blue,'LineWidth',.65, ...
    'DisplayName','With interleaving');
set(ax,'FontName',st.font,'FontSize',8.5,'TickDir','in', ...
    'Box','on','LineWidth',.5,'GridAlpha',.15);grid(ax,'on');
xlabel(ax,'$t/T_{\mathrm{sw}}$','Interpreter','latex','FontSize',8.5);
ylabel(ax,'$i_{\mathrm{dc}}$ (p.u.)','Interpreter','latex','FontSize',8.5);
ylim(ax,[min(y,[],'all')-.006,max(y,[],'all')+.006]);
xlim(ax,[0 100]);
legend(ax,'Location','northoutside','Box','off','FontSize',8.5);
set(fig,'PaperUnits','centimeters','PaperPosition',[0 0 8.8 4.6], ...
    'PaperSize',[8.8 4.6]);
out=fullfile(outdir,'fig_dclink_ripple');
savefig(fig,[out '.fig']);print(fig,[out '.pdf'],'-dpdf','-painters');
if usejava('desktop'),set(fig,'Visible','on');end

function c=pwmCoefficients(shift,H,M,phi,Im,ratio)
h=(0:H)';c=complex(zeros(H+1,1));
knots=((-2:2*ratio+2)/2+shift)/ratio;
knots=unique([0,knots(knots>0 & knots<1),1]);
for theta=[0,-2*pi/3,2*pi/3]
    gap=@(t) M*cos(2*pi*t-theta-phi)-(1-4*abs(mod(ratio*t-shift,1)-.5));
    edges=[0,1];
    for j=1:numel(knots)-1
        lo=knots(j);hi=knots(j+1);
        if gap(lo)*gap(hi)<0
            for iteration=1:48
                mid=(lo+hi)/2;
                if gap(lo)*gap(mid)<=0,hi=mid;else,lo=mid;end
            end
            edges(end+1)=(lo+hi)/2; %#ok<SAGROW>
        end
    end
    edges=sort(edges);
    for j=1:numel(edges)-1
        a=edges(j);b=edges(j+1);
        if gap((a+b)/2)<=0,continue;end
        c=c+Im/2*(exp(-1i*theta)*intervalIntegral(h-1,a,b) ...
            +exp(1i*theta)*intervalIntegral(h+1,a,b));
    end
end
end
function v=intervalIntegral(r,a,b)
x=r*(b-a);s=ones(size(x));nz=x~=0;
s(nz)=sin(pi*x(nz))./(pi*x(nz)); % Toolbox-free normalized sinc.
v=(b-a)*s.*exp(-1i*pi*r*(a+b));
end
function y=reconstruct(c,ns)
s=complex(zeros(ns,1));s(1:numel(c))=c;
s(end-numel(c)+2:end)=conj(flipud(c(2:end)));
y=real(ifft(s))*ns;
end

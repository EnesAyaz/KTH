%% Adaptive Multi-Carrier PWM — Sinusoidal Reference, Sign-Based Rule
% =====================================================================
% Duty cycles follow sinusoidal SPWM references (vary over fundamental).
% Phase currents are sinusoidal, lagged by power factor angle.
%
% At each switching interval:
%   1) Determine which leg is "lone-sign" (its current sign differs
%      from the other two) — this changes as the fundamental rotates.
%   2) Assign:
%        Leg A = lone-sign leg
%        Leg B = same-bank leg 1  → theta_B = 0   (START aligned with A)
%        Leg C = same-bank leg 2  → theta_C = dA - dC (END aligned with A)
%   3) Apply the two-subtraction rule. No LUT, no sweep.
%
% The sign pattern of (ia, ib, ic) rotates through 6 sectors per cycle:
%   Sector 1:  (+, -, -)   Sector 2:  (+, +, -)
%   Sector 3:  (-, +, -)   Sector 4:  (-, +, +)
%   Sector 5:  (-, -, +)   Sector 6:  (+, -, +)

clear; clc; close all;

%% ── PARAMETERS ──────────────────────────────────────────────────────────────
ma      = 1;      % Modulation index
Iph     = 1.0;      % Peak phase current (p.u.)
pf      = 1;     % Power factor (lagging)
Nsw     = 200;      % Switching intervals per fundamental period (resolution)

phi_pf  = acos(pf); % Power factor angle (rad)

%% ── FUNDAMENTAL ANGLE SWEEP ─────────────────────────────────────────────────
theta   = linspace(0, 2*pi, Nsw+1);
theta   = theta(1:end-1);   % Nsw points, one per switching interval

% Duty cycles (SPWM, da+db+dc = 1.5 always)
da_vec  = 0.5 + 0.5*ma*cos(theta);
db_vec  = 0.5 + 0.5*ma*cos(theta - 2*pi/3);
dc_vec  = 0.5 + 0.5*ma*cos(theta - 4*pi/3);

% Phase currents (lagging by phi_pf)
ia_vec  = Iph * cos(theta           - phi_pf);
ib_vec  = Iph * cos(theta - 2*pi/3 - phi_pf);
ic_vec  = Iph * cos(theta - 4*pi/3 - phi_pf);

%% ── PER-INTERVAL: SIGN DETECTION + PHASE ASSIGNMENT ─────────────────────────
theta_b_vec = zeros(1, Nsw);   % carrier phase shift for leg b
theta_c_vec = zeros(1, Nsw);   % carrier phase shift for leg c
sector_vec  = zeros(1, Nsw);   % which sector (1-6)
rms_opt_vec = zeros(1, Nsw);
rms_conv_vec= zeros(1, Nsw);

for k = 1:Nsw
    da = da_vec(k);  db = db_vec(k);  dc = dc_vec(k);
    ia = ia_vec(k);  ib = ib_vec(k);  ic = ic_vec(k);

    % Sign vector: +1 or -1
    sa = sign(ia);  sb = sign(ib);  sc = sign(ic);

    % Identify lone-sign leg:
    %   Lone = the one whose sign differs from the other two.
    %   Since ia+ib+ic=0, exactly one or two can share a sign.
    %   The two same-sign legs form the "bank"; the lone leg is "A".
    %
    %   6 sectors based on current signs:
    %   (+--): lone=a   (++-): lone=c   (-+-): lone=b
    %   (-++): lone=a   (--+): lone=c   (+-+): lone=b
    %
    % Rule: theta_B = 0,  theta_C = dA - dC
    %   where A=lone, B=same-bank leg1, C=same-bank leg2

    if sa ~= sb && sa ~= sc          % lone = a,  bank = {b, c}
        dA=da; dB=db; dC=dc;
        if ia > 0; sector_vec(k)=1; else; sector_vec(k)=4; end
        tb_raw = 0;
        tc_raw = dA - dC;

    elseif sb ~= sa && sb ~= sc      % lone = b,  bank = {a, c}
        dA=db; dB=da; dC=dc;
        if ib > 0; sector_vec(k)=3; else; sector_vec(k)=6; end
        % carrier of actual leg b is "A" reference: theta_b=0 by convention
        % actual leg a gets theta_B=0, actual leg c gets theta_B=dA-dC
        % but we always express shifts relative to leg-a carrier = 0
        % so here:  leg-b is lone → leg-b stays at 0 (reference)
        %           leg-a aligned to start of b → same start → theta_a_shift=0
        %           leg-c aligned to end   of b → theta_c_shift = dA-dC
        % Re-express as (theta_b, theta_c) where theta_a=0 always:
        %   lone = b: we need leg_b at 0 (it already is if we set theta_b=0)
        %             leg_a start = leg_b start → theta_a_shift=0 (already 0)
        %             leg_c end   = leg_b end   → theta_c = theta_b + dA - dC
        tb_raw = 0;                  % b is lone, a is already at 0 aligned
        tc_raw = dA - dC;            % end of c = end of b

    else                             % lone = c,  bank = {a, b}
        dA=dc; dB=da; dC=db;
        if ic > 0; sector_vec(k)=5; else; sector_vec(k)=2; end
        % lone = c: leg_c should be the reference.
        % Align leg_a START with leg_c START → theta_a=0 (fixed), so
        %   theta_c = 0 (c starts at same place as a)
        % Align leg_b END with leg_c END:
        %   theta_b + db = theta_c + dc → theta_b = dc - db
        tb_raw = dA - dC;            % = dc - db
        tc_raw = 0;
    end

    % Store phase shifts
    theta_b_vec(k) = mod(tb_raw, 1.0);
    theta_c_vec(k) = mod(tc_raw, 1.0);

    % RMS calculation for this interval
    rms_opt_vec(k)  = interval_rms(ia,ib,ic,da,db,dc, theta_b_vec(k), theta_c_vec(k));
    rms_conv_vec(k) = interval_rms(ia,ib,ic,da,db,dc, 0, 0);
end

% Overall fundamental-period RMS (Eq.7 from paper)
RMS_opt_total  = sqrt(mean(rms_opt_vec.^2));
RMS_conv_total = sqrt(mean(rms_conv_vec.^2));
reduction_total = 100*(RMS_conv_total - RMS_opt_total)/RMS_conv_total;

fprintf('============================================================\n');
fprintf('  Full-Cycle Results  (ma=%.2f, pf=%.2f)\n', ma, pf);
fprintf('============================================================\n');
fprintf('  Conventional total RMS = %.6f p.u.\n', RMS_conv_total);
fprintf('  Optimal total RMS      = %.6f p.u.\n', RMS_opt_total);
fprintf('  Total RMS reduction    = %.2f%%\n',     reduction_total);
fprintf('============================================================\n');

%% ── WAVEFORM RECONSTRUCTION (one representative switching period) ────────────
% Pick one interval near theta=45 deg for detailed waveform display
[~, k_demo] = min(abs(theta - deg2rad(45)));

da_d = da_vec(k_demo);  db_d = db_vec(k_demo);  dc_d = dc_vec(k_demo);
ia_d = ia_vec(k_demo);  ib_d = ib_vec(k_demo);  ic_d = ic_vec(k_demo);
tb_d = theta_b_vec(k_demo);
tc_d = theta_c_vec(k_demo);

Nw = 50000;
tau = linspace(0,1,Nw+1); tau=tau(1:end-1);

[icap_opt_d,  Sa_o, Sb_o, Sc_o] = build_icap(ia_d,ib_d,ic_d,da_d,db_d,dc_d,0,tb_d,tc_d,tau);
[icap_conv_d, Sa_c, Sb_c, Sc_c] = build_icap(ia_d,ib_d,ic_d,da_d,db_d,dc_d,0,0,  0,  tau);

%% ── PLOTTING ─────────────────────────────────────────────────────────────────
bg_col    = [0.051 0.067 0.090];
panel_col = [0.086 0.106 0.133];
grid_col  = [0.129 0.149 0.173];
text_col  = [0.545 0.580 0.616];
white_col = [0.902 0.929 0.953];
col_a     = [0.969 0.506 0.400];
col_b     = [0.475 0.753 1.000];
col_c     = [0.337 0.827 0.392];
col_cap   = [1.000 0.651 0.341];
col_conv  = [0.400 0.420 0.440];
col_sec   = [0.800 0.700 0.200];

theta_deg = rad2deg(theta);
fig = figure('Color',bg_col,'Position',[60 30 1400 980]);

%% Row 1: Sinusoidal duty cycles and currents
ax1 = subplot(5,2,1);
hold on; box on;
plot(theta_deg, da_vec, 'Color',col_a, 'LineWidth',1.8);
plot(theta_deg, db_vec, 'Color',col_b, 'LineWidth',1.8);
plot(theta_deg, dc_vec, 'Color',col_c, 'LineWidth',1.8);
yline(0.5,'--','Color',grid_col,'LineWidth',0.8);
style_ax(ax1,panel_col,grid_col,text_col,white_col,...
    'Duty Cycles  d_a, d_b, d_c  (sinusoidal)','Duty cycle');
legend({'d_a','d_b','d_c'},'TextColor',white_col,'Color',panel_col,...
    'EdgeColor',grid_col,'FontSize',8,'Location','northeast');

ax2 = subplot(5,2,2);
hold on; box on;
plot(theta_deg, ia_vec, 'Color',col_a, 'LineWidth',1.8);
plot(theta_deg, ib_vec, 'Color',col_b, 'LineWidth',1.8);
plot(theta_deg, ic_vec, 'Color',col_c, 'LineWidth',1.8);
yline(0,'--','Color',grid_col,'LineWidth',0.8);
style_ax(ax2,panel_col,grid_col,text_col,white_col,...
    sprintf('Phase Currents  (p.f.=%.2f, \\phi=%.1f°)',pf,rad2deg(phi_pf)),'Current (p.u.)');
legend({'i_a','i_b','i_c'},'TextColor',white_col,'Color',panel_col,...
    'EdgeColor',grid_col,'FontSize',8,'Location','northeast');

%% Row 2: Sign sectors and phase shifts
ax3 = subplot(5,2,3);
hold on; box on;
% Shade sectors by background colour
sector_colors = [col_a*0.4; col_b*0.3; col_c*0.3; col_a*0.3; col_b*0.4; col_c*0.4];
for s = 1:6
    idx = find(sector_vec == s);
    if ~isempty(idx)
        for ii = 1:length(idx)
            xb = theta_deg(idx(ii));
            xw = 360/Nsw;
            patch(ax3,[xb xb+xw xb+xw xb],[0 0 7 7], ...
                sector_colors(s,:),'FaceAlpha',0.5,'EdgeColor','none');
        end
    end
end
text_sectors = {'(+--) lone=a','(++-) lone=c','(-+-) lone=b',...
                '(-++) lone=a','(--+) lone=c','(+-+) lone=b'};
% Add sector labels at midpoints
for s = 1:6
    idx = find(sector_vec == s);
    if ~isempty(idx)
        xmid = mean(theta_deg(idx));
        text(ax3, xmid, 6.3, text_sectors{s}, 'Color',white_col,...
            'FontSize',6.5,'HorizontalAlignment','center');
    end
end
plot(theta_deg, sector_vec, 'Color',col_sec,'LineWidth',1.5,'LineStyle','none',...
    'Marker','.','MarkerSize',4);
ylim([0 7]);
style_ax(ax3,panel_col,grid_col,text_col,white_col,...
    'Current Sign Sector  (which leg is lone-sign)','Sector');
yticks(1:6);

ax4 = subplot(5,2,4);
hold on; box on;
plot(theta_deg, theta_b_vec*360, 'Color',col_b, 'LineWidth',1.8, ...
    'DisplayName','\theta_b (deg)');
plot(theta_deg, theta_c_vec*360, 'Color',col_c, 'LineWidth',1.8, ...
    'DisplayName','\theta_c (deg)');
yline(0,'--','Color',grid_col,'LineWidth',0.8);
style_ax(ax4,panel_col,grid_col,text_col,white_col,...
    'Optimal Carrier Phase Shifts  \theta_b, \theta_c  (deg)','Phase shift (deg)');
legend('TextColor',white_col,'Color',panel_col,'EdgeColor',grid_col,...
    'FontSize',8,'Location','northeast');

%% Row 3: Per-interval RMS comparison
ax5 = subplot(5,2,[5 6]);
hold on; box on;
plot(theta_deg, rms_conv_vec, 'Color',col_conv,'LineWidth',1.5,...
    'DisplayName',sprintf('Conventional  (total=%.4f p.u.)',RMS_conv_total));
plot(theta_deg, rms_opt_vec,  'Color',col_cap, 'LineWidth',2.0,...
    'DisplayName',sprintf('Optimal       (total=%.4f p.u.)  [%.1f%% reduction]',...
    RMS_opt_total, reduction_total));
yline(0,'--','Color',grid_col,'LineWidth',0.8);
style_ax(ax5,panel_col,grid_col,text_col,white_col,...
    'Per-Switching-Interval Capacitor RMS  I_{cap,rms}[k]','RMS (p.u.)');
leg5 = legend('Location','northeast','FontSize',9);
set(leg5,'Color',panel_col,'TextColor',white_col,'EdgeColor',grid_col);

%% Row 4: Demo switching interval — signals
offset = 1.35;
ax6 = subplot(5,2,7);
hold on; box on;
stairs(tau, Sa_c+2*offset,'Color',col_a,'LineWidth',1.8);
stairs(tau, Sb_c+1*offset,'Color',col_b,'LineWidth',1.8);
stairs(tau, Sc_c+0*offset,'Color',col_c,'LineWidth',1.8);
style_ax(ax6,panel_col,grid_col,text_col,white_col,...
    sprintf('Conventional — demo interval (\\theta=%.0f°)',rad2deg(theta(k_demo))));
ylim([-0.2 3.3]);
yticks([0.5 0.5+offset 0.5+2*offset]); yticklabels({'Sc','Sb','Sa'});
add_info(ax6, ia_d,ib_d,ic_d,da_d,db_d,dc_d, col_a,col_b,col_c,white_col,offset);

ax7 = subplot(5,2,8);
hold on; box on;
stairs(tau, Sa_o+2*offset,'Color',col_a,'LineWidth',1.8);
stairs(tau, Sb_o+1*offset,'Color',col_b,'LineWidth',1.8);
stairs(tau, Sc_o+0*offset,'Color',col_c,'LineWidth',1.8);
xline(ax7, 0,    '--','Color',[1 1 1 0.4],'LineWidth',1.0);
xline(ax7, tb_d, '--','Color',col_b,      'LineWidth',1.0,'Alpha',0.6);
xline(ax7, tc_d, '--','Color',col_c,      'LineWidth',1.0,'Alpha',0.6);
style_ax(ax7,panel_col,grid_col,text_col,white_col,...
    sprintf('Optimal — demo interval  \\theta_b=%.3f  \\theta_c=%.3f',tb_d,tc_d));
ylim([-0.2 3.3]);
yticks([0.5 0.5+offset 0.5+2*offset]); yticklabels({'Sc','Sb','Sa'});
add_info(ax7, ia_d,ib_d,ic_d,da_d,db_d,dc_d, col_a,col_b,col_c,white_col,offset);

%% Row 5: Demo capacitor current
ax8 = subplot(5,2,[9 10]);
hold on; box on;
stairs(tau, icap_conv_d,'Color',col_conv,'LineWidth',1.2,...
    'DisplayName',sprintf('Conventional  RMS=%.4f p.u.',sqrt(mean(icap_conv_d.^2))));
stairs(tau, icap_opt_d, 'Color',col_cap, 'LineWidth',2.0,...
    'DisplayName',sprintf('Optimal       RMS=%.4f p.u.',sqrt(mean(icap_opt_d.^2))));
yline(0,'--','Color',grid_col,'LineWidth',0.8);
style_ax(ax8,panel_col,grid_col,text_col,white_col,...
    sprintf('Capacitor Current — demo interval (\\theta=%.0f°)',rad2deg(theta(k_demo))),...
    'i_{cap} (p.u.)');
leg8 = legend('Location','northeast','FontSize',9);
set(leg8,'Color',panel_col,'TextColor',white_col,'EdgeColor',grid_col);

% Main title
annotation(fig,'textbox',[0 0.968 1 0.032],...
    'String',sprintf('Adaptive Multi-Carrier PWM — Full Cycle  (m_a=%.2f, p.f.=%.2f)',ma,pf),...
    'Color',white_col,'FontSize',13,'FontWeight','bold',...
    'HorizontalAlignment','center','EdgeColor','none','BackgroundColor','none');

saveas(fig,'sync_rule_fullcycle.png');
fprintf('\n  Figure saved: sync_rule_fullcycle.png\n');

%% ═══════════════════════════════════════════════════════════════════════════
%%  LOCAL FUNCTIONS
%% ═══════════════════════════════════════════════════════════════════════════

function rms_val = interval_rms(ia,ib,ic,da,db,dc,tb,tc)
    F0   = ia^2*da*(1-da) + ib^2*db*(1-db) + ic^2*dc*(1-dc);
    lab  = overlap(da,db,tb);
    lac  = overlap(da,dc,tc);
    lbc  = overlap(db,dc,tc-tb);
    rms2 = F0 + 2*ia*ib*(lab-da*db) + 2*ia*ic*(lac-da*dc) + 2*ib*ic*(lbc-db*dc);
    rms_val = sqrt(max(rms2, 0));
end

function ov = overlap(dx,dy,delta)
    delta = mod(delta,1.0);
    ov1 = max(0, min([dx, dy, dx+dy-delta]));
    ov2 = max(0, min([dx, dy, dx+dy-(1-delta)]));
    ov  = ov1 + ov2;
end

function [icap, Sa, Sb, Sc] = build_icap(ia,ib,ic,da,db,dc,ta,tb,tc,tau)
    Sa   = make_pulse(da,ta,tau);
    Sb   = make_pulse(db,tb,tau);
    Sc   = make_pulse(dc,tc,tau);
    idc  = ia*da + ib*db + ic*dc;
    icap = ia*Sa + ib*Sb + ic*Sc - idc;
end

function s = make_pulse(d,theta,tau)
    s0 = mod(theta,1.0);
    s1 = mod(theta+d,1.0);
    if s0 < s1
        s = double(tau>=s0 & tau<s1);
    else
        s = double(tau>=s0 | tau<s1);
    end
end

function style_ax(ax,panel_col,grid_col,text_col,white_col,ttl,ylbl)
    set(ax,'Color',panel_col,'XColor',text_col,'YColor',text_col,...
        'GridColor',grid_col,'FontSize',8,'XGrid','on','YGrid','on',...
        'GridAlpha',0.25);
    title(ax,ttl,'Color',white_col,'FontSize',9,'FontWeight','bold');
    xlabel(ax,'Fundamental angle  \theta  (deg)','Color',text_col,'FontSize',8);
    if nargin >= 7
        ylabel(ax,ylbl,'Color',text_col,'FontSize',8);
    end
    xlim(ax,[0 360]);
    xticks(ax,0:60:360);
end

function add_info(ax,ia,ib,ic,da,db,dc,ca,cb,cc,cw,offset)
    text(ax,0.99,2*offset+0.5,sprintf('i_a=%+.3f  d_a=%.3f',ia,da),...
        'Color',ca,'FontSize',7.5,'HorizontalAlignment','right','Units','data');
    text(ax,0.99,1*offset+0.5,sprintf('i_b=%+.3f  d_b=%.3f',ib,db),...
        'Color',cb,'FontSize',7.5,'HorizontalAlignment','right','Units','data');
    text(ax,0.99,0*offset+0.5,sprintf('i_c=%+.3f  d_c=%.3f',ic,dc),...
        'Color',cc,'FontSize',7.5,'HorizontalAlignment','right','Units','data');
end

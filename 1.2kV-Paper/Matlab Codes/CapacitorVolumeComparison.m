%% ====================== Parametric Capacitance vs. f_sw ======================
% Compare DC-link capacitance and estimated volume vs. switching frequency
% for two different DC-link voltages, with muted blue color palette.
% Requires: mod_2lcarr() on MATLAB path.

clear; clc;
addpath('C:\Github\KTH\ECCE\Modlab used in the course folder');

%% ----------------------- User Parameters -------------------------------------
f1          = 500;                % Fundamental frequency [Hz]
ma_sel      = 1;               % Modulation index
pf_sel      = 0.90;               % Power factor (cos phi)
P_out       = 300e3;              % Output power [W]
overmod_fac = 1.15;               % Overmodulation factor

Ud_list     = [800, 1200];        % DC-link voltages to compare [V]

% Ripple target
use_frac_ripple = true;           % true: fractional ripple; false: absolute
DeltaV_frac      = 0.01;          % 1% ripple of Ud
DeltaV_abs       = 10;            % 10 V absolute ripple

% Switching frequency sweep
f_sw_vec    = 5e3 : 1e3 : 20e3;   % [Hz]

% Carrier/reference settings
carrytype   = 'tria';
smp         = 'ns';
cmode       = 'tri6';
thetac      = 0;
start_angle = 0;
end_angle   = 2*pi;
ma_dc       = 0;

% Volume scaling (distinct for each Ud)
k_vol_map = containers.Map( ...
    {num2str(Ud_list(1)), num2str(Ud_list(2))}, ...
    {1.5,              2.0});   % [m^3/F] example values

%% ----------------------- Helper Function -------------------------------------
calc_C_required = @(Ic, t, dV) ...
    ( max(cumtrapz(t(:), Ic(:))) - min(cumtrapz(t(:), Ic(:))) ) / dV;

phi_load = acos(pf_sel);

%% ----------------------- Preallocate Outputs ---------------------------------
C_vs_f = zeros(numel(Ud_list), numel(f_sw_vec));  % [F]
V_vs_f = zeros(numel(Ud_list), numel(f_sw_vec));  % [m^3]

%% ----------------------- Main Sweep ------------------------------------------
for iu = 1:numel(Ud_list)
    Ud = Ud_list(iu);

    if use_frac_ripple
        DeltaV_pp = DeltaV_frac * Ud;
    else
        DeltaV_pp = DeltaV_abs;
    end

    Upk_ref = overmod_fac * Ud / 2;
    ippk    = P_out * 2/3 / (Upk_ref * pf_sel);

    for k = 1:numel(f_sw_vec)
        fc = f_sw_vec(k);
        pn = round(fc / f1);

        % --- Generate modulation waveforms ---
        theta0 = 0;
        [vp_a, wt, ~, ~] = mod_2lcarr(ma_sel, pn, 10000, carrytype, smp, cmode, theta0, thetac, start_angle, end_angle, ma_dc);
        theta0 =  2*pi/3;
        [vp_b, ~,  ~, ~] = mod_2lcarr(ma_sel, pn, 10000, carrytype, smp, cmode, theta0, thetac, start_angle, end_angle, ma_dc);
        theta0 = -2*pi/3;
        [vp_c, ~,  ~, ~] = mod_2lcarr(ma_sel, pn, 10000, carrytype, smp, cmode, theta0, thetac, start_angle, end_angle, ma_dc);

        % Force column vectors
        vp_a = vp_a(:); vp_b = vp_b(:); vp_c = vp_c(:);
        wt   = wt(:);
        t = wt / (2*pi*f1);

        % --- Phase currents ---
        ip_a =  ippk * cos(wt - phi_load);
        ip_b =  ippk * cos(wt - phi_load + 2*pi/3);
        ip_c =  ippk * cos(wt - phi_load - 2*pi/3);

        % --- Conduction pattern ---
        Ipk = ip_a; Upk = vp_a;
        sw = (Ipk>=0 & Upk>0) | (Ipk<0 & Upk<=0);
        Isw_a = abs(Ipk .* sw);

        Ipk = ip_b; Upk = vp_b;
        sw = (Ipk>=0 & Upk>0) | (Ipk<0 & Upk<=0);
        Isw_b = abs(Ipk .* sw);

        Ipk = ip_c; Upk = vp_c;
        sw = (Ipk>=0 & Upk>0) | (Ipk<0 & Upk<=0);
        Isw_c = abs(Ipk .* sw);

        Ic = Isw_a + Isw_b + Isw_c;
        Ic = Ic - mean(Ic);

        % --- Capacitance and Volume ---
        C_req = calc_C_required(Ic, t, DeltaV_pp);
        C_vs_f(iu, k) = C_req;

        k_vol = k_vol_map(num2str(Ud));
        V_vs_f(iu, k) = k_vol * C_req;
    end
end

%% ----------------------- Plot Styling ----------------------------------------
% Muted blue color palette (dark → light)
c_darkblue  = [0.25 0.40 0.70];
c_midblue   = [0.36 0.54 0.75];
c_lightblue = [0.55 0.70 0.85];

font_axes  = 18;
font_label = 18;
lw = 2.0;

%% ----------------------- Plot 1: Capacitance vs f_sw -------------------------
figure('Color','w','Position',[160 90 940 480]);
axes1 = axes('FontName','Times New Roman','FontSize',font_axes,'LineWidth',1.2);
hold(axes1,'on'); grid on; box on;

plot(f_sw_vec/1e3, C_vs_f(1,:)*1e6, '-', 'Color', c_darkblue, 'LineWidth', lw);
plot(f_sw_vec/1e3, C_vs_f(2,:)*1e6, '-',  'Color', c_lightblue, 'LineWidth', lw);

xlabel('Switching Frequency f_{sw} [kHz]', 'FontSize', font_label);
ylabel('Required C_{bus} [\muF]', 'FontSize', font_label);
%title(sprintf('C_{bus} vs f_{sw}  (m_a = %.2f, cos\\phi = %.2f)', ma_sel, pf_sel), ...
%    'FontWeight', 'normal', 'FontSize', font_label);
legend(arrayfun(@(u) sprintf('U_{dc} = %d V', u), Ud_list, 'UniformOutput', false), ...
    'Location','northeast', 'FontSize', 14);

%% ----------------------- Plot 2: Volume vs f_sw ------------------------------
figure('Color','w','Position',[160 90 940 480]);
axes2 = axes('FontName','Times New Roman','FontSize',font_axes,'LineWidth',1.2);
hold(axes2,'on'); grid on; box on;

plot(f_sw_vec/1e3, V_vs_f(1,:)*1e3, '-', 'Color', c_darkblue, 'LineWidth', lw);
plot(f_sw_vec/1e3, V_vs_f(2,:)*1e3, '-',  'Color', c_lightblue, 'LineWidth', lw);

xlabel('Switching Frequency f_{sw} [kHz]', 'FontSize', font_label);
ylabel('Capacitor Volume [L]', 'FontSize', font_label);
%title('Estimated Capacitor Volume vs f_{sw}', 'FontWeight', 'normal', 'FontSize', font_label);
legend(arrayfun(@(u) sprintf('U_{dc} = %d V', u), Ud_list, 'UniformOutput', false), ...
    'Location','northeast', 'FontSize', 14);

%% ----------------------- Notes ------------------------------------------------
% - Uses blue-only color shades: dark (low voltage) and light (high voltage).
% - Font, line, and axes settings match your earlier muted plots.
% - Update k_vol_map for realistic capacitor technology data.
% - If mod_2lcarr() supports non-integer pn, you can remove rounding.

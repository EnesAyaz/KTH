function SPB_Loss_GUI_v3
% SPB_Loss_GUI_v3
% Parametric sizing and loss calculator for a Stacked Polyphase Bridges (SPB)
% converter using datasheet-level semiconductor parameters.
%
% Run in MATLAB with:
%   SPB_Loss_GUI_v3
%
% Notes:
% - This is an early-stage engineering calculator, not a detailed electro-thermal model.
% - Switching energy is scaled linearly with voltage and current from datasheet reference values.
% - Conduction loss is approximated for a three-phase two-level bridge per SPB submodule.
% - Parallel devices are assumed to share current ideally.

    app = struct();
    app.fig = uifigure('Name','SPB Datasheet-Based Loss and Sizing Calculator v3', ...
        'Position',[80 80 1280 760]);
    app.grid = uigridlayout(app.fig,[1 2]);
    app.grid.ColumnWidth = {430,'1x'};

    left = uipanel(app.grid,'Title','Inputs');
    left.Scrollable = 'on';
    gl = uigridlayout(left,[38 3]);
    gl.ColumnWidth = {210,120,70};
    gl.RowHeight = repmat({28},1,38);

    row = 1;
    addSection('System requirements');
    app.Vdc          = addNum('Total DC-link voltage', 1200, 'V');
    app.Pout         = addNum('Output power', 300, 'kW');
    app.pf           = addNum('Power factor', 0.95, '-');
    app.modIndex     = addNum('Modulation index, M', 0.90, '-');
    app.etaInitial   = addNum('Initial efficiency guess', 0.98, '-');
    app.Vmargin      = addNum('Voltage safety margin', 1.50, 'x');
    app.Imargin      = addNum('Current derating margin', 1.25, 'x');
    app.postFault    = addCheck('Post-fault N-1 voltage check', true);

    addSection('Device datasheet parameters');
    app.Vrated       = addNum('Device voltage rating', 750, 'V');
    app.Irated       = addNum('Device RMS current rating', 300, 'A');
    app.Rds25        = addNum('Rds(on) at 25 C', 5.0, 'mΩ');
    app.alphaR       = addNum('Rds temp. coefficient', 0.004, '1/C');
    app.Eon          = addNum('Eon at ref. point', 5.0, 'mJ');
    app.Eoff         = addNum('Eoff at ref. point', 4.0, 'mJ');
    app.Vref         = addNum('Reference voltage for E', 400, 'V');
    app.Iref         = addNum('Reference current for E', 300, 'A');
    app.energyExpI   = addNum('Current scaling exponent', 1.0, '-');
    app.energyExpV   = addNum('Voltage scaling exponent', 1.0, '-');

    addSection('Thermal parameters');
    app.Tamb         = addNum('Ambient / coolant temperature', 65, 'C');
    app.Tmax         = addNum('Maximum junction temperature', 150, 'C');
    app.RthJC        = addNum('Rth junction-case per device', 0.15, 'C/W');
    app.RthCH        = addNum('Rth case-heatsink per device', 0.05, 'C/W');
    app.RthHA        = addNum('Rth heatsink-ambient per SPB module', 0.025, 'C/W');
    app.PauxModule   = addNum('Auxiliary loss per SPB module', 10, 'W');

    addSection('Search and sweep settings');
    app.NsMax        = addNum('Maximum series modules to test', 20, '-');
    app.NpMax        = addNum('Maximum parallel devices to test', 20, '-');
    app.fswDesign    = addNum('Design switching frequency', 20, 'kHz');
    app.fswMin       = addNum('Sweep fsw minimum', 5, 'kHz');
    app.fswMax       = addNum('Sweep fsw maximum', 100, 'kHz');
    app.fswStep      = addNum('Sweep fsw step', 5, 'kHz');

    app.calcButton = uibutton(gl,'Text','Calculate / Update Plot','ButtonPushedFcn',@(~,~)calculateAndPlot());
    app.calcButton.Layout.Row = row; app.calcButton.Layout.Column = [1 3];

    right = uipanel(app.grid,'Title','Results');
    rgl = uigridlayout(right,[3 1]);
    rgl.RowHeight = {210,230,'1x'};

    app.summary = uitable(rgl,'ColumnName',{'Quantity','Value','Unit'}, ...
        'ColumnWidth',{260,130,80});
    app.sweepTable = uitable(rgl,'ColumnName',{'fsw_kHz','Ns','Np','Loss_W','Efficiency_%','Tj_C','Feasible'}, ...
        'ColumnWidth',{80,60,60,100,100,80,80});
    app.ax = uiaxes(rgl);
    title(app.ax,'Efficiency vs switching frequency');
    xlabel(app.ax,'Switching frequency (kHz)');
    ylabel(app.ax,'Efficiency (%)');
    grid(app.ax,'on');

    calculateAndPlot();

    function addSection(name)
        lbl = uilabel(gl,'Text',name,'FontWeight','bold');
        lbl.Layout.Row = row; lbl.Layout.Column = [1 3];
        row = row + 1;
    end

    function h = addNum(label, value, unit)
        lab = uilabel(gl,'Text',label);
        lab.Layout.Row = row; lab.Layout.Column = 1;
        h = uieditfield(gl,'numeric','Value',value);
        h.Layout.Row = row; h.Layout.Column = 2;
        un = uilabel(gl,'Text',unit);
        un.Layout.Row = row; un.Layout.Column = 3;
        row = row + 1;
    end

    function h = addCheck(label, value)
        lab = uilabel(gl,'Text',label);
        lab.Layout.Row = row; lab.Layout.Column = 1;
        h = uicheckbox(gl,'Value',value,'Text','');
        h.Layout.Row = row; h.Layout.Column = 2;
        row = row + 1;
    end

    function p = readInputs()
        p.Vdc        = app.Vdc.Value;
        p.Pout       = app.Pout.Value * 1e3;
        p.pf         = app.pf.Value;
        p.M          = app.modIndex.Value;
        p.eta0       = app.etaInitial.Value;
        p.Vmargin    = app.Vmargin.Value;
        p.Imargin    = app.Imargin.Value;
        p.postFault  = app.postFault.Value;

        p.Vrated     = app.Vrated.Value;
        p.Irated     = app.Irated.Value;
        p.Rds25      = app.Rds25.Value * 1e-3;
        p.alphaR     = app.alphaR.Value;
        p.Eon        = app.Eon.Value * 1e-3;
        p.Eoff       = app.Eoff.Value * 1e-3;
        p.Vref       = app.Vref.Value;
        p.Iref       = app.Iref.Value;
        p.expI       = app.energyExpI.Value;
        p.expV       = app.energyExpV.Value;

        p.Tamb       = app.Tamb.Value;
        p.Tmax       = app.Tmax.Value;
        p.RthJC      = app.RthJC.Value;
        p.RthCH      = app.RthCH.Value;
        p.RthHA      = app.RthHA.Value;
        p.PauxModule = app.PauxModule.Value;

        p.NsMax      = round(app.NsMax.Value);
        p.NpMax      = round(app.NpMax.Value);
        p.fswDesign  = app.fswDesign.Value * 1e3;
        p.fswMin     = app.fswMin.Value * 1e3;
        p.fswMax     = app.fswMax.Value * 1e3;
        p.fswStep    = app.fswStep.Value * 1e3;
    end

    function calculateAndPlot()
        try
        p = readInputs();
        [best, candidates] = findBestDesign(p, p.fswDesign);

        if isempty(best)
            app.summary.Data = {'No feasible design found within search limits','',''; ...
                                'Try increasing NsMax/NpMax or relaxing thermal/current margins','',''};
            app.sweepTable.Data = {};
            cla(app.ax);
            return;
        end

        summary = {
            'Required series SPB modules, Ns', best.Ns, '-';
            'Required parallel devices per switch, Np', best.Np, '-';
            'DC voltage per SPB module', best.Vmodule, 'V';
            'Voltage utilization incl. margin', best.VstressWithMargin, 'V';
            'Estimated module phase RMS current', best.Iphase, 'A';
            'Estimated RMS current per device', best.IdevRms, 'A';
            'Total conduction loss', best.PcondTotal, 'W';
            'Total switching loss', best.PswTotal, 'W';
            'Total auxiliary loss', best.PauxTotal, 'W';
            'Total inverter loss', best.PlossTotal, 'W';
            'Efficiency at design fsw', 100*best.eta, '%';
            'Estimated worst-case junction temp.', best.Tj, 'C';
            'Feasibility status', char(best.status), '-'};
        app.summary.Data = summary;

        fswVec = p.fswMin:p.fswStep:p.fswMax;
        out = cell(numel(fswVec),7);
        etaVec = nan(size(fswVec));
        feasibleVec = false(size(fswVec));
        for k = 1:numel(fswVec)
            p2 = p;
            [b,~] = findBestDesign(p2, fswVec(k));
            if ~isempty(b)
                out(k,:) = {fswVec(k)/1e3, b.Ns, b.Np, b.PlossTotal, 100*b.eta, b.Tj, 'Yes'};
                etaVec(k) = 100*b.eta;
                feasibleVec(k) = true;
            else
                out(k,:) = {fswVec(k)/1e3, NaN, NaN, NaN, NaN, NaN, 'No'};
            end
        end
        app.sweepTable.Data = out;

        cla(app.ax);
        plot(app.ax, fswVec(feasibleVec)/1e3, etaVec(feasibleVec), '-o','LineWidth',1.5);
        grid(app.ax,'on');
        xlabel(app.ax,'Switching frequency (kHz)');
        ylabel(app.ax,'Efficiency (%)');
        title(app.ax,sprintf('Best feasible design at each fsw; design point: Ns=%d, Np=%d',best.Ns,best.Np));

        % Optional: show candidate matrix in command window for debugging/use.
        assignin('base','SPB_last_candidates',candidates);
        assignin('base','SPB_last_best',best);
        catch ME
            disp(getReport(ME,'extended'));
            app.summary.Data = {'Error', ME.message, '-'; 'Check inputs', 'Use positive numeric values', '-'};
            app.sweepTable.Data = {};
            cla(app.ax);
            title(app.ax,'Calculation error');
        end
    end
end

function [best, candidates] = findBestDesign(p, fsw)
    candidates = struct([]);
    best = [];
    idx = 0;

    for Ns = 1:p.NsMax
        for Np = 1:p.NpMax
            r = evaluateDesign(p, Ns, Np, fsw);
            if r.validBasic
                idx = idx + 1;
                candidates(idx) = r; %#ok<AGROW>
            end
        end
    end

    if isempty(candidates)
        return;
    end

    feasible = candidates([candidates.feasible]);
    if isempty(feasible)
        return;
    end

    % Objective: first minimize total device count, then maximize efficiency.
    deviceCount = [feasible.Ns] .* [feasible.Np] * 6;
    minDev = min(deviceCount);
    subset = feasible(deviceCount == minDev);
    [~,i] = max([subset.eta]);
    best = subset(i);
end

function r = evaluateDesign(p, Ns, Np, fsw)
    r = struct();
    r.Ns = Ns;
    r.Np = Np;
    r.fsw = fsw;

    r.Vmodule = p.Vdc / Ns;
    if p.postFault && Ns > 1
        r.VmoduleWorst = p.Vdc / (Ns - 1);
    elseif p.postFault && Ns == 1
        r.VmoduleWorst = Inf;
    else
        r.VmoduleWorst = r.Vmodule;
    end
    r.VstressWithMargin = r.VmoduleWorst * p.Vmargin;
    voltageOK = r.VstressWithMargin <= p.Vrated;

    % Approximate line-line RMS voltage capability of each SPB bridge.
    % M is assumed to map Vdc_module to fundamental line-line RMS as M*Vdc/sqrt(2).
    r.VllModuleRms = p.M * r.Vmodule / sqrt(2);
    r.Pmodule = p.Pout / Ns;
    r.Iphase = r.Pmodule / (sqrt(3) * max(r.VllModuleRms,eps) * max(p.pf,eps));

    r.IdevRms = r.Iphase / sqrt(2) / Np; % each switch conducts about half cycle
    currentOK = r.IdevRms * p.Imargin <= p.Irated;

    % Iterative Rds correction with junction temperature.
    TjGuess = p.Tamb + 50;
    for it = 1:5
        RdsT = p.Rds25 * (1 + p.alphaR * (TjGuess - 25));
        RdsT = max(RdsT, p.Rds25*0.2);

        % Total conduction loss for Ns three-phase bridges.
        PcondModule = 3 * r.Iphase^2 * RdsT / Np;
        PcondTotal = Ns * PcondModule;

        % Switching energy per paralleled device, scaled from datasheet point.
        IeventPerDevice = sqrt(2) * r.Iphase / Np;
        Escaled = (p.Eon + p.Eoff) * (r.Vmodule / max(p.Vref,eps))^p.expV * ...
                  (IeventPerDevice / max(p.Iref,eps))^p.expI;
        Escaled = max(Escaled,0);
        PswDevice = Escaled * fsw;
        PswTotal = Ns * 6 * Np * PswDevice;

        PauxTotal = Ns * p.PauxModule;
        PlossTotal = PcondTotal + PswTotal + PauxTotal;
        PmoduleLoss = PlossTotal / Ns;
        PcondDevice = (r.Iphase^2 / 2) * RdsT / Np;
        Pdev = PcondDevice + PswDevice;
        Tcase = p.Tamb + PmoduleLoss * p.RthHA;
        TjGuess = Tcase + Pdev * (p.RthJC + p.RthCH);
    end

    r.RdsT = RdsT;
    r.PcondModule = PcondModule;
    r.PcondTotal = PcondTotal;
    r.PswDevice = PswDevice;
    r.PswTotal = PswTotal;
    r.PauxTotal = PauxTotal;
    r.PlossTotal = PlossTotal;
    r.eta = p.Pout / (p.Pout + PlossTotal);
    r.Tj = TjGuess;
    r.Pdev = Pdev;

    thermalOK = r.Tj <= p.Tmax;
    r.validBasic = isfinite(r.VmoduleWorst) && r.VllModuleRms > 0 && r.Iphase > 0;
    r.feasible = r.validBasic && voltageOK && currentOK && thermalOK;

    if r.feasible
        r.status = 'OK';
    else
        fail = strings(0);
        if ~voltageOK, fail(end+1) = 'Voltage'; end %#ok<AGROW>
        if ~currentOK, fail(end+1) = 'Current'; end %#ok<AGROW>
        if ~thermalOK, fail(end+1) = 'Thermal'; end %#ok<AGROW>
        r.status = strjoin(fail, ', ');
    end
end

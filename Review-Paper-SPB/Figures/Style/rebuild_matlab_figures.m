function rebuild_matlab_figures()
% Run from any folder after the MATLAB network license becomes available.
root=fileparts(fileparts(mfilename('fullpath')));
files={fullfile(root,'Section-Intro','fig_intro_hv_motivation.m'), ...
 fullfile(root,'Section-Intro','fig_intro_ronsp_trend.m'), ...
 fullfile(root,'Section-DCLinkBalancing','fig_dclink_balancing.m'), ...
 fullfile(root,'Section-Modulation','fig_dclink_ripple.m')};
for k=1:numel(files),runOne(files{k});end
end
function runOne(file)
run(file);
end

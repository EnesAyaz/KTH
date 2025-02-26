load('C:\Github\KTH\IEMDC-2025\Final Paper Codes\Three-Level\Waweforms\F\current_waveform10.mat')
figure();
plot(data.time,data.i_q_time)
hold on
plot(data.time,data.i_d_time)

% 
% data.i_d_time(end)-data.i_d_time(1)
% 
% data.i_q_time(end)-data.i_q_time(1)
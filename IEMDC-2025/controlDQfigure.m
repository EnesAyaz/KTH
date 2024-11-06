load('C:\Github\KTH\IEMDC-2025\Waveforms\4\current_waveform10.mat')
figure()
plot(data.time, data.i_q_time,"r")
hold on
plot(data.time, data.i_d_time,"b")
hold on

[ mean(data.i_q_time) mean(data.i_d_time) max(data.i_q_time)-min(data.i_q_time) max(data.i_d_time)-min(data.i_d_time) ]
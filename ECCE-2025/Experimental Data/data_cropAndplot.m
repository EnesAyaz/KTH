
start_point=13;

time_data=Time(start_point:end);

phA_voltage=Va(start_point:end);

phB_voltage=Vb(start_point:end);

phC_voltage=Vc(start_point:end);


%%

figure();

plot(time_data,phA_voltage)
hold on; 
plot(time_data,phB_voltage)
hold on; 
plot(time_data,phC_voltage)
hold on; 

%%
figure();

plot(time_data,phA_voltage+phB_voltage+phC_voltage)



counter_freq=1e6; 
switching_freq=40e3; 
fundamental_freq= 400;

maximum_count= (counter_freq/switching_freq)/2;

carrier_A=0; 
carrier_p=-1;

carrier_A_cum=[];

for i=0:1/counter_freq:1/fundamental_freq

if carrier_A<=maximum_count && carrier_A>carrier_p
    carrier_p=carrier_A;
    carrier_A=carrier_A+1
elseif carrier_A>maximum_count
    carrier_p=carrier_A;
    carrier_A=carrier_A-1;
elseif carrier_A<=maximum_count && carrier_A<=carrier_p
    carrier_p=carrier_A;
    carrier_A=carrier_A-1;
elseif carrier_A<=-maximum_count
    carrier_p=carrier_A;
    carrier_A=carrier_A+1;
end 

carrier_A_cum= [carrier_A_cum carrier_A];

end

plot(carrier_A_cum)
f_o= 500; %hz % fundamental frequency
f_s=10*1e3; %hz % switching frequency
The_o= [0 -2*pi/3 2*pi/3];
The_c=[0 pi/2 pi 3*pi/2]; % carrier phase shift
k=0.9; % modulation index

%% Phase A;
[frequencyA,SA]= SwitchingFunction(f_o,f_s,The_o(1),The_c(1),k);


%% phase B
[frequencyB,SB]= SwitchingFunction(f_o,f_s,The_o(2),The_c(1),k);

%% phase C

[frequencyC,SC]= SwitchingFunction(f_o,f_s,The_o(3),The_c(1),k);


%%  Convolution;
phaseAcurrent= [f_o ,-pi/9, 320];  % fout phase magnitude
phaseBcurrent= [f_o ,(-2*pi/3)-pi/9, 320];
phaseCcurrent= [f_o ,(2*pi/3)-pi/9, 320];

%% phase A
frequency_A_new= [];
SAIA=[];
for i=1:length(frequencyA)
    
   frequency_A_new =[ frequency_A_new, abs(frequencyA(i)- phaseAcurrent(1)), abs(frequencyA(i)+ phaseAcurrent(1))];
   SAIA= [SAIA, SA(i)*exp(1i*phaseAcurrent(2))*phaseAcurrent(3)/2,SA(i)*exp(1i*phaseAcurrent(2))*phaseAcurrent(3)/2];
        
end

%% phase B
frequency_B_new= [];
SBIB=[];
for i=1:length(frequencyB)
    
   frequency_B_new =[ frequency_B_new, abs(frequencyB(i)- phaseBcurrent(1)), abs(frequencyB(i)+ phaseBcurrent(1))];
   SBIB= [SBIB, SB(i)*exp(1i*phaseBcurrent(2))*phaseBcurrent(3)/2,SB(i)*exp(1i*phaseBcurrent(2))*phaseBcurrent(3)/2];
        
end

%%

%% phase C
frequency_C_new= [];
SCIC=[];
for i=1:length(frequencyC)
    
   frequency_C_new =[ frequency_C_new, abs(frequencyC(i)- phaseCcurrent(1)), abs(frequencyC(i)+ phaseCcurrent(1))];
   
   SCIC= [SCIC, SC(i)*exp(1i*phaseCcurrent(2))*phaseCcurrent(3)/2,SC(i)*exp(1i*phaseCcurrent(2))*phaseCcurrent(3)/2];
        
end


%% capacitor responses
w= 2*pi*frequency_C_new;

stepResponsesAllPhase

% 
% [capA_phA, capA_phB,capA_phC,...
%           capB_phA, capB_phB,capB_phC,...
%           capC_phA, capC_phB,capC_phC]= capacitor_response(w);
      
      
      
%% capacitor response A 
cap1= cap1_phA.*SAIA+ cap1_phB.*SBIB+ cap1_phC.*SCIC;
cap2= cap2_phA.*SAIA+ cap2_phB.*SBIB+ cap2_phC.*SCIC;
cap3= cap3_phA.*SAIA+ cap3_phB.*SBIB+ cap3_phC.*SCIC;
cap4= cap4_phA.*SAIA+ cap4_phB.*SBIB+ cap4_phC.*SCIC;

cap1= cap1_phA.*SAIA + cap1_phB.*SBIB+ cap1_phC.*SCIC

S=SAIA+SBIB+SCIC
%%

FreqLimit=80e3;
figure;
hold all;
subplot(2,1,1);
stem(w/(2*pi),abs(SAIA),'b-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of'  ' Capaacitor A'} ...
    ,'FontSize',14,'FontWeight','Bold');
grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])

subplot(2,1,2);
stem(w/(2*pi),abs(S),'b-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of'  ' Capaacitor A'} ...
    ,'FontSize',14,'FontWeight','Bold');
grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])



%%
FreqLimit=80e3;
figure;
hold all;
subplot(2,2,1);
stem(w/(2*pi),abs(cap1),'b-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of'  ' Capaacitor A'} ...
    ,'FontSize',14,'FontWeight','Bold');
grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])



subplot(2,2,2);
stem(w/(2*pi),abs(cap2),'r-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of' 'Capaacitor B'} ...
    ,'FontSize',14,'FontWeight','Bold');

grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])

subplot(2,2,3);
stem(w/(2*pi),abs(cap3),'k-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of'  'Capacitor C'} ...
    ,'FontSize',14,'FontWeight','Bold');


grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])
      
subplot(2,2,4);
stem(w/(2*pi),abs(cap4),'k-','Linewidth',1);
xlabel('Frequency (Hz)','FontSize',14,'FontWeight','Bold')
ylabel({'Frequency Response (Mag) of'  'Capacitor C'} ...
    ,'FontSize',14,'FontWeight','Bold');
grid on;
set(gca,'FontSize',10);
xlim([0 FreqLimit])

%%
cap2(isnan(cap2)) = 0;

sqrt(sum(abs(cap2).^2))


% sqrt(sum(abs(SAIA).^2))
